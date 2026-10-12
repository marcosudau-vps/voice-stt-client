"""V2 trigger/session/admin UI over immutable core-loop projections."""
from __future__ import annotations

from copy import deepcopy
import json

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
    QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget,
    QListWidgetItem, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget)

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.settings_service import NA_KEYS, SERVER_DEFAULT_KEYS, UNSUPPORTED_SESSION
from voice_stt_client.core.v2_controls import ActiveAction
from voice_stt_client.core.settings_ui_service import ApplyChoice


ERROR_TEXT = {
    "admin_key_required": "Bitte einen Admin-Key eingeben oder den gespeicherten Key laden.",
    "admin_unauthorized": "Der Admin-Key fehlt oder ist falsch (401).",
    "admin_disabled": "Remoteverwaltung ist auf diesem Server deaktiviert (403).",
    "settings_revision_conflict": "Die Serverrevision wurde geändert (409). Neu laden und bewusst erneut anwenden.",
    "server_settings_rejected": "Der Server hat die Werte abgelehnt (422). Keine Teiländerung.",
    "server_persistence_failed": "Der Server konnte die Änderung nicht speichern (500). Serverwerte erneut prüfen.",
    "credential_store_unavailable": "Windows-Anmeldeinformationsverwaltung nicht verfügbar. Key bleibt höchstens im Prozessspeicher; kein Klartextfallback.",
    "http_outcome_unknown": "Die Antwort fehlt. Der Ausgang ist unklar; neu laden, bevor erneut geschrieben wird.",
    "apply_context_changed": "Diktat oder Verbindung hat sich geändert. Erneut laden und entscheiden.",
    "connection_changed": "Die Verbindung wurde geändert. Neu laden; Admin-Key erneut prüfen.",
    "server_origin_changed": "Der Server wurde geändert. Dialog neu öffnen und den eigenen Admin-Key prüfen.",
    "drain_pending_retry": "Ergebnisse stehen noch aus. Verbindung bleibt bestehen; später erneut anwenden.",
    "profile_persistence_failed": "Lokale Einstellungen konnten nicht gespeichert werden.",
    "profile_persistence_required": "Die Anwendung hat die lokale Profilverwaltung noch nicht angeschlossen.",
    "catalog_unavailable": "Wake-Word-Katalog fehlt oder ist veraltet. Neu laden.",
    "profile_repair_required": "Das migrierte Profil benötigt eine bestätigte Korrektur. Offene Werte prüfen; unbekannte Konflikte bleiben erhalten.",
}
POLICY_TEXT = {"live": "Sofort", "next_activation": "Nächstes Diktat",
               "next_session": "Nächste Verbindung", "server_restart": "Serverneustart"}
LABELS = {
    "activation.initialSpeechTimeoutMs": "Warten auf erste Sprache",
    "activation.followupTimeoutMs": "Warten auf Folgeeingabe",
    "activation.segmentWatchdogInitialMs": "Daueraufnahme-Schutz",
    "activation.segmentWatchdogRefreshMs": "Schutz nach Refresh",
    "activation.segmentWatchdogWarningMs": "Vorwarnung",
    "activation.closingRecoveryTimeoutMs": "Warten auf Eingabeschluss",
    "wakeWord.sensitivity": "Wake-Empfindlichkeit",
    "wakeWord.minConsecutivePredictionFrames": "Aufeinanderfolgende Wake-Treffer",
    "wakeWord.cooldownMs": "Wake-Abklingzeit", "wakeWord.preRollMs": "Wake-Audiovorlauf",
    "wakeWord.detectorGain": "Wake-Verstärkung", "wakeWord.noiseSuppressionEnabled": "Wake-Rauschunterdrückung",
    "wakeWord.vadThreshold": "Wake-Sprachschwelle", "wakeWord.selection": "Wake-Auswahl",
    "runtimeSuppression.manual": "Manuelle Laufzeitpause", "runtimeSuppression.wakeWord": "Wake-Laufzeitpause",
    "wakeWord.inferenceBackend": "Wake-Backend", "wakeWord.globalDisabledIds": "Serverweit gesperrte Wake-IDs",
}


def display(value):
    if value is None:
        return "—"
    value = p._thaw(value)
    if type(value) is bool:
        return "Ja" if value else "Nein"
    if isinstance(value, list):
        return ", ".join(value) or "(leer)"
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, allow_nan=False)


def make_editor(definition):
    if definition.type == "bool":
        editor = QComboBox()
        editor.addItem("Nein", False)
        editor.addItem("Ja", True)
        return editor
    allowed = definition.constraints.get("allowedValues", definition.constraints.get("allowed"))
    if definition.type == "string" and allowed:
        editor = QComboBox()
        for value in allowed:
            editor.addItem(value, value)
        return editor
    editor = QLineEdit()
    if definition.type == "string_list":
        editor.setPlaceholderText("IDs durch Komma trennen; leer = keine")
    elif definition.type == "float":
        editor.setPlaceholderText("Zahl mit Dezimalpunkt, z. B. 0.5")
    return editor


def set_editor(editor, definition, value):
    value = p._thaw(value)
    if isinstance(editor, QComboBox):
        editor.setCurrentIndex(editor.findData(value))
    elif definition.type == "string_list":
        editor.setText(", ".join(value or []))
    else:
        editor.setText(str(value) if value is not None else "")


def read_editor(editor, definition):
    if isinstance(editor, QComboBox):
        return editor.currentData()
    if definition.type == "string_list":
        return [part.strip() for part in editor.text().split(",") if part.strip()]
    if definition.type == "string":
        return editor.text()
    return json.loads(editor.text())


def constraint_text(definition):
    c = definition.constraints
    unit = c.get("unit", "")
    text = []
    if "min" in c:
        text.append(f"Minimum {c['min']} {unit}".strip())
    if "max" in c:
        text.append(f"Maximum {c['max']} {unit}".strip())
    if "minItems" in c:
        text.append(f"Mindestens {c['minItems']} Einträge")
    if c.get("lessThanKeys"):
        text.append("Strikt kleiner als " + ", ".join(LABELS.get(k, k) for k in c["lessThanKeys"]))
    if c.get("calibration") == "pending":
        text.append("calibration pending: Startwert, keine kalibrierte Empfehlung")
    return " · ".join(text)


class ApplyDecisionDialog(QDialog):
    """Default is no decision; Cancel/close never grants destruction."""
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("Neue Verbindung – Diktat und Ergebnisse schützen")
        layout = QVBoxLayout(self)
        label = QLabel("Die Änderung benötigt eine neue Verbindung. Ein offenes Diktat und noch ausstehende Ergebnisse werden dabei nicht fortgesetzt.")
        label.setWordWrap(True)
        layout.addWidget(label)
        self.choice = QComboBox()
        self.choice.addItem("Bitte ausdrücklich entscheiden …", None)
        self.choice.addItem("Diktat abbrechen und neu verbinden", ApplyChoice.CANCEL)
        self.choice.addItem("Eingabe fertigstellen und auf Ergebnisse warten", ApplyChoice.FINISH)
        self.choice.addItem("Vormerken – erst bei nächster Verbindung verwenden", ApplyChoice.DEFER)
        layout.addWidget(self.choice)
        self.drain = QComboBox()
        self.drain.addItem("Ausstehende Hintergrund-Ergebnisse: bitte entscheiden …", None)
        self.drain.addItem("Auf alle Ergebnisse warten", "wait")
        self.drain.addItem("Verlust unveröffentlichter Ergebnisse ausdrücklich akzeptieren", "discard")
        if context.drain_ids or context.activation_id:
            warning = QLabel(f"{len(context.drain_ids)} Diktate warten im Hintergrund. Auch das aktuelle Diktat kann nach Eingabeschluss noch Ergebnisse liefern. Abbrechen verwirft unveröffentlichte Ergebnisse des aktuellen Diktats.")
            warning.setWordWrap(True)
            layout.addWidget(warning)
            layout.addWidget(self.drain)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.choice.currentIndexChanged.connect(self._enable)
        self.drain.currentIndexChanged.connect(self._enable)
        layout.addWidget(self.buttons)
        self._enable()

    def _enable(self):
        choice = self.choice.currentData()
        allowed = choice is not None and (choice == ApplyChoice.DEFER or not self.context.drain_ids or self.drain.currentData() is not None)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(allowed)

    def plan(self):
        if self.result() != QDialog.DialogCode.Accepted:
            return None
        return self.choice.currentData(), self.drain.currentData() or "wait"


class V2SettingsDialog(QDialog):
    """Use with V2SettingsBridge; optional existing local SettingsDialog.

    local_dialog must be constructed with v2_local=True to retain history,
    devices, clipboard, appearance/feedback/logging without legacy controls.
    QSettings metadata is optional and receives only target/saved flags.
    """
    def __init__(self, bridge, parent=None, *, local_dialog=None, metadata=None):
        super().__init__(parent)
        self.bridge, self.local_dialog, self.metadata = bridge, local_dialog, metadata
        self._view = None
        self._request_id = None
        self._editors = {"session": {}, "server": {}}
        self._rows = {"session": {}, "server": {}}
        self._profile_loaded = False
        self._decision = None
        self.setWindowTitle("RealtimeSTT – V2-Einstellungen")
        self.resize(1120, 700)
        root = QVBoxLayout(self)
        self.origin_label = QLabel()
        root.addWidget(self.origin_label)
        self.tabs = QTabWidget()
        root.addWidget(self.tabs)
        self._build_local()
        self._build_session()
        self._build_server()
        self.status = QLabel("Einstellungen werden geladen …")
        self.status.setWordWrap(True)
        root.addWidget(self.status)
        row = QHBoxLayout()
        self.reload_button = QPushButton("Serverwerte und Katalog neu laden")
        self.reload_button.clicked.connect(lambda: self._request("load"))
        close = QPushButton("Schließen")
        close.clicked.connect(self.close)
        row.addWidget(self.reload_button)
        row.addWidget(close)
        root.addLayout(row)
        self.bridge.replied.connect(self._receive, Qt.ConnectionType.QueuedConnection)
        self.timer = QTimer(self)
        self.timer.setInterval(500)
        self.timer.timeout.connect(lambda: self._request("inspect", quiet=True))

    def _build_local(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        form = QFormLayout()
        self.manual = QCheckBox("Manuelle Aktivierung")
        self.wake = QCheckBox("Wake Word")
        form.addRow("Dauerhaft konfigurierte Trigger", self.manual)
        form.addRow("Beide Quellen sind gleichzeitig nutzbar", self.wake)
        self.controls = {}
        for key, label in (("primary_key", "Primärer Hotkey"), ("secondary_key", "Sekundärer Hotkey"),
                           ("wake_pause_key", "Optionaler Wake-Pause-Hotkey"),
                           ("reinsert_last_key", "Letzten Text erneut einfügen"), ("overlay_toggle_key", "Overlay umschalten")):
            editor = QLineEdit()
            self.controls[key] = editor
            form.addRow(label, editor)
        for key, label in (("primary_action", "Primäre Aktion bei offenem Diktat"), ("secondary_action", "Sekundäre Aktion bei offenem Diktat")):
            editor = QComboBox()
            for value, text in ((ActiveAction.REFRESH, "Refresh"), (ActiveAction.FINISH, "Fertigstellen"),
                                (ActiveAction.CANCEL, "Abbrechen"), (ActiveAction.NONE, "Keine Aktion")):
                editor.addItem(text, str(value))
            self.controls[key] = editor
            form.addRow(label, editor)
        self.controls_enabled = QCheckBox("Globale Hotkeys aktivieren")
        form.addRow(self.controls_enabled)
        layout.addLayout(form)
        self.trigger_status = QLabel()
        self.trigger_status.setWordWrap(True)
        layout.addWidget(self.trigger_status)
        self.repair_status = QLabel()
        self.repair_status.setWordWrap(True)
        layout.addWidget(self.repair_status)
        self.repair = QCheckBox("Gezeigte Trigger-, Wake-, Zeit- und Hotkeywerte ausdrücklich als Migrationskorrektur bestätigen")
        layout.addWidget(self.repair)
        layout.addWidget(QLabel("Hotkeys steuern auch Wake-only-Diktate. Laufzeitpausen werden nicht dauerhaft gespeichert."))
        if self.local_dialog is not None:
            local = QPushButton("Lokale Geräte, Verlauf, Zwischenablage, Darstellung und Diagnose …")
            local.clicked.connect(self.local_dialog.show)
            layout.addWidget(local)
        layout.addStretch()
        self.tabs.addTab(page, "Lokale Trigger & Bedienung")

    def _table(self, layout, scope):
        table = QTableWidget(0, 8)
        table.setHorizontalHeaderLabels(("Einstellung", "Wunsch / Entwurf", "Angefordert", "Wirksam",
            "Serverstandard", "Schema-Startwert", "Wirksam ab", "Grenzen / Hinweise"))
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._tables = getattr(self, "_tables", {})
        self._tables[scope] = table
        layout.addWidget(table)

    def _build_session(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        self.revisions = QLabel()
        layout.addWidget(self.revisions)
        self.catalog_status = QLabel()
        self.catalog_status.setWordWrap(True)
        layout.addWidget(self.catalog_status)
        self.wake_list = QListWidget()
        self.wake_list.setMaximumHeight(140)
        layout.addWidget(self.wake_list)
        self._table(layout, "session")
        self.pending_label = QLabel()
        self.pending_label.setWordWrap(True)
        layout.addWidget(self.pending_label)
        self.apply_profile_button = QPushButton("Trigger und Sessionwünsche übernehmen")
        self.apply_profile_button.clicked.connect(self.apply_profile)
        layout.addWidget(self.apply_profile_button)
        self.tabs.addTab(page, "Session")

    def _build_server(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Serverweite Defaults für neue Diktate/Verbindungen. Öffentliche Reads entsperren diese Seite nicht."))
        form = QFormLayout()
        self.key = QLineEdit()
        self.key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Admin-Key", self.key)
        self.remember = QCheckBox("Im Windows Credential Manager speichern / ersetzen")
        form.addRow(self.remember)
        layout.addLayout(form)
        row = QHBoxLayout()
        self.verify_button = QPushButton("Key prüfen (ohne Werteänderung)")
        self.verify_button.clicked.connect(self.verify)
        self.load_key_button = QPushButton("Gespeicherten Key laden")
        self.load_key_button.clicked.connect(lambda: self._request("load_credential"))
        self.delete_key_button = QPushButton("Gespeicherten Key löschen")
        self.delete_key_button.clicked.connect(lambda: self._request("delete_credential"))
        for button in (self.verify_button, self.load_key_button, self.delete_key_button):
            row.addWidget(button)
        layout.addLayout(row)
        self.admin_status = QLabel("Gesperrt – Admin-Key prüfen.")
        layout.addWidget(self.admin_status)
        self._table(layout, "server")
        self.apply_server_button = QPushButton("Serverdefaults ausdrücklich ändern")
        self.apply_server_button.clicked.connect(self.apply_server)
        self.apply_server_button.setEnabled(False)
        layout.addWidget(self.apply_server_button)
        self.tabs.addTab(page, "Serververwaltung")

    def showEvent(self, event):
        super().showEvent(event)
        self._profile_loaded = False
        self.repair.setChecked(False)
        self.bridge.open()
        self.timer.start()

    def hideEvent(self, event):
        self.timer.stop()
        self.bridge.close()
        self._view = None
        self._request_id = None
        self.key.clear()
        self.apply_server_button.setEnabled(False)
        if self._decision is not None:
            self._decision.reject()
        super().hideEvent(event)

    def _request(self, operation, *, quiet=False, **payload):
        request = self.bridge.request(operation, **payload)
        if request is not None:
            self._request_id = request
            if not quiet:
                self.status.setText("Anfrage läuft …")
        return request

    def _receive(self, reply):
        if not self.isVisible() or reply.epoch != self.bridge.epoch:
            return
        if self._request_id is not None and reply.request_id < self._request_id:
            return
        reset = reply.operation in ("load", "apply_profile", "patch_server") and reply.error is None
        if reply.view is not None:
            previous = self._view
            self._view = reply.view
            if self._decision is not None and (previous is None or previous.context != reply.view.context):
                self._decision.reject()
            self.render(reset=reset)
        if reply.error:
            self.status.setText(ERROR_TEXT.get(reply.error, "Einstellung konnte nicht übernommen werden: " + reply.error))
        elif reply.operation != "inspect":
            if reply.operation == "apply_profile" and reply.view and self._reconnect_pending(reply.view):
                self.status.setText("Profil gespeichert. Trigger-/Wake-Auswahl für die nächste Verbindung vorgemerkt; aktuelle Eingabe bleibt bestehen.")
            else:
                self.status.setText("Serverwerte geladen." if reply.operation == "load" else "Anfrage bestätigt.")

    @staticmethod
    def _reconnect_pending(view):
        return (view.profile["manual"], view.profile["wake_word"], tuple(view.profile["wake_word_ids"]) if view.profile["wake_word"] else ()) != (
            view.connected_triggers.get("manual"), view.connected_triggers.get("wakeWord"), view.connected_wake_ids)

    def render(self, *, reset=False):
        v = self._view
        self.origin_label.setText("Server: " + v.origin)
        self.revisions.setText(f"Sessionrevision: {v.settings.session_revision} · Serverrevision: {v.settings.server_revision} · Katalogrevision: {v.settings.catalog_revision}")
        self.trigger_status.setText("Aktuelle Verbindung: Manuell " + display(v.connected_triggers.get("manual")) +
            ", Wake " + display(v.connected_triggers.get("wakeWord")) +
            (". Gespeicherte Trigger-/Wake-Auswahl ist noch vorgemerkt." if self._reconnect_pending(v) else ". Gespeichertes Triggerprofil ist wirksam."))
        self.repair_status.setText("Offene Migrationswerte: " + ", ".join(v.profile["unresolved"]) if v.profile["unresolved"] else "")
        self.repair.setVisible(bool(v.profile["unresolved"]))
        verified = v.admin_verified
        self.apply_server_button.setEnabled(verified)
        self.admin_status.setText(("Admin-Key geprüft. " if verified else "Gesperrt – Admin-Key prüfen. ") +
            ("Key im Credential Manager gespeichert." if v.credential_saved else "Keine bestätigte dauerhafte Speicherung."))
        if self.metadata is not None:
            self.metadata.setValue("admin/" + v.credential_target + "/saved", v.credential_saved)
            self.metadata.setValue("admin/" + v.credential_target + "/target", v.credential_target)
        if not self._profile_loaded or reset:
            self._profile_loaded = True
            self.manual.setChecked(v.profile["manual"])
            self.wake.setChecked(v.profile["wake_word"])
            for key, editor in self.controls.items():
                value = v.profile["controls"][key]
                if isinstance(editor, QComboBox):
                    editor.setCurrentIndex(editor.findData(str(value)))
                else:
                    editor.setText(value)
            self.controls_enabled.setChecked(v.profile["controls"]["enabled"])
            self._render_catalog(v)
        elif self.wake_list.property("revision") != v.settings.catalog_revision:
            self._render_catalog(v, keep_draft=True)
        self.catalog_status.setText("Katalog fehlt / Ladefehler – Auswahl bleibt erhalten." if v.catalog is None else
            ("Katalog veraltet / Ladefehler – neu laden." if v.settings.catalog_stale else
             "Keine Wake Words im Serverkatalog verfügbar." if not v.catalog.entries else
             "Wake-Auswahl gilt bei nächster Verbindung. Unverfügbare IDs bitte abwählen oder korrigieren."))
        self.pending_label.setText("Ausstehend: " + (", ".join(LABELS.get(k, k) for k in v.settings.pending) or "keine") +
            ". Rauschunterdrückung und VAD sind hier nur lesbar; wirksame Änderung über Serverdefaults.")
        for scope, table in self._tables.items():
            keys = [key for key, definition in v.schema.items() if (definition.scope == "session" if scope == "session" else key in SERVER_DEFAULT_KEYS or definition.scope == "server")]
            if list(self._rows[scope]) != keys:
                self._rows[scope] = {key: row for row, key in enumerate(keys)}
                self._editors[scope] = {}
                table.setRowCount(len(keys))
            for key, row in self._rows[scope].items():
                definition = v.schema[key]
                writable = key in (NA_KEYS if scope == "session" else SERVER_DEFAULT_KEYS)
                requested = (v.settings.requested if scope == "session" else v.server_requested).get(key)
                effective = (v.settings.effective if scope == "session" else v.server_effective).get(key)
                default = v.server_requested.get(key)
                value = v.profile["desired_settings"].get(key, requested if requested is not None else default)
                if scope == "server":
                    value = requested
                editor = self._editors[scope].get(key)
                if editor is None:
                    editor = make_editor(definition)
                    self._editors[scope][key] = editor
                    table.setCellWidget(row, 1, editor)
                    set_editor(editor, definition, value if value is not None else definition.default_value)
                elif reset:
                    set_editor(editor, definition, value if value is not None else definition.default_value)
                editor.setEnabled(writable and (scope == "session" or verified))
                hints = constraint_text(definition)
                if key in UNSUPPORTED_SESSION and scope == "session":
                    hints += " · Nur über Admin-Serverdefault wirksam"
                values = {0: LABELS.get(key, key), 2: display(requested), 3: display(effective),
                    4: display(default), 5: display(definition.default_value),
                    6: POLICY_TEXT.get(str(definition.apply_policy), str(definition.apply_policy)), 7: hints}
                for column, text in values.items():
                    item = QTableWidgetItem(text)
                    item.setToolTip(key + " · " + definition.description)
                    table.setItem(row, column, item)
            table.resizeColumnsToContents()

    def _render_catalog(self, view, *, keep_draft=False):
        selected = set(self.selected_wake_ids()) if keep_draft else set(view.profile["wake_word_ids"])
        self.wake_list.clear()
        entries = view.catalog.entries if view.catalog else {}
        for key in dict.fromkeys((*entries, *sorted(selected - set(entries)))):
            entry = entries.get(key)
            available = entry is not None and entry["available"]
            label = entry["displayName"] if entry else key
            reason = "" if available else " – nicht verfügbar: " + (entry.get("unavailableReason", "unknown") if entry else "ID fehlt im Katalog")
            item = QListWidgetItem(label + reason)
            item.setData(Qt.ItemDataRole.UserRole, key)
            flags = Qt.ItemFlag.ItemIsUserCheckable
            if available or key in selected:
                flags |= Qt.ItemFlag.ItemIsEnabled
            item.setFlags(flags)
            item.setCheckState(Qt.CheckState.Checked if key in selected else Qt.CheckState.Unchecked)
            self.wake_list.addItem(item)
        self.wake_list.setProperty("revision", view.settings.catalog_revision)

    def selected_wake_ids(self):
        return [self.wake_list.item(i).data(Qt.ItemDataRole.UserRole) for i in range(self.wake_list.count())
                if self.wake_list.item(i).checkState() == Qt.CheckState.Checked]

    def verify(self):
        key = self.key.text()
        self.key.clear()
        self._request("verify", key=key or None, remember=self.remember.isChecked())

    def _changes(self, scope):
        values = {}
        source = self._view.profile["desired_settings"] if scope == "session" else self._view.server_requested
        for key, editor in self._editors[scope].items():
            if key not in (NA_KEYS if scope == "session" else SERVER_DEFAULT_KEYS):
                continue
            value = read_editor(editor, self._view.schema[key])
            self._view.schema[key].validate(value)
            if p._thaw(source.get(key)) != value:
                values[key] = value
        return values

    def apply_server(self):
        if self._view is None or not self._view.admin_verified:
            return
        try:
            changes = self._changes("server")
            if not changes:
                self.status.setText("Keine Änderungen.")
                return
            self._request("patch_server", changes=changes)
        except (ValueError, TypeError):
            self.status.setText("Ungültiger Wert. Typ und Schema-Grenzen prüfen.")

    def apply_profile(self):
        if self._view is None:
            return
        try:
            profile = p._thaw(self._view.profile)
            profile["manual"], profile["wake_word"] = self.manual.isChecked(), self.wake.isChecked()
            profile["wake_word_ids"] = self.selected_wake_ids()
            profile["desired_settings"].update(self._changes("session"))
            profile["controls"] = {key: editor.currentData() if isinstance(editor, QComboBox) else editor.text()
                                   for key, editor in self.controls.items()}
            profile["controls"]["enabled"] = self.controls_enabled.isChecked()
            if not profile["manual"] and not profile["wake_word"]:
                raise ValueError
            context = self._view.context
            old = self._view.profile
            reconnect = (profile["manual"], profile["wake_word"], tuple(profile["wake_word_ids"]) if profile["wake_word"] else ()) != (
                self._view.connected_triggers.get("manual", old["manual"]),
                self._view.connected_triggers.get("wakeWord", old["wake_word"]), self._view.connected_wake_ids)
            choice, drain = None, None
            if reconnect and (context.activation_id or context.drain_ids):
                decision = ApplyDecisionDialog(context, self)
                self._decision = decision
                decision.exec()
                self._decision = None
                plan = decision.plan()
                if plan is None:
                    self.status.setText("Nicht übernommen – keine Entscheidung.")
                    return
                choice, drain = plan
            repairs = [key for key in old["unresolved"] if key in ("wake_words", "session.mode", "session.trigger_flags", "hotkey", *NA_KEYS)] if self.repair.isChecked() else []
            self._request("apply_profile", profile=profile, context=context, choice=choice, drain_choice=drain, repair_fields=repairs)
        except (ValueError, TypeError):
            self.status.setText("Ungültige Einstellungen. Mindestens eine Triggerquelle und gültige Werte sind erforderlich.")
