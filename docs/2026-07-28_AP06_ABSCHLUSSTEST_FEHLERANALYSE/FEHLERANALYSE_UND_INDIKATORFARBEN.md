# AP6-Abschlusstest – Fehleranalyse und Indikatorfarben

> **Stand:** 28. Juli 2026  
> **Ergebnis:** AP6 ist aufgrund zweier nachgewiesener Clientfehler im
> Betriebsmoduswechsel noch nicht abnahmefähig.  
> **Änderungsgrenze:** Die beiden Fehler wurden in diesem Arbeitsschritt
> absichtlich nicht behoben. Umgesetzt wurde ausschließlich das separat
> beauftragte Farbkonzept für Tray und kurzes Fehlerfeedback.

> **Nachtrag:** F-01 und F-02 wurden anschließend behoben und durch
> wiederholte lokale sowie produktive Moduswechsel verifiziert. Maßgeblicher
> Abschlussnachweis:
> `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`. Die nachfolgende
> Darstellung bleibt als ursprünglicher Diagnosebefund erhalten.

## 1. Ausgangslage

Der Benutzer hat die manuellen AP6-Prüfungen 1 bis 4 erfolgreich
durchgeführt. Damit sind Hotkey-Diktat, Initial-Timeout, Folgeaufnahme und
manuelle Verlängerung im realen Bedienlauf grundsätzlich belegt.

Prüfung 5 scheiterte in folgender Folge:

1. Wechsel vom Hotkey- in den Wake-Word-Modus;
2. Wake Word wurde nicht erkannt;
3. der primäre Hotkey löste keine direkte Aufnahme aus;
4. beim Rückwechsel in den Hotkeymodus endete der Core;
5. der Tray blieb rot und meldete einen Core-Fehler.

Für die Analyse wurden `logs/client.log`, die gespeicherte
Benutzerkonfiguration unter
`%LOCALAPPDATA%\RealtimeSTT Client\config.yaml`, die beteiligten
Controller-/UI-Pfade und der aktuell veröffentlichte Serververtrag gelesen.

## 2. Belegte Laufzeitfolge

### 2.1 Erster Wechsel in den Wake-Word-Modus

Der Client speicherte am 28. Juli um 02:10:31 Uhr die neue Konfiguration.
Danach wurde die alte Verbindung kontrolliert mit
`session_configuration_changed` geschlossen. Um 02:10:33 Uhr stand eine neue
Session der Generation 2 bereit:

```text
wss://stt.voice.marcosudau.com/ws/transcribe
  ?wakeWordEnabled=true
  &wakeWords=hey_jarvis
```

Der Server akzeptierte damit den Sessionwunsch bis `READY`. Zwischen diesem
`READY` und 02:14:24 Uhr startete der Client jedoch keine Audioaufnahme.
Ohne kontinuierliches PCM-Audio kann der serverseitige Wake-Word-Detektor
nichts erkennen.

### 2.2 Hotkeybetätigung im Wake-Word-Modus

Ab 02:14:24 Uhr zeigen die Logs mehrere Paare aus:

```text
Audio capture started
Sent start command
Audio capture stopped
Sent stop command
```

Das entspricht der derzeit implementierten Wake-Word-Bediensemantik: Der
primäre Hotkey aktiviert oder pausiert den Wake-Word-Hintergrundstream. Er
umgeht die serverseitige Wake-Word-Schranke nicht und startet daher keine
direkte Hotkey-Diktierung. Ein Druck bei bereits aktivem Stream pausiert
stattdessen die Wake-Word-Erkennung.

Nach einem Anwendungsneustart startete der Client um 02:16:30 Uhr bereits im
gespeicherten Wake-Word-Modus. In diesem Fall wurde der Hintergrundstream
automatisch gestartet. Nach weiteren Hotkey-Pause/Fortsetzungsvorgängen lief
der letzte belegte Stream von 02:16:59 bis zum Rückwechsel um 02:22:41 Uhr.

### 2.3 Absturz beim Rückwechsel

Um 02:22:41 Uhr wurde der Wechsel zurück zum Hotkeymodus angestoßen. Der
Client stoppte zunächst korrekt die aktive Audioaufnahme. Danach endete
`STTController._maintain_wake_word_mode()` regulär, weil die laufende
Konfiguration nicht mehr `wake_word` war.

Der allgemeine Task-Wächter in `STTController.run()` behandelt aber jedes
normale Ende dieses Helper-Tasks als unerwarteten Fehler:

```text
RuntimeError: Helper task ... _maintain_wake_word_mode() ...
finished unexpectedly.
```

Daraufhin wurde der gesamte Core-Thread beendet. Die UI zeigte folgerichtig
den fatalen roten Zustand. Der noch laufende Settings-Apply wurde
zurückgerollt; deshalb enthält die Benutzerkonfiguration weiterhin
`session.mode: wake_word`.

## 3. Hergeleitete Ursachen

### F-01 – Wake-Wort-Stream wird nach Hotkey → Wake Word nicht automatisch erzeugt

**Einstufung:** eindeutig clientbedingt.

Der Wake-Word-Maintainer wird in `STTController.run()` nur dann als Helper-Task
erzeugt, wenn der Prozess bereits im Wake-Word-Modus startet. Ein späterer
Laufzeitwechsel ändert zwar Session und Konfiguration, erzeugt diesen Task
aber nicht. Genau deshalb blieb zwischen 02:10:33 und der ersten
Hotkeybetätigung um 02:14:24 die Audioaufnahme aus.

**Folge:** Der Dialog kann einen erfolgreichen Sessionwechsel melden, obwohl
der notwendige dauerhafte Wake-Word-Audiostream nicht scharfgeschaltet ist.

### F-02 – Reguläres Ende des Wake-Word-Maintainers wird als fatal bewertet

**Einstufung:** eindeutig clientbedingt.

Beim Rückwechsel muss der Wake-Word-Maintainer enden. Sein normales
`return` wird vom generischen Run-Loop dennoch als unerwartetes Helper-Ende
behandelt. Das erklärt den exakten Stacktrace, den roten Indikator und den
beendeten Core vollständig.

**Folge:** Der Client ist in diesem Pfad nicht selbstheilend. Nach dem
Core-Ende existiert kein Hintergrundmechanismus mehr, der den Betriebsmodus
oder die Verbindung wiederherstellen könnte.

### F-03 – Hotkey im Wake-Word-Modus ist kein Direct-Hotkey

**Einstufung:** kein Protokollfehler, aber missverständliche Bediensemantik.

Der aktuelle Vertrag verwendet die primäre Aktion im Wake-Word-Modus zum
Aktivieren und Pausieren des Hintergrundstreams. Ein Direct-Hotkey, der die
Wake-Word-Schranke für genau eine Aufnahme umgeht, ist nicht implementiert.
Das beobachtete Verhalten entspricht daher dem Code, ist im manuellen Test
aber leicht als Startfehler zu deuten.

### F-04 – Ausbleibende Erkennung bei tatsächlich laufendem Stream

**Einstufung:** noch offen; weder Client noch Server abschließend belegt.

Für die Session ab 02:16:30 bestätigt der Client:

- akzeptierte Wake-Word-Session mit `hey_jarvis`,
- Serverzustand `READY`,
- gestartete Audioaufnahme und gesendeten `start`-Befehl,
- keinen protokollierten Session-, Recorder- oder Enginefehler.

Der aktuelle Server veröffentlicht über `/api/config` weiterhin:

- Sessionvertrag Version 1,
- Wake Word unterstützt,
- Backend `openwakeword`,
- Modell-ID `hey_jarvis` in ONNX und TFLite.

Damit ist eine Vertragsablehnung ausgeschlossen. Die Client-INFO-Logs
enthalten jedoch weder die fortlaufenden Recorderzustände noch
Wake-Word-Scores oder Audiopegel. Sie beweisen deshalb nicht, ob der Server
PCM-Pakete in ausreichender Qualität erhalten und wie OpenWakeWord sie
bewertet hat.

Für die serverseitige Prüfung ist insbesondere die Session
`abb10b59684a40e384ec5331aec8441d` im Zeitraum
**02:16:30 bis 02:22:41 Uhr (Europe/Berlin)** relevant. Zu prüfen sind:

1. effektive Recorder-/Wake-Word-Konfiguration;
2. `wakeword_wait_started` und nachfolgende Status-/Timelineereignisse;
3. empfangene PCM-Chunks, Audiolücken und Pegel;
4. OpenWakeWord-Scores, Sensitivität, Fallbacks und Detektionen;
5. Recorderwarnungen oder verworfene Audiopakete.

Ohne diese Serverbelege wäre eine Aussage „Serverfehler“ ebenso unzulässig
wie die Aussage „nur falsche Aussprache“.

## 4. Client-/Server-Abgrenzung

| Beobachtung | Client | Server | Ergebnis |
|---|---:|---:|---|
| Sessionwunsch `wakeWordEnabled=true` akzeptiert | belegt | belegt | Vertrag funktioniert |
| Nach Laufzeitwechsel zunächst kein Audiostream | ursächlich | nicht beteiligt | Clientfehler F-01 |
| Hotkey startet keine direkte Aufnahme | aktueller Bedienvertrag | Wake-Word-Schranke arbeitet weiter | kein Direct-Hotkey vorhanden |
| Rückwechsel beendet Core | ursächlich | nicht beteiligt | Clientfehler F-02 |
| Wake Word bei laufendem Stream nicht erkannt | noch nicht ausgeschlossen | noch nicht ausgeschlossen | Server-/Audiobelege fehlen |
| roter Zustand bleibt bestehen | Folge des beendeten Core-Threads | nicht beteiligt | Client-Selbstheilung greift hier nicht |

## 5. Bewusst noch nicht vorgenommene Fehlerkorrekturen

Auf ausdrücklichen Auftrag wurden keine Fixes für F-01 bis F-04 umgesetzt.
Insbesondere unverändert blieben:

- Erzeugung und Lebenszyklus des Wake-Word-Maintainers,
- Moduswechsel und Settings-Apply/Rollback,
- Semantik der primären Aktion im Wake-Word-Modus,
- fataler Core-Fehlerpfad und automatischer Wiederanlauf,
- Protokollierung der Wake-Word-/Audiomesswerte.

Diese Trennung verhindert, dass die Diagnose durch einen vorzeitigen Fix
verwischt wird.

## 6. Umgesetztes Indikator-Farbkonzept

Das separat beauftragte Farbkonzept wurde implementiert:

| Modus/Zustand | Darstellung |
|---|---|
| Hotkey, wartet auf Hotkey | dunkelgrün |
| Hotkey, wartet auf erste oder weitere Sprache | dunkelgrün mit weißem Rand |
| Hotkey, Serversegment aktiv | hellgrün |
| Wake Word, wartet auf Wake Word | dunkelblau |
| Wake Word erkannt / wartet auf Sprache | dunkelblau mit weißem Rand |
| Wake Word, Sprache/Recorder aktiv | hellblau |
| Wake Word bewusst pausiert | grau |
| Netzwerk-, Server- oder Mikrofonproblem | gelb |
| interner/protokollarischer Fehler | rot |
| Shutdown/gestoppt | grau |

Der weiße Rand ist Teil des tatsächlich gerenderten Tray-Icons. Der
UI-neutrale Snapshot transportiert dazu den servergemeldeten Recorderzustand;
Statusänderungen erzeugen nur bei einem tatsächlichen Zustandswechsel einen
neuen Snapshot. Start-, Stop- und Reconnectlogik wurden dafür nicht geändert.

Kurzes aktionsbezogenes Feedback verwendet ebenfalls Gelb für externe
Netzwerk-, Server-, Timeout-, Audio- und Mikrofonursachen. Rot bleibt internen
beziehungsweise protokollarischen Fehlern vorbehalten.

## 7. Teststand dieser Änderung

Vor der Farbänderung bestand die vollständige Baseline mit 257 Tests.
Ergänzt wurden gezielte Prüfungen für:

- alle drei Hotkey-Farbphasen;
- alle drei Wake-Word-Farbphasen;
- einheitliches Gelb für externe Verfügbarkeitsprobleme;
- Rot für Protokollfehler;
- tatsächliches Rendern des weißen Tray-Rands;
- Snapshot-Veröffentlichung bei geändertem Server-Recorderzustand.

Gezielte Präsentations-, AP6-, UI- und Controllertests bestanden. Anschließend
bestand die vollständige Regression:

```text
Ran 261 tests in 6.619s
OK
```

`compileall` über `app.py`, `core/`, `ui/` und `tests/` war ebenfalls
erfolgreich. Diese grünen Tests betreffen das neue Farbkonzept und die
bisherige Regression; sie widerlegen die im manuellen Lauf nachgewiesenen,
absichtlich noch nicht korrigierten Betriebsmodusfehler nicht.
