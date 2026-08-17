# RUN_LOG – OBS-010-01 (DeepSeek)

Run-ID: `RUN-OBS-010-01_2026-08-17_DEEPSEEK`
Work Package: `OBS-010 – Canonical Model, Redaction, Normalizer & Contracts`
Implementierung: DeepSeek (opencode-go/deepseek-v4-flash)
Datum: 2026-08-17
Session-Root: `P:\GithubRepos\marcosudau-vps`
Client-Workspace (git): `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

## Startzustand

- Git-Repo: der Client-Workspace selbst (Branch `feat/einheitliche-triggerarchitektur`).
- HEAD: `f3908cff01cebf54db76a492e0a95ae882a98a4d` — **entspricht exakt dem im Auftrag erwarteten Client-HEAD**.
- Baseline-Commit vorhanden: `f3908cf "chore: establish OBS-010 project baseline and work archive"` (Vorgänger `5f2ee4b`).
- Working Tree: sauber, mit genau einem untracked File — dem Auftrag selbst
  (`ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/OBS-010_DEEPSEEK_IMPLEMENTIERUNGSAUFTRAG.md`).
- Relevante vorhandene Tests analoges Baseline-Register: keine observability-Tests vorhanden.
- Vollständige bestehende Client-Suite als Baseline ausgeführt:
  `python -m pytest -q` → **513 passed** (26.4 s). Keine Failures.
- Python-Interpreter: `P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe`
  (Python 3.12.13). Im Workspace selbst existiert kein venv (gitignored); das
  Projekt-venv der voice-stt-client-Instanz wird als Interpreter verwendet, die
  Tests laufen gegen den Workspace-Baum (`workdir` = Workspace).

## Pflichtlektüre (vollständig)

- `ARBEITSDATEIEN/README.md`, `ARBEITSDATEIEN/AGENTS.md`
- `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`, `MASTERPLAN.md`, `ARBEITSPROZESS.md`
- `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md` (über System-Kontext geladen)
- `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md`, `LOGGING_CONTRACTS_FREEZE_V1.md`,
  `LOGGING_DECISIONS_FREEZE_V1.md`, `00_NORMATIV/README.md`
- `20_PLANUNG/LOGGING_GESAMTPLAN/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md`,
  `workpackages/WP-OBS-010_CANONICAL_MODEL_CONTRACTS.md`
- `40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md`
- Referenzproduktcode: `core/event_models.py` (`_freeze`-Muster,
  `EventEnvelope`, `EventOrigin`), `core/event_protocol.py` (`EventProtocolResult`,
  `EventResultKind`, `_freeze_mapping`), `core/session_coordinator.py` (`SessionContext`),
  `core/logging_setup.py` (bestehender `extra`-Vertrag), reale Transkript-Logzeilen in
  `core/stt_session.py:1297` und `core/controller.py:2077/2145` (N-02),
  `tests/test_event_protocol.py` (echte `log.event`-Frames), Serverdocs
  `04-server-events-katalog-und-chronologie.md` (reale `logAccess`-/`hello`-Struktur).

## Umsetzungsplan (Schritte)

1. `core/observability/` Paket anlegen: `models.py`, `redaction.py`,
   `normalizer.py`, `ingress.py`, `storage/base.py`, `sinks/base.py`,
   `query/base.py` + Paket-`__init__.py`, Unterpaket-`__init__.py`.
2. Tests unter `tests/test_obs010_*.py` (unittest-Stil, kompatibel mit
   pytest- und unittest-Lauf).
3. Baseline-Suite erneut grün halten (keine bestehende Datei/kein bestehender Test
   wird geändert). Nur neue Dateien (WP-OBS-010: "Dieses Paket legt ausschließlich
   neue Dateien an.") plus Evidence-/Trackingdateien unter ARBEITSDATEIEN.
4. Evidence, Steuerungsdateien, Abschlussprüfung.

## Umgesetzte Teilpunkte

Siehe RESULT.md und die Dateien selbst. Kurz:

- [x] `models.py`: Enums + frozen `CanonicalLogRecord` exakt nach CONTRACTS §1.4;
      `details`/`raw` beim Bau eingefroren (Muster `event_models._freeze`), Übernahme
      bereits eingefrorener `MappingProxyType`-Strukturen ohne Kopie (ARCH §8.2);
      `priority`-Property exakt nach §1.5 (inkl. `not replayed`); Feld-/Typ-Validierung.
- [x] `redaction.py`: `SENSITIVE_KEYS`, `TRANSCRIPT_KEYS`, `unfreeze()`,
      `redact_mapping`, `redact_text`, `shorten_user_paths` nach CONTRACTS §4
      (R-3, R-8, R-9, R-10, R-11, R-12) und FD-C11/FD-C12.
- [x] `normalizer.py`: drei Eingänge nach CONTRACTS §3; `LOGGER_CHANNEL_MAP`;
      `_normalize_level` mit INFO-Rückfall + `source_severity`; Redaction am Ende
      jedes Pfades; der Normalizer wirft nie (im Zweifel `None`).
- [x] `ingress.py`: `Ingress`-Protocol (Signatur der strukturierten
      Client-Observation-API `event(...)`), damit OBS-020 sie nur noch implementiert.
- [x] `storage/base.py`: `LogStore`-Protokoll (Signaturen).
- [x] `sinks/base.py`: `Sink`-Protokoll (Signaturen).
- [x] `query/base.py`: `ProviderState`, `ProviderStatus`, `QueryFilter`,
      `LogRecordView`, `QueryPage`, `LogProvider` nach CONTRACTS §8.
- [x] Tests + Contract-Tests (Qt-/sqlite3-Grenzen, Zyklenfreiheit, keine Referenz
      auf Controller/Session/Coordinator im Python-Logpfad).
- [x] Diagnose-Skript für die reale `hello`-Struktur (Evidence).

## Entscheidungen / Auslegungen innerhalb des freigegebenen Vertragsrahmens

1. **`__init__.py`-Re-Exports:** ARCH §5.1 nennt als Endstand vier Namen
   (`ObservabilityManager`, `ObservabilityIngress`, `NULL_INGRESS`,
   `CanonicalLogRecord`). OBS-010 baut Manager/Ingress noch nicht (OBS-020/030).
   Das `__init__.py` re-exportiert deshalb additiv die jetzt vorhandenen Namen
   (CanonicalLogRecord, Enums, redaction/normalizer/query-öffentliche Funktionen.
   kein Vertragskonflikt, additive Erweiterung in Folgepaketen.
2. **`from_log_record`-Signatur:** Die eingefrorene Signatur fordert
   `session_id`/`generation` als Parameter; CONTRACTS §3.1 / FD-R8 bestimmen,
   dass die Werte **ausschließlich** aus `record.__dict__` stammen. Die Parameter
   bleiben (Signatur-Treue), die effektiven Werte kommen aus `record.__dict__` —
   der UnifiedLogHandler darf keine Laufzeitsitzung abfragen.
3. **`raw`-Redaction bei Serverrecords:** ARCH §8.2 verlagert Entfrieren/
   Serialisieren/Redigieren von `raw` in den Worker (OBS-030). Der OBS-010-Normalizer
   MAPPED `raw` als eingefrorene Referenz (`result.payload`), redigiert aber
   `details` (clientseitig erzeugte bzw. kleine Strukturen). `store_raw_payload=False`
   bzw. `channel == "performance"` → `raw=None`. `unfreeze`/`redact_mapping` sind
   als separate, vom Worker in OBS-030 nutzbare Funktionen implementiert (N-01).
4. **`hello`-Whitelist:** R-6 umgesetzt, `accessToken`, `websocketPath`,
   `historyPath`, `deliveryMode`, `replayAvailable` und `logAccess.sessionId`
   werden NICHT in `details` übernommen; `raw=None`.
5. **`redact_text`:** R-10 für unstrukturierte Logtexte. Umgesetzt als
   Erkennung der realen, abschließend benannten Produktions-Logzeilen
   (stt_session `Final [seg=%s]: %s`, controller-Dedup-`existing=…, new=…`)
   plus URL-Query-/Fragment-Entfernung (R-8) und Pfadkürzung (R-9). Kein Versuch,
   Transkripttext per Werteheuristik zu erkennen (verboten).
6. **Truncation-Marker bei Tiefen-/Knotengrenze (R-12):** verwendet wird
   `{"_truncated": True, "_reason": "<max_depth|max_nodes>"}`, analog zum
   freigegebenen 64-KiB-Marker `{"_truncated": true, "_bytes": n}` (FD-C12).
   Der Marker ist im Vertrag nicht festgelegt; kleinstmögliche Wahl dokumentiert.
7. **Control-Mapping:** nur Control-Fälle nach CONTRACTS §3.2 umgesetzt; für
   `log.subscribed`/`log.error`/`log.replay_completed`/`log.pong`/`log.keepalive`
   ist `details` = redigierter Payload, `raw` = Payload (außer hello).
8. **Duplicate-Events** werden gemäß CONTRACTS §3.2 als CONTROL gemappt
   (`client.eventstream.<kind>`, `component=eventstream`).

## Abweichungen / Scope

- Keine fachlichen Scope-Abweichungen. Nur neue Dateien im Produktbaum
  (`core/observability/**`, `tests/test_obs010_*.py`).
- Kein bestehender Test wurde geändert; keine bestehende Produktdatei geändert.

## Tests

- Neue OBS-010-Testdateien (siehe RESULT.md).
- Vollständige Client-Suite am Ende erneut: → siehe RESULT.md / TEST_RESULTS.md.
- Keine bestehenden Tests geändert → "Ein bestehender Test wird geändert" = Alarmsignal = NICHT eingetreten.

## Endzustand

- Working Tree enthält nur OBS-010-Scope-Änderungen (neue Dateien) plus
  Run-/Evidence-/Steuerungsdateien unter `ARBEITSDATEIEN`.
- Siehe Abschlussprüfung in RESULT.md.