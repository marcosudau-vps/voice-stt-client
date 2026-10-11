# Build- und Release-Anleitung

Stand 2026-10-11, AP-CV2-000: aus V1 portierte Build-/Releaseguards. Keine V2-Veröffentlichung beauftragt. Kandidat und Tree zusätzlich zur portierten VERSION 1.0.0 aus Git/Paketakte bestimmen.

## Qualifikation

CI prüft main/feat-client-v2-Pushes und Pull Requests (auch Base feat/client-v2) unter Windows mit Python **3.12.10**. Vollständige Unittest-Suite, compileall, PyInstaller mit Versions- und Qt-Importsmoke, Wheel/sdist, Twine und außerhalb Source installierter Wheelnamespace bilden den Prüfpfad. Artefakte sind zeitlich begrenzte CI-Kandidaten, kein Release.

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\venv\Scripts\python.exe -m compileall -q voice_stt_client scripts tests
.\venv\Scripts\python.exe scripts\build.py
.\venv\Scripts\python.exe -m build --sdist --wheel
.\venv\Scripts\python.exe -m twine check dist/*.whl dist/*.tar.gz
```

Build prüft die qualifizierte Pythonpatchversion, Qt-Runtime-DLLs und gebündelte Feedbackressourcen. Ein separates `--dist-dir dist-feedback-rc-<name>` erhält vorhandene Distartefakte. AP000-Wheel- und sdist-Installationsnachweise liegen in der [Runakte](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md). Finaler V2-Frozen-/Hardwaregate bleibt späteren Paketen zugeordnet.

## Veröffentlichung

`scripts/release.py` erlaubt nur lokale Dry-run-Diagnose; der frühere lokale Tag-first-Publishpfad ist deaktiviert. `.github/workflows/release.yml` wird separat manuell auf main mit `candidate_run_id` eines erfolgreichen main-CI-Laufs gestartet. Er prüft Workflow-/Branch-/SHA-Herkunft, VERSION und unveränderte Kandidatenbytes, veröffentlicht und verifiziert Pythonartefakte; erst danach folgen immutable Tag/GitHub-Release. Keine automatische Veröffentlichung durch Paket-PR, Featurepush oder Tagpush. Der derzeit portierte Releaseguard ist bewusst auf V1 1.0.0 begrenzt; V2-Releaseplanung erfordert eigenen Auftrag.

Eine Veröffentlichung ist kein Schritt dieses Client-V2-Paketauftrags. Kein Releaseworkflow wurde ausgeführt.
