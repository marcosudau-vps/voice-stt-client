# LOGGING_TEST_MATRIX

Deckt Auftragsabschnitt **20**.

**Leitsatz dieses Dokuments.** Ein vollständig grüner Testlauf ist **kein**
Fertigstellungsnachweis. Wenn ein Testdouble vom Produktionsobjekt abweicht,
beweist der Test nur das Verhalten des Doubles. Diese Matrix ist deshalb so
gebaut, dass die **wichtigsten** Nachweise gegen die **echten** Klassen laufen
und dass am Ende eine manuelle Abnahme am realen Produktionspfad steht.

**Rahmen.** Die Client-Suite läuft mit `unittest` **und** mit `pytest`
(`requirements-dev.txt`). Neue Tests heißen `tests/test_observability_*.py` bzw.
`tests/test_log_view.py`. Skripte, die keine Unittests sind, müssen
`manual_test_*` heißen, sonst sammelt pytest sie ein.

---

# Wo ein Double erlaubt ist und wo nicht

| Objekt | Double erlaubt? | Begründung |
|---|---|---|
| `ObservabilityIngress` | **ja**, ein aufzeichnender Fake ist der Standardweg | Er ist die Grenze; sein Verhalten wird in OBS-03 eigenständig bewiesen |
| `LogStore` | ja in Worker-Tests, **nein** in Store-Tests | – |
| Datei-Sink | ja | – |
| `EventProtocolProcessor` | **NEIN** im Isolationsnachweis | Ein Double würde die Cursor-Bestätigungssemantik selbst definieren — genau das, was bewiesen werden soll |
| `EventCursorStore` | **NEIN** im Isolationsnachweis; echte Instanz auf einer temporären Datei | dito |
| `DualSessionCoordinator` | **NEIN** im Isolationsnachweis | dito |
| `STTSession` (WebSocket) | ja, über das bestehende `ScriptedLogSocket`-Muster (`tests/test_event_stream.py:37`) | Netz ist nicht Gegenstand |
| Qt-Widgets | ja, `offscreen`-Plattform wie in `tests/test_ui_widgets.py` | – |

---

# U — Unit

## U-1 Canonical Normalization

| # | Fall | Erwartung |
|---|---|---|
| U-1.1 | `logging.LogRecord` (INFO, Logger `controller`) | `channel=system`, `component=controller`, `level=INFO`, `type=None`, `message` gerendert |
| U-1.2 | `LogRecord` mit `exc_info` | `details["exception"]` ist Text; `record.args` erscheint **nirgends** |
| U-1.3 | `LogRecord` mit den vier bestehenden `extra`-Feldern (`session_id`, `segment_id`, `event_type`, `detail`) | alle vier landen in `details` bzw. in den passenden Spalten |
| U-1.4 | `LogRecord` von `lefx.device.respeaker.transport` | `producer_kind=led`, `producer_id=respeaker-led-controller` |
| U-1.5 | Realer `log.event`-Frame aus `tests/test_event_protocol.py::event_message` | `event_id`, `server_cursor`, `channel`, `session_id`, `segment_id`, `replayed` korrekt |
| U-1.6 | Serverevent mit `meldung` im Rest-Payload | `message` gefüllt (Befund C-2) |
| U-1.7 | Serverevent mit `severity="critical"` und mit `severity="verbose"` | `level=CRITICAL` bzw. `INFO`, Original in `details["source_severity"]` |
| U-1.8 | `log.gap`-Controlframe | ein Record `client.eventstream.gap` mit `lostFromCursor`/`lostToCursor` |
| U-1.9 | Serverevent mit `data.activationId` | `activation_id` gefüllt |
| U-1.10 | Normalizer mit `result.event = None` bei `kind=EVENT` | liefert `None`, wirft nicht |

## U-2 Redaction

| # | Fall | Erwartung |
|---|---|---|
| U-2.1 | Realer `hello`-Payload mit `logAccess.accessToken` | Token nirgends im Ergebnis, auf keiner Ebene |
| U-2.2 | `accessToken` / `access_token` / `ACCESS-TOKEN` / `authorization` / `adminKey` / `password` / `secret` / `cookie` verschachtelt in Listen und Dicts | alle ersetzt |
| U-2.3 | `store_transcription_content=False` mit `text`, `displayText`, `rawText`, `stableText`, `unstableText`, `committedStableText`, `visualUnstableText` | alle ersetzt, Zeichenzahl erhalten |
| U-2.4 | `store_transcription_content=True` | Text unverändert |
| U-2.5 | URL mit Query (`wss://…/ws/transcribe?wakeWords=…&wakeWordSensitivity=…`) | Query entfernt, Host und Pfad erhalten |
| U-2.6 | Pfad `C:\Users\marco\AppData\Local\…` | `~\AppData\Local\…` |
| U-2.7 | Zyklisches `details` | endet, Ergebnis abgeschnitten, keine Rekursionsgrenze der Laufzeit |
| U-2.8 | Wert, dessen `__str__`/`__repr__` wirft | wird ersetzt, kein Durchreichen der Ausnahme |
| U-2.9 | `store_raw_payload=False` | `raw` ist `None` |
| U-2.10 | Ein Objekt, das nicht JSON-serialisierbar ist | `default=str`-Rückfall, kein Fehler |

## U-3 Dedupe

| # | Fall | Erwartung |
|---|---|---|
| U-3.1 | Zweimal derselbe `event_id` | genau eine Zeile |
| U-3.2 | Zweimal derselbe `event_id` **im selben Batch** | genau eine Zeile |
| U-3.3 | Zwei Records mit `event_id=None` und gleichem Inhalt | zwei Zeilen (Clientrecords sind nie Duplikate) |
| U-3.4 | Gleicher `event_id`, unterschiedliche `producer_id` | zwei Zeilen |
| U-3.5 | Erst live (`replayed=0`), dann als Replay (`replayed=1`) | eine Zeile, `replayed=0` bleibt |
| U-3.6 | Vollständiger Replay von 5000 bereits gespeicherten Events | 0 neue Zeilen, keine Ausnahme, Laufzeit gemessen |

## U-4 Store

| # | Fall | Erwartung |
|---|---|---|
| U-4.1 | Neue Datei | Schema angelegt, `user_version=1`, `journal_mode=wal` |
| U-4.2 | Batch von 200 | 200 Zeilen, eine Transaktion |
| U-4.3 | Retention nach Alter | nur ältere Zeilen gelöscht |
| U-4.4 | Retention nach Anzahl | genau `max_entries` bleiben, die neuesten |
| U-4.5 | Retention nach Größe | `max_entries` wird für den Lauf gesenkt, `incremental_vacuum` läuft |
| U-4.6 | `user_version` = 99 | Nur-Lesen, `DEGRADED_STORE`, **nichts gelöscht** |
| U-4.7 | Datei ist ein Verzeichnis | `FAILED_STORE`, keine Ausnahme nach außen |
| U-4.8 | Datei ist keine SQLite-Datei | dito, Datei bleibt unverändert |
| U-4.9 | Nebenläufiger Leser mit offener Abfrage | `write_batch` bleibt erfolgreich |

## U-5 Query

| # | Fall | Erwartung |
|---|---|---|
| U-5.1 | Jeder Filter aus `QueryFilter` einzeln | korrekte Teilmenge |
| U-5.2 | Kombination Channel + Level + Zeitbereich | korrekte Teilmenge |
| U-5.3 | Keyset über drei Seiten | keine Doppel, keine Lücke |
| U-5.4 | Keyset bei parallelem Schreiben | dito |
| U-5.5 | Filterwert mit `'`, `%`, `_`, `\` | als Literal behandelt, kein Syntaxfehler |
| U-5.6 | `limit` über `max_limit` | auf `max_limit` gekappt |
| U-5.7 | Unbekannte `provider_id` | `QueryPage` mit `state=ERROR`, leer |
| U-5.8 | `fetch_raw` für einen Record ohne `raw` | `None` |
| U-5.9 | Listenabfrage | `raw_json` wird **nicht** geladen (Nachweis über die tatsächlich abgesetzte SQL) |

## U-6 Backpressure

| # | Fall | Erwartung |
|---|---|---|
| U-6.1 | `low` voll | `submit` liefert `False`, `dropped_low` steigt |
| U-6.2 | `high` voll, `low` hat Platzinhalt | ein LOW-Record wird verworfen, der HIGH-Record kommt hinein |
| U-6.3 | Beide voll | `submit` liefert `False`, wirft nicht |
| U-6.4 | 100.000 `submit` bei voller Queue | unter der festgelegten Zeitgrenze, keine Ausnahme |
| U-6.5 | Acht Threads × 5000 Submits | `written + dropped_low + dropped_high` geht exakt auf |
| U-6.6 | Erholung nach Überlast | genau ein `logging.records_dropped`, Zähler zurückgesetzt |
| U-6.7 | `enabled=False` | `submit` liefert sofort `False`, nichts wird gebaut |
| U-6.8 | `NullIngress` | verhaltensgleich, keine Ausnahme |

## U-7 Health

| # | Fall | Erwartung |
|---|---|---|
| U-7.1 | Zustandsübergänge OK → DEGRADED_STORE → FAILED_STORE → OK | Snapshot korrekt, `since` gesetzt |
| U-7.2 | 2000 Fehler in einer Sekunde | ≤ 1 stderr-Zeile, Wiederholungszähler stimmt |
| U-7.3 | `sys.stderr = None` | keine Ausnahme, Zähler laufen weiter |
| U-7.4 | `observability.internal`-Logger | `propagate is False` |
| U-7.5 | Import-Prüfung | `health.py` importiert weder `core.event_models` noch `core.feedback_reducer` |

---

# I — Integration

| # | Fall | Beteiligte echte Objekte | Erwartung |
|---|---|---|---|
| I-1 | `logging.getLogger("controller").info(...)` → SQLite | `UnifiedLogHandler`, echter Ingress, echter Worker, echter Store auf tmpdir | genau eine Zeile mit korrektem `component`/`channel` |
| I-2 | Serverevent → SQLite | echter `EventProtocolProcessor`, echter `DualSessionCoordinator`, echter Adapter, echter Store | eine Zeile mit `event_id`, `server_cursor`, `raw` |
| I-3 | Strukturiertes Clientevent → SQLite | echter Ingress/Worker/Store | eine Zeile mit `type` und Korrelationsfeldern |
| I-4 | Replay: 200 Events, davon 120 bereits gespeichert | echter Processor auf einem Skript-Socket | 80 neue Zeilen, keine Ausnahme |
| I-5 | Reconnect mit Cursorstore auf temporärer Datei, danach Serverwechsel (`server_instance_id` ändert sich) | echter `EventCursorStore` | Cursor wird verworfen, voller Replay, **keine** doppelten Zeilen |
| I-6 | Shutdown/Flush | echter Manager | Queue geleert oder `dropped_shutdown` gesetzt; kein Thread bleibt zurück |
| I-7 | Korrelation Ende zu Ende | echter `STTController` mit Skript-Session | `client.trigger.sent` und `client.trigger.ack_received` tragen dieselbe `command_id` |
| I-8 | Settings-Apply | echter `AppConfig`, echter Controller | `retention_days` wirkt zur Laufzeit; **kein** Reconnect, **kein** Audio-Neustart |
| I-9 | Query nach Ingest | echter Store + echter `LocalLogProvider` | die geschriebenen Records sind über jeden Filter auffindbar |
| I-10 | Doppelter `setup_logging`-Aufruf | – | genau ein `UnifiedLogHandler` am Root (`handlers.clear()` verhindert Dopplung, `logging_setup.py:77`) |

---

# F — Failure

| # | Fall | Provokation | Erwartung |
|---|---|---|---|
| F-1 | Logging deaktiviert | `enabled=False` | Client fachlich identisch; **derselbe Testkörper** wie F-0 (Referenzlauf) |
| F-2 | SQLite nicht beschreibbar | Datei read-only / Verzeichnis entzogen | Audio, WebSocket, Trigger, Activation, Feedback funktionieren; Health `FAILED_STORE` |
| F-3 | File-Sink kaputt | Sink wirft bei jedem Schreiben | keine fachliche Auswirkung; Store schreibt weiter |
| F-4 | Queue voll | Worker angehalten, 20.000 Records | Producer blockiert nicht (harte Zeitgrenze je `submit`); Dropstrategie greift; App bedienbar |
| F-5 | Worker-Exception | Schleifenkörper wirft `RuntimeError` bzw. `MemoryError` | App bedienbar; Health gesetzt; Schleife läuft weiter bzw. wechselt sauber nach `FAILED_WORKER` |
| F-6 | Fehlerhafter Record | Normalizer wirft; `details` nicht serialisierbar | Record verworfen bzw. mit `default=str` gerettet; ein `logging.record_rejected`; Producerpfad unbeeinflusst |
| F-7 | Serverevent-Replay | siehe I-4/I-5 | keine unkontrollierte doppelte Persistenz |
| F-8 | Beobachter wirft im Fan-out | `on_observation` wirft `MemoryError` | `_handle_event` liefert weiterhin `True`; `confirm_event` läuft; **Cursor wird committed** — Nachweis über die echte Cursordatei |
| F-9 | Beobachter blockiert | `on_observation` schläft 2 s | dokumentiert die Grenze und begründet, warum der Ingress nie blockiert |
| F-10 | Store gelöscht im Betrieb | Datei entfernt, während der Worker läuft | Health `FAILED_STORE`, keine Ausnahme nach außen, Anwendung läuft |
| F-11 | Rekursion | Store loggt seinen eigenen Fehler über `logging` | Anzahl erzeugter Records bleibt unter einer festen Obergrenze |
| F-12 | Migration schlägt fehl | Migrationsschritt wirft | Rollback, `FAILED_STORE`, **Datei unverändert**, Anwendung läuft |

---

# R — Runtime isolation (der wichtigste Test)

```text
Logging kaputt
  -> Audio / WebSocket / Controller / Feedback funktionieren weiter
```

| # | Aufbau | Nachweis |
|---|---|---|
| R-1 | Referenzlauf **ohne** Observability: ein vollständiger Diktatzyklus über den echten `STTController` mit Skript-Session (Muster `tests/test_trigger_lifecycle.py`, `tests/test_feedback_integration.py`). Alle beobachtbaren Wirkungen werden aufgezeichnet: gesendete Frames, `CommandResult`, `FeedbackDecision`-Folge, Snapshotfolge, `FinalProcessingResult`. | Referenzprotokoll |
| R-2 | Derselbe Lauf **mit** funktionierender Observability | Protokoll **identisch** zu R-1 |
| R-3 | Derselbe Lauf mit einem Ingress, der bei **jedem** `submit` wirft | Protokoll identisch zu R-1 |
| R-4 | Derselbe Lauf mit einem Store, der bei **jedem** `write_batch` wirft | identisch |
| R-5 | Derselbe Lauf mit voller Queue von Beginn an | identisch |
| R-6 | Derselbe Lauf mit einem Worker, der nie startet | identisch |
| R-7 | Derselbe Lauf mit einem `on_observation`, das bei jedem Aufruf wirft | identisch, **und** die Cursordatei enthält denselben Endstand wie in R-1 |

**Warum in dieser Form.** Der Vergleich zweier Protokolle ist stärker als eine
Reihe von Einzelbehauptungen: er erfasst auch Wirkungen, an die beim
Testschreiben niemand gedacht hat. Er ist außerdem der einzige Test, der eine
Regression bemerkt, wenn später ein Beobachtungsaufruf versehentlich an eine
Stelle rutscht, an der er den Ablauf verändert.

**Bedingung.** R-1 bis R-7 verwenden den **echten** `STTController`, die
**echte** `FeedbackEngine`, den **echten** `DualSessionCoordinator` und den
**echten** `EventProtocolProcessor`. Nur der WebSocket und die Ausgabegeräte
(LED, Ton, Injektion) sind Doubles.

---

# P — Performance

| # | Messung | Aufbau | Grenzwert |
|---|---|---|---|
| P-1 | Audio-Callback-Latenz ohne Logging | 10.000 Aufrufe von `AudioCapture._audio_callback` mit realistischem Puffer | Referenzwert |
| P-2 | dieselbe Messung mit Logging | Observability aktiv | Abweichung im Rahmen der Messstreuung; die HOT-PATH-Funktionen enthalten **keinen** `submit` (Quelltextprüfung ergänzt die Messung) |
| P-3 | `submit` bei voller Queue | 100.000 Aufrufe | harte obere Zeitgrenze, im Testprotokoll festgehalten |
| P-4 | `write_batch` | 10.000 Records in Batches à 200 | obere Zeitgrenze, Dateigröße protokolliert |
| P-5 | Burst | 50.000 Records in 5 s | Anwendung bleibt bedienbar; `dropped_*` protokolliert; keine unbegrenzte Speicherzunahme |
| P-6 | Queue-Overload mit angehaltenem Worker | 200.000 Submits | Speicher bleibt unter der aus den Queue-Größen berechneten Obergrenze |
| P-7 | Batchgröße | 50 / 200 / 1000 im Vergleich | Messwerte protokolliert; 200 wird bestätigt oder korrigiert |
| P-8 | UI-Reaktionszeit | LogWindow im Live-Modus bei 500 Records/s | Abstand zweier `QTimer`-Durchläufe bleibt unter einer festen Grenze |
| P-9 | Abfragezeit | 200.000 Zeilen, jede Filterkombination der UI | jede Abfrage unter einer festen Grenze; belegt die Indexauswahl aus Schema §9.2 |

**Wichtig.** Alle Grenzwerte sind **Regressionswächter auf der Maschine des
Entwicklers**, keine Leistungszusagen. Die absoluten Zahlen werden beim ersten
Lauf ermittelt und im Testprotokoll festgeschrieben; spätere Läufe vergleichen
gegen diese Zahlen.

---

# M — Manuelle Abnahme (Pflicht, nicht optional)

Ein grüner Lauf von U, I, F, R und P begründet **nicht**, dass V1 fertig ist.
Erst die folgenden Schritte am realen Produktionspfad tun das. Sie werden mit
Datum, Serveradresse und Clientversion protokolliert.

| # | Schritt | Nachweis |
|---|---|---|
| M-1 | Anwendung starten, ein Diktat per Hotkey, Text wird eingefügt | Bildschirmfoto oder Protokoll |
| M-2 | `observability.sqlite3` öffnen | `client.trigger.sent` und `client.trigger.ack_received` mit gleicher `command_id`; `transcription.completed` des Servers vorhanden |
| M-3 | Reihenfolge prüfen | `ORDER BY id` ergibt eine plausible, lückenlose Abfolge des Diktats |
| M-4 | DB-Datei schreibgeschützt setzen, neu starten, Diktat wiederholen | Text wird eingefügt; LED und Ton reagieren; Health `FAILED_STORE` |
| M-5 | Serverprozess neu starten, während der Client läuft | `SELECT event_id, COUNT(*) FROM logs WHERE event_id IS NOT NULL GROUP BY event_id HAVING COUNT(*)>1` liefert **keine** Zeile |
| M-6 | Log-Ansicht öffnen, nach Session filtern, Detail und Raw JSON prüfen | Bildschirmfoto |
| M-7 | Nach `accessToken` suchen | `SELECT COUNT(*) FROM logs WHERE raw_json LIKE '%accessToken%'` — Erwartung, dass nur redigierte Vorkommen erscheinen; zusätzlich Volltextsuche in der JSONL-Datei |
| M-8 | Transkriptsuche bei `store_transcription_content=false` | ein bekannter gesprochener Satz ist in `logs` **nicht** auffindbar |
| M-9 | Retention | `retention_days=0.001` setzen, Retention auslösen, Zeilenzahl prüfen |
| M-10 | Anwendung beenden | keine Restthreads; DB konsistent; `client.log` unverändert im Format |

**Ohne ein vollständiges M-Protokoll gilt der Status von V1 als „offen" oder
„teilweise", nicht als „erledigt".**
