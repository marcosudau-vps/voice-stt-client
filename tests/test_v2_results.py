"""AP060: real SQLite and serial injection worker, controlled OS boundary."""
from dataclasses import replace
from contextlib import closing
import asyncio
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import ActivationMirror, FinalResult, Reduction
from voice_stt_client.core.config import AppConfig, HistoryConfig, HistoryPersistentConfig
from voice_stt_client.core.final_results import V2ResultService
from voice_stt_client.core.history import HistoryAddStatus, TranscriptHistoryManager
from voice_stt_client.core.reinsertion import TranscriptReinsertionService
from voice_stt_client.core.text_injector import TextInjectionQueue, QueueState
from tests.test_text_injector import MockInjectionBackend
from tests.test_v2_mirror import A, B, S, snapshot, msg
from tests.test_v2_protocol import IDS


def make_v1(path):
    with closing(sqlite3.connect(path)) as conn:
        conn.executescript('''
            PRAGMA foreign_keys=ON;
            CREATE TABLE history_entries (id TEXT PRIMARY KEY,session_id TEXT,segment_id INTEGER,
                timestamp REAL,text TEXT,text_length INTEGER,UNIQUE(session_id,segment_id));
            CREATE TABLE injection_attempts (id TEXT PRIMARY KEY,entry_id TEXT,status TEXT,error TEXT,timestamp REAL,
                FOREIGN KEY(entry_id) REFERENCES history_entries(id) ON DELETE CASCADE);
            INSERT INTO history_entries VALUES ('legacy-entry','legacy-session',42,123.25,'ä preserved',11);
            INSERT INTO injection_attempts VALUES ('legacy-attempt','legacy-entry','command_sent',NULL,124.75);
        ''')


class Migration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name)/'history.sqlite'
        self.config = HistoryConfig(persistent=HistoryPersistentConfig(enabled=True, store_all=True,
                                                                      retention_days=0, max_entries=0))

    def test_v1_backup_ids_attempts_origin_and_second_start_idempotent(self):
        make_v1(self.db)
        original = self.db.read_bytes()
        manager = TranscriptHistoryManager(self.config, str(self.db))
        entry = manager.get_persistent_entries()[0]
        self.assertEqual((entry.id, entry.session_id, entry.segment_id, entry.text, entry.timestamp),
                         ('legacy-entry','legacy-session',42,'ä preserved',123.25))
        self.assertEqual((entry.protocol_version, entry.activation_id, entry.segment_sequence,
                          entry.event_id, entry.event_seq, entry.primary_source, entry.activation_sequence),
                         (1, None, None, None, None, None, None))
        self.assertEqual((entry.attempts[0].id,entry.attempts[0].entry_id,entry.attempts[0].status,
                          entry.attempts[0].timestamp,entry.attempts[0].error),
                         ('legacy-attempt','legacy-entry','command_sent',124.75,None))
        backup = manager.migration_backup
        with closing(sqlite3.connect(backup)) as conn:
            self.assertEqual(conn.execute('SELECT segment_id,text FROM history_entries').fetchall(),[(42,'ä preserved')])
            self.assertEqual(conn.execute('SELECT id,status FROM injection_attempts').fetchall(),[('legacy-attempt','command_sent')])
        backup_bytes=backup.read_bytes()
        before = self.db.read_bytes()
        again = TranscriptHistoryManager(self.config,str(self.db))
        self.assertEqual(self.db.read_bytes(),before)
        self.assertEqual(again.get_persistent_entries(),manager.get_persistent_entries())
        self.assertEqual(backup.read_bytes(),backup_bytes)
        self.assertEqual(manager.add_entry_with_status('legacy-session',42,'duplicate').status,
                         HistoryAddStatus.ALREADY_EXISTS)

    def test_mid_migration_ddl_failure_rolls_back_and_retry_uses_backup(self):
        make_v1(self.db)
        original = TranscriptHistoryManager._migrate_v1
        class FailingConnection:
            def __init__(self,conn): self.conn=conn
            def __getattr__(self,name): return getattr(self.conn,name)
            def execute(self,sql,*args):
                if sql.startswith('INSERT INTO injection_attempts'):
                    raise sqlite3.OperationalError('synthetic migration failure')
                return self.conn.execute(sql,*args)
        with patch.object(TranscriptHistoryManager,'_migrate_v1',
                          lambda self,conn: original(self,FailingConnection(conn))):
            with self.assertLogs('text',level='ERROR'):
                failed=TranscriptHistoryManager(self.config,str(self.db))
        self.assertFalse(failed._db_enabled)
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('SELECT * FROM history_entries').fetchone()[2],42)
            self.assertEqual(conn.execute('SELECT id FROM injection_attempts').fetchone()[0],'legacy-attempt')
            self.assertNotIn('protocol_version',{r[1] for r in conn.execute('PRAGMA table_info(history_entries)')})
            self.assertEqual(conn.execute('PRAGMA foreign_key_check').fetchall(),[])
        self.assertTrue(TranscriptHistoryManager(self.config,str(self.db))._db_enabled)

    def test_uuid_origin_unique_and_fk_survive_reopen(self):
        make_v1(self.db)
        history=TranscriptHistoryManager(self.config,str(self.db))
        entry=history.add_entry_with_status(IDS['sessionId'], S, 'v2 text', protocol_version=2,
            activation_id=A, segment_sequence=8, event_id=IDS['eventId'],event_seq=21,
            primary_source='wake_word',activation_sequence=3).entry
        attempt=history.reserve_injection(entry,'automatic')
        history.finish_injection(attempt.id,'command_sent')
        again=TranscriptHistoryManager(self.config,str(self.db))
        persisted=next(e for e in again.get_persistent_entries() if e.protocol_version==2)
        self.assertEqual(persisted,entry)
        self.assertEqual((persisted.activation_id,persisted.segment_sequence,persisted.event_id,
                          persisted.event_seq,persisted.primary_source,persisted.activation_sequence),
                         (A,8,IDS['eventId'],21,'wake_word',3))
        with history._db_session() as conn:
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute('INSERT INTO injection_attempts (id,entry_id,status) VALUES (?,?,?)',('bad','absent','pending'))
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute('INSERT INTO history_entries (id,session_id,segment_id,protocol_version) VALUES (?,?,?,?)',
                             ('dup',IDS['sessionId'],S,2))
        history.delete_entry(entry.id)
        with history._db_session() as conn:
            self.assertEqual(conn.execute('SELECT id FROM injection_attempts').fetchall()[0][0],'legacy-attempt')

    def test_future_schema_is_preserved(self):
        make_v1(self.db)
        with closing(sqlite3.connect(self.db)) as conn: conn.execute('PRAGMA user_version=99')
        before=self.db.read_bytes()
        with self.assertLogs('text',level='ERROR'):
            manager=TranscriptHistoryManager(self.config,str(self.db))
        self.assertFalse(manager._db_enabled)
        self.assertEqual(self.db.read_bytes(),before)

    def test_failed_backup_never_migrates_or_leaves_partial_backup(self):
        # Exercise a path alias: History resolves it, as it does Windows 8.3 temp names.
        (self.db.parent/'alias').mkdir()
        self.db = self.db.parent/'alias'/'..'/self.db.name
        make_v1(self.db)
        original=sqlite3.connect
        class BackupFailure:
            def __init__(self,conn): self.conn=conn
            def __getattr__(self,name): return getattr(self.conn,name)
            def backup(self,destination): raise sqlite3.OperationalError('synthetic full backup disk')
        def connection(*args,**kwargs):
            conn=original(*args,**kwargs)
            return BackupFailure(conn) if Path(args[0]).resolve()==self.db.resolve() else conn
        with patch('sqlite3.connect',side_effect=connection),self.assertLogs('text',level='ERROR'):
            failed=TranscriptHistoryManager(self.config,str(self.db))
        self.assertFalse(failed._db_enabled)
        self.assertFalse(self.db.with_name(self.db.name+'.v1-backup.sqlite').exists())
        self.assertEqual(list(self.db.parent.glob('*.backup-tmp')),[])
        with closing(sqlite3.connect(self.db)) as conn:
            self.assertEqual(conn.execute('SELECT segment_id FROM history_entries').fetchone()[0],42)
        self.assertTrue(TranscriptHistoryManager(self.config,str(self.db))._db_enabled)


class Results(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db=Path(self.tmp.name)/'history.sqlite'
        self.config=AppConfig()
        self.config.history.persistent=HistoryPersistentConfig(enabled=True,store_all=True,max_entries=0,retention_days=0)
        self.config.text_injection.paste_delay_ms=0
        self.config.clipboard.restore_delay_ms=0
        self.history=TranscriptHistoryManager(self.config.history,str(self.db))
        self.backend=MockInjectionBackend()
        self.queue=TextInjectionQueue(self.config,self.history,self.backend)
        self.queue.start()
        self.addCleanup(lambda: self.queue.stop(timeout=2))
        self.service=V2ResultService(self.history,self.queue)
        self.mirror=ActivationMirror()
        self.service.consume(self.mirror.begin(1,snapshot(),1))
        self.seq=0

    def send(self,kind,**fields):
        self.seq+=1
        reduction=self.mirror.consume(1,msg(kind,self.seq,**fields),1)
        return reduction,self.service.consume(reduction)

    def drain(self):
        self.queue._queue.join()

    def test_delayed_A_final_during_B_keeps_every_origin_and_pastes_once(self):
        self.send(p.EventType.ACTIVATION_STARTED,primarySource='wake_word')
        self.send(p.EventType.RECORDING_STARTED)
        self.send(p.EventType.INPUT_CLOSED)
        self.send(p.EventType.ACTIVATION_STARTED,aid=B,activationSequence=2)
        reduction,outcomes=self.send(p.EventType.COMPLETED,text=' late A ')
        self.drain()
        self.assertEqual(outcomes[0].status,'queued')
        entry=self.history.get_persistent_entries()[0]
        final=reduction.finals[0]
        self.assertEqual((entry.session_id,entry.activation_id,entry.segment_id,entry.segment_sequence,
                          entry.event_id,entry.event_seq,entry.primary_source),
                         (final.session_id,A,S,1,final.event_id,final.event_seq,'wake_word'))
        self.assertEqual(entry.text,' late A ')
        self.assertEqual(self.mirror.view.input.activation_id,B)
        self.service.consume(reduction)
        self.send(p.EventType.COMPLETED,text='contradictory')
        self.drain()
        self.assertEqual(len(self.backend.send_input_calls),1)
        self.assertEqual(len(entry.attempts),1)
        self.assertEqual((entry.attempts[0].status,entry.attempts[0].source),('command_sent','automatic'))

    def test_interim_stable_fields_have_no_history_reservation_or_clipboard_effect(self):
        with patch.object(self.history,'add_entry_with_status',wraps=self.history.add_entry_with_status) as add, \
             patch.object(self.history,'reserve_injection',wraps=self.history.reserve_injection) as reserve:
            for i in range(6):
                self.send(p.EventType.INTERIM,text='preview',stableDelta='stable',committedStableText='committed')
            self.assertEqual(add.call_count,0)
            self.assertEqual(reserve.call_count,0)
        self.assertEqual(self.history.get_memory_entries(),[])
        self.assertEqual(self.backend.set_calls,[])
        self.assertEqual(self.backend.send_input_calls,[])

    def test_first_discard_failed_empty_then_completed_and_late_interim_never_paste(self):
        for i,kind in enumerate((p.EventType.DISCARDED,p.EventType.FAILED,p.EventType.COMPLETED),1):
            sid=p.new_id()
            self.send(kind,sid=sid,segment_sequence=i,text='   ')
            self.send(p.EventType.COMPLETED,sid=sid,segment_sequence=i,text='late')
            self.send(p.EventType.INTERIM,sid=sid,segment_sequence=i,text='later')
            self.send(p.EventType.RECORDING_ENDED,sid=sid,segment_sequence=i)
        self.drain()
        self.assertEqual(self.history.get_memory_entries(),[])
        self.assertEqual(self.backend.send_input_calls,[])

    def test_identical_texts_different_segments_are_not_deduplicated(self):
        for i in range(1,4):
            self.send(p.EventType.COMPLETED,sid=p.new_id(),segment_sequence=i,text='same')
        self.drain()
        self.assertEqual([e.segment_sequence for e in self.history.get_persistent_entries()],[1,2,3])
        self.assertEqual(len(self.backend.send_input_calls),3)

    def test_history_off_keeps_process_dedup_and_outputs(self):
        self.history.config.enabled=False
        reduction,_=self.send(p.EventType.COMPLETED,text='with history off')
        for _ in range(4): self.service.consume(reduction)
        self.drain()
        self.assertEqual(len(self.backend.send_input_calls),1)
        self.assertEqual(self.history.get_memory_entries(),[])
        self.assertEqual(self.history.get_persistent_entries(),[])

    def test_concurrent_reduction_delivery_and_eviction_do_not_repeat_effect(self):
        reduction,_=self.send(p.EventType.COMPLETED,text='original')
        self.drain()
        self.history.clear_entries()
        threads=[threading.Thread(target=self.service.consume,args=(reduction,)) for _ in range(12)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(2); self.assertFalse(thread.is_alive())
        self.drain()
        self.assertEqual(len(self.backend.send_input_calls),1)

    def test_gap_salvage_publication_order_and_snapshot_never_infers_text(self):
        # Receive two finals backwards; snapshot repair publishes in server event order.
        self.service.consume(self.mirror.consume(1,msg(p.EventType.COMPLETED,3,sid=p.new_id(),segment_sequence=2,text='second'),1))
        self.service.consume(self.mirror.consume(1,msg(p.EventType.COMPLETED,2,text='first'),1))
        outcomes=self.service.consume(self.mirror.consume(1,snapshot(seq=3,version=3),1))
        self.drain()
        self.assertEqual([o.final.text for o in outcomes],['first','second'])
        self.assertEqual(self.backend.set_calls,['first','second'])
        self.service.consume(self.mirror.consume(1,snapshot(seq=3,version=3),1))
        self.drain()
        self.assertEqual(len(self.backend.send_input_calls),2)

    def test_cancel_disconnect_and_recovery_preserve_published_text(self):
        reduction,_=self.send(p.EventType.COMPLETED,text='preserved')
        self.drain()
        before=self.history.get_persistent_entries()
        self.send(p.EventType.ACTIVATION_CANCELLED)
        self.service.consume(self.mirror.disconnect(1))
        new=snapshot().to_mapping(); new['sessionId']=p.new_id()
        self.service.consume(self.mirror.begin(2,p.parse_snapshot(new),1))
        self.assertEqual(self.service.consume(reduction),())
        self.assertEqual(self.history.get_persistent_entries(),before)
        self.assertEqual(len(self.backend.send_input_calls),1)

    def test_cancelled_activation_unpublished_final_is_suppressed(self):
        self.send(p.EventType.ACTIVATION_CANCELLED)
        self.send(p.EventType.COMPLETED,text='never published')
        self.drain()
        self.assertEqual(self.backend.send_input_calls,[])

    def test_wrong_session_or_forged_identity_cannot_reach_output(self):
        reduction=self.mirror.consume(1,msg(p.EventType.COMPLETED,1,text='legit'),1)
        altered=replace(reduction.finals[0],activation_id=p.new_id())
        self.assertEqual(self.service.consume(replace(reduction,finals=(altered,))),())
        wrong_session=replace(reduction,view=replace(reduction.view,session_id=p.new_id()))
        self.assertEqual(self.service.consume(wrong_session),())
        self.assertEqual(self.backend.send_input_calls,[])

    def test_reinsert_has_separate_manual_attempt_and_clipboard_restore(self):
        self.config.clipboard.restore_previous=True
        self.backend.clipboard_data='backup'
        self.send(p.EventType.COMPLETED,text='automatic')
        self.drain()
        entry=self.history.get_persistent_entries()[0]
        result=TranscriptReinsertionService(self.history,self.queue).reinsert_entry(entry.id)
        self.assertEqual(result.status.value,'queued')
        self.drain()
        current=self.history.get_persistent_entries()[0]
        self.assertEqual([a.source for a in current.attempts],['automatic','manual'])
        self.assertEqual([a.status for a in current.attempts],['command_sent','command_sent'])
        self.assertEqual(self.backend.clipboard_data,'backup')

    def test_reservation_committed_before_clipboard_and_send_input(self):
        old=self.backend.set_clipboard_data_unicode
        observed=[]
        def clipboard(text):
            entry=self.history.get_persistent_entries()[0]
            observed.append(entry.attempts[0].status)
            return old(text)
        self.backend.set_clipboard_data_unicode=clipboard
        self.send(p.EventType.COMPLETED,text='reserved')
        self.drain()
        self.assertEqual(observed,['pending'])

    def test_sqlite_reservation_failure_is_visible_no_paste_mirror_keeps_running(self):
        outcomes=[]; self.service.on_result=outcomes.append
        with patch.object(self.history,'_get_connection',side_effect=sqlite3.OperationalError('synthetic SQLite outage')):
            with self.assertLogs('text',level='ERROR'):
                self.send(p.EventType.COMPLETED,text='retained in memory')
        self.assertEqual(outcomes[0].reason,'injection_reservation_failed')
        self.assertEqual(len(self.history.get_memory_entries()),1)
        self.assertTrue(self.mirror.view.operations_ready)
        self.send(p.EventType.COMPLETED,sid=p.new_id(),segment_sequence=2,text='next works')
        self.drain()
        self.assertEqual(len(self.backend.send_input_calls),1)

    def test_sqlite_outcome_failure_unknown_and_no_retry(self):
        callback=[]; self.service.on_attempt_result=callback.append
        old_finish=self.history.finish_injection
        def fail_commit(*args):
            with patch.object(self.history,'_get_connection',side_effect=sqlite3.OperationalError('outcome failure')):
                return old_finish(*args)
        self.history.finish_injection=fail_commit
        with self.assertLogs('text',level='ERROR'):
            reduction,_=self.send(p.EventType.COMPLETED,text='pasted once')
            self.drain()
        self.assertEqual(callback[0].status,'unknown')
        self.service.consume(reduction); self.drain()
        restarted=TranscriptHistoryManager(self.config.history,str(self.db))
        self.assertEqual(restarted.get_persistent_entries()[0].attempts[0].status,'unknown')
        self.assertEqual(len(self.backend.send_input_calls),1)

    def test_clipboard_failure_does_not_block_later_segment(self):
        self.backend.set_fail=True
        self.send(p.EventType.COMPLETED,text='first failure'); self.drain()
        self.backend.set_fail=False
        self.send(p.EventType.COMPLETED,sid=p.new_id(),segment_sequence=2,text='later succeeds'); self.drain()
        self.assertEqual([e.attempts[0].status for e in self.history.get_persistent_entries()],['failed','command_sent'])
        self.assertEqual(len(self.backend.send_input_calls),1)

    def test_queue_unavailable_and_service_close_have_no_external_effect(self):
        self.queue.stop(2)
        _,outcomes=self.send(p.EventType.COMPLETED,text='not enqueued')
        self.assertEqual(outcomes[0].reason,'queue_unavailable')
        self.assertEqual(self.history.get_persistent_entries()[0].attempts,[])
        self.service.close()
        self.send(p.EventType.COMPLETED,sid=p.new_id(),segment_sequence=2,text='closed')
        self.assertEqual(len(self.history.get_persistent_entries()),1)

    def test_disconnected_same_generation_stale_reduction_is_rejected(self):
        reduction=self.mirror.consume(1,msg(p.EventType.COMPLETED,1,text='not yet consumed'),1)
        self.service.consume(self.mirror.disconnect(1))
        self.assertEqual(self.service.consume(reduction),())
        self.assertEqual(self.history.get_memory_entries(),[])

    def test_retention_preserves_pending_attempt_until_outcome(self):
        self.history.config.persistent.max_entries=1
        entry=self.history.add_entry_with_status(IDS['sessionId'],S,'pending',timestamp=1,protocol_version=2).entry
        attempt=self.history.reserve_injection(entry,'automatic')
        self.history.add_entry(IDS['sessionId'],1,'newer',timestamp=2)
        self.assertIn(entry.id,[e.id for e in self.history.get_persistent_entries()])
        self.history.finish_injection(attempt.id,'command_sent')
        self.history.cleanup()
        self.assertNotIn(entry.id,[e.id for e in self.history.get_persistent_entries()])

    def test_explicit_history_deletion_during_reserved_job_does_not_resurrect_text(self):
        entry=self.history.add_entry(IDS['sessionId'],42,'explicitly deleted')
        attempt=self.history.reserve_injection(entry,'manual')
        self.history.delete_entry(entry.id)
        self.history.finish_injection(attempt.id,'command_sent')
        self.assertEqual(self.history.get_persistent_entries(),[])
        self.assertEqual(self.history.get_memory_entries(),[])

    def test_filtered_history_failure_attempt_preserves_v2_origin(self):
        self.history.config.persistent.store_all=False
        self.history.config.persistent.min_characters=100
        self.backend.set_fail=True
        self.send(p.EventType.COMPLETED,text='short'); self.drain()
        entry=self.history.get_persistent_entries()[0]
        self.assertEqual((entry.protocol_version,entry.activation_id,entry.segment_id),(2,A,S))
        self.assertEqual(entry.attempts[0].status,'failed')

    def test_legacy_reinsert_reserves_manual_source(self):
        entry=self.history.add_entry('v1-session',42,'legacy reinsert')
        result=TranscriptReinsertionService(self.history,self.queue).reinsert_entry(entry.id)
        self.drain()
        self.assertEqual(result.status.value,'queued')
        self.assertEqual(self.history.get_persistent_entries()[0].attempts[0].source,'manual')

    def test_callback_exceptions_do_not_break_reduction_or_worker(self):
        def fail(_): raise RuntimeError('synthetic callback failure')
        self.service.on_result=self.service.on_attempt_result=fail
        with self.assertLogs('text',level='ERROR'):
            self.send(p.EventType.COMPLETED,text='first'); self.drain()
            self.send(p.EventType.COMPLETED,sid=p.new_id(),segment_sequence=2,text='second'); self.drain()
        self.assertEqual(len(self.backend.send_input_calls),2)

    def test_controller_port_attaches_once_preserves_legacy_cancel_and_shutdown_guard(self):
        from voice_stt_client.core.controller import STTController
        from voice_stt_client.core.v2_transport import V2STTSession
        from voice_stt_client.core.v2_mirror import V2MirrorConnection
        from tests.test_controller import FakeAudioCapture,FakeSTTSession
        controller=STTController(self.config,session=FakeSTTSession(),audio=FakeAudioCapture(),
                                 history_manager=self.history,injection_queue=self.queue)
        connection=V2MirrorConnection(V2STTSession())
        observed=[]; connection.on_reduction=observed.append
        service=controller.attach_v2_results(connection)
        with self.assertRaises(RuntimeError): controller.attach_v2_results(connection)
        callbacks=[]; controller.on_final_result=callbacks.append
        controller._discard_finals=True
        connection._publish(connection.mirror.begin(1,snapshot(),1))
        reduction=connection.mirror.consume(1,msg(p.EventType.COMPLETED,1,text='V2 delivered'),1)
        connection._publish(reduction); self.drain()
        self.assertEqual(len(observed),2)
        self.assertEqual((callbacks[0].activation_id,callbacks[0].segment_id,callbacks[0].generation),(A,S,1))
        self.assertEqual(len(self.backend.send_input_calls),1)
        current=snapshot().to_mapping(); current['sessionId']=p.new_id()
        connection._publish(connection.mirror.begin(2,p.parse_snapshot(current),1))
        self.assertEqual(service.consume(reduction),())
        new_event=msg(p.EventType.COMPLETED,1,sid=p.new_id(),text='new generation').to_mapping()
        new_event['sessionId']=current['sessionId']
        connection._publish(connection.mirror.consume(2,p.decode_server_message(new_event),1))
        self.drain()
        self.assertEqual(len(self.backend.send_input_calls),2)
        asyncio.run(controller.shutdown())
        self.assertEqual(service.consume(reduction),())


class CrashRecovery(unittest.TestCase):
    def test_real_process_crash_at_five_boundaries_never_auto_reinjects(self):
        for point,status in (('before_reserve',None),('after_reserve','unknown'),
                             ('paste','unknown'),('after_paste','unknown'),('after_status','command_sent')):
            with self.subTest(point=point),tempfile.TemporaryDirectory() as tmp:
                db=Path(tmp)/'history.sqlite'
                result=subprocess.run([sys.executable,'-m','tests.test_v2_results','--crash',str(db),point],
                                      capture_output=True,text=True,timeout=15)
                self.assertEqual(result.returncode,71,result.stderr)
                config=AppConfig(); config.history.persistent=HistoryPersistentConfig(enabled=True,store_all=True)
                history=TranscriptHistoryManager(config.history,str(db))
                entries=history.get_persistent_entries()
                self.assertEqual(len(entries),1)
                self.assertEqual(entries[0].attempts[0].status if entries[0].attempts else None,status)
                backend=MockInjectionBackend(); queue=TextInjectionQueue(config,history,backend)
                queue.start()
                try:
                    mirror=ActivationMirror(); service=V2ResultService(history,queue)
                    service.consume(mirror.begin(1,snapshot(),1))
                    outcome=service.consume(mirror.consume(1,msg(p.EventType.COMPLETED,1,text='crash fixture'),1))
                    self.assertEqual(outcome[0].status,'deduplicated')
                    queue._queue.join()
                    self.assertEqual(backend.send_input_calls,[])
                finally: queue.stop(2)


def crash_probe(db,point):
    config=AppConfig(); config.history.persistent=HistoryPersistentConfig(enabled=True,store_all=True)
    config.text_injection.paste_delay_ms=config.clipboard.restore_delay_ms=0
    history=TranscriptHistoryManager(config.history,db)
    # IDs from committed fixture stay identical in the restarted process.
    entry=history.add_entry_with_status(IDS['sessionId'],S,'crash fixture',protocol_version=2,
        activation_id=IDS['activationId'],segment_sequence=1,event_id=IDS['eventId'],event_seq=1).entry
    if point=='before_reserve': os._exit(71)
    backend=MockInjectionBackend(); queue=TextInjectionQueue(config,history,backend)
    if point=='after_reserve':
        queue._state=QueueState.RUNNING; queue.enqueue_reserved(entry); os._exit(71)
    if point=='paste': backend.send_input_keyboard=lambda events: os._exit(71)
    if point=='after_paste': history.finish_injection=lambda *args: os._exit(71)
    if point=='after_status': queue.on_attempt_result=lambda attempt: os._exit(71)
    queue.start(); queue.enqueue_reserved(entry); queue._queue.join()
    raise AssertionError('Crash boundary was not reached')


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--crash': crash_probe(sys.argv[2],sys.argv[3])
    else: unittest.main()
