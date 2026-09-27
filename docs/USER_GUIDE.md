# Voice-STT Client 1.0 – Anwenderhandbuch

## Installation und erster Start

Die Windows-EXE benötigt keine Python-Installation. Starte sie einmal; danach
erscheint das Voice-STT-Symbol im Infobereich der Taskleiste. Über
**Einstellungen** werden Verbindung, Betriebsmodus, Mikrofon, Hotkeys und
Feedback geändert.

Für einen Start aus dem Checkout:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m voice_stt_client
```

Der Diagnosemodus läuft mit `python -m voice_stt_client --headless`. Eine
alternative YAML-Datei wird mit
`python -m voice_stt_client --config C:\Pfad\client.yaml` geladen. Nach einer
PyPI-Installation steht zusätzlich der Befehl `voice-stt-client` mit denselben
Optionen zur Verfügung.

## Bedienung

Standardmäßig startet `Ctrl+Shift+Space` ein Hotkey-Diktat und verlängert bei
erneutem Drücken dessen Zeitfenster. `Ctrl+Alt+Space` fügt das letzte finale
Transkript erneut ein. Im Einstellungsdialog werden Hotkeys direkt als
Tastenkombination aufgenommen; optionale Belegungen lassen sich leeren.

Kann Windows eine gespeicherte Kombination nicht registrieren, prüft der
Client beim Start ungewöhnlichere Alternativen. Nur eine erfolgreich
registrierte Kombination wird übernommen und gespeichert; eine Tray-Sitzung
ohne funktionierenden Hotkey wird nicht gestartet. Im Dialog schlägt
**Generieren** eine aktuell freie Kombination vor; **Übernehmen** registriert
sie verbindlich. Scheitert das, erscheint ein verständlicher Grund und das
Feld zeigt wieder die bisher aktive Kombination. **Schließen** ohne
**Übernehmen** verwirft einen noch nicht gespeicherten Vorschlag; beim
erneuten Öffnen steht wieder der tatsächlich aktive Wert im Feld.

Im Wake-Word-Modus schaltet der primäre Hotkey das serverseitige Warten ein
oder aus. Das Standard-Wakeword ist `hey_jarvis`. Realtime-Text erscheint nur
im Overlay; ausschließlich finale Texte werden in die aktive Anwendung
eingefügt.

## Verbindung und API

Der Desktop-Client verwendet den WebSocket-Endpunkt `/ws/transcribe`. Die
vollständige URL steht unter `server.url`, die HTTP-Prüfadresse unter
`server.health_url`. `ws://` ist für lokale unverschlüsselte Tests geeignet;
über ein Netzwerk sollte `wss://` verwendet werden.

Der Client handelt Sessionkonfiguration und einen sitzungsgebundenen
Logzugriff im `hello`-Handshake aus. Ein Admin-Key gehört nicht in den
Desktop-Client. Falls der Server einen Client-API-Key verlangt, wird dieser
derzeit nicht als allgemeines YAML-Feld gespeichert; Zugangsdaten dürfen nicht
in Logs oder Screenshots kopiert werden.

## Dateien und Logs

Der gemeinsame Standardordner ist:

```text
%USERPROFILE%\.voice-stt\client\
├── config.yaml
├── data\transcript_history.db
└── logs\client.log
```

`VOICESTT_CLIENT_HOME` verschiebt den gesamten Ordner,
`VOICESTT_CLIENT_CONFIG` nur die Benutzerkonfiguration. `logging.log_dir` und
`history.persistent.db_path` überschreiben die jeweiligen Einzelpfade.
Vorhandene Konfiguration und Historie an den alten LocalAppData-Pfaden werden
weiterverwendet, solange am neuen Ort noch keine Datei besteht.
Auch eine mit `--config` ausgewählte Datei ergänzt nur die mitgelieferten
Defaults; der Einstellungsdialog schreibt Änderungen in diese ausgewählte
Datei zurück. Bei einer normalen Installation ist kein Flag nötig.

Logs sind standardmäßig rotierende JSON-Zeilen. Für Supportfälle sind der
Zeitpunkt, die Clientversion, die Server-URL ohne Secrets und der relevante
Logausschnitt hilfreich.

## Häufige Fallstricke

| Symptom | Prüfung |
| --- | --- |
| Hotkey reagiert nicht | Den im Dialog angezeigten aktiven Hotkey prüfen. Bei Konflikten **Generieren** und danach **Übernehmen** nutzen; ohne registrierbare Kombination startet der Tray-Client nicht. |
| Windows-Taste im Hotkey | Qt zeigt diese Taste im Eingabefeld als `Meta` an; in der Konfigurationsdatei heißt sie `Win`. Beides bezeichnet dieselbe Taste. |
| Verbunden, aber kein Text | Richtiges Mikrofon wählen und den 3-Sekunden-Test ausführen. |
| Browser funktioniert, Desktop nicht | Desktop braucht `/ws/transcribe`, nicht die HTTP-Startseite oder `/health`. |
| Wakeword reagiert nicht | Modus `wake_word`, veröffentlichte Modell-ID und bestätigte `hello.sessionConfig` prüfen. |
| Text erscheint im falschen Fenster | Nach dem Start des Diktats das Zielfenster fokussieren; erhöhte Anwendungen können erhöhte Clientrechte erfordern. |
| Einstellungen scheinen ignoriert | Prüfen, ob `--config` oder `VOICESTT_CLIENT_CONFIG` gesetzt ist und welche Datei dadurch ausgewählt wurde. Der Dialog speichert an diesen Pfad. |
| Kein ReSpeaker/LED-Ring | Die Diktierfunktion bleibt nutzbar; LED-Ausgabe ist optional und fällt auf den Nulladapter zurück. |
| LED sehr dunkel | Im Dialog unter **Erscheinungsbild & Feedback** prüfen, ob ReSpeaker-LED aktiviert und die Helligkeit ausreichend hoch ist; ein alter Benutzerwert übersteuert den mitgelieferten Default. Die Mute-Taste am Gerät kann den Ring hardwareseitig ausschalten. |
| Keine Feedback-Töne | Im selben Dialog **Sounds** aktivieren und die angezeigten Dateipfade prüfen. Ein Logeintrag zur Sound-Entscheidung allein beweist keine hörbare Wiedergabe, solange Sounds deaktiviert sind. |

Die vollständige Feldreferenz steht in [CONFIGURATION.md](CONFIGURATION.md).
