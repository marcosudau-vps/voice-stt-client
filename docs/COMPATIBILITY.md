# Release-Kompatibilität

## Gemeinsames V1-Release

| Client | Server | Status | Nachweis |
| --- | --- | --- | --- |
| `1.0.0` | `1.0.0` | gemeinsam funktionsgeprüft und separat veröffentlicht | Desktop-Client gegen Windows-/VPS-Free/Pro; Echtzeit- und Finaltext bestätigt; Ton/LED lokal bestätigt |

Server-Release: [v1.0.0](https://github.com/marcosudau-vps/voice-stt-server/releases/tag/v1.0.0),
Quellcommit `3df318635aef00a05417f74bce3f5d21b746eb59`, Candidate-Run
`36294216937`. Die veröffentlichten OCI-Digests sind Free
`sha256:c2369e49d6d780a4a8e6bfeb9aff82d0e309c9228765058e91e5b3752feecaea`
und Pro
`sha256:f3046a4b6f40f448d6dd7a4e8f3d15261a487b16ce540a5750f1d960998e5de6`.
PyPI-Free-/Pro- und GitHub-Wheels stammen bytegleich aus diesem Candidate.

Client-Release: [v1.0.0](https://github.com/marcosudau-vps/voice-stt-client/releases/tag/v1.0.0),
Quellcommit (Ziel des annotierten Tags) `2c86bfd9f2b8b3c686373ae43f6efb30d9835ee2`,
[Windows-CI `36328855780`](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/36328855780),
[Publish `36329267215`](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/36329267215).
Die veröffentlichte EXE hat SHA-256
`7c030369a9e8383cd59dcee05f2ddfac0c83adbf4cf2350dfb4e86010a440b82`,
das Wheel `1a6e10856ad8f55784ad9a9b455bb8b72cc159b0434f28848d92b83f0e463101`
und die sdist `e94a8b984e0cc63647d8ea0823f3f870e6cd49d33c21bc7e33c162031a333525`.
Beide PyPI-Dateien und alle GitHub-Assets wurden gegen den CI-Kandidaten
remote als `MATCH` geprüft. Dieser Nachtrag auf `main` entstand **nach**
dem unveränderlichen V1-Tag; er ändert keine Release-Bytes. Die gemeinsame
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
