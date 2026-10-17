# Tatsächliche Sounds, LED-Effekte und Auslöser

Stand 18.10.2026, Produktkandidat7bb5646 mit UX03-Korrektur; isoliertes
`client-both.yaml`. Keine Wiedergabe aller Sounds durch das Erstellen dieser
Übersicht. Tabelle beschreibt die wirksame Code-/Konfigurationszuordnung;
nicht jede Zeile ist bereits als reale menschliche Wahrnehmung qualifiziert.

## Wirksamer V2-Diktierablauf

| Auslöser / Zustand | Sound | LED-Ausgabe |
| --- | --- | --- |
| Bereit, keine aktive Eingabe (`idle`) | Keiner | `ready_state`: grün `#00C066`, sanftes Atmen |
| Server bestätigt neue Aktivierung, Hotkey oder Wakeword (`activation.started`) | `wake_word.wav`, ca.800ms | `wakeword_detected`: cyan `#00D0D0`, ca.300ms Impuls; anschließend Wartezustand |
| Auf erste Sprache warten (`waiting_first_speech`) | Kein zusätzlicher Ton | `waiting`: langsam umlaufender cyanfarbener Punkt |
| Sprachsegment beginnt (`segment.recording_started`, Vordergrund `segment_active`) | `start.wav`, ca.900ms | `listening`: cyanfarbener, atmender Ring |
| Sprachsegment endet (`segment.recording_ended`) | `stop.wav`, ca.661ms | Daueranzeige folgt der Serverphase; kein zusätzlich erzwungener Thinking-Zustand aus diesem Impuls |
| Auf weiteren Satz warten (`followup_wait`, aktuell5s) | Keiner | `waiting`: cyanfarbener umlaufender Punkt |
| Eingabe wird geschlossen (`closing_input`) | Keiner allein durch die Phase | `thinking`: violetter Sweep `#8000FF` |
| Eingabe serverbestätigt geschlossen (`activation.input_closed`, `finished` oder `timed_out`) | **`stop.wav`, ca.661ms; UX03** | Dauerzustand wieder nach aktuellem Vordergrund, normalerweise grün/bereit; kein eigener LED-Impuls |
| Finaltranskript erstmals verfügbar (`transcription.completed`) | `complete.wav`, ca.2300ms | `success_event`: grüner Erfolgsimpuls, hier700ms |
| Segment verworfen (`transcription.discarded`) | `cancel.wav`, ca.1343ms | `reject_event`: Ablehnungssignal, Standard460ms |
| Aktivierung abgebrochen (`activation.cancelled`) | `cancel.wav`, ca.1343ms | `reject_event`, Standard460ms |
| Transkription oder Aktivierung fehlgeschlagen | `error.wav`, ca.2000ms | `error_event`: rote Pulsfolge, hier1200ms |
| Server weist manuellen Trigger zurück (`activation.trigger_suppressed`) | `warning.wav`, ca.1315ms | `warn_event`: gelbe Warnpulse, Standard1000ms |
| Daueraufnahme-Watchdog warnt (`watchdog.warning`) | `timeout_tick.wav`, einmal ca.3000ms, Mappinglautstärke0,85 | `countdown_ring`: abnehmender Ring, grün→gelb→rot; Dauer aus serverseitigem `remainingMs` |
| Verbindung/Spiegel nicht bereit, Audio weiter verfügbar | Kein zusätzlicher Ton aus der Zustandsprojektion | `reconnect_network_state`: gelber/dunkelgelber atmender Ring |
| Audio nicht verfügbar (auch beim Verbindungsaufbau möglich) | Kein zusätzlicher Ton aus der Zustandsprojektion | `reconnect_mic_state`: orange/dunkelorange atmender Ring |
| Mikrofon stummgeschaltet, per Gerät oder Tray | Kein eigener Ton | Animierter Ring aus; separate Hardware-Mute-LED, sofern Gerät erreichbar |

Reguläre Mappinglautstärke der übrigen ausgegebenen Sounds:1,0, also100% des
jeweiligen WAV-Pegels vor Windows-/Gerätelautstärke. Das ist kein gemessener
Schalldruck. LED-Ausgabe: ReSpeaker, globale Helligkeit192/255,30FPS; zusätzlich
besitzen die Effekte eigene Helligkeitsparameter.

## Wichtige Abgrenzungen

- `wakeword.detected` selbst ist V2-Quelldiagnose. Der gemeinsame Startimpuls
  entsteht bereits aus `activation.started`; deshalb kein zweiter Startton.
- Phasenprojektionen übernehmen nur dauerhafte LED-/App-Zustände, keine Sounds
  und keine Eventimpulse. Die YAML-Regel für `idle` enthält z.B. einen Cancelton,
  er wird beim bloßen Wechsel auf idle **nicht** abgespielt.
- `activation.completed` ist kein erfolgreicher Finaltext. Es spielt keinen
  zusätzlichen Complete-Sound, auch wenn es vor `activation.input_closed` kommt.
- Segmentende und Eingabeschluss sind unterschiedliche Grenzen. Mit Nutzsprache
  kann der vorhandene Stoppton daher am Segmentende und später am Ende des
  Nachsprechfensters auftreten. Die UX03-Korrektur dedupliziert den Eingabeschluss,
  entfernt aber kein bisheriges Segmentfeedback.
- Ein später Final von Aktivierung A darf einen Erfolgsimpuls/Ton erzeugen,
  während B aufnimmt. B bleibt dabei Vordergrund; sein dauerhafter LED-Zustand
  wird nicht auf Bereit umgeschaltet.
- Snapshot/Logreplay erzeugt keine neuen Sounds. Alte Generationen und ein
  verspätetes Close von A beenden nicht akustisch die laufende Eingabe B.
- Bei ausgeschalteten Sounds oder leerem Soundpfad bleibt die betreffende
  Ausgabe stumm. Fehlendes Gerät oder Asset bleibt eine Diagnose, kein PASS.

## Nur deklarierte oder diagnostische Regeln

Diese Regeln stehen im Profil/YAML, werden vom aktuellen V2-Domainpfad aber
nicht als eigene akustische/LED-Impulse ausgeführt. Sie sind daher keine
zugesicherte Ausgabe in der laufenden Instanz.

| Deklarierter Trigger | Sound laut YAML | LED laut YAML | Tatsächliche V2-Einordnung |
| --- | --- | --- | --- |
| `client.lifecycle.started` | start | `init_event`, dann ready | Lokales Lifecycle-Feedback löst keinen eigenen Impuls aus; Grundzustand kommt über Snapshot |
| `client.lifecycle.stopping` | keiner | primary löschen | Kein eigener Lifecycle-Impuls; echter Shutdown baut den LED-Worker ab |
| `client.transport.disconnected` | warning | reconnect_network_state | Dauer-LED über Spiegelprojektion, kein eigener Warnton |
| `client.microphone.lost` | warning | reconnect_mic_state | Dauer-LED über Audioverfügbarkeit, kein eigener Warnton |
| `client.microphone.recovered` | complete | success_event, dann ready | Zustand wird neu projiziert, kein eigener Erfolgston/-impuls |
| `client.injection.accepted` | keiner | init_event | Keine eigene Impulsausgabe |
| `client.injection.succeeded` | keiner | success_event | Keine eigene Impulsausgabe; Finaltranskript hat getrenntes Erfolgsfeedback |
| `client.injection.failed` | error | error_event | Sekundärer Diagnosehinweis, kein zusätzlicher Warnton/Fehlerimpuls |
| `client.dictation.interrupted` | warning | warn_event, dann ready | Kein eigener V2-Normalisierungspfad; serverseitiges Cancel/Failed bleibt maßgeblich |
| `client.dictation.timeout_warning_cleared` | timeout_tick stoppen | schwarzes1ms-Countdownoverlay | Deklariert, derzeit kein eigener V2-Aufrufpfad |
| `client.tts.started` / `.stopped` / `.failed` | start/stop mit0,8, bzw.error | speaking/ready/error_event | Kein ausführbarer TTS-Lifecycle in diesem V2-Domainpfad |
| `client.led.unavailable` | warning | keiner | Sekundärer Diagnosehinweis; keine akustische Warnschleife |
| `client.sound.failed` | keiner | keiner | Sekundärer Diagnosehinweis |
| `client.configuration.invalid` | keiner | error_event | Blockierender Konfigurationsstatus; kein eigener Mappingimpuls |
| Eventstream connecting/replaying/live/degraded | keiner | keiner | Diagnostisch; verändert keinen Diktier-Lifecycle |
| `server.transcription.rejected` | error | reject_event | Kein entsprechendes V2-Wireevent; vorhandene Failed-/Discardevents sind maßgeblich |

## Konfiguration

Sounddateien, Soundschalter und LED-Helligkeit: V2-Einstellungen →
**Lokale Trigger & Bedienung** → **Lokale Geräte, Verlauf, Zwischenablage,
Darstellung und Diagnose …** → **Erscheinungsbild & Feedback** → Sound bzw.LED.

Die Ereigniszuordnungen stehen unter `feedback_mappings.events` in der
ausgewählten Benutzer-YAML. Sie besitzen derzeit keinen vollständigen
Mappingeditor. Für den neuen Eingabeschluss kann eine explizite Regel
`server.input.closed` gesetzt werden; ansonsten übernimmt die Migration nur
Sound/Lautstärke der vorhandenen `server.recording.ended`-Regel. Eine ausdrücklich
leere neue Regel schaltet ausschließlich dieses Abschlussfeedback stumm.

Quellen: `core/event_normalizer.py`, `core/feedback_reducer.py`,
`core/v2_feedback.py`, `ui/feedback.py`, aktive Profil-YAML und tatsächlich
installierter LEFX-Smartspeaker-Katalog. Sounddauern aus den WAV-Headern gelesen.
