# OBS-000 – Entscheidungen und Freeze Gate

```text
Status  ABGESCHLOSSEN
Gate    G-OBS-000 PASS
Run     RUN-OBS-000-01_2026-08-15_CLAUDE
Datum   2026-08-15
```

## Zweck

Diese Checkliste musste vor dem ersten Produktcode-Work-Package geschlossen
werden. Jeder Punkt trägt jetzt die Fundstelle seiner Auflösung.

**Kurzbezeichner der normativen Dateien in diesem Dokument:**

```text
ARCH       00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md
CONTRACTS  00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md
DECISIONS  00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md
EV-nn      40_EVIDENCE/OBS-000/EV-nn_*.md
```

---

## Einzuarbeitende Claude-Ergebnisse

- [x] `LOGGING_CODE_INTEGRATION_AUDIT.md`
- [x] `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md`
- [x] `LOGGING_CONCURRENCY_FAILURE_MODEL.md`
- [x] `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md`
- [x] `LOGGING_V1_IMPLEMENTATION_PLAN.md`
- [x] `LOGGING_OPEN_DECISIONS.md`
- [x] `LOGGING_TEST_MATRIX.md` — vorhanden und eingearbeitet
- [x] `LOGGING_ADVERSARIAL_REVIEW.md`
- [x] `00_README_UND_ABSCHLUSSBEWERTUNG.md` *(zusätzlich vorgefunden)*

Herkunft, Integrität und Auswahl: `10_ANALYSE/CLAUDE_VORARBEIT/SOURCE_MANIFEST.md`
und `EV-01`. Alle neun Dateien byteidentisch mit dem Archiv; keine
widersprüchliche Variante; keine fehlende Pflichtdatei.

---

## Entscheidungen

| # | Punkt | Ergebnis | Fundstelle |
|---|---|---|---|
| 1 | CanonicalRecord exakt festgelegt | 24 Felder, neun davon Pflicht | `CONTRACTS §1` |
| 2 | Record-/Schema-Versionierung | `PRAGMA user_version` + `schema_meta`; JSONL je Zeile; keine Spalte je Record | `CONTRACTS §2.3`, `FD-C9` |
| 3 | Producer-Identität | `producer_kind` ∈ {client, server, led, other}; `producer_id` als Konstante; `instance_id` je Prozess | `CONTRACTS §1.1` |
| 4 | Channelmodell | vier Server-Channels, **klein**, keine zusätzlichen | `CONTRACTS §2.2`, `FD-C6` |
| 5 | Event-/Record-Dedupe | `(producer_id, event_id)`, partieller UNIQUE-Index, `ON CONFLICT DO NOTHING` | `CONTRACTS §5.5`, `FD-C7` |
| 6 | Replay-Semantik | erste Fassung gewinnt; `replayed` bleibt diagnostisch; Dedupe wirkt nur auf der Persistenz; `deduplicated` wird gezählt | `CONTRACTS §5.5`, `FD-R5` |
| 7 | Ingress-/Fan-out-Hook | `DualSessionCoordinator._handle_event` / `_handle_control`, erste Anweisung, `try/except Exception` | `CONTRACTS §7`, verifiziert `EV-02 / C-02, C-03` |
| 8 | Queue-Typ/Default/Dropstrategie | **eine** `queue.Queue`, 8192, Wasserstandsregel bei 75 % | `ARCH §7`, `FD-S2`, `FD-R1` |
| 9 | Worker-Lifecycle | dedizierter Daemon-Thread; Manager in `app.py::main()` mit `try/finally` | `ARCH §6.2`, `FD-R4` |
| 10 | SQLite-Pfad | `%LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3` | `CONTRACTS §5.1`, `FD-C9` |
| 11 | SQLite Schema/Migration | vollständiges DDL; Migration über `user_version`; Datei wird nie gelöscht | `CONTRACTS §5.2`, `§5.5` |
| 12 | Retention Defaults | 14 Tage / 200.000 / 256 MiB (nur Warnsignal); beide Hauptgrenzen wirken; blockweises Löschen | `CONTRACTS §5.6`, `FD-D3`, `FD-D8` |
| 13 | Raw-Payload Default | `true`, außer `channel == "performance"`; Obergrenze 64 KiB | `FD-D2`, `FD-C12` |
| 14 | Transcription-Content Default | `false`; Zeichenzahl bleibt; gilt **auch** für unstrukturierte Logtexte | `FD-D1`, Regel `R-10` |
| 15 | Secret-Redaction-Liste | zwölf Regeln `R-1…R-12` plus `P-8/P-9` | `CONTRACTS §4` |
| 16 | V1 File-Sinks | nur JSONL; `file_sink_format` entfällt | `FD-D4` |
| 17 | Query-Provider-Interface | `LogProvider`-Protokoll mit vier Methoden; `query()` wirft nie; opaker Cursor; kein `ProviderCapabilities` in V1 | `CONTRACTS §8`, `FD-S3` |
| 18 | UI-Position | eigenes `LogWindow`; sechster Settings-Tab „Logging & Diagnose" | `CONTRACTS §9`, verifiziert `EV-02 / C-08` |
| 19 | Settings-Scope | 14 Konfigfelder, 9 davon im Dialog; zwei Schaltflächen | `CONTRACTS §10` |
| 20 | V1 Observation-Hooks | vollständige Liste, nach Channel geordnet, mit Umsetzungsreihenfolge | `CONTRACTS §12` |
| 21 | Hot-Path Sampling/Aggregation | Hot-Path-Liste; dort nur `int`-Zähler; Aggregat alle 5 s **vom Worker** | `ARCH §8.6` |
| 22 | Shutdown-/Flush-Semantik | `manager.stop(2.0)` **nach** `bridge.stop(10.0)`, im `finally`; Handler-`flush`/`close` sind No-Ops | `ARCH §6.2`, `§8.1` G-7 |

## Zusätzlich in diesem Run geschlossen

| # | Punkt | Ergebnis |
|---|---|---|
| 23 | Paketname | `core/observability/`, Konfig `logging.observability.*` (`FD-N1`) — war die **einzige** blockierende Entscheidung |
| 24 | Serialisierung des Rohpayloads | `unfreeze()` für `MappingProxyType`, `tuple` **und `frozenset`**; `default=str` nur je Blattwert (`FD-C11`) |
| 25 | Levelzuständigkeit | ein Konfigwert speist Handler- und Ingress-Level (`FD-D9`) |
| 26 | `LOGGER_CHANNEL_MAP` | nur `text` → `transcription`, alles andere → `system` (`FD-R2`) |
| 27 | Protokollfehler-Beobachtung | zusätzlicher Punkt in `EventStreamTransport.run()` (`FD-R3`) |
| 28 | Löschfunktion | „Diagnosehistorie löschen" kommt in V1, am **Store** (`FD-S4`) |
| 29 | Work-Package-Grenzen | Abbildung 14 → 6, zwei Titelkorrekturen, eine Abhängigkeitskorrektur (`DECISIONS §8`) |
| 30 | W-16 | `IMPLEMENTATION_ROADMAP.md` geprüft — **kein Widerspruch** (`EV-02 / C-13`) |

---

## Freeze-Kriterium

> `PASS`, wenn keine dieser Fragen mehr von einem Coding-Agenten entschieden
> werden muss.

```text
Blockierende offene Entscheidungen:  KEINE
Offene Widersprueche:                KEINE  (19 aufgeloest)
Offene Informationsluecken:          KEINE

ERGEBNIS:  G-OBS-000 PASS
```

## Nicht Teil dieses Gates

Fünf Punkte sind bewusst nach Teil B verschoben. Sie berühren **keinen**
V1-Codepfad, und V1 trifft jeweils die benannte Vorkehrung:
Capability-Modell (`FD-B1`), Reihenfolge der Remote-Provider (`FD-B2`),
HTTP-Fähigkeit (`FD-B3`), Multi-Host/`host`-Spalte (`FD-B4`), LedAdapter
(`FD-B5`).
