# OBS-030 – Gate Review II (unabhängiger Re-Review, frische Session)

Datum: 2026-08-17
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-030_GATE_REVIEW_II.md`
(verbindlicher Gate-Auftrag: `Prompts/OBS-030_GATE_REVIEW.md`)
Geprüfter Stand: OBS-030-Endstand seit dem letzten freigegebenen lokalen
Commit `b363346` — RUN-01, Gate-FAIL, Korrekturlauf RUN-OBS-030-02, Cleanup.
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
(dieser Workspace ist die Repowurzel)
Branch: `feat/einheitliche-triggerarchitektur`, HEAD vor diesem Review `b363346`
Interpreter: Python 3.12.10 (global), pytest 9.1.1

## Ergebnis

**OBS-030 GATE PASS – OBS-040 MAY PROCEED**

Geprüft wurde ausschließlich der tatsächliche Repositoryzustand: Produktcode,
`git diff`/`git status`, eigene Testläufe mit **beiden** Runnern, eigene
Fault-Injection- und Laufzeitproben sowie ein Vergleichslauf gegen einen aus
`b363346` frisch ausgepackten Baum. Die vorliegenden Abschluss-, Korrektur-
und Cleanup-Berichte wurden als Hinweis gelesen, aber an keiner Stelle als
Nachweis übernommen.

---

# A. Ursprüngliche Blocker – unabhängig nachgeprüft

## B-1 – Worker-Fehlerisolation → **GESCHLOSSEN**

### Code

`core/observability/worker.py`:

- `run()` klammert `self._iteration()` in `try/except Exception`
  (`worker.py:139-146`); `_record_loop_failure()` erhöht `worker_errors`
  ausschließlich über `LoggingInternalHealth.record_worker_error` →
  ratenbegrenztes `emergency()` (G-2/G-4).
- Auch `_open_store()` und der erste `_run_retention_if_due(force=True)`
  liegen in Guards (`worker.py:130-137`); der gesamte Rumpf hat ein
  `finally: self._finish()`.
- `_finish()` setzt `FAILED_WORKER` **vor** `_shutdown_flush()`
  (`worker.py:167-179`) und fängt jeden Fehler von `_shutdown_flush`,
  `store.close()` und `sink.close()`.
- `_prepare_record`: `dataclasses.replace(...)` liegt jetzt **innerhalb** des
  `try` (`worker.py:317`) — der im ersten Gate beanstandete Austrittspfad ist
  geschlossen; der Ersatzpfad ist zusätzlich abgesichert.
- `_drain_and_count_leftovers()` fängt auch einen defekten `drain` und fällt
  auf `qsize()` zurück.

### Eigene Fault-Injection (`probe_gate2_b1_worker.py`)

```text
P1  eine injizierte Ausnahme im Schleifenrumpf (drain wirft einmal)
    worker alive after the exception : True
    worker_errors                    : 1
    health.state                     : ok
    rows written after the exception : 3
    stderr                           : '[observability] worker_loop_failed: injected loop failure'
    contains 'Traceback'             : False

P2  4 aufeinanderfolgende Fehler, danach Erfolg
    worker alive = True | worker_errors = 4 | state = ok | submit() = True

P3  dauerhaft werfende Schleife
    worker alive                     : False
    health.state                     : failed_worker
    health.is_failed()               : True
    worker_errors                    : 6
    dropped_shutdown (Queue-Reste)   : 5
    submit() nach dem Ausfall        : [False, False, False, False, False]
    Observability-Threads uebrig     : []
    store.close()/sink.close()       : True / True
    stderr enthaelt 'Traceback'      : False
    stderr-Zeilen                    : [observability] worker_loop_failed: ...
                                       [observability] worker_drain_failed: ...
                                       [observability] shutdown_flush_incomplete: 5 records dropped at shutdown

P4  _prepare_record mit nicht redigierbarem raw
    Rueckgabe raw = {'_truncated': True, '_bytes': -1} | malformed = 1
    Nicht-Dataclass als Eingabe      : keine Ausnahme entkommt

P5  weitere Iterationsschritte
    qsize wirft         : alive=True  state=ok            worker_errors=0
    run_retention wirft : alive=True  state=ok            retention_errors=1
    store.open() wirft  : alive=True  state=failed_store  worker_errors=0

P6  stop() auf nie gestartetem Worker
    stop() = True | enqueued = 7 | dropped_shutdown = 7 | queue depth = 0
```

Damit ist jede Anforderung des Prüfauftrags belegt: kein stiller Tod, korrekt
reagierender `worker_errors`, ausschließlich der isolierte ratenbegrenzte
Fehlerpfad, **kein** ungefilterter `threading`-Traceback, `FAILED_WORKER` beim
endgültigen Ausfall, danach keine scheinbar erfolgreichen `True`-Submits mehr,
Queue-Reste gezählt.

### Ausdrücklich geprüft: die Schwelle `WORKER_FAILURE_THRESHOLD = 5`

**Ergebnis: normativ gedeckt, keine neue Semantik.** Begründung, nicht auf
Tests gestützt, sondern auf die Normtexte:

1. `ARCH §8.3` regelt für die Zeile „Worker-Ausnahme in der Schleife" nur
   **was geschieht, wenn** die Schleife abbricht („Bricht sie dennoch ab:
   …"), **nicht wann**. Die Abbruchbedingung ist nicht eingefroren.
2. Dieselbe Zeile liefert die Prämisse für ein Aufgeben ausdrücklich mit:
   *„Kein Neustartversuch — ein Worker, der zweimal stirbt, stirbt beim
   dritten Mal auch."* Der Freeze behandelt wiederholtes Scheitern selbst als
   dauerhaftes Scheitern.
3. Die **beobachtbare** Semantik nach dem Abbruch ist exakt die eingefrorene:
   `FAILED_WORKER` (Zustandsmenge `§8.3`, Enum `CONTRACTS §11.2`), kein
   Neustart, Ingress im `FAILED`-Zweig aus `ARCH §5`. Es entsteht **kein**
   neuer Zähler, kein neuer Zustand, kein Konfigfeld, keine DDL-Änderung und
   keine Vertragsform — also keine Erweiterung eines eingefrorenen Vertrags.
4. Der Wert ist eine modulinterne Konstante. Für den Normalfall bleibt die
   Regel „Schleife läuft weiter" nachweislich unangetastet: ein Einzelfehler
   und auch vier aufeinanderfolgende Fehler beenden den Worker nicht (P1/P2),
   ein erfolgreicher Durchlauf setzt den Zähler zurück (`worker.py:145-146`).
5. Die Gegenvariante („nie aufgeben") führte bei dauerhaft defekter Schleife
   zu einem endlos fehlschlagenden Worker bei Health `OK` — genau die blinde
   Stelle, die `ARCH §7.3`/`§8` verhindern sollen.

**Nicht-blockierende Beobachtung N-2** (siehe unten): die beiden Guards vor
der Schleife teilen sich den Zähler `_consecutive_loop_failures`, ohne dass
dazwischen zurückgesetzt wird. Es bleiben fünf echte unerwartete Ausnahmen,
aber die Kopplung ist unbeabsichtigt und sollte in OBS-060 sauber getrennt
werden.

## B-2 – Evidence-Konsistenz → **GESCHLOSSEN**

- Die RUN-02-Evidence stimmt mit dem Code überein. Alle nachprüfbaren Zahlen
  wurden eigenständig reproduziert (siehe Abschnitt G): 6/23/18 neue Tests,
  129 OBS-030-Tests unter `pytest` **und** `unittest`, 331 Tests für
  OBS-010+020+030, Vollsuite 843 passed / 1 vorbestehender Fehlschlag,
  `unittest` 844 Ran / 1 Error.
- Die im ersten Gate beanstandete Zeile ist in
  `RUN-02/CONTRACT_COVERAGE.md` korrigiert **und** trifft jetzt zu
  (`worker_errors` hat reale Aufrufer, Health-Spalte `FAILED_WORKER`).
- Kein Gate-FAIL-Befund ist gelöscht oder verschleiert:
  `GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md` ist vollständig
  unverändert vorhanden, inklusive aller Befunde B-1/B-2/B-3 und W-1..W-7.
- Frühere falsche Aussagen sind eindeutig als historisch widerlegt
  gekennzeichnet — Details unter E.

## B-3 – `CONTRACTS §4.3 P-8` → **GESCHLOSSEN**

Geprüft gegen den **real aufgelösten** Benutzerprofilpfad dieses Rechners
(`USERPROFILE`/`HOME`/`Path.home()` = `C:\Users\marco`,
`DEFAULT_LOCAL_APP_DIR` = `C:\Users\marco\AppData\Local\RealtimeSTT Client`),
für `db_path` **und** `file_sink_dir`, an der Config-Grenze **und** im
produktiven Managerpfad (`probe_gate2_b3_paths.py`).

| Fall | Config-`validate()` | Managerpfad |
|---|---|---|
| gültiger Profilpfad, Profilwurzel, `/`-Separatoren, gemischte Groß-/Kleinschreibung, doppelte Separatoren, `.`-Segment, `~` | akzeptiert | übernommen |
| absoluter Fremdpfad (`C:\ProgramData\…`, `C:\Windows\Temp\…`) | `ValueError` | Standardort, eine ratenbegrenzte stderr-Zeile |
| `..`-Escape (auch mehrstufig aus `AppData` heraus) | `ValueError` | Standardort |
| Fremdprofil (`C:\Users\anderer-nutzer\…`) und Präfixfalle (`C:\Users\marco-evil\…`) | `ValueError` | Standardort |
| Windows-Laufwerkspfad (`D:\…`, `C:\…`-Wurzel) | `ValueError` | Standardort |
| UNC (`\\fileserver\share\…`, `\\127.0.0.1\C$\…`) | `ValueError` | Standardort |
| relativ, laufwerksrelativ (`C:obs\…`), leer, nur Leerzeichen | `ValueError` | Standardort |

Ende-zu-Ende mit feindlicher Konfiguration (`db_path` nach `C:\ProgramData\…`,
`file_sink_dir` als UNC):

```text
store path             : C:\Users\marco\AppData\Local\RealtimeSTT Client\observability.sqlite3
sink dir               : C:\Users\marco\AppData\Local\RealtimeSTT Client\logs\observability
inside profile (store) : True
Verzeichnis C:\ProgramData\obs-gate-review angelegt? False
AppConfig.validate()   : ValueError -> logging.observability.db_path must resolve
                         to a path inside the user profile (CONTRACTS §4.3 P-8)
```

P-9 zusätzlich belegt: `['obs.sqlite3', 'obs.sqlite3-shm', 'obs.sqlite3-wal']`
entstehen im selben Verzeichnis.

Die zweite Prüfung im Manager ist notwendig und nicht redundant:
`app.py::main()` baut den Manager aus `AppConfig.load()` **ohne**
`AppConfig.validate()`.

---

# B. W-1 bis W-7 – unabhängig nachgeprüft

## W-1 – Store-/Sink-Isolation → **korrekt gelöst**

**Normative Klärung (nicht aus RUN-02 übernommen).** Der Freeze verlangt
**nicht** ausdrücklich, dass ein intakter JSONL-Sink bei defektem Store
weiterarbeitet; er verbietet die Entkopplung aber ebenso wenig, und
`CONTRACTS §11.1` legt nur eine **Reihenfolge** fest („write_batch ZUERST,
Sink DANACH"), keine Bedingung. `ARCH §8.3` zählt die Reaktionen auf einen
Store-Fehler abschließend auf; ein stilles Mit-Abschalten des Sinks steht dort
nicht. `O-05` führt Store und Sink als getrennte Fehlerdomänen. Die
Entkopplung ist damit die vertragstreue Ausgestaltung.

Nachgeprüft am Code (`worker.py:294`, `_write_sink` unbedingt) und zur
Laufzeit:

```text
Store degradiert (< 5 Fehlschlaege) : sink records written = 20/20
Reihenfolge im Worker              : ['store', 'sink']
Sink kaputt                        : sink write attempts = 1 (danach deaktiviert),
                                     sink_errors = 1, state = degraded_sink,
                                     Store schreibt weiter: 50/50 Zeilen,
                                     genau eine stderr-Zeile
```

**Benannte Grenze — ausdrücklich als normkonform bestätigt.** Bei
`FAILED_STORE` weist der **Ingress** selbst ab, der Sink erhält dann nichts
mehr (eigene Probe: 5 von 20 Submits angenommen). Das ist **kein** Defekt:
`ARCH §5` friert die Ingressreihenfolge wörtlich ein —

```text
ObservabilityIngress
  - Health == FAILED?        -> return False
  - enabled / Level-Filter   -> return False
  - Wasserstandsregel (7.2)  -> return False
  - queue.put_nowait         -> bei Full: zaehlen, False
```

`ingress.py::submit` ist exakt diese Reihenfolge und gegenüber `HEAD`
unverändert.

## W-2 – `logging.retention_pressure` → **korrekt, Feld für Feld geprüft**

Eigene Laufzeitprobe, Record direkt aus der SQLite gelesen:

```text
type          : logging.retention_pressure
channel       : performance        (CONTRACTS §12.4 "Zahlen – Channel performance")
level         : WARNING            (§5.6 "Health-Warnsignal")
component     : observability.worker
producer_kind : client   producer_id : voice-stt-client
instance_id   : <ingress.instance_id>   scope : instance
replayed      : 0        message : NULL
details_json  : {"db_bytes": 45056, "max_db_bytes": 1}
```

Erzeugt vom **Worker**, direkt geschrieben unter Umgehung von Handler und
Queue (G-6), `is_internal=True` (also HIGH, `CONTRACTS §1.5`). Flanke geprüft:
bei 2600 Records und mehreren Retentionsläufen entsteht **genau ein** Record;
ohne Überschreitung keiner. Kein Eingriff in `max_entries`, kein `VACUUM`,
kein `auto_vacuum`, kein `incremental_vacuum` (FD-D8) — im Quelltext des
Stores existiert keine einzige ausgeführte `VACUUM`-Anweisung.

## W-3 – Lücke bei nicht zugeordneten Verwürfen → **dokumentierte Lücke, kein Blocker**

Reproduziert: bei ausgesetztem/degradiertem Store gilt
`enqueued = 5`, `written = 0`, alle `dropped_*` = 0 — die arithmetische
Identität bricht während einer Störung auf.

Bewertung: `ARCH §7.3` ist mit „Zähler – **eingefroren**" abschließend und
enthält für diesen Fall keinen Zähler; `CONTRACTS §11.2` friert
`LoggingHealthSnapshot` entsprechend ein. **Es wird hier weder ein neuer
Zähler verlangt noch akzeptiert.** Sichtbar bleibt der Fall über
`store_errors`, den Health-State und die ratenbegrenzte stderr-Zeile; seit
W-1 erreichen diese Records zusätzlich den JSONL-Sink, sofern konfiguriert.
Die Lücke ist damit benannt, nicht repariert — die richtige Behandlung nach
`AGENTS.md` („Fund → dokumentieren → Blocker? nein: späteres WP").

## W-4 – leerer Testschreibvorgang → **korrekt**

`SQLiteLogStore.probe_write()` führt `BEGIN IMMEDIATE` + `COMMIT` ohne Zeilen
aus. Eigene Probe:

```text
nach >=5 Fehlschlaegen pausiert   : True
probe_write()-Aufrufe             : 1
write_batch-Aufrufe beim Resume   : 0     <- der Batch kostet nichts mehr
Ergebnis des Resume-Aufrufs       : (0, 0, False), Pause um 60 s verlaengert
echter Store: probe_write()       : True, Zeilen danach = 0
```

Entspricht `ARCH §8.3` wörtlich („danach mit einem leeren Testschreibvorgang
prüfen").

## W-5 – `DISABLED` → **korrekt**

`enabled=False` → `state = disabled`, Ingress = `NullIngress`, `stop()`/
`clear_history()` ohne Worker unkritisch. `store_enabled=False` bleibt `OK` —
richtig, denn Queue, Worker und Sink laufen dann weiter (`_NullStore`); die
Observability ist nicht abgeschaltet. `DISABLED` ist kein Failure-State.

## W-6 – blockierendes `clear_history()` → **zu Recht nach OBS-050 verschoben**

In OBS-030 existiert kein Qt-Aufrufer; `ui/**` ist im gesamten Diff
unverändert. Das Ausführen auf dem Workerthread ist durch `CONTRACTS §5.4`
(alleiniger Eigentümer der Schreibverbindung) sogar geboten. Die Auflage für
OBS-050 (`O-03`: nicht aus dem Qt-Mainthread) ist dokumentiert.

## W-7 – kleinere Abweichungen → **alle drei korrekt**

```text
PRAGMA-Reihenfolge in open()      : ['journal_mode', 'synchronous', 'busy_timeout', 'foreign_keys']
erwartet (CONTRACTS §5.2)         : identisch
_records_since_retention nach fehlgeschlagenem Batch : 0   (zaehlt GESCHRIEBENE)
_records_since_retention nach gutem Batch            : 10
stop() auf nie gestartetem Worker : dropped_shutdown = 7 von 7 eingereihten
```

---

# C. ARCH §8.3 „nur verwerfen und zählen" – Entscheidung

## Befund

Nach `FAILED_WORKER` weist `ObservabilityIngress.submit()` ab, ohne dass ein
Zähler bewegt wird. Eigene Messung, alle Zählerstände vorher/nachher bei 10
abgewiesenen Submits: **keiner** ändert sich.

## Entscheidung: **Variante 1**

Der bestehende, eingefrorene Vertrag ist so auszulegen, dass die aktuelle
Implementierung **ohne neuen Zähler vollständig normkonform** ist. Die
Auslegung stützt sich ausschließlich auf bestehende Normtexte:

**1. `ARCH §5` friert die Ingressreihenfolge wörtlich ein** — und markiert
selbst, wo gezählt wird:

```text
- Health == FAILED?        -> return False
- enabled / Level-Filter   -> return False
- Wasserstandsregel (7.2)  -> return False
- queue.put_nowait         -> bei Full: zaehlen, False
```

Der `FAILED`-Zweig ist im eingefrorenen Komponentenbild ein reines
`return False`; das Wort „zaehlen" steht ausschließlich am Queue-voll-Schritt.
Der Code ist genau diese Reihenfolge.

**2. `§8.3` definiert nirgends Zähler; es referenziert sie.** Wo die Tabelle
einen Zähler meint, nennt sie ihn beim Namen — in **derselben Zeile**
(`worker_errors++`), in der Shutdown-Zeile (`dropped_shutdown`), in der
Normalizer-Zeile (`malformed++`). Die Wendung „nur verwerfen und zählen"
steht in Anführungszeichen und ist ein **Modusname**; sie nennt keinen Zähler
und kann deshalb keinen gegen die in `§7.3` ausdrücklich als *eingefroren*
überschriebene, abschließende Liste erzeugen.

**3. `ARCH §8.5 GRENZE 3` behandelt genau diesen Zeitraum abschließend:**
*„Fällt der Worker aus, gehen ab diesem Zeitpunkt alle Records verloren. Der
bestehende RotatingFileHandler bleibt davon UNBERÜHRT und ist genau deshalb
die Rückfallebene."* Die vier Grenzen sind laut Vorspann *„Eigenschaften der
Architektur, keine Mängel. Sie werden benannt, damit niemand sie später für
einen Defekt hält."* Ein Freeze, der den Verlust nach dem Workerausfall als
unquantifizierten, ausdrücklich akzeptierten Totalverlust benennt und auf die
Rückfallebene verweist, verlangt für denselben Zeitraum keine Zählung je
Record.

**4. Was `§8.3` in dieser Zeile tatsächlich an Zählung nennt, geschieht:**
`worker_errors++` (gemessen: 6), `FAILED_WORKER`, kein Neustart; und alles,
was zum Zeitpunkt des Ausfalls bereits ein eingereihter Record war, wird als
`dropped_shutdown` gezählt (gemessen: 5) mit genau einer ratenbegrenzten
stderr-Zeile.

**5. `CONTRACTS §6`** definiert für den abgewiesenen Submit den vertraglichen
Rückkanal: `submit(...) -> bool`, *„False = nicht angenommen (deaktiviert,
gefiltert, verworfen)"*. Der Ingress liefert ihn.

Damit liegt **kein** Contract-Widerspruch und **kein** DECISION-REQUIRED-Bedarf
für die Abnahme von OBS-030 vor. Es wurde folgerichtig **kein** Zähler
implementiert, **keine** Freeze-Datei erweitert und **keine**
Architekturentscheidung durch den Reviewer getroffen.

**Ergänzender, nicht gate-relevanter Hinweis an die Entscheidungsinstanz.**
Wünscht die Instanz dennoch die Lesart A (eigener Zähler je abgewiesenem
Submit), so ist das eine autorisierte, additive Erweiterung von `ARCH §7.3`
**und** `CONTRACTS §11.2`, die sinnvoll zusammen mit W-3 und dem
Härtungspaket OBS-060 entschieden wird. Sie ist **keine** Voraussetzung für
die Abnahme von OBS-030 und blockiert OBS-040 nicht.

---

# D. Freeze-Integrität

```text
$ git diff --stat HEAD -- .../LOGGING_OBSERVABILITY/00_NORMATIV/
(leer)
```

Alle vier Dateien in `00_NORMATIV/` sind **byte-identisch** zu `b363346` —
dem Stand vor RUN-OBS-030-01 und damit auch vor RUN-OBS-030-02. Sie stehen in
keinem `git status`-Eintrag.

`DR-OBS-030-01` kommt in `00_NORMATIV/` **nirgends** vor (repoweiter
`grep`); alle verbleibenden Treffer liegen ausschließlich in Run-,
Evidence- und Steuerungsunterlagen und beschreiben die Rücknahme. Offener
Entscheidungsbedarf ist damit dokumentiert, aber nirgends als beschlossene
Norm ausgegeben.

Ebenfalls geprüft: `LoggingHealthSnapshot` hat wieder exakt die 16 Felder aus
`CONTRACTS §11.2` in derselben Reihenfolge, `LoggingHealthState` exakt die
sieben eingefrorenen Werte, `LoggingObservabilityConfig` exakt die 14
Schlüssel aus `CONTRACTS §10.1`, die DDL exakt `§5.2` (eine UNIQUE- und fünf
weitere Indizes), und `core/observability/ingress.py` ist gegenüber `HEAD`
unverändert. Kein `dropped_failed` mehr im gesamten Repository.

---

# E. Historische RUN-01-Evidence

Drei Dateien tragen einen Nachtrag:
`40_EVIDENCE/OBS-030/RUN-01_…/CONTRACT_COVERAGE.md` (ab Zeile 99),
`40_EVIDENCE/OBS-030/RUN-01_…/TEST_RESULTS.md` (ab Zeile 126),
`30_AUSFUEHRUNG/runs/RUN-OBS-030-01_…/RESULT.md` (ab Zeile 98).

| Prüfung | Ergebnis |
|---|---|
| ursprünglicher Text unverändert? | ja — die vom Gate beanstandete Zeile steht wörtlich weiterhin in `CONTRACT_COVERAGE.md:43`, `RESULT.md:5` meldet weiterhin `OBS-030 IMPLEMENTED – READY FOR REVIEW`, `TEST_RESULTS.md` weiterhin „796 passed" |
| Nachträge abgesetzt und datiert? | ja — jeweils `---` + Überschrift `## KORREKTURVERMERK (RUN-02, 2026-08-17)` am Dateiende |
| Aussage gelöscht oder ersetzt? | nein — jeder Nachtrag zitiert die falsche Aussage und benennt, warum sie falsch war |
| Gate-FAIL-Historie erhalten? | ja — `GATE-REVIEW-01_…/GATE_REVIEW.md` vollständig unverändert |
| Rekonstruierbarkeit? | ausreichend — RUN-01 → Gate-FAIL → RUN-02 → Cleanup → dieser Re-Review sind lückenlos nachvollziehbar |

Einordnung: **transparenter Korrekturvermerk**, keine Manipulation und keine
Verschleierung. Kein materielles Evidence-Problem, kein Gate-Blocker.

Rein organisatorischer Verbesserungspunkt (kein Befund): für solche
Nachträge existiert keine normative Evidence-Regel; ein kurzer Absatz in
`ARBEITSDATEIEN/AGENTS.md` wäre für künftige Läufe hilfreich.

---

# F. Checkliste und Steuerungsdateien

| Prüfung | Ergebnis |
|---|---|
| `LOGGING_V1_CHECKLISTE.md` vollständig/konsistent | ja |
| frühere Häkchen erhalten | ja — `git diff` zeigt als einzige Statusänderung `OBS-030 … Implementierung` von `[ ]` auf `[x]` |
| OBS-030 Gate vorzeitig abgehakt? | nein — stand bis zu diesem Review auf `[ ]` |
| CURRENT_STATE korrekt | ja — Gate-FAIL-Eintrag steht weiterhin da, entfernt wurden ausschließlich zwei „Nächster Schritt"-Zeilen |
| LOG_VERLAUF append-only | ja — `git diff --numstat`: **353 Zeilen hinzugefügt, 0 entfernt** |
| Zweitfassung als kanonischer Stand? | nein — die Datei in `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` ist eine unbenutzte Vorlage (alle Punkte `[ ]`, „Läuft: OBS-010") und wurde nicht angefasst; kanonisch bleibt der versionierte Pfad |

---

# G. Eigene Tests

Alle Läufe in diesem Workspace, globales Python 3.12.10.

```text
$ python -m pytest -q tests/test_obs030_*.py            129 passed, 10 subtests
$ python -m unittest discover -s tests -p "test_obs030_*.py"
                                                        Ran 129 tests   OK
$ python -m pytest -q -k "obs010 or obs020 or obs030"   331 passed, 112 subtests
$ python -m pytest -q tests/                            1 failed, 843 passed, 351 subtests
$ python -m unittest discover -s tests -p "test_*.py"   Ran 844, FAILED (errors=1)
$ git diff --check                                      leer, Exit 0
```

## Nachweis, dass der eine Fehlschlag vorbestehend und diffunabhängig ist

Nicht aus dem Bericht übernommen, sondern gemessen: aus `b363346` wurde per
`git archive` ein sauberer Baum ausgepackt und dort dieselbe Suite gefahren.

```text
Baum aus b363346 (ohne jede OBS-030-Änderung):
  tests/test_ap06_followup.py     1 failed, 23 passed
  tests/ (Vollsuite)              1 failed, 714 passed, 337 subtests

Arbeitsbaum (OBS-030-Endstand):
  tests/ (Vollsuite)              1 failed, 843 passed, 351 subtests

Differenz: 843 - 714 = 129  == genau die 129 neuen OBS-030-Tests.
Fehlschlag identisch: tests/test_ap06_followup.py::TestSettingsDialog::
  test_failed_runtime_submit_rolls_hotkeys_and_file_back
  -> ModuleNotFoundError: No module named 'lefx.interfaces'
```

Die im ersten Gate beobachtete Flakiness in `tests/test_core_bridge.py` wurde
sechsmal isoliert nachgefahren: jeweils `7 passed`, in keinem der Vollläufe
aufgetreten. Kein OBS-030-Bezug.

## Eigene Laufzeitproben (zusätzlich zu den Tests)

```text
Worker-Fault-Injection      probe_gate2_b1_worker.py    (P1..P6, siehe A/B-1)
Store-/Sink-Isolation       probe_gate2_w_findings.py
Store-Ausfall               dauerhaft werfender Store -> DEGRADED_STORE -> FAILED_STORE,
                            Anwendung/Worker unbeeinflusst
Sink-Ausfall                1 Schreibversuch, danach deaktiviert, sink_errors=1,
                            DEGRADED_SINK, Store schreibt 50/50 weiter, EINE stderr-Zeile
Backpressure/Recovery       Queue 20: LOW 8/40, HIGH 12/40 akzeptiert,
                            dropped_watermark=32, dropped_queue_full=28,
                            enqueued+watermark+full = 80 (exakt),
                            nach Erholung genau EIN logging.records_dropped
                            {"dropped_watermark": 185, "dropped_queue_full": 0}
HIGH-Sonderregel            replayed+type -> low | nicht replayed+type -> high |
                            is_internal -> high   (CONTRACTS §1.5, nicht verallgemeinert)
Shutdown mit Queue-Resten   3000 Records: enqueued=written=3000, keine Reste,
                            stop(0.2)=True, keine Observability-Threads uebrig
E2E logger.info -> SQLite   1 Zeile, channel=system, component=core.controller,
                            details={"logger":…,"func":…,"line":…,"thread":…}
SQLite-Dedupe               (producer_id,event_id): 2 -> reopen -> +1 inserted,
                            1 deduplicated, 3 Zeilen, replayed-Flag bleibt 0
                            (erste Fassung gewinnt); ohne event_id keine Dedupe
Persistenz ueber Neustart   Daten ueberleben close()/reopen
Migration                   user_version=99 -> ok/degraded, Nur-Lesen, nichts geloescht,
                            Dateigroesse unveraendert; fehlgeschlagene Migration ->
                            Rollback, keine Tabellen, user_version=0, Datei erhalten
N-05                        Fremdthread -> sqlite3.ProgrammingError
Retention                   Alter 50 geloescht, Anzahl 30 geloescht, max_entries >
                            Zeilenzahl -> 0 (NULL-gesichert), kein VACUUM
Kein Ringbuffer             kein deque/ring_buffer/live_buffer; genau EIN queue.Queue(
                            in core/observability/ (ingress.py)
P-8 / P-9                   probe_gate2_b3_paths.py (siehe B-3)
```

## Scope-Prüfung des Diffs

Geänderte **verfolgte** Dateien — vollständig und abschließend:

```text
 M app.py                          (+27/-8)   AR-5/AR-6-Verdrahtung
 M core/config.py                  (+182)     §10.1-Schema + P-8-Prüfung
 M core/observability/__init__.py  (+8)       Re-Exporte
 M core/observability/health.py    (+21/-2)   Worker-Zähler, kein Snapshot-Feld
 M ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md
 M ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md            (append-only)
 M .../30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md
```

Neue Produkt-/Testdateien: `core/observability/{manager,worker}.py`,
`core/observability/storage/sqlite.py`,
`core/observability/sinks/jsonl_file.py`, zehn `tests/test_obs030_*.py`.

Unverändert und stichprobenhaft bestätigt: `ui/**`, `core/controller.py`,
`core/session_coordinator.py`, `core/event_stream.py`, `core/stt_session.py`,
`core/logging_setup.py`, `core/led_controller.py`,
`core/observability/{ingress,normalizer,redaction,models}.py`,
`core/observability/adapters/python_logging.py`,
`core/observability/{query,sinks,storage}/base.py`. **Kein** bestehender Test
geändert (alle `test_obs030_*.py` sind neu). **Kein** OBS-040/OBS-050-Vorgriff:
kein `adapters/server_live.py`, kein `query/local.py`, kein `ui/logs/**`, kein
Settings-Eintrag, kein Fan-out-Hook. Server- und LED-Workspace liegen in
eigenen Repositories und sind nicht berührt.

---

# H. Nicht-blockierende Beobachtungen (für OBS-040/OBS-050/OBS-060)

**N-1 `logging.record_rejected` existiert nirgends im Code.**
`ARCH §8.3` (Zeile „Normalizer-Ausnahme") und `CONTRACTS §12.4` nennen ihn;
im Repository gibt es keinen einzigen Treffer. Alle betroffenen Pfade
(`ingress.event`, `ingress.observe_server_result`,
`adapters/python_logging.py`, `worker._prepare_record`) erhöhen korrekt
`malformed`, erzeugen aber keinen Ersatzrecord.
**Kein OBS-030-Blocker:** Auslöser ist der Normalizer-/Handlerpfad aus
OBS-010/OBS-020 (dort gate-geprüft, und der Normalizer wirft konstruktiv nie,
sondern liefert `None`); im Worker wird der Record bei einem
Serialisierungsfehler nicht verworfen, sondern mit
`{"_truncated": true, "_bytes": -1}` weitergeschrieben. Weder `WP-OBS-030`
noch der OBS-030-Implementierungsauftrag führen `§12` im Scope; die übrigen
`§12.4`-Einträge (`client.audio.stream_stats`, `client.queue.state`) sind
unstrittig OBS-040. **Empfehlung:** in OBS-040 bzw. OBS-060 nachziehen.
Ergänzend: die Zeile „`logging.record_rejected` | Ingress/Normalizer-Pfad
(OBS-020) | unverändert" in `RUN-02/CONTRACT_COVERAGE.md:60` legt eine
Umsetzung nahe, die es nicht gibt; Zeile 23 derselben Datei ist mit
„Normalizer wirft nie (OBS-010)" präziser.

**N-2 `_consecutive_loop_failures` wird von den beiden Guards vor der
Schleife mitgezählt** (`worker.py:130-137`), ohne Reset vor dem ersten
Schleifendurchlauf. Es bleiben fünf echte unerwartete Ausnahmen bis
`FAILED_WORKER`, aber die Kopplung ist unbeabsichtigt. Für OBS-060.

**N-3 `app.py::main()`**: `ObservabilityManager(...)`, `.start()` und
`setup_logging(...)` liegen **vor** dem `try`. `ARCH §6.2` spricht von einem
`try/finally` „um den GESAMTEN Ablauf". Wirkung ist minimal (der Worker ist
ein Daemon-Thread, der Prozess endet ohnehin), aber ein Fehler in
`setup_logging` erreicht `observability.stop(2.0)` nicht. Für OBS-060.

**N-4 `ARCH §6.2`**: *„DesktopApplication bekommt den Manager übergeben und
stoppt ihn nicht."* Übergeben wird er heute nicht — `run_gui(config, argv)`
ist unverändert. Erst OBS-050 braucht ihn (Statuszeile im LogWindow,
„Diagnosehistorie löschen"). Als Readiness-Punkt für OBS-050 vorgemerkt.

**N-5 Verzeichnisschreibweise `prompts/` vs. `Prompts/`.** Der versionierte
Pfad lautet `30_AUSFUEHRUNG/prompts/`; im Arbeitsbaum heißt das Verzeichnis
`Prompts/`. Auf case-insensitiven Dateisystemen ist das dasselbe Verzeichnis.
Neue Prompts wurden in diesem Commit bewusst unter dem bestehenden
kleingeschriebenen Pfad aufgenommen, damit im Repository keine zweite
Verzeichnisschreibweise entsteht.

---

# I. Readiness-Check OBS-040 (nächstes vorbereitetes Work Package)

Voraussetzungen laut `01_WORKPACKAGE_INDEX.md` (`depends_on: OBS-020, OBS-030`)
gegen den realen Endzustand:

| Voraussetzung | Zustand |
|---|---|
| Ingress mit `observe_server_result` | vorhanden (`ingress.py:128`), unverändert |
| Persistenz-/Dedupe-Pfad für Serverevents | vorhanden und nachgewiesen (partieller UNIQUE-Index, `deduplicated`) |
| `raw`-Redaction im Worker (`ARCH §8.2`) | vorhanden (`_prepare_record`), 64-KiB-Grenze wirksam |
| Prioritätsregel inkl. `replayed is False` | vorhanden und geprüft |
| Kompositionswurzel + Lebenszyklus | vorhanden (`ObservabilityManager`, `app.py`) |
| Fan-out-Hook in `core/session_coordinator.py` | **noch nicht vorhanden** — genau der Gegenstand von OBS-040 |

Keine Blocker. Die §8.3-Zählfrage und W-3 berühren OBS-040 nicht.

---

# Abschluss

```text
OBS-030 GATE PASS – OBS-040 MAY PROCEED
```
