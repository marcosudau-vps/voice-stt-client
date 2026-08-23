# EILAUFTRAG – verbleibende Opus-Zeit maximal für Architekturverständnis nutzen

Nutze die verbleibende Session **nicht für Implementierung**, sondern für eine möglichst vollständige, belastbare Rekonstruktion der tatsächlich implementierten Architektur.

Wir brauchen danach eine dauerhafte technische Grundlage, anhand derer die eigentliche Korrektur geplant und umgesetzt werden kann.

## WICHTIG: zunächst ausschließlich Code als Wahrheit

Für den ersten und wichtigsten Teil dieser Untersuchung:

**Lies keine bestehenden Architektur-, Plan-, Diagnose-, Status-, Report- oder Konzeptdokumente.**

Insbesondere zunächst nicht:

- bestehende `docs/*.md`
- Architekturpläne
- frühere Reports
- `STATUS.md`
- `VALIDATION.md`
- `CONTRACTS.md`
- Diagnosebericht
- Zielbildspezifikation
- frühere Soll-/Ist-Prüfungen
- Agenten-Handoffs

Rekonstruiere den Ist-Zustand **unabhängig aus dem tatsächlich ausgeführten Produktivcode**.

Tests dürfen später ergänzend betrachtet werden, aber ebenfalls **nicht als Wahrheit über die Architektur**. Wenn Testdouble und Produktivcode voneinander abweichen, gilt der Produktivcode.

Arbeitsbereich:

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude
```

Relevant:

```text
voice-stt-server
voice-stt-client
led_controller_respeaker-v3
```

Keine Produktcodeänderungen.

Keine Teständerungen.

Kein Commit, Push, Merge, Rebase oder PR.

Du darfst ausschließlich Analyseartefakte außerhalb des Produktcodes bzw. im dafür vorgesehenen Arbeits-/Zusammenarbeitsbereich erstellen.

---

# PHASE A – CODE-ONLY ARCHITECTURE BASELINE

Erstelle zunächst einen **vollständigen Ist-Zustand ohne Sollbewertung**.

Die Leitfrage lautet:

> Wenn ein neuer Entwickler ausschließlich den heutigen Produktivcode bekommt: Wie funktioniert dieses System tatsächlich?

Nicht erklären, wie es funktionieren sollte.

Erklären, wie es **wirklich implementiert ist**.

---

# 1. Gesamtsystem und Repository-Grenzen

Erstelle zuerst eine Übersicht:

```text
voice-stt-client
voice-stt-server
led_controller_respeaker-v3
```

Für jedes Repository:

- fachliche Verantwortung;
- Runtime-Verantwortung;
- Einstiegspunkte;
- langfristig laufende Prozesse/Threads/Tasks;
- Zustandsbesitzer;
- relevante öffentliche Schnittstellen;
- Beziehungen zu den anderen beiden Repositories.

Danach ein Mermaid-Gesamtschaubild:

```text
Benutzer
↓
Client UI / Hotkeys
↓
Client Controller
↓
Audio / WebSocket / Eventstream
↓
Server
↓
Activation / Recorder / VAD / Transcription
↓
Events
↓
Client Feedback
↓
Tray / Sound / LED
```

Aber ausschließlich anhand des tatsächlichen Codes.

---

# 2. Runtime-Start bis stabiler Idle-Zustand

Verfolge **vom echten Programmeinstieg aus** den vollständigen Startvorgang.

Client:

```text
app start
→ Config laden
→ UI
→ Controller
→ Hotkeys
→ Audio
→ WebSocket
→ Eventstream
→ Feedback
→ LED
→ stabiler Zustand
```

Server:

```text
Serverstart
→ Config
→ FastAPI
→ Modelle
→ WebSocket admission
→ Session
→ Recorder
→ ActivationController
→ Eventstream
→ stabiler Zustand
```

Für jeden Schritt:

- konkrete Datei;
- Klasse/Funktion;
- wer ruft wen auf;
- was wird erzeugt;
- welcher Zustand entsteht;
- welche Hintergrundtasks werden gestartet.

---

# 3. Concurrency Map – besonders wichtig

Ermittle vollständig, **was parallel läuft**.

Insbesondere:

- Python Threads;
- asyncio Tasks;
- Qt Threads/Signals;
- Audio Callback Threads;
- WebSocket receive/send loops;
- Eventstream;
- Recorder;
- VAD;
- Wake-Word-Erkennung;
- Transcription Worker;
- Timer;
- Scheduler;
- Feedback-/LED-Worker;
- Reconnect Tasks;
- Maintainer-/Watchdog-Loops.

Erstelle eine Tabelle:

| Task/Thread/Loop | Repo | Start | Ende | Owner | liest Zustand | schreibt Zustand | kommuniziert mit |
|---|---|---|---|---|---|---|---|

Danach ein Mermaid-Diagramm der wichtigsten parallel laufenden Komponenten.

Wir müssen erkennen können:

> Welche Abläufe können gleichzeitig gegeneinander laufen?

---

# 4. Vollständiger Audio-Datenpfad

Verfolge ein echtes Mikrofonpaket **Byte für Byte beziehungsweise logisch von Ursprung bis Verarbeitung**.

```text
Mikrofon
→ AudioCapture
→ Callback
→ Queue/Buffer
→ Sender
→ WebSocket
→ Server receive
→ Recorder / Gate
→ VAD
→ Transcription
→ Final
```

Dokumentiere:

- wann AudioCapture gestartet wird;
- wann es gestoppt wird;
- unter welchen Bedingungen Pakete verworfen werden;
- wann Audio über WebSocket geschickt wird;
- was `start` und `stop` technisch bedeuten;
- welche Buffer existieren;
- wo Preroll entsteht;
- wo VAD sitzt;
- wer entscheidet „Sprache beginnt“;
- wer entscheidet „Sprache endet“;
- wann Transcription startet;
- wie ein Segment abgeschlossen wird.

Ganz wichtig:

**Manual und Wake Word separat vom Eintritt bis zum ersten gemeinsamen Codepunkt verfolgen.**

Danach eindeutig angeben:

```text
Gemeinsamer Codepfad beginnt tatsächlich hier:
<konkrete Funktion>
```

oder:

```text
Es existiert kein vollständig gemeinsamer Codepfad.
```

---

# 5. Hotkey – vollständiger Ist-Ablauf

Verfolge den **normalen Hotkey** ausgehend vom echten globalen Hotkey-Callback.

Für jeden möglichen Zustand:

### Idle

```text
Hotkey
→ ?
→ ?
→ Server?
→ Audio?
→ Activation?
```

### Start läuft

```text
Hotkey
→ ?
```

### Activation/Recording aktiv

```text
Hotkey
→ ?
```

### Follow-up

```text
Hotkey
→ ?
```

### Finalizing

```text
Hotkey
→ ?
```

### Fehler / disconnected

```text
Hotkey
→ ?
```

Dabei jede Entscheidung dokumentieren:

```python
if ...
elif ...
```

insbesondere alle Abhängigkeiten von:

- `mode`;
- Triggerflags;
- `_dictation_requested`;
- `DictationState`;
- Window Phase;
- Streaming State;
- Activation State;
- Server Capability.

Erstelle anschließend ein Hotkey-State-Diagramm des **Ist-Zustands**.

---

# 6. Wake Word – vollständiger Ist-Ablauf

Dasselbe für Wake Word.

Beginne beim kontinuierlichen bzw. tatsächlichen Audiopfad und verfolge:

```text
Audio
→ Wake Word Detector
→ Callback
→ Serverlogik
→ ActivationController
→ Recorder Gate
→ Recording
→ Follow-up
→ Finalisierung
```

Zusätzlich clientseitig untersuchen:

- `_wake_mode_desired`;
- Wake-Word-Maintainer;
- welche Commands der Client sendet;
- wodurch Wake Word „armed“ wird;
- wodurch es deaktiviert wird;
- welche Rolle `mode` spielt;
- welche Rolle Triggerflags spielen.

Danach Ist-State-Diagramm erstellen.

---

# 7. Manual vs Wake Word – struktureller Vergleich

Erstelle danach eine **Side-by-Side-Tabelle**:

| Phase | Manual heute | Wake Word heute | gemeinsam? |
|---|---|---|---|
| Streamaufbau | | | |
| Mikrofonstart | | | |
| Trigger | | | |
| Activation | | | |
| Gate | | | |
| VAD | | | |
| Recording | | | |
| Recording-Ende | | | |
| Follow-up | | | |
| Finalisierung | | | |
| UI-State | | | |
| Feedback | | | |
| Cleanup | | | |

Das ist eine der wichtigsten Ausgaben.

---

# 8. Serverseitiger ActivationController vollständig dokumentieren

Nicht nur State-Namen.

Für **jede öffentliche und relevante interne Methode**:

- Eingaben;
- erlaubte Ausgangszustände;
- Zustandsänderung;
- Side Effects;
- Events;
- Timer;
- Gate-Aufrufe;
- Rückgabewerte;
- Ablehnungsgründe.

Insbesondere:

```text
activate
extend
finish
cancel
expire
recording_started
recording_ended
finalized
reset
```

Erstelle:

1. State Transition Table;
2. Mermaid State Diagram;
3. Command Matrix.

Beispiel:

| Phase | activate | extend | finish | cancel | recording_started | recording_ended |
|---|---|---|---|---|---|---|

Keine Sollbewertung in Phase A.

---

# 9. Clientseitige State Machines vollständig inventarisieren

Suche alle Zustände, die fachlich etwas über Diktat, Aufnahme, Server, Stream oder Activation aussagen.

Zum Beispiel:

```text
DictationState
DictationWindowPhase
availability_state
connection state
streaming_requested
server_status
wake_mode_desired
dictation_requested
pending trigger state
feedback state
```

Für jeden:

- Owner;
- Schreibstellen;
- Lesestellen;
- Zweck;
- Quelle der Wahrheit;
- Lebensdauer;
- Resetpfade.

Danach eine **Authority Matrix**:

| Information | Server hält Zustand | Client hält Zustand | UI liest | Wer gewinnt bei Widerspruch? |
|---|---:|---:|---|---|

Wir müssen danach exakt erkennen können, wo doppelte Wahrheiten existieren.

---

# 10. Event- und Command-Architektur

Erstelle ein vollständiges Inventar aller relevanten Nachrichten zwischen Client und Server.

## Client → Server

Zum Beispiel:

```text
start
stop
trigger activate
trigger extend
trigger finish
trigger cancel
audio binary
...
```

Für jede:

- Sender;
- Empfänger;
- wann gesendet;
- erforderlicher Zustand;
- Ack;
- Side Effects.

## Server → Client

Inventarisiere:

```text
hello
ready
trigger_ack
recording_started
recording_ended
final
activation.*
wakeword.*
timeout.*
feedbackrelevante Events
...
```

Unterscheide:

- Haupt-WebSocket;
- `/ws/logs`;
- Timeline/Eventstream;
- Replay;
- sonstige Kanäle.

Erstelle ein Diagramm:

```text
Command
→ Ack
→ State Transition
→ Event
→ Client Mirror/UI/Feedback
```

Besonders markieren:

> Events, die produziert, aber nicht konsumiert werden.

und:

> Zustände, die clientseitig erwartet werden, für die kein Serverevent existiert.

---

# 11. Vollständiger Ablauf eines echten Diktats

Erstelle mindestens diese Sequenzdiagramme des **heutigen Codes**:

### A. Manual – normaler Ablauf

```text
Idle
→ Hotkey
→ Sprache
→ VAD-Ende
→ Final
→ ...
```

bis zum tatsächlich erreichten Endzustand.

### B. Wake Word – normaler Ablauf

```text
Idle
→ Wake Word
→ Sprache
→ VAD-Ende
→ Final
→ ...
```

### C. Manual ohne Sprache

### D. Wake Word ohne Sprache

### E. Hotkey während laufender Manual-Activation

### F. Hotkey während Wake-Word-Activation

### G. Wake Word während Manual-Activation

### H. zweites Wake Word während Wake-Word-Activation

### I. Manual und Wake Word nahezu gleichzeitig

### J. Reconnect während laufender Activation

Für jeden Ablauf:

- Clientzustand;
- Serverzustand;
- Audiozustand;
- Activation-ID;
- relevante Timer;
- Commands;
- Events.

---

# 12. Timer- und Timeout-Inventar

Erstelle eine zentrale Tabelle aller Timer:

| Timer | Repo | Owner | Startbedingung | Deadline | Callback | Cancel-Bedingung | Generation Guard |
|---|---|---|---|---|---|---|---|

Insbesondere:

- initial speech;
- follow-up;
- extension;
- warning;
- activation expiration;
- ack timeout;
- reconnect;
- maintenance loops;
- feedback durations.

Danach beantworten:

> Welcher Zustand kann theoretisch unbegrenzt bestehen bleiben?

Nicht nur anhand von Namen – anhand aller tatsächlichen Exitpfade.

---

# 13. Config-Datenfluss

Verfolge jede für diese Architektur relevante Konfiguration von:

```text
config.yaml
→ Dataclass
→ Migration
→ Settings Metadata
→ Settings Dialog
→ Apply
→ RuntimeConfig
→ WebSocket Query
→ Server Admission
→ Resolved Session Config
```

Mindestens:

```text
mode
manual_trigger_enabled
wake_word_trigger_enabled
wake_words
wake_word_sensitivity
initial_speech_timeout
followup_timeout
extension
hotkeys
feedback config
```

Für jedes Feld:

| Feld | Quelle | Default | Migration | UI | Persistenz | Runtime Consumer | Serverwirkung |
|---|---|---|---|---|---|---|---|

Besonders:

> Alle Stellen dokumentieren, an denen zwei Configfelder dieselbe fachliche Entscheidung beeinflussen.

---

# 14. UI-/Tray-/Feedback-Datenfluss

Für folgende sichtbare Zustände zurückverfolgen, **woher sie tatsächlich kommen**:

- grüner Ring;
- blauer Ring;
- weißer Ring;
- gelbes Warnblinken;
- „Wartet auf Hotkey“;
- „Wartet auf Wake Word“;
- „Wartet auf Sprache“;
- „Sprache wird aufgenommen“;
- „Diktat starten“;
- „Diktat verlängern“;
- „Wake Word pausieren“;
- „Aktion derzeit nicht verfügbar“.

Für jeden:

```text
Serverzustand?
→ Event?
→ Controllerfeld?
→ Presentation?
→ Tray/Overlay/LED/Sound?
```

Damit muss erkennbar werden, ob die Darstellung auf:

- Serverwahrheit;
- lokaler Clientwahrheit;
- `mode`;
- Triggerquelle;
- Feedbackimpuls

beruht.

---

# 15. LED-Controller-Grenze

Beim LED-Repository nur feststellen:

- welche öffentliche API der Client tatsächlich benutzt;
- welche Effekte/States/Events relevant sind;
- ob das LED-Repo irgendeine fachliche Trigger-/Activation-Entscheidung trifft;
- welche Teile reine Darstellung sind.

Keine unnötige Detailanalyse der Effektengine, wenn sie für die Triggerarchitektur irrelevant ist.

---

# 16. Dead Code / Halb entfernte Architektur

Suche besonders nach Komponenten, die:

- noch existieren, aber keine vollständigen Aufrufer mehr besitzen;
- noch Zustand schreiben, der niemanden mehr sinnvoll steuert;
- noch gelesen werden, obwohl ihre ursprüngliche Authority entfernt wurde;
- nur in Tests benutzt werden;
- nur durch Legacy-Mode erreichbar sind;
- parallel zu einem neuen Mechanismus existieren.

Kategorisieren:

```text
ACTIVE
PARTIALLY DISCONNECTED
DEAD
COMPATIBILITY
UNKNOWN
```

Das ist besonders wichtig für die halb entfernte Hotkey-Architektur.

---

# 17. Produktionscode vs Testdoubles

Erst nachdem die Codearchitektur vollständig rekonstruiert ist:

Untersuche die wichtigsten Testdoubles.

Für jedes relevante Double:

```text
STTSession
AudioCapture
Recorder
Scheduler
Eventstream
ActivationController
```

prüfen:

> Verhält sich das Double an den Architekturgrenzen wie die Produktionsklasse?

Erstelle nur die Abweichungen.

Wir brauchen eine Liste:

```text
Test sieht grün aus, weil Double X Produktionsverhalten Y nicht abbildet.
```

---

# PHASE B – Erst danach Soll/Ist-Vergleich

**Erst wenn PHASE A vollständig dokumentiert ist**, darfst du lesen:

```text
.claude/ZIELBILD_EINHEITLICHE_TRIGGERARCHITEKTUR.md
```

Danach keinen zweiten Diagnosebericht schreiben, sondern eine präzise **Migration Map**:

| Ist-Komponente | Sollrolle | behalten | umbauen | entfernen | Grund |
|---|---|---:|---:|---:|---|

Wichtig:

- Welche guten neuen Komponenten können unverändert bleiben?
- Welche Komponenten sind strukturell richtig, nur falsch verdrahtet?
- Welche Altkomponenten müssen vollständig weg?
- Welche Schnittstellen müssen sich ändern?
- Welche Zustände müssen zusammengeführt werden?
- Welche neuen Events/Commands fehlen?
- Welche Tests müssen bewusst ersetzt werden, weil sie das falsche Soll festschreiben?

---

# PHASE C – Reparaturwissen für den nächsten Agenten

Zum Abschluss beantworte kompakt die Frage:

> Welche Informationen muss ein Implementierungsagent unbedingt verstanden haben, bevor er dieses System sicher umbauen darf?

Erstelle daraus eine **Implementation Prerequisites Checklist**.

Beispielsweise:

```text
[ ] tatsächlicher Stream-Lifecycle verstanden
[ ] Server-Activation-State-Machine verstanden
[ ] Client-State-Authorities verstanden
[ ] Event-/Commandpfade verstanden
[ ] Timerbesitzer verstanden
[ ] Configmigration verstanden
[ ] UI-Zustandsherkunft verstanden
[ ] Legacy-/Dead-Code-Grenzen verstanden
[ ] Testdouble-Abweichungen verstanden
```

---

# Zu erstellende Artefakte

Speichere die Ergebnisse als getrennte Dateien:

```text
CODE_ARCHITECTURE_BASELINE.md
RUNTIME_FLOWS_AND_CONCURRENCY.md
STATE_EVENT_COMMAND_ATLAS.md
CONFIG_UI_FEEDBACK_ATLAS.md
LEGACY_AND_DEAD_CODE_MAP.md
TARGET_MIGRATION_MAP.md
IMPLEMENTATION_PREREQUISITES.md
```

Bevorzugt im vorhandenen Arbeits-/Zusammenarbeitsbereich für diese Aktion, **nicht in den drei Produkt-Repositories**, sofern dort kein bereits dafür vorgesehener Analyseordner existiert.

---

# Qualitätsanforderung

Keine vagen Formulierungen wie:

```text
„scheint“
„wahrscheinlich“
„dürfte“
```

wenn der Code die Antwort hergibt.

Jede wichtige Aussage möglichst mit:

```text
Repo
Datei
Klasse/Funktion
relevanter Codepfad
```

belegen.

Bei Unsicherheit ausdrücklich:

```text
UNGEKLÄRT
```

und beschreiben, welche konkrete Information fehlt.

---

# LIMIT-/ZEIT-SICHERUNG

Die verbleibende hochwertige Modellzeit ist wertvoll.

Falls absehbar ist, dass das Limit erreicht wird:

1. keine begonnenen Erkenntnisse nur im Kontext lassen;
2. alle bis dahin gewonnenen Informationen sofort in die Artefakte schreiben;
3. `IMPLEMENTATION_PREREQUISITES.md` beziehungsweise einen Checkpoint aktualisieren;
4. festhalten:
   - vollständig untersucht;
   - teilweise untersucht;
   - noch offen;
   - nächster sinnvoller Einstiegspunkt.

**Breite und belastbare Architekturkenntnis ist für diesen Auftrag wichtiger als perfekte Formulierungen.**

Keine Implementierung beginnen.

Jetzt sofort mit der CODE-ONLY-Rekonstruktion starten.