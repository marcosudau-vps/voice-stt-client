---
id: EV-OBS-040-TEST-RESULTS
run: RUN-OBS-040-01_2026-08-17
work_package: OBS-040
authority: evidence
date: 2026-08-17
---

# OBS-040 – Testergebnisse

Umgebung: Windows 11, Python 3.12.10, `QT_QPA_PLATFORM=offscreen`.
Arbeitsverzeichnis:
`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`.

## 1. Baseline vor der ersten Codeänderung

```text
$ python -m pytest tests -q
1 failed, 843 passed, 351 subtests passed in 51.47s
```

Der eine Fehlschlag ist
`tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`
mit `ModuleNotFoundError: No module named 'lefx.interfaces'` in
`core/led_controller.py:310`. Er ist umgebungsbedingt (das optionale
LEFX-Interface-Paket fehlt in dieser Prüfumgebung), war bereits vor OBS-040
vorhanden und liegt außerhalb des OBS-040-Diffs — `git diff --stat` nennt weder
diese Testdatei noch `core/led_controller.py`.

## 2. Endstand nach OBS-040

```text
$ python -m pytest tests -q
1 failed, 958 passed, 531 subtests passed in 53.82s
```

```text
$ python -m unittest discover -s tests -p "test_*.py"
Ran 959 tests in 49.060s
FAILED (errors=1)
```

Differenz zur Baseline: **exakt die 115 neuen OBS-040-Tests**
(843 + 115 = 958 unter `pytest`; 844 + 115 = 959 unter `unittest`, das die
Fehlschlag-Testmethode mitzählt). Der Fehlschlag ist derselbe wie in der
Baseline, mit identischer Ursache.

## 3. Nur OBS-040

```text
$ python -m pytest tests -q -k obs040
115 passed, 844 deselected, 178 subtests passed in 4.45s

$ python -m unittest discover -s tests -p "test_obs040_*.py"
Ran 115 tests in 2.922s
OK
```

Beide Runner, wie in OBS-030 verlangt.

## 4. Gesamte Observability-Foundation

```text
$ python -m pytest tests -q -k "obs010 or obs020 or obs030 or obs040"
446 passed, 513 deselected, 292 subtests passed in 23.28s
```

331 Tests aus OBS-010/020/030 unverändert grün, plus 115 neue.

## 5. Aufteilung der neuen Tests

| Datei | Tests | Subtests | Gegenstand |
|---|---|---|---|
| `tests/test_obs040_server_live_adapter.py` | 22 | – | Server-Live-Normalisierung, replayed/non-replayed, Eventidentität/Dedupe, Controlframes, `raw`-Identität, Adapter-Fehlerisolation, Cursorunberührtheit |
| `tests/test_obs040_fanout_hook.py` | 18 | 8 | Fan-out-Hook, **N-07** (werfender Beobachter), unabhängiges Fan-out, verbotene Hookstellen, `state_changed`, `protocol_error`, Default-Factory |
| `tests/test_obs040_client_hooks.py` | 35 | 8 | `ClientEventEmitter`, §12.1–§12.5-Hooks, Korrelationsfelder, §12.7-Nichtinstrumentierung |
| `tests/test_obs040_hot_path.py` | 14 | 9 | §8.6-Quelltextnachweis, kein per-Packet-Logging (3×1000 Ereignisse), Worker-Aggregat |
| `tests/test_obs040_failure_isolation.py` | 10 | – | Logging-Ausfall ohne Runtime-Ausfall, toter Worker, volle Queue, Feedback-Regression |
| `tests/test_obs040_contracts.py` | 16 | 153 | Modulstruktur, Importrichtung, eingefrorener Zählersatz, Verdrahtungsvertrag, Hookliste-Deckung |
| **Summe** | **115** | **178** | |

## 6. Die im Auftrag verlangten Testgegenstände

| Verlangt | Nachweis |
|---|---|
| Server-Live-Event-Normalisierung | `TestServerEventNormalisation` (8 Tests): jedes eingefrorene Feld, `segment_id` als INTEGER, Severity-Fallback, `raw`-Identität, `store_raw_payload=false`, Channel `performance` ohne `raw` |
| replayed/non-replayed | `TestReplayedAndPriority` (3): `replayed=True` → LOW, gleiche Form live → HIGH, Wasserstandsregel verwirft replayte Records nachweislich |
| Eventidentität/Dedupe | `TestEventIdentityAndDedupe` (2) + Probe P-2: Duplikat wird beobachtet, erzeugt **keine** zweite Zeile, `deduplicated` steigt; `event_id`/`server_cursor` stabil, `instance_id` einheitlich |
| unabhängiges Fan-out Feedback vs. Logging | `TestIndependentFanOut` (4): beide Zweige sehen dasselbe Objekt; ein ablehnender Feedbackzweig ändert die Beobachtung nicht; vom Runtimepfad verworfene Events werden trotzdem beobachtet |
| Logging-Observer-Ausfall ohne Runtime-Ausfall | `TestObserverFailureDoesNotAffectTheClient` (7), `TestDeadWorkerDoesNotAffectTheClient` (2), `TestAdapterFailureIsolation` (4), N-07 |
| relevante Client-Hooks | `TestSessionHooks` (9), `TestControllerHooks` (13), `TestAudioCaptureHooks` (2), `TestInjectionQueueStateHook` (1), `TestClientEventEmitter` (5) |
| Korrelationsfelder | Trigger send/ack teilen `command_id` und `correlation_id`; `client.command.requested/.completed`; `settings.apply_started/.apply_completed/.runtime_apply`; `injection:<entryId>`; `hotkey:<gen>:<token>` |
| kein per-packet Logging | `TestNoPerPacketLogging` (3): je 1000 `send_audio`, 1000 `_enqueue_audio_packet`, 1000 `_audio_callback` → **0 Records**, Zähler bewegt; `TestHotPathSourceIsClean` liest den Quelltext aller neun §8.6-Funktionen |
| Reconnect/Replay-nahe Fälle | `client.reconnect.scheduled` mit berechnetem Delay; zwei Fehlschläge hintereinander erzeugen zwei `disconnected`-Records; Replayphase → `replay_completed` → Live; `log.gap(retention)` mit Cursorbereich; Cursorunberührtheit über echten `EventCursorStore` |
| Regression Feedback/Eventstream | `tests/test_session_coordinator.py`, `tests/test_event_stream.py`, `tests/test_feedback_integration.py`, `tests/test_trigger_feedback_contract.py` **unverändert grün**; zusätzlich `TestExistingBehaviourIsUnchanged` |

```text
$ python -m pytest tests/test_session_coordinator.py tests/test_event_stream.py \
      tests/test_feedback_integration.py tests/test_trigger_feedback_contract.py -q
(alle grün, keine Datei geändert)
```

## 7. Ende-zu-Ende-Diagnoseskript

`probe_obs040_end_to_end.py` in diesem Ordner. Es benutzt den **echten**
`ObservabilityManager` mit echtem `SQLiteLogStore`, den **echten**
`EventProtocolProcessor`, den **echten** `EventCursorStore` auf einer
temporären Datei und den **echten** Fan-out-Hook. Kein Double.

```text
$ python ARBEITSDATEIEN/.../probe_obs040_end_to_end.py
[PASS] P-1 live server event stored with canonical fields — row id=4, canonical fields ok=True
[PASS] P-2 duplicate observed, no second row, deduplicated rises — rows=1, deduplicated=1, duplicate_flag=True
[PASS] P-3 throwing observer changes neither return value nor cursor — returned=True, resume before/after dispatch=5/5, after confirm=6
[PASS] P-4 client hook stored with correlation fields — command_id=cmd-probe-0001, correlation_id=trigger:cmd-probe-0001, event_id=None
[PASS] P-5 1000 packets add no row; the worker aggregate does — rows before/after 1000 packets=6/6, aggregate rows=1, chunks_captured=1000, level=DEBUG
[PASS] P-6 logging.record_rejected exists and no token is ever stored — record_rejected rows=1, no token anywhere=True
[PASS] P-7 no observability thread left after stop() — []

all checks passed
EXIT=0
```

P-6 prüft zusätzlich **jede** gespeicherte Zeile der Probe-Datenbank auf das
Token `THE-SESSION-SECRET-TOKEN`, das im `log.hello`-Payload nachweislich
enthalten war: `details_json`, `raw_json` und `message` sind über alle Zeilen
tokenfrei (R-6/FD-D5).

## 8. Git-Pflichtprüfungen

```text
$ git diff --check
(leer; nur die im Repository übliche CRLF-Hinweiszeile von Git)

$ git diff --stat
 16 files changed, 1324 insertions(+), 57 deletions(-)

$ git status --short
16 geänderte Bestandsdateien, 2 neue Produktmodule, 6 neue Testdateien,
1 neuer Evidence-Ordner, plus die vor diesem Run bereits unversionierten
Prompt-Dateien.
```

`00_NORMATIV/` erscheint in `git status --short` **nicht** — kein normatives
Dokument ist durch diesen Run verändert.

## 9. Bekannte Einschränkungen dieses Testlaufs

1. Der eine Fehlschlag (`lefx.interfaces`) ist vorbestehend und
   umgebungsbedingt; er wird in diesem Run nicht behoben, weil er außerhalb des
   Work Packages liegt.
2. Es gibt **keinen** Testlauf gegen den echten Server
   (`stt.voice.marcosudau.com`). Alle Serverframes stammen aus dem echten
   Protokollprozessor, gefüttert mit Frames nach
   `server-docs-for-client-development/`-Form. Ein Lauf gegen die reale
   Instanz gehört zur manuellen Abnahme (OBS-060).
3. Das 5-Sekunden-Intervall des Aggregats wird in den Unit-Tests durch direkten
   Aufruf von `_emit_aggregates_if_due()` geprüft, nicht durch Warten; die
   Probe P-5 wartet dagegen auf den echten Workertakt.
4. `client.queue.state` wird ereignisgetrieben und ratenbegrenzt erzeugt, nicht
   von einem Timer (Begründung in `CONTRACT_COVERAGE.md`, Punkt zu §12.4).
