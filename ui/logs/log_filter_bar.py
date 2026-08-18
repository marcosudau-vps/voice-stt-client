"""
``LogFilterBar`` — the declarative filter row above the log table (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §8 (``QueryFilter`` is
purely declarative and no consumer may modify it), §9.2 (*"Signal
filter_changed(QueryFilter) (entprellt, 300 ms)"*) and §9.3 (the context
actions that set this bar's fields), plus ``LOGGING_ARCHITEKTUR_FREEZE_V1.md``
§3.4 / ``FD-C2``: *"Der UI-Filter 'nur diese Activation' traegt einen
sichtbaren Hinweis auf die Unzuverlaessigkeit."*

The level box filters *from* a minimum level upwards and expands that to the
explicit set ``QueryFilter.levels`` expects. Levels are a closed set
(CONTRACTS §2.1), so the expansion is total and no level can be missed —
whereas an exact-match level box would hide the ERROR somebody is looking for
behind a WARNING selection.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from PySide6.QtCore import QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QWidget,
)

from core.observability.query.base import QueryFilter

DEBOUNCE_MS = 300

ANY_LABEL = "Alle"
_PRODUCER_KINDS = ("client", "server", "led", "other")
_CHANNELS = ("system", "audit", "transcription", "performance")
_LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

ACTIVATION_HINT = (
    "Diagnostisch, nicht autoritativ: der Server liest die activationId erst "
    "beim Veröffentlichen frisch aus dem Controller. Ist die Activation "
    "geschlossen, fehlt sie; ist inzwischen eine neue geöffnet, ist sie falsch."
)


def _levels_from(minimum: str) -> Tuple[str, ...]:
    if minimum not in _LEVELS:
        return ()
    start = _LEVELS.index(minimum)
    return _LEVELS[start:]


class LogFilterBar(QWidget):
    """Builds one ``QueryFilter`` from the visible fields."""

    filter_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(DEBOUNCE_MS)
        self._debounce.timeout.connect(self._emit_filter)
        self._suspended = False

        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        dimensions = QGroupBox("Filter")
        form = QFormLayout(dimensions)
        self.producer_box = self._choice(_PRODUCER_KINDS)
        form.addRow("Quelle", self.producer_box)
        self.channel_box = self._choice(_CHANNELS)
        form.addRow("Channel", self.channel_box)
        self.level_box = self._choice(_LEVELS, current="DEBUG")
        form.addRow("ab Level", self.level_box)
        self.type_edit = self._line("z. B. client.trigger")
        form.addRow("Typ (Präfix)", self.type_edit)
        self.text_edit = self._line("Freitext über Meldung, Typ und Component")
        form.addRow("Text", self.text_edit)
        layout.addWidget(dimensions, 0, 0)

        context = QGroupBox("Kontext")
        context_form = QFormLayout(context)
        self.session_edit = self._line("Session-ID")
        context_form.addRow("Session", self.session_edit)
        self.activation_edit = self._line("Activation-ID")
        self.activation_edit.setToolTip(ACTIVATION_HINT)
        activation_label = QLabel("Activation ⚠")
        activation_label.setToolTip(ACTIVATION_HINT)
        context_form.addRow(activation_label, self.activation_edit)
        self.segment_edit = self._line("Segment-ID (Zahl)")
        context_form.addRow("Segment", self.segment_edit)
        self.correlation_edit = self._line("z. B. trigger:cmd-…")
        context_form.addRow("Korrelation", self.correlation_edit)
        self.replayed_box = QCheckBox("Replayte Records anzeigen")
        self.replayed_box.setChecked(True)
        self.replayed_box.toggled.connect(self._schedule)
        context_form.addRow("", self.replayed_box)
        layout.addWidget(context, 0, 1)

        # FD-C2: the hint is visible, not only a tooltip.
        self.activation_hint = QLabel(
            "⚠ Der Activation-Filter ist diagnostisch und serverseitig "
            "unzuverlässig — nie zum fachlichen Gruppieren verwenden."
        )
        self.activation_hint.setWordWrap(True)
        layout.addWidget(self.activation_hint, 1, 0, 1, 2)

    # -- construction helpers --------------------------------------------

    def _choice(self, values, *, current: Optional[str] = None) -> QComboBox:
        box = QComboBox(self)
        box.addItem(ANY_LABEL, None)
        for value in values:
            box.addItem(value, value)
        if current is not None:
            index = box.findData(current)
            if index >= 0:
                box.setCurrentIndex(index)
        box.currentIndexChanged.connect(self._schedule)
        return box

    def _line(self, placeholder: str) -> QLineEdit:
        edit = QLineEdit(self)
        edit.setPlaceholderText(placeholder)
        edit.setClearButtonEnabled(True)
        edit.textChanged.connect(self._schedule)
        return edit

    # -- filter -----------------------------------------------------------

    def current_filter(self) -> QueryFilter:
        """The declarative filter for the current field values.

        Every empty field means *"no restriction"*, which is what an empty
        tuple and ``None`` mean in ``QueryFilter``.
        """
        producer = self.producer_box.currentData()
        channel = self.channel_box.currentData()
        minimum_level = self.level_box.currentData()
        return QueryFilter(
            producer_kinds=(producer,) if producer else (),
            channels=(channel,) if channel else (),
            levels=_levels_from(minimum_level) if minimum_level else (),
            type_prefix=_text_or_none(self.type_edit),
            session_id=_text_or_none(self.session_edit),
            activation_id=_text_or_none(self.activation_edit),
            segment_id=_int_or_none(self.segment_edit),
            correlation_id=_text_or_none(self.correlation_edit),
            text=_text_or_none(self.text_edit),
            include_replayed=self.replayed_box.isChecked(),
            newest_first=True,
        )

    def apply_context(
        self,
        *,
        session_id: Optional[str] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[Any] = None,
        type_value: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> None:
        """Set one context field from the table's context menu (§9.3).

        The fields are set with signals suspended and exactly one
        ``filter_changed`` is emitted afterwards — a context action is one
        user decision, not four.
        """
        self._suspended = True
        try:
            if session_id is not None:
                self.session_edit.setText(str(session_id))
            if activation_id is not None:
                self.activation_edit.setText(str(activation_id))
            if segment_id is not None:
                self.segment_edit.setText(str(segment_id))
            if correlation_id is not None:
                self.correlation_edit.setText(str(correlation_id))
            if type_value is not None:
                self.type_edit.setText(str(type_value))
        finally:
            self._suspended = False
        self._emit_filter()

    def reset(self) -> None:
        self._suspended = True
        try:
            for box in (self.producer_box, self.channel_box):
                box.setCurrentIndex(0)
            index = self.level_box.findData("DEBUG")
            self.level_box.setCurrentIndex(index if index >= 0 else 0)
            for edit in (
                self.type_edit,
                self.text_edit,
                self.session_edit,
                self.activation_edit,
                self.segment_edit,
                self.correlation_edit,
            ):
                edit.clear()
            self.replayed_box.setChecked(True)
        finally:
            self._suspended = False
        self._emit_filter()

    def _schedule(self, *unused: object) -> None:
        del unused
        if self._suspended:
            return
        self._debounce.start()

    def _emit_filter(self) -> None:
        self._debounce.stop()
        self.filter_changed.emit(self.current_filter())


def _text_or_none(edit: QLineEdit) -> Optional[str]:
    text = edit.text().strip()
    return text or None


def _int_or_none(edit: QLineEdit) -> Optional[int]:
    text = edit.text().strip()
    if not text:
        return None
    try:
        return int(text)
    except ValueError:
        # A half-typed number is not an error state: it simply does not
        # restrict anything yet.
        return None


__all__ = ["LogFilterBar", "DEBOUNCE_MS", "ACTIVATION_HINT"]
