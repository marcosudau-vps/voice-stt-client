# Agentenbericht – AP-CLI-000 / Run 01_BASELINE

**Status:** PASS

## 1. Ausgangslage

- Branch `feat/einheitliche-triggerarchitektur`, Start-HEAD und aktueller HEAD
  vor dieser AP-Akte: `db102fdc6dd70e4de798a363608d1e7412533dd7`.
- Working Tree vor Anlage der AP-CLI-000-Akte: sauber (die Akte selbst war
  der einzige erwartete Scope-Bestandteil, siehe `git status --short` unten).
- Verwendete Umgebung ausschließlich:
  `P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe`
  (Python 3.12.13). Keine globale Installation, keine neue venv angelegt.
- Pflichtlektüre gemäß Originalauftrag vollständig durchgeführt: `AGENTS.md`,
  `CLAUDE.md`, `CURRENT_STATE.md`, aktiver Arbeitsblock (`README.md`,
  `STATUS.md`), AP-CLI-000 `README.md`/`PLAN.md`, `PLANUNG/IMPLEMENTIERUNGSPLAN.md`
  (Abschnitt AP-CLI-000), `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md`,
  `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`, `NACHVERFOLGUNG/TRACEABILITY.md`
  sowie `PLANUNG/ANALYSEN/LEGACY_AND_DEAD_CODE_MAP.md`. `IDEEN/` wurde nicht
  gelesen.

## 2. Governanceabweichung: nachgewiesen und korrigiert

`AGENTS.md` verwies (Abschnitte „Zielarchitektur und gewünschtes Verhalten“,
„Arbeits- und Dokumentationsordnung“, Stufe-1-Leseliste, „Vor Abschluss“) auf
`docs/IMPLEMENTATION_ROADMAP.md` und
`docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`. Nachweis: `docs/` enthält
im Worktree nur `PROJEKTUEBERSICHT.md` und `RELEASE.md` sowie die
Unterordner `decisions/`, `guides/`, `observability/`; beide Dateien
existieren nicht. `git log --diff-filter=D -- <Datei>` zeigt, dass beide am
17. August 2026 in Commit `f3908cf` („chore: establish OBS-010 project
baseline and work archive“) im Zuge der ARBEITSDATEIEN-Migration nach
`ARBEITSDATEIEN/90_HISTORIE/VOR_NEUEM_ARBEITSSYSTEM/` verschoben wurden. Der
zugehörige, bereits vorhandene `<!-- BEGIN ARBEITSSTRUKTUR -->`-Block am Ende
von `AGENTS.md`/`CLAUDE.md` dokumentiert bereits das neue System
(`ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`,
`.agents/skills/arbeitsstruktur/SKILL.md`); die Migration der oberen
Quellenhierarchie-Abschnitte wurde dabei nicht nachgezogen. Historische
Dateiinhalte wurden dafür nicht geladen, nur `git log`-Metadaten.

Korrigiert (kleinstmögliche Abweichung, nur die zwei benannten toten
Verweise, keine Neuplanung):

- `AGENTS.md`: „Zielarchitektur“ zeigt jetzt auf `PLANUNG/` des aktiven
  Arbeitsblocks (Einstieg `CURRENT_STATE.md`); „Arbeits- und
  Dokumentationsordnung“ auf `.agents/skills/arbeitsstruktur/SKILL.md`;
  Stufe-1-Leseliste und „Vor Abschluss“-Checkliste entsprechend angepasst.
  Jeweils mit Datum/Commit der Verschiebung dokumentiert.
- `README.md`, `ÜBERGABE.md`, `docs/PROJEKTUEBERSICHT.md`: dieselben zwei
  Verweise auf die aktuellen Nachfolger korrigiert.

Nicht angetastet: `docs/PROJEKTUEBERSICHT.md`s Dokumentenlandkarte enthält
weitere, historisch korrekt datierte Verweise auf inzwischen ebenfalls nach
`ARBEITSDATEIEN/90_HISTORIE/` verschobene `docs/work-packages/*`- und
`docs/2026-07-*`-Belege. Das ist vorbestehende, größere Dokumentationsschuld
außerhalb der zwei im Originalauftrag ausdrücklich benannten
Governanceverweise und wird hier nicht pauschal mit repariert, um keine
großflächige Neuplanung dieses Baselinepakets auszulösen. Empfehlung für ein
späteres Dokumentationspaket, siehe Abschnitt 6.

## 3. Baseline-Testlauf und eine notwendige Baseline-Korrektur

Die Pflichtvalidierung verlangt `python -m pytest`. Der allererste Lauf
brach die gesamte Sammlung mit einem Kollisionsfehler ab:

```text
ERROR tests/test_obs010_normalizer_server.py
ModuleNotFoundError: No module named 'test_event_protocol'
```

Ursache: `tests/__init__.py` macht `tests` zu einem Package. Pytests
Standard-Importmodus (`prepend`) legt dadurch das Repository-Root statt
`tests/` selbst auf `sys.path[0]`. Der bare Import
`from test_event_protocol import (...)` in
`tests/test_obs010_normalizer_server.py` funktioniert nur unter
`unittest discover -s tests` (fügt `tests/` explizit dem Pfad hinzu), nicht
unter `pytest`. Es ist die einzige Datei mit diesem Importmuster
(`grep -rn "^from test_\|^import test_" tests/*.py` liefert genau einen
Treffer). Reproduktion vor der Korrektur:
`pytest -q --continue-on-collection-errors --collect-only` sammelte 1168
Tests plus genau diesen einen Fehler.

Minimale, reine Testinfrastruktur-Korrektur (kein Produktverhalten, kein
Zielverhalten vorweggenommen): Import auf
`from tests.test_event_protocol import (...)` geändert. Diese Korrektur ist
laut Originalauftrag Punkt 8 zulässig, weil sie eine reproduzierbare
Baselineinkonsistenz minimal behebt und die vorgeschriebene
Pflichtvalidierung (`python -m pytest`) überhaupt erst lauffähig macht.

Danach:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe -m pytest -q
1191 passed in 85.45s
```

Zweiter Lauf zur Flake-Kontrolle: `1191 passed in 82.10s`, identisch, keine
Flakes beobachtet.

## 4. Inventar: Tests und Runtimepfade je Themenfeld

Alle Zuordnungen referenzieren `NACHVERFOLGUNG/TRACEABILITY.md`-IDs und
bauen auf der bereits vorhandenen Ist-Analyse
`PLANUNG/ANALYSEN/LEGACY_AND_DEAD_CODE_MAP.md` (§16.1, §16.4, §17) auf statt
sie zu wiederholen.

### 4.1 Lokaler Dictation-/Follow-up-Lifecycle

- Code: `core/controller.py` `DictationState` (`IDLE/STARTING/ACTIVE`),
  `DictationWindowPhase` (`INACTIVE/WAITING_FIRST_SPEECH/SEGMENT_ACTIVE/
  FOLLOWUP_WAIT`), `_arm_dictation_window`/`_dictation_window_timeout`/
  `_cancel_dictation_window`, gated über `_client_owns_dictation_window`.
- Tests: `tests/test_ap06_followup.py::TestDictationWindow` (7 Tests),
  `tests/test_controller.py` (Start/Stop/Toggle-Lebenszyklus).
- Ist-Befund (siehe Dead-Code-Map §16.1): Gegen den produktiven Server, der
  `activationTriggers` meldet, ist `_client_owns_dictation_window` immer
  `False`; die lokale lokale Fensterzeitgebung ist **PARTIALLY
  DISCONNECTED/DEAD**, bleibt aber als `DictationWindowPhase`-Wert in jedem
  Snapshot sichtbar und wird von `ui/presentation.py` gelesen. Produktiv
  wirken die Serverereignisse (`recording_started`/`recording_ended`) über
  `_handle_timeline_event`.
- Zielcontract: `PHASE-01` (`idle/waiting_first_speech/segment_active/
  followup_wait/closing_input`), `PHASE-02` (`finalizing` ist kein
  Vordergrundzustand), `PHASE-03`. Fehlt aktuell vollständig: `closing_input`
  als eigene Phase sowie serverautoritatives `inputPhase`-Mirroring
  (ActivationMirror ist laut Nicht-Zielen dieses Pakets nicht vorzuziehen).
- Folge-AP: `SRV-010` (State Machine serverseitig), `CLI-010`
  (ActivationMirror, `CORE-05`).

### 4.2 `session.mode` und lokale VAD-Autorität

- Code: `core/config.py` `OperatingMode`-Enum, `SessionConfig.mode`
  (`:276`), `effective_manual_trigger_enabled`/`effective_wake_word_trigger_enabled`
  leiten sich exklusiv aus `mode` ab (`:301-310`), `presentation_mode`
  (`:325-336`); `core/controller.py:1151-1160` bestimmt `_wake_mode_desired`
  aus `session.mode`, nicht aus den Triggerflags.
- Tests: `tests/test_ap06_followup.py::TestRuntimeModeSwitchLifecycle`
  (Hotkey↔Wake-Word-Moduswechsel mit Reconnect),
  `tests/test_trigger_lifecycle.py::HotkeyRegistrationFollowsTheManualTrigger`.
- Ist-Befund: `session.mode` besitzt echte Laufzeitautorität (Dead-Code-Map
  §16.1: „**ACTIVE** (Runtime-Autorität, kein reiner Migrationsadapter)“) und
  steuert Trigger-Flags, Wake-Word-Armierung, UI-Sichtbarkeit und
  Darstellungsmodus – ein exklusiver Moduswechsel mit Reconnect statt
  gleichzeitig aktiver, getrennt suppressierbarer Quellen.
- Zielcontract: `CORE-09` „`session.mode` besitzt keine Runtime-Autorität“;
  `TRIGGER-01`/`A-06` (getrennte laufzeitweite Suppression statt Modus).
  Lokale VAD-Autorität dagegen ist bereits **erfüllt**: `grep -rin
  "vad|webrtc|silero"` über `core/`/`ui/` liefert außer einem Docstring
  keinen Treffer, `requirements.txt` enthält keine VAD-Abhängigkeit
  (Dead-Code-Map §16.1, „vollständig entfernt“); `CORE-07` ist insofern
  bereits konsistent mit dem Contract, nicht überholt.
- Folge-AP: `SRV-070`, `CLI-050`.

### 4.3 Kumulative Extension

- Code: `core/controller.py::extend_dictation_window` (`:1168-1211`),
  `self._pending_window_extension += extension` in den Zweigen `STARTING`
  und `SEGMENT_ACTIVE` (`:1188-1198`); `phase in {WAITING_FIRST_SPEECH,
  FOLLOWUP_WAIT}` addiert die Restzeit zur Extension und rearmt
  (`:1199-1205`).
- Tests: `tests/test_trigger_lifecycle.py::ContinuousStreamingInvariant::
  test_extending_the_window_creates_no_second_stream`,
  `tests/test_ap06_followup.py::TestDictationWindow::
  test_timeline_and_extension_are_bound_to_current_window`.
- Ist-Befund: Client akkumuliert `extension_seconds` clientseitig in einem
  Zeitguthaben (`_pending_window_extension`); gegen den produktiven Server
  sind laut Dead-Code-Map §16.1 nur `state == STARTING` und der `not_active`-
  Endzweig erreichbar, die übrigen Phasenzweige inklusive `trigger
  action=extend` sind **DEAD**.
- Zielcontract: §4 des Contract-Freeze – „Es gibt kein `extensionSeconds`
  und kein Zeitguthaben“; `refresh` setzt die Deadline serverseitig absolut
  (`now + followupTimeoutMs` bzw. `max(currentDeadline, now +
  segmentWatchdogRefreshMs)`), nie kumulativ. Traceability: `TIME-03`,
  `TIME-05`, `HK-02` („nie kumulativ“).
- Folge-AP: `SRV-030`, `CLI-020`.

### 4.4 Streamstart je Activation

- Code: `core/stt_session.py::send_start`/`send_stop`/`set_streaming`
  (`:622-625`, `:758-781`), `TriggerAck`, `request_trigger`/`send_trigger`,
  `supports_activation_triggers` (`:573-578`); `core/controller.py::
  _begin_stream_and_trigger` (`:809-826`).
- Tests: `tests/test_trigger_lifecycle.py` vollständig (590 Zeilen: `type=
  "trigger"`-Commands, `trigger_ack`, `activationTriggers`-Capability,
  `ContinuousStreamingInvariant`).
- Ist-Befund: Das heutige Protokoll ist ein **v1-Zwischenschritt** – eigener
  Nachrichtentyp `trigger` mit `commandId`/`accepted`/`reason`/
  `activationId`, getrennt von `start`/`stop` als Stream-Commands, mit
  Capability-Flag `activationTriggers` statt fixem `protocolVersion=2`. Das
  ist vollständig anders benannt und strukturiert als
  `PROTOKOLL_V2_WIRE_SCHEMA.md` (`activation.command`, `command.ack`,
  `result`-Enum, keine getrennten `start`/`stop`-Stream-Commands mehr). Die
  „ein Stream, viele Activations“-Invariante selbst ist konzeptionell mit
  `CORE-06`/`CORE-16` verträglich, aber am heutigen v1-Transport hängend.
  Zusätzlich (siehe Abschnitt 5) ist die Test-Invariante selbst nur wegen
  einer produktionsuntreuen Test-Doppel-Implementierung grün.
- Zielcontract: `CORE-05`, `CORE-06`, `A-04` (IDs/Idempotenz/Replay/stale),
  `A-05` (Protokoll v2, klarer Cut), `CMD-01/02/05/07/08`, `WIRE-01..13`.
- Folge-AP: `CLI-010` (v2-Transport), `AP-SRV-040` serverseitig.

### 4.5 Source-Merge

- Code: keine Client-Produktionslogik (Client sendet laut heutigem Code nur
  `source="manual"`, nie `wake_word`); Server-Timeline-Events tragen bereits
  heute `sources: [...]`-Arrays, die der Client passiv entgegennimmt.
- Tests: `tests/test_trigger_feedback_contract.py::
  ManualDuringWakeWordActivation` und `::WakeWordDuringManualActivation`
  modellieren serverseitiges Mergen einer zweiten Triggerquelle in eine
  bereits offene Activation (`sources=["wake_word", "manual"]`) und prüfen,
  dass daraus **keine zweite** Feedback-Sequenz entsteht.
- Ist-Befund: Diese Tests referenzieren explizit den überholten Merge-
  Mechanismus. Der neue Contract entfernt Source-Merge und das Öffnen einer
  neuen Activation während eines offenen Eingabefensters vollständig
  (`AP-SRV-010`-Scope: „Source-Merge und neue Activation während eines
  offenen Eingabefensters entfernen“); `CORE-02` verlangt zusätzlich, dass
  Manual/Wake Word Triggerquellen und keine Betriebsmodi sind. Nach der
  Migration kann in einer offenen Activation keine zweite Quelle mehr
  „mergen“ – First-Trigger-wins ersetzt das Merge-Verhalten.
- Zielcontract: `CORE-02`, `AP-SRV-010`-Scope, `CORE-16`.
- Folge-AP (getrennt nach Verantwortung, keine Sammelzuordnung): `SRV-010`
  für die serverseitige Source-/Admission-Semantik (Source-Merge und
  Zweitaktivierung im offenen Eingabefenster entfallen dort); `CLI-020` für
  die manuelle Command-/Hotkey-Semantik (Client sendet weiterhin nur
  `source=manual`, First-Trigger-wins ändert daran nichts); `CLI-040` für
  das source-neutrale Feedback und die hier referenzierten
  Feedback-Reducer-Tests selbst
  (`tests/test_trigger_feedback_contract.py::ManualDuringWakeWordActivation`/
  `::WakeWordDuringManualActivation`), die auf First-Trigger-wins statt
  Source-Merge umgestellt werden müssen.

### 4.6 Session-/Feedback-/Hotkey-Testhilfen

Kritische, mehrfach wiederverwendete Ist-Helfer und ihre bereits in
`PLANUNG/ANALYSEN/LEGACY_AND_DEAD_CODE_MAP.md` §17 dokumentierten,
verifizierten Abweichungen von der echten Produktionsklasse:

| Helfer | Datei | Dokumentierte Lücke (Map §17) |
|---|---|---|
| `FakeSTTSession` | `tests/test_controller.py:158` | besitzt kein `supports_activation_triggers` (Produktivserver meldet es immer) → alle damit gebauten Controllertests fahren den Nicht-Activation-Pfad; `set_streaming` setzt nicht `state.streaming_requested`; `send_start` bestätigt synchron statt über ein späteres `status`-Event |
| `TriggerCapableSession`/`StreamCountingSession` | `tests/test_trigger_lifecycle.py:217,318` | `request_trigger` antwortet immer sofort (kein Ack-Timeout/Replay/Race abbildbar); `set_streaming` bleibt produktionsuntreu (siehe Abschnitt 5) |
| `FakeAudioCapture` | `tests/test_controller.py:130` | ruft `on_audio_packet` nie auf; Audioweg/Generationsprüfung/Queue-Überlauf laufen in Controllertests nie durch |
| `FakeInjectionQueue` | `tests/test_controller.py:95` | keine echten Threads; für die Triggerarchitektur unkritisch |
| `RecordingHotkeyBackend`/`ReconfigurableFakeSTTSession` | `tests/test_ap06_followup.py:55,67` | reproduzieren echte Session-Generationswechsel für Moduswechseltests; an das überholte `session.mode`-Modell gebunden (siehe 4.2) |

Bewertung: Diese Helfer sind für die *heutige* v1-Suite brauchbar, aber alle
außer `FakeInjectionQueue` müssen für `CLI-010` (v2-Transport,
ActivationMirror) durch produktionsgetreuere Doubles ersetzt oder ergänzt
werden. Keine Änderung in diesem Baselinepaket – reine Charakterisierung.

## 5. Ergänzter Charakterisierungstest

`tests/test_ap_cli_000_baseline_characterization.py` (neu, 1 Test) macht
einen in der Dead-Code-Map bereits benannten, aber nicht mehr reproduzierbar
vorhandenen Befund erneut nachweisbar (§17.2, Fund 7 verweist auf ein
inzwischen aus dem Repository entferntes Diagnoseskript `repro_stream.py`):

- Reale `STTSession.set_streaming` (`core/stt_session.py:622-625`) setzt
  neben `_streaming` auch `state.streaming_requested`.
- `StreamCountingSession` (`tests/test_trigger_lifecycle.py`) überschreibt
  `send_start`/`send_stop`, aber nicht `set_streaming` – es erbt die
  unvollständige Fake-Implementierung, die `state.streaming_requested`
  nie zurücksetzt.
- `core/controller.py::_stop_dictation_locked` ruft
  `self.session.set_streaming(False)` (`:1118`) **unconditional**, auch auf
  dem `_server_owns_activation`-Zweig, dessen Inline-Kommentar
  (`:1123-1125`) behauptet, der Stream bleibe absichtlich bestehen.

Mit einem `set_streaming`, das den echten Seiteneffekt nachbildet, zeigt der
neue Test reproduzierbar: Nach `finish` der ersten Activation ist
`streaming_requested` `False`, wodurch `_begin_stream_and_trigger`
(`core/controller.py:815`) bei der zweiten Activation erneut `send_start()`
aufruft (`stream_starts == 2` statt `1`). Das widerspricht der von
`ContinuousStreamingInvariant` behaupteten Invariante „ein Stream, viele
Activations“ – diese Suite kann den Widerspruch nicht sehen, weil ihr
eigenes Double den Seiteneffekt nicht nachbildet.

Der neue Test ändert **keinen** Produktcode und entscheidet nicht, ob der
Kommentar oder das Flag der beabsichtigte Zielzustand ist; das ist unter
dem v2-Transport (`CLI-010`) zu klären, wo `streaming_requested` durch
serverautoritatives `inputPhase` ersetzt wird. Er ist rein additiv und lief
zusammen mit der Gesamtsuite grün (siehe Abschnitt 7).

## 6. Empfehlung für ein späteres Dokumentationspaket

Außerhalb des Scopes dieses Baselinepakets: `docs/PROJEKTUEBERSICHT.md`s
Dokumentenlandkarte referenziert weitere historische `docs/work-packages/*`-
und datierte `docs/2026-07-*`-Belege, die ebenfalls bereits nach
`ARBEITSDATEIEN/90_HISTORIE/` verschoben wurden. Diese sind als „historische
Belege“ gekennzeichnet und verletzen damit nicht dieselbe Governanceregel
wie die zwei aktiv als verbindlich referenzierten Dateien, sollten aber bei
Gelegenheit bereinigt werden.

## 7. Validierung

```powershell
& '...\main\venv\Scripts\python.exe' -m pytest -q tests/test_trigger_lifecycle.py tests/test_trigger_feedback_contract.py tests/test_ap06_followup.py tests/test_ap_cli_000_baseline_characterization.py tests/test_controller.py tests/test_stt_session.py
# 164 passed in 7.41s

& '...\main\venv\Scripts\python.exe' -m pytest -q
# 1192 passed in 80.81s (0:01:20)

git diff --check
# kein Output, Exit 0

git status --short
# nur AP-eigene und in diesem Bericht genannte Dateien
```

Zweifacher voller Suite-Lauf vor der Charakterisierungsergänzung: `1191
passed` / `1191 passed`, keine Flakes. Nach Ergänzung: `1192 passed`
(einmal einzeln für den neuen Test, einmal in der Gesamtsuite).

## 8. Implementiert/charakterisiert (Zusammenfassung)

- Baseline reproduzierbar: 1192 Tests grün auf Start-HEAD, zweimal ohne
  Flake.
- Eine reproduzierbare Baselineinkonsistenz minimal behoben (pytest-
  Importkollision in `tests/test_obs010_normalizer_server.py`).
- Ein neuer deterministischer Charakterisierungstest für einen zuvor nur
  durch ein nicht mehr vorhandenes Diagnoseskript belegten Ist-Befund.
- Sechs geforderte Themenfelder (4.1–4.6) vollständig inventarisiert und
  Contractabschnitten/Traceability-IDs/Folge-APs zugeordnet, aufbauend auf
  der bestehenden Ist-Analyse statt sie zu duplizieren.
- Zwei stale Governanceverweise nachgewiesen und in den tatsächlich davon
  betroffenen kanonischen Dokumenten korrigiert.
- Kein v2-Transport, kein ActivationMirror, keine sonstige Zielverhaltens-
  Vorwegnahme; keine Serverdatei verändert.

## 9. Geänderte/neue Dateien in diesem AP

- `tests/test_obs010_normalizer_server.py` (Importkorrektur)
- `tests/test_ap_cli_000_baseline_characterization.py` (neu)
- `AGENTS.md`, `README.md`, `ÜBERGABE.md`, `docs/PROJEKTUEBERSICHT.md`
  (Governanceverweise korrigiert)
- `task.md` (Baseline-Zusatzabschnitt)
- `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/ARBEITSPAKETE/AP-CLI-000/runs/01_BASELINE/REPORT.md`
  (dieser Bericht)
