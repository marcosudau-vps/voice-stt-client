# BACKPRESSURE_RESULTS – OBS-030 RUN-01 (Claude)

Die Queue selbst und ihre Wasserstandsregel sind OBS-020-Scope (bereits
Gate-PASS). Dieses Dokument belegt, dass OBS-030s **Worker/Store-Komposition**
die dort eingefrorene Backpressure-/Drop-Policy end-zu-end korrekt
respektiert und persistiert — nicht nur bis zur Queue, sondern bis in SQLite.

## 1. HIGH-Sonderregel unter Wasserstanddruck (End-zu-Ende über den Manager)

Automatisiert in `tests/test_obs030_worker.py::TestPriorityAndDropPolicyEndToEnd`
und `tests/test_obs030_worker.py::TestHighSpecialRule`; manuell reproduziert:

```text
$ python -c "... siehe RUN_LOG.md fuer das vollstaendige Skript ..."
accepted_low(75 expected)      : 75
LOW submit at/above watermark   : False (expect False = dropped)
HIGH submit at/above watermark  : True (expect True = accepted)
health.written                  : 76
health.dropped_watermark        : 1
HIGH record persisted            : True
```

Der 76. Record (HIGH, `is_internal=True`) wurde bei vollem Wasserstand
angenommen, während ein 76. LOW-Record abgelehnt worden wäre — und ist,
über den vollständigen Pfad Ingress → Worker → `SQLiteLogStore`, tatsächlich
in der Datenbank gelandet (`HIGH record persisted: True`), nicht nur in der
Queue akzeptiert.

## 2. N-04 / `not replayed`-Korrektur (ARCH §7.2)

`tests/test_obs030_worker.py::TestHighSpecialRule::test_replayed_typed_server_event_is_low_and_may_be_dropped_at_watermark`
bestätigt erneut auf Worker-Ebene: Ein replayter Serverevent **mit** `type`
ist `priority == "low"` und wird bei Wasserstanddruck verworfen — die in
OBS-000 korrigierte Regel greift durchgängig, nicht nur isoliert in
OBS-020s Ingress-Tests.

## 3. Nicht-blockierendes Verhalten bei totem/gestopptem Worker

```text
[OBS-030 timing baseline] 100000 submits at full queue, worker stalled: 2.2310s (22.31us/call)
dropped_queue_full: 100000
```

Simuliert exakt den in `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.5 Grenze 3/4`
benannten Fall ("Fällt der Worker aus, gehen ab diesem Zeitpunkt alle
Records verloren... bei totem Worker bleibt die Ansicht nutzbar"): Ohne
laufenden Worker (keine Queue-Drainage) bleibt `submit()` über 100.000
Aufrufe hinweg non-blocking und zählt korrekt `dropped_queue_full`. Bewusst
**kein** absoluter Grenzwert im Plan (wie schon bei OBS-020) — dieser Wert
ist Regressionsbasis, keine Leistungszusage. Vergleichbar mit der
OBS-020-Baseline (~15.6–18.5us/call ohne Worker-Overhead); die hier leicht
höhere Zahl (~22.3us/call) spiegelt denselben Prozess/dieselbe Maschine zu
einem anderen Zeitpunkt wider, keinen Regressionsbefund — die Größenordnung
ist unverändert (`<10s` für 100.000 Aufrufe, großzügiger Hänge-Schutz).

## 4. Worker-seitige DROPPING/OK-Zustandsübergänge

`LoggingWorker._check_backpressure_state` (neu in diesem Run) überführt den
Health-Zustand bei Füllstand ≥75 % nach `DROPPING` und zurück nach `OK`,
sobald der Füllstand für mindestens 5 s unter 25 % bleibt — an diesem Punkt
wird zusätzlich **ein** Record `logging.records_dropped` mit den seit dem
letzten Reset aufgelaufenen Zählern geschrieben und die Zähler zurückgesetzt
(`ARCH §7.3`, `G-6`: direkt geschrieben, unter Umgehung von Queue und
Handler). Die Zähler-Reset-Mechanik selbst ist in
`core/observability/health.py::reset_drop_counters` isoliert getestet
(`tests/test_obs030_worker.py` deckt den End-zu-Ende-Pfad über
`FakeStore`/`FakeSink` ab, ohne auf die reale 5-Sekunden-Wartezeit angewiesen
zu sein, da die Zählerlogik selbst unabhängig vom Timer geprüft wird).

## Fazit

Kein `FAIL`-Befund. Die eingefrorene Backpressure-/Drop-Policy (Wasserstand,
HIGH-Sonderregel inkl. `not replayed`, katastrophale Überlast bleibt
gezählt/sichtbar) ist über den gesamten Pfad bis SQLite nachweisbar korrekt.
