# Agentenbericht – AP-CLI-000 / Run 03_CORRECTION

**Status:** PASS

## 1. Befund 1 – falscher venv-Pfad in den neuen AP-CLI-000-Passagen

Die in Run `01_BASELINE`/`02_CORRECTION` neu ergänzten AP-CLI-000-Passagen in
`task.md`, `ÜBERGABE.md` und im Baseline-Testbefehl von
`runs/01_BASELINE/REPORT.md` nannten `.\venv\Scripts\python.exe`. Dieser
Worktree besitzt keine eigene lokale `venv`; der Originalauftrag legt
ausdrücklich die geteilte Umgebung
`P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe`
fest (bereits korrekt in `runs/01_BASELINE/REPORT.md` Abschnitt 1 sowie in
den Validierungsblöcken von Abschnitt 7 referenziert). Historische
Betriebsbefehle außerhalb der neuen AP-CLI-000-Passagen (z. B. `task.md:371`
sowie die Start-/Build-/Release-Befehle in `ÜBERGABE.md` Abschnitt 5)
beschreiben den Pre-Trigger-Stand und wurden unverändert gelassen.

### Änderung

- `task.md`: neuer Baseline-Absatz zeigt jetzt auf den vollständigen
  geteilten venv-Pfad und nennt explizit, dass dieser Worktree keine eigene
  `venv` besitzt.
- `ÜBERGABE.md`: neuer Abschnitt „0. Baseline …“ ebenso korrigiert.
- `runs/01_BASELINE/REPORT.md` Abschnitt 3: der dort protokollierte
  Baseline-Testbefehl (`.\venv\Scripts\python.exe -m pytest -q`) auf den
  vollständigen geteilten Pfad korrigiert. Die bereits davor (Abschnitt 1)
  und danach (Abschnitt 7, mit `...\main\venv\Scripts\python.exe`-Kurzform)
  vorhandenen korrekten Referenzen blieben unverändert.

### Nachweis

```powershell
git diff --check -- task.md "ÜBERGABE.md" "ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/ARBEITSPAKETE/AP-CLI-000/runs/01_BASELINE/REPORT.md"
# kein Output, Exit 0

grep -n "venv" task.md ÜBERGABE.md ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/ARBEITSPAKETE/AP-CLI-000/runs/01_BASELINE/REPORT.md
# alle verbleibenden Treffer sind entweder historische Pre-Trigger-Befehle
# (task.md:371, ÜBERGABE.md Abschnitt 5) oder nennen den vollständigen
# geteilten Pfad main\venv\Scripts\python.exe
```

## 2. Befund 2 – Source-Merge-Folge-AP fälschlich allein `CLI-020` zugeordnet

`runs/01_BASELINE/REPORT.md` Abschnitt 4.5 ordnete die Umstellung des
Feedback-Reducers auf First-Trigger-wins pauschal `CLI-020` zu. Verbindlich
ist die getrennte Zuordnung: serverseitige Source-/Admission-Semantik
`SRV-010`, manuelle Command-/Hotkey-Semantik `CLI-020`, source-neutrales
Feedback und die betroffenen Feedback-Reducer-Tests
(`tests/test_trigger_feedback_contract.py::ManualDuringWakeWordActivation`/
`::WakeWordDuringManualActivation`) `CLI-040`.

### Änderung

- `runs/01_BASELINE/REPORT.md` Abschnitt 4.5, Zeile „Folge-AP“: auf die drei
  getrennten Verantwortlichkeiten `SRV-010`/`CLI-020`/`CLI-040` mit
  Begründung je AP umgestellt. Andere Folge-AP-Zuordnungen in Abschnitt 4
  (4.1–4.4, 4.6) blieben unverändert, da nicht Gegenstand dieses Befunds.
- `ÜBERGABE.md` Abschnitt 0: die dortige zusammenfassende Folge-AP-Liste um
  `AP-CLI-040` ergänzt, sodass sie mit der korrigierten Zuordnung in
  Abschnitt 4.5 des Baseline-Berichts konsistent ist.

### Nachweis

```text
grep -n "CLI-020\|CLI-040\|Source-Merge" .../AP-CLI-000/runs/01_BASELINE/REPORT.md
# Abschnitt 4.5 nennt jetzt SRV-010 (Server-Admission), CLI-020 (manuelle
# Command-/Hotkey-Semantik) und CLI-040 (Feedback-Reducer/-Tests) getrennt
# mit je eigener Begründung; die unveränderte Zuordnung in Abschnitt 4.3
# (SRV-030, CLI-020, kumulative Extension) ist nicht betroffen.
```

## 3. Keine Produkt-/Teständerung

Es wurde ausschließlich Dokumentation korrigiert. Kein Produktcode und kein
Test wurden geändert; eine erneute Vollsuite war für diese reine
Dokumentkorrektur nicht erforderlich und wurde nicht ausgeführt.

## 4. Staging, Amend und Abschlussprüfung

Gestaged wurden ausschließlich:

- `task.md`
- `ÜBERGABE.md`
- `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/ARBEITSPAKETE/AP-CLI-000/runs/01_BASELINE/REPORT.md`
- `runs/03_CORRECTION/PROMPT.md` (unveränderter Korrekturauftrag)
- `runs/03_CORRECTION/REPORT.md` (dieser Bericht)

Amend mit `git commit --amend --no-edit` auf den vorhandenen AP-Commit
`c8c0fea67bd8f3392e46d2ad997899c401c78f30`; kein zweiter Commit erstellt,
Commit-Message unverändert. `runs/01_BASELINE/ABNAHME.md` sowie alle
früheren Originalprompts (`runs/01_BASELINE/PROMPT.md`,
`runs/02_CORRECTION/PROMPT.md`) blieben unangetastet.

```powershell
git status --short
# leer (sauberer Working Tree)

git log --oneline db102fdc6dd70e4de798a363608d1e7412533dd7..HEAD
# genau ein Commit seit Start-HEAD (neue SHA nach Amend)
```

Kein Push ausgeführt.
