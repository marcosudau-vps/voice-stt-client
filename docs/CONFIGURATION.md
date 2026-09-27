# Client-Konfigurationsreferenz

## Priorität und Speicherorte

Ohne `--config` lädt der Client zuerst die im Paket beziehungsweise in der EXE
mitgelieferte `voice_stt_client/config.yaml` und legt darüber die
Benutzerdatei `~/.voice-stt/client/config.yaml`. Existiert sie
nicht, wird einmalig kompatibel am alten Windows-Pfad
`%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` gesucht. Der
Einstellungsdialog speichert immer am neuen Standardpfad.

Mit `--config DATEI` wird diese Datei **über die mitgelieferten Defaults**
gelegt; fehlende Felder behalten also die Standardwerte. Der Dialog speichert
danach wieder in genau diese Datei. Eine ausdrücklich benannte, fehlende oder
ungültige YAML-Datei führt zum Startfehler. Unbekannte Felder werden im Log
benannt, die übrigen gültigen Einstellungen bleiben wirksam.

Ältere, automatisch gespeicherte Konfigurationen mit acht leeren (`null`)
Soundpfaden übernehmen wieder die mitgelieferten Dateipfade. Der bisherige
Ein-/Auszustand von `feedback.sounds_enabled` bleibt dabei erhalten.

## Environment und CLI

| Name | Bedeutung |
| --- | --- |
| `VOICESTT_CLIENT_HOME` | Basisordner für Config, Logs und Daten; Standard `~/.voice-stt/client`. |
| `VOICESTT_CLIENT_CONFIG` | Pfad der Benutzer-YAML; Standard `<HOME>/.voice-stt/client/config.yaml`. |
| `--config PATH` | Überlagert die Paketdefaults mit dieser YAML-Datei; der Dialog speichert an denselben Pfad. |
| `--headless` | Diagnosebetrieb ohne Tray-/Qt-Oberfläche. |
| `--version` | Gibt die Clientversion aus und beendet sich. |

## Verbindung und Eventstream

| Feld | Auslieferungswert | Bedeutung |
| --- | --- | --- |
| `server.url` | produktives `wss://…/ws/transcribe` | STT-WebSocket. |
| `server.health_url` | produktives `https://…/health` | HTTP-Healthcheck. |
| `server.reconnect_min_delay` / `reconnect_max_delay` | `0.5` / `30.0` s | Reconnect-Grenzen. |
| `server.reconnect_jitter` | `0.3` | Zufälliger Backoff-Anteil, 0 bis kleiner 1. |
| `server.server_busy_min_delay` | `10.0` s | Mindestpause bei ausgelastetem Server. |
| `server.ping_interval` / `ping_timeout_count` | `10.0` / `3` | Keepalive-Intervall und erlaubte Ausfälle. |
| `server.start_confirmation_timeout` | `10.0` s | Frist für Startbestätigung. |
| `server.hello_timeout` / `ready_timeout` | `5.0` / `180.0` s | Handshake- und Bereitschaftsfrist. |
| `event_stream.enabled` | `true` | Sitzungsgebundenen `/ws/logs`-Stream verwenden. |
| `event_stream.connect_timeout` / `handshake_timeout` | `10.0` / `10.0` s | Aufbau- und Handshakefrist. |
| `event_stream.replay_timeout` / `message_timeout` | `60.0` / `30.0` s | Replay- und Nachrichtenfrist. |
| `event_stream.reconnect_min_delay` / `reconnect_max_delay` | `0.5` / `30.0` s | Eventstream-Reconnect-Grenzen. |
| `event_stream.reconnect_jitter` | `0.3` | Zufälliger Backoff-Anteil. |
| `event_stream.max_message_size` | `1048576` Byte | Maximale WebSocket-Nachricht. |
| `event_stream.queue_maxsize` | `512` | Lokale Eventqueue-Grenze. |
| `event_stream.cursor_persistence_enabled` | `true` | Replay-Cursor dauerhaft speichern. |
| `event_stream.cursor_path` | leer | Optionaler eigener Cursorpfad. |

## Session, Mikrofon und Diktierfenster

| Feld | Auslieferungswert | Bedeutung |
| --- | --- | --- |
| `session.mode` | `hotkey` | `hotkey` oder `wake_word`. |
| `session.wake_word_backend` | leer | Optionaler serverseitiger Backendwunsch. |
| `session.wake_words` | `hey_jarvis` | Kommagetrennte logische Modell-IDs. |
| `session.wake_word_inference_framework` | leer | Optional `onnx` oder `tflite`. |
| `session.wake_word_sensitivity` | leer | Optional 0 bis 1. |
| `session.wake_word_activation_delay` | leer | Optionale Serververzögerung. |
| `session.wake_word_timeout` | leer | Optionale Serverfrist nach Erkennung. |
| `session.wake_word_buffer_duration` | leer | Optionale Wakeword-Pufferdauer. |
| `session.wake_word_followup_window` | leer | Optionales Nachsprechfenster. |
| `dictation_window.initial_speech_timeout` | `15.0` s | Zeit bis zur ersten Sprache. |
| `dictation_window.followup_timeout` | `3.0` s | Zeit für einen weiteren Sprachabschnitt. |
| `dictation_window.extension_seconds` | `15.0` s | Verlängerung durch erneuten Hotkey. |
| `dictation_window.timeout_warning_seconds` | `3.0` s | Vorwarnung vor Ablauf. |
| `audio.device` | `null` | Eingabegeräteindex; leer nutzt Systemstandard. |
| `audio.sample_rate` / `channels` | `16000` / `1` | PCM-Samplerate und Kanäle. |
| `audio.chunk_duration_ms` | `40` | Capture-Blockdauer. |
| `audio.dtype` | `int16` | PCM-Datentyp. |

## Hotkeys, Text und Zwischenablage

| Feld | Auslieferungswert | Bedeutung |
| --- | --- | --- |
| `hotkey.enabled` | `true` | Für den Tray-Client erforderlich; ohne registrierbaren Hotkey startet er nicht. |
| `hotkey.mode` | `actions` | Aktuelles Aktionsschema. |
| `hotkey.toggle_key` | `Ctrl+Shift+Space` | Primäre Diktataktion. |
| `hotkey.reinsert_last_key` | `Ctrl+Alt+Space` | Letzten Finaltext einfügen. |
| `hotkey.finish_key` / `cancel_key` | leer | Optionale Abschluss-/Abbruchbelegung. |
| `hotkey.overlay_toggle_key` | leer | Optional Overlay umschalten. |
| `hotkey.auto_start` | `false` | Diktat beim Start automatisch anfordern. |
| `text_injection.final_strategy` | `clipboard` | Finale Textinjektionsstrategie. |
| `text_injection.paste_delay_ms` | `50` | Pause vor dem Einfügen. |
| `text_injection.append_space` | `true` | Leerzeichen an Finaltext anhängen. |
| `text_injection.warn_elevated` | `true` | Bei Integritäts-/Rechteproblem warnen. |
| `clipboard.restore_previous` | `false` | Vorherigen Clipboardinhalt wiederherstellen. |
| `clipboard.restore_delay_ms` | `300` | Wartezeit vor Wiederherstellung. |
| `clipboard.backup_max_bytes` | `1048576` | Größenlimit für Clipboardbackup. |
| `clipboard.open_retries` / `open_retry_delay_ms` | `5` / `20` | Öffnungsversuche und Pause. |

`hotkey.key` ist nur ein eingelesener Legacy-Alias und wird beim Speichern in
`hotkey.toggle_key` migriert.

## Overlay, Historie und Logging

| Feld | Auslieferungswert | Bedeutung |
| --- | --- | --- |
| `overlay.enabled` / `show_realtime_text` | `true` / `true` | Overlay und Zwischentext. |
| `overlay.position` | `bottom_center` | Bildschirmposition. |
| `overlay.width` / `max_height` | `600` / `100` px | Abmessungen. |
| `overlay.opacity` / `fade_after` | `0.85` / `2.0` s | Deckkraft und Ausblendfrist. |
| `overlay.font_size` / `font_family` | `14` / leer | Schrift. |
| `overlay.background_color` / `text_color` | `#20242a` / `#ffffff` | Farben als `#RRGGBB`. |
| `overlay.margin` | `60` px | Bildschirmrand. |
| `history.enabled` | `true` | Verlauf führen. |
| `history.memory.max_entries` | `5` | RAM-Einträge. |
| `history.persistent.enabled` | `true` | SQLite-Verlauf aktivieren. |
| `history.persistent.max_entries` | `100` | SQLite-Anzahlgrenze; 0 unbegrenzt. |
| `history.persistent.retention_days` | `0` | Altersgrenze; 0 unbegrenzt. |
| `history.persistent.min_characters` | `1000` | Mindestlänge für reguläre Speicherung. |
| `history.persistent.store_failed_injections` | `true` | Fehlgeschlagene Einfügungen speichern. |
| `history.persistent.store_all` | `false` | Alle Finaltexte unabhängig von Mindestlänge speichern. |
| `history.persistent.db_path` | leer | Eigene SQLite-Datei. |
| `logging.level` | `INFO` | `DEBUG`, `INFO`, `WARNING` oder `ERROR`. |
| `logging.log_dir` | `~/.voice-stt/client/logs` | Logordner; kann in Benutzer-YAML ergänzt werden. |
| `logging.max_bytes` / `backup_count` | `5242880` / `3` | Rotation pro Datei und Backups. |
| `logging.stdout` / `json_format` | `true` / `true` | Konsolenausgabe und JSONL-Dateiformat. |
| `logging.channel_levels` | `{}` | Optionale Loglevel je Kanal. |

## Sound, LED und Feedback-Mapping

| Feld | Bedeutung |
| --- | --- |
| `feedback.sounds_enabled` | Sämtliche Sound-Cues ein-/ausschalten. |
| `feedback.wake_word_sound`, `start_sound`, `stop_sound`, `complete_sound` | Audiodateien für den normalen Ablauf. |
| `feedback.cancel_sound`, `warning_sound`, `error_sound`, `timeout_tick_sound` | Audiodateien für Abbruch, Warnung, Fehler und Countdown. |
| `led.enabled` / `sink` | LED aktivieren; `respeaker`, `simulator` oder `null`. |
| `led.fps`, `brightness` | Aktualisierungsrate und Helligkeit 0 bis 255. |
| `led.vendor_id`, `product_id` | USB-IDs des Geräts. |
| `led.usb_timeout_ms`, `shutdown_timeout` | USB- und Beendigungsfristen. |
| `led.effect_paths` | Zusätzliche `.lefxset`-Katalogordner. |
| `led.simulation_offer_after_s` | Frist bis zum Simulatorangebot; 0 deaktiviert es. |

Relative Soundpfade wie `assets/feedback_sounds/debug/start.wav` beziehen sich
auf das installierte Paket – auch in der EXE –, nicht auf das aktuelle
Ausführungsverzeichnis. Eigene Dateien können als absolute Pfade angegeben
werden. `feedback.sounds_enabled: false` unterdrückt die Wiedergabe auch dann,
wenn ein Event im Log einem Sound-Cue zugeordnet ist.

`feedback_mappings.schema_version` ist derzeit `2`.
`feedback_mappings.events` ordnet kanonische `server.*`- und `client.*`-Events
den optionalen Ausgaben `led`, `sound` und `app` zu. LED-Aktionen sind
`set_state`, `clear_state`, `emit_event`, `set_overlay` und `set_output`.
Soundregeln verwenden `cue`, optional `volume` und `action`; Appregeln
verwenden `action`. Die ausgelieferte `config.yaml` ist die vollständige
Referenz aller bekannten Event-IDs und enthält kommentierte Beispiele.
