# AP-IV2-020 – unsere Testcheckliste

**Stand: 15.10.2026 · Technische Qualifikation grün · Gemeinsame Realtests offen**

Ich pflege die Häkchen nach den tatsächlichen Nachweisen. „Teilweise geprüft“
bedeutet noch keinen vollständig bestandenen Pflichtfall. Derselbe R01 und
[Draft-PR15](https://github.com/marcosudau-vps/voice-stt-client/pull/15) bleiben aktiv.

## Jetzt: nur die beiden Wake-Sätze wiederholen

- [ ] **„Sprachtest starten“** klicken, wenn du für die zwei Sätze bereit bist.
- [x] Automatische native Einfügeprobe mit Leerzeichen erfolgreich.
- [ ] „Hey Jarvis“ + roter Ball vollständig, ohne Rufwort im Editor.
- [ ] „Alexa“ + gelbe Tasche vollständig, ohne Rufwort im Editor.
- [ ] Beide Finals mit Leerzeichen getrennt; F9-Steuerung und Fokus nachgewiesen.
- [ ] Dein Urteil zu **320ms Pre-Roll** und direktem Sprechbeginn festhalten.

Die jeweilige kurze Aktion steht im Testfenster. Erst nach **FERTIG** zurück
in den Chat wechseln. Die Einfügeprobe ist bereits bestanden. Der neue Sprachtest wartet auf seinen eigenen Startknopf.

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
