# LOGGING_OPEN_DECISIONS

Deckt Auftragsabschnitt **23**.

**Aufnahmekriterium:** Nur echte Entscheidungen. Fragen, die sich am Code
eindeutig beantworten lassen, stehen **nicht** hier, sondern sind in den
Analysedokumenten beantwortet. Am Ende dieses Dokuments steht eine Liste der
Fragen aus den beiden Entwürfen, die durch den Code bereits entschieden sind —
damit sie nicht ein zweites Mal diskutiert werden.

---

## OD-01 — Name des Pakets: `logging` oder `observability`

**Frage.** Heißt das neue Paket `core/observability/` oder `core/logging/`?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | `core/observability/`, Konfigabschnitt `logging.observability` |
| B | `core/logging/`, Konfigabschnitt `logging.*` erweitert |
| C | `core/obs/` (kurz) |

**Vor-/Nachteile.**
- **A** trennt sichtbar vom bestehenden `core/logging_setup.py` und vom
  stdlib-Modul `logging`. Der Begriff deckt auch Serverevents und Metriken ab,
  die keine „Logs" sind. Nachteil: zwei Begriffe für den Nutzer, wobei die
  Konfiguration den Bruch über `logging.observability` überbrückt.
- **B** ist für den Nutzer einfacher, erzeugt aber innerhalb des Pakets ein
  echtes Problem: `core/logging/` neben `import logging` ist bei absoluten
  Importen zwar zulässig, aber jeder Leser muss zweimal hinsehen — und das
  Repository importiert `logging` in 20 Modulen.
- **C** spart nichts und ist weniger lesbar.

**Empfehlung.** **A.** Der Konflikt mit dem stdlib-Namen in einem Repository,
das `logging` überall importiert, ist ein realer Stolperstein; die
Nutzersichtbarkeit wird über den Konfigabschnitt und den Tabnamen
„Logging & Diagnose" gelöst.

**Blockiert V1?** **JA** — betrifft jeden Dateipfad und jeden Import.

---

## OD-02 — Zusätzliche Spalte `transcription_id`

**Frage.** Wird `transcription_id` als eigene Spalte geführt, oder wird der
Wert in `correlation_id` untergebracht?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Eigene Spalte `transcription_id` |
| B | Nur `correlation_id`, Wert als `"transcription:<id>"` |

**Vor-/Nachteile.**
- **A**: `transcriptionId` ist ein Feld erster Ordnung im Server-Envelope
  (`event_models.py:156`) und in der Server-DB indiziert
  (`event_logging.py:477`). Es ist der einzige Schlüssel, der alle Ereignisse
  eines Final-Transkripts über HTTP und WebSocket hinweg verbindet
  (`structured-logging.md:53-56`). Der spätere `ServerHistoryProvider` kennt
  ihn als eigenen Query-Parameter. Kosten: eine Spalte, kein Index.
- **B**: eine Spalte weniger, aber `correlation_id` würde zwei Namensräume mit
  völlig verschiedener Herkunft mischen (clientseitig erzeugte
  Feedback-Korrelationen und serverseitige Transkriptions-IDs). Ein
  Gleichheitsfilter auf `correlation_id` würde dann davon abhängen, dass die
  Präfixe stimmen.

**Empfehlung.** **A.** Der Auftrag verlangt „keine unnötigen Felder" — dieses
ist nachweislich nötig, weil es ein bestehender, indizierter Fremdschlüssel des
Servers ist.

**Blockiert V1?** **JA** — betrifft Schema und Migration.

---

## OD-03 — Default für `store_transcription_content`

**Frage.** Werden Transkriptinhalte standardmäßig lokal gespeichert?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Default `false` — Inhalte werden redigiert, Metadaten und Zeichenzahl bleiben |
| B | Default `true` — der bisherige Zustand der `client.log` wird fortgeschrieben |

**Vor-/Nachteile.**
- **A** ist datensparsam. Nachteil: bei der Diagnose eines
  Deduplikationskonflikts fehlt genau die Information, die den Konflikt zeigt
  (`controller.py:2077-2080` loggt heute beide Texte).
- **B** entspricht dem heutigen faktischen Zustand: `stt_session.py:1296-1300`
  schreibt bereits die ersten 80 Zeichen jedes Finals auf INFO in die
  `client.log`, und `controller.py` schreibt bei Konflikten den vollen Text auf
  WARNING. Ein Default `false` **verringert** also die heute gespeicherte
  Menge — das ist gut, überrascht aber möglicherweise.

**Empfehlung.** **A (`false`)**, mit einer ausdrücklichen Beschreibung im
Settings-Tab („Transkripttexte in der Diagnosehistorie speichern — betrifft
auch technische Logzeilen"). Begründung: Die neue Historie ist deutlich
langlebiger (Retention 14 Tage, 200.000 Einträge) als die rotierende
`client.log` (4 × 5 MiB). Was heute in Tagen verfällt, bliebe sonst wochenlang.

**Blockiert V1?** **NEIN** — der Mechanismus wird in jedem Fall gebaut; nur der
Defaultwert steht zur Wahl und ist eine Zeile.

---

## OD-04 — Default für `store_raw_payload`

**Frage.** Wird der vollständige Serverpayload standardmäßig gespeichert?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | `true` — Rohpayload aller `/ws/logs`-Events wird gespeichert |
| B | `false` — nur `details` (also `envelope.data`) |
| C | granular: `true` für `audit`/`transcription`, `false` für `performance` |

**Vor-/Nachteile.**
- **A**: forensisch vollständig, entspricht Zielbild §13. Kosten: `raw_json`
  ist das größte Feld; bei aktivem `realtime_log_detail=events` erzeugt der
  Server einen Performance-Record je Realtime-Ausgabe
  (`structured-logging.md:142-146`), und das kann viel sein.
- **B**: spart am meisten, verliert aber genau die Felder, die der
  Client-Envelope in `extra` schiebt — darunter `meldung` und alle künftigen
  Servererweiterungen. Damit wäre der Store nicht mehr vorwärtskompatibel.
- **C**: löst das Volumenproblem an der einzigen Stelle, an der es entsteht.

**Empfehlung.** **C**, implementiert als eine einzige Regel: `raw` wird
gespeichert, außer `channel == "performance"`. Ein granulares Feld je Channel
in der Konfiguration wäre Überkonfiguration.

**Blockiert V1?** **NEIN.**

---

## OD-05 — Retention-Defaults

**Frage.** Welche Standardgrenzen gelten für die lokale Historie?

**Technische Optionen.**

| Option | `retention_days` | `max_entries` | `max_db_bytes` |
|---|---|---|---|
| A | 7 | 100.000 | 128 MiB |
| B | 14 | 200.000 | 256 MiB |
| C | 30 | 1.000.000 | 1 GiB |

**Vor-/Nachteile.** Der Zweck von V1 ist ausdrücklich, die kommende
Triggerarchitektur-Migration nachvollziehbar zu machen. Eine Migration dauert
Wochen; ein Fehler wird oft erst Tage später bemerkt. 7 Tage sind zu knapp.
1 GiB auf einem Arbeitsplatzrechner ist unhöflich. Zum Vergleich: die
bestehende `client.log` belegt maximal 20 MiB (`config.py:793-794`), die
Transkripthistorie ist auf 100 Einträge begrenzt (`config.py:649`).

**Empfehlung.** **B.** Zusätzlich: `retention_days` und `max_entries` wirken
**beide** (das Erste, das greift, gewinnt), und `max_db_bytes` ist nur eine
Notbremse.

**Blockiert V1?** **NEIN.**

---

## OD-06 — Datei-Sinks in V1: JSONL, Text, beide oder keiner

**Frage.** Welche optionalen Datei-Sinks werden in V1 gebaut?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | nur JSONL |
| B | JSONL und Text |
| C | keiner in V1 |

**Vor-/Nachteile.**
- **C** ist verlockend, weil der bestehende `RotatingFileHandler` bereits eine
  Datei schreibt und mit `json_format: true` sogar JSON Lines
  (`logging_setup.py:26-43`). **Aber**: diese Datei enthält nur Python-Logs, nie
  Serverevents und nie strukturierte Clientevents. Sie ist also **kein** Ersatz.
- **A** liefert genau eine maschinenlesbare Datei, die man weiterreichen kann,
  ohne die SQLite-Datei zu kopieren — praktisch für die Übergabe eines
  Fehlerberichts.
- **B** verdoppelt Formatcode, Rotationscode und Fehlerfläche für einen
  Textexport, den man aus JSONL in einer Zeile erzeugen kann.

**Empfehlung.** **A.** Ein Format, ein Test, ein Fehlerpfad.

**Blockiert V1?** **NEIN** — OBS-12 ist das letzte inhaltliche Paket und kann
entfallen, ohne etwas anderes zu berühren.

---

## OD-07 — Zeitpunkt und Umfang des `hello`-Records

**Frage.** Wird die `hello`-Nachricht von `/ws/transcribe` überhaupt als Record
gespeichert, und wenn ja, mit welchem Inhalt?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | gar nicht speichern |
| B | nur eine Whitelist (Session, `logAccess.available/code/reason/expiresAt/serverInstanceId/oldest/latestCursor`, `sessionConfig`, `activationConfig`, `sessionCapabilities`) |
| C | vollständig, aber redigiert |

**Vor-/Nachteile.**
- `hello` ist diagnostisch außerordentlich wertvoll: es enthält
  `sessionConfig` mit `warnings`/`fallbacks`/`ignoredFields`
  (`stt_session.py:1174-1182`) und `activationConfig` — genau die Felder, an
  denen sich Fehlkonfigurationen zeigen. Es enthält aber auch
  `logAccess.accessToken` (Befund P-1 im Audit).
- **C** verlässt sich darauf, dass die Redaction jeden Weg abdeckt. Sie tut es
  vermutlich; aber „vermutlich" ist bei einem Token der falsche Maßstab.
- **A** verliert die wertvollsten Konfigurationsdiagnosedaten des Systems.

**Empfehlung.** **B.** Eine ausdrückliche Whitelist ist bei einem Payload, der
nachweislich ein Geheimnis enthält, die einzig belastbare Form. Die Redaction
läuft **zusätzlich**.

**Blockiert V1?** **NEIN**, aber die Entscheidung muss **vor** OBS-08 fallen.

---

## OD-08 — Behandlung von `activation_id`

**Frage.** Wird `activation_id` in V1 überhaupt befüllt, obwohl die Zuordnung
serverseitig nachweislich unzuverlässig ist?

**Belegter Hintergrund.**
`LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md §1.2` weist nach: die
`activationId` wird zum Publikationszeitpunkt frisch aus dem Controller gelesen;
ist die Activation bereits geschlossen, fehlt sie; ist inzwischen eine neue
geöffnet, ist sie **falsch**.

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Spalte befüllen, in der UI als „diagnostisch" kennzeichnen |
| B | Spalte anlegen, aber leer lassen, bis der Server die Bindung korrigiert |
| C | keine Spalte |

**Vor-/Nachteile.**
- **A** liefert für die Mehrzahl der Ereignisse den richtigen Wert und macht
  gerade die **falschen** Zuordnungen sichtbar — was für die kommende Migration
  wertvoll ist, weil genau dieser Defekt behoben werden soll.
- **B** wäre eine tote Spalte.
- **C** würde nach der Serverkorrektur eine Migration erzwingen.

**Empfehlung.** **A**, mit einer harten Zusatzregel: Der Wert darf **nie** zum
Zusammenfassen oder Gruppieren im fachlichen Sinn benutzt werden, und der
Filter „nur diese Activation" wird in der UI mit einem Hinweis versehen. Der
Wert wird ausschließlich aus `envelope.data.activationId` übernommen, nie
clientseitig ergänzt oder geraten.

**Blockiert V1?** **NEIN** — die Spalte existiert in jedem Fall (OD-02-Schema).

---

## OD-09 — Capability-Modell für spätere Admin-Funktionen

**Frage.** Welches Modell beschreibt später Adminrechte — das im Zielbild §27
skizzierte benannte Capability-Set oder der binäre Serverzustand?

**Belegter Hintergrund.** Der Server kennt **kein** benanntes Capability-Set für
Admins, sondern nur „admin ja/nein" plus die daraus abgeleiteten Erweiterungen
`allSessions`, `allChannels`, Channel `system` (`server.py:6511-6544`).
`sessionCapabilities` ist etwas anderes: Fähigkeiten der Session, nicht Rechte
eines Nutzers.

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Serverseitig ein benanntes Capability-Set einführen (`globalLogsRead`, `historyLogsRead`, …) |
| B | Clientseitig aus dem binären Adminstatus ableiten |
| C | Vollständig offen lassen, bis V2 beginnt |

**Empfehlung.** **C für jetzt, mit Tendenz zu B.** V1 baut keine
Auth-Schnittstelle; die Entscheidung kostet heute nichts. Die Tendenz zu B
begründet sich damit, dass ein Capability-Set nur dann Wert hat, wenn der Server
Rechte **feiner** vergeben kann als „alles oder nichts" — und das ist eine
Serverproduktentscheidung, keine Clientarchitekturfrage.

**Blockiert V1?** **NEIN.** V1 muss nur sicherstellen, dass
`ProviderState.AUTH_REQUIRED` von Anfang an existiert (getan, §15).

---

## OD-10 — Nächster Provider nach V1: Session-Historie oder Admin

**Frage.** Was ist der zweite Provider — `SessionHistoryProvider`
(eigene Session, kein Admin-Key) oder `ServerHistoryProvider` (Admin)?

**Belegter Hintergrund.** `hello.logAccess` liefert bereits `historyPath`
(`/api/logs/events`); der Client **verwirft** das Feld heute
(`session_coordinator.py:286-306`). Der vorhandene Session-Token berechtigt zu
`/api/logs/sessions/{sessionId}` **ohne** Admin-Key (`server.py:6372-6377`).

**Empfehlung.** **`SessionHistoryProvider` zuerst.** Er braucht keine
Authentifizierung, keinen Key in der UI, keine `ServerControlConnection` und
liefert sofort den wertvollsten Vergleich: „Serverhistorie hat
`transcription.completed`, lokale Historie nicht" — genau der Diagnosefall aus
Zielbild §24.

**Blockiert V1?** **NEIN.** Die Entscheidung beeinflusst V1 nur insoweit, als
`_build_access` das Feld `historyPath` später übernehmen müsste — eine additive
Zeile, die V1 **nicht** vorwegnimmt.

---

## OD-11 — Umgang mit dem doppelten Datenverzeichnis

**Frage.** `RealtimeSTT Client` (Logs, Config, Cursor, LEFX) und
`RealtimeSTT_Client` (Transkripthistorie) existieren nebeneinander
(Befund D-1). Wie geht V1 damit um?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Neue Datei in `RealtimeSTT Client`, bestehende Abweichung unangetastet |
| B | Vereinheitlichen und die Historie migrieren |

**Empfehlung.** **A.** Option B ist eine Produktänderung mit
Datenmigrationsrisiko an einer Stelle, die das Logging-Vorhaben nicht berührt,
und fällt damit unter Auftrag §21 (nichts reparieren, was nicht zum Auftrag
gehört). Die Abweichung wird dokumentiert.

**Blockiert V1?** **NEIN.**

---

## OD-12 — Verhalten bei einem logging-internen Fatalfehler

**Frage.** Was geschieht, wenn der LoggingWorker endgültig ausfällt?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Still weiterlaufen; nur Health, stderr und die Statuszeile im LogWindow |
| B | Zusätzlich eine Tray-Benachrichtigung |
| C | Worker automatisch neu starten |

**Vor-/Nachteile.**
- **B** würde ein Diagnoseproblem zu einer Nutzerunterbrechung machen.
  `TrayController.notify` wird heute nur für Dinge verwendet, die den Nutzer
  wirklich betreffen (Gerätemute, LED-Simulation).
- **C** klingt hilfreich, ist es aber selten: ein Worker, der an einem defekten
  Store stirbt, stirbt nach dem Neustart erneut, und ein Neustartzyklus wäre
  eine zusätzliche Fehlerquelle im Shutdownpfad.

**Empfehlung.** **A**, mit einer Ausnahme: Wenn der LogWindow **geöffnet** ist,
zeigt die Statuszeile den Zustand deutlich. Wer die Logs ansieht, soll sofort
sehen, dass sie unvollständig sind.

**Blockiert V1?** **NEIN.**

---

## OD-13 — Erfassung von `client.log`-Duplikaten

**Frage.** Der bestehende `RotatingFileHandler` und der neue Store schreiben
dieselben Python-Logzeilen. Bleibt das so?

**Technische Optionen.**

| Option | Beschreibung |
|---|---|
| A | Beides bleibt; die `client.log` ist die Rückfallebene |
| B | `client.log` nur noch für WARNING+, der Store bekommt alles |
| C | `client.log` abschalten, sobald der Store läuft |

**Empfehlung.** **A für V1.** Der bestehende Weg ist heute die einzige
Diagnosequelle und darf erst dann eingeschränkt werden, wenn der neue Weg über
mehrere Wochen im echten Betrieb bewiesen ist. Die Doppelung kostet
Plattenplatz, nicht Korrektheit. **B** ist ein sinnvoller Schritt nach der
Triggerarchitektur-Migration, nicht davor.

**Blockiert V1?** **NEIN.**

---

# Bereits am Code entschieden — nicht mehr zu diskutieren

Die folgenden Punkte stehen als „offene Entscheidung" in
`LOGGING_ZIELBILD_..._ENTWURF.md §46` und `LOGGING_V1_ABGRENZUNG_ENTWURF.md §13`.
Sie sind durch den Code eindeutig beantwortet und werden hier nur mit der
Fundstelle geschlossen.

| Entwurfsfrage | Antwort | Fundstelle |
|---|---|---|
| exakte Client-Channels | die vier Server-Channels, **klein** geschrieben; keine zusätzlichen | Audit §6 |
| `producer_kind`-Werte | `client`, `server`, `led`, `other` — `led` ist nötig, weil LEFX in-process läuft | Audit §17 |
| Dedupe-Schlüssel des Serverstreams | `(producer_id, event_id)`, partieller UNIQUE-Index | Schema §7.3 |
| lokale DB-Datei und Ablageort | `%LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3` | Schema §9.7 |
| SQLite-Schema-Versionierung/Migration | `PRAGMA user_version` + `schema_meta`, keine Migrationstabelle | Schema §9.4 |
| Queue-Größe und Priorisierung | zwei Queues, 1024/8192, zwei Prioritäten | Concurrency §10.4 |
| wie strukturierte Clientevents emittiert werden | ein injizierter `ObservabilityIngress`, kein Eventbus, kein Singleton | Audit §3.2 |
| genaue Adaptergrenze zum Server-Eventstream | `DualSessionCoordinator._handle_event` / `_handle_control` | Audit §2.4 |
| genaue Auth-/Capability-Schnittstelle des Servers | vollständig ermittelt; V1 nutzt sie nicht | Boundaries §16.1 |
| exakter UI-Ort der Logansicht | eigenes, nicht-modales `LogWindow` | Boundaries §13.3 |
| exakter UI-Ort der Logging-Konfiguration | sechster Tab im bestehenden `SettingsDialog` | Boundaries §13.3 |
| Konfigurationsmodell | `logging.observability.*` als Unterabschnitt | Boundaries §13.2 |
| Shutdown-/Flush-Verhalten | `manager.stop(2.0)` **nach** `bridge.stop(10.0)` | Plan, Übergreifende Regeln |
| Metriken/Health für gedroppte Records | `LoggingHealthSnapshot`, Zähler, ein `logging.records_dropped` nach Erholung | Concurrency §11.5 |
| ob `ServerHistoryProvider` cached | entfällt — er ist nicht Teil von V1 | Boundaries §16.2 |
| ob Text-/JSONL-Sinks in V1 | offen als OD-06, aber die Frage „welches Format" ist beantwortet: JSONL | OD-06 |
| endgültiges CanonicalRecord-Schema | Feld für Feld belegt | Schema §5.1 |
| endgültige Feldnamen | ebenda | Schema §5.1 |
| `host` sinnvoll? | nein, in V1 nicht führen | Schema §5.1/5.2 |
| `sequence` nötig? | nein, `logs.id` genügt | Schema §5.2 |
| `provider`/`source_record_id` nötig? | nein als Spalte, ja am Query-DTO | Schema §5.2 |
| separate `server_event_id` und `record_id`? | ja, beide | Schema §5.2 |
| Enum-Versionierung | TEXT, offen, nur `level` geschlossen | Schema §5.2 |
