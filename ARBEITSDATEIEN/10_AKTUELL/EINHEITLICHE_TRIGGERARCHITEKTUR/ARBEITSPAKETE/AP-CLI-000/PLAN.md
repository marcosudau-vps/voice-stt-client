# AP-CLI-000 – Plan

## Ziel

Der aktuelle Desktop-Client-Ist-Stand ist auf festem Start-SHA reproduzierbar
getestet. Überholte Triggerannahmen, wiederverwendbare Komponenten und
Governance-/Umgebungsabweichungen sind dokumentiert und durch passende
Charakterisierungstests abgesichert.

## Ausgangspunkt

- Branch: `feat/einheitliche-triggerarchitektur`
- Start-HEAD: `db102fdc6dd70e4de798a363608d1e7412533dd7`
- Working Tree vor Anlage dieser AP-Akte: sauber
- Geteilte Projektumgebung:
  `P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe`

## Nicht-Ziele

- keine Umsetzung des v2-Transports oder ActivationMirror;
- keine Entfernung lokaler Runtime-Autorität vor AP-CLI-010/050;
- keine Client-/Server-Schnittstellenneuerfindung;
- keine Serveränderung;
- kein Push durch den Agenten.

## Akzeptanz

- Baseline und Flakes sind reproduzierbar dokumentiert;
- überholte Clienttests sind Contractabschnitten/Folge-APs zugeordnet;
- kritische Ist-Helfer für Session, Feedback und Hotkeys sind charakterisiert;
- fokussierte und vollständige Clientsuite sind grün;
- kanonische Clientdokumentation und AP-Bericht sind aktuell;
- genau ein lokaler AP-Commit, kein Push.
