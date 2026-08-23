# RESULT – RUN-OBS-040-01_2026-08-17

Work Package: **OBS-040 – Server Live Adapter & Client Observation Hooks**

## Ergebnis

```text
OBS-040 IMPLEMENTED – READY FOR REVIEW
```

**Kein Gate-PASS in diesem Run.** Das Work Package verlangt einen separaten
Review in frischer Session; grüne eigene Tests sind ausdrücklich kein
Fertigstellungsnachweis.

## Was entstanden ist

### Zwei neue Produktmodule (beide in `ARCH §5.1` eingefroren vorgesehen)

- `core/observability/adapters/server_live.py` — `ServerLiveAdapter`, der
  passive Konsument des Fan-outs. Fängt selbst (`ARCH §7.3` Ebene 1), meldet an
  `LoggingInternalHealth`, fängt **nie** `BaseException`.
- `core/observability/adapters/client_events.py` — `ClientEventEmitter`, die
  eine nie werfende Grenze, durch die jede der 40 Client-Hook-Aufrufstellen
  geht.

### Der Fan-out-Hook

`core/session_coordinator.py`: `on_observation`, `_notify_observer` mit
bewusst leerem `except Exception`, je **erste Anweisung** in `_handle_event`
und `_handle_control`. Der Feedbackzweig läuft unverändert über `on_event`
weiter.

### Der zweite Beobachtungspunkt

`core/event_stream.py`: **eine** Zeile im `except`-Zweig von `run()` →
`client.eventstream.protocol_error`, ohne Rohframe (FD-R3).

### 42 Recordtypen aus `CONTRACTS §12`

Vollständige Matrix in
`40_EVIDENCE/OBS-040/RUN-01_2026-08-17/OBSERVATION_HOOK_MATRIX.md`. Alle
`S`- und `P+S`-Einträge der §12.1–§12.5 sind umgesetzt; die reinen `P`-Einträge
brauchten nichts, weil der `UnifiedLogHandler` aus OBS-020 sie ohnehin erfasst,
und ihre bestehenden `logger`-Zeilen sind unverändert.

Darunter neu und über §12 hinaus lückenschließend: `logging.record_rejected`
(Gate-Befund N-1 des OBS-030-Reviews), erzeugt an allen vier Stellen, die eine
Normalizer-Ausnahme sehen können.

### Das 5-Sekunden-Aggregat nach `ARCH §8.6`

Hot-Path-Funktionen erhöhen ausschließlich `int`-Attribute; der **Worker** liest
sie über eine read-only-Registry am Ingress und erzeugt
`client.audio.stream_stats`, Channel `performance`, Level `DEBUG`. Ein Import
`worker → core.audio_capture` wäre ein Verstoß gegen `ARCH §5.2`; die Registry
ist der einzige Weg, der `§8.6` und `§5.2` gleichzeitig hält.

### Verdrahtung

`app.py` → `run_gui`/`run_headless` → `DesktopApplication` → `CoreBridge` →
`STTController` → Session / AudioCapture / Coordinator / InjectionQueue, plus
Hotkeys, LED und Settings-Dialog. Überall additiv mit Default `NULL_INGRESS`;
der **Manager** bleibt in `app.py::main()` (`ARCH §6.2(b)`, FD-R4).

## Der wichtigste Nachweis (N-07)

> Ein WERFENDER Beobachter verändert WEDER den Rückgabewert von
> `_handle_event` NOCH den Cursorstand.

Erbracht mit dem **echten** `EventProtocolProcessor` und dem **echten**
`EventCursorStore` auf einer temporären Datei — kein Double, weil ein Double die
Cursor-Bestätigungssemantik selbst definieren würde, also genau das, was zu
beweisen ist.

```text
$ python ARBEITSDATEIEN/.../probe_obs040_end_to_end.py
[PASS] P-3 throwing observer changes neither return value nor cursor —
       returned=True, resume before/after dispatch=5/5, after confirm=6
```

Zusätzlich als Unit-Test
(`test_throwing_observer_changes_neither_return_value_nor_cursor`) und ergänzt
um `test_throwing_observer_does_not_break_control_handling` sowie
`test_base_exception_from_the_observer_is_not_swallowed`.

Die vom Work Package verlangten bestehenden Suiten laufen **unverändert** grün:
`test_session_coordinator.py`, `test_event_stream.py`,
`test_feedback_integration.py`, `test_trigger_feedback_contract.py`.

## Teststand

| Lauf | Ergebnis |
|---|---|
| `pytest tests -q` (Baseline vor dem Run) | 843 passed / 1 vorbestehender Fehlschlag |
| `pytest tests -q` (Endstand) | **958 passed** / derselbe 1 Fehlschlag |
| `unittest discover -s tests -p "test_*.py"` | Ran 959, 1 error (derselbe) |
| `pytest -k obs040` | **115 passed**, 175 subtests |
| `unittest discover -p "test_obs040_*.py"` | Ran 115, **OK** |
| `pytest -k "obs010 or obs020 or obs030 or obs040"` | 446 passed |
| Ende-zu-Ende-Probe | P-1 … P-7 **alle PASS**, exit 0 |

Differenz zur Baseline: exakt die 115 neuen Tests. Der eine Fehlschlag
(`test_ap06_followup.py`, `lefx.interfaces` fehlt in dieser Prüfumgebung) ist
vorbestehend, umgebungsbedingt und liegt außerhalb des Diffs.

**Kein bestehender Test wurde geändert** (`ARCH §12`).

## Diff

```text
16 files changed, 1324 insertions(+), 57 deletions(-)
```

Alle 57 Löschungen sind Zeilen, die im selben Diff in geänderter Form wieder
erscheinen. `git diff --check` leer. Kein Cross-Workstream-Diff.
`00_NORMATIV/` ist unverändert.

## Entscheidungen

Neun Entscheidungen, alle aus dem bestehenden Freeze auflösbar, keine
Erweiterung eines eingefrorenen Vertrags, **kein `DECISION REQUIRED`**. Liste in
`RUN_LOG.md`, Abschnitt 6; Begründungen in `OBSERVATION_HOOK_MATRIX.md`
(A-1 bis A-6) und `CONTRACT_COVERAGE.md`.

Ausdrücklich **nicht** erweitert: `LoggingHealthSnapshot`. Der Zählersatz aus
`ARCH §7.3` ist unverändert und jetzt durch einen Contract-Test fixiert — die
Lektion aus dem OBS-030-Cleanup, in dem der Zähler `dropped_failed`
zurückgenommen werden musste.

## Offene Entscheidungen

Keine.

## Offene Punkte für spätere Pakete

| Punkt | Zuständig |
|---|---|
| `self.observability.apply_config(...)` in `apply_runtime_config` (`CONTRACTS §10.4`) — in V1 existiert kein `apply_config`; die Settings-Einträge gehören nach `§10.3` in den sechsten Tab | OBS-050 |
| Übergabe des **Managers** an `DesktopApplication` (`ARCH §6.2(b)`, Befund N-4) | OBS-050 |
| Logging-Tab, LogWindow, `query/local.py`, `query/service.py` | OBS-050 |
| N-2 (`_consecutive_loop_failures` zählt die zwei Guards vor der Workerschleife mit) | OBS-060 |
| N-3 (`Manager`/`setup_logging` liegen in `app.py::main()` vor dem `try`) | OBS-060 |
| W-3-Lücke aus dem OBS-030-Gate | OBS-060 |
| Lauf gegen den echten Server `stt.voice.marcosudau.com` | OBS-060, manuelle Abnahme |

## Blocker

Keine.

## Gate-Empfehlung

Bereit für den unabhängigen Review. Empfohlene Schwerpunkte:

1. **N-07 selbst nachmessen**, nicht nur den Bericht lesen: werfender
   Beobachter gegen echten Prozessor und echten Cursorstore.
2. Die drei Signaturinspektionen prüfen
   (`app._call_with_optional_observability`,
   `ui/application.py::_request_runtime_apply`, Default-Transport-Factory) —
   sie existieren, weil bestehende Tests die alten Signaturen fixieren, und sie
   sind die unkonventionellste Stelle des Runs.
3. Die sechs benannten Abweichungen/Auslegungen A-1 bis A-6 gegen den Freeze
   nachvollziehen, insbesondere A-1 (`_fire_transport_change` statt
   `_update_transport`) und A-4 (`client.queue.state` ohne Timer).
4. Eigenständig prüfen, dass **kein** Token in der Historie landet: die Probe
   tut das über jede Zeile, aber ein eigener Lauf ist der Maßstab.
5. `git diff` auf `core/session_coordinator.py` gegen die
   Work-Package-Forderung „keine Änderung an einer bestehenden Zeile außer den
   zwei eingefügten Aufrufen" — es sind zwei weitere Zeilen, begründet in
   `DIFF_SUMMARY.md`, Abschnitt 4.

## Nächster Schritt

`OBS-040 Gate Review` in frischer Session,
`30_AUSFUEHRUNG/Prompts/OBS-040_GATE_REVIEW.md`.
