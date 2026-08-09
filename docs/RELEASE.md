# Build- und Release-Anleitung

> **Status:** aktiv  
> **Stand:** 9. August 2026  
> **Zuständig für:** Windows-PyInstaller-Build, normale CI und GitHub-Releases

Repository: <https://github.com/marcosudau-vps/voice-stt-client>

## Normaler Commit

Jeder Push auf `main` und jeder Pull Request startet `.github/workflows/ci.yml`
auf einem Windows-Runner mit Python 3.12. Der Workflow installiert
`requirements-dev.txt`, führt die vollständige Unittest-Suite und
`compileall` aus, baut `dist/voice-stt-client.exe` mit PyInstaller und startet
die EXE einmal mit `--version`. Die EXE wird anschließend als zeitlich
begrenztes Workflow-Artefakt abgelegt.

Lokaler identischer Build:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe scripts\build.py --clean
```

`VERSION` ist die einzige Release-Versionsquelle. PyInstaller übernimmt sie
sowohl in die Anwendung als auch in die Windows-Dateieigenschaften.

## Offizielles Release

```powershell
.\venv\Scripts\python.exe scripts\release.py
```

Das Skript verwendet `GH_TOKEN`, wenn die Variable gesetzt ist. Alternativ
liest es `GITHUB_TOKEN_VPS` aus einer mit `--env-file` angegebenen Datei oder
aus `%USERPROFILE%\OneDrive\Desktop\github_accounts.env`. Der Token wird nicht
ausgegeben und nicht ins Repository geschrieben.

Der Ablauf stoppt beim ersten Fehler:

1. `main`, sauberer Arbeitsbaum, `origin/main` synchron, öffentliches Zielrepo
   und GitHub-Account `marcosudau-vps` prüfen;
2. Version selbstständig bestimmen: Solange die aktuelle `VERSION` noch nicht
   getaggt ist, wird sie wiederverwendet; andernfalls folgt der nächste Patch;
3. neue Version vorübergehend setzen;
4. vollständige Tests, `compileall`, PyInstaller-Build und EXE-Smoke ausführen;
5. bei einem lokalen Fehler `VERSION` automatisch zurücksetzen;
6. erfolgreichen Versionsstand committen und pushen;
7. auf grünes `ci.yml` für exakt diesen Commit warten;
8. erst danach den annotierten Tag `vX.Y.Z` pushen;
9. auf `release.yml` warten und die entstandene GitHub-Release-URL ausgeben.

Ohne Tag wird kein offizielles Release erzeugt. Schlägt CI nach dem
Versionscommit fehl, bleibt der Tag frei; nach der Korrektur verwendet das
Skript dieselbe noch nicht veröffentlichte Version erneut. Dadurch wird keine
Versionsnummer übersprungen.

### Vorabprüfung ohne Commit oder Tag

```powershell
.\venv\Scripts\python.exe scripts\release.py --dry-run
```

### Explizite Version

```powershell
.\venv\Scripts\python.exe scripts\release.py --version 1.0.0
```

Das Tag startet `.github/workflows/release.yml`. Der Workflow wiederholt Tests,
Syntaxprüfung und Build, prüft Tag gegen `VERSION` und erstellt anschließend
das GitHub-Release mit:

- `voice-stt-client-vX.Y.Z-windows-x64.exe`
- `SHA256SUMS.txt`

Es gibt bewusst keinen Sync in ein zweites Repository und keinen
Releasepfad, der das grüne CI-Gate vor dem Tag umgehen kann.
