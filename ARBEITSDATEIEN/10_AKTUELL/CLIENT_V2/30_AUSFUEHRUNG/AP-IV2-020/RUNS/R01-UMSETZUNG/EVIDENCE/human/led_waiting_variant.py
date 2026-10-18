"""Check/apply the requested white ring variant to the isolated Both profile.

No hardware writes, server changes or product changes. Stop the owned client
before --apply; restart with the existing managed test-instance launcher.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0, str(ROOT))
LOCAL = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
os.environ['VOICESTT_CLIENT_HOME'] = str(LOCAL/'client')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    import yaml
    from lefx.engine.library import EffectLibrary
    from lefx.sdk import RenderContext, resolve_configuration, scale_color
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.event_models import CanonicalEventType
    from voice_stt_client.core.led_controller import _catalogue_directories

    path = LOCAL/'client-both.yaml'
    original = path.read_bytes()
    raw = yaml.safe_load(original)
    before = AppConfig.load(path)
    assert before.server.url == 'ws://127.0.0.1:18020/ws/v2'
    levels = [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1., 1., 1.]
    palette = [scale_color(0xFFFFFF, level) for level in levels]
    effect = {'set_state': 'palette_cycle', 'config': {
        'colors': [f'#{color:06X}' for color in palette],
        'brightness': 1.0, 'speed': 6.0, 'reverse': False}}
    modified = deepcopy(raw)
    events = modified.setdefault('feedback_mappings', {}).setdefault('events', {})
    keys = ('server.input.waiting', 'server.input.followup', 'server.input.idle')
    for key in keys:
        rule = before.feedback_mappings.rule_for(CanonicalEventType(key)).to_mapping()
        calls = rule['led'] if isinstance(rule['led'], list) else [rule['led']]
        states = [call for call in calls if 'set_state' in call]
        assert len(states) == 1
        if key.endswith('.idle'):
            assert states[0]['set_state'] == 'ready_state'
            states[0].setdefault('config', {})['color'] = '#FFFFFF'
        else:
            assert states[0]['set_state'] in ('waiting', 'palette_cycle')
            states[0].clear()
            states[0].update(deepcopy(effect))
        events[key] = rule

    library = EffectLibrary(search_paths=_catalogue_directories(before.led.effect_paths))
    try:
        registered = library.registry.get('palette_cycle')
        params = resolve_configuration(registered.definition, overrides=effect['config'])
        renderer = registered.effect_class()
        frames = []
        period = 4.0 / params['speed']
        for step in range(12):
            # Midstep avoids floating-point edge ambiguity at exact boundaries.
            elapsed = (step + .25) * period / 12
            frame = renderer.render(RenderContext(elapsed, 0, 12, registered.definition, params, {}))
            assert frame == palette[step:] + palette[:step], (step, frame)
            assert len(frame) == 12 and all(frame)
            frames.append(frame)
        assert len({tuple(frame) for frame in frames}) == 12
    finally:
        library.close()

    candidate = path.with_name('client-both-led-candidate.yaml')
    try:
        candidate.write_text(yaml.safe_dump(modified, allow_unicode=True, sort_keys=False), encoding='utf-8')
        after = AppConfig.load(candidate)
        previous = before.feedback_mappings.to_mapping()
        following = after.feedback_mappings.to_mapping()
        for key in keys:
            old_rule = previous['events'].pop(key)
            new_rule = following['events'].pop(key)
            old_rule.pop('led', None)
            new_rule.pop('led', None)
            assert old_rule == new_rule, key
        assert previous == following  # activation flash, sound, other phases preserved
        stripped_before, stripped_after = deepcopy(raw), deepcopy(modified)
        for stripped in (stripped_before, stripped_after):
            for key in keys:
                stripped['feedback_mappings']['events'].pop(key, None)
        assert stripped_before == stripped_after
        backup = None
        if args.apply:
            import ctypes
            from ctypes import wintypes
            active = json.loads((LOCAL/'active-session.json').read_text(encoding='utf-8'))
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            kernel.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.CloseHandle.argtypes = (wintypes.HANDLE,)
            handle = kernel.OpenProcess(0x1000, False, active['pid'])
            if handle:
                kernel.CloseHandle(handle)
                raise RuntimeError('Owned test client must be stopped first')
            assert ctypes.get_last_error() == 87, 'Cannot establish that owned process exited'
            assert path.read_bytes() == original, 'Profile changed during check'
            backup = LOCAL/('client-both.before-white-led-' + datetime.now().strftime('%Y%m%d-%H%M%S') + '.yaml')
            backup.write_bytes(original)
            os.replace(candidate, path)
        result = {
            'timeUtc': datetime.now(timezone.utc).isoformat(), 'result': 'PASS',
            'applied': args.apply, 'profileSha256Before': hashlib.sha256(original).hexdigest(),
            'profileSha256Candidate': hashlib.sha256(path.read_bytes() if args.apply else candidate.read_bytes()).hexdigest(),
            'backupLocalOnly': str(backup) if backup else None,
            'changedLedRules': keys, 'waitingLedCall': effect, 'brightnessLevels': levels,
            'frames': frames, 'rotationPeriodSeconds': period, 'rotationsPerSecond': 1/period,
            'globalBrightnessUnchanged': before.led.brightness, 'fpsUnchanged': before.led.fps,
            'activationFlashAndSoundsUnchanged': True, 'allOtherSettingsUnchanged': True,
            'boundaries': 'SDK render/config checks; no optical measurement or human acceptance. No color-profile implementation.'}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(json.dumps({k: result[k] for k in ('result', 'applied', 'rotationPeriodSeconds', 'globalBrightnessUnchanged')}))
    finally:
        candidate.unlink(missing_ok=True)


if __name__ == '__main__':
    main()
