# SPEKULATIVE VORIMPLEMENTIERUNG – AP-SRV-040

## 1. Rolle

Du bist der ausführende Coding-Agent für eine **spekulative Vorimplementierung**
von `AP-SRV-040 – Protokoll v2, Handshake, Events und Snapshot`.

Das ist echte Produktcode-Arbeit mit echten Tests, aber **noch nicht die kanonische
AP-Ausführung** und **keine Root-Abnahme**.

Ziel: einen möglichst großen, sauber portierbaren Teil von SRV-040 jetzt bereits
fertigstellen, ohne sich an unsichere interne SRV-030-Details festzukleben.


## Gemeinsamer Referenzzustand

- Repository: `marcosudau-vps/voice-stt-server`
- Start-SHA: `db3d2b49539afbf4812d90e13f26f099b9314fe9`
- Start-Tree: `579d5f5dfb2e3a2ab4e7891cf1b233c7fa8422e3`
- C1 ist ein veröffentlichter, aber nicht final abgenommener AP-SRV-030-Candidate.
- Die kanonische SRV-030-Korrektur läuft getrennt.
- Dieser Prep-Branch darf C1 nicht amendieren und nicht pushen.

### Normative Quellen im Clientrepo – NUR LESEN

`P:\GithubRepos\marcosudau-vps\voice-stt-client\ARBEITSDATEIEN\10_AKTUELL\EINHEITLICHE_TRIGGERARCHITEKTUR\`

Mindestens vollständig lesen:

- `PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`
- `PLANUNG/ZIELBILD.md`
- `PLANUNG/TECHNISCHER_CONTRACT_FREEZE.md`
- `PLANUNG/PROTOKOLL_V2_WIRE_SCHEMA.md`
- `PLANUNG/VERTRAGSVEKTOREN/protocol-v2-vectors.json`
- `PLANUNG/IMPLEMENTIERUNGSPLAN.md`
- `NACHVERFOLGUNG/TRACEABILITY.md`
- `NACHVERFOLGUNG/FUNDE.md`

Serverseitig mindestens:

- `AGENTS.md`
- `docs/.archiv/README.md`
- `docs/einheitliche-triggerarchitektur.md`
- `docs/module-map.md`

Keine Clientdatei verändern.

Bei Widerspruch:
1. Frozen Contract / bestätigte Entscheidungen
2. Frozen Wire-Schema
3. Implementierungsplan
4. Code
5. Tests
6. alte Analysen

Tests können falsches Altsoll enthalten.


## 2. Arbeitsort / Git

Erwarteter Worktree:

```text
P:\GithubRepos\marcosudau-vps\voice-stt-server\workspaces\prep-srv-040
```

Erwarteter Branch:

```text
prep/AP-SRV-040/protocol-v2
```

Vor Änderungen:

```powershell
git branch --show-current
git rev-parse HEAD
git rev-parse HEAD^{tree}
git status --short
```

Erwartung:

```text
branch = prep/AP-SRV-040/protocol-v2
HEAD   = db3d2b49539afbf4812d90e13f26f099b9314fe9
tree   = 579d5f5dfb2e3a2ab4e7891cf1b233c7fa8422e3
working tree = clean
```

Bei Abweichung: `BLOCKED`.

Kein Rebase, Merge, Amend von C1 oder Push.
Keine neue venv.

## 3. Zielbild

SRV-040 macht den bereits eingefrorenen Domainvertrag über einen versionierten,
resynchronisierbaren v2-Wire-Pfad vollständig nutzbar.

Der heutige Server besitzt bereits ActivationController, Ledger, Commands,
Timer und Timeline-/Eventpfade. Diese Domainlogik darf **nicht** als zweite
Protokoll-State-Machine dupliziert werden.

Architektur:

```text
WebSocket transport
      ↓
Protocol-v2 parser / handshake / envelope validation
      ↓
schmaler Session-/Domain-Port
      ↓
bestehende SRV-030-Domainlogik
      ↓
Protocol-v2 event/snapshot projection
      ↓
WebSocket transport
```

Unsichere C1→final-SRV-030-Bindings müssen in einem kleinen Adapter/Port liegen.
Der Protokollkern selbst folgt dem Frozen Wire-Schema.

## 4. Nicht verhandelbare Wire-Regeln

### Allgemein

- UTF-8 JSON-Objekte.
- `camelCase` Felder.
- nach Handshake jede Nachricht mit `protocolVersion=2` und `sessionId`.
- Commands mit UUID `commandId`.
- Domain-Events mit `eventId`, `eventSeq`, `stateVersion`, `occurredAtUnixMs`.
- UUIDs kanonisch mit Bindestrichen.
- unbekannte additive Felder derselben Protokollversion ignorieren.
- unbekannte Nachrichtentypen nie als bekannte Zustandsänderung behandeln.

### Handshake

Erste Textnachricht exakt `hello`.

Pflicht:
- `supportedProtocolVersions`
- `clientVersion`
- `clientCommit`
- `clientRunId`
- `requestedSession.trigger.manual`
- `requestedSession.trigger.wakeWord`
- `requestedSession.wakeWordIds`
- `runtimeSuppression.manual`
- `runtimeSuppression.wakeWord`

Vor `hello.accepted`:
- kein Audio,
- keine manuelle Triggerannahme,
- keine Wake-Word-Admission.

Keine gemeinsame Version:
- `protocol.incompatible`
- keine `sessionId`
- Close 4406.

Ungültiges Handshake:
- Close 4400.

Handshake-Timeout:
- Close 4408.

Sessionadmission abgelehnt:
- `session.rejected`
- keine `sessionId`
- Close 4409.

Interner unerwarteter Fehler:
- 1011.

### Commands

`activation.command` besitzt genau zwei semantische Formen:

Activate:
```json
{
  "action": "activate",
  "source": "manual"
}
```

Control:
```json
{
  "action": "refresh|finish|cancel",
  "activationId": "..."
}
```

- Client darf `wake_word` nicht als Source behaupten.
- `activate` verbietet `activationId`.
- Control verlangt `activationId` und verbietet im finalen v2-Wire `source`.

Weitere Commands:
- `trigger_suppression.set`
- `audio_availability.set`
- `session_settings.patch`
- `session.snapshot.request`

Jeder syntaktisch erkennbare Command erhält genau ein `command.ack`.

Verbindliche Resultcodes:
- `applied`
- `no_change`
- `activation_locked`
- `not_active`
- `invalid_phase`
- `closing_input`
- `stale_session`
- `stale_activation`
- `command_id_conflict`
- `invalid_payload`
- `trigger_suppressed`
- `audio_unavailable`
- `settings_revision_conflict`
- `settings_rejected`
- `internal_error`

`accepted=true` nur für `applied|no_change`.

Replay desselben `commandId` + identischem semantischem Payload:
- byte-semantisch dasselbe Ack,
- keine zweite Wirkung.

### Domain-Events

Mindestens:
- `activation.started`
- `activation.phase_changed`
- `activation.input_closed`
- `activation.completed`
- `activation.cancelled`
- `activation.failed`
- `activation.trigger_suppressed`
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

`activation.input_closed` ist genau-einmal pro wirksamem Eingabeschluss und
nicht dasselbe wie das spätere Activationterminal.

`causedByCommandId`:
- finish/cancel → akzeptierte Command-ID,
- Timer/VAD/Watchdog/Gerät/Session/Recovery → `null`.

## 5. ProtocolSessionState

Führe eine klar verantwortete sessionlokale Protocol-v2-Zustandskomponente ein.

Sie besitzt mindestens:

```text
protocolVersion
sessionId
stateVersion
settingsRevision
nextEventSeq / lastEventSeq
```

Regeln:

- `eventSeq` streng monoton je Session.
- `eventId` einmal je logischem Domainereignis.
- Transportwiederholung erzeugt kein neues logisches Event.
- `stateVersion` steigt nur bei für den Client sichtbarer bestätigter Zustandsänderung.
- `settingsRevision` wird aus einem Adapter/Provider bezogen; nicht parallel zu SRV-050
  als zweite Settings-Control-Plane erfinden.

Nicht blind den internen `ActivationController.version` als vollständige Wire-
`stateVersion` wiederverwenden. Wire-State umfasst mehr als nur den Controller.

## 6. Parser / Encoder / Adapter

Bevorzuge kleine testbare Module unter `api_fastapi_server/`.

Zielaufteilung sinngemäß:

```text
protocol_v2/
  models/parser
  session_state
  events
  snapshot
  adapter/ports
```

Die genaue Dateiaufteilung darf dem Repo-Stil angepasst werden.

Nicht:
- 1000 weitere Zeilen direkt in `server.py`,
- zweite Activation-State-Machine,
- zweite Replayarchitektur,
- zweite Settings-Registry.

## 7. Handshake-State-Machine

Implementiere soweit realistisch integriert:

```text
CONNECTED
  ↓ hello
VALIDATING
  ↓
ACCEPTED
```

oder eindeutige äquivalente Zustände.

Sessionobjekt / Session-ID erst dann als angenommen betrachten, wenn die
Sessionauswahl vollständig validiert ist.

Der bestehende v1-Pfad darf in diesem Prep-Branch vorerst parallel bestehen.
**Legacyabbau gehört SRV-070.**

## 8. Command-Routing

Der v2-Layer validiert Envelope und Session-ID und delegiert fachliche Wirkung.

- Activation commands → vorhandener SRV-030-Command-/Controller-Port.
- `audio_availability.set` → vorhandene Audio-Availability-Policy.
- `trigger_suppression.set` → eigene kleine sessionlokale Policy, sofern noch nicht vorhanden.
- `session.snapshot.request` → Snapshot.
- `session_settings.patch` → klarer Port für SRV-050.

Für `session_settings.patch` keine neue Settingsarchitektur erfinden.
Ein testbarer Interface-/Adapterpunkt reicht, der später die SRV-050-Control-Plane aufruft.

## 9. Trigger-Suppression

Abbilden:

```text
configured
suppressed
effective
```

Effective je Source sinngemäß:
`configured && !suppressed`.

Runtime darf beide Sources gleichzeitig suppressen, obwohl persistente Basis mindestens
eine konfigurierte Quelle besitzen muss.

Suppression:
- neue Admission live beeinflussen,
- laufende Activation nicht rückwirkend umquellen oder beenden,
- Wake-/Manual getrennt.

## 10. Snapshot

Implementiere `session.snapshot` exakt gemäß Wire-Schema.

Pflichtstruktur:

```text
protocolVersion
serverVersion
serverCommit
sessionId
stateVersion
lastEventSeq
settingsRevision
input
pendingActivations
trigger
audioAvailable
effectiveSettings
wakeWordCapabilities
```

`input`:
```text
phase
activationId
primarySource
deadlineAtUnixMs
remainingMs
closeRequested
```

Idle:
- IDs/Deadline null,
- `closeRequested=false`.

`pendingActivations`:
- aus Ledger/Backgroundzustand,
- streng nach `activationSequence`,
- niemals aus globalem Current-Activation-Zeiger rekonstruieren.

Snapshot muss korrekt abbilden:
- `idle` mit null, einer oder mehreren drainenden alten Activations,
- offene Activation plus ältere Pendingactivations.

Monotone interne Timer bleiben Domainwahrheit.
`deadlineAtUnixMs`/`remainingMs` sind Projektion für Darstellung.

## 11. Eventprojection

Baue eine zentrale Eventfabrik/Projection.

Sie erhält Domainereignis + aktuelle ProtocolSessionState und erzeugt
das frozen v2-Event.

Keine Eventnamen frei erfinden.
Keine doppelten Events aus mehreren Legacy-Publishern erzeugen.

Observability-Korrelation:
`sessionId`, `activationId`, `segmentId`, `commandId`, `eventId`
mit der jeweiligen Funktion integrieren.

## 12. Vertragstestvektoren

`protocol-v2-vectors.json` ist direkt wiederzuverwenden.

Mindestens alle enthaltenen Positiv-/Negativvektoren automatisieren, darunter:

- `hello_v2`
- `manual_activate`
- `manual_activate_replay`
- `refresh_active_activation`
- `activation_started_event`
- `idle_snapshot`
- `wake_enabled_without_selection`
- `client_claims_wake_word`
- `activate_with_activation_id`
- `refresh_without_activation_id`
- `command_id_conflict`

Zusätzlich Pflicht:
- erste Nachricht nicht hello,
- ungültiges JSON,
- leere supported versions,
- keine gemeinsame Version,
- stale sessionId,
- unknown message type,
- additive unknown fields,
- EventSeq streng monoton,
- StateVersion nur bei sichtbarer Änderung,
- genau ein eventId je logischem Event,
- Snapshotrequest,
- Snapshot mit älteren Pendingactivations,
- kein Domaintraffic vor hello.accepted,
- inkompatibler Client erzeugt keine teilweise Session.

## 13. Integrationsgrenze zu noch unfertigem SRV-030

Bekannte C1-Rootkorrekturen laufen parallel.

Darum:
- keine neuen Annahmen über interne Close-/Lockmethoden;
- Events aus einem schmalen Domainadapter beziehen;
- Final-SRV-030 kann Methodennamen/Close-Orchestrierung ändern;
- Wiresemantik bleibt frozen.

Markiere Restbindungen im Bericht explizit als:

```text
REQUIRES_FINAL_SRV_030_BINDING
```

Nicht als TODO über die ganze Codebasis verteilen.

## 14. Nicht in diesem Prep-Paket

- echte SRV-050 Settings-Control-Plane;
- Wake-Word-Katalogumbau aus SRV-060;
- Legacy-Löschungen aus SRV-070;
- Clientcode;
- Browserclient.

## 15. Dokumentation

Produktdokumentation im Server so ergänzen, dass der neue v2-Pfad und seine
temporäre Koexistenz mit v1 klar beschrieben sind.

Keine kanonischen Gate-/Planungsdokumente im Clientrepo verändern.

Für diesen spekulativen Branch keine offizielle `ABNAHME.md`.

## 16. Validierung

Mindestens:
1. neue Protocol-v2-Unit-/Schema-/Vektortests,
2. relevante Server-Integrationstests,
3. vollständige Serversuite,
4. `git diff --check`.

Keine roten Tests mit „ist nur Prep“ entschuldigen.

Falls ein alter v1-Test durch reine Koexistenz unbeabsichtigt bricht:
Kompatibilität erhalten, solange SRV-070 nicht begonnen hat.

## 17. Commit

Genau ein lokaler Prep-Commit nach grüner Validierung.

Empfohlene Message:

```text
prep(protocol): implement speculative AP-SRV-040 v2 layer
```

Kein Push.

## 18. Abschlussbericht

Zurückgeben:

```text
STATUS
Branch
Start-SHA
Prep-SHA
Prep-Tree
Working Tree clean

Architektur
- neue Module
- Ownership
- Domainadapter

Fertig umgesetzt
- Handshake
- Commands
- Events
- Snapshot
- Suppression
- Tests

REQUIRES_FINAL_SRV_030_BINDING
- konkrete Stellen

Bewusst SRV-050/060/070 überlassen
- ...

Tests
- exakte Befehle
- counts
- full suite

Geänderte Dateien
git diff --check
Push: nein
```

Nach Bericht stoppen.
