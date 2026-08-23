# Entscheidungen vor Implementierung

**Zweck:** Alles, was sonst während der Implementierung spontan entschieden würde, wird hier vorher festgelegt.

## A. Bereits durch das Zielbild entschieden

- [x] Es gibt genau einen serverseitigen Activation-/Recording-/VAD-/Finalisierungspfad.
- [x] Manual und Wake Word sind Triggerquellen, keine Betriebsmodi.
- [x] Der erste akzeptierte Activation-Trigger gewinnt.
- [x] Während einer laufenden Activation werden weitere Wake-Word-Trigger fachlich unterdrückt.
- [x] Der normale Hotkey bedeutet im Idle `activate`.
- [x] Der normale Hotkey bedeutet während einer laufenden Activation `finish`.
- [x] Wake-Word-Pause erhält einen separaten Hotkey.
- [x] Der Client besitzt keine unabhängige fachliche Aufnahme-/Diktat-State-Machine.
- [x] Das lokale VAD ist keine Manual-Aufnahmeautorität.
- [x] Der Audiostream ist sessiongebunden, nicht activationgebunden.
- [x] UI/Tray/LED/Sound stellen Lifecycle-Zustände source-neutral dar.
- [x] `session.mode` darf keine Runtime-Autorität besitzen.
- [x] Triggerquellen werden erst im stabilen Idle wieder für neue Activations freigegeben.

## B. Noch vor AP-1 verbindlich entscheiden

### B1. Exakte Serverphasen
- [ ] Kanonische Phase-Namen festlegen.
- [ ] Festlegen, ob `activation_closed` weiterhin benötigt wird.
- [ ] Semantik von `closed` eindeutig definieren.
- [ ] Semantik von `finalizing` eindeutig definieren.
- [ ] Semantik von `finalized` eindeutig definieren.
- [ ] Eindeutigen Freigabepunkt des Trigger-Locks bestimmen.

### B2. Client-Resynchronisierung
**Wichtiger Architekturpunkt:** Ein Client-Watchdog darf nicht einfach selbst „Idle“ erfinden, wenn der Server alleinige Autorität ist.

- [ ] Verhalten bei ausbleibendem Finalized-Event festlegen.
- [ ] Empfehlung prüfen: `UNKNOWN/STALE → State-Snapshot anfordern oder reconnect`, statt lokal Idle zu behaupten.
- [ ] Festlegen, welche Server-State-Snapshot-Nachricht nach Connect/Reconnect geliefert wird.
- [ ] Festlegen, wie verlorene Eventstream-Ereignisse erkannt werden.
- [ ] Festlegen, ob Timeline-Fallback genügt oder explizite State-Synchronisation erforderlich ist.

### B3. Extend
- [ ] Wird `extend` weiterhin als Benutzerfunktion benötigt?
- [ ] Falls ja: eigener Hotkey, Tray-Aktion oder nur API?
- [ ] Normaler Diktat-Hotkey darf `extend` niemals auslösen.
- [ ] Semantik und erlaubte Serverphasen für `extend` festlegen.

### B4. Mute
- [ ] Exakte Semantik festlegen: Streamverbindung bleibt offen, aber Audio wird nicht gesendet / Null-Audio / Capture pausiert?
- [ ] Sicherstellen, dass Mute nicht wieder Session- und Activation-Lifecycle vermischt.
- [ ] Verhalten von Wake-Word-Erkennung während Mute festlegen.

### B5. Wake-Word-Katalog
- [ ] Für diese Reparatur nur Mindestlösung (Text/CSV-Feld) oder direkt echte Mehrfachauswahl?
- [ ] Falls Mehrfachauswahl: Capability-/API-Vertrag für verfügbaren Katalog definieren.
- [ ] Default-Wake-Word festlegen.
- [ ] Verhalten bei unbekanntem Wake Word festlegen.

### B6. Zeitwerte / Single Source of Truth
Heute existieren doppelte Zeitwerte auf Client und Server.

- [ ] Server als alleinige Quelle für Activation-Timings bestätigen.
- [ ] Festlegen, welche Werte vom Client konfigurierbar sein dürfen.
- [ ] Doppelte `dictation_window`-Werte entfernen oder nur als Darstellung verwenden.
- [ ] Defaultwerte zentral definieren.
- [ ] Server-resolved Werte an Client zurückmelden.

### B7. Legacy-Adapter
- [ ] Exakt definieren, welche alten Clients weiter unterstützt werden müssen.
- [ ] Legacy-Adapter darf nur am Protokollrand existieren.
- [ ] Festlegen, wann/ob der Adapter später entfernt wird.
- [ ] Browserclient ausdrücklich als aktueller Client oder Legacy-Konsument klassifizieren.

### B8. Protokoll-ID-/Versionierungsmodell
- [ ] `sessionId` Owner/Lifetime.
- [ ] `generation` Owner/Lifetime.
- [ ] `activationId` Owner/Lifetime.
- [ ] `commandId` Idempotenz.
- [ ] `eventId`/Cursor für Replay.
- [ ] Regeln für stale Events und stale Acks.
- [ ] Snapshot/Event-Version festlegen.

## C. Entscheidungen dokumentieren

Für jede offene Entscheidung:

- [ ] Entscheidung formuliert.
- [ ] Alternativen genannt.
- [ ] Grund genannt.
- [ ] Auswirkung auf Server dokumentiert.
- [ ] Auswirkung auf Client dokumentiert.
- [ ] Auswirkung auf Tests dokumentiert.
- [ ] In `16_TRACEABILITY_MATRIX.md` verlinkt.
