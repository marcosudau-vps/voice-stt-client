## UX02 geschlossen: reale physische Tastenfreigabe und native Ausgabe PASS, 16.10.2026

[Realer Nachweis](EVIDENCE/ux02/native-physical-20261016-01/assessment.json) am Quellcommit8c8e36b mit **vollständig identischem Produkt-/Test-/Skriptmanifest** zum qualifizierten Produkt d95043e: der tatsächliche Produktworker sieht physisches Shift+Ctrl, wartet250ms auf Freigabe, anschließend genau vier native SendInput-Ereignisse bei freien Modifiertasten. Genau ein Paste-Key ohne Shift/Alt und ein tatsächlicher MIME-Paste; exakter33-Zeichen-Zieltext einschließlich Leerzeichen. Autoritativer Text/IDs erhalten, Worker vor Ergebnisanzeige beendet. Mensch bestätigt [„Text sichtbar, Testblock abgeschlossen“](ZUSATZPROMPTS/013_UX02_NATIVE_BESTAETIGUNG.md). **IV2-020-UX02 CLOSED**; komplette M-Fälle bleiben offen.

Die Bestätigung erfolgte im Chat, nicht über den noch wartenden GUI-Übernahmeknopf. [Herkunft](EVIDENCE/ux02/native-physical-20261016-01/human-decision-chat.json) getrennt erhalten; nach nachgewiesenem Produktworkerstop nur den inaktiven eigenen Testcontroller beendet, eigene Anzeige abgeschlossen und tatsächliche F9-Registrierung erneut erfolgreich geprüft/freigegeben. [Finalisierung](EVIDENCE/ux02/native-physical-20261016-01/finalization.json). Der äußere Prozessbeleg endet dadurch mit erwartetem Nichtnull-Exit/Command-FAIL aus Helferbereinigung; dies ist kein funktionaler Produktfehler und wird nicht in PASS umetikettiert. Physischer Versuch/Workerstop und Cleanup sind separat erfolgreich belegt.

[Gesamtbeleg](EVIDENCE/ux02/qualification-summary.json) und wiederverwendbarer Evidenzprüfer prüfen nun zusätzlich diese native Quelle/Hashes/Herkunft. Kein erneuter Produktwechsel; volle1390er Suite/Build-/Paarbelege weiterhin exakt gültig. Nächster Schritt im selben R01: realer F8→Sprache→F9-Pfad, danach verbleibende gebündelte Realgates/Endkalibrierung. Kein REVIEW_READY.

### Vorheriger Zwischenstand vor physischer Bestätigung

## UX02 technisch requalifiziert; physische Tastenprobe offen

Status **IN_PROGRESS**, [zusätzliche menschliche Freigabe012](ZUSATZPROMPTS/012_UX02_FREIGABE.md), gleicher R01/Paketbranch/Draft-PR15. Native Backendabfrage berücksichtigt Shift/Ctrl/Alt/beide Windows-Tasten anhand des aktuellen High-Bits. Bestehender serieller Worker wartet höchstens1,5s auf Freigabe, in10ms-Schritten und beim Shutdown abbrechbar. Kein eigener Task/Thread, keine künstlichen Key-up-Ereignisse, keine automatische Nachinjektion. Vor dem Warten Fokus/Clipboardsequenz sichern; bei Wechsel überspringen. Vor tatsächlichem Paste erneut Sequenz validieren. Später während der Pasteverzögerung gedrückte Modifier werden ebenfalls berücksichtigt; gemeinsamer begrenzter Deadlinebereich. Autoritative Texte/IDs/History/Deduplizierung und bestehende Bedienfristen unverändert.

[Baseline](EVIDENCE/ux02/baseline.json)100 PASS. [Permanenter Rotbeleg](EVIDENCE/ux02/permanent-red.json): elf neue Tests,14 Subtest-/Fallfehler und ein erwarteter Fehler wegen noch fehlender nativer Backendmethode. Danach [112 gezielte PASS](EVIDENCE/ux02/targeted-green-final.json), zwölf neue dauerhafte Tests einschließlich zusätzlichem Sequenzabfragefehlerfall. Erstes Green enthielt eine alte nth-call-Faultfixture, deren Fehler durch die zusätzliche Sequenzvalidierung nun zu früh ausgelöst wurde; Fixture explizit wieder auf Restorephase ausgerichtet, gleiche fachliche Erwartungen erhalten. [Ursprünglicher komponierter Nachweis nach Korrektur](EVIDENCE/ux02/original-composed-green.json) ebenfalls PASS; OS-Modell und Statusabfrage verwenden denselben gehaltenen Tastensatz mit tatsächlicher zeitverzögerter Freigabe.

Win32-Grundlage: [Microsoft GetAsyncKeyState](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getasynckeystate) (aktueller Zustand im High-Bit; generische Shift/Ctrl/Alt decken beide Seiten) und [SendInput](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput) (vorhandene gedrückte Tasten beeinflussen Eingabe). Vollständige finale Windows-/Build-/Serverpaar-/Runtimequalifikation am Produkt d95043e bestanden. UX02 bleibt bis technischem Nachweis **und** realem Halte-/Freigabefall offen. Vorherige Produkt172-Belege bleiben historisch zugeordnet.

## Neue technische Qualifikation am Produkt d95043e, 16.10.2026

[Verifizierter Gesamtbeleg](EVIDENCE/ux02/qualification-summary.json): vollständige Windows-Suite **1390 PASS/0 Skips**, Server **1964 PASS/14 erwartete optionale Skips**, elf Prozessfälle,17 Grenztests und sieben echte Server-Socketsmokes. Alle555 gepinnten Serverblobs bytegeprüft; Compile/Diff/Umgebungen grün. [Wiederverwendbarer Evidenzprüfer](EVIDENCE/ux02/aggregate_qualification.py) validiert vollständige Loghashes, exakte Quellmanifeste, Produkt-/Serveridentitäten und lokale Binärhashes.

Produktcommit **d95043e96051d4022b297099391a4fdff0dcc12b**, Tree **413467dffb8b98a15c77617a34ed097d21b216df**, unveränderter kanonischer Parent b80ed8b, Server ada13b011e1d3829f78e7f389e3b927795a2b3be. [EXE/Wheel/sdist](EVIDENCE/ux02/build/artifacts.json) neu gebaut, Releaseguard/Twine PASS; native EXE und frisch isoliert installiertes Wheel melden exakt diesen sauberen Build und tatsächlich den gepinnten lokalen Server. Kein Release. Diese GUIproben verwenden absichtlich nicht verfügbaren Capture; reale Mikrofonprüfung separat.

[Echte Recovery](EVIDENCE/ux02/real-recovery-summary.json) PASS: HTTP408/429/5xx ohne JSON/Timeout, unklarer PATCH ohne Replay, drei Serverneustarts mit41,172/30,313/26,422s Wiederherstellung, Shutdown0,422s. [Trace](EVIDENCE/ux02/real-recovery-trace.json) und Vollstdout erhalten. Detail-JSON wurde durch namensgleiche äußere Commandmetadaten überschrieben; Zusammenfassung ausdrücklich aus Vollstdout rekonstruiert, keine verlorenen hochauflösenden Ressourcenwerte behauptet. Erstes Paar-Preflight verwendete falschen Serverrepo-Elternpfad, stoppte vor Tests; korrigierter echter Gitpfad /main bytegeprüft, Fehlerbeleg erhalten.

[Native Desktop-/ReSpeaker-Messung](EVIDENCE/ux02/native-desktop-metrics.json):40 Sekunden, ein tatsächlicher Neustart, Wiederbereitschaft35,25s, maximal12 Tasks/118251520 WorkingSet-/438775808 PrivateBytes, am Ende keine offenen Commands/Einfügungen, keine Captureüberläufe/-drops. Kein Aktivierungs-/30min100-Nachweis. Native Hotkey- sowie Settings/Credential-Prüfung PASS. Alle drei isolierten Profile unverändert durch temporäre Roundtrips geprüft:5000ms Follow-up,320ms Pre-Roll, AppendSpace=true.

[Sechs Originalaufnahmen erneut durch echte lokale Modelle](EVIDENCE/ux02/real-model-replay-summary.json) am neuen Quellstand: drei echte Wakepositive, zwei direkte Nutzsätze exakt, drei bekannte Negativaufnahmen ohne Aktivierung. Alexa-Pausensatz weicht weiter vom geplanten Wortlaut ab; gesprochener Wortlaut bleibt ohne menschliche Annotation NOT_PROVEN. Rohtext nur lokal; Replay ersetzt keine Liveaufnahme/native Ausgabe.

[Physische Tastenprobe](EVIDENCE/human/native_modifier_trial.py) mit [GUIadapter](EVIDENCE/human/native_modifier_editor.py) vorbereitet und Selbstprüfungen/Qt/Compile bestanden: alle Schritte vorher sichtbar, eigener Start,8s Vorbereitung, freiwilliges Wiederholen/Übernehmen. Produktworker muss tatsächlich gehaltene physische Modifier und deren Freigabe sehen, genau ein natives Paste mit freien Tasten und exakter Ausgabe; sonst NOT_PROVEN/FAIL. Keine synthetischen Tastenzustände/Mikrofon-/Serverbeteiligung in dieser Probe. **UX02 bleibt bis zu diesem Nachweis offen**, alle vollständigen M-Gates und menschliche Endkalibrierung ebenfalls offen. Historische Fehler-/Qualifikationsstände unten bleiben erhalten.

### Historischer Stand vor UX02-Freigabe

## Dauerhafter Testclient fertig; AP durch UX02 blockiert, 16.10.2026

Status **BLOCKED**, gleicher R01/Paketbranch/Draft-PR15. [UI-Auftrag011](ZUSATZPROMPTS/011_DAUERHAFTER_TESTCLIENT_UND_SCHRITTE.md) umgesetzt: [Code/Startanleitung](../../../../../../../tests/manual/v2/README.md), kompatible alte EVIDENCE-Einstiege. Alle acht Schritte vorher sichtbar, blauer Fokus wandert nach unten, kommende Schritte abgedunkelt, Satz bei Sprechfreigabe grün; Timer rechts. Acht Sekunden Bereitmachen nach tatsächlicher Runtime-/Audiobereitschaft (`--prepare-seconds 0..30`, nur Testzeit). Eigenes Lesen/Starten/Wiederholen/Abbrechen/Übernehmen ohne kurzen Folgetimer. Produkt-/Serverfristen unverändert. Launcher lehnt externe Server/andere Ports ab. Vorschau ohne Sprachclient/Mikrofon geöffnet.

[Prüfungen](EVIDENCE/ux01/manual-tool-permanent/summary.json): volle Windows-Regressionssuite1378 PASS/0Skips, zehn Helferregressionen PASS, echte Qt-Widgetprüfung für Schritte/Countdown/grüne Freigabe/keinen Rücksprung durch alte Events/Wiederholen/Abbrechen PASS; Legacy-Einstiege/CLI/Compile grün. Ein durch die neue Close-Sperre verzögerter erster Selbstprüfungsprozess wurde sauber beendet; finale Selbstprüfung endet regulär mit Exit0. Vorschauschriften nur lokal geladen, keine Fontdatei versioniert. Produkt und scripts unverändert; neue Tests unter tests/manual sind getrennt vom früheren Gesamtquellmanifest ausgewiesen.

[Reale Manualprobe](EVIDENCE/ux01/repeatable-manual-20261016-01/assessment.json): F8 activate/F9 finish tatsächlich accepted/applied, gleiche Activation, input_closed=finished, ein Final/ein command_sent. **Native Textausgabe FAIL**: Ctrl+Shift+V bei noch gehaltenem Shift, kein MIME-Paste,0Zeichen. Nutzer bewertet die Testbedienung positiv, bestätigt keinen eingefügten Text. F8/F9-Controlteil PASS; vollständige M01/M04 offen, M11 FAIL. [Gezielter UX02-Rotbeleg](EVIDENCE/ux01/modifier-finding/held-shift-red.json) reproduziert den Fehler am echten Final-/SQLite-/Queuepfad mit ersetzter OS-Grenze. Erwartetes FAIL eines Fehlernachweises, kein grüner Regressionstest.

[Konkreter zusätzlicher Korrekturscope](08_SCOPE_VORSCHLAG_UX02_MODIFIERTASTEN.md) ist vorbereitet und nicht angewandt. Bestehende Produktausnahmen002/006 betreffen Recovery/UX01; zusätzliche Entscheidung nötig. UI-Auftrag erledigt; vollständiges AP und REVIEW_READY wegen UX02/übriger Realgates offen.

## Wiederholen/Abbrechen und dauerhaft grüner Testsatz, 16.10.2026

Die menschlichen Vorgaben [009 Wiederholbarkeit](ZUSATZPROMPTS/009_WIEDERHOLBARE_TESTAUFGABEN.md) und [010 Farbe](ZUSATZPROMPTS/010_SATZ_FARBLICH_HERVORHEBEN.md) sind ausschließlich in Testhilfen umgesetzt. Eigenes großes grünes Plaintext-Satzfeld bleibt vor Start/während Statuswechseln sichtbar. Kein kurzer Vorlesetimer: der Controller startet erst nach bewusstem aufgabengebundenem Klick. Nach beendetem Client wählt der Mensch Wiederholen oder Übernehmen; keine automatische Folgeaufgabe. Abbrechen beendet die eigene Clientinstanz regulär über Qt, danach neue Vorschau und erneuter Startklick. Jede Wiederholung hat eine neue unverwechselbare Attempt-ID; Belege/Quellidentitäten/Exit/Editorhash/Bedienentscheidung bleiben pro Versuch erhalten. Bei Wiederholung wird nur der Text dieser Aufgabe zurückgesetzt; vorher übernommene Aufgabentexte bleiben erhalten. Veraltete Statusmeldungen/Bedienrequests wirken nicht auf neue Attempts.

[Helferprüfungen](EVIDENCE/ux01/repeat-controls/summary.json) PASS: acht Regressionen einschließlich zusammengesetztem Controllerlauf repeat→abort→accept mit getrennten Kindprozessen und Klicks; tatsächliche Qt-Widgets prüfen grüne separate Phrase, unveränderte Sichtbarkeit, Wiederholen ohne Autostart, Abbrechen, Restore des angenommenen Texts und Ablehnung alter Meldungen. Compile/Observer-CLI PASS. Synthetische Helferprüfungen sind kein Hardware-/M-PASS. CLIENT BEREIT erscheint jetzt erst bei tatsächlicher Runtimebereitschaft **und** verfügbarem Audio, nicht schon beim einzelnen Transportstatus. Produktfristen/Defaults bleiben unverändert; keine Produktänderung gegenüber17261e6.

[Vorherige manuelle Hotkeyprobe](EVIDENCE/ux01/manual-hotkey-20261016-01/assessment.json): null Activations/Finals, tatsächlicher Secondaryempfang nur in idle, keine F8-Callbackevidenz. Beide konfigurierten Keys bestätigt, kein Produktdefekt nachgewiesen. Nach menschlicher UX-Rückmeldung ausschließlich eigene Testsitzung regulär beendet, vollständige minimierte Diagnosen erhalten. Status NOT_PROVEN, kein funktionales PASS aus Prozess-Exit0.

## Zwei einzeln gestartete Live-Wake-Aufgaben bestätigt, 16.10.2026

[Auswertung](EVIDENCE/ux01/stepped-20261016-01/assessment.json): beide tatsächlichen Startklicks1/2, zwei vollständig beendete separate Produktsitzungen, kanonische IDs hey_jarvis/alexa mit Scores0,99658/0,99884, jeweils genau eine Activation/ein Final/ein command_sent-Einfügeversuch. Genau71Zeichen im eigenen Editor, beide Nutzsätze exakt und ohne Rufwort, Leerzeichen getrennt; Mensch bestätigt **„Beide vollständig, mit Leerzeichen“**. ReSpeaker und echte Modelle, tatsächliche native Paste-Ereignisse; unveränderte autoritative History. Sämtliche gemessenen Produktsourcehashes entsprechen exakt Produkt17261e6. Effektive Settings nach Bootstrap5000/320 in beiden Sitzungen. Keine Audioüberläufe, Capture-Drops oder ausstehenden Commands/Einfügungen am Ende.

F9 ausdrücklich **NOT_PROVEN**: kein Activation-Command-Ack, beide input_closed=timed_out nachjeweils5003ms ab recording_ended. Kein behaupteter Hotkeydefekt ohne reproduzierten Fehler. Nur direkte Nutzsprachvollständigkeit/Spaced Output PASS; M02 insgesamt weiterhin NOT_PROVEN (getrennte Sitzungen, Controls/Grenzannotation offen). Keine phonetische Echtzeitannotation ohne Rohaufnahme.

Nächster gezielter Test: eine manuelle F8/F9-Aufgabe mit Satz-/Tastenvorschau und eigenem Start, tatsächlichen nativen Controlcallbacks und semantischen Acks als zusätzliche passive Diagnose. [Vorprüfungen](EVIDENCE/ux01/hotkey-task-precheck/summary.json): sechs Gate-/I/O-Regressionen, Qt-Startkontrollen, Manual-/Wake-CLI und Compile PASS; beide konkreten Ctrl+Shift+F8/F9-Bindings temporär erfolgreich registriert und freigegeben. Keine Eingabe, Mikrofon- oder Fremdregistrierungsänderung beim Binding-Vorcheck. Produktcode unverändert. Dieselbe R01, kein vollständiger M-PASS/REVIEW_READY.

## Aufgabenweise Vorschau und ausdrücklicher Start, 16.10.2026

[Bedienvorgabe008](ZUSATZPROMPTS/008_AUFGABEN_START_UND_VORSCHAU.md) umgesetzt: Satz und Schritte vorab sichtbar, eigener Start für jede Aufgabe, zwischen den Aufgaben vollständig beendeter Client, erster Text bei zweiter Aufgabe erhalten. Nur Testhelfer verändert. `stepped_wake_trial.py` nutzt pro Aufgabe eine eigene tatsächliche Produktsession; diese beiden Einzelversuche beweisen für sich keine vollständige Same-Session-M02-/M12-Qualifikation.

[Helferprüfungen](EVIDENCE/ux01/task-start-controls/summary.json): sechs dauerhafte Gate-/I/O-Regressionen PASS, echte Qt-Widget-Selbstprüfung für Vorschau/voneinander getrennte Klicks/kein Autostart/Texterhalt PASS, alte automatische Zwei-Aufgaben-CLI wird vor Clientstart abgewiesen. Das sind Helferprüfungen, keine Sprach-/Hardware-PASS. Produkt17261e6 unverändert und dessen Qualifikation erhalten. Der vorige voice-repeat02 lief ohne Startklick in den Vorbereitungs-Timeout; keine neue Clientausführung daraus abgeleitet.

## Native UX01-Bestätigung und expliziter Sprachstart

[Echte native Probe](EVIDENCE/ux01/repeat-01/native-editor-spaced.json) PASS: genau40Zeichen mit angehängtem Leerzeichen im eigenen fokussierten Editor, ein command_sent-Versuch, vier tatsächliche SendInput-Ereignisse, autoritativer Text unverändert. [Quellhashbindung](EVIDENCE/ux01/repeat-01/native-product-binding.json) an vollständig qualifiziertes Produkt17261e6 exakt. **UX01 geschlossen.** Dies schließt keine vollständige M-Fallabnahme ein.

Der Auftraggeber war nach der Einfügeprobe abgelenkt und hatte einen weiteren Knopfdruck erwartet. Der automatisch angeschlossene Sprachlauf hatte null Activations/Finals und wurde normal beendet; [Bewertung](EVIDENCE/ux01/repeat-01/voice-attempt-assessment.json) NOT_RUN_HUMAN_SPEECH, kein funktionales PASS aus Exit0. Zur Entlastung erhält Sprache einen eigenen sichtbaren Startknopf; die bereits erfolgreiche native Probe wird nicht unnötig wiederholt. Reine Testhelferänderung, Produkt unverändert. [Gate-Selbstprüfungen](EVIDENCE/ux01/voice-ready-gate-check.json) PASS; die [Checkliste](07_TESTCHECKLISTE.md) ist aktualisiert.

## Wiederholung und sichtbare Checkliste, 15.10.2026

Der [menschliche Fortsetzungswunsch007](ZUSATZPROMPTS/007_WIEDERHOLUNG_UND_CHECKLISTE.md) verlangt Wiederholung des letzten kurzen Blocks und eine laufend gepflegte Liste. [Checkliste07](07_TESTCHECKLISTE.md) trennt technische PASS-Nachweise von offenen/partiellen realen M-Fällen. Ein frischer eigener Testeditor ersetzt den inzwischen beendeten alten Editor.

Der frühere Startversuch2 scheiterte vor der Freigabe/Einfügung mit tatsächlichem PermissionError beim Lesen der Diagnose; der Produktpfad war nicht gestartet. [Befund](EVIDENCE/ux01/editor-read-finding.json): zugrunde liegende Freigabe-/AppData-Ursache nicht sicher reproduziert. Der reine Testhelfer behält den logischen I/O-Pfad und liest die atomar ersetzte Diagnose bei erwarteten vorübergehenden Zugriffskonflikten begrenzt erneut. Kein Clipboard-/SendInput-Retry. Dauerhafte/andere Fehler blockieren. [Vier Helferregressionen](EVIDENCE/ux01/editor-diagnostic-reader-regression.json) und [500 tatsächliche Kindprozess-Lesezugriffe](EVIDENCE/ux01/editor-diagnostic-live-validation.json) PASS. Keine Produktänderung gegenüber17261e6; dessen volle Windows-/Build-/Paarqualifikation bleibt eindeutig gebunden.

## Neuer technischer Stand17261e6, 2026-10-15

UX01-Produktkorrektur und dauerhafte Regressionen umgesetzt. [Neue technische Qualifikation](EVIDENCE/ux01/qualification-summary.json): Windows1378 ohne Skips, Server1964/14 ausgewiesene optionale Skips,11 reale Prozessfälle,17 Grenztests und7/7 Smokes PASS. EXE SHA256 `56fe943b8dff3cacd554dc6ee8c5adc537bdd4fdbe397c65e1357ce80ba5160a`, Wheel/sdist und Releaseguard/Twine PASS. Neue Frozen-/Wheel-Laufzeit, echte ReSpeaker-/Desktop-Recovery, reales HTTP-/Ack-/Restart-/Shutdown und natives Hotkey/Credential grün. Serverpin und kanonischer Parent unverändert. Lokaler feat-Branch ist veraltet; maßgebliche Remote-Base/merge-base b80ed8b wurde erneut per ls-remote bestätigt.

Echter separater Logstore-ENOSPC-Fall ohne STT-Lock PASS; Logerholung am Ende noch Backoff und daher unbewiesen. Zwei direkte Wake-Nutzsätze exakt und drei Negativaufnahmen ohne Aktivierung. Alexa-Pausenclip verfehlt den geplanten Text; manuelle Vergleichsausgabe enthält identisch denselben Nutztext. Tatsächlichen Wortlaut noch annotieren. Alle vollständigen M-Gates,30min100 und finale Wahrnehmung/Kalibrierung offen. UX01 bleibt bis tatsächlicher nativer Ausgabe mit aktivierter Einstellung offen. Ein-Klick-Probe mit anschließend zwei kurzen geführten Wakeaufgaben vorbereitet; keine allgemeine neue Freigabe erforderlich. IN_PROGRESS, kein REVIEW_READY.

## Fortschreibung UX01, 2026-10-15

[Zusatzfreigabe006](ZUSATZPROMPTS/006_UX01_FREIGABE.md) erweitert den Produktscope eng auf die bestehende Einstellung Leerzeichen anhängen. Fünf dauerhafte komponierte Regressionen in `tests/test_text_injector_spacing.py` führen autoritative Mirrorfinals über Finalconsumer, echte SQLite und seriellen Queueworker bis zur ersetzten Win32-Grenze. Drei Fälle reproduzierten das fehlende Leerzeichen vor der Produktkorrektur. Unveränderte Finals/History/IDs, Replaydeduplizierung, explizite Wiedereinfügung, False, vorhandener Whitespace und Clipboardrestore werden geprüft. Produktfix bildet ausschließlich den lokalen Ausgabepayload; vorhandene Rohtext-Testfixtures schalten die Einstellung ausdrücklich aus. [Gezielte100 PASS](EVIDENCE/human/ux01-targeted-green-final.json). Neue Voll-/Build-/Paarqualifikation läuft; UX01 bleibt bis dahin offen. Die vorherigen 41ca761-Qualifikationen bleiben historisch gebunden.

Menschlicher geführter Wakebefund: „Beide Sätze vollständig“. [Technischer Lauf](EVIDENCE/human/guided-wake-320.json) belegt die erste echte Einfügung; vor der zweiten war der eigene Editor nicht mehr im Vordergrund. Diese Abweichung ist dokumentiert und bleibt Teilnachweis. Kein vollständiger M02-PASS.

# AP-IV2-020 / R01-UMSETZUNG – IN_PROGRESS (Fortsetzung)

Die [ausdrückliche Scope-Freigabe](ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md)
erlaubt eng begrenzte Produkt-/Testkorrekturen für Reconnect/Recovery.
Maßgeblicher Fortsetzungsstand: [Audit und Korrekturen](05_RECONNECT_AUDIT.md).
Derselbe R01, Branch und Draft-PR #15 bleiben aktiv. Neue technische Qualifikation ist vollständig grün (1373 Windows-Tests,
1964 Server-Unit-Tests mit14 ausgewiesenen optionalen Skips,11 Prozessfälle,
neue EXE/Wheel/sdist und native Frozenprüfung). Zehn technische Findings geschlossen; reale M-Fälle und gemeinsame Kalibrierung bleiben offen. Kein REVIEW_READY.

## Gemeinsame Phase C – aktueller Zwischenstand

Reale Manualprobe durchgeführt: sieben Finals in vier bewusst wiederholten
Activations, jeweils genau ein Einfügeversuch. [3000ms](EVIDENCE/human/manual-followup-3000.json)
und [5000ms](EVIDENCE/human/manual-followup-5000.json) verglichen; Auftraggeber
bestätigt5000ms als passend. Isolierte Manual/Wake/Both-Profile entsprechend
gesichert, keine Produkt-/Serverdefaults geändert. M-01 bleibt wegen Overlap offen.
Separater UX-Befund: `append_space=true` ohne Wirkung; außerhalb Recoveryfreigabe.

Vor Wakeblock [reale Hostspeichergrenze](EVIDENCE/human/host-memory-constraint.json):
PowerShellstart mit OutOfMemoryException, nach sauberem Ende des Testclients nur
0,95GB bis Commitlimit. Mensch hat unbenötigte Anwendungen geschlossen; erneute
Prüfung ergibt10,7GiB Commitreserve. Wakeclient ist bereit mit bestätigten5000ms,
erster Wakeversuch ausgewertet. Beide IDs erkannt, keine sichtbare Injektion, weil
der Mensch das Editorfeld nicht fokussiert hatte. Danach sechs bewusst gestartete
WAVs aufgenommen und auf ausdrücklichen Wunsch mit Messskripten versioniert.
Echte Replays: Pre-Roll0 schneidet Wortanfänge,160ms reicht für Alexa nicht,
320/480ms erhalten beide direkten Nutzsätze.320ms für Liveprüfung vorbereitet. Keine eigene oder produktive
Installation beeinträchtigt. Kein vollständiger M-PASS und kein REVIEW_READY.

## Historischer Zwischenstand vor Scope-Freigabe

# AP-IV2-020 / R01-UMSETZUNG – BLOCKED

Stand 2026-10-15. Ein Umsetzer, derselbe laufende Auftrag. **Kein REVIEW_READY,
kein Eigenreview, kein ROOT_PASS und keine reale Gesamtabnahme.**
Produktcode unverändert; Testhilfen/Testkonfiguration, Belege und Planpflege erstellt.

## Ergebnis und nächste notwendige Entscheidung

**IV2-020-F01 / REAL-03 / M-07 FAIL:** Ein vorübergehender HTTPausfall bei echtem
lokalem Serverrestart wird dauerhaft `blocked/settings_preflight_failed`.
Zweimal mit echtem Desktop/ReSpeaker/source-qualified Server reproduziert,
Ursache mit zwei roten gezielten Reprotests isoliert. Kein Produktfix angewandt.
[Konkreter Korrekturvorschlag samt noch nicht angewandtem Patch](04_KORREKTURVORSCHLAG.md).
Der menschliche Originalauftrag verlangt für Produktänderungen eine ausdrückliche
Freigabe. Nächste Aktion: Entscheidung über enge Korrektur an SettingsService.prepare
und V2STTSession._connection plus Regressionen und neue Build-/Paarqualifikation.

Danach bleiben dieselben vorbereiteten [fünf Realtestblöcke](02_GEMEINSAMER_TESTABLAUF.md)
und die [gemeinsame Kalibrierung](03_KALIBRIERUNG.md). Kein neuer Pflichtchat/-run.
Keine endgültigen Defaultwerte gewählt. 30min/100Activations noch NOT_RUN.

## Git-/Build-/Serveridentität und Schutz der V1

Ausgangscheckout sauber AP010/fdb91f3; alle Remote-Paketbranches und offene PRs
abgeglichen, keine konkurrierende Paketlinie. AP010 nach unabhängigem R02-PASS und
menschlichem R03-Originalprompt tatsächlich über PR14 übernommen.
[Git-/PR-Nachmergebeleg](EVIDENCE/start-provenance.json): Single-Parent-Aggregat
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`, Parent43759d3, Tree
`b12a3f4dc1f2c51d2c4a70680e63c988e729f666`, gleich finalem PR14-Head05da00a.
Aktiver Paketbranch `work/client-v2/ap-iv2-020`, Base `feat/client-v2`.

Die Vollsuite ist an diese Basis plus vollständige Produkt-/Test-/Scriptdateihashes
und Diffhash in [client-full.json](EVIDENCE/client-full.json) gebunden. Spätere
Unterlagennachträge ändern diesen Stand nicht. Finale Gitidentität aus Paketref/PR
auflösen; keine unmögliche Selbst-SHA in der eigenen Commitdatei.

Frozen: AP110-EXE, SHA256 `dccc449d227e7e3580bbdfa333f7386ac6070f007eee29c40971f863375c6f5d`,
Buildcommitcf42a2a; [Produktbaumgleichheit bis b80ed8b](EVIDENCE/build-equivalence.json).
Native [Frozenprobe](EVIDENCE/frozen-runtime.json) verbindet den tatsächlichen Build
an den echten lokalen Server, GUI-/Settings-/Corethread-/Shutdownnachweis; dort
absichtlich ungültiges Capturedevice und kein Paste/LED/Soundplayback.

Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`, lokal127.0.0.1:18020,
[Image-/Konfigurations-/Sourcebeleg](EVIDENCE/local-server-build.json):
Image `sha256:5aaa17e9963fea4c3109027a2ce141b2037b5eadfe7cbd91ff39a9f15626ff20`,
**555 Git-Blobs bytegenau verifiziert**, native Dependencies aus dem separat
identifizierten vorhandenen Free-Image. Docker-UID0 im isolierten Testcontainer,
keine Host-Rechteerhöhung. Eigene Docker-Datenvolume, read-only Modellmount,
synthetischer Admin-Guard. Community-DE64 final/realtime gemeinsam, ONNX-Wake.
Modelldigests unter [model-identities.json](EVIDENCE/model-identities.json).

V1-Profile/Installation, produktiver lokaler Container und produktive Serverzustände
unverändert. VPS vor dem lokalen Zusatzprompt ausschließlich lesend geprüft,
danach keine VPS-Aktionen. Keine Serverpromotion, Releases, Tags oder Übernahme.
Rohsamples/DBs/Runtimezustände außerhalb Git; keine Credentials/privaten Transkripte
in der öffentlichen Akte. Testvault-Einträge gelöscht, Hardwaremute zurückgesetzt,
Testdesktops kontrolliert beendet; isolierter Modellserver bleibt bereit.

## Phase A/B – ausgeführte autonome Qualifikation

Vollständige [Testfähigkeitsanalyse mit fünf Kategorien](EVIDENCE/testability.md).
Windows11Pro26300/Python3.12.10, [Runtime](EVIDENCE/windows-runtime.json),
[Gerätetreiber](EVIDENCE/windows-drivers.json).

| Prüfung | Tatsächliches Ergebnis / Grenze |
| --- | --- |
| Windowsbaseline | 1354 PASS / 173,528s, keine Skips, vor Testcodeänderung |
| Windows-Vollregression | 1360 PASS, keine Skips, alle test_*.py einschließlich sechs neuen Werkzeugregressionen |
| Prozesse | 11 PASS, echte getrennte gepinnte Prozesse mit modellfreier Recordergrenze; keine Real-ASRbehauptung daraus |
| Native Hotkeys | PASS, tatsächliche Win32registrierung/SendInput/Kollision/Rollback |
| Native Settings/Credentials | PASS, echte Qt-UI/Guard/Create/Replace/Delete/Originisolation; modellfreie Servergrenze dieses separaten UI-Checks |
| ReSpeaker capture | 73 echte mono16000/40ms-Pakete in3s; null Drops/Overflows, PCM nicht gespeichert |
| USB/LED/Mute | Firmware2.0.10/GPO-Read und echte LEDcommands, Muteschreiben/Readback/Restore PASS; physische Taste/visuelle Wahrnehmung offen |
| Echtmodelladmission | Manual/Wake/Both PASS, zwei echte ausgewählte ONNX-IDs; Audio explizit unavailable, keine positive Wakequalifikation |
| ASR-Golden | echtes englisches Communitymodell, ein Goldenfall PASS; erwarteter Wortlaut exakt, Referenz kein Nutzeraudio |
| Realer Audiopfad | echte WAV→V2-WS→Mirror→deutsches ASR, ein Final; 0,391s nach Audioende. Sprachmismatch ist ausdrücklich keine deutsche Qualitätsabnahme |
| Wake-Ressourcen/Negativ | echte1/3/25 ONNX-Modelle; RSS und Latenzen gemessen. 51,925s negatives Referenzmaterial: hey_jarvis/alexa null Hits; positive Grenze NOT_PROVEN |
| Desktopcapture | nativer Desktop/Corethread, echtes Mikrofon und kontinuierliche V2-Übertragung PASS; 13 Messpunkte, keine Aktivierung/Einfügung |
| Frozenbootstrap | unveränderte qualifizierte EXE an source-qualified Modellserver PASS; Bedien-/Feedbackwahrnehmung offen |
| Native Clipboardvorbereitung | NOT_RUN: Windows verweigert Vordergrundfokus. Guard sendete nichts, Clipboard unverändert. Testziel/Konflikt/Reinsert-Automation vorbereitet |
| Echter Serverrestart | FAIL, IV2-020-F01; zwei Wiederholungen, anschließend Server wieder ready |
| Legal verkürzter Watchdog | NOT_PROVEN: 30s-Aufnahmehardcut erzeugt neue Segmente vor legalem60s-Watchdog. Realer70s-Replay belegt Finals, keine warning/expiry; keine Sicherheitsgrenze angepasst |
| compileall / Diff-/Aktenprüfung | PASS; kein Produktdiff |

RSS bei1/3/25 Modellen nach Init ca193/227/210MB; P95-Detektionszeit3,38/2,65/4,81ms.
Sequenzielle Läufe im selben Prozess mit Allocator-/GC-Wiederverwendung, keine
lineare Speicherprognose und kein Ersatz für30min-Stabilität. Rohmessungen erreichbar.

## Fehlversuche und Grenzen

Erster Serverarchivaufbau zeigte Windows-EOL-Konvertierung; durch exakten Gitblob-
Export ersetzt und555 Blobs verifiziert. Vorherige Modellvorchecks sind diagnostisch;
maßgeblich sind als exact bezeichnete Wiederholungen und die Produktionsbaumprüfung.
Docker-AppData-Bindmount war leer; eigene Datenvolume und kontrolliertes Configcopy
verwendet. Ungültiger Testlogmodus/AdminKey-im-YAML bei Vorbereitung korrigiert,
Secret ausschließlich in lokalem Envfile. Pro16-Versuch wegen erreichtem Lizenzlimit
beendet; kein Pro16-PASS, produktive Lizenzverbindungen nicht beendet.

Erster erweiterter Windowslauf1359 hatte zwei Pfadfixturefehler durch die von der
Testhilfe injizierte Profilumgebung; Testhilfe korrigiert,29 gezielte Checks PASS,
vollständiger1360-Lauf PASS. Fehlversuch samt vollständigem Log erhalten, keine
Tests geschwächt. Der erste Goldenlauf wurde wegen parallel geänderter Helferidentität
verworfen und stabil sowie nach Exactexport wiederholt. Alle übrigen FAIL/NOT_RUN-
Diagnosen sind im Index eingeordnet; ein grüner Unitlauf verdeckt IV2-020-F01 nicht.

## Requirement-/Fallstatus und Übergabe

[real-cases.json](EVIDENCE/real-cases.json) ist das einzelne reale Ergebnisregister.
REAL-01/02/04/05 NOT_PROVEN, REAL-03 FAIL/IV2-020-F01. REAL-06 bleibt offen, weil
noch keine vollständige fachliche Abgabe vorliegt; Grenzen werden explizit geführt.
M-07 hat den gesicherten fehlerhaften Vorcheck, übrige verpflichtende Inhalte und
alle anderen M-Fälle sind NOT_RUN, Wakegrenze/Kalibrierung NOT_PROVEN.

Keine neuen Produktinterfaces/Migrationen oder Nutzerdefaults. Helferketten behalten
alle Produktionscallbacks und Threadgrenzen, loggen ausschließlich Ereignis-/Ack-
Identität, Zähler, Zustände und Speicher. Sampleaufnahme ist ein expliziter
CLI-Schritt; Vorbereitungen speichern kein allgemeines Mikrofonaudio.

**BLOCKED.** Schreibhoheit R01 bleibt für die Fortsetzung im selben Chat erhalten;
Draft-PR dient Sicherung/Koordination und ist nicht reviewbereit. Nach menschlicher
Freigabe nur den benannten Fix umsetzen, neu bauen/qualifizieren, dann dieselbe
interaktive Kalibrierung fortsetzen. Kein Eigenreview oder Merge.

## Bereitstellung

[Kumulativer Draft-PR #15](https://github.com/marcosudau-vps/voice-stt-client/pull/15), Base feat/client-v2.
Quell-/Test-/Evidenzkandidat d5c621f, nachfolgender PR-Verweisnachtrag rein administrativ.
[Abgabeidentität](EVIDENCE/submission.json). Kein Reviewauftrag/Schreibrechtswechsel.
