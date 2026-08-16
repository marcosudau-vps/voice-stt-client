---
id: OBS-040
status: DRAFT
authority: planning
workstream: OBS
phase: A
depends_on: OBS-020, OBS-030
freeze_reference: 00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md
last_updated: 2026-08-15
---

# OBS-040 – Server Live Adapter & Client Observation Hooks

> **Verbindliche Vorgaben aus OBS-000**
>
> - **Hookstelle:** `DualSessionCoordinator._handle_event` und
>   `_handle_control`, jeweils als **erste** Anweisung, rückgabewertfrei, in
>   `try/except Exception`. Verboten sind
>   `STTController.on_event_stream_event`, `EventStreamTransport._dispatch`,
>   `EventProtocolProcessor.process_mapping`,
>   `FeedbackEngine.handle_event_stream` und `_on_feedback_decision` —
>   Begründung je Stelle in `CONTRACTS §7.4`.
> - **`BaseException` wird nirgends gefangen.** Der Dispatch ruft bei einer
>   durchschlagenden Ausnahme `reject_event(result)`; ein werfender Beobachter
>   würde das Event also **aktiv verwerfen**. `asyncio.CancelledError` muss
>   durchkommen.
> - **Zweiter Beobachtungspunkt** für Protokollfehler im `except`-Zweig von
>   `EventStreamTransport.run()` → `client.eventstream.protocol_error`, ohne
>   Rohframe (`FD-R3`).
> - **Injektionsweg** über die Default-Factory in `CoreBridge`, damit die
>   einstellige `ControllerFactory` unverändert bleibt (`CONTRACTS §6`).
> - **Hookliste** vollständig und verbindlich in `CONTRACTS §12`, einschließlich
>   der Umsetzungsreihenfolge nach aufsteigendem Risiko.
> - **Hot-Path-Regeln** in `ARCH §8.6`: dort ausschließlich `int`-Zähler; das
>   5-Sekunden-Aggregat erzeugt der **Worker**, der die Zähler liest.
> - **`raw` wird im Producer nicht kopiert und nicht serialisiert.** Entfrieren,
>   Serialisieren und Redigieren geschehen im Worker (`ARCH §8.2`).
> - **Korrigierte Testerwartung:** Ein Duplikat erzeugt **keinen** Record mit
>   `replayed=True`. Es wird beobachtet, normalisiert und an den Store
>   übergeben; der Store fügt **keine** zweite Zeile ein; `deduplicated` steigt.

## Ziel

Die Foundation mit realen Datenquellen verbinden, ohne fachliche Pfade
umzubauen.

## Scope

- [ ] passiven `ServerLiveAdapter` am freigegebenen Fan-out-Punkt anbinden
- [ ] zweiten Beobachtungspunkt für Protokollfehler ergänzen
- [ ] bestehenden Feedbackpfad unverändert lassen
- [ ] V1 Client Observation Hooks nach `CONTRACTS §12` hinzufügen
- [ ] Hot-Path-Ereignisse nur aggregiert erfassen
- [ ] Replay-/Origin-/Cursor-Metadaten erhalten
- [ ] `lefx.*`-Normalizer-Regel scharf schalten — sie **beweist** die
      Erweiterbarkeit des Producer-Modells, ohne dass ein Adapter entsteht

## Der wichtigste Nachweis dieses Pakets (N-07)

```text
Ein WERFENDER Beobachter veraendert WEDER den Rueckgabewert von _handle_event
NOCH den Cursorstand.

Aufbau: der ECHTE EventProtocolProcessor und der ECHTE EventCursorStore auf
einer temporaeren Datei. KEIN Double -- ein Double wuerde die
Cursor-Bestaetigungssemantik selbst definieren, also genau das, was bewiesen
werden soll.

Zusaetzlich: die bestehenden Suiten test_session_coordinator.py,
test_event_stream.py, test_feedback_integration.py und
test_trigger_feedback_contract.py laufen UNVERAENDERT gruen.

git diff zeigt in session_coordinator.py KEINE Aenderung an einer bestehenden
Zeile ausser den zwei eingefuegten Aufrufen.
```

## Non-Scope

- Keine stillen Änderungen außerhalb dieses Work Packages.
- Keine Änderung normativer Contracts ohne `DECISION REQUIRED`.
- Keine fachliche Runtime-Autorität für Logging.
- Keine Git-History-Aktion ohne ausdrückliche Freigabe.

## Pflichtprüfungen

- [ ] Positive Tests
- [ ] Negative Tests
- [ ] Failure-/Edge-Tests passend zum Paket
- [ ] relevante Produktionspfade
- [ ] `git diff --check`
- [ ] kein unbeabsichtigter Cross-Workstream-Diff

## Evidence

Evidence wird unter einem paketbezogenen Evidence-Ordner abgelegt und enthält mindestens Commands, Exitcodes, Ergebnisse und bekannte Einschränkungen.

## Gate

`PASS` nur nach separatem Review. Ein Coding-Agent darf nicht allein aufgrund eigener grüner Tests das Gate vergeben.
