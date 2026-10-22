## AP-IV2-020/R01 – Abschlussproben,22.10.2026

[Bericht38](../38_ADMIN_UAC_EXE_UND_MINIMALER_ABSCHLUSS.md): Adminguard positiv und generationgebunden, erhöhtes eigenes UAC-Ziel/APIstatus und drei native Stereomix-EXE-Einfügungen belegt. Erste ReSpeaker-ASR korrekt, automatische Einfügung fehlte; bewusster EXE-Reinsert erfolgreich. Minimaler Ein-Satz-Wakeversuch ohne Hotkeys vorbereitet, Wiederholen/Weiter repariert.80Helfer/Qt PASS; Produkt0f6c85e und1400Windowsbeleg unverändert. Wahrnehmungsabfragen menschlich abgeschlossen. Zehn beendete Profile plus Helfer-TEMP hashgesichert entfernt; nur ungestartete Abschlussprobe bleibt. Technische Restgrenzen NOT_PROVEN, BLOCKED/gleicher R01/PR15.

## Autonome Restqualifikation –21.10.2026

[Bericht37](../37_AUTONOME_RESTQUALIFIKATION_UND_MENSCHLICHE_GRENZEN.md), [abschließender29-Fälle-Lauf](technical-rest-20261021/technical-final-all/result.json), [Windows/Helfer](technical-rest-20261021/technical-final-regression/result.json), [Logstoresperre](technical-rest-20261021/logstore-rest-bounded/result.json), [native Einfügung/Crash](technical-rest-20261021/native-rest-preservation.json), [Frozen-Idle](technical-rest-20261021/frozen-native-confirmed.json), [Validierung](technical-rest-20261021/validation.json), [Manifest](technical-rest-20261021/export-manifest.json), [Aufräumen](technical-rest-20261021/cleanup.json). Die historischen Fehlversuche bleiben separat erhalten.

## BOTH-Abschluss und autonomer Watchdog –20.10.2026

- [Vier Bedienversuche/fallgenaue Bewertung](both-live-20261020/attempts.json), [Quellherkunft](both-live-20261020/source-identity.json), [stabile Info](both-live-20261020/server-info-after.json).
- [Unveränderter Watchdog-Rohdurchlauf mit Hilfstest-FAIL](both-live-20261020/watchdog-raw.json), [korrigierte Auswertung desselben Laufs](both-live-20261020/watchdog-reassessment.json), [Log](both-live-20261020/watchdog.log.gz).
- [Validierung](both-live-20261020/validation.json), [61Helfer](both-live-20261020/helpers.log.gz), [Qt](both-live-20261020/qt.log.gz), [native Voraussetzungen](both-live-20261020/native-prerequisites.json), [Aufräumen](both-live-20261020/cleanup.json), [Manifest](both-live-20261020/export-manifest.json), [Bericht34 und kompakte Restgates](../34_BOTH_ABSCHLUSS_UND_KONSOLIDIERTE_RESTGATES.md).

## Hardware-Mute/Reinsert und aktive Wakepause –20.10.2026

- [Beide menschlichen Versuche](mute-reinsert-20261020/attempts.json), [Herkunft](mute-reinsert-20261020/source-identity.json), [Info](mute-reinsert-20261020/server-info-after.json).
- [Diagnoseresultate](mute-reinsert-20261020/probe-summary.json), [endgültige Wakepausen](mute-reinsert-20261020/pause-confirmed.json), [W02 erster FAIL](mute-reinsert-20261020/overlap-failed.json), [W02 wiederholter FAIL](mute-reinsert-20261020/overlap-repeat.json).
- [Validierung](mute-reinsert-20261020/validation.json), [59Helfer](mute-reinsert-20261020/helpers.log.gz), [Qt](mute-reinsert-20261020/qt.log.gz), [Aufräumen](mute-reinsert-20261020/cleanup.json), [Manifest](mute-reinsert-20261020/export-manifest.json), [Bericht32](../32_MUTE_REINSERT_UND_WAKEPAUSEN.md), [lokaler Issueentwurf33](../33_W02_SERVER_ISSUE_ENTWURF.md).

## Native Refreshpfade –20.10.2026

- [Menschlicher Aufnahme-Refresh](refresh-native-20261020/human-attempt.json), [Quellherkunft](refresh-native-20261020/source-identity.json), [stabile Info](refresh-native-20261020/server-info-after.json), [Ereignisse](refresh-native-20261020/events.jsonl.gz).
- [Zwei endgültige native OS-/ASR-Nachsprechfälle](refresh-native-20261020/native-followup.json), [erster erfolgreicher Lauf](refresh-native-20261020/native-first.json), [Protokoll](refresh-native-20261020/native.log.gz).
- [56Helfer](refresh-native-20261020/helpers.log.gz), [Qt](refresh-native-20261020/qt.log.gz), [Validierung](refresh-native-20261020/validation.json), [Aufräumen](refresh-native-20261020/cleanup.json), [Exportmanifest](refresh-native-20261020/export-manifest.json), [Bericht31](../31_REFRESH_AUFNAHME_UND_NATIVER_NACHSPRECHPFAD.md).

## Controls/Logs und Refresh –20.10.2026

- [Sechs tatsächliche Versuche](controls-live-20261020/attempts.json), [Herkunft](controls-live-20261020/source-identity.json), [stabile Info](controls-live-20261020/server-info-after.json).
- [Autonomer realer Refresh](controls-live-20261020/refresh-confirmed.json), [erste Diagnose erhalten](controls-live-20261020/refresh-first.json), [fehlgeschlagene Vorherregression](controls-live-20261020/progress-before.log.gz).
- [Validierung](controls-live-20261020/validation.json), [52Helfer](controls-live-20261020/helpers.log.gz), [Qt](controls-live-20261020/qt.log.gz), [neue volle Windowsregression](controls-live-20261020/windows-confirmed.log.gz), [erster FAIL erhalten](controls-live-20261020/windows-first.log.gz).
- [Aufräumen](controls-live-20261020/cleanup.json), [Exportmanifest](controls-live-20261020/export-manifest.json), [Bericht30](../30_CONTROLS_LOGANSICHT_UND_REFRESH.md).

## Aktuelle W01-Kontrolle –20.10.2026

- [Sound-aus PASS_SCOPED mit allen Checks](wake-silent-confirmed-20261020/attempt.json), [Source-/Konfigurationsherkunft](wake-silent-confirmed-20261020/source-identity.json), [stabile Info](wake-silent-confirmed-20261020/server-info-after.json).
- [Ereignisse](wake-silent-confirmed-20261020/events.jsonl.gz), [Status](wake-silent-confirmed-20261020/status.json.gz), [Bedienaktionen](wake-silent-confirmed-20261020/operator-events.jsonl.gz).
- [Validierung](wake-silent-confirmed-20261020/validation.json), [Redaktion/Konsistenz](wake-silent-confirmed-20261020/redaction-and-consistency.json), [Aufräumen](wake-silent-confirmed-20261020/cleanup.json), [Exportmanifest](wake-silent-confirmed-20261020/export-manifest.json).
- [Bericht29 und aktuelle Restgates](../29_W01_KONTROLLE_BESTAETIGT_UND_RESTGATES.md). Historische zu kurze Sound-aus-Probe bleibt NOT_PROVEN, nur die neue Wiederholung schließt den Kontrollbedarf.

## Aktuelle reale Wakeproben,20.10.2026

- [2PASS/1NOT_PROVEN mit Zeiten/Checks](wake-live-20261020/attempts.json), [Human-/Sourceherkunft](wake-live-20261020/source-identity.json), [unveränderte Serverinfo](wake-live-20261020/server-info-after.json).
- [48Helfertests](wake-live-20261020/helpers-48.log.gz), [Qt-Stopverzögerung](wake-live-20261020/qt-stop-deferral.log.gz), [1400Windows/0Skips](wake-live-20261020/windows-1400.log.gz), [Validierung](wake-live-20261020/validation.json), [Aufräumen](wake-live-20261020/cleanup.json), [Exportmanifest](wake-live-20261020/export-manifest.json).
- [Bericht28, nur Kontrollprobe wiederholen](../28_WAKE_LIVEAUSWERTUNG_UND_RUHEKONTROLLE.md).

## Serverfix-Rückkehr,20.10.2026

- [Info vorher](server-return-20261020/server-info-before.json), [nachher](server-return-20261020/server-info-after.json), [Git/PR/CI-Provenienz](server-return-20261020/server-provenance.json).
- [13Fallübersicht/18Activations](server-return-20261020/summary.json), [vollständige erlaubte Replayereignisse](server-return-20261020/replay-matrix.json), [echter nativer Hello](server-return-20261020/native-hello.json), [133ReSpeakerpakete](server-return-20261020/native-smoke.json).
- [1400Windows-Tests/0Skips](server-return-20261020/windows-1400.log.gz), [43Helfertests](server-return-20261020/helpers-43.log.gz), [Validierung](server-return-20261020/validation.json), [Aufräumen](server-return-20261020/cleanup.json), [Exportmanifest](server-return-20261020/export-manifest.json).
- [Rückkehrbericht27 und reale Restprüfung](../27_SERVERFIX_RUECKKEHR_UND_REQUALIFIKATION.md).

## Autonome Restprüfung,19.10.2026

- [Native Windows-Credentials](autonomous-rest-20261019/repeat-credentials.json), [reale idle-Pausen/Recovery](autonomous-rest-20261019/repeat-runtime.json), [Ereignisse](autonomous-rest-20261019/repeat-events.json).
- [Quell-/Runtimeidentität](autonomous-rest-20261019/repeat-identity.json), [Serverpin](autonomous-rest-20261019/server-identity-after.json), [Validierung](autonomous-rest-20261019/validation.json).
- [36Helfertests](autonomous-rest-20261019/helpers-36.log.gz), [neue volle1400Windows-Tests/0Skips](autonomous-rest-20261019/windows-1400.log.gz).
- [Aufräumblocker](autonomous-rest-20261019/cleanup.json), [Exportmanifest](autonomous-rest-20261019/export-manifest.json), [konkrete Restliste](../26_AUTONOME_RESTPRUEFUNG_UND_OFFENE_PUNKTE.md).

## Bestätigter Idle-Puls und autonome LED-Isolation,19.10.2026

- [Menschliche Originalbewertung](idle-confirmed-20261019/human-result.json), [PASS_SCOPE/Konfiguration](idle-confirmed-20261019/assessment.json), [gesicherte Testwerte](idle-confirmed-20261019/confirmed-calibration.yaml).
- [LED-only erster FAIL](idle-confirmed-20261019/led-first-smoke.json), [neuer nativer PASS](idle-confirmed-20261019/led-pass-smoke.json), [Zusatzprüfung ohne AudioAvailability-Änderung](idle-confirmed-20261019/led-isolation-assessment.json), [Serveridentität danach](idle-confirmed-20261019/server-identity-after.json).
- [Validierung/33Helfertests](idle-confirmed-20261019/validation.json), [vollständiger Helferlog](idle-confirmed-20261019/helper-tests-33.log.gz), [Aufräumstatus](idle-confirmed-20261019/cleanup.json).

## Direkter Idle-Vergleich statt unbewiesenem Zielübergang,19.10.2026

- [Letzter Lauf und menschliche Bewertung](direct-idle-20261019/assessment.json), [Identität](direct-idle-20261019/identity.json), [erlaubte Wire-/Messspur](direct-idle-20261019/prior-events.jsonl.gz).
- [31Helfertests/Qt-Validierung und Grenzen](direct-idle-20261019/validation.json), [vollständiger Helferlog](direct-idle-20261019/direct-idle-helper-tests.log.gz), [Qt-Selbstcheck](direct-idle-20261019/direct-idle-qt.log.gz).
- [Aufräumrest](direct-idle-20261019/cleanup.json); keine neue physische Kalibrierung behauptet.

## Physischer USB-Folgeversuch und Idle-Kalibrierung,19.10.2026

- [Bewertung mit menschlichen Notizen](usb-feedback-repeat-20261019/assessment.json), [Identität](usb-feedback-repeat-20261019/identity.json), [Server nach dem Lauf](usb-feedback-repeat-20261019/server-identity-after.json).
- [Technische Validierung](usb-feedback-repeat-20261019/validation.json), [1400Windows-Tests](usb-feedback-repeat-20261019/windows-1400.log.gz), [29Helfertests](usb-feedback-repeat-20261019/helper-tests-29.log.gz), [Qt-Selbsttest](usb-feedback-repeat-20261019/qt-selfcheck.log.gz).
- [Kalibrierinventar/Framevergleich](usb-feedback-repeat-20261019/idle-calibration.json), [bewusste menschliche LED-Bewertung](usb-feedback-repeat-20261019/human-feedback-note.md), [neuer Testwert](usb-feedback-repeat-20261019/requested-idle-calibration.yaml).
- [Aufräumrest und automatische Ablehnung](usb-feedback-repeat-20261019/cleanup.json).

## Geführter Lauf und USB-Stillstand R11, 19.10.2026

- [Bewertete11Aufgaben](guided-results-20261019/task-assessment.json), [alle15Versuche samt menschlichen Notizen](guided-results-20261019/attempts.json), [Native Fortschrittsereignisse](guided-results-20261019/operator-events.jsonl).
- [R11-Qualifikation und Buildhashes](usb-stall-20261019/assessment.json), [vollständige1400Windows-Tests](usb-stall-20261019/usb-windows.log.gz), [gezielte rote Regression](usb-stall-20261019/usb-red.log.gz), [48grüne Audio-/Recoverytests](usb-stall-20261019/usb-green.log.gz).
- [Source-ReSpeaker/Server-Stillstand](usb-stall-20261019/source-native-stall.json), [installiertesWheel](usb-stall-20261019/wheel-native-stall.json), [Frozen-GUI-Probe](usb-stall-20261019/usb-exe-probe.json), [nachträgliche Serveridentität](usb-stall-20261019/server-post-human-identity.json).
- [Logbefund](guided-results-20261019/log-observation.json), [physischer Screenshot](guided-results-20261019/Screenshot_test8.png), [verweigerte Bereinigung](usb-stall-20261019/cleanup.json).
- [Auswerteskript](guided-results-20261019/evaluate_human_run.py) erzeugt nur Fakten/Hashes; Scope-Urteile separat. Keine Rohsprache/History-Datenbank committed.

## T03: Ereignisgebundener Livefortschritt der Testoberfläche,19.10.2026

- [Bericht21](../21_TESTOBERFLAECHE_LIVE_FORTSCHRITT.md).
- [Finale27 Helfer/1398Windows/Qt und reale Vorprüfung](guided-progress-20261019/validation.json).
- [Vollständiger Windowslog](guided-progress-20261019/windows-1398.log.gz), [Helfer27](guided-progress-20261019/progress-tests-27.log.gz), [Qt-Polling-Selbsttest](guided-progress-20261019/qt-ui-self-check.json).
- [Alter echter Versuch, Fehlerursache und Replay](guided-progress-20261019/finding-and-replay.json), [alte redigierte Ereignisspur](guided-progress-20261019/prior-attempt-events.jsonl).
- [Zusätzlicher Windows-Sharingfehler und begrenzte Korrektur](guided-progress-20261019/sharing-failure.json).
- [Aufgeräumte Verzeichnisse und ausdrücklich verbleibender Löschblocker](guided-progress-20261019/cleanup.json).

## Genehmigte Ablage, finale technische Prüfung und bisheriges Aufräumen,19.10.2026

- [1398Windows-PASS,16 Helfer/43 Fokus, Identitäten und Diagnose der Fehlversuche](guided-suite-20261019/authorized-validation.json).
- [Vollständiger grüner Windows-Log](guided-suite-20261019/authorized-windows-pass.log.gz), [gezielte43](guided-suite-20261019/fixture-green-43.log.gz), [Helfer16](guided-suite-20261019/authorized-helper-tests.log.gz).
- [Zusätzlicher fehlgeschlagener Startlauf](guided-suite-20261019/authorized-first-windows-fail.log.gz), [roter Pfadfixture-Nachweis](guided-suite-20261019/path-fixture-red.log.gz).
- [Echter Source-/Audio-/Log-Vorcheck](guided-suite-20261019/authorized-preflight-summary.json), [Wire/Metriken](guided-suite-20261019/authorized-preflight-events.jsonl), [Quell-/Runtimeidentität](guided-suite-20261019/authorized-preflight-identity.json).
- [Vier Laufordner nach Export entfernt; menschlicher Lauf anschließend ebenfalls aufzuräumen](guided-suite-20261019/authorized-cleanup-progress.json).

## Geführte Resttests,19.10.2026

- [Bericht20](../20_GEFUEHRTE_RESTTESTS.md).
- [Validierung, finale Helferhashes und ausdrücklich fehlgeschlagene Vollsuite](guided-suite-20261019/validation.json).
- [Vollständiger Windows-Fail-Log](guided-suite-20261019/windows-suite-failed-profile.log.gz), [16 grüne Helfertests](guided-suite-20261019/helper-tests.log.gz).
- [Qt-Selbsttest](guided-suite-20261019/ui-self-check.json), [Vorschau](guided-suite-20261019/preview.png).
- [Vorläufiger realer Audioprecheck](guided-suite-20261019/preliminary-smoke.json), [erlaubte Wire-/Messspur](guided-suite-20261019/preliminary-events.jsonl), [GET-APIs](guided-suite-20261019/preliminary-http.json).

Kein finaler Profil-/Realgate-PASS; Ablagefreigabe und Wiederholung ausstehend.

## W01-Fortsetzungsumfang und tatsächliches V2-Testziel,19.10.2026

- [Bericht19 / unveränderte Pflichtgates und Reihenfolge](../19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
- [Fallbezogene maschinenlesbare Disposition](target-and-deferral-20261019/w01-impact.json).
- [Tatsächliche HTTP-V2-Erreichbarkeit beider Adressen](target-and-deferral-20261019/v2-http-preflight.json), [Pro-V2-Hello ohne Audio](target-and-deferral-20261019/v2-hello-preflight.json).
- [Buildmanifeste, Quellstände, aktuelle Image-/Container-/Wheelbindung und acht Runtime-Quellvergleiche](target-and-deferral-20261019/selected-server-identity.json).
- [Validierung und begrenzte/fehlgeschlagene Diagnoseversuche](target-and-deferral-20261019/validation.json), [lesender Erfassungshelfer](human/capture_selected_server_identity.py).

Frühere V1-404-Diagnose durch menschliche URL-Korrektur überholt; kein aktueller V2-Blocker.

## Autonome Klärung und verbleibende Restpunkte, 19.10.2026

- [Bericht18 mit kompakter Restübersicht](../18_AUTONOME_KLAERUNG_UND_RESTPUNKTE.md).
- [Offline-Metadaten, historische Helfer-/Session-/Profilbindungen und Terminalauswertung](retained-closure-20261019/results.json).
- [Ausführung, vollständige Logs und Hashes](retained-closure-20261019/validation.json).
- [Unveränderte zwölf M-Status im Restnachweis](retained-closure-20261019/real-case-rests.json).
- [Wiederverwendbare rein lesende Prüfung](human/resolve_retained_evidence.py), [fünf gezielte Tests](human/test_retained_evidence.py).

Keine historische Akte wird umetikettiert; neue Ausführung ausschließlich Offline-ONNX-Metadaten.

## Testlücken und Wiederholungen, 19.10.2026

- [Fallbezogener Plan A/B/C und bestehende M-Gates](../17_TESTLUECKEN_UND_WIEDERHOLUNGEN.md).
- [Nachgeprüfte Loghashes, Vergleichsfelder und vollständige Zuordnung der24 Deklarationsakten](server-identity-audit-20261018/followup-disposition.json).
- [Konsistenzprüfung der Liste](server-identity-audit-20261018/followup-list-validation.json): PASS; historische Akten und M-Status unverändert.
- Historisches Auditinventar und fünf Ausschlüsse unverändert. Keine neue Server-/Modellausführung oder Produktqualifikation.

## Verbindliche Ausschlüsse aus dem Servercommit-Audit

[Fünf frühe Docker-Modellläufe nicht qualifikationsgültig](server-identity-audit-20261018/early-image-exclusions.json).
Die entsprechenden `qualificationUseOverride` im [vollständigen Inventar](server-identity-audit-20261018/inventory.json)
gehen den historischen Roh-PASS/FAIL-Angaben vor. Keine Übertragung des späteren
555-Dateien-Abgleichs auf diese älteren Versuche.

## Menschlich angeordnete Serverentfernung und Commit-Audit

[Entfernung](../15_SERVER_ENTFERNT.md),
[exakte Ressourcen/Nachkontrolle](server-removal-20261018/removed-resources.json),
[drei Prüfungen deaktivierter Starter](server-removal-20261018/retired-launcher.json),
[vollständiger Testlog](server-removal-20261018/retired-launcher.txt.gz).
[Commit-Audit/Gültigkeitsregeln](../16_SERVER_COMMIT_AUDIT.md),
[komplettes363-Akten-Inventar/555-Blobabgleich/56 Quellprüfungen](server-identity-audit-20261018/inventory.json),
[wiederverwendbarer Auditor](human/audit_server_commit_evidence.py).
Keine neue Instanz, kein ungebundener Gesamt-PASS. Nicht belegbare serverabhängige
Einzelansprüche bleiben NOT_PROVEN; bei Commitabweichung ungültig.

## Starter-/Serverziel-/Ablageprüfung T02

[Prüfbericht](../14_STARTER_SERVERZIEL_UND_ABLAGE.md),
[Pfadauflösung/Trace/Container/Autorisierung](launcher-context-20261018/assessment.json),
[gezielte echte Helper-/Qt-Fehlerpfade](launcher-context-20261018/probe.json),
[menschlicher Screenshot](launcher-context-20261018/human-starter-error.png),
[wiederverwendbarer Prüfhelfer](human/probe_launcher_settings_context.py).
Desktop-Kontextfehler bestätigt; kein externer Schreib-/Startvorgang in dieser
Diagnose. Korrektur noch offen, Reconnectverdacht nicht nachgewiesen.

## Letzter TV-/Hotkey-/Overlayfall O01

[Auswertung](../13_TV_WAKE_FINISH_UND_HINTERGRUND.md),
[gefilterte Livebelege/Bindings](tv-wake-finish-20261018/live-analysis.json),
[59 bestehende Feedback-/Controltests PASS](tv-wake-finish-20261018/feedback-controls-regression.json),
[vollständiger Log](tv-wake-finish-20261018/feedback-controls-regression.txt.gz).
Kein Cancel im Verlauf; finish bestätigt. Fehlender Terminalstatus bleibt
OPEN_INVESTIGATION, kein behaupteter reiner UI-Defekt oder kompletter PASS.

## Server-Issue7 dokumentiert

[Server-Issue](https://github.com/marcosudau-vps/voice-stt-server/issues/7), [exakter Issueinhalt](wake-retrigger-20261018/server-issue-body.md), [verifizierte Remoteanlage](wake-retrigger-20261018/server-issue.json). Kein Implementierungsauftrag.

## IV2-020-W01 – SERVER_FIX_REQUIRED, 18.10.2026

[Finding/Korrekturweg](../12_WAKE_REAKTIVIERUNG_W01.md),
[Livekorrelation](wake-retrigger-20261018/live-analysis.json),
[echter Modellvergleich](wake-retrigger-20261018/rearm-replay-result.json),
[Aufruf/Identität](wake-retrigger-20261018/rearm-replay.json),
[vollständiger Log](wake-retrigger-20261018/rearm-replay.txt.gz),
[Quellenhashes](wake-retrigger-20261018/inspected-server-sources.json),
[wiederverwendbarer Reprohelfer](human/probe_wake_rearm.py).
Fall FAIL; Serverkorrektur nicht freigegeben/instanziiert. Kein vollständiger PASS.

## LED-Vergleich Weiß / Farbprofiluntersuchung, 18.10.2026

[Bericht](../11_FARBPROFILE_UNTERSUCHUNG.md),
[wiederverwendbarer Helfer](human/led_waiting_variant.py),
[SDK-Frames](led-white-variant/check.json),
[isolierte Anwendung/Profilhash](led-white-variant/applied.json),
[native Bereitschaft](led-white-variant/native-ready.json),
[114 Feedback-/LED-/Triggerprüfungen](led-white-variant/feedback-regression.json),
[vollständiger Testlog](led-white-variant/feedback-regression.txt.gz).
Optische Wirkung/menschliche Akzeptanz noch NOT_PROVEN; Produkt unverändert.

## Stoppton-Dauer und -Lautstärke bestätigt, LED-Details offen

[Originalantwort und angenommene bestehende Werte](ux03-close-sound/human-feedback-calibration.json): „Beides passt“. Keine Produkt-/Konfigurationsänderung. LED-Änderung gewünscht, genaue Phase/Wirkung noch offen; keine vollständige Feedbackabnahme.

## UX03: Beendigungston korrigiert und native Ausgabe belegt, 18.10.2026

[Freigabe/Befund](../09_UX03_CLOSE_SOUND.md),
[vollstaendige Sound-/LED-/Triggeruebersicht](../10_FEEDBACK_UEBERSICHT.md),
[acht echte protokollierte Alexa-Treffer](ux03-close-sound/alexa-observed-hits.json),
[Repro rot](ux03-close-sound/red-close-sound.json),
[gezielte76 PASS](ux03-close-sound/green-close-sound.json),
[native QSoundEffect-Probe](ux03-close-sound/native-probe.json),
[Stand und Grenzen](ux03-close-sound/assessment.json).
Produkt7bb5646 technisch neu qualifiziert: Windows1398/0 Skips, Server1964/14
erwartete Skips,11 Prozessfaelle,17 Grenzen und7/7 Socketsmokes PASS.
[Paarlauf](ux03-close-sound/pair/validation.json),
[neue Builds](ux03-close-sound/build/artifacts.json),
[native EXE](ux03-close-sound/frozen-native-runtime.json),
[nativ installiertes Wheel](ux03-close-sound/wheel-native-runtime.json),
[wirksames Mapping/SDK-/WAV-Inventar](ux03-close-sound/feedback-inventory.json). Ein realer no-speech
Timeout erzeugt genau einen nativen Stop-Playerlauf. [Menschliche Hörbestätigung](ux03-close-sound/human-hearing-confirmed.json) am realen Alexa-Durchlauf: UX03 CLOSED. Kein voller Realgates-PASS und kein REVIEW_READY.

## Klickbarer Teststarter und Alexa-Fehlalarme, 18.10.2026

[Dauerhafter Startknopf/Anleitung](human/STARTER_README.md), [Code](human/test_instance_launcher.py),
[Helferregression](clickable-starter-20261018/launcher-checks.json),
[neue volle Windows1390-Regression](clickable-starter-20261018/client-full.json),
[Managerbootstrap erneut PASS](clickable-starter-20261018/managed-bootstrap-retry.json),
[native Starteranzeige und Helferhashes](clickable-starter-20261018/summary.json).
Native Starteroberfläche geöffnet; bestehende freie Instanz bleibt unverändert.
[Zwei getrennte Alexa-Fehlaktivierungen](wake-false-activation-20261017/assessment.json)
vom17.10. um21:20:02/21:20:17 MESZ, Scores0,767410/0,646442, jeweils15s
initial_speech_timeout und null Sprachsegmente. Kein Audio-Rohbeleg; Rückkopplung
oder sonstiger akustischer Auslöser nicht bewiesen. Positive Vergleichsversuche offen.

## Freie Feedbackprobe und Einstellungstabs

[Freie Instanz](human/free-exploration-20261016-01.json), [menschliche Kalibrierungsrückmeldung](human/feedback-calibration-20261016-01.json), [Qt-Settingsnavigation](settings-navigation/summary.json). Kein genannter Tab entfernt; zweiter lokaler Dialog über Knopf. Testharness-Logmanagerlücke T01 festgestellt und Korrektur vorbereitet, native Log-UI-Bestätigung noch offen. Keine vollständige M-/Feedbackabnahme behauptet.

### Vorheriger Zwischenstand

## Neuer Live-Sprachpfad am korrigierten Produkt bestanden

[Manual-F8/F9-/ASR-/Native-Ausgabe](ux02/manual-voice-20261016-01/assessment.json), [menschlich bestätigt](../ZUSATZPROMPTS/014_MANUAL_SPRACHPFAD_BESTAETIGUNG.md). Ein Final und genau ein unveränderter nativer Zieltext samt Leerzeichen; erkannter Bindestrich statt geplanter Zusammenschreibung explizit dokumentiert. Vollständige M-Fälle/Kalibrierung weiterhin offen.

### Vorheriger Zwischenstand

## UX02 physisch bestätigt und geschlossen

[250ms tatsächlicher Halte-/Freigabenachweis und exakte native Ausgabe](ux02/native-physical-20261016-01/assessment.json), [menschliche Chatbestätigung](../ZUSATZPROMPTS/013_UX02_NATIVE_BESTAETIGUNG.md), [saubere Quieszenz-/Hotkeybereinigung](ux02/native-physical-20261016-01/finalization.json). Äußerer Helferprozess bewusst nach Chatabschluss statt GUIklick beendet; dessen Nichtnull-Exit bleibt separat dokumentiert. [Gesamtbeleg aktualisiert](ux02/qualification-summary.json). Übrige M-Gates/Kalibrierung weiterhin offen.

### Vorheriger technischer Zwischenstand

## Aktueller Produktstand d95043e: technische Requalifikation PASS

[UX02-Gesamtbeleg](ux02/qualification-summary.json), [vollständiger Index](ux02/INDEX.md), [Buildidentitäten/Hashes](ux02/build/artifacts.json), [reale neue Modellreplays](ux02/real-model-replay-summary.json). Windows1390/Server1964+14 erwartete Skips, elf Prozessfälle/17 Grenztests/sieben Smokes, reale Recovery-/Desktop-/Win32-/Credential- und Buildprüfungen grün. UX02 benötigt noch physischen Halte-/Freigabenachweis; vollständige M01..M12/30min100/Kalibrierung offen. Keine Übertragung älterer vollständiger Hardwarequalifikation.

### Frühere Zwischenstände und Beleggruppen

## Aktuell: dauerhafter Testclient fertig, UX02 offen

[Testclient](../../../../../../../../tests/manual/v2/README.md), [zehn Helferprüfungen/Qt/Windows1378 PASS](ux01/manual-tool-permanent/summary.json). Feste Schritte, wandernder Fokus, Vorbereitung8s und Timer rechts. [Manualprobe](ux01/repeatable-manual-20261016-01/assessment.json): F8/F9 PASS, Zieleinfügung FAIL durch gehaltenes Shift. [Nicht angewandter Scopevorschlag](../08_SCOPE_VORSCHLAG_UX02_MODIFIERTASTEN.md). BLOCKED bezüglich vollständiger Qualifikation; kein geänderter Produktcode.

## Neue Bedienhilfen für die gemeinsame Durchführung

[Wiederholen/Abbrechen und grünes persistentes Satzfeld geprüft](ux01/repeat-controls/summary.json). [Voriger manueller Teilversuch NOT_PROVEN](ux01/manual-hotkey-20261016-01/assessment.json), null Activations/Finals, Secondary nur idle; kein nachgewiesener Produktfehler. Neuer Einzelversuch bleibt bis tatsächlicher Bedienung und Auswertung offen.

## Aktuell: bestätigte Wake-Einzelsätze und nächster Hotkeyteil

[Zwei bewusst separat gestartete Liveversuche](ux01/stepped-20261016-01/assessment.json): vollständige Nutzsätze, zwei native Einfügungen,71Zeichen mit Leerzeichen und tatsächlicher menschlicher Bestätigung PASS am unveränderten qualifizierten Produkt17261e6. F9-Finish weiterhin NOT_PROVEN; beide Eingaben per Timeout. [Vorbereitete Hotkeydiagnose und Helferprüfungen](ux01/hotkey-task-precheck/summary.json). UX01 bereits geschlossen. [Aktuelle Checkliste](../07_TESTCHECKLISTE.md), vollständige M-Gates weiterhin offen.

[Fortlaufende gemeinsame Checkliste](../07_TESTCHECKLISTE.md): jetziger Block native Leerzeichenprobe plus zwei direkte Wake-Sätze. Die vollständigen M-Fälle bleiben offen; Häkchen erst nach tatsächlichen Nachweisen. [Helfer-I/O-Regression](ux01/editor-diagnostic-reader-regression.json) und [realer Diagnose-Lesetest](ux01/editor-diagnostic-live-validation.json) sichern die Wiederholung.

## Neue Produktausnahme UX01 – laufende Requalifikation

[UX01-Evidenzindex](ux01/INDEX.md), Produkt17261e65afeda3f2c7412d5bfe6006b76863acdb. Neue Windows1378 ohne Skips, neue EXE/Wheel/sdist, native Desktop-/ReSpeaker-Recovery, reale HTTP-/Ack-/Restartfälle und natives Settings/Hotkey grün. Realer separater SQLite-ENOSPC-Fall ohne STT-Lock grün. Vollständiger neuer Paarlauf PASS: Windows1378/0skips, Server1964/14 erwartete optionale Skips,11 Prozessfälle,17 Grenztests,7/7 Smokes. Native Ausgabe mit Leerzeichen benötigt noch den gebündelten menschlichen Fokus-Klick. Direkte Wakephrase-Nutzsätze im Modellreplay exakt; Alexa-Pausenaufnahme weicht vom geplanten Text ab, im manuellen Vergleich jedoch derselbe Nutztext. Kein vollständiges Realgate-PASS.

# AP-IV2-020 R01 – Fortsetzung / IN_PROGRESS

[Scope-Freigabe](../ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md),
[systematischer Audit und Findingzuordnung](../05_RECONNECT_AUDIT.md).
Neue Recoverybelege unter `recovery-audit/`, jeweils JSON mit Runtime/Befehl/
Vorher-Nachherquellhashes und vollständigem .txt.gz-Log. Rote Repros und gescheiterte
Hilfsmittelversuche bleiben erkennbar. Vorfixbelege unten sind historisch.
Kein REVIEW_READY, kein ROOT_PASS, keine vollständige menschliche Realabnahme.

Gemeinsame Phase läuft: [echte Manualbaseline](human/manual-followup-3000.json),
[gewünschte5000ms-Variante](human/manual-followup-5000-configuration.json).
[5000ms-Vergleich](human/manual-followup-5000.json) menschlich passend;
[reproduzierbare Profile](human/calibrated-profiles.json). M-01 bleibt wegen
offenem Overlap NOT_PROVEN. [Hostspeichergrenze](human/host-memory-constraint.json)
vor Wakeblock und [passiver Eventbeobachter](human/observed_session.py) mit
Identitäts-/Scoreallowlist; keine Tokens.
[Gemeinsame Phase mit ausdrücklich freigegebenen sechs Sprach-Testfixtures](human/INDEX.md):
Herkunft/Hashes, wiederverwendbare Skripte und tatsächliche Modell-/ASR-Messwerte.

## Maßgebliche neue Belege

- [Qualifikationsübersicht und Quellbindung](recovery-audit/qualification-summary.json), [zehn technische Findings](recovery-audit/findings.json).
- [Finale Windowsvollsuite](recovery-audit/client-full-final-environment.json), [vollständiger Log](recovery-audit/client-full-final-environment.txt.gz):1373 PASS/0 Skips.
- [Paarqualifikation](recovery-audit/pair/validation.json), alle komprimierten Voll- und Szenariologs im selben Ordner; Server1964 PASS/14 einzeln ausgewiesene Skips.
- [Reale Recovery/HTTP/Ack/Neustarts/Shutdown](recovery-audit/real-recovery.json), [vollständiger Log](recovery-audit/real-recovery-final.txt.gz), [redigierte Spur](recovery-audit/real-recovery-trace.json).
- [ReSpeaker-Desktoprestart](recovery-audit/native/desktop-smoke.json), [Identität](recovery-audit/native/desktop-identity.json), [Spur](recovery-audit/native/desktop-trace.jsonl).
- [Reale neue ASR-Pipeline](recovery-audit/native/real-audio-pipeline.json), [Golden-EN](recovery-audit/native/real-golden.txt.gz), [echte Modelladmission](recovery-audit/native/real-admission.json).
- [Neue Artefaktidentitäten](recovery-audit/build/artifacts.json), [Build](recovery-audit/build/pyinstaller-serialized.json), [Paketprüfung](recovery-audit/build/release-guard.json), [native Frozen-GUI](recovery-audit/build/frozen-native-runtime.json).
- [Echter Watchdog bei PCM-Stall](recovery-audit/real-watchdog-stalled-media.json), [Helfer](recovery-audit/watchdog_stalled_media.py): zulässige Fristen, echte Uhr/ASR, kein menschlicher Dauersprachbeleg.
- [Native Hotkeys](recovery-audit/native/windows-hotkeys.txt.gz), [native Settings/Credential Manager](recovery-audit/native/windows-settings.txt.gz).
- [Neue Parameter](recovery-audit/native/parameter-inventory.json), [Serverinventar](recovery-audit/native/real-server-inventory.json).

## Historischer Evidenzindex vor Produktkorrektur

# AP-IV2-020 R01 – Evidenz / BLOCKED

Basis b80ed8b81ad92bd02ac32553883443d2b7673bcd, Tree
b12a3f4dc1f2c51d2c4a70680e63c988e729f666, Server ada13b0.
Tester Codex auf Windows; noch keine menschliche Sprach-/Wahrnehmungsdurchführung.
Kein REVIEW_READY oder ROOT_PASS.

## Maßgebliche Belege

- [Vorgänger-/Gitprovenienz](start-provenance.json).
- [Testfähigkeit, fünf Kategorien](testability.md), [Windowsruntime](windows-runtime.json), [Treiber](windows-drivers.json).
- [Clientbaseline](baseline-client.json) und [vollständiger Log](baseline-client.txt.gz):1354 PASS.
- [Clientvollsuite](client-full.json) und [vollständiger Log](client-full.txt.gz):1360 PASS,176,893s,keine Skips.
- [Native Aufnahme/USB/Vault/EXE](native-preflight.json), [LED/Muteschreiben/Restore](native-led-mute.json).
- [555 exakte Serverblobs/Image/Config](local-server-build.json), [Modelldigests](model-identities.json).
- [Echtmodelladmission Manual/Wake/Both](real-admission.json), [Audio/ASRpipeline](real-audio-pipeline.json).
- [Frozenruntime](frozen-runtime.json), [Produktbaumgleichheit](build-equivalence.json).
- [Instrumentierter Desktop](desktop-identity.json), [rohe redigierte Metrikspur](desktop-trace.jsonl), [Smokeresultat](desktop-smoke.json).
- [Parameter-/LEFX-/Soundinventar](parameter-inventory.json), [Registry/effective/Modelhealth](real-server-inventory.json).
- [Alle realen M-Fälle und tatsächliche Grenzen](real-cases.json).
- **IV2-020-F01**: [zweiter realer Restarttrace](restart-repro-trace.jsonl), [Identität](restart-repro-identity.json), [FAIL](restart-repro-smoke.json),
  [Reprotests](repro_transient_preflight.py), [kompletter Reprolog](repro-transient-preflight.txt.gz),
  [noch nicht angewandter Fixpatch](proposed-client-recovery-fix.patch).
- [Clipboardvorcheck](native-paste.json):NOT_RUN mangels Vordergrundfokus, keine Eingabe/Clipboardänderung.
- [Realer Watchdogversuch](real-watchdog.json):NOT_PROVEN; Aufnahmehardcut30s verhindert60s-Expiry. Kein Produktdefekt daraus abgeleitet.
- [RSS-Messinstrumentierung](measure_wake_resources.py):/proc/self/statm statt fehlendem optionalen psutil; echte Modelle unverändert.
- [Watchdog-Replayharness](watchdog_real_audio.py):echte energieausgewählte Referenzaudiochunks, echte Uhr/ASR, keine menschliche Neusprache.

## Befehle und vollständige Logs

Jede nachfolgende Befehlsakte enthält exakte argv/cwd, Exitcode, Dauer, Windows-/Python-
Runtime, vor/nach Quellidentität, vollständigen komprimierten Log sowie dessen Raw-/Gzip-
SHA256. Loggzip mit Standardgzip lesbar; keine gekürzten Erfolgszitate als Ersatz.
Produktdateien unverändert; spätere Änderungen ausschließlich administrativ.

| Lauf | Wrapperresultat / Exit | Befehlsakte | Vollständiger Log |
| --- | --- | --- | --- |
| baseline-client | PASS baseline / 0 | [baseline-client.json](baseline-client.json) | [baseline-client.txt.gz](baseline-client.txt.gz) |
| client-full | PASS / 0 | [client-full.json](client-full.json) | [client-full.txt.gz](client-full.txt.gz) |
| compileall | PASS / 0 | [compileall.json](compileall.json) | [compileall.txt.gz](compileall.txt.gz) |
| cross-process | PASS / 0 | [cross-process.json](cross-process.json) | [cross-process.txt.gz](cross-process.txt.gz) |
| frozen-probe-exact | PASS / 0 | [frozen-probe-exact.json](frozen-probe-exact.json) | [frozen-probe-exact.txt.gz](frozen-probe-exact.txt.gz) |
| frozen-real-server-probe | PASS / 0 | [frozen-real-server-probe.json](frozen-real-server-probe.json) | [frozen-real-server-probe.txt.gz](frozen-real-server-probe.txt.gz) |
| native-hotkeys | PASS / 0 | [native-hotkeys.json](native-hotkeys.json) | [native-hotkeys.txt.gz](native-hotkeys.txt.gz) |
| native-paste-attempt | FAIL / 1 | [native-paste-attempt.json](native-paste-attempt.json) | [native-paste-attempt.txt.gz](native-paste-attempt.txt.gz) |
| native-settings-ui | PASS / 0 | [native-settings-ui.json](native-settings-ui.json) | [native-settings-ui.txt.gz](native-settings-ui.txt.gz) |
| real-golden-asr-stable | PASS / 0 | [real-golden-asr-stable.json](real-golden-asr-stable.json) | [real-golden-asr-stable.txt.gz](real-golden-asr-stable.txt.gz) |
| real-golden-asr | FAIL / 0 | [real-golden-asr.json](real-golden-asr.json) | [real-golden-asr.txt.gz](real-golden-asr.txt.gz) |
| real-golden-exact | PASS / 0 | [real-golden-exact.json](real-golden-exact.json) | [real-golden-exact.txt.gz](real-golden-exact.txt.gz) |
| real-wake-artifacts | PASS / 0 | [real-wake-artifacts.json](real-wake-artifacts.json) | [real-wake-artifacts.txt.gz](real-wake-artifacts.txt.gz) |
| real-wake-negative | PASS / 0 | [real-wake-negative.json](real-wake-negative.json) | [real-wake-negative.txt.gz](real-wake-negative.txt.gz) |
| real-wake-resources | PASS / 0 | [real-wake-resources.json](real-wake-resources.json) | [real-wake-resources.txt.gz](real-wake-resources.txt.gz) |
| real-watchdog-run | FAIL / 0 | [real-watchdog-run.json](real-watchdog-run.json) | [real-watchdog-run.txt.gz](real-watchdog-run.txt.gz) |
| repro-transient-preflight | FAIL / 1 | [repro-transient-preflight.json](repro-transient-preflight.json) | [repro-transient-preflight.txt.gz](repro-transient-preflight.txt.gz) |
| superseded-client-full | FAIL / 1 | [superseded-client-full.json](superseded-client-full.json) | [superseded-client-full.txt.gz](superseded-client-full.txt.gz) |
| wake-negative-exact | PASS / 0 | [wake-negative-exact.json](wake-negative-exact.json) | [wake-negative-exact.txt.gz](wake-negative-exact.txt.gz) |
| wake-resources-exact-rss | PASS / 0 | [wake-resources-exact-rss.json](wake-resources-exact-rss.json) | [wake-resources-exact-rss.txt.gz](wake-resources-exact-rss.txt.gz) |

Native-paste-attempt hat Wrapperexit1, das tatsächliche Fallresultat ist NOT_RUN wegen
Fokus, kein gesendetes Zeichen. Repro-transient-preflight enthält zwei absichtlich
rote gewünschte Recoveryregressionen und einen grünen permanenten Fehlerkontrollfall.
Diese Fehler sind offen und werden durch die grüne bestehende Vollsuite nicht verdeckt.
Real-watchdog-run hat zusätzlich eine während des Laufs geänderte Helferidentität;
seine tatsächlichen Events zeigen30s-Hardcuts und werden ausschließlich diagnostisch
verwendet. Watchdogprüfung bleibt NOT_PROVEN, kein Warnungs-/Expiry-PASS.

Superseded-client-full:1359/2 Pfadfixturefehler durch injiziertes Profilroot; Helfer
korrigiert, [29 gezielte Checks](harness-env-recheck.txt.gz), vollständiger1360-Lauf
PASS. Erster Goldenlauf wegen Helferidentitätswechsel verworfen; stable und exact
wiederholt. Vor-exact `real-wake-*` und `frozen-real-server-probe` sind Vorchecks;
maßgeblich exact-Runs und separates frozen-runtime.json. Keine davon belegt eine
menschliche positive Wakegrenze oder deutsches ASR-Qualitätsurteil.

Die Prozessharnessbelege `test_*.json` gehören zum11er-Prozesslauf. Produktionscode/
HTTP/WS/Logs sind echt; Recorder/ASR/Audioausgabe dort explizit modellfreie Testgrenzen.
Sie ersetzen keine Realfälle. `accessToken` ist redigiert, Testtexte sind synthetisch.

## Weitere Belege in dieser Akte

- [baseline-client.json](baseline-client.json)
- [baseline-client.txt.gz](baseline-client.txt.gz)
- [build-equivalence.json](build-equivalence.json)
- [client-full.json](client-full.json)
- [client-full.txt.gz](client-full.txt.gz)
- [compileall.json](compileall.json)
- [compileall.txt.gz](compileall.txt.gz)
- [cross-process.json](cross-process.json)
- [cross-process.txt.gz](cross-process.txt.gz)
- [desktop-autosmoke.txt.gz](desktop-autosmoke.txt.gz)
- [desktop-identity.json](desktop-identity.json)
- [desktop-restart-repro.txt.gz](desktop-restart-repro.txt.gz)
- [desktop-restart.txt.gz](desktop-restart.txt.gz)
- [desktop-smoke.json](desktop-smoke.json)
- [desktop-trace.jsonl](desktop-trace.jsonl)
- [frozen-probe-exact.json](frozen-probe-exact.json)
- [frozen-probe-exact.txt.gz](frozen-probe-exact.txt.gz)
- [frozen-real-server-probe.json](frozen-real-server-probe.json)
- [frozen-real-server-probe.txt.gz](frozen-real-server-probe.txt.gz)
- [frozen-runtime.json](frozen-runtime.json)
- [harness-env-recheck.txt.gz](harness-env-recheck.txt.gz)
- [local-server-build.json](local-server-build.json)
- [measure_wake_resources.py](measure_wake_resources.py)
- [model-identities.json](model-identities.json)
- [native-hotkeys.json](native-hotkeys.json)
- [native-hotkeys.txt.gz](native-hotkeys.txt.gz)
- [native-led-mute.json](native-led-mute.json)
- [native-paste-attempt.json](native-paste-attempt.json)
- [native-paste-attempt.txt.gz](native-paste-attempt.txt.gz)
- [native-paste.json](native-paste.json)
- [native-preflight.json](native-preflight.json)
- [native-settings-ui.json](native-settings-ui.json)
- [native-settings-ui.txt.gz](native-settings-ui.txt.gz)
- [parameter-inventory.json](parameter-inventory.json)
- [proposed-client-recovery-fix.patch](proposed-client-recovery-fix.patch)
- [real-admission.json](real-admission.json)
- [real-audio-pipeline.json](real-audio-pipeline.json)
- [real-cases.json](real-cases.json)
- [real-golden-asr-stable.json](real-golden-asr-stable.json)
- [real-golden-asr-stable.txt.gz](real-golden-asr-stable.txt.gz)
- [real-golden-asr.json](real-golden-asr.json)
- [real-golden-asr.txt.gz](real-golden-asr.txt.gz)
- [real-golden-exact.json](real-golden-exact.json)
- [real-golden-exact.txt.gz](real-golden-exact.txt.gz)
- [real-server-inventory.json](real-server-inventory.json)
- [real-wake-artifacts.json](real-wake-artifacts.json)
- [real-wake-artifacts.txt.gz](real-wake-artifacts.txt.gz)
- [real-wake-negative.json](real-wake-negative.json)
- [real-wake-negative.txt.gz](real-wake-negative.txt.gz)
- [real-wake-resources.json](real-wake-resources.json)
- [real-wake-resources.txt.gz](real-wake-resources.txt.gz)
- [real-watchdog-run.json](real-watchdog-run.json)
- [real-watchdog-run.txt.gz](real-watchdog-run.txt.gz)
- [real-watchdog.json](real-watchdog.json)
- [repro-transient-preflight.json](repro-transient-preflight.json)
- [repro-transient-preflight.txt.gz](repro-transient-preflight.txt.gz)
- [repro_transient_preflight.py](repro_transient_preflight.py)
- [restart-repro-identity.json](restart-repro-identity.json)
- [restart-repro-smoke.json](restart-repro-smoke.json)
- [restart-repro-trace.jsonl](restart-repro-trace.jsonl)
- [start-provenance.json](start-provenance.json)
- [superseded-client-full.json](superseded-client-full.json)
- [superseded-client-full.txt.gz](superseded-client-full.txt.gz)
- [test_autonomous_terminal_recovery_and_stale_callback.json](test_autonomous_terminal_recovery_and_stale_callback.json)
- [test_client_dropped_final_is_incomplete_without_log_paste.json](test_client_dropped_final_is_incomplete_without_log_paste.json)
- [test_client_injected_gap_salvages_buffered_final.json](test_client_injected_gap_salvages_buffered_final.json)
- [test_device_loss_drain_and_led_isolation.json](test_device_loss_drain_and_led_isolation.json)
- [test_lost_finish_ack_retries_identical_without_second_effect.json](test_lost_finish_ack_retries_identical_without_second_effect.json)
- [test_negative_admission.json](test_negative_admission.json)
- [test_segments_overlap_interim_and_log_dedup.json](test_segments_overlap_interim_and_log_dedup.json)
- [test_settings_atomicity_and_admin.json](test_settings_atomicity_and_admin.json)
- [test_wake_only_and_shared_admission_race.json](test_wake_only_and_shared_admission_race.json)
- [test_wake_sources_settings_and_bootstrap.json](test_wake_sources_settings_and_bootstrap.json)
- [testability.md](testability.md)
- [wake-negative-exact.json](wake-negative-exact.json)
- [wake-negative-exact.txt.gz](wake-negative-exact.txt.gz)
- [wake-resources-exact-rss.json](wake-resources-exact-rss.json)
- [wake-resources-exact-rss.txt.gz](wake-resources-exact-rss.txt.gz)
- [watchdog_real_audio.py](watchdog_real_audio.py)
- [windows-drivers.json](windows-drivers.json)
- [windows-runtime.json](windows-runtime.json)

- [Finale Quell-/Test-/Stagingkonsistenz](source-consistency.json)
- [Redaktionsprüfung](redaction-check.json)
- [Diffprüfung](diff-check.json), [kompletter Log](diff-check.txt.gz)
- [Aktenprüfung](work-records.json), [kompletter Log](work-records.txt.gz)

- [Draft-Abgabeidentität und nächste Aktion](submission.json)


## Dauerlauf, strengere Wakeanforderungen und Aufräumen –21.10.2026

- [Bericht35](../35_DAUERLAUF_WAKEANFORDERUNGEN_UND_AUFRAEUMEN.md), [Validierung](endurance-wake-20261020/validation.json).
- [100Activations/1800s](endurance-wake-20261020/confirmed-result.json), [Auswertung](endurance-wake-20261020/confirmed-assessment.json), [Messwerte](endurance-wake-20261020/confirmed-summary.json), [Historybindung](endurance-wake-20261020/history-accounting.json).
- [Erster Roh-FAIL](endurance-wake-20261020/first-attempt-raw.json), [Hilfstestfehleranalyse](endurance-wake-20261020/first-attempt-reassessment.json), [zweiter Roh-FAIL/ASRtimeout](endurance-wake-20261020/second-attempt-raw.json).
- [Wakevergleich](endurance-wake-20261020/wake-comparison-summary.json), [NONE](endurance-wake-20261020/none-controls.json), [native Kollision](endurance-wake-20261020/native-collision.json).
- [Neue1400Windows/0Skips](endurance-wake-20261020/windows.json), [Vollausgabe](endurance-wake-20261020/windows.log.gz), [70Helfer](endurance-wake-20261020/helpers.log.gz), [Qt](endurance-wake-20261020/qt.log.gz).
- [Alle Löschbelege](endurance-wake-20261020/cleanup-receipts.json), [leerer Namensraum](endurance-wake-20261020/cleanup-final.json), [Archivbindung](endurance-wake-20261020/private-archive-binding.json), [Manifest](endurance-wake-20261020/export-manifest.json). Rohereignisse/Messpunkte/Logs und ausgeführte Quellversionen komprimiert im selben Ordner; keine neuen Rohtranskripte oder privaten Datenbanken in Git.


## Menschlicher W02-Abschluss und konkrete Freigabereste,21.10.2026

[Bericht36](../36_W02_ABSCHLUSS_UND_FREIGABERESTE.md), [Entscheidung](../ZUSATZPROMPTS/034_W02_SCHLIESSEN_UND_FREIGABERESTE.md). W02 geschlossen durch menschliche Disposition, keine neue Testausführung und keine nachgewiesene Ursachenbehebung. Bestehende Roh-FAILs und spätere PASS_SCOPED-Belege unverändert. Keine identischen Bedienwiederholungen aus pauschalen Matrixstatus ableiten.
