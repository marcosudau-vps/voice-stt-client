# Traceability Matrix – Logging / Observability

**Stand:** 2026-08-15, nach `G-OBS-000 PASS`

Kurzbezeichner: `ARCH` = `LOGGING_ARCHITEKTUR_FREEZE_V1.md`,
`CONTRACTS` = `LOGGING_CONTRACTS_FREEZE_V1.md` (beide unter `00_NORMATIV/`).

---

## Invarianten

| ID | Invariante | Vertrag | Primär-WP | Automatischer Nachweis | Manueller Nachweis |
|---|---|---|---|---|---|
| O-01 | Observability only | `ARCH §1.1`, `§9` | OBS-020/040 | Failure-/Isolationstests; Protokollvergleich mit und ohne Logging | Runtime-Smoke |
| O-02 | Fan-out statt Vermittlung | `CONTRACTS §7` | OBS-040 | Dispatch-Tests gegen den **echten** Coordinator | Eventfluss-Review |
| O-03 | Non-Blocking | `ARCH §6.3` | OBS-020/060 | Überlast-/Perf-Tests; Quelltextprüfung der Hot-Path-Funktionen | Laufzeitverhalten |
| O-04 | Bounded Memory | `ARCH §7` | OBS-020 | Queue-Sättigung; Speicherobergrenze aus `queue_size` | – |
| O-05 | Failure Isolation | `ARCH §8.3` | OBS-060 | injizierte Fehler (Store, Sink, Worker, Queue) | manueller Smoke |
| O-06 | Struktur statt Textparsing | `CONTRACTS §1`, `§12` | OBS-010/040 | Schema-/Hooktests | LogView-Inspektion |
| O-07 | Source Preservation | `ARCH §3.1` | OBS-010 | Normalisierungstests | Filterprüfung |
| O-08 | Replay Safety | `CONTRACTS §5.5` | OBS-030/040 | Replay-Tests; `deduplicated`-Zähler | Reconnect-Smoke, M-5 |
| O-09 | Security / Redaction | `CONTRACTS §4` | OBS-010/020/060 | Redaction-Tests; Mutationscheck | Secret-Audit M-7 |
| O-10 | Query Independence | `CONTRACTS §8`, `§9.2` | OBS-050 | Contract-Test: kein `sqlite3` unter `ui/`, kein Zugriff auf `storage` | Code-Review |
| O-11 | Extensibility | `ARCH §10` | OBS-010/050/140 | Protokolltests; die `lefx.*`-Regel **beweist** den zweiten Producer | Integrationsreview |
| O-12 | Admin Separation | `ARCH §10.1` | OBS-110/120 | Import-/Dependency-Tests | Code-Review |
| O-13 | Control-Plane-Trennung | `ARCH §9` | OBS-040/100 | Architekturtests; Cursor-Nachweis bei werfendem Beobachter | Lifecycle-Smoke |
| **O-14** | **Schreibmonopol** *(neu)* | `ARCH §1.2` | OBS-050 | Contract-Test: `LogProvider` hat keine Schreibmethode; `PRAGMA query_only` | Code-Review |

## Features

| ID | Feature | Vertrag | Primär-WP | Automatischer Nachweis | Manueller Nachweis |
|---|---|---|---|---|---|
| F-01 | Python logging → Store | `CONTRACTS §3.1` | OBS-020/030 | Handler-Integration | – |
| F-02 | SQLite-Historie | `CONTRACTS §5` | OBS-030 | Store-/Query-Tests | UI-Historie |
| F-03 | Live-Serverlogs | `CONTRACTS §3.2`, `§7` | OBS-040 | Adapter-Integration | Live-Lauf M-2 |
| F-04 | Strukturierte Client-Observationen | `CONTRACTS §12` | OBS-040/100 | Hooktests je Typ | Timeline M-3 |
| F-05 | Minimal-UI | `CONTRACTS §9` | OBS-050 | Modelltests, offscreen-Qt | visueller Smoke M-6 |
| F-06 | Remote-Historie | `ARCH §10.3` | OBS-120 | Provider-Integration | Admin-Lauf |
| F-07 | Server-Admin-Config | `ARCH §10.5` | OBS-130 | Service-Tests | Admin-UI |
| F-08 | LED als Producer | `ARCH §10.6` | OBS-040 *(Regel)*, OBS-140 *(Adapter)* | Normalizer-Test `lefx.*` → `producer_kind=led` | Hardware-Smoke |
| F-09 | Zusätzliche Sinks | `ARCH §10.7` | OBS-030 *(JSONL)*, OBS-150 | Sink-Tests | konfigurierter Smoke |
| F-10 | Forensischer Vergleich | `ARCH §3.2` | OBS-170 | Korrelationstests | Incident-Walkthrough |

## Neue, in OBS-000 hinzugekommene Nachweispflichten

| ID | Gegenstand | Vertrag | WP | Nachweis |
|---|---|---|---|---|
| N-01 | `unfreeze()` behandelt `MappingProxyType`, `tuple`, `frozenset` | `CONTRACTS §4.1` | OBS-010 | Test mit einem echten `EventProtocolResult.payload`; Ergebnis ist ein JSON-**Objekt**, kein String |
| N-02 | Redaction wirkt auch auf unstrukturierte Logtexte | `R-10` | OBS-010 | Test gegen die realen `Final [seg=…]`- und `existing=%r, new=%r`-Zeilen |
| N-03 | Handler `flush`/`close` sind No-Ops | `ARCH §8.1` G-7 | OBS-020 | Test, dass `logging.shutdown()` nicht auf den Worker wartet |
| N-04 | Replayte Records sind LOW | `CONTRACTS §1.5` | OBS-020 | Wasserstandstest mit replayten Serverevents |
| N-05 | Store-Verbindung entsteht im Worker-Thread | `CONTRACTS §5.4` | OBS-030 | Test, der die Verbindung aus einem Fremdthread benutzt und den Fehler erwartet |
| N-06 | Leser können nicht schreiben | `CONTRACTS §5.4` | OBS-050 | Test: `INSERT` über die Leseverbindung scheitert |
| N-07 | Werfender Beobachter ändert Cursor nicht | `CONTRACTS §7.3` | OBS-040 | **echter** Processor + **echter** `EventCursorStore` auf temporärer Datei |
| N-08 | Protokollfehler werden strukturiert erfasst | `FD-R3` | OBS-040 | Test mit einem ungültigen Frame |
| N-09 | Reine Observability-Änderung löst keinen Reconnect aus | `CONTRACTS §10.4` | OBS-050 | `apply_runtime_config` mit einer Fake-Session, deren `reconfigure` durchfällt |
| N-10 | Dateirechte belegt | `P-8/P-9`, `M-11` | OBS-060 | einmalige `icacls`-Ausgabe im Abnahmeprotokoll |
| N-11 | Mutationschecks | `Plan §13` | OBS-060 | acht Mutationen, jede muss einen Test rot werden lassen |
| N-12 | Verschachtelte Configdataclass wird aufgelöst | `CONTRACTS §10.2` | OBS-050 | Test: ein `config.yaml` mit abweichenden Observability-Werten kommt im Objekt an |
