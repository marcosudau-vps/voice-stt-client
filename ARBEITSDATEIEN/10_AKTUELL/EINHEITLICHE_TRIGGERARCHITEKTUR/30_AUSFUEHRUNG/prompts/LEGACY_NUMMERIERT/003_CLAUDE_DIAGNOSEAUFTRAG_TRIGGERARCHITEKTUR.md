# Claude-Diagnoseauftrag – Abweichungen von der einheitlichen Triggerarchitektur

## Auftrag

Bei der ersten echten manuellen Abnahme sind mehrere schwerwiegende Probleme aufgetreten. Der bisherige Validierungsstand ist daher bis zur Klärung nur vorläufig.

**In diesem Auftrag noch nichts implementieren oder reparieren.**

Erstelle ausschließlich:

1. eine forensische Ist-Analyse,
2. Root-Cause-Ermittlung,
3. ein vollständiges Legacy-/Altpfad-Inventar,
4. eine State-/Transition-Analyse,
5. eine Testlückenanalyse,
6. einen verbindlichen Korrekturplan.

Danach stoppen.

---

# 1. Normative Grundlage

Die Datei

```text
ZIELBILD_EINHEITLICHE_TRIGGERARCHITEKTUR.md
```

ist die **verbindliche Soll-Spezifikation**.

Sie ist nicht nur Kontext oder ein Vorschlag. Prüfe den aktuellen Stand in allen drei Repositories konsequent gegen diese Spezifikation:

```text
voice-stt-server
voice-stt-client
led_controller_respeaker-v3
```

Wenn bisherige Implementierungen, Tests, Dokumentationen oder frühere Entscheidungen der Zielbildspezifikation widersprechen, hat für diese Untersuchung die Zielbildspezifikation Vorrang.

Insbesondere gilt jetzt verbindlich:

- im Idle können `manual` und `wake_word` die nächste gemeinsame serverseitige Activation auslösen;
- der **erste akzeptierte Trigger gewinnt** und setzt den Activation-/Trigger-Lock;
- weitere Activation-Trigger sind bis zur vollständigen Rückkehr nach Idle gesperrt;
- während einer laufenden Activation bedeutet der normale Hotkey `finish`;
- Wake Words während einer laufenden Activation haben keine fachliche Wirkung;
- der alte clientseitige Hotkey-Aufnahme-/VAD-Pfad darf keine eigene Runtime-Autorität mehr bilden;
- es gibt keine unterschiedlichen Betriebsmodi, Aufnahmewege oder Feedbackmodelle für Manual und Wake Word.

---

# 2. Harte Arbeitsregel

Für diesen Auftrag:

- keine Produktcodeänderung;
- keine Testcodeänderung;
- keine Configänderung;
- keine Dokumentation passend machen;
- keine Commits;
- keine Pushes;
- keine Merges;
- keine Rebases;
- keine Tags;
- keine PRs.

Erlaubt:

- Code und Konfiguration lesen;
- Git-Diffs untersuchen;
- vorhandene Tests ausführen;
- rein diagnostische Befehle;
- Logs/Eventfolgen untersuchen;
- lokale Testumgebung verwenden;
- reproduzierende Tests ohne Dateiänderungen;
- temporäre rein diagnostische Ausgaben außerhalb der Repositories, falls nötig.

---

# 3. Beobachteter Realfehler A – Activation/Diktat bleibt hängen

Manueller Bedienablauf:

1. Anwendung im Manual-/Hotkey-Zustand gestartet.
2. Idle-Anzeige zunächst korrekt.
3. normaler Hotkey betätigt.
4. Aufnahme/Activation startete.
5. Sprache wurde transkribiert.
6. eigentliche Aufnahme war anschließend erkennbar beendet.

Danach blieb der Client jedoch fachlich in einem aktiven Diktatzustand:

- weißer Ring blieb aktiv;
- „Diktat verlängern“ blieb dauerhaft auswählbar;
- kein sauberer Rücksprung in Idle.

Untersuche die **gesamte reale Produktionskette**, nicht nur die UI:

```text
Manual Trigger
→ serverseitige Activation
→ Recording Start
→ serverseitiges VAD
→ Recording End
→ Final
→ Follow-up / Finish / Timeout / Finalisierung
→ Trigger-Lock freigeben
→ Idle
```

Ermittle exakt:

- welcher Übergang stattgefunden hat;
- welcher fehlt;
- welcher Serverzustand vorliegt;
- welcher Clientzustand vorliegt;
- wer den weißen Ring steuert;
- wer „Diktat verlängern“ enabled;
- ob Client und Server auseinanderlaufen;
- ob ein Event/Ack fehlt;
- ob ein Timer fehlt oder stale ist;
- ob alte lokale Hotkey-/VAD-/Diktatlogik weiterhin Autorität besitzt;
- ob ein Legacy-`mode` den Zustand beeinflusst;
- ob der Trigger-Lock oder Activation-State nicht korrekt freigegeben wird.

Besonders prüfen, ob hier genau die verbotene doppelte Wahrheit existiert:

```text
Server: Recording/Activation bereits beendet
Client: alter lokaler Diktatstate glaubt weiterhin „aktiv“
```

Keine kosmetische UI-Reparatur planen, bevor die Lifecycle-Ursache nachgewiesen ist.

---

# 4. Beobachteter Realfehler B – Legacy-Betriebsmodus im Settings-UI

Im realen Einstellungsdialog erscheint weiterhin:

```text
Legacy
  Legacy-Betriebsmodus: Hotkey
```

und separat:

```text
Triggerquellen
  Manueller Trigger
  Wake-Word-Trigger
```

Das widerspricht dem Zielmodell.

Untersuche:

- woher der Legacy-Bereich kommt;
- welche Settings-Metadaten ihn erzeugen;
- ob `mode` nur noch ein versehentlich sichtbarer Migrationsrest ist;
- oder ob `mode` weiterhin Runtime-Autorität besitzt.

Prüfe ausdrücklich, ob `mode` noch Einfluss hat auf:

- Sessionerzeugung;
- WebSocket-Parameter;
- Recorder;
- lokales oder serverseitiges VAD;
- Triggerlogik;
- Start/Stop;
- UI-/Traystatus;
- Feedback;
- Follow-up;
- Reconnect;
- Settings Apply.

Klassifiziere jeden relevanten Fund:

```text
A – aktive alte Runtime-Autorität → Architekturdefekt
B – begrenzter Compatibility-Adapter
C – reine Config-Migration ohne Runtime-Autorität
D – historisch/archiviert
E – unkritischer Name
```

---

# 5. Beobachteter Realfehler C – Wake-Word-Gruppe leer

Im Einstellungsdialog existiert eine Gruppe:

```text
Wake Word
```

ohne Eingabeelemente.

Prüfe:

- welches Wake-Word-Datenmodell existiert;
- welche Wake Words aktuell tatsächlich unterstützt/verfügbar sind;
- ob ein Serverkatalog/Capability existiert;
- ob Mehrfachauswahl vorgesehen oder bereits teilweise implementiert ist;
- wo Settings-Metadaten oder Wiring fehlen;
- ob Persistenz existiert;
- wie die Werte an den Server gelangen.

Ziel laut Spezifikation:

- bevorzugt Mehrfachauswahl der verfügbaren Wake Words;
- mindestens jedoch eine funktionierende Eingabemöglichkeit mit sinnvollem Default.

Noch nichts implementieren.

---

# 6. Beobachteter Realfehler D – dauerhaftes gelbes Warnblinken

Nach dem Versuch, Trigger-/Betriebseinstellungen zu verändern, entstand dauerhaftes gelbes Warnblinken mit:

```text
Aktion derzeit nicht verfügbar
```

Untersuche:

- welches Event/Command die Warnung auslöst;
- welchen Codepfad sie nimmt;
- welche Aktion angeblich nicht verfügbar ist;
- warum sie wiederholt/dauerhaft ausgelöst wird;
- ob eine Event-/Command-Schleife entsteht;
- ob nach Apply/Reconnect stale Commands gesendet werden;
- ob Client und Server unterschiedliche Activation-Zustände haben;
- ob Legacy-`mode` beteiligt ist;
- ob Trigger-Lock/Activation-State falsch ausgewertet wird;
- ob die Warnung nur Symptom eines tieferen Lifecycle-Fehlers ist.

Nicht als LED-Problem behandeln, solange die Quelle nicht bewiesen ist.

---

# 7. Altarchitektur besonders gründlich prüfen

Die Zielbildspezifikation beschreibt ausdrücklich, dass im früheren Hotkey-Modus ein eigener clientseitiger Aufnahme-/VAD-/Lifecycle-Pfad existierte.

Suche deshalb nicht nur nach dem Wort `legacy`, sondern nach den **alten Verantwortlichkeiten** selbst:

- lokales VAD als Aufnahmeende-Autorität;
- clientseitige Recording-Ende-Entscheidung;
- `_dictation_requested` oder sinngleiche Zustände;
- lokale Diktat-State-Machine;
- lokaler Follow-up-Owner;
- Hotkey-spezifischer Recorder;
- Hotkey-spezifische Timer;
- mode-basierte Sessionerzeugung;
- mode-basierte WebSocket-Parameter;
- mode-basierte UI-/Tray-/Feedbacklogik;
- getrennte Hotkey-/Wake-Word Start-/Stop-Pfade;
- getrennte Audio-/Recording-Lifecycles;
- Hotkey/Wake-Word als Betriebsmodi statt Triggerquellen.

Zentrale Prüffrage:

> Würde dieser Code noch gebraucht, wenn es fachlich überhaupt keinen „Hotkey-Modus“ und keinen „Wake-Word-Modus“ mehr gäbe, sondern nur die gemeinsame serverseitige Activation?

Wenn nein, ist er sehr wahrscheinlich Altarchitektur.

---

# 8. First-Trigger-Lock und Hotkey-Zweitbedeutung prüfen

Prüfe die tatsächliche Implementierung gegen folgende verbindliche Semantik:

## Idle

Wenn aktiviert:

```text
normaler Hotkey
→ Manual-Activation
```

oder:

```text
Wake Word
→ Wake-Word-Activation
```

Der erste akzeptierte Trigger gewinnt.

## Laufende Activation / Verarbeitung

Danach gilt bis zum stabilen Idle ein Trigger-Lock.

Währenddessen:

```text
normaler Hotkey
→ Finish der aktuellen Activation
```

unabhängig davon, ob die Activation ursprünglich durch Manual oder Wake Word gestartet wurde.

Dagegen:

```text
Wake Word während aktiver Activation
→ keine fachliche Wirkung
```

Es darf dadurch insbesondere nicht entstehen:

- zweite Activation;
- zweiter Recorder;
- Extend;
- Finish;
- Quellen-Merge;
- Moduswechsel.

## Rückkehr zu Idle

Erst nach vollständiger Finalisierung und stabilem Idle:

```text
Trigger-Lock lösen
→ konfigurierte Triggerquellen wieder freigeben
```

Prüfe auch nahezu simultane Manual-/Wake-Word-Trigger: genau ein Gewinner, der zweite wird unterdrückt.

---

# 9. Sekundären Wake-Word-Pause-Hotkey abgrenzen

Historisch hatte der normale Hotkey im alten Wake-Word-Betrieb teilweise andere Sonderbedeutungen.

Im Zielmodell ist das verboten.

Prüfe:

- ob der normale Hotkey im Idle noch irgendwo Wake Word pausiert/deaktiviert;
- ob seine Bedeutung noch von `mode` abhängt;
- ob ein separater konfigurierbarer Wake-Word-Pause-Hotkey vorhanden/vorgesehen ist;
- ob diese Bedienfunktion sauber von Manual-Trigger und Finish getrennt ist.

Ziel:

```text
normaler Hotkey:
Idle      → Activation starten
Activation→ aktuelle Activation finishen

sekundärer Wake-Word-Pause-Hotkey:
Wake-Word-Erkennung pausieren / fortsetzen
```

---

# 10. Continuous Streaming erneut am echten Produktionspfad prüfen

Nicht nur Tests lesen.

Rekonstruiere den realen Produktionspfad:

```text
Client verbindet
→ Stream startet einmal

Activation 1
→ beendet

Activation 2
→ beendet

...

Sessionende
→ Stream stoppt
```

Dokumentiere:

- wo der Stream tatsächlich gestartet wird;
- wo er beendet wird;
- wo Activation geöffnet wird;
- wo Activation beendet wird;
- welche Commands tatsächlich gesendet werden;
- ob Manual und Wake Word nach Triggerannahme exakt denselben serverseitigen Aufnahme-/VAD-/Finalisierungspfad benutzen.

Wenn der Manual-Pfad noch lokales VAD als fachlichen Aufnahmeende-Owner verwendet, ist die Zielarchitektur nicht erreicht.

---

# 11. State-/Transition-Sicherheit vollständig analysieren

Erstelle die tatsächliche produktive State Machine.

Mindestens fachlich abdecken:

```text
Idle
Activation geöffnet
Warten auf erste Sprache
Recording
Nachlauf / Follow-up
Finish
Cancel
Timeout
Finalisierung
Idle
```

Für jeden Zustand:

- Owner;
- Eintritt;
- erlaubte Commands;
- Exit;
- Timer;
- maximale Lebensdauer;
- Generation-/Activation-ID-Guards;
- Reconnect;
- Session Close;
- Serverfehler;
- Clientfehler;
- stale Events;
- stale Timer;
- doppelte Finish-/Cancel-Kommandos;
- Race Recording-End vs Final;
- Race Timeout vs Final;
- Race Finish vs Recording-End.

Besonders prüfen:

> Kann irgendein nichtterminaler Zustand ohne definierten Fallback unbegrenzt bestehen bleiben?

Das darf nicht möglich sein.

---

# 12. UI-/Feedbackmodell gegen die Architektur prüfen

Die Zielarchitektur kennt keine unterschiedlichen fachlichen Recording-/Lifecycle-Farben für Manual und Wake Word.

Prüfe:

- Trayfarbe;
- Statusring;
- Statusbeschriftung;
- LED-State;
- Sounds;
- Button-Enablement;
- Warnungen.

Für denselben Serverzustand muss dieselbe fachliche Darstellung entstehen, unabhängig vom ursprünglichen Trigger.

Suche insbesondere nach source-/mode-abhängiger Darstellung, die unterschiedliche Lifecycle-Darstellungen erzeugt.

Triggerquelle darf diagnostische Information sein, aber kein zweites Feedbackmodell.

---

# 13. Settings Apply / Reconnect untersuchen

Untersuche den realen Ablauf bei:

```text
Apply
Server neu verbinden
```

Prüfe:

- welche Config gespeichert wird;
- welche Config tatsächlich verwendet wird;
- welche Query-/Admission-Parameter gesendet werden;
- welche alten Zustände verworfen werden;
- Pending Commands;
- Activation-ID;
- Generation;
- Trigger-Lock;
- Recorderstate;
- UI-/Feedbackstate;
- Triggerquellen;
- Wake Words.

Nach Reconnect darf kein alter Diktat-/Activation-Zustand weiterleben.

---

# 14. Testlücken erklären

Die bisherigen automatisierten Nachweise waren umfangreich und trotzdem sind diese Probleme beim ersten realen Bedienlauf sichtbar geworden.

Für jeden bestätigten Defekt beantworten:

```text
Welche konkrete Testlücke hat diesen Fehler durchgelassen?
```

Vorgehen:

1. Produktionspfad verfolgen.
2. tatsächliche Root Cause bestimmen.
3. erst danach vorhandene Tests bewerten.
4. erklären, warum sie den Fehler nicht erkennen konnten.

Keine grünen Tests als Ersatz für Produktionspfad-Analyse verwenden.

---

# 15. Geforderter Diagnosebericht

Erstelle einen Bericht mit dieser Struktur:

## A. Executive Diagnosis

Beantworte zuerst:

> Ist das überwiegend ein UI-/Wiring-Rest oder steckt die alte Architektur noch substanziell im Produktivpfad?

Einstufung:

```text
A – überwiegend UI/Metadata-Fehler
B – begrenzte Lifecycle-/Wiring-Defekte
C – relevante alte Architektur weiterhin aktiv
D – grundlegende Zielarchitektur nicht erreicht
```

Mit Begründung.

## B. Befunde

Für jeden bestätigten Defekt:

- Reproduktion;
- Root Cause;
- betroffene Dateien/Funktionen;
- Architekturwirkung;
- Schweregrad;
- Testlücke;
- Zusammenhang mit anderen Defekten.

Mindestens:

```text
DEFECT-1 – Diktat/Activation bleibt aktiv
DEFECT-2 – Legacy-Betriebsmodus im Settings-UI
DEFECT-3 – Wake-Word-Gruppe leer
DEFECT-4 – dauerhaft „Aktion derzeit nicht verfügbar“
```

Weitere Funde separat.

## C. Legacy-/Altpfad-Inventar

Tabelle:

| Fund | Repo | Datei/Funktion | heutige Wirkung | Klassifikation A–E | Zielmaßnahme |
|---|---|---|---|---|---|

## D. State-Machine-Analyse

- tatsächliche aktuelle State Machine;
- erforderliche Ziel-State-Machine;
- fehlende Transitions;
- doppelte Authorities;
- unbegrenzte Zustände;
- Race-/stale-state-Risiken.

Mermaid verwenden, wenn es die Gegenüberstellung klarer macht.

## E. Testlücken

Für jeden Defekt konkret.

## F. Verbindlicher Korrekturplan

Erst aus der Diagnose ableiten.

Nicht symptomweise flicken.

Für jedes Arbeitspaket:

- Ziel;
- betroffene Komponenten;
- zu entfernende alte Verantwortlichkeiten;
- notwendige Implementierung;
- Tests;
- Negativtests;
- Race-/Lifecycle-Tests;
- Akzeptanzkriterien.

---

# 16. Keine kosmetische Reparatur

Nicht einfach planen:

- Legacy-Combobox ausblenden;
- weißen Ring manuell zurücksetzen;
- Warnmeldung unterdrücken;
- Wake-Word-Textfeld ergänzen;

wenn darunter die alte Architektur oder doppelte Lifecycle-Autorität bestehen bleibt.

Die sichtbaren Fehler sind zunächst **Indikatoren**.

Zuerst muss bewiesen werden, ob das Zielmodell im Produktionspfad wirklich erreicht ist.

---

# 17. Abschluss

Am Ende ausschließlich liefern:

```text
DIAGNOSE
ARCHITEKTURBEWERTUNG
ROOT CAUSES
LEGACY-/ALTPFAD-INVENTAR
STATE-MACHINE-ANALYSE
TESTLÜCKEN
KORREKTURPLAN
RISIKEN
```

Danach stoppen.

**Keine Implementierung beginnen, bevor der Diagnosebericht und Korrekturplan ausdrücklich freigegeben wurden.**
