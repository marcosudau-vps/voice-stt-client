---
id: OBS-140
status: DRAFT
authority: planning
workstream: OBS
phase: D
---

# OBS-140 – LED-Controller Logging Integration

> **Übergabe aus OBS-000** (`00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md §10.6`,
> `LOGGING_DECISIONS_FREEZE_V1.md FD-B5`)
>
> - **Ein Teil dieses Pakets ist bereits in V1 erledigt.** LEFX ist eine
>   reguläre Abhängigkeit und läuft **im selben Prozess**; alle
>   `lefx.*`-Records erreichen den Root-Logger ohnehin. OBS-040 schaltet
>   lediglich **eine Normalizer-Regel** scharf:
>   `logger startswith "lefx."` → `producer_kind="led"`,
>   `producer_id="respeaker-led-controller"`, `component=<logger name>`.
>   Damit ist die Herkunftstrennung erfüllt, **ohne** dass ein Feld, eine
>   Tabelle oder eine Schnittstelle hinzukommt — und die Erweiterbarkeit des
>   Producer-Modells ist **bewiesen** statt behauptet.
> - **Ein echter Adapter wird erst nötig**, wenn der LED-Controller in einen
>   eigenen Prozess oder auf ein eigenes Gerät wandert. Er implementiert dann
>   denselben Adaptervertrag wie der `ServerLiveAdapter`; `producer_kind="led"`
>   existiert bereits.
> - **Nichtziel bleibt:** keine Logging-Abhängigkeit für die LED-Ausführung.
> - Das Repository `led_controller_respeaker-v3` wurde für V1 **nicht**
>   verändert und muss auch hier nur dann verändert werden, wenn der
>   Prozesswechsel tatsächlich stattfindet.

## Ziel

`led_controller_respeaker-v3` als vollwertigen, transportgebundenen Producer
integrieren — falls und sobald er den Prozess verlässt.

## Scope

- [ ] LED-Istzustand neu auditieren (läuft er noch in-process?)
- [ ] nur falls out-of-process: minimalen Transport/Adapter wählen
- [ ] `LedAdapter` implementieren
- [ ] Producer/Korrelation/Health integrieren
- [ ] LED failure isolation testen

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
