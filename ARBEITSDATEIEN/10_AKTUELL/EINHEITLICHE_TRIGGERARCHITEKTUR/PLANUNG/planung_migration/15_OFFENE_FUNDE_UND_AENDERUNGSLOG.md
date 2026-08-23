# Offene Funde und Änderungslog

**Zweck:** Neue Erkenntnisse aufnehmen, ohne den roten Faden zu verlieren.

## Verwendung

Für jeden neuen Fund einen Block kopieren:

```markdown
### FIND-XXX – Kurztitel
- Datum:
- Gefunden durch:
- Beobachtung:
- Betroffene Repos/Dateien:
- Betroffene Zielbild-Invarianten:
- Vermutete Phase/AP:
- Blockiert aktuelles Gate? JA/NEIN
- Wenn JA: warum?
- Wenn NEIN: wann bearbeiten?
- Evidence:
- Status: OPEN / CONFIRMED / RESOLVED / NOT-A-BUG
```

---

## Bereits bekannte Kerndefekte

### FIND-001 – Client bleibt nach Activation aktiv
- [x] Bestätigt.
- Ziel-AP: ClientMirror + Server Finalisierung.
- Status: CONFIRMED.

### FIND-002 – `session.mode` besitzt Runtime-Autorität
- [x] Bestätigt.
- Ziel-AP: Config-Migration.
- Status: CONFIRMED.

### FIND-003 – Wake-Word-Gruppe leer
- [x] Bestätigt.
- Ziel-AP: Settings/Wake Word.
- Status: CONFIRMED.

### FIND-004 – Warnloop „Aktion derzeit nicht verfügbar“
- [x] Bestätigt.
- Ziel-AP: Client Lifecycle + Feedback.
- Status: CONFIRMED.

### FIND-005 – normaler Hotkey hat falsche Zweitbedeutung
- [x] Bestätigt.
- Ziel-AP: Trigger/Hotkey.
- Status: CONFIRMED.

### FIND-006 – Source-Merge statt First-Trigger-Lock
- [x] Bestätigt.
- Ziel-AP: Server Activation.
- Status: CONFIRMED.

### FIND-007 – Continuous Streaming nicht erreicht
- [x] Bestätigt.
- Ziel-AP: Continuous Stream.
- Status: CONFIRMED.

### FIND-008 – source-abhängige Darstellung
- [x] Bestätigt.
- Ziel-AP: UI/Feedback.
- Status: CONFIRMED.

### FIND-009 – Manual-Aufnahmefeedback fällt auf falsche Basisdarstellung zurück
- [x] Bestätigt.
- Ziel-AP: ClientMirror + UI.
- Status: CONFIRMED.

---

## Neue Funde

Noch keine. Neue Erkenntnisse aus Claudes Code-Only-Atlas hier ergänzen.
