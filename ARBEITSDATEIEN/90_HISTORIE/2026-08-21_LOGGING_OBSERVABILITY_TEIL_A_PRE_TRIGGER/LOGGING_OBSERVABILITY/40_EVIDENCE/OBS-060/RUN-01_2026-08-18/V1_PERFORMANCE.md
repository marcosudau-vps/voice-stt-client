# OBS-060 – V1_PERFORMANCE

Run: `RUN-OBS-060-01_2026-08-18`
Skript: `probe_obs060_performance.py` — vollständige Ausgabe in
`output/probe_obs060_performance.out.txt` (exit 0)
Maschine: Windows 11 Pro 10.0.26200, Python 3.12.10

Die Zahlen sind auf **einer** Maschine gemessen und werden auch so
ausgewiesen. Die geprüfte Eigenschaft ist „begrenzt und nicht blockierend",
nicht „schnell auf diesem Rechner" — die Schwellen sind deshalb bewusst
großzügig.

---

## 1. Der eingefrorene Nachweis (ARCH §6.3)

> Nachweis (verbindlich, OBS-020 und OBS-060):
> Worker anhalten, danach 20.000 Records einreichen. `submit()` muss
> durchgehend unter einer im ersten Lauf festgeschriebenen Zeitgrenze
> zurückkehren und darf nie werfen.

Aufbau: `queue_size=8192`, **kein Worker** — nichts leert die Queue, sie läuft
voll und bleibt es.

| Messgröße | Wert |
|---|---|
| Submits | 20 000 |
| Gesamtzeit | 245,1 ms |
| Mittel je `submit` | 3,08 µs |
| Median | 3,20 µs |
| p99 | 5,70 µs |
| **Langsamster einzelner `submit`** | **0,038 ms** |
| festgeschriebene Zeitgrenze | 5,0 ms je Aufruf |

```text
[PASS] B-1.1 submit() hat über 20 000 Einreichungen nie geworfen
[PASS] B-1.2 alle 20 000 Einreichungen wurden versucht
[PASS] B-1.3 jeder einzelne submit blieb unter 5,0 ms       (langsamster 0,038 ms)
[PASS] B-1.4 der Speicher blieb begrenzt                    (qsize=8192)
[PASS] B-1.5 nichts ging ungezählt verloren                 (8192 + 0 + 11808 = 20000)
```

B-1.5 ist die eigentliche Aussage: von 20 000 Records sind 8 192 in der Queue
und 11 808 als `dropped_queue_full` gezählt. Die Summe geht exakt auf — **kein
Record verschwindet still**, und der Speicher wächst nicht über `queue_size`
hinaus (O-04).

Zum Vergleich meldet der bestehende OBS-020-Timingtest im selben Lauf
`100000 submits at full queue: 1.6811s (16.81us/call)` — dieselbe
Größenordnung, unter der zusätzlichen Last einer vollen Suite.

## 2. Durchsatz durch den echten Worker in echtes SQLite

| Messgröße | Wert |
|---|---|
| eingereicht | 20 000 |
| persistiert | 20 000 |
| Einreichphase | 232,0 ms |
| Einreichdurchsatz | 86 202 Records/s |
| Ende-zu-Ende (einreichen + schreiben) | 474,8 ms |
| **Ende-zu-Ende-Durchsatz** | **42 124 Records/s** |

```text
[PASS] B-2.1 der Worker hat alles persistiert, was er angenommen hat
[PASS] B-2.2 Ende-zu-Ende-Durchsatz mindestens 2 000 Records/s
```

## 3. Hot-Path-Aufwand (ARCH §8.6)

An den in §8.6 aufgezählten Stellen ist ausschließlich das Erhöhen einfacher
`int`-Attribute erlaubt. Gemessen wurde genau dieser Aufruf:

| Messgröße | Wert |
|---|---|
| Hot-Path-Aufrufe | 100 000 |
| Gesamtzeit | 7,28 ms |
| **je Paket** | **72,8 ns** |
| Records, die dabei entstanden | 1 (das 5-Sekunden-Aggregat) |

```text
[PASS] B-3.1 ein Hot-Path-Aufruf kostet deutlich unter 1 µs   (72,8 ns)
[PASS] B-3.2 100 000 Aufrufe erzeugten keinen Record je Paket (rows=1)
```

Das ist die Rechtfertigung der Regel: bei 40-ms-Blöcken wären ~90 000 Records je
Diktierstunde entstanden. Es entsteht **ein** Aggregatrecord, erzeugt vom
Worker, der die Zähler liest.

## 4. Abfragelatenz (Qt-Reaktionsfähigkeit)

Über einen Store mit **50 000** Zeilen, gemessen am echten `LocalLogProvider`:

| Abfrage | Dauer |
|---|---|
| erste Seite ohne Filter (limit 200) | 3,45 ms |
| zweite Seite über den Keyset-Cursor | 3,44 ms |
| gefiltert nach `session_id` | 4,00 ms |
| gefiltert nach `channel` | 6,47 ms |
| Freitextfilter | 3,42 ms |
| `fetch_raw` für einen Record | 14,72 ms |

```text
[PASS] B-4.1 jede Abfrage antwortet weit unter einer Sekunde  (langsamste 14,72 ms)
[PASS] B-4.2 die zweite Keyset-Seite ist nicht langsamer als die erste
```

B-4.2 ist die Eigenschaft, wegen der `CONTRACTS §5.7` Keyset statt `OFFSET`
einfriert: die Seitenkosten bleiben konstant, statt mit der Seitenzahl zu
wachsen. Die UI führt diese Abfragen ohnehin auf einem eigenen Thread aus
(`ThreadPoolExecutor(max_workers=1)`), der Qt-Thread wartet nie.

## 5. Retention

Über 30 000 Zeilen, alle älter als der Cutoff:

| Messgröße | Wert |
|---|---|
| Zeilen vorher | 30 000 |
| in einem Durchgang gelöscht | 30 000 |
| Zeilen nachher | 0 |
| Dauer | 108,0 ms |
| Zeitbudget je Durchgang | 0,2 s |

```text
[PASS] B-5.1 Retention hält ihr Zeitbudget ein                (0,108 s)
[PASS] B-5.2 Retention löscht blockweise und kommt voran      (30000 -> 0)
[PASS] B-5.3 Retention führt nie VACUUM aus
```

Blockgröße 5 000 (`RETENTION_BLOCK_SIZE`), Zeitbudget 0,2 s
(`RETENTION_TIME_BUDGET_S`) — beide aus `CONTRACTS §5.6`. `FD-D8` verbietet
`VACUUM`/`auto_vacuum`/`incremental_vacuum`; das ist strukturell in
`tests/test_obs030_sqlite_store.py` festgehalten.

## 6. Was hier bewusst nicht gemessen wurde

- **Eventstream-Empfangslatenz unter echter Netzlast.** Dafür bräuchte es einen
  laufenden Server; die Beobachterseite ist stattdessen im Protokollvergleich
  R-1…R-7 gemessen, der zeigt, dass die Beobachtung den Ablauf gar nicht ändert.
- **Qt-Bildwiederholrate.** `CONTRACTS §9.3` schreibt für V1 keine an; die
  relevante Eigenschaft — die Abfrage läuft nicht auf dem Qt-Thread — ist in
  den OBS-050-Tests festgehalten und hier über die Abfragelatenz belegt.
- **Absolute Speichergrenzen.** O-04 ist eine Struktureigenschaft (eine
  begrenzte Queue, kein Ringbuffer); B-1.4 misst sie direkt.
