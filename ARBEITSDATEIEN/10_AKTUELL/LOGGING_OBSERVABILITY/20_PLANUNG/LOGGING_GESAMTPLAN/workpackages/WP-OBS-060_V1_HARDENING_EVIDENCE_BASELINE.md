---
id: OBS-060
status: DRAFT
authority: planning
workstream: OBS
phase: A
depends_on: OBS-040, OBS-050
freeze_reference: 00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md
last_updated: 2026-08-15
---

# OBS-060 – V1 Hardening, Evidence & Baseline

## Ziel

Teil A als eigenständige, belastbare Foundation abschließen.

## Scope

- [ ] Failure-Injection-Matrix vollständig ausführen
- [ ] Runtime-Isolationsnachweis über **Protokollvergleich** (siehe unten)
- [ ] Performance-/Hot-Path-Benchmarks
- [ ] Security-/Privacy-Audit
- [ ] **Mutationschecks** (`FD` / Plan §13) — acht Stück
- [ ] **Dateirechte-Beleg** (P-8/P-9, Test M-11)
- [ ] Build-/Packaging-/Restart-/Upgrade-Smokes
- [ ] Evidence-Index und Baseline-Gate
- [ ] **manuelle Abnahme am realen Produktionspfad** — Pflicht, nicht optional

## Der Runtime-Isolationsnachweis – verbindliche Form

```text
R-1  Referenzlauf OHNE Observability: ein vollstaendiger Diktatzyklus ueber den
     ECHTEN STTController mit Skript-Session. Aufgezeichnet werden ALLE
     beobachtbaren Wirkungen: gesendete Frames, CommandResult,
     FeedbackDecision-Folge, Snapshotfolge, FinalProcessingResult.
R-2  Derselbe Lauf MIT funktionierender Observability   -> Protokoll IDENTISCH
R-3  ... mit einem Ingress, der bei JEDEM submit wirft  -> identisch
R-4  ... mit einem Store, der bei JEDEM write_batch wirft -> identisch
R-5  ... mit voller Queue von Beginn an                 -> identisch
R-6  ... mit einem Worker, der nie startet              -> identisch
R-7  ... mit einem on_observation, das bei jedem Aufruf wirft
        -> identisch UND die Cursordatei enthaelt denselben Endstand wie R-1

Bedingung: ECHTER STTController, ECHTE FeedbackEngine, ECHTER
DualSessionCoordinator, ECHTER EventProtocolProcessor. Nur der WebSocket und
die Ausgabegeraete (LED, Ton, Injektion) sind Doubles.

Warum der Protokollvergleich und keine Einzelbehauptungen: Er erfasst auch
Wirkungen, an die beim Testschreiben niemand gedacht hat, und er bemerkt eine
Regression, wenn spaeter ein Beobachtungsaufruf versehentlich an eine Stelle
rutscht, an der er den Ablauf veraendert.
```

## Mutationschecks – jede muss einen Test rot werden lassen

| Mutation | erwartet rot |
|---|---|
| `ON CONFLICT DO NOTHING` → einfaches `INSERT` | Dedupe-Tests, manuelle Abnahme M-5 |
| `except Exception` im Beobachterwrapper entfernen | Fan-out-Isolationstest, R-7 |
| `put_nowait` → blockierendes `put` | Backpressure-Test |
| Wasserstandsregel entfernen | Backpressure-Test |
| Redaction-Aufruf im Normalizer entfernen | Redaction-Tests |
| `WHERE event_id IS NOT NULL` aus dem Index entfernen | Clientrecords würden fälschlich dedupliziert |
| Handlerlevel auf DEBUG setzen | Nachweis, dass Realtime-Text nicht gespeichert wird |
| `PRAGMA query_only = ON` entfernen | Nachweis, dass der Leser nicht schreiben kann |

## Manuelle Abnahme – Pflicht

```text
Ein gruener Lauf der automatisierten Suite begruendet NICHT, dass V1 fertig
ist. Erst das folgende Protokoll tut das -- mit Datum, Serveradresse und
Clientversion.

M-1   Anwendung starten, Diktat per Hotkey, Text wird eingefuegt.
M-2   observability.sqlite3 oeffnen: client.trigger.sent und
      client.trigger.ack_received tragen dieselbe command_id;
      transcription.completed des Servers ist vorhanden.
M-3   ORDER BY id ergibt eine plausible, lueckenlose Abfolge.
M-4   DB-Datei schreibgeschuetzt setzen, neu starten, Diktat wiederholen:
      Text wird eingefuegt, LED und Ton reagieren, Health FAILED_STORE.
M-5   Serverprozess neu starten, waehrend der Client laeuft:
        SELECT event_id, COUNT(*) FROM logs WHERE event_id IS NOT NULL
        GROUP BY event_id HAVING COUNT(*) > 1
      liefert KEINE Zeile.
M-6   Log-Ansicht oeffnen, nach Session filtern, Detail und Raw JSON pruefen.
M-7   SELECT COUNT(*) FROM logs WHERE raw_json LIKE '%accessToken%'
      -- nur redigierte Vorkommen; zusaetzlich Volltextsuche in der
      JSONL-Datei.
M-8   Bei store_transcription_content=false ist ein bekannter gesprochener
      Satz in logs NICHT auffindbar.
M-9   retention_days sehr klein setzen, Retention ausloesen, Zeilenzahl
      pruefen.
M-10  Anwendung beenden: keine Restthreads, DB konsistent, client.log im
      Format unveraendert.
M-11  Effektive Dateirechte von Store und Sink einmalig protokollieren
      (icacls).

OHNE ein vollstaendiges M-Protokoll gilt V1 als "teilweise", nicht als
"erledigt".
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
