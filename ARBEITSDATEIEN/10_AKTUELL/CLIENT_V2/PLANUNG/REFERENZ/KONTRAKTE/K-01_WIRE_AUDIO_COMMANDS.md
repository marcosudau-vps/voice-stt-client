# K-01 – Wire, Identitäten, Audio und Commands

Geltung: exakte Serverfelder und Serverlimits sind verbindlich; interne Clientrepräsentationen sind Vorschläge, lokale technische Werte begründbar anpassbare Startwerte gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Produktverhalten und Schutzwirkungen bleiben Pflicht.

## 1. Transport und Handshake

Endpoint: `ws://<host>:<port>/ws/v2` beziehungsweise `wss://<host>/ws/v2`. Desktop-Standardhost: `stt.voice.marcosudau.com`. Audio-, Log- und HTTP-Endpunkte teilen denselben Origin. Jeder WebSocket ist genau eine neue Session.

Textframes sind UTF-8-JSON-Objekte. Nur Client→Server sendet binäres Audio. Der Server sendet vor `hello` nichts. Der Client sendet `hello` unmittelbar nach Open; serverseitiger Schweigetimeout: **10 Sekunden**, Close `4408`. Es existieren weder `ready` noch `start`/`stop` noch ein Domain-`ping` auf V2. Keepalive verwendet den WebSocket-Ping der Bibliothek.

```json
{
  "type": "hello",
  "supportedProtocolVersions": [2],
  "clientVersion": "2.0.0-desktop",
  "clientCommit": "unknown",
  "clientRunId": "10000000-0000-4000-8000-000000000001",
  "requestedSession": {
    "trigger": {"manual": true, "wakeWord": true},
    "wakeWordIds": ["hey_jarvis"]
  },
  "runtimeSuppression": {"manual": false, "wakeWord": false}
}
```

Alle gezeigten Felder sind Pflicht. `clientVersion`/`clientCommit`: nicht leere Strings; Commit darf `unknown` sein. Versionsliste: nicht leer, Integers, Bool zählt nicht als Integer. Trigger- und Suppressionfelder: echte Booleans. Mindestens ein konfigurierter Trigger; `wakeWordIds` nicht leer genau bei aktiviertem Wake Word. Pausiertes Wake Word benötigt trotzdem eine Auswahl. Unbekannte Zusatzfelder sind toleriert; Sessionsettings in Zusatzfeldern werden **nicht** angewendet.

Optionales `?clientId=<id>` oder `X-VoiceSTT-Client-Id`: reine Auditkorrelation, 1–128 Zeichen aus `A–Z a–z 0–9 . _ : -`. Kein Auth- und kein Sessionkonfigurationsfeld. Andere Queryparameter haben keine V2-Wirkung.

Annahme:

```text
hello.accepted:
  type, protocolVersion=2, sessionId, serverVersion, serverCommit,
  snapshot (K-02, ohne inneres type), logAccess (K-04)
```

Mit Annahme öffnet der Server seinen Audiopfad und setzt die Hello-Suppression. Clientaudio und Nutzercommands werden erst nach Annahme und dem lokalen Konfigurationsbootstrap freigegeben. `serverCommit` wird aus der Build-/Runtime-Identität gelesen und kann `unknown` sein; dann muss die Integration den tatsächlich gestarteten Checkout bzw. Image-Digest separat belegen.

Ablehnungen:

| Fall | Vorherige Nachricht | Close | Clientreaktion |
| --- | --- | ---: | --- |
| erstes Frame ungültig, JSON unlesbar, binär, fehlende Pflichttypen | keine | 4400 | Konfigurations-/Clientfehler, keine Schleife |
| keine gemeinsame Version | `protocol.incompatible` | 4406 | inkompatibel anzeigen |
| kein Hello innerhalb 10 s | keine | 4408 | einmal erneut; Wiederholung als Clientfehler |
| Sessionkonfiguration unzulässig | `session.rejected` mit `errors[]` | 4409 | Fehler anzeigen; unveränderten Request nicht wiederholen |
| Kapazitätsgrenze | `session.rejected.reason=session_limit_reached` | 4409 | langer Backoff mit Jitter |
| interner Fehler / terminale Recovery | ggf. keine letzte Nachricht | 1011 | neue Session mit Backoff |

`protocol.incompatible` und `session.rejected` enthalten `reason`, `serverVersion`, `serverCommit`, `supportedProtocolVersions`, aber keine Session-ID. Fehlerobjekte enthalten `field`, `code`, `message`; Wake-Fehler zusätzlich `reason`/`wakeWordId`. Die Sessionauswahl ist atomar.

## 2. Identitäten und Sequenzen

Kanonische UUID: 36 Zeichen, Kleinbuchstaben, Bindestriche, `str(uuid.UUID(value)) == value`; die UUID-Version wird serverseitig nicht geprüft. Client erzeugt UUIDv4 für `clientRunId` und `commandId`. Alle Server-IDs unverändert speichern.

| Feld | Owner und Bedeutung |
| --- | --- |
| `clientRunId` | Client, neu pro Prozessstart, bei Reconnect gleich; Server prüft nur Syntax und speichert keine Run-Suppression für den Client |
| `sessionId` | Server, neu je Verbindung |
| `commandId` | Client, neu pro logischem Command innerhalb einer Session |
| `activationId`, `segmentId` | Server, stabile Herkunft der jeweiligen Daten |
| `activationSequence`, `segmentSequence` | pro Session steigende Ganzzahlen; Segmentsequence wird nicht pro Activation neu gestartet |
| `eventId` | Identität des logischen Events |
| `eventSeq` | Domain-Eventordnung, ab 1 lückenlos |
| `stateVersion` | sichtbare Zustandsversion; nicht lückenlos im Eventstrom |
| `settingsRevision` | Sessionrevision; REST-Serverrevision ist ein getrennter Zähler |

Lokale `connectionGeneration` grenzt alte Socket-/Audio-/UI-Callbacks ab. Sie ist kein Wirefeld. Server-Timerrevisionen bleiben serverintern; der Client erfindet dafür keinen Commandparameter.

## 3. Clientcommands

Jeder Command trägt `type`, `protocolVersion: 2`, aktuelle `sessionId`, neue kanonische `commandId`.

Client-Soll: `protocolVersion` als JSON-Integer `2` serialisieren. Präzisierung des Server-Ist: Der Commandparser prüft numerische Gleichheit und schließt Bool aus, akzeptiert dadurch auch `2.0`. Diese Toleranz gilt nicht für die Integerliste im Hello und ist kein alternativer Clientvertrag.

| `type` | Pflichtpayload | Verbot / Verhalten |
| --- | --- | --- |
| `activation.command`, `action=activate` | `source="manual"` | Schlüssel `activationId` verboten; niemals `source= wake_word` |
| `activation.command`, `action=refresh/finish/cancel` | `activationId` | Schlüssel `source` verboten; keine `extend`-Aktion |
| `trigger_suppression.set` | `manual`, `wakeWord` Bool | komplette Maske; Änderung erzeugt kein Domain-Event |
| `audio_availability.set` | `audioAvailable` Bool | Änderung erzeugt kein eigenes Availability-Event |
| `session_settings.patch` | `baseSettingsRevision` int ≥ 0, `changes` nicht leeres Objekt | K-03, atomarer Patch |
| `session.snapshot.request` | keine weiteren Fachfelder | Ack, anschließend Snapshot; auch beim Replay neuer Snapshot |

### Phasenmatrix

| Phase | `activate` | `refresh` | `finish` / `cancel` |
| --- | --- | --- | --- |
| `idle` | `applied`, wenn Audio und Manual verfügbar | `not_active` | `not_active` |
| `waiting_first_speech` | `activation_locked` | `invalid_phase` | `applied` |
| `segment_active` | `activation_locked` | `applied`; `max(Deadline, now + segmentWatchdogRefreshMs)` | `applied` |
| `followup_wait` | `activation_locked` | `applied`; `now + followupTimeoutMs` | `applied` |
| `closing_input` | `activation_locked` | `closing_input` | `no_change` |

Bei einer anderen als der offenen `activationId`: `stale_activation`; bei fremder Session: `stale_session`. `activate` prüft Audioverfügbarkeit vor Phase und Triggerfreigabe; `audio_unavailable` hat deshalb Vorrang vor `activation_locked`. Wake-Admission wird serverintern entschieden.

## 4. Ack und Idempotenz

Ack-Pflichtfelder: `type="command.ack"`, `protocolVersion=2`, `sessionId`, `commandId`, `accepted`, `result`, `activationId` (UUID/null), `inputPhase`, `stateVersion`, `settingsRevision`. `errors[]` erscheint bei Settingsablehnungen und Revisionskonflikten, nicht pauschal bei `invalid_payload`.

| Result | accepted | Konsequenz |
| --- | --- | --- |
| `applied` | true | Command abgeschlossen; zuständige Events bzw. Ack-/Snapshotprojektion anwenden |
| `no_change` | true | keine zweite fachliche Wirkung |
| `activation_locked` | false | Serverzustand übernehmen; keine Ersatzactivation |
| `not_active` | false | Control-Pending beenden, Snapshot bei widersprüchlichem Spiegel |
| `invalid_phase` | false | keine Warnschleife; Phase beachten |
| `closing_input` | false | weitere Refreshs sperren |
| `stale_session` | false | Command falsch gebunden; nicht auf neuer Session wiederholen |
| `stale_activation` | false | Snapshot anfordern, alte ID nicht auf aktuelle umschreiben |
| `command_id_conflict` | false | Clientfehler; dieselbe ID nie mit anderem Payload senden |
| `invalid_payload` | false | Clientfehler; keine identische Wiederholung |
| `trigger_suppressed` | false | Quelle gesperrt; danach kann Diagnoseevent folgen |
| `audio_unavailable` | false | Gerät verfügbar machen und melden |
| `settings_revision_conflict` | false | Snapshot/Serverread, neue Revision, bewusst neu berechneter Patch mit neuer ID |
| `settings_rejected` | false | Feldfehler anzeigen, gesamte Änderung abgelehnt |
| `internal_error` | false | Diagnose, Snapshot; bei unbrauchbarem Zustand Reconnect |

Events eines wirksamen Commands können **vor dem Ack** eintreffen; `activation.trigger_suppressed` folgt seinem Ablehnungsack, der angeforderte Snapshot folgt dem Snapshot-Ack. Finish-/Cancel-Acks können eine ältere `closing_input`-Version tragen als bereits empfangene Close-/Terminalevents. Das Ack bestätigt das Command und darf einen neueren Spiegel niemals zurücksetzen.

Kein Event für Suppression, Audioverfügbarkeit oder Refresh ohne Friständerung: Nach Ack den bestätigten Commandpayload versionsgesichert spiegeln oder Snapshot holen. Pending-Commands bleiben korreliert; mutationsgleiche Domains werden serialisiert. Veraltete Replay-Acks wirken ausschließlich auf die Pending-Bestätigung, nicht auf neuere Zustände.

Gleiche ID und gleicher Payload liefert unverändertes ursprüngliches Ack ohne neue Wirkung. Die Clientregel ist **bytegleicher Retry** desselben gespeicherten JSON. Der Server vergleicht Activation-/Audio-Commands semantisch, andere Typen teilweise vollständig. Replaycache lebt bis Sessionende. Neue Session: keine alten IDs, Controls oder Retrys übernehmen.

Unlesbares JSON, kein Objekt, unbekannter Typ, zweites Hello, fehlende oder nicht kanonische `commandId`: ignoriert, **kein Ack**. Wohlgeformte ID plus erkannter Typ und ungültige Fachfelder: `invalid_payload`. Ein Commandtimeout ist lokal begrenzt und löst Transport-/Snapshotklärung aus; er ist kein Beweis, dass das Command unwirksam war.

## 5. Binäraudio

```text
uint32 Little-Endian N | N Bytes UTF-8 JSON-Objekt | PCM signed int16 Little-Endian
```

Es gibt kein Magic, kein `VSTT`, keine Versionsbytes und keine Flags.

| Metadatum | Regel |
| --- | --- |
| `sampleRate` | Pflicht, positive Ganzzahl; Server resampelt auf 16 kHz |
| `channels` | optional, Default 1, Integer 1–8, interleaved |
| `format` | optional, Default und einziger Wert `pcm_s16le` |
| `frames` | optional; falls vorhanden positive Ganzzahl (Bool ausgeschlossen) und `frames * channels * 2 == PCM-Bytes` |

Metadaten ≤ 65 536 Bytes, PCM ≤ `max_audio_packet_bytes` (Code-Default 524 288; aktuelle Grenze aus `/api/config`). PCM-Länge muss Vielfaches von `channels*2` sein. Ungültige Frames werden still verworfen, nie quittiert. Gleichmäßige Pakete mit 20–100 ms sind eine technische Empfehlung, 40 ms der erste Clientstartwert; passende vorhandene Paketierung darf nach Latenz-/Lastprüfung weitergenutzt werden. Float vor int16-Umwandlung clampen. Gerätewechsel aktualisiert Rate und Kanalzahl jedes Pakets. Audio vor Annahme ist untersagt.

Client-Sendqueue ist begrenzt: Überlauf, stale Generation und Encoderfehler werden gezählt und sichtbar diagnostiziert. Es gibt kein unbeschränktes Nachsenden alter Mikrofondaten. Technischer Startwert: 500 ms Audio in der Sendqueue; bei anhaltendem Überlauf Aufnahmeverfügbarkeit degradieren und Transport prüfen. Ein anderer begrenzter Wert ist mit Latenz-/Überlauftest und dokumentierter Begründung zulässig; kein Serverlimit.

## 6. Quellen

Präzisierung AP-CV2-010, 2026-10-11: Der gepinnte `server.py:packet_to_server_samples` prüft vorhandene `frames` über `require_positive_int`; `frames=0` ist auch bei leerem PCM ungültig. Ein leeres Paket ohne `frames` ist zulässig. Keine Änderung der Serverbaseline.

Servermodule `api_fastapi_server/protocol_v2/{schema,handshake,commands,connection,session}.py`, `api_fastapi_server/protocol.py`, `/ws/v2` in `api_fastapi_server/server.py`; Tests `test_protocol_v2_contract`, `test_protocol_v2_e2e`, `test_protocol_v2_state_version`, `test_protocol_v1_v2_boundary`. Der [Quellenindex](../../EVIDENCE/source-manifest.json) fixiert alle Pfade auf den Servercommit.
