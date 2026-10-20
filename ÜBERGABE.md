## AP-IV2-020/R01 – BOTH abgeschlossen, Restgates konsolidiert,20.10.2026

[Bericht34](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/34_BOTH_ABSCHLUSS_UND_KONSOLIDIERTE_RESTGATES.md): Drei übernommene BOTH-Aufgaben PASS_SCOPED: natives Manual-F8/F9 und beide direkten Wake-Nutzsätze genau einmal ohne Rufwort;18,782/23,313s echte Ruhe ohne Zusatzwake. Erster Alexa-Versuch bewusst wiederholt, bleibt NOT_PROVEN. Realer Watchdog55,062sWarnung/60,015sAblauf und3gebundene ASRfinals aus demselben Rohdurchlauf nach phasengenauer Nachauswertung PASS_SCOPED; falsche Einsegmentannahme als Hilfstest-FAIL erhalten.61Helfer/Qt PASS, Produkt0f6c85e/1400Windowsbeleg unverändert. Keine identischen Sprechwiederholungen; technische/EXE-/Dauerreste gebündelt, W02 offen.23Aufräumreste automatisch gesperrt. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.

## AP-IV2-020/R01 – Mute/Reinsert bestätigt, überlagerter Wakefall offen,20.10.2026

[Bericht32](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/32_MUTE_REINSERT_UND_WAKEPAUSEN.md): Hardware-Mute27,297s/zehn blockierte F8 und bewusste Wiederfreigabe/1exakte Einfügung sowie Reinsert1Final/2passende automatische+manuelle Ausgaben PASS_SCOPED. Zwei aktive Wake-Modell-/Pausen-/Reconnectfälle PASS_SCOPED. Erweiterte Pause→Recovery→manuelle Aufnahme mit Wakefixture→Cancel erzeugt zweimal Zusatzwake bei Stille: IV2-020-W02 offen, Ursache noch einzugrenzen; kein Serverfix vorgenommen.59Helfer/Qt PASS, Produkt0f6c85e unverändert/1400Windowsbeleg erhalten.22gesicherte Aufräumreste automatisch gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – native Refreshpfade geprüft,20.10.2026

[Bericht31](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/31_REFRESH_AUFNAHME_UND_NATIVER_NACHSPRECHPFAD.md): Menschlicher nativer F8-Refresh während segment_active, F9/Finish und2exakte native Einfügungen derselben Activation PASS_SCOPED; menschlicher15sNachsprechfall bleibt phasenbedingt NOT_PROVEN. Ohne weitere menschliche Wiederholung:2reale native Windows→WM_HOTKEY→Qt→Controls→ASR-Nachsprechfälle bei5000ms/6Callbacks PASS_SCOPED, Fristverlängerung/nichtadditives Wiederholen/Timeout bestätigt. T04 unterscheidet Phasen;56Helfer/Qt PASS, bytegleiches Produkt0f6c85e behält1400Windows/0Skips.21hashgesicherte Aufräumreste automatisch gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – Controls/Logansicht und Refresh,20.10.2026

[Bericht30](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/30_CONTROLS_LOGANSICHT_UND_REFRESH.md): Denkpause mit2Segmenten/F9/2exakten nativen Einfügungen, Cancel mit82,969s weiterer Audioübertragung ohne Ausgabe und menschlich ausdrücklich bestätigte Server-/Tab-/Logansicht PASS_SCOPED; T01 geschlossen. Native Refreshprobe enthielt kein Refresh und bleibt NOT_PROVEN, lieferte aber korrekt gebundenen Altfinal-nach-Neustart-Beleg203ms. Zwei autonome reale ASR-/Controls-/Deadline-Refreshfälle PASS_SCOPED. T04-Testhäkchenfehler mit Regression/Qt korrigiert; nur native Refreshprobe entspannt erneut vorbereiten, übrige vollständige Gates offen. Produkt0f6c85e/Server67f3ce45 unverändert, gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – W01-Rückkehr erfolgreich,20.10.2026

[Bericht29](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/29_W01_KONTROLLE_BESTAETIGT_UND_RESTGATES.md): W01-Kontrolle Alexa ohne Sound PASS_SCOPED: genau1Wake/Activation/Timeout,29,765s weitere echte Audio-Nachbeobachtung ohne Folgetrigger,1543Pakete, keine Sprache/Final/Paste, menschlich Wie erwartet, Exit0. Damit alle3vorgesehenen Livekontrollen und13Modellfälle erfolgreich; konkretes W01 CLOSED_VERIFIED_SCOPED. Vollständige M-/Frozen-/Both-/Nutzsprachgrenzen-/30min100-Gates bleiben offen. Produkt0f6c85e/Server67f3ce45 unverändert;19private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – aktuelle Wake-Liveauswertung,20.10.2026

[Bericht28](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/28_WAKE_LIVEAUSWERTUNG_UND_RUHEKONTROLLE.md): Aktuelle reale Alexa-/Hey-Jarvis-Proben mit Sound je genau1Activation/Timeout,20,625s bzw6,954s weitere belegte Audiobeobachtung ohne Folgetrigger, menschlich Wie erwartet: PASS_SCOPED. Sound-aus-Kontrolle endet vorzeitig: nur1,875s Audio nach Timeout, NOT_PROVEN statt angenommener5s. Nur diesen Fall wiederholen; Testoberfläche wartet eine bereits laufende Ruhephase nach explizitem Beendenwunsch ab, Fensterclose bleibt Abbrechen.48Helfer/Qt und neue1400Windows/0Skips PASS. Produkt0f6c85e/Server67f3ce45 unverändert;18private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – Rückkehr vom Serverfix,20.10.2026

[Bericht27](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md): Neuer Pro-V2-Server67f3ce45/Tree74f37cad/Version2.0.0 über öffentliche Info, passenden Gitbaum/-datum und echten Hello bestätigt; Wakefix-Mergee761b973 direkter Parent.13reale Modellreplays/18Activations ohne Zusatzwake in geprüfter digitaler Stille PASS_SCOPED, native Source/ReSpeaker133Pakete und neue1400Windows/0Skips/43Helfertests PASS. W01-Live-Mikrofon-/Schweige-/Soundvergleich vorbereitet, keine vollständige M-/Frozen-/30min100-Abnahme; Clientprodukt0f6c85e unverändert.17beendete private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – autonome Restprüfungen,19.10.2026

[Konkrete Restliste und neue Nachweise](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/26_AUTONOME_RESTPRUEFUNG_UND_OFFENE_PUNKTE.md): Windows-Vault-Lebenszyklus mit frischen Prozessen/Origintrennung und Löschung PASS_SCOPED; reale idle-Runpausen über zwei manuelle Reconnects/eigenen TCP-Abbruch/Software-Mute sowie frische Runtime PASS_SCOPED. Wakeengine aus, keine Aktivierung/Paste,5000ms erhalten;1400Windows/0Skips und36Helfertests PASS. Produkt0f6c85e unverändert. Offene Kombinationen, Frozen/Admin/W01 und Gesamtgates bleiben;15private gesicherte Laufordner automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – Idle bestätigt, LED-only-Störung autonom geprüft,19.10.2026

[Bericht25](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/25_IDLE_BESTAETIGT_UND_LED_ISOLATION.md): Weiß/min30%/peak100% am realen ReSpeaker nach20s ausdrücklich bestätigt und reproduzierbar gespeichert. R11 CLOSED, Produkt0f6c85e unverändert. Zusätzlicher nativer LED-only-Transportausfall bei idle isoliert: automatische LED-Recovery, Audio/Session stabil,59→210Frames, keine neue Activation/AudioAvailability-Mutation. Erster fehlerhafter Hilfstest bleibtFAIL wegen falscher Persistenzannahme; neue33Helfertests PASS.1400Windows-/Buildbeleg am bytegleichen Produkt bleibt gültig. Übrige Real-/Frozen-/W01-Gates offen, kein REVIEW_READY; gleiche R01/PR15.13gesicherte externe Aufräumreste durch automatische Freigabeprüfung „blocked by policy“ nicht gelöscht.

## AP-IV2-020/R01 – direkte Idle-Vorschau vorbereitet,19.10.2026

[Bericht24](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/24_IDLE_ZIELZUSTAND_UND_DIREKTVORSCHAU.md): Letzte menschliche Akzeptanz bewahrt, aber kein Aktivierungs-/Idle-Zielübergang im Lauf, daher30/100%-Kalibrierung NOT_PROVEN. Dauerhafte LED-only-Vorschau mit eigenem START/20s/Übernehmen erstellt, kein Mikrofon/Server/Hotkey nötig;31Helfertests/Qt-Selbstcheck PASS. Produkt0f6c85e unverändert, R11 CLOSED. Neue physische Bewertung und weitere M-/Frozen-/W01-Gates offen; BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher PR15. Zehn gesicherte externe Restordner automatisch mit „blocked by policy“ gegen Löschen gesperrt.

## AP-IV2-020/R01 – physische USB-Recovery bestätigt, Idle-Feinabstimmung offen,19.10.2026

[Neuer Nachweis](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/23_USB_BESTAETIGT_UND_IDLE_KALIBRIERUNG.md): R11 CLOSED am unveränderten Produkt0f6c85e; echter USB-Ausfall/Servercancel/Wiederöffnung und bewusstes neues F8/F9-Diktat exakt einmal eingefügt. Manual-Timeoutfeedback menschlich bestätigt. Gewünschte weiße Idle-Pulsvariante30/100% als bestehende Testkonfiguration gespeichert, Sichtbestätigung offen; Farbprofile ausdrücklich später.29Helfer-/1400Windows-Tests ohne Skips PASS. Gesamtpaket weiter BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleiche R01/PR15, kein REVIEW_READY. Neun gesicherte beendete externe Laufordner wegen automatischer Freigabeprüfung „blocked by policy“ nicht gelöscht.

## AP-IV2-020/R01 – aktueller Wiedereinstieg, 19.10.2026

[Auswertung und Belege](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/22_GEFUEHRTER_DURCHLAUF_UND_USB_RECOVERY.md): 15 menschliche Versuche/14 Activations am alten Sourceprodukt7bb5646. Teilnachweise getrennt von vollständigen M-Gates; USB-Test FAIL. Autorisierte Recoverykorrektur am neuen Produkt `0f6c85e0ecf971e596aae1b7d265dad7132754e2`: 48 gezielte/1400 volle Windows-Tests ohne Skips, neue EXE/Wheel/sdist und native Source-/Wheel-Stillstandsprobe PASS. Physische USB-Wiederholung, Feedbackbestätigung, endgültige Frozen-/Realqualifikation und W01 offen. Workflow IMPLEMENTATION_IN_PROGRESS, Gesamtabnahme BLOCKED; kein REVIEW_READY. Sieben privat gesicherte externe Laufordner wegen automatischer Freigabeprüfung nicht gelöscht; Aufräumpflicht bleibt offen.

## AP-IV2-020/R01 – korrigierte ereignisgebundene Testführung,19.10.2026

Aufgabe1 erneut selbst starten. F8/Sprach-/Abschlussereignisse bewegen die
Markierung; nur echte Beobachtungen erzeugen Häkchen. Alte Resultate gesichert.
27 Helfer/Qt-Polling,1398Windows ohne Skips und compileall PASS. Neuer realer
Vorcheck134Frames ohne Activation. T03 bis menschlicher UI-Bestätigung offen.
Gesicherter Ordner `C:/Users/marco/.voice-stt/qualification/AP-IV2-020/progress-regression-20261019-162446`
konnte trotz erlaubter Aufräumaktion wegen automatischer Freigabeprüfung nicht
entfernt werden (nur „blocked by policy“). Aufräumpflicht bleibt offen; keine
Umgehung. Übrige neue Vorprüfungs-/alte Bedienordner nach Sicherung entfernt.
[Bericht21](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/21_TESTOBERFLAECHE_LIVE_FORTSCHRITT.md).

## AP-IV2-020/R01 – genehmigter geführter Bedienlauf startbereit,19.10.2026

`venv/Scripts/python.exe -m tests.manual.v2.guided_suite --profile-runtime`
öffnet elf einzeln startbare Aufgaben. Letzte Suite1398/0Skips PASS,
16 Helfer/43 Fokus/compileall PASS, realer Audio-/Log-Vorcheck
130Frames/40Logzeilen. Produkt unverändert7bb5646; Source- statt Frozen-Prüfung.
Ablage nur `C:/Users/marco/.voice-stt/qualification/AP-IV2-020`, vom Menschen
unter verbindlicher Export-/Aufräumbedingung freigegeben. Vier autonome Laufordner
bereits exportiert/entfernt; menschlichen Lauf nach Auswertung und Sicherung der
benötigten Projektbelege ebenfalls entfernen, zuletzt leeren eigenen AP-Ordner.
[Bericht20](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/20_GEFUEHRTE_RESTTESTS.md).

## AP-IV2-020/R01 – geführter Resttest, Ablageentscheidung offen,19.10.2026

[Bericht20](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/20_GEFUEHRTE_RESTTESTS.md).
`venv/Scripts/python.exe -m tests.manual.v2.guided_suite` öffnet nur die Vorschau.
Reallauf `--profile-runtime` erst nach tatsächlicher Freigabe der separat
angefragten `.voice-stt/qualification/AP-IV2-020`-Ablage im Benutzerprofil.
Elf unabhängige Bedienaufgaben; kein automatischer Start/Weiter-PASS. Helfer16/Qt
PASS, vorläufige echte Audioübertragung135Frames; Windows1398aktuell FAIL durch
TEMP-/Profilgrenzen. V1 und Server geschützt, unverändertes Produkt7bb5646.

## AP-IV2-020/R01 – ausgewähltes vorhandenes V2-Testziel,19.10.2026

Aktuell: [Bericht19](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
`wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`, alternativ Normal ohne `pro.`.
HTTP-/Hello-Drahtcommit unknown ist separat zu Image/Build/Gitpinada13b0 gebunden.
Pro-Image57a7907, Normal6dcc498; neue Modelle-/Settings-/Clientpaarqualifikation
nötig, alte Communitybelege nicht übertragen. Diagnostische Wartegrenzen180s.
W01 blockiert volle Wake-/Feedback-/gemischte Dauergates, nicht alle Restarbeiten.
Unabhängige Teile zuerst; später eigener Server-FIX ohne vorzeitigen AP020-PASS.
Keine Wiederanlage/Serveränderung/Neustarts; Docker am Windows-PC muss für die
benannten vorhandenen HTTPS/WSS-Ziele nicht entpausiert werden.

## AP-IV2-020/R01 – Offline-Belegklärung, 19.10.2026

Maßgeblich für weitere Schritte: [Bericht18 / sieben verbleibende Punkte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/18_AUTONOME_KLAERUNG_UND_RESTPUNKTE.md).
Autonome Akten-/Metadatenklärung durchgeführt; fehlende historische Antworten nicht
rekonstruierbar, keine weitere allgemeine Recherche als Voraussetzung offen.
Vor Realtests tatsächliches Serverziel/Commit/Modelle/Konfiguration und zulässige
Ablage festlegen. Entfernten Server nicht wieder anlegen, deaktivierten Starter
nicht starten/funktional freigeben. W01-FIX nicht beauftragt. BLOCKED bleibt.

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
[Aktuelle Sound-/LED-/Triggerübersicht](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/10_FEEDBACK_UEBERSICHT.md). Acht Alexa-Treffer mit
Scores0,908322..0,999994; Schwelle0,85 nur ungesetzter Offlinekandidat.
Dauerhafter Desktopstarter bleibt verfügbar. V1/VPS geschützt; gleicher PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – klickbarer Teststarter, 18.10.2026

Isolierte Both-Instanz mit Logdienst erneut bereit; dauerhaftes Startfenster mit
Desktopverknüpfung **V2-Testinstanz** hinzugefügt. Start-/Doppelstart-, Profil- und
Containergrenzen sowie echter Qt-Klick gezielt geprüft (5 PASS). Erneute volle
Windows-Regression1390 PASS/0 Skips, Managerbootstrap-Retry PASS; frühere
Speicherfehlernachweise erhalten. Nur Testhilfen,
kein Produkt-/Build- oder Kalibrierwertwechsel. [Anleitung](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/STARTER_README.md).
Zwei separate Alexa-Fehlalarme vom17.10. um21:20 gesichert; Scores0,767/0,646,
null Sprachsegmente, akustischer Auslöser nicht bewiesen. Echte positive
Vergleichsversuche und übrige Realgates weiter offen; kein REVIEW_READY.
Overlayklarstellung: Der V2-Statuspfad blendet nicht über `fade_after: 2.0` aus;
dieser Dateiwert ist kein wirksamer V2-Anzeigedauerregler. T01-Manager real aktiv,
sichtbare menschliche Bestätigung der Logansicht weiterhin offen.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – IN_PROGRESS, UX02 technisch und real geschlossen, 16.10.2026

Produkt d95043e nach freigegebener Modifierkorrektur:1390 Windows-Tests/0 Skips,1964 Servertests/14 erwartete optionale Skips,11 Prozessfälle,17 Grenztests,7 Socketsmokes PASS. EXE/Wheel/sdist und native Produkt-/Serverlaufzeit erneut qualifiziert; reale Recovery, ReSpeaker-Desktop-Neustart und sechs Modellreplays neu gebunden. Physische Modifierprobe PASS:250ms tatsächliche Halte-/Freigabe, exakte einmalige native Ausgabe/menschlich bestätigt; UX02 CLOSED. Zusätzlich realer Manual-F8→Sprache→F9-Pfad PASS: ein erkannter Final exakt nativ eingefügt/menschlich bestätigt. Freie isolierte Both-Instanz für LED/Sound/Overlay aktiv. Genannte Einstellungstabs über zweiten lokalen Dialog vorhanden; Teststarter-Logmanagerlücke T01 festgestellt, Korrektur vorbereitet/gezielt geprüft, native Bestätigung nach abgestimmtem Neustart offen. Übrige Realgates/Kalibrierung weiter offen. Kein REVIEW_READY, gleicher R01/Paketbranch/PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – BLOCKED durch UX02, 16.10.2026

[Testclient](tests/manual/v2/README.md) fertig: feste Schritte, wandernder Fokus, Countdown8s, eigener Start/Wiederholen/Abbrechen. Zehn Helferprüfungen/Qt und volle1378Windows-Regression PASS. Manuelle F8/F9-Steuerung PASS, Zieleinfügung FAIL (Shift gehalten). Produktausnahme noch nicht freigegeben; Produkt17261e6 unverändert. Derselbe R01/Branch/Draft-PR15; kein REVIEW_READY. [Aktueller Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md).

### Vorheriger datierter Zwischenstand

**Aktualisierung16.10.:** UX01 nativ bestätigt und geschlossen. Zwei einzeln gestartete direkte Wake-Nutzsätze vollständig, ohne Rufwort und mit Leerzeichen bestätigt. F9-Finish mangels Commandack noch unbewiesen; gezielter einzelner Manualtest mit eigener Vorschau/Start folgt. Produkt17261e6 unverändert; vollständige M-Gates/30min100 weiter offen.

# AP-IV2-020 – IN_PROGRESS, Phase C läuft, 2026-10-15

Kanonischer Parent `b80ed8b` unverändert, Vorgänger AP010 tatsächlich ACCEPTED.
Paketbranch `work/client-v2/ap-iv2-020`, kumulativer Draft-PR #15, derselbe R01.
Ausdrücklich freigegebener Reconnect-/Recovery-Audit abgeschlossen: zehn technische
Findings behoben. Recoveryprodukt41ca761 historisch; zusätzlicher freigegebener UX01-Fix am Produkt `17261e6`, neue EXE/Wheel/sdist sauber gebunden.
1378 Windows-Tests ohne Skips, 11 Prozessfälle, alle sieben Server-Smokes PASS;
1964 Server-Unit-Tests PASS/14 ausgewiesene optionale Skips. Echter ReSpeaker- und
Desktop-Reconnect, HTTP-/Ackausfall, drei Neustarts, Shutdown und Frozen-GUI grün.
M-Fälle, echte Wakepositive/Nutzsprachgrenze, Wahrnehmung/Kalibrierung und30min100
bleiben NOT_RUN/NOT_PROVEN. Nächste Aktion: gemeinsamer erster Sprach-/Windowsblock.
[Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/VPS geschützt; Server nur lokal. Kein REVIEW_READY, Eigenreview, Merge oder Release.


Neuer Produkt-/Build-/Paarstand17261e6 autonom qualifiziert; native Ausgabebestätigung und vollständige Realgates bleiben offen. Der nächste Ein-Klick-Block steht im Testeditor bereit.

## Vorheriger datierter Stand

# Client V2 – AP-IV2-010 / R01-UMSETZUNG / REVIEW_READY, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Client V2 – AP-CV2-110 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-14

[Paket-PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base `feat/client-v2`, Head `work/client-v2/ap-cv2-110`.

Aktiver Arbeitsblock [CLIENT_V2](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/README.md);
[Einstieg Planung](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).
AP000 bis AP100 tatsächlich ACCEPTED auf feat/client-v2; letzter kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100-PASS, menschlicher R06-Auftrag und wirklicher PR12-Squash
[verifiziert](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).

AP110 auf `work/client-v2/ap-cv2-110`: ausführbare V1-Autoritäten entfernt,
Migrationreader und Utilities erhalten, Source/Wheel/sdist/Frozen mit belegter
Helloidentität und nativer Windows-GUI qualifiziert. Windows **1353 PASS**,
gezielte **234 PASS**, Servercheckpoint **17 PASS**, compileall/diffcheck und
alle Build-/Ressourcen-/Installationschecks PASS. Getesteter Produktcommit
`cf42a2a9d96c1ebc88035817a5d529dfe04e4306`; finale PR-Spitze ergänzt ausschließlich administrative Unterlagen.
[Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Kompatibilität](docs/compatibility.md), [Runtime](docs/protocol-v2-runtime.md).

Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.
Bekannte Legacy-Profile und History werden mit Backup migriert; kein V1-Fallback.
Builds liegen lokal unter dist, kein veröffentlichter Release. Keine realen
ASR-/Mikrofon-/USB-/Fremdanwendungs-/Wahrnehmungsgates behauptet.

**Aktueller Reviewabschluss (2026-10-14):** [AP110 R02 unabhängiger ROOT_PASS](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) auf `44cf9a8fd1669242c00997966addc3667d448aa0`; FINAL-03 bis FINAL-09 technisch PASS, keine offenen Pflichtfindings. **ROOT_PASS** mit menschlicher **R03-Freigabe** – finale Git-/CI-Prüfung und Squash stehen aus. Kein AP-IV2-010-Start zuvor.

**Übernahmefreigabe 2026-10-14:** [R03-Originalprompt](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) und [R03-Abschlussablauf](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/01_REPORT.md) dokumentiert. Aktuelle Phase **READY_FOR_CANONICALIZATION**; unabhängiger R02-ROOT_PASS unverändert. Nach finaler CI und Head-/Baseprüfung ist der einzelne Squash-Merge von PR #13 erlaubt. Ohne belegten GitHub-Merge noch nicht ACCEPTED; kein Release/Tag/Servermerge/AP-IV2-010.

---

## Historischer AP100-Stand vor dessen tatsächlicher kanonischer Übernahme

# Client V2 – AP-CV2-100 / R05-ABNAHME / ROOT_PASS, 2026-10-13

AP-CV2-000 bis AP-CV2-090 auf `feat/client-v2` ACCEPTED; letzter kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der aktuelle AP-CV2-100-Paketbranch `work/client-v2/ap-cv2-100` ([PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)) wurde unabhängig am Kandidaten `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` geprüft: **technischer ROOT_PASS**, 6/6 Paketrequirements erfüllt, `CV2-100-R03-F01` geschlossen.

[R05-Abnahmebericht](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md), [unabhängige Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/EVIDENCE/INDEX.md), [R04-Korrekturbelege](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Extern qualifizierte Windows11-Suite **1581 PASS**, gezielte Tests **210 PASS**, **17** echte gepinnte Client-/Servercheckpoints am Server `ada13b0`, GitHub-Actions-CI **38394758805** erfolgreich auf dem geprüften Kandidaten. Reviewer hat diese Belege unabhängig geprüft, aber keine eigene Windows-/Hardwaretestausführung vorgenommen.

**Nächster Schritt: WAITING_FOR_APPROVAL.** Ausdrückliche menschliche Freigabe des Squash-Merges von PR #12 erforderlich, davor aktueller PR-Head, unveränderte Base, ausschließlich administrative R05-Nachträge sowie finale CI prüfen. Kein Merge und kein Start von AP-CV2-110 durch dieses Review.

---

## Historischer R04-Stand vor unabhängigem R05-Review

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json), [Runtimeinterfaces](docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

## Historischer Stand vor AP-CV2-020

# Aktueller Client-V2-Stand – AP-CV2-010, 2026-10-11

AP-CV2-000 ist nach unabhängigem PASS und menschlicher Freigabe über PR #2 als `1cf076bd2ed56929b1a3780bc140da51348a8295` übernommen. AP-CV2-010 ist nach unabhängigem R02-Review ROOT_PASS in [PR #3](https://github.com/marcosudau-vps/voice-stt-client/pull/3) auf `work/client-v2/ap-cv2-010`: reiner V2-Codec, Datentypen und Vertragsfixtures. Windowsvollsuite1263, Codec30 und gepinnter Servercheckpoint188 PASS; menschliche Übernahmefreigabe als nächste Aktion, Schreibhoheit pausiert; [R02-Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/RUNS/R02-ABNAHME/01_REPORT.md). Runtime bleibt bis zur Transportintegration auf ihrem bisherigen Pfad; keine Datenmigration. [Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md), [Codecvertrag](docs/protocol-v2-codec.md). Historische Einstiege unten bleiben ihrem Datum zugeordnet.

# Aktueller Client-V2-Korrekturstand R03 – 2026-10-11

AP-CV2-000 **REVIEW_READY** in [PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2), Branch `work/client-v2/ap-cv2-000`, Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [R03-Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md) und [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json) sind der aktuelle Übergabestand.

F01: Hotkeyersatz wird erst nach erfolgreichem Corestart gespeichert; fehlgeschlagener Start erhält Profil und ursprüngliche Hotkeys. 1233 Gesamttests PASS, Packaging-/Installations-/Frozen-Smokes bestanden. Projektvenv Python 3.12.10. Nächste Aktion: frischer unabhängiger Vollreview einschließlich eigener Windows-Gesamtregression. Schreibrecht nach Übergabe pausiert; kein ROOT_PASS, Übernahmeprompt oder Folgepaketstart. Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`; V1-Transport und spätere V2-/Hardwaregates bleiben offen.

## Historischer Einstieg vor R03

# Client V2 – Operative Übergabe, 2026-10-11

Aktiver Block CLIENT_V2, Planung Revision 10. AP-CV2-000 **REVIEW_READY** auf `work/client-v2/ap-cv2-000`, Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [Aktueller Einstieg](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md), [Runreport](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md).

Feature-/Releaseintegration in `voice_stt_client`, Präferenzen/Legacydaten erhalten. Gesamte pytest-/Unittestregression je 1221 Tests grün, Wheel und sdist außerhalb Source qualifiziert. Start `.\venv\Scripts\python.exe -m voice_stt_client`; Details zu Profilen und Pfaden in [Kompatibilität](docs/compatibility.md). Projektvenv Python 3.12.10; lokale venv-Verknüpfung zur bestehenden Clientumgebung.

Nächste Aktion: frische unabhängige Abnahme des vollständigen Kandidaten. Schreibrecht des Umsetzers nach Abgabe pausiert; kein unabhängiger PASS, menschlicher Übernahmeprompt oder kanonischer AP-Commit. Server ada13b0/Distributed bleibt offen; Transport noch V1 und bekannter Streamstartfehler dokumentiert. Keine V2-/Live-ASR-/Hardwareabnahme. AP-CV2-010 startet erst nach tatsächlicher kanonischer Übernahme.

---

Die folgende datierte Vorfassung bleibt historische Provenienz; ihre Next-/Freeze-/Branchanweisungen steuern Client V2 nicht.

# ÜBERGABE – RealtimeSTT Windows Desktop Client

> **Stand:** 25. August 2026, operative Triggerübergabe; historische Clientdetails unten
> **Projektpfad:** `P:\GithubRepos\marcosudau-vps\voice-stt-client`
> **Status:** Triggerarchitektur in Umsetzung; AP-SRV-000, AP-CLI-000, AP-SRV-010 und AP-SRV-020 abgenommen
> **Nächster Schritt:** AP-SRV-030; AP-CLI-010 bleibt bis AP-SRV-040 blockiert
> **Kanonischer Wiedereinstieg:** `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/NACHVERFOLGUNG/WIEDEREINSTIEG.md`
> **Repository:** `https://github.com/marcosudau-vps/voice-stt-client` (`PUBLIC`)  
> **Historischer Pre-Trigger-Nachweis:** Client 451 Tests und `compileall` grün; aktueller
> Windows-PyInstaller-Build grün;
> Server 378 Tests, 13 Skips und 78 Subtests grün
> **Historischer Live-Stand:** zusätzlich beide Sessionmodi, zwei Laufzeitmoduswechsel und
> sessiongebundener `/ws/logs`-Replay/LIVE-Pfad ohne Audio oder Injection grün
> **Separater Restpunkt:** gesprochenes `hey_jarvis` nach dem AP6-Fix einmal
> mit echtem Mikrofon bestätigen

## Aktuelle operative Übergabe – Triggerarchitektur

Der aktuelle Server-Feature-Stand ist
`8535ee79bb2d898d9897e91b57d6a735c479edf0` im Repository
`P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\einheitliche-triggerarchitektur`.
Er enthält die abgenommene Fünf-Phasen-State-Machine aus AP-SRV-010 sowie das
immutable, threadsichere Segmentledger und den geordneten Background-Drain aus
AP-SRV-020. Der
Desktop-Client besitzt mit AP-CLI-000 weiterhin nur die abgenommene Baseline
`042fcd203c873d6f84a270413c47bc5da1fbf1ed`; seine erste Produktmigration
beginnt erst nach dem Server-Wirepaket AP-SRV-040.

Alle aktuellen SHAs, Dependencies, Paketgrenzen, Testbefehle und
Wiedereinstiegsschritte stehen in der oben verlinkten kanonischen Datei. Die
nachfolgenden Abschnitte dokumentieren überwiegend den Pre-Trigger-Clientstand
und dürfen den aktuellen Trigger-Gate-Status nicht überschreiben.

## 0. Baseline für die einheitliche Triggerarchitektur (AP-CLI-000, 25. August 2026)

Der Client wird auf `feat/einheitliche-triggerarchitektur` schrittweise auf
die einheitliche Trigger-/Wire-v2-Architektur umgebaut
(`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/`, Einstieg über
`ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`). AP-CLI-000 hat den
Ist-Stand auf Start-HEAD `db102fdc6dd70e4de798a363608d1e7412533dd7`
reproduzierbar verifiziert: **1192 Tests grün** über
`P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe -m pytest`
(geteilte Projektumgebung; dieser Worktree besitzt keine eigene lokale
venv), zweimal ohne Flake wiederholt. Eine Ein-Zeilen-Importkorrektur
in `tests/test_obs010_normalizer_server.py` war nötig, damit `pytest`
überhaupt sammeln kann (siehe `task.md`); kein Produktverhalten wurde
geändert. Das vollständige Inventar der überholten Trigger-Solltests
(`tests/test_trigger_lifecycle.py`, `tests/test_trigger_feedback_contract.py`,
Teile von `tests/test_ap06_followup.py`) und ihre Zuordnung zu
`AP-SRV-010`/`AP-CLI-010`/`AP-CLI-020`/`AP-CLI-040`/`AP-CLI-050` steht im
Baseline-Bericht
`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/ARBEITSPAKETE/AP-CLI-000/runs/01_BASELINE/REPORT.md`.
Die restlichen Abschnitte dieses Dokuments beschreiben weiterhin den
Pre-Trigger-Stand vom 12. August 2026.

## 1. Projektziel und aktueller Stand

Der Windows-Client läuft im Hintergrund, überträgt Mikrofon-Audio an
`wss://stt.voice.marcosudau.com/ws/transcribe`, zeigt Realtime-Text nur
passiv an und fügt ausschließlich Finaltexte über Clipboard und `SendInput`
in die fokussierte Anwendung ein.

Implementiert sind:

- AP1: thread-sichere RAM-/SQLite-Transkripthistorie,
- AP2: serialisierte Text-Injection-Queue,
- AP3: Reinsertion früherer Finaltexte,
- AP4: UI-neutraler Integrationscontroller,
- AP5: stille, unbegrenzte Transportheilung ohne Fortsetzung abgebrochener
  Diktate,
- AP6: PySide6-Tray, passives Overlay, native globale Win32-Hotkeys,
  Single Instance, Qt-/asyncio-Brücke, Betriebsmodi, Hotkey-Diktatfenster,
  Einstellungen, Verlaufspflege und optionales Feedback.

Die Servervorstufe und Vertragsynchronisierung von AP7 (M0–M3) sind
abgenommen. M4 stellt immutable Event-/Kontrollmodelle, eine typisierte
Eventstream-Konfiguration, ein strikt validiertes YAML-Mapping für
`server.*`- und lokale `client.*`-Ereignisse sowie einen atomaren,
endpointgebundenen Cursorstore bereit. Mit M5 führt AP7 eine zweite
sessiongebundene Verbindung zu `/ws/logs` ein. Der isolierte Transport und der
strikte Protokollprocessor sind mit M5 einschließlich Replay/Live, Reconnect,
Ping/Pong, expliziter Cursorbestätigung und typisierten Fehlerfällen
implementiert. M6 ergänzt den generationgebundenen `DualSessionCoordinator`:
Er übernimmt `hello.logAccess` ausschließlich für die aktuelle STT-Session,
verwirft alte Tokens und In-Flight-Events beim Reconnect, behandelt
Tokenablauf/`available=false` und beendet beide Transporte deterministisch.
M7 führt exakte Eventnormalisierung, reinen Feedback-Reducer, impulsfreies
Replay, begrenzte Deduplizierung und kontrollierten STT-Fallback ein. M8 bindet
die Reducerausgaben queued an Qt, Tray und Overlay an, wahrt die vorhandenen
Modusfarben und erzeugt optionale Sounds ausschließlich aus den sieben
YAML-konfigurierbaren Cues. Adapterfehler bleiben nicht fatal und werden als
lokales `client.sound.failed` zurückgeführt. M9 steuert den nachgewiesenen
ReSpeaker XVF3800 über einen koaleszierenden USB-Worker, isoliert Gerätefehler
als `client.led.unavailable` und setzt beim Shutdown sicher `off`. Allgemeine
Geräte-Hot-Plug-Heilung, Sleep/Wake, Multi-Monitor/DPI, Autostart,
weitergehendes Packaging-/Release-Polish und Langzeit-/Stresstests folgen als
AP8; die grundlegende GitHub-/CI-/PyInstaller-/Release-Strecke ist bereits da.

## 2. Bedien- und Betriebsmodi

### Hotkeymodus

- Sessionanforderung: `wakeWordEnabled=false`.
- `Ctrl+Shift+Space` startet das Diktat.
- Nach bestätigtem `start` läuft ein Initial-Sprach-Timeout von 15 Sekunden.
- `recording_started` und `recording_ended` des Servers steuern Segment- und
  Follow-up-Phase; es existiert kein lokales VAD.
- Das Follow-up-Fenster beträgt derzeit 3 Sekunden.
- Ein erneuter primärer Hotkeydruck verlängert das aktuelle beziehungsweise
  vorgemerkte Fenster standardmäßig um 15 Sekunden.
- Ein unterbrochenes oder kontrolliert reconnectetes Diktat wird beendet und
  nicht fortgesetzt.

### Wake-Word-Modus

- Sessionanforderung: `wakeWordEnabled=true`.
- Projektdefault für die logische Modell-ID: `hey_jarvis`.
- Nach `ready` wird der Audiostream einmal gestartet und bleibt auch in
  `wakeword_wait` aktiv.
- Nach heilbaren Reconnects wird dieser Hintergrundmodus neu scharfgeschaltet.
- Bewusstes Pausieren über die primäre Aktion bleibt respektiert.

Für beide Modi ist ausschließlich
`sessionConfig.effectiveWakeWordEnabled` in `hello` und `ready` maßgeblich.
Fallbacks, Warnungen und ignorierte Felder werden protokolliert. Ein
`error.where=session_config` beziehungsweise eine widersprechende effektive
Konfiguration pausiert Reconnects bis zu einer tatsächlichen
Konfigurationsänderung.

### Tray- und Feedbackfarben

| Zustand | Farbe |
| --- | --- |
| Hotkeymodus wartet / nimmt auf | dunkelgrün / hellgrün |
| Wake-Word-Modus wartet / nimmt auf | dunkelblau / hellblau |
| wartet auf erste oder weitere Sprache | jeweilige dunkle Modusfarbe mit weißem Rand |
| äußeres Netzwerk-, Server-, Timeout-, Audio- oder Mikrofonproblem | gelb |
| tatsächlicher interner oder protokollarischer Fehler | rot |
| Wake Word pausiert, Shutdown oder beendet | grau |

Gelb und Rot sind damit keine Betriebsmodusfarben. Gelb signalisiert eine
äußere Störung; Rot bleibt echten Fehlerzuständen vorbehalten.

## 3. Einstellungen und Persistenz

`AppConfig` und ihre typisierten Unterobjekte sind die einzige Wertquelle.
`core/settings_metadata.py` beschreibt Darstellung, Grenzen und
Änderungswirkung, speichert aber keine eigenen Laufzeitwerte.

Ladereihenfolge:

1. Code-/Dataclass-Defaults,
2. versionierte `config.yaml`,
3. `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml`.

Der Benutzer-Override wird atomar über temporäre Datei und `os.replace`
geschrieben. Enthält er unbekannte Felder, wird der Override vollständig
verworfen statt teilweise übernommen. Vor jeder Änderung wird eine vollständige
Kandidatenkonfiguration validiert. Hotkey-, Audio- und Sessionübernahmen
besitzen Rollbackpfade.

Der Einstellungsdialog enthält genau:

1. Verlauf,
2. Allgemein,
3. Verbindung & Betriebsmodus,
4. Geräte & Audio,
5. Erscheinungsbild & Feedback.

Der Verlauf unterstützt Reinsertion, einzelnes Löschen und bestätigtes
Gesamtlöschen. Gelöschte Einträge verlieren während des laufenden Prozesses
nicht ihre Deduplizierungsidentität.

## 4. Threading und öffentliche Grenzen

- Qt-Widgets, Tray, Overlay, Dialog und Native Event Filter: Main Thread.
- `STTController`, `STTSession` und asyncio: eigener nicht-daemonisierter
  `RealtimeSTT-AsyncCore`-Thread.
- Audio: sounddevice-Callback-/Verarbeitungsthread, Übergabe via
  `loop.call_soon_threadsafe`.
- Textinjektion: eigener nicht-daemonisierter FIFO-Worker.

Wichtige neue Schnittstellen:

```python
EventStreamAccess(...)
EventProtocolProcessor.begin_subscription()
EventProtocolProcessor.process_frame(frame)
EventProtocolProcessor.confirm_event(result)
await EventStreamTransport.run()
await EventStreamTransport.reconfigure(access)
await EventStreamTransport.stop()

await DualSessionCoordinator.begin_generation(generation)
await DualSessionCoordinator.adopt_hello(generation, hello)
await DualSessionCoordinator.invalidate_generation(generation)
await DualSessionCoordinator.shutdown()

SessionConfig.build_url(base_url)
await STTSession.reconfigure(session_config, server_config)

await STTController.primary_dictation_action()
STTController.extend_dictation_window()
await STTController.cancel_dictation()
await STTController.apply_runtime_config(candidate)

TranscriptHistoryManager.delete_entry(entry_id)
TranscriptHistoryManager.clear_entries()
```

Finaltexte bleiben die einzige Quelle für automatische Historie und
Textinjektion. Realtime- und Timeline-Ereignisse werden nie eingefügt.

## 5. Start und Prüfkommandos

Regulärer Start:

```powershell
.\venv\Scripts\python.exe -m voice_stt_client
```

Headless-Diagnose:

```powershell
.\venv\Scripts\python.exe -m voice_stt_client --headless
```

Automatische Gesamtsuite:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Sicherer Live-Smoke beider Sessionmodi, ohne Audio oder Textinjektion:

```powershell
$env:PYTHONUTF8='1'
.\venv\Scripts\python.exe -m tests.manual_test_ap06_modes
```

Sichere AP07-Live-Smokes ohne Aufnahme oder Textinjektion:

```powershell
$env:PYTHONUTF8='1'
.\venv\Scripts\python.exe -m tests.manual_test_ap07_event_stream

$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m tests.manual_test_ap07_adapter_failures
.\venv\Scripts\python.exe -m tests.manual_test_ap07_led_hardware
```

Letzter belegter automatischer Stand:

```text
Ran 396 tests
OK
```

Zusätzlich erfolgreich:

- M10: beide vollständigen Gesamtsuiten wiederholt stabil; Client 396 Tests,
  Server 379 Tests bei 13 Skips und 78 Subtests,
- M10: 227 fokussierte AP07-/Reconnect-Tests mit `-W error`,
- M10: echter sessiongebundener STT- plus `/ws/logs`-Handshake über Replay bis
  LIVE und sauberer gemeinsamer Shutdown,
- M10: reale Adapterklassen mit nicht vorhandenem USB-Gerät und defektem
Soundasset; Fehler isoliert, gedrosselt und Worker sauber beendet,
- Debugfeedback: Start-/Stopping-Lifecycle exakt einmal, Helligkeit 192/255,
  acht ausgelieferte nichtsprachliche PCM-WAVs und unabhängige Cue-Player,
- Timeoutfeedback: `easter_egg_tick` als dreisekündiger Tick-Cue plus LEFX-
  `countdown_ring` für Hotkey- und Wake-Word-Follow-up; neue Sprache stoppt
  beide Ausgaben,
- M10: isolierte Store-/Retention-/WebSocket-Kampagne und persistenter
  Serverneustart über zwei echte Betriebssystemprozesse grün,
- M10: Cursor-Schreibfehler/Replays ohne Doppelimpuls, extreme Backoffzähler,
  Tokenablauf, Prozessstart-, Pipe-, Timeout- und Minimal-Shutdown-Fälle grün,
- M10: echter ReSpeaker-Smoke über fünf Effekte bis `off`, ohne verwaisten
  Hilfsprozess,

- 32 fokussierte AP07-M4-Tests für Konfiguration, Modelle, YAML-Mapping und
  Cursorstore,
- 23 fokussierte AP07-M5-Tests für Protokoll, Replay/Live, Reconnect,
  Cursorbestätigung und Shutdown; zusätzlich mit `-W error` grün,
- 14 neue AP07-M6-Race-/Lifecycle-Tests für Generation, Session-/Tokenbindung,
  Reconnect, stale Events und gemeinsamen Shutdown; 59 relevante Prüfungen
  zusätzlich mit `-W error` grün,
- 30 AP07-M7-Tests für Normalisierung, Reducer, Replay, Quellenwechsel,
  Fallback, Deduplizierung und neutrale Controllerausgabe; 183 relevante
  Prüfungen zusätzlich mit `-W error` grün,
- 13 neue AP07-M8-Prüfungen für queued Qt-Übergabe, Mappingwirkung,
  Eventstream-Zusatzstatus, Replay-/Legacy-Soundunterdrückung und isolierte
  Soundfehler; 232 relevante Prüfungen zusätzlich mit `-W error` grün,
- 13 neue AP07-M9-Prüfungen für USB-Kommandos, Koaleszierung,
  Impulsrückkehr, Replayunterdrückung, Hardwareverlust, Fehlerdrosselung und
  begrenzten Shutdown; 254 relevante Prüfungen zusätzlich mit `-W error` grün,
- ReSpeaker-Hardware: `VID_2886/PID_001A`, Control-Interface 3, Firmware
  `2.0.10`; realer LED-Smoke für sechs Dauerzustände und einen Erfolgsimpuls,
- Windows-Onefile-Build mit gebündelter `libusb-1.0.dll`: 74.758.009 Byte,
  SHA-256 `1e6b2b54ed010149bd233d3c77071a096df769de9bac3dfbc41d06d234bd5d5a`,
- realer Qt-Soundbackend-Smoke mit lokalem Windows-WAV: Asset akzeptiert,
  Backendstatus `Ready`, keine Fehlermeldung,
- `compileall` über `app.py`, `core/`, `ui/`, `scripts/` und `tests/`,
- Offscreen-Qt-Smoke des fünfteiligen Einstellungsdialogs,
- produktiver Health-/WebSocket-/Pong-Test,
- Live-Vertragstest:
  `hotkey → effectiveWakeWordEnabled=False`,
  `wake_word + hey_jarvis → effectiveWakeWordEnabled=True`.
- AP07-Servergesamtsuite: zweimal 379 Tests erfolgreich, 13 Skips; `compileall` und
  `git diff --check` grün.
- Produktiver AP07-Livevertrag: `logProtocolVersion=2`,
  `deliveryMode=sqlite_first`, zwei voneinander isolierte Session-Scope-
  Abonnements sowie Replay nach Reconnect.
- Ein durch die vorhandene Server-Test-WAV ausgelöstes
  `transcription.completed` wurde ohne Ausgabe von Transkriptinhalt über
  Event-ID/Cursor zwischen Live-Stream, HTTP-/SQLite-Historie und Replay
  korreliert.
- PyInstaller-Onefile-Build `dist/voice-stt-client.exe` für Version `0.1.0`:
  73.299.320 Byte; eingebettete Datei-/Produktversion und `--version`-Smoke
  erfolgreich.
- aktueller Debugfeedback-Onefile-Build für Version `0.2.0`: 73.747.530 Byte,
  SHA-256 `0b43f3da0ed61304087a32d952ce1c42011f42a717b22c7027ac3888f8f8b7ac`;
  acht WAVs plus Attribution im Archiv nachgewiesen.

Build und Release:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe scripts\build.py --clean
.\venv\Scripts\python.exe scripts\release.py --dry-run
.\venv\Scripts\python.exe scripts\release.py
```

Der Releasebefehl setzt die Version erst innerhalb eines rückrollbaren lokalen
Gates, wartet vor dem Tag auf grünes GitHub-CI für exakt den Release-Commit und
lässt das Tag-Workflow anschließend EXE und `SHA256SUMS.txt` veröffentlichen.
Details: `docs/RELEASE.md`.

Der vollständige Nachweis für M0–M3 steht unter
`docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/2026-08-09_AP07_M0_BIS_M3_ABNAHME_ABSCHLUSSBERICHT.md`.

Der aktuelle M10-Prüfstand und die noch offene reale 13-Punkte-Matrix stehen
unter `docs/2026-08-09_AP07_M10_FEHLERKAMPAGNE/PRUEFBERICHT.md`. M10 ist noch
nicht abgeschlossen: gesprochenes Hotkey-/Wake-Word-E2E, sichtbarer realer
STT-Disconnect, stilles Final und Langlauf fehlen. Store, Retention und
Serverneustart sind in der isolierten lokalen Kampagne erledigt.

Die erwarteten Fehlerlogs der Gesamtsuite stammen aus absichtlich simulierten
Negativfällen.

Auf diesem Windows-Host können Python-3.12-Plattformabfragen über WMI hängen.
Tests verwenden deshalb feste Windows-Werte. Der native LED-Zugriff läuft in
einem abbrechbaren Hilfsprozess; Build-Isolate und Onefile-App erhalten vor
Abhängigkeitsimporten eine Windows-spezifische Plattforminitialisierung. Der
Build-, Versions- und Prozessabschluss-Smoke ist damit grün.

## 6. Ergebnis des manuellen Schluss-Smokes

Die Prüfungen 1 bis 4 wurden am 28. Juli erfolgreich durchgeführt:

1. Hotkeystart bis Finaltext und Textinjektion;
2. Initial-Timeout ohne Sprache;
3. Folgeaufnahme nach kurzer Pause;
4. Hotkeyverlängerung bei längerer Denkpause.

Prüfung 5 deckte zwei eindeutige Clientfehler auf, die anschließend behoben
wurden:

1. Der Wake-Word-Maintainer existiert nun dauerhaft unabhängig vom Startmodus.
2. Moduswechsel beenden ihn nicht mehr und können daher keinen fatalen
   Helperabschluss erzeugen.
3. Ein Wechsel nach Wake Word gilt erst nach bestätigtem `READY`, gestartetem
   Audio und serverbestätigtem `start` als erfolgreich.
4. Scheitert die Aktivierung, wird die letzte Konfiguration einschließlich
   bestätigter Servergeneration wiederhergestellt.

Die frühere Fehlerfolge wurde lokal dreimal wiederholt. Zusätzlich bestanden
gegen den produktiven Server zwei vollständige Wechselzyklen über die
Generationen 1 bis 5; der Stream war bei jedem Hinwechsel aktiv und der Core
blieb bei jedem Rückwechsel am Leben.

Der sichere Live-Test verwendete absichtlich kein Mikrofon-Audio. Die
tatsächliche Erkennung eines gesprochenen `hey_jarvis` bleibt daher als kurzer
manueller Hardware-/Server-Nachweis offen. Vollständiger Fixnachweis:
`docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`.

## 7. Maßgebliche Dokumente

- `PLANUNG/` des aktiven Arbeitsblocks unter `ARBEITSDATEIEN/10_AKTUELL/` (Einstieg über `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`; ersetzt das frühere `docs/IMPLEMENTATION_ROADMAP.md`)
- `docs/PROJEKTUEBERSICHT.md`
- `task.md`
- `docs/work-packages/AP06_UI_SHELL.md`
- `docs/work-packages/AP06_UI_SHELL_FOLGEUMFANG_AUSFUEHRUNGSAUFTRAG.md`
- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md`
- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md`
- `docs/2026-07-28_AP06_FOLGEUMFANG_ABSCHLUSS/ABSCHLUSSBERICHT.md`
- `docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md`
- `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`
- `docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/2026-08-09_AP07_M0_BIS_M3_ABNAHME_ABSCHLUSSBERICHT.md`
- `docs/RELEASE.md`
- `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`
- `server-docs-for-client-development/`

Historische datierte Ordner bleiben Belege und überschreiben diesen aktuellen
Stand nicht.
