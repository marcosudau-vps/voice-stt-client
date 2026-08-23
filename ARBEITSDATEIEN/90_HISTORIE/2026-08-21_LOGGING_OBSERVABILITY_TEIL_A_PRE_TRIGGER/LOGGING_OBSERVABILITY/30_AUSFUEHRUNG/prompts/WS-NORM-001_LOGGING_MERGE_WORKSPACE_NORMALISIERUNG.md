# WS-NORM-001 – Logging-Merge und Workspace-Normalisierung

## 1. Ziel

Dieser Run soll die gesamte Logging-/Branch-Separations-/CI-/Workspace-
Aufräumphase (`OBS-CLOSE-001`, `OBS-CLOSE-002`, `BS-001`, `BS-002`, `BS-003`)
formal und technisch abschließen.

Verbindliche Vorgaben für diesen Run:

1. Kein relevanter Prompt, Report oder Evidence-Nachweis darf beim Entfernen
   des temporären Logging-Worktrees verloren gehen.
2. Ein zentraler `AUFRAEUMPHASE_INDEX.md` muss `OBS-CLOSE-001`,
   `OBS-CLOSE-002`, `BS-001`, `BS-002`, `BS-003` und `WS-NORM-001` mit ihren
   tatsächlichen Artefakten und Pfaden zuordnen.
3. `LOG_VERLAUF.md` muss einen neuen Abschlussmeilenstein mit tatsächlichem
   Datum UND Uhrzeit erhalten, der auf Run-Report und Output-Index verweist.
4. Der endgültige Workspace-Zustand soll eindeutig sein:
   - `main\` = Branch `main` / Baseline
   - `workspaces\einheitliche-triggerarchitektur\` = aktiver
     Entwicklungs-Workspace
   - `workspaces\logging-observability-pre-trigger\` = nach Abschluss entfernt
5. Der dauerhafte Standard-Startordner für normale Agenten-Sessions ist
   danach:
   `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`
6. `ARBEITSDATEIEN` niemals manuell zwischen Worktrees kopieren. Die
   Konsolidierung erfolgt ausschließlich über Git.
7. Der Trigger-Worktree (`workspaces\einheitliche-triggerarchitektur`) ist in
   diesem Run vollständig read-only.

Schlussurteil ausschließlich:

`WORKSPACE NORMALIZED – READY FOR TRIGGER MAIN-INTEGRATION`

oder ein konkreter Blocker.

---

## 2. Arbeitsbereich

Primär arbeitend in:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\logging-observability-pre-trigger`

Branch:

`feat/logging-observability-pre-trigger`

Lesend (nicht verändernd) referenziert:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`
(Branch `feat/einheitliche-triggerarchitektur`, vollständig read-only in
diesem Run)

`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`
(unabhängiger Clone, aktuell auf Branch `wip/led-sound-debugfeedback-sicherung`
– unverändert und nicht Gegenstand dieses Runs)

---

## 3. Ausgangsbefund (bei Run-Start festgestellt)

- PR `#1` (`feat/logging-observability-pre-trigger` → `main`) ist `OPEN`,
  `MERGEABLE`, CI grün für HEAD `7d4ac6a` (bestätigt durch `BS-003`).
- `main` (im geteilten `workspaces`-Repo sowie im unabhängigen Clone
  `P:\...\main`) steht unverändert auf `178d32b` und enthält noch keinerlei
  `ARBEITSDATEIEN`.
- `feat/einheitliche-triggerarchitektur` ist **nicht** von
  `feat/logging-observability-pre-trigger` abgeleitet (gemeinsamer
  Merge-Base mit `main` = `178d32b`); die dort vorhandene
  `STEUERUNG_SNAPSHOT/LOG_VERLAUF.md`-Kopie ist ein manueller Snapshot aus
  einem früheren Run, kein Git-Merge-Ergebnis.
- `BS-001` liegt als Prompt ausschließlich im Trigger-Workspace unter
  `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/30_AUSFUEHRUNG/prompts/BRANCH_MAINTENANCE/BS-001_LOGGING_SEPARATION_TO_MAIN.md`.
- Drei Artefakte aus `BS-002`/`BS-003` waren zu Run-Beginn im Arbeitsbaum
  ungetrackt: `BS-002_PUSH_PR_CI_VALIDATION.md`, `BS-003_CI_GREEN_GATE.md`,
  `runs/RUN-BS-003_2026-08-23/CI_GREEN_REPORT.md`. Der `CI_GREEN_REPORT.md`
  sollte laut `BS-003` bewusst lokal/ungetrackt bleiben; da dieser Run den
  Worktree entfernt, wird diese frühere Entscheidung hiermit ausdrücklich
  aufgehoben zugunsten von Punkt 1 (kein Evidence-Verlust).

Konsequenz: Die einzige Git-only-Konsolidierung, die Punkt 1 und Punkt 6
erfüllt, ist das Mergen von PR `#1` nach `main`, bevor der Logging-Worktree
entfernt wird.

---

## 4. Nicht Gegenstand dieses Runs

- Keine Änderung an `main`s aktuellem Checkout
  (`wip/led-sound-debugfeedback-sicherung`) außerhalb des reinen
  Branch-Ref-Updates von `main` selbst.
- Kein Merge von `feat/logging-observability-pre-trigger` bzw. `main` nach
  `feat/einheitliche-triggerarchitektur` (das ist der nachfolgende, separate
  Schritt "Trigger Main-Integration").
- Keine fachliche Änderung an Produktcode.
