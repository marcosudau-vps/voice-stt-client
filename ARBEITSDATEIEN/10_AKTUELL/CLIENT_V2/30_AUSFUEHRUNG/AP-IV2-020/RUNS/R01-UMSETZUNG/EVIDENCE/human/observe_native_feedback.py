"""Passive QSoundEffect observations around the isolated managed test client.

No injected feedback decisions or synthetic success. Cue calls, native player
status and playing transitions only; no speech text or audio samples retained.
"""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from unittest.mock import patch
import explore_with_logging


def main():
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    os.environ['VOICESTT_CLIENT_HOME'] = str(local/'client')
    from voice_stt_client.ui.feedback import SoundFeedback
    folder = local/'feedback-probes'/datetime.now().strftime('%Y%m%d-%H%M%S')
    folder.mkdir(parents=True)
    trace = folder/'sound.jsonl'
    (local/'active-feedback-probe.json').write_text(json.dumps({
        'folder': str(folder), 'pid': os.getpid(),
        'helperSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}), encoding='utf-8')
    def emit(kind, **fields):
        with trace.open('a', encoding='utf-8') as handle:
            handle.write(json.dumps({'timeUtc': datetime.now(timezone.utc).isoformat(),
                                     'kind': kind, **fields})+'\n')
    original_effect = SoundFeedback._effect_for_cue
    original_play = SoundFeedback.play
    def observe_effect(adapter, cue):
        player = original_effect(adapter, cue)
        if not getattr(player, '_qualification_observed', False):
            player._qualification_observed = True
            player.playingChanged.connect(lambda: emit('playing', cue=cue.value,
                playing=player.isPlaying(), status=player.status().name))
            player.statusChanged.connect(lambda: emit('status', cue=cue.value,
                playing=player.isPlaying(), status=player.status().name))
        return player
    def observe_play(adapter, effect):
        result = original_play(adapter, effect)
        emit('cue', cue=effect.cue.value if effect else None,
             action=effect.action if effect else None, accepted=result)
        return result
    with patch.object(SoundFeedback, '_effect_for_cue', observe_effect), \
         patch.object(SoundFeedback, 'play', observe_play):
        return explore_with_logging.main()


if __name__ == '__main__':
    raise SystemExit(main())
