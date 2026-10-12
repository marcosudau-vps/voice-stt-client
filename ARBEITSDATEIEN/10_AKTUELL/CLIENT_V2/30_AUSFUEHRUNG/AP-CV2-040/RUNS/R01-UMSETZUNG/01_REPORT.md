# AP-CV2-040 / R01 – Umsetzung

Status **REVIEW_READY** (technische Selbstqualifikation, unabhängige Abnahme offen).
2026-10-12; Branch `work/client-v2/ap-cv2-040`, Base `feat/client-v2`, erwarteter
Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`, Server
`ada13b011e1d3829f78e7f389e3b927795a2b3be`. Genau ein Umsetzungslauf,
zwischenzeitlich unterbrochen und fortgesetzt. [Originalauftrag](00_PROMPT_ORIGINAL.md),
[Statusnachfrage](ZUSATZPROMPTS/001_STATUSNACHFRAGE.md),
[Wiederaufnahme](ZUSATZPROMPTS/002_STATUSNACHFRAGE.md), [Belegindex](EVIDENCE/INDEX.md).

## Ergebnis und Herkunft

Kontinuierlicher sessiongebundener PCMflow und unabhängiger V2-Logbootstrap
sind im headless Clientpfad umgesetzt. Bestehende AudioCapture,
DualSessionCoordinator, Logparser/-transport/-cursorstore und Observability
bleiben erhalten. Neue `V2MediaConnection` komponiert diese mit V2STTSession.
Keine lokale zweite Activationautorität, kein lokales VAD-/Wake-Modell und
keine Logfinal-Injektion. Die Qt-Appkomposition erfolgt in CV2-100.

Start vom sauberen tatsächlichen aktuellen Feature-HEAD nach Fetch.
AP030 R02-ROOT_PASS, menschlicher Originalfreigabetext, gemergter PR #5,
genau ein neuer Commit, exakter Single-Parent und Baumgleichheit zur
freigegebenen Paketspitze geprüft: [Übernahmebeleg](EVIDENCE/predecessor-canonicalization.json).
Der neue Paketbranch führt dessen ACCEPTED-Status in aktuellen Einstiegen,
Manifest und Matrix nach; alte Runberichte und PASS-Belege bleiben unverändert.

Baseline vor erster Produktänderung: **128 PASS**.
Umsetzungsskizze vor Implementierung: Capture/Logs erhalten; headless
Adapter mit begrenzter PCMqueue, Mute-/Gerätebarriere, epochgebundenen
Callbacks und Logbootstrap ergänzen; Settings-/Qtports den Folgeownern
übergeben. Keine fremde WIP am Start, keine Nutzerdaten/Secrets übernommen.
Fortgeltende AP000-Arbeitsfreigabe deckt Kandidatencommit, normalen Push und
Paket-PR samt Übergabekommentar; keine kanonische Übernahme.

## Schnittstellen, Reihenfolge und Wirkungen

Öffentliche API und Beispiel: [Audio-/Logvertrag](../../../../../../../docs/protocol-v2-media.md).
`V2MediaConnection(session, capture, logs=None, settings_bootstrap=None,
queue_ms=500, recovery_interval=.25, shutdown_timeout=3)` vor run und vor
einem bereits gesetzten Bootstrap anbringen. Vorhandene Transportcallbacks
werden verkettet. Probe und eventuelle audioAvailable=false-Bestätigung
gehen der Settingsfunktion und Wiederherstellung gewünschter Suppression
voraus; READY startet Capture. Gerätefehler nach Probe meldet false, erneutes
Öffnen true. Einstellungen während Bootstrap erneut gegen Geräte/Mutezustand
prüfen. Callbackguard: genaue Bindingidentität und lokaler Queue-Epoch.

`set_device_available`/`set_hardware_muted` werden auf dem Coreloop aufgerufen,
optionales altes Binding wird abgewiesen. Änderungen schließen das lokale
Gate sofort und leeren Samples. Recovery öffnet erst nach bestätigter
Audioavailability; kein Trigger, kein Suppressionreset. LEDavailability
besitzt keinen Audio- oder Domain-Effekt. Gemeinsamer USBverlust meldet beide
Ports. Physischer Gerätemonitor/LEDadapter bleibt spätere Integration.

Capture läuft auch bei idle/waiting/recording/followup/draining, Finish,
Cancel und Wakepause. Serveraudioavailability cancelt nur die offene
Activation, erhält Session und ältere drainende Finaljobs. Netzverlust
sperrt alte Frames, leert Queues und hält keine alten Socketcallbacks gültig;
Transport/Mirror behalten ihre AP020/030-Aufräum-/Interruptedlogik und
veröffentlichte Texte. Reconnect benutzt neue Session-/Command-/Domain-IDs,
neues Logmaterial und die gewünschte Run-Suppression.

Queue validiert PCM int16 LE, Rate, Kanäle, Frames und Paketlimit.
500-ms-Senderqueue, max128 Pakete/4 MiB, alters- und epochgebundener Pop;
Capturequeue ebenfalls 500 ms (40-ms-Chunks: zwölf Pakete). Zwei getrennte
Puffer, insgesamt höchstens etwa eine Sekunde plus ein begrenzter Send.
2000-Paket-Berstentest erzeugt nur einen ausstehenden Coreloop-Handle.
Überlauf verwirft älteste Frames, Zähler bleiben sichtbar. Drei aufeinander-
folgende Sends mit weiterem Überlauf lösen kontrollierten Reconnect aus.
`counters()` veröffentlicht nur Zähler/Verfügbarkeiten, keine PCM-/Text-/Tokeninhalte.

Logbootstrap aus hello.accepted prüft WebSocket und History auf denselben
Origin. unavailable braucht keine weiteren Capabilityfelder. Token nur im
Speicher/ersten Subscribe, redigierter repr und redigierte Fehlerdiagnose.
Snapshot wiederholt keine Credentials und löscht sie nicht. Ablauf/Auth/
Cursor-/Storefehler bleiben STT-unabhängig. Der bestehende Diagnoseobserver
läuft weiterhin zuerst; ein überholtes Runtimebinding bestätigt kein Event.
Observation ist keine Mirror-/Injektionsautorität.

Cursorload/commit erweitern die bestehende atomare Persistenz um Session
und sortierte Channels. Schema1 liest historische Records weiterhin; ein
unscoped Record wird für scoped Zugriff ignoriert und beim Lesen erhalten.
Keine Config-, History-DB-, Registry- oder Credentialmigration; unveränderte
Dependencies. Logsegmentmetadaten akzeptieren Integer und opake Strings.
K-04 präzisiert die am gepinnten Server nachgewiesene Stringform; LOG-10 und
die strengen Domain-UUID-Regeln bleiben unverändert.

Shutdown stoppt Transport, cancelt/joint Media-Sender/Lifecycle, joint einen
laufenden nativen Geräteaufruf vor Capturestop und fährt Logs herunter.
Idempotenz und Reihenfolge geprüft. Asyncio kann einen festhängenden nativen
Treiber nicht hart abbrechen; 3-s-Timeout wird dem Owner gemeldet, kein
fiktiver erfolgreicher Shutdown. Logclose hat ebenfalls ein endliches Budget.

## Ausgeführte Validierung und Fehlerkorrekturen

| Prüfung | Ergebnis | Vollständiger Beleg |
| --- | --- | --- |
| Vorher-Baseline, relevante bestehende Module | PASS, 128 Tests | [baseline.txt](EVIDENCE/baseline.txt) |
| Gezielte Audio-/Log-/Transport-/Mirror-/OBSregression, warnings=error | PASS, 222 Tests | [targeted-unittest.txt](EVIDENCE/targeted-unittest.txt) |
| Vollständige Windows-Clientsuite, verbose | PASS, 1367 Tests, kein Skip | [windows-full-unittest.txt](EVIDENCE/windows-full-unittest.txt) |
| Echter gepinnter Servercheckpoint | PASS, 41 Fälle/46 bytegeprüfte Quellen | [JSON](EVIDENCE/server-audio-checkpoint.json), [stderr](EVIDENCE/server-audio-checkpoint.json.stderr.txt) |
| compileall, voice_stt_client/scripts/tests | PASS | [Log](EVIDENCE/compileall.txt) |
| Gitdiff-/Arbeitsaktenprüfung | PASS bei Abgabe | [Abgabeprüfung](EVIDENCE/submission-validation.json) |

[Windowsmanifest](EVIDENCE/windows-validation.json) enthält ausführbare
Identität, Plattform, Python/Qt/Dependencies, Befehle, Exitcodes, Laufzeiten,
Testzahlen, vollständige Loghashes, alle Produkt-/Test-/Konfigurationsblob-IDs
und lokale Laufzeitbytes. Getestete Basis plus exakter gestagter
[Produktdiff](EVIDENCE/tested-product.patch) binden die Qualifikation vor dem
Kandidatencommit. Administrative Nachträge werden über Blobvergleich belegt;
kein geänderter Produkt-/Test-/Konfigurationsstand nach der Vollsuite.
[Qualifikationsskript](EVIDENCE/qualify_windows.py) ist reproduzierbar in der
Projektvenv; Quellbytehashes werden vor und nach dem Lauf verglichen.

Ein früherer Vorprüflauf mit 1365 Tests fand fünf Regressionen im neuen
Integrationsansatz: veränderte Observerreihenfolge (zwei eingefrorene
Hookassertions plus Stalediagnose), zu stark verkürzte Protokollfehlerdiagnose
und ein Capturecallback-Runningguard. Originalreihenfolge beibehalten,
Fehlertext tokenredigiert erhalten und den unnötigen Runningguard entfernt;
ursprüngliche Assertions nicht abgeschwächt. Danach gezielt und vollständig
grün. Persistenzfixtures erhalten dieselben Erwartungen, ergänzen die reale
Session-/Channelbindung. Neue Testdoubles wurden an die tatsächliche
Transport-API und immutable Finaljob-Contextübergabe angepasst.

Der Serverlauf deckte reale opake Logsegmentstrings auf; Parser dafür gezielt
erweitert, keine Umdeutung in Domain-IDs. Der modellfreie Harness musste bei
Cancel B den noch ausstehenden Context von Final A erhalten. Explicit
ManualScheduler/Recorder-Contextsubstitution nachgebildet; serverseitige
Produktquellen unverändert. Das Storefehlerexperiment darf Close1011 sehen,
auch wenn die letzte log.error-Nachricht nicht mehr zugestellt wird; keine
garantierte letzte Nachricht angenommen. Auth/Retention/Replay/Cursorsprünge
sind echte Serverrouten-/SQLitefälle.

Alle23 AUDIO-/LOG-Requirements besitzen ausgeführte Methoden, Serverfälle
wo zutreffend, Report- und Kandidatenbezug:
[Coverage](EVIDENCE/requirement-coverage.md),
[Matrix](../../../../PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md),
[Requirements](../../../../PLANUNG/REFERENZ/TRACEABILITY/requirements.json).
Requirementtexte, Owner, Kontraktzuordnung und sourceRefs unverändert.
Status CLIENT OPEN; nur Implementierungsbelege ergänzt, keine Eigenabnahme.

## Servercheckpoint und Beweisgrenzen

Tatsächlicher Pfad: AudioCapture Callback/Processingthread → begrenzte
Mediaqueue → realer V2STTSession TCP/WebSocket → FastAPI PCMdecoder/Resampler/
Recordergate/Activationcontroller/Ledger. Separat reale SQLite-Logs,
WSsubscribe, Filter, Replay, Retentionpruning und Authrouten. Idle, Aufnahme,
ältere Backgroundfinals bei neuem Devicecancel, 16k mono → 48k stereo,
LED-only, Verfügbarkeit, Suppressionpause, Reconnect, neue Token und Shutdown
nachgewiesen. Manual-only, Wake-only und kombinierte Admission/Idle-/Pausepfade.

Substitutionen ausschließlich Hardware/Modelle: synthetische PortAudioeingabe,
GateAwareRecorder mit immutable Finaljobcontext und gehaltenem ManualScheduler,
Wakecatalog-Modellprobe. Retentiontimestamps und Storeavailability sind
isolierte synthetische Faultinputs. Kein echter Mikrofon-/USB-/LED-/Hardwaremute-
oder ASR/Wakequalitätsnachweis: **NOT_PROVEN**, in diesem Paket kein Pflichtfall;
IV2-020 und weitere spätere Plattformgates bleiben offen. Kein Live-VPS- oder
Serverprodukt-/Distributedbranch-Eingriff. Serverada13b0 bleibt gepinnt.

## Abgabe und nächste Aktion

Vollständiger Paketkandidat **REVIEW_READY**, keine offenen bekannten
Pflichtlücken aus Selbstchecks; unabhängiger Review offen. Ein Paket-PR gegen
feat/client-v2; genaue finale Spitze/Tree werden bei Veröffentlichung aus Git
genannt. Paketbranch ab Übergabe pausiert, writeOwner=null. Kein eigener
ROOT_PASS, Merge oder Folgepaketstart. Nach unabhängiger Abnahme bleibt eine
separate ausdrückliche menschliche Übernahmefreigabe erforderlich.

Veröffentlicht in [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6). Qualifizierter vollständiger Umsetzungscommit `efd8362fc63bc8a98fdbc9edccd4b4074c659393`, Tree `dd63a7822a39ca332a2a62a113ad75b16bf9397b`. Nachtrag zu PR-/Gitidentität ausschließlich administrativ; Produkt/Test/Konfigurationsblobs bleiben beim Windowsnachweis. Finale Spitze im Übergabekommentar.
