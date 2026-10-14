# Reproduzierbare V2-Paarqualifikation (AP-IV2-010)

Der Harness startet die unveränderte Produktions-ASGI-App aus dem exakten
Servercommit `ada13b011e1d3829f78e7f389e3b927795a2b3be` in einem getrennten
Pythonprozess. Der Client verwendet V2Runtime, tatsächliches TCP/HTTP,
`/ws/v2`, `/ws/logs`, Settings, Controls, Mirror, Results, Feedback und SQLite.
Der Serverbranch muss dafür weder übernommen noch veröffentlicht werden.

Recorder/VAD/ASR/Scheduler, PortAudio und Clipboard-/SendInputausgänge sind
benannte Testgrenzen. PCM und Texte sind synthetisch. Der Recorder liefert
immutable Jobherkunft auch bei Überlappung; ein Cancel darf nicht den FIFO
eines älteren Modelljobs wecken. Die vorhandenen AP040/050/060/070/090/100-Smokes
ergänzen die Prozessprüfung. Seltene Eventreihenfolgen, Crash und native
Registrierungsfehler werden durch konkrete vorhandene Grenztests geprüft.
Dies ersetzt keine reale ASR-, Mikrofon-, USB-, Paste- oder Wahrnehmungsabnahme.

## Vorbereitung

Windows, Projektvenv Python 3.12 und ein erreichbares Server-Gitrepository mit
dem gepinnten Commit sind erforderlich. Alle Serverdateien müssen bytegleich
mit Git sein. `git archive` kann EOL-Attribute anwenden; der Exporter liest
deshalb die Blobs direkt. Sein Zielverzeichnis muss neu sein.

```powershell
$pairServerRoot = Join-Path $env:TEMP 'voice-stt-iv2-pinned-server'
$pairServerRepo = 'P:/GithubRepos/marcosudau-vps/voice-stt-server/main'
.\venv\Scripts\python.exe scripts/export_v2_server.py --repository $pairServerRepo --destination $pairServerRoot
```

Im exportierten Server eine eigene `venv/Scripts/python.exe` bereitstellen.
Im R01 wurde sie mit der Clientprojektvenv erstellt; ein expliziter lokaler
`.pth` verweist auf die bereits vorhandenen Testabhängigkeiten. FastAPI 0.115.12
und Starlette 0.46.2 liegen separat in dieser Servervenv. Erforderlich sind
insbesondere pytest, httpx, numpy, uvicorn, PyYAML, soundfile, python-dotenv,
scipy, torch, webrtcvad, onnxruntime, python-multipart und für die vollständigen
HTTP-Audiounittests faster-whisper 1.2.1 mit PyAV <19. Die tatsächlichen
Versionen stehen im kandidatgebundenen Umgebungsnachweis. Keine dieser
Testabhängigkeiten wird dadurch zur auszuliefernden Clientanforderung.

## Gesamtlauf

```powershell
.\venv\Scripts\python.exe scripts/qualify_v2_pair.py --server-root $pairServerRoot --server-repository $pairServerRepo --evidence '<Paketrun>/EVIDENCE'
```

Während des Laufs HEAD und Produkt-/Testdateien unverändert halten. Die
vollständige Clientsuite prüft unter anderem die stabile Git-Buildidentität.
Der Runner prüft alle Serverblobs und den Crossrepo-Vektorhash vor Ausführung,
führt Client-/schnelle Serverregression, Prozessfälle, konkrete Szenariobindungen,
sieben Smokes, compileall und Diffcheck aus. Vollständige Logs werden komprimiert;
Runtime, Befehle, Exitcodes und Hashes stehen in `validation.json`. Ein Fehler
oder fehlender Serverinput ist kein erfolgreicher optionaler Skip.

Der Prozessserver bindet ausschließlich Loopback auf einen dynamischen Port,
hat maximal eine Session und lokale temporäre Persistenz. Seine ausschließlich
lokalen Test-Control-Routen stimulieren Modell-/Recordergrenzen. Readiness 30s,
Clientwaits 15s, Control-HTTP 10s, Shutdown 15s und Prozesswatchdog 180s sind
begrenzt. Die vollständige Server-unit-Suite hat einen 1800s-Prozessbound.
Der Runner ersetzt keine Produktfristen durch lokale Diktattimer.

`tests.test_v2_cross_repository` führt im normalen Lauf die Bindungsprüfung aus.
`IV2_PROCESS_GATE=1` aktiviert in einem frischen Interpreter die Prozessfälle;
`IV2_SERVER_ROOT`, `IV2_SERVER_REPOSITORY` und `IV2_EVIDENCE` sind dann erforderlich.
Die vollständige Qualifikation aktiviert sie selbst. Das reguläre Clientprodukt
importiert keine dieser Hilfen.

Der Prozessmanifest kompensiert `serverCommit=unknown` mit SHA, PID, Interpreter
und vor/nach Lauf geprüften Quellhashes. Empfangene JSON-Felder werden redigiert,
PCM nur als Bytezahl dokumentiert. Logtokens bleiben memory-only und erhalten
keine Domainautorität. Ein absichtlich verlorener Final bleibt unvollständig;
Loghistory erzeugt weder Ersatztext noch automatische Wiedereinfügung.

[Paketreport und vollständige Nachweise](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md).
