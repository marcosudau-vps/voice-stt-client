# Zielbildspezifikation – Einheitliche serverseitige Triggerarchitektur

> **Status 2026-08-24: TEILKONSOLIDIERT.** Bereits besprochene Wake-Word-,
> Pause- und Hotkeyentscheidungen sind in dieses Dokument übernommen. Noch
> offene Detailverträge bleiben bis zum Plan-Freeze in
> `ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md` maßgeblich.

**Status:** Soll-Spezifikation in laufender Konsolidierung

**Zweck:** bisherige Soll-Referenz; nach Konsolidierung wieder normative
Referenz für Implementierung, Review, Diagnose, Tests und manuelle Abnahme

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

Als persistierte Basiskonfiguration sind vorgesehen:

```text
manual=true,  wake_word=false
manual=false, wake_word=true
manual=true,  wake_word=true
```

Folgende persistierte Basiskonfiguration ist nicht zulässig:

```text
manual=false, wake_word=false
```

Davon zu unterscheiden ist der **effektive Laufzeitzustand**: Bewusste
Laufzeitsperren dürfen vorübergehend dazu führen, dass keine
Activation-Triggerquelle wirksam ist. Dieser Zustand übersteht automatische
Server-Reconnects, neue Sessions, Serververbindungs- und Geräteverlust,
solange dieselbe Client-Anwendung läuft. Ein vollständiger Programmneustart
verwirft die Laufzeitsperren und beginnt wieder mit der funktionsfähigen
persistierten Basiskonfiguration. Der Null-Trigger-Zustand ist damit erlaubt,
sichtbar und absichtlich, aber nicht als Startkonfiguration persistent.

Im stabilen Idle-Zustand gilt:

- ist `manual` aktiviert, darf der normale Hotkey eine Activation auslösen;
- ist `wake_word` aktiviert, darf ein erkanntes Wake Word eine Activation auslösen;
- sind beide aktiviert, konkurrieren beide ausschließlich darum, **welcher Trigger als erster die nächste Activation eröffnet**.

---

# 5. First-Trigger-Lock: Der erste Trigger sperrt weitere Activation-Trigger

Sobald im Idle-Zustand der erste zulässige Trigger angenommen wurde, wird für
das offene Eingabefenster ein **Activation-/Trigger-Lock** gesetzt.

Der erste angenommene Trigger:

1. bestimmt die ursprüngliche Triggerquelle der Activation;
2. öffnet genau eine serverseitige Activation;
3. sperrt weitere Activation-Trigger bis das Eingabefenster sicher geschlossen
   und der triggerrelevante Vordergrundzustand wieder `idle` ist.

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

Der Lock wird **nicht bereits beim bloßen Ende eines Audiosegments**
freigegeben, weil danach noch `followup_wait` weitere Sprache derselben
Activation annehmen kann. Er endet aber nach Ablauf beziehungsweise bewusstem
Schließen dieses Eingabefensters, sobald Gate/Aufnahme geschlossen und alle
angenommenen Segmentjobs oder Verwerfungsterminals dauerhaft registriert sind.
Noch laufende Final-Transkriptionen älterer Activations blockieren `idle` und
neue Trigger nicht.

Danach werden alle konfigurierten Triggerquellen erneut freigegeben.

---

# 6. Semantik der Hotkeys und Activation-Steuerung

Es gibt einen primären Hotkey, einen zweiten separat konfigurierbaren
Activation-Control-Hotkey und einen dritten separat konfigurierbaren
Hotkeyplatz für Wake-Word-Pause/-Fortsetzen. Die beiden Activation-Hotkeys
wirken zustandsabhängig und bilden keine zweite Trigger- oder
Aufnahmearchitektur. Der dritte Hotkey kann ungebunden bleiben und steuert
keine Activation.

## 6.1 Im Idle-Zustand

```text
Hotkey
→ Manual-Trigger
→ serverseitige Activation starten
```

Der Client startet dabei keinen eigenen Aufnahmevorgang, sondern sendet lediglich das entsprechende Manual-Trigger-/Activation-Command an den Server.

## 6.2 Während einer laufenden Activation / Aufnahme / Verarbeitung

Die Active-Aktion des primären Hotkeys ist konfigurierbar:

```text
refresh | finish | cancel | none
```

Die besprochene Ausgangsbelegung ist:

```text
primärer Hotkey: Idle = activate, Active = refresh
zweiter Hotkey:  Idle = keine Activation, Active = finish
cancel:          optional bzw. zunächst ungebunden
dritter Hotkey:  Wake-Word-Pause/-Fortsetzen, sofern belegt
```

Die Active-Aktion steuert immer die laufende Activation – unabhängig davon,
ob sie durch Manual oder Wake Word gestartet wurde. Sie eröffnet keine zweite
Activation und wird nicht als weitere Triggerquelle gemerged.

Für den Inaktivitäts-/Follow-up-Timer ist `refresh` ausschließlich in
`followup_wait` gültig und ausdrücklich **nicht kumulativ**:

```text
neue Deadline = Zeitpunkt der letzten gültigen Interaktion
               + konfigurierter Inaktivitäts-Timeout
```

Mehrfaches Drücken addiert keine Sekunden und erzeugt kein Zeitguthaben. In
`waiting_first_speech` ist `refresh` ungültig. In `segment_active` setzt ein
gültiges `refresh` ausschließlich den separaten Daueraufnahme-
Sicherheitswatchdog. Seine neue Deadline ist
`max(bisherige Deadline, Interaktionszeitpunkt + 180 Sekunden)`. Ein früher
Druck verkürzt die initiale Zehn-Minuten-Frist nicht; spätere Betätigungen
geben jeweils drei Minuten ab der letzten Interaktion, ohne Zeitguthaben für
den späteren Follow-up-Timer anzusparen.

Beispiel mit zehn Sekunden Timeout:

```text
refresh um 12:00:00 → Deadline 12:00:10
refresh um 12:00:04 → Deadline 12:00:14
kein Ergebnis von 20 oder 30 Sekunden
```

`finish` schließt die Eingabe geordnet und lässt alle bereits angenommenen
Segmente regulär zu einem terminalen Ergebnis verarbeiten. `cancel` schließt
die Eingabe sofort und verwirft die noch ausstehenden Nutzresultate der
Activation. Jeder akzeptierte Finish- oder Cancel-Command erzeugt auch ohne
vorhandenes Segment ein korreliertes fachliches Lifecycle-Ereignis; ein Ack
allein genügt nicht.

Die verbindliche Phasenwirkung ist:

| Phase | `finish` | `cancel` |
|---|---|---|
| `idle` | abweisen, kein Lifecycle-Ereignis | abweisen, kein Lifecycle-Ereignis |
| `waiting_first_speech` | ohne Transkript schließen und Finish-Ereignis senden | ohne Transkript abbrechen und Cancel-Ereignis senden |
| `segment_active` | über `closing_input` Aufnahme beenden und Job sicher registrieren; danach `idle`, Final im Hintergrund | über `closing_input` Aufnahme beenden, Verwerfung registrieren und danach `idle` |
| `followup_wait` | Eingabe schließen und sofort nach `idle`; Final im Hintergrund | Eingabe schließen, unveröffentlichte Resultate verwerfen und nach `idle` |
| `closing_input` | idempotente Rückmeldung, keine zweite Transition | idempotente Rückmeldung, keine zweite Transition |

Ein Replay derselben `commandId` liefert dasselbe Ack ohne weiteres
Lifecycle-Ereignis. Ein späterer Command nach bereits erfolgter Transition
liefert einen definierten Zustand wie `already_input_closed` oder
`stale_activation`, ebenfalls ohne zweites Ereignis.

Bereits vor Cancel veröffentlichter oder eingefügter Text bleibt bestehen und
wird nicht automatisch zurückgenommen. Ab Annahme des Cancel wird kein
weiteres Nutzresultat dieser Activation veröffentlicht. Nicht sicher
abbrechbare Inferenz darf intern fertiglaufen, ihre Veröffentlichung bleibt
aber unterdrückt und ihr Segment erhält einen verwerfenden terminalen Ausgang.
Nur konkrete Wire-Namen und Felder werden im technischen Contract festgelegt.

## 6.3 Mehrere Sprachsegmente innerhalb derselben Activation

Eine Activation darf mehrere aufeinanderfolgende Sprachsegmente enthalten.
Nach dem durch VAD erkannten Ende eines Segments bleibt das Follow-up-Fenster
offen. Erneutes Sprechen startet darin das nächste Segment mit derselben
`activationId` und derselben ursprünglichen Triggerquelle. Die Segmente
werden serverseitig seriell verarbeitet; es gibt keine gleichzeitigen
Recording-Segmente derselben Session.

Das Ende eines Segments beendet daher nicht automatisch die Activation und
gibt den Trigger-Lock nicht frei. Erst Follow-up-Timeout, `finish`, `cancel`
oder ein definierter Fehler-/Recoverypfad schließt sie.

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

Das gesprochene Audio bleibt normales Activation-Audio. Erkennt VAD darin
Sprache, beeinflusst diese Sprache den Inaktivitätstimer wie jede andere
Sprache; das ist keine besondere Wake-Word-Wirkung.

---

# 8. Keine Source-Aggregation als Laufzeitsteuerung

Im Zielmodell erzeugt ein zweiter Activation-Trigger während einer bereits aktiven Activation **keine zusätzliche Quelle derselben Activation**.

Der erste angenommene Trigger gewinnt.

Damit ist insbesondere **nicht** das Ziel:

```text
Wake Word startet
→ Hotkey wird als zweite Triggerquelle in dieselbe Activation gemerged
```

Ein Hotkey wird während der aktiven Activation gemäß seiner konfigurierten
Active-Aktion (`refresh`, `finish`, `cancel` oder `none`) behandelt.

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

# 9. Wake-Word-Pause als separater Laufzeitzustand

Das Pausieren/Aktivieren der Wake-Word-Erkennung ist eine **separate Bedienfunktion**.

Die fachliche Semantik lautet:

```text
Wake-Word-Pause-Aktion
→ Wake-Word-Erkennung pausieren / fortsetzen
```

Diese Funktion:

- startet keine Activation;
- beendet keine Activation;
- verändert nicht die Manual-Triggerquelle;
- darf keine alte `mode`-Semantik wieder einführen.

Der Zustand übersteht automatische Reconnects während derselben
Client-Laufzeit. Bei einem vollständigen Neustart der Client-Anwendung startet
Wake Word immer ungepausiert, soweit es in der Basiskonfiguration aktiviert
und serverseitig verfügbar ist.

Für diese Funktion existiert ein dritter, separat konfigurierbarer
Hotkeyplatz. Er darf ungebunden bleiben; eine zusätzliche Tray-Bedienung ist
zulässig. Konkrete Default-Tastenkombination und Konfliktregeln sind noch
festzulegen.
Hardware-/Firmware-Mute des ReSpeaker bleibt davon unabhängig und wird
ausschließlich clientseitig behandelt.

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
- nicht kumulatives `refresh` des relevanten Inaktivitätstimers;
- Finish;
- Cancel;
- Timeout;
- Finalisierung;
- Rückkehr nach Idle;
- Freigabe der Triggerquellen.

Der Client darf keine zweite, unabhängige Wahrheit über diese Zustände besitzen.

„Serverautorität“ bezieht sich auf fachliche Commands und Zustände, nicht auf
physische Eingabegeräte. Der Server kennt keinen konkreten Hotkey und keinen
ReSpeaker. Der Client übersetzt lokale Tastendrücke in `activate`, `refresh`,
`finish` oder `cancel` und meldet Audioverfügbarkeit nur als generischen
fachlichen Zustand. Welche Taste gedrückt wurde, welches Gerät fehlt oder wie
Mute-LED und Wiederverbindung funktionieren, bleibt clientseitig.

---

# 11. Rolle des Clients

Der Client darf:

- Mikrofon-Audio erfassen;
- den kontinuierlichen Audiostream übertragen;
- primären und zweiten konfigurierten Activation-Hotkey erkennen;
- den optional belegten dritten Hotkey für Wake-Word-Pause erkennen und die
  separat modellierte Pause-/Fortsetzen-Aktion auslösen;
- Manual-/Refresh-/Finish-/Cancel-/sonstige zulässige Commands senden;
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

Die triggerrelevante Vordergrund-State-Machine besitzt folgende kanonische
Phasen:

```text
idle
→ waiting_first_speech
→ segment_active
→ followup_wait
→ segment_active ... oder closing_input
→ idle
```

`closing_input` ist ausschließlich der kurze technische Übergang, in dem Gate
und gegebenenfalls Aufnahme geschlossen sowie Segmentjob oder
Verwerfungsterminal dauerhaft registriert werden. Er darf nicht auf die
Inferenz warten.

Die Verarbeitung geschlossener Activations ist davon getrennt:

```text
draining
→ completed | cancelled | failed
```

`draining` ist keine Vordergrundphase und setzt keinen Trigger-Lock. Mehrere
ältere Activations dürfen noch Final-Ergebnisse ausstehen haben, während der
Vordergrund bereits `idle` oder in einer neuen Activation ist.

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

## 13.1 Daueraufnahme-Sicherheitswatchdog

`segment_active` besitzt zusätzlich einen großzügigen, serverautoritativen
und pro Session konfigurierbaren Sicherheitswatchdog mit zehn Minuten Default.
Der genaue zulässige Wertebereich wird im Settings-Contract festgelegt. Er
schützt insbesondere vor einer unbeabsichtigten
Daueraufnahme bei kontinuierlicher Fremdsprache, etwa durch einen Fernseher.

- VAD setzt den Watchdog nicht zurück.
- Ein Hotkey-`refresh` in `segment_active` setzt nur diesen Watchdog neu und
  gilt als menschliches Anwesenheitssignal. Die neue Deadline ist
  `max(bisherige Deadline, Zeitpunkt + 180 Sekunden)`; die initiale längere
  Restzeit wird nicht verkürzt und es wird nichts kumuliert.
- Eine konfigurierbare Vorwarnung mit 30 Sekunden Default wird als
  zuverlässiges Ereignis für das Client-Feedback veröffentlicht.
- Bei Ablauf endet die gesamte Activation und kehrt nach ihrem definierten
  Abschluss nach Idle zurück; es folgt kein `followup_wait`.
- Eine weitere Aufnahme benötigt danach einen neuen Trigger.

Das bis dahin erfasste Audio wird beim Schutzablauf wie bei `finish` regulär
verarbeitet. Bereits investierte Sprechzeit darf ohne aktive
Anwenderentscheidung nur dann verworfen werden, wenn Verarbeitung oder sichere
Weiterführung technisch nicht mehr möglich oder nachweisbar unvertretbar ist.
Jeder solche Verlust besitzt einen sichtbaren, terminalen Grund.

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

Wake-Word-Modelle werden mit dem jeweiligen Server-Build ausgeliefert. Ein
Build darf eine kleine Auswahl oder den vollständigen vorgesehenen Katalog
enthalten. Alle enthaltenen, grundsätzlich validierten und nicht global
deaktivierten Modelle bilden den verfügbaren Katalog, ohne dass sie alle
gleichzeitig als Inferenzmodelle initialisiert sein müssen.

Der Server muss den verfügbaren Katalog abfragbar machen. Einzelne enthaltene
Modelle dürfen serverseitig global deaktiviert werden. Pro Session wählt der
Client genau ein oder mehrere Modelle aus dem verfügbaren Katalog aus. Nur
diese Auswahl wird beim Sessionstart geladen/initialisiert; nicht ausgewählte
Katalogmodelle verbrauchen keine sessionbezogenen Inferenzressourcen.

Die Sessionauswahl wird atomar validiert. Sobald eine ausgewählte ID
unbekannt, deaktiviert oder nicht ladbar ist, wird die gesamte Auswahl mit
maschinenlesbarer Liste aller problematischen IDs abgelehnt. Teilerfolg und
stiller Fallback sind unzulässig.

Konfigurationseingaben werden mindestens groß-/kleinschreibungsunabhängig
aufgelöst. Natürliche Kurzformen wie `jarvis` für `Hey Jarvis` werden über
Aliase einer stabilen kanonischen Modell-ID zugeordnet. Die genaue
Normalisierungs- und Kollisionsregel ist noch festzulegen.

Für alle in einer Session aktiven Wake Words gilt eine gemeinsame,
konfigurierbare Empfindlichkeit. Das verbindliche Detection-Ereignis nennt
die kanonische ID des tatsächlich erkannten Wake Words.

Der heutige Adapter akzeptiert bereits einen einzelnen neuesten Score über
dem Schwellwert; eine explizite Mehrfach-Chunk-Bestätigung existiert dort
nicht. Das Zielbild schreibt deshalb noch keine willkürliche Zahl
aufeinanderfolgender Treffer fest. Der erste akzeptierte Treffer setzt
verbindlich einen fachlichen Latch; bis zum Unlock wird keine weitere
Wake-Word-Detection akzeptiert. Score- und Audio-Traces bestimmen nur noch,
ob gegen Fehlalarme zusätzlich eine kleine zeitliche Mehrheitsregel
erforderlich ist. Unabhängig davon darf eine gesprochene Wake-Word-Äußerung
höchstens ein fachliches Detection-Ereignis auslösen.

Die kleine Modellartefaktgröße darf nicht mit dem Laufzeitspeicher
gleichgesetzt werden. RAM und Session-Startzeit werden für typische und
maximale Sessionauswahlen gemessen; die selected-only Initialisierung ist die
verbindliche Ressourcenstrategie.

Eine leere Wake-Word-Gruppe ohne Auswahlmöglichkeit ist nicht zulässig.

## 14.4 Hotkey-Konfiguration

Primärer Hotkey und zweiter Activation-Control-Hotkey müssen getrennt
konfigurierbar sein. Für ihre Active-Phase sind mindestens `refresh`,
`finish`, `cancel` und `none` als Aktionen modellierbar. Zusätzlich existiert
ein dritter, separat belegbarer Hotkeyplatz für Wake-Word-Pause/-Fortsetzen;
seine Belegung darf leer sein.

## 14.5 Serverautorisierte Einstellungen

Server- und sessionswirksame Einstellungen werden über eine einheitliche
Server-API gelesen und geändert. Der Server veröffentlicht je Wert Scope,
Auth-Anforderung, Typ/Wertebereich, Default, effektiven Wert und Apply-Policy
und bleibt letzte Validierungs- und Laufzeitautorität.

Der Client unterscheidet mindestens:

- sessionspezifische Werte, die ohne Adminrecht für die eigene Session
  angefordert und – sofern erlaubt – während der Session geändert werden;
- serverweite Werte und Defaults, deren Änderung eine erfolgreiche
  Admin-Authentifizierung verlangt;
- unvermeidbar lokale Geräte-/Bedienwerte, die keine Serverautorität besitzen.

Client-lokal sind insbesondere Serveradresse/TLS, Admin-Credential, physische
Hotkeybelegungen, Audio-/ReSpeaker-Gerätewahl, Hardware-Mute, Autostart,
Fenster-/Tray-Verhalten, Textinjektion und die vollständige
Feedbackkonfiguration. Der Server sendet dafür nur zuverlässige Domain-Events;
In-App-, Tray-, Overlay-, Sound- und LED-Darstellung werden ausschließlich im
Client bestimmt.

Der Einstellungsdialog erhält eine eigene Seite für serverweite Einstellungen.
Sie ist zunächst gesperrt und wird nach erfolgreicher Prüfung eines
eingegebenen Admin-Keys freigeschaltet. Der Key darf auf Wunsch dauerhaft,
aber nicht als Klartext in der normalen Konfigurationsdatei oder über einen
normalen `QSettings`-Registrywert gespeichert werden. Das Secret liegt im
Windows Credential Manager; die UI kann es anlegen, ersetzen und löschen.
`QSettings` hält nur nicht geheime Metadaten. Ohne verfügbaren
Credential-Speicher bleibt der Key ausschließlich im Prozessspeicher; ein
Klartext-Fallback ist unzulässig.

Dieser Architekturumbau liefert Contract, Apply-Mechanik, Trigger-/Wake-Word-/
Timing-Einstellungen und die erweiterbare Servereinstellungsseite. Weitere
fachfremde Einstellungsdomänen können der spätere Settings-Arbeitsblock auf
derselben Grundlage ergänzen.

## 14.6 Keine hotkey-spezifischen Lifecycle-Bezeichnungen

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

Jede Activation friert beim Start einen unveränderlichen Snapshot ihrer
wirksamen Einstellungen ein. Änderungen währenddessen gelten je
veröffentlichter Apply-Policy `live`, `next_activation`,
`next_session/reconnect` oder `server_restart`, verändern die laufende
Activation aber niemals rückwirkend.

Erfordert eine Änderung einen Reconnect, während eine Activation läuft, fragt
der Client vor dem Apply: sofort abbrechen und reconnecten, regulär abschließen
und danach automatisch reconnecten oder die Änderung bis zu einem später
manuell ausgelösten Reconnect vormerken. Ohne ausdrückliche Auswahl wird die
Activation nicht wegen einer Einstellungsänderung gecancelt.

- keine alte Activation darf lokal weiterleben;
- Pending Commands müssen kontrolliert behandelt/verworfen werden;
- stale Activation-IDs dürfen nicht weiterverwendet werden;
- stale Generationen dürfen keine Events mehr beeinflussen;
- UI-/Feedback-State muss aus dem neuen serverseitigen Zustand aufgebaut werden;
- Triggerquellen müssen nach Reconnect dem neuen Config-Stand entsprechen;
- eine vom Anwender gesetzte Wake-Word-Pause muss während derselben
  Client-Laufzeit ohne unbeabsichtigtes Aktivierungsfenster wiederhergestellt
  werden;
- kein gelber Warnloop darf aus wiederholten ungültigen Commands entstehen.

Bricht eine Serververbindung während einer Activation ab, wird diese
Activation nicht wiederaufgenommen. Bereits veröffentlichter Text bleibt
bestehen; unveröffentlichte Resultate werden verworfen. Die neue Session
beginnt im stabilen Idle und übernimmt die für die Client-Laufzeit geltenden
Trigger-Suppressionszustände.

Ein Verlust der ReSpeaker-/Audiogeräteverbindung lässt die Serversession
bestehen und startet lokale Wiederverbindungsversuche. Eine dabei laufende
Activation wird jedoch sofort gecancelt.

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

## Während des offenen Activation-Eingabefensters

```text
primärer oder zweiter Hotkey
→ konfigurierte Active-Aktion ausführen
  (refresh | finish | cancel | none)
```

`refresh` setzt in `followup_wait` den Inaktivitätstimer und in
`segment_active` ausschließlich den Daueraufnahme-Sicherheitswatchdog neu. In
`waiting_first_speech` besitzt es keine Wirkung.

```text
dritter Hotkey, sofern belegt
→ Wake-Word-Pause/-Fortsetzen toggeln
→ keine Wirkung auf die laufende Activation
```

```text
Wake Word
→ keine fachliche Wirkung
```

Weitere Activation-Trigger bleiben gesperrt.

## Nach Schließen des Eingabefensters und Rückkehr zu Idle

Activation-/Trigger-Lock wird aufgehoben.

Alle konfigurierten Triggerquellen werden wieder freigegeben.

Noch ausstehende Final-Ergebnisse älterer Activations werden korrekt
zugeordnet nachgereicht und blockieren die Bedienung nicht.

---

# 18. Überprüfbare Kerninvarianten

## I-1: Manual allein

```text
Hotkey im Idle
→ genau 1 Activation
→ gemeinsamer serverseitiger Recording-Lifecycle
→ genau 1 Finalisierung
→ Idle
```

## I-2: Wake Word allein

```text
Wake Word im Idle
→ genau derselbe Lifecycle
→ genau 1 Activation
→ gemeinsamer serverseitiger Recording-Lifecycle
→ genau 1 Finalisierung
→ Idle
```

## I-3: Wake Word startet, Hotkey aktualisiert den Timer

```text
Wake Word
→ Activation A
→ Recording

primärer Hotkey mit Active-Aktion refresh
→ laufenden Inaktivitätstimer ab dieser Interaktion neu setzen
→ keine kumulative Zeitgutschrift
→ keine zweite Activation
```

## I-4: Manual startet, zweiter Hotkey finisht

```text
Hotkey
→ Activation B

zweiter Hotkey mit Active-Aktion finish
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
- genau ein gemeinsamer Activation-/Recording-Pfad;
- genau ein Final;
- kein zweiter Pfad;
- zweiter Trigger wird unterdrückt.

## I-8: Trigger-Lock bleibt bis Idle

Das Ende eines einzelnen Audiosegments gibt die Triggerquellen nicht frei,
solange das Follow-up-Eingabefenster offen ist. Nach dessen sicherem Abschluss
kehrt der Vordergrund dagegen auch bei noch laufender Final-Transkription nach
`idle` zurück und gibt die Triggerquellen frei.

## I-9: Source-neutrales Feedback

Gleicher serverseitiger Zustand → gleiche fachliche UI-/Tray-/LED-/Sound-Darstellung, unabhängig vom ursprünglichen Trigger.

## I-10: Kein lokales VAD als Manual-Aufnahmeautorität

Das Ende einer manuell ausgelösten Aufnahme wird durch denselben serverseitigen VAD-/Lifecycle-Pfad bestimmt wie nach Wake Word.

## I-11: Kein dauerhafter Zwischenzustand

Jede Activation erreicht über regulären Abschluss, Finish, Cancel, Timeout, Reconnect oder Fehlerpfad wieder einen definierten stabilen Zustand.

## I-12: Mehrere Segmente bleiben eine Activation

Nach VAD-Ende eines Segments darf erneute Sprache im Follow-up ein weiteres
serielles Segment derselben Activation öffnen. Es entsteht keine neue
Activation und der Trigger-Lock bleibt gesetzt.

## I-13: Finish und Cancel sind fachlich sichtbar

Jeder akzeptierte Finish- oder Cancel-Command erzeugt genau eine korrelierbare
fachliche Lifecycle-Rückmeldung. Bei Finish erhält jedes bereits angenommene
Segment einen regulären terminalen Ausgang; bei Cancel erhält jedes Segment
einen verwerfenden/abgebrochenen terminalen Ausgang und kein Nutzresultat wird
anschließend veröffentlicht. Vor Cancel bereits veröffentlichter oder
eingefügter Text wird nicht zurückgenommen. Command-Replays und spätere
Commands nach derselben Transition erzeugen kein zweites Lifecycle-Ereignis.

## I-14: Reconnect setzt keine Activation fort

Eine beim Serververbindungsverlust aktive Activation wird verworfen. Die neue
Session beginnt in Idle; bereits veröffentlichter Text bleibt bestehen und
unveröffentlichte Resultate erscheinen später nicht mehr.

## I-15: Triggerlose Laufzeit ist nicht persistiert

Null effektive Trigger dürfen während derselben Client-Laufzeit Reconnects,
neue Sessions und Geräteverlust überstehen. Nach Client-Neustart gilt wieder
eine persistierte Basiskonfiguration mit mindestens einer funktionsfähigen
Triggerquelle.

Manual und Wake Word werden dabei getrennt unterdrückt. Eine zusätzliche
Sammelaktion „alle Trigger pausieren“ existiert nicht.

## I-16: Activation-Einstellungen sind unveränderlich

Eine Activation verwendet vom Start bis zu ihrem terminalen Abschluss exakt
den beim Start bestätigten Einstellungs-Snapshot. Spätere Änderungen wirken
frühestens gemäß ihrer Apply-Policy und niemals rückwirkend.

## I-17: Schutzablauf bewahrt Anwenderarbeit

Der Daueraufnahme-Watchdog beendet die gesamte Activation, verarbeitet das
erfasste Audio jedoch regulär. Automatisches Verwerfen ist nur ein letzter,
explizit begründeter Fehlerpfad.

## I-18: Hintergrund-Finalisierung blockiert keine neue Activation

Nach sicherem Eingabeschluss darf eine neue Activation beginnen, obwohl
ältere Activations noch `draining` sind. Kein verspätetes Ergebnis darf dabei
Zustand, ID oder Settings-Snapshot einer neueren Activation übernehmen.

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
> Während des laufenden Prozesses führen Hotkeys ihre konfigurierte
> Active-Aktion aus. `refresh` setzt den Inaktivitätstimer neu und kumuliert
> niemals Zeit. Weitere Wake Words haben **keine direkte fachliche Wirkung**.
>
> Nach vollständiger Rückkehr zu Idle werden die konfigurierten Triggerquellen wieder freigegeben.
