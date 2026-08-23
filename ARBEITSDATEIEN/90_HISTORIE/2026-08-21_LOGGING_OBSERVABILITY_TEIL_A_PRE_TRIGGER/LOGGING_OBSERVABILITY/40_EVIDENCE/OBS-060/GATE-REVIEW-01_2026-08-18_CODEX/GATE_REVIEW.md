# OBS-060 – Logging V1 Final Gate Review

Datum: 2026-08-18  
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-060_V1_GATE_REVIEW.md`  
Gepruefter Run: `RUN-OBS-060-01_2026-08-18`  
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`  
Branch/HEAD bei Reviewbeginn: `feat/einheitliche-triggerarchitektur`, `7fc6ca6`  
Pruefinterpreter: Python 3.12.13, PySide6 offscreen

## Ergebnis

**`G-OBS-V1 FAIL`**

Logging V1 ist automatisiert weitgehend belastbar, aber nicht gate-faehig.
Der zwingende manuelle Produktionsnachweis M-1…M-11 fehlt. Zusaetzlich bestehen
eine reproduzierte Contract-Verletzung bei der als `IMMEDIATE` eingefrorenen
Aktivierung aus einem initial deaktivierten Prozess, eine offene
Architektur-/Contract-Entscheidung zu `logging.record_rejected` sowie weitere
noch nicht entschiedene Freeze-Fragen. Deshalb wurden weder Gate-Haken noch
Abschlusskriterium gesetzt und kein Commit erstellt.

## 1. Unabhaengig gepruefter Repositoryzustand

- HEAD ist `7fc6ca6` (`feat(observability): complete OBS-050 local log view`).
- Der OBS-060-Produktdiff umfasst sechs Dateien: `app.py`,
  `core/audio_capture.py`, `core/observability/ingress.py`,
  `core/observability/manager.py`, `core/observability/query/local.py` und
  `core/observability/worker.py` (+131/-13 laut Run-Scope).
- `00_NORMATIV/` und der Logging-Gesamtplan besitzen keinen Diff gegen HEAD.
- Zwei geaenderte Triggerarchitektur-Dokumente sind laufsfremd und duerfen
  nicht in einen Logging-Commit gelangen (O-3).
- Die acht bewusst unversionierten Prompt-/Pipeline-Eintraege wurden nicht
  veraendert, gestaged oder aufgenommen.
- `git diff --check` ist leer.

Die Codekorrekturen B-1 (Store-Recovery), B-2 (`malformed++`),
Worker-Fehlerbudget, Sink-Reuse, `complete`-Semantik und der Lifecycle-Guard
sind im Diff vorhanden und durch die zugeordneten Tests abgedeckt. Der Gate-
Review hat keinen Produktcode geaendert.

## 2. Blockierende Befunde

### B-G1 – Das vorgeschriebene manuelle Produktionsprotokoll fehlt

`WP-OBS-060` erklaert die manuelle Abnahme am realen Produktionspfad zur
Pflicht und bestimmt ausdruecklich: Ohne vollstaendiges M-Protokoll gilt V1 als
„teilweise“, nicht als „erledigt“. Gefordert sind Datum, Serveradresse und
Clientversion.

Ein solches Protokoll existiert nicht. Automatisierte Pendants belegen viele
Teilwirkungen, ersetzen aber keinen der ausdruecklich manuellen Schritte:

| M | Gate-Befund am realen Produktionspfad |
|---|---|
| M-1 | offen |
| M-2 | offen; nur automatisiertes Pendant vorhanden |
| M-3 | offen; nur automatisiertes Pendant vorhanden |
| M-4 | offen; nur automatisiertes Pendant vorhanden |
| M-5 | offen; nur automatisiertes Pendant vorhanden |
| M-6 | offene manuelle Sichtpruefung |
| M-7 | offen; automatisierter Privacy-Test ist kein manueller Produktionslauf |
| M-8 | offen; automatisierter Policy-Test ist kein manueller Produktionslauf |
| M-9 | offen; automatisierter Retention-Test ist kein manueller Produktionslauf |
| M-10 | offen; Prozess-/Threadpruefung am installierten Client fehlt |
| M-11 | offen am realen Ablageort; `icacls` wurde nur in `%LOCALAPPDATA%\\Temp` ausgefuehrt |

Damit ist ein PASS unabhaengig von allen automatisierten Ergebnissen
ausgeschlossen.

### B-G2 – Initial deaktivierte Observability kann nicht `IMMEDIATE` aktiviert werden

`CONTRACTS §10.3` friert `logging.observability.enabled` als `IMMEDIATE` ein.
Der reale Kompositionspfad baut bei `enabled=False` jedoch `NULL_INGRESS`,
keinen Worker und keinen Store. `NullIngress.apply_config()` und
`register_config_listener()` sind No-Ops. Eine spaetere Aktivierung erreicht
deshalb weder Manager noch Worker.

Unabhaengige Laufzeitprobe gegen den Produktcode:

```text
vor Apply : NullIngress disabled None
nach Apply: NullIngress disabled None False
```

Der Prozess bleibt also deaktiviert. Die bestehenden OBS-050-Tests pruefen nur
„enabled -> disabled -> enabled“ an einem bereits voll aufgebauten Manager und
decken „initial disabled -> enabled“ nicht ab. Das verletzt den eingefrorenen
Apply-Contract und das Final-Gate-Kriterium zur Settings-Ownership.

Minimale Korrekturanforderung: Verhalten und Regressionstest fuer den
Initial-Disabled-Pfad. Falls Aktivierung stattdessen einen Neustart verlangen
soll, ist das eine Contract-/Apply-Policy-Aenderung und benoetigt eine
ausdrueckliche Entscheidung.

### B-G3 – O-1 ist eine echte offene Architektur-/Contract-Entscheidung

`ARCH §8.3` verlangt bei einer Normalizer-Ausnahme genau einen Ersatzrecord
`logging.record_rejected` mit Komponente und Ausnahmetyp. `CONTRACTS §3`
verlangt zugleich, dass der Normalizer nie wirft und im Zweifel `None` liefert.
Der aktuelle Clientpfad zaehlt seit OBS-060 zwar `malformed`, kann den
Ausnahmetyp nach dem intern verschluckten Fehler aber nicht mehr kennen und
erzeugt keinen Ersatzrecord.

Die unabhaengig wiederholte Failure-Probe meldet selbst:

```text
[OPEN] F-7.4 no substitute record logging.record_rejected for a normalizer
exception the normalizer swallowed itself (count=0)
```

Das Gate darf weder `CONTRACTS §3` noch `ARCH §8.3` stillschweigend priorisieren
oder eine Signaturaenderung freigeben. **DECISION REQUIRED.** Bis dahin sind
Fehlerfallabdeckung und Failure-Evidence nicht vollstaendig.

### B-G4 – O-7 ist eine unentschiedene Erweiterung einer Freeze-Liste

`client.audio.stream_stats` traegt `capture_queue_depth` und
`send_queue_depth` zusaetzlich zu der in `ARCH §8.6` ausgeschriebenen
Feldliste. `details` ist zwar allgemein ein offenes Mapping, der konkrete
Aggregatvertrag ist jedoch normativ ausgeschrieben. Weder Entfernung noch
nachtraegliche Aufnahme in den Freeze ist durch diesen Gate-Auftrag
autorisiert. **DECISION REQUIRED** vor einem echten Abschluss-Freeze.

## 3. Evidence-Befunde

### E-1 – Traceability behauptet Erfuellung trotz eigenem OPEN

`V1_REQUIREMENTS_TRACEABILITY.md` markiert Final-Gate-Kriterium 4
„Fehler intern isolieren“ mit `FI F-1…F-10, alle zehn Faelle` als erfuellt.
`V1_FAILURE_INJECTION.md` und die Rohausgabe enthalten aber F-7.4 als `OPEN`.
Die Traceability ist damit fuer dieses Kriterium nicht konsistent.

### E-2 – Performance-Pruefung B-4.2 ist falsch beschriftet

Die unabhaengige Wiederholung ergab erste Seite 3,74 ms, zweite Keyset-Seite
5,48 ms. Die Probe meldet trotzdem „the keyset second page is not slower than
the first“, weil der Code tatsaechlich nur
`page2 < max(50 ms, first_page * 5)` prueft. Die gemessene Performance ist
unauffaellig; Aussage, Implementierung und `V1_PERFORMANCE.md` muessen aber
dieselbe Eigenschaft benennen.

## 4. Alle 13 offenen Punkte aus V1_OPEN_POINTS.md

| Punkt | Unabhaengige Gate-Einordnung |
|---|---|
| O-1 | **blockierend, DECISION REQUIRED**; siehe B-G3 |
| O-2 | Produkt-DDL ist normativ partiell und Mutation wird rot; die falsche Begruendung im Work Package/Gesamtplan braucht eine planerische Entscheidung, kein stilles Umschreiben |
| O-3 | nicht Logging-Scope; in keinem Logging-Commit aufnehmen |
| O-4 | bekannte Zaehlerluecke; Zaehlersatz ist eingefroren, keinen Zaehler erfinden |
| O-5 | `qsize()` ist fuer `max_send_queue_depth` nachvollziehbar, steht aber in Spannung zur woertlichen „ausschliesslich int-Attribute erhoehen“-Formulierung; als Freeze-Klaerung dokumentieren, nicht still aendern |
| O-6 | historischer Zahlenfehler bleibt sichtbar; nicht rueckwirkend umschreiben |
| O-7 | **blockierend, DECISION REQUIRED**; siehe B-G4 |
| O-8 | aktuelle Form erfuellt nur das Format `namespace:value`; semantische Korrelationsaenderung beruehrt §12 und braucht eine Entscheidung |
| O-9 | redaktionelle Fragilitaet, kein Produktblocker |
| O-10 | Rollback der Observability-Konfiguration ist in §10.4 nicht festgelegt; Erweiterung nur nach Entscheidung |
| O-11 | Sichtbarkeit der 5000-Zeilen-Kappung waere eine UI-Vertragserweiterung; Entscheidung ausstehend |
| O-12 | historischer Checklist-Haken bleibt nach der ausdruecklichen Checklist-Regel unangetastet; organisatorische Richtigstellung ausstehend |
| O-13 | Tests sind mit externem WMI-Shim reproduzierbar; eine versionierte Testumgebungsloesung bleibt organisatorisch zu entscheiden |

Von den sieben im Run als entscheidungsbeduerftig ausgewiesenen Punkten sind
O-1 und O-7 vor einem echten V1-Abschluss gate-relevant. O-2, O-8, O-10,
O-11 und O-13 bleiben ausdrueckliche Entscheidungen; dieses Gate loest keine
davon eigenmaechtig auf.

## 5. Final-Gate-Kriterien

| # | Kriterium | Gate-Ergebnis |
|---|---|---|
| 1 | rein beobachtend | automatisiert belegt |
| 2 | keine Runtime-/Lifecycle-Autoritaet | automatisiert belegt |
| 3 | kanonische Records | automatisiert belegt |
| 4 | Fehler intern isoliert | **nicht vollstaendig: O-1/E-1** |
| 5 | nicht blockierend | belegt |
| 6 | bounded Backpressure | belegt |
| 7 | SQLite als lokale Wahrheit | belegt |
| 8 | kein Memory-Ringbuffer | belegt |
| 9 | Privacy/Redaction | automatisiert belegt, manuelle M-7-Abnahme offen |
| 10 | keine Audio-Payloads/Secrets | automatisiert belegt, manuelle M-7-Abnahme offen |
| 11 | Transcript-Policy | automatisiert belegt, manuelle M-8-Abnahme offen |
| 12 | Server-Live/Client-Hooks | automatisiert belegt, Produktionsabnahme offen |
| 13 | Replay/Dedupe/Identity | automatisiert belegt, manuelle M-5-Abnahme offen |
| 14 | Query/UI-Schicht | automatisiert belegt, manuelle M-6-Abnahme offen |
| 15 | Settings-Ownership | **FAIL: Initial-Disabled -> Enabled funktioniert nicht** |
| 16 | Betrieb ohne UI | belegt |
| 17 | Regressionstests | belegt |
| 18 | Failure/Performance/Privacy-Evidence | **PARTIAL: O-1/E-1, E-2 und M-Protokoll offen** |

## 6. Unabhaengig wiederholte Tests und Probes

```text
pytest V1-Auswahl:       652 passed, 513 deselected                     exit 0
pytest volle Suite:      1165 passed                                    exit 0
unittest volle Suite:    Ran 1165 tests, OK                             exit 0
E2E-Probe:               24 PASS, 0 FAIL                                exit 0
Failure-Injection:       48 PASS, 0 FAIL, 1 OPEN (O-1)                  exit 0
Runtime-Isolation:       R-2…R-7 identisch zu R-1                       exit 0
Performance:             14 PASS laut Probe, Beschriftungsfehler E-2    exit 0
Privacy:                 24 PASS, M-11 nur im Temp-Pfad                 exit 0
Packaging:               7 PASS                                         exit 0
Mutationen:              8/8 machen Tests rot; 6 Dateien byte-identisch exit 0
```

Die volle Suite wurde mit dem bereits dokumentierten externen WMI-Shim und
`QT_QPA_PLATFORM=offscreen` ausgefuehrt. Anders als im Implementierungslauf ist
die zuvor fehlende `lefx.interfaces`-Abhaengigkeit in der aktuellen Umgebung
verfuegbar; deshalb sind jetzt alle 1165 Tests gruen.

## 7. Entscheidung und naechster zulässiger Schritt

**`G-OBS-V1 FAIL`**

Vor einem Re-Gate sind mindestens erforderlich:

1. vollstaendiges manuelles M-1…M-11-Protokoll am realen Produktionspfad mit
   Datum, Serveradresse und Clientversion;
2. ausdrueckliche Entscheidung und anschliessende vertragskonforme Behandlung
   von O-1;
3. Korrektur oder ausdrueckliche Apply-Policy-Entscheidung fuer
   Initial-Disabled -> Enabled, inklusive Regressionstest;
4. Entscheidung zu O-7 sowie dokumentierte Behandlung der uebrigen fuenf
   entscheidungsbeduerftigen offenen Punkte;
5. Konsistenzkorrekturen E-1 und E-2.

Danach ist ein neuer unabhaengiger OBS-060 Final Gate Review zulaessig.
Kein OBS-V1-Abschlusscommit, kein Push und keine Triggerarchitektur-Migration.
