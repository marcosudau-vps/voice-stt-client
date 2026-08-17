"""
Structured logging setup for the RealtimeSTT client.

Provides rotating file logs (optionally JSON Lines) and stdout output.
Channels: connection, audio, text, app, overlay.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.config import LoggingConfig


# Well-known channel names
CHANNELS = ("connection", "audio", "text", "app", "overlay")


class JsonFormatter(logging.Formatter):
    """Formats log records as single-line JSON objects (JSON Lines)."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "ts": self._format_time(record),
            "level": record.levelname,
            "channel": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            entry["exception"] = self.formatException(record.exc_info)
        # Preserve any extra fields attached to the record
        for key in ("session_id", "segment_id", "event_type", "detail"):
            val = getattr(record, key, None)
            if val is not None:
                entry[key] = val
        return json.dumps(entry, ensure_ascii=False)

    @staticmethod
    def _format_time(record: logging.LogRecord) -> str:
        ct = time.localtime(record.created)
        return time.strftime("%Y-%m-%dT%H:%M:%S", ct) + f".{int(record.msecs):03d}"


class ReadableFormatter(logging.Formatter):
    """Human-readable formatter for stdout."""

    FORMAT = "%(asctime)s │ %(levelname)-5s │ %(name)-12s │ %(message)s"
    DATE_FMT = "%H:%M:%S"

    def __init__(self):
        super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FMT)


def setup_logging(config: LoggingConfig, *, observability=None) -> None:
    """
    Configure the root logger and per-channel loggers.

    - Rotating file handler in the configured log directory.
    - Optional stdout handler.
    - Per-channel log levels from config.
    """
    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    root_level = getattr(logging, config.level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # handlers do their own filtering

    # Clear any pre-existing handlers (e.g. from basicConfig)
    root_logger.handlers.clear()

    # --- File handler ---
    log_file = log_dir / "client.log"
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    file_handler.setLevel(root_level)
    if config.json_format:
        file_handler.setFormatter(JsonFormatter())
    else:
        file_handler.setFormatter(ReadableFormatter())
    root_logger.addHandler(file_handler)

    # --- Stdout handler ---
    if config.stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(root_level)
        stdout_handler.setFormatter(ReadableFormatter())
        root_logger.addHandler(stdout_handler)

    # --- Per-channel levels ---
    for channel in CHANNELS:
        channel_logger = logging.getLogger(channel)
        if channel in config.channel_levels:
            ch_level = getattr(
                logging, config.channel_levels[channel].upper(), root_level
            )
            channel_logger.setLevel(ch_level)

    # Quiet down noisy third-party loggers
    for noisy in ("websockets", "PIL", "pystray"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger("app").info(
        "Logging initialized: level=%s, dir=%s, json=%s",
        config.level,
        log_dir,
        config.json_format,
    )

    # --- OBS-020: optional third handler, additive only. Without
    # ``observability`` this function behaves exactly as before
    # (WP-OBS-020 Sollzustand / LOGGING_CONTRACTS_FREEZE_V1.md §6).
    if observability is not None:
        from core.observability.adapters.python_logging import UnifiedLogHandler
        from core.observability.normalizer import from_log_record

        ingress = observability.ingress

        def _normalize(record, _ingress=ingress):
            return from_log_record(
                record,
                instance_id=_ingress.instance_id,
                store_transcription_content=_ingress.store_transcription_content,
                user_profile=_ingress.user_profile,
            )

        observability_handler = UnifiedLogHandler(ingress, _normalize)
        observability_handler.setLevel(observability.level)
        root_logger.addHandler(observability_handler)
