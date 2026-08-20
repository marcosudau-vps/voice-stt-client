# OBS-060 – V1_OPEN_POINTS

Run: `RUN-OBS-060-01_2026-08-18`

Diese Datei führt **alle** in diesem Lauf gefundenen und alle aus früheren
Gates übernommenen Punkte, jeweils mit Zustand. Nichts hier ist stillschweigend
erledigt.

Gliederung:

- **B** – in diesem Lauf gefundene, blockierende Befunde. Alle geschlossen.
- **N** – aus den Gates OBS-030/040/050 für OBS-060 vorgemerkte Beobachtungen.
- **O** – offene Punkte, die eine Entscheidung der unabhängigen Instanz brauchen
  oder ausdrücklich außerhalb von Logging V1 liegen. **Keine Implementierung in
  diesem Lauf nimmt eine dieser Entscheidungen vorweg.**

---

# B – Befunde dieses Laufs (alle geschlossen)

## B-1 – Die Store-Erholung nach ARCH §8.3 war unerreichbar

**Norm.** `ARCH §8.3`, Zeile „Store wirft beim Schreiben": *„nach 5
aufeinanderfolgenden Fehlschlägen Store für 60 s aussetzen, **danach mit einem
leeren Testschreibvorgang prüfen**"*. `CONTRACTS §11.2`: *„Recovery
**Automatisch** und still. Nach Rückkehr in OK genau EIN Record
`logging.recovered` …"*.

**Befund.** Die Aussetzung wird zusammen mit `FAILED_STORE` gesetzt. Ab diesem
Moment lehnt `ObservabilityIngress.submit` **jeden** Record ab
(`health.is_failed()` umfasst `FAILED_STORE`). Damit wird nichts mehr in die
Queue gelegt, der Worker zieht keinen Batch mehr, und `_write_with_policy` —
die **einzige** Stelle, an der die Pause geprüft und `probe_write()` gerufen
wurde — läuft nie wieder. Der vorgeschriebene leere Testschreibvorgang fand
nicht statt, und die als „automatisch" zugesagte Erholung konnte im laufenden
Prozess nicht mehr eintreten: `FAILED_STORE` war faktisch endgültig.

**Reproduktion.** `probe_obs060_b1_reproduction.py`:

```text
FAILED_STORE reached          : True LoggingHealthState.FAILED_STORE
write_calls at that moment    : 10
queue depth                   : 0
--- store is healthy again; waiting well past the 0.5 s pause ---
state after 3 s               : LoggingHealthState.FAILED_STORE
probe_write calls             : 0
rows in db                    : 0
--- a producer tries to log again ---
qsize after the new event     : 0 (0 means the ingress refused it)
state                         : LoggingHealthState.FAILED_STORE
probe_write calls             : 0
```

**Korrektur.** `core/observability/worker.py`: ein neuer Schritt
`_resume_store_if_due()` am Anfang von `_iteration()`. Ist der Store ausgesetzt
und die Pause abgelaufen, läuft `_probe_store()` — aus der **Schleife**, nicht
aus einem Batch. Gelingt die Probe, geht der Weg durch das bestehende
`_on_store_write_success()`; scheitert sie, verlängert sich die Aussetzung um
ein Intervall.

**Warum diese Form.** Es entsteht **kein** neuer Zähler, **kein** neuer
Health-Zustand, **kein** neues Konfigfeld und **kein** zweiter Erholungspfad:
`logging.recovered` schreibt weiterhin genau der Code, der es nach einem
geglückten Batch schreibt. Die Korrektur macht ausschließlich eingefrorenes
Verhalten wieder erreichbar. **Kein normatives Dokument ist verändert.**

**Nachweis.** `V1_FAILURE_INJECTION.md` F-10 (vorher/nachher) und vier
Regressionstests in `TestStoreRecoveryIsReachable`.

## B-2 – Ein `None` des Client-Normalizers wurde nicht gezählt

**Norm.** `CONTRACTS §3`, wörtlich: *„**Der Normalizer wirft nie.** Im Zweifel
liefert er `None`, **und der Aufrufer zählt `malformed`**."*

**Befund.** `ObservabilityIngress.event` hatte für diesen Fall nur
`if record is None: return`. `from_client_event` besitzt genau **ein**
`return None`, und das steht in seinem eigenen `except`-Zweig — der Fall ist
also immer eine verschluckte Normalizer-Ausnahme. Er war vollständig unsichtbar:
kein Zähler, kein Health-Signal, nichts.

**Korrektur.** `core/observability/ingress.py`: `self.health.record_malformed()`
auf diesem Pfad, mit Begründung im Quelltext.

**Bewusst nicht mitkorrigiert:** der Serverpfad. Dort bedeutet `None` auch
*„diese Ergebnisart bildet auf keinen Record ab"* — eine Entscheidung, kein
Zweifel. Es dort zu zählen würde den Zähler bei jedem nicht abgebildeten
Controlframe hochtreiben und seine Bedeutung verfälschen.

**Nachweis.** F-7.3 (vorher `malformed=0`, jetzt `malformed=1`) und fünf
Regressionstests in `TestNormalizerNoneIsCounted`, darunter ausdrücklich einer,
der belegt, dass der Serverpfad **nicht** mitzählt.

## B-3 – Die Mutation M-6 hatte keinen Wächter

**Befund.** Die Mutationstabelle von `WP-OBS-060` erwartet, dass das Entfernen
von `WHERE event_id IS NOT NULL` aus dem UNIQUE-Index dazu führt, dass
„Clientrecords fälschlich dedupliziert" würden. Gemessen trifft das nicht zu
(siehe **O-2**), und es existierte **kein** Test, den diese Mutation rot macht:
`tests/test_obs030_sqlite_store.py` prüft nur den **Namen** des Index.

**Korrektur.** Zwei Tests in `TestFrozenDdlIsPartial`, die den eingefrorenen
DDL-Bestandteil selbst prüfen (`CONTRACTS §5.2` friert die DDL ein, `FD-C7`
nennt den Index ausdrücklich **partiell**) und die messbare Folge belegen: der
Index trägt keinen Eintrag für eine Zeile ohne `event_id`.

---

# N – Übernommene Beobachtungen aus früheren Gates

| # | Herkunft | Beobachtung | Zustand nach OBS-060 |
|---|---|---|---|
| N-2 | OBS-030 Gate II | `_consecutive_loop_failures` wurde von den beiden Startupguards mitgezählt | **behoben** – Reset vor der Schleife, `core/observability/worker.py`; Regression in `TestLoopFailureBudget` |
| N-3 | OBS-030 Gate II | `ObservabilityManager(...)`, `.start()` und `setup_logging(...)` lagen **vor** dem `try`, obwohl `ARCH §6.2` ein `try/finally` „um den GESAMTEN Ablauf" verlangt | **behoben** – nur der Konstruktor bleibt außerhalb (davor gibt es nichts zu stoppen), `app.py` |
| W-3 | OBS-030 Gate II | nicht zugeordnete Verwürfe während einer Störung brechen die arithmetische Identität der Zähler | **bleibt offen, bewusst** – siehe O-4 |
| N-1 | OBS-040 Gate | `_enqueue_audio_packet` liest `qsize()` und steht damit nicht unter den benannten Auslegungen A-1…A-6 | **redaktionell, offen** – siehe O-5 |
| N-2 | OBS-040 Gate | Zahlenfehler in `RUN-01/RESULT.md` („175" statt 178 subtests) | **nicht angefasst** – historische Evidence eines abgeschlossenen, gate-geprüften Laufs wird nicht nachträglich umgeschrieben; siehe O-6 |
| N-3 | OBS-040 Gate | `client.audio.stream_stats` trägt zwei Felder über die §8.6-Liste hinaus | **offen** – siehe O-7 |
| N-4 | OBS-040 Gate | Hot-Path-Zähler werden nie zurückgesetzt; der Kommentar an `client.audio.stream_stopped` behauptete „die Summen einer Session" | **behoben** – Kommentar richtiggestellt, `core/audio_capture.py`; der Code bleibt unverändert |
| N-5 | OBS-040 Gate | `correlation_id=f"client:{event_type}:{timestamp}"` ist eine Identität, keine Korrelation | **offen** – siehe O-8 |
| N-6 | OBS-040 Gate | `RUN-OBS-040-01` besitzt kein `RUN_REPORT.md` | organisatorisch; dieser Lauf legt eines an |
| N-7 | OBS-040 Gate | ein von einem Quelltexttest geformter Kommentar in `AudioCapture._audio_callback` | **offen, nicht blockierend** – siehe O-9 |
| N-1 | OBS-050 Gate | `_on_config_applied` baute bei **jedem** Apply einen neuen `JsonlSink` | **behoben** – neuer Sink nur bei geänderter Sinkkonfiguration, `core/observability/manager.py` |
| N-2 | OBS-050 Gate | ein werfendes `_build_sink` brach vor `_follow_enabled_state` ab; eine gleichzeitige `enabled`-Änderung fiel still aus | **behoben** – drei eigene Guards statt eines gemeinsamen |
| N-3 | OBS-050 Gate | `_restore_runtime_config` stellt den Observability-Zustand nicht mit her | **offen** – siehe O-10 |
| N-4 | OBS-050 Gate | `complete=False` für `limit <= 0`, obwohl nichts abgeschnitten wurde | **behoben** – `core/observability/query/local.py`; Regression in `TestProviderCompleteFlag` |
| N-5 | OBS-050 Gate | `LogTableModel.max_rows = 5000` ist in der Statuszeile nicht sichtbar | **offen** – siehe O-11 |
| N-6 | OBS-050 Gate | die `.gitignore`-Negation `!ui/logs/` würde künftige Laufzeitartefakte unter `ui/logs/` mitversionieren | **geprüft, unverändert** – `probe_obs060_packaging.py` P-3.2 belegt, dass `ui/logs/__pycache__` weiterhin ignoriert ist |
| N-7 | OBS-050 Gate | in der Checkliste steht „OBS-010 – Implementierung" unangehakt, während das Gate angehakt ist | **nicht angefasst** – die Regel „bestehende frühere Häkchen nicht verändern" gilt; siehe O-12 |

---

# O – Offene Punkte

## O-1 – Kein `logging.record_rejected` für eine verschluckte Normalizer-Ausnahme

**Ausgangsproblem.** `ARCH §8.3`, Zeile „Normalizer-Ausnahme": *„Record
verworfen; **ein** Ersatzrecord `logging.record_rejected` mit Komponente und
**Ausnahmetyp**, **ohne** Originaldaten"*, Health `OK` + `malformed++`.

**Konflikt.** `CONTRACTS §3` verlangt gleichzeitig, dass der Normalizer **nie
wirft** und „im Zweifel `None`" liefert. `from_client_event` hält sich daran und
fängt seine Ausnahme selbst ab. Damit erreicht den Ingress kein
Ausnahmeobjekt — und ohne Ausnahmeobjekt gibt es keinen **Ausnahmetyp**, den der
Ersatzrecord nach §8.3 tragen müsste. Der `except`-Zweig des Ingress, der
`emit_record_rejected(...)` ruft, ist nur noch für Aufruffehler (z. B. ein
fehlendes Pflicht-Keyword) erreichbar, nicht für Datenfehler.

**Auslegbare Lesarten.**

1. §3 hat Vorrang: der Normalizer bleibt wie er ist, und §8.3 meint mit
   „Normalizer-Ausnahme" nur die Fälle, in denen tatsächlich eine Ausnahme die
   Grenze erreicht. Dann ist der heutige Zustand vollständig — `malformed++`
   geschieht seit B-2, ein Ersatzrecord ist nicht geschuldet.
2. §8.3 hat Vorrang: der Ersatzrecord ist für jeden verworfenen Record
   geschuldet. Dann muss der Normalizer dem Aufrufer den Ausnahmetyp mitteilen —
   das ist eine **Signaturänderung an einer eingefrorenen Funktion**
   (`CONTRACTS §3`) und damit eine echte Contract-Änderung.

**Warum hier nichts implementiert wurde.** Lesart 2 verlangt eine Erweiterung
eines eingefrorenen Vertrags. Der Kernbefund B-2 (`malformed` wird gezählt) ist
**ohne** diese Erweiterung vollständig behoben; nach dem Prüfstein „lässt sich
der Befund auch ohne die strittige Erweiterung beheben?" ist die Erweiterung
kein Blocker und darf nicht mitgeliefert werden.

**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

## O-2 – Die Mutationstabelle begründet M-6 mit einer unzutreffenden Annahme

**Ausgangsproblem.** `WP-OBS-060` und Plan §13 erwarten für die Mutation
„`WHERE event_id IS NOT NULL` aus dem Index entfernen" die Folge
„Clientrecords würden fälschlich dedupliziert".

**Messung.** In SQLite sind `NULL`-Werte in einem UNIQUE-Index **immer**
voneinander verschieden. Ein voller UNIQUE-Index über `(producer_id, event_id)`
lässt zwei Clientzeilen ohne `event_id` also genauso durch wie der partielle:

```text
--- PARTIAL index (production) ---
  two NULL-event_id client rows -> rows stored: 2
  same event_id twice           -> rows: ['first']
--- FULL index (mutation M-6) ---
  two NULL-event_id client rows -> rows stored: 2
  same event_id twice           -> rows: ['first']
sqlite version: 3.49.1
```

**Bewertung.** Der Nutzen des Prädikats liegt nicht in der Dedupe-Semantik,
sondern darin, dass der Index ausschließlich Serverzeilen mit `event_id` trägt.
`FD-C7` nennt den Index ausdrücklich **partiell**, `CONTRACTS §5.2` friert die
DDL ein. Der Wächter, den dieser Lauf ergänzt (B-3), prüft deshalb genau das —
und **nicht** eine Dedupe-Folge, die es nicht gibt.

**Offen bleibt:** ob die Begründungsspalte der Mutationstabelle im Work Package
und im Gesamtplan richtiggestellt werden soll. Das sind planerische Dokumente,
die ein Implementierungslauf nicht ändert.
**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

## O-3 – Zwei vorbestehende, laufsfremde Änderungen im Arbeitsbaum

`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/20_PLANUNG/planung_migration/15_OFFENE_FUNDE_UND_AENDERUNGSLOG.md`
(+9 Zeilen) und `…/16_TRACEABILITY_MATRIX.md` (1 Zeile) liegen seit **vor**
diesem Lauf uncommittet im Baum. Inhaltlich sind es reine Markdown-Formatierungen
(Leerzeilen vor Überschriften, Tabellentrenner). Sie gehören zum
Triggerarchitektur-Workstream, **nicht** zu Logging V1, und wurden in diesem Lauf
weder angefasst noch zurückgenommen. Sie gehören **nicht** in einen
Logging-Commit.

## O-4 – W-3: Zählerlücke bei nicht zugeordneten Verwürfen

Aus dem OBS-030-Gate übernommen, dort bereits abschließend bewertet: bei
ausgesetztem oder degradiertem Store gilt vorübergehend `enqueued > written`,
ohne dass ein `dropped_*`-Zähler das auffängt. `ARCH §7.3` ist mit „Zähler –
**eingefroren**" abschließend und kennt für diesen Fall keinen Zähler,
`CONTRACTS §11.2` friert `LoggingHealthSnapshot` entsprechend ein. **Es wird
hier weder ein neuer Zähler verlangt noch akzeptiert.** Sichtbar bleibt der Fall
über `store_errors`, den Health-State und die ratenbegrenzte stderr-Zeile.
Unverändert übernommen, **nicht** repariert.

## O-5 – OBS-040 N-1: `_enqueue_audio_packet` liest `qsize()`

Die Stelle ist nach dem Gate „nicht vermeidbar" (das Aggregat aus `ARCH §8.6`
verlangt `max_send_queue_depth`, und ein Maximum über die Zeit lässt sich aus
einem 5-Sekunden-Abtastpunkt nicht rekonstruieren) und O(1) ohne Lock, Format,
JSON oder `submit`. Zu beanstanden war nur, dass sie **nicht** unter den
benannten Auslegungen A-1…A-6 des OBS-040-Laufs steht. Das ist eine
redaktionelle Ergänzung an der Evidence eines abgeschlossenen Laufs; dieser Lauf
nimmt sie nicht vor. **Kein Blocker.**

## O-6 – OBS-040 N-2: Zahlenfehler in abgeschlossener Evidence

`40_EVIDENCE/OBS-040/RUN-01_2026-08-17/RESULT.md` nennt „175 subtests", gemessen
sind 178. Die Datei gehört zu einem abgeschlossenen, gate-geprüften Lauf.
Historische Evidence nachträglich umzuschreiben würde den Nachweiswert der
Kette beschädigen; der Fehler ist hier benannt und bleibt dort stehen.
**Kein Blocker.**

## O-7 – OBS-040 N-3: zwei Zusatzfelder in `client.audio.stream_stats`

`capture_queue_depth` und `send_queue_depth` gehen über die in `ARCH §8.6`
ausgeschriebene Feldliste hinaus. `details` ist ein offenes Mapping, also liegt
kein Vertragsbruch vor — aber es ist eine unbenannte Erweiterung einer Liste,
die der Freeze ausschreibt. Eine Entfernung wäre ein Funktionsverlust ohne
Auftrag, eine Aufnahme in die Liste eine Freeze-Änderung.
**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

## O-8 – OBS-040 N-5: `correlation_id` aus einer Wanduhrzeit

`STTController._emit_feedback_event` bildet
`correlation_id=f"client:{event_type.value}:{event.timestamp}"`. Die Form
„`<namensraum>:<wert>`" nach `CONTRACTS §1.1` ist erfüllt, aber der Wert
korreliert mit nichts anderem. Eine Änderung berührt die Korrelationsketten von
`CONTRACTS §12` und ist damit keine reine Aufräumarbeit.
**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

## O-9 – OBS-040 N-7: ein von einem Test geformter Kommentar

Der Kommentar in `AudioCapture._audio_callback` vermeidet Wörter, die ein
OBS-020-Quelltexttest verbietet. Inhaltlich ist der Code sauber und die
Testabsicht erfüllt; ein von einem Test geformter Kommentar bleibt trotzdem
fragil. Beide möglichen Korrekturen (Kommentar umschreiben oder Quelltexttest
lockern) sind Eingriffe in gate-geprüften Bestand ohne fachlichen Anlass.
**Kein Blocker.**

## O-10 – OBS-050 N-3: `_restore_runtime_config` stellt Observability nicht mit her

Schlägt `apply_runtime_config` **nach** dem Observability-Apply fehl, stellt
`_restore_runtime_config` die alte Konfiguration wieder her, **nicht** aber den
alten Observability-Zustand. `CONTRACTS §10.4` verlangt das nicht — im Gegenteil:
§10.4 friert ein, dass ein Fehler im Logging-Apply das Apply-Ergebnis **nicht**
beeinflussen darf, und eine Rückabwicklung würde diese Richtung umkehren. Eine
Änderung wäre eine Erweiterung der Apply-Kette.
**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

## O-11 – OBS-050 N-5: `max_rows = 5000` ist in der Statuszeile unsichtbar

`LogTableModel.max_rows` schneidet auch in der Historie die ältesten Zeilen ab.
Das ist O-04-konform und gewollt, aber für den Nutzer nicht erkennbar. Eine
Anzeige dafür ist eine UI-Erweiterung; `CONTRACTS §9.3` schreibt den
V1-Umfang der Ansicht aus und nennt sie nicht.
**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

## O-12 – OBS-050 N-7: „OBS-010 – Implementierung" ohne Haken

In `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` ist „OBS-010 – Implementierung"
unangehakt, während „OBS-010 – Gate Review" angehakt ist. Vorbestehend, nicht
aus diesem Lauf. Die Regel der Datei lautet „bestehende frühere Häkchen nicht
verändern", und ein Implementierungslauf setzt keine fremden Haken.
**Status: Richtigstellung durch die entscheidende Instanz ausstehend.**

## O-13 – Die Testumgebung blockiert ohne einen externen Shim

Auf dieser Maschine hängt `platform._wmi_query` unbegrenzt, sodass jeder
Testlauf blockiert, der `sounddevice` importiert. Der ausgelieferte Client ist
nicht betroffen — `voice-stt-client.spec` neutralisiert dieselbe Sonde für den
gefrorenen Build (`scripts/pyinstaller_runtime_platform.py`). Für die Testläufe
dieses Runs wurde ein `sitecustomize.py` **außerhalb** des Projektbaums benutzt;
**keine Projektdatei ist dafür verändert worden**. Ob die Testumgebung eine
dauerhafte, versionierte Lösung bekommen soll (etwa ein `conftest.py`), ist eine
organisatorische Frage, die ein Implementierungslauf nicht entscheidet.
Details in `V1_TEST_RESULTS.md`, Abschnitt 5.
**Status: Entscheidung durch die unabhängige Instanz ausstehend.**

---

# Zusammenfassung für das V1-Gate

- **Blockierend offen: nichts.** B-1, B-2 und B-3 sind geschlossen und mit
  Regressionstests versehen.
- **O-1, O-2, O-7, O-8, O-10, O-11, O-13** brauchen eine Entscheidung, liegen
  aber sämtlich **außerhalb** der V1-Gate-Kriterien: keiner betreibt Runtime-
  oder Lifecycle-Autorität, keiner verletzt Redaction, Backpressure,
  Fehlerisolation oder die Transcript-Policy.
- **O-3, O-4, O-5, O-6, O-9, O-12** sind benannte, bewusst nicht reparierte
  Punkte.
- Keiner der offenen Punkte gefährdet die anschließende
  Triggerarchitektur-Phase: alle liegen entweder in der Logging-Domäne selbst
  (die beobachtend bleibt) oder in der Dokumentation.
