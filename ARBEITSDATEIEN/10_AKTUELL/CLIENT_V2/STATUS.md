## AP-IV2-020/R01 – BOTH abgeschlossen, Restgates konsolidiert,20.10.2026

[Bericht34](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/34_BOTH_ABSCHLUSS_UND_KONSOLIDIERTE_RESTGATES.md): Drei übernommene BOTH-Aufgaben PASS_SCOPED: natives Manual-F8/F9 und beide direkten Wake-Nutzsätze genau einmal ohne Rufwort;18,782/23,313s echte Ruhe ohne Zusatzwake. Erster Alexa-Versuch bewusst wiederholt, bleibt NOT_PROVEN. Realer Watchdog55,062sWarnung/60,015sAblauf und3gebundene ASRfinals aus demselben Rohdurchlauf nach phasengenauer Nachauswertung PASS_SCOPED; falsche Einsegmentannahme als Hilfstest-FAIL erhalten.61Helfer/Qt PASS, Produkt0f6c85e/1400Windowsbeleg unverändert. Keine identischen Sprechwiederholungen; technische/EXE-/Dauerreste gebündelt, W02 offen.23Aufräumreste automatisch gesperrt. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.

## AP-IV2-020/R01 – Mute/Reinsert bestätigt, überlagerter Wakefall offen,20.10.2026

[Bericht32](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/32_MUTE_REINSERT_UND_WAKEPAUSEN.md): Hardware-Mute27,297s/zehn blockierte F8 und bewusste Wiederfreigabe/1exakte Einfügung sowie Reinsert1Final/2passende automatische+manuelle Ausgaben PASS_SCOPED. Zwei aktive Wake-Modell-/Pausen-/Reconnectfälle PASS_SCOPED. Erweiterte Pause→Recovery→manuelle Aufnahme mit Wakefixture→Cancel erzeugt zweimal Zusatzwake bei Stille: IV2-020-W02 offen, Ursache noch einzugrenzen; kein Serverfix vorgenommen.59Helfer/Qt PASS, Produkt0f6c85e unverändert/1400Windowsbeleg erhalten.22gesicherte Aufräumreste automatisch gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – native Refreshpfade geprüft,20.10.2026

[Bericht31](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/31_REFRESH_AUFNAHME_UND_NATIVER_NACHSPRECHPFAD.md): Menschlicher nativer F8-Refresh während segment_active, F9/Finish und2exakte native Einfügungen derselben Activation PASS_SCOPED; menschlicher15sNachsprechfall bleibt phasenbedingt NOT_PROVEN. Ohne weitere menschliche Wiederholung:2reale native Windows→WM_HOTKEY→Qt→Controls→ASR-Nachsprechfälle bei5000ms/6Callbacks PASS_SCOPED, Fristverlängerung/nichtadditives Wiederholen/Timeout bestätigt. T04 unterscheidet Phasen;56Helfer/Qt PASS, bytegleiches Produkt0f6c85e behält1400Windows/0Skips.21hashgesicherte Aufräumreste automatisch gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – Controls/Logansicht und Refresh,20.10.2026

[Bericht30](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/30_CONTROLS_LOGANSICHT_UND_REFRESH.md): Denkpause mit2Segmenten/F9/2exakten nativen Einfügungen, Cancel mit82,969s weiterer Audioübertragung ohne Ausgabe und menschlich ausdrücklich bestätigte Server-/Tab-/Logansicht PASS_SCOPED; T01 geschlossen. Native Refreshprobe enthielt kein Refresh und bleibt NOT_PROVEN, lieferte aber korrekt gebundenen Altfinal-nach-Neustart-Beleg203ms. Zwei autonome reale ASR-/Controls-/Deadline-Refreshfälle PASS_SCOPED. T04-Testhäkchenfehler mit Regression/Qt korrigiert; nur native Refreshprobe entspannt erneut vorbereiten, übrige vollständige Gates offen. Produkt0f6c85e/Server67f3ce45 unverändert, gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS.

## AP-IV2-020/R01 – W01-Rückkehr erfolgreich,20.10.2026

[Bericht29](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/29_W01_KONTROLLE_BESTAETIGT_UND_RESTGATES.md): W01-Kontrolle Alexa ohne Sound PASS_SCOPED: genau1Wake/Activation/Timeout,29,765s weitere echte Audio-Nachbeobachtung ohne Folgetrigger,1543Pakete, keine Sprache/Final/Paste, menschlich Wie erwartet, Exit0. Damit alle3vorgesehenen Livekontrollen und13Modellfälle erfolgreich; konkretes W01 CLOSED_VERIFIED_SCOPED. Vollständige M-/Frozen-/Both-/Nutzsprachgrenzen-/30min100-Gates bleiben offen. Produkt0f6c85e/Server67f3ce45 unverändert;19private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – aktuelle Wake-Liveauswertung,20.10.2026

[Bericht28](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/28_WAKE_LIVEAUSWERTUNG_UND_RUHEKONTROLLE.md): Aktuelle reale Alexa-/Hey-Jarvis-Proben mit Sound je genau1Activation/Timeout,20,625s bzw6,954s weitere belegte Audiobeobachtung ohne Folgetrigger, menschlich Wie erwartet: PASS_SCOPED. Sound-aus-Kontrolle endet vorzeitig: nur1,875s Audio nach Timeout, NOT_PROVEN statt angenommener5s. Nur diesen Fall wiederholen; Testoberfläche wartet eine bereits laufende Ruhephase nach explizitem Beendenwunsch ab, Fensterclose bleibt Abbrechen.48Helfer/Qt und neue1400Windows/0Skips PASS. Produkt0f6c85e/Server67f3ce45 unverändert;18private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – Rückkehr vom Serverfix,20.10.2026

[Bericht27](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md): Neuer Pro-V2-Server67f3ce45/Tree74f37cad/Version2.0.0 über öffentliche Info, passenden Gitbaum/-datum und echten Hello bestätigt; Wakefix-Mergee761b973 direkter Parent.13reale Modellreplays/18Activations ohne Zusatzwake in geprüfter digitaler Stille PASS_SCOPED, native Source/ReSpeaker133Pakete und neue1400Windows/0Skips/43Helfertests PASS. W01-Live-Mikrofon-/Schweige-/Soundvergleich vorbereitet, keine vollständige M-/Frozen-/30min100-Abnahme; Clientprodukt0f6c85e unverändert.17beendete private Aufräumreste automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – autonome Restprüfungen,19.10.2026

[Konkrete Restliste und neue Nachweise](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/26_AUTONOME_RESTPRUEFUNG_UND_OFFENE_PUNKTE.md): Windows-Vault-Lebenszyklus mit frischen Prozessen/Origintrennung und Löschung PASS_SCOPED; reale idle-Runpausen über zwei manuelle Reconnects/eigenen TCP-Abbruch/Software-Mute sowie frische Runtime PASS_SCOPED. Wakeengine aus, keine Aktivierung/Paste,5000ms erhalten;1400Windows/0Skips und36Helfertests PASS. Produkt0f6c85e unverändert. Offene Kombinationen, Frozen/Admin/W01 und Gesamtgates bleiben;15private gesicherte Laufordner automatisch gegen Löschen gesperrt. Gleicher R01/PR15, BLOCKED/IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY.

## AP-IV2-020/R01 – Idle bestätigt, LED-only-Störung autonom geprüft,19.10.2026

[Bericht25](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/25_IDLE_BESTAETIGT_UND_LED_ISOLATION.md): Weiß/min30%/peak100% am realen ReSpeaker nach20s ausdrücklich bestätigt und reproduzierbar gespeichert. R11 CLOSED, Produkt0f6c85e unverändert. Zusätzlicher nativer LED-only-Transportausfall bei idle isoliert: automatische LED-Recovery, Audio/Session stabil,59→210Frames, keine neue Activation/AudioAvailability-Mutation. Erster fehlerhafter Hilfstest bleibtFAIL wegen falscher Persistenzannahme; neue33Helfertests PASS.1400Windows-/Buildbeleg am bytegleichen Produkt bleibt gültig. Übrige Real-/Frozen-/W01-Gates offen, kein REVIEW_READY; gleiche R01/PR15.13gesicherte externe Aufräumreste durch automatische Freigabeprüfung „blocked by policy“ nicht gelöscht.

## AP-IV2-020/R01 – direkte Idle-Vorschau vorbereitet,19.10.2026

[Bericht24](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/24_IDLE_ZIELZUSTAND_UND_DIREKTVORSCHAU.md): Letzte menschliche Akzeptanz bewahrt, aber kein Aktivierungs-/Idle-Zielübergang im Lauf, daher30/100%-Kalibrierung NOT_PROVEN. Dauerhafte LED-only-Vorschau mit eigenem START/20s/Übernehmen erstellt, kein Mikrofon/Server/Hotkey nötig;31Helfertests/Qt-Selbstcheck PASS. Produkt0f6c85e unverändert, R11 CLOSED. Neue physische Bewertung und weitere M-/Frozen-/W01-Gates offen; BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher PR15. Zehn gesicherte externe Restordner automatisch mit „blocked by policy“ gegen Löschen gesperrt.

## AP-IV2-020/R01 – physische USB-Recovery bestätigt, Idle-Feinabstimmung offen,19.10.2026

[Neuer Nachweis](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/23_USB_BESTAETIGT_UND_IDLE_KALIBRIERUNG.md): R11 CLOSED am unveränderten Produkt0f6c85e; echter USB-Ausfall/Servercancel/Wiederöffnung und bewusstes neues F8/F9-Diktat exakt einmal eingefügt. Manual-Timeoutfeedback menschlich bestätigt. Gewünschte weiße Idle-Pulsvariante30/100% als bestehende Testkonfiguration gespeichert, Sichtbestätigung offen; Farbprofile ausdrücklich später.29Helfer-/1400Windows-Tests ohne Skips PASS. Gesamtpaket weiter BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleiche R01/PR15, kein REVIEW_READY. Neun gesicherte beendete externe Laufordner wegen automatischer Freigabeprüfung „blocked by policy“ nicht gelöscht.

## AP-IV2-020/R01 – elf Aufgaben ausgewertet, USB-Wiederholung offen

[Auswertung und Belege](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/22_GEFUEHRTER_DURCHLAUF_UND_USB_RECOVERY.md): 15 menschliche Versuche/14 Activations am alten Sourceprodukt7bb5646. Teilnachweise getrennt von vollständigen M-Gates; USB-Test FAIL. Autorisierte Recoverykorrektur am neuen Produkt `0f6c85e0ecf971e596aae1b7d265dad7132754e2`: 48 gezielte/1400 volle Windows-Tests ohne Skips, neue EXE/Wheel/sdist und native Source-/Wheel-Stillstandsprobe PASS. Physische USB-Wiederholung, Feedbackbestätigung, endgültige Frozen-/Realqualifikation und W01 offen. Workflow IMPLEMENTATION_IN_PROGRESS, Gesamtabnahme BLOCKED; kein REVIEW_READY. Sieben privat gesicherte externe Laufordner wegen automatischer Freigabeprüfung nicht gelöscht; Aufräumpflicht bleibt offen.

## AP-IV2-020/R01 – unabhängige Restprüfungen vor W01-FIX,19.10.2026

[Bericht19](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md):
Workflow IMPLEMENTATION_IN_PROGRESS im selben R01; Gesamtabnahme/Paketstatus
weiter BLOCKED durch offene Pflichtnachweise. W01 wird nach unabhängigen
Clientprüfungen separat korrigiert; keine Serverproduktfreigabe. Vorhandenes
Pro-/Normal-V2 /ws/v2 samt Pinada13b0 über tatsächliche Build-/Image-/Quellbelege
bestätigt. Keine neue Instanz, kein Deployment/Neustart; diagnostische Wartezeit180s.

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
[Aktuelle Sound-/LED-/Triggerübersicht](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/10_FEEDBACK_UEBERSICHT.md). Acht Alexa-Treffer mit
Scores0,908322..0,999994; Schwelle0,85 nur ungesetzter Offlinekandidat.
Dauerhafter Desktopstarter bleibt verfügbar. V1/VPS geschützt; gleicher PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – IN_PROGRESS, UX02 technisch und real geschlossen, 16.10.2026

Produkt d95043e nach freigegebener Modifierkorrektur:1390 Windows-Tests/0 Skips,1964 Servertests/14 erwartete optionale Skips,11 Prozessfälle,17 Grenztests,7 Socketsmokes PASS. EXE/Wheel/sdist und native Produkt-/Serverlaufzeit erneut qualifiziert; reale Recovery, ReSpeaker-Desktop-Neustart und sechs Modellreplays neu gebunden. Physische Modifierprobe PASS:250ms tatsächliche Halte-/Freigabe, exakte einmalige native Ausgabe/menschlich bestätigt; UX02 CLOSED. Zusätzlich realer Manual-F8→Sprache→F9-Pfad PASS: ein erkannter Final exakt nativ eingefügt/menschlich bestätigt. Freie isolierte Both-Instanz für LED/Sound/Overlay aktiv. Genannte Einstellungstabs über zweiten lokalen Dialog vorhanden; Teststarter-Logmanagerlücke T01 festgestellt, Korrektur vorbereitet/gezielt geprüft, native Bestätigung nach abgestimmtem Neustart offen. Übrige Realgates/Kalibrierung weiter offen. Kein REVIEW_READY, gleicher R01/Paketbranch/PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – BLOCKED durch UX02, 16.10.2026

[Testclient](../../../tests/manual/v2/README.md) fertig: feste Schritte, wandernder Fokus, Countdown8s, eigener Start/Wiederholen/Abbrechen. Zehn Helferprüfungen/Qt und volle1378Windows-Regression PASS. Manuelle F8/F9-Steuerung PASS, Zieleinfügung FAIL (Shift gehalten). Produktausnahme noch nicht freigegeben; Produkt17261e6 unverändert. Derselbe R01/Branch/Draft-PR15; kein REVIEW_READY. [Aktueller Report](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md).

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
[Report](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/VPS geschützt; Server nur lokal. Kein REVIEW_READY, Eigenreview, Merge oder Release.


Neuer Produkt-/Build-/Paarstand17261e6 autonom qualifiziert; native Ausgabebestätigung und vollständige Realgates bleiben offen. Der nächste Ein-Klick-Block steht im Testeditor bereit.

## Vorheriger datierter Stand

# Client V2 – AP-IV2-010 / R02-ABNAHME / ROOT_PASS, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

**R02:** [unabhängiger ROOT_PASS](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R02-ABNAHME/01_REPORT.md), 7/7 GATE PASS, 0 Findings. **R03-Freigabe ausdrücklich erteilt**; READY_FOR_CANONICALIZATION, Merge steht noch aus. Reales AP-IV2-020-Gate weiterhin NOT_RUN.

**R03-Übernahmebereit:** [menschlicher Originalprompt](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md), [Preflightbericht](30_AUSFUEHRUNG/AP-IV2-010/RUNS/R03-UEBERNAHME/01_REPORT.md), CI des letzten Docs-Commit noch zu prüfen; kein ACCEPTED vor nachgewiesenem Squash.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Client V2 – AP-CV2-110 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-14

[Paket-PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base `feat/client-v2`, Head `work/client-v2/ap-cv2-110`.

Aktiver Arbeitsblock [CLIENT_V2](README.md);
[Einstieg Planung](PLANUNG/README.md), [Workflowstatus](WORKFLOW_STATUS.json).
AP000 bis AP100 tatsächlich ACCEPTED auf feat/client-v2; letzter kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100-PASS, menschlicher R06-Auftrag und wirklicher PR12-Squash
[verifiziert](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).

AP110 auf `work/client-v2/ap-cv2-110`: ausführbare V1-Autoritäten entfernt,
Migrationreader und Utilities erhalten, Source/Wheel/sdist/Frozen mit belegter
Helloidentität und nativer Windows-GUI qualifiziert. Windows **1353 PASS**,
gezielte **234 PASS**, Servercheckpoint **17 PASS**, compileall/diffcheck und
alle Build-/Ressourcen-/Installationschecks PASS. Getesteter Produktcommit
`cf42a2a9d96c1ebc88035817a5d529dfe04e4306`; finale PR-Spitze ergänzt ausschließlich administrative Unterlagen.
[Report](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Kompatibilität](../../../docs/compatibility.md), [Runtime](../../../docs/protocol-v2-runtime.md).

Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.
Bekannte Legacy-Profile und History werden mit Backup migriert; kein V1-Fallback.
Builds liegen lokal unter dist, kein veröffentlichter Release. Keine realen
ASR-/Mikrofon-/USB-/Fremdanwendungs-/Wahrnehmungsgates behauptet.

**Aktueller Reviewabschluss (2026-10-14):** [AP110 R02 unabhängiger ROOT_PASS](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) auf `44cf9a8fd1669242c00997966addc3667d448aa0`; FINAL-03 bis FINAL-09 technisch PASS, keine offenen Pflichtfindings. **ROOT_PASS** mit menschlicher **R03-Freigabe** – finale Git-/CI-Prüfung und Squash stehen aus. Kein AP-IV2-010-Start zuvor.

**Übernahmefreigabe 2026-10-14:** [R03-Originalprompt](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) und [R03-Abschlussablauf](30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/01_REPORT.md) dokumentiert. Aktuelle Phase **READY_FOR_CANONICALIZATION**; unabhängiger R02-ROOT_PASS unverändert. Nach finaler CI und Head-/Baseprüfung ist der einzelne Squash-Merge von PR #13 erlaubt. Ohne belegten GitHub-Merge noch nicht ACCEPTED; kein Release/Tag/Servermerge/AP-IV2-010.

---

## Historischer AP100-Stand vor dessen tatsächlicher kanonischer Übernahme

# Client V2 – AP-CV2-100 / R05-ABNAHME / ROOT_PASS, 2026-10-13

AP-CV2-000 bis AP-CV2-090 auf `feat/client-v2` ACCEPTED; letzter kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der aktuelle AP-CV2-100-Paketbranch `work/client-v2/ap-cv2-100` ([PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)) wurde unabhängig am Kandidaten `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` geprüft: **technischer ROOT_PASS**, 6/6 Paketrequirements erfüllt, `CV2-100-R03-F01` geschlossen.

[R05-Abnahmebericht](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md), [unabhängige Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/EVIDENCE/INDEX.md), [R04-Korrekturbelege](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json).

Extern qualifizierte Windows11-Suite **1581 PASS**, gezielte Tests **210 PASS**, **17** echte gepinnte Client-/Servercheckpoints am Server `ada13b0`, GitHub-Actions-CI **38394758805** erfolgreich auf dem geprüften Kandidaten. Reviewer hat diese Belege unabhängig geprüft, aber keine eigene Windows-/Hardwaretestausführung vorgenommen.

**Nächster Schritt: WAITING_FOR_APPROVAL.** Ausdrückliche menschliche Freigabe des Squash-Merges von PR #12 erforderlich, davor aktueller PR-Head, unveränderte Base, ausschließlich administrative R05-Nachträge sowie finale CI prüfen. Kein Merge und kein Start von AP-CV2-110 durch dieses Review.

---

## Historischer R04-Stand vor unabhängigem R05-Review

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](WORKFLOW_STATUS.json), [Runtimeinterfaces](../../../docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

## Historischer Stand vor AP-CV2-020

# Client V2 – AP-CV2-010

AP-CV2-000 ACCEPTED auf `1cf076bd2ed56929b1a3780bc140da51348a8295`, PR #2. AP-CV2-010 ROOT_PASS (R02; Übernahmefreigabe ausstehend): [Paketakte](30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md), [Workflowstatus](WORKFLOW_STATUS.json). Reiner Codec; unveränderte Serverbaseline ada13b0. Nachmergeprovenienz ist in der AP010-Akte nachgewiesen, kein zweiter AP000-Abschlusscommit.

Die folgenden datierten Angaben bleiben Historie.

# Status – Client V2

## Aktuelle ergänzende Abnahme R05 (2026-10-11)

**AP-CV2-000 ROOT_PASS / READY_FOR_CANONICALIZATION**. R04 schließt F01 fachlich; R05 schließt den Testblocker: 1233 Windows-PASS plus5 Startup-PASS. [Report/Freigabe](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md). Finale PR-CI/Base vor Einzel-Squash prüfen; tatsächliche kanonische Übernahme noch nicht erfolgt. Neue Testverantwortung: Windows-Vollsuite im Umsetzungslauf, unabhängiger ChatGPT-Review anhand Code und gültigem Nachweis.

## Historische unabhängige Folgesichtung R04 (2026-10-11)

**AP-CV2-000 BLOCKED** ausschließlich wegen des noch fehlenden unabhängig durchgeführten/veranlassten vollständigen Windows-Prüflaufs. [R04-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R04-ABNAHME/01_REPORT.md). Das frühere Produktfinding `CV2-R02-F01` wurde anhand der korrigierten Startlogik fachlich geschlossen; die vorhandene Windows-CI [38163179818](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38163179818) besteht mit 1233 Tests. Unabhängiger eigener Windows-Test **NOT_RUN**, kein ROOT_PASS. Workflow-/Unterlagenänderungen auf ausdrücklichen Wunsch nicht inhaltlich bewertet. Keine kanonische Übernahme/kein Folgepaket.

## Vorheriger R03-Selbstqualifikationsstand

## Historischer Korrekturkandidat – R03 (2026-10-11)

**AP-CV2-000 REVIEW_READY**. [R03-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md): F01 selbst korrigiert, gesamte Clientsuite 1233 PASS; Wheel/sdist und EXE samt Smokes bestanden. Gemeinsamer Aktenprüfer, Statusabgleich und Testweg präzisiert. [Belegsatz einschließlich drei Archivteilen](PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/README.md) im selben Kandidaten. Nächste Aktion: unabhängiger Vollreview; bisheriger F01 braucht unabhängigen Recheck und R02-NOT_RUN eigenständige Windows-Nachweise. Kein ROOT_PASS oder Merge; Schreibrecht zurückgegeben.

## Historische unabhängige Abnahme – R02 (2026-10-11)

**AP-CV2-000 CHANGES_REQUIRED**. Im [R02-Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R02-ABNAHME/01_REPORT.md) ist `CV2-R02-F01` dokumentiert: Hotkey-Fallback speichert Benutzerpräferenz vor bestätigtem Corestart. Der unabhängige Windows-Gesamttest ist **NOT_RUN**, CI 38145266161 ist dagegen grün. Prüfkandidat `8b1c4c157b6b431dac6af69e2e264d0c37579bef`, Tree `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e`, Parent unverändert. Umsetzer-Korrektur und frischer unabhängiger Review stehen an; **kein ROOT_PASS, keine Übernahmefreigabe, kein CV2-010**.

## Historischer R01-Stand vor R02

Stand 2026-10-11. Planung Revision 10; **AP-CV2-000 REVIEW_READY** auf `work/client-v2/ap-cv2-000` ab Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [Paketakte](30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md), [Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json).

Feature-/Releasebasis in voice_stt_client integriert; vollständige pytest-/Unittest-Suite je 1221 Tests grün, Wheel und sdist außerhalb Checkout qualifiziert. Bisheriger V1-Transport bleibt; keine V2-Kompatibilität oder reale Hardwareabnahme. Alle Folgepakete PLANNED; bedingtes Server-FIX nicht gestartet.

Kein unabhängiger PASS und keine menschliche Übernahmefreigabe. Gemeinsame Feature-Spitze bleibt `050e776cf316eb332177294db0c0a2719c2b4415`; integrierter kanonischer Client-SHA offen. Nächste Aktion: unabhängige Abnahme in frischer Session. Ab Abgabe Umsetzer-Schreibrecht pausiert. CV2-010 erst nach PASS, ausdrücklichem Übernahmeprompt und nachgewiesenem Einzelaggregat.

Workflowweite Kandidaten-Gitrechte aus [Originalauftrag](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md) gesichert; keine Main-/Serverpromotion, Tags, Releases, Force-Pushes oder Cleanup. Server-Distributed/ada13b0 bleibt offen. Historischer Revision-9-Start bfade9d und Dokumentkorrektur Revision 10 bleiben erhalten.
