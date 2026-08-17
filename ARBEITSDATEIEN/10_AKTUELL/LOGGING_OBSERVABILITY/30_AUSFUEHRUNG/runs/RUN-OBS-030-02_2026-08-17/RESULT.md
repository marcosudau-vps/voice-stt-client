# RESULT – RUN-OBS-030-02_2026-08-17 (Korrekturlauf inkl. Cleanup)

## Status

`OBS-030 CLEANUP COMPLETED – READY FOR INDEPENDENT RE-REVIEW`

Vorheriger Stand dieses Runs: `OBS-030 CORRECTED – READY FOR RE-REVIEW`.
Der anschließende Cleanup (Prompt `OBS-030_FIX_RUN_II.md`) hat zwei nicht
autorisierte Änderungen dieses Runs zurückgenommen — den Zähler
`dropped_failed` und den Nachtrag `DR-OBS-030-01` in
`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`. Die fachlichen Korrekturen
B-1, B-3 und W-1/W-2/W-4/W-5/W-7 bleiben vollständig bestehen.
**Dieser Run verändert damit kein normatives Dokument.**

**Kein Gate-PASS in diesem Run.** Das OBS-030 Gate bleibt offen; ein
Korrekturlauf darf seinen eigenen Gate-Punkt nicht setzen. In
`LOGGING_V1_CHECKLISTE.md` bleibt „OBS-030 – Gate Review" unverändert `[ ]`.

## Ausgangspunkt

`40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`
→ **OBS-030 GATE FAIL** (B-1, B-2, B-3; dazu W-1 bis W-7).
Diese Historie bleibt vollständig erhalten und wurde nicht verändert.

## Blockierende Befunde

| Befund | Ergebnis | Korrektur | Testnachweis |
|---|---|---|---|
| **B-1** Keine Fehlerisolation auf Schleifenebene im Worker | **BEHOBEN** | `run()` guarded; `_record_loop_failure` (`worker_errors++` über den observability-internen Fehlerpfad, G-2/G-4); Abbruch erst nach 5 aufeinanderfolgenden Fehlern, **kein Neustartversuch**; `_finish()` setzt `FAILED_WORKER` **vor** dem Flush, damit `Ingress.is_failed()` greift und `submit()` ab da `False` liefert; bereits eingereihte Queue-Reste werden als `dropped_shutdown` gezählt; `dataclasses.replace` im `try`. Ob darüber hinaus die *nach* dem Ausfall abgewiesenen Submits eigens zu zählen sind, ist die **offene** Frage aus `DECISION_REQUIRED.md` — der zwischenzeitliche Zähler `dropped_failed` ist zurückgenommen | `tests/test_obs030_worker_fault_injection.py` (6), Laufzeitprobe `FAULT_INJECTION.md` |
| **B-2** Evidence widerspricht dem Code | **BEHOBEN** | korrigierte `CONTRACT_COVERAGE.md` in RUN-02; Korrekturvermerke an RUN-01-`CONTRACT_COVERAGE.md`, RUN-01-`TEST_RESULTS.md` und RUN-01-`RESULT.md` angehängt, **ohne** die Gate-FAIL-Historie zu löschen oder umzuschreiben | Abgleich Zeile für Zeile gegen Code und ausgeführte Tests |
| **B-3** `CONTRACTS §4.3 P-8` nicht umgesetzt | **BEHOBEN** | `LoggingObservabilityConfig.validate()` prüft `db_path`/`file_sink_dir` gegen den **aufgelösten** Pfad; `ObservabilityManager._resolve_profile_path()` wiederholt die Prüfung zur Laufzeit, weil `app.py::main()` kein `validate()` ruft | `tests/test_obs030_path_boundaries.py` (23), `PATH_BOUNDARIES.md` |

## W-1 bis W-7

| # | Gegenstand | Entscheidung | Normbezug |
|---|---|---|---|
| W-1 | Defekter Store legt den JSONL-Sink still | **FIXED** | `ARCH §8.3` (Reaktionen abschließend, Sink nicht genannt), `O-05`, `CONTRACTS §11.1` (Reihenfolge, keine Bedingung) |
| W-2 | `logging.retention_pressure` nur als stderr | **FIXED** | `CONTRACTS §12.4`, `§5.6`, `FD-D8` |
| W-3 | Kein Zähler für Verwürfe bei ausgesetztem Store | **NOT A DEFECT** (Lücke ausdrücklich benannt) | `ARCH §7.3` („Zähler – eingefroren") und `CONTRACTS §11.2` kennen keinen; Abbildung auf vorhandene Zähler würde `logging.records_dropped` verfälschen |
| W-4 | Kein „leerer Testschreibvorgang" nach der Store-Pause | **FIXED** | `ARCH §8.3` wörtlich |
| W-5 | `DISABLED` wird nie erzeugt | **FIXED** | `ARCH §8.3` (eingefrorene Zustandsmenge), `CONTRACTS §11.2` |
| W-6 | `clear_history()` blockiert bis zu 5 s | **DEFERRED → OBS-050** | `CONTRACTS §5.8`, `§10.3`, `§9.2`, `ARCH §4.1`/`§5.1`; in OBS-030 existiert kein Qt-Aufrufer, `ui/**` unverändert |
| W-7 | PRAGMA-Reihenfolge / Retentionstakt / `stop()` ohne Start | **FIXED (alle drei)** | `CONTRACTS §5.2`, `§5.6`, `ARCH §8.3` |

Vollständige Begründungen: `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/GATE_FINDINGS.md`.

## Teststand

```text
tests/test_obs030_worker_fault_injection.py    6 passed
tests/test_obs030_path_boundaries.py          23 passed
tests/test_obs030_gate_corrections.py         18 passed
pytest -q -k obs030                          129 passed, 10 subtests
unittest discover -p test_obs030_*.py        Ran 129, OK
pytest -q -k "obs010 or obs020 or obs030"    331 passed, 112 subtests
pytest -q  (volle Client-Suite)                1 failed, 843 passed, 351 subtests
unittest discover -p test_*.py               Ran 844, FAILED (errors=1)
git diff --check                             leer, Exit 0
```

Der eine Fehlschlag ist der vorbestehende, umgebungsbedingte
`lefx.interfaces`-Fehler in `tests/test_ap06_followup.py`; erneut geprüft und
nachweislich außerhalb des Diffs. Der vom Gate benannte intermittierende
`test_core_bridge`-Befund trat in diesem Run nicht auf (fünf isolierte Läufe
grün) und bleibt als vorbestehende Flakiness außerhalb des Diffs notiert.

## Geänderte Dateien

**Produkt**

```text
core/observability/worker.py          B-1, W-1, W-2, W-4, W-7b, W-7c
core/observability/storage/sqlite.py  W-7a (PRAGMA-Reihenfolge), W-4 (probe_write)
core/observability/manager.py         B-3 (_resolve_profile_path), W-5 (DISABLED)
core/config.py                        B-3: P-8-Prüfung
```

Nach dem Cleanup sind **keine** weiteren Bestandsdateien betroffen als in
RUN-01: `core/observability/health.py` steht wieder bei `+21/-2` (RUN-01-Stand,
vom Gate-Review verifiziert), `core/observability/ingress.py` ist wieder
unverändert gegenüber `HEAD`. Der zwischenzeitlich dort eingefügte Zähler
`dropped_failed` ist vollständig entfernt.

**Tests**

```text
tests/test_obs030_worker_fault_injection.py   neu (Assertion auf dropped_failed im
                                              Cleanup entfernt, Test unverändert grün)
tests/test_obs030_path_boundaries.py          neu
tests/test_obs030_gate_corrections.py         neu
tests/test_obs030_config.py                   ein Pfadliteral (P-8-konform), begründet
```

**Dokumentation**

```text
30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/{RUN_LOG,RESULT,RUN_REPORT,OUTPUT_INDEX}.md
40_EVIDENCE/OBS-030/RUN-02_2026-08-17/{GATE_FINDINGS,TEST_RESULTS,FAULT_INJECTION,
    PATH_BOUNDARIES,CONTRACT_COVERAGE,DIFF_SUMMARY,DECISION_REQUIRED}.md
40_EVIDENCE/OBS-030/RUN-02_2026-08-17/probe_obs030_gate_fixes.py
40_EVIDENCE/OBS-030/RUN-01_.../{CONTRACT_COVERAGE,TEST_RESULTS}.md   Korrekturvermerk
30_AUSFUEHRUNG/runs/RUN-OBS-030-01_.../RESULT.md                      Korrekturvermerk
30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md       wiederhergestellt und fortgeschrieben
00_STEUERUNG/CURRENT_STATE.md, 00_STEUERUNG/LOG_VERLAUF.md (append-only)
```

`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` steht **nicht** mehr auf dieser
Liste: der Nachtrag `DR-OBS-030-01` wurde im Cleanup entfernt, die Datei ist
byte-identisch zum Stand vor diesem Run.

## Offene Punkte

1. **Auslegung von `ARCH §8.3` „nur verwerfen und zählen"** — verlangt die
   Zeile einen eigenen Zähler für nach `FAILED_WORKER` abgewiesene Submits,
   oder genügt die eingefrorene Zählersemantik samt Behandlung der
   Queue-Reste? Vollständig dargestellt in
   `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md`. **Vom Gate
   zu entscheiden; dieser Run entscheidet sie nicht** und enthält keine
   Implementierung, die sie vorwegnimmt.
2. **W-3** — bewusst nicht gelöst; betrifft dieselbe Frage nach der
   Vollständigkeit des eingefrorenen Zählersatzes und lässt sich gemeinsam
   mit Punkt 1 entscheiden (sinnvollerweise zu OBS-060).
3. **W-6** — Auflage für OBS-050: `clear_history()` nicht aus dem
   Qt-Mainthread rufen (`O-03`).
4. **Ablageort der Fortschrittscheckliste** — die kanonische Datei war im
   Arbeitsbaum gelöscht; eine leere Zweitfassung liegt im nicht versionierten
   `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/`. Wiederhergestellt wurde
   der kanonische Pfad; ein bewusster Umzug ist eine Entscheidung für Marco
   (siehe `RUN_LOG.md`, Abschnitt 6).
5. **`test_core_bridge`-Flakiness** — vorbestehend, außerhalb dieses
   Workstreams, nicht repariert.
6. **Nachträgliche Korrekturvermerke in der RUN-01-Evidence** — drei Dateien
   sind am Ende um einen gekennzeichneten Vermerk ergänzt (Inhalt selbst
   unverändert). Eine normative Regel zum Umgang mit abgeschlossener Evidence
   existiert nicht; die Ergänzung stützt sich allein auf die Auftragszeile
   B-2 („falsche Aussagen korrigieren" bei gleichzeitigem Verbot,
   Gate-FAIL-Historie zu löschen oder umzuschreiben). Laut Cleanup-Auftrag
   bleiben sie unverändert und sind Gegenstand des unabhängigen Gate-Reviews.

## Git

Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
Der lokale Commit darf erst nach einem erneuten unabhängigen Gate-Review mit
`PASS` erstellt werden.

## Nächster zulässiger Schritt

Erneuter **unabhängiger OBS-030 Gate-Review** in einer frischen Session,
gegen den Repositoryzustand, `git diff`/`git status`, eigenständige Testläufe
und diese Evidence — nicht gegen diesen Bericht.
**OBS-040 darf nicht beginnen.**
