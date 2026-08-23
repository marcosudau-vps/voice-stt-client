# OBS-060 – V1_TEST_RESULTS

Run: `RUN-OBS-060-01_2026-08-18`
Ausgangscommit: `7fc6ca6` („feat(observability): complete OBS-050 local log view")
Umgebung: Windows 11 Pro 10.0.26200, Python 3.12.10, PySide6 offscreen
Kein Commit in diesem Lauf.

---

## 1. Teststand

| Lauf | Kommando | Ergebnis |
|---|---|---|
| Neue OBS-060-Tests (`pytest`) | `python -m pytest tests -q -k obs060` | **27 passed**, 1138 deselected, 3 subtests, exit 0 |
| Neue OBS-060-Tests (`unittest`) | `python -m unittest discover -s tests -p "test_obs060_*.py"` | **Ran 27 … OK**, exit 0 |
| Gesamte V1-Kette | `python -m pytest tests -q -k "obs010 or obs020 or obs030 or obs040 or obs050 or obs060"` | **652 passed**, 623 subtests, exit 0 |
| Volle Suite (`pytest`) | `python -m pytest tests -q` | **1164 passed / 1 failed**, 862 subtests, 80.9 s |
| Volle Suite (`unittest`) | `python -m unittest discover -s tests -p "test_*.py"` | **Ran 1165**, `FAILED (errors=1)`, 77.7 s |
| `git diff --check` | `git diff --check` | leer, exit 0 |

Vor diesem Lauf (gemessen auf `7fc6ca6`, unveränderter Baum): **1137 passed / 1
failed**. Die Differenz ist **exakt** die 27 neuen Tests in
`tests/test_obs060_v1_hardening.py`. **Kein bestehender Test wurde geändert.**

## 2. Der eine Fehlschlag

`tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`
scheitert mit `ModuleNotFoundError: No module named 'lefx.interfaces'`
(`core/led_controller.py:310`).

Er ist **vorbestehend und umgebungsbedingt**, nicht durch diesen Lauf
verursacht:

- Er tritt in derselben Form schon in der Baseline auf, die vor der ersten
  Änderung dieses Laufs gemessen wurde (1137 passed / 1 identischer Fehlschlag).
- Weder `tests/test_ap06_followup.py` noch `core/led_controller.py` liegen im
  Diff dieses Laufs (`git status --short` nennt beide nicht).
- Dieselbe Einordnung tragen bereits die Gates von OBS-020 bis OBS-050.

## 3. Die neuen Tests

`tests/test_obs060_v1_hardening.py`, 27 Tests in acht Klassen. Sie zerfallen in
zwei Gruppen: Regressionstests für die drei in diesem Lauf geschlossenen Befunde
und Anker, an denen die Mutationschecks messen.

### 3.1 Regression auf die Befunde dieses Laufs

| Klasse | Tests | sichert |
|---|---|---|
| `TestStoreRecoveryIsReachable` | 4 | **B-1**: ein ausgesetzter Store erholt sich ohne neuen Batch, die Erholung kostet eine Probe statt eines Batches, ein weiterhin defekter Store bleibt ausgesetzt und wird erneut geprüft, und genau **ein** `logging.recovered` dokumentiert die Rückkehr |
| `TestNormalizerNoneIsCounted` | 5 | **B-2**: ein Clientevent, an dem der Normalizer scheitert, wird als `malformed` gezählt; Health bleibt `OK`; kein Record wird eingereiht; ein gesundes Event wird **nicht** gezählt; der Serverpfad behält `None` als stille Entscheidung |
| `TestLoopFailureBudget` | 2 | **OBS-030 N-2**: die beiden Startupguards verbrauchen das Fehlerbudget der Schleife nicht mehr, bleiben aber sichtbar (`FAILED_STORE`, `retention_errors`) |
| `TestProviderCompleteFlag` | 3 | **OBS-050 N-4**: `complete` ist nur dann `False`, wenn wirklich abgeschnitten wurde |
| `TestSinkIsNotRebuiltWithoutReason` | 3 | **OBS-050 N-1/N-2**: unveränderte Sinkkonfiguration ⇒ dasselbe Objekt; geänderte ⇒ ein neues; ein werfender Sinkbau verschluckt die `enabled`-Änderung nicht mehr |

### 3.2 Anker für die Mutationschecks

| Klasse | Tests | Anker für |
|---|---|---|
| `TestNonBlockingInvariantAnchor` | 5 | M-3 (`put_nowait`), M-4 (Wasserstandsregel), M-8 (`PRAGMA query_only`), M-1 (`ON CONFLICT DO NOTHING`) |
| `TestFrozenDdlIsPartial` | 2 | M-6 (partieller UNIQUE-Index) |
| `TestTranscriptPolicyAnchor` | 2 | M-7 (Handlerlevel) |
| `TestInternalRecordsStayHigh` | 1 | `logging.record_rejected` bleibt `HIGH` und trägt keine Originaldaten |

## 4. Die Probeskripte dieses Laufs

Alle liegen neben dieser Datei; ihre vollständige Ausgabe steht unter
`output/`. Jedes meldet exit 0.

Die Zählungen unten sind aus den Rohausgaben ausgezählt
(`grep -c "^\[PASS\]"` bzw. `"^\[FAIL\]"`, `"^\[OPEN\]"`).

| Skript | Prüfgegenstand | PASS | FAIL | OPEN |
|---|---|---|---|---|
| `probe_obs060_e2e_chain.py` | Canonical Model → Ingress → Queue → Worker → SQLite → Query → UI | **24** | 0 | 0 |
| `probe_obs060_failure_injection.py` | die zehn Fehlerfälle der Testmatrix | **48** | 0 | 1 |
| `probe_obs060_runtime_isolation.py` | R-1 … R-7, Protokollvergleich | **10** | 0 | 0 |
| `probe_obs060_performance.py` | ARCH §6.3 und die Benchmarks aus Plan §13 | **14** | 0 | 0 |
| `probe_obs060_privacy.py` | Redaction, Transcript-Policy, Audio, Pfade, 64-KiB-Grenze, M-11 | **24** | 0 | 0 |
| `probe_obs060_mutation_checks.py` | die acht Mutationen | **15** | 0 | 0 |
| `probe_obs060_packaging.py` | Erreichbarkeit im Importgraph, Versionierbarkeit, Packagingkonfiguration | **7** | 0 | 0 |
| **Summe** | | **142** | **0** | **1** |

Alle sieben melden exit 0.

Zur Lesart einzelner Zahlen:

- `probe_obs060_mutation_checks.py`: die 15 setzen sich zusammen aus einem
  Vorlauf („alle betroffenen Auswahlen laufen unmutiert grün"), den **acht**
  Mutationen und den **sechs** Wiederherstellungsprüfungen per SHA-256.
- `probe_obs060_failure_injection.py`: das eine `OPEN` ist F-7.4, der bewusst
  nicht reparierte offene Punkt **O-1** — es ist kein Fehlschlag und wird
  ausdrücklich als offener Punkt ausgewiesen.
- `probe_obs060_runtime_isolation.py`: die 10 sind die sechs
  Protokollvergleiche R-2…R-7 plus vier Zusatzprüfungen (der werfende
  Beobachter wurde wirklich gerufen; Cursordatei und Resume-Cursor stimmen mit
  R-1 überein; R-2 hat wirklich etwas aufgezeichnet).

Zusätzlich:

| Datei | Inhalt |
|---|---|
| `probe_obs060_b1_reproduction.py` | die gezielte Reproduktion von B-1 **vor** der Korrektur |
| `failure_injection_BEFORE_FIX.txt` | die Failure-Injection-Matrix vor den Korrekturen, mit den sechs Fehlschlägen, die zu B-1 und B-2 geführt haben |

## 5. Die Testumgebung – ein reproduzierbarkeitsrelevanter Befund

Auf dieser Maschine blockiert `platform._wmi_query` (Python 3.12, Windows)
unbegrenzt: der WMI-Dienst antwortet nicht. `sounddevice` ruft beim **Import**
`platform.system()`/`win32_ver()`, also hängt jeder Testlauf, der
`core.audio_capture` — und damit `core.controller` — importiert. Der erste
Versuch, die volle Suite zu fahren, stand nach zwölf Minuten bei 1,67 s CPU-Zeit;
der Stacktrace (`faulthandler`) zeigt die Blockade in
`platform.py:327 _wmi_query`.

**Das ist keine Eigenschaft des Produkts, sondern der Maschine** — und das
Projekt kennt sie bereits: `voice-stt-client.spec` installiert für den
gefrorenen Build einen Runtime-Hook `scripts/pyinstaller_runtime_platform.py`
mit genau derselben Begründung („Python's Windows platform probes reach for WMI,
which is slow on the first call and can be far worse on a managed machine").
Der ausgelieferte Client ist also nicht betroffen.

Für die Testläufe dieses Runs wurde deshalb **außerhalb des Projektbaums** ein
`sitecustomize.py` auf den `PYTHONPATH` gelegt, das `platform._wmi_query` einen
`OSError` werfen lässt — genau der Fall, den CPython selbst als „WMI nicht
verfügbar" behandelt und über die Registry auffängt. **Keine Datei des Projekts
ist dafür angefasst worden.** Mit dem Shim braucht die volle Suite 80,9 s statt
unbegrenzt, und die Zahlen decken sich mit denen des OBS-050-Gates (dort 84,6 s
bei 1137 passed).

Vollständige Kommandozeile aller Läufe dieses Runs:

```text
QT_QPA_PLATFORM=offscreen PYTHONPATH=<shimdir> python -m pytest tests -q
```

`QT_QPA_PLATFORM=offscreen` ist dieselbe Einstellung, die schon die
OBS-050-Evidence nennt.

## 6. Git-Zustand am Ende

```text
$ git diff --check
(leer, exit 0)

$ git diff --stat
 app.py                              | 11 +++-
 core/audio_capture.py               |  8 ++-
 core/observability/ingress.py       | 10 ++++
 core/observability/manager.py       | 59 +++++++++++++++++++---
 core/observability/query/local.py   |  7 ++-
 core/observability/worker.py        | 38 ++++++++++++++
 (+ 2 vorbestehende, laufsfremde Dateien, siehe V1_OPEN_POINTS.md O-3)
```

Neu und unversioniert: `tests/test_obs060_v1_hardening.py` und
`40_EVIDENCE/OBS-060/`. **Kein Commit, kein Push, kein Merge, kein Rebase, kein
Tag, kein PR.**
