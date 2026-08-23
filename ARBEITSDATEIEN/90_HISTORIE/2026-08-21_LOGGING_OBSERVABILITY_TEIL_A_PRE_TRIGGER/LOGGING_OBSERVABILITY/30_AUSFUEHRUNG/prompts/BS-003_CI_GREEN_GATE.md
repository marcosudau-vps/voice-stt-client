# BS-003 – PR #1 auf tatsächlich grünen CI-Zustand bringen

## 1. Ziel

Der Pull Request

`#1 – feat(observability): establish pre-trigger logging baseline`

ist aktuell NICHT mergebereit im qualitativen Sinn, weil die GitHub-CI rot ist.

Dieser Run soll den konkreten verbliebenen CI-Fehler beheben und PR #1 auf
einen tatsächlich vollständig grünen GitHub-Actions-Zustand bringen.

Ein Schlussurteil `READY TO MERGE` ist ausschließlich zulässig, wenn für den
tatsächlich aktuellen PR-HEAD die GitHub-CI vollständig erfolgreich ist.

Bekannte Fehler dürfen in diesem Run nicht mehr als akzeptabler roter
CI-Zustand behandelt werden.

Kein Merge nach main.

---

## 2. Arbeitsbereich

Ausschließlich arbeiten in:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`

Branch:

`feat/logging-observability-pre-trigger`

GitHub-Remote:

`github`

Der bestehende Remote `origin` zeigt in dieser Repository-Struktur auf einen
lokalen Pfad und darf nicht verändert werden.

Main- und Trigger-Worktree nicht verändern.

Insbesondere unangetastet lassen:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`

und:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

---

## 3. Aktuellen Zustand zuerst verifizieren

Ausführen:

```powershell
git branch --show-current
git status --short
git rev-parse HEAD
git fetch github
git rev-parse github/feat/logging-observability-pre-trigger
gh pr view 1 --repo marcosudau-vps/voice-stt-client --json headRefOid,state,mergeable
````

Zum Zeitpunkt der Auftragserstellung ist der aktuelle GitHub-PR-HEAD:

`47ea3cea4602eab9d5d28afdb72bf6b9deb87bb0`

Der aktuelle GitHub-CI-Lauf für diesen HEAD ist rot.

Falls sich der HEAD inzwischen geändert hat, den tatsächlichen aktuellen
Stand verwenden.

Keine alten Report-Angaben als maßgeblich behandeln.

---

## 4. Verbliebenen CI-Fehler als echten Merge-Blocker behandeln

Aktuell scheitert:

`tests/test_obs040_contracts.py`

mit drei `FileNotFoundError`.

Betroffen sind:

* `LOGGING_ARCHITEKTUR_FREEZE_V1.md`
* `LOGGING_CONTRACTS_FREEZE_V1.md`
* `LOGGING_DECISIONS_FREEZE_V1.md`

Die Tests suchen diese Dateien offenbar weiterhin unter:

`ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/00_NORMATIV/`

Logging Teil A wurde aber bewusst und kontrolliert archiviert nach:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/00_NORMATIV/`

Der frühere Agent klassifizierte dies als „vorbestehenden Fehler“.

Für diesen Run gilt ausdrücklich:

**Ein Testfehler, den der PR nach main übernehmen würde, ist kein akzeptabler
Mergezustand.**

Die Tests und die neue Archivstruktur müssen wieder konsistent werden.

---

## 5. Testintention vor Änderung kurz prüfen

Untersuche gezielt:

`tests/test_obs040_contracts.py`

und die drei archivierten Normativdokumente.

Kläre die bestehende Testintention, insbesondere:

* Welche Inhalte bzw. Hashes/Counter/Frozen Contracts werden geschützt?
* Prüft der Test die Unverändertheit der Dokumente?
* Ist nur der alte Dateipfad durch die kontrollierte Archivierung veraltet?

Wenn – wie erwartet – ausschließlich der Pfad veraltet ist:

die Tests minimal auf den tatsächlich kanonischen historischen Archivpfad
umstellen.

Dabei müssen die eigentlichen Schutzinvarianten erhalten bleiben.

---

## 6. Verbotene „Fixes“

Nicht:

* Tests löschen,
* Tests skippen,
* `@unittest.skip` hinzufügen,
* xfail-artige Mechanismen einführen,
* Assertions abschwächen,
* erwartete Hashes/Inhalte ohne fachlichen Grund ändern,
* `continue-on-error` in der CI hinzufügen,
* den Test-Step künstlich erfolgreich machen,
* die drei Fehler lediglich dokumentieren und trotzdem READY melden.

Ebenso nicht die archivierten Dokumente einfach als Duplikat wieder unter
`10_AKTUELL/LOGGING_OBSERVABILITY` zurückkopieren, nur um den alten Pfad
wiederherzustellen, sofern die kontrollierte Archivierungsentscheidung
eindeutig besagt, dass Teil A dort nicht mehr aktiv liegen soll.

Ziel ist Konsistenz zwischen Test und bewusstem Archivzustand.

---

## 7. Minimalen Fix durchführen

Wenn die Analyse bestätigt, dass nur der Pfad veraltet ist:

`tests/test_obs040_contracts.py`

so minimal wie möglich auf den kanonischen Archivpfad umstellen.

Die drei Normativdokumente selbst nicht inhaltlich verändern.

Keine Produktcodeänderung durchführen, sofern sie für diesen Fehler nicht
erforderlich ist.

---

## 8. Lokale Validierung

Zuerst gezielt:

```powershell
python -m unittest tests.test_obs040_contracts
```

Erwartung:

PASS.

Danach vollständige Suite:

```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Akzeptanzkriterium:

**0 failures, 0 errors.**

Die bisherige Zahl war 1125 Tests.

Falls die Anzahl weiterhin 1125 beträgt, müssen alle 1125 erfolgreich sein.

Anschließend:

```powershell
python -m compileall -q app.py core ui scripts tests
python scripts/build.py --clean
```

Beide müssen erfolgreich sein.

---

## 9. Commit und Push

Wenn alle lokalen Prüfungen erfolgreich sind:

```powershell
git status --short
git diff --check
```

Dann ausschließlich den notwendigen Fix committen.

Bevorzugte Commit-Message:

`test(observability): follow archived normative contract paths`

Danach:

```powershell
git push github feat/logging-observability-pre-trigger
```

Nicht `origin` verwenden.

---

## 10. Pull-Request-Beschreibung aktualisieren

Die bestehende PR-Beschreibung enthält derzeit sinngemäß:

* 1125 Tests
* 1122 erfolgreich
* 3 bekannte Fehler

Nach erfolgreichem Fix ist diese Angabe veraltet.

Aktualisiere PR #1 so, dass der tatsächlich neue Zustand korrekt dargestellt
wird.

Bei 1125/1125 beispielsweise:

* 1125 Tests total
* 1125 erfolgreich
* 0 Fehler

Keine Aussage stehen lassen, wonach drei rote Tests für den Merge akzeptiert
würden.

---

## 11. GitHub-CI vollständig abwarten

Nach dem Push den GitHub-Actions-Lauf für den NEUEN PR-HEAD abwarten.

Akzeptanzkriterium ist nicht nur die Test-Suite.

Für den finalen PR-HEAD müssen im GitHub-Workflow erfolgreich sein:

* Enable Windows long paths
* Check out repository
* Set up Python
* Install dependencies
* Run complete test suite
* Compile all Python modules
* Build and smoke-test executable
* Read version
* Upload Windows executable

Keiner dieser relevanten Schritte darf wegen eines vorherigen Fehlers
`skipped` sein.

Falls ein eindeutiger transienter GitHub-Runner-Fehler auftritt, darf genau
ein sinnvoller Retry erfolgen.

Falls danach irgendein fachlicher/Test-/Build-Fehler verbleibt:

nicht READY melden.

---

## 12. Strenges Schlussgate

`READY TO MERGE PR INTO MAIN`

darf ausschließlich ausgegeben werden, wenn:

1. aktueller PR-HEAD eindeutig festgestellt ist,
2. vollständige lokale Tests grün sind,
3. Compile lokal grün ist,
4. Build lokal grün ist,
5. derselbe finale PR-HEAD auf GitHub gepusht ist,
6. GitHub Actions für genau diesen HEAD `success` meldet,
7. die vollständige CI einschließlich Build und Artifact-Upload durchgelaufen
   ist,
8. PR #1 weiterhin offen und ungemerged ist.

Ein rotes GitHub-Actions-Symbol ist mit `READY TO MERGE` unvereinbar.

---

## 13. Abschlussbericht

Nachdem der finale GitHub-CI-Lauf abgeschlossen ist, erstelle lokal:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-BS-003_2026-08-23/CI_GREEN_REPORT.md`

Der Bericht muss enthalten:

### Baseline

* Start-HEAD
* finaler HEAD
* PR #1
* verwendeter Remote

### Ursache

* konkrete Ursache der drei bisherigen Fehler
* warum die bisherige Klassifikation als akzeptabler „vorbestehender Fehler“
  für einen Main-Merge nicht ausreichend war

### Änderung

* exakt geänderte Dateien
* Testinvariante vor/nach Änderung
* Bestätigung, dass Tests nicht abgeschwächt oder deaktiviert wurden

### Lokale Tests

* gezielter OBS-040-Test
* vollständige Test-Suite
* Compile
* Build

### GitHub CI

* finale Run-ID
* finaler Head-SHA
* Ergebnis jedes relevanten Workflow-Schritts
* Gesamtstatus

### PR

* aktualisierte Testangaben
* weiterhin offen
* nicht gemerged

### Schlussurteil

Genau eines:

`READY TO MERGE PR INTO MAIN`

oder:

`CI NOT GREEN – DO NOT MERGE`

WICHTIG:
Den CI_GREEN_REPORT.md nach dem final grünen CI-Lauf NICHT mehr committen
oder pushen.

Sonst würde durch den Report selbst erneut ein neuer PR-HEAD und ein neuer
CI-Lauf entstehen.

Der Bericht bleibt für die externe Sichtung lokal liegen.

---

## 14. Nicht tun

Nicht:

* nach main mergen,
* Main-Worktree verändern,
* Trigger-Worktree verändern,
* Remotes umkonfigurieren,
* origin ersetzen,
* CI-Fehler ignorieren,
* rote CI als mergebereit bewerten.

Der Run endet mit grünem PR oder eindeutigem
`CI NOT GREEN – DO NOT MERGE`.

