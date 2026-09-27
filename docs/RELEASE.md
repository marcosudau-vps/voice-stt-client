# Build- und Release-Anleitung

> **Status:** aktiv
> **Stand:** 26. September 2026
> **Zuständig für:** Windows-PyInstaller-Build, PyPI-Paket, CI und Releases

Repository: <https://github.com/marcosudau-vps/voice-stt-client>

## Normaler Commit

Jeder Push auf `main` und jeder Pull Request startet `.github/workflows/ci.yml`
auf einem Windows-Runner mit Python 3.12. Der Workflow installiert
`requirements-dev.txt`, führt die vollständige Unittest-Suite und
`compileall` aus, baut und startet `dist/voice-stt-client.exe`, erzeugt Wheel
und Source Distribution und installiert das Wheel isoliert. Dabei wird
ausdrücklich geprüft, dass nur `voice_stt_client.*` bereitgestellt wird und
Konfiguration sowie Sounds aus dem installierten Paket verfügbar sind. Alle
drei Kandidaten werden anschließend als zeitlich begrenztes
Workflow-Artefakt abgelegt.

Lokaler identischer Build:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe scripts\build.py --clean
.\venv\Scripts\python.exe -m build --sdist --wheel
.\venv\Scripts\python.exe -m twine check dist\*.whl dist\*.tar.gz
```

Für einen neuen Kandidaten neben einer bereits laufenden alten EXE kann
`scripts\build.py --dist-dir dist-local-test` verwendet werden. Das ist nur
ein isoliertes lokales Testverzeichnis; vor dem Release muss der endgültige
Build wieder über den normalen `dist`-Pfad samt vollständiger Prüfung laufen.
Die Build-Option ersetzt keine Anwenderkonfiguration.

Beim manuellen EXE-Test zuerst ohne CLI-Flags und ohne Spezialprofil starten.
Der Client lädt die mitgelieferten Defaults und darüber die Benutzerdatei
`%USERPROFILE%\.voice-stt\client\config.yaml`, falls vorhanden. Den
Einstellungsdialog und die Persistenz nach einem regulären Neustart prüfen;
ein technischer Test mit `--config` ist nur eine zusätzliche Matrixprüfung.
Belegte Hotkeys, LED und Sound müssen unter diesen normalen Bedingungen
explizit geprüft werden; ein grüner Build-Smoke allein ist keine Freigabe.

`VERSION` ist die einzige Release-Versionsquelle. PyInstaller übernimmt sie
sowohl in die Anwendung als auch in die Windows-Dateieigenschaften;
`pyproject.toml` verwendet denselben Wert für die PyPI-Metadaten.

## Offizielles Release 1.0.0 – ausschließlich GitHub Actions

Das alte lokale `scripts/release.py` darf **keinen Tag mehr erzeugen**; sein
Schreibpfad ist gesperrt. `--dry-run` bleibt als lokale Zusatzprüfung möglich.
Der erste Client-Release verwendet nur den erfolgreichen Windows-CI-Lauf
auf `main` und die daraus stammenden unveränderten EXE-/Python-Artefakte.

1. Den vollständigen Client-Stand committen und auf `main` pushen.
2. `ci.yml` für genau diesen Commit vollständig grün abwarten; dieser Lauf
   baut die EXE, Wheel und sdist, prüft Tests, GUI-Smoke und Installation.
3. Den CI-Run und seine Artefakte vor Veröffentlichung qualifizieren;
   `candidate_run_id` notieren.
4. Den manuellen Workflow `.github/workflows/release.yml` auf `main` mit
   dieser `candidate_run_id` starten. Sein Preflight prüft CI-Ergebnis,
   Branch/Commit und genau einen Satz EXE, Wheel, sdist. Er baut **nicht neu**.
5. PyPI Trusted Publishing lädt nur noch fehlende Dateien hoch. Vor und nach
   dem Upload werden die Remote-Dateien anhand SHA-256 klassifiziert;
   `CONFLICT`/unerwartete Dateien stoppen den Lauf.
6. **Erst nach PyPI-MATCH** entsteht der annotierte Git-Tag `v1.0.0` am
   qualifizierten CI-Commit. GitHub Release ist der letzte Schritt und
   enthält dieselbe EXE, Wheel, sdist sowie `SHA256SUMS.txt`.

Der PyPI-Pending-Publisher für `voice-stt-client` muss vor Schritt 4 diese
Werte enthalten: Owner `marcosudau-vps`, Repository `voice-stt-client`,
Workflow `release.yml`, Environment `pypi`. Das GitHub-Environment heißt
ebenfalls `pypi`; kein langlebiger PyPI-Token ist nötig. Falls ein späterer
Job scheitert, wird **derselbe CI-Run mit denselben Bytes** erneut angegeben.
Schon passende PyPI-Dateien werden nicht erneut hochgeladen; ein anderer
Hash stoppt. Kein Tag-Push startet automatisch einen neuen Build.

Die vier GitHub-Release-Assets sind:

- `voice-stt-client-v1.0.0-windows-x64.exe`
- `voice_stt_client-1.0.0-py3-none-any.whl`
- `voice_stt_client-1.0.0.tar.gz`
- `SHA256SUMS.txt`

## Gemeinsames erstes Release

Client `1.0.0` ist für VoiceSTT Server `1.0.0` vorgesehen. Die gemeinsam
getestete Zuordnung wird vor Tagging in `docs/COMPATIBILITY.md` mit den finalen
Quellcommits und Artefakt-Hashes festgeschrieben. Diese Zuordnung trifft keine
Aussage darüber, ob spätere Client- und Serverversionen gekoppelt oder
unabhängig veröffentlicht werden.

Beim ersten gemeinsamen Release wird zuerst der Server vollständig bis zu
PyPI, Docker Hub, GHCR, Git-Tag und GitHub Release abgeschlossen. Erst danach
startet der Client seinen eigenständigen `1.0.0`-Release aus diesem Repository.

Der Client verwendet ausschließlich den eindeutigen Python-Namespace
`voice_stt_client`. Die früheren generischen Top-Level-Pakete `core` und `ui`
werden weder in Wheel noch sdist installiert. CI und Release prüfen dies aus
einem frischen Installationsverzeichnis.
