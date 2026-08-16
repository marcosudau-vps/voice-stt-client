# Zielbildspezifikation – Einheitliche serverseitige Triggerarchitektur

**Status:** Verbindliche Soll-Spezifikation  
**Zweck:** Normative Referenz für Implementierung, Review, Diagnose, Tests und manuelle Abnahme  
**Geltungsbereich:** `voice-stt-server`, `voice-stt-client`, `led_controller_respeaker-v3`

---

# 1. Zentrale Architekturvorgabe

Es gibt fachlich und technisch **genau einen Aktivierungs-, Aufnahme-, Verarbeitungs-, VAD-, Transkriptions- und Abschlussvorgang**.

`manual` (normaler Diktat-/Hotkey) und `wake_word` sind **keine Betriebsmodi** und erzeugen **keine unterschiedlichen Aufnahmewege**. Sie unterscheiden sich ausschließlich in der Art, wie im Idle-Zustand dieselbe serverseitige Activation ausgelöst wird.

Nach Annahme eines Triggers darf der weitere fachliche Ablauf nicht davon abhängen, ob der erste Auslöser `manual` oder `wake_word` war.

Kurzform:

```text
Idle
  ├─ normaler Hotkey ─────┐
  └─ Wake Word ───────────┤
                          ▼
                EINE serverseitige Activation
                          ▼
                EINE Recording-/VAD-Logik
                          ▼
                EINE Transkriptionslogik
                          ▼
                EINE Abschluss-/Finalisierung
                          ▼
                         Idle
```

Der Unterschied zwischen `manual` und `wake_word` endet am Trigger-Eingang.

---

# 2. Abgrenzung zum früheren Modell

## 2.1 Früherer Hotkey-Pfad

Im früheren Hotkey-Betrieb war der Hotkey Bestandteil eines eigenen clientseitigen Diktatpfads:

```text
Hotkey auf dem Client
→ lokaler Diktat-/Aufnahmevorgang
→ lokales VAD auf dem Client
→ lokale Erkennung des Aufnahmeendes
→ clientseitige Lifecycle-Verantwortung
→ Übertragung/Verarbeitung durch den Server
```

Der alte Hotkey-Pfad war damit ein eigenständiger Aufnahme- und Lifecycle-Vorgang.

## 2.2 Früherer Wake-Word-Pfad

Im früheren Wake-Word-Betrieb bestand dagegen bereits ein serverseitig kontrollierter Vorgang:

```text
kontinuierlicher Audiostream
→ serverseitige Wake-Word-Erkennung
→ serverseitige Activation
→ serverseitiges Recording Gate / Recorder
→ serverseitiges VAD
→ serverseitiges Aufnahmeende
→ serverseitige Follow-up-/Timeout-/Finalisierungslogik
```

## 2.3 Ziel der Vereinheitlichung

Der frühere clientseitige Hotkey-Aufnahmeweg darf als eigenständiges Konzept **nicht fortbestehen**.

Der serverseitige Activation-/Recording-/VAD-Ablauf ist der **einzige allgemeine Vorgang**. Er darf nicht mehr als „Wake-Word-Modus“ behandelt werden.

Der normale Hotkey ist nur noch eine zweite Möglichkeit, denselben serverseitigen Vorgang aus dem Idle-Zustand auszulösen.

Das bedeutet insbesondere:

- kein lokales VAD als Autorität über Ende einer Manual-Aufnahme;
- kein clientseitiger Hotkey-Recorder als eigener Aufnahmeweg;
- keine getrennte Hotkey-State-Machine;
- keine getrennte Wake-Word-State-Machine;
- keine getrennten Sessiontypen;
- keine getrennten Recorder-Lifecycles;
- keine getrennten Start-/Stop-Pfade;
- keine getrennten Follow-up-/Timeout-Pfade.

---

# 3. Session- und Streammodell

Es gibt pro laufender Clientverbindung **eine gemeinsame Session** mit einem **kontinuierlichen Audiostream**.

Beispiel:

```text
Client verbindet
→ Stream startet genau einmal

Activation 1
→ beendet

Activation 2
→ beendet

Activation 3
→ beendet

...

Client-/Sessionende
→ Stream endet
```

Nicht zulässig:

```text
Hotkey
→ eigener Stream / eigene Session
→ Stop

Wake Word
→ anderer Stream / andere Session
```

Ebenso nicht zulässig:

```text
start = Activation starten
stop  = Activation beenden
```

Session-/Stream-Lifecycle und Activation-Lifecycle sind getrennte Ebenen.

---

# 4. Triggerquellen im Idle-Zustand

Konfigurierbare Triggerquellen:

```text
manual_trigger_enabled
wake_word_trigger_enabled
```

Zulässige Kombinationen:

```text
manual=true,  wake_word=false
manual=false, wake_word=true
manual=true,  wake_word=true
```

Nicht zulässig:

```text
manual=false, wake_word=false
```

Mindestens eine Triggerquelle muss aktiv sein.

Im stabilen Idle-Zustand gilt:

- ist `manual` aktiviert, darf der normale Hotkey eine Activation auslösen;
- ist `wake_word` aktiviert, darf ein erkanntes Wake Word eine Activation auslösen;
- sind beide aktiviert, konkurrieren beide ausschließlich darum, **welcher Trigger als erster die nächste Activation eröffnet**.

---

# 5. First-Trigger-Lock: Der erste Trigger sperrt weitere Activation-Trigger

Sobald im Idle-Zustand der erste zulässige Trigger angenommen wurde, wird für den gesamten laufenden Aufnahme-/Verarbeitungsprozess ein **Activation-/Trigger-Lock** gesetzt.

Der erste angenommene Trigger:

1. bestimmt die ursprüngliche Triggerquelle der Activation;
2. öffnet genau eine serverseitige Activation;
3. sperrt weitere Activation-Trigger bis zur vollständigen Rückkehr in den stabilen Idle-Zustand.

Beispiele:

```text
Wake Word gewinnt
→ Activation A startet
→ weitere Wake Words lösen keine neue Activation aus
→ ein normaler Hotkey wird jetzt NICHT als neuer Manual-Trigger behandelt
```

```text
Hotkey gewinnt
→ Activation B startet
→ Wake Words lösen keine neue Activation aus
→ weiterer normaler Hotkey wird jetzt NICHT als neuer Manual-Trigger behandelt
```

Der Lock wird **nicht bereits beim bloßen Ende der Audioaufnahme** freigegeben, sondern erst, wenn der gesamte laufende Activation-/Verarbeitungsprozess sauber abgeschlossen ist und das System wieder im stabilen Idle-Zustand angekommen ist.

Danach werden alle konfigurierten Triggerquellen erneut freigegeben.

---

# 6. Semantik des normalen Diktat-/Manual-Hotkeys

Der normale Hotkey hat eine **zustandsabhängige, aber einheitliche** Semantik.

## 6.1 Im Idle-Zustand

```text
Hotkey
→ Manual-Trigger
→ serverseitige Activation starten
```

Der Client startet dabei keinen eigenen Aufnahmevorgang, sondern sendet lediglich das entsprechende Manual-Trigger-/Activation-Command an den Server.

## 6.2 Während einer laufenden Activation / Aufnahme / Verarbeitung

Der normale Hotkey wechselt in seine zweite Bedeutung:

```text
Hotkey
→ aktuelle Activation sofort beenden / finishen
```

Das gilt unabhängig davon, wodurch die aktuelle Activation gestartet wurde.

Beispiel Wake Word:

```text
Wake Word
→ Activation A
→ Recording läuft

normaler Hotkey
→ Finish für Activation A
→ Aufnahme wird beendet
→ reguläre serverseitige Finalisierung
→ Idle
```

Beispiel Manual:

```text
normaler Hotkey
→ Activation B

normaler Hotkey erneut
→ Finish für Activation B
→ reguläre serverseitige Finalisierung
→ Idle
```

„Sofort beenden“ bedeutet: Der Server soll die laufende Aufnahme/Activation unverzüglich in den vorgesehenen gemeinsamen Finish-/Finalisierungspfad überführen. Bereits vorhandene Daten dürfen regulär finalisiert werden; es ist kein harter Prozessabbruch gemeint.

---

# 7. Verhalten des Wake Words während einer laufenden Activation

Ein Wake Word darf während einer bereits laufenden Activation **nicht**:

- die Activation beenden;
- die Aufnahme beenden;
- die Activation verlängern;
- eine zweite Activation öffnen;
- eine zweite Aufnahme starten;
- die Triggerquelle wechseln;
- einen anderen Betriebsmodus aktivieren.

Wake-Word-Erkennungen während des gesetzten Activation-/Trigger-Locks werden für die Activation-Steuerung **ignoriert bzw. unterdrückt**.

Optional dürfen sie rein diagnostisch/Audit-seitig als unterdrückter Trigger protokolliert werden. Sie dürfen aber keine fachliche Zustandsänderung auslösen.

---

# 8. Keine Source-Aggregation als Laufzeitsteuerung

Im Zielmodell erzeugt ein zweiter Activation-Trigger während einer bereits aktiven Activation **keine zusätzliche Quelle derselben Activation**.

Der erste angenommene Trigger gewinnt.

Damit ist insbesondere **nicht** das Ziel:

```text
Wake Word startet
→ Hotkey wird als zweite Triggerquelle in dieselbe Activation gemerged
```

Der normale Hotkey hat während der aktiven Activation bereits seine andere Bedeutung: `finish`.

Entsprechend soll der Ursprung einer Activation eindeutig sein, z. B.:

```text
primarySource = manual
```

oder

```text
primarySource = wake_word
```

Unterdrückte Trigger dürfen separat diagnostisch erfasst werden, aber nicht die fachliche Activation-Quelle verändern.

---

# 9. Sekundärer Hotkey für Wake-Word-Pause

Das Pausieren/Aktivieren der Wake-Word-Erkennung ist eine **separate Bedienfunktion**.

Dafür gibt es einen separat konfigurierbaren sekundären Hotkey, z. B.:

```text
Wake-Word-Pause-Hotkey
```

Semantik:

```text
Wake-Word-Pause-Hotkey
→ Wake-Word-Erkennung pausieren / fortsetzen
```

Diese Funktion:

- startet keine Activation;
- beendet keine Activation;
- ist nicht der normale Diktat-/Manual-Hotkey;
- verändert nicht die Manual-Triggerquelle;
- darf keine alte `mode`-Semantik wieder einführen.

Der normale Hotkey darf im Idle-Zustand nicht länger die Bedeutung „Wake Word pausieren“ besitzen.

---

# 10. Server ist die fachliche Lifecycle-Autorität

Der Server bzw. der zentrale ActivationController ist die Autorität für:

- Activation-Eröffnung;
- Activation-ID;
- ursprüngliche Triggerquelle;
- Activation-/Trigger-Lock;
- Recording Gate;
- Recorder;
- VAD;
- Recording Start;
- Recording End;
- Follow-up;
- Extend, soweit im Zielsystem weiterhin vorgesehen;
- Finish;
- Cancel;
- Timeout;
- Finalisierung;
- Rückkehr nach Idle;
- Freigabe der Triggerquellen.

Der Client darf keine zweite, unabhängige Wahrheit über diese Zustände besitzen.

---

# 11. Rolle des Clients

Der Client darf:

- Mikrofon-Audio erfassen;
- den kontinuierlichen Audiostream übertragen;
- den normalen Hotkey erkennen;
- den Wake-Word-Pause-Hotkey erkennen;
- Manual-/Finish-/Cancel-/sonstige zulässige Commands senden;
- Server-Acks und Serverevents konsumieren;
- UI, Tray, Sound und LED-Feedback aus dem serverseitigen Zustand ableiten.

Der Client darf **nicht** eigenständig entscheiden:

- dass eine Manual-Aufnahme fachlich begonnen hat;
- dass eine Aufnahme fachlich beendet ist;
- dass eine Activation noch läuft;
- dass Follow-up begonnen oder beendet wurde;
- dass eine Activation finalisiert wurde.

Insbesondere darf ein lokales VAD nicht mehr als Aufnahmeende-Autorität des Manual-Pfads fungieren.

Lokale Audioerfassung ist zulässig. Eine lokale zweite Diktat-State-Machine ist es nicht.

---

# 12. Verbotene alte Runtime-Autoritäten

Folgende Konzepte dürfen im aktuellen Produktivpfad keine fachliche Autorität mehr besitzen:

```text
mode: hotkey
mode: wake_word
Legacy-Betriebsmodus
Hotkey-Session
Wake-Word-Session
Hotkey-spezifischer Recorder
Hotkey-spezifisches VAD als Aufnahmeautorität
lokale Hotkey-Follow-up-State-Machine
start/stop als Diktat-Lifecycle
source-abhängige Aufnahme-State-Machine
```

Falls alte Konfigurationen noch unterstützt werden müssen, darf `mode` ausschließlich als **begrenzter Migrationsadapter** verwendet werden.

Zulässig:

```text
alte Config:
mode: hotkey

einmalige Übersetzung:
manual_trigger_enabled=true
wake_word_trigger_enabled=false

ab hier:
Runtime kennt mode fachlich nicht mehr
```

Nicht zulässig:

```text
mode
→ bestimmt Session
→ bestimmt Recorder
→ bestimmt VAD
→ bestimmt UI
→ bestimmt Feedback
→ bestimmt Triggerverhalten
```

Im aktuellen Einstellungsdialog darf ein solcher reiner Legacy-Migrationsparameter nicht mehr erscheinen.

---

# 13. Zustandsmodell und Hängesicherheit

Die tatsächlichen Zustandsnamen können implementierungsbedingt abweichen, fachlich müssen jedoch mindestens folgende Phasen eindeutig abgebildet werden:

```text
Idle
Activation geöffnet
Warten auf Sprache
Recording
Nachlauf / Follow-up
Finish / Cancel / Timeout
Finalisierung
Idle
```

Jeder nichtterminale Zustand muss einen definierten Exit besitzen.

Kein Zustand darf durch ein verlorenes Ack, Event oder einen Race-Zustand unbegrenzt hängen bleiben.

Für jeden Zustand müssen definiert sein:

- Owner;
- Eintrittsbedingung;
- erlaubte Commands;
- Austrittsbedingungen;
- Timer;
- maximale Lebensdauer;
- Verhalten bei Reconnect;
- Verhalten bei Session Close;
- Verhalten bei Serverfehler;
- Verhalten bei Clientfehler;
- Verhalten bei stale Events;
- Verhalten bei stale Timern;
- Verhalten bei doppeltem Finish/Cancel;
- Generation-/Activation-ID-Guards.

Der Trigger-Lock muss auf allen regulären und Fehlerpfaden zuverlässig freigegeben werden, sobald wieder ein stabiler Idle-Zustand erreicht ist.

---

# 14. UI- und Einstellungsmodell

## 14.1 Kein Legacy-Betriebsmodus im aktuellen UI

Der aktuelle Einstellungsdialog darf keinen Abschnitt wie:

```text
Legacy
  Legacy-Betriebsmodus
  Hotkey / Wake Word
```

enthalten.

Es gibt im Zielbild keinen auswählbaren Hotkey- oder Wake-Word-Betriebsmodus.

## 14.2 Triggerquellen

Der Einstellungsdialog enthält einen Abschnitt:

```text
Triggerquellen
```

mit mindestens:

```text
[ ] Manueller Trigger
[ ] Wake-Word-Trigger
```

Validierung:

- mindestens eine Option muss aktiv sein;
- beide dürfen gleichzeitig aktiv sein;
- die Auswahl muss persistiert werden;
- sie muss beim Verbindungsaufbau/Admission wirksam werden;
- kein Legacy-Feld darf sie überschreiben.

## 14.3 Wake-Word-Auswahl

Ist `wake_word_trigger_enabled=true`, muss eine funktionierende Wake-Word-Konfiguration vorhanden sein.

Bevorzugtes Ziel:

- Mehrfachauswahl der tatsächlich verfügbaren Wake Words;
- vorhandene Wake Words aus einem realen Katalog/Capability ableiten;
- mindestens ein sinnvoller Standardwert.

Falls dynamische Mehrfachauswahl technisch noch nicht möglich ist, muss mindestens ein funktionierendes Text-/Listenfeld vorhanden sein, über das Wake Words eingegeben werden können.

Eine leere Gruppe „Wake Word“ ohne Eingabeelement ist nicht zulässig.

## 14.4 Hotkey-Konfiguration

Der normale Diktat-/Manual-Hotkey und der Wake-Word-Pause-Hotkey müssen getrennt konfigurierbar sein.

## 14.5 Keine hotkey-spezifischen Lifecycle-Bezeichnungen

Einstellungen, die fachlich für den allgemeinen Activation-/Recording-Lifecycle gelten, dürfen nicht als „Hotkey-Diktatfenster“ oder anderweitig als hotkey-spezifischer Betriebsmodus dargestellt werden.

Ihre Benennung muss den gemeinsamen serverseitigen Activation-/Recording-Lifecycle widerspiegeln.

---

# 15. UI-, Tray-, Sound- und LED-Feedback ist source-neutral

Es gibt keine zwei fachlichen Feedbacksysteme für Manual und Wake Word.

Für denselben serverseitigen Zustand muss dieselbe fachliche Darstellung verwendet werden, unabhängig von der ursprünglichen Triggerquelle.

Beispiel:

```text
Recording(source=manual)
Recording(source=wake_word)
```

→ gleicher Recording-Zustand, gleiche fachliche Farbe/Animation.

Entsprechend für:

- Idle;
- Waiting;
- Recording;
- Follow-up;
- Finishing;
- Warning;
- Error.

Historische Farbschemata wie „Hotkey = eigene Farbe“ und „Wake Word = andere Farbe“ dürfen nicht fortgeführt werden, wenn sie zwei Betriebsmodi darstellen.

Die ursprüngliche Triggerquelle darf optional diagnostisch sichtbar gemacht werden, aber nicht einen separaten Lifecycle oder ein zweites Feedbackmodell erzeugen.

---

# 16. Verhalten bei Settings Apply / Reconnect

Bei Änderungen der Triggerkonfiguration und anschließendem Apply/Reconnect gilt:

- keine alte Activation darf lokal weiterleben;
- Pending Commands müssen kontrolliert behandelt/verworfen werden;
- stale Activation-IDs dürfen nicht weiterverwendet werden;
- stale Generationen dürfen keine Events mehr beeinflussen;
- UI-/Feedback-State muss aus dem neuen serverseitigen Zustand aufgebaut werden;
- Triggerquellen müssen nach Reconnect dem neuen Config-Stand entsprechen;
- kein gelber Warnloop darf aus wiederholten ungültigen Commands entstehen.

Nach kontrolliertem Reconnect muss ein definierter stabiler Zustand entstehen.

---

# 17. Verbindliche Bediensemantik

## Idle

Wenn aktiviert:

```text
normaler Hotkey
→ nächste Activation starten
```

oder:

```text
Wake Word
→ nächste Activation starten
```

Der erste angenommene Trigger gewinnt und setzt den Lock.

## Während Activation / Aufnahme / Verarbeitung

```text
normaler Hotkey
→ aktuelle Activation finishen
```

```text
Wake Word
→ keine fachliche Wirkung
```

Weitere Activation-Trigger bleiben gesperrt.

## Nach vollständiger Rückkehr zu Idle

Activation-/Trigger-Lock wird aufgehoben.

Alle konfigurierten Triggerquellen werden wieder freigegeben.

---

# 18. Überprüfbare Kerninvarianten

## I-1: Manual allein

```text
Hotkey im Idle
→ genau 1 Activation
→ genau 1 Recording-Lifecycle
→ genau 1 Finalisierung
→ Idle
```

## I-2: Wake Word allein

```text
Wake Word im Idle
→ genau derselbe Lifecycle
→ genau 1 Activation
→ genau 1 Recording-Lifecycle
→ genau 1 Finalisierung
→ Idle
```

## I-3: Wake Word startet, Hotkey beendet

```text
Wake Word
→ Activation A
→ Recording

Hotkey
→ Finish Activation A
→ keine zweite Activation
→ Idle
```

## I-4: Manual startet, Hotkey beendet

```text
Hotkey
→ Activation B

Hotkey erneut
→ Finish Activation B
→ keine zweite Activation
→ Idle
```

## I-5: Manual startet, Wake Word währenddessen

```text
Hotkey
→ Activation C

Wake Word während C
→ keine zweite Activation
→ kein Finish
→ kein Extend
→ keine Zustandsänderung
```

## I-6: Wake Word startet, weiteres Wake Word währenddessen

```text
Wake Word
→ Activation D

weiteres Wake Word
→ keine zweite Activation
→ keine Zustandsänderung
```

## I-7: Nahezu simultane Trigger

```text
Manual und Wake Word nahezu gleichzeitig
```

Erwartung:

- genau ein Gewinner;
- genau eine Activation;
- genau ein Recorder-/Recording-Lifecycle;
- genau ein Final;
- kein zweiter Pfad;
- zweiter Trigger wird unterdrückt.

## I-8: Trigger-Lock bleibt bis Idle

Das Aufnahmeende allein darf die Triggerquellen nicht vorzeitig freigeben, solange Finalisierung/Processing noch läuft.

## I-9: Source-neutrales Feedback

Gleicher serverseitiger Zustand → gleiche fachliche UI-/Tray-/LED-/Sound-Darstellung, unabhängig vom ursprünglichen Trigger.

## I-10: Kein lokales VAD als Manual-Aufnahmeautorität

Das Ende einer manuell ausgelösten Aufnahme wird durch denselben serverseitigen VAD-/Lifecycle-Pfad bestimmt wie nach Wake Word.

## I-11: Kein dauerhafter Zwischenzustand

Jede Activation erreicht über regulären Abschluss, Finish, Cancel, Timeout, Reconnect oder Fehlerpfad wieder einen definierten stabilen Zustand.

---

# 19. Merksatz

> Es gibt nicht mehr „Hotkey-Diktat“ und „Wake-Word-Diktat“.
>
> Es gibt nur noch **eine serverseitige Activation und einen gemeinsamen Aufnahme-/Verarbeitungsprozess**.
>
> Im Idle können `manual` und `wake_word` diesen einen Prozess auslösen.
>
> **Der erste Trigger gewinnt und sperrt weitere Activation-Trigger bis zur Rückkehr nach Idle.**
>
> Während des laufenden Prozesses bedeutet der normale Hotkey **Finish**, während weitere Wake Words **keine fachliche Wirkung** haben.
>
> Nach vollständiger Rückkehr zu Idle werden die konfigurierten Triggerquellen wieder freigegeben.
