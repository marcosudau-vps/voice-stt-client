# Release-Kompatibilität

## Gemeinsames V1-Release

| Client | Server | Status | Nachweis |
| --- | --- | --- | --- |
| `1.0.0` | `1.0.0` | gemeinsam funktionsgeprüft; Server veröffentlicht, Client-Release folgt separat | Desktop-Client gegen Windows-/VPS-Free/Pro; Echtzeit- und Finaltext bestätigt; Ton/LED lokal bestätigt |

Server-Release: [v1.0.0](https://github.com/marcosudau-vps/voice-stt-server/releases/tag/v1.0.0),
Quellcommit `3df318635aef00a05417f74bce3f5d21b746eb59`, Candidate-Run
`36294216937`. Die veröffentlichten OCI-Digests sind Free
`sha256:c2369e49d6d780a4a8e6bfeb9aff82d0e309c9228765058e91e5b3752feecaea`
und Pro
`sha256:f3046a4b6f40f448d6dd7a4e8f3d15261a487b16ce540a5750f1d960998e5de6`.
PyPI-Free-/Pro- und GitHub-Wheels stammen bytegleich aus diesem Candidate.

Beim Client verweist der spätere Tag `v1.0.0` auf den qualifizierten
Client-CI-Commit. Die vier SHA-256-Werte stehen in dessen veröffentlichtem
`SHA256SUMS.txt`; dadurch muss für eine Commit-ID kein selbstreferenzieller
Dokumentations-Commit nach dem Candidate entstehen. Diese gemeinsame
V1-Zuordnung legt keine Kopplungsregel für künftige Versionen fest.

## Übergang zur laufenden V2-Entwicklung

Dieses nachträgliche V1-Release ergänzt `main`, während die V2-Arbeit bereits
auf eigenen Feature-Branches fortgesetzt wurde. Die V2-Branches werden für V1
weder verschoben noch umgeschrieben. Beim späteren V2-Release zuerst beide
Historien und die V2-Arbeitsstände sichern, dann V1-`main` und den gewählten
V2-Branch in einem eigenen Integrationszweig zusammenführen. Dabei die
V1-Release-Dateien und V2-Änderungen dateiweise prüfen, alle Tests und den
realen Client/Server-Verbund erneut qualifizieren und erst danach `main`
aktualisieren. Keinesfalls einen V2-Branch blind per Force-Push auf `main`
setzen oder V1-Commits aus der Historie entfernen.
