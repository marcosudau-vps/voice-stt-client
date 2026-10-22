# Idle-Zielzustand und direkte LED-Vorschau – 19.10.2026

Status **BLOCKED**, Workflow **IMPLEMENTATION_IN_PROGRESS**; gleicher R01/PR15.
R11 bleibt CLOSED. Produkt0f6c85e unverändert, kein neuer Produktfix.

[Letzter Vergleich](EVIDENCE/direct-idle-20261019/assessment.json): Versuch9e2b0bd8,
Exit0, menschlich „Wie erwartet“ / „Es ist in Ordnung so.“ übernommen.
Keine nativen Steuerereignisse, keine Activation, kein Übergang nach Eingabeschluss.
Die gewünschte30/100%-Konfiguration hing am`server.input.idle`-Mapping; der
Lebenszyklusstart ruft separat`ready_state` auf. Deshalb ist nicht belegt, dass
der Mensch tatsächlich die neue Variante beurteilt hat. Die Rückmeldung wird
bewahrt, aber **nicht als PASS der30/100%-Kalibrierung ausgegeben**.
Kein nachgewiesener Produktfehler und keine Schuldzuweisung aus fehlenden Keys.

Die dauerhafte Testhilfe`tests/manual/v2/idle_preview.py` zeigt die gewünschte
Konfiguration jetzt direkt über den vorhandenen LED-Controller:

- Vor eigenem START weder LED-Übernahme noch Client, Mikrofon, Audio, Hotkey,
  Settings-HTTP oder Serververbindung.
- START setzt exakt`ready_state` mit weiß/min0,30/peak1,0 und dem bisherigen
  globalen Helligkeitswert192/255. Keine zusätzliche farbige Übergangsanimation.
-20sBeobachtungszeit erst ab gemeldeter realer LED-Verfügbarkeit; bei fehlender
  Ausgabe begrenzter Fehler statt künstlich erfolgreichem Countdown.
- Anschließend explizite Auswahl „Passt“, „Noch violett“ oder andere Abweichung,
  optionale Notiz und Übernehmen. Ausgabe wird dann freigegeben.
- Wiederholen erhält frühere Versuche separat. Schließen stoppt nur den eigenen
  Controller. Derselbe Hardware-Qualifikationsmutex verhindert parallele Testclients.
- Hashes von Vorschau, Testwertdatei und produktivem LED-Controller werden gesichert.

[Validierung](EVIDENCE/direct-idle-20261019/validation.json):31Helfertests PASS;
Qt-Selbstcheck prüft tatsächliche Widgets/Start/Verfügbarkeit/20s/Auswahl/Stop und
Wiederholung mit erhaltenem Vorversuch, ausdrücklich Dummycontroller/keine Hardware.
Der echte LEFX-Renderer ist bereits in den31Tests für alle12LEDs über einen ganzen
Zyklus enthalten. Unverändertes Produkt behält den1400Windows-/Buildnachweis;
keine neue physische oder vollständige Paketqualifikation durch Helfer-Selbstchecks.

Nächste notwendige menschliche Handlung: im direkten Vorschaufenster START,
20sbeobachten, Ergebnis übernehmen. Keine zusätzliche Taste/Sprache/USB-Aktion.
Neue physische Bewertung bleibt bis dahin NOT_RUN. Farbprofile weiter ausdrücklich
separates späteres Feature. Weitere M-/Frozen-/W01-/100Activations-Gates unverändert.

Der beendete Lauf ist privat hashgeprüft im Projekt gesichert. Auch seine Entfernung
wurde durch automatische Freigabeprüfung mit ausschließlich „blocked by policy“
abgelehnt. Damit10beendete gesicherte externe Ordner als Aufräumreste; genaue
Zuordnung im[Aufräumprotokoll](EVIDENCE/direct-idle-20261019/cleanup.json).
Keine Umgehung/erneute Löschversuche derselben Ziele. Neue LED-only-Laufzeit nach
Auswertung ebenfalls ins Projekt sichern und im genehmigten Namensraum aufräumen.
