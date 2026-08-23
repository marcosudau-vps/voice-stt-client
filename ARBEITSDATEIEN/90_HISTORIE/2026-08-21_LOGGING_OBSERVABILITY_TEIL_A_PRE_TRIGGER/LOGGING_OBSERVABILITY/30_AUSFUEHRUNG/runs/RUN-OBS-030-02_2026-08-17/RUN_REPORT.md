# RUN_REPORT – RUN-OBS-030-02_2026-08-17

Gliederung nach `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`, Abschnitt
„Abschluss eines Runs".

## Run-ID

`RUN-OBS-030-02_2026-08-17`
Prompts: `30_AUSFUEHRUNG/Prompts/OBS-030_FIX_RUN.md` (Korrekturlauf) und
`30_AUSFUEHRUNG/Prompts/OBS-030_FIX_RUN_II.md` (Cleanup desselben Runs).

## Work Package

OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink
(`20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-030_QUEUE_WORKER_SQLITE_RETENTION.md`).
Kein neues Work Package, keine Neuplanung.

## Ausgangszustand

`OBS-030 GATE FAIL`
(`40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md`) mit
den blockierenden Befunden B-1 (keine Fehlerisolation auf Schleifenebene im
Worker), B-2 (Evidence widerspricht dem Code), B-3 (`CONTRACTS §4.3 P-8`
nicht umgesetzt) sowie W-1 bis W-7. Architektur, Schema und Testbasis aus
RUN-01 wurden vom Gate eigenständig verifiziert und blieben unangetastet.

## Durchgeführte Arbeiten

**Fachlich (Korrekturlauf).**

1. *Der Worker stirbt nicht mehr still.* Vorher beendete eine unerwartete
   Ausnahme im Schleifenrumpf den Thread, während Health `ok` meldete,
   `worker_errors` `0` blieb und `submit()` weiter `True` lieferte. Jetzt:
   Ausnahme gefangen, `worker_errors++` über den ratenbegrenzten, nicht
   propagierenden Notausgang, Schleife läuft weiter; nach fünf
   aufeinanderfolgenden Fehlern endgültiger Abbruch mit `FAILED_WORKER`
   **vor** dem Flush, kein Neustartversuch, Queue-Reste als
   `dropped_shutdown` gezählt, kein `threading`-Traceback an G-2/G-4 vorbei.
2. *Store und Sink sind getrennte Fehlerdomänen.* Ein degradierter,
   ausgesetzter oder nur lesbarer Store nimmt den intakten JSONL-Sink nicht
   mehr mit; die Reihenfolge „Store zuerst, Sink danach" bleibt erhalten —
   sie war nie eine Bedingung.
3. *Store- und Sink-Pfade können das Benutzerprofil nicht verlassen.* Geprüft
   wird der aufgelöste Pfad, in der Konfigurationsvalidierung **und** in der
   Kompositionswurzel, weil der reale Startpfad `AppConfig.validate()` nicht
   aufruft.
4. *Drei Vertragsdetails stimmen jetzt wörtlich:* PRAGMA-Reihenfolge,
   Retentionstakt nach *geschriebenen* Records, leerer Testschreibvorgang
   nach der 60-Sekunden-Pause.
5. `logging.retention_pressure` entsteht als kanonischer Record;
   `DISABLED` wird erzeugt.

**Cleanup (`OBS-030_FIX_RUN_II.md`).** Rücknahme zweier nicht autorisierter
Änderungen dieses Runs — Details in `RUN_LOG.md`, Abschnitt 8:

- Zähler `dropped_failed` vollständig entfernt (Snapshot, Health, Ingress,
  Test-Assertion, Probeskript, Evidence-Aussagen). Kein Ersatzzähler, keine
  Abbildung auf einen vorhandenen Zähler.
- Nachtrag `DR-OBS-030-01` aus `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`
  entfernt; die Datei ist byte-identisch zum Stand vor diesem Run.
- Zuvor die im Korrekturlauf ausgelassene Pflichtlektüre nachgeholt
  (`README.md`, `AGENTS.md`, `MASTERPLAN.md`, `ARBEITSPROZESS.md`,
  Themen-`AGENTS.md`).

## Erzeugte / geänderte Dateien

Vollständig in `RESULT.md` („Geänderte Dateien") und
`40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DIFF_SUMMARY.md`.

Produkt: `core/observability/worker.py`, `.../storage/sqlite.py`,
`.../manager.py`, `core/config.py`. Nach dem Cleanup sind
`core/observability/health.py` (wieder `+21/-2`) und
`core/observability/ingress.py` (wieder unverändert) auf dem Stand, den der
Gate-Review für RUN-01 festgehalten hat.

Tests: drei neue Dateien (47 Tests); an `tests/test_obs030_config.py` ein
Pfadliteral, begründet in `PATH_BOUNDARIES.md`.

**Kein normatives Dokument wird durch diesen Run verändert.**

## Entscheidungen

| Befund | Entscheidung | Normbezug |
|---|---|---|
| W-1 | FIXED | `ARCH §8.3` (Reaktionen abschließend), `O-05`, `CONTRACTS §11.1` |
| W-2 | FIXED | `CONTRACTS §12.4`, `§5.6`, `FD-D8` |
| W-3 | NOT A DEFECT, Lücke benannt | `ARCH §7.3` eingefroren, keine Normzeile verlangt Zählen |
| W-4 | FIXED | `ARCH §8.3` wörtlich |
| W-5 | FIXED | `ARCH §8.3` (eingefrorene Zustandsmenge), `CONTRACTS §11.2` |
| W-6 | DEFERRED → OBS-050 | `CONTRACTS §5.8`, `§10.3`, `§9.2`, `ARCH §4.1`/`§5.1` |
| W-7a/b/c | FIXED | `CONTRACTS §5.2`, `§5.6`, `ARCH §8.3` |

Ausdrücklich **keine** Entscheidung getroffen wurde zur Auslegung von
`ARCH §8.3` „nur verwerfen und zählen" (siehe unten). Der Korrekturlauf hatte
sie faktisch getroffen; der Cleanup hat das zurückgenommen.

## Offene Entscheidungen

1. **Auslegung `ARCH §8.3` „nur verwerfen und zählen"** — eigener Zähler für
   nach `FAILED_WORKER` abgewiesene Submits, oder genügt die eingefrorene
   Zählersemantik samt Behandlung der Queue-Reste? Vollständig in
   `40_EVIDENCE/OBS-030/RUN-02_2026-08-17/DECISION_REQUIRED.md`; `dropped_failed`
   ist **nicht** Bestandteil des finalen Stands.
2. **W-3** — dieselbe Frage aus der Store-Perspektive; gemeinsam entscheidbar.
3. **W-6** — Auflage für OBS-050 (`clear_history()` nicht aus dem
   Qt-Mainthread, `O-03`).
4. **Ablageort von `LOGGING_V1_CHECKLISTE.md`** — kanonischer Pfad
   wiederhergestellt, leere Zweitfassung im nicht versionierten
   V2-Verzeichnis; ein bewusster Umzug ist eine Entscheidung für Marco.
5. **Nachträgliche Korrekturvermerke in der RUN-01-Evidence** — durch die
   Auftragszeile B-2 gedeckt, durch kein Freeze-Dokument geregelt; laut
   Cleanup-Auftrag unverändert gelassen und dem Gate vorgelegt.

## Tests / Evidence

`40_EVIDENCE/OBS-030/RUN-02_2026-08-17/TEST_RESULTS.md` (inkl. Abschnitt 8:
Cleanup-Verifikation). Kurzfassung nach dem Cleanup:

```text
-k obs030                       129 passed (pytest) / Ran 129 OK (unittest)
obs010+020+030                  331 passed
volle Client-Suite              1 failed, 843 passed, 351 subtests
unittest discover               Ran 844, FAILED (errors=1)
Fault-Injection                 6 passed
test_core_bridge (3x)           je 7 passed
git diff --check                leer, Exit 0
```

Weitere Evidence: `GATE_FINDINGS.md`, `FAULT_INJECTION.md`,
`PATH_BOUNDARIES.md`, `CONTRACT_COVERAGE.md`, `DIFF_SUMMARY.md`,
`DECISION_REQUIRED.md`, `probe_obs030_gate_fixes.py`.

## Blocker

Keine. Der eine Testfehlschlag (`lefx.interfaces` in
`tests/test_ap06_followup.py`) ist vorbestehend, umgebungsbedingt und
nachweislich außerhalb des Diffs; `core/led_controller.py` und diese
Testdatei erscheinen in keinem `git status`-Eintrag dieses Stands.

## Risiken und Grenzen

- `probe_write()` erkennt gesperrte, nur lesbare und geschlossene
  Datenbanken; ein reiner `disk full`-Zustand ist über eine leere
  Transaktion nicht in jedem Fall erzwingbar. Dafür greift der unveränderte
  `disk full`-Pfad aus `ARCH §8.3`.
- Der Schwellenwert „fünf aufeinanderfolgende Schleifenfehler" ist nicht
  normativ vorgegeben; `ARCH §8.3` sagt nur „ein Worker, der zweimal stirbt,
  stirbt beim dritten Mal auch". Fünf ist eine dokumentierte Wahl in
  Anlehnung an `STORE_FAILURE_THRESHOLD`.
- Die P-8-Prüfung akzeptiert neben `%USERPROFILE%` auch `$HOME`/`Path.home()`
  und `DEFAULT_LOCAL_APP_DIR`; unter Windows deckungsgleich, hält die
  Testsuite auf anderen Plattformen lauffähig.
- Die vom Gate benannte `test_core_bridge`-Flakiness bleibt bestehen; sie
  liegt außerhalb dieses Workstreams.

## Gate-Empfehlung

**Kein Gate-PASS durch diesen Run.** Ein Korrekturlauf vergibt sein eigenes
Gate nicht; `OBS-030 – Gate Review` bleibt in `LOGGING_V1_CHECKLISTE.md`
unabgehakt.

Empfehlung an den unabhängigen Review: Prüfung gegen den Repositoryzustand,
`git diff`/`git status` und eigenständige Testläufe — nicht gegen diesen
Bericht. Besonders zu prüfen sind die fünf offenen Entscheidungen oben,
allen voran die Auslegung von `ARCH §8.3`.

Abschlussstatus dieses Runs:
`OBS-030 CLEANUP COMPLETED – READY FOR INDEPENDENT RE-REVIEW`.

## Nächster Schritt

Erneuter unabhängiger OBS-030 Gate-Review in frischer Session
(`Prompts/OBS-030_GATE_REVIEW.md` bzw. `OBS-030_GATE_REVIEW_II.md`).
Kein Commit vor einem Gate-`PASS`. **OBS-040 darf nicht beginnen.**
