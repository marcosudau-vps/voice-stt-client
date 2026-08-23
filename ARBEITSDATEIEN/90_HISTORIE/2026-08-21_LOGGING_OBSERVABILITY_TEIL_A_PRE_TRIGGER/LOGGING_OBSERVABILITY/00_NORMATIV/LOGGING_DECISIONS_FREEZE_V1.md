---
id: OBS-FREEZE-DECISIONS
status: FROZEN
authority: normative
workstream: OBS
freeze_gate: OBS-000
run: RUN-OBS-000-01_2026-08-15_CLAUDE
last_updated: 2026-08-15
---

# Logging-/Observability-Entscheidungen – FREEZE

> **Zweck.** Dieses Dokument schließt jede Architekturentscheidung, die ein
> Coding-Agent sonst selbst treffen müsste. Es ist zugleich das Register aller
> Widersprüche zwischen den Quellen und ihrer Auflösung.
>
> **Lesart der Statusspalte.**
> `GESCHLOSSEN` – entschieden, ab sofort verbindlich.
> `GESCHLOSSEN (Teil B)` – für V1 folgenlos, wird im genannten Teil-B-Paket
> entschieden; V1 muss dafür nur die genannte Vorkehrung treffen.
>
> **Abschnitt 4 ist die Leseempfehlung für Marco.** Dort stehen die vier
> Entscheidungen, die eine ausdrücklich benannte Anforderung aus den Entwürfen
> ändern.

---

# 1. Blockierende Entscheidung

## FD-N1 / OD-01 — Paketname `observability`, nicht `logging`

```text
ENTSCHEIDUNG   core/observability/
               Konfigabschnitt logging.observability.*
               UI-Tab "Logging & Diagnose"
STATUS         GESCHLOSSEN
```

**Begründung.** `core/logging/` neben `import logging` ist bei absoluten
Importen zwar zulässig, aber das Repository importiert `logging` in rund 20
Modulen — jeder Leser müsste zweimal hinsehen. Der Begriff „Observability" deckt
zudem Serverevents und Metriken ab, die keine „Logs" sind.

**Der Nachteil ist adressiert.** Zwei Begriffe für den Nutzer werden über den
Konfigpfad (`logging.observability`) und den Tabnamen („Logging & Diagnose")
überbrückt. Der Nutzer sieht durchgehend „Logging", der Entwickler durchgehend
„observability".

**Verworfen:** `core/obs/` — spart nichts und ist weniger lesbar.

**Warum das die einzige blockierende Entscheidung war.** Sie betrifft jeden
Dateipfad und jeden Import. Alles andere war entweder ein Defaultwert, eine
nachrüstbare Spalte oder eine Teil-B-Frage.

---

# 2. Entscheidungen zum Datenmodell

## FD-C1 / OD-02 — `transcription_id` als eigene Spalte

```text
ENTSCHEIDUNG   eigene Spalte, nullable, ohne Index
STATUS         GESCHLOSSEN.  NICHT blockierend.
```

`transcriptionId` ist ein Feld erster Ordnung im Server-Envelope und in der
Server-DB indiziert. Es ist der einzige Schlüssel, der alle Ereignisse eines
Final-Transkripts über HTTP und WebSocket hinweg verbindet, und der spätere
Serverprovider kennt ihn als eigenen Query-Parameter. Kosten: eine Spalte.

**Verworfen:** den Wert in `correlation_id` als `"transcription:<id>"`
unterzubringen. Das mischte zwei Namensräume völlig verschiedener Herkunft —
clientseitig erzeugte Feedbackkorrelationen und serverseitige
Transkriptions-IDs — und machte einen Gleichheitsfilter davon abhängig, dass die
Präfixe stimmen.

**Herabstufung gegenüber `LOGGING_OPEN_DECISIONS.md`:** Dort war OD-02 als
blockierend eingestuft. Das war zu streng: Genau dafür existiert der
Migrationsmechanismus, eine nullable Spalte ist ein einzeiliges `ALTER TABLE`,
und in V1 braucht **kein** Filter das Feld — lokal deckt `session_id` +
`segment_id` denselben Zugriff ab.

## FD-C2 / OD-08 — `activation_id` wird befüllt, aber als diagnostisch markiert

```text
ENTSCHEIDUNG   befuellen; ausschliesslich aus envelope.data.activationId;
               NIE gruppieren; UI-Filter mit Hinweis
STATUS         GESCHLOSSEN
```

Die serverseitige Zuordnung ist nachweislich unzuverlässig: Der Wert wird zum
Publikationszeitpunkt frisch aus dem Controller gelesen; ist die Activation
geschlossen, fehlt er, ist inzwischen eine neue geöffnet, ist er **falsch**.

Trotzdem befüllen, weil der Wert für die Mehrzahl der Ereignisse stimmt — und
weil gerade die **falschen** Zuordnungen für die kommende Migration wertvoll
sind: Genau dieser Defekt soll dort behoben werden.

**Verworfen:** Spalte leer lassen (tote Spalte) oder gar keine Spalte (erzwänge
nach der Serverkorrektur eine Migration).

## FD-C3 — `monotonic_ns`, `host`, `process_id`, `sequence` entfallen als Spalten

```text
STATUS         GESCHLOSSEN
```

- `monotonic_ns`: innerhalb eines Prozesses leistet `logs.id` dasselbe;
  prozessübergreifend ist der Wert bedeutungslos (kein gemeinsamer Nullpunkt).
  Im **Speicher** wird er zur Ordnung vor dem Schreiben verwendet.
- `host`: auf einem Einzelplatzrechner ohne Aggregation ohne Abfragewert, aber
  personenbezogen (Windows-Rechnernamen sind regelmäßig `VORNAME-PC`).
  Wiedereinführbar als nullable Spalte, sobald Multi-Host-Aggregation kommt.
- `process_id`: ein Desktop-Client hat einen Prozess je `instance_id`; gehört in
  `details` der `client.app.started`-Zeile.
- `sequence`: `logs.id AUTOINCREMENT` **ist** die lokale Sequenz.

## FD-C4 — `record_id` **und** `event_id`, beide

```text
STATUS         GESCHLOSSEN
```

Unterschiedliche Lebensdauer, Autorität und Eindeutigkeit. Zusammenlegen ließe
entweder Clientrecords ohne Identität oder zerstörte das Dedupe.

## FD-C5 — `server_cursor` als eigene Spalte

```text
STATUS         GESCHLOSSEN
```

Die einzige streng monotone, retentionsfeste Ordnung der Serverereignisse und
der einzige Weg, eine Lücke von einer Filterlücke zu unterscheiden. Ohne sie
lässt sich die Serverhistorie lokal nicht rekonstruieren.

**Auflage:** nie ohne `instance_id` sortieren oder vergleichen.

## FD-C6 — Channels klein, keine zusätzlichen Client-Channels

```text
ENTSCHEIDUNG   system | audit | transcription | performance, klein
STATUS         GESCHLOSSEN
```

Der Code kennt ausschließlich Kleinschreibung; der Zielbildentwurf schreibt groß.
Zwei Wertemengen für ein Feld wären ein Dauerfehler.

Keine zusätzlichen Client-Channels: Der Channel ist orthogonal zu
`producer_kind`. Ein Channel `client_ui` mischte Herkunft in die Kategorie,
obwohl `producer_kind=client` plus `component` dieselbe Auswahl erlaubt. `led`
ist ein `producer_kind`, kein Channel.

## FD-C7 — Dedupe-Schlüssel `(producer_id, event_id)`, partieller UNIQUE-Index

```text
STATUS         GESCHLOSSEN
```

Dedupe ist **Pflicht, nicht Kür**: `server_instance_id` wird bei jedem
Serverneustart neu erzeugt, der Client verwirft daraufhin seinen Cursor
(verifiziert in `EV-02 / C-04`), und der Server replayt die gesamte verbliebene
Historie. Die vorhandene In-Memory-Dedupe von 2048 Einträgen fängt das nicht ab
und überlebt einen Clientneustart ohnehin nicht.

`producer_id` im Index schützt gegen einen künftigen zweiten Produzenten mit
eigenem ID-Schema, ohne heute etwas zu kosten.

## FD-C8 — Enum-Versionierung: TEXT, offen, nur `level` geschlossen

```text
STATUS         GESCHLOSSEN
```

Ein numerischer Code erzwänge eine Migration bei jedem neuen Wert. `severity`
ist serverseitig kein geschlossenes Enum, `event` ist offen, und `SessionState`
des Clients hat bereits einen bewussten Vorwärtskompatibilitätspfad. Nur `level`
wird hart abgebildet, weil Filter und Priorisierung darauf beruhen; der
Originalwert bleibt in `details.source_severity`.

**Ein neuer `channel` oder `type` löst KEINE Migration aus.**

## FD-C9 — Ablageort und Schema-Versionierung

```text
ENTSCHEIDUNG   %LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3
               PRAGMA user_version + Tabelle schema_meta
               KEINE migrations-Tabelle (waere eine zweite Wahrheit)
               KEINE schema_version-Spalte je Zeile (100 % redundant)
               JSONL: schemaVersion je Zeile (kontextlos gelesen)
STATUS         GESCHLOSSEN
```

## FD-C10 / OD-11 — Das doppelte Datenverzeichnis bleibt unangetastet

```text
ENTSCHEIDUNG   neue Datei in "RealtimeSTT Client"; die bestehende Abweichung
               ("RealtimeSTT_Client" fuer die Transkripthistorie) wird
               dokumentiert, nicht repariert
STATUS         GESCHLOSSEN
```

Eine Vereinheitlichung wäre eine Produktänderung mit Datenmigrationsrisiko an
einer Stelle, die das Logging-Vorhaben nicht berührt.

## FD-C11 — `unfreeze()` ist Pflicht; `default=str` nur je Blattwert

```text
STATUS         GESCHLOSSEN.  Sicherheitsrelevant.
```

`EventProtocolResult.payload` ist rekursiv eingefroren in `MappingProxyType`,
`tuple` **und `frozenset`** (verifiziert in `EV-02 / C-05`). Ein
`default=str`-Rückfall auf Containerebene kollabierte den Payload zu einem
String — und dann greift die schlüsselbasierte Redaction nicht mehr, weil es
keine Schlüssel mehr gibt.

**Gegenüber der Vorarbeit erweitert:** Das adversariale Review nennt nur
`MappingProxyType` und Tupel. `frozenset` ist der schwerere Fall.

## FD-C12 / OD-18 — Obergrenze 64 KiB für gespeicherte `raw`-Payloads

```text
ENTSCHEIDUNG   > 64 KiB -> {"_truncated": true, "_bytes": n}
STATUS         GESCHLOSSEN
```

`max_message_size` ist 1 MiB. Ein 1-MiB-Event ist ein Serverdefekt, kein
Diagnosefall; ihn zu speichern verdoppelte kurzzeitig den Speicher und blähte
die Historie.

---

# 3. Entscheidungen zu Defaults und Betrieb

## FD-D1 / OD-03 — `store_transcription_content` Default `false`

```text
STATUS         GESCHLOSSEN
```

Die neue Historie ist deutlich langlebiger (14 Tage, 200.000 Einträge) als die
rotierende `client.log` (4 × 5 MiB). Was heute in Tagen verfällt, bliebe sonst
wochenlang.

**Ehrlich benannt:** Das **verringert** die heute gespeicherte Menge — der
Client loggt Transkripttext bereits auf INFO und bei Konflikten vollständig auf
WARNING. Das ist gut, könnte aber überraschen. Deshalb eine ausdrückliche
Beschreibung im Settings-Tab: „Transkripttexte in der Diagnosehistorie speichern
— betrifft auch technische Logzeilen."

**Preis:** Bei der Diagnose eines Deduplikationskonflikts fehlt genau die
Information, die den Konflikt zeigt. Die Zeichenzahl bleibt erhalten.

## FD-D2 / OD-04 — `store_raw_payload` Default `true`, außer Channel `performance`

```text
ENTSCHEIDUNG   eine einzige Regel: raw wird gespeichert, ausser
               channel == "performance"
STATUS         GESCHLOSSEN
```

Vollständig `true` wäre forensisch ideal, aber bei aktivem
`realtime_log_detail=events` erzeugt der Server einen Performance-Record je
Realtime-Ausgabe — dort entsteht das Volumen. Vollständig `false` verlöre die
Felder, die der Envelope in `extra` schiebt (darunter `meldung`) und wäre nicht
vorwärtskompatibel.

**Verworfen:** ein granulares Feld je Channel in der Konfiguration —
Überkonfiguration für ein Problem, das an genau einer Stelle entsteht.

## FD-D3 / OD-05 — Retention 14 Tage / 200.000 Einträge / 256 MiB

```text
ENTSCHEIDUNG   retention_days = 14
               max_entries    = 200000      beide wirken; die erste greifende
                                            Grenze gewinnt
               max_db_bytes   = 268435456   NUR Warnsignal (siehe FD-D8)
STATUS         GESCHLOSSEN
```

Zweck von V1 ist, die kommende Migration nachvollziehbar zu machen. Eine
Migration dauert Wochen; ein Fehler wird oft erst Tage später bemerkt. 7 Tage
sind zu knapp. 1 GiB auf einem Arbeitsplatzrechner ist unhöflich. Zum Vergleich:
die `client.log` belegt maximal 20 MiB, die Transkripthistorie ist auf 100
Einträge begrenzt.

## FD-D4 / OD-06 — Datei-Sinks in V1: nur JSONL

```text
ENTSCHEIDUNG   nur JSONL. Feld file_sink_format entfaellt in V1.
STATUS         GESCHLOSSEN
```

Der bestehende `RotatingFileHandler` schreibt zwar bereits JSON Lines, enthält
aber **nur** Python-Logs — nie Serverevents, nie strukturierte Clientevents. Er
ist also **kein** Ersatz. Ein Textformat verdoppelte Format-, Rotations- und
Fehlercode für einen Export, den man aus JSONL in einer Zeile erzeugt.

Ein Konfigfeld mit genau einer Option ist Überkonfiguration; es kehrt in OBS-150
zurück, wenn ein zweites Format existiert.

## FD-D5 / OD-07 — `hello` nur über eine Whitelist

```text
ENTSCHEIDUNG   Whitelist (Liste in LOGGING_CONTRACTS_FREEZE_V1.md, R-6).
               hello wird NIE raw. Die Redaction laeuft ZUSAETZLICH.
STATUS         GESCHLOSSEN
```

`hello` ist diagnostisch außerordentlich wertvoll — es enthält `sessionConfig`
mit `warnings`/`fallbacks`/`ignoredFields` und `activationConfig`, also genau
die Felder, an denen sich Fehlkonfigurationen zeigen. Es enthält aber auch
`logAccess.accessToken`, und dieser Payload wird heute bereits an jeden
Eventkonsumenten weitergereicht.

**Verworfen:** „vollständig, aber redigiert". Das verlässt sich darauf, dass die
Redaction jeden Weg abdeckt. Sie tut es vermutlich — aber „vermutlich" ist bei
einem Token der falsche Maßstab.

**Verworfen:** gar nicht speichern — verlöre die wertvollsten
Konfigurationsdiagnosedaten des Systems.

## FD-D6 / OD-12 — Logging-interner Fatalfehler: still

```text
ENTSCHEIDUNG   nur Health, ratenbegrenztes stderr und die Statuszeile im
               LogWindow. Keine Tray-Benachrichtigung. Kein Neustartversuch.
STATUS         GESCHLOSSEN
```

Eine Tray-Benachrichtigung machte ein Diagnoseproblem zu einer
Nutzerunterbrechung; `TrayController.notify` ist heute den Dingen vorbehalten,
die den Nutzer wirklich betreffen. Ein automatischer Neustart klingt hilfreich,
ist es aber selten: Ein Worker, der an einem defekten Store stirbt, stirbt nach
dem Neustart erneut — und ein Neustartzyklus wäre eine zusätzliche Fehlerquelle
im Shutdownpfad.

**Ausnahme:** Wer das LogWindow geöffnet hat, sieht sofort, dass die Daten
unvollständig sind.

## FD-D7 / OD-13 — `client.log` bleibt neben dem Store

```text
STATUS         GESCHLOSSEN
```

Der bestehende Weg ist heute die einzige Diagnosequelle und darf erst
eingeschränkt werden, wenn der neue über mehrere Wochen im echten Betrieb
bewiesen ist. Er ist zugleich die **Rückfallebene** bei totem Worker. Die
Doppelung kostet Plattenplatz, nicht Korrektheit.

„`client.log` nur noch für WARNING+" ist ein sinnvoller Schritt **nach** der
Triggerarchitektur-Migration, nicht davor.

## FD-D8 — `max_db_bytes` ist ein Warnsignal, kein Eingriff

```text
ENTSCHEIDUNG   messen, bei Ueberschreitung logging.retention_pressure und
               Health-Warnung. KEIN automatisches Absenken von max_entries,
               KEIN incremental_vacuum, KEIN VACUUM, KEIN auto_vacuum.
STATUS         GESCHLOSSEN
```

`retention_days` und `max_entries` verhindern den Fall bereits; eine dritte,
eingreifende Mechanik wäre ein zusätzlicher Fehlerpfad. Nebeneffekt: Die heikle
Bedingung „`auto_vacuum` muss vor der ersten Tabelle gesetzt werden" entfällt
ersatzlos.

## FD-D9 — Level-Default `INFO`; ein Wert speist Handler und Ingress

```text
ENTSCHEIDUNG   logging.observability.level speist BEIDE Filter.
               Handler-Level  -> Python-Logs
               Ingress-Level  -> strukturierte Client- und Serverevents
               Default INFO. DEBUG ist waehlbar.
STATUS         GESCHLOSSEN
```

Ohne diese Festlegung hätte ein Coding-Agent zwei plausible Deutungen.

`DEBUG` ist datenschutzseitig unbedenklich, weil Regel `R-10` auch für
unstrukturierte Logtexte gilt und den Realtime-Text redigiert — aber teuer,
weil der Handler dann für jeden DEBUG-Record läuft.

---

# 4. Entscheidungen, die eine benannte Entwurfsanforderung ändern

> **Diese vier Punkte weichen von einer ausdrücklich benannten Anforderung der
> Entwürfe ab.** Sie sind hier geschlossen, damit OBS-010 beginnen kann. Marco
> kann jede davon per `DECISION REQUIRED` zurückdrehen; die Auswirkung ist
> jeweils genannt.

## FD-S1 / OD-14 — Der Memory-Ringbuffer entfällt

```text
ANFORDERUNG    Zielbild §17 und V1-Abgrenzung §3.11/§3.12 verlangen einen
               Memory-Ringbuffer und die Einstellung live_buffer_size.
ENTSCHEIDUNG   Ringbuffer entfaellt. Live-Ansicht als tailende Abfrage
               WHERE id > :last ORDER BY id LIMIT 500, alle 250 ms.
               live_buffer_size entfaellt aus den Einstellungen.
STATUS         GESCHLOSSEN
RUECKDREHKOSTEN  ein Modul, ein Lock, eine Konfigoption, eine live_since-API,
                 plus die Klaerung der Eigentuemerfrage (Ingress oder Worker)
```

**Die geforderte Funktion — Live-Ansicht — bleibt vollständig erfüllt. Nur die
Bauform ändert sich.**

Zielbild §17 nennt als Zweck des Ringbuffers „geringe DB-Leselast". Eine
indizierte Tailabfrage auf dem Primärschlüssel alle 250 ms in WAL ist keine
Last. Der Ringbuffer brächte den Vorsprung eines halben Flushintervalls.

Drei Nebengewinne, die den Ausschlag geben:

1. Der Live-Pfad benutzt **dieselbe** Provider-Schnittstelle wie die Historie —
   eine Abstraktion **weniger**, nicht mehr.
2. Die UI wird vom Worker entkoppelt: OBS-050 hängt danach nur noch am
   Query-Layer und kann parallel zu OBS-040 gebaut werden.
3. Bei totem Worker bleibt die Live-Ansicht nutzbar und zeigt schlicht keine
   neuen Zeilen — was der Wahrheit entspricht. Der Ringbuffer hätte hier
   Daten gezeigt, die nie gespeichert wurden.

## FD-S2 / OD-15 — Eine Queue statt zweier

```text
ANFORDERUNG    Der Concurrency-Entwurf sieht zwei Queues (1024/8192) mit
               gegenseitiger Verdraengung vor.
ENTSCHEIDUNG   EINE bounded queue.Queue (8192) mit Wasserstandsregel bei 75 %.
STATUS         GESCHLOSSEN
RUECKDREHKOSTEN  gering, aber die Zweiqueue-Loesung braucht den Fremdgriff
                 low.get_nowait() AUS DEM PRODUCER-THREAD
```

Beide Lösungen erreichen dasselbe Ziel („DEBUG/PERFORMANCE zuerst verwerfen").
Die Zweiqueue-Lösung kostet zusätzlich: doppelte Buchführung, einen
Prioritätsvergleich und den Zugriff eines Producer-Threads auf eine fremde
Queue.

## FD-S3 / OD-16 — `ProviderCapabilities` entfällt in V1

```text
ANFORDERUNG    Der Boundaries-Entwurf §15 fuehrt ProviderCapabilities als
               Bestandteil von ProviderStatus.
ENTSCHEIDUNG   entfaellt in V1; wird in OBS-120 eingefuehrt.
STATUS         GESCHLOSSEN
RUECKDREHKOSTEN  keine -- ProviderStatus ist eine frozen dataclass mit
                 Defaults, das Feld ist additiv nachruestbar
```

In V1 existiert genau **ein** Provider, der jeden Filter beantwortet. **Kein
einziger V1-Codepfad läse das Objekt.** Es entsteht sinnvoll erst mit dem ersten
Provider, der nicht alles kann — und dessen Fähigkeiten kennt man erst dann
genau.

Was V1 stattdessen leistet, damit später nichts umgebaut werden muss: siehe
`LOGGING_ARCHITEKTUR_FREEZE_V1.md §10.3`.

## FD-S4 / OD-17 — „Diagnosehistorie löschen" kommt **zusätzlich** in V1

```text
ANFORDERUNG    Der V1-Scope verlangt sie NICHT.
ENTSCHEIDUNG   aufnehmen. Schaltflaeche im Logging-Tab; LogStore.clear();
               DELETE FROM logs + PRAGMA wal_checkpoint(TRUNCATE).
               Am STORE, nicht am Query-Provider (O-14).
STATUS         GESCHLOSSEN
UMFANG         etwa zehn Zeilen plus eine Schaltflaeche
```

Ohne sie ist die Datenschutzoption unvollständig: Ein Nutzer, der
Transkriptinhalte gespeichert hat und sie loswerden will, hätte **keinen Weg**.
Die Transkript-Historie hat mit `clear_entries()` bereits ein Vorbild.

---

# 5. Entscheidungen aus diesem Run

Diese fünf Punkte wurden von der Vorarbeit **nicht** beantwortet oder
**falsch** beantwortet. Sie werden hier erstmals geschlossen.

## FD-R1 / OD-19 — Replayte Records sind grundsätzlich LOW

```text
ENTSCHEIDUNG   HIGH := is_internal
                    OR ( NOT replayed
                         AND ( level >= WARNING
                               OR channel == "audit"
                               OR type is not None ) )
STATUS         GESCHLOSSEN
```

**Warum das eine Korrektur ist.** Das adversariale Review begründet den Schutz
gegen die Replay-Flut damit, dass replayte Records „ohne `type`" als LOW gälten.
Das trifft nicht zu: **Jedes** Serverevent hat einen `type` und wäre nach der
ursprünglichen Regel HIGH. Der Flutschutz hätte in genau dem Fall nicht
gegriffen, für den er gedacht war — Serverneustart bei serverseitiger Retention
`0` löst einen Replay der **vollständigen** Serverhistorie aus.

Mit `NOT replayed` ist der Schutz wirksam **und verlustfrei**: Replayte Daten
stehen bereits in der Datenbank und würden vom Dedupe-Index ohnehin unterdrückt.

**Benannte Grenze, bewusst akzeptiert.** Ein replayter `ERROR`, den der Client
noch nie gesehen hat — also beim allerersten Verbindungsaufbau —, kann unter
Überlast verworfen werden. Sichtbar über `dropped_watermark` und
`logging.records_dropped`.

## FD-R2 / OD-20 — `LOGGER_CHANNEL_MAP` verbindlich festgelegt

```text
ENTSCHEIDUNG   Nur "text" -> "transcription". ALLES ANDERE -> "system".
               NIE "performance" aus einem Loggernamen.
               NIE "audit" aus einem Loggernamen.
STATUS         GESCHLOSSEN
```

Das Audit enthielt an dieser Stelle einen unaufgelösten Gedanken im Fließtext
(„→ performance? NEIN → system"). Ein Coding-Agent hätte dort echten
Interpretationsspielraum gehabt.

## FD-R3 / OD-21 — Zusätzlicher Beobachtungspunkt für Protokollfehler

```text
ENTSCHEIDUNG   in V1, in OBS-040. EventStreamTransport.run(), except-Zweig
               -> client.eventstream.protocol_error, OHNE Rohframe.
STATUS         GESCHLOSSEN
```

Der Coordinator-Hook sieht jedes erfolgreich **validierte** Ergebnis, nicht
jedes Frame. Ausgerechnet der interessanteste Diagnosefall — ein Server, der das
Protokoll verletzt — bliebe sonst ein unstrukturierter WARNING-Text. Kosten: eine
Zeile, kein zusätzlicher Kontrollfluss.

## FD-R4 / OD-22 — Lebensdauer des Managers in `app.py::main()`

```text
ENTSCHEIDUNG   Manager wird in app.py::main() erzeugt und in einem
               try/finally gestoppt, NACH bridge.stop(10.0).
               DesktopApplication bekommt ihn uebergeben und stoppt ihn NICHT.
STATUS         GESCHLOSSEN
```

Es gibt **vier** Wege, auf denen `run_gui` zurückkehrt, ohne dass eine
`DesktopApplication` existiert oder ihr `shutdown` läuft: Instanzsperre,
fehlendes Tray, `LedConfigurationError`, UI-Initialisierungsfehler. Genau diese
Startabbrüche sind diagnostisch am wichtigsten — ihre Records blieben in der
Queue eines Daemon-Threads liegen. Der Headless-Pfad ruft `shutdown` überhaupt
nie.

Zugleich korrigiert: Der Manager kann **nicht** vor `AppConfig.load()` starten,
weil er dessen Ergebnis braucht. Der ältere Plan widersprach sich darin selbst.

## FD-R5 / OD-23 — Zähler `deduplicated` ist Pflicht

```text
ENTSCHEIDUNG   write_batch liefert (eingefuegt, dedupliziert);
               LoggingHealthSnapshot fuehrt deduplicated.
STATUS         GESCHLOSSEN
```

Ohne diesen Zähler ist im Betrieb **nicht unterscheidbar**, ob ein Replay
korrekt dedupliziert oder ob überhaupt nichts angekommen ist.

---

# 5b. Drei Lücken aus dem Readiness-Review von OBS-010

Der adversariale Implementation-Readiness-Review von OBS-010 (Run Report,
Abschnitt „OBS-010 Readiness Review") hat drei Stellen gefunden, an denen ein
Coding-Agent hätte raten müssen. Sie sind hier geschlossen und in die Verträge
eingearbeitet.

## FD-R6 — `scope` für `led` und `other`

```text
ENTSCHEIDUNG   session_id gesetzt                  -> "session"
               sonst und producer_kind == "server" -> "global"
               sonst (client, led, other)          -> "instance"
STATUS         GESCHLOSSEN.  Vertrag: CONTRACTS §1.3
```

Die ursprüngliche Formulierung nannte nur `server` und `client` und ließ `led`
und `other` undefiniert. Ein `lefx.*`-Record ohne Session ist eine Aussage über
**diese Prozessinstanz**, also `instance`.

## FD-R7 — `component` bei Controlframes

```text
ENTSCHEIDUNG   component = "eventstream", FEST.
STATUS         GESCHLOSSEN.  Vertrag: CONTRACTS §3.2
```

Die Regel „Namensraumpräfix von `type`" war nur für Serverevents formuliert. Auf
einen Controlframe angewandt (`type = "client.eventstream.gap"`) ergäbe sie
`"client"` — als Filterwert nutzlos.

## FD-R8 — Herkunft von `session_id`/`generation` bei Python-Logs

```text
ENTSCHEIDUNG   ausschliesslich aus record.__dict__ (bestehender extra-Vertrag).
               Der UnifiedLogHandler fragt KEINEN Sessionzustand ab und haelt
               KEINE Referenz auf Controller, Session oder Coordinator.
STATUS         GESCHLOSSEN.  Vertrag: CONTRACTS §3.1
```

Die Signatur `from_log_record(record, *, instance_id, session_id, generation)`
ließ offen, **wer** `session_id` liefert. Die naheliegende Antwort — der Handler
liest den aktuellen Sessionzustand — wäre falsch: Der Handler läuft auf sechs
Threads, darunter dem PortAudio-Callbackthread und dem Qt-Mainloop. Eine solche
Abfrage wäre entweder nicht thread-sicher oder bräuchte ein Lock im Hot Path —
und sie wäre eine Kopplung des Loggings an die Runtime, also ein Verstoß gegen
O-01.

Wer Korrelationsfelder braucht, benutzt die strukturierte
Client-Observation-API, **nicht** eine Python-Logzeile. Das ist zugleich der
inhaltliche Grund, warum es die strukturierte API überhaupt gibt.

---

# 6. Bewusst nach Teil B verschobene Entscheidungen

Diese Punkte sind **nicht** offen im Sinne des Freeze-Kriteriums: Sie berühren
keinen V1-Codepfad, und V1 trifft die genannte Vorkehrung, damit sie später
additiv entschieden werden können.

## FD-B1 / OD-09 — Capability-Modell für Adminrechte

```text
STATUS         GESCHLOSSEN (Teil B, OBS-110)
V1-VORKEHRUNG  ProviderState.AUTH_REQUIRED existiert von Anfang an.
               Der LoggingCore importiert nichts aus core/server_control/.
TENDENZ        aus dem binaeren Adminstatus ableiten
```

Der Server kennt **kein** benanntes Capability-Set für Admins, sondern nur
„admin ja/nein" plus die abgeleiteten Erweiterungen (`allSessions`,
`allChannels`, Channel `system`). `sessionCapabilities` ist etwas anderes:
Fähigkeiten der **Session**, nicht Rechte eines Nutzers.

Ein benanntes Set hat nur Wert, wenn der Server Rechte **feiner** vergeben kann
als „alles oder nichts" — und das ist eine **Serverproduktentscheidung**, keine
Clientarchitekturfrage. Sie heute zu treffen kostet nichts und nützt nichts.

## FD-B2 / OD-10 — Der zweite Provider ist die Session-Historie, nicht der Admin

```text
STATUS         GESCHLOSSEN als Planungsrichtung (Teil B, OBS-120)
V1-VORKEHRUNG  keine. hello.logAccess.historyPath wird von V1 bewusst NICHT
               vorweggenommen -- die Uebernahme ist eine additive Zeile.
```

Der vorhandene Session-Token berechtigt zu `/api/logs/sessions/{sessionId}`
**ohne** Admin-Key, und der Server liefert `historyPath` bereits in `hello` —
der Client verwirft das Feld heute. Ein `SessionHistoryProvider` braucht keine
Authentifizierung, keinen Key in der UI, keine `ServerControlConnection` und
liefert sofort den wertvollsten Vergleich: „Serverhistorie hat
`transcription.completed`, lokale Historie nicht."

**Das soll die V2-Planung wissen, bevor sie mit dem Admin-Key beginnt.**

## FD-B3 — HTTP-Fähigkeit für die Remote-Historie

```text
STATUS         GESCHLOSSEN als benannte Auflage (Teil B, OBS-120)
```

In diesem Run neu ermittelt: Der Client hat **keinen HTTP-Client**.
`requirements.txt` kennt nur `websockets`, `sounddevice`, `numpy`, `PySide6`,
`PyYAML` und `led-controller-version-3`. Die Historien-Endpunkte des Servers
sind HTTP. OBS-120 muss deshalb eine Abhängigkeits- und Buildentscheidung
mitplanen (stdlib gegen neue Abhängigkeit) und die PyInstaller-Spec prüfen.

Die dortigen `excludes` stehen dem **nicht** entgegen: Sie betreffen den
Server-Stack innerhalb von LEFX (`fastapi`, `starlette`, `uvicorn`, `pydantic`,
`lefx.interfaces.api|cli`), keinen HTTP-Client.

## FD-B4 — Multi-Host: `host` als spätere nullable Spalte

```text
STATUS         GESCHLOSSEN (Teil B, fruehestens mit einem Collector)
BEWERTUNG      ehrlich: TEILWEISE vorbereitet
```

Zwei Instanzen auf **zwei** Maschinen, die dieselbe Historie sehen wollen,
brauchen einen Collector — und dann fehlt `host`. Das ist **kein** Umbau des
Cores, sondern eine Migration: nullable Spalte hinzufügen, Altbestand `NULL`.
`SingleInstanceGuard` verhindert den Fall heute ohnehin auf derselben Maschine.

## FD-B5 — Der LedAdapter entsteht erst außerhalb des Prozesses

```text
STATUS         GESCHLOSSEN (Teil B, OBS-140)
V1-VORKEHRUNG  producer_kind = "led" existiert; eine Normalizer-Regel
               (logger startswith "lefx.") genuegt.
```

LEFX ist eine reguläre Abhängigkeit und läuft **im selben Prozess**; alle
`lefx.*`-Records erreichen den Root-Logger ohnehin. Ein echter,
transportgebundener Adapter wird erst nötig, wenn der LED-Controller in einen
eigenen Prozess oder auf ein eigenes Gerät wandert.

**Nebennutzen:** Die Erweiterbarkeit des Producer-Modells wird damit in V1
**bewiesen**, statt behauptet — ohne dass ein Feld, eine Tabelle oder eine
Schnittstelle hinzukommt.

---

# 7. Widerspruchsregister

Vollständig, einschließlich der Widersprüche innerhalb der Vorarbeit selbst.
Keine stille Korrektur.

| # | Widerspruch | Quellen | Auflösung | blockierte V1? |
|---|---|---|---|---|
| **W-1** | Channels groß- vs. kleingeschrieben | Zielbild §9/§16 ↔ Code | Kleinschreibung verbindlich (FD-C6). Zielbild bei nächster Überarbeitung angleichen | nein |
| **W-2** | Zielbild verlangt Einzelindizes auf `source_timestamp`, `producer_kind`, `type`, `level`, `segment_id`, `event_id` | Zielbild §16 ↔ Schema §9.2 | **Bewusste Abweichung**, begründet in `CONTRACTS §5.3`. Jeder Index kostet Schreibzeit; die gewählte Auswahl deckt jede Abfrage der V1-Filterleiste ab | nein |
| **W-3** | Ringbuffer und `live_buffer_size` gefordert | Zielbild §17, Abgrenzung §3.11/§3.12 ↔ Review §3 | **FD-S1** — gestrichen; die geforderte *Funktion* bleibt erfüllt, die *Bauform* ändert sich. **Abschnitt 4 zur Kenntnis** | nein |
| **W-4** | Zielbild sieht `core/server_control/` und `adapters/led.py` in der Modulstruktur | Zielbild §39 ↔ Plan §18 | Kein echter Widerspruch: Zielbild beschreibt den **Endzustand**. Beide entfallen in V1, sind in Teil B vorgesehen (FD-B1, FD-B5) | nein |
| **W-5** | V1-Abgrenzung listet das Canonical Record ohne `transcription_id` und ohne `server_cursor` | Abgrenzung §3.1 ↔ Schema §5.1 | Beide ergänzen: `server_cursor` zwingend (FD-C5), `transcription_id` empfohlen (FD-C1) | nein |
| **W-6** | Abgrenzung §8 verlangt Dateirechteprüfungen; die Vorarbeit übergeht sie | Abgrenzung §8 ↔ Vorarbeit | Nachgetragen als P-8/P-9 und Test M-11 in `CONTRACTS §4.3` | nein |
| **W-7** | Plan verlangt Managerstart *vor* `AppConfig.load` — unmöglich | Plan OBS-06 ↔ Plan „Übergreifende Regeln" | **FD-R4**: Reihenfolge korrigiert | nein |
| **W-8** | `manager.stop()` in `DesktopApplication.shutdown()`, obwohl vier Startabbruchpfade dort nie hinkommen | Plan ↔ `ui/application.py` | **FD-R4**: Lebensdauer nach `app.py::main()` | nein |
| **W-9** | Testerwartung „Duplikat erzeugt Record mit `replayed=True`" ↔ Dedupe-Index unterdrückt die Zeile | Plan OBS-07 ↔ Schema §7.3 | Erwartung korrigiert: *„Ein Duplikat wird beobachtet, normalisiert und an den Store übergeben; der Store fügt KEINE zweite Zeile ein; `deduplicated` steigt."* | nein |
| **W-10** | Audit: „JEDES `/ws/logs`-Frame" ↔ Protokollfehler erreichen den Dispatch nie | Audit §2.4 ↔ `event_stream.py` | Präzisiert zu *„jedes erfolgreich validierte Ergebnis"*; Lücke geschlossen durch **FD-R3** | nein |
| **W-11** | Ringbuffer im Worker, „damit die Live-Ansicht exakt sieht, was gespeichert wurde" — falsch, sobald der Store scheitert | Concurrency §10.4 | Entfällt mit **FD-S1** | nein |
| **W-12** | Blockweises Löschen nur bei der Altersretention gefordert, bei der Anzahlretention ein einzelnes großes `DELETE` | Schema §9.5 | **Beide** blockweise, Anzahlgrenze zusätzlich gegen NULL gesichert (`CONTRACTS §5.6`) | nein |
| **W-13** | `mode=ro` für Leser ↔ WAL erlaubt das nicht allgemein | Schema §8.3/§14.4 | `PRAGMA query_only = ON` statt `mode=ro` (`CONTRACTS §5.4`) | nein |
| **W-14** | Regel R-2 („kein unredigierter Record je in der Queue") ↔ Redaction von `raw` gehört in den Worker | Audit §12.2 ↔ Review AR-2 | R-2 präzisiert: gilt für **clienterzeugte** Records; Serverpayloads im Worker (`ARCH §8.2`) | nein |
| **W-15** | OD-02 als blockierend eingestuft | OPEN_DECISIONS ↔ Review §5.2 | Herabgestuft auf **nicht blockierend** (FD-C1) | nein |
| **W-16** | `voice-stt-client/AGENTS.md` nennt `docs/IMPLEMENTATION_ROADMAP.md` als maßgeblich; die Vorarbeit hat sie nicht herangezogen | AGENTS.md ↔ Vorarbeit | **GEPRÜFT UND GESCHLOSSEN** in `EV-02 / C-13`: kein Widerspruch. Die Roadmap trifft keine Aussage über einen clientseitigen Observability-Store, eine Logansicht oder ein kanonisches Recordmodell | nein |
| **W-17** *(neu)* | Wasserstandsregel sollte replayte Records verwerfen, stufte sie aber als HIGH ein | Review S-2 ↔ Review RD-2 | **FD-R1**: `NOT replayed` in die Prioritätsregel aufgenommen | nein |
| **W-18** *(neu)* | Zwei Nummernkreise für dieselbe Arbeit: `OBS-00…OBS-13` im V1-Plan gegen `OBS-010…OBS-060` im Gesamtplan | V1-Plan §19 ↔ Gesamtplan §5 | **Abschnitt 8**: verbindliche Abbildung 14 → 6. Der Gesamtplan-Nummernkreis ist maßgeblich | nein |
| **W-19** *(neu)* | Der Gesamtplan ordnet die Redaction OBS-020 zu, der V1-Plan liefert sie zusammen mit dem Normalizer in OBS-00 | Gesamtplan §9 ↔ V1-Plan OBS-00 | **Abschnitt 8**: Redaction gehört zu OBS-010. Normalizer und Redaction sind untrennbar — der Normalizer ruft `redact` am Ende jedes Pfades | nein |

**Keiner der 19 Widersprüche blockiert V1.** Alle sind aufgelöst.

---

# 8. Korrektur der Work-Package-Grenzen

Der Gesamtplan und der V1-Implementierungsplan benutzen **zwei verschiedene
Nummernkreise** für dieselbe Arbeit. Das wäre für einen Coding-Agenten eine
echte Fehlerquelle. Verbindlich ist der Nummernkreis des **Gesamtplans**.

## 8.1 Abbildung 14 → 6

| Gesamtplan | enthält aus dem V1-Plan | Gegenstand |
|---|---|---|
| **OBS-010** | OBS-00, OBS-01, Protokolle aus OBS-04/09/12 | `models.py`, `redaction.py`, `normalizer.py`, `storage/base.py`, `sinks/base.py`, `query/base.py`, ClientObservation-API-Signatur |
| **OBS-020** | OBS-02, OBS-03, OBS-06 | `health.py`, `ingress.py`, `adapters/python_logging.py`, Backpressure |
| **OBS-030** | OBS-04, OBS-05, OBS-12 | `storage/sqlite.py`, `worker.py`, `manager.py`, Retention, `sinks/jsonl_file.py` |
| **OBS-040** | OBS-07, OBS-08 | `adapters/server_live.py`, Fan-out-Hook, strukturierte Client-Hooks |
| **OBS-050** | OBS-09, OBS-10, OBS-11 | `query/local.py`, `query/service.py`, Settings, `ui/logs/*` |
| **OBS-060** | OBS-13 | Failure-, Isolations- und Performance-Gate, manuelle Abnahme |

## 8.2 Zwei Titelkorrekturen mit Begründung

```text
OBS-020  Titel bisher "Ingress, Health & Redaction"
         Titel jetzt   "Ingress, Backpressure, Health & Python-Logging-Handler"

  Begruendung: Die Redaction wandert nach OBS-010, weil sie vom Normalizer am
  Ende JEDES Pfades aufgerufen wird -- die beiden sind nicht sinnvoll trennbar,
  und beide sind reine, I/O-freie Logik, die das Gate von OBS-010 erfuellt
  ("funktioniert ohne Qt, SQLite und WebSocket"). OBS-020 besitzt dafuer den
  Python-Logging-Handler, der bisher unklar zwischen 020 und 030 lag.

OBS-030  Titel bisher "Queue, Worker, SQLite & Retention"
         Titel jetzt   "Worker, SQLite-Store, Retention & JSONL-Sink"

  Begruendung: Die Queue liegt im Ingress und damit in OBS-020. Der bisherige
  Titel haette einen Coding-Agenten dazu verleitet, sie zweimal zu bauen.
```

**Keine Paketvermehrung.** Es bleibt bei sechs Paketen in Teil A und neun in
Teil B.

## 8.3 Eine Reihenfolgekorrektur

```text
Der V1-Plan baut den Store (OBS-04) VOR dem Handler (OBS-03), damit der erste
Ende-zu-Ende-Nachweis frueh moeglich ist. In der Sechserstruktur liegt der
Handler in OBS-020 und der Store in OBS-030, also umgekehrt.

FESTLEGUNG
  Das ist zulaessig. Der Handler ist gegen den Ingress allein vollstaendig
  testbar (aufzeichnender Fake). Der Ende-zu-Ende-Nachweis
  "logger.info -> SQLite" gehoert zum GATE VON OBS-030, nicht zu OBS-020.
  OBS-020 darf ohne ihn abgenommen werden.

  Gruene Tests gegen Fakes sind ausdruecklich KEIN Fertigstellungsnachweis --
  diese Regel gilt unveraendert; sie verlagert hier nur, WO der Nachweis
  faellig wird.
```

## 8.4 Eine Abhängigkeitskorrektur

```text
BISHER   OBS-050 haengt an OBS-030.
JETZT    OBS-050 haengt an OBS-030 UND ist von OBS-040 UNABHAENGIG.

Grund: Nach dem Wegfall des Ringbuffers (FD-S1) benutzt der Live-Modus
dieselbe Provider-Schnittstelle wie die Historie. Damit haengt die UI nur noch
am Query-Layer und kann PARALLEL zu OBS-040 gebaut werden.
```

---

# 9. Was ausdrücklich **nicht** mehr zu diskutieren ist

Die folgenden Fragen standen als „offene Entscheidung" in Zielbild §46 bzw.
V1-Abgrenzung §13. Sie sind durch den **Code** beantwortet, nicht durch eine
Abwägung, und werden hier nur mit der Fundstelle geschlossen.

| Frage | Antwort |
|---|---|
| exakte Client-Channels | die vier Server-Channels, klein; keine zusätzlichen |
| `producer_kind`-Werte | `client`, `server`, `led`, `other` |
| Dedupe-Schlüssel des Serverstreams | `(producer_id, event_id)`, partieller UNIQUE-Index |
| lokale DB-Datei und Ablageort | `%LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3` |
| SQLite-Schema-Versionierung/Migration | `PRAGMA user_version` + `schema_meta`, keine Migrationstabelle |
| wie strukturierte Clientevents emittiert werden | ein injizierter `ObservabilityIngress`; kein Eventbus, kein Singleton |
| genaue Adaptergrenze zum Server-Eventstream | `DualSessionCoordinator._handle_event` / `_handle_control` |
| genaue Auth-/Capability-Schnittstelle des Servers | vollständig ermittelt; V1 nutzt sie nicht |
| exakter UI-Ort der Logansicht | eigenes, nicht-modales `LogWindow` |
| exakter UI-Ort der Logging-Konfiguration | sechster Tab im bestehenden `SettingsDialog` |
| Konfigurationsmodell | `logging.observability.*` als Unterabschnitt |
| Shutdown-/Flush-Verhalten | `manager.stop(2.0)` **nach** `bridge.stop(10.0)`, im `finally` von `app.py::main()` |
| Metriken/Health für gedroppte Records | `LoggingHealthSnapshot`; ein `logging.records_dropped` nach Erholung |
| ob `ServerHistoryProvider` cached | entfällt — nicht Teil von V1 |
| endgültiges CanonicalRecord-Schema und Feldnamen | `LOGGING_CONTRACTS_FREEZE_V1.md §1` |
| `host` sinnvoll? | nein, in V1 nicht führen |
| `sequence` nötig? | nein, `logs.id` genügt |
| `provider`/`source_record_id` nötig? | nein als Spalte, ja am Query-DTO |
| separate `server_event_id` und `record_id`? | ja, beide |
| Enum-Versionierung | TEXT, offen, nur `level` geschlossen |
| Queue-Größe und Priorisierung | eine Queue, 8192, Wasserstandsregel bei 75 % |

---

# 10. Abschluss

```text
Blockierende offene Entscheidungen nach diesem Freeze:  KEINE
Offene Widersprueche:                                    KEINE
Offene Informationsluecken:                              KEINE
```

Kein Coding-Agent muss ab hier eine grundlegende Logging-Architekturentscheidung
treffen. Wo dennoch eine nötig wird, gilt:

```text
DECISION REQUIRED
  -> anhalten
  -> im Run Report des Pakets begruenden
  -> hier nachtragen
  -> KEINE stille Planaenderung
```
