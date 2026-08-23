# OBS-060 – V1_REQUIREMENTS_TRACEABILITY

Run: `RUN-OBS-060-01_2026-08-18`

Diese Datei bildet jede verbindliche V1-Anforderung auf ihren Nachweis ab.
Nachweise sind **immer** ein Testname, ein Probeschritt oder eine Codestelle,
nie eine Behauptung aus einem Abschlussbericht.

Abkürzungen der Nachweisquellen:

| Kürzel | Datei |
|---|---|
| `E2E` | `probe_obs060_e2e_chain.py` |
| `FI` | `probe_obs060_failure_injection.py` |
| `RI` | `probe_obs060_runtime_isolation.py` |
| `PERF` | `probe_obs060_performance.py` |
| `PRIV` | `probe_obs060_privacy.py` |
| `MUT` | `probe_obs060_mutation_checks.py` |
| `PKG` | `probe_obs060_packaging.py` |
| `T060` | `tests/test_obs060_v1_hardening.py` |

---

## 1. Die verbindlichen Final-Gate-Kriterien

Aus `Prompts/OBS-060_V1_GATE_REVIEW.md`. Logging V1 muss:

| # | Kriterium | Nachweis | Zustand |
|---|---|---|---|
| 1 | rein beobachtend sein | `RI` R-1…R-7: sechs Störungsläufe, Protokoll identisch zum Referenzlauf ohne Observability | erfüllt |
| 2 | Runtime/Lifecycle niemals besitzen oder steuern | `RI` R-7 (werfender Beobachter ändert weder Rückgabewert, Bestätigung noch Cursordatei); `_notify_observer` ist rückgabewertfrei (`core/session_coordinator.py`); `MUT` M-2 | erfüllt |
| 3 | kanonische strukturierte Records konsistent verwenden | `E2E` P-1.2/P-1.4 (Korrelationskette über den Roundtrip), `CanonicalLogRecord.__post_init__` validiert jede Wertemenge; `tests/test_obs010_*` | erfüllt |
| 4 | Fehler intern isolieren | `FI` F-1…F-10, alle zehn Fälle; `MUT` M-2 | erfüllt |
| 5 | nicht blockierend arbeiten | `PERF` B-1 (ARCH §6.3 wörtlich: 20 000 Records, langsamster `submit` 0,038 ms, nie geworfen); `MUT` M-3 (blockierendes `put` ⇒ Testlauf endet nie) | erfüllt |
| 6 | bounded Backpressure besitzen | `FI` F-5; `PERF` B-1.4/B-1.5; `T060 TestNonBlockingInvariantAnchor`; `MUT` M-4 | erfüllt |
| 7 | SQLite als lokale V1-Wahrheit verwenden | `E2E` P-1, P-3 (Neustart), P-6 (Kompositionswurzel) | erfüllt |
| 8 | ohne Memory-Ringbuffer auskommen | `FD-S1`; eine begrenzte `queue.Queue`, kein Ringbuffer im Code; `PERF` B-1.4 misst die Grenze | erfüllt |
| 9 | Privacy-/Redaction-Regeln erfüllen | `PRIV` S-1, S-4, S-5; `MUT` M-5 | erfüllt |
| 10 | keine Audio-Payloads/Secrets persistieren | `PRIV` S-1 (sechs Secretarten), S-3 (Audio), S-5.3 (Secret in übergroßer Payload) | erfüllt |
| 11 | Transcript-Policy einhalten | `PRIV` S-2.1…S-2.4; `T060 TestTranscriptPolicyAnchor`; `MUT` M-7 | erfüllt |
| 12 | Server-Live-Events und Client-Hooks korrekt beobachten | `RI` (drei Serverevents durch den echten Dispatch, `event_stream_accepted` identisch); `E2E` P-2; `tests/test_obs040_*` | erfüllt |
| 13 | Replay/Dedupe/Identity im V1-Scope korrekt behandeln | `E2E` P-2.1…P-2.4 („die erste Fassung gewinnt"); `T060 TestNonBlockingInvariantAnchor`; `MUT` M-1, M-6 | erfüllt |
| 14 | Query/UI über die vorgesehene Schicht bedienen | `E2E` P-1.2, P-5 (echter `LogQueryController`, echte Qt-Ereignisschleife); `FI` F-8 | erfüllt |
| 15 | Settings-Ownership trennen | `tests/test_obs050_settings.py` (37 Tests); `T060 TestSinkIsNotRebuiltWithoutReason` | erfüllt |
| 16 | bei UI-Abwesenheit vollständig weiterarbeiten | `tests/test_obs050_contracts.py` – Subprozess ohne Qt-Import, Record trotzdem in der Datenbank | erfüllt |
| 17 | alle relevanten Regressionstests bestehen | volle Suite 1164 passed / 1 vorbestehender Fehlschlag; V1-Kette 652 passed | erfüllt |
| 18 | belastbare Evidence für Failure-/Performance-/Privacy-Fälle besitzen | `V1_FAILURE_INJECTION.md`, `V1_PERFORMANCE.md`, `V1_PRIVACY_REDACTION.md` samt Rohausgaben unter `output/` | erfüllt |

## 2. Der Scope aus dem Implementierungsauftrag

| Scopepunkt | Nachweis |
|---|---|
| End-to-End Canonical Model → Ingress → Queue/Worker → SQLite → Query/UI | `E2E` P-1 (Kette), P-5 (UI), P-6 (Kompositionswurzel) |
| Fehlerisolation sämtlicher Logging-Komponenten | `FI` F-1…F-10 (Store, Sink, Queue, Worker, Normalizer, Aggregatquelle, Provider) |
| Backpressure-/Overload-Verhalten | `FI` F-5; `PERF` B-1 |
| Health-/Counter-Konsistenz | `PERF` B-1.5; `E2E` P-4.3; `FI` F-1.2, F-4.2, F-6.2, F-9.2 |
| Redaction/Privacy | `PRIV` S-1, S-4, S-5 |
| Retention | `PERF` B-5; `tests/test_obs030_sqlite_store.py` |
| Replay/Dedupe, soweit V1 betroffen | `E2E` P-2 |
| Restart-/Recovery-Verhalten | `E2E` P-3 (Neustart über dieselbe Datei), P-4 (Shutdown-Flush); `FI` F-10 (Store-Erholung) |
| Performance unter kontrollierten Lastfällen | `PERF` B-1…B-5 |
| keine Runtime-Blockade | `RI` R-1…R-7; `PERF` B-1 |
| keine Logging-Rekursion | G-2 (eigener, nicht propagierender Logger `observability.internal`), G-4 (ratenbegrenzt), G-6 (interne Records am Handler und an der Queue vorbei); `tests/test_obs020_python_logging_handler.py::test_records_from_observability_internal_are_filtered_out` |
| keine Audio-Payloads/Secrets | `PRIV` S-1, S-3 |
| Transcript-Policy | `PRIV` S-2 |
| UI-/Query-Stabilität | `FI` F-8; `E2E` P-5 |
| Regression gegen bestehende Clientfunktion | `V1_REGRESSION.md` Abschnitte 1–3 |
| Build-/Packaging-relevante Prüfung | `PKG` P-1…P-4 |
| verbliebene technische Schulden korrigieren | `V1_OPEN_POINTS.md` Abschnitte B und N |
| vollständige V1-Evidence | diese sieben `V1_*.md` plus die Rohausgaben |

## 3. Der Runtime-Isolationsnachweis in seiner verbindlichen Form

| Schritt | Bedingung | Ergebnis |
|---|---|---|
| R-1 | Referenzlauf **ohne** Observability, vollständiger Diktatzyklus | Protokoll aufgezeichnet |
| R-2 | mit funktionierender Observability | identisch, 6 Records geschrieben |
| R-3 | Ingress wirft bei **jedem** Aufruf | identisch |
| R-4 | Store wirft bei **jedem** `write_batch` | identisch |
| R-5 | Queue von Beginn an voll | identisch |
| R-6 | Worker startet nie | identisch |
| R-7 | `on_observation` wirft bei jedem Aufruf | identisch **und** Cursordatei mit demselben Endstand |

Bedingung erfüllt: echter `STTController`, echte `FeedbackEngine`, echter
`DualSessionCoordinator`, echter `EventProtocolProcessor`. Doubles nur für
WebSocket und Ausgabegeräte.

## 4. Die acht Mutationschecks

Jede muss einen Test rot werden lassen. Rohausgabe:
`output/probe_obs060_mutation_checks.out.txt`.

| # | Mutation | Ergebnis |
|---|---|---|
| M-1 | `ON CONFLICT DO NOTHING` → einfaches `INSERT` | rot (2 failed) |
| M-2 | `except Exception` im Beobachterwrapper entfernen | rot (2 failed) |
| M-3 | `put_nowait` → blockierendes `put` | rot (Lauf endet nie – Timeout nach 240 s) |
| M-4 | Wasserstandsregel entfernen | rot (3 failed) |
| M-5 | Redaction-Aufruf im Normalizer entfernen | rot (6 failed) |
| M-6 | `WHERE event_id IS NOT NULL` aus dem Index entfernen | rot (1 failed) — Wächter neu, siehe B-3/O-2 |
| M-7 | Handlerlevel auf DEBUG setzen | rot (1 failed) |
| M-8 | `PRAGMA query_only = ON` entfernen | rot (2 failed) |

Vorlauf und Wiederherstellung sind Teil des Nachweises: **vor** der ersten
Mutation laufen alle betroffenen Auswahlen grün (143 passed), und **nach** jedem
Schritt ist jede berührte Datei per SHA-256 als byte-identisch belegt.

Zu M-3: ein Timeout zählt hier als rot, und das ist die richtige Lesart — das
Symptom eines blockierten Producer-Threads ist kein fehlschlagendes Assert,
sondern ein Lauf, der nicht endet.

## 5. Die dreizehn Invarianten (`ARCH §1.1`) und O-01…O-14

| Invariante | Nachweis |
|---|---|
| O-01 Observability Only | `RI` R-1…R-7 |
| O-02 Fan-out statt Vermittlung | `_notify_observer` als erste Anweisung beider Dispatchpfade, rückgabewertfrei; `tests/test_obs040_fanout_hook.py` |
| O-03 Non-Blocking | `PERF` B-1; `MUT` M-3 |
| O-04 Bounded Memory | `PERF` B-1.4; `FD-S1` (kein Ringbuffer) |
| O-05 Failure Isolation | `FI` F-1…F-10 |
| O-06 Struktur statt Textparsing | `CanonicalLogRecord`, Normalizer mit drei Eingängen; `tests/test_obs010_*` |
| O-07 Source Preservation | `E2E` P-2 (`producer_kind`, `event_id`, `server_cursor` überleben) |
| O-08 Replay Safety | `E2E` P-2.2/P-2.3; `MUT` M-1 |
| O-09 Security / Redaction | `PRIV`; `MUT` M-5 |
| O-10 Query Independence | `E2E` P-1.2, P-6.2; `FI` F-8 |
| O-11 Extensible Producer/Provider Boundaries | `LogQueryService` als Registry; `FI` F-8.5 |
| O-12 Admin Separation | in V1 nicht gebaut (`FD-B1`, Teil B) |
| O-13 Runtime-Control-Plane getrennt | `ARCH §9`; `RI` R-7 |
| O-14 Schreibmonopol | `MUT` M-8; `T060 test_the_reader_connection_cannot_write`; `LocalLogProvider` legt die Datei nie an |

## 6. Manuelle Abnahme M-1…M-11

`WP-OBS-060` erklärt das M-Protokoll zur **Pflicht** und stellt fest: *„OHNE ein
vollständiges M-Protokoll gilt V1 als ‚teilweise', nicht als ‚erledigt'."*

Dieser Lauf hat kein Installationssystem mit laufendem Server. Was automatisiert
belegbar war, ist belegt; was einen echten Diktatzyklus gegen einen echten
Server braucht, ist **nicht** erledigt und wird hier ausdrücklich als offen
ausgewiesen.

| M | Inhalt | Zustand |
|---|---|---|
| M-1 | Anwendung starten, Diktat per Hotkey, Text wird eingefügt | **offen** – braucht Installation und Server |
| M-2 | `client.trigger.sent`/`ack_received` mit derselben `command_id`, `transcription.completed` vorhanden | **automatisiert belegt**: `E2E` P-1.4 (Korrelationskette), `RI` (drei Serverevents durch den echten Dispatch). Am realen Server **offen** |
| M-3 | `ORDER BY id` ergibt eine lückenlose Abfolge | **automatisiert belegt**: `E2E` P-1.2, `PERF` B-4 (Keyset über fünf Seiten in OBS-050 nachgemessen). Am realen Server **offen** |
| M-4 | DB schreibgeschützt, Neustart, Diktat: Text wird eingefügt, Health `FAILED_STORE` | **automatisiert belegt**: `FI` F-1 (Health) und `RI` R-4 (Diktatzyklus unverändert). Am realen Gerät **offen** |
| M-5 | Serverneustart während der Client läuft, keine doppelten `event_id` | **automatisiert belegt**: `E2E` P-2.2/P-2.3. Am realen Server **offen** |
| M-6 | Log-Ansicht öffnen, nach Session filtern, Detail und Raw JSON | **automatisiert belegt**: `E2E` P-5 (echter Controller, echte Qt-Schleife, `fetch_raw`). Manuelle Sichtprüfung **offen** |
| M-7 | keine unredigierten `accessToken`-Vorkommen in `logs` und in der JSONL-Datei | **automatisiert belegt**: `PRIV` S-1 über beide Dateien |
| M-8 | bei `store_transcription_content=false` ist ein bekannter Satz nicht auffindbar | **automatisiert belegt**: `PRIV` S-2.1, mit Gegenprobe S-2.4 |
| M-9 | `retention_days` klein setzen, Retention auslösen, Zeilenzahl prüfen | **automatisiert belegt**: `PERF` B-5 (30 000 → 0) |
| M-10 | Anwendung beenden: keine Restthreads, DB konsistent, `client.log` unverändert | **teilweise**: `E2E` P-4 (Shutdown-Flush, `stop()` liefert `True`, Zähler gehen auf), `FD-D7`/`tests/test_obs020_logging_setup_integration.py` (Ausgabe unverändert). Threadprüfung am realen Prozess **offen** |
| M-11 | effektive Dateirechte von Store und Sink einmalig protokollieren (`icacls`) | **belegt**: `V1_PRIVACY_REDACTION.md` Abschnitt 6, mit der ausdrücklich benannten Einschränkung, dass die Messung in einem temporären Verzeichnis desselben Benutzerprofils lief |

**Folgerung, ohne Beschönigung:** Neun der elf M-Punkte sind gegen den echten
Stack automatisiert belegt, M-11 ist protokolliert. Was aussteht, ist die
Durchführung am realen Produktionspfad — mit Datum, Serveradresse und
Clientversion, wie das Work Package es verlangt. Das ist eine
Abnahmehandlung am Installationssystem, die dieser Lauf nicht ersetzen kann und
nicht ersetzt.
