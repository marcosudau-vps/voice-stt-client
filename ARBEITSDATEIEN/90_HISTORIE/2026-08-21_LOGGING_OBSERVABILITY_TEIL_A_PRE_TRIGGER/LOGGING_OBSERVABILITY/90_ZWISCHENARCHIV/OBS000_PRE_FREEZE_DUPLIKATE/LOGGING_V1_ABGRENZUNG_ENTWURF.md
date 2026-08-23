# Logging-/Observability-V1 – Abgrenzung der ersten Implementierungsstufe

**Status:** Erster Entwurf / noch nicht freigegeben  
**Bezug:** `LOGGING_ZIELARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md`  
**Zweck:** Klare Abgrenzung dessen, was vor der Triggerarchitektur-Migration implementiert werden soll

---

# 1. Ziel von V1

V1 schafft eine belastbare **Observability Foundation** für die kommende Triggerarchitektur-Migration.

V1 ist keine eigene Kurzzeitarchitektur, sondern die erste Teilimplementierung des langfristigen Zielbilds.

> **Featureumfang klein – Architektur nicht kurzsichtig.**

---

# 2. Warum V1 vorgezogen wird

Die kommende Migration verändert unter anderem:

- ActivationController;
- Trigger-Lock;
- Finalisierung;
- Runtime-State-Sync;
- Continuous Streaming;
- Client ActivationMirror;
- Hotkeysemantik;
- Reconnect;
- Settings.

V1 soll früh ermöglichen, vollständige Abläufe strukturiert zu rekonstruieren.

---

# 3. V1 – verbindlicher Scope

## 3.1 Canonical Record

- [ ] gemeinsames kanonisches Recordmodell;
- [ ] Producer/Herkunft;
- [ ] Channel;
- [ ] Level;
- [ ] Type;
- [ ] Component;
- [ ] Zeitfelder;
- [ ] Session ID;
- [ ] Generation;
- [ ] Activation ID;
- [ ] Segment ID;
- [ ] Command ID;
- [ ] Event ID;
- [ ] Correlation ID;
- [ ] Message;
- [ ] Details;
- [ ] Raw;
- [ ] Replay-Flag.

## 3.2 Lokale Python-Logs

- [ ] eigener `logging.Handler`;
- [ ] bestehendes Python-Logging bleibt erhalten;
- [ ] definierte strukturierte `extra`-Felder.

## 3.3 Strukturierte Client-Observability-Events

Mindestens Integrationspunkte für:

- [ ] App-/Controller-Start;
- [ ] WebSocket Connect/Disconnect;
- [ ] Reconnect;
- [ ] Hotkey;
- [ ] Trigger send;
- [ ] Trigger ack;
- [ ] Audio Stream Start/Stop;
- [ ] Settings Apply;
- [ ] Feedback Dispatch;
- [ ] relevante Fehler.

Diese Records beobachten nur den Ablauf und lösen keine fachlichen Aktionen aus.

## 3.4 Server Live Adapter

- [ ] bestehende Server Live Events/Logs parallel konsumieren;
- [ ] Server-Channels erhalten;
- [ ] Originalpayload erhalten;
- [ ] Event ID / Replay erhalten;
- [ ] keine Abhängigkeit des FeedbackControllers vom Logger;
- [ ] Logging nicht als Runtime-Control-Plane verwenden.

## 3.5 Non-Blocking Ingress

- [ ] bounded Queue;
- [ ] Producer blockieren nie;
- [ ] Drop-Strategie;
- [ ] Drop-Counter;
- [ ] interner Health-State.

## 3.6 Worker

- [ ] Hintergrundworker;
- [ ] Batch-Writes;
- [ ] sauberes Start/Stop;
- [ ] Flush bei kontrolliertem Shutdown;
- [ ] Workerfehler bleiben isoliert.

## 3.7 SQLite

- [ ] Storage-Interface;
- [ ] SQLite-Implementierung;
- [ ] Schema-Version;
- [ ] zentrale Indizes;
- [ ] Retention;
- [ ] Cleanup;
- [ ] Dedupe für Server-Replay.

## 3.8 Optional File Sink

Mindestens einer:

- [ ] JSONL **oder**
- [ ] Text.

Ob beide bereits V1 werden, vor Implementierung entscheiden.

## 3.9 Local Query Provider

- [ ] Filter;
- [ ] Zeitbereich;
- [ ] Pagination;
- [ ] Producer;
- [ ] Channel;
- [ ] Level;
- [ ] Type;
- [ ] Component;
- [ ] Session;
- [ ] Activation;
- [ ] Segment;
- [ ] Freitext.

## 3.10 Query Service

- [ ] UI spricht nur mit Query Service;
- [ ] Provider-Schnittstelle ist bereits für spätere Remote-Provider geeignet.

## 3.11 Minimal Log View

- [ ] Tabelle;
- [ ] Zeit;
- [ ] Producer/Source;
- [ ] Channel;
- [ ] Level;
- [ ] Type;
- [ ] Component;
- [ ] Message;
- [ ] Detailansicht;
- [ ] strukturierte Details;
- [ ] Raw JSON;
- [ ] grundlegende Filter;
- [ ] Live-Ansicht;
- [ ] History-Ansicht;
- [ ] Kontextfilter für Session/Activation/Segment.

## 3.12 Logging Settings

- [ ] Logging enabled;
- [ ] lokale Historie enabled;
- [ ] Retention;
- [ ] Max Entries;
- [ ] File Sink enabled;
- [ ] File Format;
- [ ] File Directory;
- [ ] Log Level;
- [ ] Transkriptinhalt speichern ja/nein;
- [ ] Raw Payload speichern ja/nein;
- [ ] Live Buffer Size.

---

# 4. Noch NICHT in V1

Architektonisch berücksichtigt, aber nicht zwingend jetzt implementiert:

- [ ] ServerHistoryProvider;
- [ ] globale Serverlogs;
- [ ] Admin-Authentifizierung;
- [ ] Admin-Capability-UI;
- [ ] ServerAdminService;
- [ ] serverweite Config im Desktopclient;
- [ ] LED Adapter;
- [ ] MySQL/PostgreSQL;
- [ ] Remote Collector;
- [ ] Exportdialog;
- [ ] gespeicherte Filterpresets;
- [ ] komplexe Farbregeln;
- [ ] Charts/Statistiken;
- [ ] externe Debug-App;
- [ ] REST-/CLI-Query;
- [ ] Multi-Host-Aggregation.

---

# 5. Schnittstellen, die schon in V1 zukunftsfest sein sollen

## Adapter

```text
Producer
→ Adapter
→ Canonical Record
```

## Storage

```text
LogStore
→ SQLiteLogStore
```

## Query

```text
LogProvider
→ LocalLogProvider
```

## Query Service

```text
LogQueryService
→ Provider
```

## UI

```text
UI
→ LogQueryService
```

## Admin-Abgrenzung

Keine Admin-Logik im Logging-Core.

Später:

```text
ServerHistoryProvider
→ ServerControlConnection
```

---

# 6. Zwingende Failure-Isolation-Tests

## F-1 Logging deaktiviert
- [ ] Client funktioniert fachlich identisch.

## F-2 SQLite nicht beschreibbar
- [ ] Audio funktioniert.
- [ ] WebSocket funktioniert.
- [ ] Trigger funktionieren.
- [ ] Activation funktioniert.
- [ ] Feedback funktioniert.

## F-3 File Sink kaputt
- [ ] keine fachliche Auswirkung.

## F-4 Queue voll
- [ ] Producer blockiert nicht.
- [ ] Dropstrategie greift.
- [ ] App bleibt bedienbar.

## F-5 LoggingWorker Exception
- [ ] App bleibt bedienbar.
- [ ] Health-State wird gesetzt.

## F-6 fehlerhafter Record
- [ ] Record wird verworfen/quarantänisiert.
- [ ] Producerpfad bleibt unbeeinflusst.

## F-7 Serverevent-Replay
- [ ] keine unkontrollierte doppelte Persistenz.

---

# 7. Performance-Gate

- [ ] Audio-Callback-Latenz ohne Logging messen.
- [ ] mit Logging messen.
- [ ] WebSocket-Send-/Receive-Pfad prüfen.
- [ ] UI-Responsiveness prüfen.
- [ ] Burst mit Performance-/Debug-Records testen.
- [ ] Queue-Overload testen.
- [ ] SQLite Batchgröße prüfen.

Ziel:

> Kein fachlich relevanter Einfluss auf Audio-/Trigger-/WebSocket-Laufzeit.

---

# 8. Security-/Privacy-Gate

- [ ] Secrets redigiert.
- [ ] zukünftiger Admin-Key nicht logbar.
- [ ] Authorization Header redigiert.
- [ ] Transkriptcontent konfigurierbar.
- [ ] Raw Payload konfigurierbar/granular.
- [ ] DB-Dateirechte geprüft.
- [ ] File-Sink-Dateirechte geprüft.

---

# 9. Empfohlene V1-Modulstruktur

```text
core/
└── observability/
    ├── models.py
    ├── normalizer.py
    ├── ingress.py
    ├── manager.py
    ├── health.py
    ├── worker.py
    ├── adapters/
    │   ├── python_logging.py
    │   ├── client_events.py
    │   └── server_live.py
    ├── storage/
    │   ├── base.py
    │   └── sqlite.py
    ├── query/
    │   ├── base.py
    │   ├── local.py
    │   └── service.py
    └── sinks/
        ├── text_file.py       # optional V1
        └── jsonl_file.py      # optional V1

ui/
└── logs/
    ├── log_page.py
    ├── log_table_model.py
    ├── log_filter_bar.py
    └── log_detail_view.py
```

---

# 10. Nicht mit V1 vermischen

V1 darf nicht gleichzeitig:

- Triggerarchitektur reparieren;
- ActivationMirror bauen;
- Continuous Streaming einführen;
- `mode` entfernen;
- Hotkeysemantik ändern;
- Feedbacklogik fachlich umbauen;
- Server-Lifecycle ändern.

Ausnahme:

Nur minimale, rein beobachtende Hooks dürfen ergänzt werden.

Wenn Logging einen fachlichen Runtime-Umbau voraussetzt, ist die Logging-Architektur zu überprüfen.

---

# 11. Eigener Commit

V1 wird als eigener, klar identifizierbarer Commit abgeschlossen.

Vor Commit:

- [ ] vollständige Client-Suite;
- [ ] Logging-Tests;
- [ ] Failure-Isolation;
- [ ] Performance-Smoke;
- [ ] `git diff --check`;
- [ ] keine Triggerarchitektur-Reparaturen im selben Diff.

Dieser Commit bildet die **Observability Baseline** für die eigentliche Migration.

---

# 12. Definition of Done V1

V1 ist fertig, wenn:

- [ ] Client- und Server-Live-Daten in ein gemeinsames Recordmodell überführt werden können;
- [ ] lokale Python-Logs erfasst werden;
- [ ] kritische Clientabläufe strukturiert beobachtbar sind;
- [ ] SQLite-Historie funktioniert;
- [ ] Query Layer funktioniert;
- [ ] minimale Logansicht funktioniert;
- [ ] Logging Settings funktionieren;
- [ ] Replay dedupliziert wird;
- [ ] Retention funktioniert;
- [ ] Loggingfehler fachlich isoliert sind;
- [ ] Queue bounded und non-blocking ist;
- [ ] Tests Logging-Ausfälle aktiv provozieren;
- [ ] kein kritischer Runtimepfad vom Logging abhängt;
- [ ] spätere Endzustands-Schnittstellen nicht verbaut wurden.

---

# 13. Offene Entscheidungen vor Implementierung

- [ ] endgültiges Canonical Record Schema;
- [ ] endgültige Feldnamen;
- [ ] `producer_kind` Werte;
- [ ] Client-Channels;
- [ ] Dedupe-Schlüssel;
- [ ] SQLite-Schema;
- [ ] Schema-Migration;
- [ ] DB-Pfad;
- [ ] Retention Defaults;
- [ ] Queuegröße;
- [ ] Prioritäts-/Dropstrategie;
- [ ] JSONL und/oder Text in V1;
- [ ] Default für Transkriptinhalt;
- [ ] Default für Raw Payload;
- [ ] genauer ServerLiveAdapter-Hook;
- [ ] genaue Client Structured Event Hooks;
- [ ] UI-Tab/Seite;
- [ ] Konfigurationsmodell;
- [ ] Shutdown-/Flush-Verhalten.

---

# 14. Übergang nach V1

```text
Observability V1 Commit
→ produktnahes Testfundament / rote Zieltests
→ Triggerarchitektur PLAN FREEZE
→ Server Activation Lifecycle
→ Protocol / State Sync
→ Continuous Stream
→ Client ActivationMirror
→ Hotkey-/Triggersemantik
→ weitere Pakete
```

Die Observability Foundation soll während dieser Migration möglichst stabil bleiben und hauptsächlich um neue strukturierte Beobachtungspunkte ergänzt werden.

---

# 15. Spätere Ausbaustufen

## V2 – Server Admin / Remote History

- ServerControlConnection;
- Admin Auth;
- Capability State;
- ServerHistoryProvider;
- globale Serverlogs;
- historische Serverlogs;
- ServerAdminService;
- Server Admin Settings UI.

## V3 – weitere Producer / Storage

- LED Adapter;
- weitere Prozesse;
- optionale SQL-/Remote-Backends;
- Remote Collector.

## V4 – erweiterte UX / Analyse

- gespeicherte Filter;
- komplexe Farblogik;
- Export;
- Statistiken;
- Charts;
- Debug-App.

Die Versionsnummern sind vorläufige Planungsnamen.

---

# 16. Kernaussage

V1 bleibt klein genug, um die Triggerarchitektur nicht unnötig zu verzögern.

Gleichzeitig wird sie auf Schnittstellen aufgebaut, die bereits das vollständige langfristige Zielbild berücksichtigen.

> **Featureumfang klein – Architektur nicht kurzsichtig.**
