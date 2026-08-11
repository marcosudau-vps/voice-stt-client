# AP05 – Gesamtabnahme und Selbstfertigstellung

> **Datum:** 25. Juli 2026  
> **Gegenstand:** unabhängige Prüfung und Korrektur des ersten
> Antigravity-Durchlaufs  
> **Ergebnis:** nach Korrektur abgenommen; AP6 ist das nächste Paket

## 1. Kurzurteil

Der von Antigravity gemeldete Stand mit 170 grünen Tests war nicht
abnahmefähig. Die Grundarchitektur entsprach weitgehend AP05, aber mehrere
kritische Rennen und Fehlerpfade waren nicht korrekt umgesetzt oder nicht
realitätsnah getestet.

Die Fehler wurden im bestehenden Scope in `core/stt_session.py`,
`core/controller.py` und `core/config.py` korrigiert. Die Audio-
Generationsgrenze in `app.py` beziehungsweise der Controller-Audiobrücke und
die betroffenen Tests wurden ebenfalls gehärtet. Nach der Korrektur bestehen
197 automatische Tests, eine verschärfte Warnungsprüfung, `py_compile`, der
vorhandene Live-Verbindungstest und ein zusätzlicher Smoke-Test der echten
`STTSession`.

## 2. Vor der Korrektur reproduzierte Hauptfehler

### F-01 – Alter Status bestätigte einen neuen Start

Ein bereits vor dem neuen Start vorhandener `LISTENING`-Zustand konnte
`start_dictation()` sofort erfolgreich machen. Es fehlte die eindeutige Bindung
an den konkreten Startversuch und an eine danach eingetroffene
Serverbestätigung.

Reproduzierter Altbefund:

```text
STALE_PREEXISTING_STATUS: True listening active
```

### F-02 – Disconnect während `STARTING` konnte anschließend `ACTIVE` werden

Bei einem Transportverlust während der Startbestätigung wurde zwar
`dictation_interrupted` emittiert, der wartende Startpfad konnte danach aber
trotzdem Erfolg zurückgeben und das Diktat reaktivieren.

Reproduzierter Altbefund:

```text
DISCONNECT_DURING_STARTING: True listening active ['dictation_interrupted']
```

### F-03 – Start-Timeout beendete die gesamte Session-Schleife

Der Timeout rief `session.stop()` auf. Damit wurde nicht nur der defekte Socket
verworfen, sondern der für AP05 ausdrücklich zeitlich unbegrenzte
Reconnect-Loop beendet.

### F-04 – Ping/Pong-Gesundheit war nicht ausreichend isoliert

Die Implementierung konnte während eines offenen Pings weitere Pings senden.
Außerdem konnten unaufgeforderte oder nicht zur aktuellen Generation gehörende
Pongs Backoff beziehungsweise Miss-Zähler beeinflussen.

### F-05 – Audio konnte nach Sessionwechsel falsch neu etikettiert werden

Die Generation wurde erst beim später im asyncio-Thread ausgeführten Callback
bestimmt. Ein im alten Audiothread erzeugtes Paket konnte dadurch nach einem
Reconnect die neue Generation erhalten.

### F-06 – Statusmodell und Fehlerklassen waren unvollständig

Revisionen änderten sich nicht zuverlässig bei Diktatübergängen. Admission-,
Engine-/Recorder-, Command- und wiederholte Audiofehler wurden nicht hinreichend
getrennt. Callback-Ausnahmen konnten empfindliche Laufzeitpfade stören.

### F-07 – Langzeitgrenzen und Konfigurationsvalidierung waren lückenhaft

Die Menge bereits verarbeiteter Finalidentitäten war unbeschränkt. Numerische
Konfiguration akzeptierte unter anderem falsche Typen beziehungsweise
nicht-endliche Werte. Mehrere Tests prüften interne Zähler direkt, statt den
wirklichen Ping- oder Verbindungsloop auszuführen.

### F-08 – Dokumentation widersprach Code und Paketvertrag

Aktive Dokumente meldeten AP05 vorschnell als mit 170 Tests abgenommen und
enthielten zugleich alte Aussagen, AP05 sei noch nicht implementiert. Der
Jitter wurde mehrfach als 0–20 Prozent beschrieben, obwohl Paketvertrag und
`config.yaml` einen konfigurierten Anteil von `0.3` festlegen.

## 3. Durchgeführte Korrekturen

### Start- und Diktatlifecycle

- Jeder Start besitzt einen eigenen Token, Generation, Session-ID, Future und
  Send-Task.
- Nur ein nach dem Start eingetroffener Status der aktuellen Session und
  Generation darf bestätigen.
- Status, der synchron während des Sendens eintrifft, wird nur für denselben
  Versuch gepuffert und anschließend ausgewertet.
- Disconnect, Stop, Shutdown, Command-Fehler und Timeout gewinnen
  deterministisch gegen verspätete Bestätigungen.
- Ein abgebrochener Start kann nicht nachträglich `ACTIVE` werden.
- Ein Start bei nicht bereitem Transport bleibt ohne Vormerkung.
- Timeout invalidiert nur die aktuelle Verbindung und lässt den
  Reconnect-Loop weiterlaufen.
- Headless-Autostart wird höchstens einmal versucht; sein Fehlschlag beendet
  den Controller nicht.

### Transport, Backoff und Ping/Pong

- `is_connected` und `is_ready` erfordern neben dem Protokollzustand einen
  tatsächlich offenen WebSocket.
- Pro Generation existiert höchstens ein ausstehender Anwendungsping.
- Während dieser offen ist, werden Misses gezählt, aber keine weiteren Pings
  gesendet.
- Nur der passende Pong für den offenen Ping der aktuellen Generation und
  Session darf RTT, Miss-Zähler und Backoff zurücksetzen.
- Ping-Sendefehler und Ping-Timeout invalidieren genau die aktuelle
  Verbindung.
- Erster Backoff verwendet das konfigurierte Minimum; exponentielles Wachstum,
  1013-Untergrenze und harte Obergrenze einschließlich Jitter sind
  deterministisch getestet.
- Backoff- und Ping-Tasks werden bei Stop abgebrochen und abgewartet.
- Wiederholte Verbindungsversuche erzeugen keine verwaisten Ping-Tasks.
- Admission vor `hello`, `ready(ok=false)` und Close-Code-Varianten werden
  ausdrücklich klassifiziert.

### Session-, Audio- und Datengrenzen

- Serverevents tragen die interne Empfangsgeneration; der Controller verwirft
  alte Generationen.
- Statusbestätigung erfordert zusätzlich eine passende `sessionId`.
- Die Audiogeneration wird bereits im Audio-Thread aufgenommen und zusammen
  mit dem Paket weitergereicht.
- Der Sender prüft nochmals Diktatzustand, Streaminggrenze und Generation.
- Pakete aus einer alten Session können nicht für eine neue Session
  umetikettiert werden.
- Finalidentitäten werden bei neuer Session bereinigt und auf 4096 Einträge
  begrenzt.

### Status, Fehler und Konfiguration

- Availability- und Dictation-Übergänge erhöhen Snapshot-Revisionen und lösen
  defensive Callback-Kopien aus.
- Fehlerorte `admission`, `engines`/`recorder`, `command`,
  `audio_packet`/`audio` und unbekannte Fehler besitzen getrennte Reaktionen.
- Callback-Ausnahmen werden geloggt und bleiben für Core, Audio und Reconnect
  nicht fatal.
- Serverkonfiguration lehnt boolesche Werte, falsche Typen, nicht-endliche
  Zahlen, ungültige Timeoutwerte und ungültige Ping-Zähler ab.

## 4. Ergänzte oder verschärfte Nachweise

Neu beziehungsweise wesentlich erweitert wurden insbesondere Tests für:

- alten `LISTENING`-Status vor einem neuen Start,
- Disconnect während `STARTING` und doppelte Disconnect-Meldung,
- Session-ID- und Generations-Mismatch,
- Command-Fehler ohne Reconnect-Sturm,
- Timeout mit Socket-Recycling statt Session-Stop,
- Stop während Reconnect und idempotenten Shutdown,
- Snapshot-Revisionen für `STARTING`, `ACTIVE` und `IDLE`,
- nicht-fatale UI-Callback-Ausnahmen,
- begrenzten Finalidentitätscache,
- echten Ping-Loop mit genau einem offenen Ping,
- unaufgeforderten und alten Pong,
- Ping-Sendefehler, Backoff-Capping und 1013-Minimum,
- wiederholte Verbindungszyklen ohne Task-Leak,
- Admission-Fehler vor `hello` und `ready(ok=false)`,
- Audio aus einem alten Thread nach Reconnect,
- strikte Typ-, Endlichkeits- und Timeoutvalidierung.

## 5. Abnahmebelege

### Gesamtsuite

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

```text
Ran 197 tests in 6.771s
OK
```

Nach dem vollständigen Dokumentationsabgleich wurde die Gesamtsuite erneut
ausgeführt:

```text
Ran 197 tests in 5.682s
OK
```

Modulaufteilung:

| Modul | Tests |
| --- |---:|
| `tests/test_history.py` | 30 |
| `tests/test_text_injector.py` | 41 |
| `tests/test_reinsertion.py` | 26 |
| `tests/test_controller.py` | 62 |
| `tests/test_config.py` | 10 |
| `tests/test_stt_session.py` | 18 |
| `tests/test_app.py` | 10 |
| **Gesamt** | **197** |

Die im Lauf sichtbaren Fehlerlogs stammen aus absichtlich simulierten
Negativfällen.

### Warnungsprüfung

```powershell
.\venv\Scripts\python.exe -W error::RuntimeWarning -W error::ResourceWarning `
  -m unittest tests.test_config tests.test_stt_session `
  tests.test_controller.TestSTTControllerAP05Hardening tests.test_app
```

```text
Ran 51 tests in 0.736s
OK
```

### Syntax und Importe

`py_compile` für `app.py`, die drei geänderten Core-Module und die vier
betroffenen Testmodule: Exit-Code 0.

### Echte Serververbindung

Der vorhandene Test `tests/test_connection.py` bestand Health, WebSocket-
Handshake und Ping/Pong. In einem zweiten sicheren Smoke-Test durchlief die
tatsächlich gehärtete `STTSession`:

```text
STTSESSION_LIVE_SMOKE: PASS
READY: True
GENERATION: 1
EVENTS: [('hello', False), ('ready', False), ('pong', True)]
STOPPED_CLEANLY: True
```

Es wurden dabei weder Mikrofonaufnahme noch `start`, Audioübertragung oder
Textinjektion ausgelöst.

## 6. Bewusst verbleibende Grenzen

AP05 ist innerhalb seines festgelegten Scopes abgenommen. Nicht als Teil dieser
Abnahme behauptet werden:

- PySide6, Tray, Overlay, globale Hotkeys und Single-Instance-Verhalten
  (AP6),
- Mikrofonverlust, Hot-Plug, Gerätewechsel und Windows-Sleep/Wake (AP7),
- Langzeit-Stresstest über viele reale Stunden oder Tage (AP7),
- absichtlich ausgelöster realer Netzabbruch während eines laufenden
  Mikrofon-Diktats. Dessen Semantik ist deterministisch automatisiert getestet,
  aber in dieser Abnahme nicht am produktiven Server provoziert.

Diese Grenzen sind kein verdeckter AP05-Mangel, sondern die dokumentierte
Paketgrenze. AP6 darf nun auf den UI-neutralen Status- und Befehlsvertrag
aufsetzen; AP7 bleibt davon getrennt.
