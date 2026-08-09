# Stellungnahme und überarbeitetes Gesamtkonzept für das Client-Feedback- und Server-Eventsystem

> **Datum:** 1. August 2026  
> **Status:** nicht bindende Planungsfortsetzung und technische Gegenprüfung  
> **Bezug:** `2026-07-31_ERSTER_VORSCHLAG_CLIENT_FEEDBACK_EVENTSYSTEM_GESAMTKONZEPT.md`  
> **Ergebnis:** Der Erstvorschlag enthält viele tragfähige Bausteine, seine zentrale Festlegung von `/ws/logs` als primärer Quelle für zeitkritisches Benutzerfeedback sollte jedoch nicht übernommen werden.

## 1. Auftrag und Einordnung

Dieses Dokument reagiert auf den ersten Gesamtvorschlag für das Client-Feedback-, Event- und Logsystem. Es vergleicht den Vorschlag mit:

- dem am 1. August 2026 veröffentlichten Serverstand,
- dem tatsächlichen Serververtrag und den dokumentierten Abweichungen,
- der bereits implementierten und getesteten Clientarchitektur,
- den verbindlichen Technologie-, Threading- und Dokumentationsregeln des Clients.

Es ist bewusst keine neue verbindliche Roadmap und kein Implementierungsauftrag. Eine spätere Übernahme erfordert einen eigenen Paketvertrag, einen Abgleich der kanonischen Client-Protokolldokumentation und eine ausdrückliche Freigabe.

Mit „Planung von null“ kann sinnvollerweise nur das neue Feedback- und Server-Eventvorhaben gemeint sein. Die implementierten und verifizierten Clientpakete AP1 bis AP6 sind keine leere Ausgangslage und sollten nicht neu entworfen werden. Das neue Vorhaben muss auf ihren stabilen Grenzen aufsetzen.

## 2. Kurzfazit

Meine Empfehlung lautet:

1. `/ws/transcribe` bleibt die primäre und autoritative Laufzeitquelle für die aktuelle Diktatsession, ihre Bedienzustände, Wake-Word-, Aufnahme- und Transkriptionsmeilensteine sowie Realtime- und Finaltext.
2. Lokale Tatsachen wie Hotkeyannahme, Mikrofonzustand, Soundausgabe, spätere TTS-Ausgabe, Textinjektion und LED-Gerätefehler bleiben lokale Clientereignisse.
3. `/ws/logs` wird als ergänzende Beobachtungs- und Diagnoseebene integriert: aktueller Session-Eventfeed, Performancewerte, bounded Eventjournal, Gap-Anzeige und optional spätere Historienansicht.
4. Replay aus `/ws/logs` darf Diagnosemodelle und eine Eventansicht vervollständigen, aber weder alte Sounds und LED-Impulse auslösen noch den aktuellen operativen Sessionzustand gegen `/ws/transcribe` überschreiben.
5. Die bestehende Clientarchitektur wird erweitert, nicht durch eine parallele zweite Zustandsmaschine ersetzt.
6. Interaktives Feedback, ReSpeaker-LED, Live-Diagnose und administrative Historie werden in getrennte Arbeitspakete aufgeteilt.

Der wichtigste Unterschied zum Erstvorschlag ist damit:

```text
Nicht:
    /ws/logs -> primäre Bedienzustände und Feedback

Sondern:
    /ws/transcribe + lokale Ereignisse -> operative Wahrheit und Feedback
    /ws/logs                         -> Beobachtung, Diagnose und Historie
```

## 3. Tatsächliche Ausgangslage

### 3.1 Der Serverstand ist nicht mehr nur geplant

Das neue Serversystem ist veröffentlicht und in wesentlichen Teilen live. Implementiert sind unter anderem:

- die Channels `system`, `audit`, `transcription` und `performance`,
- ein gemeinsamer Envelope mit `schemaVersion`, `eventId`, globalem `cursor`, `timestamp`, `channel`, `event`, `severity`, `serverInstanceId`, Korrelationsfeldern und `data`,
- ein zentraler `StructuredEventHub`,
- unabhängige begrenzte Queues für SQLite, JSONL, stdout und Live-Publishing,
- `/ws/logs` mit Session- oder Adminzugriff,
- Replay bis zu einem beim Verbindungsaufbau erfassten Cursor-Wasserstand,
- die History-Routen,
- sessiongebundene Logtokens aus `hello.logAccess`,
- zentrale Redaction und eine konfigurierbare Transkripttextpolicy.

Bekannt und ausdrücklich dokumentiert sind zwei Grenzen:

- Bei gleichzeitiger Überlast mehrerer Sinks ist nicht für jeden Sink ein eigener `log.gap` garantiert.
- Ein leeres finales WebSocket-Ergebnis erhält derzeit kein terminales `transcription.completed`, `transcription.failed` oder `transcription.cancelled`.

### 3.2 Der vorhandene Client besitzt bereits die operative Zustandsachse

Der Client enthält bereits:

- `STTSession` als gehärteten `/ws/transcribe`-Transport,
- einen `STTController` als UI-neutrale Orchestrierungs- und Zustandsgrenze,
- `ControllerStatusSnapshot`, `AvailabilityState`, `DictationState` und `DictationWindowPhase`,
- eine generationgebundene Session- und Reconnectlogik,
- einen vorhandenen Serverevent-Einstieg über `handle_server_event`,
- die produktiv genutzten `status`- und `timeline`-Ereignisse,
- thread-sichere Qt-Signale über `CoreBridge`,
- reine Präsentationsabbildungen in `ui/presentation.py`,
- vorhandenes optionales Soundfeedback in `ui/feedback.py`,
- Tray und Overlay als bereits getestete Ausgabekanäle.

Besonders wichtig: `timeline(recording_started)` und `timeline(recording_ended)` steuern heute bereits das generationgebundene Diktatfenster. `status` bestätigt Startversuche und prägt die Traydarstellung. Diese Logik darf durch eine zweite, zeitlich nachgelagerte Logzustandsmaschine nicht dupliziert werden.

### 3.3 Die kanonische Clientkopie des Serververtrags ist noch nicht aktualisiert

Nach `AGENTS.md` sind ausschließlich die Dateien unter `server-docs-for-client-development/` die verbindliche Protokollquelle des Clients. Diese lokale Kopie enthält den neuen Vertrag zu `hello.logAccess`, `/ws/logs`, Cursor-Replay und History derzeit noch nicht.

Das ist vor jeder Implementierung zu beheben. Die jetzt verwendeten Serverquellen sind für diese Planungsprüfung ausdrücklich freigegeben, ersetzen aber noch nicht die im Client festgelegte Quellenhierarchie.

## 4. Was am Erstvorschlag überzeugt

Folgende Leitgedanken sollten übernommen werden:

### 4.1 Keine Auswertung menschenlesbarer Logtexte

Feedback und Diagnose dürfen nur strukturierte Felder verwenden. `meldung` ist Anzeige- und Diagnoseinhalt, kein stabiler Steuervertrag.

### 4.2 Text bleibt auf `/ws/transcribe` autoritativ

Realtime- und Finaltexte dürfen nicht aus strukturierten Logs rekonstruiert werden. Das schützt den Client zudem gegen `transcript_log_mode=none` und gegen unterschiedliche Datenschutzkonfigurationen.

### 4.3 Transport, Normalisierung und Ausgabe werden getrennt

Eine saubere Trennung zwischen Transport, Protokollvalidierung, fachlicher Normalisierung, Policy und konkreten Ausgabegeräten ist richtig. Sie sollte jedoch in die vorhandenen Komponenten integriert und nicht als große Parallelarchitektur umgesetzt werden.

### 4.4 Replay löst keine alten Impulse aus

Historische oder nachgelieferte Ereignisse dürfen keine vergangenen Sounds, Kurzzeiteffekte oder vollständigen Overlaydauern erneut auslösen. Diese Regel ist verbindlich sinnvoll.

### 4.5 Bounded Buffer und Qt-Modell

Eine Eventansicht benötigt ein begrenztes Modell, keine unbegrenzte Widget- oder Textfeldsammlung. `QAbstractTableModel` ist dafür passend.

### 4.6 Lokale Ereignisse bleiben lokale Tatsachen

Hotkey, Mikrofon, TTS, Textinjektion und Ausgabegeräte sind nicht durch Serverlogs zu ersetzen. Das ist eine wichtige und richtige Abgrenzung.

### 4.7 Keine direkte Kopplung von WebSocket an LED oder Sound

Konkrete Hardware- oder Multimediaaktionen dürfen nicht in einem Transportcallback liegen. Die Ausgaben sollen nur abstrahierte, bereits bewertete Instruktionen erhalten.

## 5. Zentrale Korrektur: `/ws/logs` ist nicht die primäre Feedbackquelle

### 5.1 Semantische Reihenfolge im Server

Der Server erzeugt bei den zentralen Sessionmeilensteinen zuerst das `timeline`-Event für `/ws/transcribe` und leitet danach daraus das strukturierte Event ab.

Beispiele:

```text
timeline(recording_started)
    -> anschließend transcription.recording_started

timeline(wakeword_detected)
    -> anschließend wakeword.detected

final + timeline(final_transcript)
    -> anschließend transcription.completed
```

Damit ist `/ws/transcribe` nicht nur ohnehin nötig, sondern auch näher am interaktiven Vorgang.

### 5.2 Der strukturierte Eventpfad ist absichtlich best effort

Der `StructuredEventHub` vergibt zwar früh einen Cursor, fächert das Ereignis danach aber unabhängig auf begrenzte Queues für Store, Datei, stdout und Publish aus. Das Live-Publishing:

- kann überlastet sein,
- kann einzelne Events verlieren,
- kann einen Subscriber-Gap erzeugen,
- ist nicht atomar mit der SQLite-Persistenz,
- garantiert nicht, dass ein live gesendetes Event zuvor gespeichert wurde.

Kritische und terminale Ereignisse haben eine bessere Priorität, aber keine absolute Zustellgarantie.

### 5.3 Replay verbessert Diagnose, nicht zeitkritische Wirkung

Replay ist für eine Eventansicht sehr wertvoll. Für einen Aufnahmestartton oder Wake-Word-Impuls hilft eine spätere Nachlieferung jedoch nicht: Ein alter Ton darf gerade nicht nachgeholt werden.

Die Zuverlässigkeitsvorteile von Cursor und Replay rechtfertigen deshalb keine Verlagerung der interaktiven Primärquelle. Sie rechtfertigen eine ergänzende Diagnoseebene.

### 5.4 Eine doppelte operative Zustandsmaschine wäre riskant

Wenn `status` und `timeline` weiterhin Startbestätigung, Diktatfenster und Reconnect steuern, `/ws/logs` aber LED und Sound als angeblich primäre Quelle steuert, entstehen zwei zeitlich verschiedene Wahrheiten über denselben Vorgang. Das begünstigt:

- widersprüchliche Zustände,
- verspätete Rücksetzungen,
- Doppelimpulse,
- schwer testbare Cross-Transport-Deduplizierung,
- neue Race Conditions bei Reconnect und Sessionwechsel.

Die bessere Lösung ist eine operative Zustandsachse mit mehreren Präsentationsausgängen.

## 6. Empfohlene Quellenhierarchie im laufenden Client

| Sachverhalt | Primäre Quelle | Ergänzende Quelle | Begründung |
|---|---|---|---|
| Hotkey erkannt | lokaler Win32-Hotkey | keine | Nur der Client kennt die tatsächliche lokale Annahme. |
| Startbefehl angenommen/bestätigt | bestehender Controller über `/ws/transcribe` | strukturiertes Event nur Diagnose | Der Startversuch ist bereits generation- und sessiongebunden gehärtet. |
| Wake Word erkannt | `/ws/transcribe` `timeline(wakeword_detected)` | `/ws/logs` `wakeword.detected` im Journal | Timeline wird zuerst publiziert und gehört zur aktuellen Session. |
| Aufnahme begonnen/beendet | `/ws/transcribe` `timeline` und `status` | strukturierte Events im Journal | Bereits operative Grundlage des Diktatfensters. |
| Realtime- und Finaltext | `/ws/transcribe` `realtime` und `final` | niemals aus Logs rekonstruieren | Datenschutzmodus kann Text in Logs entfernen. |
| Finaltext speichern/einfügen | bestehender Finalpfad im `STTController` | `transcription.completed` nur Korrelation/Diagnose | History und Deduplizierung sind bereits getestet. |
| Mikrofon verfügbar/verloren | `AudioCapture` | Serverfehler nur ergänzend | Lokales Gerät ist Clientbesitz. |
| TTS/Sound läuft | lokaler Ausgabedienst | keine | Der Client kontrolliert den tatsächlichen Ausgabestart und das Ende. |
| Textinjektion erfolgreich/fehlgeschlagen | `TextInjectionQueue`/History | keine | Nur der Client kennt Zielprozess und Win32-Ergebnis. |
| Server-Performance | `/ws/logs` `performance` | History-API | Das ist der vorgesehene Diagnosekanal. |
| Aktuelle strukturierte Sessionereignisse | `/ws/logs` | History-API für Nachladung | Cursor und Replay sind hier sinnvoll. |
| Globale Serverdiagnose | Adminzugriff, optionales separates Werkzeug | keine normale Session-UI | Sessiontokens dürfen `system` nicht lesen. |

## 7. Überarbeitete Zielarchitektur

Die Architektur sollte zwei Ebenen besitzen, die bewusst nicht gleichberechtigt den Bedienzustand schreiben.

```text
OPERATIVE EBENE

Win32-Hotkey ─┐
AudioCapture ─┼──────────────┐
/ws/transcribe ──> STTSession ├─> STTController ─> ControllerStatusSnapshot
Injection ────┘              │                    + TransientEvent
TTS/Soundstatus ─────────────┘                              │
                                                           v
                                                  FeedbackPolicy
                                               /        |        \
                                            Tray     Overlay    Sound/LED


BEOBACHTUNGS- UND DIAGNOSEEBENE

hello.logAccess
      │
      v
ServerEventStream (/ws/logs)
      │
      v
ServerEventProtocol
      │
      +──> begrenztes ServerEventJournal ──> Qt-Eventmodell/Diagnose
      +──> Gap-/Transportstatus
      +──> optionale Performance-Aggregation

GET /api/logs/events ──> explizite historische Abfrage
```

### 7.1 Nur eine operative Zustandsinstanz

Der `STTController` bleibt Besitzer der Sessiongeneration, der Diktatzustände und der operativen Laufzeitentscheidung. Es wird kein zweiter `FeedbackController` eingeführt, der dieselben Serverzustände unabhängig rekonstruiert.

Stattdessen wird die vorhandene Ausgabegrenze erweitert:

- `ControllerStatusSnapshot` für dauerhafte Zustände,
- ein erweitertes, typisiertes Impulsmodell für kurzzeitige Ereignisse,
- eine reine `FeedbackPolicy`, die Snapshot plus Impuls auf Sound-, Overlay- und LED-Instruktionen abbildet.

### 7.2 Orthogonale Zustände statt einer einzigen Prioritätenliste

Die im Erstvorschlag genannte lineare Reihenfolge `ERROR > SPEAKING > RECORDING > ...` ist zu grob. Verfügbarkeit, Diktataktivität, lokaler Ausgabestatus, Logtransport und Gerätegesundheit sind verschiedene Achsen.

Empfohlen sind mindestens:

```text
Availability:   starting | ready | network_unavailable | server_busy | ...
Dictation:      idle | starting | active
Server phase:   wakeword_wait | listening | recording | transcribing | ...
Output:         silent | sound_playing | tts_speaking
Log transport:  disabled | connecting | replaying | live | degraded
LED device:     unavailable | ready | failed
```

Erst die reine Präsentationspolicy entscheidet, was ein konkreter Ausgabekanal zeigt. Dadurch kann beispielsweise eine gelbe Netzwerkstörung sichtbar sein, ohne einen bereits sauber abgeschlossenen lokalen Injektionsstatus zu verlieren.

### 7.3 Zustände, Impulse und Overlays bleiben getrennt

Dieser Gedanke aus dem Erstvorschlag wird beibehalten:

- Zustand: hält an, bis eine neue operative Tatsache eintritt;
- Impuls: einmalige, nicht nachholbare Wirkung;
- Overlay: zeitgebundene Zusatzdarstellung über einem Grundzustand.

Ein Impuls erhält zusätzlich eine stabile lokale `impulse_id`. Dadurch können einzelne UI-Ausgänge idempotent reagieren, ohne Server-`eventId` und lokale Ereignisse gleichsetzen zu müssen.

## 8. Schlankere Modulgrenzen

Die vorgeschlagenen Verzeichnisse `logging_client/` und `feedback/` würden große Teile der bestehenden Architektur duplizieren und außerdem mit dem lokalen Python-Logging verwechselt werden.

Eine angemessenere Zielstruktur wäre zunächst:

```text
core/
├── stt_session.py                 # vorhanden, /ws/transcribe
├── controller.py                  # vorhanden, operative Wahrheit
├── server_event_stream.py         # neu, /ws/logs-Transport + Sessionbindung
├── server_event_protocol.py       # neu, Envelope und Protokollrahmen
└── feedback_models.py             # neu oder aus controller.py extrahiert

ui/
├── presentation.py                # vorhanden, reine Zustandsdarstellung
├── feedback.py                    # vorhanden, Soundausgabe erweitern
├── led.py                         # neu nach Hardware-Spike
└── server_event_model.py          # erst bei einer Eventansicht
```

Ein eigener Router ist erst nötig, wenn tatsächlich mehrere unabhängige Eventkonsumenten existieren. Für den ersten Session-Eventfeed genügen typisierte Callbacks beziehungsweise ein kleiner Dispatcher. Eine abstrakte Schicht sollte aus realem Bedarf entstehen, nicht aus der bloßen Anzahl geplanter Ansichten.

## 9. Präziser `/ws/logs`-Vertrag und Konsequenzen

### 9.1 Lebenszyklus ist an die STT-Sessiongeneration gebunden

Der Logtoken kommt aus `hello.logAccess`. Daraus folgt:

1. `/ws/transcribe` verbindet sich und liefert `hello`.
2. Der Client übernimmt `websocketPath`, `historyPath`, `accessToken`, `sessionId` und `expiresAt` nur in den Speicher.
3. Für genau diese Clientgeneration wird `/ws/logs` geöffnet.
4. Bei neuer STT-Sessiongeneration wird der alte Logstream beendet und sein Token verworfen.
5. Der neue Logstream darf den Start oder die Bereitschaft der STT-Session nicht blockieren.

Tokens werden weder in URLs noch in Clientlogs, Fehlermeldungen, YAML, SQLite oder Cursordateien geschrieben.

### 9.2 Normaler Sessionumfang

Ein Sessiontoken darf `audit`, `transcription` und `performance` der eigenen Session lesen. `system` ist nicht erlaubt.

Für den normalen Desktopbetrieb empfehle ich:

- `transcription` als standardmäßigen Eventjournal-Channel,
- `performance` nur bei aktivierter Diagnoseansicht,
- `audit` nicht standardmäßig,
- keinen Adminschlüssel im normalen Clientpfad.

Globale Serverdiagnose ist ein separates Administrationsfeature und darf nicht still in das normale Feedbacksystem hineinwachsen.

### 9.3 Replay ist tatsächlich markiert

Der Live-Endpunkt sendet jedes Replayevent als:

```json
{
  "type": "log.event",
  "event": {},
  "replay": true
}
```

Live-Events tragen `replay: false`. Zusätzlich beendet `log.replay_completed` die Replayphase. Der Client sollte beides konsistent prüfen. Ein widersprüchlicher Rahmen degradiert nur den Eventfeed, niemals die STT-Session.

### 9.4 Der Cursor ist global und gefilterte Streams sind nicht lückenlos

Der Cursor wird global vor dem Fan-out vergeben. Ein Sessionabonnement sieht aber nur ausgewählte Channels und genau eine Session. Deshalb sind Sprünge normal:

```text
empfangene Cursor: 1201, 1207, 1214
```

Das ist kein Nachweis verlorener Events. Die ausgelassenen Cursor können anderen Sessions oder Channels gehören.

Folglich ist die Regel aus dem Erstvorschlag zu korrigieren:

```text
Cursor nicht fortlaufend
    != automatisch log.gap
```

Eine Lücke gilt als bestätigt durch:

- eine explizite `log.gap`-Nachricht,
- einen Protokollbruch wie rückläufige Cursor innerhalb desselben geordneten Streams,
- oder einen fehlgeschlagenen, ausdrücklich erwarteten Replayvertrag.

### 9.5 `serverInstanceId` und Cursor haben unterschiedliche Lebenszyklen

`serverInstanceId` wird pro Serverprozess neu erzeugt. Bei aktiviertem SQLite-Store startet der Cursor dagegen am zuletzt persistierten Cursor und kann einen Prozessneustart überleben.

Deshalb darf ein Instanzwechsel den Cursor nicht blind auf null setzen. Empfohlen:

- neue Instanz plus `latestCursor >= resumeCursor`: normalen Replayversuch fortsetzen;
- `latestCursor < resumeCursor`: Store wurde zurückgesetzt oder ersetzt, Cursor für diesen Scope verwerfen und sauber neu beginnen;
- Store oder Replay deaktiviert: Eventfeed als live-only kennzeichnen.

### 9.6 Resume-Position und Event-ID

Für die aktuelle Session reichen zunächst:

- ein monotoner `resume_cursor`,
- optional ein kleiner LRU-Satz zuletzt akzeptierter `eventId`s als defensive Absicherung,
- idempotente Übernahme ins bounded Journal.

`resume_cursor` kann nach einem akzeptierten `log.event` auf dessen Cursor steigen. Nach einem gültigen `log.replay_completed` darf er auch auf dessen globalen Wasserstand steigen, obwohl der gefilterte Stream dazwischen keine eigenen Events enthalten haben muss.

Eine persistente Cursorablage ist für den normalen Sessionclient zunächst nicht nötig: Der Token ist kurzlebig, pro Session begrenzt und darf nicht mitpersistiert werden. Persistenz wird erst für ein ausdrücklich entworfenes Admin- oder Historienfeature relevant.

### 9.7 `log.gap` muss nach Ursache klassifiziert werden

Ein Subscriber-Gap kann durch Reconnect ab dem letzten sicher übernommenen Cursor häufig aus SQLite nachgeladen werden.

Ein Store-Gap kann gerade nicht aus demselben Store repariert werden. Er muss als dauerhafter Diagnoseverlust sichtbar bleiben. Ein pauschales „bei jedem Gap Replay starten und danach vollständig“ wäre falsch.

### 9.8 Es gibt kein Client-Acknowledgement

Der Server bestätigt keinen vom Client verarbeiteten Cursor. „Cursor kontrolliert bestätigen“ kann daher nur eine interne Clienttransaktion meinen.

Der Client sollte die Resume-Position aktualisieren, nachdem:

- Envelope und Scope validiert wurden,
- das Event idempotent in den bounded In-Memory-Journalzustand übernommen wurde,
- notwendige fachliche Diagnoseaggregate aktualisiert wurden.

Er darf nicht auf langsame UI-Darstellung, Sound oder LED-I/O warten. Sonst würde ein Ausgabegerät die Protokollfortschreibung blockieren.

## 10. Feedbackpolicy

### 10.1 Sounds

Sounds benötigen sprechende fachliche Namen, nicht bloß `start`, `stop` und `cancel`. Gleichzeitig sollte nicht jeder Servermeilenstein automatisch hörbar werden.

Empfohlene Policy:

| Situation | Standard | Quelle |
|---|---|---|
| Lokale Aktion registriert | optionaler sehr kurzer Aktivierungsimpuls | Hotkey/UI |
| Diktatstart serverbestätigt | vorhandener Startsound optional | bestehender Controller über `/ws/transcribe` |
| Wake Word erkannt | kurzer Bestätigungston optional | `timeline(wakeword_detected)` |
| Aufnahme beginnt | standardmäßig kein zusätzlicher Ton | `timeline(recording_started)` |
| Aufnahme endet | optionaler Stoppton | `timeline(recording_ended)` oder erfolgreicher Stopbefehl, policyabhängig |
| Finaltext verarbeitet/eingereiht | optionaler Fertigton | Client-Finalverarbeitung, nicht Logevent |
| Diktat abgebrochen/fehlgeschlagen | unterscheidbarer Warn-/Fehlerton | Controller-Impuls |

Ein nach Aufnahmebeginn abgespielter Sound kann in das Mikrofon gelangen. Deshalb sollte `recording_started` standardmäßig LED und Zustand, aber keinen weiteren Ton auslösen.

Die Soundausgabe bleibt Qt-seitig im Main Thread, solange `QSoundEffect` verwendet wird. Sie braucht keine eigene asyncio- oder Transportlogik.

### 10.2 LED

Die ReSpeaker-LED sollte nicht direkt Serverevents kennen. Ein `LedAdapter` erhält ausschließlich bereits entschiedene Instruktionen, beispielsweise:

```text
set_base_state(...)
show_impulse(...)
set_overlay(...)
clear_overlay(...)
shutdown()
```

Vor der endgültigen Architektur ist ein kleiner Hardware-Spike erforderlich:

- exaktes ReSpeaker-Modell und Windows-Treiber/API,
- Zugriffsverfahren und Lizenz,
- Blockierverhalten und Thread-Sicherheit,
- Geräteverlust und Wiederanlauf,
- Koexistenz mit Audioaufnahme,
- Verhalten bei Sleep/Wake und Prozessende.

Falls der Gerätezugriff blockieren kann, gehört er in einen begrenzten Worker innerhalb des Clientprozesses. Ein Admin-Service wird gemäß Projektregeln nicht eingeführt.

### 10.3 Overlay und Tray

Die vorhandenen Präsentationsfunktionen sollten erweitert werden. Dauerzustände kommen aus `ControllerStatusSnapshot`; kurzzeitige Hinweise aus typisierten Impulsen. Der Logtransport erhält höchstens einen separaten Diagnoseindikator und darf den gesamten Client nicht auf „nicht verbunden“ setzen.

### 10.4 Replay

Replay schreibt ausschließlich:

- Eventjournal,
- Diagnoseaggregate,
- Gap-/Vollständigkeitsstatus,
- optional historische Transkriptionschronologie.

Replay schreibt nicht:

- den aktuellen `ControllerStatusSnapshot`,
- Startbestätigung oder Diktatfenster,
- Sound- oder LED-Impulse,
- Textinjektion oder Transkripthistorie.

## 11. Eventmapping

Für den aktuellen Sessionbetrieb wird das interaktive Mapping aus `/ws/transcribe` beibehalten beziehungsweise erweitert:

| `/ws/transcribe` | Operative Bedeutung | Mögliche Wirkung |
|---|---|---|
| `timeline(wakeword_wait_started)` | Wake-Word-Wartephase | Basisdarstellung aktualisieren |
| `timeline(wakeword_wait_ended)` | Wartephase verlassen | Basisdarstellung neu ableiten |
| `timeline(wakeword_detected)` | Wake Word erkannt | optionaler Live-Impuls |
| `timeline(wakeword_timeout)` | Wake-Word-Fenster abgelaufen | optionaler dezenter Hinweis |
| `timeline(wakeword_followup_started)` | Follow-up-Fenster | zeitgebundenes Overlay |
| `timeline(wakeword_followup_timeout)` | Follow-up beendet | Overlay schließen |
| `timeline(recording_started)` | Segment nimmt auf | Phase/LED aktualisieren |
| `timeline(recording_ended)` | Segmentaufnahme beendet | Processing-/Follow-up-Phase |
| `timeline(transcription_started)` | finale Verarbeitung läuft | Diagnose/Processing |
| `final` | autoritativer Finaltext | bestehender History-/Injectionpfad |
| `status` | aktueller serverseitiger Sessionzustand | Snapshot und Startbestätigung |
| `warning`/`error` | unmittelbarer Sessionfehler | bestehende Fehlerklassifikation |

Die entsprechenden strukturierten Events werden in das Servereventjournal abgebildet, aber nicht ein zweites Mal zu interaktiven Impulsen:

```text
transcription.recording_started
transcription.recording_ended
transcription.started
transcription.completed
transcription.failed
transcription.rejected
transcription.cancelled
wakeword.wait_started
wakeword.wait_ended
wakeword.detected
wakeword.timeout
wakeword.followup_started
wakeword.followup_timeout
```

Sessionweite Wake-Word-Ereignisse können ohne `transcriptionId` und `segmentId` auftreten. Der Parser darf solche Events nicht pauschal als ungültig verwerfen.

## 12. Datenschutz und Sicherheit

### 12.1 Clientseitige Logs bleiben getrennt

`core/logging_setup.py` verwaltet Clientprozesslogs. Serverevents sind fremde strukturierte Daten und sollten nicht ungefiltert in diese lokalen Logs gespiegelt werden.

Insbesondere `transcription.completed` kann im aktuellen Liveprofil finalen Text enthalten. Deshalb gilt:

- kein automatisches Dumping ganzer Envelopes in Clientlogs,
- UI-Anzeige von Textfeldern nur nach ausdrücklicher Produktentscheidung,
- kein persistentes Servereventjournal im ersten Schritt,
- begrenzter In-Memory-Puffer,
- Redaction auch clientseitig als zweite Schutzschicht,
- Token und `hello.logAccess` niemals protokollieren.

### 12.2 Adminzugriff ist ein eigenes Sicherheitsfeature

Ein Adminschlüssel ist für Feedback der aktuellen Session nicht nötig. Eine globale Live- oder Historienansicht benötigt einen eigenen Threat Model, Credential-Manager-Integration, klare Rollen und eine ausdrückliche Freigabe.

Dieses Thema gehört nicht in das erste Feedbackpaket.

## 13. Empfohlene Arbeitspakete

Die neun Pakete des Erstvorschlags schneiden zu stark nach hypothetischen Klassen und vermischen Produktziele. Ich empfehle stattdessen folgende ergebnisorientierte Folge.

### Paket A – Vertragsübernahme und Entscheidung

Ziel:

- neuen Serververtrag in die kanonische Clientkopie übernehmen,
- Dokumentlinks und Versionsstand prüfen,
- Quellenhierarchie wieder widerspruchsfrei machen,
- diese Stellungnahme bewerten,
- eine verbindliche Architekturentscheidung als Paketvertrag oder ADR treffen.

Noch kein Produktivcode.

### Paket B – Feedbackdomäne auf vorhandener Laufzeitachse

Ziel:

- bestehende Snapshots und `TransientEvent` zu einem kleinen typisierten Impulsmodell weiterentwickeln,
- reine Feedbackpolicy definieren,
- Soundnamen und Policies erweitern,
- vorhandene Tray-/Overlaydarstellung integrieren,
- keine `/ws/logs`-Abhängigkeit.

Damit wird Benutzerfeedback zuerst auf der bereits verifizierten Quelle sauber.

### Paket C – ReSpeaker-Hardwareadapter

Ziel:

- Hardware-Spike,
- Adapter und gegebenenfalls bounded Worker,
- Geräteverlust, Shutdown, Sleep/Wake und Wiederanlauf,
- klare Fallbackdarstellung ohne LED.

Dieses Paket kann mit den bereits für AP7 geplanten Hardware- und Sleep/Wake-Prüfungen abgestimmt werden, sollte aber einen eigenen Vertrag erhalten.

### Paket D – Sessiongebundener Server-Eventfeed

Ziel:

- `hello.logAccess` sicher übernehmen,
- separaten `/ws/logs`-Lifecycle an die STT-Generation binden,
- Subscribe, Replay, Keepalive/Ping, Reconnect und Gapklassifikation,
- Envelopeparser und bounded In-Memory-Journal,
- keine interaktiven Feedbacktrigger.

Standardchannels: zunächst nur `transcription`, optional `performance` bei Diagnose.

### Paket E – Diagnoseansicht und Performance

Ziel:

- `QAbstractTableModel`,
- bounded Live-/Replayansicht,
- Filter und Vollständigkeitsstatus,
- optionale Performanceaggregate,
- klare Datenschutzdarstellung.

### Paket F – Historie und optionaler Adminmodus

Nur nach eigener Produktentscheidung:

- HTTP-Pagination,
- Abbruch und Fehlerzustände,
- Credential Manager für Adminzugriff,
- ältere Sessions und globale Channels,
- getrennte Sicherheits- und Datenschutzabnahme.

## 14. Teststrategie

### 14.1 Feedbackdomäne

- Snapshot plus Live-Impuls ergibt deterministische Sound-, Tray-, Overlay- und LED-Instruktionen.
- Replayobjekte können keine Impulse auslösen.
- verspäteter Abschluss eines alten Segments überschreibt keine neue Aufnahme.
- Sessiongeneration verhindert Wirkungen alter Events.
- deaktivierte oder fehlgeschlagene Ausgabekanäle beeinflussen den Core nicht.

### 14.2 Serverevent-Protokoll

- gültige und ungültige Envelopes,
- unbekannte zusätzliche Felder und Eventnamen,
- unbekannte Schema-Version degradiert nur den Eventfeed,
- fehlende optionale Korrelationsfelder,
- explizites `replay: true|false`,
- `log.replay_completed`, `log.keepalive`, `log.pong`, `log.error`,
- gefilterte, nicht fortlaufende Cursor werden akzeptiert,
- rückläufige Cursor werden erkannt,
- `serverInstanceId`-Wechsel mit fortgesetztem Cursor,
- Store-Reset mit `latestCursor < resumeCursor`,
- Subscriber-Gap versus Store-Gap,
- Token erscheint in keiner Logausgabe.

### 14.3 Lifecycle und Threading

- neue STT-Generation beendet den alten Logstream,
- verspätete Frames des alten Logstreams werden ignoriert,
- Logstreamausfall beeinflusst Audio, Finaltext und Injection nicht,
- Shutdown beendet WebSockets und optionale Worker idempotent,
- Qt erhält nur queued Signals und bleibt responsiv,
- volle UI-Puffer erzeugen Backpressure nur innerhalb der Diagnoseebene.

### 14.4 Integration gegen den realen Server

- `hello.logAccess` und Sessiontoken,
- Replay mit `afterCursor=0`,
- Wechsel zu Live nach `log.replay_completed`,
- paralleler Nachweis derselben Wake-/Recording-Meilensteine in Timeline und strukturiertem Eventjournal,
- Messung der relativen Ankunftszeiten, ohne daraus die operative Quellenhierarchie umzudrehen,
- Socketabbruch und Replay,
- Serverneustart mit neuer `serverInstanceId` und fortgesetztem oder zurückgesetztem Cursor,
- Konfiguration mit deaktiviertem Store beziehungsweise deaktiviertem Livezugriff.

### 14.5 Regression

Jedes Paket muss die vollständige bestehende Testsuite ausführen. Besonders zu schützen sind:

- Startbestätigung,
- Hotkey-Diktatfenster,
- Moduswechsel,
- Sessiongeneration und Reconnect,
- Finaltext-Deduplizierung,
- History und Injection,
- Qt-/asyncio-Threadgrenze,
- Headless-Diagnosepfad.

## 15. Offene Produktentscheidungen vor Implementierung

Folgende Punkte sind keine Protokollfragen und müssen bewusst entschieden werden:

1. Welche konkreten Sounds sind standardmäßig aktiv?
2. Soll ein erfolgreicher Final-/Injectionpfad hörbar bestätigt werden oder nur Aufnahmebedienung?
3. Welches ReSpeaker-Modell und welche LED-Fähigkeiten sind verbindlich?
4. Ist eine sichtbare Serverevent-Diagnoseansicht überhaupt Teil des normalen Desktopprodukts?
5. Soll `performance` standardmäßig abonniert oder nur im Diagnosemodus aktiviert werden?
6. Ist eine administrative globale Historie gewünscht oder genügt die aktuelle Session?
7. Dürfen finale Transkripttexte aus Serverevents in einer Diagnoseansicht erscheinen?
8. Wie lange soll das lokale In-Memory-Journal sein und welche Felder werden angezeigt?

Keine dieser Entscheidungen sollte implizit durch eine Transportklasse oder ein UI-Widget vorweggenommen werden.

## 16. Konkrete Bewertung der ursprünglichen Kernfragen

| Frage | Ergebnis |
|---|---|
| Ist der Envelope implementiert? | Ja, Schema-Version 1 mit den dokumentierten Pflicht- und optionalen Korrelationsfeldern. |
| Ist der Cursor global? | Ja. Gefilterte Sessionstreams besitzen deshalb normale Sprünge. |
| Wann wird der Cursor vergeben? | Vor dem unabhängigen Fan-out. Ein Sinkfehler verwendet ihn nicht erneut. |
| Ist Persistenz vor Liveversand garantiert? | Nein. Store und Publish besitzen unabhängige Queues und Worker. |
| Ist Replay markiert? | Ja, `log.event.replay` plus `log.replay_completed`. |
| Ist der Wechsel Replay -> Live lückenarm konstruiert? | Ja, der Server registriert zuerst den Live-Subscriber, erfasst den Wasserstand und replayt bis dorthin. Store-/Queueverluste bleiben dennoch möglich und werden best effort als Gap sichtbar. |
| Wie lange gilt der Sessiontoken? | 24 Stunden innerhalb des aktuellen Serverprozesses; Scope ist genau eine Session. |
| Welche Channels darf ein Sessionclient lesen? | `audit`, `transcription`, `performance`; nicht `system`. |
| Sind alle terminalen Transkriptionen vollständig? | Nein, leere finale WebSocket-Ergebnisse besitzen derzeit kein terminales strukturiertes Event. |
| Ist `/ws/logs` für primäres Echtzeitfeedback besser als Timeline? | Nein. Timeline wird im Server zuerst publiziert; der Logpfad ist zusätzlich queuebegrenzt und asynchron. |

## 17. Endgültige Empfehlung

Der Erstvorschlag sollte nicht verworfen, aber an seiner zentralen Stelle umgebaut werden.

Zu übernehmen sind:

- strukturierte statt textbasierter Auswertung,
- normalisierte interne Modelle,
- Trennung von Zustand, Impuls und Overlay,
- Replay ohne vergangene Effekte,
- bounded Eventmodelle,
- sichere Tokenbehandlung,
- getrennte Ausgabegeräteadapter,
- umfangreiche Protokoll-, Race- und Integrationstests.

Zu ändern sind:

- `/ws/logs` nicht als primäre interaktive Feedbackquelle,
- keine zweite operative Zustandsmaschine neben dem `STTController`,
- keine Gap-Erkennung aus Cursor-Sprüngen,
- kein blindes Cursorreset allein wegen neuer `serverInstanceId`,
- keine Cursorpersistenz im ersten normalen Sessionclient,
- keine Vermischung von Feedback, Hardware, Diagnose-UI und Adminhistorie,
- keine große Parallelmodulstruktur ohne realen Bedarf.

Das robuste Zielbild lautet:

```text
/ws/transcribe + lokale Clientereignisse
    -> eine operative Zustands- und Feedbackachse
    -> Tray, Overlay, Sound und ReSpeaker

/ws/logs + History-API
    -> eine getrennte, fehlertolerante Beobachtungsachse
    -> Eventjournal, Performance, Gapstatus und optionale Diagnose
```

Damit bleibt das Benutzerfeedback schnell, der bereits gehärtete Core geschützt und das neue Serversystem wird dort genutzt, wo seine besonderen Stärken tatsächlich liegen: strukturierte Korrelation, Replay, Historie und Diagnose.

## 18. Verwendete Quellen

### Client

- `AGENTS.md`
- `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`
- `docs/PROJEKTUEBERSICHT.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `ÜBERGABE.md`
- `task.md`
- `core/stt_session.py`
- `core/controller.py`
- `core/config.py`
- `ui/core_bridge.py`
- `ui/application.py`
- `ui/presentation.py`
- `ui/feedback.py`
- der Erstvorschlag vom 31. Juli 2026

### Server

- `docs/structured-logging.md`
- `docs/client-development/README.md`
- `docs/client-development/02-websocket-protokoll.md`
- `docs/client-development/06-http-api-und-authentifizierung.md`
- `docs/client-development/07-robustheit-grenzen-und-sicherheit.md`
- `docs/.archiv/neues_logging_event_system/2026-07-30_LOGGING_EVENT_SYSTEM.md`
- `docs/.archiv/neues_logging_event_system/2026-08-01_logging-projekt-live-stand.md`
- `docs/.archiv/neues_logging_event_system/2026-08-01_NEUES_LOGGING_EVENT_SYSTEM_ABWEICHUNGEN.md`
- zur Detailverifikation `VoiceSTT_server/event_logging.py` und `api_fastapi_server/server.py`
