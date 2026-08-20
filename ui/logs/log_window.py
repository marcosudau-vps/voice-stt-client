"""
``LogWindow`` — the non-modal V1 log view (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.1 (*"eigenes,
nicht-modales ``LogWindow``, erreichbar über das Tray-Menü und über einen
Knopf im Logging-Tab"*, Health status line inside it) and §9.3 (*"``hide()``
statt ``close()``; Geometrie über ``QSettings``"*).

§9.1 also records why this is **not** a settings tab: the settings dialog is
a modal ``QDialog`` with an Apply button ("Übernehmen" is meaningless on a
query page), it is created once and kept alive (a log view in it would keep
querying while invisible), diagnosis happens *while* settings are changed,
and the dialog's fixed 820×620 geometry does not fit a table plus a detail
pane.

Closing hides the window and stops both timers, so a closed log view costs
nothing at all — logging keeps running without it (O-01: the view is a
consumer, never infrastructure).
"""

from __future__ import annotations

from typing import Any, Callable, Optional

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.logs.log_page import LogPage
from ui.logs.log_query_controller import LogQueryController

SETTINGS_GROUP = "logs"
GEOMETRY_KEY = "log_window/geometry"
DEFAULT_SIZE = (1100, 700)


class LogWindow(QWidget):
    """Top-level, non-modal window holding one :class:`LogPage`."""

    def __init__(
        self,
        service: Any,
        *,
        health_provider: Optional[Callable[[], Any]] = None,
        parent: Optional[QWidget] = None,
        settings: Optional[QSettings] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("RealtimeSTT – Logs & Diagnose")
        self.setWindowFlag(Qt.WindowType.Window, True)
        self.resize(*DEFAULT_SIZE)

        self._settings = settings if settings is not None else QSettings()
        self.controller = LogQueryController(service, self)
        self.page = LogPage(
            self.controller,
            health_provider=health_provider,
            parent=self,
            settings=self._settings,
        )
        layout = QVBoxLayout(self)
        layout.addWidget(self.page)

        self._restore_geometry()

    # -- geometry ----------------------------------------------------------

    def _restore_geometry(self) -> None:
        try:
            geometry = self._settings.value(GEOMETRY_KEY)
        except Exception:  # noqa: BLE001 - a broken settings store must not
            # stop the window from opening.
            return
        if geometry:
            try:
                self.restoreGeometry(geometry)
            except Exception:  # noqa: BLE001
                pass

    def _save_geometry(self) -> None:
        try:
            self._settings.setValue(GEOMETRY_KEY, self.saveGeometry())
        except Exception:  # noqa: BLE001
            pass

    # -- show / hide -------------------------------------------------------

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.page.refresh_providers()
        self.page.start()

    def hideEvent(self, event) -> None:  # noqa: N802
        self.page.save_view_state()
        self.page.stop()
        super().hideEvent(event)

    def closeEvent(self, event) -> None:  # noqa: N802
        """§9.3: ``hide()`` statt ``close()``. The window keeps its state and
        its geometry, and reopening it is free."""
        self._save_geometry()
        self.page.save_view_state()
        self.page.stop()
        event.ignore()
        self.hide()

    def shutdown(self) -> None:
        """Application teardown: stop the timers, release the query thread and
        remember the geometry. Safe to call more than once."""
        self._save_geometry()
        self.page.save_view_state()
        self.page.stop()
        self.controller.shutdown()


__all__ = ["LogWindow", "GEOMETRY_KEY"]
