"""
core.observability — Observability foundation (OBS-010).

ARCH §5.1 freezes the final re-export set (``ObservabilityManager``,
``ObservabilityIngress``, ``NULL_INGRESS``, ``CanonicalLogRecord``). OBS-010
re-exports what exists at this stage; OBS-020/030 extend this module
additively with the concrete ingress and manager.
"""

from __future__ import annotations

from .models import (
    CanonicalLogRecord,
    Channel,
    Level,
    ProducerKind,
    RecordPriority,
    Scope,
    level_rank,
)
from .redaction import (
    SENSITIVE_KEYS,
    TRANSCRIPT_KEYS,
    redact_mapping,
    redact_text,
    shorten_user_paths,
    unfreeze,
)
from .normalizer import (
    LOGGER_CHANNEL_MAP,
    from_client_event,
    from_log_record,
    from_server_result,
)
from .health import (
    LoggingHealthSnapshot,
    LoggingHealthState,
    LoggingInternalHealth,
)
from .ingress import Ingress, NULL_INGRESS, NullIngress, ObservabilityIngress
from .adapters.python_logging import UnifiedLogHandler
from .query.base import (
    LogProvider,
    LogRecordView,
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryPage,
)
from .storage.sqlite import SQLiteLogStore
from .sinks.jsonl_file import JsonlSink
from .worker import LoggingWorker
from .manager import ObservabilityManager

__all__ = [
    "CanonicalLogRecord",
    "Channel",
    "Level",
    "ProducerKind",
    "RecordPriority",
    "Scope",
    "level_rank",
    "SENSITIVE_KEYS",
    "TRANSCRIPT_KEYS",
    "redact_mapping",
    "redact_text",
    "shorten_user_paths",
    "unfreeze",
    "LOGGER_CHANNEL_MAP",
    "from_client_event",
    "from_log_record",
    "from_server_result",
    "LoggingHealthSnapshot",
    "LoggingHealthState",
    "LoggingInternalHealth",
    "Ingress",
    "NULL_INGRESS",
    "NullIngress",
    "ObservabilityIngress",
    "UnifiedLogHandler",
    "LogProvider",
    "LogRecordView",
    "ProviderState",
    "ProviderStatus",
    "QueryFilter",
    "QueryPage",
    "SQLiteLogStore",
    "JsonlSink",
    "LoggingWorker",
    "ObservabilityManager",
]