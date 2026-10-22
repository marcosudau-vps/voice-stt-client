## AP-IV2-020/R01 – REVIEW_READY,22.10.2026

[Abschlussbericht40](RUNS/R01-UMSETZUNG/40_REVIEW_READY_UND_KONSOLIDIERTE_QUALIFIKATION.md): **REVIEW_READY**: native ReSpeaker-Altfinal/Recovery/Runpausen und finale normale EXE mit A-final während B-Sprache sowie zwei sichtbaren Ausgaben belegt. Vollständige1400Windows/0Skips/79Module,83Helfer/0Skips,compileall PASS. Produkt0f6c85e/Server67f3ce45 unverändert.18letzte eigene Profile archiviert entfernt, externer Namensraum leer. Zusammengesetzte Methoden/Grenzen und historische Fehlläufe explizit dokumentiert; kein eigener ROOT_PASS. Gleicher R01/Paketbranch/PR15; Schreibhoheit für unabhängigen Review zurückgegeben.

Nachfolgende datierte Zwischenstände sind historisch und durch Bericht40 konsolidiert.

## AP-IV2-020/R01 – Laufzuordnung und Hilfstimer,22.10.2026

[Bericht39](RUNS/R01-UMSETZUNG/39_LAUFZUORDNUNG_UND_TESTTIMER.md): Mensch meldet eingefügten Text/Fensterschluss; gespeicherte Vorbereitung dagegen TIMEOUT ohne Clientstart, Satz nicht mehr bekannt. Beobachtung erhalten, Zuordnung NOT_PROVEN. Hilfstimer korrigiert: vor Start unbegrenzt warten, Laufbudget erst ab Clientstart.82Helfer/0Skips und compileall PASS, Produkt0f6c85e unverändert. Alle verbliebenen eigenen Profile/Helfer-TEMP archiviert entfernt, genehmigter Namensraum leer, kein laufender Test. Keine weitere Sprach-/Wahrnehmungsprobe gestartet. Technische Restmatrix bleibt BLOCKED, gleicher R01/PR15.

## Aktuelle Restqualifikation,22.10.2026

[Bericht38](RUNS/R01-UMSETZUNG/38_ADMIN_UAC_EXE_UND_MINIMALER_ABSCHLUSS.md): Adminguard positiv und generationgebunden, erhöhtes eigenes UAC-Ziel/APIstatus und drei native Stereomix-EXE-Einfügungen belegt. Erste ReSpeaker-ASR korrekt, automatische Einfügung fehlte; bewusster EXE-Reinsert erfolgreich. Minimaler Ein-Satz-Wakeversuch ohne Hotkeys vorbereitet, Wiederholen/Weiter repariert.80Helfer/Qt PASS; Produkt0f6c85e und1400Windowsbeleg unverändert. Wahrnehmungsabfragen menschlich abgeschlossen. Zehn beendete Profile plus Helfer-TEMP hashgesichert entfernt; nur ungestartete Abschlussprobe bleibt. Technische Restgrenzen NOT_PROVEN, BLOCKED/gleicher R01/PR15.

## Aktuelle Paarqualifikation,20.10.2026

Neuer menschlich benannter und tatsächlich belegter Serverstand `67f3ce45f6ea1ff659382e40c194c70bd33d58ff` nach Wakefix/Identitätserweiterung. Bisheriger Pinada13b0 bleibt historische Vertrags-/Testherkunft. [Rückkehr und neue Belege](RUNS/R01-UMSETZUNG/27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md); keine ungeprüfte Übertragung alter Paar-PASS.

# AP-IV2-020 – reale Windows-, Modell- und Hardwarequalifikation

Status **REVIEW_READY**, Workflow **REVIEW_READY**,22.10.2026.
Aktuelle Gesamtbewertung siehe Bericht40; unabhängige Abnahme ausstehend.
Rolle: ein Umsetzer, R01-UMSETZUNG. Schreibhoheit für unabhängiges Review zurückgegeben.
Branch `work/client-v2/ap-iv2-020`, Base `feat/client-v2`, tatsächlicher Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
Serverbasis `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Clientprodukt erhält ausdrücklich freigegebene enge Recoverykorrekturen; neue Qualifikation erforderlich.

[Vertrag](../../PLANUNG/ARBEITSPAKETE/AP-IV2-020.md), Planung Revision 10,
Rollenregelversion 7. Keine Produktcodeänderung ohne gesonderte Freigabe.
Keine kanonische Übernahme, Releases, Tags oder Serverpromotion beauftragt.

- [Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md)
- [Laufender Report](RUNS/R01-UMSETZUNG/01_REPORT.md)
- [Evidenzindex](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md)

AP-IV2-010 nach unabhängigem R02-ROOT_PASS und menschlichem R03-Prompt
tatsächlich per PR14-Squash übernommen. Nachmergebeleg in dieser Akte.
Reale Pflichtfälle bleiben bis zur Durchführung NOT_RUN/NOT_PROVEN.

Zehn technische Reconnect-/Recoveryfindings behoben; [Audit und neue Qualifikation](RUNS/R01-UMSETZUNG/05_RECONNECT_AUDIT.md).
Keine fachliche Abgabe. R01-Schreibhoheit bleibt für autorisierte Fortsetzung erhalten.

Kumulativer [Draft-PR #15](https://github.com/marcosudau-vps/voice-stt-client/pull/15), Base feat/client-v2.
IN_PROGRESS, kein REVIEW_READY; R01 behält Schreibhoheit für die genehmigte Fortsetzung.

## Scope-Ausnahme bei Fortsetzung R01 (2026-10-15)

Der [menschliche Fortsetzungsauftrag](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md) erlaubt eng auf Client-Reconnect/Recovery begrenzte Produktcode- und Testkorrekturen einschließlich weiterer nachgewiesener zusammenhängender Fehler. Dies ersetzt die ursprüngliche Produktcode-Sperre ausschließlich in diesem Scope. Derselbe R01, Paketbranch und Draft-PR #15 bleiben aktiv. Neue Produktidentität erfordert neue Windows-, Build- und Paarqualifikation; bisherige Nachweise bleiben historische Evidenz. Keine Servercodeänderung, Protokoll-/Sicherheitsänderung, Promotion, Release, Tags oder kanonische Übernahme freigegeben. Keine unabhängige Abnahme vorweggenommen.

## Zusätzliche Produktausnahme UX01, gleicher R01

[Ausdrücklich freigegeben](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/006_UX01_FREIGABE.md): bestehende Einstellung Leerzeichen anhängen wirksam machen, rohe Finals/History/Deduplizierung erhalten, dauerhafte Regressionen und neue Produkt-/Buildqualifikation. Produkt17261e6, neue [Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/ux01/INDEX.md). Keine sonstige Erweiterung der ursprünglichen Qualifikationsausnahme. Reale Pflichtfälle bleiben bis zur vollständigen Durchführung offen.

## Zusätzliche Produktausnahmen UX02 und UX03, gleicher R01

UX02 ist [ausdrücklich freigegeben](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/012_UX02_FREIGABE.md)
und am Produktd95043e technisch sowie physisch belegt: begrenztes Warten auf
freigegebene Modifiertasten vor nativer Einfügung, keine künstlichen Key-Ups.

UX03 ist durch den [direkten Fixauftrag vom18.10.2026](RUNS/R01-UMSETZUNG/09_UX03_CLOSE_SOUND.md)
freigegeben: fehlenden Beendigungston an serverbestätigtem Eingabeschluss
korrigieren, einschließlich Regression und neuer Kandidaten-/Buildqualifikation.
Produkt7bb5646, [Belege](RUNS/R01-UMSETZUNG/EVIDENCE/ux03-close-sound/assessment.json).
Kein Server-/Wirewechsel. Die ergänzte [Sound-/LED-/Triggerübersicht](RUNS/R01-UMSETZUNG/10_FEEDBACK_UEBERSICHT.md)
unterscheidet wirkliche V2-Ausgaben von lediglich deklarierten Regeln.

## Serverblocker IV2-020-W01

[Livebefund, echter Modellrepro und konkreter Korrekturweg](RUNS/R01-UMSETZUNG/12_WAKE_REAKTIVIERUNG_W01.md). Serverfix noch nicht beauftragt/instanziiert; Clientprodukt/Parent unverändert. Kein REVIEW_READY.

## Testlückenliste nach Infrastrukturentfernung, 19.10.2026

[Liste17](RUNS/R01-UMSETZUNG/17_TESTLUECKEN_UND_WIEDERHOLUNGEN.md) trennt
bereits abgedeckte enge Prüfungen, zuerst aus Belegen zu klärende Zuordnungen,
erforderliche praktische Nachprüfungen und die schon vorher offenen M01–M12.
Vier ausgeschlossene Frühakten besitzen spätere scopegleiche Wiederholungen;
keine rückwirkende Heilung, kein neuer M-PASS. Keine Serverwiederanlage beauftragt.

## Autonome Belegklärung durchgeführt, 19.10.2026

[Bericht18: Ergebnisse und sieben tatsächliche Restpunkte](RUNS/R01-UMSETZUNG/18_AUTONOME_KLAERUNG_UND_RESTPUNKTE.md).
25 neue Offline-Metadatenprüfungen PASS, sechs Fixtures und elf Archive identisch,
elf konkrete Fall-/Sessionverknüpfungen, Logfault-Imagebindung geschlossen.
Frühe nicht rekonstruierbare Runner und fehlende Admissionantworten ausdrücklich
begrenzt. Kein neuer Server-/Clientlauf, kein M-PASS; W01 und Zielentscheidung offen.

## Reihenfolgeentscheidung und vorhandenes V2-Ziel,19.10.2026

[Menschliche Präzisierungen017](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/017_W01_AUFSCHUB_UND_V2_TESTZIEL.md):
unabhängige Clientarbeiten zuerst; W01 später als gesonderter Server-FIX, betroffene
Realgates weiter vor vollständiger AP020-Annahme. [Fallabgrenzung19](RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
Pro-/Normal-V2 unter /ws/v2 erreichbar und Build-/aktuelle Image-/Quell-/Wheel-
Identitäten dem Serverpin zugeordnet.180s diagnostische Wartegrenzen. Kein neuer
Server-/Produktstand, keine Serverproduktfreigabe und keine voreilige Paketabnahme.

## Zusatznachweis 19.10.2026 – R11 im freigegebenen Recovery-Scope

[Durchlauf und USB-Korrektur](RUNS/R01-UMSETZUNG/22_GEFUEHRTER_DURCHLAUF_UND_USB_RECOVERY.md): reale USB-Abweichung reproduziert, eng begrenzt korrigiert, neues Produkt0f6c85e und1400Windows-Tests PASS. Kein Abschluss der offenen Realgates.

## Physische R11-Schließung und Idle-Kalibrierung,19.10.2026

[Bericht23](RUNS/R01-UMSETZUNG/23_USB_BESTAETIGT_UND_IDLE_KALIBRIERUNG.md): R11 physisch erfolgreich geschlossen. Weitere Pflichtgates unverändert offen; neue gewünschte Idle-Untergrenze30% nur Testkonfiguration, Sichtbestätigung ausstehend. Paket weiter BLOCKED, kein REVIEW_READY.

## Idle bestätigt / LED-only-Isolation,19.10.2026

[Bericht25](RUNS/R01-UMSETZUNG/25_IDLE_BESTAETIGT_UND_LED_ISOLATION.md): menschliche direkte Idle-Kalibrierung30/100% bestätigt, zusätzlicher kontrollierter LED-only-Ausfall bei idle ohne Audio-/Sessionwirkung PASS_SCOPED. Gesamte M-/Frozen-/Wakequalifikation weiter offen; Paketstatus BLOCKED, gleicher R01/PR15.


## Autonome Restprüfung,19.10.2026

[Bericht26](RUNS/R01-UMSETZUNG/26_AUTONOME_RESTPRUEFUNG_UND_OFFENE_PUNKTE.md):
native Credential-Lebenszyklen und idle-Runpause/Recovery PASS_SCOPED,36Helfer-
und neue volle1400Windows-Tests/0Skips PASS. Keine Produktänderung;
fehlende Kombinationen/Admin/Frozen/W01 bleiben offen.15gesicherte externe
Aufräumreste wegen automatischer Löschablehnung. Gleicher R01/PR15, kein REVIEW_READY.


## Reale Wakeauswertung,20.10.2026

[Bericht28](RUNS/R01-UMSETZUNG/28_WAKE_LIVEAUSWERTUNG_UND_RUHEKONTROLLE.md):
zwei aktuelle Sound-an-Wake-/Timeoutproben PASS_SCOPED, Sound-aus-Kontrolle
wegen kurzer Ruhephase NOT_PROVEN und allein zu wiederholen.48Helfer/Qt und
erneut1400Windows/0Skips PASS. Keine Produkt-/Serveränderung, übrige Gates offen.


## AP-IV2-020/R01 – W01-Kontrolle bestätigt,20.10.2026

[Bericht29](RUNS/R01-UMSETZUNG/29_W01_KONTROLLE_BESTAETIGT_UND_RESTGATES.md): W01-Kontrolle Alexa ohne Sound PASS_SCOPED: genau1Wake/Activation/Timeout,29,765s weitere echte Audio-Nachbeobachtung ohne Folgetrigger,1543Pakete, keine Sprache/Final/Paste, menschlich Wie erwartet, Exit0. Damit alle3vorgesehenen Livekontrollen und13Modellfälle erfolgreich; konkretes W01 CLOSED_VERIFIED_SCOPED. Vollständige M-/Frozen-/Both-/Nutzsprachgrenzen-/30min100-Gates bleiben offen. Produkt0f6c85e/Server67f3ce45 unverändert;19private Aufräumreste automatisch gegen Löschen gesperrt. REAL-01/02/03/04 sowie M-02/M-10 bleiben vollständige Pflichtgates mit getrennten Teilbelegen.


## AP-IV2-020/R01 – Controls/Logs,20.10.2026

[Bericht30](RUNS/R01-UMSETZUNG/30_CONTROLS_LOGANSICHT_UND_REFRESH.md): Denkpause mit2Segmenten/F9/2exakten nativen Einfügungen, Cancel mit82,969s weiterer Audioübertragung ohne Ausgabe und menschlich ausdrücklich bestätigte Server-/Tab-/Logansicht PASS_SCOPED; T01 geschlossen. Native Refreshprobe enthielt kein Refresh und bleibt NOT_PROVEN, lieferte aber korrekt gebundenen Altfinal-nach-Neustart-Beleg203ms. Zwei autonome reale ASR-/Controls-/Deadline-Refreshfälle PASS_SCOPED. T04-Testhäkchenfehler mit Regression/Qt korrigiert; nur native Refreshprobe entspannt erneut vorbereiten, übrige vollständige Gates offen. REAL-01/02/04/06 und volle M-Gates bleiben Teilqualifikation.


## AP-IV2-020/R01 – native Refreshpfade,20.10.2026

[Bericht31](RUNS/R01-UMSETZUNG/31_REFRESH_AUFNAHME_UND_NATIVER_NACHSPRECHPFAD.md): Menschlicher nativer F8-Refresh während segment_active, F9/Finish und2exakte native Einfügungen derselben Activation PASS_SCOPED; menschlicher15sNachsprechfall bleibt phasenbedingt NOT_PROVEN. Ohne weitere menschliche Wiederholung:2reale native Windows→WM_HOTKEY→Qt→Controls→ASR-Nachsprechfälle bei5000ms/6Callbacks PASS_SCOPED, Fristverlängerung/nichtadditives Wiederholen/Timeout bestätigt. T04 unterscheidet Phasen;56Helfer/Qt PASS, bytegleiches Produkt0f6c85e behält1400Windows/0Skips.21hashgesicherte Aufräumreste automatisch gesperrt. REAL-01/04/06 und volle M-Gates bleiben Teilqualifikation.


## AP-IV2-020/R01 – Mute/Reinsert/Wakepause,20.10.2026

[Bericht32](RUNS/R01-UMSETZUNG/32_MUTE_REINSERT_UND_WAKEPAUSEN.md): Hardware-Mute27,297s/zehn blockierte F8 und bewusste Wiederfreigabe/1exakte Einfügung sowie Reinsert1Final/2passende automatische+manuelle Ausgaben PASS_SCOPED. Zwei aktive Wake-Modell-/Pausen-/Reconnectfälle PASS_SCOPED. Erweiterte Pause→Recovery→manuelle Aufnahme mit Wakefixture→Cancel erzeugt zweimal Zusatzwake bei Stille: IV2-020-W02 offen, Ursache noch einzugrenzen; kein Serverfix vorgenommen.59Helfer/Qt PASS, Produkt0f6c85e unverändert/1400Windowsbeleg erhalten.22gesicherte Aufräumreste automatisch gesperrt. REAL-01/03/04/06 bleiben Teilqualifikation; W02 ausdrücklich FAIL.


## AP-IV2-020/R01 – BOTH und konsolidierte Restgates,20.10.2026

[Bericht34](RUNS/R01-UMSETZUNG/34_BOTH_ABSCHLUSS_UND_KONSOLIDIERTE_RESTGATES.md): Drei übernommene BOTH-Aufgaben PASS_SCOPED: natives Manual-F8/F9 und beide direkten Wake-Nutzsätze genau einmal ohne Rufwort;18,782/23,313s echte Ruhe ohne Zusatzwake. Erster Alexa-Versuch bewusst wiederholt, bleibt NOT_PROVEN. Realer Watchdog55,062sWarnung/60,015sAblauf und3gebundene ASRfinals aus demselben Rohdurchlauf nach phasengenauer Nachauswertung PASS_SCOPED; falsche Einsegmentannahme als Hilfstest-FAIL erhalten.61Helfer/Qt PASS, Produkt0f6c85e/1400Windowsbeleg unverändert. Keine identischen Sprechwiederholungen; technische/EXE-/Dauerreste gebündelt, W02 offen.23Aufräumreste automatisch gesperrt.


## AP-IV2-020/R01 – Dauerlauf/Wakeanforderungen/Aufräumen,21.10.2026

[Bericht35](RUNS/R01-UMSETZUNG/35_DAUERLAUF_WAKEANFORDERUNGEN_UND_AUFRAEUMEN.md): Automatischer zusammenhängender1800.015s/100Activations-Lauf mit echten Modellen PASS_SCOPED;100Finals/100Historyeinträge/100kontrollierte Injektionsversuche, drei eigene Recoveryaktionen. Physische/Frozen-M12-Anteile offen. W02 unverändert0/2reproduziert, historische2FAIL bleiben offen;0,90/2Frames erhält beide Positivfixtures,3/5Frames verfehlen Jarvis. Keine Defaultübernahme. Alle26eigenen externen Laufzeitordner hashgesichert entfernt.70Helfer/Qt und neue1400Windows/0Skips PASS; Produkt0f6c85e unverändert. Zwei Fehlversuche separat erhalten.


## W02-Disposition und Freigabereste,21.10.2026

[Bericht36](RUNS/R01-UMSETZUNG/36_W02_ABSCHLUSS_UND_FREIGABERESTE.md): W02 auf ausdrückliche menschliche Entscheidung als aktuell nicht mehr reproduzierbar geschlossen; kein eigener Freigabeblocker. Historische2FAIL erhalten, keine identifizierte Codekorrektur behauptet. Rest: technische Kombinationen, finaler EXE-/Admin-/Clipboard-/physischer Abschluss und Akten/ unabhängige Abnahme. Keine Wiederholung bestandener Standarddiktate, USB-Grundprobe oder des identischen30min100-Replaylaufs. Keine Testurteile rückwirkend geändert.


## Autonome Restqualifikation,21.10.2026

[Bericht37](RUNS/R01-UMSETZUNG/37_AUTONOME_RESTQUALIFIKATION_UND_MENSCHLICHE_GRENZEN.md): Autonome Restprüfung:29aktuelle Runtime-Kombinationsfälle, beide engen Renngewinner,3Altfinal/B-Sprache-Paare, native Clipboard-/Prozessabbruchfälle, echter LED-only-Ausfall bei offenem Input und separate SQLite-Logstoresperre PASS_SCOPED. Qualifizierte EXE startet nativ mit realem ReSpeaker/Ready. Neue1400Windows/0Skips,73Helfer/0Skips und Qt/retirierter Starter PASS; Produkt0f6c85e unverändert. Alle19neuen Laufzeitordner gesichert entfernt. Menschlicher Rest: gültiger Admincheck, erhöhtes Ziel/UAC, finaler EXE-/physischer/Umwelt-/Overlay-Abschluss einschließlich T02/T03; W02 bleibt geschlossen. BLOCKED/IMPLEMENTATION_IN_PROGRESS, gleicher R01/PR15.
