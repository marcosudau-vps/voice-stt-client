# RESULT.md – OBS-010 RUN-01 (DeepSeek)

Run-ID: `RUN-OBS-010-01_2026-08-17_DEEPSEEK`
Work Package: `OBS-010 – Canonical Model, Redaction, Normalizer & Contracts`
Status: **Implementierung abgeschlossen – Review/Gate ausstehend**

## Ergebnis in Kürze

OBS-010 ist vollständig im freigegebenen Scope umgesetzt. Es entstehen
ausschließlich neue Dateien:

- Paket `core/observability/` mit `models.py`, `redaction.py`, `normalizer.py`,
  `ingress.py` (Protokoll), `storage/base.py`, `sinks/base.py`,
  `query/base.py` (Protokolle/Contract-Typen) und Paket-`__init__`-Dateien.
- Tests `tests/test_obs010_{models,redaction,normalizer_python,
  normalizer_server,normalizer_client,query_contracts,contracts}.py`
  (127 Tests).
- Evidence + Run-Dokumentation unter ARBEITSDATEIEN.

## Wesentliche Vertrags-/Fachentscheidungen (innerhalb Freeze)

1. `__init__.py`-Re-Exports additiv (Endstand ARCH §5.1 folgt in OBS-020/030).
2. `from_log_record`: Signatur getreu, Werte ausschließlich aus
   `record.__dict__` (CONTRACTS §3.1 / FD-R8).
3. Server-`raw` wird MAPPED (eingefrorene Referenz, keine Kopie; ARCH §8.2);
   `details` werden redigiert; `store_raw_payload=False`/`channel=performance`
   → `raw=None`; `unfreeze`/`redact_mapping` sind für den Worker (OBS-030)
   bereit.
4. `hello`-Whitelist nach R-6; `accessToken` auf keiner Ebene.
5. `redact_text` erkennt nur die benannten realen Transkript-Logzeilen (N-02),
   keine Werteheuristik (R-3).
6. Truncation-Marker `{"_truncated": True, "_reason": ...}` für R-12
   (im Vertrag nicht vorgegeben; kleinste Abweichung, analog FD-C12).
7. Duplicate-Events werden als CONTROL gemappt (§3.2 / W-9).
8. Strikter Datenmodell-Gültigkeitscheck („Verwerfen statt Reparieren"):
   ungültige Felder → None durch den Normalizer, kein stilles Coercing.

## Tests

- Neue OBS-010-Tests: **127 passed** (pytest) / **127 OK** (unittest).
- Vollständige Suite: **640 passed / OK** (513 Baseline + 127 neue);
  kein bestehender Test geändert.
- Mutationschecks MT-1 (Redaction entfernen → rot) und MT-2 (`unfreeze`
  entfernen → N-01 rot) ausgeführt und bestätigt, danach zurückgesetzt.
- Diagnose-Skript (reale `hello`-Struktur): Exit 0, Token verschwinden.

## Evidence

`40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/`:
`TEST_RESULTS.md`, `DIFF_SUMMARY.md`, `CONTRACT_COVERAGE.md`,
`OBS-010_RUN-01_hello_redaction_diagnose.py`.

## Abschlussprüfung

- `git diff --check` → leer (Exit 0).
- `git status --short` → nur untracked; keine ` M`/` D`.
- `git diff --stat` → leer (nur neue Dateien, daher kein tracked Diff).
- Nur OBS-010-Scope verändert (Produkt-/Testbaum); Evidence/Tracking unter
  ARBEITSDATEIEN.
- kein Commit, kein Push, keine Änderungen an Server-/LED-Repo.

## Offene Punkte

- Gate-Review (frischer Run) ausstehend: `30_AUSFUEHRUNG/Prompts/
  OBS-010_GATE_REVIEW.md` (extern vorinstalliert).
- Keine fachlichen Blocker. Externe, vorinstallierte Prompt-Pipeline-Dateien
  (OBS-020 ff.) wurden nicht angefasst.

## Gate-Empfehlung

`OBS-010 IMPLEMENTED – READY FOR CLAUDE GATE REVIEW`