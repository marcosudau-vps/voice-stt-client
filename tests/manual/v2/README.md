# Geführte manuelle V2-Tests

Aktueller Einstieg, 19.10.2026, derselbe AP-IV2-020/R01:

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.guided_suite --profile-runtime
# oder aus dem Projekt:
.\tests\manual\v2\Start-GuidedTests.ps1 -ProfileRuntime
```

**Freigabe vom19.10.2026:** Die dedizierte Windows-Profilablage ist für diesen
AP/R01 ausdrücklich freigegeben, unter der verbindlichen Bedingung, benötigte
Nachweise anschließend ins Projekt zu kopieren und die dort angelegten
Laufzeitdaten wieder zu entfernen. `--profile-runtime` öffnet den bedienbereiten
Ablauf. Ohne dieses Argument bleibt die reine Vorschau mit deaktiviertem Start.

Das Fenster startet zunächst **nur die Aufgabenliste**, keinen Sprachclient.
Alle Schritte und Sätze stehen vorher da. Jede Aufgabe benötigt einen eigenen
**Start**. Nach wirklicher Client-/Audiobereitschaft folgen zehn Sekunden
Vorbereitung. Der aktuelle Schritt ist blau, der Testsatz groß/grün; vergangene
Schritte werden nur bei passender Beobachtung abgehakt. Die Markierung folgt
automatisch den echten Aktivierungs-, Aufnahme-, Hotkey- und Abschlussereignissen;
kurze Phasen zwischen Bildschirmaktualisierungen gehen dabei nicht verloren.
**Beobachtung / Geräteaktion erledigt** ist nur für menschliche Wahrnehmung bzw.
nicht automatisch feststellbare Schritte aktiv. **Versuch beenden** stoppt nur diesen Testclient regulär. Danach Ergebnis
auswählen und **Wiederholen**, **Übernehmen → Weiter** oder **Offen lassen → Weiter**.
Die nächste Aufgabe beginnt erst mit dem nächsten Startklick. **Übernehmen ist
kein technisches PASS.** Alle Versuche, auch Wiederholungen, bleiben erhalten.
Beenden hakt fehlende Schritte nicht nachträglich ab. Beispielsweise bleibt F9
bei einem reinen Timeout unbestätigt; die Oberfläche zeigt einen entsprechenden
Hinweis. Cancel-/None-/USB-Wartezeiten erhalten ihren tatsächlichen Countdown.

Die elf Aufgaben bündeln Finish, zwei Segmente/Follow-up, Cancel, Refresh,
None, Feedback/Timeout, Hardware-Mute, USB-Recovery, manuellen Client-Reconnect,
bewusstes Reinsert und Einstellungen/Verlauf/Logs. F8/F9/F11 im Ablauf meint
immer **Strg+Umschalt+F8/F9/F11**. F9 ist pro Aufgabe ausdrücklich Finish, Cancel
oder None; das jeweilige isolierte Profil legt dies vor dem Start fest.
Keine automatisch gestarteten Wake-Versuche, keine rohen Audioaufnahmen.

## Ziel und Isolation

Verwendet wird ausschließlich das vom Auftraggeber ausgewählte vorhandene
`wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`; die alternative Normal-V2-
Adresse ist im URL-Validator explizit zugelassen, aber kein automatischer Fallback.
Serverpin: `ada13b011e1d3829f78e7f389e3b927795a2b3be`, nach separater
[Deployment-/Image-/Quellprüfung](../../../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
Der Draht meldet weiterhin `unknown`; die datierte externe Zuordnung wird nicht
als live vom Server gemeldeter Commit ausgegeben. Pro16-ASR ist ein neues Testpaar.

Der Helfer legt **keinen Server an**, startet/stoppt keinen Server, wechselt keine
Modelle und patcht keine Serverdefaults. Sessionwünsche: Manual an, Wake aus,
Follow-up 5000 ms. Der gewünschte vorläufig weiße LED-Ring mit zwölf leuchtenden
LEDs/Speed6 und weißem Idle wird als Testkonfiguration reproduziert. HTTP,
Connect, Admission und Bootstrap erhalten diagnostisch je180s; keine feste
Wire-/Sicherheitsgrenze und kein Produktdefault wird geändert.

Vorschau-/Helferdaten liegen in **`build/ap-iv2-020-suite/`**, bewusst
Git-ignorierte Testlaufzeit im Projekt. Für vertragskonforme Realläufe und die
expliziten Pfadtests der Produktsuite ist ausschließlich die gesondert freigegebene
**`%USERPROFILE%/.voice-stt/qualification/AP-IV2-020/`** als Profil-/TEMP-/Log-/
Test-Historyablage vorgesehen. Nach beendetem Lauf und geprüftem Belegexport
nur dessen eigene Laufordner entfernen; keine V1-Pfade oder laufenden Versuche.
Keine V1-Konfiguration und keine AppData-Profile werden geladen oder verändert.
ReSpeaker wird vor jedem Versuch erneut gewählt; kein stiller Ersatz durch ein
anderes Mikrofon. Native Einfügung bleibt auf das eigene fokussierte Testfeld
begrenzt. Qt läuft im Main Thread, der Produkt-Core im separaten asyncio-Thread.
Ein echter gemeinsamer ObservabilityManager versorgt Runtime, Bridge und Desktop.

`build/ap-iv2-020-suite/active-suite.json` führt zum aktuellen Lauf. Dort stehen
`report.json` (alle menschlichen Entscheidungen), `identity.json` und je Attempt
`profile.yaml`, `events.jsonl`, `status.json`, `process.log`, isolierte Logs/History
und `test-editor.txt`. Öffentliche Belege erst nach Auswertung und Redigierung
exportieren; Laufzeittext, Datenbanken und Credentials bleiben unversioniert.
Ereignisbeobachter exportiert IDs, Zeiten und Texthashes, keine Logzugangstokens.
Ein verwaister Client stoppt bei ausbleibendem UI-Heartbeat nach15s; ein Versuch
hat einen30min-Schutz. Schließen des Fensters wartet auf reguläres Clientende.

## Ehrliche Grenzen

Die Oberfläche zeigt separat offene Pflichtanteile. Insbesondere bleiben
W01/Issue7, wiederholte Wake-/Both-Folgen, Wake-Parität und der gemischte
30min/100-Lauf zurückgestellt. Die elf Bedienaufgaben sind **Teilprüfungen**,
keine vollständige Abdeckung von M-01 bis M-12. Faulttests mit offenen Finals,
isolierter LED-/Logstörung, Run-Pausen, Sessiontransaktionen, Credentials,
elevated Ziel/Clipboardkonflikt/Crash und Frozen-Build brauchen ihre eigenen
Vorbereitungen/Nachweise. Sie werden nicht durch Klicks auf Weiter geschlossen.

## Helferprüfungen

Aktueller minimaler Abschlusslauf mit der normalen gehashten EXE:

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.frozen_acoustic_probe --human --only wake --output build/ap-iv2-020-suite/<neuer-eindeutiger-lauf> --expected-server-commit 67f3ce45f6ea1ff659382e40c194c70bd33d58ff
```

Der eigene Client startet erst nach dem Startklick. Satz und alle Schritte
vorher sichtbar, acht Sekunden Vorbereitung nach Ready, genau ein Alexa-Satz,
keine Hotkeys, keine automatische Folgeaufgabe. Bei fehlender Einfügung kann
der idle Versuch mit Abweichung beendet und dieselbe Aufgabe wiederholt
werden; Test beenden ist jederzeit erreichbar. Ein Fokusverlust nach Start
beendet den eigenen Client. Reale Ergebnisse stehen im gewählten result.json;
History-/Profilbytes bleiben privat und werden vor Cleanup hasharchiviert.

Ohne --human können bewusste WAVs über Fixtureknöpfe abgespielt werden. Ein
explizit gewählter --device verwendet dessen native Rate/Kanalzahl und echte
PortAudio-/Wiremetadaten. Stereomix ist eine andere Eingabe und ersetzt keinen
ReSpeaker-Akustikbeleg. Erfolgreicher ASRtexttransfer bedeutet keine perfekte
ASRqualität. Bewusstes --reinsert-history akzeptiert nur eigene Qualifikations-
History im genehmigten Namensraum. Keine V1-Daten oder Secrets importieren.

```powershell
.\venv\Scripts\python.exe -m unittest discover -v -s tests/manual/v2 -p test_*.py
$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m tests.manual.v2.guided_suite --self-check
```

`preflight_suite --profile-runtime` prüft nach derselben Ablagefreigabe zusätzlich echte GET-APIs und fünf Sekunden tatsächliche
Audioübertragung im Manual-only-Produktdesktop, ohne Controls/LED/Sound oder
Activation. Das ist kein menschlicher Bedien- oder Frozen-Nachweis.

Die älteren Module `__main__`, `human_test_editor`, `stepped_wake_trial` und
`observed_session` bleiben historische reproduzierbare Einstiege. Sie erwarten
die **entfernte** lokale Port18020-/AppData-Umgebung und sind für den aktuellen
Durchlauf nicht zu benutzen. `scripts/qualify_v2_session.py prepare` nicht erneut
ausführen; es gehört zur stillgelegten Infrastruktur. Die sechs ausdrücklich
freigegebenen Sprachfixtures bleiben unverändert versioniert.

## Gezielte Wiederholung nach Auswertung

Die reproduzierbaren Idle-Testwerte liegen in [calibration.yaml](calibration.yaml):
weiß, `min_brightness: 0.30`, `brightness: 1.0`. Der Starter übernimmt sie über
das bestehende Feedback-Konfigurationssystem. Die globale LED-Helligkeit bleibt
unverändert; dies sind Effektwerte, keine zugesagte absolute Lichtleistung.
Farbprofile und Produktdefaults werden damit nicht geändert. Die Untergrenze wurde am19.10.2026 über die direkte LED-Vorschau menschlich bestätigt.

`./tests/manual/v2/Start-GuidedTests.ps1 -ProfileRuntime -Tasks usb,feedback`
zeigt ausschließlich USB und Feedback, weiterhin mit eigenem Start und Wiederholen
pro Aufgabe. Öffnen startet weder Mikrofon noch Client. Jede neue Durchführung
braucht ihre eigene Auswertung/Profilarchivierung/Bereinigung.

`venv/Scripts/python.exe -m tests.manual.v2.probe_stalled_capture --profile-runtime`
prüft einen kontrollierten echten PortAudio-Stillstand mit scheinbar aktivem
Treiber am ausgewählten Pro-V2. Optional `--installed-root <Projektpfad>` für
ein entpacktes eigenes Wheel. Keine Aktivierung/Textinjektion/PCM-Datei; kein
physischer USB- oder Frozen-PASS aus dieser Diagnose.

## Direkte Idle-Vorschau ohne Client/Mikrofon/Server

`venv/Scripts/python.exe -m tests.manual.v2.idle_preview --profile-runtime`
öffnet einen eigenen START/20s/Ergebnis-Dialog. Er setzt die Werte aus
[calibration.yaml](calibration.yaml) direkt am vorhandenen LED-Controller.
Vor START keine LED-Übernahme; keine Hotkeys, Aufnahme oder Serververbindung.
Jeder Versuch wird separat behalten; Schließen/Übernehmen stoppt eigene Ausgabe.
`--self-check` prüft Qt mit Dummycontroller, ausschließlich im Projektbuildordner.

## Autonome LED-only-Störung

`venv/Scripts/python.exe -m tests.manual.v2.preflight_suite --profile-runtime --led-only-fault`
startet einen isolierten echten Source-Desktop/ReSpeaker am ausgewählten Pro-V2,
ohne Trigger/Sounds. Nur der eigene native LED-USB-Transport wird kurz gestoppt;
Sinkwechsel und mögliche automatische Wiederherstellung werden beobachtet.
Audio/Session dürfen dabei nicht wechseln. Das ist ein idle-Teilnachweis, kein
physisches Abziehen oder vollständiger M-06-/Frozen-PASS. Laufdaten anschließend
exportieren und im genehmigten Namensraum aufräumen.

## Autonome Run-Pausen und Windows-Credentials

`venv/Scripts/python.exe -m tests.manual.v2.autonomous_rest --profile-runtime`
prüft den echten Windows-Credentialspeicher mit zwei zufälligen `.invalid`-Origins:
Speichern, Ersetzen, frische Leseprozesse, Origintrennung und Löschen. Erwartungen
werden nur über stdin übertragen; keine Zugangsdaten im Aufruf oder Ergebnis.
Die beiden eigenen Einträge werden in `finally` entfernt.

Danach läuft eine tatsächliche Manual-only-Source-Runtime mit ReSpeaker am
ausgewählten Pro-V2. Sie prüft getrennte serverbestätigte Pausenmasken, zwei
manuelle Reconnects, Abbruch ausschließlich des eigenen TCP-Transports, ein
simuliertes Mute-Signal und eine neue Runtime aus demselben isolierten Profil.
Nach jedem Reconnect werden mindestens25weitere echte Audiopakete verlangt.
Kein Trigger, Speichern von PCM, Paste, globaler Hotkey, Sound, LED oder Admin-PATCH.
Der Wake-Engine-Pfad bleibt aus; das qualifiziert weder echte Wakepause noch
physisches Mute oder offene Diktate/Finals. Beide vollständigen M-Gates bleiben
offen. Ergebnisse anschließend ins Projekt exportieren und Laufzeit bereinigen.

## Serverfix/Info-Rückkehr und geführte Wakeprobe

`venv/Scripts/python.exe -m tests.manual.v2.verify_server_fix --expected-server-commit <voller bestätigter SHA> --output build/<eigenes Ergebnisverzeichnis>`
prüft den vorhandenen ausgewählten Pro-V2 über13reale Modell-/Transportfälle:
beide Wakewords nach Timeout/Finish/Cancel/Reconnect, drei Negativclips und zwei
direkte Wake-/Nutzsprachaufnahmen. Echte zuvor freigegebene WAVs, Echtzeit-Pacing,
digitale Stille als Teststimulus. Keine neue Mikrofon-/Sound-/Frozenqualifikation.
Infoidentität vor/nach und jeder echte Hello müssen zum gewählten SHA passen.
180s Modellstart-/HTTP-/Connect-/Bootstrapgrenzen, keine Serverproduktänderung.

Für aktuelle bewusste Mikrofon-/Soundproben:

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.guided_suite --profile-runtime --tasks wake_alexa wake_jarvis wake_silent --server-info ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/server-return-20261020/server-info-after.json
```

Öffnen startet keinen Client/Mikrofon. Jede Aufgabe eigener Start, vorher alle
Schritte lesen;10s Vorbereitung, dann nur das sichtbare Rufwort einmal sprechen.
Nach echtem Timeout weitere5s beobachtetes Schweigefenster mit Countdown.
Alexa/Hey Jarvis mit Sound und Alexa ohne Sound als Kontrollvergleich. Danach
selbst Versuch beenden und übernehmen/wiederholen. Der gespeicherte Servercommit
bindet den Child-Hello vor Bootstrap. Ergebnis ist menschliche Beobachtung,
kein automatischer PASS; ein neues Info-/Serverziel braucht neue Provenienz.

Ein während der bereits laufenden fünfsekündigen Wake-Ruheprüfung gewünschtes
Beenden wird vorgemerkt und nach deren Ende ausgeführt. Fenster schließen
bleibt sofortiges Abbrechen. Das ergänzt keine künstliche Testzeit nach einem
schon beendeten Client: Die Auswertung verwendet den letzten echten Audiomesspunkt
vor Stop und wertet eine zu kurze Phase als `NOT_PROVEN`.
Das neue Ruhefenster dauert sieben Sekunden, damit auch der letzte sekündliche
Audiomesspunkt mindestens fünf Sekunden Nachbeobachtung belegt.

## Gezielter Refresh-Nachweis

`verify_server_fix --controls-refresh-only --expected-server-commit <voller SHA> --output build/<eigener Lauf>`
prüft zwei echte bereits freigegebene Sprachfixtures über Produktions-Controls,
Settings, Mirror, TLS und reale ASR. Bei5000msFollow-up werden Verlängerung,
sofortiges nichtkumulatives Wiederholen, Weiterbestehen über der alten Deadline
und neuer natürlicher Timeout geprüft. Keine native Hotkey-/Mikrofon-/Pasteprüfung.

Die geführte Aufgabe `refresh` hat für die verbleibende native F8-Probe ein
eigenes entspanntes **15-Sekunden-Testfenster**. Nur ihr isoliertes Sessionprofil
wird so vorbereitet; die gewählte5sBedienkonfiguration und alle anderen Aufgaben
bleiben unverändert. Nach erstem Satz/Sprachende erneut F8, tatsächlichen
„REFRESH BESTÄTIGT“-Ack und3sCountdown abwarten, erst bei der Sprechaufforderung
den zweiten Satz sprechen. Ein Refresh-Häkchen braucht ein akzeptiertes Command
der aktuellen Activation; zwei Segmente plus Finish allein reichen nicht.

`venv/Scripts/python.exe -m tests.manual.v2.native_refresh_probe --expected-server-commit <voller SHA> --output build/<eigener Lauf>`
ergänzt die automatische native Windowskette: eigene erfolgreiche Registrierung
von Ctrl+Shift+F8, atomare SendInput-Impulse, tatsächliche WM_HOTKEY-/Qt-Zustellung,
Controls im separaten asyncio-Thread und zwei reale ASR-/Nachsprechfälle bei5000ms.
Gehaltene Modifiertasten/F8 oder belegte Registrierung brechen ab; verspätete
Zustellung darf keine spätere Session/Generation/Phase/Activation adressieren.
Keine Mikrofonaufnahme, Zwischenablage, Sound oder Server-Lifecycleoperation.
Synthetische OS-Impulse werden ausdrücklich von menschlichen Tastendrücken
unterschieden. Ein Refresh während `segment_active` ist ein Watchdog-Teilfall;
es bestätigt keinen Refresh des Nachsprechfensters. Die Testanzeige zählt
diese beiden Phasen getrennt.

## Wakepause, Recovery und expliziter BOTH-Kandidat

`verify_server_fix --pause-recovery-only --expected-server-commit <voller SHA> --output build/<eigener Lauf>`
prüft beide echten Wake-Modelle mit denselben autorisierten Sprachfixtures:
unabhängige Runpausen, bestätigte Masken über manuellen Reconnect und Abbruch
nur des eigenen TCP-Sockets, blockierter Primary und bewusste Wiederfreigabe.
Das ist ein Controls-/Settings-/Mirror-/TLS-Modellnachweis, kein nativer
Mikrofon-/Hardware-Mute-/Frozen-Nachweis.

`verify_server_fix --manual-boundary-only --expected-server-commit <voller SHA> --output build/<eigener Lauf>`
diagnostiziert die Grenze nach manueller Aufnahme im BOTH-Modus: positives
Wakefixture oder gleichlange digitale Stille, zwei Sekunden Stille vor
Finish/Cancel, sieben Sekunden danach. Diese Diagnose verwendet15000msFollow-up,
damit nicht schon der Stimulus die Aufnahme natürlich schließt. Das ist kein
5000msBediennachweis. Mit `--immediate-close` entfallen die zwei zusätzlichen
Sekunden vor dem Abschluss (vier Fälle). Alle sechs Standardfälle werden auch bei
Fehlern aufgezeichnet; FAIL bleibt FAIL. Kein Server-Lifecycleeingriff.

`--pause-manual-boundary-only` führt die Pause-/Reconnectfolge mit5000ms aus
und spielt zusätzlich das positive Fixture innerhalb der letzten manuellen
Activation. Diese überlagerte Folge bleibt als eigener Fehler-/Risikotest erhalten;
ein erfolgreicher einfacher Kontrollfall ersetzt ihren Nachweis nicht.

Die geführte Oberfläche akzeptiert ausdrücklich `--both --tasks finish wake_alexa wake_jarvis`
zusätzlich zu `--profile-runtime --server-info <aktuelle Projekt-Evidenzdatei>`.
Nur diese isolierten Aufgaben aktivieren Manual und beide Wake-Modelle gemeinsam,
mit5000msNachsprechen und320msPre-Roll als zu prüfendem Kandidaten. Die beiden
Wakeaufgaben zeigen Rufwort und Nutzsatz vor dem eigenen Start; ohne absichtliche
Pause sprechen. Die Standardaufgaben bleiben unverändert. Frühere Liveprofile
ohne explizites Pre-Roll werden dadurch nicht rückwirkend zu320msNachweisen.

`verify_server_fix --watchdog-only --expected-server-commit <voller SHA> --output build/<eigener Lauf>`
prüft den echten Warnungs-/Ablauf-/ASRpfad mit legalen Sessionwerten60000/30000/5000ms.
Ein unveränderter Einsekundenausschnitt einer freigegebenen Sprachprobe wird
als künstlicher Kontinuitätsstimulus65mal wiederholt. Der Server darf daraus
mehrere Segmente bilden; Warnung und60sFrist müssen zum tatsächlichen gewarnten
Segment passen, alle aufgenommenen Segmente benötigen ihren eigenen Final.
Dies beweist keinen60sDauersprach-/Fernseherfall ohne Segmentwechsel und keinen
30minHardwarelauf. Keine globalen Serverdefaults ändern; Sitzung danach schließen.

## Automatischer Dauerlauf und Wake-Anforderungen

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.endurance_probe --expected-server-commit <voller SHA> --output build/<neuer Lauf>
.\venv\Scripts\python.exe -m tests.manual.v2.endurance_dashboard --help
.\venv\Scripts\python.exe -m tests.manual.v2.wake_requirement_probe --expected-server-commit <voller SHA> --single 0.90 2 --output build/<neuer Vergleich>
```

Der Dauerlauf misst nach abgeschlossenem Bootstrap mindestens1800s und verteilt
100Manual-/Alexa-/Hey-Jarvis-Aktivierungen in18sAbständen. Reale freigegebene
Sprachfixtures durchlaufen AudioCapture, TLS, echte Modelle, Controls, Mirror,
Results, History, Injektionsqueue und Logging. Eigene Reconnects nach25/75 und
eigener TCP-Abbruch nach50; keine Serverneustarts. PortAudio-Eingang und
Windows-Clipboardgrenze sind kontrollierte Testadapter. Dies ersetzt keinen
physischen30minReSpeaker-/Frozen-/Feedbacknachweis. Das Dashboard liest nur
Fortschrittsdateien; sein Schließen beendet keinen Test. Lange180sBootstrap-
Timeouts berücksichtigen kalte Modelle. Jeder Lauf braucht einen neuen Ausgabeordner.

`endurance_measurements --folder build/<Lauf> --output build/<Messwerte>.json`
berechnet Latenzen, Scoreverteilungen und Ressourcenwerte erneut aus gespeicherten
Rohereignissen/Messpunkten, ohne einen neuen Client-/Serverlauf zu starten.
`endurance_assessment.assess` prüft getrennt IDs,100Completions,Messzeit und
Buildidentität. Messwertzusammenfassung und fachliches Gate bleiben getrennt.

Wakevergleiche ändern ausschließlich Sitzungseinstellungen. `sensitivity`
bezeichnet die minimale Modellscore-Schwelle: höher ist strenger. Zusätzlich
werden aufeinanderfolgende qualifizierende Frames verlangt. Unveränderte
W02-Baseline zuerst mit `verify_server_fix --pause-manual-boundary-only` prüfen;
danach Positivproben beider Modelle und negative Sprache mitprüfen. Ein
erfolgreicher Vergleich ohne reproduzierten Baselinefehler beweist keine Heilung.
Kein Parameter wird durch den Vergleich dauerhaft übernommen.

`server_defaults_probe --expected-server-commit <SHA> --output build/<datei>.json`
liest ausschließlich Info und ausgewählte öffentliche Serverdefaults mit180s
Timeout. Ein solcher Snapshot beweist keine fremden Session-Effectivewerte.
Server-Follow-up3000ms und eigener Sessionwert5000ms bleiben getrennt.

`verify_server_fix --none-matrix-only` prüft reale NONE-Controls bei Warten,
Aufnahme und Nachsprechen; `native_collision_probe --help` dokumentiert eine
separate native Windows-Kollision ohne fremde Hotkeyregistrierung anzutasten.

## Verifiziertes Aufräumen eigener Laufzeitordner

`cleanup_audit --output build/<audit>.json --active <laufender Ordnername>`
liest ausschließlich den genehmigten Profilnamensraum und prüft vorhandene
private Projektarchive. Laufende Ordner ausdrücklich ausschließen. Benötigte
Belege zuerst redigiert exportieren; vollständige private Daten bleiben
Git-ignoriert unter `build/ap-iv2-020-suite/private-archive/`.

```powershell
& .\tests\manual\v2\Remove-VerifiedRuntime.ps1 -Name '<beendeter eigener Ordner>'
& .\tests\manual\v2\Remove-VerifiedRuntime.ps1 -Name '<beendeter eigener Ordner>' -Delete
```

Ohne `-Delete` nur Prüfung. Mit `-Delete`: gebundene Archiv-/Dateihashes,
Containment, Reparse-/Prozessschutz, erneute Einzeldateiprüfung und ausschließlich
nichtrekursive LiteralPath-Löschung; danach nur nachweislich leere Verzeichnisse.
Kein Löschen des Namensraumroots, privater Archive oder der V1-Installation.


## Autonome technische Restfälle (aktuelles Pro-V2-Ziel)

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.technical_rest_probe --group all --expected-server-commit <SHA> --output build/<neuer Lauf>
.\venv\Scripts\python.exe -m tests.manual.v2.technical_rest_probe --group race --race-offset 1.78 --expected-server-commit <SHA> --output build/<neues Rennen>
.\venv\Scripts\python.exe -m tests.manual.v2.technical_rest_probe --group overlap --expected-server-commit <SHA> --output build/<neue Überlappung>
.\venv\Scripts\python.exe -m tests.manual.v2.logstore_runtime_probe --expected-server-commit <SHA> --output build/<neue Logsperre>
.\venv\Scripts\python.exe -m tests.manual.v2.native_rest_probe --output build/<neue native Probe>
.\venv\Scripts\python.exe -m tests.manual.v2.preflight_suite --profile-runtime --led-only-fault --led-open-input --expected-server-commit <SHA>
```

Runtimefälle: Produktionsruntime und reale Modelle/TLS, kontrollierte PCM- und
Clipboardgrenze. Jedes Rezept wird nach Änderungen gespeichert und neu geladen,
damit der V2-Migrationssnapshot den tatsächlich geprüften Werten entspricht.
Rennzeitpunkt ist nur ein gemessener Ausgangswert; tatsächlicher Abstand zur
Admission und Gewinner/Finalzahl müssen passen. Ein akzeptiertes Refresh nach
Wake ist keine zweite Admission. Überlappung kürzt ausschließlich führende Stille
des vorhandenen bewussten Sprachfixtures; keine Wireumordnung/-verzögerung.

Native Probe: nur eigener Qt-Editor/produktivem Win32backend. Fenster prüfen und
Startknopf anklicken; die Anwendung fokussiert ihren eigenen leeren Editor.
Kein fremder Editor, keine Elevation. Originalclipboard nur im Speicher, keine
privaten Bytes im Bericht. Workerabbrüche sind bewusst erzeugte Prozessfehler;
der Zustand unknown darf danach nicht automatisch erneut eingefügt werden.
Wenn sich der Clipboardinhalt fremd ändert, wird er nicht überschrieben.

LEDprobe aktiviert bewusst einen leeren manuellen Input vor dem nativen
LEDtransportausfall, bei realem Audio und blockierter Fremdeinfügung. Sie ersetzt
keinen physischen USB-/Mute-/Pendingfinalfall. Storeprobe hält nur eine eigene
SQLite-Schreibtransaktion; erste reale Störung ergibt DEGRADED_STORE, erst
wiederholte Fehler FAILED_STORE. Kein Server-/Default-/V1-Eingriff.

Alle Laufzeitdaten anschließend nach genehmigtem privatem Archivexport mit
Remove-VerifiedRuntime prüfen/entfernen. PIDbindungen berücksichtigen ausführbare
Datei und Erstellungszeit, weil Windows PIDs wiederverwendet. Der historische
AppData-/Loopbackstarter ist deaktiviert; aktuelle Bedienläufe verwenden
Start-GuidedTests/ guided_suite und ausschließlich den genehmigten Profilnamensraum.
