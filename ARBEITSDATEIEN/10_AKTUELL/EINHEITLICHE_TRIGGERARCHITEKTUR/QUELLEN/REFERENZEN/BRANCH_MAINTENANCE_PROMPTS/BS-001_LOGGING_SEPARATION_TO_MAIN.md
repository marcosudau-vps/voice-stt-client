# BS-001 – Logging/Observability aus Trigger-Branch separieren und als eigenständigen Main-basierten Branch herstellen

## 1. Ziel

Die abgeschlossene Logging-/Observability-Teil-A-Arbeit befindet sich historisch im Branch:

`feat/einheitliche-triggerarchitektur`

Sie soll jetzt fachlich und Git-historisch von der unfertigen Triggerarchitektur getrennt werden.

Erzeuge dafür einen eigenständigen Branch:

`feat/logging-observability-pre-trigger`

direkt auf Basis von `origin/main`.

Der neue Branch soll die abgeschlossene Logging-/Observability-Teil-A-Arbeit enthalten, aber keine unfertige Triggerarchitektur.

Dieser Auftrag ist ausdrücklich **kein reiner Untersuchungsrun**.

Die Separation soll in diesem Run tatsächlich durchgeführt, getestet und bis zu einem mergefähigen lokalen Logging-Branch fertiggestellt werden.

Noch NICHT:

- nach `main` mergen,
- pushen,
- Pull Request erzeugen,
- den bestehenden Trigger-Branch rebasen oder umschreiben.

---

# 2. Verbindliche lokale Repository-/Worktree-Struktur

Repository-Stamm:

`P:\GithubRepos\marcosudau-vps\voice-stt-client`

Der vorhandene Main-Worktree ist:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`

und muss weiterhin Branch:

`main`

behalten.

Der vorhandene Trigger-Worktree ist:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

mit Branch:

`feat/einheitliche-triggerarchitektur`

Dieser Worktree enthält weiterhin vorbestehende uncommittete Trigger-Arbeitsdateien und darf deshalb weder umgeschaltet noch bereinigt werden.

Der NEUE Logging-Worktree muss exakt hier angelegt werden:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`

und genau den Branch enthalten:

`feat/logging-observability-pre-trigger`

Damit ist der gewünschte Endzustand:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-client\
│
├── main\
│   └── main
│
└── workspaces\
    ├── einheitliche-triggerarchitektur\
    │   └── feat/einheitliche-triggerarchitektur
    │
    └── logging-observability-pre-trigger\
        └── feat/logging-observability-pre-trigger
```

Diese Zuordnung ist verbindlich.

---

# 3. Bekannter Ausgangsstand

Der Logging-Abschlusscommit wurde bereits erfolgreich erstellt und auf den Remote-Triggerbranch gepusht:

`dd0af5e – chore(observability): archive pre-trigger logging workstream`

Remote:

`origin/feat/einheitliche-triggerarchitektur`

Der Push war erfolgreich:

`9f136c3..dd0af5e`

Der Remote-Main-Stand war zuletzt:

`178d32b – fix(feedback): debug LED and sound feedback`

Vor der Separation muss einmal `git fetch origin` ausgeführt und der tatsächliche aktuelle Stand von `origin/main` geprüft werden.

Wenn `origin/main` weiterhin `178d32b...` ist, normal fortfahren.

Falls er inzwischen abweicht, den aktuellen `origin/main` verwenden und dies lediglich im Abschlussbericht dokumentieren.

Keinen zusätzlichen Analyse- oder Freigaberun daraus machen.

---

# 4. Bestehenden Trigger-Worktree vollständig schützen

Zu Beginn im vorhandenen Trigger-Worktree erfassen:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git log -1 --oneline
git fetch origin
git rev-parse origin/main
git log -1 --oneline origin/main
git rev-parse origin/feat/einheitliche-triggerarchitektur
```

Erwartung für den Triggerbranch:

`dd0af5e...`

Der bestehende Trigger-Worktree darf in diesem Run NICHT:

* den Branch wechseln,
* gestasht werden,
* zurückgesetzt werden,
* bereinigt werden,
* rebaset werden,
* gemerged werden.

Insbesondere verboten:

```text
git stash
git reset
git clean
git restore .
git checkout <anderer-branch>
git switch <anderer-branch>
git rebase
```

Die bereits vorhandenen uncommitteten Triggerdateien müssen unverändert erhalten bleiben.

---

# 5. Neuen Logging-Worktree anlegen

Prüfe zunächst, ob Branch oder Zielordner bereits existieren:

```powershell
git branch --list feat/logging-observability-pre-trigger
git worktree list
```

Wenn weder Branch noch Zielworktree bereits existieren, erzeuge sie direkt von `origin/main`:

```powershell
git worktree add -b feat/logging-observability-pre-trigger `
  "P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger" `
  origin/main
```

Danach alle weiteren Arbeiten ausschließlich im neuen Worktree:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`

durchführen.

Falls Branch oder Worktree bereits existieren, nichts überschreiben oder löschen. Prüfe, ob sie eindeutig zu diesem Auftrag gehören und gefahrlos weiterverwendet werden können. Nur bei echter Unklarheit `SEPARATION BLOCKED`.

---

# 6. Commit-Historie zwischen Main und Triggerbranch erfassen

Im neuen Logging-Worktree:

```powershell
git log --reverse --oneline origin/main..origin/feat/einheitliche-triggerarchitektur
```

Nach bisher bekanntem Verlauf ist ungefähr folgende Struktur zu erwarten:

```text
5f2ee4b  frühe Triggerarchitektur-Arbeit
f3908cf  OBS-010 Projektbaseline / Arbeitsakte
b363346  OBS-010/OBS-020
cb0b81f  OBS-030
91a7b7f  OBS-040
7fc6ca6  OBS-050
8eea774  OBS-060
d9369c5  Logging UI/Diagnostics Polish
9f136c3  Logging Phase vor Trigger-Migration schließen
dd0af5e  Logging-Arbeitsakte archivieren
```

Diese Liste ist nur Orientierung.

Die tatsächliche Git-Historie ist maßgeblich.

---

# 7. Separation unmittelbar durchführen

Der frühe Trigger-Commit darf nicht automatisch übernommen werden.

Für die nachfolgenden Logging-/Observability-Commits soll die bestehende Historie soweit möglich erhalten werden.

Bevorzugtes Verfahren:

1. Logging-Commits chronologisch identifizieren.
2. Diese einzeln oder in eindeutig zusammenhängenden Sequenzen auf
   `feat/logging-observability-pre-trigger`
   cherry-picken.
3. Auftretende Konflikte unmittelbar fachlich sauber lösen.
4. Keine unfertige Trigger-Semantik übernehmen.

Dabei nicht wegen jedes Konflikts stoppen.

Ein Konflikt ist zunächst ein normaler Teil dieser Separation.

Wenn ein Logging-Commit Änderungen voraussetzt, die im frühen Trigger-Commit vorhanden waren, konkret prüfen:

* Ist diese Änderung tatsächlich Logging-Infrastruktur?
* Oder gehört sie fachlich zur unfertigen Triggerarchitektur?

Wenn sie ausschließlich für Logging erforderlich und fachlich unabhängig vom Trigger-Zielbild ist, darf die notwendige Änderung gezielt in den Logging-Branch übernommen werden.

Wenn sie fachlich Trigger-Semantik verändert, darf sie nicht übernommen werden.

Gemischte Commits dürfen gezielt aufgeteilt beziehungsweise als äquivalente Logging-only Änderung reproduziert werden.

Keine unnötige Historienneuschreibung und kein künstliches Squashing.

---

# 8. Gewünschter Inhalt des Logging-Branches

Der resultierende Branch soll die abgeschlossene Logging-/Observability-Teil-A-Baseline enthalten, insbesondere soweit Bestandteil der tatsächlich abgeschlossenen Arbeit:

* Logging-/Observability-Produktcode
* Canonical Log Model / Contracts
* Ingress
* Redaction
* Health
* Queue / Worker
* SQLite / Retention
* Observation Hooks
* Query-Layer
* Logging-/Diagnose-UI
* Logging-Settings
* Tests
* Evidence
* `docs/observability/**`
* archivierte Logging-Arbeitsakte
* globale Steuerungsdokumente in ihrem nach OBS-CLOSE-001/002 vorgesehenen Zustand
* Verankerung von Logging Teil B als deferred:

  * OBS-100 bis OBS-180

Die Triggerarchitektur darf in Dokumenten als nächster beziehungsweise aktiver Workstream erwähnt werden.

Nicht enthalten sein darf jedoch unfertige Trigger-Lifecycle-Implementierung, nur weil sie historisch vor den Logging-Commits lag.

---

# 9. Gegen Quellbranch prüfen

Nach der Übertragung prüfen:

```powershell
git log --oneline origin/main..HEAD
git diff --stat origin/main...HEAD
git diff --name-status origin/main...HEAD
```

Zusätzlich den Logging-relevanten Produktstand mit dem Quellbranch vergleichen.

Ziel:

Die Logging-Funktionalität des Triggerbranches muss reproduziert sein, soweit sie unabhängig von der unfertigen Triggerarchitektur ist.

Abweichungen müssen entweder:

* bewusst ausgeschlossene Triggeränderungen,
* rein historische Branch-spezifische Artefakte,
* oder dokumentierte Separation-Anpassungen

sein.

---

# 10. Funktionale Tests

Im neuen Logging-Worktree die reguläre lokale Testbasis ausführen.

Mindestens:

```powershell
python -m unittest discover -s tests -p "test_*.py"
python -m compileall -q app.py core ui scripts tests
```

Zusätzlich vorhandene Logging-/Observability-spezifische Tests bzw. geeignete bestehende Probes ausführen, soweit lokal reproduzierbar.

Wenn Dependencies fehlen, die im Projekt vorgesehene Entwicklungsumgebung verwenden beziehungsweise installieren, ohne Projektabhängigkeiten willkürlich umzuschreiben.

Hardware-, Server- oder manuell erforderliche Prüfungen, die lokal nicht reproduzierbar sind, sauber dokumentieren.

Nicht Tests verändern, nur damit sie grün werden.

Wenn Tests fehlschlagen:

Ursache konkret untersuchen und eine eindeutig durch die Separation verursachte Logging-Regression in diesem neuen Logging-Branch beheben.

Keine Triggerimplementierung hineinziehen, nur um einen Test grün zu bekommen.

---

# 11. Git- und Scope-Abschlussprüfung

Am Ende im neuen Logging-Worktree:

```powershell
git status --short
git diff --check
git log --oneline --decorate origin/main..HEAD
```

Der Worktree soll für einen späteren Push/PR konsistent sein.

Es dürfen keine unbeabsichtigten losen Änderungen übrig bleiben.

Erforderliche Separation-Fixes dürfen mit klaren Commit-Messages committed werden.

Beispiel:

`chore(observability): adapt logging baseline to main`

---

# 12. Ursprünglichen Trigger-Worktree erneut verifizieren

Zum Abschluss den ursprünglichen Worktree nur lesend prüfen:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Erfassen:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
```

Bestätigen:

* Branch weiterhin `feat/einheitliche-triggerarchitektur`
* HEAD weiterhin mindestens auf dem bereits gepushten Abschlussstand `dd0af5e`
* vorbestehende uncommittete Triggerdateien weiterhin vorhanden
* kein Stash
* kein Reset
* kein Clean
* kein Branch-Wechsel
* keine durch BS-001 verursachte Änderung

---

# 13. Abschlussbericht

Erstelle im NEUEN Logging-Worktree:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger\
ARBEITSDATEIEN\90_HISTORIE\2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER\
LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\runs\RUN-BS-001_2026-08-23\
BRANCH_SEPARATION_REPORT.md
```

Der Bericht muss kompakt, aber vollständig enthalten:

## Baselines

* tatsächlicher `origin/main`-SHA
* tatsächlicher Quellbranch-SHA
* neuer Branch
* neuer Worktree-Pfad

## Commit-Übertragung

Tabelle mit:

* Quellcommit
* Kurzbeschreibung
* Klassifikation Logging / Trigger / gemischt
* übernommen ja / nein / teilweise
* resultierender Commit
* kurze Begründung

## Separation

* welche Triggeränderungen bewusst ausgeschlossen wurden
* welche Konflikte auftraten
* wie sie gelöst wurden
* ob Logging technische Abhängigkeiten vom frühen Trigger-Commit hatte

## Tests

* ausgeführte Tests
* Ergebnisse
* nicht ausführbare Checks mit Grund

## Endzustand

* `git status --short`
* Commitliste des neuen Branches gegenüber `origin/main`
* grobe Diff-Statistik
* Bestätigung des lokalen Worktree-Pfads
* Bestätigung, dass `main\` nicht umgeschaltet wurde
* Bestätigung, dass der ursprüngliche Trigger-Worktree unverändert blieb

## Schlussurteil

Exakt eines:

`READY TO PUSH AND OPEN PR AGAINST MAIN`

oder

`SEPARATION BLOCKED`

`SEPARATION BLOCKED` nur bei einem echten, konkret belegten fachlichen Problem verwenden.

---

# 14. Bericht committen

Wenn der Branch konsistent ist, den Abschlussbericht selbst als letzten Commit auf:

`feat/logging-observability-pre-trigger`

committen.

Anschließend nochmals:

```powershell
git status --short
git log -1 --oneline
```

Der neue Logging-Worktree soll clean sein.

---

# 15. In diesem Run ausdrücklich NICHT

Nicht:

* `git push`
* Merge nach `main`
* PR erstellen
* Main-Worktree umschalten
* Triggerbranch rebasen
* Triggerbranch zurücksetzen
* bestehenden Trigger-Dirty-State anfassen

Der Run endet lokal.

---

# Definition of Done

Der Auftrag ist erfolgreich abgeschlossen, wenn:

1. der neue Worktree exakt unter
   `workspaces\logging-observability-pre-trigger`
   existiert,
2. dort ausschließlich
   `feat/logging-observability-pre-trigger`
   ausgecheckt ist,
3. der Branch direkt auf dem aktuellen `origin/main` basiert,
4. Logging Teil A tatsächlich separiert wurde,
5. unfertige Triggerarchitektur ausgeschlossen wurde,
6. die Logging-Baseline lokal getestet wurde,
7. erforderliche Separation-Anpassungen committed wurden,
8. `BRANCH_SEPARATION_REPORT.md` vorliegt und committed ist,
9. der neue Logging-Worktree clean ist,
10. der bestehende Main-Worktree unverändert `main` bleibt,
11. der bestehende Trigger-Worktree unverändert auf
    `feat/einheitliche-triggerarchitektur`
    bleibt,
12. kein Push und kein Merge erfolgt ist,
13. das Schlussurteil eindeutig
    `READY TO PUSH AND OPEN PR AGAINST MAIN`
    oder `SEPARATION BLOCKED`
    lautet.
