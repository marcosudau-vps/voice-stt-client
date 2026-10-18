"""Read-only real-model rearm probe inside the isolated pinned container.

Replay an authorized WAV up to first accepted hit. Emulate recorder gating
(no inference during activation), then release the real evaluator latch and
feed digital silence. No server/product files or running session are changed.
This isolates model-state retention; it cannot reconstruct past microphone PCM.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    for value in (args.audio, args.out):
        assert Path(value).resolve().is_relative_to('/tmp/iv2-020-human')
    sys.path.insert(0, '/qualified')
    from tools.wakeword_calibration import load_backend, read_wav
    from VoiceSTT.core.wakeword_catalog import WakeWordCatalogAuthority
    from VoiceSTT.core.wake_detection import WakeAttemptPolicy, WakeDetectionEvaluator

    authority = WakeWordCatalogAuthority()
    selection, errors = authority.admit_selection(['hey_jarvis', 'alexa'])
    assert not errors
    data = read_wav(Path(args.audio))
    rows = []
    for mode in ('retained_engine', 'reset_engine_control'):
        engine = load_backend(selection)
        policy = WakeAttemptPolicy(sensitivity=.5)
        evaluator = WakeDetectionEvaluator(engine=engine, policy_supplier=lambda: policy)
        try:
            first = None
            for offset in range(0, len(data) - 1280 + 1, 1280):
                hits = evaluator.process(data[offset:offset+1280], now=offset/32000)
                if hits:
                    first = hits[0]
                    evaluator.accept(first, activation_id='replay-first', now=offset/32000)
                    break
            assert first is not None, 'Fixture did not produce initial accepted hit'
            assert evaluator.release_latch(activation_id='replay-first')
            if mode == 'reset_engine_control':
                engine.reset()  # experimental control on this disposable engine only
            second = []
            maxima = {}
            silence = b'\0' * 1280  # 640 samples /40ms; no sound/voice replay
            for index in range(125):
                for frame in engine.process(silence):
                    for key, score in frame.scores.items():
                        maxima[key] = max(maxima.get(key, 0), float(score))
                    hit = evaluator.observe_scores(frame.scores, end_sample=frame.end_sample,
                                                   now=15+(index+1)*.04)
                    if hit:
                        second.append({'wakeWordId': hit.canonical_wake_word_id,
                                       'score': hit.peak_score,
                                       'silenceMsAfterRearm': (index+1)*40})
            rows.append({'mode': mode, 'firstWakeWordId': first.canonical_wake_word_id,
                         'firstScore': first.peak_score, 'silenceHits': second,
                         'silenceMaxScores': maxima})
        finally:
            engine.close()
    Path(args.out).write_text(json.dumps({
        'fixtureSha256': hashlib.sha256(Path(args.audio).read_bytes()).hexdigest(),
        'rows': rows,
        'boundary': 'Real pinned models/evaluator, recorded speech followed by synthetic digital silence; lifecycle gate emulated, no realtime wait. Not proof of historical acoustic cause; no live-server mutation.'
    }, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
