# OBS-060 – V1_FAILURE_INJECTION

Run: `RUN-OBS-060-01_2026-08-18`
Skript: `probe_obs060_failure_injection.py` — vollständige Ausgabe in
`output/probe_obs060_failure_injection.out.txt` (exit 0)
Reproduktion **vor** der Korrektur: `failure_injection_BEFORE_FIX.txt`

Jeder Fall benutzt die **echte** Komponente und setzt den Fehler an ihrer
echten Grenze. Die Frage ist immer dieselbe: Bleibt der Fehler in der
Logging-Fehlerdomäne (O-05), und ist er danach über Health und Zähler
**sichtbar**?

---

## Übersicht

| # | Fehlerfall | Norm | Health danach | Ergebnis |
|---|---|---|---|---|
| F-1 | SQLite read-only | ARCH §8.3 | `FAILED_STORE`, `store_errors=5` | PASS |
| F-2 | SQLite locked | ARCH §8.3 | Ausnahme gehört dem Worker, nächster Schreibvorgang gelingt | PASS |
| F-3 | DB-Pfad ungültig | ARCH §8.3 | `FAILED_STORE`, Worker lebt | PASS |
| F-4 | Datei-Sink defekt | ARCH §8.3, §11.1 | `DEGRADED_SINK`, Store schreibt weiter | PASS |
| F-5 | Queue voll / Wasserstand | ARCH §7.1/§7.2 | gezählt, kein Log, kein Wurf | PASS |
| F-6 | Worker-Ausnahme | ARCH §8.3 | einzeln überlebt, fünf in Folge ⇒ `FAILED_WORKER` ohne Neustart | PASS |
| F-7 | malformed Event | ARCH §8.3, CONTRACTS §3 | `OK` + `malformed++` | PASS (1 offener Punkt) |
| F-8 | UI-Abfragefehler | CONTRACTS §8.1 | Anzeigezustand `ERROR`, kein Wurf | PASS |
| F-9 | werfende Aggregatquelle | ARCH §8.6 | übersprungen, `malformed++`, Worker lebt | PASS |
| F-10 | Store-Erholung nach Aussetzung | ARCH §8.3, CONTRACTS §11.2 | `FAILED_STORE` → Probe → `OK` + `logging.recovered` | **PASS nach Korrektur B-1** |

---

## F-1 SQLite read-only

Ein Store, dessen `write_batch` durchgängig
`sqlite3.OperationalError("attempt to write a readonly database")` wirft.

```text
[PASS] F-1.1 FAILED_STORE erreicht                       (LoggingHealthState.FAILED_STORE)
[PASS] F-1.2 gezählt, nicht still                        (store_errors=5)
[PASS] F-1.3 Producer weder blockiert noch getroffen     (enqueued=30)
[PASS] F-1.4 Workerthread lebt weiter
[PASS] F-1.5 danach lehnt der Ingress ab, statt Speicherung zu versprechen
```

F-1.5 ist die Stelle, an der ARCH §8.3 „nur verwerfen und zählen" messbar wird:
`submit()` liefert `False`, sobald Health `FAILED` ist — kein Producer bekommt
je ein „angenommen" für einen Record, den niemand mehr abholt.

## F-2 SQLite locked

Eine fremde Verbindung hält `BEGIN EXCLUSIVE`. Der Schreibvorgang scheitert als
`OperationalError` — also als Ausnahme, deren Wiederholungs- und
Circuit-Breaker-Politik nach ARCH §8.3 dem **Worker** gehört, nicht dem Store.
Nach dem `ROLLBACK` der fremden Verbindung gelingt der **nächste** Batch sofort
(`inserted=1`): die Sperre hinterlässt keinen Folgeschaden.

## F-3 DB-Pfad ungültig

Ein **Verzeichnis** an der Stelle der Datenbankdatei. Das Öffnen scheitert, und
zwar als Health-Zustand statt als Absturz; der Worker überlebt das gescheiterte
Öffnen, und ein Producer, der danach ein Event erzeugt, bekommt keine Ausnahme.
Die Datei wird — wie ARCH §8.3 verlangt — **nicht** gelöscht oder umbenannt.

## F-4 Datei-Sink defekt

Ein Sink, dessen `write_batch` immer `OSError` wirft.

```text
[PASS] F-4.1 der defekte Sink stoppt den Store nicht      (rows=30)
[PASS] F-4.2 der Sinkfehler wird gezählt                  (sink_errors=1)
[PASS] F-4.3 der Sink wird nach EINEM Fehler abgeschaltet (sink calls=1)
[PASS] F-4.4 Health zeigt DEGRADED_SINK, nie einen Storefehler
```

F-4.3 belegt die Ordnung aus CONTRACTS §11.1 („write_batch ZUERST, Sink
DANACH"): der Sink wird genau einmal versucht und dann dauerhaft deaktiviert,
statt pro Batch erneut zu scheitern.

## F-5 Queue voll und Wasserstand

Bei `queue_size=20` und ohne Worker:

```text
[PASS] F-5.1 LOW wird am Wasserstand verworfen, nicht erst am Rand
[PASS] F-5.2 der Wasserstand stoppt LOW bei 75 % (15 von 20)
[PASS] F-5.3 ein HIGH-Record kommt weiterhin durch
[PASS] F-5.4 am Rand wird auch HIGH als queue_full verworfen und gezählt
[PASS] F-5.5 submit hat über die gesamte Überlast nie geworfen
[PASS] F-5.6 die Zähler gehen auf (enqueued=20)
```

Beim ersten Lauf schlugen F-5.1/F-5.2 fehl — **ein Fehler der Probe, nicht des
Produkts**: die Testrecords hatten Level `DEBUG` und wurden schon vom
Ingress-Level `INFO` gefiltert, bevor die Wasserstandsregel überhaupt greifen
konnte. Mit `INFO`-Records greift die Regel exakt wie eingefroren.

## F-6 Worker-Ausnahme

Zwei Läufe. Erst drei aufeinanderfolgende Fehlschläge in `drain()`, dann
dauerhafte:

```text
[PASS] F-6.1 drei Fehlschläge in Folge werden überlebt
[PASS] F-6.2 sie werden als worker_errors gezählt          (worker_errors=3)
[PASS] F-6.3 unterhalb der Schwelle kein FAILED_WORKER
[PASS] F-6.4 dauerhafter Fehler endet in FAILED_WORKER, kein Neustartversuch
[PASS] F-6.5 die Schleife hat wirklich aufgegeben (Thread beendet)
[PASS] F-6.6 danach verwirft und zählt der Ingress nur noch
```

## F-7 malformed Event

```text
[PASS] F-7.1 ein Detailwert mit werfendem __str__ entkommt dem Ingress nicht
[PASS] F-7.2 ein Nicht-Mapping als details entkommt ebenfalls nicht
[PASS] F-7.3 die Ablehnung wird als malformed gezählt      (malformed=1)
[OPEN] F-7.4 kein Ersatzrecord logging.record_rejected für eine Ausnahme,
             die der Normalizer selbst verschluckt hat     → offener Punkt O-1
[PASS] F-7.5 der Ersatzrecord trägt Komponente und Ausnahmetyp, keine Originaldaten
[PASS] F-7.6 er ist HIGH und überlebt damit die Überlast, die er erklärt
[PASS] F-7.7 Health bleibt OK
```

F-7.3 **war vor diesem Lauf rot** (`malformed=0`) — das ist der Befund **B-2**,
siehe `V1_OPEN_POINTS.md`. F-7.4 bleibt als benannter offener Punkt **O-1**
stehen und wird ausdrücklich **nicht** repariert.

## F-8 UI-Abfragefehler

Ein Provider, dessen `status()`, `query()` und `fetch_raw()` alle werfen, dazu
eine korrupte Datenbankdatei und ein ungültiger Cursor. Alle sieben Prüfungen
grün: ein Providerdefekt ist nach CONTRACTS §8.1 ein **Anzeigezustand**, kein
Programmfehler. Auch ein unbekannter `provider_id` ist `UNAVAILABLE` statt einer
Ausnahme.

## F-9 werfende Aggregatquelle

Eine registrierte Zählerquelle, die bei jedem Lesen wirft, wird übersprungen und
als `malformed` gezählt; der Worker schreibt normale Records unverändert weiter.
Ein defekter Zählerleser kann die Schleife nicht mitnehmen.

## F-10 Store-Erholung — der Befund B-1

**Vorher (reproduziert, `failure_injection_BEFORE_FIX.txt`):**

```text
[PASS] F-10.1 fünf Schreibfehler in Folge setzen den Store aus
[FAIL] F-10.2 nach der Pause wird der Store geprüft und erholt sich  (FAILED_STORE)
[FAIL] F-10.3 die Erholung benutzte eine Probe, keinen Batch         (probe_calls=0)
[FAIL] F-10.4 Records fließen nach der Erholung wieder               (rows=0)
[FAIL] F-10.5 ein logging.recovered dokumentiert die Erholung        (0 Zeilen)
```

Die gezielte Einzelreproduktion (`probe_obs060_b1_reproduction.py`) zeigt es
noch deutlicher: nach `FAILED_STORE` bleibt der Zustand auch dann `FAILED_STORE`,
wenn der Store längst wieder gesund ist und die Pause um ein Vielfaches
überschritten wurde — `probe_write` wurde **nie** gerufen, und ein neues
Producerevent landet nicht einmal in der Queue (`qsize=0`).

**Nachher:**

```text
[PASS] F-10.1 fünf Schreibfehler in Folge setzen den Store aus
[PASS] F-10.2 nach der Pause wird der Store geprüft und erholt sich   (OK)
[PASS] F-10.3 die Erholung benutzte eine Probe, keinen Batch          (probe_calls=1)
[PASS] F-10.4 Records fließen nach der Erholung wieder                (rows=2)
[PASS] F-10.5 ein logging.recovered dokumentiert die Erholung         (1 Zeile)
```

Ursache, Norm und Umfang der Korrektur stehen in `V1_OPEN_POINTS.md` unter B-1.
