"""Run with project Python outside checkout and PYTHONPATH=installation target."""

import hashlib
import importlib.util
from importlib.metadata import distribution
from pathlib import Path
import sys
import tempfile
import wave

import voice_stt_client
from voice_stt_client import app
from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
from voice_stt_client.ui.feedback import application_resource_root

target = Path(sys.argv[1]).resolve()
package = Path(voice_stt_client.__file__).resolve().parent
assert package.is_relative_to(target), package
assert importlib.util.find_spec("core") is None
assert importlib.util.find_spec("ui") is None
assert DEFAULT_CONFIG_PATH == package / "config.yaml"
assert application_resource_root() == package
assert voice_stt_client.__version__ == "1.0.0"
assert distribution("voice-stt-client").version == voice_stt_client.__version__
assert any(ep.name == "voice-stt-client" and ep.value == "voice_stt_client.app:main"
           for ep in distribution("voice-stt-client").entry_points)
with tempfile.TemporaryDirectory() as directory:
    config = AppConfig.load(user_path=Path(directory) / "missing.yaml")
    assert config.session.effective_manual_trigger_enabled
    assert not config.session.effective_wake_word_trigger_enabled
    assert "client.lifecycle.started" in config.feedback_mappings.events
sounds = sorted((package / "assets/feedback_sounds/debug").glob("*.wav"))
assert len(sounds) == 8, sounds
for sound in sounds:
    with wave.open(str(sound), "rb") as wav:
        assert wav.getnframes() > 0
assert (sounds[0].parent / "ATTRIBUTION.md").is_file()
assert app.main(["--verify-gui-runtime"]) == 0
print("PASS: installed namespace, config, all 8 WAVs, attribution, entrypoint, version, GUI imports")
for file in sorted(package.rglob("*")):
    if file.is_file() and file.suffix in {".py", ".yaml", ".wav", ".md"}:
        print(hashlib.sha256(file.read_bytes()).hexdigest(), file.relative_to(package))
