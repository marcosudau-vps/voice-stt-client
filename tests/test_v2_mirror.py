from copy import deepcopy
from dataclasses import FrozenInstanceError
import asyncio
import itertools
import unittest

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import ActivationMirror, MirrorLimits, MirrorState
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from voice_stt_client.core.command_tracker import TransportLost
from tests.test_v2_protocol import FIXTURES, IDS, event
from tests.test_v2_transport import FakeWebSocket, no_settings, until

A, B, S = IDS['activationId'], p.new_id(), IDS['segmentId']


def snapshot(seq=0, version=0, *, active=None, phase='idle', pending=(), **fields):
    data = deepcopy(FIXTURES['snapshot'])
    data.update(lastEventSeq=seq, stateVersion=version, settingsRevision=0, pendingActivations=list(pending), **fields)
    data['audioAvailable'] = True
    data['trigger']['effective']['manual'] = True
    data['input'] = dict(phase=phase, activationId=active, primarySource='manual' if active else None,
                         deadlineAtUnixMs=100000 if active else None, remainingMs=10000 if active else None,
                         closeRequested=phase == 'closing_input')
    return p.parse_snapshot(data)


def pending(aid=A, count=1, terminal=0, seq=1):
    return dict(activationId=aid, activationSequence=seq, inputClosedReason='finished', processingState='draining',
                acceptedSegmentCount=count, terminalSegmentCount=terminal)


def msg(kind, seq, *, aid=A, sid=S, segment_sequence=1, version=None, **fields):
    data = event(kind)
    data.update(eventId=p.new_id(), eventSeq=seq, stateVersion=seq if version is None else version)
    if 'activationId' in data:
        data['activationId'] = aid
    if 'segmentId' in data and kind != p.EventType.WATCHDOG_WARNING:
        data.update(segmentId=sid, segmentSequence=segment_sequence)
    data.update(fields)
    return p.decode_server_message(data)


class Mirror(unittest.TestCase):
    def setUp(self):
        self.m = ActivationMirror()
        self.m.begin(1, snapshot(), 10)
        self.seq = 0

    def send(self, kind, **fields):
        self.seq += 1
        return self.m.consume(1, msg(kind, self.seq, **fields), 10)

    def test_all_eighteen_events_have_actual_reduction(self):
        for kind in p.EventType:
            with self.subTest(kind=kind):
                m = ActivationMirror()
                m.begin(1, snapshot(active=A, phase='waiting_first_speech'), 10)
                result = m.consume(1, msg(kind, 1, **({'catalogRevision':2} if kind == p.EventType.WAKE_AVAILABILITY else {})), 10)
                self.assertEqual(result.view.last_event_seq, 1)
                self.assertEqual(result.events[0].type, kind)
                if kind == p.EventType.COMPLETED:
                    self.assertEqual(len(result.finals), 1)
                if kind == p.EventType.WAKE_DETECTED:
                    self.assertEqual(result.view.activations[A].wake_word_id, msg(kind, 1).payload['wakeWordId'])
                if kind == p.EventType.WATCHDOG_WARNING:
                    self.assertIsNotNone(result.view.activations[A].watchdog)
                if kind == p.EventType.SETTINGS_CHANGED:
                    self.assertIn('settings_required', result.effects)
                if kind == p.EventType.WAKE_AVAILABILITY:
                    self.assertIn('catalog_required', result.effects)

    def test_server_foreground_phases_and_countdown(self):
        self.send(p.EventType.ACTIVATION_STARTED)
        for phase in list(p.InputPhase)[1:]:
            result = self.send(p.EventType.PHASE_CHANGED, inputPhase=phase, deadlineAtUnixMs=100000, remainingMs=3000)
            self.assertEqual(result.view.input.phase, phase)
            self.assertEqual(result.view.input.close_requested, phase == p.InputPhase.CLOSING_INPUT)
            self.assertEqual(result.view.input.deadline.remaining(11), 2000)
            self.assertEqual(result.view.input.deadline.remaining(99), 0)
        self.assertEqual(self.m.tick(1, 11).effects, ())
        self.assertEqual(self.m.view.input.phase, p.InputPhase.CLOSING_INPUT)

    def test_known_additive_fields_cannot_cross_domain_boundaries(self):
        session_events = (p.EventType.TRIGGER_SUPPRESSED, p.EventType.WAKE_AVAILABILITY, p.EventType.SETTINGS_CHANGED)
        segment_events = (p.EventType.RECORDING_STARTED, p.EventType.RECORDING_ENDED, p.EventType.TRANSCRIPTION_ACCEPTED,
                          p.EventType.INTERIM, p.EventType.COMPLETED, p.EventType.DISCARDED, p.EventType.FAILED)
        for kind in p.EventType:
            with self.subTest(kind=kind):
                self.setUp()
                data = msg(kind, 1).to_mapping()
                if kind in session_events:
                    data['activationId'] = 'future unused field'
                if kind not in segment_events and kind != p.EventType.WATCHDOG_WARNING:
                    data['segmentId'] = 'future unused field'
                    data['segmentSequence'] = 'future unused field'
                result = self.m.consume(1, p.decode_server_message(data), 10)
                self.assertEqual(result.view.last_event_seq, 1)
                if kind not in segment_events:
                    self.assertFalse(result.view.segments)
                if kind in session_events:
                    self.assertFalse(result.view.activations)

    def test_countdown_uses_receipt_not_wallclock_and_nulls(self):
        result = self.m.consume(1, snapshot(active=A, phase='followup_wait'), 50)
        self.assertEqual(result.view.input.deadline.remaining(52.5), 7500)
        self.assertEqual(result.view.input.deadline.remaining(49), 10000)
        self.assertEqual(self.m.consume(1, snapshot(), 55).view.input.deadline, None)
        self.assertFalse(self.m.view.input.close_requested)

    def test_manual_and_wake_share_one_foreground(self):
        self.send(p.EventType.ACTIVATION_STARTED, primarySource='wake_word')
        self.send(p.EventType.WAKE_DETECTED)
        self.send(p.EventType.TRIGGER_SUPPRESSED)
        self.assertEqual(self.m.view.input.activation_id, A)
        self.assertEqual(self.m.view.input.primary_source, 'wake_word')
        self.assertFalse(self.m.view.manual_available)
        self.send(p.EventType.RECORDING_ENDED)
        self.send(p.EventType.PHASE_CHANGED, inputPhase='followup_wait')
        self.assertFalse(self.m.view.manual_available)

    def test_terminal_before_close_does_not_release_foreground(self):
        for terminal in (p.EventType.ACTIVATION_COMPLETED, p.EventType.ACTIVATION_CANCELLED, p.EventType.ACTIVATION_FAILED):
            self.setUp()
            self.send(p.EventType.ACTIVATION_STARTED)
            self.send(terminal)
            self.assertEqual(self.m.view.input.activation_id, A)
            self.assertFalse(self.m.view.manual_available)
            self.send(p.EventType.INPUT_CLOSED)
            self.assertEqual(self.m.view.input.phase, p.InputPhase.IDLE)

    def test_b_start_before_a_close_and_old_final_during_b(self):
        self.send(p.EventType.ACTIVATION_STARTED)
        self.send(p.EventType.RECORDING_STARTED)
        self.send(p.EventType.ACTIVATION_STARTED, aid=B, activationSequence=2)
        self.send(p.EventType.PHASE_CHANGED, aid=B, inputPhase='segment_active')
        self.send(p.EventType.INPUT_CLOSED)
        final = self.send(p.EventType.COMPLETED, text='synthetic old final')
        self.assertEqual(final.finals[0].activation_id, A)
        self.assertEqual(self.m.view.input.activation_id, B)
        self.assertEqual(self.m.view.input.phase, p.InputPhase.SEGMENT_ACTIVE)
        self.assertTrue(self.m.view.activations[A].input_closed)

    def test_idle_with_multiple_drains_allows_manual(self):
        self.send(p.EventType.ACTIVATION_STARTED)
        self.send(p.EventType.INPUT_CLOSED)
        self.send(p.EventType.ACTIVATION_STARTED, aid=B, activationSequence=2)
        self.send(p.EventType.INPUT_CLOSED, aid=B)
        self.assertEqual([a.status for a in self.m.view.activations.values()], ['draining', 'draining'])
        self.assertTrue(self.m.view.manual_available)
        self.assertNotIn('finalizing', {x.value for x in p.InputPhase})

    def test_discard_and_failure_before_ended_accepted_interim(self):
        for terminal in (p.EventType.DISCARDED, p.EventType.FAILED, p.EventType.COMPLETED):
            self.setUp()
            self.send(terminal)
            first = self.m.view.segments[S]
            for kind in (p.EventType.RECORDING_ENDED, p.EventType.TRANSCRIPTION_ACCEPTED,
                         p.EventType.RECORDING_STARTED, p.EventType.INTERIM, p.EventType.COMPLETED):
                result = self.send(kind)
                self.assertEqual(self.m.view.segments[S], first)
                self.assertFalse(result.finals)

    def test_multiple_segments_and_terminal_holes_do_not_block_final(self):
        self.send(p.EventType.ACTIVATION_STARTED)
        collected = []
        for i, terminal in enumerate((p.EventType.DISCARDED, p.EventType.FAILED, p.EventType.COMPLETED, p.EventType.COMPLETED), 1):
            sid = p.new_id()
            self.send(p.EventType.RECORDING_STARTED, sid=sid, segment_sequence=i)
            self.send(p.EventType.RECORDING_ENDED, sid=sid, segment_sequence=i)
            collected.extend(self.send(terminal, sid=sid, segment_sequence=i, **({'text':'same synthetic text'} if terminal == p.EventType.COMPLETED else {})).finals)
        self.assertEqual([x.segment_sequence for x in collected], [3, 4])
        self.assertEqual(len(self.m.view.segments), 4)
        self.assertEqual({s.activation_id for s in self.m.view.segments.values()}, {A})

    def test_interims_equal_versions_segment_owned_display_fallback(self):
        self.send(p.EventType.INTERIM, version=0, text='one', displayText='display')
        self.send(p.EventType.INTERIM, version=0, text='two', displayText=False)
        self.send(p.EventType.INTERIM, aid=B, sid=p.new_id(), segment_sequence=2, version=0, text='new recording')
        self.assertEqual(self.m.view.segments[S].preview, 'two')
        self.assertEqual(self.m.view.state_version, 0)
        self.assertEqual(self.m.view.last_event_seq, 3)
        self.assertEqual(self.m.view.input.phase, p.InputPhase.IDLE)

    def test_generation_session_duplicate_and_unknown_sequence(self):
        value = msg(p.EventType.INTERIM, 1)
        self.assertFalse(self.m.consume(2, value, 10).events)
        foreign = value.to_mapping(); foreign['sessionId'] = p.new_id()
        self.assertFalse(self.m.consume(1, p.decode_server_message(foreign), 10).events)
        self.m.consume(1, value, 10)
        self.assertFalse(self.m.consume(1, value, 10).events)
        data = value.to_mapping(); data.update(type='future.additive', eventId=p.new_id(), eventSeq=2, stateVersion=42)
        result = self.m.consume(1, p.decode_server_message(data), 10)
        self.assertEqual(result.view.last_event_seq, 2)
        self.assertEqual(result.view.state_version, 42)
        self.assertEqual(result.view.state, MirrorState.READY)
        self.assertEqual(result.effects, ('unknown_event',))
        self.assertEqual(result.view.segments[S].preview, value.preview_text)

    def test_state_version_jump_without_sequence_gap(self):
        self.send(p.EventType.INTERIM, version=99)
        self.send(p.EventType.INTERIM, version=99)
        self.assertEqual(self.m.view.state, MirrorState.READY)
        self.assertEqual(self.m.view.state_version, 99)

    def test_conflicting_event_id_never_republishes(self):
        value = msg(p.EventType.COMPLETED, 1, text='one')
        self.m.consume(1, value, 10)
        bad = value.to_mapping(); bad.update(text='contradiction', eventSeq=2)
        result = self.m.consume(1, p.decode_server_message(bad), 10)
        self.assertEqual(result.view.state, MirrorState.RESYNCING)
        self.assertFalse(result.finals)
        self.assertEqual(result.view.segments[S].text, 'one')

    def test_segment_identity_and_sequence_collision_degrade(self):
        for fields in (dict(aid=B), dict(segment_sequence=2), dict(sid=p.new_id())):
            self.setUp()
            self.send(p.EventType.INTERIM)
            result = self.send(p.EventType.COMPLETED, **fields)
            self.assertEqual(result.view.state, MirrorState.RESYNCING)
            self.assertFalse(result.finals)
            self.assertEqual(len(result.view.segments), 1)
            self.assertEqual(set(result.view.activations), {A})

    def test_snapshot_equal_version_higher_seq_and_stale_bounds(self):
        self.send(p.EventType.INTERIM, version=4)
        self.m.consume(1, snapshot(7, 4), 11)
        self.assertEqual(self.m.view.last_event_seq, 7)
        for seq, version in ((6, 4), (7, 3), (10, 3)):
            result = self.m.consume(1, snapshot(seq, version), 12)
            self.assertIn('stale_snapshot', result.effects)
            self.assertEqual(result.view.last_event_seq, 7)
            self.assertEqual(result.view.state_version, 4)

    def test_snapshot_all_domains_and_safe_immutable_projection(self):
        original = self.m.view
        result = self.m.consume(1, snapshot(1, 3, active=A, phase='closing_input', pending=(pending(B, seq=2),)), 10)
        self.assertEqual(result.view.input.phase, p.InputPhase.CLOSING_INPUT)
        self.assertTrue(result.view.input.close_requested)
        self.assertEqual(result.view.activations[B].status, 'draining')
        self.assertEqual(len(result.view.requested_settings), 16)
        self.assertIn('catalogRevision', result.view.capabilities)
        with self.assertRaises(TypeError): result.view.activations[A] = None
        with self.assertRaises(TypeError): result.view.requested_settings['x'] = 1
        with self.assertRaises(FrozenInstanceError): result.view.input.phase = 'idle'
        self.assertEqual(len(original.activations), 0)

    def test_activation_settings_frozen_across_snapshot_and_settings_events(self):
        self.send(p.EventType.ACTIVATION_STARTED, effectiveSettings={'activation.followupTimeoutMs': 1234})
        self.send(p.EventType.SETTINGS_CHANGED, settingsRevision=1)
        newer = snapshot(self.seq, self.seq, active=A, phase='followup_wait').to_mapping()
        newer['effectiveSettings']['activation.followupTimeoutMs'] = 5000
        newer['settingsRevision'] = 1
        newer['requestedSettings']['activation.followupTimeoutMs'] = 6000
        self.m.consume(1, p.parse_snapshot(newer), 11)
        self.assertEqual(self.m.view.activations[A].effective_settings['activation.followupTimeoutMs'], 1234)
        self.assertEqual(self.m.view.effective_settings['activation.followupTimeoutMs'], 5000)
        self.assertEqual(self.m.view.requested_settings['activation.followupTimeoutMs'], 6000)
        self.send(p.EventType.ACTIVATION_STARTED, aid=B, activationSequence=2, effectiveSettings={'activation.followupTimeoutMs':6000})
        self.assertEqual(self.m.view.activations[B].effective_settings['activation.followupTimeoutMs'], 6000)

    def test_close_reason_command_identity_and_unknown_reasons(self):
        for reason, command in (('finished', p.new_id()), ('cancelled', p.new_id()), ('timed_out', None), ('device_lost', None), ('future_reason', None)):
            self.setUp(); self.send(p.EventType.ACTIVATION_STARTED)
            self.send(p.EventType.INPUT_CLOSED, reason=reason, causedByCommandId=command)
            a = self.m.view.activations[A]
            self.assertEqual((a.close_reason, a.caused_by_command_id), (reason, command))

    def test_gap_requests_once_and_buffers_until_snapshot(self):
        self.send(p.EventType.RECORDING_STARTED)
        result = self.m.consume(1, msg(p.EventType.INTERIM, 3), 10)
        self.assertEqual(result.effects, ('snapshot_required',))
        self.assertFalse(result.view.operations_ready)
        for i in (5, 4):
            result = self.m.consume(1, msg(p.EventType.INTERIM, i), 10)
            self.assertNotIn('snapshot_required', result.effects)
        result = self.m.consume(1, snapshot(3, 3, active=A, phase='segment_active'), 11)
        self.assertEqual(result.view.last_event_seq, 5)
        self.assertTrue(result.view.operations_ready)
        self.assertFalse(result.view.snapshot_pending)

    def test_buffered_final_at_or_behind_cursor_salvaged_once(self):
        for cursor in (3, 4, 5):
            self.setUp(); self.send(p.EventType.RECORDING_STARTED)
            value = msg(p.EventType.COMPLETED, 3, text='synthetic salvaged')
            self.m.consume(1, value, 10)
            result = self.m.consume(1, snapshot(cursor, 5, pending=(pending(terminal=1),)), 11)
            self.assertEqual([x.text for x in result.finals], ['synthetic salvaged'])
            self.assertFalse(result.view.incomplete)
            self.assertEqual(result.view.input.phase, p.InputPhase.IDLE)
            self.assertFalse(self.m.consume(1, value, 12).finals)
            self.assertFalse(self.m.consume(1, snapshot(cursor, 5), 12).finals)

    def test_snapshot_preserves_received_final_and_terminal_dedup(self):
        first = self.send(p.EventType.COMPLETED, text='synthetic retained')
        self.m.consume(1, snapshot(5, 5), 11)
        self.assertEqual(self.m.view.segments[S].text, first.finals[0].text)
        self.assertFalse(self.m.consume(1, msg(p.EventType.COMPLETED, 6), 12).finals)

    def test_lost_final_and_disappeared_pending_are_incomplete_no_text(self):
        self.send(p.EventType.RECORDING_STARTED)
        result = self.m.consume(1, snapshot(4, 4, pending=(pending(terminal=1),)), 11)
        self.assertTrue(result.view.incomplete)
        self.assertFalse(result.finals)
        result = self.m.consume(1, snapshot(5, 5), 12)
        self.assertEqual(result.view.activations[A].status, 'terminal_unknown')
        self.assertEqual(result.view.segments[S].status, 'terminal_unknown')
        self.assertIsNone(result.view.segments[S].text)

    def test_buffered_lifecycle_not_applied_backwards(self):
        self.send(p.EventType.ACTIVATION_STARTED)
        self.m.consume(1, msg(p.EventType.PHASE_CHANGED, 3, inputPhase='segment_active'), 10)
        result = self.m.consume(1, snapshot(4, 4, active=B, phase='followup_wait'), 11)
        self.assertEqual(result.view.input.activation_id, B)
        self.assertEqual(result.view.input.phase, p.InputPhase.FOLLOWUP_WAIT)
        self.assertEqual(result.view.activations[A].status, 'terminal_unknown')

    def test_buffered_cancel_failed_tombstones_suppress_unpublished_only(self):
        for terminal in (p.EventType.ACTIVATION_CANCELLED, p.EventType.ACTIVATION_FAILED):
            self.setUp()
            self.send(p.EventType.COMPLETED, text='already published')
            self.m.consume(1, msg(terminal, 3), 10)
            self.m.consume(1, msg(p.EventType.COMPLETED, 4, sid=p.new_id(), segment_sequence=2, text='forbidden'), 10)
            result = self.m.consume(1, snapshot(4, 4), 11)
            self.assertFalse(result.finals)
            self.assertEqual(result.view.segments[S].text, 'already published')
            self.assertEqual(result.view.activations[A].status, terminal.split('.')[1])
            result = self.m.consume(1, msg(p.EventType.COMPLETED, 5, sid=p.new_id(), segment_sequence=3), 12)
            self.assertFalse(result.finals)
            self.assertEqual(result.view.input.phase, p.InputPhase.IDLE)

    def test_buffered_final_before_cancel_remains_published(self):
        self.send(p.EventType.RECORDING_STARTED)
        self.m.consume(1, msg(p.EventType.COMPLETED, 3, text='synthetic valid before cancel'), 10)
        self.m.consume(1, msg(p.EventType.ACTIVATION_CANCELLED, 4), 10)
        result = self.m.consume(1, snapshot(4, 4), 11)
        self.assertEqual(len(result.finals), 1)
        self.assertEqual(result.view.segments[S].status, 'completed')

    def test_new_gap_during_replay_stays_gated_with_new_request(self):
        self.send(p.EventType.RECORDING_STARTED)
        self.m.consume(1, msg(p.EventType.INTERIM, 3), 10)
        self.m.consume(1, msg(p.EventType.INTERIM, 5), 10)
        result = self.m.consume(1, snapshot(3, 3, active=A, phase='segment_active'), 11)
        self.assertEqual(result.view.state, MirrorState.RESYNCING)
        self.assertIn('snapshot_required', result.effects)
        self.assertEqual(result.view.last_event_seq, 3)
        result = self.m.consume(1, snapshot(4, 4, active=A, phase='segment_active'), 12)
        self.assertEqual(result.view.last_event_seq, 5)
        self.assertTrue(result.view.operations_ready)

    def test_resync_event_and_byte_overflow_is_incomplete_reconnect(self):
        for limits in (MirrorLimits(max_events=1), MirrorLimits(max_bytes=1)):
            m = ActivationMirror(limits); m.begin(1, snapshot(active=A, phase='segment_active'), 10)
            result = m.consume(1, msg(p.EventType.INTERIM, 2), 10)
            if result.view.state != MirrorState.RECONNECT_REQUIRED:
                result = m.consume(1, msg(p.EventType.INTERIM, 3), 10)
            self.assertEqual(result.view.state, MirrorState.RECONNECT_REQUIRED)
            self.assertTrue(result.view.incomplete)
            self.assertIn('reconnect_required', result.effects)
            self.assertFalse(result.view.snapshot_pending)

    def test_timeout_two_attempts_stale_snapshot_does_not_extend_budget(self):
        self.send(p.EventType.RECORDING_STARTED)
        self.m.consume(1, msg(p.EventType.INTERIM, 3), 10)
        result = self.m.consume(1, snapshot(0, 0), 14)
        self.assertNotIn('snapshot_required', result.effects)
        self.assertEqual(self.m.tick(1, 15).effects, ('snapshot_required',))
        result = self.m.tick(1, 20)
        self.assertEqual(result.view.state, MirrorState.RECONNECT_REQUIRED)
        self.assertTrue(result.view.incomplete)
        self.assertEqual(result.view.activations[A].status, 'terminal_unknown')

    def test_start_missing_deadline_clarification_does_not_timeout_activation(self):
        result = self.send(p.EventType.ACTIVATION_STARTED)
        self.assertEqual(result.effects, ('snapshot_required',))
        self.m.consume(1, snapshot(1, 1, active=A, phase='waiting_first_speech'), 11)
        result = self.m.tick(1, 1000)
        self.assertEqual(result.view.input.phase, p.InputPhase.WAITING_FIRST_SPEECH)
        self.assertFalse(result.effects)

    def test_disconnect_retains_text_and_rebind_isolated(self):
        self.send(p.EventType.COMPLETED, text='synthetic retained')
        sid = p.new_id(); self.send(p.EventType.INTERIM, sid=sid, segment_sequence=2)
        old = self.m.view
        result = self.m.disconnect(1)
        self.assertEqual(result.view.state, MirrorState.DISCONNECTED)
        self.assertTrue(result.view.incomplete)
        self.assertEqual(result.view.segments[S].text, 'synthetic retained')
        self.assertFalse(self.m.consume(1, msg(p.EventType.COMPLETED, 3), 11).finals)
        self.m.begin(2, snapshot(), 12)
        self.assertEqual(len(self.m.view.segments), 0)
        self.assertEqual(old.segments[S].status, 'completed')
        self.m.disconnect(1)
        self.assertEqual(self.m.view.state, MirrorState.READY)
        self.m.begin(1, snapshot(9, 9), 12)
        self.assertEqual(self.m.view.last_event_seq, 0)

    def test_empty_completed_is_terminal_final_and_repr_has_no_text(self):
        result = self.send(p.EventType.COMPLETED, text='')
        self.assertEqual(result.finals[0].text, '')
        self.assertEqual(result.view.segments[S].status, 'completed')
        self.send(p.EventType.COMPLETED, sid=p.new_id(), segment_sequence=2, text='private synthetic sentinel')
        self.assertNotIn('private synthetic sentinel', repr(self.m.view))

    def test_generated_races_have_id_and_terminal_invariants_each_step(self):
        count = 0
        # Enumerate all valid interleavings: A's final/terminal/close and B's
        # start/recording. Terminals and close may race; B start precedes B segment.
        labels = ('a_final', 'a_terminal', 'a_close', 'b_start', 'b_record')
        for order in itertools.permutations(labels):
            if order.index('b_start') > order.index('b_record'): continue
            self.setUp(); self.send(p.EventType.ACTIVATION_STARTED); self.send(p.EventType.RECORDING_STARTED)
            bs = p.new_id(); finals = []
            operations = {'a_final':(p.EventType.COMPLETED, {}), 'a_terminal':(p.EventType.ACTIVATION_COMPLETED, {}),
                          'a_close':(p.EventType.INPUT_CLOSED, {}),
                          'b_start':(p.EventType.ACTIVATION_STARTED, dict(aid=B, activationSequence=2)),
                          'b_record':(p.EventType.RECORDING_STARTED, dict(aid=B, sid=bs, segment_sequence=2))}
            b_started = False
            for label in order:
                kind, fields = operations[label]; result = self.send(kind, **fields); finals.extend(result.finals)
                b_started |= label == 'b_start'
                self.assertEqual(result.view.segments[S].activation_id, A)
                if b_started: self.assertEqual(result.view.input.activation_id, B)
                self.assertNotEqual(result.view.input.phase, 'finalizing')
            self.assertEqual(len(finals), 1)
            count += 1
        self.assertEqual(count, 60)

    def test_default_512_event_buffer_bound_and_no_duplicate_budget_use(self):
        first = msg(p.EventType.INTERIM, 2)
        self.m.consume(1, first, 10)
        for _ in range(20): self.m.consume(1, first, 10)
        for i in range(3, 514): self.m.consume(1, msg(p.EventType.INTERIM, i), 10)
        self.assertEqual(self.m.view.state, MirrorState.RESYNCING)
        self.assertEqual(len(self.m._buffer), 512)
        result = self.m.consume(1, msg(p.EventType.INTERIM, 514), 10)
        self.assertEqual(result.view.state, MirrorState.RECONNECT_REQUIRED)
        self.assertEqual(len(self.m._buffer), 0)

    def test_snapshot_cannot_change_activation_identity_or_regress_settings(self):
        self.send(p.EventType.ACTIVATION_STARTED, activationSequence=1)
        result = self.m.consume(1, snapshot(1, 1, pending=(pending(seq=9),)), 10)
        self.assertIn('protocol_fault', result.effects)
        self.assertEqual(result.view.activations[A].sequence, 1)
        self.setUp(); self.send(p.EventType.SETTINGS_CHANGED, settingsRevision=5)
        result = self.m.consume(1, snapshot(4, 4), 10)
        self.assertIn('stale_snapshot', result.effects)
        self.assertEqual(result.view.settings_revision, 5)

    def test_unseen_buffered_segment_missing_lifecycle_is_unknown(self):
        self.m.consume(1, msg(p.EventType.COMPLETED, 3), 10)
        result = self.m.consume(1, snapshot(3, 3), 11)
        self.assertEqual(len(result.finals), 1)
        self.assertEqual(result.view.activations[A].status, 'terminal_unknown')
        self.assertTrue(result.view.incomplete)

    def test_all_terminal_cancel_permutations_first_terminal_wins(self):
        for order in itertools.permutations((p.EventType.DISCARDED, p.EventType.RECORDING_ENDED,
                                            p.EventType.TRANSCRIPTION_ACCEPTED, p.EventType.INTERIM)):
            self.setUp()
            for kind in order:
                result = self.send(kind)
                if result.view.segments[S].status == 'discarded':
                    self.assertIsNone(result.view.segments[S].preview)
            self.assertEqual(self.m.view.segments[S].status, 'discarded')
            self.assertFalse(self.send(p.EventType.COMPLETED).finals)

    def test_invalid_local_limits(self):
        for kwargs in (dict(max_events=0), dict(max_bytes=True), dict(snapshot_attempts=0), dict(snapshot_timeout=float('nan'))):
            with self.assertRaises(ValueError): ActivationMirror(MirrorLimits(**kwargs))

    def test_retention_pins_late_final_and_gap_salvage_until_settled(self):
        self.m = ActivationMirror(MirrorLimits(retained_activations=2))
        self.m.begin(1, snapshot(), 10)
        self.send(p.EventType.ACTIVATION_STARTED)
        self.send(p.EventType.RECORDING_STARTED)
        self.send(p.EventType.INPUT_CLOSED, acceptedSegmentCount=1)
        self.send(p.EventType.ACTIVATION_COMPLETED, acceptedSegmentCount=1, terminalSegmentCount=1)
        for number in range(2, 202):
            aid, sid = p.new_id(), p.new_id()
            self.send(p.EventType.ACTIVATION_STARTED, aid=aid, activationSequence=number)
            self.send(p.EventType.COMPLETED, aid=aid, sid=sid, segment_sequence=number)
            self.send(p.EventType.INPUT_CLOSED, aid=aid, acceptedSegmentCount=1)
            self.send(p.EventType.ACTIVATION_COMPLETED, aid=aid, acceptedSegmentCount=1, terminalSegmentCount=1)
        self.assertEqual(len(self.m.activations), 201)
        self.assertEqual(self.m._retired_segment_sequence, 0)
        # The old final arrives across a gap and at the snapshot cursor.
        self.seq += 2
        late = msg(p.EventType.COMPLETED, self.seq, text='late preserved')
        self.m.consume(1, late, 11)
        result = self.m.consume(1, snapshot(self.seq, self.seq), 12)
        self.assertEqual([f.text for f in result.finals], ['late preserved'])
        self.assertTrue(result.view.operations_ready)
        self.assertEqual(result.view.segments[S].text, 'late preserved')
        self.assertFalse(self.m.consume(1, late, 12).finals)
        result = self.m.consume(1, snapshot(self.seq, self.seq), 13)
        self.assertLessEqual(len(result.view.activations), 2)

    def test_unknown_or_unresolved_retention_budget_fails_visibly_without_eviction(self):
        for unknown in (False, True):
            with self.subTest(unknown=unknown):
                m = ActivationMirror(MirrorLimits(retained_activations=1, max_records=4))
                m.begin(1, snapshot(), 1)
                for seq in range(1, 6):
                    result = m.consume(1, msg(p.EventType.RECORDING_STARTED, seq,
                        aid=p.new_id(), sid=p.new_id(), segment_sequence=seq), 1)
                    if unknown and seq == 1:
                        m.consume(1, snapshot(1, 1), 1)
                self.assertEqual(result.view.state, MirrorState.RECONNECT_REQUIRED)
                self.assertIn('session_retention_overflow', result.view.loss_reasons)
                self.assertTrue(result.view.incomplete)
                self.assertFalse(result.finals)
                self.assertEqual(len(m.segments), 5)  # bounded triggering record, never silently evicted

    def test_retired_cancel_failed_and_empty_terminals_never_reopen_or_emit(self):
        for terminal in (p.EventType.ACTIVATION_CANCELLED, p.EventType.ACTIVATION_FAILED,
                         p.EventType.ACTIVATION_COMPLETED):
            with self.subTest(terminal=terminal):
                self.setUp()
                self.m = ActivationMirror(MirrorLimits(retained_activations=1))
                self.m.begin(1, snapshot(), 10)
                self.send(p.EventType.ACTIVATION_STARTED)
                self.send(p.EventType.COMPLETED, text='')
                self.send(terminal, acceptedSegmentCount=1, terminalSegmentCount=1)
                self.send(p.EventType.INPUT_CLOSED, acceptedSegmentCount=1)
                self.send(p.EventType.ACTIVATION_STARTED, aid=B, activationSequence=2)
                self.assertNotIn(A, self.m.activations)
                for kind in (p.EventType.COMPLETED, p.EventType.INTERIM, p.EventType.RECORDING_ENDED,
                             p.EventType.ACTIVATION_STARTED):
                    result = self.send(kind)
                    self.assertFalse(result.finals)
                    self.assertFalse(result.events)
                    self.assertNotIn(A, result.view.activations)
                    self.assertEqual(result.view.input.activation_id, B)
                # Lifecycle without a sequence cannot resurrect an expired ID.
                result = self.send(p.EventType.INPUT_CLOSED)
                self.assertEqual(result.view.state, MirrorState.RESYNCING)
                self.assertNotIn(A, result.view.activations)


class Connection(unittest.IsolatedAsyncioTestCase):
    async def start(self, *, limits=None):
        class FreshSocket(FakeWebSocket):
            def push(self, value):
                if isinstance(value, dict) and value.get('type') == 'hello.accepted':
                    value['snapshot']['lastEventSeq'] = 0
                    value['snapshot']['settingsRevision'] = 0
                super().push(value)
        socket = FreshSocket()
        async def connect(*args, **kwargs): return socket
        session = V2STTSession(V2TransportConfig(ack_timeout=.1, command_retries=0, backoff_initial=.01), bootstrap=no_settings, connector=connect)
        adapter = V2MirrorConnection(session, ActivationMirror(limits))
        async def reply(command):
            if command['type'] == p.CommandType.SNAPSHOT_REQUEST:
                data = snapshot().to_mapping(); data['sessionId'] = socket.session_id
                socket.push(data)
            socket.reply(command, revision=0)
        socket.on_send = reply
        task = asyncio.create_task(session.run())
        self.addAsyncCleanup(adapter.close)
        self.addAsyncCleanup(self.join, task)
        await until(lambda: session.is_ready and not adapter.mirror.view.snapshot_pending)
        return session, adapter, socket

    async def join(self, task):
        task.cancel(); await asyncio.gather(task, return_exceptions=True)

    async def test_eventless_bootstrap_ack_reads_actual_snapshot(self):
        session, adapter, socket = await self.start()
        self.assertTrue(adapter.mirror.view.manual_available)
        self.assertEqual(len([x for x in socket.commands if x['type'] == p.CommandType.SNAPSHOT_REQUEST]), 1)
        with self.assertRaises(RuntimeError): V2MirrorConnection(session)

    async def test_gap_gates_actual_transport_and_resync_before_ack(self):
        session, adapter, socket = await self.start()
        allow = asyncio.Event(); requested = asyncio.Event()
        async def reply(command):
            if command['type'] == p.CommandType.SNAPSHOT_REQUEST:
                requested.set(); await allow.wait()
                socket.push(snapshot(3, 3, pending=(pending(terminal=1),)).to_mapping())
            socket.reply(command, revision=0, version=3)
        socket.on_send = reply
        socket.push(msg(p.EventType.COMPLETED, 3, text='synthetic resync').to_mapping())
        await requested.wait()
        with self.assertRaises(TransportLost): await session.request(p.CommandType.ACTIVATION, action='activate', source='manual')
        self.assertEqual(adapter.mirror.view.state, MirrorState.RESYNCING)
        allow.set(); await until(lambda: adapter.mirror.view.operations_ready)
        self.assertEqual(adapter.mirror.view.segments[S].text, 'synthetic resync')
        self.assertEqual(adapter.mirror.view.last_event_seq, 3)

    async def test_malformed_known_event_degrades_without_guessing_identity(self):
        session, adapter, socket = await self.start()
        data = msg(p.EventType.INTERIM, 1).to_mapping(); del data['activationId']
        seen = []; adapter.on_reduction = lambda result: seen.append(result)
        socket.push(data)
        await until(lambda: any('protocol_fault' in x.effects for x in seen))
        await until(lambda: adapter.mirror.view.operations_ready)
        self.assertFalse(adapter.mirror.view.segments)
        self.assertTrue(session.is_ready)

    async def test_closing_ack_clarifies_never_overwrites_foreground(self):
        session, adapter, socket = await self.start()
        session.dispatch(snapshot(2, 2, active=B, phase='segment_active'), session.binding)
        async def reply(command):
            if command['type'] == p.CommandType.SNAPSHOT_REQUEST:
                socket.push(snapshot(2, 2, active=B, phase='segment_active').to_mapping())
                socket.reply(command, version=2, revision=0)
            else: socket.reply(command, 'closing_input', version=1, revision=0, phase='closing_input')
        socket.on_send = reply
        await session.request(p.CommandType.ACTIVATION, action='refresh', activationId=A)
        await until(lambda: not adapter.mirror.view.snapshot_pending)
        self.assertEqual(adapter.mirror.view.input.activation_id, B)
        self.assertEqual(adapter.mirror.view.input.phase, p.InputPhase.SEGMENT_ACTIVE)

    async def test_queued_activation_rechecks_resync_guard_before_send(self):
        session, adapter, socket = await self.start()
        entered = asyncio.Event(); release = asyncio.Event()
        original = socket.on_send
        async def hold(command):
            if command['type'] == p.CommandType.ACTIVATION:
                entered.set(); await release.wait()
                socket.reply(command, revision=0)
            else: await original(command)
        socket.on_send = hold
        first = asyncio.create_task(session.request(p.CommandType.ACTIVATION, action='activate', source='manual'))
        await entered.wait()
        second = asyncio.create_task(session.request(p.CommandType.ACTIVATION, action='activate', source='manual'))
        await asyncio.sleep(0)
        adapter._publish(adapter.mirror.protocol_fault(session.generation, adapter.clock()))
        # Keep snapshot reply behind the activation Ack so the queued command
        # would otherwise leave the domain lock during resync.
        async def only_ack(command): socket.reply(command, revision=0)
        socket.on_send = only_ack
        release.set(); await first
        with self.assertRaises(TransportLost): await second
        self.assertEqual(len([x for x in socket.commands if x['type'] == p.CommandType.ACTIVATION]), 1)

    async def test_1011_recovery_new_session_and_stale_binding_guard(self):
        from tests.test_v2_transport import close_error
        session, adapter, socket = await self.start()
        old = session.binding
        session.dispatch(msg(p.EventType.INTERIM, 1), old)
        class NewSocket(FakeWebSocket):
            def push(self, value):
                if isinstance(value, dict) and value.get('type') == 'hello.accepted':
                    value['snapshot']['lastEventSeq'] = 0
                    value['snapshot']['settingsRevision'] = 0
                super().push(value)
        newer = NewSocket(session_id=p.new_id())
        async def connect(*args, **kwargs): return newer
        async def reply(command):
            if command['type'] == p.CommandType.SNAPSHOT_REQUEST:
                data = snapshot().to_mapping(); data['sessionId'] = newer.session_id; newer.push(data)
            newer.reply(command, revision=0)
        newer.on_send = reply; session._connector = connect
        losses = []; previous = session.on_lost
        def lost(binding):
            previous(binding); losses.append(adapter.mirror.view)
        session.on_lost = lost
        socket.inbox.put_nowait(close_error(1011))
        await until(lambda: session.is_ready and session.binding is not old and not adapter.mirror.view.snapshot_pending)
        self.assertTrue(losses[0].incomplete)
        self.assertEqual(losses[0].segments[S].status, 'terminal_unknown')
        self.assertEqual(adapter.mirror.view.input.phase, p.InputPhase.IDLE)
        self.assertFalse(adapter.mirror.view.segments)
        self.assertFalse(session.dispatch(msg(p.EventType.COMPLETED, 2), old))
        self.assertEqual(adapter.mirror.view.session_id, newer.session_id)

    async def test_missing_snapshot_even_with_ack_reconnects_bounded(self):
        session, adapter, socket = await self.start(limits=MirrorLimits(snapshot_timeout=.02))
        async def reply(command): socket.reply(command, revision=0)
        socket.on_send = reply
        old_binding = session.binding
        socket.push(msg(p.EventType.INTERIM, 2).to_mapping())
        await until(lambda: session.binding is not old_binding)
        self.assertTrue(socket.closed)
        self.assertEqual(adapter.mirror.view.state, MirrorState.DISCONNECTED)
        self.assertTrue(adapter.mirror.view.incomplete)
        requests = [x for x in socket.commands if x['type'] == p.CommandType.SNAPSHOT_REQUEST]
        self.assertEqual(len(requests), 3)  # bootstrap clarification plus two attempts
        self.assertFalse(adapter.mirror.view.snapshot_pending)
