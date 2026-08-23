# Tests, Validierung und Garantien

## Kurz und einfach erklärt

Tests beweisen nicht, dass niemals irgendein Fehler existiert.

Sie sollen aber wichtige Versprechen absichern, zum Beispiel:

> „Wenn die Logdatenbank kaputtgeht, darf deshalb nicht die Aufnahme kaputtgehen.“

oder:

> „Wenn der Server beim Reconnect denselben Event noch einmal liefert, darf er nicht doppelt in der lokalen Historie landen.“

Diese Datei beschreibt die abgesicherten **Eigenschaften**, nicht jede einzelne Testfunktion.

---

## 1. Testebenen

### Unit

Einzelne Bausteine:

- Canonical Model;
- Normalizer;
- Redaction;
- Priorität;
- Health;
- Queryfilter;
- Retention;
- Store.

### Integration

Ketten:

```text
Python logging → SQLite
Serverevent → SQLite
Clientevent → SQLite
SQLite → Provider → Query
Query → UI-Model
```

### Failure Injection

Absichtlich provozierte Fehler:

- SQLite read-only;
- SQLite locked;
- ungültiger DB-Pfad;
- File-Sink-Fehler;
- Queue voll;
- Workerexception;
- malformed event;
- UI-/Queryfehler.

### Runtime Isolation

Prüft, dass Observabilityfehler keinen fachlichen Clientpfad beschädigen.

### Mutation Checks

Ein Schutz wird absichtlich entfernt und der zugehörige Test muss rot werden.

---

## 2. Zentrale Garantien

### Canonical Model

Unterschiedliche Quellen können in einen stabilen gemeinsamen Recordvertrag überführt werden.

### Non-Mutation

Normalisierung darf Quellstrukturen nicht unkontrolliert verändern.

### Non-Throwing Observer Boundary

Ein Fehler im Beobachter darf nicht bis in den fachlichen Eventdispatcher eskalieren.

### Non-Blocking

Producer warten nicht auf Store-/File-I/O.

### Bounded Memory

Queue und Abfrageverhalten bleiben begrenzt.

### Dedupe

Derselbe Serverevent kann beim Replay nicht unkontrolliert doppelt persistiert werden.

### Pagination

Mehrseitige History-Abfragen bleiben innerhalb des Cursorvertrags lücken-/duplikatarm.

### Query Independence

UI arbeitet über Provider/Service, nicht direkt über SQLite.

### Failure Isolation

Store-/Sink-/Worker-/Queryprobleme bleiben Observability-Probleme.

### Shutdown

Queue/Worker/Store werden kontrolliert beendet.

---

## 3. Besonders wichtige Mutation Checks

Beispiele aus V1:

```text
ON CONFLICT DO NOTHING entfernen
→ Dedupe-Test muss rot werden

Observer-except entfernen
→ Isolationstest muss rot werden

put_nowait durch blockierendes put ersetzen
→ Backpressure-Test muss rot werden

Wasserstandsregel entfernen
→ Queue-/Backpressure-Test muss rot werden

Redaction-Aufruf entfernen
→ Content-/Redaction-Test muss rot werden

partielle event_id-Bedingung entfernen
→ Dedupe-Vertrag muss auffallen

PRAGMA query_only entfernen
→ Reader-Schutz-Test muss auffallen
```

Der Zweck: beweisen, dass ein Test tatsächlich den Schutz abdeckt und nicht nur zufällig grün ist.

---

## 4. OBS-060 Hardening

OBS-060 bündelte insbesondere:

- Failure Injection;
- Performanceprobes;
- Runtime-Isolation;
- Recovery;
- Shutdown/Flush;
- Policyprobes;
- Evidence;
- Produktionspfad-Abnahme.

Der Implementierungsstand wurde anschließend in einem eigenen lokalen Checkpoint gesichert.

---

## 5. Historischer Teststand des akzeptierten V1-/UI-Polish

Zum Abschluss wurde berichtet:

```text
fokussiert:
197 passed
305 subtests passed

derselbe Lauf mit -W error:
197 passed
305 subtests passed

gesamter Client:
1191 passed
862 subtests passed

compileall:
erfolgreich

git diff --check:
sauber
```

Diese Zahlen sind eine Momentaufnahme.

Für spätere Arbeit gilt:

> Immer die **aktuell vollständige** vorhandene Suite ausführen – nicht eine alte Mindestzahl als Definition von „vollständig“ verwenden.

---

## 6. Warum kein erfundenes `G-OBS-V1 PASS`

Der letzte formale Gate-Stand hatte noch offene Punkte, insbesondere:

- vollständiges manuelles Produktionsprotokoll;
- Initial-Disabled→Enabled;
- einzelne Evidence-/Entscheidungsreste.

Die Projektentscheidung lautete:

```text
V1 als belastbaren Zwischenabschluss akzeptieren
→ Triggerarchitektur fortsetzen
→ betroffene End-to-End-Grenzen danach erneut validieren
```

Darum behauptet diese Produktdokumentation keinen historischen 100-%-PASS, der nicht tatsächlich dokumentiert wurde.

---

## 7. Was bereits stark abgesichert ist

Automatisiert weitreichend geprüft wurden insbesondere:

- passive Beobachtungsarchitektur;
- Canonical Records;
- Queue/Backpressure;
- SQLite-Persistenz;
- Replay-Dedupe;
- Query/Pagination;
- Failure Isolation;
- Settings-/UI-Verträge;
- Regressionen bestehender Clientpfade.

---

## 8. Was sinnvoll manuell geprüft wird

Menschen sollten vor allem Dinge beurteilen, die tatsächlich menschliche Wahrnehmung brauchen:

- Layout;
- Lesbarkeit;
- Filterbedienung;
- Live-Aktualisierung;
- Auto-Scroll;
- Details/Raw;
- normaler Realbetrieb des Clients;
- subjektive UI-Reaktionsfähigkeit.

SQL-Konsistenz, Dedupe, Retention oder ACLs gehören dagegen eher in automatisierte/agentische Prüfung.

---

## 9. Evidence liegt getrennt

Detaillierte Nachweise:

```text
ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/
```

Die Trennung ist beabsichtigt:

```text
Produktdokumentation → erklärt das System
Evidence             → beweist konkrete Umsetzung und Gates
```

---

## 10. Regression bei Teil B

Nach der Triggerarchitektur-Migration muss OBS-100 nicht nur neue Instrumentierung testen, sondern auch beweisen, dass die V1-Invarianten erhalten bleiben:

- keine Runtime-Autorität;
- keine Blockade;
- Store/Query weiterhin korrekt;
- neue Trigger-/Activation-Events korrelierbar;
- keine doppelte Eventwelt.
