"""
``ObservabilityManager`` — the OBS-030 composition root.

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5 (component picture),
§6.2 (lifecycle: built/started **after** ``AppConfig.load()``, stopped
**after** ``bridge.stop(10.0)``, in ``app.py::main()``'s ``finally`` — never
in ``DesktopApplication.shutdown()``), ``LOGGING_DECISIONS_FREEZE_V1.md``
FD-R4 / OD-22.

Owns the ``ObservabilityIngress``, the ``LoggingWorker``, the
``SQLiteLogStore`` and the optional ``JsonlSink``. Constructed and stopped
exactly once per process.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Sequence
from uuid import uuid4

from core.config import DEFAULT_LOCAL_APP_DIR, is_inside_user_profile

from .health import LoggingHealthState, LoggingInternalHealth, emergency
from .ingress import NULL_INGRESS, ObservabilityIngress
from .sinks.jsonl_file import JsonlSink
from .storage.sqlite import OpenResult, SQLiteLogStore
from .worker import LoggingWorker

DEFAULT_DB_PATH = DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"
DEFAULT_SINK_SUBDIR = "observability"


class _NullStore:
    """Used when ``store_enabled`` is ``False``: keeps the worker/sink
    pipeline running (the JSONL sink is independent of the store) without
    ever touching disk. Always reports success so Health stays ``OK``."""

    def open(self) -> OpenResult:
        return OpenResult(True, False, "")

    def write_batch(self, records: Sequence[Any]) -> tuple[int, int]:
        return (0, 0)

    def clear(self) -> int:
        return 0

    def run_retention(self, **_kwargs: Any) -> tuple[int, int]:
        return (0, 0)

    def probe_write(self) -> bool:
        return True

    def measure_db_bytes(self) -> Optional[int]:
        return None

    def close(self) -> None:
        return None


class ObservabilityManager:
    """Built from ``config.logging.observability`` (``LoggingObservabilityConfig``).
    ``AppConfig.load()`` must run first (AR-5) — the manager cannot start
    before its own configuration exists."""

    def __init__(
        self,
        config: Any,
        *,
        instance_id: Optional[str] = None,
        log_dir: Optional[str] = None,
    ) -> None:
        self._config = config
        self._instance_id = instance_id or uuid4().hex
        self._health = LoggingInternalHealth()
        self._enabled = bool(getattr(config, "enabled", True))
        self._worker: Optional[LoggingWorker] = None

        if not self._enabled:
            # ARCH §8.3 freezes ``DISABLED`` as part of the state set; the
            # manager is the only component that knows observability was
            # switched off, so it is the only place the state can arise.
            # Without it Health reports ``OK`` for an observability that
            # records nothing at all.
            self._health.set_state(
                LoggingHealthState.DISABLED, "logging.observability.enabled = false"
            )
            self._ingress: Any = NULL_INGRESS
            return

        self._ingress = ObservabilityIngress(
            instance_id=self._instance_id,
            enabled=True,
            level=getattr(config, "level", "INFO"),
            queue_size=getattr(config, "queue_size", 8192),
            store_raw_payload=getattr(config, "store_raw_payload", True),
            store_transcription_content=getattr(config, "store_transcription_content", False),
            health=self._health,
        )

        store: Any
        if getattr(config, "store_enabled", True):
            db_path = getattr(config, "db_path", None)
            resolved_db = self._resolve_profile_path(db_path, DEFAULT_DB_PATH, "db_path")
            store = SQLiteLogStore(resolved_db)
        else:
            store = _NullStore()

        sink = None
        if getattr(config, "file_sink_enabled", False):
            sink_dir = getattr(config, "file_sink_dir", None)
            if log_dir:
                default_sink_dir = Path(log_dir) / DEFAULT_SINK_SUBDIR
            else:
                default_sink_dir = DEFAULT_LOCAL_APP_DIR / "logs" / DEFAULT_SINK_SUBDIR
            resolved_sink_dir = self._resolve_profile_path(
                sink_dir, default_sink_dir, "file_sink_dir"
            )
            sink = JsonlSink(resolved_sink_dir)

        self._worker = LoggingWorker(
            self._ingress,
            store,
            health=self._health,
            sink=sink,
            batch_size=getattr(config, "batch_size", 200),
            flush_interval_s=getattr(config, "flush_interval_s", 0.5),
            retention_days=getattr(config, "retention_days", 14),
            max_entries=getattr(config, "max_entries", 200_000),
            max_db_bytes=getattr(config, "max_db_bytes", None),
            queue_size=getattr(config, "queue_size", 8192),
            store_transcription_content=getattr(config, "store_transcription_content", False),
        )

    @staticmethod
    def _resolve_profile_path(configured: Any, default_path: Any, field_name: str) -> Path:
        """CONTRACTS §4.3 P-8: *"KEIN Pfad ausserhalb des Benutzerprofils
        akzeptiert"*. ``LoggingObservabilityConfig.validate()`` rejects such a
        path outright, but ``app.py::main()`` builds the manager straight from
        ``AppConfig.load()`` without a ``validate()`` call — so the manager
        repeats the check rather than trusting it. A rejected path is **not
        accepted**: the frozen default location is used instead and one
        rate-limited stderr line says so (G-4). The store must never be
        silently created in a directory with a foreign ACL, and the manager
        must never abort the application over a configuration mistake."""
        if not configured:
            return Path(default_path)
        candidate = Path(str(configured)).expanduser()
        if candidate.is_absolute() and is_inside_user_profile(candidate):
            return candidate
        emergency(
            "path_outside_user_profile",
            f"logging.observability.{field_name} is outside the user profile "
            f"(CONTRACTS §4.3 P-8) and was not accepted; using the default location",
        )
        return Path(default_path)

    # -- composition root surface -----------------------------------------

    @property
    def ingress(self) -> Any:
        return self._ingress

    @property
    def level(self) -> str:
        return getattr(self._ingress, "level", "INFO")

    @property
    def health(self) -> LoggingInternalHealth:
        return self._health

    @property
    def instance_id(self) -> str:
        return self._instance_id

    def start(self) -> None:
        if self._worker is not None:
            self._worker.start()

    def stop(self, timeout: float = 2.0) -> bool:
        if self._worker is None:
            return True
        return self._worker.stop(timeout)

    def clear_history(self, timeout: float = 5.0) -> int:
        """FD-S4 ``LogStore.clear()``, invoked by the future Logging
        settings tab (OBS-050). ``0`` if disabled or the worker never
        started — never raises for that case."""
        if self._worker is None or not self._worker.is_alive():
            return 0
        return self._worker.request_clear(timeout)
