"""Real human WAV replay through production V2 transport/mirror and local ASR.

No microphone capture or Windows text injection. Raw recognized text is saved
only beside the deliberate WAVs outside Git; publish sanitized metrics separately.
Each sample gets a new session; no synthetic trigger substitutes for Wake mode.
"""
import argparse
import asyncio
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import wave

ROOT = next(p for p in Path(__file__).resolve().parents
            if (p / 'scripts/qualify_v2_session.py').is_file())
sys.path.insert(0, str(ROOT))
from observed_session import safe_event


async def one(path, mode, pre_roll):
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.settings_service import SettingsService
    with wave.open(str(path), 'rb') as handle:
        if (handle.getframerate(), handle.getnchannels(), handle.getsampwidth()) != (16000, 1, 2):
            raise ValueError('Real sample must be mono/16000Hz/int16')
        pcm = handle.readframes(handle.getnframes())
    metadata = json.loads(path.with_suffix('.json').read_text(encoding='utf8'))
    if metadata['sha256'] != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError('Sample identity mismatch')
    if not metadata['operatorInitiated'] or metadata['inputOverflow']:
        raise ValueError('Unqualified sample origin/capture')
    ids = ['hey_jarvis', 'alexa'] if mode == 'wake' else []
    profile = V2Profile(manual=mode == 'manual', wake_word=mode == 'wake',
                        wake_word_ids=ids, desired_settings={
                            'activation.followupTimeoutMs': 5000,
                            'wakeWord.preRollMs': pre_roll})
    session = V2STTSession(V2TransportConfig(url='ws://127.0.0.1:18020/ws/v2',
                          manual=profile.manual, wake_word=profile.wake_word,
                          wake_word_ids=tuple(ids)))
    mirror = V2MirrorConnection(session)
    settings = SettingsService(session, profile)

    async def bootstrap(client, binding):
        await settings.bootstrap(client, binding)
        await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY,
                                       audioAvailable=True)

    session.bootstrap = bootstrap
    events = []
    finals = []
    old_message = session.on_message

    def receive(binding, event):
        old_message(binding, event)
        record = safe_event(binding, event)
        record['monotonic'] = time.monotonic()
        events.append(record)

    session.on_message = receive
    previous = mirror.on_reduction

    def reduce(reduction):
        if previous:
            previous(reduction)
        for final in reduction.finals:
            finals.append(dict(activationId=final.activation_id, segmentId=final.segment_id,
                               text=final.text, eventSeq=final.event_seq,
                               monotonic=time.monotonic()))

    mirror.on_reduction = reduce
    task = asyncio.create_task(session.run())

    async def wait_ready():
        async with asyncio.timeout(60):
            while not session.is_ready or not mirror.mirror.view.operations_ready:
                if task.done():
                    await task
                    raise RuntimeError('Transport ended before ready')
                if session.status.state.value == 'blocked':
                    raise RuntimeError('Transport blocked: ' + session.status.reason)
                await asyncio.sleep(.02)

    try:
        await wait_ready()
        if session.binding.accepted.payload['serverCommit'] != 'ada13b011e1d3829f78e7f389e3b927795a2b3be':
            raise RuntimeError('Wrong server')
        if mode == 'manual':
            ack = await session.request(p.CommandType.ACTIVATION, action='activate', source='manual')
            if not ack.ack.accepted:
                raise RuntimeError('Manual baseline activation rejected')
        started = time.monotonic()
        data = pcm + b'\0' * (6 * 32000)
        for offset in range(0, len(data), 1280):
            chunk = data[offset:offset + 1280]
            if not await session.send_audio(chunk, 16000, 1, len(chunk) // 2,
                                            binding=session.binding):
                raise RuntimeError('Replay audio rejected')
            await asyncio.sleep(max(0, started + (offset + len(chunk)) / 32000 - time.monotonic()))
        await asyncio.sleep(.5)
        snapshot = settings.report()
        result = dict(case=metadata['case'], mode=mode, preRollMs=pre_roll,
                      audioSha256=metadata['sha256'], origin=metadata['origin'],
                      method='Real human recording replay; real local models/production V2 components; no live native paste',
                      replayStartedMonotonic=started, events=events, finals=finals,
                      recognizedText=''.join(f['text'] for f in finals),
                      expectedUserPhrase=metadata['expectedUserPhrase'],
                      expectedWakePhrase=metadata['expectedWakePhrase'],
                      desiredFollowupMs=5000,
                      effectiveFollowupMs=snapshot.effective.get('activation.followupTimeoutMs'),
                      pending=session.pending_count, generation=session.generation,
                      finalInputPhase=str(mirror.mirror.view.input.phase))
        print(json.dumps(dict(case=metadata['case'], mode=mode, preRollMs=pre_roll,
                              wakes=sum(e['type'] == 'wakeword.detected' for e in events),
                              finals=len(finals), characters=len(result['recognizedText']))), flush=True)
        return result
    finally:
        await session.stop()
        await mirror.close()
        await asyncio.gather(task, return_exceptions=True)


async def main(args):
    local = Path(os.environ['LOCALAPPDATA']) / 'VoiceSTT-Qualification/AP-IV2-020'
    os.environ['VOICESTT_CLIENT_HOME'] = str(local / 'client')
    audio = [p.resolve() for p in args.audio]
    output = args.out.resolve()
    fixture_root = Path(__file__).resolve().parent / 'samples'
    allowed_inputs = ((local / 'samples').resolve(), fixture_root)
    if not all(any(p.is_relative_to(root) for root in allowed_inputs) for p in audio):
        raise ValueError('Only deliberate local samples or authorized repository fixtures allowed')
    if not output.is_relative_to((local / 'samples').resolve()):
        raise ValueError('Raw recognized output must remain in the local samples directory')
    if not 0 <= args.pre_roll_ms <= 1000:
        raise ValueError('Qualification sweep limited to 0..1000ms pre-roll')
    output.parent.mkdir(parents=True, exist_ok=True)
    from scripts.qualify_v2_real import identity
    result = dict(timeUtc=datetime.now(UTC).isoformat(), identity=identity(),
                  helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), rows=[])
    for path in audio:
        row = await one(path, args.mode, args.pre_roll_ms)
        result['rows'].append(row)
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, action='append', required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--mode', choices=('manual', 'wake'), default='wake')
    parser.add_argument('--pre-roll-ms', type=int, default=0)
    asyncio.run(main(parser.parse_args()))
