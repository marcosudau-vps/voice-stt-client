# Originalauftrag – AP-CLI-000 / Run 01_BASELINE

Du implementierst ausschließlich AP-CLI-000 im Desktop-Clientrepository.

## Laufmetadaten

```text
AP-ID: AP-CLI-000
Run-ID: 01_BASELINE
Modell/Lane: Claude Code Sonnet / Client
Repository: P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur
Branch: feat/einheitliche-triggerarchitektur
Start-HEAD: db102fdc6dd70e4de798a363608d1e7412533dd7
Freigegebene Planungs-SHA: db102fdc6dd70e4de798a363608d1e7412533dd7
Python: P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe
Zielremote nach Root-PASS: github/feat/einheitliche-triggerarchitektur
Push durch Agent: nein
```

Du bist nicht allein im Gesamtprojekt. Parallel arbeitet ein GPT-Agent
ausschließlich im Serverrepository. Ändere keine Serverdatei und setze keine
fremden Änderungen zurück.

## Verbindliche Lektüre

1. `AGENTS.md` und `CLAUDE.md` im Clientroot vollständig.
2. `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`.
3. Aktiver Arbeitsblock: `README.md`, `STATUS.md`, diese AP-Akte und dieser
   Originalauftrag vollständig.
4. Außerhalb von `IDEEN/`:
   - `PLANUNG/IMPLEMENTIERUNGSPLAN.md`, Abschnitt AP-CLI-000;
   - `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md`;
   - `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`;
   - `NACHVERFOLGUNG/TRACEABILITY.md`, insbesondere AP `CLI-000` und
     clientrelevante Summaryzeilen;
   - relevante Ist-Analysen unter `PLANUNG/ANALYSEN/`.
5. Tatsächlich betroffene Clientmodule, direkte Abhängigkeiten und Tests.

Lies keinerlei Datei unter `IDEEN/` und insbesondere keine Namespace-Datei.
Historische Unterlagen sind keine Sollquelle.

Hinweis: `AGENTS.md` verweist derzeit auf
`docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` und
`docs/IMPLEMENTATION_ROADMAP.md`, die im Worktree nicht existieren. Weise
diese Governanceabweichung nach und korrigiere kanonische Verweise im Scope
dieses Baselinepakets, ohne historische Dateien pauschal zu laden.

## Auftrag

1. Verifiziere Branch, Start-HEAD und den Status. Vor Anlage dieser AP-Akte
   war der Working Tree sauber; die AP-Akte selbst ist erwarteter Scope.
2. Führe die vorhandene relevante Testsuite als Baseline mit der oben
   angegebenen Projekt-Python-Umgebung aus.
3. Inventarisiere Tests und Runtimepfade zu:
   - lokalem Dictation-/Follow-up-Lifecycle;
   - `session.mode` und lokaler VAD-Autorität;
   - kumulativer Extension;
   - Streamstart je Activation;
   - Source-Merge;
   - Session-/Feedback-/Hotkey-Testhilfen.
4. Ordne jede überholte Annahme dem neuen Contract und dem zuständigen
   Folge-AP zu. Ändere alte Tests noch nicht auf Zielverhalten, außer eine
   rein beschreibende Kennzeichnung oder ein zusätzlicher
   Charakterisierungstest ist für die Baseline notwendig.
5. Ergänze deterministische Charakterisierungstests nur für kritische
   vorhandene Ist-Abläufe ohne reproduzierbaren Nachweis. Implementiere weder
   v2-Transport noch ActivationMirror vorzeitig.
6. Kläre die fehlende lokale `venv`-Abweichung und die zwei stale
   Governanceverweise dokumentarisch. Verwende die freigegebene geteilte
   Projektumgebung; installiere nichts global.
7. Aktualisiere `task.md`, `ÜBERGABE.md`, `docs/PROJEKTUEBERSICHT.md` und
   weitere tatsächlich betroffene kanonische Dokumentation auf den
   verifizierten Baselinestand.
8. Führe fokussierte Tests und anschließend die vollständige Clientsuite aus.
   Debugge iterativ bis grün. Verändere Produktverhalten nur, wenn eine
   reproduzierbare Baselineinkonsistenz dies minimal erfordert und kein
   Folge-AP vorweggenommen wird.
9. Schreibe den vollständigen Abschlussbericht nach
   `runs/01_BASELINE/REPORT.md`. Ändere weder diesen Originalprompt noch
   `ABNAHME.md`.
10. Wenn alle verpflichtenden Tests grün sind, stage ausschließlich
    AP-eigene Dateien und erstelle genau einen lokalen Commit:
    `chore(trigger): establish AP-CLI-000 client baseline`.
11. Nicht pushen. Danach stoppen und den strukturierten Bericht zurückgeben.

Bei einem echten Umgebungsblocker: keinen Commit erstellen, `BLOCKED`
berichten und den konkreten reproduzierbaren Nachweis liefern.

## Pflichtvalidierung

```powershell
& 'P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe' -m pytest [fokussierte Tests]
& 'P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe' -m pytest
git diff --check
git status --short
```

## Rückgabeformat

```text
Status: PASS | FAIL | BLOCKED
AP / Run:
Start-HEAD:
Lokale Commit-SHA:
Implementiert/charakterisiert:
Geänderte Produktdokumentation:
Tests mit Ergebnis:
Contract-/Traceability-Zuordnung:
Abweichungen, Flakes, Risiken:
Working-Tree-Status:
Hinweise für Root-Endabnahme:
```
