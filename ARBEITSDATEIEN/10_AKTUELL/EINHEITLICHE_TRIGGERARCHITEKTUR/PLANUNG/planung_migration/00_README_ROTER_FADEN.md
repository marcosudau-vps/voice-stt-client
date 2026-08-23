# Roter Faden – Wiederherstellung der einheitlichen Triggerarchitektur

**Status:** Living Plan  
**Zweck:** Dieser Ordner ist ab jetzt die operative Steuerzentrale. Neue Erkenntnisse werden hier einsortiert, statt den Arbeitsfluss spontan umzubauen.

## 1. Normative Reihenfolge

1. `REFERENZ_ZIELBILD_EINHEITLICHE_TRIGGERARCHITEKTUR.md` – **Soll**
2. `REFERENZ_DIAGNOSEBERICHT_TRIGGERARCHITEKTUR.md` – **bekannter Ist-/Defektstand**
3. Die Checklisten in diesem Ordner – **Abarbeitungs- und Nachweisstruktur**
4. Neue Code-Only-Artefakte von Claude – werden als zusätzliche Ist-Evidence eingearbeitet, ändern aber das Zielbild nicht automatisch.

## 2. Grundregel gegen erneutes Verzetteln

Ein neu gefundener Fehler wird **nicht sofort repariert**, nur weil er sichtbar oder störend ist.

Stattdessen:

- [ ] Fund in `15_OFFENE_FUNDE_UND_AENDERUNGSLOG.md` eintragen.
- [ ] Betroffene Spezifikationsinvariante(n) zuordnen.
- [ ] Betroffenes Arbeitspaket bestimmen.
- [ ] Prüfen, ob der Fund ein Blocker für das aktuelle Gate ist.
- [ ] Nur wenn **Blocker**, innerhalb des aktuellen Arbeitspakets bearbeiten.
- [ ] Sonst im vorgesehenen späteren Paket belassen.

Damit bestimmt der Plan die Reihenfolge – nicht der zuletzt sichtbare Fehler.

## 3. Verbindliche Phasen und Gates

### Phase 0 – Governance, Entscheidungen, Baseline
- [ ] `01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md` vollständig entschieden.
- [ ] Code-Only-Architekturaufnahme von Claude eingearbeitet.
- [ ] Traceability-Matrix aktualisiert.
- [ ] Repos/HEADs/Working Trees erneut gesichert.
- [ ] Kein ungeklärter Architekturkonflikt zwischen Zielbild und geplantem Umbau.

**GATE 0:** Architektur und offene Entscheidungen sind ausreichend präzise, dass Implementierung ohne Interpretation beginnen kann.

### Phase 1 – Server: Activation-Lifecycle
Datei: `02_SERVER_ACTIVATION_LIFECYCLE.md`

**GATE 1:** First-Trigger-Lock, vollständige Finalisierung und garantiertes Idle sind serverseitig bewiesen.

### Phase 2 – Protokoll, Events, State-Sync
Datei: `03_PROTOCOL_EVENTS_STATE_SYNC.md`

**GATE 2:** Der Server kann seinen autoritativen Activation-Zustand vollständig, versioniert und reconnect-sicher an den Client vermitteln.

### Phase 3 – Continuous Audio Stream
Datei: `04_CONTINUOUS_AUDIO_STREAM.md`

**GATE 3:** Stream-/Mikrofon-Lifecycle ist von Activations getrennt; mehrere Activations laufen auf demselben Stream.

### Phase 4 – Client: ActivationMirror statt zweiter Wahrheit
Datei: `05_CLIENT_ACTIVATION_MIRROR.md`

**GATE 4:** UI- und Bedienzustand werden ausschließlich aus Serverzustand/Acks abgeleitet; kein fachlich unabhängiger Client-Diktat-Lifecycle bleibt übrig.

### Phase 5 – Trigger- und Hotkey-Semantik
Datei: `06_TRIGGER_HOTKEY_SEMANTICS.md`

**GATE 5:** Idle-Hotkey = Activate, Active-Hotkey = Finish, Wake Word während Lock = keine fachliche Wirkung, separater Wake-Word-Pause-Hotkey.

### Phase 6 – Legacy-Mode und Config-Migration
Datei: `07_CONFIG_LEGACY_MODE_MIGRATION.md`

**GATE 6:** `mode` besitzt keinerlei Runtime-Autorität mehr; nur noch kontrollierte Migration alter Configs.

### Phase 7 – Wake-Word-Konfiguration und Settings
Datei: `08_WAKEWORD_SETTINGS_CATALOG.md`

**GATE 7:** Triggerquellen und Wake Words sind vollständig, widerspruchsfrei und persistierbar konfigurierbar.

### Phase 8 – UI / Tray / Feedback
Datei: `09_UI_TRAY_FEEDBACK.md`

**GATE 8:** Gleicher Serverzustand erzeugt gleiche fachliche Darstellung – unabhängig von Manual/Wake Word.

### Phase 9 – Testfundament + Architekturtests
Datei: `10_TESTFUNDAMENT_UND_MUTATION.md`

**Hinweis:** Dieses Paket läuft bereits ab Phase 0 parallel und wird in jeder Phase ergänzt.

**GATE 9:** Testdoubles entsprechen Produktionsgrenzen; die alten falschen Solltests sind ersetzt; Mutationen beweisen die kritischen Invarianten.

### Phase 10 – Kompatibilität / Browser / Legacy-Adapter
Datei: `11_KOMPATIBILITAET_BROWSER_LEGACY.md`

**GATE 10:** Browserclient, erlaubter Legacy-Adapter und aktuelle Clients passen zum neuen Protokoll, ohne zweite Runtime-Architektur.

### Phase 11 – Vollregression / Build / Evidence
Datei: `12_REGRESSION_BUILD_EVIDENCE.md`

**GATE 11:** Alle Repos grün, Build reproduzierbar, Evidence vollständig, keine unbeabsichtigten Pfade/Artefakte.

### Phase 12 – Reale manuelle Abnahme
Datei: `13_MANUELLE_ABNAHME.md`

**GATE 12:** Zielbild in echter Bedienung mit Audio, Hotkeys, Wake Word, Browser und ReSpeaker nachgewiesen.

### Phase 13 – Dokumentation und Abschluss
Datei: `14_DOKUMENTATION_FINALISIERUNG.md`

**GATE 13:** Aktive Doku beschreibt ausschließlich die tatsächlich abgenommene Architektur; historische Doku ist klar als historisch markiert.

## 4. Cross-Cutting Tracks

Diese Punkte laufen durch alle Phasen:

- [ ] `10_TESTFUNDAMENT_UND_MUTATION.md` nach jedem Defekt/Testfund aktualisieren.
- [ ] `15_OFFENE_FUNDE_UND_AENDERUNGSLOG.md` bei jedem neuen Fund aktualisieren.
- [ ] `16_TRACEABILITY_MATRIX.md` bei jeder Spezifikations-/Planänderung aktualisieren.
- [ ] Evidence direkt beim Gate sammeln, nicht am Projektende rekonstruieren.
- [ ] Jede Phase endet mit einem klaren PASS/FAIL – kein „größtenteils fertig“.

## 5. Definition „fertig“

Ein Arbeitspaket ist erst fertig, wenn:

- [ ] Implementierung abgeschlossen.
- [ ] Alte widersprechende Verantwortlichkeit entfernt oder klar als Compatibility isoliert.
- [ ] Positive Tests vorhanden.
- [ ] Negativtests vorhanden.
- [ ] Race-/Lifecycle-Tests vorhanden, falls relevant.
- [ ] Mindestens ein False-Positive-/Mutation-Nachweis für kritische Invarianten vorhanden.
- [ ] Vollständige betroffene Repo-Suite grün.
- [ ] Produktionspfad manuell oder E2E geprüft.
- [ ] Evidence gespeichert.
- [ ] Checkliste aktualisiert.
- [ ] Keine offenen Blocker für das Gate.

## 6. Kein „Papier-PASS“

Grüne Tests allein sind kein Gate-Nachweis. Jedes Gate braucht zusätzlich einen Beleg am tatsächlichen Produktionspfad oder einen echten E2E-/Integrationspfad.
