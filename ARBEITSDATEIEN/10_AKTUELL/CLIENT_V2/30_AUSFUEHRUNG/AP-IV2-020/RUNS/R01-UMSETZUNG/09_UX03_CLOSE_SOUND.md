# UX03 – fehlender Stoppton beim Schließen einer Aktivierung

Stand 18.10.2026; derselbe AP-IV2-020/R01/Paketbranch/Draft-PR15.

## Ausdrücklicher Zusatzauftrag

„Ich habe jetzt einfach mehrere Male Alexa gesagt in der Zeit. Guck dir einfach
die Logs an, vielleicht erkennst du da was. Mir ist auch, wir waren ja gerade bei
den Feedback-Korrekturen, aufgefallen, dass bei Beenden gar kein Sound kommt.
Also der Sound wird nicht richtig wiedergegeben. Bitte überprüfe und fixe das
auch direkt.“

Dieser Auftrag erlaubt die eng auf den nachgewiesenen fehlenden Beendigungston
begrenzte Produkt-/Testkorrektur im bisherigen R01. Keine weitere Einzelabfrage.
Er erweitert weder Server-/Wireänderungen noch kanonische Übernahmefreigaben.

## Befund und Fehlernachweis

Acht Alexa-Erkennungen am18.10. zwischen00:53:22 und00:59:29 MESZ mit Scores
0,908322 bis0,999994. Jede Aktivierung endet ohne Nutzsprache nach15s mit
`initial_speech_timeout`. Serverseitiges Close ist vorhanden, aber
`EventNormalizer.normalize_domain` bildet `activation.input_closed` bisher nicht
auf Feedback ab. Der Stoppsound ist nur an `segment.recording_ended` gebunden;
ohne Segment wird keine Ausgabeentscheidung erzeugt. Kein Beleg eines defekten
WAV-Assets oder ausgefallenen Windows-Audiobackends aus diesen Ereignissen.

[Baseline](EVIDENCE/ux03-close-sound/feedback-baseline.json),
[roter Reproduktionsnachweis](EVIDENCE/ux03-close-sound/red-close-sound.json),
[gezielte grüne Regression](EVIDENCE/ux03-close-sound/green-close-sound.json),
[positive Wake-Scores](EVIDENCE/ux03-close-sound/alexa-observed-hits.json).
Der rote Lauf sammelte zusätzlich importierte vorhandene Testklassen ein;
der Import wurde anschließend modulqualifiziert, um doppelte Testausführung zu
vermeiden. Der eigentliche Fehler wird auch durch den echten Qt-Ausgabeadapter
bis zum fehlenden STOP-Player reproduziert.

## Begrenzte Korrektur

- Neues internes Mappingereignis `server.input.closed`; kein neues Wireevent.
- Nur serverbestätigtes `finished`/`timed_out` einer zuvor konsistent bekannten
  Vordergrundaktivierung erzeugt den einmaligen Stoppton.
- Aktivierungsterminal davor oder danach ist kein zweiter Soundauslöser.
- Abbruch/Fehler/Watchdog und unbekannte Recoverygründe behalten ihre bestehenden
  Diagnose-/Fehlersounds. Close einer alten Aktivierung, Resync, Snapshot und
  alte Generation erzeugen keinen irreführenden Stoppton.
- Fehlende neue Mappingregel übernimmt ausschließlich den bisherigen Stoppsound
  und dessen Lautstärke. Keine Finalizing-/LED-Zustandsübernahme; explizite neue
  Benutzerregel einschließlich leerer Regel bleibt erhalten.
- Keine lokale Lifecycleautorität, kein Timer, keine Audio-/Triggerfreigabe,
  keine Änderungen an Textinjektion, Protokoll oder serverseitiger Erkennung.

## Qualifikationsgrenze

76 gezielte und1398 Windows-Tests PASS/0 Skips;1964 Servertests PASS/14 erwartete
optionale Skips,11 Prozessfälle,17 Grenzen und7 Socketsmokes am Produkt7bb5646
neu belegt. EXE/Wheel/sdist, Releaseguard/Twine sowie native EXE-/Wheel-
Serverlaufzeiten PASS. Echter no-speech Timeout: genau ein Stop-Playerlauf,
QSoundEffect Ready/playing=true, ca.14ms nach empfangenem Close.
[Gesamtbeleg](EVIDENCE/ux03-close-sound/assessment.json). Technische Korrektur
belegt und [menschlich hörbar bestätigt](EVIDENCE/ux03-close-sound/human-hearing-confirmed.json): UX03 CLOSED. Lautstärke-/Dauerkalibrierung bleibt getrennt. Frühere
Hardwarebelege bleiben historisch; übrige Pflichtfälle werden nicht übertragen.
Ein Wake-Schwellwert0,85 trennt die acht protokollierten positiven Treffer von
den zwei bekannten Fehlalarmen nur in dieser Stichprobe. Er wurde nicht gesetzt;
kein Nachweis von Recall oder allgemeiner Fehlalarmrate.
