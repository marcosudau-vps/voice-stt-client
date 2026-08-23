# RUN_REPORT – RUN-OBS-060-01_2026-08-18

Pflichtgliederung nach `10_AKTUELL/LOGGING_OBSERVABILITY/AGENTS.md`.

---

## Run-ID

`RUN-OBS-060-01_2026-08-18`

## Work Package

**OBS-060 – V1 Hardening, Evidence & Baseline**
(`20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-060_V1_HARDENING_EVIDENCE_BASELINE.md`,
Plan §13, Auftrag `30_AUSFUEHRUNG/Prompts/OBS-060_IMPLEMENTIERUNGSAUFTRAG.md`)

## Ausgangszustand

Branch `feat/einheitliche-triggerarchitektur`, HEAD `7fc6ca6`
(„feat(observability): complete OBS-050 local log view"). OBS-050 ist mit
unabhängigem Gate `PASS` abgeschlossen und lokal committet; `CURRENT_STATE.md`
weist `OBS-050 GATE PASS – OBS-060 MAY PROCEED` aus.

Der Arbeitsbaum trug vor Beginn zwei uncommittete, laufsfremde Dateien des
Triggerarchitektur-Workstreams sowie die acht bewusst unversionierten
Prompt-/Pipeline-Einträge. Beides blieb unberührt.

Testbaseline auf diesem Stand: **1137 passed / 1 vorbestehender Fehlschlag**.

## Durchgeführte Arbeiten

1. **Umgebungsblocker diagnostiziert und umgangen, ohne das Projekt zu ändern.**
   `platform._wmi_query` antwortet auf dieser Maschine nicht; `sounddevice` ruft
   es beim Import, also hängt jeder Lauf, der `core.controller` importiert.
   Ursache per `faulthandler`-Stackdump belegt. Ein `sitecustomize.py`
   **außerhalb** des Projektbaums stellt das von CPython selbst vorgesehene
   Verhalten her.
2. **Sieben Probeskripte** gebaut und gefahren: Ende-zu-Ende-Kette,
   Failure-Injection-Matrix, Runtime-Isolation R-1…R-7, Performance,
   Privacy/Redaction, acht Mutationschecks, Packaging.
3. **Drei Befunde** gefunden, vor jeder Korrektur reproduziert, behoben und mit
   Regressionstests versehen: B-1 (unerreichbare Store-Erholung), B-2
   (ungezähltes `None` des Client-Normalizers), B-3 (fehlender Wächter für
   Mutation M-6).
4. **Sechs übernommene Gate-Beobachtungen** geschlossen: OBS-030 N-2/N-3,
   OBS-040 N-4, OBS-050 N-1/N-2/N-4.
5. **27 neue Tests** in `tests/test_obs060_v1_hardening.py`.
6. **Sieben `V1_*.md`-Evidencedokumente** plus `DIFF_SUMMARY.md` und die
   Rohausgaben aller Proben.
7. Steuerungsdateien und Fortschrittscheckliste aktualisiert.

## Erzeugte/geänderte Dateien

**Produktcode (6 Dateien, +131/−13):** `core/observability/worker.py`,
`core/observability/manager.py`, `core/observability/ingress.py`,
`core/observability/query/local.py`, `app.py`, `core/audio_capture.py`
(nur Kommentar). Einzelbegründung je Datei in
`40_EVIDENCE/OBS-060/RUN-01_2026-08-18/DIFF_SUMMARY.md`.

**Tests (neu):** `tests/test_obs060_v1_hardening.py`.

**Run:** `RUN_LOG.md`, `RESULT.md`, `RUN_REPORT.md`, `OUTPUT_INDEX.md`.

**Evidence:** `V1_TEST_RESULTS.md`, `V1_REQUIREMENTS_TRACEABILITY.md`,
`V1_FAILURE_INJECTION.md`, `V1_PERFORMANCE.md`, `V1_PRIVACY_REDACTION.md`,
`V1_REGRESSION.md`, `V1_OPEN_POINTS.md`, `DIFF_SUMMARY.md`, sieben
`probe_obs060_*.py`, `failure_injection_BEFORE_FIX.txt`, `output/` mit den
Rohausgaben.

**Steuerung:** `00_STEUERUNG/CURRENT_STATE.md`,
`00_STEUERUNG/LOG_VERLAUF.md` (append-only),
`30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md`.

**Nicht verändert:** `00_NORMATIV/` (byte-identisch zu `7fc6ca6`),
`20_PLANUNG/`, jeder bestehende Test, `voice-stt-client.spec`, Server- und
LED-Workspace.

## Entscheidungen

Neun, alle aus dem bestehenden Freeze auflösbar; die Tabelle mit Norm-Bezug
steht in `RUN_LOG.md` Abschnitt 3. **Kein neuer Zähler, kein neuer Recordtyp,
kein neues Konfigfeld, kein neuer Health-Zustand, keine geänderte Signatur einer
eingefrorenen Funktion, kein `DECISION REQUIRED` in einem normativen Dokument.**

## Offene Entscheidungen

Dreizehn, vollständig in
`40_EVIDENCE/OBS-060/RUN-01_2026-08-18/V1_OPEN_POINTS.md`. Sieben davon (O-1,
O-2, O-7, O-8, O-10, O-11, O-13) brauchen eine Entscheidung der unabhängigen
Instanz; keine Implementierung dieses Laufs nimmt eine davon vorweg.

Hervorzuheben:

- **O-1** – ein Ersatzrecord `logging.record_rejected` für eine vom Normalizer
  selbst verschluckte Ausnahme bräuchte den Ausnahmetyp und damit eine
  Signaturänderung an einer in `CONTRACTS §3` eingefrorenen Funktion. Der
  Kernbefund B-2 ist ohne diese Erweiterung vollständig behoben, also ist sie
  kein Blocker und wurde nicht mitgeliefert.
- **O-2** – die Begründungsspalte der Mutationstabelle trifft für M-6 sachlich
  nicht zu (SQLite behandelt `NULL` in UNIQUE-Indizes stets als verschieden).
  Planerische Dokumente ändert ein Implementierungslauf nicht.

## Tests/Evidence

| Lauf | Ergebnis |
|---|---|
| `pytest tests -q -k obs060` | 27 passed, exit 0 |
| `unittest discover -p "test_obs060_*.py"` | Ran 27, OK |
| `pytest tests -q -k "obs010 … obs060"` | 652 passed, exit 0 |
| volle Suite `pytest` | **1164 passed / 1 failed** (vorbestehend) |
| volle Suite `unittest` | Ran 1165, 1 error (derselbe) |
| `git diff --check` | leer, exit 0 |
| sieben Probeskripte | alle exit 0 |

Details: `40_EVIDENCE/OBS-060/RUN-01_2026-08-18/V1_TEST_RESULTS.md`.

## Blocker

**Keine.**

Ausdrücklich als **nicht erledigt** ausgewiesen — und damit nicht als Blocker
dieses Laufs, sondern als benannte Lücke der V1-Abnahme: die **manuelle Abnahme
M-1…M-11 am realen Produktionspfad**. Neun der elf Punkte sind gegen den echten
Stack automatisiert belegt und M-11 ist protokolliert; der Durchlauf auf einem
Installationssystem mit laufendem Server, mit Datum, Serveradresse und
Clientversion, steht aus. `WP-OBS-060` erklärt ihn zur Pflicht.

## Gate-Empfehlung

`OBS-060 IMPLEMENTED – READY FOR V1 GATE`.

Kein Gate-PASS in diesem Lauf — ein Implementierungslauf vergibt sein eigenes
Gate nicht. Der lokale Abschlusscommit entsteht erst nach dem unabhängigen
V1-Gate und nur bei `PASS`.

## Nächster Schritt

**OBS-060 – Logging V1 Final Gate Review**, unabhängig, in frischer Session
(`30_AUSFUEHRUNG/Prompts/OBS-060_V1_GATE_REVIEW.md`). Der Review prüft nicht nur
den OBS-060-Diff, sondern die vollständige V1-Kette OBS-010 bis OBS-060 gegen
die achtzehn Final-Gate-Kriterien; die Abbildung Kriterium → Nachweis liegt in
`V1_REQUIREMENTS_TRACEABILITY.md` Abschnitt 1 bereit.
