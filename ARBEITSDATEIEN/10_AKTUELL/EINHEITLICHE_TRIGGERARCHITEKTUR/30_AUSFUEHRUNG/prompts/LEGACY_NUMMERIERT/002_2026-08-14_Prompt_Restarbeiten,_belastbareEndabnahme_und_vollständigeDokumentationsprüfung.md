Die bisherige Arbeit ist qualitativ deutlich besser abgesichert als der vorherige Stand. Insbesondere die Mutationstests, die Untersuchung eigener False Positives und die vorsichtige Kennzeichnung nicht real durchgeführter Tests sind genau richtig.

Ich möchte den Stand trotzdem **noch nicht final abnehmen**, weil bei der Gegenprüfung der Abschlussdokumentation einige konkrete Nachweislücken beziehungsweise Statusinkonsistenzen aufgefallen sind.

Bitte arbeite diese Punkte jetzt gezielt ab und führe anschließend noch eine vollständige Dokumentationsprüfung über **alle drei Repositories** durch.

Die bisherigen Regeln gelten unverändert:

**NICHT COMMITTEN. NICHT PUSHEN. KEIN MERGE. KEIN REBASE. KEIN PR.**

Alle Änderungen bleiben uncommitted.

# 1. GATE 4 – Kollisionsmatrix vollständig nachweisen

Der bisherige Server-E2E-Nachweis ist inzwischen deutlich stärker, erfüllt aber noch nicht vollständig die ursprünglich verlangte Kollisionsmatrix.

Für diese drei Fälle müssen getrennte echte E2E-Nachweise existieren:

```text
Manual → Wake Word
Wake Word → Manual
nahezu simultan
```

Für **jeden einzelnen Fall** muss konkret nachgewiesen werden:

```text
Activations = 1
Segments = 1
Finals = 1
Scheduler allocations = 1
```

Zusätzlich prüfen und protokollieren:

```text
activationId
primarySource
sources
segmentId
Recording-Start-Anzahl
Final-Anzahl
```

Wichtig:

Ein reiner `ActivationController`-Concurrency-Test ersetzt den dritten E2E-Fall „nahezu simultan“ nicht.

Ebenso reicht es nicht, nur nachzuweisen, dass genau eine Activation und ein Recording entstehen. Gerade doppelte Segmente, Finals oder Scheduler-/Timer-Allokationen gehören zu den zentralen Risiken dieser Architektur.

Falls aktuell keine geeignete Instrumentierung für `Scheduler allocations` existiert, ergänze eine testgeeignete, möglichst nicht-invasive Möglichkeit, diese Invariante eindeutig nachzuweisen.

Erst danach darf GATE 4 endgültig PASS sein.

---

# 2. AP7 / Client-Lifecycle – Continuous Streaming ausdrücklich beweisen

Die bisherige Client-Lifecycle-Arbeit sieht grundsätzlich plausibel aus:

- `start` / `stop` wieder als Stream-/Sessionbefehle;
- Trigger additiv;
- `trigger_ack`;
- Pending-Command-Verwaltung;
- Reconnect;
- Generation;
- Removal beziehungsweise Einschränkung alter Client-Autoritäten.

Was mir noch fehlt, ist ein **expliziter Nachweis der zentralen Zielinvariante**:

> Eine Session besitzt einen kontinuierlichen Audiostream, während mehrere Activations unabhängig davon stattfinden können.

Ergänze einen belastbaren Lifecycle-/Integrationstest, der mindestens sinngemäß beweist:

```text
Session verbinden
→ Stream genau einmal starten

Activation 1
→ Recording / Final / Finish

Activation 2
→ Recording / Final / Finish

währenddessen:
Stream-Start-Anzahl bleibt 1
Stream-Stop-Anzahl bleibt 0

erst beim echten Session-/Streamende:
Stream-Stop-Anzahl = 1
```

Zusätzlich prüfen:

- Hotkey-Aktivierung darf den Audiostream nicht pro Dictation neu erzeugen.
- Wake-Word-Aktivierung ebenso nicht.
- Finish beendet die Activation, nicht den Stream.
- Cancel beendet die Activation, nicht versehentlich die Session.
- Follow-up / Extend erzeugen keinen zweiten Stream.
- Reconnect besitzt eine klar definierte neue Stream-/Session-Lebensdauer.
- Legacy-Verhalten bleibt dort erhalten, wo es vertraglich noch unterstützt werden muss.

Der Test soll den **realen Produktionspfad** der betroffenen Clientkomponenten benutzen und nicht nur interne Flags setzen.

Erst danach ist das zentrale AP7-Ziel „continuous streaming“ tatsächlich bewiesen.

---

# 3. GATE 5 – Kompatibilitätsstatus korrigieren beziehungsweise vollständig herstellen

In der bisherigen Validierung wird GATE 5 teilweise als PASS beschrieben, obwohl gleichzeitig dokumentiert ist, dass der mitgelieferte Browserclient derzeit nicht erfolgreich gegen den vorgesehenen Serverpfad nachgewiesen wurde.

Das ist mit unserer Gate-Semantik nicht vereinbar.

Ein Gate ist entweder vollständig bestanden oder nicht.

Bitte prüfe den Originalauftrag erneut und arbeite die dort definierten Anforderungen vollständig ab.

Insbesondere:

- Legacy-Desktopclient gegen neuen Server;
- Browserclient gegen neuen Server;
- `start`;
- `stop`;
- Capability-Vertrag;
- `trigger`;
- `trigger_ack`;
- Eventstream;
- Replay;
- Serverregression;
- produktionsnaher Smoke-Test soweit autonom möglich.

Wenn der Browserclient tatsächlich eine falsche WebSocket-URL beziehungsweise einen nicht existierenden Serverpfad verwendet und er laut Originalauftrag Teil dieses Kompatibilitätsgates ist, darf dies nicht nur als „vorbestehender Fehler“ dokumentiert werden.

Dann gilt:

> Entweder innerhalb des vorgesehenen Scopes korrekt herstellen und testen oder das Gate nicht als PASS markieren.

Falls für einen Teil echte Benutzerinteraktion notwendig ist:

```text
MANUAL VALIDATION REQUIRED
```

statt PASS.

---

# 4. GATE 8 – Feedback-/LEFX-Abnahme korrekt kennzeichnen

Prüfe noch einmal exakt die Kriterien des ursprünglichen Auftrags.

Falls dort sowohl:

- Simulator
- als auch echter ReSpeaker

als Bestandteil der Abnahme verlangt werden, darf ein ausschließlich automatisierter Softwaretest nicht zu einem vollständigen GATE-8-PASS führen.

Die Softwarekette kann selbstverständlich als verifiziert dokumentiert werden:

```text
Server Event
→ Eventstream
→ Client
→ Normalizer
→ Dedupe
→ Reducer
→ Mapping
→ Sound / LEFX
```

Aber nicht tatsächlich durchgeführte Hardwaretests müssen korrekt als:

```text
MANUAL VALIDATION REQUIRED
```

gekennzeichnet werden.

Keine reale Hardware-Evidence behaupten, wenn keine reale Hardware verwendet wurde.

---

# 5. GATE 9 – vollständige Regression wirklich grün herstellen

Der bisherige Stand war:

```text
voice-stt-server: vollständig grün
voice-stt-client: vollständig grün
led_controller_respeaker-v3: 1500 passed, 6 failed, 23 skipped
```

Die sechs LED-Fehler wurden als vorbestehend und durch fehlende `.lefxset`-Artefakte erklärt.

Später wurde für den Build jedoch ein Verfahren verwendet, mit dem diese benötigten Effektartefakte im eigenen Claude-Arbeitsbereich korrekt erzeugt werden können.

Nutze deshalb diesen inzwischen bekannten reproduzierbaren Setup-Pfad und führe die **vollständige LED-Testsuite noch einmal in einem korrekt vorbereiteten Claude-Environment** aus.

Ziel:

```text
Server: vollständige aktuelle Suite grün
Client: vollständige aktuelle Suite grün
LED: vollständige aktuelle Suite grün
```

Falls danach weiterhin Fehler bestehen:

- nicht wegklassifizieren;
- Root Cause untersuchen;
- gegen Baseline und Auftrag bewerten;
- Gate entsprechend FAIL oder PARTIAL lassen.

Eine „vollständige Regression PASS“ soll diesmal tatsächlich bedeuten:

> Die vollständigen für den Auftrag relevanten Suites laufen im korrekt vorbereiteten Environment ohne Fehler.

Skipped Tests selbstverständlich separat dokumentieren.

---

# 6. Gate-Status insgesamt noch einmal streng prüfen

Nach diesen Restarbeiten gehe sämtliche Gates noch einmal gegen den **ursprünglichen normativen Auftrag** durch.

Verwende ausschließlich:

```text
PASS
FAIL
MANUAL VALIDATION REQUIRED
```

Kein:

```text
PASS für den automatisierbaren Teil
```

wenn das Gate selbst zusätzliche noch offene Kriterien besitzt.

PASS bedeutet:

> Alle verbindlichen Kriterien dieses Gates sind erfüllt und nachgewiesen.

Wenn reale Benutzer-/Hardwaretests fehlen:

> MANUAL VALIDATION REQUIRED.

Wenn technisch noch etwas fehlt:

> FAIL beziehungsweise Gate noch offen.

---

# 7. PLAN / STATUS / VALIDATION / REPORT vollständig synchronisieren

Die Abschlussdokumente enthalten noch einzelne Statusabweichungen beziehungsweise alte Arbeitsstände.

Bitte gleiche insbesondere ab:

```text
PLAN.md
STATUS.md
VALIDATION.md
CONTRACTS.md
DECISIONS.md
REPORT.md
```

Es darf am Ende nicht beispielsweise:

- ein AP in `PLAN.md` noch als offen erscheinen,
- während `VALIDATION.md` PASS meldet;
- `STATUS.md` einen anderen Fortschritt nennen als `REPORT.md`;
- ein Gate in einem Dokument PASS und in einem anderen offen sein.

Die Dokumente müssen denselben tatsächlichen Zustand beschreiben.

---

# 8. Anschließend: vollständiger Dokumentationsaudit über ALLE DREI REPOSITORIES

Nachdem die technischen Restarbeiten abgeschlossen und validiert sind, führe zusätzlich eine **systematische Dokumentationsprüfung in allen drei Repositories** durch:

```text
voice-stt-server
voice-stt-client
led_controller_respeaker-v3
```

Diese Prüfung betrifft ausdrücklich nicht nur die zentralen Abschlussdokumente, sondern die **gesamte relevante Produkt- und Entwicklerdokumentation** innerhalb der Repositories.

Ziel:

> Nach diesem Umbau darf keine aktive Dokumentation mehr die alte Architektur als aktuellen Zustand beschreiben.

---

# 9. Suche gezielt nach veralteten Architekturaussagen

Durchsuche README-, Docs-, Guides-, Markdown-, Beispiel-, Konfigurations- und relevante Kommentar-/Docstring-Dokumentation nach Aussagen zur alten Architektur.

Besonders auf folgende Themen achten:

```text
session.mode
hotkey-only / wake-word-only Mode
separate Hotkey- und Wakeword-Sessions
clientseitige Dictation-Autorität
start/stop als Activation-Steuerung
alter Wakeword-Follow-up
alte Triggersemantik
fehlender trigger_ack
alte Queryparameter
alte Capability-Struktur
alte Eventnamen
alte Konfigurationsnamen
alte Lifecycle-Diagramme
alte Reconnect-Semantik
alte Feedback-/LEFX-Verträge
```

Nicht mechanisch Texte ersetzen.

Jede Stelle gegen den tatsächlichen aktuellen Code prüfen.

Wenn eine alte Information absichtlich noch für Legacy gilt, klar als **Legacy-Verhalten** kennzeichnen statt sie zu löschen.

---

# 10. Neue Architektur vollständig und verständlich dokumentieren

Die neue Architektur soll nicht nur korrekt, sondern auch für einen Entwickler nachvollziehbar erklärt sein.

Mindestens dokumentieren:

## Gesamtarchitektur

```text
eine Client-Session
→ kontinuierlicher Audiostream
→ serverautoritatives Activation-Modell
→ Manual und Wake Word als gleichwertige Triggerquellen
→ gemeinsamer Recorder-/VAD-/Transkriptionspfad
```

## Trigger-Lifecycle

```text
activate
extend
finish
cancel
```

inklusive:

```text
commandId
trigger_ack
activationId
generation/version
primarySource
sources
```

## Controlled Recorder Gate

- wer es öffnet;
- wer es schließt;
- warum Wake Word es nicht umgehen darf;
- Generation-/Activation-Schutz.

## ActivationController

- Zustände;
- Transitionen;
- Follow-up;
- Timeout;
- Finish;
- Cancel;
- Generation;
- monotone Deadline.

## Client Lifecycle

- Sessionstart;
- Streamstart;
- Activation;
- mehrere Activations innerhalb derselben Session;
- Reconnect;
- Sessionende;
- Legacy-Fallback.

## Konfiguration

Die kanonischen aktuellen Parameter:

```text
manualTriggerEnabled
wakeWordTriggerEnabled
initialSpeechTimeout
followupTimeout
extensionSeconds
```

inklusive Migration und ungültiger Kombinationen.

## Capability-Vertrag

Wann und wie der Client erkennt, ob Activation Triggers unterstützt werden.

## Trigger-Ack-Vertrag

Request/Ack-Beispiele und Fehler-/Duplicate-Semantik.

## Kollisionsverhalten

Insbesondere:

```text
Manual → Wake Word
Wake Word → Manual
simultan
```

und warum daraus jeweils nur eine Activation entsteht.

## Event-/Feedbackfluss

Soweit repositoryübergreifend relevant:

```text
Server
→ Eventstream
→ Client
→ Normalizer
→ Reducer
→ Mapping
→ Sound / LEFX
→ ReSpeaker
```

## Legacy-Kompatibilität

Klar trennen zwischen:

```text
aktueller bevorzugter Architektur
```

und

```text
bewusst weiterhin unterstütztem Legacy-Pfad
```

---

# 11. Anschauliche Diagramme verwenden

Für komplexe Abläufe bitte nicht ausschließlich Fließtext verwenden.

Wo sinnvoll, aktualisiere beziehungsweise ergänze Mermaid-Diagramme.

Mindestens sinnvoll sind:

### Architekturübersicht

```text
Client
→ Stream
→ Server Session
→ ActivationController
→ Controlled Gate
→ Recorder/VAD
→ Transcription
```

### Sequence Diagram – Manual Trigger

```text
Hotkey
→ Controller
→ STTSession
→ Server
→ ActivationController
→ Recorder
→ Ack/Event/Final
```

### Sequence Diagram – Wake Word

### Sequence Diagram – Manual/Wake-Word-Kollision

### State Diagram – ActivationController

### Client Session-/Stream-Lifecycle

Ziel ist, dass ein neuer Entwickler die Architektur verstehen kann, ohne sie erst aus dem Produktionscode rekonstruieren zu müssen.

---

# 12. Cross-Repository-Dokumentation abgleichen

Achte darauf, dass dieselbe Schnittstelle nicht in drei Repositories unterschiedlich beschrieben wird.

Insbesondere synchron halten:

- Triggernamen;
- Feldnamen;
- IDs;
- Queryparameter;
- Capability-Namen;
- Eventnamen;
- Ack-Format;
- Lifecycle-Semantik;
- Legacy-Verhalten.

Wenn mehrere Repositories denselben Vertrag dokumentieren, müssen diese Beschreibungen semantisch übereinstimmen.

---

# 13. Beispiele und Konfigurationen ebenfalls prüfen

Nicht nur Fließtext.

Prüfe auch:

- Beispiel-YAMLs;
- Defaultconfigs;
- Beispiel-WebSocket-Nachrichten;
- JSON-Beispiele;
- CLI-/Startbeispiele;
- Screenshots oder beschriebenes UI-Verhalten;
- Kommentare neben Configfeldern;
- Settings-Metadaten.

Veraltete Beispiele sind genauso problematisch wie veralteter Text.

---

# 14. Dokumentationsabschluss nachweisen

Erstelle am Ende eine kurze Dokumentations-Evidence:

Für jedes Repository:

```text
Repository:
geprüfte relevante Dokumentationsbereiche:
aktualisierte Dateien:
entfernte/veraltete Aussagen:
neu dokumentierte Architekturthemen:
bewusst erhaltene Legacy-Dokumentation:
offene Dokumentationspunkte:
```

Zusätzlich eine kurze Cross-Repo-Aussage:

> Sind Trigger-, Config-, Lifecycle-, Event- und Feedbackverträge über alle drei Repositories konsistent?

---

# 15. Finale technische Regression

Nach sämtlichen Code- und Dokumentationsänderungen:

- alle spezifischen Gate-Tests;
- vollständige Server-Suite;
- vollständige Client-Suite;
- vollständige LED-Suite;
- Build/Frozen-Validierung soweit vorgesehen;
- `git diff --check` in allen drei Repositories.

Keine historische Testzahl als Soll verwenden.

Die tatsächlich vorhandene Suite vollständig ausführen und die gefundenen Zahlen dokumentieren.

---

# 16. Git-Safety bleibt unverändert

Noch einmal ausdrücklich:

**KEIN COMMIT.**

**KEIN PUSH.**

**KEIN MERGE.**

**KEIN REBASE.**

**KEIN PR.**

Am Ende für alle drei Repositories:

```powershell
git rev-parse HEAD
git status --short
git diff --check
git diff --stat
git log -1 --oneline
```

Es muss weiterhin gelten:

```text
INITIAL_HEAD == FINAL_HEAD
```

---

# 17. Finaler Bericht

Nach Abschluss bitte keinen pauschalen „alles fertig“-Text.

Beginne mit:

```text
VERIFIZIERTER GESAMTSTATUS:
<vollständig bestanden / manuelle Restabnahme erforderlich / nicht vollständig>
```

Dann:

## Seit der letzten Abnahme ergänzt

## GATE-4-Kollisionsnachweise

## Continuous-Streaming-Nachweis

## Kompatibilitätsstatus / GATE 5

## Feedback-/Hardwarestatus / GATE 8

## vollständige Regression / GATE 9

## offene manuelle GATE-10-Szenarien

## Dokumentationsaudit voice-stt-server

## Dokumentationsaudit voice-stt-client

## Dokumentationsaudit led_controller_respeaker-v3

## Cross-Repository-Dokumentationskonsistenz

## vollständige Testsuiten

## offene Punkte

## Git-Safety-Nachweis

Wichtig ist diesmal nicht, unbedingt einen vollständigen PASS zu erreichen.

Wichtig ist, dass **jeder PASS tatsächlich genau das bedeutet, was im ursprünglichen Auftrag definiert wurde**, und dass die Dokumentation anschließend den realen neuen Systemzustand vollständig, aktuell, anschaulich und widerspruchsfrei beschreibt.

Arbeite diese Restpunkte bitte autonom vollständig ab und bleibe weiterhin bei der bisher guten beweisorientierten Arbeitsweise.