# Architekturentscheidungen – kuratierte Übersicht

## Kurz und einfach erklärt

Bei der Entwicklung gab es oft mehrere technisch mögliche Wege.

Diese Datei hält nicht nur fest:

> „Was wurde gebaut?“

sondern:

> „Warum wurde genau diese Variante gewählt – und welche Alternative wurde bewusst nicht genommen?“

So muss eine spätere Änderung nicht dieselbe Diskussion noch einmal von vorn führen.

---

## DEC-001 – eigenes Paket `core/observability`

### Entscheidung

```text
core/observability/
```

### Warum

Die neue Infrastruktur ist mehr als klassisches Python-Logging und umfasst Modell, Normalisierung, Ingress, Worker, Store, Query und Adapter. `logging` als Paketname hätte außerdem unnötig mit bestehendem Logging/Python-Begriffen kollidiert.

---

## DEC-002 – Observability ist nie Runtime-Autorität

### Entscheidung

Logging beeinflusst keinen fachlichen Lifecycle und keinen Business-Rückgabewert.

### Konsequenz

Fehler müssen an der Beobachtergrenze isoliert werden.

---

## DEC-003 – Fan-out statt Middleware

### Entscheidung

```text
Event
├→ Fachlogik
└→ Observability
```

nicht:

```text
Event → Observability → Fachlogik
```

### Warum

Die Fachlogik darf nicht von einem Diagnosebaustein abhängen.

---

## DEC-004 – kein Memory-Ringbuffer

### Ursprüngliche Idee

Live-Records zusätzlich im RAM halten.

### Entscheidung

Live tailt SQLite über denselben Provider wie History.

### Gründe

- nur eine lokale Wahrheit;
- keine zusätzliche Lock-/Ownership-Frage;
- UI vom Worker entkoppelt;
- gleicher Querypfad für History und Live;
- UI zeigt nur persistierte Records;
- weniger Komponenten.

---

## DEC-005 – eine Queue statt High-/Low-Queues

### Entscheidung

Eine bounded Queue mit 75-%-Wasserstandsregel.

### Warum

Zwei Queues hätten zusätzliche Cross-Queue-Manipulation, Buchführung und Fehlerfläche erzeugt, ohne einen entsprechend großen Nutzen.

---

## DEC-006 – SQLite als lokale persistente Wahrheit

### Warum

SQLite bietet:

- Filter;
- Pagination;
- Dedupe;
- Retention;
- Neustartpersistenz;
- lokalen Betrieb ohne Zusatzdienst.

---

## DEC-007 – bestehendes `client.log` bleibt

### Warum

- unabhängiger Fallback;
- bewährte Diagnosequelle;
- Observability-Ausfall bleibt beobachtbar;
- kein unnötiger gleichzeitiger Rückbau des alten Loggingpfads.

---

## DEC-008 – V1-File-Sink nur JSONL

### Entscheidung

Kein Text-/Formatdropdown.

### Warum

Eine Option mit genau einem echten Wert wäre Überkonfiguration. Weitere Formate gehören in OBS-150.

---

## DEC-009 – `max_db_bytes` ist Warnsignal

### Entscheidung

Kein automatisches Ändern von Retention-Policies.

### Warum

`retention_days` und `max_entries` existieren bereits. Ein dritter selbsttätiger Regler würde zusätzliche Fehlerpfade schaffen.

---

## DEC-010 – kein automatisches VACUUM

### Entscheidung

Kein `VACUUM`, `auto_vacuum` oder `incremental_vacuum` im normalen Runtimepfad.

### Warum

Unnötiger schwerer I/O-/Lock-Pfad für eine Diagnoseinfrastruktur.

---

## DEC-011 – Query-Schicht zwischen UI und Store

```text
UI → LogQueryService → Provider
```

### Warum

- UI bleibt DB-agnostisch;
- Remote Provider später möglich;
- bessere Testbarkeit;
- saubere Qt/Core-Grenze.

---

## DEC-012 – Raw lazy laden

### Warum

Große Payloads sind für eine Tabellenübersicht unnötig. Raw wird erst beim ausgewählten Record benötigt.

---

## DEC-013 – kein History-/Live-Mischbetrieb in V1

### Warum

Eine Mischansicht verlangt gleichzeitig Dedupe, Reordering, Filterwechsel und mehrere Cursorrichtungen. Das wäre der aufwendigste Teil der Log-UI gewesen und war für das V1-Ziel nicht nötig.

---

## DEC-014 – `activation_id` speichern, aber nicht als Wahrheit verwenden

### Warum

Gerade falsch oder widersprüchlich zugeordnete Activation-IDs sind für die kommende Trigger-Migration diagnostisch wertvoll.

Der Client soll sie nicht „reparieren“, indem er eigene Annahmen hineinmischt.

---

## DEC-015 – Servereventstruktur erhalten

### Entscheidung

Serverevent-ID, Cursor, Channel, Typ, Zeit, Replay und optional Raw möglichst verlustarm übernehmen.

### Warum

Forensik soll nicht von einer reduzierten menschenlesbaren Meldung abhängen.

---

## DEC-016 – kein Logtext-Parsen als Datenquelle

### Entscheidung

`message` dient der Darstellung.

Keine Lifecycleentscheidung aus Strings wie:

```text
"Recording started"
```

ableiten.

---

## DEC-017 – Hot Paths nur minimal instrumentieren

### Entscheidung

Keine Record-pro-Paket-/Frame-Flut.

### Warum

Das Diagnosewerkzeug darf nicht die Performance verschlechtern, die es beobachten soll.

---

## DEC-018 – V1 / Teil B splitten

```text
Teil A vor Trigger-Migration
Teil B danach
```

### Warum

Die Migration braucht gute Diagnostik. Remote-Admin-, weitere Sink- und Forensikfunktionen dürfen den Hauptumbau aber nicht unnötig verzögern.

---

## DEC-019 – `/ws/transcribe` bleibt operative Wahrheit

### Entscheidung

```text
/ws/transcribe + lokale Clientereignisse
→ operative Zustands-/Feedbackachse

/ws/logs
→ Beobachtung, Diagnose, Replay, History
```

### Warum

Der Logstream ist asynchron/bounded und Replay darf keine vergangenen Bedienimpulse erneut auslösen. Eine zweite operative State Machine wäre race-anfällig.

---

## DEC-020 – ehrlicher Zwischenabschluss statt künstlichem 100-%-Gate

### Entscheidung

Die V1-Foundation wird als belastbarer Arbeitsstand akzeptiert, obwohl einzelne formale Restprüfungen offen blieben.

### Warum

Mehrere dieser Integrationsgrenzen werden durch die unmittelbar folgende Triggerarchitektur ohnehin verändert und danach erneut validiert.

### Konsequenz

Kein falsches historisches `G-OBS-V1 PASS` behaupten.
