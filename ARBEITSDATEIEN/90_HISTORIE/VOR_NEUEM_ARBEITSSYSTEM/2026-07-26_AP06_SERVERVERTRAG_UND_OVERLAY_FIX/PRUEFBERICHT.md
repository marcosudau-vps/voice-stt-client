# AP06 – Overlay-Fix und Prüfung des neuen Session-Wake-Word-Vertrags

> **Datum:** 26. Juli 2026  
> **Status:** Overlayfehler behoben; Serververtrag live verifiziert;
> Clientintegration fachlich noch nicht festgelegt

## 1. Anlass

Im laufenden GUI-Betrieb trat wiederholt folgender Fehler auf:

```text
TypeError: QLabel.setText(int)
```

Parallel wurde auf dem produktiven Server ein neuer versionierter
Session-Create-Contract für Hotkey- und Wake-Word-Betrieb bereitgestellt.
Dieser Bericht trennt deshalb:

1. den unmittelbar behobenen Clientfehler,
2. die nachgewiesenen Eigenschaften des neuen Serververtrags,
3. die noch nicht entschiedene Einbindung in AP06.

## 2. Overlayfehler

### Ursache

Der Controller- und Bridgevertrag liefert Text als:

```text
(segment_id: int, text: str, is_final: bool)
```

`TranscriptOverlay.show_transcript()` erwartet dagegen:

```text
(text: str, is_final: bool)
```

Die Qt-Signalverbindung war direkt hergestellt worden. Dadurch erhielt das
Overlay die Segment-ID als `text` und reichte eine Ganzzahl an
`QLabel.setText()` weiter.

### Korrektur

`DesktopApplication` besitzt nun einen expliziten, typisierten Adapter:

```text
CoreBridge.text_received(segment_id, text, is_final)
  -> DesktopApplication._on_text_received(...)
  -> TranscriptOverlay.show_transcript(text, is_final)
```

Die Segment-ID wird an dieser reinen Darstellungsgrenze bewusst nicht
verwendet.

### Regressionstest

Ein neuer Integrationstest emittiert die reale dreiteilige Bridge-Payload und
prüft, dass ausschließlich der Text im Overlay landet. Damit ist genau die
zuvor fehlende Verdrahtungsgrenze abgedeckt.

## 3. Verbindlicher neuer Serververtrag

Die aktuelle Serverdokumentation wurde aus
`P:\DockerProjekte\voice-stt-server\docs\client-development\` nach
`server-docs-for-client-development/` synchronisiert. Die ausführliche
Erweiterungsbeschreibung liegt nun zusätzlich unter
`server-docs-for-client-development/session-wakeword-erweiterung.md`.

Contract-Version: **1**  
Server-API-Version: **2.0.0**

Der WebSocket-Aufbau unterstützt:

| Queryparameter | Zweck |
| --- | --- |
| `wakeWordEnabled=false` | Wake Word nur für diese Session deaktivieren |
| `wakeWordEnabled=true` | Wake Word nur für diese Session aktivieren |
| fehlend/`null`/`inherit` | Serverbaseline übernehmen |
| `wakeWords` | logische, kommaseparierte Modell-IDs |
| `wakeWordBackend` | derzeit `openwakeword` |
| `wakeWordInferenceFramework` | `onnx` oder `tflite` |
| `wakeWordSensitivity` | Erkennungsschwelle |
| `wakeWordActivationDelay` | Aktivierungsverzögerung |
| `wakeWordTimeout` | Sprachzeitfenster nach Erkennung |
| `wakeWordBufferDuration` | Wake-Word-Puffer |
| `wakeWordFollowupWindow` | Follow-up-Zeitfenster |

Die globale Serverbaseline und andere Sessions werden dabei nicht verändert.

## 4. Maßgebliche Bestätigung

Die angeforderte URL allein ist nicht autoritativ. Maßgeblich sind:

- `hello.sessionConfig`,
- `ready.sessionConfig`,
- `sessionCapabilities`.

Geprüft werden müssen mindestens:

- Contract-Version,
- `requestedWakeWordEnabled`,
- `effectiveWakeWordEnabled`,
- `effectiveWakeWordBackend`,
- `effectiveWakeWords`,
- `fallbacks`,
- `ignoredFields`,
- `warnings`.

`hello.sessionConfig` und `ready.sessionConfig` waren in allen erfolgreichen
Live-Prüfungen identisch.

## 5. Live-Prüfungen gegen den produktiven Server

Ziel:

```text
https://stt.voice.marcosudau.com
wss://stt.voice.marcosudau.com/ws/transcribe
```

### 5.1 HTTP- und WebSocket-Feature-Nachweis

Ergebnis:

```text
ApiVersion:               2.0.0
SessionContractVersion:   1
WakeWordSessionContract:  True
OpenWakeWordAdvertised:   True
WebSocketHandshake:       passed
```

Eine Session mit `wakeWordEnabled=false` und absichtlich zusätzlichem
`wakeWords` bestätigte:

- angefordert: `false`,
- effektiv: `false`,
- `wakeWords` korrekt in `ignoredFields`.

### 5.2 Parallele Sessionisolation

Gleichzeitig geöffnet wurden:

1. Hotkey-Session mit `wakeWordEnabled=false`,
2. Wake-Word-Session mit `wakeWordEnabled=true`,
   `wakeWords=hey_jarvis`, Sensitivität `0.42` und Follow-up `3`.

Beide Sessions erhielten unterschiedliche Session-IDs und gleichzeitig die
jeweils angeforderte effektive Konfiguration.

Ergebnis: **Isolation bestanden.**

### 5.3 Startbestätigung

Nach `{"type":"start"}` traf unmittelbar ein sessionspezifisches
`status`-Event ein:

- Hotkey-Session: `listening`,
- Wake-Word-Session: `wakeword_wait`.

Der Status enthält unter anderem:

- `sessionId`,
- `state`,
- `wakeWordEnabled`,
- `wakeWord`.

Präzisierung: Es existiert weiterhin **kein separates Ack mit Request-ID**.
Die unmittelbare Bestätigung erfolgt über das Statusereignis. Die vollständige
effektive Sessionkonfiguration steht in `hello.sessionConfig` und
`ready.sessionConfig`; der Status enthält die für den laufenden Modus relevante
Wake-Zusammenfassung.

### 5.3.1 Auffälliger Vor-Start-Status

Bei wiederholten Hotkey-Session-Prüfungen traf bereits vor `start` ein
Status mit folgenden Werten ein:

```text
state=voice
activeClientId=null
wakeWordEnabled=false
```

Unmittelbar nach `start` folgte korrekt:

```text
state=listening
activeClientId=<eigene sessionId>
wakeWordEnabled=false
```

Die gemessene Bestätigungslatenz lag unterhalb der Zeitauflösung des
Testskripts. Der Vor-Start-Status ist dennoch semantisch auffällig: Eine neue,
noch nicht streamende Session wäre gemäß Dokumentation typischerweise `idle`.
Ein Client darf deshalb nicht allein `state=voice` als Startbestätigung
behandeln, sondern sollte für den neuen Serververtrag zusätzlich prüfen, dass
`activeClientId` der eigenen `sessionId` entspricht.

Der aktuelle Controller bindet Bestätigungen bereits an Session-ID,
Generation und einen laufenden Startversuch, prüft `activeClientId` aber noch
nicht. Dieser Punkt gehört in die anstehende Contract-Integration
beziehungsweise sollte serverseitig darauf geprüft werden, weshalb vor
`start` überhaupt `voice` gemeldet wird.

### 5.4 Fallbacks und Warnungen

Nachgewiesen:

- ungültiges `wakeWordEnabled=flase` erbt sichtbar die Baseline,
- ungültiges Backend mit gültigem `hey_jarvis` fällt sichtbar auf
  OpenWakeWord zurück,
- Sensitivität außerhalb des Wertebereichs mit gültigem Modell fällt sichtbar
  auf den Serverwert zurück,
- `fallbacks` und `warnings` enthalten maschinenlesbare Angaben.

### 5.5 Harte Konfigurationsfehler

Nachgewiesen:

- doppelt übergebenes `wakeWordEnabled`:
  `error.where=session_config`, Close-Code `1008`,
- unbekanntes Modell ohne verfügbares Fallbackprofil:
  `error.where=session_config`, Close-Code `1008`,
- Aktivierung ohne auflösbares Baseline-/Standardmodell:
  `error.where=session_config`, Close-Code `1008`.

Ein Client darf diese deterministischen Fehler nicht mit einer schnellen
Endlos-Reconnectschleife beantworten.

### 5.6 Aktuelle Clientkompatibilität

Die produktive `STTSession` des Desktop-Clients wurde jeweils bis `READY`
geprüft mit:

```text
?wakeWordEnabled=false
?wakeWordEnabled=true&wakeWords=hey_jarvis
```

Beide Verbindungen waren erfolgreich. Zusätzliche Handshakefelder werden
toleriert, und `hello.sessionConfig` stimmte mit `ready.sessionConfig`
überein.

Der vorhandene allgemeine Connection-Test bestand ebenfalls:

```text
health -> hello -> ready -> pong
ALL TESTS PASSED
```

## 6. Noch bestehende Clientlücken

Der aktuelle Client:

- erzeugt noch keine Session-Queryparameter aus einer Moduskonfiguration,
- persistiert noch keinen gewünschten Hotkey-/Wake-Word-Modus,
- wertet `sessionConfig`, `sessionCapabilities`, Fallbacks und Warnungen noch
  nicht fachlich aus,
- besitzt noch keine UI für Modus, Wake-Word-ID oder Tuningwerte,
- behandelt `error.where=session_config` noch nicht als eigenen
  deterministischen Konfigurationszustand,
- bezieht `activeClientId` noch nicht in die Startbestätigung ein.

Diese Punkte wurden bewusst noch nicht implementiert. Ihr Umfang wird in der
nachgeholten AP06-Scopebesprechung festgelegt.

## 7. Automatisierte Clientverifikation

Gezielte UI-Tests:

```text
Ran 25 tests
OK
```

Vollständige Suite:

```text
Ran 239 tests in 6.726s
OK
```

`py_compile` über `app.py` sowie sämtliche Python-Dateien unter `core/`, `ui/`
und `tests/` war erfolgreich.

Die während der Suite ausgegebenen Fehlerlogs sind absichtlich simulierte
Negativpfade.

## 8. Fazit

- Der Overlayfehler ist behoben und regressionsgesichert.
- Der neue Session-Wake-Word-Contract ist auf dem produktiven Server aktiv.
- Hotkey- und Wake-Word-Sessions sind parallel isoliert nutzbar.
- Effektive Werte, Fallbacks und harte Fehler sind für einen robusten Client
  ausreichend sichtbar.
- Der vorhandene Transport ist mit dem erweiterten Handshake kompatibel.
- Die eigentliche Produkt- und UI-Integration bleibt bis zur AP06-Abstimmung
  offen.
