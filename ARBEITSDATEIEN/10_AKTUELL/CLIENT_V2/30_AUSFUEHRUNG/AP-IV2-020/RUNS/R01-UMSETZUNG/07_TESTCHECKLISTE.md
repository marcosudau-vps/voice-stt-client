# AP-IV2-020 – unsere Testcheckliste

**Stand: 16.10.2026 · Technische Qualifikation grün · Gemeinsame Realtests offen**

Ich pflege die Häkchen nach den tatsächlichen Nachweisen. „Teilweise geprüft“
bedeutet noch keinen vollständig bestandenen Pflichtfall. Derselbe R01 und
[Draft-PR15](https://github.com/marcosudau-vps/voice-stt-client/pull/15) bleiben aktiv.

## Gerade bestätigt: beide Wake-Sätze

- [x] Aufgabe 1 und Aufgabe 2 vorher gelesen und jeweils selbst gestartet.
- [x] „Hey Jarvis“ + roter Ball vollständig, ohne Rufwort im Editor.
- [x] „Alexa“ + gelbe Tasche vollständig, ohne Rufwort im Editor.
- [x] Beide Nutzsätze mit Leerzeichen getrennt; zwei echte native Einfügungen.
- [x] Menschliche Bestätigung: **„Beide vollständig, mit Leerzeichen“**.
- [x] Effektiv **5000ms Nachsprechfenster / 320ms Pre-Roll** in beiden Sitzungen bestätigt.
- [ ] F9 als tatsächlichen Finish-Befehl nachweisen: beide bisherigen Eingaben endeten per Timeout.
- [ ] Endgültiges Gefühl zu Pre-Roll und dem übrigen Feedback gemeinsam bewerten.

[Auswertung mit Quellbindung, Messwerten und Diagnosen](EVIDENCE/ux01/stepped-20261016-01/assessment.json).
Die zwei getrennten Sitzungen sind ein erfolgreicher Teilnachweis, noch kein vollständiger M-02.

## Jetzt: eine kurze manuelle Hotkeyprobe

- [ ] Vorschau und Satz **vorher in Ruhe lesen**.
- [ ] Eigenen Startknopf klicken; auf **CLIENT BEREIT** warten.
- [ ] **Strg+Umschalt+F8**, bei **F8 ANGEKOMMEN** den angezeigten Satz sprechen.
- [ ] **Direkt am Satzende Strg+Umschalt+F9** drücken.
- [ ] Auf **FERTIG** warten; der Agent prüft Tastenempfang, Ack, Lebenszyklus und Einfügung.

Jede weitere Aufgabe benötigt erneut deinen eigenen Start. Kein automatischer Folgetest.
Die native Leerzeichenprobe und die beiden erfolgreichen Wake-Sätze werden dafür nicht wiederholt.

## Bereits erledigt

- [x] Git-Baseline, tatsächlich übernommener Vorgänger und Paketbranch geprüft.
- [x] Isolierter **lokaler** Server mit gepinntem Stand und echten Modellen bereit.
- [x] Zehn nachgewiesene Reconnect-/Recoveryfehler behoben und regressionsgesichert.
- [x] UX01 vollständig technisch nachgewiesen, einschließlich echter nativer Ausgabe mit Leerzeichen.
- [x] 100 gezielte Tests, einschließlich fünf neuer Ausgabe-/History-Regressionen, grün.
- [x] Neuer Produktstand17261e6: **1378 Windows-Tests**, keine Skips, grün.
- [x] Paarlauf:1964 Server-Tests/14 begründete optionale Skips,11 Prozessfälle,
  17 Grenztests und sieben Server-Smokes grün.
- [x] Neue EXE/Wheel/sdist gebaut; Buildidentitäten und Runtime geprüft.
- [x] Native ReSpeaker-/Desktop-Recovery, Hotkey- und Credential-Vorprüfungen grün.
- [x] Echter separater SQLite-Schreibausfall getestet: STT läuft weiter.
- [x] **Fünf Sekunden Nachsprechfenster** von dir gewählt; in Testprofilen gespeichert.
- [x] Sechs bewusst aufgenommene Sprachproben samt wiederverwendbaren Helfern versioniert.
- [x] Modellreplay: zwei direkte Wake-Nutzsätze vollständig; drei Negativclips ohne Aktivierung.

## Noch gemeinsam zu prüfen

- [ ] **Bedienung und Trigger** — Manual mit mehreren Sätzen, Start vor altem Final,
  Hotkey/Wake-Rennen, Refresh/Finish/Cancel und Watchdog. M-01/M-03/M-04 teilweise vorbereitet.
- [ ] **Pausen und Hardware** — Runpausen, Hardware-Mute, USB abziehen/verbinden,
  LED-Ausfall bei weiterlaufendem Mikrofon. M-05/M-06.
- [ ] **Fehler und Settings** — Netz-/Serverausfall bei Vorschau und ausstehendem Final,
  Logerholung sowie Settings bei Aufnahme/Drain. M-07/M-08 teilweise technisch geprüft.
- [ ] **Windows-Bedienoberfläche** — Credential-Abläufe/Export, Frozen-Tray/Overlay,
  LED-/Soundgefühl, normale und erhöhte Einfügeziele, Wiedereinfügung. M-09/M-10/M-11 teilweise vorgeprüft.
- [ ] **Sprachproben annotieren** — tatsächliches Wakeende/Nutzsprachbeginn und Wortlaut
  der Alexa-Pausenaufnahme gemeinsam bestätigen; deren geplanter Zieltext wurde nicht exakt erkannt.
- [ ] **Dauerlauf** — mindestens30Minuten/100 abgeschlossene Activations mit Ressourcen-,
  Latenz-, Wake- und Recoverymessung. M-12.
- [ ] **Finale Kalibrierung** — Wake/Pre-Roll, Nachsprechfenster, Trigger, LED, Sound und
  Overlay gemeinsam bestätigen und reproduzierbare Werte sichern.

## Danach selbstständig durch den Agenten

- [ ] Betroffene Regressionen nach Änderungen wiederholen; finalen Stand eindeutig binden.
- [ ] Fallakte, Messwerte, Traceability und PR-Nachweise vervollständigen.
- [ ] Erst bei erfüllten Pflichtkriterien **REVIEW_READY** für unabhängige Abnahme melden.

Aktuell **0/12 vollständige reale M-Pflichtfälle abgeschlossen**. Einzelne erfolgreiche
Teilversuche sind erhalten. Keine Übernahme älterer Belege als pauschaler PASS.

[Mess- und Qualifikationsnachweise](EVIDENCE/ux01/qualification-summary.json) ·
[Fallakte M-01 bis M-12](EVIDENCE/real-cases.json) ·
[Kalibrierung](03_KALIBRIERUNG.md)
