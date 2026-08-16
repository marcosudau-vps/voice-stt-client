# Gezielter Untersuchungsauftrag – letzte offene Architekturfragen vor PLAN v1 FREEZE

Wir besitzen inzwischen:

- eine verbindliche Zielbildspezifikation;
- einen ausführlichen Diagnosebericht;
- eine Code-Only-Architekturaufnahme;
- einen Recovery-/Gate-Plan.

Die grundlegenden Architekturdefekte sind ausreichend bekannt.

**Dieser Auftrag ist ausdrücklich KEINE weitere breite Architekturuntersuchung.**

Untersuche ausschließlich die unten genannten offenen Punkte, die noch echte Implementierungsentscheidungen für den kommenden Umbau blockieren.

## Arbeitsbereich

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude
```

Relevant:

```text
voice-stt-server
voice-stt-client
led_controller_respeaker-v3
```

## Harte Regeln

Für diesen Auftrag:

- keine Produktcodeänderungen;
- keine Testcodeänderungen;
- keine Configänderungen;
- keine Dokumentationsänderungen;
- kein Commit;
- kein Push;
- kein Merge;
- kein Rebase;
- kein Tag;
- kein PR.

Du darfst:

- Produktivcode vollständig untersuchen;
- Tests ergänzend lesen;
- bestehende Tests ausführen;
- kleine rein diagnostische Skripte außerhalb der Repositories erzeugen;
- Callgraphs, Tabellen und Diagramme erstellen;
- vorhandene Zielbild-/Analyseunterlagen zur Einordnung lesen.

Wichtig:

> Bei technischen Aussagen ist der tatsächlich ausgeführte Produktivcode die primäre Ist-Quelle.

Bestehende Dokumentation oder Tests dürfen die Codeanalyse nicht ersetzen.

---

# FRAGE 1 – Wo liegt der fachlich korrekte Finalisierungszeitpunkt einer Activation?

Dies ist die wichtigste offene Frage.

Bekannter Stand:

```text
Activation
→ Recording
→ Segment
→ Transcription
→ finalizing
→ ???
→ finalized()
→ Idle
```

`ActivationController.finalized()` existiert, hat im derzeitigen Produktionscode aber offenbar keinen regulären Aufrufer.

Wir dürfen `finalized()` nicht einfach irgendwo anschließen, ohne den tatsächlichen Transkriptions-/Scheduler-Lifecycle vollständig verstanden zu haben.

## 1.1 Vollständigen Verarbeitungspfad rekonstruieren

Verfolge ein aufgenommenes Segment ab:

```text
recording_ended
```

vollständig durch:

```text
Recorder
→ Segment
→ InferenceJob / entsprechendes Jobmodell
→ Scheduler
→ Worker
→ Transcription
→ Result
→ final / terminal event
→ weitere Verarbeitung
```

Verwende die tatsächlichen Klassennamen des Codes.

Für jeden Übergang angeben:

- Repo;
- Datei;
- Klasse/Funktion;
- erzeugte IDs;
- Queue/Task/Scheduler;
- relevante Datenfelder;
- Terminalzustände;
- Fehlerzustände.

Erstelle ein Sequenzdiagramm.

---

## 1.2 ID-Zuordnung

Prüfe insbesondere, welche Zuordnungen heute tatsächlich existieren:

```text
sessionId
segmentId
activationId
jobId
generation
commandId
```

Erstelle eine Tabelle:

| Objekt/ID | entsteht wo | weitergereicht an | verfügbar beim Transkriptionsabschluss? |
|---|---|---|---|

Beantworte ausdrücklich:

> Ist `activationId` heute bereits zuverlässig bis zum Abschluss des Transkriptionsjobs verfügbar?

Falls nein:

> An welcher technisch sauberen Stelle müsste diese Zuordnung ergänzt werden?

Noch nichts ändern.

---

## 1.3 Mehrere Segmente innerhalb EINER Activation

Das Zielmodell erlaubt innerhalb derselben Activation mehrere Sprachsegmente / Follow-up.

Untersuche:

```text
Activation A
  Segment 1
  Segment 2
  Segment 3
```

und beantworte:

- Können mehrere Segmente gleichzeitig in Verarbeitung sein?
- Können Transkriptionsjobs in anderer Reihenfolge fertig werden?
- Kann `final` für Segment 1 eintreffen, während Segment 2 noch verarbeitet wird?
- Wo wird heute gezählt, welche Segmente noch offen sind?
- Gibt es bereits einen geeigneten Pending-/Reference-Count?
- Wie erkennt das System heute, dass **alle** für Activation A relevanten Arbeiten beendet sind?

Die entscheidende Frage:

> Welches reale Ereignis beziehungsweise welche Kombination von Bedingungen bedeutet sicher: „Diese Activation ist vollständig finalisiert und darf nach Idle wechseln“?

---

## 1.4 Finish / Cancel / Timeout

Den Ablauf getrennt untersuchen für:

### reguläres VAD-Ende
### explizites `finish`
### `cancel`
### Initial-Speech-Timeout
### Follow-up-Timeout
### Fehler der Transkription
### verworfener Job
### Worker-/Schedulerfehler

Für jeden Fall:

| Abschlussart | vorhandene Segmente? | Transkription läuft? | muss Result abgewartet werden? | gewünschter Finalized-Punkt |
|---|---:|---:|---:|---|

Keine Sollannahmen erfinden.

Wenn für eine Semantik eine Produktentscheidung nötig ist, als:

```text
ENTSCHEIDUNG ERFORDERLICH
```

markieren.

---

## 1.5 Ergebnis für Frage 1

Am Ende eine konkrete Empfehlung:

```text
Empfohlener Finalisierungspunkt:
<konkrete Funktion / Event / Condition>

Begründung:
...

Erforderliche minimale Verdrahtung:
...

Risiken:
...
```

Noch keine Implementierung.

---

# FRAGE 2 – Welcher Kanal soll die autoritative Activation-Wahrheit zum Client transportieren?

Heute existieren mindestens:

```text
/ws/transcribe
/ws/logs
```

und verschiedene Mechanismen wie:

```text
trigger_ack
timeline
status
final
activation.*
eventstream
replay
cursor
```

Wir müssen vor dem Client-`ActivationMirror` entscheiden, **welcher Kanal Runtime-Control-Plane und welcher Observability ist**.

---

## 2.1 Tatsächlichen heutigen Nachrichtenfluss inventarisieren

Erstelle für relevante Lifecycleinformationen:

| Information/Event | erzeugt Server wo | `/ws/transcribe` | `/ws/logs` | Client konsumiert heute | Reliability/Reconnect |
|---|---|---:|---:|---|---|

Mindestens:

- Activation startet;
- Waiting-for-Speech;
- Recording Start;
- Recording End;
- Follow-up;
- Finish;
- Cancel;
- Timeout;
- Finalizing;
- Finalized/Closed;
- Trigger suppressed;
- Trigger Ack;
- Serverstatus;
- Session Ready;
- Session Close.

---

## 2.2 `/ws/transcribe` als mögliche Control Plane

Prüfe:

- Nachrichtenreihenfolge;
- Verbindungslifetime;
- was bei Disconnect passiert;
- ob Commands und Acks geordnet genug sind;
- welche Activationinformationen dort bereits vorliegen;
- welche lediglich fehlen;
- welche Stateinformationen `hello`, `ready`, `status` oder Timeline bereits liefern.

Beantworte:

> Könnte `/ws/transcribe` mit einer kleinen, sauberen Ergänzung allein genügend autoritative Lifecycleinformation liefern, damit der Client seinen ActivationMirror darauf aufbaut?

Falls ja:

- welche konkreten Nachrichten/Statefelder fehlen?

---

## 2.3 `/ws/logs` als mögliche Runtime-Abhängigkeit

Untersuche:

- wofür `/ws/logs` ursprünglich gedacht ist;
- Replay/Cursor;
- Ausfallverhalten;
- Eventverluste;
- Reconnect;
- ob FeedbackController bereits funktional davon abhängt;
- ob UI-/Lifecycle-State davon abhängig gemacht werden sollte.

Ganz wichtig:

> Bewerte ausdrücklich, ob es architektonisch sinnvoll wäre, dass ein Ausfall der Logging-/Eventstream-Verbindung die Bedienlogik des Clients unbrauchbar macht.

---

## 2.4 State Snapshot / Resync

Wir wollen vermeiden, dass der Client bei einem verlorenen Event selbst „Idle“ erfindet.

Untersuche deshalb:

- existiert bereits ein autoritativer Session-/Activation-Snapshot?
- enthält `hello` bereits genug Informationen?
- könnte ein bestehendes Messageformat erweitert werden?
- existiert eine Statusabfrage?
- wie teuer wäre ein expliziter `activation_state`-/session-state Snapshot?

Betrachte:

```text
Connect
Reconnect
Event verloren
/ws/logs getrennt
/ws/transcribe getrennt
Settings Apply
```

und beantworte jeweils:

> Wie kann der Client danach sicher wieder die Serverwahrheit kennen?

---

## 2.5 Ergebnis für Frage 2

Gib eine klare Architekturentscheidungsempfehlung:

```text
Empfohlene Runtime-Control-Plane:
...

Rolle von /ws/logs:
...

Empfohlener State-Sync:
...

Erforderliche Protokolländerungen:
...
```

mit konkreten Vor- und Nachteilen.

---

# FRAGE 3 – Wie kann Wake Word pro Session pausiert werden, ohne den kontinuierlichen Stream zu stoppen?

Zielmodell:

```text
Client verbunden
→ Audio streamt kontinuierlich

sekundärer Wake-Word-Pause-Hotkey
→ Wake-Word-Erkennung dieser Session pausieren

Manual Trigger bleibt grundsätzlich unabhängig davon möglich.

Stream bleibt bestehen.
```

Der alte Mechanismus „Wake Word pausieren = Stream stoppen / Wake-Word-Modus disarmen“ darf mit Continuous Streaming nicht weiterverwendet werden.

---

## 3.1 Heutige Wake-Word-Aktivierung vollständig verfolgen

Untersuche:

- Session Admission;
- resolved wake-word config;
- Recorder;
- Wake-Word-Detector;
- Registry;
- `_on_wakeword_detected`;
- Runtimeflags;
- eventuell vorhandene Enable-/Disable-Mechanismen.

Liste alle Zustände/Felder, die heute bestimmen:

```text
Wake Word wird für Session ausgewertet: JA/NEIN
```

---

## 3.2 Vorhandene Runtime-Schnittstellen suchen

Prüfe gezielt, ob bereits etwas existiert wie:

```text
enable wake word
disable wake word
pause wake word
session config update
runtime config update
wake_word_enabled
/api/wake-word
```

Für jeden Fund:

- global oder pro Session?
- persistent oder runtime-only?
- WebSocket oder HTTP?
- wirkt er auf laufende Sessions?
- beeinflusst er Stream/Recorder?
- ist er für unseren Zweck geeignet?

---

## 3.3 Minimal sauberer Mechanismus

Falls keine passende Schnittstelle existiert:

Entwerfe **nur konzeptionell** die kleinste saubere Erweiterung.

Beispielsweise:

```text
Client
→ session control command
   wake_word_enabled=false
→ Server
→ Detector/Gate ignoriert Wake Words dieser Session
```

Aber nicht blind dieses Beispiel übernehmen.

Prüfe zuerst, wo diese Information am saubersten liegen müsste.

Anforderungen:

- per Session;
- kein Stream-Neustart;
- keine neue Activation;
- laufende Activation nicht beeinflussen;
- Manual Trigger nicht beeinflussen;
- reconnect-sicher;
- Status für Client auslesbar;
- idempotent.

---

## 3.4 Sonderfälle

Untersuche/definiere Entscheidungspunkte:

```text
Pause-Hotkey im Idle
Pause-Hotkey während Recording
Pause-Hotkey während Finalizing
Reconnect bei pausiertem Wake Word
Settings Apply
Wake-word trigger configured=false
```

Nicht implementieren.

---

## 3.5 Ergebnis für Frage 3

Liefern:

```text
Heutiger Mechanismus:
...

Wiederverwendbar:
JA/NEIN

Empfohlener per-Session Mechanismus:
...

Betroffene Komponenten:
...

Benötigte Contract-Erweiterung:
...
```

---

# FRAGE 4 – Ist `segment_active` bereits gegen Hängen abgesichert?

Aus der bisherigen Analyse:

```text
segment_active
```

hat im `ActivationController` offenbar selbst keine Deadline.

Gleichzeitig existiert serverseitig ein Recorder-/ForceFinalize-Mechanismus.

Wir müssen wissen, ob das bereits einen vollständigen Hängeschutz ergibt oder nur Teile des Recorderpfads absichert.

---

## 4.1 Recorder-/VAD-Abschluss rekonstruieren

Verfolge:

```text
recording_started
→ VAD
→ Speech End
→ Recorder Stop
→ recording_ended callback
→ ActivationController
```

und zusätzlich:

```text
Recorder/VAD hängt
→ ForceFinalize
→ ?
```

---

## 4.2 ForceFinalize genau analysieren

Beantworte:

- Wer startet den Timer?
- Wann?
- Welche Deadline?
- Welche Generation/Session/Activation schützt ihn?
- Welche Funktion wird ausgelöst?
- Stoppt er nur den Recorder?
- Erzeugt er garantiert `recording_ended`?
- Wird dadurch ActivationController sicher aus `segment_active` bewegt?
- Was passiert, wenn Callback verloren geht?
- Was passiert, wenn Recorder bereits beendet wurde?
- Ist der Vorgang idempotent?
- Gibt es Races mit normalem VAD-Ende?

---

## 4.3 Failure Matrix

Erstelle:

| Ausfall | heutiger Schutz | Ergebnis | kann Activation hängen? |
|---|---|---|---|
| VAD erkennt Ende nie | | | |
| Recorder stop callback fehlt | | | |
| ForceFinalize feuert | | | |
| ForceFinalize callback schlägt fehl | | | |
| Session schließt | | | |
| Client disconnected | | | |
| Server worker exception | | | |

---

## 4.4 Ergebnis für Frage 4

Klare Aussage:

```text
segment_active ist ausreichend abgesichert:
JA / NEIN / TEILWEISE
```

Falls NEIN/TEILWEISE:

- welche minimale zusätzliche Absicherung nötig wäre;
- wo sie hingehört;
- ob sie ActivationController, Recorder oder Session-Lifecycle besitzen sollte.

Noch nicht implementieren.

---

# FRAGE 5 – Verifikation der normalen Hotkey-Registrierung für Wake-Word-only

Hier besteht bereits eine wichtige Sollvorgabe, die in einem früheren Vorschlag leicht falsch umgesetzt werden könnte.

Ziel:

```text
manual=false
wake_word=true
```

muss bedeuten:

### Idle
normaler Hotkey startet **keine** Manual-Activation.

### Wenn Wake Word bereits eine Activation gestartet hat
normaler Hotkey muss **trotzdem verfügbar sein**, um diese bestehende Activation mit `finish` zu beenden.

Daraus folgt:

> Der normale Diktat-Hotkey darf nicht einfach komplett abregistriert werden, nur weil `manual_trigger_enabled=false` ist.

Untersuche den heutigen Registrierungs-/Dispatchpfad und beantworte:

- Wo werden globale Hotkeys registriert?
- Wovon hängt Registrierung heute ab?
- Kann ein registrierter Hotkey im Idle sauber als „keine Aktion“ behandelt werden, wenn Manual deaktiviert ist?
- Welche minimale Struktur erlaubt:
  - Idle + Manual disabled → kein Activate;
  - aktive Activation → Finish;
  - unabhängig von `primarySource`?

Nur analysieren.

---

# FRAGE 6 – Logging-Vorhaben: nur Integrationspunkte ermitteln, noch nicht designen

Es gibt separat die Überlegung, **vor der eigentlichen Migration eine Client-Logging-Komponente einzuführen**, um die kommenden Arbeiten und realen Laufzeitabläufe besser diagnostizieren zu können.

Ein ungeprüfter erster Entwurf liegt hier:

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude\.plan\.unverbindlich_ungeprueft\ErsterEntwurf_Logging.md
```

Für diesen Auftrag:

> Den Entwurf noch NICHT als Soll übernehmen und noch KEIN Logging implementieren.

Aber während der vier Untersuchungen bitte die natürlichen Beobachtungspunkte markieren.

Erstelle am Ende eine kleine Tabelle:

| Beobachtungspunkt | Repo/Komponente | vorhandene Daten | möglicher Client-Logging-Channel | darf Verhalten beeinflussen? |
|---|---|---|---|---|

Insbesondere interessante Punkte:

- Session/Connection;
- Audio/Stream;
- Trigger Commands/Acks;
- Activation Lifecycle;
- Recording/VAD;
- Transcription;
- Reconnect;
- Config/Settings;
- Feedback;
- Fehler/Warnings;
- Performance/Timing.

Dabei ausdrücklich markieren:

```text
OBSERVATION ONLY
```

für Stellen, an denen eine spätere Logging-Komponente **keine Runtime-Autorität und keinen Einfluss auf den Ablauf** bekommen darf.

Ziel ist nur, die spätere Logging-Architekturentscheidung mit belastbaren Integrationspunkten zu versorgen.

---

# Was NICHT erneut untersucht werden soll

Nicht noch einmal breit untersuchen:

- ob lokales Client-VAD entfernt ist;
- ob `mode` Runtime-Autorität besitzt;
- ob Source-Merge aktuell implementiert ist;
- ob Continuous Streaming aktuell fehlt;
- warum der weiße Ring hängen bleibt;
- warum der gelbe Warnloop entsteht;
- ob LED-Controller diese Fehler verursacht;
- ob Client und Server heute zwei Zustandswahrheiten besitzen;
- ob bestehende Tests teilweise das falsche Soll prüfen.

Diese Punkte gelten bereits als ausreichend geklärt.

Nur dann erneut darauf eingehen, wenn sie für eine der sechs konkreten Fragen unmittelbar relevant sind.

---

# Erwartete Ausgabe

Erstelle genau eine Datei:

```text
LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md
```

Struktur:

```text
1. FINALIZATION OWNERSHIP
2. RUNTIME CONTROL PLANE / STATE SYNC
3. WAKE WORD PAUSE ON CONTINUOUS STREAM
4. SEGMENT_ACTIVE / FORCE FINALIZE SAFETY
5. HOTKEY REGISTRATION IN WAKE-WORD-ONLY
6. LOGGING OBSERVATION HOOKS
7. REQUIRED ARCHITECTURE DECISIONS
8. PLAN UPDATES REQUIRED
9. IMPLEMENTATION BLOCKERS
```

Für jeden Punkt:

- Ist-Zustand;
- Codebelege;
- klare Schlussfolgerung;
- Empfehlung;
- offene Entscheidung, falls vorhanden.

## Abschlussklassifikation

Am Ende jede Frage klassifizieren:

```text
RESOLVED – Umsetzung kann geplant werden
DECISION REQUIRED – Produkt-/Architekturentscheidung nötig
FURTHER CODE INVESTIGATION REQUIRED – konkrete technische Information fehlt
```

Falls `FURTHER CODE INVESTIGATION REQUIRED`:

> exakt angeben, welche einzelne Information fehlt und wo weitergesucht werden müsste.

Keine Implementierung beginnen.

Keine neue breite Untersuchung starten.

Danach stoppen.