# CI_GREEN_REPORT — BS-003 CI Green Gate

## Baseline

- Start-HEAD (Arbeitsverzeichnis bei Run-Start): `47ea3cea4602eab9d5d28afdb72bf6b9deb87bb0`
- Finaler HEAD (gepusht, PR-HEAD, CI-geprüft): `7d4ac6a401245d8ef8afeca57d02d02d77583c44`
- PR: `#1 – feat(observability): establish pre-trigger logging baseline`
  (marcosudau-vps/voice-stt-client)
- Verwendeter Remote: `github` (origin unverändert, zeigt weiterhin auf
  lokalen Pfad `P:/GithubRepos/marcosudau-vps/voice-stt-client/main`)

## Ursache

Der GitHub-CI-Lauf für den Start-HEAD `47ea3ce` scheiterte deterministisch
mit drei `ERROR`-Fällen in
`tests.test_obs040_contracts.TestFrozenCounterSetIsUnchanged
.test_normative_documents_are_untouched_by_this_run`:

```
FileNotFoundError: [Errno 2] No such file or directory:
'...\ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\00_NORMATIV\LOGGING_ARCHITEKTUR_FREEZE_V1.md'
```

Analog für `LOGGING_CONTRACTS_FREEZE_V1.md` und `LOGGING_DECISIONS_FREEZE_V1.md`.

Ursache: `tests/test_obs040_contracts.py` las die drei eingefrorenen
Normativdokumente weiterhin unter dem alten Pfad
`ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/`. Dieser Pfad
existiert im Arbeitsbaum nicht mehr, weil Logging Teil A bewusst und
kontrolliert nach
`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/00_NORMATIV/`
archiviert wurde. Die drei Dokumente selbst liegen dort unverändert vor
(`status: FROZEN`, `OBS-040` erscheint nicht vor der ersten `# 1.`-Sektion).

Die frühere Klassifikation als „vorbestehender Fehler" war für einen
Main-Merge nicht ausreichend, weil ein PR, der diesen Testfehler nach main
mitnimmt, main selbst mit einer roten Testsuite belasten würde. Ein CI-Rot-
Zustand ist unabhängig von der Frage, wann der Fehler entstanden ist, kein
akzeptabler Mergezustand.

## Änderung

Exakt geänderte Datei: `tests/test_obs040_contracts.py`
(Commit `7d4ac6a` — `test(observability): follow archived normative
contract paths`)

Geänderte Methode:
`TestFrozenCounterSetIsUnchanged.test_normative_documents_are_untouched_by_this_run`

- Vorher: `normative = ROOT / "ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV"`
- Nachher: `normative = ROOT / "ARBEITSDATEIEN/90_HISTORIE" / "2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER" / "LOGGING_OBSERVABILITY/00_NORMATIV"`

Testinvariante vor/nach Änderung: unverändert. Der Test prüft weiterhin für
alle drei Dokumente `assertIn("status: FROZEN", text)` und
`assertNotIn("OBS-040", text.split("# 1.")[0])`. Nur die Pfadauflösung der
Dateien wurde auf den tatsächlichen, kontrollierten Archivpfad umgestellt;
die geprüften Inhalte/Schutzinvarianten sind identisch geblieben. Die drei
Normativdokumente selbst wurden nicht verändert. Es wurde keine
Produktcodeänderung vorgenommen.

Bestätigung: keine Tests wurden gelöscht, geskippt, mit
`@unittest.skip`/xfail versehen, oder in ihren Assertions abgeschwächt.
Kein `continue-on-error` wurde in der CI ergänzt.

## Lokale Tests

- Gezielter OBS-040-Test:
  `python -m unittest tests.test_obs040_contracts` → **OK** (16 Tests)
- Vollständige Suite:
  `python -m unittest discover -s tests -p "test_*.py"` →
  **Ran 1125 tests in 96.956s — OK** (0 failures, 0 errors)
- Compile: `python -m compileall -q app.py core ui scripts tests` →
  erfolgreich (keine Ausgabe/Fehler)
- Build: `python scripts/build.py --clean` → erfolgreich,
  `Built dist\voice-stt-client.exe (79060897 bytes)`,
  Version 0.2.0, SHA-256 `c73c717f4421cc3a67680cf9deb3a65552b2d1851b33b83cc7cb6c06c8a5e8f3`

## GitHub CI

Für den finalen PR-HEAD `7d4ac6a` wurde GitHub Actions Run
`32642707868` (Workflow „CI", Job „Test and build Windows executable")
ausgewertet.

**Erster Versuch (Job-ID 97202152841):** Der Test-Schritt brach nach
~49s ohne unittest-Abschlusszeile (kein `Ran N tests`, kein `OK`/`FAILED`)
mitten in der Suite ab (`Process completed with exit code 1` direkt nach
einer regulär geloggten, im Produktcode abgefangenen `TimeoutError` aus
einer UI-Testdouble). Lokal lief zum Vergleich die komplette Suite in
~97s sauber durch (1125/1125 OK). Das abrupte Abbrechen ohne jede
Python-Fehlermeldung wurde als eindeutiger transienter GitHub-Runner-
Fehler bewertet (kein deterministischer Test-/Codefehler, keine
Assertion, kein Traceback eines Fehlschlags). Gemäß Vorgabe wurde
genau ein Retry durchgeführt (`gh run rerun 32642707868 --failed`,
gleicher HEAD `7d4ac6a`, gleiche Run-ID).

**Retry (Job-ID 97202712996):** vollständig grün.

| Schritt | Ergebnis |
|---|---|
| Set up job | success |
| Enable Windows long paths | success |
| Check out repository | success |
| Set up Python 3.12 | success |
| Install dependencies | success |
| Run complete test suite | success — `Ran 1125 tests in 79.718s` / `OK` |
| Compile all Python modules | success |
| Build and smoke-test executable | success |
| Read version | success |
| Upload Windows executable | success |
| Post Set up Python 3.12 | success |
| Post Check out repository | success |
| Complete job | success |

- Finale Run-ID: `32642707868`
- Finaler Head-SHA: `7d4ac6a401245d8ef8afeca57d02d02d77583c44`
- Gesamtstatus: `completed` / `success`
- Kein Schritt war `skipped`.

## PR

- PR-Beschreibung wurde aktualisiert auf: 1125 Tests total, 1125
  erfolgreich, 0 Fehler (vorher: 1122/1125, 3 bekannte Fehler).
- PR #1 ist weiterhin `state: OPEN`, `mergeable: MERGEABLE`.
- PR #1 ist nicht gemerged.

## Schlussurteil

`READY TO MERGE PR INTO MAIN`
