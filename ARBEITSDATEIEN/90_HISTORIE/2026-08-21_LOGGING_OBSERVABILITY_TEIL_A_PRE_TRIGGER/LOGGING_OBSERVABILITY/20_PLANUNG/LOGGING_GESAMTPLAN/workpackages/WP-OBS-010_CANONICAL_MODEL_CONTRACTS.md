---
id: OBS-010
status: READY
authority: planning
workstream: OBS
phase: A
depends_on: OBS-000
freeze_reference: 00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md
last_updated: 2026-08-15
---

# OBS-010 – Canonical Model, Redaction, Normalizer & Contracts

> **READY FOR IMPLEMENTATION.** Alle Architekturentscheidungen sind in OBS-000
> geschlossen. Dieses Paket enthält **keine** Architekturentscheidung mehr. Wird
> dennoch eine nötig: `DECISION REQUIRED` — anhalten, nicht selbst entscheiden.

## Vorbedingung

Der Arbeitsbaum von `voice-stt-client` ist festzuschreiben, bevor dieses Paket
beginnt (Commit der 22 offenen Änderungen oder ausdrückliche Bestätigung, dass
er unverändert bleibt). Grund und Details:
`40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md`.

---

## Ziel

Die stabilen, UI-/Storage-/Transport-unabhängigen Kernverträge implementieren.
Nach diesem Paket existiert das gemeinsame Datenmodell, die Redaction und die
Umwandlung aller drei Eingangsformen — **ohne** Qt, **ohne** SQLite, **ohne**
WebSocket, **ohne** Thread.

## Scope

- [ ] `core/observability/__init__.py` — nur Re-Exports
- [ ] `core/observability/models.py` — `CanonicalLogRecord`, `ProducerKind`,
      `Channel`, `Level`, `Scope`, `RecordPriority`
- [ ] `core/observability/redaction.py` — `unfreeze`, `redact_mapping`,
      `redact_text`, `shorten_user_paths`, `SENSITIVE_KEYS`, `TRANSCRIPT_KEYS`
- [ ] `core/observability/normalizer.py` — drei Eingänge, `LOGGER_CHANNEL_MAP`
- [ ] `core/observability/storage/base.py` — `LogStore`-Protokoll
- [ ] `core/observability/sinks/base.py` — `Sink`-Protokoll
- [ ] `core/observability/query/base.py` — `LogProvider`, `QueryFilter`,
      `QueryPage`, `ProviderStatus`, `ProviderState`, `LogRecordView`
- [ ] Signatur der strukturierten Client-Observation-API (`Ingress.event(...)`)
      als Protokoll, damit OBS-020 sie nur noch implementiert

## Non-Scope

- Kein Handler, kein Ingress, keine Queue, kein Worker, kein Store, keine UI.
- Keine Änderung an bestehendem Produktcode. **Dieses Paket legt ausschließlich
  neue Dateien an.**
- Keine stillen Änderungen außerhalb dieses Work Packages.
- Keine Änderung normativer Contracts ohne `DECISION REQUIRED`.
- Keine Git-History-Aktion ohne ausdrückliche Freigabe.

---

## Sollzustand – verbindliche Quellen

| Gegenstand | Fundstelle |
|---|---|
| Feldliste, Typen, Nullbarkeit, Sollzustand als Code | `CONTRACTS §1` |
| Prioritätsableitung | `CONTRACTS §1.5` |
| Wertemengen, offen vs. geschlossen, `source_severity` | `CONTRACTS §2.1` |
| Channels und ihre Bedeutung | `CONTRACTS §2.2` |
| `LOGGER_CHANNEL_MAP` — verbindliche Fassung | `CONTRACTS §3.1` |
| Serverpfad Feld für Feld, `meldung`, `log.gap` | `CONTRACTS §3.2` |
| `unfreeze()` und die zwölf Redaction-Regeln | `CONTRACTS §4` |
| Query-Protokolle und was bewusst fehlt | `CONTRACTS §8` |
| Schichtung und Importrichtung | `ARCH §5.2` |

## Implementierungsschritte

1. Enums und `CanonicalLogRecord` als frozen dataclass; `details`/`raw` beim Bau
   einfrieren (Muster `event_models._freeze`).
2. `priority` nach `CONTRACTS §1.5` — **inklusive** `not replayed`.
3. `redaction.py`: `SENSITIVE_KEYS`, `TRANSCRIPT_KEYS` als Modulkonstanten;
   `unfreeze` für `MappingProxyType`, `tuple`, `frozenset`; Tiefengrenze 16 und
   Knotengrenze 500.
4. `normalizer.py` mit den drei Eingängen; Redaction am **Ende** jedes Pfades;
   Zeitkonvertierung `record.created` → ISO-8601 UTC mit `Z`;
   `_normalize_level` mit Rückfall auf `INFO` und Ablage des Originalwerts in
   `details["source_severity"]`.
5. Protokolle in `storage/base.py`, `sinks/base.py`, `query/base.py` — nur
   Signaturen, keine Implementierung.

---

## Tests

### Positiv

- Modellinvarianten; `details` nach dem Bau unveränderlich.
- Prioritätsableitung: alle vier HIGH-Bedingungen und ihr Zusammenspiel mit
  `replayed`.
- Python-`LogRecord` (INFO, Logger `controller`) → `channel=system`,
  `component=controller`, `type=None`, gerenderte `message`.
- `LogRecord` mit den vier bestehenden `extra`-Feldern (`session_id`,
  `segment_id`, `event_type`, `detail`) → alle vier landen korrekt.
- `LogRecord` von `lefx.device.respeaker.transport` → `producer_kind=led`,
  `producer_id=respeaker-led-controller`, **`channel=system`**.
- Realer `log.event`-Frame aus `tests/test_event_protocol.py::event_message` →
  `event_id`, `server_cursor`, `channel`, `session_id`, `segment_id`,
  `replayed` korrekt.
- Serverevent mit `meldung` im Restpayload → `message` gefüllt.
- Serverevent mit `data.activationId` → `activation_id` gefüllt.
- `log.gap`-Controlframe → ein Record `client.eventstream.gap` mit
  `lostFromCursor`/`lostToCursor`.

### Negativ

- `producer_kind`/`channel`/`level` außerhalb der Menge.
- `details` ist kein Mapping; `segment_id` negativ oder `bool`.
- Envelope mit `severity="critical"` **und** mit `severity="verbose"` →
  `CRITICAL` bzw. `INFO`, Original in `details["source_severity"]`.
- Envelope ohne `data`; `result.event is None` bei `kind == EVENT` → liefert
  `None`, wirft nicht.
- `LogRecord` mit `%s`-Platzhaltern ohne Argumente.
- `LogRecord` mit `exc_info`, dessen Exception beim Formatieren wirft.
- `context` mit `session_id=None`.

### Failure / Edge

- Zyklisches `details` → endet, Ergebnis abgeschnitten und markiert.
- `details` mit 10.000 Schlüsseln → Knotengrenze greift.
- Wert, dessen `__str__`/`__repr__` wirft → wird ersetzt, keine Ausnahme.
- Nicht JSON-serialisierbares Objekt → `default=str` **je Blattwert**.

### Redaction – die sicherheitsrelevanten Fälle

- Realer `hello`-Payload mit `logAccess.accessToken` → Token auf **keiner**
  Ebene mehr im Ergebnis.
- `accessToken` / `access_token` / `ACCESS-TOKEN` / `authorization` /
  `adminKey` / `password` / `secret` / `cookie`, verschachtelt in Listen **und**
  Dicts → alle ersetzt.
- `store_transcription_content=False` mit `text`, `displayText`, `rawText`,
  `stableText`, `unstableText`, `committedStableText`, `visualUnstableText` →
  alle ersetzt, **Zeichenzahl erhalten**.
- `store_transcription_content=True` → Text unverändert.
- **N-02:** Regel `R-10` wirkt auch auf einen **unstrukturierten** Logtext.
  Prüfen gegen die realen Zeilen `"Final [seg=%s]: %s"` und
  `"… existing=%r, new=%r"`.
- URL mit Query → Query und Fragment entfernt, Host und Pfad erhalten.
- Pfad `C:\Users\<name>\AppData\Local\…` → `~\AppData\Local\…`, auch in einem
  Traceback.
- `store_raw_payload=False` → `raw is None`.

### N-01 – der wichtigste Einzeltest dieses Pakets

```text
Ein echter EventProtocolResult.payload (MappingProxyType mit verschachtelten
Tupeln UND einem frozenset) wird durch unfreeze() und json.dumps geschickt.

ERWARTUNG
  * Das Ergebnis ist ein JSON-OBJEKT, kein String.
  * Es enthaelt NICHT die Zeichenfolgen "mappingproxy(" oder "frozenset(".
  * Die schluesselbasierte Redaction greift danach nachweislich.

Ohne diesen Test waere D-1 unbemerkt geblieben -- ein stiller Fehler mit
Sicherheitsfolge.
```

### Contract-Tests

- `core/observability/**` importiert **kein** `PySide6`, **kein** `QtCore`.
- `models.py` importiert **nichts** aus dem eigenen Paket.
- `normalizer.py` importiert **kein** `sqlite3`.
- `normalizer.py` hält **keine** Referenz auf Controller, Session oder
  Coordinator und liest **keinen** Laufzeitzustand — `session_id`,
  `generation` und `segment_id` kommen für Python-Logs ausschließlich aus
  `record.__dict__` (`CONTRACTS §3.1`).
- Jedes Modul ist einzeln importierbar (kein Zyklus).

### Mutationschecks – hier vorgezogen, nicht erst in OBS-060

Die Redaction ist die einzige sicherheitsrelevante Regel dieses Pakets. Ein
grüner Redaction-Test, der auch ohne Redaction grün bliebe, wäre wertlos.
Deshalb werden zwei Mutationen bereits hier geprüft:

| Mutation | muss rot werden |
|---|---|
| Redaction-Aufruf am Ende des Normalizer-Pfades entfernen | U-Redaction-Tests |
| `unfreeze()` vor der Serialisierung entfernen | N-01 |

Die übrigen sechs Mutationschecks bleiben in OBS-060.

### Randfälle, die in OBS-000 nachgetragen wurden

- `scope` für einen `lefx.*`-Record ohne Session → `instance`
  (`CONTRACTS §1.3`).
- `component` eines Controlframes → fest `"eventstream"`, **nicht** das
  `type`-Präfix (`CONTRACTS §3.2`).
- `session_id`/`generation` einer Python-Logzeile ohne `extra` → `None`, ohne
  jeden Zugriff auf Laufzeitzustand (`CONTRACTS §3.1`).

---

## Pflichtprüfungen

- [ ] Positive Tests
- [ ] Negative Tests
- [ ] Failure-/Edge-Tests
- [ ] Contract-Tests (Qt-Grenze, Zyklenfreiheit)
- [ ] **Die vollständige bestehende Client-Suite bleibt grün, ohne dass ein
      bestehender Test geändert wird.** Da dieses Paket nur neue Dateien
      anlegt, ist jede Abweichung ein Alarmsignal.
- [ ] `git diff --check`
- [ ] kein unbeabsichtigter Cross-Workstream-Diff

## Akzeptanzkriterien

- Ein Mapping mit `accessToken`/`authorization`/`adminKey`/`password` auf
  **jeder** Verschachtelungsebene enthält den Originalwert nachweislich nicht
  mehr.
- Bei `store_transcription_content=False` enthält kein Ergebnisfeld den Text,
  aber die Zeichenzahl bleibt.
- Ein Pfad `C:\Users\<name>\AppData\…` erscheint als `~\AppData\…`.
- Der Normalizer **wirft nie**; er liefert im Zweifel `None`.
- Die Coremodelle funktionieren ohne Qt, SQLite und WebSocket.

## Evidence

Ablage: `40_EVIDENCE/OBS-010/`.

- Testlauf mit Kommando, Exitcode und Ergebnis.
- Ein Diagnoseskript **außerhalb des Produktrepos**, das die reale
  `hello`-Struktur aus der Serverdokumentation durch `redact` schickt und zeigt,
  dass `accessToken` verschwindet.
- Ein Vergleich Feld für Feld gegen `CONTRACTS §1.1` als Kommentar im Test.
- `git diff --stat`.

## Gate

`PASS` nur nach separatem Review. **Ein Coding-Agent darf das Gate nicht allein
aufgrund eigener grüner Tests vergeben.** Grüne Tests gegen Testdoubles beweisen
das Verhalten der Doubles, nicht das der Anwendung.
