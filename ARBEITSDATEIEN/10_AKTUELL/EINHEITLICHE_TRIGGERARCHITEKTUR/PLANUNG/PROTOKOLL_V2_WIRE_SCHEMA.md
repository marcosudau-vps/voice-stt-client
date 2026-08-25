# Protokoll v2 – verbindliches Wire-Schema

**Status:** FROZEN als normative Ergänzung zu
`TECHNISCHER_CONTRACT_FREEZE.md`

**Stand:** 2026-08-25

Dieses Dokument beseitigt den verbleibenden Interpretationsspielraum zwischen
Server- und Desktop-Client-Paketen. Es legt Nachrichtennamen, Pflichtfelder,
Null-/Omission-Semantik, Result-Codes und repräsentative Testvektoren fest.
Fachliche Semantik und State-Machine bleiben im Contract-Freeze definiert.

## 1. Allgemeine Regeln

- Transportpayloads sind UTF-8-kodierte JSON-Objekte.
- Feldnamen verwenden `camelCase`; Enumwerte und Nachrichtentypen verwenden
  `snake_case` beziehungsweise die unten festgelegten punktgetrennten Namen.
- Jede Nachricht nach erfolgreichem Handshake enthält
  `protocolVersion = 2` und `sessionId`.
- Clientcommands enthalten zusätzlich eine UUID in `commandId`.
- Serverevents enthalten zusätzlich `eventId`, `eventSeq`, `stateVersion` und
  `occurredAtUnixMs`.
- IDs sind nicht leere Strings; UUIDs werden kanonisch mit Bindestrichen
  serialisiert. Zeitpunkte sind UTC-Unixzeit in Millisekunden.
- Ein Pflichtfeld darf nicht durch `null` ersetzt werden. `null` ist nur dort
  zulässig, wo es ausdrücklich genannt ist.
- Empfänger ignorieren unbekannte Zusatzfelder derselben Protokollversion,
  dürfen aber unbekannte Nachrichtentypen nicht als bekannte Zustandsänderung
  interpretieren. Dadurch sind additive v2-Erweiterungen möglich.
- Der Client leitet Zustände ausschließlich aus Acks, Events und Snapshots ab;
  er erzeugt keine Server-ID und keine serverseitige Phase selbst.

Die maschinenlesbaren Positiv- und Negativbeispiele liegen unter
`VERTRAGSVEKTOREN/protocol-v2-vectors.json`.

## 2. Handshake

### 2.1 `hello`

Client → Server, exakt einmal als erste Textnachricht:

| Feld | Typ | Pflicht | Regel |
|---|---|---:|---|
| `type` | String | ja | `hello` |
| `supportedProtocolVersions` | Array<Integer> | ja | nicht leer, für diesen Cut `[2]` |
| `clientVersion` | String | ja | nicht leer |
| `clientCommit` | String | ja | nicht leer; Buildcommit oder `unknown` |
| `clientRunId` | UUID | ja | neu je Programmstart |
| `requestedSession` | Object | ja | enthält `trigger` und `wakeWordIds` |
| `runtimeSuppression` | Object | ja | exakt `manual` und `wakeWord` als Boolean |

`requestedSession.trigger` enthält die Pflicht-Booleans `manual` und
`wakeWord`; mindestens einer ist `true`. `requestedSession.wakeWordIds` ist
ein Array kanonischer Wake-Word-IDs. Bei `trigger.wakeWord=true` ist es nicht
leer. Nur bei `trigger.wakeWord=false` darf es leer sein. Eine
`runtimeSuppression.wakeWord=true` hebt diese Admission-Regel nicht auf,
damit ein späteres Unsuppress derselben Client-Laufzeit weiterhin definierte
Modelle besitzt. Unbekannte, deaktivierte oder nicht ladbare IDs lehnen die
gesamte Session ab. Weitere Sessionwerte werden durch das Settings-Schema aus
AP-SRV-050 definiert und serverseitig validiert.

### 2.2 `hello.accepted`

Server → Client:

| Feld | Typ | Pflicht |
|---|---|---:|
| `type` | String = `hello.accepted` | ja |
| `protocolVersion` | Integer = `2` | ja |
| `sessionId` | UUID | ja |
| `serverVersion` | String | ja |
| `serverCommit` | String | ja |
| `snapshot` | `session.snapshot`-Payload ohne doppeltes `type` | ja |

Vor `hello.accepted` sind Audiostream, manuelle Triggerannahme und
Wake-Word-Erkennung gesperrt.

### 2.3 Ablehnungen

- `protocol.incompatible`: keine gemeinsame Protokollversion;
- `session.rejected`: Protokoll passt, aber die angeforderte Session ist
  ungültig oder kann nicht atomar aufgebaut werden.

Beide enthalten `type`, `reason`, `serverVersion`, `serverCommit` und
`supportedProtocolVersions`. `session.rejected` enthält zusätzlich
`errors[]` mit `field`, `code` und einer nicht geheimen `message`. Danach
schließt der Server die Verbindung; es entsteht keine `sessionId`.

## 3. Clientcommands

Gemeinsame Pflichtfelder jedes Commands:

```text
type, protocolVersion, sessionId, commandId
```

### 3.1 `activation.command`

Zulässige disjunkte Formen:

```json
{
  "type": "activation.command",
  "protocolVersion": 2,
  "sessionId": "…",
  "commandId": "…",
  "action": "activate",
  "source": "manual"
}
```

```json
{
  "type": "activation.command",
  "protocolVersion": 2,
  "sessionId": "…",
  "commandId": "…",
  "action": "refresh|finish|cancel",
  "activationId": "…"
}
```

Wichtig:

- Der Desktop-Client darf ausschließlich `source = manual` senden.
- `wake_word` ist eine serverinterne Triggerquelle. Ein akzeptierter
  serverseitiger Treffer läuft durch dieselbe Activation-Admission und wird
  in Events/Snapshots als `primarySource = wake_word` sichtbar, aber nie vom
  Client behauptet.
- Bei `activate` ist `activationId` verboten.
- Bei `refresh`, `finish` und `cancel` ist `activationId` Pflicht und `source`
  verboten.

### 3.2 Weitere Commands

- `trigger_suppression.set`: `manual` und `wakeWord` als Pflicht-Booleans.
- `audio_availability.set`: `audioAvailable` als Pflicht-Boolean.
- `session_settings.patch`: `baseSettingsRevision` als nicht negative
  Ganzzahl und nicht leeres Objekt `changes`.
- `session.snapshot.request`: keine weiteren fachlichen Felder.

## 4. `command.ack`

Jeder syntaktisch erkennbare Command erhält genau ein logisches Ack:

| Feld | Typ | Pflicht | Regel |
|---|---|---:|---|
| `type` | String | ja | `command.ack` |
| `protocolVersion` | Integer | ja | `2` |
| `sessionId` | UUID | ja | aktuelle Session |
| `commandId` | UUID | ja | Echo |
| `accepted` | Boolean | ja | fachlich wirksam/akzeptiert |
| `result` | Enum | ja | siehe unten |
| `activationId` | UUID oder `null` | ja | nach Ack beobachtete Activation |
| `inputPhase` | Enum | ja | nach Ack beobachtete Phase |
| `stateVersion` | Integer | ja | nicht negativ |
| `settingsRevision` | Integer | ja | nicht negativ |
| `errors` | Array | nein | nur bei feldbezogener Ablehnung |

Verbindliche `result`-Werte:

```text
applied, no_change,
activation_locked, not_active, invalid_phase, closing_input,
stale_session, stale_activation, command_id_conflict,
invalid_payload, trigger_suppressed, audio_unavailable,
settings_revision_conflict, settings_rejected, internal_error
```

`accepted=true` ist nur für `applied` und `no_change` zulässig. Ein Replay
desselben `commandId` mit identischem Payload liefert byte-semantisch dasselbe
Ack einschließlich ursprünglichem `result`, IDs und Versionswerten; es gibt
keinen gesonderten `replayed`-Result-Code.

## 5. Serverevents

Gemeinsame Pflichtfelder jedes Domain-Events:

```text
type, protocolVersion, sessionId, eventId, eventSeq,
stateVersion, occurredAtUnixMs
```

Zustandsbezogene Events enthalten `activationId`; segmentbezogene Events
zusätzlich `segmentId` und `segmentSequence`. `reason` ist Pflicht, wenn ein
Ereignis einen Abbruch, Discard, Fehler, eine Unterdrückung oder einen
Eingabeschluss beschreibt.

| Event | Zusätzliche Pflichtfelder |
|---|---|
| `activation.started` | `activationId`, `activationSequence`, `primarySource`, `inputPhase`, `effectiveSettings` |
| `activation.phase_changed` | `activationId`, `previousPhase`, `inputPhase`, `deadlineAtUnixMs`, `remainingMs` |
| `activation.input_closed` | `activationId`, `reason`, `causedByCommandId`, `acceptedSegmentCount` |
| `activation.completed` | `activationId`, `acceptedSegmentCount`, `terminalSegmentCount` |
| `activation.cancelled` | `activationId`, `reason`, `acceptedSegmentCount`, `terminalSegmentCount` |
| `activation.failed` | `activationId`, `reason`, `acceptedSegmentCount`, `terminalSegmentCount` |
| `activation.trigger_suppressed` | `source`, `reason` |
| `segment.recording_started` | `activationId`, `segmentId`, `segmentSequence` |
| `segment.recording_ended` | `activationId`, `segmentId`, `segmentSequence`, `reason` |
| `transcription.accepted` | `activationId`, `segmentId`, `segmentSequence` |
| `transcription.completed` | `activationId`, `segmentId`, `segmentSequence`, `text` |
| `transcription.discarded` | `activationId`, `segmentId`, `segmentSequence`, `reason` |
| `transcription.failed` | `activationId`, `segmentId`, `segmentSequence`, `reason` |
| `watchdog.warning` | `activationId`, `segmentId`, `segmentSequence`, `deadlineAtUnixMs`, `remainingMs` |
| `wakeword.detected` | `activationId`, `wakeWordId`, `score`, `primarySource` = `wake_word` |
| `wakeword.availability_changed` | `catalogRevision`, `availableWakeWordIds` |
| `settings.changed` | `settingsRevision`, `scope`, `changedKeys`, `applyPolicy` |

`activation.input_closed` ist das genau-einmal-Ereignis für die Freigabe des
Vordergrundslots. Das spätere Activation-Terminal ist davon getrennt.
`wakeword.detected.activationId` ist die durch denselben Treffer akzeptierte
Activation; unterdrückte oder gelatchte Rohdetektionen erzeugen dieses Event
nicht.

`causedByCommandId` ist bei durch `finish` oder `cancel` ausgelöstem
Eingabeschluss die UUID des akzeptierten Commands. Bei VAD-/Follow-up-/Timer-,
Watchdog-, Geräte-, Session- oder Recoveryabschluss ist das Feld `null`.

## 6. `session.snapshot`

Server → Client als eigenständige Nachricht oder als `snapshot` in
`hello.accepted`:

```text
type, protocolVersion, serverVersion, serverCommit,
sessionId, stateVersion, lastEventSeq, settingsRevision,
input, pendingActivations, trigger, audioAvailable,
effectiveSettings, wakeWordCapabilities
```

Bei Einbettung in `hello.accepted` entfällt nur das innere Feld `type`.

`input` enthält immer:

```text
phase, activationId, primarySource, deadlineAtUnixMs,
remainingMs, closeRequested
```

In `idle` sind `activationId`, `primarySource`, `deadlineAtUnixMs` und
`remainingMs` jeweils `null`; `closeRequested=false`. In einer offenen Phase
sind `activationId` und `primarySource` nicht null. `pendingActivations` ist
streng nach der serverseitig je Session steigenden `activationSequence`
sortiert; jeder Eintrag enthält diese Sequence ausdrücklich.

## 7. Transportabschluss

Verbindliche anwendungsbezogene WebSocket-Close-Codes:

| Code | Bedeutung |
|---:|---|
| `4400` | ungültige erste Nachricht oder nicht parsebares Handshake |
| `4406` | keine gemeinsame Protokollversion |
| `4408` | Handshake-Timeout |
| `4409` | Sessionadmission abgelehnt |
| `1011` | unerwarteter interner Serverfehler |

Fachlich abgelehnte Commands schließen die Session nicht. Normale
Netzwerk-/Clienttrennung verwendet den üblichen WebSocket-Abschluss und folgt
den Recoveryregeln des Contract-Freeze.

## 8. Contract-Test-Gate

AP-SRV-040 und AP-CLI-010 müssen dieselben Vektoren verwenden. PASS verlangt:

1. alle `validMessages` werden akzeptiert beziehungsweise korrekt gespiegelt;
2. alle `invalidMessages` werden mit dem erwarteten Code abgelehnt;
3. `manual_activate_replay` erzeugt nur eine Activation und dasselbe Ack;
4. `client_claims_wake_word` wird als `invalid_payload` abgelehnt;
5. Snapshot und Eventfelder werden ohne Umbenennung auf beiden Seiten
   verarbeitet;
6. additive unbekannte Felder verändern keine bekannte Semantik.
