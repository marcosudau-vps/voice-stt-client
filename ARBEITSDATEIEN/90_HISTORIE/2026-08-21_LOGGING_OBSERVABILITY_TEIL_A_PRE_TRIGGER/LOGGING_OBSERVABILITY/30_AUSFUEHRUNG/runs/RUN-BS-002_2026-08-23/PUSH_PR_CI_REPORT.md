# BS-002 – Push, PR und CI-Validierung: Abschlussbericht

Run-Datum: 2026-08-23
Worktree: `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`

---

## 0. Abweichung von den Vorgaben: Remote

Der im Prompt vorausgesetzte Remote `origin` zeigt in diesem Repository **nicht** auf GitHub,
sondern auf einen lokalen Dateisystempfad:

```
origin  P:/GithubRepos/marcosudau-vps/voice-stt-client/main  (fetch/push)
```

`gh repo view` bestätigte: *"none of the git remotes configured for this repository point to a
known GitHub host."* Es existiert kein echter GitHub-Remote in diesem Repo, obwohl `gh` selbst
authentifiziert ist und `.github/workflows/ci.yml` / `release.yml` vorhanden sind.

Vor jeder Push-Aktion wurde dies dem Nutzer gemeldet und die korrekte Ziel-Organisation erfragt.
Bestätigt wurde: `marcosudau-vps/voice-stt-client` (per `gh api repos/marcosudau-vps/voice-stt-client`
verifiziert, `default_branch: main`).

Da `origin` als Git-Remote-Konfiguration zwischen dieser Worktree und der Trigger-Worktree
`workspaces/einheitliche-triggerarchitektur` geteilt ist (beide sind Linked Worktrees desselben
`.git`-Verzeichnisses, das physisch unter der Trigger-Worktree liegt), wurde **`origin` bewusst
nicht verändert**, um die Trigger-Worktree nicht anzutasten. Stattdessen wurde ein zusätzlicher,
neuer Remote `github` ergänzt:

```
git remote add github https://github.com/marcosudau-vps/voice-stt-client.git
```

Alle Push-/PR-Operationen dieses Runs liefen über `github`, nicht über `origin`. Dies ist die
einzige Abweichung von der wörtlichen Vorgabe in Abschnitt 6 des Prompts (`git push -u origin ...`)
und war zwingend notwendig, weil kein funktionierender GitHub-`origin`-Remote existierte.

---

## 1. Git-Baseline

Vor Beginn geprüft (Abschnitt 4/5 des Prompts):

| Größe | Wert |
|---|---|
| Branch | `feat/logging-observability-pre-trigger` |
| lokaler HEAD (Start) | `48be8736395433f10d9c6354c6cec22bc391fdb9` (= erwartet aus BS-001) |
| Worktree-Status | clean, bis auf die untracked Prompt-Datei `.../prompts/BS-002_PUSH_PR_CI_VALIDATION.md` (vom Nutzer für diesen Run abgelegt, nicht Teil des Commits) |
| `origin/main` (nach `git fetch origin`) | `178d32bdf17d4709307e7a2a944888d2cf294e42` (identisch zu BS-001) |
| GitHub `main` (`marcosudau-vps/voice-stt-client`) | `178d32bdf17d4709307e7a2a944888d2cf294e42` (identisch) |
| Worktree-Pfad | `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger` |

Die aus BS-001 dokumentierten Angaben wurden damit gegen den tatsächlichen Git-Zustand bestätigt
und nicht blind übernommen.

Finaler lokaler/Remote-HEAD nach diesem Run (inkl. CI-Fix und diesem Report):
`2acb93bbdd4deadd7069a03624ee46b9e778a563` (vor dem Report-Commit; siehe Abschnitt 6 für den
tatsächlich finalen PR-HEAD nach dem Report-Commit).

---

## 2. Push

- Befehl: `git push -u github feat/logging-observability-pre-trigger`
- Ergebnis: **Erfolgreich**, neuer Branch auf GitHub angelegt.
- Remote-Tracking bestätigt: lokaler HEAD und `github/feat/logging-observability-pre-trigger`
  waren nach jedem Push identisch (verifiziert per `git rev-parse`).
- `origin` (lokaler Pfad-Remote, von der Trigger-Worktree mitgenutzt) wurde nicht verändert.

---

## 3. Pull Request

| Feld | Wert |
|---|---|
| PR-Nummer | **#1** |
| PR-Titel | `feat(observability): establish pre-trigger logging baseline` |
| Source | `feat/logging-observability-pre-trigger` |
| Target | `main` |
| URL | https://github.com/marcosudau-vps/voice-stt-client/pull/1 |

PR-Beschreibung enthält wie gefordert: Separation aus dem Trigger-Branch, Basis auf `main`,
bewusster Ausschluss der unfertigen Triggerarchitektur, Status
`CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`, expliziten Hinweis, dass `G-OBS-V1` formal
nicht bestanden wurde und nicht fälschlich als PASS dargestellt wird, Deferral von Logging Teil B,
lokale Testzahlen (1125 / 1122 / 3 bekannte Pfadfehler), und den Hinweis, dass keine
Trigger-Migration Bestandteil dieses PRs ist. Kein Merge wurde durchgeführt.

---

## 4. CI – Verlauf und Auswertung

Workflow: **CI** (`.github/workflows/ci.yml`), Job `Test and build Windows executable`
(`windows-latest`).

### 4.1 Run 1 – Run-ID `32639950547` (HEAD `48be873`)

Status: **failure**, Dauer 14s.

Fehler bereits im Checkout-Schritt:

```
unable to create file ARBEITSDATEIEN/90_HISTORIE/.../13_HEALTH_BACKPRESSURE_FAILURE_ISOLATION.md:
Filename too long
```

**Klassifikation: A – Separation-Regression.** Verifiziert: die betroffenen, sehr tief
verschachtelten Pfade unter `90_HISTORIE/.../80_DOCS/Logging_Observability_V1_Produktdokumentation_.../`
existieren ausschließlich auf dem Logging-Branch (`git cat-file -e HEAD:<pfad>` → vorhanden;
`git cat-file -e 178d32b:<pfad>` → nicht vorhanden). Der Windows-Runner scheiterte am Anlegen
dieser Pfade beim Checkout (MAX_PATH-Limit ohne `core.longpaths`).

**Fix (eindeutig notwendig, logging-branch-bedingt):** Neuer Workflow-Schritt vor dem Checkout:

```yaml
- name: Enable Windows long paths
  run: git config --system core.longpaths true
```

Commit `2acb93b` (`fix(ci): enable windows long paths for checkout`), lokal geprüft (Diff minimal,
nur dieser eine Schritt ergänzt), committed und nach `github` gepusht.

### 4.2 Run 2 – Run-ID `32640038822`, erster Versuch (HEAD `2acb93b`)

Checkout jetzt erfolgreich. Status: **failure**, Job-Dauer 2m4s.

Der Schritt „Run complete test suite" brach **ohne** die reguläre Unittest-Zusammenfassung
(„Ran N tests …") ab; letzte sichtbare Ausgabe war ein durch `test_a_failing_clear_is_reported_not_raised`
(`tests/test_obs050_ui.py`) absichtlich ausgelöster und korrekt abgefangener `TimeoutError`
(erwartetes Verhalten der Anwendung, siehe `ui/application.py:632-637`), unmittelbar gefolgt von
„Process completed with exit code 1" ohne weitere Testausgabe.

**Klassifikation (vorläufig): C – Infrastruktur-/Runner-Anomalie.** Kein Produktcode geändert.
Gemäß Prompt „ggf. fehlgeschlagenen Job einmal erneut ausführen, wenn sinnvoll" → Retry ausgelöst:
`gh run rerun 32640038822 --failed`.

### 4.3 Run 2 – Retry (Job-ID `97196420173`, gleicher HEAD `2acb93b`)

Status: **failure**, Job-Dauer 2m34s. Diesmal lief die Suite **vollständig durch**:

```
Ran 1125 tests in 89.365s
FAILED (errors=3)
```

Alle drei Fehler sind `FileNotFoundError` in
`test_obs040_contracts.TestFrozenCounterSetIsUnchanged.test_normative_documents_are_untouched_by_this_run`
für die Dokumente `LOGGING_ARCHITEKTUR_FREEZE_V1.md`, `LOGGING_CONTRACTS_FREEZE_V1.md`,
`LOGGING_DECISIONS_FREEZE_V1.md` unter `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/`
– dieser Pfad existiert nach der Archivierung nach `90_HISTORIE` (Commits vor BS-001) nicht mehr.

**Lokaler Vergleichslauf** (identischer Befehl, gleicher Branch-Stand, dieser Windows-Rechner):

```
Ran 1125 tests in 103.634s
FAILED (errors=3)
```

Identische 3 Fehler, identische Ursache. Das deckt sich exakt mit dem in BS-001 dokumentierten
Ausgangsstand („1125 total, 1122 pass, 3 vorbestehende, nachweislich nicht durch die Separation
verursachte Pfad-Test-Fehler").

**Klassifikation: B – Vorbestehender, bereits vor diesem Run bekannter Fehler.** Nicht blind
repariert, hier dokumentiert. Kein neuer Fehler gegenüber dem BS-001-Referenzstand.

Der abgebrochene erste Versuch von Run 2 (4.2) wird damit rückwirkend als einmalige, nicht
reproduzierbare Runner-Anomalie (Kategorie C) eingestuft: der Retry auf demselben Commit lief
deterministisch und deckt sich exakt mit dem lokalen Ergebnis.

### 4.4 Nachgelagerte Schritte (compileall, Build, Smoke-Test, Artifact-Upload)

Der Workflow hat zwischen den Steps keine Fehlertoleranz (kein `continue-on-error`, kein
`if: always()`); da „Run complete test suite" mit Exit-Code 1 endet (unittest liefert bei
`errors=3` konsequent ungleich 0), werden `Compile all Python modules`, `Build and smoke-test
executable`, `Read version` und `Upload Windows executable` von der CI **nicht ausgeführt**
(als „skipped" markiert). Dieses Verhalten ist eine bestehende Eigenschaft der geteilten
`ci.yml`-Struktur und keine Separation-Regression – sie träte identisch auf `main` auf, sobald
dort ein Test scheitert.

Um dennoch eine Aussage zu diesen Schritten treffen zu können, wurden sie **lokal** mit denselben
Befehlen wie im Workflow nachvollzogen (auf diesem Windows-Rechner, gleicher Branch-Stand
`2acb93b`):

```
python -m compileall -q app.py core ui scripts tests   → erfolgreich, keine Ausgabe/Fehler
python scripts/build.py --clean                         → erfolgreich
  Build complete! dist\voice-stt-client.exe (79.061.247 bytes)
  Version 0.2.0; SHA-256 97e4de5f...
```

Beide Schritte liefen sauber durch; es gibt keinen Hinweis auf eine durch die Separation
verursachte Regression in Compile/Build/Smoke-Test.

### 4.5 Finaler PR-HEAD (nach Report-Commit)

Siehe Abschnitt 6 – der Report-Commit löst laut Vorgabe einen weiteren CI-Lauf aus; dessen
Ergebnis wird unten in Abschnitt 6 zusammengefasst und ist maßgeblich für das Schlussurteil.

---

## 5. Lokale Worktree-Sicherheit

Bestätigt:

- **Main-Worktree** (`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`): nicht geöffnet, nicht
  gelesen, nicht verändert. Kein Branch-Wechsel, kein Reset, kein Clean, kein Stash dort ausgeführt.
- **Trigger-Worktree** (`workspaces\einheitliche-triggerarchitektur`): keine Datei, kein Branch,
  kein Index-Zustand dort verändert. Einzige geteilte Auswirkung: da beide Worktrees Linked
  Worktrees desselben `.git`-Verzeichnisses sind, ist die Remote-Liste (`git remote -v`)
  repository-weit geteilt; es wurde bewusst ein **zusätzlicher** Remote `github` ergänzt statt
  `origin` zu verändern, um den bestehenden, von der Trigger-Worktree genutzten `origin`-Eintrag
  nicht anzutasten. Branch, HEAD, Arbeitsverzeichnis und Index der Trigger-Worktree blieben
  unberührt.
- **Logging-Worktree**: bleibt bestehen, wurde nicht gelöscht.
- **Kein Merge** wurde in main durchgeführt oder ausgelöst.

---

## 6. Bericht committen und pushen – finaler PR-HEAD

*(Dieser Abschnitt wird nach dem Commit/Push des Reports und dem Abwarten des dadurch
ausgelösten CI-Laufs vervollständigt – siehe Commit-Historie und finale CI-Bewertung unten.)*

---

## 7. Schlussurteil

*(wird nach Abschnitt 6 gesetzt)*
