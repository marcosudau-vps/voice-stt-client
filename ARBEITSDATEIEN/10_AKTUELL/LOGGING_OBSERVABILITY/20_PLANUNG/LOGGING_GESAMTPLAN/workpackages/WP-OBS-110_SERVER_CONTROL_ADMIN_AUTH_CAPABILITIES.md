---
id: OBS-110
status: DRAFT
authority: planning
workstream: OBS
phase: C
---

# OBS-110 – Server Control, Admin Auth & Capabilities

> **Übergabe aus OBS-000** (`00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md §10.1`,
> `LOGGING_DECISIONS_FREEZE_V1.md FD-B1`)
>
> - **Hier fällt die Capability-Entscheidung**, nicht in V1. Der Server kennt
>   **kein** benanntes Capability-Set für Admins, sondern nur „admin ja/nein"
>   plus die abgeleiteten Erweiterungen `allSessions`, `allChannels` und Channel
>   `system`. `sessionCapabilities` ist etwas anderes: Fähigkeiten der Session,
>   nicht Rechte eines Nutzers. Ein benanntes Set hat nur Wert, wenn der Server
>   feiner vergeben kann als „alles oder nichts" — das ist eine
>   **Serverproduktentscheidung**. Tendenz: aus dem binären Status ableiten.
> - **V1 hat vorgesorgt:** `ProviderState.AUTH_REQUIRED` existiert; der
>   LoggingCore importiert nichts aus `core/server_control/`; er sieht den
>   Session-Log-Token auch nicht indirekt.
> - **Auflage:** `SettingDefinition.sensitive` existiert heute, wird aber von
>   **keinem** UI-Code ausgewertet (verifiziert `EV-02 / C-08`). Bevor es je
>   einen Admin-Key trägt, muss es **zuerst tatsächlich wirken**: Maskierung,
>   kein Klartext in `config.yaml`, keine Aufnahme in `changes`-Logs.
> - **Der Admin-Key liegt in einem eigenen Paket** `core/server_control/`,
>   niemals unterhalb von `core/observability/` (Invariante O-12).

## Ziel

Die bestehende zweite Serververbindung als Control-/Observability-Verbindung im
Desktopclient sauber abstrahieren.

## Scope

- [ ] bestehenden Server-/Browser-Admincontract prüfen und wiederverwenden
- [ ] `ServerControlConnection` abstrahieren
- [ ] Auth-State und bestätigte Capabilities implementieren
- [ ] secure credential handling; `sensitive` zuerst wirksam machen
- [ ] expiry/reconnect/failure behavior

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
