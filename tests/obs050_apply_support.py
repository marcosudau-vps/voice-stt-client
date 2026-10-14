"""Logging preference regression fixtures against the actual V2Runtime."""
import tempfile
import shutil
from pathlib import Path
from voice_stt_client.core.v2_runtime import V2Runtime
from tests.test_v2_runtime_integration import config_in
from tests.test_text_injector import MockInjectionBackend

class RecordingIngress:
    """An ``Ingress`` double that records what ``apply_config`` received."""

    def __init__(self, *, raises: bool = False) -> None:
        self.applied: list[Any] = []
        self.events: list[tuple] = []
        self._raises = raises

    def register_aggregate_source(self, *args, **kwargs): pass

    def event(self, type, **kwargs):  # noqa: A002
        self.events.append((type, kwargs))

    def submit(self, record):
        return False

    def observe_server_result(self, context, result):
        return None

    def apply_config(self, config):
        self.applied.append(config)
        if self._raises:
            raise RuntimeError("apply_config exploded")


class IngressWithoutApplyConfig(RecordingIngress):
    """A pre-OBS-050 double: everything except ``apply_config``."""

    apply_config = None

    def __getattribute__(self, name):
        if name == "apply_config":
            raise AttributeError(name)
        return super().__getattribute__(name)



def build_controller(*, apply_config_raises=False, apply_config_missing=False, cleanup=None):
    directory = tempfile.mkdtemp()
    config = config_in(directory)
    ingress = IngressWithoutApplyConfig() if apply_config_missing else RecordingIngress(raises=apply_config_raises)
    runtime = V2Runtime(config, observability=ingress, backend=MockInjectionBackend())
    if cleanup is not None:
        cleanup.append(lambda: shutil.rmtree(directory, ignore_errors=True))
    return runtime, runtime.session
