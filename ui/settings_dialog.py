"""Typed six-tab settings and transcript-history dialog.

The sixth tab, "Logging & Diagnose", is frozen in
``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.1 as the place for the logging
configuration — and §9.1 equally freezes that the *log view* is **not** a tab
here but its own non-modal window. This tab therefore carries the settings
plus two buttons: "Diagnosehistorie löschen" (FD-S4, at the store) and "Logs
anzeigen" (opens that window). Both are actions, not settings, so they sit
outside the form and do not wait for "Übernehmen" — the same pattern the
device and server reconnect buttons already use.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable, Iterable, Optional

import numpy as np
import sounddevice as sd
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.audio_capture import AudioCapture
from core.config import AppConfig
from core.history import HistoryEntry
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.ingress import NULL_INGRESS
from core.logging_settings_metadata import ALL_SETTING_DEFINITIONS
from core.settings_metadata import (
    ApplyPolicy,
    SettingDefinition,
    SettingType,
    build_candidate,
    get_config_value,
)

# The dialog edits every declared setting, including the sixth tab's, which
# lives in its own metadata module (see the module docstring there).
SETTING_DEFINITIONS = ALL_SETTING_DEFINITIONS

ApplyCallback = Callable[[AppConfig, frozenset[ApplyPolicy]], bool]


class SettingsDialog(QDialog):
    """One UI over typed config values; metadata stores no second values."""

    history_refresh_requested = Signal()
    history_reinsert_requested = Signal(str)
    history_delete_requested = Signal(str)
    history_clear_requested = Signal()
    reconnect_device_requested = Signal()
    reconnect_server_requested = Signal()
    logging_clear_requested = Signal()
    logging_view_requested = Signal()

    TAB_NAMES = (
        "Verlauf",
        "Allgemein",
        "Verbindung & Betriebsmodus",
        "Geräte & Audio",
        "Erscheinungsbild & Feedback",
        "Logging & Diagnose",
    )

    def __init__(
        self,
        config: AppConfig,
        on_apply: ApplyCallback,
        parent: Optional[QWidget] = None,
        *,
        observability=NULL_INGRESS,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("RealtimeSTT – Einstellungen")
        self.resize(820, 620)
        self._config = config
        self._on_apply = on_apply
        self._observe = ClientEventEmitter(
            observability, component="ui.settings_dialog"
        )
        self._editors: dict[str, QWidget] = {}
        self._labels: dict[str, QWidget] = {}
        self._definitions: dict[str, SettingDefinition] = {
            definition.path: definition for definition in SETTING_DEFINITIONS
        }
        self._history_entries: list[HistoryEntry] = []

        root = QVBoxLayout(self)
        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)
        self._history_tab = self._build_history_tab()
        self.tabs.addTab(self._history_tab, "Verlauf")
        for name in self.TAB_NAMES[1:]:
            self.tabs.addTab(self._build_settings_tab(name), name)
        for editor in self._editors.values():
            if isinstance(editor, QComboBox):
                editor.currentIndexChanged.connect(self._update_visibility)
            elif isinstance(editor, QCheckBox):
                editor.toggled.connect(self._update_visibility)
        self._update_visibility()

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Apply
            | QDialogButtonBox.StandardButton.Close
        )
        self.buttons.button(QDialogButtonBox.StandardButton.Apply).clicked.connect(
            self.apply_changes
        )
        self.buttons.rejected.connect(self.close)
        root.addWidget(self.buttons)

    def _build_settings_tab(self, category: str) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        grouped: dict[str, list[SettingDefinition]] = defaultdict(list)
        for definition in SETTING_DEFINITIONS:
            if definition.category == category and definition.show_in_dialog:
                grouped[definition.group].append(definition)
        for group_name, definitions in grouped.items():
            group = QGroupBox(group_name)
            form = QFormLayout(group)
            for definition in sorted(definitions, key=lambda item: item.order):
                editor = self._create_editor(definition)
                editor.setToolTip(definition.description)
                self._editors[definition.path] = editor
                form.addRow(definition.label, editor)
                label = form.labelForField(editor)
                if label is not None:
                    self._labels[definition.path] = label
            layout.addWidget(group)
        if category == "Geräte & Audio":
            test_button = QPushButton("Mikrofon 3 Sekunden testen")
            test_button.clicked.connect(self._start_microphone_test)
            self.microphone_result = QLabel("")
            layout.addWidget(test_button)
            layout.addWidget(self.microphone_result)

            # An action, not a setting: it changes nothing that gets saved, so
            # it sits outside the form and does not wait for "Übernehmen".
            self.reconnect_device_button = QPushButton("ReSpeaker neu verbinden")
            self.reconnect_device_button.setToolTip(
                "Trennt die USB-Verbindung zum LED-Ring und baut sie sofort neu "
                "auf, statt auf den nächsten Versuch zu warten."
            )
            self.reconnect_device_button.clicked.connect(
                self.reconnect_device_requested.emit
            )
            layout.addWidget(self.reconnect_device_button)

        if category == "Verbindung & Betriebsmodus":
            self.reconnect_server_button = QPushButton("Server neu verbinden")
            self.reconnect_server_button.setToolTip(
                "Verwirft die bestehende Serververbindung, damit sie sofort neu "
                "aufgebaut wird, statt den Wartezeitplan abzuwarten."
            )
            self.reconnect_server_button.clicked.connect(
                self.reconnect_server_requested.emit
            )
            layout.addWidget(self.reconnect_server_button)

        if category == "Logging & Diagnose":
            self.show_logs_button = QPushButton("Logs anzeigen")
            self.show_logs_button.setToolTip(
                "Öffnet die Logansicht in einem eigenen Fenster. Die Ansicht "
                "liest nur; das Logging läuft unabhängig davon weiter."
            )
            self.show_logs_button.clicked.connect(self.logging_view_requested.emit)
            layout.addWidget(self.show_logs_button)

            self.clear_logs_button = QPushButton("Diagnosehistorie löschen")
            self.clear_logs_button.setToolTip(
                "Löscht alle lokal gespeicherten Diagnoseeinträge "
                "unwiderruflich. Die Transkripthistorie bleibt unberührt."
            )
            self.clear_logs_button.clicked.connect(self._clear_diagnostics)
            layout.addWidget(self.clear_logs_button)

            self.logging_status = QLabel("")
            self.logging_status.setWordWrap(True)
            layout.addWidget(self.logging_status)
        layout.addStretch(1)
        return page

    def _clear_diagnostics(self) -> None:
        """FD-S4: the deletion is irreversible, so it is confirmed — the same
        warning shape the transcript history's "Alles löschen" already uses."""
        answer = QMessageBox.warning(
            self,
            "Diagnosehistorie löschen",
            "Alle lokal gespeicherten Diagnoseeinträge löschen? Dies kann "
            "nicht rückgängig gemacht werden.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.logging_clear_requested.emit()

    def set_logging_status(self, text: str) -> None:
        """Result line of the two logging actions. Separate from
        ``status_label``, which belongs to the settings apply chain."""
        label = getattr(self, "logging_status", None)
        if label is not None:
            label.setText(text)

    def _create_editor(self, definition: SettingDefinition) -> QWidget:
        value = get_config_value(self._config, definition.path)
        if definition.editor == "audio_device":
            editor = QComboBox()
            editor.addItem("Systemstandard", None)
            for device in AudioCapture.list_devices():
                if int(device.get("channels", 0)) > 0:
                    editor.addItem(
                        str(device["name"]), int(device["index"])
                    )
            index = editor.findData(value)
            editor.setCurrentIndex(max(0, index))
            return editor
        if definition.setting_type == SettingType.BOOLEAN:
            editor = QCheckBox()
            if definition.path == "session.manual_trigger_enabled":
                editor.setChecked(bool(self._config.session.effective_manual_trigger_enabled))
            elif definition.path == "session.wake_word_trigger_enabled":
                editor.setChecked(bool(self._config.session.wake_word_enabled))
            else:
                editor.setChecked(bool(value))
            return editor
        if definition.setting_type == SettingType.CHOICE:
            editor = QComboBox()
            for label, option in definition.options:
                editor.addItem(label, option)
            index = editor.findData(value)
            editor.setCurrentIndex(max(0, index))
            return editor
        if definition.setting_type == SettingType.INTEGER:
            editor = QSpinBox()
            editor.setRange(
                int(definition.minimum if definition.minimum is not None else -2147483647),
                int(definition.maximum if definition.maximum is not None else 2147483647),
            )
            editor.setSingleStep(int(definition.step or 1))
            editor.setValue(int(value))
            if definition.unit:
                editor.setSuffix(f" {definition.unit}")
            return editor
        if definition.setting_type == SettingType.FLOAT:
            editor = QDoubleSpinBox()
            step = float(definition.step or 0.1)
            minimum = float(
                definition.minimum if definition.minimum is not None else -1e9
            )
            if definition.editor == "optional_float":
                editor.setMinimum(minimum - step)
                editor.setSpecialValueText("Serverstandard")
                editor.setValue(minimum - step if value is None else float(value))
            else:
                editor.setMinimum(minimum)
                editor.setValue(float(value))
            editor.setMaximum(
                float(definition.maximum if definition.maximum is not None else 1e9)
            )
            editor.setSingleStep(step)
            editor.setDecimals(4)
            if definition.unit:
                editor.setSuffix(f" {definition.unit}")
            return editor
        editor = QLineEdit("" if value is None else str(value))
        return editor

    def _update_visibility(self, *unused: object) -> None:
        del unused
        for path, definition in self._definitions.items():
            editor = self._editors.get(path)
            if editor is None:
                continue
            visible = True
            if definition.visible_when is not None:
                dependency, expected = definition.visible_when
                dependency_definition = self._definitions[dependency]
                dependency_value = self._editor_value(dependency_definition)
                visible = dependency_value == expected
            editor.setVisible(visible)
            label = self._labels.get(path)
            if label is not None:
                label.setVisible(visible)

    def _editor_value(self, definition: SettingDefinition) -> Any:
        editor = self._editors[definition.path]
        if isinstance(editor, QCheckBox):
            return editor.isChecked()
        if isinstance(editor, QComboBox):
            return editor.currentData()
        if isinstance(editor, QSpinBox):
            return editor.value()
        if isinstance(editor, QDoubleSpinBox):
            if (
                definition.editor == "optional_float"
                and editor.value() < float(definition.minimum or 0)
            ):
                return None
            return editor.value()
        if isinstance(editor, QLineEdit):
            text = editor.text().strip()
            if (
                definition.editor in ("optional_hotkey", "optional_path")
                or get_config_value(self._config, definition.path) is None
            ):
                # ``optional_path`` is checked by name rather than by the
                # current value: once a path HAS been set, clearing the field
                # has to mean "back to the default" again, not the empty
                # string — which config validation rejects (P-8).
                return text or None
            return text
        raise TypeError(f"Unsupported editor for {definition.path}")

    def apply_changes(self) -> None:
        changes: dict[str, Any] = {}
        policies: set[ApplyPolicy] = set()
        try:
            for path, definition in self._definitions.items():
                value = self._editor_value(definition)
                current_val = (
                    self._config.session.effective_manual_trigger_enabled
                    if path == "session.manual_trigger_enabled"
                    else (
                        self._config.session.wake_word_enabled
                        if path == "session.wake_word_trigger_enabled"
                        else get_config_value(self._config, path)
                    )
                )
                if value != current_val:
                    changes[path] = value
                    policies.add(definition.apply_policy)
            if not changes:
                self.status_label.setText("Keine Änderungen.")
                return
            candidate = build_candidate(self._config, changes)
        except (TypeError, ValueError, KeyError) as exc:
            self.status_label.setText(f"Ungültige Einstellung: {exc}")
            # CONTRACTS §12.1: client.config.validation_failed (P+S). Only the
            # setting PATHS are recorded, never the rejected values -- a value
            # here is user input and the paths alone answer "which setting did
            # the dialog refuse".
            self._observe.system(
                "client.config.validation_failed",
                level="WARNING",
                details={
                    "source": "settings_dialog",
                    "paths": sorted(changes),
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                },
            )
            return

        if ApplyPolicy.SESSION_RECONNECT in policies:
            answer = QMessageBox.question(
                self,
                "Verbindung neu aufbauen",
                "Die Änderung beendet ein laufendes Diktat und baut die "
                "Session neu auf. Das Diktat wird nicht fortgesetzt. Anwenden?",
            )
            if answer != QMessageBox.StandardButton.Yes:
                return
        if self._on_apply(candidate, frozenset(policies)):
            self.status_label.setText(
                "Einstellungen werden geprüft und angewendet …"
            )
            self.buttons.button(
                QDialogButtonBox.StandardButton.Apply
            ).setEnabled(False)
        else:
            self.status_label.setText("Einstellungen konnten nicht eingeplant werden.")

    def complete_apply(
        self, success: bool, config: Optional[AppConfig], message: str
    ) -> None:
        self.buttons.button(
            QDialogButtonBox.StandardButton.Apply
        ).setEnabled(True)
        if success and config is not None:
            self._config = config
            self.status_label.setText("Einstellungen wurden übernommen.")
        else:
            self.status_label.setText(f"Übernahme fehlgeschlagen: {message}")

    def _build_history_tab(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        self.history_table = QTableWidget(0, 3)
        self.history_table.setHorizontalHeaderLabels(("Zeit", "Text", "Status"))
        self.history_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.history_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.history_table)
        buttons = QHBoxLayout()
        refresh = QPushButton("Aktualisieren")
        refresh.clicked.connect(self.history_refresh_requested.emit)
        reinsert = QPushButton("Erneut einfügen")
        reinsert.clicked.connect(self._reinsert_selected)
        delete = QPushButton("Eintrag löschen")
        delete.clicked.connect(self._delete_selected)
        clear = QPushButton("Alles löschen")
        clear.clicked.connect(self._clear_history)
        for button in (refresh, reinsert, delete, clear):
            buttons.addWidget(button)
        layout.addLayout(buttons)
        return page

    def set_history_entries(self, entries: Iterable[HistoryEntry]) -> None:
        self._history_entries = list(entries)
        self.history_table.setRowCount(len(self._history_entries))
        for row, entry in enumerate(self._history_entries):
            values = (
                str(entry.timestamp),
                entry.text,
                entry.attempts[-1].status if entry.attempts else "ohne Einfügeversuch",
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setData(Qt.ItemDataRole.UserRole, entry.id)
                self.history_table.setItem(row, column, item)
        self.history_table.resizeColumnsToContents()

    def _selected_entry_id(self) -> Optional[str]:
        row = self.history_table.currentRow()
        if row < 0:
            return None
        item = self.history_table.item(row, 0)
        return str(item.data(Qt.ItemDataRole.UserRole)) if item else None

    def _reinsert_selected(self) -> None:
        entry_id = self._selected_entry_id()
        if entry_id:
            self.history_reinsert_requested.emit(entry_id)

    def _delete_selected(self) -> None:
        entry_id = self._selected_entry_id()
        if not entry_id:
            return
        answer = QMessageBox.question(
            self, "Eintrag löschen", "Den ausgewählten Verlaufseintrag löschen?"
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.history_delete_requested.emit(entry_id)

    def _clear_history(self) -> None:
        answer = QMessageBox.warning(
            self,
            "Verlauf vollständig löschen",
            "Alle gespeicherten Transkripte löschen? Dies kann nicht "
            "rückgängig gemacht werden.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.history_clear_requested.emit()

    def _start_microphone_test(self) -> None:
        device_editor = self._editors.get("audio.device")
        device = (
            device_editor.currentData()
            if isinstance(device_editor, QComboBox)
            else self._config.audio.device
        )
        sample_rate = int(
            self._editor_value(self._definitions["audio.sample_rate"])
        )
        try:
            self.microphone_result.setText("Aufnahme läuft – jetzt sprechen …")
            recording = sd.rec(
                int(3 * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="int16",
                device=device,
            )
        except Exception as exc:
            self.microphone_result.setText(f"Mikrofontest konnte nicht starten: {exc}")
            return

        def finish() -> None:
            try:
                sd.stop()
                values = recording[:, 0].astype(np.float64)
                rms = float(np.sqrt(np.mean(values * values)))
                peak = float(np.max(np.abs(values)) / 32767 * 100)
                self.microphone_result.setText(
                    f"RMS {rms:.1f}, Peak {peak:.2f} %"
                )
            except Exception as exc:
                self.microphone_result.setText(f"Mikrofontest fehlgeschlagen: {exc}")

        QTimer.singleShot(3000, finish)
