---
id: OBS-050
title: Local Query, Log View & Settings
status: DRAFT
authority: planning
workstream: OBS
phase: A
depends_on: OBS-030
freeze_reference: 00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md
last_updated: 2026-08-15
---

# OBS-050 – Local Query, Log View & Settings

> **Abhängigkeitskorrektur aus OBS-000.** Dieses Paket hängt an OBS-030 und ist
> von **OBS-040 unabhängig**. Nach dem Wegfall des Ringbuffers (`FD-S1`) benutzt
> der Live-Modus dieselbe Provider-Schnittstelle wie die Historie; die UI hängt
> damit nur noch am Query-Layer und kann **parallel zu OBS-040** gebaut werden.
>
> **Verbindliche Vorgaben aus OBS-000**
>
> - **Kein Ringbuffer.** Live-Modus als tailende Store-Abfrage
>   (`QTimer` 250 ms, `WHERE id > :last ORDER BY id LIMIT 500`), **kein Signal
>   je Record**. `live_buffer_size` entfällt aus der Konfiguration.
> - **Kein `ProviderCapabilities`** in V1 (`FD-S3`). `ProviderStatus` trägt nur
>   `provider_id`, `display_name`, `state`, `detail`.
> - **Leseverbindung** mit `PRAGMA query_only = ON`, **nicht** `mode=ro`
>   (`CONTRACTS §5.4`) → Nachweis N-06.
> - **Query läuft nicht über `CoreBridge`** — dort liegen Audio und WebSocket.
>   Eigener `ThreadPoolExecutor(max_workers=1)` im `LogQueryController`.
> - **Sieben Spalten**, eigenes nicht-modales `LogWindow`, sechster
>   Settings-Tab (`CONTRACTS §9`).
> - **Konfigfelder und Apply-Policies** verbindlich in `CONTRACTS §10.3`.
> - **`LoggingObservabilityConfig` braucht dieselbe Sonderbehandlung im
>   `_from_dict` wie `history`** — `_build` löst verschachtelte Dataclasses
>   nicht auf. Ohne sie trüge das Feld immer die Defaultwerte, ein stiller
>   Fehler (`CONTRACTS §10.2`) → Nachweis N-12.
> - **Löschfunktion** „Diagnosehistorie löschen" am **Store**, nicht am
>   Query-Provider (`FD-S4`, O-14).
> - **Der Activation-Filter trägt einen Hinweis** auf die Unzuverlässigkeit des
>   Wertes (`FD-C2`).

## Ziel

Die Daten praktisch nutzbar machen, ohne die spätere Remote-Provider-Architektur
zu verbauen.

## Scope

- [ ] `LocalLogProvider` und `LogQueryService` (Registry)
- [ ] Keyset-Pagination nach `CONTRACTS §5.7`; `raw_json` **nicht** in der
      Listenabfrage
- [ ] `LogTableModel` (`QAbstractTableModel`) + `LogWindow`/`LogPage`
- [ ] `LogFilterBar`, `LogDetailView`, `LogQueryController`
- [ ] Detail-/Raw-JSON-/Filter-/Kontextansichten
- [ ] Logging-Settings in bestehende Config und UI integrieren
- [ ] Schaltflächen „Diagnosehistorie löschen" und „Logs anzeigen"

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
