"""Read-only packaging probe used by source, installed and frozen build gates.

No recording, paste, credential access or user configuration writes. The optional
loopback connection uses the production V2 transport/settings/mirror services.
"""
from __future__ import annotations

import asyncio
import hashlib
from importlib import resources
import json
from pathlib import Path
import sys
import wave
import tempfile
import time
import threading
from dataclasses import asdict
from urllib.parse import urlsplit

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
from voice_stt_client.core.version import BUILD_IDENTITY, __version__, __commit__
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig, V2TransportState


async def network_probe(url):
    from voice_stt_client.core.settings_service import SettingsService
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    # This packaging diagnostic must never connect to an arbitrary/live host.
    parts = urlsplit(url)
    if parts.scheme != 'ws' or parts.hostname not in ('127.0.0.1', 'localhost', '::1') or parts.path != '/ws/v2':
        raise ValueError('Packaging probe requires a loopback /ws/v2 endpoint')
    session = V2STTSession(V2TransportConfig(url=url))
    mirror = V2MirrorConnection(session)
    settings = SettingsService(session, V2Profile())
    async def bootstrap(client, binding):
        await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=False)
        await settings.bootstrap(client, binding)
    session.bootstrap = bootstrap
    task = asyncio.create_task(session.run())
    try:
        async def wait():
            while not session.is_ready:
                if task.done() or session.status.state == V2TransportState.BLOCKED:
                    raise RuntimeError('V2 probe blocked: ' + session.status.reason)
                await asyncio.sleep(.01)
        await asyncio.wait_for(wait(), 20)
        binding = session.binding
        snapshot = await session.request(p.CommandType.SNAPSHOT_REQUEST)
        if not snapshot.ack.accepted or not mirror.mirror.view.operations_ready:
            raise RuntimeError('V2 snapshot not confirmed')
        return dict(result='PASS', serverCommit=binding.accepted.payload['serverCommit'],
                    sessionId=binding.session_id, settingsRevision=mirror.mirror.view.settings_revision,
                    audioAvailable=False, snapshotAck=str(snapshot.ack.result))
    finally:
        await session.stop()
        await mirror.close()
        await asyncio.gather(task, return_exceptions=True)


def desktop_probe(url, qt, packaged_config):
    """Actual desktop/bridge/core with a deliberately invalid capture device.

    Uses native mutex/Qt, production services and temporary history/profile.
    No global key registration, physical audio capture, USB or text injection.
    """
    from copy import deepcopy
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.ui.v2_application import V2DesktopApplication
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    with tempfile.TemporaryDirectory(prefix='cv2-release-desktop-') as folder:
        config = deepcopy(packaged_config)
        config.server.url = url
        config.audio.device = 2147483647  # Explicitly nonexistent; never default mic.
        config.led.enabled = False
        config.feedback.sounds_enabled = False
        config.event_stream.enabled = False
        config.event_stream.cursor_persistence_enabled = False
        profile = V2Profile()
        profile.controls['enabled'] = False
        config.v2_profile = asdict(profile)
        config._config_source_path = Path(folder)/'profile.yaml'
        config._v2_migration_source = {'v2_profile': asdict(profile)}
        config.history.persistent.db_path = str(Path(folder)/'history.sqlite')
        guard = SingleInstanceGuard('Local\\CV2_release_probe_' + p.new_id())
        if not guard.acquire().acquired:
            raise RuntimeError('Native probe mutex failed')
        desktop = None
        try:
            desktop = V2DesktopApplication(qt, config, guard)
            if not desktop.start():
                raise RuntimeError('Actual V2 desktop did not start')
            deadline = time.monotonic() + 30
            while not desktop._runtime_ready:
                qt.processEvents()
                if time.monotonic() > deadline:
                    raise RuntimeError('Actual desktop bootstrap timed out')
                time.sleep(.01)
            desktop.show_settings()
            qt.processEvents()
            if not desktop.settings_dialog.isVisible():
                raise RuntimeError('Actual V2 settings did not show')
            runtime = desktop.bridge._controller
            identity = runtime.session.binding.accepted.payload['serverCommit']
            result = dict(result='PASS', serverCommit=identity, settingsVisible=True,
                settingsTabs=desktop.settings_dialog.tabs.count(),
                coreThreadSeparate=desktop.bridge.worker_thread_id != threading.get_ident(),
                audioAvailable=runtime.media.audio_available, audioCaptured=runtime.audio.is_running,
                globalKeysRegistered=bool(desktop.hotkeys._registered_ids))
            if result['audioCaptured'] or result['globalKeysRegistered'] or not result['coreThreadSeparate']:
                raise RuntimeError('Probe isolation or threading failed')
            desktop.shutdown()
            result['coreStopped'] = not desktop.bridge.is_running
            return result
        finally:
            if desktop is not None:
                desktop.shutdown()
            guard.release()


def run_probe(output: Path | None = None, server_url: str | None = None):
    from PySide6.QtCore import QUrl
    from PySide6.QtMultimedia import QAudioDecoder, QMediaDevices, QSoundEffect
    from PySide6.QtWidgets import QApplication
    from voice_stt_client.ui.feedback import resolve_sound_asset
    from voice_stt_client.ui.overlay import TranscriptOverlay
    from voice_stt_client.ui.settings_dialog import SettingsDialog
    from voice_stt_client.ui.tray import create_status_icon
    from voice_stt_client.ui.v2_application import V2DesktopApplication
    del V2DesktopApplication  # Import the entire actual composition, including native ports.

    qt = QApplication.instance() or QApplication([])
    audio_output_available = bool(QMediaDevices.audioOutputs())
    config = AppConfig._load_single(DEFAULT_CONFIG_PATH)
    overlay = TranscriptOverlay(config.overlay)
    dialog = SettingsDialog(config, lambda *_: False, v2_local=True, audio_devices=())
    sounds, effects = {}, []
    try:
        dialog.show()
        overlay.show_transcript('V2 packaging probe', False)
        qt.processEvents()
        if not dialog.isVisible() or not overlay.isVisible() or create_status_icon('#35c759').isNull():
            raise RuntimeError('Qt widgets/icon did not initialize')
        for name, value in vars(config.feedback).items():
            if name.endswith('_sound') and value:
                path = resolve_sound_asset(value)
                with wave.open(str(path), 'rb') as sound:
                    if sound.getnframes() <= 0:
                        raise RuntimeError('Empty sound asset')
                if audio_output_available:
                    effect = QSoundEffect()
                    effect.setSource(QUrl.fromLocalFile(str(path.resolve())))
                    effects.append(effect)
                else:
                    # A CI desktop may have no audio output. Decode the real
                    # asset through Qt instead of requiring playback hardware.
                    decoder = QAudioDecoder()
                    decoded = {'frames': 0, 'finished': False, 'error': False}
                    def read_buffer():
                        decoded['frames'] += decoder.read().frameCount()
                    decoder.bufferReady.connect(read_buffer)
                    decoder.finished.connect(lambda: decoded.update(finished=True))
                    decoder.error.connect(lambda *_: decoded.update(error=True))
                    decoder.setSource(QUrl.fromLocalFile(str(path.resolve())))
                    try:
                        decoder.start()
                        deadline = time.monotonic() + 10
                        while not (decoded['finished'] or decoded['error']) and time.monotonic() < deadline:
                            qt.processEvents()
                            time.sleep(.01)
                        if decoded['error'] or not decoded['finished'] or decoded['frames'] <= 0:
                            raise RuntimeError('Qt sound decoder failed: ' + decoder.errorString())
                    finally:
                        decoder.stop()
                        decoder.deleteLater()
                        qt.processEvents()
                sounds[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        # Loading uses Qt's real multimedia backend without audibly playing.
        deadline = time.monotonic() + 10
        while any(x.status() == QSoundEffect.Status.Loading for x in effects) and time.monotonic() < deadline:
            qt.processEvents()
            time.sleep(.01)
        if any(x.status() != QSoundEffect.Status.Ready for x in effects):
            raise RuntimeError('Qt sound assets failed to load')
        resource_hashes = {}
        for name in ('protocol-v2-vectors.json','protocol-v2-client-fixtures.json','protocol-v2-provenance.json'):
            content = resources.files('voice_stt_client').joinpath('resources', name).read_bytes()
            json.loads(content)
            resource_hashes[name] = hashlib.sha256(content).hexdigest()
        hello = p.build_hello(clientVersion=__version__, clientCommit=__commit__, clientRunId=p.new_id(),
            manual=True, wakeWord=False, wakeWordIds=[], suppressManual=True, suppressWakeWord=True)
        result = dict(result='PASS', version=__version__, buildIdentity=BUILD_IDENTITY,
            packageRoot=str(Path(__file__).resolve().parent), cwd=str(Path.cwd()),
            frozen=bool(getattr(sys, 'frozen', False)), configUrl=config.server.url,
            sounds=sounds, resources=resource_hashes, hello=hello.to_mapping(),
            gui=dict(platform=qt.platformName(), localTabs=dialog.tabs.count(), overlayVisible=overlay.isVisible(), icon=True,
                audioOutputAvailable=audio_output_available,
                soundLoadMode='QSoundEffect' if audio_output_available else 'QAudioDecoder',
                playbackTest='NOT_RUN'))
        if server_url:
            result['network'] = asyncio.run(network_probe(server_url))
            result['desktop'] = desktop_probe(server_url, qt, config)
        if output:
            Path(output).write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        return result
    finally:
        for effect in effects:
            effect.stop()
            effect.deleteLater()
        overlay.close()
        dialog.close()
        qt.processEvents()
