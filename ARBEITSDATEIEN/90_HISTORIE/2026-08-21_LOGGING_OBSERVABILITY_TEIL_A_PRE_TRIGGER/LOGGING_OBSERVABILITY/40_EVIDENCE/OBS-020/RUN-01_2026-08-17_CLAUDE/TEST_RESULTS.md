# TEST_RESULTS – OBS-020 RUN-01 (Claude)

Datum: 2026-08-17
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Interpreter: `voice-stt-client/main/venv/Scripts/python.exe` (Python 3.12.13)
CWD für alle Läufe: der Client-Workspace

## Befehle und Ergebnisse

### 1. Baseline vor Änderungen (nach OBS-010)

```text
$ python -m pytest -q
640 passed in 27.62s
```

### 2. Neue OBS-020-Tests (nur neue Dateien)

```text
$ python -m pytest -q -k obs020
75 passed, 640 deselected in 5.94s

$ python -m unittest discover -s tests -p "test_obs020_*.py"
Ran 75 tests in 5.16s
OK
```

Aufteilung der 75 neuen Tests:

| Datei | Tests | Fokus |
|---|---|---|
| `test_obs020_health.py` | 16 | Health-Zustände/-Snapshot, Zähler, Rate-Limiter, `sys.stderr`-Abwehr, `propagate` |
| `test_obs020_ingress.py` | 19 | `submit`-Reihenfolge, Wasserstand/N-04, Queue-voll, `NullIngress`, Nebenläufigkeit, Zeitbasislinie |
| `test_obs020_python_logging_handler.py` | 15 | Positiv/Negativ/Failure, Rekursionssperre, `flush`/`close`, interner Filter |
| `test_obs020_logging_setup_integration.py` | 5 | Rückwärtskompatibilität, `client.log`-Gleichheit, dritter Handler, doppelter Aufruf |
| `test_obs020_contracts.py` | 11 | Isolation, azyklische Importe, Signaturen, `observability.internal` |
| `test_obs020_redaction_end_to_end.py` | 9 | Secrets, nicht-sensible Struktur, Audio-Payload-Abwehr, Transkript-Policy, keine Mutation |

### 3. Vollständige Client-Suite nach OBS-020

```text
$ python -m pytest -q
715 passed in 31.47s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 715 tests in 30.58s
OK
```

Kein bestehender Test wurde geändert; die bestehende Suite bleibt grün
(715 = 640 bestehende + 75 neue). Bestätigt über `git diff --name-only`: nur
`core/logging_setup.py` unter den Produktdateien geändert, keine
`tests/test_*.py`-Datei außerhalb der neuen `test_obs020_*` verändert.

### 4. Nebenläufigkeits-/Zeitmessungen (WP-OBS-020, als Regressionsbasis
      festgeschrieben)

```text
[OBS-020 timing baseline] 100000 submits at full queue: 1.5586s–1.8496s
                            (~15.6–18.5us/call, zwei unabhängige Läufe)
```

Gemessen in `TestConcurrencyAndTiming::test_100000_submits_against_a_full_queue_timing_baseline`
(`tests/test_obs020_ingress.py`). Bewusst **kein** absoluter Grenzwert im
Plan (ARCH §6.3) — dieser Wert ist der Ausgangspunkt für spätere
Regressionsvergleiche, keine Leistungszusage. Der Test selbst trägt nur
einen großzügigen Hänge-Schutz (`< 10s` für 100 000 Aufrufe).

Der 8-Threads-×-5000-Submits-Nebenläufigkeitstest
(`test_eight_threads_5000_submits_counts_reconcile_no_duplicates`) bestätigt:
`enqueued + dropped_watermark + dropped_queue_full == 40000` exakt, und kein
`record_id` erscheint doppelt unter den nach Testende noch in der Queue
verbliebenen Records.

### 5. `client.log`-Vorher/Nachher-Diagnose (Datei-Sink unverändert)

```text
$ python ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/OBS-020_RUN-01_client_log_before_after_diagnose.py
PASS  OLD vs NEW (no observability) client.log content identical
PASS  NEW (no observability) vs NEW (with observability) client.log content identical
Alle Erwartungen erfuellt. client.log ist im Format unveraendert.
EXIT=0
```

Methode: Die Fassung von `core/logging_setup.py` **vor** dieser Änderung wird
direkt aus `git show HEAD:core/logging_setup.py` in ein isoliertes Modul
geladen (der Arbeitsbaum bleibt unangetastet) und mit der neuen Fassung
verglichen — sowohl ohne als auch mit `observability`-Parameter. Beide
Vergleiche bestätigen: Der dritte Handler verändert das Datei-Sink-Format in
keinem Byte (`ts`-Feld und der laufabhängige Temp-Pfad im
"Logging initialized"-Text sind die einzigen erwartungsgemäß variablen
Anteile und werden vor dem Vergleich normalisiert).

Für die CI-Läufe gültige Kommandos (identisch zu den obigen):

- vollständige Suite: `python -m unittest discover -s tests -p "test_*.py"`
- neue Paket-Tests: `python -m unittest discover -s tests -p "test_obs020_*.py"`

## Prüfpflichten (WP-OBS-020)

- [x] Positive Tests
- [x] Negative Tests
- [x] Failure-/Edge-Tests
- [x] Nebenläufigkeitstests (8×5000, Zeitbasislinie 100 000 Submits)
- [x] Contract-Tests (`observability.internal` propagate, keine
      `event_models`/`feedback_reducer`-Importe in `health.py`, kein
      `PySide6`, azyklische Importe, `Ingress`-Signaturabgleich)
- [x] Die vollständige bestehende Client-Suite bleibt grün, ohne dass ein
      bestehender Test geändert wird
- [x] `git diff --check` → leer/Exit 0
- [x] `git diff` zeigt in `core/logging_setup.py` **keine** Änderung an
      einer bestehenden Zeile außer der notwendigen Signaturzeile (siehe
      DIFF_SUMMARY.md — der Sollzustand-Codeblock des Work Packages selbst
      zeigt genau diese eine geänderte Zeile)
- [x] kein unbeabsichtigter Cross-Workstream-Diff

## Beobachtete, nicht behobene Umgebungsauffälligkeit (außerhalb des Scopes)

Unter einer `cp1252`-Windows-Konsole erzeugt der bereits bestehende
Stdout-Handler (`ReadableFormatter`, Trennzeichen `│`) einen intern
abgefangenen `UnicodeEncodeError` beim Schreiben auf `sys.stdout`
("--- Logging error ---", kein Testfehlschlag, kein Absturz). Vorbestehendes
Verhalten, unabhängig vom `observability`-Parameter; im Diagnoseskript mit
`stdout=False` umgangen, damit die Format-Prüfung unbeeinflusst bleibt. Nicht
behoben (außerhalb WP-OBS-020-Scope: "keine fachfremden Produktänderungen").
