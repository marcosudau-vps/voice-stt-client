---
id: EV-OBS-040-DIFF-SUMMARY
run: RUN-OBS-040-01_2026-08-17
work_package: OBS-040
authority: evidence
date: 2026-08-17
---

# OBS-040 – Diff-Zusammenfassung

```text
$ git diff --stat
 16 files changed, 1324 insertions(+), 57 deletions(-)
```

Alle 57 Löschungen sind Zeilen, die im selben Diff in geänderter Form wieder
erscheinen (Signaturen, Aufrufstellen, ein umgebautes `_reject_command`). Keine
Zeile wurde entfernt, ohne ersetzt zu werden; kein bestehendes Verhalten ist
gelöscht. Die Einzelnachweise stehen unten je Datei.

## 1. Neue Produktmodule

| Datei | Zeilen | Inhalt |
|---|---|---|
| `core/observability/adapters/server_live.py` | 89 | `ServerLiveAdapter` – der passive Konsument des Fan-outs (`ARCH §5.1`, `§7.3` Ebene 1) |
| `core/observability/adapters/client_events.py` | 102 | `ClientEventEmitter` – die eine nie werfende Grenze, durch die jede Hook-Aufrufstelle geht (`ARCH §5.1`) |

Beide Module und Klassennamen stehen wörtlich in der eingefrorenen
Modulstruktur `ARCH §5.1`; OBS-040 legt sie an, es erfindet sie nicht.

## 2. Geänderte Bestandsdateien

| Datei | +/− | Art der Änderung |
|---|---|---|
| `core/session_coordinator.py` | +59/−2 | **Der Fan-out-Hook.** `on_observation`, `_notify_observer`, je eine erste Anweisung in `_handle_event`/`_handle_control`, `client.eventstream.state_changed`, Default-Factory für den Transport |
| `core/event_stream.py` | +23/−0 | **Zweiter Beobachtungspunkt.** Optionales `observability`-Keyword, `_observe_protocol_error`, **eine** Zeile im `except`-Zweig von `run()` |
| `core/stt_session.py` | +154/−0 | §12.1/§12.2-Hooks (websocket connecting/connected/disconnected, session admitted/ready, reconnect scheduled, trigger sent/ack_received/ack_dropped, stream start_sent) + zwei Hot-Path-`int`-Zähler und `send_counters()` |
| `core/controller.py` | +299/−7 | Konstruktorinjektion, `ServerLiveAdapter`-Verdrahtung, Zählerquelle für das Aggregat, §12.1–§12.5-Hooks (run_started, dictation start_attempt/confirmed/failed/interrupted, action.blocked, settings.runtime_apply, config.validation_failed, injection enqueued/rejected, final.deduplicated, server.error_classified) + zwei Send-Queue-Zähler |
| `core/audio_capture.py` | +62/−1 | Optionales `observability`, `client.audio.stream_started/.stream_stopped`, vier Hot-Path-`int`-Zähler, `capture_counters()` |
| `core/text_injector.py` | +59/−1 | Optionales `observability`, `client.queue.state` (aggregiert, ratenbegrenzt), zwei Jobzähler |
| `core/observability/ingress.py` | +147/−5 | `emit_record_rejected` (N-1), Aggregatquellen-Registry (`ARCH §8.6`), `NullIngress`-Gegenstücke |
| `core/observability/worker.py` | +79/−1 | `_emit_aggregates_if_due`/`_build_aggregate_record` – der Worker liest die Zähler und erzeugt `client.audio.stream_stats` |
| `core/observability/adapters/python_logging.py` | +20/−4 | `_handle_exception`: `handleError` plus der von `ARCH §8.3` verlangte Ersatzrecord |
| `core/observability/__init__.py` | +4/−0 | zwei Re-Exports |
| `ui/application.py` | +152/−6 | `client.app.started/.stopping`, `settings.apply_started/.apply_completed`, `feedback.decision`, `sound.failed`, Weitergabe des Ingress an Bridge/Hotkeys/LED/Dialog, `run_gui(observability=…)` |
| `ui/core_bridge.py` | +160/−26 | `client.core.thread_started/.thread_stopped`, `client.command.requested/.completed` mit gemeinsamer `correlation_id`, Default-Controller-Factory |
| `ui/hotkeys.py` | +22/−0 | `client.hotkey.pressed` (§12.2: *„heute völlig ungeloggt"*) |
| `ui/led_feedback.py` | +28/−0 | `client.led.dispatch_failed`, `client.led.queue_overflow` |
| `ui/settings_dialog.py` | +21/−0 | `client.config.validation_failed` (Dialogseite) |
| `app.py` | +35/−4 | Der Ingress erreicht `run_gui`/`run_headless`; der **Manager** bleibt in `main()` (ARCH §6.2(b)) |

## 3. Neue Testdateien

| Datei | Zeilen | Tests |
|---|---|---|
| `tests/test_obs040_server_live_adapter.py` | 539 | 22 |
| `tests/test_obs040_fanout_hook.py` | 598 | 18 |
| `tests/test_obs040_client_hooks.py` | 706 | 35 |
| `tests/test_obs040_hot_path.py` | 360 | 14 |
| `tests/test_obs040_failure_isolation.py` | 248 | 10 |
| `tests/test_obs040_contracts.py` | 365 | 16 |

**Kein bestehender Test wurde geändert** (`ARCH §12`). `git status --short`
zeigt keine Testdatei als `M`.

## 4. `session_coordinator.py` im Detail

Der Auftrag verlangt: *„`git diff` zeigt in `session_coordinator.py` KEINE
Änderung an einer bestehenden Zeile außer den zwei eingefügten Aufrufen."*

Tatsächlich geändert sind **zwei** bestehende Zeilen, beide in der
Konstruktorsignatur bzw. deren Zuweisung:

```diff
-        transport_factory: TransportFactory = EventStreamTransport,
+        transport_factory: Optional[TransportFactory] = None,
...
-        self._transport_factory = transport_factory
+        self._transport_factory: TransportFactory = transport_factory or (
+            lambda config, access, processor, **kwargs: EventStreamTransport(
+                config, access, processor, observability=observability, **kwargs
+            )
+        )
```

**Begründung, warum das nötig und die kleinstmögliche Abweichung ist.** Der
zweite Beobachtungspunkt liegt laut `CONTRACTS §7.5` in
`EventStreamTransport.run()` und braucht dort einen Ingress. Der Transport wird
ausschließlich vom Coordinator über `self._transport_factory(...)` gebaut. Ein
zusätzliches Keyword an *dieser Aufrufstelle* hätte die eigene Factory des
bestehenden Tests `tests/test_session_coordinator.py::FakeEventTransport`
gebrochen, deren `__init__` genau sechs Parameter hat — und damit die Regel
„kein bestehender Test wird geändert". `CONTRACTS §6` löst genau dieses Problem
für `CoreBridge` mit einer **Default-Factory** und begründet es dort mit
demselben Argument; OBS-040 überträgt das Muster wortgleich. Eine von außen
übergebene Factory wird weiterhin exakt sechsstellig aufgerufen (Test
`TestTransportFactoryInjection.test_an_external_factory_is_still_called_with_six_arguments`),
und der Standardwert `EventStreamTransport` bleibt semantisch erhalten:
`transport_factory=None` erzeugt denselben Transport, nur mit Ingress.

Alle übrigen Änderungen dieser Datei sind reine Ergänzungen: der
`on_observation`-Slot, `_notify_observer`, die zwei eingefügten Aufrufe, der
`state_changed`-Block in `_handle_state` (nach `_set_context`, also nach dem
Runtime-Übergang) und zwei Importe.

## 5. Kein Cross-Workstream-Diff

Alle 16 geänderten Dateien liegen im Client-Produktbaum und sind entweder in
`CONTRACTS §12` als Hookstelle oder in `CONTRACTS §6`/`§7` als Verdrahtungsort
benannt. Nicht berührt:

- `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/**` – byte-identisch
- Server-Workspace und LED-Workspace – nur lesend verwendet
- `core/led_controller.py`, `core/history.py`, `core/config.py`,
  `core/event_models.py`, `core/event_protocol.py`, `core/event_normalizer.py`,
  `core/feedback_reducer.py`, `core/feedback_mapping.py`,
  `core/settings_metadata.py`, `core/actions.py`, `core/version.py`,
  `core/reinsertion.py`, `core/logging_setup.py`, `ui/tray.py`,
  `ui/overlay.py`, `ui/feedback.py`, `ui/presentation.py`,
  `ui/single_instance.py` – unverändert

`core/config.py` bleibt insbesondere deshalb unverändert, weil der dortige
`client.config.validation_failed`-Anteil laut `ARCH §6.2(a)` ohnehin verloren
ist (der Manager kann nicht vor `AppConfig.load()` starten) und weil ein
Modul-Singleton dort durch `CONTRACTS §6` ausdrücklich verboten ist. Siehe
`CONTRACT_COVERAGE.md`.

## 6. `git diff --check`

```text
$ git diff --check
(leer)
```

Keine Whitespace-Fehler, keine Konfliktmarker.
