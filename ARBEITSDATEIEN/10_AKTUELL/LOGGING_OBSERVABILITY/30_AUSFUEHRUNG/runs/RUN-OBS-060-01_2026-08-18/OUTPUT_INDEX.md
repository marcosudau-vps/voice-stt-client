# OUTPUT_INDEX – RUN-OBS-060-01_2026-08-18

Alle Artefakte dieses Laufs, nach Ablageort.

---

## 1. Run-Ordner

`30_AUSFUEHRUNG/runs/RUN-OBS-060-01_2026-08-18/`

| Datei | Inhalt |
|---|---|
| `RUN_LOG.md` | Verlauf, Diagnosen, Entscheidungen mit Norm-Bezug, Zwischenfälle |
| `RESULT.md` | Ergebnis, die drei Befunde, Zahlen, was aussteht |
| `RUN_REPORT.md` | Pflichtgliederung nach der Themen-`AGENTS.md` |
| `OUTPUT_INDEX.md` | diese Datei |

## 2. Evidence

`40_EVIDENCE/OBS-060/RUN-01_2026-08-18/`

### 2.1 Die sieben geforderten V1-Dokumente

| Datei | Inhalt |
|---|---|
| `V1_TEST_RESULTS.md` | Teststand beider Runner, der eine vorbestehende Fehlschlag, die 27 neuen Tests, der Umgebungsbefund |
| `V1_REQUIREMENTS_TRACEABILITY.md` | achtzehn Final-Gate-Kriterien → Nachweis; Scope, R-1…R-7, acht Mutationen, O-01…O-14, M-1…M-11 |
| `V1_FAILURE_INJECTION.md` | zehn Fehlerfälle, je vorher/nachher wo relevant |
| `V1_PERFORMANCE.md` | ARCH §6.3 wörtlich, Durchsatz, Hot Path, Abfragelatenz, Retention |
| `V1_PRIVACY_REDACTION.md` | Secrets, Transcript-Policy, Audio, Pfade, 64-KiB-Grenze, M-11-Rechteprotokoll |
| `V1_REGRESSION.md` | Protokollvergleich, Regression gegen Suite und frühere Pakete, Packaging |
| `V1_OPEN_POINTS.md` | B-1…B-3, alle übernommenen N-Beobachtungen, O-1…O-13 |

Dazu `DIFF_SUMMARY.md` – der vollständige Diff, Änderung für Änderung begründet.

### 2.2 Probeskripte

Zählungen aus den Rohausgaben ausgezählt; alle sieben melden exit 0.

| Datei | Prüfgegenstand | PASS/FAIL/OPEN |
|---|---|---|
| `probe_obs060_e2e_chain.py` | Canonical Model → Ingress → Queue → Worker → SQLite → Query → UI | 24 / 0 / 0 |
| `probe_obs060_failure_injection.py` | die zehn Fehlerfälle der Testmatrix | 48 / 0 / 1 |
| `probe_obs060_runtime_isolation.py` | R-1…R-7 als Protokollvergleich | 10 / 0 / 0 |
| `probe_obs060_performance.py` | ARCH §6.3 und die Benchmarks aus Plan §13 | 14 / 0 / 0 |
| `probe_obs060_privacy.py` | Redaction, Transcripts, Audio, Pfade, Rechte | 24 / 0 / 0 |
| `probe_obs060_mutation_checks.py` | die acht Mutationen (plus Vorlauf und sechs Wiederherstellungsprüfungen) | 15 / 0 / 0 |
| `probe_obs060_packaging.py` | Importgraph, Versionierbarkeit, Spec | 7 / 0 / 0 |
| **Summe** | | **142 / 0 / 1** |

Das eine `OPEN` ist F-7.4 — der bewusst nicht reparierte offene Punkt **O-1**,
kein Fehlschlag.

| Datei | Inhalt |
|---|---|
| `probe_obs060_b1_reproduction.py` | die gezielte Reproduktion von B-1 **vor** der Korrektur |

### 2.3 Rohausgaben

`output/probe_obs060_*.out.txt` – die vollständige Konsolenausgabe jeder Probe,
im Endzustand des Laufs erzeugt.

`failure_injection_BEFORE_FIX.txt` – die Failure-Injection-Matrix **vor** den
Korrekturen, mit den sechs Fehlschlägen, die zu B-1 und B-2 geführt haben.

## 3. Produktcode

| Datei | Änderung |
|---|---|
| `core/observability/worker.py` | `_resume_store_if_due()` (B-1); Reset des Schleifenbudgets (OBS-030 N-2) |
| `core/observability/manager.py` | drei eigene Guards in `_on_config_applied`; Sink nur bei geänderter Konfiguration neu bauen (OBS-050 N-1/N-2) |
| `core/observability/ingress.py` | `malformed++` für ein `None` des Client-Normalizers (B-2) |
| `core/observability/query/local.py` | `complete` nur bei echter Kürzung `False` (OBS-050 N-4) |
| `app.py` | `try/finally` um den gesamten Ablauf (OBS-030 N-3) |
| `core/audio_capture.py` | Kommentar richtiggestellt, kein Code (OBS-040 N-4) |

## 4. Tests

`tests/test_obs060_v1_hardening.py` – 27 Tests in acht Klassen: Regression auf
B-1, B-2, B-3 und die vier geschlossenen N-Beobachtungen, dazu die Anker, an
denen die Mutationschecks messen.

## 5. Steuerung

| Datei | Änderung |
|---|---|
| `00_STEUERUNG/CURRENT_STATE.md` | OBS-060-Abschnitt und nächster Schritt |
| `00_STEUERUNG/LOG_VERLAUF.md` | genau ein Meilensteineintrag, append-only |
| `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` | OBS-060-Implementierung abgehakt, `Aktuell` fortgeschrieben |

## 6. Nicht versioniert, bewusst

Der Umgebungs-Shim (`sitecustomize.py`), der die blockierende WMI-Sonde
neutralisiert, liegt **außerhalb** des Projektbaums und ist kein Artefakt dieses
Laufs. Begründung und Kommandozeile stehen in `V1_TEST_RESULTS.md` Abschnitt 5,
der offene organisatorische Punkt in `V1_OPEN_POINTS.md` unter O-13.

Ebenfalls unberührt: die acht bewusst unversionierten Prompt- und
Pipeline-Einträge unter `30_AUSFUEHRUNG/`.
