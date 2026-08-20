"""Compact faceted filters for the diagnostics viewer."""

from __future__ import annotations

from typing import Any, Iterable, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QCompleter,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QWidget,
)

from core.observability.query.base import QueryFacets, QueryFilter

DEBOUNCE_MS = 300
ANY_LABEL = "Alle"

_PRODUCERS = (
    ("client", "Client"), ("server", "Server"), ("led", "LED"), ("other", "Andere")
)
_CHANNELS = (
    ("system", "System"), ("audit", "Audit"),
    ("transcription", "Transcription"), ("performance", "Performance")
)
_LEVELS = (
    ("DEBUG", "Debug"), ("INFO", "Info"), ("WARNING", "Warning"),
    ("ERROR", "Error"), ("CRITICAL", "Critical")
)

ACTIVATION_HINT = (
    "Die Activation-ID wird serverseitig beim Veröffentlichen aus dem aktuellen "
    "Controllerzustand gelesen und kann deshalb fehlen oder bereits zu einer "
    "neueren Aktivierung gehören. Sie hilft bei einer punktuellen Diagnose, ist "
    "aber nicht zuverlässig für fachliche Gruppierung. Verwenden Sie dafür "
    "vorzugsweise die Korrelations-ID und die zugehörigen Command-/Event-IDs."
)


class MultiSelectButtons(QWidget):
    """A compact checkable facet with an exclusive ``Alle`` option."""

    selection_changed = Signal()

    def __init__(self, values: Iterable[tuple[str, str]], tooltip: str, parent=None) -> None:
        super().__init__(parent)
        self._buttons: dict[str, QToolButton] = {}
        layout = QGridLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(3)
        layout.setVerticalSpacing(2)
        self.all_button = self._make(ANY_LABEL, None, tooltip)
        self.all_button.setChecked(True)
        layout.addWidget(self.all_button, 0, 0)
        for index, (value, label) in enumerate(values, start=1):
            button = self._make(label, value, tooltip)
            self._buttons[value] = button
            layout.addWidget(button, index // 4, index % 4)
        layout.setColumnStretch(4, 1)

    def _make(self, label: str, value: Optional[str], tooltip: str) -> QToolButton:
        button = QToolButton(self)
        button.setText(label)
        button.setCheckable(True)
        button.setAutoRaise(False)
        button.setProperty("facetValue", value)
        button.setToolTip(tooltip)
        button.toggled.connect(lambda checked, v=value: self._toggled(v, checked))
        return button

    def _toggled(self, value: Optional[str], checked: bool) -> None:
        if self.signalsBlocked():
            return
        blocked = self.blockSignals(True)
        try:
            if value is None and checked:
                for button in self._buttons.values():
                    button.setChecked(False)
            elif value is not None and checked:
                self.all_button.setChecked(False)
            if not any(button.isChecked() for button in self._buttons.values()):
                self.all_button.setChecked(True)
        finally:
            self.blockSignals(blocked)
        self.selection_changed.emit()

    def selected_values(self) -> tuple[str, ...]:
        if self.all_button.isChecked():
            return ()
        return tuple(value for value, button in self._buttons.items() if button.isChecked())

    def set_selected(self, values: Iterable[str]) -> None:
        selected = set(values)
        blocked = self.blockSignals(True)
        try:
            for value, button in self._buttons.items():
                button.setChecked(value in selected and button.isEnabled())
            self.all_button.setChecked(not any(button.isChecked() for button in self._buttons.values()))
        finally:
            self.blockSignals(blocked)

    def update_available(self, values: Iterable[str]) -> None:
        available = set(values)
        blocked = self.blockSignals(True)
        try:
            for value, button in self._buttons.items():
                # A selected value remains enabled: the facet query excludes
                # its own dimension and therefore accurately tells whether it
                # can still match under every other filter.
                button.setEnabled(value in available)
                if not button.isEnabled():
                    button.setChecked(False)
            self.all_button.setEnabled(True)
            if not any(button.isChecked() for button in self._buttons.values()):
                self.all_button.setChecked(True)
        finally:
            self.blockSignals(blocked)

    def button(self, value: str) -> Optional[QToolButton]:
        return self._buttons.get(value)


class LogFilterBar(QWidget):
    """Owns the separate Filter and Kontext groups and builds QueryFilter."""

    filter_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(DEBOUNCE_MS)
        self._debounce.timeout.connect(self._emit_filter)
        self._suspended = False

        self.filter_group = QGroupBox("Filter", self)
        filter_layout = QGridLayout(self.filter_group)
        filter_layout.setContentsMargins(8, 8, 8, 8)
        filter_layout.setVerticalSpacing(4)

        self.producer_select = MultiSelectButtons(
            _PRODUCERS,
            "Filtert nach der Herkunft des Records. Mehrere Quellen können gleichzeitig gewählt werden.",
            self.filter_group,
        )
        self.channel_select = MultiSelectButtons(
            _CHANNELS,
            "Filtert nach dem fachlichen Logging-Channel. Mehrfachauswahl ist möglich.",
            self.filter_group,
        )
        self.level_select = MultiSelectButtons(
            _LEVELS,
            "Filtert exakt nach einem oder mehreren Schweregraden.",
            self.filter_group,
        )
        for row, (label, widget) in enumerate((
            ("Quelle", self.producer_select), ("Channel", self.channel_select),
            ("Level", self.level_select),
        )):
            filter_layout.addWidget(QLabel(label), row, 0, Qt.AlignmentFlag.AlignTop)
            filter_layout.addWidget(widget, row, 1)

        self.type_box = QComboBox(self.filter_group)
        self.type_box.setEditable(True)
        self.type_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.type_box.setToolTip(
            "Ereignistyp, zum Beispiel client.trigger.sent. Eingaben werden als Präfix gesucht."
        )
        self.type_edit = self.type_box.lineEdit()
        self.type_edit.setPlaceholderText("Ereignistyp auswählen oder Präfix eingeben")
        self.type_edit.setClearButtonEnabled(True)
        completer = QCompleter(self.type_box.model(), self.type_box)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.type_box.setCompleter(completer)
        filter_layout.addWidget(QLabel("Ereignistyp"), 3, 0)
        filter_layout.addWidget(self.type_box, 3, 1)

        self.text_edit = self._line(
            "Meldung, Ereignistyp oder Component durchsuchen",
            "Allgemeine Freitextsuche über Meldung, Ereignistyp und Component; der Raw-Payload wird nicht durchsucht.",
            self.filter_group,
        )
        self.text_edit.setMinimumWidth(260)
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        filter_layout.addWidget(QLabel("Suche"), 4, 0)
        filter_layout.addWidget(self.text_edit, 4, 1)

        self.context_group = QGroupBox("Kontext", self)
        context_form = QFormLayout(self.context_group)
        context_form.setContentsMargins(8, 8, 8, 8)
        context_form.setVerticalSpacing(4)
        self.session_edit = self._line("Session-ID", "Exakte Session-ID des Records.", self.context_group)
        context_form.addRow("Session-ID", self.session_edit)
        self.activation_edit = self._line("Activation-ID", ACTIVATION_HINT, self.context_group)
        activation_label = QLabel("Activation-ID ⚠")
        activation_label.setToolTip(ACTIVATION_HINT)
        context_form.addRow(activation_label, self.activation_edit)
        self.segment_edit = self._line("Segment-ID (Zahl)", "Exakte numerische Segment-ID.", self.context_group)
        context_form.addRow("Segment-ID", self.segment_edit)
        self.command_edit = self._line("Command-ID", "Exakte Command-ID.", self.context_group)
        context_form.addRow("Command-ID", self.command_edit)
        self.event_edit = self._line("Event-ID", "Exakte Event-ID.", self.context_group)
        context_form.addRow("Event-ID", self.event_edit)
        self.transcription_edit = self._line("Transcription-ID", "Exakte Transcription-ID.", self.context_group)
        context_form.addRow("Transcription-ID", self.transcription_edit)
        self.correlation_edit = self._line(
            "Korrelations-ID", "Belastbare Korrelations-ID zur Gruppierung zusammengehöriger Ereignisse.", self.context_group
        )
        context_form.addRow("Korrelations-ID", self.correlation_edit)
        self.replayed_box = QCheckBox("Wiederholte Serverereignisse anzeigen", self.context_group)
        self.replayed_box.setChecked(True)
        self.replayed_box.setToolTip(
            "Zeigt zusätzlich Ereignisse an, die der Server beispielsweise nach einem Reconnect aus seiner Ereignishistorie erneut übertragen hat."
        )
        context_form.addRow("", self.replayed_box)

        for facet in (self.producer_select, self.channel_select, self.level_select):
            facet.selection_changed.connect(self._schedule)
        self.type_edit.textChanged.connect(self._schedule)
        self.replayed_box.toggled.connect(self._schedule)

    def _line(self, placeholder: str, tooltip: str, parent: QWidget) -> QLineEdit:
        edit = QLineEdit(parent)
        edit.setPlaceholderText(placeholder)
        edit.setToolTip(tooltip)
        edit.setClearButtonEnabled(True)
        edit.textChanged.connect(self._schedule)
        return edit

    def current_filter(self) -> QueryFilter:
        return QueryFilter(
            producer_kinds=self.producer_select.selected_values(),
            channels=self.channel_select.selected_values(),
            levels=self.level_select.selected_values(),
            type_prefix=_text_or_none(self.type_edit),
            session_id=_text_or_none(self.session_edit),
            activation_id=_text_or_none(self.activation_edit),
            segment_id=_int_or_none(self.segment_edit),
            command_id=_text_or_none(self.command_edit),
            event_id=_text_or_none(self.event_edit),
            transcription_id=_text_or_none(self.transcription_edit),
            correlation_id=_text_or_none(self.correlation_edit),
            text=_text_or_none(self.text_edit),
            include_replayed=self.replayed_box.isChecked(),
            newest_first=True,
        )

    def apply_facets(self, facets: QueryFacets) -> None:
        if not isinstance(facets, QueryFacets):
            return
        self._suspended = True
        try:
            self.producer_select.update_available(facets.producer_kinds)
            self.channel_select.update_available(facets.channels)
            self.level_select.update_available(facets.levels)
            current = self.type_edit.text()
            blocked = self.type_box.blockSignals(True)
            self.type_box.clear()
            self.type_box.addItems(facets.types)
            self.type_box.setEditText(current)
            self.type_box.blockSignals(blocked)
        finally:
            self._suspended = False

    def apply_context(
        self,
        *,
        session_id: Optional[str] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[Any] = None,
        type_value: Optional[str] = None,
        correlation_id: Optional[str] = None,
        command_id: Optional[str] = None,
        event_id: Optional[str] = None,
    ) -> None:
        self._suspended = True
        try:
            for edit, value in (
                (self.session_edit, session_id), (self.activation_edit, activation_id),
                (self.segment_edit, segment_id), (self.correlation_edit, correlation_id),
                (self.command_edit, command_id), (self.event_edit, event_id),
            ):
                if value is not None:
                    edit.setText(str(value))
            if type_value is not None:
                self.type_box.setEditText(str(type_value))
        finally:
            self._suspended = False
        self._emit_filter()

    def reset(self) -> None:
        self._suspended = True
        try:
            for facet in (self.producer_select, self.channel_select, self.level_select):
                facet.set_selected(())
            for edit in (
                self.type_edit, self.text_edit, self.session_edit, self.activation_edit,
                self.segment_edit, self.command_edit, self.event_edit,
                self.transcription_edit, self.correlation_edit,
            ):
                edit.clear()
            self.replayed_box.setChecked(True)
        finally:
            self._suspended = False
        self._emit_filter()

    def _schedule(self, *unused: object) -> None:
        del unused
        if not self._suspended:
            self._debounce.start()

    def _emit_filter(self) -> None:
        self._debounce.stop()
        self.filter_changed.emit(self.current_filter())


def _text_or_none(edit: QLineEdit) -> Optional[str]:
    value = edit.text().strip()
    return value or None


def _int_or_none(edit: QLineEdit) -> Optional[int]:
    value = edit.text().strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


__all__ = ["LogFilterBar", "MultiSelectButtons", "DEBOUNCE_MS", "ACTIVATION_HINT"]
