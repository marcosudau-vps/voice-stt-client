# TEST_RESULTS – OBS-010 RUN-01 (DeepSeek)

Datum: 2026-08-17
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
Interpreter: `voice-stt-client/main/venv/Scripts/python.exe` (Python 3.12.13)
CWD für alle Läufe: der Client-Workspace

## Befehle und Ergebnisse

### 1. Baseline vor Änderungen (Startzustand)

```text
$ python -m pytest -q
513 passed in 26.24s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 513 tests in 24.511s
OK
```

### 2. Neue OBS-010-Tests (nur neue Dateien, nur unittests)

```text
$ python -m pytest -q -k obs010
127 passed, 513 deselected in 2.42s

$ python -m unittest discover -s tests -p "test_obs010_*.py"
Ran 127 tests in 1.091s
OK
```

### 3. Vollständige Client-Suite nach OBS-010

```text
$ python -m pytest -q
640 passed in 27.03s

$ python -m unittest discover -s tests -p "test_*.py"
Ran 640 tests in ~25s
OK
```

Kein bestehender Test wurde geändert; die bestehende Suite bleibt grün
(640 = 513 bestehende + 127 neue). Alarmsignal laut WP-OBS-010 wäre eine
Änderung eines bestehenden Tests gewesen — nicht eingetreten.

### 4. Mutationschecks (WP-OBS-010, zwei zwingende)

| # | Mutation | erwartet rot | beobachtet | Status |
|---|----------|--------------|------------|--------|
| MT-1 | Redaction-Aufruf am Ende des Normalizer-Pfades entfernt (in `from_client_event`) | U-Redaction-Tests | `test_obs010_normalizer_client.py::TestClientEventMapping::test_message_and_details_are_redacted` FAILED (1 failed, 10 passed) | bestätigt |
| MT-2 | `unfreeze()` vor der Serialisierung entfernt (no-op gemacht) | N-01 u. a. | 5 Dämpfe rot: `TestUnfreezeN01::test_unfreeze_yields_json_object_without_frozen_reprs`, `test_frozenset_becomes_sorted_list`, `test_unfreeze_guards_throwing_repr`, `TestRedactBoundsR12::test_unfreeze_bounds_also_limit`, `tests/test_obs010_contracts.py::TestMutationGuards::test_unfreeze_is_required_before_serialization` | bestätigt |

Beide Mutationen wurden nach Verifikation vollständig zurückgesetzt
(Quelle danach wieder grün, 127/127).

### 5. Diagnose-Skript Evidence (reale `hello`-Struktur)

```text
$ python ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/OBS-010_RUN-01_hello_redaction_diagnose.py
PASS  redact_mapping(unfreeze(hello)) enthaelt accessToken nicht
PASS  Ergebnis ist ein JSON-Objekt (kein default=str-Kollaps)
PASS  MappingProxyType/tuple/frozenset-Reprs fehlen
PASS  from_server_result(log.hello) erzeugt einen Record
PASS  Der Record enthaelt den accessToken auf keiner Ebene
PASS  hello wird NIE raw gespeichert (R-6)
PASS  Whitelist-Felder sind erhalten (logAccess.available / serverInstanceId)
Alle Erwartungen erfuellt. accessToken ist in keinem Ergebnispfad.
EXIT=0
```

Für die CI-Läufe gültige Kommandos (identisch zu den obigen):

- vollständige Suite: `python -m unittest discover -s tests -p "test_*.py"`
- neue Paket-Tests: `python -m unittest discover -s tests -p "test_obs010_*.py"`

## Prüfpflichten (WP-OBS-010)

- [x] Positive Tests
- [x] Negative Tests
- [x] Failure-/Edge-Tests
- [x] Contract-Tests (Qt-Grenze, sqlite3-Grenze, Zyklenfreiheit, keine
      Runtime-Referenzen im Python-Logpfad)
- [x] Vollständige bestehende Suite grün, ohne Änderung eines bestehenden Tests
- [x] `git diff --check` → leer (Exit 0)
- [x] kein unbeabsichtigter Cross-Workstream-Diff (nur `core/observability/**`
      und `tests/test_obs010_*.py` im Produktbaum; Evidence-/Steuerungsdateien
      unter ARBEITSDATEIEN)

Mutationschecks MT-1/MT-2 (vorgezogen aus OBS-060) sind gemäß WP-OBS-010
durchgeführt und belegt (Abschnitt 4). Die übrigen sechs Mutationschecks
verbleiben bei OBS-060.

## Hinweis: externe, vorinstallierte Materialien

Unter `30_AUSFUEHRUNG/` liegen zusätzlich nicht committete Materialien
(`LOGGING_V1_CHECKLISTE.md`, `LOGGING_V1_PROMPT_PIPELINE_V2/`, `Prompts/*`),
die am 2026-08-17 02:00:02 durch ein externes Setup aus
`LOGGING_V1_PROMPT_PIPELINE_V2.zip` entpackt wurden. Sie sind **nicht** Teil
dieses Runs und wurden nicht verändert. Sie stehen für spätere
Work-Packages/Gate-Reviews bereit.