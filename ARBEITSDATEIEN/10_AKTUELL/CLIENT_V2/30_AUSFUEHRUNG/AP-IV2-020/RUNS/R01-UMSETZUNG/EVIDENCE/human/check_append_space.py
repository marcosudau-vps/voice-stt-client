"""Focused red reproduction for UX01, using the real queue and fake Win32 I/O.

No product changes, native clipboard writes or text injection. Exit1 when the
configured append_space preference is demonstrably ignored. This is intentionally
a red finding proof, not a claimed passing product regression.
"""
import argparse
import difflib
import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import time

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'scripts/qualify_v2_session.py').is_file())
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--proposed-patch', type=Path)
    parser.add_argument('--preview-candidate', action='store_true')
    args = parser.parse_args()
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.history import TranscriptHistoryManager
    from voice_stt_client.core.text_injector import TextInjectionQueue, InjectionJob
    from tests.test_text_injector import MockInjectionBackend
    path = ROOT / 'voice_stt_client/core/text_injector.py'
    original_source = path.read_text(encoding='utf8')
    already_fixed = 'self.backend.set_clipboard_data_unicode(payload_text)' in original_source
    if already_fixed and (args.preview_candidate or args.proposed_patch):
        parser.error('Historical proposal/preview requires the pre-fix product; run the normal check on fixed code')
    candidate = original_source.replace('        restore_cfg = self.config.clipboard\n',
        '        payload_text = job.text\n'
        '        if self.config.text_injection.append_space and not payload_text[-1].isspace():\n'
        '            payload_text += " "\n\n'
        '        restore_cfg = self.config.clipboard\n', 1)
    candidate = candidate.replace('self.backend.set_clipboard_data_unicode(job.text)',
                                  'self.backend.set_clipboard_data_unicode(payload_text)', 1)
    if args.preview_candidate:
        import types
        module = types.ModuleType('voice_stt_client.core._qualification_append_space_preview')
        sys.modules[module.__name__] = module
        exec(compile(candidate, '<unapplied-UX01-preview>', 'exec'), module.__dict__)
        TextInjectionQueue = module.TextInjectionQueue
        InjectionJob = module.InjectionJob
    cases = []
    for enabled, original, expected in ((True, 'Alpha.', 'Alpha. '),
                                        (False, 'Alpha.', 'Alpha.'),
                                        (True, 'Alpha. ', 'Alpha. '),
                                        (True, 'Alpha.\n', 'Alpha.\n')):
        config = AppConfig()
        config.text_injection.append_space = enabled
        config.text_injection.paste_delay_ms = 0
        config.clipboard.restore_previous = False
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        backend = MockInjectionBackend()
        backend.create_owner_window()
        queue = TextInjectionQueue(config, history, backend)
        job = InjectionJob('test-job', 'test-entry', original, time.time())
        try:
            status, error, _ = queue._process_job(job)
            cases.append(dict(appendSpace=enabled, original=original, expected=expected,
                              actual=backend.clipboard_data, status=status,
                              immutableJobPreserved=job.text == original,
                              result='PASS' if backend.clipboard_data == expected else 'FAIL'))
        finally:
            backend.destroy_owner_window()
    result = dict(finding='IV2-020-UX01', cases=cases,
                  productCommit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  sourceHead=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
                  boundary='Actual queue payload path; fake Win32 boundary; no native side effects',
                  unappliedCandidatePreview=args.preview_candidate,
                  result='FAIL' if any(c['result'] == 'FAIL' for c in cases) else 'PASS')
    args.out.write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    if args.proposed_patch:
        args.proposed_patch.write_text(''.join(difflib.unified_diff(
            original_source.splitlines(keepends=True), candidate.splitlines(keepends=True),
            fromfile='a/voice_stt_client/core/text_injector.py',
            tofile='b/voice_stt_client/core/text_injector.py')), encoding='utf8', newline='\n')
    print(json.dumps(dict(result=result['result'], cases=len(cases),
                          failed=sum(c['result'] == 'FAIL' for c in cases))))
    return result['result'] != 'PASS'


if __name__ == '__main__':
    raise SystemExit(main())
