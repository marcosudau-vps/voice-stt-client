# WORKSPACE_KONVENTION

Verbindliche Konvention für den Umgang mit den Git-Worktrees/-Clones dieses
Repositories. Gilt ab `WS-NORM-002` (2026-08-23) und ersetzt keine frühere
Konvention, da bisher keine eigenständige Konventionsdatei existierte.

## Feste Rollen

| Pfad | Rolle | Branch |
|---|---|---|
| `P:\GithubRepos\marcosudau-vps\voice-stt-client\main` | Baseline / Standalone-Clone | `main` |
| `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur` | aktiver Entwicklungs-Workspace | `feat/einheitliche-triggerarchitektur` |

- **`main\`** ist die Baseline. Governance-/Dokumentationsänderungen und
  kontrollierte Main-Integrationen erfolgen hier. Keine fachliche
  Triggerarbeit in diesem Clone.
- **`workspaces\einheitliche-triggerarchitektur\`** ist der aktive
  Entwicklungs-Workspace für die Triggerarchitektur-Migration und der
  **Standard-Agent-Session-Root** für normale Entwicklungs-Sessions dieses
  Workstreams.

## Temporäre Worktrees

- Temporäre Worktrees werden ausschließlich für einen klar benannten,
  zeitlich begrenzten Zweck angelegt (z. B. Branch-Separation, isolierte
  Aufräum-/Merge-Runs).
- Nach Abschluss ihres Zwecks werden sie git-seitig per
  `git worktree remove` entfernt. Ein physisch nicht löschbarer, leerer
  Verzeichnis-Stub (z. B. durch einen externen Dateisystem-Lock) ist ein
  rein kosmetischer Restpunkt und kein Blocker für Folgearbeit, solange
  `git worktree list` ihn nicht mehr führt.
- Es wird kein neuer dauerhafter Worktree ohne expliziten Auftrag angelegt.

## ARBEITSDATEIEN nie manuell kopieren

`ARBEITSDATEIEN/` wird zwischen Worktrees/Clones ausschließlich über reguläre
Git-Operationen (Commit, Push, Merge, Fetch) transportiert. Manuelles Kopieren
von Dateien zwischen Worktrees ist nicht zulässig, da es die Git-Historie als
verbindliche Quelle unterläuft.

## Agentenaufträge

Jeder Agentenauftrag (Prompt-Datei bzw. Chat-Auftrag) für diesen Workspace
muss mindestens enthalten:

1. **Startordner** (absoluter Pfad der Session-Root).
2. **Branch**, auf dem gearbeitet werden soll.
3. **Prompt-Pfad** (falls als Datei vorhanden).
4. **Report-Pfad**, unter dem das Ergebnisprotokoll abgelegt wird.
5. **Rückgabe-Artefakt** (z. B. `RUN_REPORT.md`, `FINALIZATION_REPORT.md`),
   das den Abschlussstatus dokumentiert.

## Standard-Session-Root

Der jeweils gültige Standard-Startordner für normale Agenten-Sessions ist
zusätzlich außerhalb von Git in
`P:\GithubRepos\marcosudau-vps\voice-stt-client\ACTIVE_SESSION_ROOT.txt`
und im Überblick in
`P:\GithubRepos\marcosudau-vps\voice-stt-client\WORKSPACE_MAP.md`
dokumentiert. Maintenance-/Governance-Runs (wie `WS-NORM-002`) können davon
abweichend explizit außerhalb aller Worktrees gestartet werden, wenn der
Auftrag dies ausdrücklich vorgibt.
