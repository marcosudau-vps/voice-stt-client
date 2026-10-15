"""Run inside the isolated server container against /qualified, outside its code.

Observe actual ONNX prediction frames while calling the unchanged server's
calibration tool. Sweep the unchanged WakeHitTracker over those same measured
frames, without repeating inference or pretending replay is new human speech.
No raw audio/text or credentials are included in the resulting JSON.
"""
import argparse
import json
from pathlib import Path
import sys


def frame_record(frame):
    return dict(endSample=frame.end_sample,
                scores={str(k): float(v) for k, v in frame.scores.items()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', action='append', default=[])
    parser.add_argument('--out')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        from types import SimpleNamespace
        row = frame_record(SimpleNamespace(end_sample=1280, scores={'alexa': .75}))
        assert json.loads(json.dumps(row)) == dict(endSample=1280, scores={'alexa': .75})
        print('PASS: prediction-frame serializer only; no model/hardware claim')
        return
    if not args.audio or not args.out:
        parser.error('--audio and --out required')
    for path in [*args.audio, args.out]:
        if not Path(path).resolve().is_relative_to('/tmp/iv2-020-human'):
            parser.error('Only isolated /tmp/iv2-020-human inputs/outputs allowed')
    sys.path.insert(0, '/qualified')
    from tools import wakeword_calibration as calibration
    from VoiceSTT.core.wake_detection import WakeAttemptPolicy, WakeHitTracker
    from VoiceSTT.core.wake_audio_boundary import resolve_wake_audio_boundary
    original = calibration.load_backend
    observed = []

    def load_backend(*values, **options):
        engine = original(*values, **options)
        rows = []
        observed.append(rows)

        class ObservedEngine:
            def process(self, chunk):
                frames = list(engine.process(chunk))
                rows.extend(frame_record(frame) for frame in frames)
                return frames

            def close(self):
                engine.close()

        return ObservedEngine()

    calibration.load_backend = load_backend
    try:
        calibration.main(['scores', '--wake-words', 'hey_jarvis', '--wake-words', 'alexa',
                          *[v for p in args.audio for v in ('--audio', p)], '--out', args.out])
    finally:
        calibration.load_backend = original
    path = Path(args.out)
    result = json.loads(path.read_text(encoding='utf8'))
    assert len(observed) == len(result['traces'])
    for trace, frames in zip(result['traces'], observed):
        trace['measuredPredictionFrames'] = frames
        sweeps = []
        for sensitivity, count in ((.35, 1), (.5, 1), (.65, 1), (.5, 2)):
            policy = WakeAttemptPolicy(sensitivity=sensitivity,
                                       min_consecutive_prediction_frames=count)
            tracker = WakeHitTracker(policy_supplier=lambda: policy)
            hits = []
            for frame in frames:
                hit = tracker.observe(frame['scores'], end_sample=frame['endSample'])
                if hit is not None:
                    hits.append(dict(wakeWordId=hit.canonical_wake_word_id,
                        peakScore=hit.peak_score,
                        zeroPointSample=hit.operational_zero_point_sample,
                        releaseCandidates=[resolve_wake_audio_boundary(
                            operational_zero_point_sample=hit.operational_zero_point_sample,
                            pre_roll_ms=roll, sample_rate=16000).to_dict()
                            for roll in (0, 80, 160)]))
            sweeps.append(dict(sensitivity=sensitivity, minFrames=count,
                               hits=hits, logicalHitCount=len(hits)))
        trace['measuredFramePolicySweeps'] = sweeps
    result['method'] = ('Real selected ONNX models and unchanged server calibration tool; '
                        'passively recorded prediction frames, unchanged tracker policy sweeps. '
                        'No live microphone or new human repetitions; input WAV hashes supplied by host.')
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
