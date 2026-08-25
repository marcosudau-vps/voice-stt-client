# Technischer Contract-Freeze – Einheitliche Triggerarchitektur

**Status:** FROZEN als Grundlage des Implementierungsplans

**Stand:** 2026-08-25

**Protokollziel:** `protocolVersion = 2`

Dieses Dokument konkretisiert das fachliche `ZIELBILD.md`. Bei technischen
Widersprüchen zu älteren Analysen oder zum heutigen Code gilt dieser Contract
für die Migration. Kalibrierwerte, die ausdrücklich als messdatenabhängig
markiert sind, dürfen innerhalb der hier festgelegten Semantik angepasst
werden.

Das ergänzende `PROTOKOLL_V2_WIRE_SCHEMA.md` und die maschinenlesbaren
Vektoren unter `VERTRAGSVEKTOREN/` sind für Nachrichtennamen, Pflichtfelder,
Result-Codes und Transportbeispiele ebenfalls normativ. Bei einer Abweichung
zwischen einem verkürzten Beispiel in diesem Dokument und dem Wire-Schema
gilt das Wire-Schema.

## 1. Begriffe und Verantwortlichkeiten

- Eine **Session** entspricht genau einer angenommenen Desktop-WebSocket-
  Verbindung und besitzt eine neue `sessionId`.
- Eine **Client-Laufzeit** wird durch eine beim Programmstart erzeugte, nicht
  persistierte `clientRunId` bezeichnet. Sie verbindet nur die bewussten
  Trigger-Suppressionszustände über Reconnects hinweg.
- Eine **Activation** ist ein durch genau einen Trigger geöffnetes
  Eingabefenster mit stabiler `activationId`, ursprünglicher Triggerquelle und
  unveränderlichem Settings-Snapshot.
- Ein **Segment** ist ein serieller Sprachabschnitt innerhalb einer Activation.
- Der **Vordergrundzustand** entscheidet allein über Triggerannahme,
  Audioaufnahme und Bedienaktionen.
- Eine geschlossene Activation darf im Hintergrund weiter **drainen**, bis
  jedes angenommene Segment einen terminalen Ausgang besitzt. Dieser Zustand
  blockiert keine Trigger.

Der Server ist Autorität über Vordergrundzustand, IDs, Timer, Segmentledger,
Resultatreihenfolge und Effective Settings. Der Client hält physische Hotkeys,
Audiogerät, ReSpeaker/Mute, Feedbackdarstellung und Credential-Speicherung.

## 2. Kanonische Vordergrund-State-Machine

| Phase | Bedeutung | Trigger-Lock | Deadline |
|---|---|---:|---|
| `idle` | Kein offenes Eingabefenster | frei | keine |
| `waiting_first_speech` | Activation angenommen, noch kein Segment | gesetzt | Initial-Speech |
| `segment_active` | Ein Segment wird aufgenommen | gesetzt | Segment-Watchdog |
| `followup_wait` | Segment beendet, weitere Sprache derselben Activation möglich | gesetzt | Follow-up |
| `closing_input` | Gate/Aufnahme schließen und Job oder Verwerfung dauerhaft registrieren | gesetzt | kurzer Recovery-Timeout |

`finalizing` ist kein Wert von `inputPhase`. Hintergrundverarbeitung wird im
Activation-/Segmentledger abgebildet.

### 2.1 Zulässige Übergänge

| Ausgang | Ursache | Ziel | Wirkung |
|---|---|---|---|
| `idle` | akzeptiertes `activate` | `waiting_first_speech` | neue Activation und Settings-Snapshot |
| `waiting_first_speech` | VAD/Recorder startet | `segment_active` | neues Segment, initialer Watchdog |
| `waiting_first_speech` | Initial-Speech-Timeout | `closing_input` → `idle` | Abschluss ohne Segment |
| `segment_active` | reguläres VAD-Ende | `followup_wait` | Segmentjob registrieren, Follow-up starten |
| `followup_wait` | neue Sprache | `segment_active` | nächstes Segment derselben Activation |
| `followup_wait` | Follow-up-Timeout | `closing_input` → `idle` | Eingabe schließen, Hintergrund darf drainen |
| jede offene Phase | `finish` | `closing_input` → `idle` | angenommene Segmente regulär verarbeiten |
| jede offene Phase | `cancel` | `closing_input` → `idle` | unveröffentlichte Resultate terminal verwerfen |
| `segment_active` | Segment-Watchdog | `closing_input` → `idle` | Audio wie Finish verarbeiten, kein Follow-up |
| jede offene Phase | `audioAvailable=false` | `closing_input` → `idle` | Activation canceln, Session bestehen lassen |
| jede offene Phase | Session-/Serververlust | Session endet | keine Fortsetzung in neuer Session |

Der Server darf `idle` erst veröffentlichen, wenn:

1. das Controlled Gate geschlossen ist;
2. kein Recorder mehr Audio unter der alten `activationId` annimmt;
3. jedes bis dahin angenommene Segment entweder dauerhaft als Final-Job oder
   als terminaler Verwerfungs-/Fehlerausgang registriert ist;
4. der Input-Close-Grund und das korrelierte Lifecycle-Ereignis registriert
   sind.

Er wartet ausdrücklich nicht auf das Ergebnis der Final-Inferenz.

### 2.2 Commands je Phase

| Phase | `activate` | `refresh` | `finish` / `cancel` |
|---|---|---|---|
| `idle` | gemäß effektiver Triggerquelle | `not_active` | `not_active` |
| `waiting_first_speech` | `activation_locked` | `invalid_phase` | zulässig |
| `segment_active` | `activation_locked` | Watchdog-Refresh | zulässig |
| `followup_wait` | `activation_locked` | Follow-up-Reset | zulässig |
| `closing_input` | `activation_locked` | `closing_input` | idempotente Zustandsantwort |

Control-Commands enthalten die vom Client beobachtete `activationId`. Ein
Command darf nie versehentlich auf eine inzwischen neuere Activation wirken.

## 3. Hintergrundledger und Terminals

Nach Eingabeschluss besitzt eine Activation einen der folgenden
Verarbeitungszustände:

```text
draining → completed | cancelled | failed
```

Jedes angenommene Segment besitzt exakt einen terminalen Zustand:

- `completed` – Final-Ergebnis veröffentlicht;
- `discarded` – kein Nutzresultat, maschinenlesbarer Grund;
- `cancelled` – durch bewussten Cancel unterdrückt;
- `failed` – Verarbeitung technisch fehlgeschlagen.

Leere Final-Transkription ist `discarded` mit `reason=empty_final`, nicht ein
fehlendes Terminal. Queue-Limit, Sessionende, Inferenzfehler und Recovery
erzeugen ebenfalls Terminals. Für jede Activation gilt nach Eingabeschluss:

```text
acceptedSegmentCount == terminalSegmentCount
```

Erst dann entsteht genau ein terminales Activation-Ereignis. Diese späte
Activation-Terminierung ändert den Vordergrundzustand nicht.

### 3.1 Pipeline und zulässige Parallelität

- Live-Transkription läuft während eines aktiven Sprachsegments.
- Eine Final-Inferenz darf aufgrund erkannter Stille bereits vor dem
  technischen Segmentende vorbereitet oder gestartet werden.
- Definitiv veröffentlicht wird ein Finalresultat erst unter der stabilen
  Identität des beendeten und im Ledger angenommenen Segments.
- Nach Segmentende dürfen Follow-up-Fenster und Final-Inferenz parallel
  laufen. Weder Follow-up noch ein neues Vordergrundfenster warten auf das
  Ende dieser Inferenz.
- Ein später Abschluss der alten Final-Inferenz darf Zustand oder Korrelation
  einer neueren Activation nicht aus einem Current-Activation-Zeiger ableiten.

### 3.2 Ergebnisreihenfolge

- Beim Annehmen erhält jedes Segment eine streng steigende
  `segmentSequence` innerhalb der Session.
- Finaljobs tragen `sessionId`, `activationId`, `segmentId`,
  `segmentSequence` und den Activation-Settings-Snapshot unveränderlich.
- Nutzresultate werden pro Session in `segmentSequence`-Reihenfolge
  veröffentlicht.
- Ein Fehler-/Discard-/Cancel-Terminal füllt die entsprechende Sequenzstelle,
  damit spätere Resultate nicht dauerhaft blockiert werden.
- Das Starten einer neueren Activation darf die Korrelation eines älteren
  Jobs niemals aus einem globalen „current activation“-Zeiger ableiten.

## 4. Timervertrag

Intern verwendet der Server monotone Zeit und eine `timerRevision`. Im Wire
werden `deadlineAtUnixMs` und `remainingMs` nur zur Darstellung geliefert;
der Client entscheidet niemals selbst, dass eine Phase abgelaufen ist.

| Setting | Default | Bereich | Apply |
|---|---:|---:|---|
| `activation.initialSpeechTimeoutMs` | 15000 | 100–3600000 | `next_activation` |
| `activation.followupTimeoutMs` | 3000 | 100–60000 | `next_activation` |
| `activation.segmentWatchdogInitialMs` | 600000 | 60000–3600000 | `next_activation` |
| `activation.segmentWatchdogRefreshMs` | 180000 | 30000–600000 | `next_activation` |
| `activation.segmentWatchdogWarningMs` | 30000 | 5000 bis kleiner als wirksame Frist | `next_activation` |
| `activation.closingRecoveryTimeoutMs` | 5000 | 1000–30000 | `next_activation` |

Regeln:

- `refresh` in `followup_wait` setzt die Deadline auf
  `now + followupTimeoutMs`. Es gibt kein `extensionSeconds` und kein
  Zeitguthaben.
- Beim Start eines Segments gilt
  `now + segmentWatchdogInitialMs`.
- `refresh` in `segment_active` setzt
  `max(currentDeadline, now + segmentWatchdogRefreshMs)`.
- Jeder wirksame Refresh ersetzt Warn- und Ablauf-Timer durch eine neue
  `timerRevision`; stale Timer haben keine Wirkung.
- Der Watchdog wird nicht durch VAD-Aktivität zurückgesetzt.
- Beim Watchdog-Ablauf wird das Segment regulär verarbeitet und die ganze
  Activation ohne Follow-up geschlossen.

## 5. Identitäten, Versionen und Idempotenz

| Feld | Owner / Lebensdauer |
|---|---|
| `protocolVersion` | Serverauswahl aus Clientangebot; für diesen Cut `2` |
| `clientRunId` | Client; neu bei jedem Programmstart, nicht persistent |
| `sessionId` | Server; neu je angenommener WebSocket-Session |
| `activationId` | Server; neu je akzeptierter Activation-Admission aus manuellem Command oder serverinterner Wake-Detection, bis Ledgerterminal erhalten |
| `activationSequence` | Server; streng steigend je akzeptierter Activation innerhalb der Session |
| `segmentId` | Server; eindeutig innerhalb der Session |
| `segmentSequence` | Server; streng steigend innerhalb der Session |
| `commandId` | Client; UUID je logischem Command |
| `eventId` | Server; UUID je logischem Ereignis |
| `eventSeq` | Server; streng steigend je Session |
| `stateVersion` | Server; steigt bei jeder sichtbaren Zustandsänderung |
| `settingsRevision` | Server; steigt bei bestätigter Settingsänderung |

- Derselbe `commandId` mit identischem Payload liefert dasselbe Ack und
  erzeugt keine zweite Wirkung.
- Derselbe `commandId` mit abweichendem Payload wird als
  `command_id_conflict` abgelehnt.
- Der Server hält den Replay-Cache mindestens für die gesamte Session.
- Erzeugt eine wirksame Transition ein Domain-Ereignis, existiert logisch
  genau ein `eventId`/`eventSeq`. Transport-Replay darf dasselbe Ereignis
  erneut liefern; der Client dedupliziert über `eventId` beziehungsweise
  `eventSeq`.
- Commands mit falscher `sessionId` oder nicht aktueller `activationId`
  werden `stale_session` beziehungsweise `stale_activation`.

## 6. Wire-Contract Version 2

Alle Nachrichten tragen `protocolVersion`, `sessionId` (nach Handshake) und
bei Zustandsbezug `stateVersion`.

### 6.1 Handshake

Client → Server:

```json
{
  "type": "hello",
  "supportedProtocolVersions": [2],
  "clientVersion": "…",
  "clientCommit": "…",
  "clientRunId": "…",
  "requestedSession": {
    "trigger": { "manual": true, "wakeWord": true },
    "wakeWordIds": ["…"]
  },
  "runtimeSuppression": { "manual": false, "wakeWord": false }
}
```

Der Server validiert Sessionauswahl und Suppression vollständig, bevor
Trigger/Wake-Word-Erkennung freigegeben werden. Bei keiner gemeinsamen Version
sendet er `protocol.incompatible` mit Serverversion, Commit und unterstützten
Versionen und eröffnet keine teilweise nutzbare Session.

Die persistierte beziehungsweise angeforderte Triggerbasis muss mindestens
eine konfigurierte Quelle enthalten. Ist `requestedSession.trigger.wakeWord`
aktiv, muss `wakeWordIds` mindestens eine gültige ID enthalten. Nur bei
deaktivierter Wake-Word-Quelle darf die Liste leer sein; eine bloße
Laufzeitsuppression ersetzt diese Auswahl nicht.

### 6.2 Clientcommands

- `activation.command` mit `commandId`, `action` = `activate|refresh|finish|cancel`;
  der Desktop-Client sendet bei `activate` ausschließlich `source=manual`,
  während `wake_word` nur serverintern durch die Detection-Admission entsteht;
  Control-Aktionen enthalten die beobachtete `activationId`;
- `trigger_suppression.set` mit getrennten Booleans `manual` und `wakeWord`;
- `audio_availability.set` mit `audioAvailable`;
- `session_settings.patch` mit `baseSettingsRevision` und Änderungen;
- `session.snapshot.request`.

Jeder Command erhält `command.ack` mit mindestens:

```text
commandId, accepted, result, sessionId, activationId,
inputPhase, stateVersion, settingsRevision
```

### 6.3 Serverevents

Verbindliche Domainnamen:

- `activation.started`
- `activation.phase_changed`
- `activation.input_closed`
- `activation.completed`
- `activation.cancelled`
- `activation.failed`
- `activation.trigger_suppressed` (diagnostisch)
- `segment.recording_started`
- `segment.recording_ended`
- `transcription.accepted`
- `transcription.completed`
- `transcription.discarded`
- `transcription.failed`
- `watchdog.warning`
- `wakeword.detected`
- `wakeword.availability_changed`
- `settings.changed`

Lifecycle-Ereignisse enthalten je nach Bezug `activationId`, `segmentId`,
`segmentSequence`, `inputPhase`, `reason`, `eventId`, `eventSeq` und
`stateVersion`. `activation.input_closed` wird genau einmal je wirksamem
Eingabeschluss erzeugt, auch wenn keine Sprache erkannt wurde.

## 7. Snapshot und Resynchronisierung

`session.snapshot` wird im angenommenen `hello`, auf explizite Anfrage und
nach festgestellter Eventlücke geliefert. Er enthält mindestens:

```text
protocolVersion, serverVersion, serverCommit,
sessionId, stateVersion, lastEventSeq, settingsRevision,
input: { phase, activationId, primarySource, deadlineAtUnixMs,
         remainingMs, closeRequested },
pendingActivations: [
  { activationId, activationSequence, inputClosedReason, processingState,
    acceptedSegmentCount, terminalSegmentCount }
],
trigger: { configured, suppressed, effective },
audioAvailable,
effectiveSettings,
wakeWordCapabilities
```

`pendingActivations` ist streng nach `activationSequence` sortiert.

- Ein Client übernimmt nur Snapshots derselben `sessionId` mit höherer oder
  gleicher `stateVersion`.
- Eine Lücke in `eventSeq` hält die betroffene UI-Ableitung auf
  `resyncing`; der Client fordert einen Snapshot an und erfindet kein `idle`.
- Ein Reconnect erzeugt immer eine neue `sessionId` und beginnt serverseitig
  in `idle`. Eine alte Activation wird nicht resynchronisiert oder fortgesetzt.
- Der Client übergibt seine Suppressionsmaske aus derselben `clientRunId`
  atomar im neuen Handshake. Bei Programmneustart existiert eine neue
  `clientRunId` und keine alte Suppression.

## 8. Settings-Control-Plane

Jede serververwaltete Einstellung veröffentlicht:

```text
key, scope, auth, type, constraints, defaultValue,
requestedValue, effectiveValue, applyPolicy, settingsRevision
```

Scopes: `session`, `server`, `client_local`.

Apply-Policies: `live`, `next_activation`, `next_session`, `server_restart`.

### 8.1 Verbindliche Zuordnung

| Domäne | Scope | Auth | Apply |
|---|---|---|---|
| Activation-/VAD-/Watchdog-Timings | Session mit Serverdefault | Sessionrecht | `next_activation` |
| Wake-Word-Auswahl | Session | Sessionrecht | `next_session` |
| Wake-Word-Sensitivity | Session mit Serverdefault, 0.0–1.0, Default 0.5 | Sessionrecht | `next_activation` |
| Wake-Word-Cooldown/-Pre-Roll | Session mit Serverdefault | Sessionrecht | `next_activation` beziehungsweise `next_session`, falls Modellneuaufbau nötig |
| Runtime-Suppression Manual/Wake | Client-Laufzeit / Sessionabbild | Sessionrecht | `live` für neue Admission |
| globale Wake-Word-Disableliste und Katalogdefaults | Server | Admin-Key | neue Sessions |
| aktivierte STT-/Realtime-Modelle und Serverdefaults | Server | Admin-Key | veröffentlichte Policy |
| Hotkeys, Gerät, Mute, Feedback, Autostart, Textinjektion | Client lokal | lokal | clientabhängig |

Eine laufende Activation behält ihren beim Start bestätigten
`effectiveSettings`-Snapshot. Reconnectpflichtige Änderungen während einer
Activation werden clientseitig nur nach der bestätigten Dreifachauswahl
ausgeführt: sofort abbrechen, nach Eingabeschluss reconnecten oder bis zum
manuellen Reconnect vormerken.

Serverweite API-Zieloberfläche:

- `GET /api/v2/settings/schema` – öffentlich;
- `GET /api/v2/settings/server` – nicht geheime Werte und Effective Values;
- `PATCH /api/v2/settings/server` – `X-Admin-Key` erforderlich;
- `GET /api/v2/wake-words` – versionierter verfügbarer Build-Katalog.

Der Admin-Key liegt bei gewünschter Persistenz im Windows Credential Manager.
Die Client-UI kann ihn anlegen, ersetzen und löschen. `QSettings` enthält nur
nicht geheime Metadaten; Klartext-Fallback ist verboten.

## 9. Wake-Word-Contract

- Katalogeinträge besitzen `id`, `displayName`, explizite `aliases`,
  `artifactVersion`, `available`, optionalen `unavailableReason` und
  `catalogRevision`.
- Normalisierung ist Unicode-Trim plus case-insensitive Vergleich. Nur
  explizite Aliase dürfen Zusätze wie „Hey“ weglassen. Alias-Kollisionen sind
  ein Katalogfehler und werden nicht heuristisch aufgelöst.
- Sessionadmission ist atomar; jede unbekannte, deaktivierte oder nicht
  ladbare ID lehnt die ganze Auswahl maschinenlesbar ab.
- Nur angenommene Modelle werden für die Session initialisiert.
- Der erste akzeptierte Treffer setzt bis zum Eingabeschluss einen Latch und
  erzeugt genau ein `wakeword.detected` mit kanonischer ID und Score.
- Rohscores bleiben Diagnose und sind kein Domain-Ereignis.
- Eine zusätzliche Mehrfach-Chunk-Regel wird nur nach dem vorgesehenen
  Score-/Audio-Charakterisierungspaket aktiviert.
- Wake-Word-Audio selbst wird aus dem Nutztranskript ausgeschlossen;
  unmittelbar folgende Sprache bleibt durch die kalibrierte Audiogrenze
  erhalten.

## 10. Protokoll-Cut und Kompatibilität

- Desktop-Client und Server werden koordiniert auf Version 2 umgestellt.
- Version-1-/Legacy-Triggeradapter werden nicht im neuen Runtimepfad
  mitgeschleppt.
- Der Browserclient ist nicht Bestandteil dieses Arbeitsblocks.
- `docs/compatibility.md` führt Desktopversion, Clientcommit, Serverversion,
  Servercommit und unterstützte Protokollversionen.
- Inkompatibilität wird vor Sessionadmission verständlich gemeldet.

## 11. Verbindliche Recoveryregeln

- `closing_input` besitzt den Recovery-Timeout aus §4. Bei Ablauf wird Gate und
  Recorder defensiv geschlossen; jedes nicht sicher eingereihte Segment
  erhält `failed` oder `discarded` mit konkretem Grund, danach wird `idle`
  erreicht.
- Server-/Sessionverlust beendet die offene Activation und verwirft
  unveröffentlichte Resultate; bereits veröffentlichter Text bleibt.
- `audioAvailable=false` cancelt nur die offene Activation und lässt Session
  sowie Hintergrundledger bestehen.
- Kein Queue-Trim darf Audio ohne terminales Ledgerereignis entfernen.
- Ein verspäteter Timer, Ack, Jobcallback oder Event mit alter ID/Revision darf
  keinen neueren Zustand verändern.

## 12. Freeze-Kriterien

Für die Umsetzung gelten insbesondere:

1. `idle` und Hintergrund-`draining` dürfen gleichzeitig existieren.
2. Der Trigger-Lock hängt ausschließlich am offenen Vordergrundzustand.
3. Kein Finalresultat wird über den jeweils aktuellen Activation-Zeiger
   korreliert.
4. Segmentterminals sind vollständig und genau einmal vorhanden.
5. Resultatreihenfolge bleibt auch bei paralleler Inferenz deterministisch.
6. Commands und Events sind idempotent beziehungsweise deduplizierbar.
7. Snapshot und Reconnect erzeugen keine erfundene Fortsetzung.
8. Settings ändern keine bereits gestartete Activation rückwirkend.
9. Watchdog-Refresh verkürzt die Initialfrist nicht und kumuliert nicht.
10. Client-/Server-Inkompatibilität scheitert vor einer teilweise aktiven
    Session.
