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
from .query.local import LocalLogProvider
from .query.service import LogQueryService
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
        self._log_dir = log_dir
        # OBS-050: the resolved store path is what the read-only query
        # provider opens. ``None`` means "no local store in this
        # installation" (``store_enabled: false``) and the provider then
        # reports UNAVAILABLE instead of inventing a path.
        self._db_path: Optional[Path] = None
        self._query_service: Optional[LogQueryService] = None
        self._log_handler: Any = None
        # Which sink the worker currently holds, and the configuration it was
        # built from; see ``_on_config_applied``. Initialised before the
        # disabled early return so both attributes always exist.
        self._sink_applied: Optional[JsonlSink] = None
        self._sink_signature_applied: tuple = self._sink_signature(config)

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
            self._db_path = resolved_db
            store = SQLiteLogStore(resolved_db)
        else:
            store = _NullStore()

        sink = self._build_sink(config)
        self._sink_applied = sink

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
        # CONTRACTS §10.4: the apply chain reaches the ingress; the settings
        # the ingress does not own arrive here through this listener.
        self._ingress.register_config_listener(self._on_config_applied)

    @staticmethod
    def _sink_signature(config: Any) -> tuple:
        """The two configuration values that decide *which* sink this is.

        Compared as raw config values, not as resolved paths: resolving runs
        the P-8 check, which may emit a stderr line, and asking "did the user
        change the sink?" must not have that side effect.
        """
        return (
            bool(getattr(config, "file_sink_enabled", False)),
            str(getattr(config, "file_sink_dir", None)),
        )

    def _build_sink(self, config: Any) -> Optional[JsonlSink]:
        """The optional JSONL sink for one configuration, or ``None``.

        Used both at construction and on a runtime apply, so the path
        resolution — including the P-8 user-profile check — happens in exactly
        one place.
        """
        if not getattr(config, "file_sink_enabled", False):
            return None
        sink_dir = getattr(config, "file_sink_dir", None)
        if self._log_dir:
            default_sink_dir = Path(self._log_dir) / DEFAULT_SINK_SUBDIR
        else:
            default_sink_dir = DEFAULT_LOCAL_APP_DIR / "logs" / DEFAULT_SINK_SUBDIR
        resolved_sink_dir = self._resolve_profile_path(
            sink_dir, default_sink_dir, "file_sink_dir"
        )
        return JsonlSink(resolved_sink_dir)

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

    @property
    def db_path(self) -> Optional[Path]:
        """The resolved store path, or ``None`` when this installation has no
        local store (``store_enabled: false``)."""
        return self._db_path

    @property
    def query_service(self) -> LogQueryService:
        """The read-only query registry the log view uses (OBS-050).

        Built lazily and exactly once, with the local provider registered
        first so ``providers()`` has a stable default. The service is
        deliberately independent of the worker: ARCH §11.2 wants the log view
        to stay usable when the worker is dead and then *"schlicht keine neuen
        Zeilen"* to appear — which is the truth, and which a query layer wired
        through the worker could not show.
        """
        if self._query_service is None:
            service = LogQueryService()
            service.register(LocalLogProvider(self._db_path))
            self._query_service = service
        return self._query_service

    def register_log_handler(self, handler: Any) -> None:
        """Called by ``core/logging_setup.py`` with the ``UnifiedLogHandler``.

        ARCH §8.7 freezes *one* configuration value for two filters: the
        handler level (Python logs) and the ingress level (structured
        events). §10.3 marks that value ``IMMEDIATE``. Without this reference
        a runtime level change would move only the ingress half and leave the
        Python-log half on the old level — a setting that visibly does only
        half of what it says.
        """
        self._log_handler = handler

    def health_snapshot(self) -> Any:
        """One snapshot for the log view's status line (CONTRACTS §11.2:
        *"Die Statuszeile des LogWindow POLLT den Snapshot (QTimer, 1 s)"*).
        Never raises — a status line must not be able to break the UI."""
        try:
            queue_depth = int(getattr(self._ingress, "qsize", lambda: 0)())
        except Exception:  # noqa: BLE001
            queue_depth = 0
        return self._health.snapshot(queue_depth=queue_depth)

    def _on_config_applied(self, config: Any) -> None:
        """The manager half of ``apply_config`` (CONTRACTS §10.4).

        Applies the ``IMMEDIATE`` settings the ingress does not own and
        nothing else. ``store_enabled``/``db_path`` are ``APP_RESTART`` and
        are deliberately ignored here. Never raises: §10.4 requires that a
        failure in this path cannot influence the apply result.

        The three steps have **their own** guards rather than one around all
        of them. With a single guard, a throwing ``_build_sink`` (the P-8 path
        check) skipped ``_follow_enabled_state``, so an ``enabled`` change
        submitted in the same apply fell out silently — a setting that does
        nothing and says nothing (OBS-050 gate observations N-1/N-2).
        """
        try:
            if self._log_handler is not None:
                level = getattr(config, "level", None)
                if isinstance(level, str) and level:
                    self._log_handler.setLevel(level.upper())
        except Exception:  # noqa: BLE001 - O-01/O-05: never influence the apply
            pass
        try:
            worker = self._worker
            if worker is not None:
                settings: dict[str, Any] = {
                    "retention_days": getattr(config, "retention_days", 14),
                    "max_entries": getattr(config, "max_entries", 200_000),
                    "max_db_bytes": getattr(config, "max_db_bytes", None),
                    "store_transcription_content": bool(
                        getattr(config, "store_transcription_content", False)
                    ),
                }
                # ``sink`` is always handed over, but a NEW sink is only built
                # when the sink configuration actually changed. Rebuilding on
                # every apply closed the open file and opened a new one even
                # when nothing about the sink had changed — correct, but a
                # rotation nobody asked for (N-1). The worker compares by
                # IDENTITY (``new_sink is not old_sink``), so handing back the
                # same instance is exactly "leave the sink alone".
                signature = self._sink_signature(config)
                if signature != self._sink_signature_applied:
                    self._sink_applied = self._build_sink(config)
                    self._sink_signature_applied = signature
                settings["sink"] = self._sink_applied
                worker.request_settings(**settings)
        except Exception:  # noqa: BLE001 - O-01/O-05
            pass
        try:
            self._follow_enabled_state(config)
        except Exception:  # noqa: BLE001 - O-01/O-05
            pass

    def _follow_enabled_state(self, config: Any) -> None:
        """``enabled`` is the only setting that changes what Health *means*.

        Switching observability off must be visible as ``DISABLED`` rather
        than as an ``OK`` that records nothing (the same reasoning as in
        ``__init__``). Switching it back on only clears ``DISABLED`` — an
        existing ``FAILED_STORE`` or ``FAILED_WORKER`` is a fact about the
        store and the worker and is never overwritten from here.
        """
        enabled = getattr(config, "enabled", None)
        if not isinstance(enabled, bool):
            return
        if not enabled:
            self._health.set_state(
                LoggingHealthState.DISABLED, "logging.observability.enabled = false"
            )
        elif self._health.state is LoggingHealthState.DISABLED:
            self._health.set_state(LoggingHealthState.OK)

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
