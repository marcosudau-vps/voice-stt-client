# V2-Codec – AP-CV2-010

Referenzserver: `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Reine Schnittstelle in [protocol_v2.py](../voice_stt_client/core/protocol_v2.py). Die laufende Anwendung verwendet bis zur Transportintegration weiterhin ihren bisherigen Transport. Dieses Paket verändert weder Profile noch SQLite, Hotkeys, Clipboard, Audioaufnahme oder UI.

## Öffentliche Schnittstelle

| Funktion / Modell | Vertrag |
| --- | --- |
| `new_id`, `is_canonical_uuid` | Client erzeugt UUIDv4; eingehende UUIDs werden nur geprüft, nie normalisiert. Auch andere kanonische UUID-Versionen sind gültig. |
| `build_hello`, `Hello` | Exakte Hellofelder, `[2]`, mindestens ein Trigger; Wakeauswahl genau bei konfiguriertem Wake. Suppression ersetzt die Auswahl nicht. `clientRunId` wird vom Aufrufer pro Prozess erzeugt. |
| `build_command`, `Command`, `CommandType`, `ActivationAction` | Alle fünf Commands. Envelopefelder automatisch gesetzt; neue UUIDv4 bei ausgelassener `commandId`. `activate` mit `source=manual` ohne `activationId`; `refresh/finish/cancel` mit ID ohne `source`. |
| `parse_client_message`, `encode_client_message` | Validieren auch übergebene Maps; Bool ist keine Zahl, Clientversion ist Integer 2. JSONstring genau einmal erzeugen und für bytegleichen Retry speichern. Kein Commandtracker/Replaycache im Codec. |
| `decode_server_message` | JSONtext oder JSONmap → `HelloAccepted`, `HandshakeRejected`, `CommandAck`, `Snapshot`, `Event`, `UnknownEvent` oder `None` für unbekannte Nicht-Events. Bekannte ungültige Nachricht bzw. ungültige Eventhülle → `ProtocolError`. Binäraudio ist keine Servertextnachricht. |
| `Event`, `EventType`, `InputPhase`, `AckResult` | 18 bekannte Events, fünf Phasen und 15 Resultcodes. Gemeinsame Eventidentität direkt typisiert; Fachpayloads unter den unveränderten Wirefeldnamen in `payload`. Nullable Pflichtfelder müssen vorhanden sein. Diagnose-Reasons bleiben additive Strings. |
| `Event.preview_text` | Nur Interim; geeignetes String-`displayText`, sonst Pflicht-`text`. Optionale Stabilisierung wird erhalten, ihr unbekanntes Format bricht den Parser nicht ab. Kein Finalsignal und keine Einfügung. |
| `parse_snapshot` | Vollständige requested/effective Maps aller 16 Sessionkeys. `embedded=True` verlangt Helloform ohne `type`. Offener Input und nach Activationsequence sortierte Pendingliste sind getrennt; keine Segment-/Textliste wird erfunden. |
| `decode_settings_schema`, `SettingsSchema` | Schema mit Eintragsmetadaten/defaultValue; keine erfundene Revision oder requested/effective Pflicht. |
| `decode_server_settings`, `ServerSettings` | Serverread mit `settings[]`, requested/effective Werten und ausdrücklich servergebundener Revision. Die gepinnte öffentliche Antwort darf `serverVersion=""` liefern. |
| `encode_server_settings_patch` | Nur `{baseSettingsRevision, changes}`; keine Session-ID und kein WebSocket-Envelope. Nicht leere Änderungen, finite JSONwerte. Feldpolicy und atomare Patchannahme entscheidet der Server. |
| `decode_settings_patch_response`, `SettingsPatchResponse`, `RevisionScope` | Maps `values/effectiveValues/applyPolicies`, separate Antwortform. RevisionScope muss der Aufrufer ausdrücklich angeben; niemals Sessionrevision als Serverrevision einsetzen. |
| `parse_log_access`, `LogAccess` | Available/unavailable getrennt, Sessionbindung und Origin-relative Pfade. Token nur im dedizierten Speichermodell; repr und Parserfehler enthalten ihn nicht. Keine Persistenz oder Token-URL. `to_mapping()` ist ein expliziter Wireexport und darf Nutztext/Token enthalten; nicht loggen. |
| `encode_audio_packet`, `decode_audio_packet`, `AudioPacket` | Bestehendes Format `uint32LE N + UTF8JSON + PCM16LE`, inklusive bestehender Encoder-Whitespace. 16/48 kHz und 1–8 Kanäle; PCM bereits int16 little-endian. Keine Floatkonvertierung im Codec. Metadaten ≤65536, PCM ≤ übergebener Servergrenze (Default524288), Kanalalignment und frames geprüft. Vorhandene frames sind positiv; leeres PCM ohne frames zulässig. |

Alle Parser liefern detached immutable Payloads; `to_mapping()` liefert eine neue veränderbare Kopie. Öffentliche Modelle werden über Parser/Builder erzeugt. Additive JSONfelder bleiben erhalten. Enumwerte sind die originalen Wirestrings. Schema-/Settingsdecoder prüfen Wireformen und bekannte Werttypen; Schema-Constraints, Crossfieldregeln, Katalogadmission und Applypolicy sind Serverautorität und werden im späteren Settingsservice ausgewertet.

## Übergabe an Transport und Mirror

Es gibt keine Callbacks und keine Sideeffects. Der Transport decodiert in Empfangsreihenfolge, prüft Generation und `sessionId` und gibt anschließend an Commandtracker/Mirror weiter. `UnknownEvent` darf nur den Sequenzfortschritt tragen. `None` verändert keine Domain. Events können vor Acks eintreffen; Ackdaten können älter als schon empfangene Events sein. Der Codec setzt keinen Zustand zurück und bewertet keine Pendingoperation. Snapshotannahme nach Stateversion/Sequenz, Resync, Terminaldedup und Finalreihenfolge bleiben Folgepaketen zugeordnet. Logcursor und Domain-eventSeq bleiben getrennt.

Ein Token wird aus `HelloAccepted.logAccess.accessToken` ausdrücklich an den vorhandenen Logpfad übergeben. Bootstrapprüfung hält Audio und Commands bis vollständiger Konfiguration zurück; das ist Aufgabe des späteren Transports, keine Codecautorität.

## Vektoren und reproduzierbare Prüfungen

[Originalservervektoren](../tests/contracts/protocol-v2-vectors.json) sind exakt die Gitbytes des gepinnten Servers. [Provenienz/SHA256](../tests/contracts/protocol-v2-provenance.json), [ergänzende vollständige Clientfixtures](../tests/contracts/protocol-v2-client-fixtures.json). Der originale `idle_snapshot` ist eine historische verkürzte Skizze und wird als unvollständig abgewiesen; das vollständige Supplement und echte Serverprojektionen werden angenommen. `command_id_conflict` ist gültige Syntax und scheitert erst am echten Server-Replaycache. Keine Originalvektoren wurden repariert oder umbenannt.

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.\venv\Scripts\python.exe -m unittest tests.test_v2_protocol -v
.\venv\Scripts\python.exe scripts/check_v2_server_contract.py --server-root <separater-ada13b0-Quellpfad> --server-repository <Server-Gitrepository>
.\venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
.\venv\Scripts\python.exe -m compileall -q voice_stt_client scripts tests
```

Der Checkpoint vergleicht jede verwendete Serverquelle bytegleich mit `git show ada13b0:<Pfad>`. Der Quellpfad muss die 17 in `SOURCE_FILES` benannten Dateien enthalten, einschließlich `VoiceSTT/_version.py` und Originalvektoren. Bei Windows-Exporten mit automatischer CRLF-Umsetzung die tatsächlichen Gitblobbytes exportieren; der Prüfer verschweigt keine Abweichung. Produktabhängigkeiten werden nicht um Server-/ASRpakete erweitert.

Der modellfreie Check verwendet echte Parser, Registry, Replaycache, Controller, Ledger, Snapshot-/Event-/Ackprojektionen. Für Audiovalidierung/Resampling werden die beiden unveränderten Produktionsfunktionen aus dem AST des gepinnten `server.py` kompiliert; so bleibt der modellabhängige Appimport außen vor. Wakeauswahl/Katalogcapabilities sind kontrollierte Testadapter. Kein Socket-, Mikrofon-, ASR- oder vollständiger Bootstrapnachweis; diese Grenzen gehören zu den Folgepaketen.
