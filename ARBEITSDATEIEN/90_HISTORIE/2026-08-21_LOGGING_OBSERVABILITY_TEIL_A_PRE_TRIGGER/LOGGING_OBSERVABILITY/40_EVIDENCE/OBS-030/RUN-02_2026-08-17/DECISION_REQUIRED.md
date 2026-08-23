# OFFENE ENTSCHEIDUNG – „nur verwerfen und zählen" nach `FAILED_WORKER`

Status: **OFFEN – durch die unabhängige Prüf-/Entscheidungsinstanz zu
entscheiden**
Aufgeworfen in: `RUN-OBS-030-02_2026-08-17` (OBS-030 Korrekturlauf)
Zuletzt bearbeitet: Cleanup `RUN-OBS-030-02` (Prompt
`OBS-030_FIX_RUN_II.md`)

> **Der Korrekturlauf und der Cleanup treffen diese Entscheidung nicht.**
> Es gibt in diesem Stand **keine** Implementierung, die sie vorwegnimmt.

## 1. Ausgangsproblem

Nach der B-1-Korrektur bricht die Worker-Schleife bei dauerhaftem Fehlschlag
endgültig ab, Health wechselt auf `FAILED_WORKER`, und
`ObservabilityIngress.submit()` liefert ab diesem Moment `False`
(`ingress.py`, erster Prüfschritt `health.is_failed()`).

Diese neu abgewiesenen Submits werden **nicht gezählt**. Offen ist, ob das
den normativen Vorgaben genügt.

## 2. Die maßgebliche Formulierung

`LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.3`, Tabellenzeile „Worker-Ausnahme in
der Schleife":

> „gefangen, `worker_errors++`, Schleife läuft weiter. Bricht sie dennoch ab:
> Ingress wechselt in **„nur verwerfen und zählen"**. **Kein
> Neustartversuch** — ein Worker, der zweimal stirbt, stirbt beim dritten Mal
> auch" → Health `FAILED_WORKER`

Die Zeile benennt **keinen** Zähler und verlangt **nicht** ausdrücklich einen
neuen.

## 3. Der Konflikt

`LOGGING_ARCHITEKTUR_FREEZE_V1.md §7.3` trägt die Überschrift
„Zähler – **eingefroren**" und listet abschließend:

```text
enqueued · written · deduplicated · dropped_watermark · dropped_queue_full ·
dropped_shutdown · malformed · store_errors · sink_errors ·
retention_errors · worker_errors · queue_depth · db_bytes
```

`LOGGING_CONTRACTS_FREEZE_V1.md §11.2` friert `LoggingHealthSnapshot` mit
genau diesen Feldern als frozen dataclass ein.

Für „nach `FAILED_WORKER` abgewiesener Submit" existiert dort kein Zähler.
Damit stehen sich zwei eingefrorene Aussagen gegenüber: §8.3 verlangt ein
Zählen, §7.3/§11.2 halten den Zählersatz geschlossen.

## 4. Die beiden auslegbaren Lesarten

**Lesart A — eigener Zähler erforderlich.**
„verwerfen **und** zählen" bezieht sich auf jeden nach dem Ausfall
angebotenen Record. Dann fehlt ein Zähler, und `ARCH §7.3` /
`CONTRACTS §11.2` müssten additiv erweitert werden.

**Lesart B — bestehende Zählersemantik genügt.**
„nur verwerfen und zählen" beschreibt den **Modus des Ingress**, nicht die
Einführung eines Zählers. Was zum Zeitpunkt des Ausfalls bereits in der Queue
lag, **wird** gezählt: `LoggingWorker._drain_and_count_leftovers()` bucht es
auf `dropped_shutdown` (`ARCH §8.3`, Shutdown-Zeile), notfalls über
`qsize()`, wenn selbst `drain` defekt ist. Nach dem Ausfall angebotene
Records erreichen die Queue nie und werden nie zu Records; ihre Ablehnung ist
über `submit() == False` am Aufrufort sichtbar, und der Ausfall selbst ist
über `worker_errors`, den Health-State `FAILED_WORKER` und die
ratenbegrenzte stderr-Zeile sichtbar.

## 5. Warum keine Ersatzabbildung gewählt wurde

Eine Abbildung auf `dropped_watermark` oder `dropped_queue_full` scheidet
aus: beide speisen laut `ARCH §7.3` den nach der Erholung erzeugten Record
`logging.records_dropped` („genau **einen** Record `logging.records_dropped`
mit den Zählerständen"). Sie zweckzuentfremden würde diesen Record eine
falsche Ursache behaupten lassen. `dropped_shutdown` bedeutet „beim
Shutdown-Timeout verworfen" und trifft den Fall ebenfalls nicht.

## 6. Was der Korrekturlauf zwischenzeitlich getan hatte – und was davon zurückgenommen ist

`RUN-OBS-030-02` hatte Lesart A gewählt und einen zusätzlichen Zähler
`dropped_failed` eingeführt (letztes Feld von `LoggingHealthSnapshot`, mit
Default, plus `LoggingInternalHealth.record_dropped_failed()` und einem
Aufruf in `ObservabilityIngress.submit()`), begleitet von einem
`DECISION REQUIRED`-Nachtrag in `LOGGING_DECISIONS_FREEZE_V1.md`.

**Beides ist im Cleanup vollständig zurückgenommen worden:**

| Gegenstand | Stand jetzt |
|---|---|
| `LoggingHealthSnapshot.dropped_failed` | entfernt — der Snapshot hat wieder exakt die Form aus `CONTRACTS §11.2` |
| `LoggingInternalHealth.record_dropped_failed()` | entfernt |
| Aufruf in `ObservabilityIngress.submit()` | entfernt; `core/observability/ingress.py` ist wieder unverändert gegenüber `HEAD` |
| Tests/Assertions auf `dropped_failed` | entfernt |
| Nachtrag `DR-OBS-030-01` in `LOGGING_DECISIONS_FREEZE_V1.md` | entfernt; die normative Datei ist wieder byte-identisch zum Stand vor `RUN-OBS-030-02` |

**Begründung der Rücknahme:** `dropped_failed` war eine echte Erweiterung
zweier eingefrorener Verträge ohne Autorisierung. Das Verfahren für einen
solchen Fall ist in `LOGGING_DECISIONS_FREEZE_V1.md §10` festgelegt und
beginnt mit **`anhalten`**; der Korrekturlauf hatte stattdessen implementiert
und dokumentiert. `AGENTS.md` des Workstreams verlangt zusätzlich
ausdrücklich: *„Neue Funde nicht automatisch reparieren. Fund → dokumentieren
→ Blocker? …"*. Der Zähler war vom blockierenden Kern des Gate-Befunds B-1
trennbar (siehe Abschnitt 7) und damit kein Blocker.

## 7. Warum die offene Frage B-1 nicht blockiert

Der Gate-Befund B-1 verlangt der Sache nach, dass ein Worker-Ausfall nicht
unbemerkt bleibt und Producer nicht scheinbar erfolgreich bedient werden.
Das ist **ohne** den Zähler vollständig erfüllt und getestet:

- unerwartete Ausnahme in der Schleife wird gefangen, `worker_errors++`,
  Schleife läuft weiter;
- bei endgültigem Abbruch: Health `FAILED_WORKER`, **kein** Neustartversuch;
- `submit()` liefert danach `False` — kein Producer wird belogen;
- bereits eingereihte Records werden als `dropped_shutdown` gezählt;
- kein ungefilterter `threading`-Traceback, ausschließlich der ratenbegrenzte
  `[observability] …`-Ausgang (G-2/G-4).

Nachweise: `tests/test_obs030_worker_fault_injection.py`, `FAULT_INJECTION.md`.

## 8. Was zu entscheiden ist

1. **Lesart B bestätigen** → nichts weiter zu tun; der aktuelle Stand ist
   vertragskonform, und `ARCH §8.3` gilt als durch `dropped_shutdown` plus
   `worker_errors` und den Health-State erfüllt.
2. **Lesart A bestätigen** → dann ist ein Zähler für nach `FAILED_WORKER`
   abgewiesene Submits vorzusehen; das erfordert eine ausdrückliche,
   autorisierte Ergänzung von `ARCH §7.3` **und** `CONTRACTS §11.2` und
   anschließend eine erneute, dann gedeckte Implementierung.
3. Ergänzend zu klären, weil derselbe Mechanismus greift: `Ingress.is_failed()`
   ist auch bei `FAILED_STORE` wahr. Eine Entscheidung nach Lesart A müsste
   sagen, ob der Zähler beide Fälle oder nur den Worker-Ausfall umfasst.

Verwandter, hiervon getrennter offener Punkt: Gate-Befund **W-3** (Records,
die während einer Store-Aussetzung verworfen werden, sind nirgends gezählt)
— Begründung in `GATE_FINDINGS.md`. Beide Punkte betreffen dieselbe Frage,
wie vollständig der eingefrorene Zählersatz sein soll, und lassen sich
sinnvoll gemeinsam entscheiden.
