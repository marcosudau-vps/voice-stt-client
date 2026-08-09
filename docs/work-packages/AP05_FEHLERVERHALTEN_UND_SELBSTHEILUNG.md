# AP05 – Fehlerverhalten und stille Selbstheilung

Status: umgesetzt; unabhängig korrigiert und abgenommen; weiterhin verbindlicher Vertrag  
Datum: 2026-07-25  
Vorgänger: AP04 Controller-Integration  
Nachfolger: AP06 UI-Shell

> **Nummerierungsnachtrag vom 2. August 2026:** Alle historischen Verweise
> dieses abgeschlossenen Vertrags auf AP7 als Geräte-, Langzeit-,
> Multi-Monitor-, Autostart- oder Release-Härtung bezeichnen nun AP8. AP7 ist
> das Feedback- und Eventsystem.

## 1. Zweck dieses Dokuments

Dieses Dokument ist der verbindliche fachliche und technische Vertrag für
Arbeitspaket 5. Es legt fest, wie sich der headless Client bei
Transportstörungen, Serverfehlern, ausbleibenden Pongs und mehrdeutigen
Startvorgängen verhält.

Dieses Dokument definiert den Vertrag und ist für sich allein kein
Implementierungsnachweis. AP05 wurde inzwischen umgesetzt und unabhängig
korrigiert abgenommen. Der operative Arbeitsauftrag steht in
`AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG_AUSFUEHRUNGSAUFTRAG.md`; Befund,
Korrekturen und Testnachweise stehen in
`../2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md`.

## 2. Verbindliche Produktentscheidung

Maßgeblich ist
`docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`.

Die drei wichtigsten Invarianten lauten:

1. **Transport heilt sich, Diktat wird nicht wieder aufgenommen.**
2. **Audio überschreitet niemals eine Sessiongrenze.**
3. **Passive Fehler bleiben unaufdringlich; direkt betroffene
   Benutzeraktionen erhalten kurzes, spezifisches Feedback.**

Alle älteren Aussagen, nach einem Reconnect müsse ein Diktierwunsch
„wiederaufgenommen“ werden, sind durch diese Entscheidung ersetzt.

## 3. Verbindliche Quellen und relevante Lektüre

Für die Ausführung gelten die Leseregeln aus `AGENTS.md`. Zusätzlich zu den
kanonischen Orientierungsdateien sind für AP5 gezielt zu lesen:

### Serververtrag

- `server-docs-for-client-development/README.md`
- `server-docs-for-client-development/02-websocket-protokoll.md`
  - Befehle `start`, `stop`, `ping`
  - Reconnect und neue Session
  - kein Replay alter Audiopakete
- `server-docs-for-client-development/03-server-events-kurzreferenz.md`
  - `status`, `error`, `pong`
  - mögliche Recorderzustände
- `server-docs-for-client-development/04-server-events-katalog-und-chronologie.md`
  - direkte und Wake-Word-Startfolge
  - Fehlerklassen und empfohlene Reaktion
- `server-docs-for-client-development/07-robustheit-grenzen-und-sicherheit.md`
  - Reconnect, Backoff, Ping/Pong und Timeouts

### Betroffene Implementierung

- `core/stt_session.py`
- `core/controller.py`
- `core/audio_capture.py`
- `core/config.py`
- `app.py`
- `config.yaml`
- die direkten AP4-Controller- und App-Tests

Nicht pauschal zu laden sind historische Übergabeordner, Archive, die
E-07-Evaluierung, sämtliche Serverdokumente oder spätere UI-Quellen.

## 4. Ausgangslage und konkret zu behebende Defizite

Der bestehende Core besitzt bereits einen grundsätzlich unbegrenzten
Reconnect-Loop und einen Controller-Lifecycle. Folgende Punkte entsprechen
noch nicht dem nun verbindlichen Vertrag:

- Ein öffentlicher Startversuch kann derzeit den Diktierwunsch setzen, obwohl
  der Transport noch nicht `READY` ist. Die Startautomatik kann ihn später
  unerwartet ausführen.
- `send_start()` behandelt das erfolgreiche Senden des JSON-Befehls bereits
  als aktives Streaming, obwohl der Server den Startzustand noch nicht
  bestätigt hat.
- Die aktuelle Ping-Schleife kann einen alten Roundtrip-Wert als scheinbar
  aktuellen Erfolg stehen lassen und überschreibt den Zeitpunkt des
  ausstehenden Pings vor der Miss-Prüfung.
- Der Reconnect-Backoff wird unmittelbar nach `ready` zurückgesetzt. Eine
  Verbindung, die wiederholt direkt nach `ready` abbricht, kann dadurch zu
  aggressiv neu verbinden.
- Sessionabbruch, Startfehler und Queuebereinigung sind noch nicht als
  zusammenhängende, race-sichere Diktatgrenze spezifiziert.
- Der Controllerstatus reicht für die spätere dezente Tray-/Overlay-Anzeige
  noch nicht aus und unterscheidet persistente Verfügbarkeit nicht sauber von
  transientem Benutzerfeedback.

## 5. Paketumfang

AP5 umfasst:

- unbegrenzte, abbrechbare Transportwiederherstellung mit begrenztem Backoff,
- belastbare Ping-/Pong-Miss-Erkennung,
- serverbestätigten Diktatstart mit Zeitgrenze,
- definiertes Ende eines Diktats bei Transportverlust,
- verlässliche Bereinigung von Audio und sessionlokalem Zustand,
- fehlerklassenspezifische Reaktionen,
- persistente UI-neutrale Zustandsdaten,
- sparsame transiente Feedbackereignisse,
- deterministische Tests für Fehlerpfade, Rennen und Ressourcenbereinigung,
- Synchronisierung der kanonischen Dokumentation nach tatsächlicher
  Implementierung.

## 6. Ausdrücklich nicht im Paket

AP5 implementiert nicht:

- PySide6, Tray, Overlay, Farben, Animationen oder Windows-Benachrichtigungen,
- globale Hotkeys,
- einen Admin-Service oder eine Wake-Word-Konfigurationsoberfläche,
- einen Sessionprofil- oder Wake-Word-Override,
- Mikrofon-Hot-Plug, Gerätewechsel oder Wiedereröffnung eines verlorenen
  Audiogeräts,
- Windows-Sleep/Wake-Behandlung,
- Netzwerkprofil- oder Windows-Netzwerkwechsel-APIs,
- Offline-Audioaufzeichnung oder Replay,
- lokales STT-Fallback,
- AP7-Langzeit-, Multi-Monitor-, Autostart- oder Release-Arbeiten.

Mikrofonverlust, Gerätewechsel und Sleep/Wake werden in AP7 umgesetzt. AP5
darf lediglich UI-neutrale Gründe wie `microphone_unavailable` reservieren,
damit AP7 das Zustandsmodell ohne Bruch erweitern kann.

## 7. Begriffe und Lebenszyklen

### Transport

Die WebSocket-Verbindung einschließlich `hello`, `ready`, Ping/Pong und
Reconnect. Der Transport lebt unabhängig davon, ob gerade diktiert wird.

### Session

Der serverseitige Lebenszyklus einer konkreten WebSocket-Verbindung. Jeder
Reconnect erzeugt eine neue Session. Zustände und Identitäten einer alten
Session dürfen nicht auf die neue Session übertragen werden.

### Diktat

Ein ausdrücklich gestarteter Aufnahmevorgang innerhalb genau einer Session.
Ein Diktat befindet sich fachlich in `idle`, `starting` oder `active`.
`interrupted` ist ein einmaliges Ereignis, kein dauerhaft fortzusetzender
Wunschzustand.

### Wiederherstellung

Der passive Versuch, wieder einen gesunden `READY`-Transport zu erhalten.
Wiederherstellung bedeutet niemals automatischer Diktatstart.

## 8. Verbindliches Zustandsmodell

### 8.1 Persistenter Verfügbarkeitszustand

Der Controller muss einen UI-neutralen, abfragbaren Snapshot bereitstellen. Die
konkreten Python-Namen dürfen sich an vorhandene Muster anpassen, die Semantik
ist jedoch verbindlich.

Mindestens unterscheidbar sein müssen:

| Verfügbarkeit | Bedeutung |
|---|---|
| `starting` | Controller wird initialisiert. |
| `connecting` | Verbindung oder Handshake läuft. |
| `ready` | Neuer Benutzerstart darf geprüft und ausgeführt werden. |
| `network_unavailable` | Netzwerk/Socket verhindert derzeit die Verbindung. |
| `server_busy` | Admission wurde abgewiesen, insbesondere Close-Code 1013. |
| `server_unavailable` | Server, Engine oder `ready(ok=false)` ist vorübergehend nicht nutzbar. |
| `protocol_error` | Nicht durch blindes Reconnect heilbarer Client-/Protokollfehler. |
| `shutting_down` | Shutdown läuft; es erfolgen keine neuen Aktionen oder Reconnects. |
| `stopped` | Controller ist vollständig beendet. |

Für AP7 muss das Modell ohne inkompatible Änderung um
`microphone_unavailable` oder einen äquivalent eindeutigen Grund erweiterbar
sein.

Der Snapshot enthält mindestens:

- aktuellen Verfügbarkeitszustand,
- aktuellen Diktatzustand,
- maschinenlesbaren Grundcode,
- optionale sichere Kurzbeschreibung,
- Reconnect-Versuchsnummer,
- optionalen Zeitpunkt oder verbleibende Dauer bis zum nächsten Versuch,
- Transport- und Serverstatus aus dem bestehenden Controller,
- eine monotone Revisionsnummer oder ein gleichwertiges Mittel, damit eine UI
  neue Zustände zuverlässig erkennen kann.

Der Snapshot enthält keine API-Schlüssel, Audioinhalte oder Transkripttexte.

### 8.2 Persistenter Diktatzustand

| Diktatzustand | Bedeutung |
|---|---|
| `idle` | Kein Start in Arbeit und kein aktives Diktat. |
| `starting` | `start` wurde für die aktuelle Session gesendet; Serverbestätigung steht aus. |
| `active` | Serverzustand hat den Start bestätigt; Audio darf gesendet werden. |

Nach einem Abbruch oder Startfehler wird wieder `idle` erreicht. Eine
Unterbrechung bleibt nicht als startbarer Wunsch gespeichert.

### 8.3 Transiente Feedbackereignisse

Zusätzlich zum Snapshot werden einzelne UI-neutrale Ereignisse unterstützt:

| Ereignis | Wann genau |
|---|---|
| `action_blocked` | Ein expliziter Start ist momentan nicht möglich. |
| `dictation_start_failed` | Ein gesendeter Start wird abgelehnt, bleibt mehrdeutig oder läuft in den Timeout. |
| `dictation_interrupted` | Ein Diktat in `starting` oder `active` verliert seine Session. |

Jedes Ereignis enthält:

- Ereignistyp,
- maschinenlesbaren Grundcode,
- sichere Kurzbeschreibung,
- Zeitpunkt beziehungsweise monotone Reihenfolge,
- optional betroffene Aktion.

Farben und Darstellungsdauer gehören nicht in den Core. Ein einzelner
Transportausfall darf höchstens ein Unterbrechungsereignis für das betroffene
Diktat erzeugen. Reconnectversuche dürfen keine Ereignisflut erzeugen.

## 9. Verbindliche Ablaufregeln

### 9.1 Start bei gesundem Transport

1. Der Controller nimmt einen expliziten Start nur an, wenn er läuft, nicht
   herunterfährt, der Transport `READY` und das Diktat `idle` ist.
2. Der Vorgang wird unter der vorhandenen Transition-Sperre atomar nach
   `starting` überführt.
3. Audiocapture darf vorbereitet werden. Audiopakete dürfen vor der
   serverseitigen Bestätigung weder als aktive Sessiondaten gelten noch in die
   WebSocket-Sendeschleife gelangen.
4. Der Client sendet genau einen `start`-Befehl.
5. Innerhalb von standardmäßig 10 Sekunden muss ein bestätigender
   Serverstatus für dieselbe aktuelle Session beobachtet werden.
6. Erst danach wird das Diktat `active` und die Audioübertragung freigegeben.

Primäre Bestätigungen sind:

- `listening` für direkten Betrieb,
- `wakeword_wait` für serverseitigen Wake-Word-Betrieb.

Da `status` laut Serververtrag Beobachtungen und keine garantiert
verlustfreien Einzelschritte darstellt, gelten auch eindeutig spätere aktive
Recorderzustände derselben Session als Bestätigung:

- `wakeword_detected`,
- `voice`,
- `silence`,
- `recording`,
- `transcribing`.

`idle`, `closed`, unbekannte Zustände oder Ereignisse einer alten Session
bestätigen den Start nicht.

### 9.2 Start bei nicht bereitem Transport

- Der Befehl wird sofort mit `success=false` und einem spezifischen Status
  beantwortet.
- Der Diktatzustand bleibt `idle`.
- Es wird kein später auszuführender Wunsch gespeichert.
- Genau ein `action_blocked`-Ereignis wird erzeugt.
- Die passive Transportwiederherstellung läuft unabhängig weiter.

### 9.3 Starttimeout oder mehrdeutiger Start

Nach 10 Sekunden ohne gültige Bestätigung:

- schlägt der Start mit `dictation_start_failed` fehl,
- Audiocapture wird gestoppt beziehungsweise in den Ruhezustand zurückgeführt,
- alle für diesen Versuch wartenden Audiopakete werden verworfen,
- der Diktatzustand wird `idle`,
- der alte Start wird niemals automatisch wiederholt.

Da unklar ist, ob der Server den Befehl teilweise verarbeitet hat, wird die
betroffene WebSocket-Session kontrolliert beendet und der Transport im
Hintergrund neu aufgebaut. Die neue Session bleibt ohne Diktierwunsch.

### 9.4 Transportverlust während eines Diktats

Sobald die aktuelle Session während `starting` oder `active` nicht mehr
verwendbar ist:

1. Diktat atomar beenden,
2. Audiocapture stoppen,
3. Audioqueue vollständig leeren,
4. pending Startbestätigung beenden,
5. sessionlokalen Diktierwunsch löschen,
6. genau ein `dictation_interrupted`-Ereignis ausgeben,
7. Diktatzustand auf `idle` setzen,
8. Transport-Reconnect im Hintergrund fortführen.

Die Reihenfolge darf intern angepasst werden, wenn Tests beweisen, dass
zwischen Sessioninvalidierung und Audiogrenze kein Paket in eine neue Session
gelangt.

### 9.5 Final- und Realtime-Text am Abbruchrand

- Ein echter, vollständig empfangener `final`-Event der alten Session darf
  noch den bestehenden AP4-Pfad History-before-enqueue durchlaufen.
- Ein Realtime-Zwischentext wird verworfen und niemals als Finaltext
  interpretiert.
- Späte Events einer nicht mehr aktuellen Session dürfen keinen neuen
  Diktatzustand bestätigen und keine Audiofreigabe bewirken.
- Bereits angenommene Injection-Aufträge und persistierte Historie werden
  durch einen Transport-Reconnect nicht abgebrochen.

### 9.6 Stop während Reconnect

`stop_dictation` ist erfolgreich idempotent, wenn der Transport gerade
wiederhergestellt wird und kein Diktat aktiv ist. Der Befehl:

- startet keine Verbindung nur für einen `stop`-Befehl,
- beendet nicht den Reconnect-Loop,
- verändert nicht die Shutdown-Semantik,
- erzeugt bei „bereits gestoppt“ kein Warnereignis.

### 9.7 Shutdown

Shutdown gewinnt gegen Start, Startbestätigung, Ping und Reconnect:

- Backoff-Wartezeiten sind sofort abbrechbar,
- keine neue Verbindung und kein Feedbackereignis wird danach gestartet,
- ausstehende Timer/Futures werden beendet,
- Audio wird gestoppt und Queueinhalte werden verworfen,
- bestehende AP4-Garantien für Injection-Queue und History bleiben erhalten.

## 10. Reconnect- und Backoff-Vertrag

### 10.1 Dauer

Wiederherstellbare Fehler werden bis zum expliziten Shutdown ohne feste
Maximalzahl erneut versucht.

### 10.2 Verzögerung

Die vorhandenen Standardwerte bleiben:

- Minimum: 0,5 Sekunden,
- Maximum: 30 Sekunden,
- Jitteranteil: 0,3.

Die Verzögerung wächst exponentiell und wird **einschließlich Jitter** auf den
konfigurierten Maximalwert begrenzt. Tests verwenden injizierbaren Zufall und
eine kontrollierbare Uhr beziehungsweise Wartefunktion; sie dürfen nicht von
realer Zeit abhängen.

Admission-Ablehnung mit Close-Code 1013 wird als `server_busy` eingeordnet und
verwendet standardmäßig mindestens 10 Sekunden Wartezeit, weiterhin begrenzt
durch das konfigurierte Maximum. Diese Untergrenze darf als benannte
Konfiguration oder Konstante umgesetzt werden, muss aber getestet und
dokumentiert sein.

### 10.3 Stabilitätsgrenze für Backoff-Reset

Ein bloß empfangenes `ready` setzt die Fehlerserie nicht zurück. Der Backoff
wird erst zurückgesetzt, wenn die neue Verbindung ihre Funktionsfähigkeit
durch den ersten gültigen `pong` für einen in dieser Verbindung ausstehenden
Ping belegt hat.

Damit führt eine Folge aus `ready` und sofortigem Verbindungsabbruch nicht
immer wieder zur Minimalverzögerung.

### 10.4 Sessionisolation

Jeder Versuch besitzt eine eigene Generation. Timer, Pongs, Startbestätigungen
und Events einer älteren Generation dürfen den Zustand der aktuellen
Verbindung nicht verändern.

## 11. Ping-/Pong-Vertrag

Der Server liefert kein Ping-ID-Feld. Deshalb gelten folgende Regeln:

- Pro Verbindung existiert höchstens ein ausstehender Anwendungsping.
- Ein neuer Ping wird erst gesendet, wenn der vorherige durch `pong` erledigt
  wurde. Solange dieser Ping aussteht, wird kein weiterer Ping gesendet.
- Der Zeitpunkt des ausstehenden Pings wird beim Senden gesetzt und nicht vor
  seiner Bewertung überschrieben.
- Ein `pong` löscht genau den aktuell ausstehenden Zustand, zeichnet den RTT
  auf und setzt die Zahl aufeinanderfolgender Misses zurück.
- Ein historischer RTT-Wert ist niemals Beweis für die Antwort auf einen neuen
  Ping.
- Nach jedem vollständigen Pingintervall ohne Pong wird für denselben
  ausstehenden Ping genau ein weiterer Miss gezählt. Der ausstehende Ping
  bleibt bis zum Pong oder bis zur Reconnect-Schwelle bestehen. Dadurch kann
  ein verspäteter Pong ohne Ping-ID nicht versehentlich einem neueren,
  parallelen Ping zugeordnet werden.
- Sobald `ping_timeout_count` aufeinanderfolgende Misses erreicht sind, wird
  die aktuelle Verbindung genau einmal invalidiert und ein Reconnect
  ausgelöst.
- Unerwartete oder verspätete Pongs ohne ausstehenden Ping ändern weder
  Generation noch Miss-Zähler.
- Alle Pingzustände werden bei jeder neuen Session und beim Shutdown
  vollständig zurückgesetzt.
- Ping-, Event- und Sendeschleifen dürfen nicht mehrfach pro Verbindung
  weiterlaufen.

Die vorhandenen Standardwerte bleiben 10 Sekunden Pingintervall und drei
aufeinanderfolgende Misses. Sie sind konfigurierbar.

## 12. Fehlerklassifikation und Reaktion

| Ursache | Persistenter Status | Diktatreaktion | Transportreaktion | Benutzerfeedback |
|---|---|---|---|---|
| DNS-, Socket-, TLS- oder Netzwerkfehler | `network_unavailable` | laufenden Start/Diktat abbrechen | unbegrenzt mit Backoff reconnecten | nur bei betroffenem Start/Diktat |
| Close-Code 1013 / Admission voll | `server_busy` | laufenden Start/Diktat abbrechen | längerer Backoff, dann erneut | nur bei betroffenem Start/Diktat |
| `ready(ok=false)`, Engine nicht bereit | `server_unavailable` | kein Start zulassen | Verbindung gemäß Vertrag beenden/neu versuchen | nur blockierte explizite Aktion |
| wiederholte Ping-Misses | `network_unavailable` oder spezifischer `ping_timeout`-Grund | laufenden Start/Diktat abbrechen | Session invalidieren, reconnecten | nur bei betroffenem Diktat |
| `error` Kategorie `recorder` | `server_unavailable` mit Recordergrund | betroffenen Start/Diktat abbrechen | bei wiederholtem/terminalem Fehler reconnecten | einmal spezifisch |
| `error` Kategorie `engine` | `server_unavailable` | Start/Diktat abbrechen | Backoff und später erneut | einmal spezifisch |
| `error` Kategorie `command` | `protocol_error` | Start fehlschlagen lassen | kein blinder Reconnect-Sturm; Verbindung darf kontrolliert geschlossen werden, automatische Wiederholung des Befehls verboten | einmal spezifisch |
| `error` Kategorie `audio_packet` | transportbereit mit degradiertem Grund | fehlerhaftes Paket verwerfen; erst bei Serie Diktat abbrechen | einzelne Ursache kein Reconnect | nur wenn Diktat beendet wird |
| `error` Kategorie `audio` | degradiert/serverseitiger Audiogrund | bei Wiederholung Diktat abbrechen | gemäß Serververtrag Recorder/Session neu aufbauen | nur wenn Diktat betroffen |
| unbekannter Serverfehler | sicherer generischer Grund | abhängig von Sessiongültigkeit | keine Endlosschleife ohne Klassifikation; Socketzustand separat bewerten | höchstens einmal pro betroffene Aktion |

Die Implementierung darf zusätzliche interne Grundcodes verwenden. Sie darf
aber keine unterschiedlichen Ursachen in einer irreführenden Meldung
zusammenfassen und keine potenziell geheimen Serverdaten ungefiltert an UI oder
Logs weiterreichen.

## 13. Controller- und Schnittstellenvertrag

### 13.1 Bestehende Schnittstellen

Die vorhandenen öffentlichen AP4-Befehle bleiben grundsätzlich erhalten:

- `start_dictation`
- `stop_dictation`
- `toggle_dictation`
- Statusabfrage und Statuscallback

Rückgabewerte müssen weiterhin ehrlich sein. Ein bloß gesendeter
WebSocket-Befehl ist kein erfolgreicher Diktatstart.

### 13.2 Erweiterungen

Erforderlich sind:

- ein immutable oder sicher kopierbarer Zustands-Snapshot,
- eine UI-neutrale Feedbackschnittstelle oder ein äquivalenter
  Ereignis-Callback,
- maschinenlesbare Enums/Reason-Codes statt Auswertung freier Logtexte,
- eine race-sichere Zuordnung von Startbestätigung und Events zur aktuellen
  Sessiongeneration.

Callbacks dürfen den asyncio-Core nicht blockieren. Exceptions in
Status-/Feedbackempfängern werden geloggt und dürfen Reconnect, Audio oder
Shutdown nicht zerstören.

### 13.3 Headless Initialstart

Der vorhandene headless Start nach dem ersten `READY` darf erhalten bleiben,
damit `app.py` weiterhin ohne UI nutzbar ist. Dafür gelten enge Grenzen:

- nur interne initiale Startoption,
- höchstens einmal je Controllerlauf,
- niemals als Folge eines Reconnects erneut scharf,
- ein Verbindungsverlust nach `starting` oder `active` beendet das Diktat
  endgültig,
- spätere AP6-Benutzerstarts werden nie vorgemerkt.

## 14. Audio- und Ressourcengrenzen

- Audiopakete besitzen implizit oder explizit die Generation der Session, für
  die sie aufgenommen wurden.
- Beim Sessionwechsel wird die Audioqueue vor einer neuen Freigabe geleert.
- Ein Producer aus einer alten Generation darf nicht in die neue
  Sendeschleife schreiben.
- Die Queue bleibt begrenzt; Reconnect erzeugt keinen wachsenden Offlinepuffer.
- Connection-, Ping-, Receive- und Starttimer-Tasks werden beim
  Generationswechsel sauber beendet.
- Deduplizierungs- und sessionlokale Eventzustände dürfen über viele
  Reconnects nicht unbeschränkt wachsen. Persistente Historie und bereits
  angenommene Injection-Aufträge bleiben davon unberührt.

## 15. Konfiguration

Folgende Werte müssen validiert, dokumentiert und testbar sein:

| Schlüssel | Standard | Bedeutung |
|---|---:|---|
| `reconnect_min_delay` | 0.5 s | kleinste Reconnectverzögerung |
| `reconnect_max_delay` | 30.0 s | harte Obergrenze einschließlich Jitter |
| `reconnect_jitter` | 0.3 | relativer Zufallsanteil |
| `server_busy_min_delay` | 10.0 s | Mindestwartezeit nach Admission/1013 |
| `ping_interval` | 10.0 s | Intervall/Miss-Zeitfenster |
| `ping_timeout_count` | 3 | aufeinanderfolgende Misses vor Reconnect |
| `start_confirmation_timeout` | 10.0 s | Wartezeit auf serverseitige Startbestätigung |

Bestehende Schlüssel dürfen kompatibel weiterverwendet werden. Neue Werte
gehören in `config.yaml`, `core/config.py`, Validierung und Konfigurationstests.
Ungültige Werte müssen früh und verständlich abgelehnt werden. Mindestens gilt:
Verzögerungen und Timeouts sind größer als null, `ping_timeout_count` ist eine
Ganzzahl größer oder gleich eins, `reconnect_jitter` liegt zwischen 0 und
kleiner als 1, und `reconnect_max_delay` ist nicht kleiner als
`reconnect_min_delay` oder `server_busy_min_delay`.

## 16. Nebenläufigkeit und Rennen

Mindestens folgende Rennen müssen explizit aufgelöst sein:

- Start gegen Transportverlust,
- Startbestätigung gegen Timeout,
- Start/Stop gegen Shutdown,
- Pong gegen Ping-Timeout,
- alter Pong gegen neue Sessiongeneration,
- alter Serverstatus gegen neuen Start,
- Audio-Callback gegen Queueleerung und Sessionwechsel,
- Finalannahme gegen Sessionabbruch,
- mehrfach gleichzeitig gemeldeter Socketfehler gegen genau einen Reconnect,
- Status-/Feedbackcallback-Exception gegen Core-Lifecycle.

Ein Lock allein genügt nicht als Nachweis. Die fachliche Gewinnerregel muss im
Test sichtbar sein. Tests verwenden Events, Futures und injizierte Uhren statt
willkürlicher Sleeps.

## 17. Verbindliche Tests

### 17.1 Baseline

Vor der ersten Codeänderung:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Erwarteter dokumentierter Ausgangsstand: 152 Tests erfolgreich. Eine
Abweichung ist vor der Implementierung zu erklären.

### 17.2 Transport und Backoff

- Reconnect läuft über beliebig viele simulierte Fehler bis Shutdown weiter.
- Verzögerung wächst exponentiell und überschreitet inklusive Jitter nie das
  Maximum.
- 1013 wird als `server_busy` mit längerer Mindestwartezeit eingeordnet.
- `ready` allein setzt den Backoff nicht zurück.
- erster gültiger Pong der aktuellen Generation setzt ihn zurück.
- Shutdown während Backoff beendet unverzüglich und ohne weiteren Versuch.
- parallele Fehlerpfade erzeugen nur einen Reconnect je Generation.

### 17.3 Ping/Pong

- höchstens ein ausstehender Ping,
- alter RTT maskiert keinen Miss,
- gültiger Pong setzt Miss-Zähler zurück,
- Schwelle invalidiert die Verbindung genau einmal,
- verspäteter/unerwarteter Pong wird sicher ignoriert,
- neue Generation startet mit leerem Pingzustand,
- Pingtask bleibt über wiederholte Reconnects nicht hängen.

### 17.4 Startbestätigung

- Start bei nicht `READY`: sofort abgelehnt, kein gespeicherter Wunsch,
  einmaliges `action_blocked`.
- direkter Start wird durch `listening` bestätigt.
- Wake-Word-Start wird durch `wakeword_wait` bestätigt.
- eindeutig spätere aktive Zustände können einen übersprungenen
  Zwischenstatus bestätigen.
- Status alter Sessiongeneration bestätigt nichts.
- Timeout nach kontrollierten 10 Sekunden beendet Start, Audio und Queue.
- Disconnect während `starting` erzeugt genau einen Abbruch und keinen
  automatischen Neustart.
- Reconnect nach aktivem Diktat bleibt `idle`, bis ein neuer Benutzerstart
  erfolgt.
- interner headless Initialstart erfolgt höchstens einmal.

### 17.5 Audio-, Final- und Queuegrenzen

- keine alten Audiopakete nach Sessionwechsel,
- Queue wird bei Startfehler und Diktatabbruch geleert,
- Callbackrennen kann kein altes Paket nach dem Leeren einschleusen,
- echter Finaltext unmittelbar vor Abbruch bleibt im AP4-Pfad,
- Realtime-Zwischentext wird nicht zu Finaltext,
- Injection-Queue und persistierte Historie laufen unabhängig vom
  Transport-Reconnect weiter.

### 17.6 Status und Feedback

- alle definierten persistenten Zustände und Grundcodes sind erreichbar,
- wiederholte Reconnectversuche erzeugen keine Feedbackereignisflut,
- blockierter Start, Startfehler und Diktatabbruch sind unterscheidbar,
- erfolgreiche Wiederherstellung wird als `ready` sichtbar, startet aber kein
  Diktat,
- Callback-Exceptions bleiben nicht fatal,
- Snapshot enthält keine Audio- oder Transkriptinhalte.

### 17.7 Ressourcen und Regression

- keine verwaisten Tasks/Futures nach Reconnect und Shutdown,
- sessionlokale Mengen und Zuordnungen bleiben über viele simulierte
  Reconnects begrenzt,
- vollständige bestehende Testsuite bleibt grün,
- Syntaxprüfung aller geänderten Python-Dateien erfolgreich.

## 18. Optionale manuelle/live Abnahme

Automatisierte Tests sind Pflicht. Zusätzlich soll, soweit der reale Server
verfügbar ist, dokumentiert werden:

1. Client ohne Diktat starten, Netzwerk kurz unterbrechen, Netzwerk
   wiederherstellen: Client wird still wieder `READY`.
2. Diktat starten, währenddessen Netzwerk unterbrechen: Diktat endet,
   Reconnect erfolgt, keine automatische neue Aufnahme.
3. Nach wiederhergestelltem `READY` bewusst neu starten: neues Diktat
   funktioniert.

Ein Live-Test darf keine automatische Manipulation von Server-Wake-Word- oder
Admin-Einstellungen vornehmen.

## 19. Abnahmekriterien

AP5 ist nur abnahmefähig, wenn:

- alle Regeln dieses Vertrags im Code nachweisbar umgesetzt sind,
- kein Startwunsch über einen Reconnect fortlebt,
- Audio und Startbestätigungen strikt sessiongebunden sind,
- Start erst nach Serverbestätigung erfolgreich wird,
- Starttimeout 10 Sekunden beträgt und konfigurierbar ist,
- Ping-Misses deterministisch und ohne alten RTT-Scheinbeleg erkannt werden,
- der Reconnect unbegrenzt, gedeckelt, jitterbehaftet und sauber abbrechbar ist,
- Status und Feedback vollständig UI-neutral sind,
- AP7-Themen nicht vorweggenommen wurden,
- sämtliche neuen und bestehenden Tests grün sind,
- Testanzahl und Befehle dokumentiert sind,
- `task.md`, Roadmap, Projektübersicht und `ÜBERGABE.md` den tatsächlich
  erreichten Stand widerspruchsfrei wiedergeben.

## 20. Feststehende Entscheidungen und offene Punkte

Für AP5 bestehen keine offenen Produktfragen mehr. Festgelegt sind:

- kein Resume nach Reconnect,
- kein Audio-Replay,
- kein verzögerter Benutzerstart,
- stiller zeitlich unbegrenzter Reconnect,
- 10 Sekunden Startbestätigung,
- serverseitige Statusbestätigung als Erfolgsgrenze,
- transientes Feedback nur bei direkt betroffener Benutzeraktion,
- Mikrofon-/Geräte-/Sleep-Wake-Heilung erst in AP7.

Implementierungsdetails dürfen nur variiert werden, wenn alle Invarianten und
Tests unverändert erfüllt bleiben. Eine fachliche Abweichung erfordert vor der
Umsetzung eine neue dokumentierte Entscheidung.
