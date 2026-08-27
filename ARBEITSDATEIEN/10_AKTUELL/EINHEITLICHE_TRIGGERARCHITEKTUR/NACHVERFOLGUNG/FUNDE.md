# Offene Funde und Änderungslog

**Zweck:** Neue Erkenntnisse aufnehmen, ohne die fachliche Planung mit
Implementierungsstatus zu vermischen. Entscheidungen selbst stehen in
`../PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`.

## Verwendung

Für jeden neuen Fund einen Block kopieren:

```markdown
### FIND-XXX – Kurztitel
- Datum:
- Gefunden durch:
- Beobachtung:
- Betroffene Repos/Dateien:
- Betroffene Zielbild-Invarianten:
- Vermutete Phase/AP:
- Blockiert aktuelles Gate? JA/NEIN
- Wenn JA: warum?
- Wenn NEIN: wann bearbeiten?
- Evidence:
- Status: OPEN / CONFIRMED / RESOLVED / NOT-A-BUG
```

---

## Bereits bekannte Kerndefekte

### FIND-001 – Client bleibt nach Activation aktiv
- [x] Bestätigt.
- Ziel-AP: ClientMirror + Server Finalisierung.
- Status: CONFIRMED.

### FIND-002 – `session.mode` besitzt Runtime-Autorität
- [x] Bestätigt.
- Ziel-AP: Config-Migration.
- Status: CONFIRMED.

### FIND-003 – Wake-Word-Gruppe leer
- [x] Bestätigt.
- Ziel-AP: Settings/Wake Word.
- Status: CONFIRMED.

### FIND-004 – Warnloop „Aktion derzeit nicht verfügbar“
- [x] Bestätigt.
- Ziel-AP: Client Lifecycle + Feedback.
- Status: CONFIRMED.

### FIND-005 – normaler Hotkey hat falsche Zweitbedeutung
- [x] Bestätigt.
- Der Ist-Pfad ist falsch verdrahtet. Das Ziel ist keine feste universelle
  Zweitbedeutung, sondern eine konfigurierbare Active-Aktion; besprochener
  Default des primären Hotkeys ist nicht kumulatives `refresh`.
- Ziel-AP: erst nach Plan-Freeze zuordnen.
- Status: CONFIRMED.

### FIND-006 – Source-Merge statt First-Trigger-Lock
- [x] Bestätigt.
- Ziel-AP: Server Activation.
- Aktuelle Evidence: Der neue Server-`ActivationController` antwortet auf
  den zweiten Trigger mit `merged`; die Tests
  `test_05_manual_then_wake_word_merges`,
  `test_06_wake_word_then_manual_merges` und
  `test_a_merge_does_not_raise_the_generation` schreiben dieses vom
  Zielbild abweichende Verhalten derzeit fest.
- **Nachschau (2026-08-27):** Der kanonische Serverstand implementiert die
  First-Trigger-wins-Regel; siehe `tests/unit/test_server_trigger_contract.py::test_a_second_source_is_locked_to_the_first_activation`
  (`activation_locked`, identische `activationId`).
- Status: RESOLVED durch AP-SRV-010.

### FIND-007 – Continuous Streaming nicht erreicht
- [x] Bestätigt.
- Ziel-AP: Continuous Stream.
- Status: CONFIRMED.

### FIND-008 – source-abhängige Darstellung
- [x] Bestätigt.
- Ziel-AP: UI/Feedback.
- Status: CONFIRMED.

### FIND-009 – Manual-Aufnahmefeedback fällt auf falsche Basisdarstellung zurück
- [x] Bestätigt.
- Ziel-AP: ClientMirror + UI.
- Status: CONFIRMED.

---

## Neue Funde

### FIND-010 – Neuer ActivationController kumuliert Extend-Zeit

- Datum: 2026-08-24
- Gefunden durch: Abgleich der besprochenen Refresh-Semantik mit dem
  aktuellen Server-Workspace.
- Beobachtung: `api_fastapi_server/activation.py` addiert in `extend()`
  `extension_seconds` zu `_pending_extension`. Beim Start des Follow-up-
  Timers wird dieser kumulierte Wert zum Timeout addiert. Zugehörige Tests
  bilden dieses Verhalten ab.
- Betroffene Repos/Dateien: `voice-stt-server`, insbesondere
  `api_fastapi_server/activation.py` und zugehörige Activation-Tests.
- Betroffene Entscheidung: HK-02.
- Arbeitspaket: erst nach Plan-Freeze zuordnen.
- Blockiert aktuelles Gate? NEIN; aktuell läuft noch die Planung.
- Evidence: Codefund; ältere Follow-up-Implementierung verwendet dagegen
  bereits Generationen zum Ersetzen laufender Timer.
- **Nachschau (2026-08-27):** AP-SRV-030 entfernt die kumulative
  Extend-Semantik; `refresh` folgt dem eingefrorenen nicht-kumulativen
  Timervertrag. Execution-Source: `325e55c186713069b25208871da4fef16470f85a`;
  kanonischer Abschluss: `b220dd03a594d2b9f8cad65fd279046be36864cc`.
- Status: RESOLVED (Resolved by: AP-SRV-030).

### FIND-011 – Mehrere Detection-Signale pro Wake-Word-Äußerung

- Datum: 2026-08-24
- Gefunden durch: Anwenderbeobachtung im realen Betrieb.
- Beobachtung: Ein einmal gesprochenes Wake Word kann momentan mehrere
  `wake_word_detected`-artige Signale auslösen. Benötigt wird genau ein
  verlässliches fachliches Ereignis und höchstens ein Activation-Versuch je
  Äußerung.
- Codebefund: `VoiceSTT/core/wakeword.py::process_wakeword()` liest bei
  OpenWakeWord je Aufruf nur `scores[-1]`; ein einzelner Wert oberhalb der
  gemeinsamen Sensitivity reicht für einen Treffer. Eine explizite Regel für
  mehrere aufeinanderfolgende Chunks existiert dort nicht. Treffen mehrere
  Modelle im selben Aufruf, wird der höchste Score ausgewählt.
- Ursachenbefund: `VoiceSTT/core/recording.py` setzt nach dem Treffer
  `wakeword_detected = True`, ruft `process_wakeword()` in den Folgechunks
  jedoch weiterhin ohne `not wakeword_detected`-Guard auf. Bleibt der Score
  hoch, kann `on_wakeword_detected` dadurch mehrfach gestartet werden.
- Audiotakt: Der aktuelle Recorder verarbeitet 512 Samples bei 16 kHz, also
  ungefähr 32 ms pro Chunk. Eine ungemessene Forderung nach fünf oder zehn
  Treffern würde entsprechend zusätzliche Latenz erzeugen.
- Betroffene Repos/Dateien: `voice-stt-server`, insbesondere
  `VoiceSTT/core/wakeword.py`, Recorder-Detection-State und serverseitige
  Event-/Triggeraufnahme.
- Betroffene Entscheidung: WW-04.
- Arbeitspaket: erst nach Verifikation und Plan-Freeze zuordnen.
- Blockiert aktuelles Gate? NEIN; muss vor Implementierungsplanung als
  reproduzierbarer Ist-Fall konkretisiert werden.
- Evidence: Adapter-, Chunk- und fehlender Guard im Callbackpfad bestätigt;
  Audio-/Score-Traces für eine möglicherweise zusätzlich nötige
  Fehlalarm-Bestätigungsregel noch zu ergänzen.
- Status: CONFIRMED / FALSE-POSITIVE POLICY TO MEASURE.
