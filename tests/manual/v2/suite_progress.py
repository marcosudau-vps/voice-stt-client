"""Passive, bounded progress observations; never sends commands or grants PASS.

The session caller serializes observe/snapshot with its existing lock. Short
phases remain visible in counters even when they end between two UI polls.
"""
from collections import Counter, deque
import math
import time


class ObservedProgress:
    def __init__(self):
        self.counts = Counter()
        self.generation = 0
        self.ready = self.audio = self.ever_audio = self.audio_lost = False
        self.secondary_at = self.cancelled_at = None
        self.audio_lost_at = None
        self.reconnect_generation = None
        self.closed_reason = ''
        self.seen, self.order = set(), deque()

    def observe(self, kind, *, now=None, **fields):
        now = time.monotonic() if now is None else now
        event = fields.get('event', fields)
        generation = event.get('generation')
        if generation is not None:
            if generation < self.generation:
                return
            self.generation = generation
        if kind == 'wire':
            event_id = event.get('eventId')
            if event_id:
                key = (self.generation, event_id)
                if key in self.seen:
                    return
                self.seen.add(key)
                self.order.append(key)
                if len(self.order) > 1024:
                    self.seen.remove(self.order.popleft())
            name = event['type']
            if name in ('activation.started', 'segment.recording_started', 'segment.recording_ended',
                        'activation.input_closed', 'activation.completed', 'activation.cancelled',
                        'activation.failed', 'transcription.completed'):
                self.counts[name] += 1
            if name == 'activation.input_closed':
                self.closed_reason = event.get('reason', '')
            if name == 'activation.cancelled':
                self.cancelled_at = now
        elif kind == 'control.received':
            if fields.get('ready') and fields.get('slot') == 'secondary' and fields.get('phase') != 'idle':
                self.counts['secondary'] += 1
                self.secondary_at = now
        elif kind == 'runtime.view':
            self.ready = bool(fields.get('ready'))
        elif kind == 'metrics':
            self.audio = bool(fields.get('audioAvailable'))
            if self.ever_audio and not self.audio:
                if not self.audio_lost:
                    self.audio_lost_at = now
                self.audio_lost = True
            self.ever_audio |= self.audio
        elif kind == 'operator.command' and fields.get('action') == 'reconnect':
            self.reconnect_generation = self.generation

    def snapshot(self, now=None):
        now = time.monotonic() if now is None else now
        def remaining(start, seconds):
            return None if start is None else max(0, math.ceil(seconds-(now-start)))
        return dict(counts=dict(self.counts), generation=self.generation, ready=self.ready,
                    audio=self.audio, audioLost=self.audio_lost, closedReason=self.closed_reason,
                    reconnectGeneration=self.reconnect_generation,
                    cancelWaitRemaining=remaining(self.cancelled_at, 10),
                    usbWaitRemaining=remaining(self.audio_lost_at, 10),
                    noneWaitRemaining=remaining(self.secondary_at, 3))


def guide_progress(task, observed, pastes):
    """Indices 0=read,1=prepare,2..4=task,5=review. Checks require evidence."""
    c = observed.get('counts', {})
    activated = c.get('activation.started', 0)
    recording = c.get('segment.recording_started', 0)
    ended = c.get('segment.recording_ended', 0)
    closed = c.get('activation.input_closed', 0)
    terminal = sum(c.get(key, 0) for key in ('activation.completed', 'activation.cancelled', 'activation.failed'))
    secondary = c.get('secondary', 0)
    active, confirmed, wait, notice = 2, set(), None, ''
    manual = task in ('mute', 'settings')
    if task in ('finish', 'followup', 'refresh'):
        if (activated if task == 'finish' else ended):
            active, confirmed = 3, {2}
        if secondary:
            active = 4
            if activated:
                confirmed.add(2)
            if recording >= (1 if task == 'finish' else 2) and activated == 1:
                confirmed.add(3)
        if closed:
            active = max(active, 4)
        expected = 1 if task == 'finish' else 2
        if terminal and pastes >= expected:
            active = 5
            confirmed.add(4)
        if closed and not secondary:
            notice = 'Kein F9 während der Eingabe bestätigt; der Finish-Schritt bleibt offen.'
    elif task == 'cancel':
        if recording:
            active, confirmed = 3, {2}
        if secondary:
            active = 4
            if recording:
                confirmed.add(3)
        wait = observed.get('cancelWaitRemaining')
        if c.get('activation.cancelled') and wait == 0:
            active = 5
            confirmed.add(4)
    elif task == 'none':
        if secondary:
            active, confirmed = 3, {2}
            wait = observed.get('noneWaitRemaining')
            if wait == 0:
                active = 4
                confirmed.add(3)
        if terminal:
            active = 5
            if observed.get('closedReason') == 'timed_out':
                confirmed.add(4)
    elif task == 'feedback':
        if activated:
            active, confirmed = 3, {2}
        if closed:
            active = 4
            if observed.get('closedReason') == 'timed_out':
                confirmed.add(3)
            manual = True  # LED/sound/overlay perception is human-owned.
    elif task == 'usb':
        if observed.get('audioLost'):
            active, confirmed = 3, {2}
            wait = observed.get('usbWaitRemaining')
            if observed.get('audio') and observed.get('ready') and wait == 0:
                active, confirmed = 4, {2, 3}
                if secondary and terminal >= 2 and pastes:
                    active = 5
                    confirmed.add(4)
    elif task == 'reconnect':
        before = observed.get('reconnectGeneration')
        if before is not None:
            active, confirmed = 3, {2}
            if observed.get('generation', 0) > before and observed.get('ready') and observed.get('audio'):
                active, confirmed = 4, {2, 3}
                if terminal and pastes:
                    active = 5
                    confirmed.add(4)
    elif task == 'reinsert':
        if pastes >= 1:
            active, confirmed = 3, {2}
        if pastes >= 2:
            active, confirmed, manual = 4, {2, 3}, True
    if activated > 1 and task not in ('usb', 'mute'):
        notice += ' Mehrere Aktivierungen im Versuch; bitte bei der Auswertung berücksichtigen.'
    return dict(active=active, confirmed=sorted(confirmed), manualAllowed=manual,
                waitRemaining=wait, notice=notice.strip())
