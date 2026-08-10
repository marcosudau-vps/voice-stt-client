"""Typed five-tab settings and transcript-history dialog."""

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
from core.settings_metadata import (
    ApplyPolicy,
    SETTING_DEFINITIONS,
    SettingDefinition,
    SettingType,
    build_candidate,
    get_config_value,
)

ApplyCallback = Callable[[AppConfig, frozenset[ApplyPolicy]], bool]


class SettingsDialog(QDialog):
    """One UI over typed config values; metadata stores no second values."""

    history_refresh_requested = Signal()
    history_reinsert_requested = Signal(str)
    history_delete_requested = Signal(str)
    history_clear_requested = Signal()
    reconnect_device_requested = Signal()
    reconnect_server_requested = Signal()

    TAB_NAMES = (
        "Verlauf",
        "Allgemein",
        "Verbindung & Betriebsmodus",
        "Geräte & Audio",
        "Erscheinungsbild & Feedback",
    )

    def __init__(
        self,
        config: AppConfig,
        on_apply: ApplyCallback,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("RealtimeSTT – Einstellungen")
        self.resize(820, 620)
        self._config = config
        self._on_apply = on_apply
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
        layout.addStretch(1)
        return page

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
            if definition.editor == "optional_hotkey" or get_config_value(
                self._config, definition.path
            ) is None:
                return text or None
            return text
        raise TypeError(f"Unsupported editor for {definition.path}")

    def apply_changes(self) -> None:
        changes: dict[str, Any] = {}
        policies: set[ApplyPolicy] = set()
        try:
            for path, definition in self._definitions.items():
                value = self._editor_value(definition)
                if value != get_config_value(self._config, path):
                    changes[path] = value
                    policies.add(definition.apply_policy)
            if not changes:
                self.status_label.setText("Keine Änderungen.")
                return
            candidate = build_candidate(self._config, changes)
        except (TypeError, ValueError, KeyError) as exc:
            self.status_label.setText(f"Ungültige Einstellung: {exc}")
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
