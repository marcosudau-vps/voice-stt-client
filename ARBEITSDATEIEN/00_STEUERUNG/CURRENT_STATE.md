## AP-IV2-020 / R04-ABNAHME – ROOT_PASS, 22.10.2026

[Unabhängige R04-Abnahme](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R04-ABNAHME/01_REPORT.md) prüft PR15-Kandidat `ca56b5ab58c47bd97bae36335e9d9314b2d35294` / Tree `631276f5ba11d49425c052e0fec5ec29636b55a9`: 6/6 REAL-Requirements PASS, R02-F02 verifiziert geschlossen, F01 durch Reviewer zurückgenommen; CI-Issue #16 technisch überprüft. CI-Run 39734511679 erfolgreich. **WAITING_FOR_APPROVAL**, keine offenen Pflichtfindings, kein Merge ohne ausdrückliche menschliche Freigabe. R03/R02-Abschnitte danach historisch.

## AP-IV2-020 / R03-KORREKTUR – 22.10.2026

Status **REVIEW_READY**. [Aktueller Korrekturbericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R03-KORREKTUR/01_REPORT.md): R02-F02 und separat Issue16 implementiert; unabhängige Nachabnahme nach grüner finaler PR-CI ausstehend. F01 zurückgenommen, Realbelege wiederverwendet. Kein ROOT_PASS/Merge. Nachfolgende datierte Stände sind historisch.

## AP-IV2-020 / R02-ABNAHME – CHANGES_REQUIRED, 22.10.2026

[Korrigierter unabhängiger R02-Bericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R02-ABNAHME/01_REPORT.md) zu PR15-Kandidat 29fb0e159c69051bedba6d097f69a5974fc09528: **F01 vom Reviewer zurückgenommen** (Dauerlauf und reale USB-Recovery dürfen komplementär belegt werden). **Alleiniges offenes Pflichtfinding F02** zur Sessionledger-/Terminal-Retention. Separates [CI-Issue #16](https://github.com/marcosudau-vps/voice-stt-client/issues/16). Kein ROOT_PASS/Merge. Frühere R01-REVIEW_READY-Angaben sind historisch.

## AP-IV2-020/R01 – REVIEW_READY,22.10.2026

[Abschlussbericht40](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/40_REVIEW_READY_UND_KONSOLIDIERTE_QUALIFIKATION.md): **REVIEW_READY**: native ReSpeaker-Altfinal/Recovery/Runpausen und finale normale EXE mit A-final während B-Sprache sowie zwei sichtbaren Ausgaben belegt. Vollständige1400Windows/0Skips/79Module,83Helfer/0Skips,compileall PASS. Produkt0f6c85e/Server67f3ce45 unverändert.18letzte eigene Profile archiviert entfernt, externer Namensraum leer. Zusammengesetzte Methoden/Grenzen und historische Fehlläufe explizit dokumentiert; kein eigener ROOT_PASS. Gleicher R01/Paketbranch/PR15; Schreibhoheit für unabhängigen Review zurückgegeben.

Nachfolgende datierte Zwischenstände sind historisch und durch Bericht40 konsolidiert.

## AP-IV2-020/R01 – Laufzuordnung und Hilfstimer,22.10.2026

[Bericht39](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/39_LAUFZUORDNUNG_UND_TESTTIMER.md): Mensch meldet eingefügten Text/Fensterschluss; gespeicherte Vorbereitung dagegen TIMEOUT ohne Clientstart, Satz nicht mehr bekannt. Beobachtung erhalten, Zuordnung NOT_PROVEN. Hilfstimer korrigiert: vor Start unbegrenzt warten, Laufbudget erst ab Clientstart.82Helfer/0Skips und compileall PASS, Produkt0f6c85e unverändert. Alle verbliebenen eigenen Profile/Helfer-TEMP archiviert entfernt, genehmigter Namensraum leer, kein laufender Test. Keine weitere Sprach-/Wahrnehmungsprobe gestartet. Technische Restmatrix bleibt BLOCKED, gleicher R01/PR15.

## AP-IV2-020/R01 – Abschlussproben,22.10.2026

[Bericht38](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/38_ADMIN_UAC_EXE_UND_MINIMALER_ABSCHLUSS.md): Adminguard positiv und generationgebunden, erhöhtes eigenes UAC-Ziel/APIstatus und drei native Stereomix-EXE-Einfügungen belegt. Erste ReSpeaker-ASR korrekt, automatische Einfügung fehlte; bewusster EXE-Reinsert erfolgreich. Minimaler Ein-Satz-Wakeversuch ohne Hotkeys vorbereitet, Wiederholen/Weiter repariert.80Helfer/Qt PASS; Produkt0f6c85e und1400Windowsbeleg unverändert. Wahrnehmungsabfragen menschlich abgeschlossen. Zehn beendete Profile plus Helfer-TEMP hashgesichert entfernt; nur ungestartete Abschlussprobe bleibt. Technische Restgrenzen NOT_PROVEN, BLOCKED/gleicher R01/PR15.

## AP-IV2-020/R01 – autonome Restprüfung,21.10.2026

[Bericht37](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/37_AUTONOME_RESTQUALIFIKATION_UND_MENSCHLICHE_GRENZEN.md): Autonome Restprüfung:29aktuelle Runtime-Kombinationsfälle, beide engen Renngewinner,3Altfinal/B-Sprache-Paare, native Clipboard-/Prozessabbruchfälle, echter LED-only-Ausfall bei offenem Input und separate SQLite-Logstoresperre PASS_SCOPED. Qualifizierte EXE startet nativ mit realem ReSpeaker/Ready. Neue1400Windows/0Skips,73Helfer/0Skips und Qt/retirierter Starter PASS; Produkt0f6c85e unverändert. Alle19neuen Laufzeitordner gesichert entfernt. Menschlicher Rest: gültiger Admincheck, erhöhtes Ziel/UAC, finaler EXE-/physischer/Umwelt-/Overlay-Abschluss einschließlich T02/T03; W02 bleibt geschlossen. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.

## AP-IV2-020/R01 – W02 geschlossen, Freigabereste konkretisiert,21.10.2026

[Bericht36](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/36_W02_ABSCHLUSS_UND_FREIGABERESTE.md): W02 auf ausdrückliche menschliche Entscheidung als aktuell nicht mehr reproduzierbar geschlossen; kein eigener Freigabeblocker. Historische2FAIL erhalten, keine identifizierte Codekorrektur behauptet. Rest: technische Kombinationen, finaler EXE-/Admin-/Clipboard-/physischer Abschluss und Akten/ unabhängige Abnahme. Keine Wiederholung bestandener Standarddiktate, USB-Grundprobe oder des identischen30min100-Replaylaufs. Gesamtpaket BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.

## AP-IV2-020/R01 – autonomer Dauerlauf und Aufräumen abgeschlossen,21.10.2026

[Bericht35](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/35_DAUERLAUF_WAKEANFORDERUNGEN_UND_AUFRAEUMEN.md): Automatischer zusammenhängender1800.015s/100Activations-Lauf mit echten Modellen PASS_SCOPED;100Finals/100Historyeinträge/100kontrollierte Injektionsversuche, drei eigene Recoveryaktionen. Physische/Frozen-M12-Anteile offen. W02 unverändert0/2reproduziert, historische2FAIL bleiben offen;0,90/2Frames erhält beide Positivfixtures,3/5Frames verfehlen Jarvis. Keine Defaultübernahme. Alle26eigenen externen Laufzeitordner hashgesichert entfernt.70Helfer/Qt und neue1400Windows/0Skips PASS; Produkt0f6c85e unverändert. Zwei Fehlversuche separat erhalten. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.

## AP-IV2-020/R01 – BOTH abgeschlossen, Restgates konsolidiert,20.10.2026

[Bericht34](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/34_BOTH_ABSCHLUSS_UND_KONSOLIDIERTE_RESTGATES.md): Drei übernommene BOTH-Aufgaben PASS_SCOPED: natives Manual-F8/F9 und beide direkten Wake-Nutzsätze genau einmal ohne Rufwort;18,782/23,313s echte Ruhe ohne Zusatzwake. Erster Alexa-Versuch bewusst wiederholt, bleibt NOT_PROVEN. Realer Watchdog55,062sWarnung/60,015sAblauf und3gebundene ASRfinals aus demselben Rohdurchlauf nach phasengenauer Nachauswertung PASS_SCOPED; falsche Einsegmentannahme als Hilfstest-FAIL erhalten.61Helfer/Qt PASS, Produkt0f6c85e/1400Windowsbeleg unverändert. Keine identischen Sprechwiederholungen; technische/EXE-/Dauerreste gebündelt, W02 offen.23Aufräumreste automatisch gesperrt. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.

## AP-IV2-020/R01 – Mute/Reinsert bestätigt, überlagerter Wakefall offen,20.10.2026

[Bericht32](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/32_MUTE_REINSERT_UND_WAKEPAUSEN.md): Hardware-Mute27,297s/zehn blockierte F8 und bewusste Wiederfreigabe/1exakte Einfügung sowie Reinsert1Final/2passende automatische+manuelle Ausgaben PASS_SCOPED. Zwei aktive Wake-Modell-/Pausen-/Reconnectfälle PASS_SCOPED. Erweiterte Pause→Recovery→manuelle Aufnahme mit Wakefixture→Cancel erzeugt zweimal Zusatzwake bei Stille: IV2-020-W02 offen, Ursache noch einzugrenzen; kein Serverfix vorgenommen.59Helfer/Qt PASS, Produkt0f6c85e unverändert/1400Windowsbeleg erhalten.22gesicherte Aufräumreste automatisch gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – native Refreshpfade geprüft,20.10.2026

[Bericht31](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/31_REFRESH_AUFNAHME_UND_NATIVER_NACHSPRECHPFAD.md): Menschlicher nativer F8-Refresh während segment_active, F9/Finish und2exakte native Einfügungen derselben Activation PASS_SCOPED; menschlicher15sNachsprechfall bleibt phasenbedingt NOT_PROVEN. Ohne weitere menschliche Wiederholung:2reale native Windows→WM_HOTKEY→Qt→Controls→ASR-Nachsprechfälle bei5000ms/6Callbacks PASS_SCOPED, Fristverlängerung/nichtadditives Wiederholen/Timeout bestätigt. T04 unterscheidet Phasen;56Helfer/Qt PASS, bytegleiches Produkt0f6c85e behält1400Windows/0Skips.21hashgesicherte Aufräumreste automatisch gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – Controls/Logansicht und Refresh,20.10.2026

[Bericht30](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/30_CONTROLS_LOGANSICHT_UND_REFRESH.md): Denkpause mit2Segmenten/F9/2exakten nativen Einfügungen, Cancel mit82,969s weiterer Audioübertragung ohne Ausgabe und menschlich ausdrücklich bestätigte Server-/Tab-/Logansicht PASS_SCOPED; T01 geschlossen. Native Refreshprobe enthielt kein Refresh und bleibt NOT_PROVEN, lieferte aber korrekt gebundenen Altfinal-nach-Neustart-Beleg203ms. Zwei autonome reale ASR-/Controls-/Deadline-Refreshfälle PASS_SCOPED. T04-Testhäkchenfehler mit Regression/Qt korrigiert; nur native Refreshprobe entspannt erneut vorbereiten, übrige vollständige Gates offen. Produkt0f6c85e/Server67f3ce45 unverändert, gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – W01-Rückkehr erfolgreich,20.10.2026

[Bericht29](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/29_W01_KONTROLLE_BESTAETIGT_UND_RESTGATES.md): W01-Kontrolle Alexa ohne Sound PASS_SCOPED: genau1Wake/Activation/Timeout,29,765s weitere echte Audio-Nachbeobachtung ohne Folgetrigger,1543Pakete, keine Sprache/Final/Paste, menschlich Wie erwartet, Exit0. Damit alle3vorgesehenen Livekontrollen und13Modellfälle erfolgreich; konkretes W01 CLOSED_VERIFIED_SCOPED. Vollständige M-/Frozen-/Both-/Nutzsprachgrenzen-/30min100-Gates bleiben offen. Produkt0f6c85e/Server67f3ce45 unverändert;19private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – aktuelle Wake-Liveauswertung,20.10.2026

[Bericht28](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/28_WAKE_LIVEAUSWERTUNG_UND_RUHEKONTROLLE.md): Aktuelle reale Alexa-/Hey-Jarvis-Proben mit Sound je genau1Activation/Timeout,20,625s bzw6,954s weitere belegte Audiobeobachtung ohne Folgetrigger, menschlich Wie erwartet: PASS_SCOPED. Sound-aus-Kontrolle endet vorzeitig: nur1,875s Audio nach Timeout, NOT_PROVEN statt angenommener5s. Nur diesen Fall wiederholen; Testoberfläche wartet eine bereits laufende Ruhephase nach explizitem Beendenwunsch ab, Fensterclose bleibt Abbrechen.48Helfer/Qt und neue1400Windows/0Skips PASS. Produkt0f6c85e/Server67f3ce45 unverändert;18private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – Rückkehr vom Serverfix,20.10.2026

[Bericht27](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md): Neuer Pro-V2-Server67f3ce45/Tree74f37cad/Version2.0.0 über öffentliche Info, passenden Gitbaum/-datum und echten Hello bestätigt; Wakefix-Mergee761b973 direkter Parent.13reale Modellreplays/18Activations ohne Zusatzwake in geprüfter digitaler Stille PASS_SCOPED, native Source/ReSpeaker133Pakete und neue1400Windows/0Skips/43Helfertests PASS. W01-Live-Mikrofon-/Schweige-/Soundvergleich vorbereitet, keine vollständige M-/Frozen-/30min100-Abnahme; Clientprodukt0f6c85e unverändert.17beendete private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – autonome Restprüfungen,19.10.2026

[Konkrete Restliste und neue Nachweise](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/26_AUTONOME_RESTPRUEFUNG_UND_OFFENE_PUNKTE.md): Windows-Vault-Lebenszyklus mit frischen Prozessen/Origintrennung und Löschung PASS_SCOPED; reale idle-Runpausen über zwei manuelle Reconnects/eigenen TCP-Abbruch/Software-Mute sowie frische Runtime PASS_SCOPED. Wakeengine aus, keine Aktivierung/Paste,5000ms erhalten;1400Windows/0Skips und36Helfertests PASS. Produkt0f6c85e unverändert. Offene Kombinationen, Frozen/Admin/W01 und Gesamtgates bleiben;15private gesicherte Laufordner automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – Idle bestätigt, LED-only-Störung autonom geprüft,19.10.2026

[Bericht25](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/25_IDLE_BESTAETIGT_UND_LED_ISOLATION.md): Weiß/min30%/peak100% am realen ReSpeaker nach20s ausdrücklich bestätigt und reproduzierbar gespeichert. R11 CLOSED, Produkt0f6c85e unverändert. Zusätzlicher nativer LED-only-Transportausfall bei idle isoliert: automatische LED-Recovery, Audio/Session stabil,59→210Frames, keine neue Activation/AudioAvailability-Mutation. Erster fehlerhafter Hilfstest bleibtFAIL wegen falscher Persistenzannahme; neue33Helfertests PASS.1400Windows-/Buildbeleg am bytegleichen Produkt bleibt gültig. Übrige Real-/Frozen-/W01-Gates offen, kein REVIEW_READY; gleiche R01/PR15.13gesicherte externe Aufräumreste durch automatische Freigabeprüfung „blocked by policy“ nicht gelöscht.

## AP-IV2-020/R01 – direkte Idle-Vorschau vorbereitet,19.10.2026

[Bericht24](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/24_IDLE_ZIELZUSTAND_UND_DIREKTVORSCHAU.md): Letzte menschliche Akzeptanz bewahrt, aber kein Aktivierungs-/Idle-Zielübergang im Lauf, daher30/100%-Kalibrierung NOT_PROVEN. Dauerhafte LED-only-Vorschau mit eigenem START/20s/Übernehmen erstellt, kein Mikrofon/Server/Hotkey nötig;31Helfertests/Qt-Selbstcheck PASS. Produkt0f6c85e unverändert, R11 CLOSED. Neue physische Bewertung und weitere M-/Frozen-/W01-Gates offen; BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher PR15. Zehn gesicherte externe Restordner automatisch mit „blocked by policy“ gegen Löschen gesperrt.

## AP-IV2-020/R01 – physische USB-Recovery bestätigt, Idle-Feinabstimmung offen,19.10.2026

[Neuer Nachweis](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/23_USB_BESTAETIGT_UND_IDLE_KALIBRIERUNG.md): R11 CLOSED am unveränderten Produkt0f6c85e; echter USB-Ausfall/Servercancel/Wiederöffnung und bewusstes neues F8/F9-Diktat exakt einmal eingefügt. Manual-Timeoutfeedback menschlich bestätigt. Gewünschte weiße Idle-Pulsvariante30/100% als bestehende Testkonfiguration gespeichert, Sichtbestätigung offen; Farbprofile ausdrücklich später.29Helfer-/1400Windows-Tests ohne Skips PASS. Gesamtpaket weiter BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleiche R01/PR15, kein REVIEW_READY. Neun gesicherte beendete externe Laufordner wegen automatischer Freigabeprüfung „blocked by policy“ nicht gelöscht.

## AP-IV2-020/R01 – R11 technisch korrigiert, Realgates offen

[Auswertung und Belege](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/22_GEFUEHRTER_DURCHLAUF_UND_USB_RECOVERY.md): 15 menschliche Versuche/14 Activations am alten Sourceprodukt7bb5646. Teilnachweise getrennt von vollständigen M-Gates; USB-Test FAIL. Autorisierte Recoverykorrektur am neuen Produkt `0f6c85e0ecf971e596aae1b7d265dad7132754e2`: 48 gezielte/1400 volle Windows-Tests ohne Skips, neue EXE/Wheel/sdist und native Source-/Wheel-Stillstandsprobe PASS. Physische USB-Wiederholung, Feedbackbestätigung, endgültige Frozen-/Realqualifikation und W01 offen. Workflow IMPLEMENTATION_IN_PROGRESS, Gesamtabnahme BLOCKED; kein REVIEW_READY. Sieben privat gesicherte externe Laufordner wegen automatischer Freigabeprüfung nicht gelöscht; Aufräumpflicht bleibt offen.

## AP-IV2-020/R01 – unabhängige Restarbeit zulässig,19.10.2026

[Bericht19: W01-Umfang, späterer Server-FIX und tatsächlich ausgewähltes V2-Ziel](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
Unabhängige Client-/Windowsprüfungen vorziehen; vollständige Abnahme bis W01 und
betroffenen Realgates weiter BLOCKED; ausführbarer Workflow IMPLEMENTATION_IN_PROGRESS. Vorhandenes Pro-V2
/ws/v2 und Normalalternative durch Menschen benannt, Pinada13b0 separat über
Build-/aktuelle Image-/Git-/Wheel-/Runtimequellbelege bestätigt trotz Wireunknown.
Kein neuer Server, kein Deployment/Neustart; gleiche R01/Branch/Draft-PR15.

## AP-IV2-020/R01 – zusätzlicher Server entfernt, 18.10.2026

Auf ausdrücklichen Wunsch eigene AP020-Servercontainer, zugeordnete Images und
Datenvolumes entfernt; Starter deaktiviert. Keine Wiederanlage oder andere
Serverwahl ohne neuen Auftrag. Historischer Commit-Audit: Referenzada13b0,
555 Gitblobs/56 Quellnachweise identisch; serverabhängige Einzelansprüche ohne
belastbare Bindung nicht abnahmewirksam. W01/Issue7 und Realgates bleiben offen,
BLOCKED / SERVER_FIX_REQUIRED. Berichte15/16 im selben R01 sind maßgeblich.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – BLOCKED / SERVER_FIX_REQUIRED, 18.10.2026

IV2-020-W01: zwei echte serverseitige Alexa-Activations nach einmaliger Wakephrase;
zweiter Start303ms nach Timeout, Score0,991943. Echter Modellreplay reproduziert
nach Inferenzpause/Freigabe zweiten Treffer bei digitaler Stille nach240ms;
Resetkontrolle ohne zweiten Treffer. Exakte historische akustische Ursache ohne
PCM NOT_PROVEN. Serverfix gesondert zu beauftragen; kein Servercode geändert.
Clientprodukt7bb5646, Parent und Draft-PR15 bleiben unverändert. LED-Muster
menschlich grundsätzlich positiv bewertet. Realgates/T01 offen, kein REVIEW_READY.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – UX03 technisch korrigiert, Realgates offen, 18.10.2026

Neues qualifiziertes Produkt `7bb564690911d52f6dfe884955ddeb6a27eea6ad`. Fehlender Stoppton bei
serverbestätigtem Eingabeschluss (`finished`/`timed_out`) behoben, direkt
freigegeben im selben R01. 76 gezielte/1398 volle Windows-Tests PASS,1964 Server/
14 erwartete Skips,11 Prozessfälle,17 Grenzen,7/7 Smokes. Neue EXE/Wheel/sdist
und native EXE-/Wheel-Laufzeit am lokalen gepinnten Server PASS. Echte
ReSpeaker-/Qt-Probe: genau ein Stop-Playerlauf, Ready/playing=true; menschliches
Hören am echten Alexa→15s-Timeout bestätigt: UX03 CLOSED. T01-Log-UI-Bestätigung offen; übrige
M-Fälle/30min100/Endkalibrierung weiter NOT_RUN/NOT_PROVEN. Kein REVIEW_READY.
[Aktuelle Sound-/LED-/Triggerübersicht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/10_FEEDBACK_UEBERSICHT.md). Acht Alexa-Treffer mit
Scores0,908322..0,999994; Schwelle0,85 nur ungesetzter Offlinekandidat.
Dauerhafter Desktopstarter bleibt verfügbar. V1/VPS geschützt; gleicher PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – IN_PROGRESS, UX02 technisch und real geschlossen, 16.10.2026

Produkt d95043e nach freigegebener Modifierkorrektur:1390 Windows-Tests/0 Skips,1964 Servertests/14 erwartete optionale Skips,11 Prozessfälle,17 Grenztests,7 Socketsmokes PASS. EXE/Wheel/sdist und native Produkt-/Serverlaufzeit erneut qualifiziert; reale Recovery, ReSpeaker-Desktop-Neustart und sechs Modellreplays neu gebunden. Physische Modifierprobe PASS:250ms tatsächliche Halte-/Freigabe, exakte einmalige native Ausgabe/menschlich bestätigt; UX02 CLOSED. Zusätzlich realer Manual-F8→Sprache→F9-Pfad PASS: ein erkannter Final exakt nativ eingefügt/menschlich bestätigt. Freie isolierte Both-Instanz für LED/Sound/Overlay aktiv. Genannte Einstellungstabs über zweiten lokalen Dialog vorhanden; Teststarter-Logmanagerlücke T01 festgestellt, Korrektur vorbereitet/gezielt geprüft, native Bestätigung nach abgestimmtem Neustart offen. Übrige Realgates/Kalibrierung weiter offen. Kein REVIEW_READY, gleicher R01/Paketbranch/PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – BLOCKED durch UX02, 16.10.2026

[Testclient](../../tests/manual/v2/README.md) fertig: feste Schritte, wandernder Fokus, Countdown8s, eigener Start/Wiederholen/Abbrechen. Zehn Helferprüfungen/Qt und volle1378Windows-Regression PASS. Manuelle F8/F9-Steuerung PASS, Zieleinfügung FAIL (Shift gehalten). Produktausnahme noch nicht freigegeben; Produkt17261e6 unverändert. Derselbe R01/Branch/Draft-PR15; kein REVIEW_READY. [Aktueller Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md).

### Vorheriger datierter Zwischenstand

# AP-IV2-020 – IN_PROGRESS, Phase C läuft, 2026-10-15

Kanonischer Parent `b80ed8b` unverändert, Vorgänger AP010 tatsächlich ACCEPTED.
Paketbranch `work/client-v2/ap-iv2-020`, kumulativer Draft-PR #15, derselbe R01.
Ausdrücklich freigegebener Reconnect-/Recovery-Audit abgeschlossen: zehn technische
Findings behoben. Recoveryprodukt41ca761 historisch; zusätzlicher freigegebener UX01-Fix am Produkt `17261e6`, neue EXE/Wheel/sdist sauber gebunden.
1378 Windows-Tests ohne Skips, 11 Prozessfälle, alle sieben Server-Smokes PASS;
1964 Server-Unit-Tests PASS/14 ausgewiesene optionale Skips. Echter ReSpeaker- und
Desktop-Reconnect, HTTP-/Ackausfall, drei Neustarts, Shutdown und Frozen-GUI grün.
M-Fälle, echte Wakepositive/Nutzsprachgrenze, Wahrnehmung/Kalibrierung und30min100
bleiben NOT_RUN/NOT_PROVEN. Manualbaseline real erfolgt, Follow-up5000ms menschlich gewählt.
Hostspeicherreserve nach menschlicher Aktion wiederhergestellt; Wakeclient bereit.
Sechs bewusste Audiofixtures auf ausdrücklichen Wunsch versioniert. Reale ASR-Replays zeigen
320ms Pre-Roll als geeigneten Livekandidaten; neue Wake-/Controlprobe mit Fokusbarriere folgt.
UX01 ausdrücklich freigegeben und umgesetzt; gezielte100 und neue volle Produkt-/Build-/Paarrequalifikation PASS. Native UX01-Ausgabebestätigung erfolgreich; UX01 geschlossen.
[Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/VPS geschützt; Server nur lokal. Kein REVIEW_READY, Eigenreview, Merge oder Release.


Neuer Produkt-/Build-/Paarstand17261e6 autonom qualifiziert; native Ausgabe und zwei einzeln gestartete direkte Wake-Nutzsätze mit Leerzeichen bestätigt. F9 und vollständige Realgates bleiben offen; nächster Einzeltest mit eigenem Start vorbereitet.

## Vorheriger datierter Stand

# Client V2 – AP-IV2-010 / R01-UMSETZUNG / REVIEW_READY, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Client V2 – AP-CV2-110 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-14

[Paket-PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base `feat/client-v2`, Head `work/client-v2/ap-cv2-110`.

Aktiver Arbeitsblock [CLIENT_V2](../10_AKTUELL/CLIENT_V2/README.md);
[Einstieg Planung](../10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).
AP000 bis AP100 tatsächlich ACCEPTED auf feat/client-v2; letzter kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100-PASS, menschlicher R06-Auftrag und wirklicher PR12-Squash
[verifiziert](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).

AP110 auf `work/client-v2/ap-cv2-110`: ausführbare V1-Autoritäten entfernt,
Migrationreader und Utilities erhalten, Source/Wheel/sdist/Frozen mit belegter
Helloidentität und nativer Windows-GUI qualifiziert. Windows **1353 PASS**,
gezielte **234 PASS**, Servercheckpoint **17 PASS**, compileall/diffcheck und
alle Build-/Ressourcen-/Installationschecks PASS. Getesteter Produktcommit
`cf42a2a9d96c1ebc88035817a5d529dfe04e4306`; finale PR-Spitze ergänzt ausschließlich administrative Unterlagen.
[Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Kompatibilität](../../docs/compatibility.md), [Runtime](../../docs/protocol-v2-runtime.md).

Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.
Bekannte Legacy-Profile und History werden mit Backup migriert; kein V1-Fallback.
Builds liegen lokal unter dist, kein veröffentlichter Release. Keine realen
ASR-/Mikrofon-/USB-/Fremdanwendungs-/Wahrnehmungsgates behauptet.

**Aktueller Reviewabschluss (2026-10-14):** [AP110 R02 unabhängiger ROOT_PASS](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) auf `44cf9a8fd1669242c00997966addc3667d448aa0`; FINAL-03 bis FINAL-09 technisch PASS, keine offenen Pflichtfindings. **ROOT_PASS** mit menschlicher **R03-Freigabe** – finale Git-/CI-Prüfung und Squash stehen aus. Kein AP-IV2-010-Start zuvor.

**Übernahmefreigabe 2026-10-14:** [R03-Originalprompt](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) und [R03-Abschlussablauf](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/01_REPORT.md) dokumentiert. Aktuelle Phase **READY_FOR_CANONICALIZATION**; unabhängiger R02-ROOT_PASS unverändert. Nach finaler CI und Head-/Baseprüfung ist der einzelne Squash-Merge von PR #13 erlaubt. Ohne belegten GitHub-Merge noch nicht ACCEPTED; kein Release/Tag/Servermerge/AP-IV2-010.

---

## Historischer AP100-Stand vor dessen tatsächlicher kanonischer Übernahme

# Client V2 – AP-CV2-100 / R05-ABNAHME / ROOT_PASS, 2026-10-13

AP-CV2-000 bis AP-CV2-090 auf `feat/client-v2` ACCEPTED; letzter kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der aktuelle AP-CV2-100-Paketbranch `work/client-v2/ap-cv2-100` ([PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)) wurde unabhängig am Kandidaten `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` geprüft: **technischer ROOT_PASS**, 6/6 Paketrequirements erfüllt, `CV2-100-R03-F01` geschlossen.

[R05-Abnahmebericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md), [unabhängige Evidenz](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/EVIDENCE/INDEX.md), [R04-Korrekturbelege](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Extern qualifizierte Windows11-Suite **1581 PASS**, gezielte Tests **210 PASS**, **17** echte gepinnte Client-/Servercheckpoints am Server `ada13b0`, GitHub-Actions-CI **38394758805** erfolgreich auf dem geprüften Kandidaten. Reviewer hat diese Belege unabhängig geprüft, aber keine eigene Windows-/Hardwaretestausführung vorgenommen.

**Nächster Schritt: WAITING_FOR_APPROVAL.** Ausdrückliche menschliche Freigabe des Squash-Merges von PR #12 erforderlich, davor aktueller PR-Head, unveränderte Base, ausschließlich administrative R05-Nachträge sowie finale CI prüfen. Kein Merge und kein Start von AP-CV2-110 durch dieses Review.

---

## Historischer R04-Stand vor unabhängigem R05-Review

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json), [Runtimeinterfaces](../../docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

## Historischer Stand vor AP-CV2-020

**Aktuelle unabhängige Abnahme: CHANGES_REQUIRED.** Einziges Pflichtfinding `CV2-060-R02-F01`; [R02-Report](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R02-ABNAHME/01_REPORT.md). Minimaler Docfix und Nachprüfung, kein Merge/AP070.

# CURRENT_STATE – AP-CV2-010

AP-CV2-000 tatsächlich CANONICALIZED/ACCEPTED auf `1cf076bd2ed56929b1a3780bc140da51348a8295` (PR #2; PASS und menschliche Freigabe vorhanden). Aktiver Auftrag AP-CV2-010, ROOT_PASS (R02); Workflow WAITING_FOR_APPROVAL auf `work/client-v2/ap-cv2-010`. [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json), [Paketakte](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md). Kein automatischer Folgepaketstart.

Die folgende datierte Steuerung bleibt Historie.

# CURRENT STATE

Stand 2026-10-11. [Aktiver Client-V2-Block](../10_AKTUELL/CLIENT_V2/README.md). **AP-CV2-000 ROOT_PASS / READY_FOR_CANONICALIZATION** nach R04-Produktreview und R05-Windows-Volltest (1233 PASS). [Abnahme/Freigabe](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md), [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Nächste Aktion: finale CI/Base050e776 prüfen und gemäß gesichertem Nutzerauftrag genau einen AP-CV2-000-Squash auf feat/client-v2 ausführen. Erst tatsächlicher Git-/PR-Nachweis gibt AP-CV2-010 frei; keine automatische Umsetzung. Der versionierte Stand bleibt vor Merge ROOT_PASS. Nach Merge kanonischen Abschluss aus Git/PR ableiten und auf dem nächsten Paketbranch nachführen.

[Planung/Rollen](../10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Nächster-Schritt-Skill](../10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md). Planrevision10, Rollenregelversion7: Windows-Vollsuite im Umsetzungslauf, ChatGPT-Reviewer prüft Code und gültige Belege ohne Pflichtwiederholung. Serverada13b0 bleibt Distributedreferenz; Logging/Feedback-Bestand und spätere reale Hardwaregates bleiben erhalten. Keine externe Arbeitsablage erforderlich.

Die folgende Vorfassung ist historische Provenienz, keine aktuelle Arbeitsanweisung.

## Historische Vorfassung – 2026-08-29

Active Workstream:
Einheitliche Triggerarchitektur

Previous Milestone:
Logging / Observability Teil A
CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE / ARCHIVED

Formal G-OBS-V1:
NOT PASSED

Deferred:
Logging / Observability Teil B
Start nach Trigger mit OBS-100 (bis OBS-180)

Next:
Triggerarchitektur: Serverlinie weiter auf `AP-SRV-070` (Legacyabbau und
Protokollgrenze); letzter kanonisch abgeschlossener Server-AP ist `AP-SRV-060`
(Serverbranch `feat/einheitliche-triggerarchitektur` =
`c82923fc6ce889b4dfbbde1f9877b8b76481a1e8`). Die Clientlane ist technisch
entblockt (technische Dependency AP-SRV-040 erfüllt), wird aber bewusst bis
zum Abschluss der Serverlinie AP-SRV-060 → AP-SRV-070 deferred.
Distributed-/Review-Branches sind Execution-Provenienz und keine neue
kanonische Basis; die zentrale Paketkette liegt auf
`feat/einheitliche-triggerarchitektur`.

---

## Logging / Observability Teil A – Zusammenfassung

Der vorgezogene Logging-/Observability-Workstream (OBS-000 bis OBS-060 plus
Diagnose-UI-Nachbesserung) ist mit Run `OBS-CLOSE-001` (2026-08-23)
organisatorisch abgeschlossen und archiviert:

- Status: `CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`.
- Formal: `G-OBS-V1 NOT PASSED` (kein formales finales Gate-PASS; bestimmte
  manuelle/formale Restabnahmen — u. a. `M-1…M-11` — wurden bewusst auf den
  nach der Trigger-Migration maßgeblichen Gesamtzustand verschoben).
- Archivpfad:
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/`
- Kanonische Produktdokumentation: `docs/observability/`
- Die vollständige Gate-für-Gate-Historie (OBS-000 bis OBS-060, alle Runs,
  Gate-Reviews, Korrekturläufe, Befunde) ist verlustfrei erhalten in:
  - `ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md` (append-only, aktiv, nicht
    verschoben),
  - der archivierten Arbeitsakte unter obigem Archivpfad (Runs, Evidence,
    Work Packages),
  - dem historischen Vor-Kompaktierungs-Snapshot dieser Datei:
    `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/90_ZWISCHENARCHIV/CURRENT_STATE_VOR_KOMPAKTIERUNG_2026-08-23.md`.
- Teil B (`OBS-100` bis `OBS-180`) ist im `MASTERPLAN.md` als
  `DEFERRED / BLOCKED BY TRIGGER ARCHITECTURE` verankert und beginnt erst nach
  der Triggerarchitektur-Migration.

## Einheitliche Triggerarchitektur

- Zielbild und Voranalysen vorhanden. Bereits besprochene Wake-Word-, Pause-
  und Hotkeyentscheidungen wurden am 2026-08-24 in die widersprechenden
  Zielbild- und Analysepassagen konsolidiert; weiterhin offene Verträge sind
  klar als offen abgegrenzt.
- Ergänzend festgelegt: mehrere serielle Sprachsegmente je Activation,
  `refresh` nur in `followup_wait`, dritter optional belegbarer
  Wake-Pause-Hotkey, Finish-/Cancel-Außenwirkung samt Lifecycle-Ereignis und
  selected-only Laden der Wake-Word-Modelle beim Sessionstart. Detection wird
  nach dem ersten akzeptierten Treffer bis zum Unlock gelatcht; nur eine
  zusätzliche Fehlalarm-Bestätigung wird nach Score-/Audio-Messung gehärtet.
- Finish-/Cancel-Phasenmatrix und Retry-Semantik sind fachlich eingefroren:
  genau ein Lifecycle-Ereignis pro neu angenommener Transition, kein Duplikat
  bei Command-Replay; Cancel unterdrückt nur unveröffentlichte Resultate und
  nimmt bereits ausgegebenen Text nicht zurück. Ungültige Wake-Word-Auswahl
  wird vollständig ohne Teilerfolg oder Fallback abgelehnt.
- Serververbindungsverlust verwirft die laufende Activation; Geräteverlust
  cancelt sie, lässt die Serversession aber bestehen. Ein triggerloser Zustand
  darf nur clientlaufzeitweit bestehen und wird beim App-Neustart verworfen.
- Settings-Control-Plane wird in den Umbau aufgenommen: Serverautorität,
  Session-/Server-Scope, Apply-Policies, triggerrelevante Einstellungen und
  admin-geschützte Servereinstellungsseite. Fachfremde Vollmigration bleibt
  für den späteren Settings-Arbeitsblock.
- Daueraufnahme-Schutz: zehn Minuten Default, kein VAD-Reset, Hotkey-Refresh
  als Anwesenheitssignal, Vorwarnung 30 Sekunden vorher und Ende der gesamten
  Activation. Das bereits erfasste Audio wird regulär verarbeitet; investierte
  Sprache wird nicht wegen eines Schutzablaufs stillschweigend verworfen.
- Manual und Wake Word sind getrennt clientlaufzeitweit suppressierbar; eine
  zusätzliche Pause-all-Funktion wird nicht eingeführt. Physische Hotkeys,
  Geräte- und Feedbackkonfiguration bleiben im Client. Der Server kennt nur
  semantische Commands und einen generischen Audioverfügbarkeitsstatus.
- Eine laufende Activation behält ihren unveränderlichen Settings-Snapshot.
  Reconnectpflichtige Änderungen währenddessen werden nicht automatisch
  abgebrochen, sondern über die drei bestätigten UI-Wege gesteuert.
- Der Admin-Key wird bei dauerhafter Speicherung im Windows Credential Manager
  gehalten und bleibt über die UI löschbar. Desktop-Client und Server erhalten
  einen klaren Protokoll-Cut samt Versions-/Commit-Kompatibilitätsmatrix;
  Browser und Legacy-Pfade blockieren den Umbau nicht.
- Der Trigger-Lock endet nach sicherem Schließen des Follow-up-/Eingabefensters
  und wartet nicht auf Final-Inferenz. Ältere Activations dürfen im Hintergrund
  drainen; ihre Resultate bleiben über stabile IDs und Segmentreihenfolge
  korrekt zugeordnet. `finalizing` ist keine blockierende Vordergrundphase.
- Segment-Watchdog: 600 Sekunden initial, nach Refresh mindestens 180 Sekunden
  ab Interaktion, ohne Verkürzung längerer Restzeit und ohne Kumulierung;
  Warnung 30 Sekunden vorher.
- Technischer Contract und finaler Implementierungsplan sind eingefroren.
  `AP-SRV-*` ändert ausschließlich Servercode, `AP-CLI-*` ausschließlich
  Clientcode; `AP-INT-*` validiert nur und ändert keinen Produktcode.
- Exaktes v2-Wire-Schema und gemeinsame maschinenlesbare Vertragsvektoren
  ergänzen den Contract-Freeze. Clientseitiges `activate` darf nur
  `source=manual` tragen; Wake-Word-Admission entsteht ausschließlich intern
  auf dem Server.
- Parallelausführung ist vorbereitet: maximal ein GPT-5.6-Sol-Sub-Agent und
  ein Claude-Code-CLI-Lauf mit Sonnet oder gezielt Opus. Wellen, Gates,
  Modellempfehlungen, Dokumentationsownership und Root-Endabnahme stehen in
  `PLANUNG/AUSFUEHRUNGS_WORKFLOW.md`; konkrete Prompts entstehen paketweise
  aus `ARBEITSPAKETE/AUFTRAGSVORLAGE.md`.
- Traceability ist nach Vollständigkeitsaudit auf 129 eindeutige Summary- und
  Einzelanforderungen granularisiert. Wire-Lücken zu Wake-Auswahl,
  serverinterner Activation-Admission, Command-Korrelation und stabiler
  Pending-Sortierung sind geschlossen; Hotkey-Konfliktregel sowie konkrete
  Wake-Cooldown-/Pre-Roll-Kalibrierwerte bleiben sichtbar vor ihren späteren
  APs offen.
- Server-Feature-Branch und Worktree existieren bereits. Die vorhandenen
  uncommitteten Serveränderungen werden als geerbter Baseline-Diff in
  AP-SRV-000 übernommen; die GitHub-Remote ist eingerichtet.
- Jedes AP erhält eine repositorylokale Akte. Agenten committen lokal, die
  Koordination prüft/amended die Endabnahme und pusht genau einen finalen
  Commit erst nach PASS.
- Nach dem kontrollierten Abschluss von Logging/Observability Teil A ist die
  Triggerarchitektur wieder alleiniger aktiver Hauptworkstream unter
  `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/`.
- Zentrale aktuelle Arbeitsdatei:
  `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`.
- Status und Funde: `NACHVERFOLGUNG/` sowie `STATUS.md` und `VERLAUF.md`.
- Kontextunabhängige operative Übergabe für neue Agents:
  `NACHVERFOLGUNG/WIEDEREINSTIEG.md`.
- Ausführungswelle 1 ist abgenommen und gepusht: AP-SRV-000 auf
  `71a35e074eb90d75f8f91f5ed7cb46accd4b6498`, AP-CLI-000 auf
  `042fcd203c873d6f84a270413c47bc5da1fbf1ed`. Die genaue Gate-Historie steht
  in `NACHVERFOLGUNG/AUSFUEHRUNGSSTATUS.md`.
- AP-SRV-020 ist nach zwei Root-Befunden, Korrektur durch denselben Agenten
  und unabhängiger Root-Abnahme als
  `8535ee79bb2d898d9897e91b57d6a735c479edf0` gepusht. AP-SRV-030 und
  AP-SRV-040 sind danach als kanonische Archive-Complete-Commits auf
  `feat/einheitliche-triggerarchitektur` geschlossen: AP-SRV-030
  `b220dd03a594d2b9f8cad65fd279046be36864cc`, AP-SRV-040
  `c0806e5bc5d503580070f2dacc88831d51447938`. Die erste
  fachliche Clientänderung in AP-CLI-010 ist technisch entblockt, wird aber
  bewusst deferred, bis die Serverlinie AP-SRV-050 → AP-SRV-060 → AP-SRV-070
  abgeschlossen ist.
- `AP-SRV-050` (Settings-Control-Plane) ist nach drei lokalen Läufen
  (C1 Implementierung, C2 sechs Root-Findings, C3 Wire-Atomicity) mit
  `ROOT PASS` abgenommen und als genau ein kanonischer Commit auf
  `feat/einheitliche-triggerarchitektur` geschlossen:
  `c901cda3f2c19eeb78c468524161728498b6e27e` (Parent `c0806e5…`,
  Root-PASS-Source C3 `18b65216433329456946afd3c41d8df6bbd07d44`).
- `AP-SRV-060` (Wake-Word-Katalog, Detection und Audiogrenze) ist mit
  `ROOT PASS` abgenommen und als genau ein kanonischer Commit auf
  `feat/einheitliche-triggerarchitektur` geschlossen:
  `c82923fc6ce889b4dfbbde1f9877b8b76481a1e8` (Parent `c901cda3f2c19eeb78c468524161728498b6e27e`,
  Tree `de6fe364545b508a47a87ead67a01c5732477e71`, Root-Source-Stand
  `2b08e379a36590c99e48e59c81a39418395d9742` aus C1/C2/C3/Asset-Finalisierung/Final-Repair).
  Der Server besitzt damit den versionierten Buildkatalog
  (`VoiceSTT/assets/wakeword_models/` mit ONNX- und TFLite-Dual-Backend-Artefakten),
  die öffentliche Catalog-API `GET /api/v2/wake-words` (`SET-13b`) und
  `POST /api/v2/wake-words/refresh`, atomare Sessionadmission,
  selected-only Modellinitialisierung, `WakeHitTracker` mit Exactly-once
  `wakeword.detected`-Eventing, Single-Backend-je-Engine-Policy sowie die
  detection-verankerte Audiogrenze (operationaler Nullpunkt an Trailing Edge des
  Wake-Hits). Vollsuite: 1180 passed, 14 skipped, 762 subtests, 0 failed.
  Empirische Kalibrierung (`WW-18`, `WW-19`) bleibt ehrlich als
  `EVIDENCE_BLOCKED / calibration pending` ausgewiesen.
  `AP-SRV-070` (Legacyabbau und Protokollgrenze) ist das nächste Serverarbeitspaket.
- Die textuelle Server-Prep-Provenienz vom 2026-08-25 ist byteidentisch
  versioniert unter
  `ARBEITSDATEIEN/90_HISTORIE/2026-08-25_TRIGGERARCHITEKTUR_SERVER_PREP/`.
  Sie ist ausdrücklich **nicht normativ**.

## Workspace-Status (WS-NORM-002)

- Aktiver Workspace: `workspaces\einheitliche-triggerarchitektur`
  (Branch `feat/einheitliche-triggerarchitektur`), Standard-Agent-Session-Root.
- Kein aktiver Logging-Worktree mehr; `workspaces\logging-observability-pre-trigger`
  ist git-seitig entfernt und physisch nicht mehr vorhanden.

## Arbeitsstruktur- und Main-Integration (DOC-ARCH-002)

- Repositoryweite deterministische Arbeitsstruktur (`.agents/skills/arbeitsstruktur/`,
  `AGENTS.md`/`CLAUDE.md`-Verweise) in `main` eingeführt und auf `origin/main`
  gepusht.
- Trigger-Arbeitsblock zunächst auf die deterministische Grundstruktur
  umgestellt und anschließend für die laufende Arbeit auf die klaren
  Einstiege `PLANUNG/` und `NACHVERFOLGUNG/` vereinfacht; doppelte Altpfade
  wurden nach Inhaltsabgleich entfernt.
- `main` kontrolliert in `feat/einheitliche-triggerarchitektur` übernommen;
  Konflikte in Governance-Dokumenten und in `core/controller.py`,
  `core/stt_session.py`, `ui/application.py` sowie den OBS-040-Tests fachlich
  zusammengeführt (beide Entwicklungsstände erhalten, keine Seite verworfen).
- Dieser Organisationsrun trifft keine fachlichen Triggerentscheidungen.

**Stand:** 2026-08-29 09:09:02 +02:00 (CANONICAL CLOSE AP-SRV-060; nächster
aktiver Server-AP ist AP-SRV-070)
