# OBS-060 – V1_REGRESSION

Run: `RUN-OBS-060-01_2026-08-18`

Zwei Fragen. Erstens: verändert Logging V1 die bestehende Clientfunktion?
Zweitens: verändert **dieser Lauf** irgendetwas an dem, was OBS-010 bis OBS-050
bereits abgenommen haben?

---

## 1. Der Protokollvergleich – die harte Antwort auf die erste Frage

`WP-OBS-060` schreibt für den Runtime-Isolationsnachweis ausdrücklich einen
**Protokollvergleich** vor und begründet das: er erfasst auch Wirkungen, an die
beim Testschreiben niemand gedacht hat, und er bemerkt es, wenn später ein
Beobachtungsaufruf an eine Stelle rutscht, an der er den Ablauf verändert.

Skript: `probe_obs060_runtime_isolation.py`, Ausgabe in
`output/probe_obs060_runtime_isolation.out.txt` (exit 0).

**Aufbau.** Echter `STTController`, echte `FeedbackEngine`, echter
`DualSessionCoordinator`, echter `EventProtocolProcessor`, echter
`EventCursorStore` auf einer temporären Datei, echter `EventStreamTransport`
mit seinem echten `_dispatch`. Doubles sind ausschließlich der WebSocket
(`FakeSTTSession`) und die Ausgabegeräte (`FakeAudioCapture`,
`FakeInjectionQueue`) — genau die Freistellung, die das Work Package erlaubt.

**Ein Diktatzyklus** je Lauf: `start_dictation` → fünf Audiopakete über den
echten Hot-Path-Eingang `_on_audio_packet_from_thread` → drei Serverevents
(Cursor 5, 6, 7) durch den echten Protokollprozessor und den echten Dispatch →
ein finales Transkript über `process_raw_final_event` → `stop_dictation`.

**Aufgezeichnet werden alle beobachtbaren Wirkungen:** gesendete Frames samt
ihrer Längen, `chunks_dropped_send_queue` und `max_send_queue_depth`, die
`CommandResult`-Folge, die `FeedbackDecision`-Folge, die vollständige
Snapshotfolge (Verfügbarkeit, Diktatzustand, `reason_code`, Revision,
Fensterphase, Serverstatus), das `FinalProcessingResult`, die Injektionen, die
Textrückrufe, die Transportwechsel, die angenommenen Eventstream-Events, der
Resume-Cursor und der Inhalt der Cursordatei.

### Ergebnis

```text
[PASS] R-2 working observability:      protocol identical to R-1
[PASS] R-3 throwing ingress:           protocol identical to R-1
[PASS] R-4 throwing store:             protocol identical to R-1
[PASS] R-5 full queue:                 protocol identical to R-1
[PASS] R-6 worker never starts:        protocol identical to R-1
[PASS] R-7 throwing on_observation:    protocol identical to R-1
[PASS] R-7 der werfende Beobachter wurde wirklich gerufen        (calls=3)
[PASS] R-7 die Cursordatei trägt denselben Endstand wie R-1
[PASS] R-7 der Resume-Cursor ist derselbe wie in R-1             (7 vs 7)
[PASS] R-2 die funktionierende Observability hat den Zyklus wirklich aufgezeichnet (rows=6)
```

Das Referenzprotokoll R-1 (ohne Observability):

```json
{"command_results": [["listening", "Dictation started"], ["stopped", "Dictation stopped"]],
 "cursor_file": {"cursor": 7, "endpoint": "wss://stt.voice.marcosudau.com/ws/logs",
                 "protocol_version": 2, "schema_version": 1, "server_instance_id": "server-1"},
 "event_stream_accepted": [[5, "evt-5"], [6, "evt-6"], [7, "evt-7"]],
 "feedback": [["local_only", null], ["local_only", null], ["stt_fallback", null]],
 "finals": [["queued", null]],
 "frames": [5, [640, 640, 640, 640, 640], [0, 5]],
 "injections": ["das ist ein diktierter satz"],
 "resume_cursor": 7,
 "snapshots": [["starting","starting","initializing",1,"inactive","idle"],
               ["starting","starting","initializing",2,"inactive","listening"],
               ["starting","active","initializing",4,"waiting_first_speech","listening"],
               ["starting","idle","initializing",5,"inactive","listening"],
               ["shutting_down","idle","shutting_down",6,"inactive","listening"],
               ["stopped","idle","stopped",7,"inactive","listening"]],
 "texts": [], "transports": []}
```

Alle sechs Vergleichsläufe liefern **dieses** Protokoll, Byte für Byte.

**Eine einzige Normalisierung**, und sie ist benannt: aus der Cursordatei wird
`updated_at` entfernt. Das ist der Wanduhrzeitpunkt des Schreibvorgangs; zwei
Läufe können ihn nie teilen, und er sagt nichts über den **Endstand** aus, nach
dem das Work Package fragt. Jedes andere Feld — insbesondere `cursor: 7` — bleibt
im Vergleich.

**R-2 beweist, dass der Vergleich etwas wert ist:** die funktionierende
Observability hat sechs Records geschrieben. Ein Isolationsnachweis, bei dem gar
nichts beobachtet wird, bewiese nichts.

### Was die einzelnen Fälle wirklich kaputt machen

| Lauf | Injizierter Defekt |
|---|---|
| R-3 | ein Ingress, dessen `submit`, `event`, `observe_server_result`, `drain`, `register_aggregate_source`, `collect_aggregates` und `apply_config` **alle** werfen |
| R-4 | ein Store, dessen `write_batch` und `run_retention` bei jedem Aufruf `sqlite3.OperationalError` werfen |
| R-5 | eine Queue der Größe 1, die von Beginn an gefüllt ist |
| R-6 | ein Worker, der nie gestartet wird — die Queue wird nie geleert |
| R-7 | ein `on_observation`, das bei **jedem** Aufruf wirft (dreimal gerufen) |

## 2. Regression gegen die bestehende Testbasis

| Lauf | vor OBS-060 (`7fc6ca6`) | nach OBS-060 |
|---|---|---|
| volle Suite, `pytest` | 1137 passed / 1 failed | **1164 passed / 1 failed** |
| volle Suite, `unittest` | Ran 1138, `FAILED (errors=1)` | **Ran 1165, `FAILED (errors=1)`** |

Differenz: **exakt +27** — die 27 neuen Tests in
`tests/test_obs060_v1_hardening.py`. Der eine Fehlschlag ist in beiden Ständen
derselbe, vorbestehende, umgebungsbedingte
`ModuleNotFoundError: No module named 'lefx.interfaces'` (siehe
`V1_TEST_RESULTS.md` Abschnitt 2).

**Kein bestehender Test wurde geändert.** Das ist nachprüfbar: `git status`
nennt unter den geänderten Dateien keine einzige aus `tests/`; die einzige
Testdatei dieses Laufs ist die **neue** `tests/test_obs060_v1_hardening.py`.

## 3. Regression gegen die früheren OBS-Pakete

Die V1-Kette insgesamt:

```text
$ python -m pytest tests -q -k "obs010 or obs020 or obs030 or obs040 or obs050 or obs060"
652 passed, 513 deselected, 623 subtests passed in 50.98s      (exit 0)
```

Die Änderungen dieses Laufs berühren fünf Produktdateien der Logging-Domäne und
eine des Clients. Für jede ist geprüft, dass die zugehörigen früheren Tests
grün bleiben:

| geänderte Datei | betroffene frühere Tests | Ergebnis |
|---|---|---|
| `core/observability/worker.py` | `test_obs030_worker.py`, `test_obs030_worker_fault_injection.py`, `test_obs030_manager.py` | grün |
| `core/observability/ingress.py` | `test_obs020_ingress.py`, `test_obs020_contracts.py`, `test_obs040_*` | grün |
| `core/observability/manager.py` | `test_obs030_manager.py`, `test_obs050_settings.py` | grün |
| `core/observability/query/local.py` | `test_obs050_local_provider.py`, `test_obs050_contracts.py` | grün |
| `app.py` | `test_obs030_app_wiring.py`, `test_app.py` | grün |
| `core/audio_capture.py` (nur Kommentar) | `test_obs040_client_hooks.py`, `test_audio_capture.py` | grün |

### Eine echte Zwischenregression, gefunden und richtig behoben

Der erste Zuschnitt der N-1-Korrektur (Sink nicht bei jedem Apply neu bauen)
ließ den `sink`-Schlüssel weg, wenn sich nichts geändert hatte. Damit wurde

```text
tests/test_obs050_settings.py::TestManagerOwnershipDomain::
    test_worker_receives_retention_entry_limit_and_sink
```

rot (`KeyError: 'sink'`) — ein bestehender, gate-geprüfter Test, der das bisherige
Verhalten festhält.

Statt den Test anzupassen wurde die **Korrektur** geändert: der Manager merkt
sich die zuletzt übergebene Sinkinstanz und übergibt sie unverändert weiter,
wenn die Sinkkonfiguration gleich geblieben ist. Der Worker vergleicht nach
Identität (`new_sink is not old_sink`), also findet keine Rotation statt — und
der bestehende Test bleibt gültig, weil `sink` weiterhin in jedem Apply
mitgeliefert wird. Danach war die Suite wieder auf ihrem Baselinestand.

Das ist die Regel dieses Projekts: ein bestehender Test wird nicht geändert,
damit eine Korrektur hineinpasst.

## 4. Verhalten ohne UI

`tests/test_obs050_contracts.py` fährt in einem Subprozess einen vollständigen
Manager-Lebenszyklus ohne jeden Qt-Import und prüft anschließend, dass
`sys.modules` weder `ui.` noch `PySide6` enthält und der Record trotzdem in der
Datenbank steht. Dieser Test läuft in diesem Lauf unverändert grün: **Logging
läuft ohne UI vollständig weiter.**

## 5. Packaging

`probe_obs060_packaging.py` (Ausgabe in
`output/probe_obs060_packaging.out.txt`, exit 0):

```text
[PASS] P-1.1 alle 24 Laufzeitmodule von V1 liegen im Importgraph von app.py
             (kein hiddenimports-Eintrag nötig)
[PASS] P-1.2 die zwei reinen Protocol-Module sind korrekt NICHT im Laufzeitgraph
[PASS] P-2.1 jedes Nicht-Qt-Modul importiert in einem frischen Interpreter
[PASS] P-3.1 kein V1-Modul wird von .gitignore verborgen (OBS-050-Befund F-1)
[PASS] P-3.2 ui/logs/__pycache__ bleibt ignoriert — die Negation ist eng
[PASS] P-4   voice-stt-client.spec unverändert
[PASS] P-4   scripts/pyinstaller_runtime_platform.py unverändert
```

P-3.1 ist die Nachprüfung des OBS-050-Befunds F-1, bei dem die `.gitignore`-Regel
`logs/` einmal das komplette Paket `ui/logs/` verborgen hatte. P-1.2 hält fest,
dass `storage/base.py` und `sinks/base.py` reine `Protocol`-Dateien sind, die zur
Laufzeit niemand importiert — sie fehlen im gefrorenen Graph zu Recht.
