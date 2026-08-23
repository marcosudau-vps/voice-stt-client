# Logging & Observability V1 – Betrieb und Diagnose

**Produktdokumentation – RealtimeSTT Client**

## 1. Zweck der Diagnoseoberfläche

Die Logansicht ist für zwei typische Aufgaben gedacht:

1. **Live beobachten:** Was passiert gerade im Client und im verbundenen Serverpfad?
2. **Historisch untersuchen:** Welche Records gehörten zu einer bestimmten Session, Activation, einem Segment oder Command?

Die Oberfläche ist ein Consumer des Query-Layers. Sie ist nicht Teil des Logging-Workers und greift nicht direkt auf SQLite zu.

---

# 2. Hauptbereiche

Die Tabelle zeigt die wichtigsten Felder kompakt:

- Zeit;
- Quelle/Producer;
- Channel;
- Level;
- Typ;
- Komponente;
- Meldung.

Darunter stehen Detail- und Raw-Informationen für den ausgewählten Record.

Raw wird bewusst erst für den ausgewählten Record nachgeladen, statt für jede Tabellenzeile große Payloads im Speicher zu halten.

---

# 3. History-Modus

History dient der rückblickenden Analyse.

Erwartete Semantik:

- neueste Records zuerst;
- paginiertes Nachladen;
- ältere Seiten werden an die bestehende Historie angefügt;
- keine Duplikate an Seitengrenzen;
- Filter wirken server-/providerseitig, nicht durch komplettes Laden aller Records in die UI.

Typischer Ablauf:

```text
1. Zeitraum oder Session eingrenzen
2. nach Channel/Level/Typ filtern
3. interessanten Record auswählen
4. Details prüfen
5. Raw nur bei Bedarf öffnen
6. über IDs zu verwandten Records navigieren
```

---

# 4. Live-Modus

Live ist kein direkter Workerstream. Die UI fragt den lokalen Store regelmäßig nach Records mit einer ID größer als dem letzten bekannten Cursor ab.

Dadurch ist das Verhalten robust:

```text
Worker schreibt → SQLite
                → Live-Tail liest
```

Wenn der Worker ausfällt, erscheinen schlicht keine neuen persistenten Records. Die UI zeigt damit keinen Zustand vor, der nie auf Disk geschrieben wurde.

Beim Live-Test sollte geprüft werden:

- neue Records erscheinen ohne UI-Hänger;
- Auto-Scroll folgt dem Strom, wenn aktiviert;
- bei deaktiviertem Auto-Scroll springt die Ansicht nicht störend;
- Filterwechsel erzeugt keine sichtbaren Duplikate;
- Detail-/Raw-Ansicht bleibt zum aktuell ausgewählten Record konsistent.

---

# 5. Filter

Die Query-Schicht unterstützt insbesondere:

- Producer/Quelle;
- Channel;
- Level;
- Typ;
- Typ-Präfix;
- Komponente;
- Session-ID;
- Generation;
- Activation-ID;
- Segment-ID;
- Command-ID;
- Correlation-ID;
- Transcription-ID;
- Event-ID;
- Zeitbereich;
- Freitext;
- Replay ein-/ausschließen.

Freitext ist für die schnelle Suche gedacht; strukturierte Felder sind für belastbare Korrelation vorzuziehen.

## Activation-Filter

`activation_id` ist vor Abschluss der Triggerarchitektur-Migration diagnostisch hilfreich, aber nicht fachlich autoritativ. Ergebnisse dieses Filters deshalb nicht als alleinigen Beweis für einen Lifecycle-Zusammenhang verwenden.

---

# 6. Channels sinnvoll verwenden

Die getrennten Dimensionen helfen, Suchräume schnell zu verkleinern.

### `system`

Technische Zustände und Infrastruktur, z. B.:

- Verbindung;
- Reconnect;
- Eventstream;
- Konfiguration;
- interne Zustandsänderungen.

### `audit`

Absichtliche Aktionen und Steuerbefehle, z. B.:

- Hotkey;
- Command angefordert/abgeschlossen;
- Trigger gesendet;
- Ack empfangen;
- Settings Apply.

### `transcription`

Transkriptionsbezogene Ereignisse und – abhängig von der Privacy-Policy – Metadaten bzw. Inhalte.

### `performance`

Aggregierte technische Messwerte. Hochfrequente Rohdaten sollen hier nicht ungefiltert in Einzelrecords explodieren.

---

# 7. Praktischer Diagnoseworkflow

## Fall A: „Hotkey gedrückt, aber Verhalten unklar“

1. auf die relevante Session filtern;
2. Channel `audit` aktivieren;
3. nach `client.hotkey.*`, `client.command.*` und `client.trigger.*` suchen;
4. `command_id` vergleichen;
5. danach Server-/Transkriptionsrecords derselben Session untersuchen.

## Fall B: „Serverevent kam, aber Feedback sah falsch aus“

1. Session eingrenzen;
2. Serverevent anhand `event_id`/Typ suchen;
3. Replay-Flag prüfen;
4. zugehörige lokale Observation/Feedback-Records vergleichen;
5. beachten: Observability ist nur Beobachter – ein fehlender Logrecord ist nicht automatisch Beweis, dass die Fachlogik nicht lief.

## Fall C: „Logs fehlen“

Health und Zähler prüfen:

```text
state
queue_depth
enqueued
written
dropped_watermark
dropped_queue_full
store_errors
worker_errors
```

Mögliche Interpretation:

```text
enqueued steigt, written nicht
    → Worker/Store untersuchen

dropped_watermark steigt
    → Lastspitze / Backpressure

dropped_queue_full steigt
    → Queue vollständig ausgelastet

store_errors steigt
    → SQLite-/Pfad-/Lockproblem

worker_errors steigt
    → interner Workerfehler
```

---

# 8. Health-Zustände

V1 kennt u. a.:

| Zustand | Bedeutung |
|---|---|
| `ok` | normaler Betrieb |
| `dropping` | Backpressure führt zu kontrolliertem Verwerfen |
| `degraded_sink` | optionaler File-Sink gestört |
| `degraded_store` | Storeproblem, Betrieb teilweise möglich |
| `failed_store` | Persistenzpfad ausgefallen |
| `failed_worker` | Worker ausgefallen |
| `disabled` | Observability deaktiviert |

Die fachliche Anwendung soll auch in degradierenden/fehlgeschlagenen Loggingzuständen weiterarbeiten.

---

# 9. Klassisches Log und Observability unterscheiden

Es existieren bewusst zwei Diagnosewege:

```text
klassisches client.log
    → bestehender Logger-/Dateipfad

Observability Store
    → strukturierte, korrelierbare Diagnosehistorie
```

Bei einem Fehler der neuen Infrastruktur kann `client.log` deshalb weiterhin wertvoll sein.

---

# 10. Retention

V1 begrenzt den Store primär über:

- `retention_days`;
- `max_entries`.

`max_db_bytes` ist ein Warnsignal, keine automatische harte Bereinigungsaktion.

Bei Retention-Problemen zuerst prüfen:

- aktuelle DB-Größe;
- `retention_errors`;
- konfigurierte Tage;
- maximale Eintragszahl;
- Schreib-/Dateirechte.

---

# 11. JSONL-Sink

Der JSONL-Sink ist optional.

Eigenschaften:

- ein JSON-Objekt pro Zeile;
- für externe Sichtung oder einfache Verarbeitung geeignet;
- nicht die primäre lokale Wahrheit – das bleibt SQLite;
- unterliegt denselben Privacy-/Redaction-Regeln.

---

# 12. Privacy im Betrieb

## Transkriptionsinhalt

Wenn `store_transcription_content=false`:

- Transkriptionsereignisse dürfen als Metadaten sichtbar sein;
- der tatsächliche diktierte Text soll nicht persistent als Diagnoseinhalt gespeichert werden.

## Raw

Raw dient der tiefen Diagnose, kann aber bewusst deaktiviert werden. Bei der UI wird Raw nur bei Auswahl geladen.

## Secrets

Sollten in einer Diagnoseausgabe Zugangsdaten, Tokens oder Auth-Header im Klartext auftauchen, ist das ein Privacy-Befund und keine akzeptable „Debug-Ausnahme“.

---

# 13. Einstellungen

In „Logging & Diagnose“ befinden sich die nutzernahen Einstellungen, u. a.:

- Observability aktiv;
- Level;
- Store aktiv;
- Retention;
- maximale Einträge;
- optionaler File-Sink;
- Transcript-Content-Policy;
- Raw-Payload-Policy;
- Diagnosehistorie löschen;
- Logs anzeigen.

Low-Level-Werte wie `queue_size`, `batch_size`, `flush_interval_s`, `db_path` und `max_db_bytes` bleiben in `config.yaml`.

---

# 14. Bekannter Konfigurations-Randfall

Der letzte formale Gate-Review identifizierte einen Übergang, der noch nicht vollständig der vorgesehenen `IMMEDIATE`-Semantik entspricht:

```text
Client startet mit Observability = false
        ↓
zur Laufzeit auf true schalten
```

Wenn beim Start nur ein Null-/No-op-Pfad komponiert wurde, können Store und Worker nicht automatisch aus dem Nichts entstehen.

Dieser Punkt ist als Folgearbeit bekannt. Er ändert nichts an der grundsätzlichen V1-Architektur, ist aber bei Tests der Laufzeitaktivierung zu beachten.

---

# 15. UI-Polish und weitere Bedienverbesserungen

Nach OBS-050 wurde ein eigener UI-Polish durchgeführt. Die vollständige manuelle Endabnahme wurde bewusst nicht bis zum letzten Randfall erzwungen, weil der unmittelbar folgende Triggerarchitektur-Umbau mehrere Integrationspfade erneut verändert.

Bei weiteren UI-Arbeiten sind insbesondere folgende Power-User-Aspekte relevant:

- freie rechteckige Zellbereichsauswahl;
- Kopieren markierter Bereiche als tabellarisches Format;
- „Als JSON kopieren“ auf Basis vollständiger betroffener Records;
- noch eindeutigere visuelle Trennung von History und Live, ggf. Tabs;
- Typ-/Typ-Präfix-Auswahl über bekannte Werte;
- breite Freitextsuche einschließlich Typ.

Diese Punkte sind Bedienkomfort, nicht Kerninvarianten des Stores oder Ingress.

---

# 16. Wann ist ein Problem ein Logging-Problem?

Als Logging-/Observability-Problem gelten beispielsweise:

- UI zeigt falsche/duplizierte Records;
- Filter liefern nachweislich falsche Ergebnisse;
- Records werden trotz erlaubter Policy nicht persistiert;
- Secrets werden persistiert;
- Worker-/Storefehler beeinflussen die Hauptanwendung;
- Backpressure blockiert Producer;
- Replay erzeugt unkontrollierte Duplikate;
- Health/Zähler widersprechen dem tatsächlichen Verhalten.

Nicht automatisch Logging-Probleme sind fachliche Fehler in:

- Triggersemantik;
- Activation Lifecycle;
- Hotkeybedeutung;
- Wakeword-Verhalten;
- Aufnahme-/Finalisierungspfad.

Diese Bereiche werden im folgenden Triggerarchitektur-Umbau separat korrigiert.
