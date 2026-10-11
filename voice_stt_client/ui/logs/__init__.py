"""
The V1 log view (OBS-050).

Frozen module structure: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.1. Import
direction (§5.2): everything under ``ui/logs/`` imports
``core.observability.query.*`` and **never** ``core.observability.storage.*``
and **never** ``sqlite3``. The view is a consumer of the query layer; it is
not logging infrastructure, and logging works whether or not it is open.
"""

from __future__ import annotations

__all__ = [
    "LogDetailView",
    "LogFilterBar",
    "LogPage",
    "LogQueryController",
    "LogTableModel",
    "LogWindow",
]


def __getattr__(name: str):
    """Lazy re-exports.

    Importing this package must not pull in PySide6 for someone who only
    wants the name of a module — and the contract tests read these files as
    text. Each symbol is imported on first use instead.
    """
    if name == "LogQueryController":
        from .log_query_controller import LogQueryController

        return LogQueryController
    if name == "LogTableModel":
        from .log_table_model import LogTableModel

        return LogTableModel
    if name == "LogFilterBar":
        from .log_filter_bar import LogFilterBar

        return LogFilterBar
    if name == "LogDetailView":
        from .log_detail_view import LogDetailView

        return LogDetailView
    if name == "LogPage":
        from .log_page import LogPage

        return LogPage
    if name == "LogWindow":
        from .log_window import LogWindow

        return LogWindow
    raise AttributeError(name)
