# STATUS – Einheitliche serverseitige Triggerarchitektur

> Permanenter Recovery-Checkpoint. Diese Datei muss allein ausreichen, um die
> Arbeit ohne Chatverlauf zu übernehmen.

**Letzte Aktualisierung:** 2026-08-14, nach den Restarbeiten R1–R8
**Gesamtstatus:** `PARTIAL` – GATE 5 und GATE 10 sind
`MANUAL VALIDATION REQUIRED`, alle übrigen Gates sind `PASS`
**Bearbeiter:** Claude (Opus 5), eigener Arbeitsbereich
**Normative Spezifikation:**
`P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur\.gemini\001_Verbindlicher Ausführungsauftrag – Einheitliche serverseitige Triggerarchitektur.md`
(READ ONLY, nur als Quelle gelesen)

---

## 1. Ziel

Aufhebung der zwei Betriebsmodi (Hotkey / Wake Word). Zielzustand:

- genau eine STT-Session pro Clientverbindung
- genau ein kontinuierlicher Audiostream
- genau eine serverseitige Aktivierungszustandsmaschine (`ActivationController`)
- genau eine Recorder-/VAD-/Transkriptionspipeline
- zwei unabhängig aktivierbare Triggerquellen: `manual`, `wake_word`
- `false/false` wird auf Konfigurationsebene abgelehnt

---

## 2. Arbeitsbereiche

### Eigener Arbeitsbereich (schreibend)

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude
├── voice-stt-server
├── voice-stt-client
├── led_controller_respeaker-v3
└── zusammenarbeit\aktionen\einheitliche-triggerarchitektur
```

### Eingefrorener Fremdstand (READ ONLY, nie verändert)

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur
```

Dieser Pfad ist die Quelle des übernommenen Arbeitsstands des vorherigen
Agenten und wird von mir ausschließlich lesend benutzt.

### Aufbau des eigenen Arbeitsbereichs

Die drei Repositories wurden **nicht** als Worktree-Kopie übernommen, sondern
per `git clone --no-hardlinks` aus den jeweiligen Hauptrepositories unter
`P:\GithubRepos\marcosudau-vps\<repo>` neu erzeugt und auf denselben Branch
`feat/einheitliche-triggerarchitektur` gesetzt. Anschließend wurden die
relevanten tracked und untracked Arbeitsstände dateiweise byteidentisch
übertragen. `temp_pytest/` wurde bewusst **nicht** übernommen (reiner
Testlaufmüll).

Verifikation der Übernahme (AP0): `git diff HEAD` und die Dateilisten aus
`git diff --name-only HEAD` + `git ls-files --others --exclude-standard`
sind zwischen Quelle und eigenem Arbeitsbereich für alle drei Repositories
**identisch**. Nachweis in `VALIDATION.md`, GATE 0.

---

## 3. Repositories, Branches, Baselines

| Repository | Branch | INITIAL_HEAD | Baseline lt. Auftrag | Zustand bei Übernahme |
| --- | --- | --- | --- | --- |
| voice-stt-server | feat/einheitliche-triggerarchitektur | `13c162950b944dc715fdd81983a7465f8eb0fd79` | `13c1629…` (identisch) | dirty (5 tracked geändert, 6 untracked relevant) |
| voice-stt-client | feat/einheitliche-triggerarchitektur | `178d32bdf17d4709307e7a2a944888d2cf294e42` | `178d32b…` (identisch, Feedback-Fix enthalten) | dirty (7 tracked geändert) |
| led_controller_respeaker-v3 | feat/einheitliche-triggerarchitektur | `aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0` | `aa2f14b…` (identisch) | **clean** – keinerlei Vorarbeit |

`git log -1 --oneline` bei Übernahme:

```text
voice-stt-server            13c1629 docs(archive): close build deployment action
voice-stt-client            178d32b fix(feedback): debug LED and sound feedback
led_controller_respeaker-v3 aa2f14b revert(tests): restore the full assertion on the offered outputs
```

**Fremde Änderungen:** keine. Der gesamte Dirty-Stand in Server und Client
stammt nachweislich aus dem Triggerarchitektur-Umbau des vorherigen Agenten
(alle geänderten Dateien liegen im Scope der Aktion). Im LED-Repository
existiert kein Dirty-Stand, also auch keine Abgrenzungsfrage.

**Git-Verbot:** Es wird während des gesamten Auftrags nicht committet, nicht
gepusht, nicht gemergt, nicht gerebased und nicht getaggt. Sämtliche Arbeit
bleibt uncommitted. `INITIAL_HEAD == FINAL_HEAD` ist Abnahmekriterium.

---

## 4. Übernommener Arbeitsstand (Dateien)

### voice-stt-server – tracked geändert

```text
VoiceSTT/audio_recorder.py        +22   Gate-API auf dem Recorder
VoiceSTT/core/initialization.py    +2   Gate-Attribute initialisieren
VoiceSTT/core/recording.py        +12/-4 VAD-Startbedingung über Gate-Funktion
api_fastapi_server/server.py     +259   Activation-Config, Triggerbefehl, Verdrahtungsansätze
docs/.archiv/README.md             +1   Registereintrag
```

### voice-stt-server – untracked neu

```text
VoiceSTT/core/activation_control.py                       96 Z.  Recorder-Gate (Modulfunktionen)
api_fastapi_server/activation.py                         233 Z.  ActivationController
tests/unit/test_recorder_activation_control.py           213 Z.
tests/unit/test_server_activation_controller.py          260 Z.
tests/unit/test_server_controlled_e2e.py                 222 Z.
tests/unit/test_server_trigger_contract.py               192 Z.
docs/.archiv/einheitliche_triggerarchitektur/2026-08-12_…_PLAN.md
```

### voice-stt-client – tracked geändert

```text
core/config.py              +53/-11  SessionConfig Triggerflags + query_parameters
core/controller.py          +16/-2   send_trigger statt send_start/send_stop
core/settings_metadata.py   +12      zwei neue Settingdefinitionen
core/stt_session.py         +29      send_trigger, supports_activation_triggers
ui/settings_dialog.py       +18/-2   Sonderbehandlung der beiden Checkboxen
tests/test_config.py        +25      AP6-Migrationstests
tests/test_stt_session.py   +15      send_trigger-Test
```

### led_controller_respeaker-v3

Keine Vorarbeit. Laut Auftrag §5 sind Produktcodeänderungen dort auch nicht
vorgesehen.

---

## 5. Klassifikation der Vorarbeit

Vollständige Begründungen in `DECISIONS.md`. Kurzfassung:

| Datei / Baustein | Klassifikation | Entscheidung |
| --- | --- | --- |
| `VoiceSTT/core/activation_control.py` | PARTIAL | KORRIGIEREN |
| `VoiceSTT/audio_recorder.py` (Gate-API) | IMPLEMENTED BUT UNVERIFIED | BEHALTEN |
| `VoiceSTT/core/initialization.py` | IMPLEMENTED BUT UNVERIFIED | BEHALTEN |
| `VoiceSTT/core/recording.py` (Gate-Aufruf) | IMPLEMENTED BUT UNVERIFIED | BEHALTEN |
| `api_fastapi_server/activation.py` | PARTIAL | KORRIGIEREN |
| `server.py` – Query-/Config-Parsing | **NOT WIRED** | KORRIGIEREN |
| `server.py` – `handle_trigger_command` | PARTIAL | KORRIGIEREN |
| `server.py` – Timeout/Scheduler | **NOT STARTED** | ERGÄNZEN |
| `server.py` – Activation-Events | **NOT STARTED** | ERGÄNZEN |
| `server.py` – Capability | **NOT STARTED** | ERGÄNZEN |
| `tests/unit/test_server_controlled_e2e.py` | **FALSE POSITIVE** | VERWERFEN/ERSETZEN |
| `tests/unit/test_server_trigger_contract.py` | PARTIAL | KORRIGIEREN |
| `tests/unit/test_server_activation_controller.py` | IMPLEMENTED BUT UNVERIFIED | BEHALTEN + ERGÄNZEN |
| `tests/unit/test_recorder_activation_control.py` | PARTIAL | KORRIGIEREN |
| Client `core/config.py` | **FEHLERHAFT** | KORRIGIEREN |
| Client `core/controller.py` | **FEHLERHAFT** | KORRIGIEREN |
| Client `core/stt_session.py` | PARTIAL | KORRIGIEREN |
| Client `tests/test_config.py` (AP6) | **FALSCHE ERWARTUNG** | KORRIGIEREN |
| Client `ui/settings_dialog.py` | PARTIAL | KORRIGIEREN |

---

## 6. Belegte Kernbefunde aus AP0

Diese Befunde sind selbst verifiziert (Fundstellen in `VALIDATION.md`):

1. **Controlled-Modus ist im Produktionspfad tot.**
   `parse_session_activation_query()` (server.py:950) und
   `resolve_session_activation_config()` (server.py:992) besitzen **null**
   Produktionsaufrufer. `admit_session()` (server.py:4262) reicht kein
   `activation_config` durch, der WebSocket-Einstieg
   `/ws/transcribe` (server.py:7061) parst die Triggerparameter nicht.
   Damit ist `self._activation` in Produktion **immer** `None` und
   `handle_trigger_command` antwortet real immer mit
   `controlled_activation_disabled`.

2. **Kein Timeout wirkt.** `ActivationController.expire()` besitzt keinen
   einzigen Produktionsaufrufer. `_activation_timer_generation` wird gesetzt,
   aber nie gelesen. Eine geöffnete Activation schließt sich nie von selbst;
   das Gate bliebe dauerhaft offen.

3. **Keine Capability.** `session_capabilities()` (server.py:4608) meldet nur
   `wakeWord`. `activationTriggers` existiert nicht. Der Client prüft in
   `STTSession.supports_activation_triggers` genau auf diesen Schlüssel und
   erhält damit **immer** `False` – der gesamte neue Clientpfad ist tot.

4. **Keine Activation-Events.** `activation.manual_accepted`,
   `activation.extended`, `activation.closed` werden nirgends erzeugt.

5. **Client bricht den Stream-Lifecycle.** `controller.py:610` ersetzt
   `session.send_start()` durch `send_trigger(activate)` und `controller.py:904`
   `session.send_stop()` durch `send_trigger(finish)`. Das verletzt §3 des
   Auftrags („`start` und `stop` bleiben ausschließlich Streambefehle") und
   würde den Audiostream nie starten.

6. **Client migriert falsch.** `SessionConfig.effective_manual_trigger_enabled`
   liefert bei `manual_trigger_enabled is None` unabhängig vom Altmodus `True`.
   Für `mode=wake_word` ergibt das `manual=true / wake_word=true` – die vom
   Auftrag §11.6 ausdrücklich verbotene implizite Migration nach `true/true`.
   Der mitgelieferte Test `test_legacy_wake_word_mode_migrates_query_parameters`
   **zementiert diesen Fehler** als Sollverhalten.

7. **Kein `trigger_ack`-Konsum im Client.** `send_trigger` ist fire-and-forget;
   es existiert keine Pending-Command-Verwaltung und keine Ack-Auswertung.
   Damit ist §20 („Kein fachliches Accepted-Feedback vor Ack") nicht erfüllbar.

8. **Angeblicher E2E-Test ist ein False Positive.**
   `test_server_controlled_e2e.py::test_04_controlled_session_timeout_expires_gate`
   kommentiert „Wait for timeout to fire in background timer thread", ruft dann
   aber selbst `expire()` **und** `close_controlled_activation()` auf und prüft
   anschließend, dass das Gate geschlossen ist. Der Test beweist ausschließlich,
   dass der Test selbst schließt. Keine der vier neuen Serverdateien benutzt
   einen echten WebSocket/TestClient-Einstieg.

---

## 7. Testlage bei Übernahme

Siehe `VALIDATION.md`. Baseline-Läufe der drei Suiten wurden gestartet;
Ergebnisse werden dort protokolliert.

---

## 8. Aktueller Stand

**Letzte Aktualisierung:** nach den Restarbeiten R1–R8.

| Gate | Thema | Status |
| --- | --- | --- |
| 0 | Recovery, Baseline, Ist-Verträge | **PASS** |
| 1 | Recorder Activation Gate | **PASS** |
| 2 | ActivationController | **PASS** |
| 3 | WebSocket-Triggervertrag | **PASS** |
| 4 | Serverintegration Trigger → Gate → Recording | **PASS** |
| 5 | Server bereit für alten und neuen Client | **MANUAL VALIDATION REQUIRED** |
| 6 | Konfigurationsmigration | **PASS** |
| 7 | Client-Lifecycle | **PASS** |
| 8 | Cross-Project Feedbackvertrag | **PASS** |
| 9 | Cross-Repository-Regressionsabnahme | **PASS** |
| 10 | Build und reale E2E-Abnahme | **MANUAL VALIDATION REQUIRED** |
| 11 | Dokumentation, Git und Abschluss | **PASS** |

Der maßgebliche Nachweisstand steht in `VALIDATION.md`.

### Testmengen (korrekt vorbereitetes Environment)

```text
voice-stt-server              siehe REPORT.md, finale Zahlen
voice-stt-client              siehe REPORT.md, finale Zahlen
led_controller_respeaker-v3   1506 passed, 23 skipped, 0 failed
```

Alle 23 LED-Skips stammen aus `tests/device/`: 21-mal ist ein ReSpeaker
angeschlossen, aber nicht zugreifbar (`Access denied`), zweimal wird eine
Person am Kabel verlangt.

### Umgesetzte Kernänderungen

**Server** – Query-Parsing im WebSocket-Einstieg und Durchreichen über
`admit_session` (damit ist der Controlled-Modus erstmals produktiv erreichbar),
generationsgebundener Activation-Timer, Rückwärtspfad
`recording_started`/`recording_ended`, Wake Word über denselben Controller und
dasselbe Gate, Abschaltung des Legacy-Wakeword-Follow-ups im Controlled-Modus,
Activation-Events, Korrelationsfelder auf allen Timeline-Events, Capability
`activationTriggers` erst nach vollständiger Verdrahtung, Reset bei
Stream-Stop/Close/Clear.

**Recorder** – Generationsbindung des Gates, `abort`/`shutdown` schließen es
produktiv mit.

**ActivationController** – `generation` von `version` getrennt,
`finalizing`-Phase, interne `RLock`-Synchronisierung, `finalized()`.

**Client** – `start`/`stop` wieder als Streambefehle, Trigger additiv,
`trigger_ack`-Konsum mit Pending-Verwaltung und Generationsbindung, kein
Accepted-Feedback vor dem Ack, korrekte Migration ohne `true/true`,
Betriebsmodus überall durch die Triggerflags ersetzt, Hotkeys nur bei aktivem
Manualtrigger.

**Browserclient** – auf den aktuellen Vertrag korrigiert (Pfad `/ws/transcribe`,
`start`, `final` statt `fullSentence`, vollständige Audiometadaten);
`index.html` bereinigt.

### Gefundene echte Defekte

1. **Controlled-Modus war produktiv unerreichbar** (AP0-Befunde B-1 bis B-3).
2. **Activation-Timeout wurde endgültig verworfen**, wenn `Event.wait()` unter
   Windows geringfügig zu früh zurückkehrte.
3. **Verbotene `true/true`-Migration** im Client, per Test festgeschrieben.
4. **Zweite Follow-up-Autorität** im Server.
5. **Manual-Accepted-Feedback wäre entfallen** (selbst verursacht, selbst
   gefunden).
6. **Ab der zweiten Activation lief der Startversuch in den Timeout**, weil die
   Bestätigung an einem Statuswechsel hing, den nur `start` auslöst (durch den
   Continuous-Streaming-Test gefunden).
7. **Browserclient sprach ein nicht mehr existierendes Protokoll.**

### Anti-False-Positive-Nachweise

Für jeden kritischen Mechanismus ist per Mutationstest belegt, dass die Tests
ihn wirklich prüfen: `evidence/ap2|ap4|ap7|ap8_mutation_check.txt` sowie
`evidence/r1_collision_mutation.txt`, `r2_streaming_mutation.txt`,
`r3_browser_mutation.txt`. Dabei wurden zweimal Schwächen der **eigenen** Tests
gefunden und geschlossen.

---

### Cleanup-Schritt (nach R8)

Die technische Implementierung ist für die parallele manuelle Endabnahme
**eingefroren**. Seitdem wurden ausschließlich Dokumentation und Nachweislogik
angefasst:

- veraltete Aussagen zu Browserclient, LED-Simulator, ReSpeaker und Build
  bereinigt;
- ein von mir selbst verursachter Whitespace-Fehler in `ADR-001` entfernt;
- der Evidence-Collector prüft jetzt echte Exitcodes und wurde in beide
  Richtungen nachgewiesen;
- der finale Build wurde vollständig vom Antigravity-Arbeitsbereich isoliert;
- der Quellschutz ist zusätzlich bytegenau über SHA-256 belegt.

**Kein Produktcode, keine Config und keine Testimplementierung wurden dabei
verändert.**

## 9. Konkreter nächster technischer Schritt

Die Softwarearbeit ist abgeschlossen. Offen sind ausschließlich die manuellen
Abnahmen:

1. **GATE 5 / M-B1** – Browserclient im echten Browser prüfen.
2. **GATE 10 / M-1 bis M-6** – Pflichtmatrix mit echter Sprache, Countdown,
   Reconnect, Serverneustart, LED-Simulator und ReSpeaker.

Für den ReSpeaker gilt der präzisierte Befund: Das Gerät **ist angeschlossen**,
die Gerätetests scheitern an fehlenden Zugriffsrechten. Die LED-Gerätetests
daher mit ausreichenden Rechten wiederholen und die zwei interaktiven Tests mit
`LEFX_INTERACTIVE=1` ausführen.

Erst danach dürfen GATE 5 und GATE 10 auf PASS gesetzt und der Gesamtstatus von
`PARTIAL` auf `DONE` geändert werden.

### Wiedereinstieg

Nichts ist committet; der Working Tree enthält den vollständigen Stand.
Umgebungsvorgaben für Testläufe:

```text
PYTHONPATH = <scratchpad>/pyenv                  WMI-Workaround für torch
pytest      --basetemp=<scratchpad>/pytest-tmp   PermissionError auf %TEMP%
```

Für die LED-Suite zusätzlich einmalig `python scripts/build_effects.py` im
eigenen LED-Clone ausführen und die drei `packages/*/src`-Verzeichnisse auf den
`PYTHONPATH` legen. Für den Clientbuild ebenso `lefx` aus dem eigenen Clone
auflösen.

---

## 10. Offene Risiken

- Der Umfang des Auftrags (AP0–AP11, drei Repositories, realer Hardwaretest)
  ist groß; AP10 verlangt Hardware- und Buildabnahmen, die in dieser Umgebung
  nicht vollständig durchführbar sind. Diese werden ausdrücklich als
  `MANUAL VALIDATION REQUIRED` mit konkreter Testanweisung ausgewiesen und
  **nicht** als PASS behauptet.
- Der übernommene Stand enthält Tests, die falsches Verhalten festschreiben.
  Diese werden korrigiert, nicht übernommen.
