---
id: OBS-020
title: Ingress, Backpressure, Health & Python-Logging-Handler
status: READY
authority: planning
workstream: OBS
phase: A
depends_on: OBS-010
freeze_reference: 00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md
last_updated: 2026-08-15
---

# OBS-020 – Ingress, Backpressure, Health & Python-Logging-Handler

> **READY FOR IMPLEMENTATION.** Alle Architekturentscheidungen sind in OBS-000
> geschlossen.
>
> **Titelkorrektur aus OBS-000.** Der frühere Titel lautete „Ingress, Health &
> Redaction". Redaction und Normalizer liegen in **OBS-010** — sie sind
> untrennbar, weil der Normalizer `redact` am Ende jedes Pfades ruft, und beide
> sind reine, I/O-freie Logik. OBS-020 besitzt dafür den
> Python-Logging-Handler. Der Dateiname bleibt aus Pfadgründen unverändert.
> Begründung: `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md §8.2`.

---

## Ziel

Alle Records durch eine passive, sichere und **nichtrekursive** Aufnahmegrenze
führen. Nach diesem Paket kann Logging aktiviert oder deaktiviert werden, ohne
das fachliche Clientverhalten zu verändern.

## Scope

- [ ] `core/observability/ingress.py` — `ObservabilityIngress`, `NullIngress`,
      `NULL_INGRESS`
- [ ] **eine** bounded `queue.Queue` (Default 8192) mit Wasserstandsregel bei
      75 %
- [ ] `core/observability/health.py` — `LoggingHealthState`,
      `LoggingHealthSnapshot`, `LoggingInternalHealth`, Emergency-stderr
- [ ] `core/observability/adapters/python_logging.py` — `UnifiedLogHandler`
- [ ] `core/logging_setup.py` — **additiv**: optionaler Parameter
      `observability=None`, optionaler dritter Handler

## Non-Scope

- Kein Worker, kein Store, kein Sink, keine UI, keine Settings.
- Keine Änderung an Datei- und Stdout-Handler. Sie bleiben **unverändert**
  bestehen — sie sind heute die einzige Diagnosequelle und zugleich die
  Rückfallebene bei totem Worker (`FD-D7`).
- Keine strukturierten Client-Hooks (das ist OBS-040).
- Keine `report_local_feedback`-Nutzung, kein `CanonicalEventType`, keine
  `FeedbackEngine` (Regel G-5).

---

## Geänderte Produktdateien

| Datei | Art | Umfang |
|---|---|---|
| `core/logging_setup.py` | optionaler Parameter, optionaler dritter Handler | ~10 Zeilen, **rein additiv** |

Alles Übrige sind neue Dateien. Das Signal für einen Fehler ist einfach: Wird
mehr als diese eine Datei geändert, ändert das Paket fachliches Verhalten.

## Sollzustand

```python
def setup_logging(config, *, observability=None) -> None:
    ...                       # unveraendert
    if observability is not None:
        handler = UnifiedLogHandler(observability.ingress, normalizer)
        handler.setLevel(observability.level)     # Default INFO
        root_logger.addHandler(handler)
```

**Rückwärtskompatibilität:** Ohne den Parameter verhält sich `setup_logging`
**exakt** wie heute. Bestehende Tests rufen es direkt auf.

## Verbindliche Quellen

| Gegenstand | Fundstelle |
|---|---|
| Backpressure, Wasserstandsregel, Zähler | `ARCH §7` |
| Prioritätsregel inkl. `not replayed` | `CONTRACTS §1.5`, `FD-R1` |
| Rekursionssperren G-1 bis G-7 | `ARCH §8.1` |
| Wo redigiert wird | `ARCH §8.2` |
| Health-Zustände, Snapshot, Ausgabewege | `CONTRACTS §11.2` |
| Levelzuständigkeit | `ARCH §8.7`, `FD-D9` |
| Ingress-Signaturen | `CONTRACTS §6` |
| Nichtblockierungs-Invariante und ihr Nachweis | `ARCH §6.3` |

## Implementierungsschritte

1. `ObservabilityIngress.submit(record) -> bool`: thread-sicher, blockiert nie,
   wirft nie. Reihenfolge: Health `FAILED`? → `enabled`/Level? →
   Wasserstandsregel → `put_nowait`.
2. `NullIngress` als verhaltensgleiches No-Op; `NULL_INGRESS` als
   Modulkonstante.
3. `drain(max_items, timeout)` für den späteren Worker.
4. `LoggingInternalHealth` mit allen Zählern unter **einem** `threading.Lock`,
   einschließlich `deduplicated` (`FD-R5`).
5. Emergency-Ausgang: eigener Logger `observability.internal` mit
   `propagate = False` und einem `StreamHandler(sys.stderr)` (G-2).
   Ratenbegrenzung als **harte** Obergrenze: höchstens eine Zeile je Code und
   60 s, unabhängig von der Fehlerzahl, mit Wiederholungszähler (G-4).
   `sys.stderr is None` abfangen (PyInstaller-GUI-Build).
6. `UnifiedLogHandler(logging.Handler)`:
   - Wiedereintrittssperre über `threading.local` (G-1);
   - `handleError` überschrieben, meldet an Health statt an stderr (G-3);
   - **`flush()` und `close()` sind No-Ops** (G-7);
   - `emit`: normalisieren → `ingress.submit`. Kein `format()`-Aufruf, kein I/O;
   - Filter, der Records des Loggers `observability.internal` verwirft
     (redundant zu `propagate=False`, aber billig).

---

## Tests

### Positiv

- Eine `logger.info`-Zeile erzeugt genau **einen** Record mit korrektem
  `component`/`channel`/`level`.
- `exc_info` landet als **Text** in `details["exception"]`; `record.args`
  erscheint **nirgends**.
- Die vier bestehenden `extra`-Felder werden übernommen.
- Reihenfolge unter Last: HIGH-Records überleben, LOW werden verworfen.
- `NullIngress` ist verhaltensgleich.

### Negativ

- `submit(None)`; `submit` mit fremdem Typ.
- Logzeile mit fehlerhaftem `%`-Format.
- `extra` mit einem Objekt, dessen `__str__` wirft.
- Logzeile aus einem Thread ohne Namen.
- `enabled=False` → `submit` liefert sofort `False`, es wird nichts gebaut.

### Failure

- Queue voll → `submit` liefert `False`, wirft nicht, `dropped_queue_full`
  steigt.
- **N-04:** Wasserstand ≥ 75 % mit **replayten** Serverevents → sie werden
  verworfen, obwohl sie einen `type` tragen. Ohne `not replayed` in der
  Prioritätsregel wäre dieser Test grün-falsch.
- Ingress liefert immer `False` → keine Ausnahme, kein stderr je Zeile.
- Normalizer wirft → `handleError` zählt, Anwendung läuft weiter.
- **Rekursionstest:** Ein Fehler wird über `logging` gemeldet → die Anzahl
  erzeugter Records bleibt unter einer festen Obergrenze.
- 2000 Fehler in einer Sekunde → **≤ 1** stderr-Zeile, Wiederholungszähler
  stimmt.
- `sys.stderr = None` → keine Ausnahme, Zähler laufen weiter.
- `sys.stderr.write` wirft → keine Ausnahme.
- **N-03:** `logging.shutdown()` (also `flush`+`close` auf jedem Handler)
  wartet **nicht** auf den Worker.

### Nebenläufigkeit und Zeit

- Acht Threads × 5000 Submits → `enqueued + dropped_watermark +
  dropped_queue_full` geht exakt auf; kein Record doppelt.
- 100.000 `submit`-Aufrufe bei **voller** Queue: Die gemessene Zeit wird im
  ersten Lauf ermittelt und **im Testprotokoll festgeschrieben**; spätere Läufe
  vergleichen dagegen.

  > Bewusst **kein** absoluter Grenzwert im Plan: Ein fester Zeitwert ist auf
  > fremder Hardware kein Kriterium, sondern erzeugt falsche Fehlschläge. Der
  > Wert ist ein **Regressionswächter**, keine Leistungszusage.

### Integration

- Doppelter `setup_logging`-Aufruf → genau **ein** `UnifiedLogHandler` am Root
  (`handlers.clear()` verhindert die Dopplung).
- Datei- und Stdout-Ausgabe sind Zeile für Zeile **identisch** zum Zustand vor
  der Änderung — Vergleich zweier `client.log` aus demselben Skript.
- Ohne `observability`-Parameter verhält sich `setup_logging` exakt wie heute.

### Contract-Tests

- `logging.getLogger("observability.internal").propagate is False`.
- `health.py` importiert weder `core.event_models` noch `core.feedback_reducer`
  — der Nachweis, dass **kein** Feedbackweg entstehen kann (G-5).
- Kein `PySide6`-Import.

---

## Pflichtprüfungen

- [ ] Positive Tests
- [ ] Negative Tests
- [ ] Failure-/Edge-Tests
- [ ] Nebenläufigkeitstests
- [ ] Contract-Tests
- [ ] **Die vollständige bestehende Client-Suite bleibt grün, ohne dass ein
      bestehender Test geändert wird.**
- [ ] `git diff --check`
- [ ] `git diff` zeigt in `core/logging_setup.py` **keine** Änderung an einer
      bestehenden Zeile
- [ ] kein unbeabsichtigter Cross-Workstream-Diff

## Akzeptanzkriterien

- Logging kann aktiviert oder deaktiviert werden, **ohne** das fachliche
  Clientverhalten zu verändern.
- `submit` blockiert unter keinem geprüften Umstand und wirft nie.
- Ein dauerhaft defekter Zustand erzeugt **höchstens eine** stderr-Zeile je
  Code und 60 s.
- Die bestehende `client.log` ist im Format unverändert.

## Gate-Hinweis

Der Ende-zu-Ende-Nachweis `logger.info → SQLite` gehört zum Gate von
**OBS-030** — in OBS-020 existiert der Store noch nicht. OBS-020 wird gegen
einen aufzeichnenden Fake-Store abgenommen. Das verschiebt, **wo** der Nachweis
fällig wird, nicht **ob**: Grüne Tests gegen Fakes bleiben ausdrücklich kein
Fertigstellungsnachweis. Begründung:
`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md §8.3`.

## Evidence

Ablage: `40_EVIDENCE/OBS-020/`.

- Testläufe mit Kommando, Exitcode, Ergebnis.
- Die gemessenen Zeiten aus dem Nebenläufigkeitstest, ausdrücklich als
  Regressionsbasis benannt.
- Der Diff zweier `client.log`-Dateien (vorher/nachher).
- `git diff --stat` und der vollständige Diff von `core/logging_setup.py`.

## Gate

`PASS` nur nach separatem Review. Ein Coding-Agent darf das Gate nicht allein
aufgrund eigener grüner Tests vergeben.
