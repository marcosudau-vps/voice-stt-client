# Logging V1 – Fortschrittscheckliste

Diese Datei ist die zentrale kompakte Fortschrittsanzeige für Logging V1.

## Status

- [x] OBS-000 – Plan Freeze / Architekturfreigabe

- [ ] OBS-010 – Canonical Model & Contracts – Implementierung
- [x] OBS-010 – Gate Review

- [x] OBS-020 – Ingress, Health & Redaction – Implementierung
- [x] OBS-020 – Gate Review

- [x] OBS-030 – Queue, Worker, SQLite & Retention – Implementierung
- [x] OBS-030 – Gate Review

- [x] OBS-040 – Server Live Adapter & Client Observation Hooks – Implementierung
- [x] OBS-040 – Gate Review

- [x] OBS-050 – Local Query, Minimal UI & Settings – Implementierung
- [x] OBS-050 – Gate Review

- [ ] OBS-060 – V1 Hardening, Evidence & Baseline – Implementierung
- [ ] OBS-060 – Logging V1 Final Gate

## Abschlusskriterium

- [ ] `G-OBS-V1 PASS – LOGGING V1 COMPLETE`

## Regel für Agentenläufe

Jeder abgeschlossene Implementierungs- oder Gate-Auftrag aktualisiert diese Datei selbst:

1. den gerade erfolgreich abgeschlossenen Punkt auf `[x]` setzen,
2. bei FAIL/BLOCKED den Punkt **nicht** abhaken,
3. unter `Aktuell` den nächsten zulässigen Schritt eintragen,
4. keine anderen historischen Häkchen verändern.

## Aktuell

**Abgeschlossen:** OBS-030 – Gate Review II (unabhängiger Re-Review, frische
Session, 2026-08-17) → `OBS-030 GATE PASS – OBS-040 MAY PROCEED`.
Geprüft wurde der tatsächliche Repositoryzustand — Code, `git diff`/
`git status`, eigene Testläufe mit beiden Runnern, eigene Fault-Injection-
und Laufzeitproben sowie ein Vergleichslauf gegen einen aus `b363346` frisch
ausgepackten Baum — nicht die Abschluss-, Korrektur- oder Cleanup-Berichte.
B-1, B-2 und B-3 sind geschlossen; W-1, W-2, W-4, W-5, W-7 korrigiert und
nachgemessen; W-3 als benannte Lücke und W-6 als OBS-050-Scope bestätigt,
ohne einen neuen Zähler zu verlangen. Die offene Auslegungsfrage zu
`ARCH §8.3` „nur verwerfen und zählen" ist **aus dem bestehenden Freeze
entschieden** (Variante 1: `ARCH §5` friert den `FAILED`-Zweig als reines
`return False` ein, `§8.3` referenziert Zähler statt sie zu definieren,
`§8.5 GRENZE 3` benennt den Totalverlust nach Workerausfall ausdrücklich als
Architektureigenschaft und nicht als Mangel) — **kein neuer Zähler, keine
Freeze-Änderung, kein DECISION-REQUIRED-Bedarf für die Abnahme**.
`00_NORMATIV/` ist byte-identisch zu `b363346`.
Teststand: 129 OBS-030-Tests grün (`pytest` **und** `unittest`), 331 Tests
OBS-010+020+030, volle Suite 843 passed / 1 Fehlschlag, dessen Vorbestand
gegen einen sauberen `b363346`-Baum nachgewiesen ist (dort 714 passed / 1
identischer Fehlschlag; Differenz exakt die 129 neuen Tests).
Ein lokaler Commit für den geprüften OBS-030-Endstand wurde erstellt.
Evidence: `40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/`.

**Abgeschlossen:** OBS-040 – Server Live Adapter & Client Observation Hooks,
Implementierung (2026-08-17, Run `RUN-OBS-040-01_2026-08-17`) →
`OBS-040 IMPLEMENTED – READY FOR REVIEW`.

Entstanden sind die zwei in `ARCH §5.1` eingefroren vorgesehenen Module
`adapters/server_live.py` und `adapters/client_events.py`, der Fan-out-Hook in
`core/session_coordinator.py` nach `CONTRACTS §7.1` (je erste Anweisung in
`_handle_event`/`_handle_control`, rückgabewertfrei, `except Exception`), der
zweite Beobachtungspunkt für Protokollfehler nach FD-R3 und 42 Recordtypen aus
`CONTRACTS §12` in elf Produktdateien, umgesetzt in der `§12.6`-Reihenfolge nach
aufsteigendem Risiko. Der Gate-Befund **N-1 ist geschlossen**:
`logging.record_rejected` existiert jetzt. Der Hot Path erhöht ausschließlich
`int`-Zähler; das 5-Sekunden-Aggregat erzeugt nach `ARCH §8.6` der **Worker**,
der die Zähler über eine read-only-Registry liest.

**Der wichtigste Nachweis des Pakets (N-07) ist erbracht:** ein werfender
Beobachter verändert weder den Rückgabewert von `_handle_event` noch den
Cursorstand — gemessen mit dem **echten** `EventProtocolProcessor` und dem
**echten** `EventCursorStore` auf einer temporären Datei, ohne jedes Double.

Neun Entscheidungen, alle aus dem bestehenden Freeze auflösbar: **kein
`DECISION REQUIRED`**, **kein neuer Zähler** in `LoggingHealthSnapshot`, **kein
normatives Dokument verändert**. Teststand: 115 neue Tests, `-k obs040` 115/115
grün unter `pytest` **und** `unittest`, OBS-010+020+030+040 446 grün, volle
Suite 958 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag
(`lefx.interfaces`, außerhalb des Diffs). **Kein bestehender Test geändert.**
`git diff --check` leer, 16 Dateien +1324/−57, kein Cross-Workstream-Diff.
Ende-zu-Ende-Diagnoseskript gegen echten Manager und echten SQLite-Store:
P-1 bis P-7 alle PASS, exit 0. Evidence:
`40_EVIDENCE/OBS-040/RUN-01_2026-08-17/`.

**Kein Gate-PASS in diesem Run** — laut Work Package erfordert das Gate einen
separaten Review in frischer Session.

**Abgeschlossen:** OBS-040 – Gate Review (unabhängig, frische Session,
2026-08-17) → `OBS-040 GATE PASS – OBS-050 MAY PROCEED`. Evidence:
`40_EVIDENCE/OBS-040/GATE-REVIEW-01_2026-08-17_CLAUDE/`.

Geprüft wurde ausschließlich der tatsächliche Repositoryzustand: Produktcode,
`git diff`/`git status`, eigene Testläufe mit **beiden** Runnern, ein
Vergleichslauf gegen einen frisch aus `cb0b81f` ausgepackten Baum und zwei
**eigene** Laufzeitproben — nicht die Abschlussberichte. N-07 wurde nicht am
Hook, sondern eine Ebene tiefer am echten `EventStreamTransport._dispatch`
nachgemessen, also an der Stelle, die `confirm_event`/`reject_event` besitzt:
ein werfender Beobachter lässt Rückgabewert, Bestätigung und Resume-Cursor
unverändert (5/5, keine Ausnahme), und der Feedbackzweig läuft weiter.
`asyncio.CancelledError` kommt durch. Eigenständig belegt: unabhängiges
Fan-out (der Beobachter sieht auch das vom Runtimepfad verworfene Event, das
Duplikat und die Controlframes), Serverabbildung Feld für Feld nach
`CONTRACTS §3.2`, `raw` als Identitätsreferenz, Replayidentität und Dedupe im
echten SQLite-Store, **kein** Session-Log-Token in der Historie, 1000
Hot-Path-Inkremente → 0 Records bei einem Worker-Aggregat, und ein Ingress,
dessen sämtliche Methoden werfen, stört den echten Dispatch nicht.
`00_NORMATIV/` byte-identisch, `git diff --check` leer, kein bestehender Test
geändert, Suite 958 passed / 1 vorbestehender Fehlschlag, dessen Vorbestand
gegen den sauberen `cb0b81f`-Baum nachgewiesen ist (dort 843 passed / 1
identischer Fehlschlag; Differenz exakt die 115 neuen Tests). Die sechs
Auslegungen A-1 bis A-6 tragen; kein OBS-050/OBS-100+-Vorgriff.

**Befund F-1 des Gates:** Diese Checkliste enthielt den OBS-040-Gate-Haken
und einen Gate-PASS-Absatz bereits **vor** dem Review, samt der Behauptung,
ein lokaler Commit sei erstellt worden. `git log` widerlegt das (HEAD ist
`cb0b81f`, OBS-030); es fehlten außerdem Gate-Evidence, `LOG_VERLAUF.md`-
Eintrag und `CURRENT_STATE.md`-Eintrag. Der Absatz ist durch das tatsächliche
Ergebnis ersetzt; der Haken wird von diesem Review nun **belegt** vergeben.
Details in Abschnitt F des Gate-Review-Dokuments.

**Lokaler OBS-040-Checkpoint-Commit erstellt** (nach ausdrücklicher Freigabe,
genau einer, auf `feat/einheitliche-triggerarchitektur`): gate-geprüfter
Produktstand, die 115 OBS-040-Tests, die RUN- und Evidence-Unterlagen sowie
das Gate-Review samt Probeskripten. Die bewusst unversionierten Prompt- und
Pipeline-Dateien unter `30_AUSFUEHRUNG/` sind **nicht** aufgenommen worden.
**Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.**

**OBS-040 ist damit vollständig abgeschlossen** — Implementierung, Gate Review
und lokaler Checkpoint.

**Läuft als Nächstes:** OBS-050 – Local Query, Minimal UI & Settings –
Implementierung (frische Session). Readiness im Gate geprüft: **keine
Blocker**; `query/base.py`, `PRAGMA query_only`, `clear()`/`clear_history()`
und `LoggingObservabilityConfig` stehen bereit, `query/local.py`,
`query/service.py`, `ui/logs/**`, die Settings-Einträge nach `CONTRACTS §10.3`
und `apply_config` nach `§10.4` sind der OBS-050-Scope.

Mitzunehmen für spätere Pakete: N-4 (Übergabe des **Managers** an
`DesktopApplication`) und `apply_config` aus `CONTRACTS §10.4` → OBS-050;
N-2, N-3 und die W-3-Lücke des OBS-030-Gates sowie die sieben
nicht-blockierenden Beobachtungen N-1 bis N-7 dieses Gates → OBS-060.

**Abgeschlossen:** OBS-050 – Local Query, Minimal UI & Settings,
Implementierung (2026-08-17, Run `RUN-OBS-050-01_2026-08-17`) →
`OBS-050 IMPLEMENTED – READY FOR REVIEW`.

Entstanden sind die beiden letzten Module der in `ARCH §5.1` eingefrorenen
Struktur — `query/local.py` (`LocalLogProvider`) und `query/service.py`
(`LogQueryService`) — sowie das Paket `ui/logs/**` mit allen sechs
eingefrorenen Modulen. Der Leser öffnet **eigene kurzlebige Verbindungen mit
`PRAGMA query_only = ON`** (nie `mode=ro`), blättert per **Keyset über
`logs.id`** und lädt `raw_json` **nicht** in die Liste. Drei getestete
Eigenschaften tragen O-14: er **legt die Datenbankdatei nie an**, er **wirft
nie**, und er **lässt keine Verbindung offen**.

**Live und Historie sind derselbe Abfragepfad** mit anderen Parametern —
Historie `newest_first=True` mit `next_cursor`, Live alle 250 ms
`newest_first=False` ab dem zuletzt gesehenen Cursor, `LIMIT 500`. **Kein
Ringbuffer, kein Signal je Record** (FD-S1), eigener
`ThreadPoolExecutor(max_workers=1)` statt `CoreBridge`.

Sechster Tab „Logging & Diagnose" mit den neun Einträgen aus
`CONTRACTS §10.3`, dazu „Diagnosehistorie löschen" **am Store über den
Manager** (FD-S4, O-14) und „Logs anzeigen". Die Ownership-Domänen sind
getrennt: Ingress vier eigene Felder, Kompositionswurzel den Handler-Level
(`ARCH §8.7`), Worker Retention/Anzahlgrenze/Datei-Sink auf **seinem eigenen**
Thread; `store_enabled`/`db_path` bleiben `APP_RESTART`. `apply_config` hängt
mit **einer** Zeile an der von `§10.4` genannten Stelle; die harte Regel ist
**gemessen** — eine reine Observability-Änderung erreicht eine Fake-Session
mit durchfallendem `reconfigure` nicht. Readinesspunkt **N-4 ist
geschlossen**.

**Drei reale Befunde, alle behoben:** F-1 `.gitignore` verbarg mit der Regel
`logs/` das komplette neue Paket `ui/logs/` — ohne Korrektur wäre das Ergebnis
dieses Work Packages nicht versionierbar gewesen; F-2 eine synchron
beantwortete Abfrage wurde als „veraltet" verworfen; F-3 ein sofort
zurückkehrendes `shutdown()` führte zu einer Zugriffsverletzung.

Zehn Entscheidungen, alle aus dem bestehenden Freeze auflösbar: **kein
`DECISION REQUIRED`**, **kein neuer Zähler**, **kein neuer Recordtyp** (`§12`
ist die verbindliche Liste), kein neues Konfigfeld, **kein normatives Dokument
verändert**; `core/settings_metadata.py` ist byte-identisch geblieben, weil
`§12.7` es „bewusst rein" hält.

Teststand: 170 neue Tests in fünf Dateien, grün unter `pytest` **und**
`unittest`; volle Suite 1128 passed / 1 vorbestehender, umgebungsbedingter
Fehlschlag (`lefx.interfaces`), dessen Vorbestand gegen einen frisch aus
`91a7b7f` ausgepackten Baum nachgewiesen ist (dort 958 passed / 1 identischer
Fehlschlag; Differenz exakt die 170 neuen Tests). **Kein bestehender Test
geändert.** `git diff --check` leer, kein Cross-Workstream-Diff.
Ende-zu-Ende-Diagnoseskript gegen echten Manager, echten Store, echten
Query-Layer und echtes Qt-Fenster: **12/12 PASS, exit 0**. Evidence:
`40_EVIDENCE/OBS-050/RUN-01_2026-08-17/`.

**Kein Gate-PASS in diesem Run** — laut Work Package erfordert das Gate einen
separaten Review in frischer Session. **Kein Commit, kein Push.**

**Läuft als Nächstes:** OBS-050 – Gate Review (unabhängig, frische Session,
`Prompts/OBS-050_GATE_REVIEW.md`).

**Abgeschlossen:** OBS-050 – Gate Review (unabhängig, frische Session,
2026-08-18) → **`OBS-050 GATE FAIL`**. Der Punkt „OBS-050 – Gate Review"
bleibt deshalb **nicht** abgehakt.

Geprüft wurde der tatsächliche Repositoryzustand — Produktcode, `git diff`/
`git status`/`git diff --check`, eigene Testläufe mit beiden Runnern, ein
Vergleichslauf gegen einen frisch aus `91a7b7f` ausgepackten Baum, das
Diagnoseskript des Runs und zwei eigene Laufzeitproben gegen den echten Stack
(echter Store, echter Provider, echter Service, echtes Qt-`LogPage`) — nicht
die Abschlussberichte. Belastbar und in Ordnung sind der **Query-Layer**
(`PRAGMA query_only = ON`, Keyset über `logs.id`, `raw_json` nicht in der
Liste, nur Platzhalterbindung, Datei wird vom Leser nie angelegt, keine offene
Verbindung, `query()` wirft nie), die **Settings** samt Ownership-Trennung und
Apply-Kette, die **Löschfunktion am Store**, die **Managerlebensdauer**
(`ARCH §6.2(b)`), die **Importrichtung** und „**Logging läuft ohne UI**".
`00_NORMATIV/` und `core/settings_metadata.py` sind byte-identisch zu
`91a7b7f`, kein bestehender Test geändert, volle Suite 1128 passed / 1
vorbestehender Fehlschlag (Baseline 958 passed / 1 identischer Fehlschlag,
Differenz exakt die 170 neuen Tests).

**Blockierend ist ausschließlich das Gate-Kriterium
„Filter/Cursor/Sortierung verhalten sich deterministisch"** — nicht im
Provider, sondern in der Ansicht `ui/logs/log_page.py`:

- **B-1** „Weitere laden" (und das automatische Nachladen am Listenende) hängt
  die umgekehrte, **ältere** Folgeseite unten an; die Zeitspalte springt in der
  Mitte rückwärts. Reproduziert: erste Seite `r7…r11`, danach
  `r7…r11, r2…r6`.
- **B-2** Startet der Live-Modus auf einer **leeren** Ergebnismenge (frische
  Installation, ein Filter, auf den noch nichts passt, jeder Filterwechsel im
  Live-Modus), wird die erste aufsteigende Tail-Antwort im absteigenden Zweig
  verarbeitet: verkehrte Reihenfolge, und `_live_cursor` wird aus der
  **ältesten** statt der jüngsten Zeile gesetzt, sodass der nächste Tail
  dieselben Zeilen als Duplikate anhängt. Reproduziert:
  `r4,r3,r2,r1,r0,r1,r2,r3,r4`. Der Normalfall (nicht leere Ergebnismenge) ist
  korrekt und gegengeprüft.

Dazu W-1 (keine Tests für Reihenfolge über zwei Seiten und für „Live auf
leerem Store" — deshalb sind B-1/B-2 unentdeckt geblieben), W-2
(`UI_ACCEPTANCE.md` A-11 „chronologisch dargestellt" gilt nur für die erste
Seite) und sieben nicht blockierende Beobachtungen N-1 bis N-7. Details:
`40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/GATE_REVIEW.md`.

**Kein Commit erstellt** (Commit nur bei `PASS`); HEAD steht unverändert auf
`91a7b7f`. Kein Push, kein Merge, kein Rebase, kein Tag, kein PR.

**Läuft als Nächstes:** OBS-050 – Korrekturlauf für B-1 und B-2
(einschließlich W-1 und W-2), Umfang **eine** Produktdatei
(`ui/logs/log_page.py`) plus zwei Tests in `tests/test_obs050_ui.py`; danach
ein **erneuter unabhängiger Gate-Review in frischer Session**. Ein
Korrekturlauf vergibt sein eigenes Gate nicht. **OBS-060 darf nicht
beginnen.**

**Abgeschlossen:** OBS-050 – Gate Review (unabhängig, frische Session,
2026-08-18) → **`OBS-050 GATE FAIL`**. Evidence:
`40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/`.

Query-Layer, Settings, Apply-Kette, Ownership-Trennung, Löschfunktion am
Store, Managerlebensdauer, Importrichtung und „Logging läuft ohne UI" sind
belastbar geprüft und in Ordnung. **Nicht erfüllt** war das Gate-Kriterium
„Filter/Cursor/Sortierung verhalten sich deterministisch" — nicht im Provider,
sondern in der Ansicht: **B-1** hängte beim Nachladen eine ältere Seite unten
an, nachdem jede Seite umgedreht worden war, sodass die sichtbare Zeitachse an
jeder Seitengrenze zurücksprang; **B-2** bestimmte die Art einer Antwort aus
`_live_cursor` statt aus der Anfrage, wodurch der Live-Modus nach einem leeren
Ausgangsergebnis verkehrt herum anzeigte und Records doppelte. Dazu **W-1**
(Testlücke) und **W-2** (Evidenzformulierung). Der Haken „OBS-050 – Gate
Review" bleibt daher **ungesetzt**.

**Abgeschlossen:** OBS-050 – Korrekturlauf (2026-08-18, Run
`RUN-OBS-050-02_2026-08-18`) → `OBS-050 CORRECTED – READY FOR RE-REVIEW`.

Beide Blocker wurden vor jeder Änderung mit der unveränderten Gate-Probe
**selbst reproduziert** (`FAILURES: 2`, exit 1) und am Code verifiziert.
**B-1** ist über die vom Gate angebotene Variante 1 behoben: die Umkehrung je
Seite entfällt, die Historie zeigt jede Seite so, wie der Provider sie
geliefert hat (neueste oben), und die ältere Folgeseite gehört damit
folgerichtig nach unten — das automatische Nachladen bleibt wörtlich „am
Listenende". **B-2** ist behoben, indem die Semantik einer Antwort aus der
**Anfrage** folgt: vier benannte Anfragearten, ein einziger Abfragetrichter,
der Anfrage-ID und Art zusammen festhält, eine Verzweigung, die die Art beim
Verarbeiten verbraucht, und ein Live-Cursor, der stets aus der **jüngsten**
gelieferten Zeile stammt. Der fehlerhafte Zweig ist nicht repariert, sondern
entfernt.

Produktseitig ist **ausschließlich** `ui/logs/log_page.py` berührt; Tests in
`tests/test_obs050_ui.py` und `tests/test_obs050_contracts.py`. **W-1** ist mit
neun Regressionstests geschlossen (Reihenfolge über drei Seiten, Live-Start auf
leerem Ergebnis, mehrere Tails, Filter ohne Treffer, Filterwechsel im
Live-Modus, befüllter Normalfall, Antwortzuordnung), **W-2** in
`40_EVIDENCE/OBS-050/RUN-02_2026-08-18/UI_ACCEPTANCE.md`.

Teststand: 170 → **179 OBS-050-Tests**, grün unter `pytest` **und**
`unittest`; OBS-010…050 625 grün; volle Suite 1137 passed / 1 vorbestehender,
umgebungsbedingter Fehlschlag (`lefx.interfaces`), dessen Lage außerhalb des
Diffs erneut nachgemessen ist. Laufzeitproben: `probe_obs050_ordering_fix.py`
8/8 und `probe_obs050_end_to_end.py` 12/12, beide exit 0.
`git diff --check` leer, HEAD unverändert `91a7b7f`, **kein Commit**.

**Läuft als Nächstes:** erneuter unabhängiger **OBS-050 Gate Review** in
frischer Session (`Prompts/OBS-050_GATE_REVIEW.md`). Ein Korrekturlauf vergibt
sein eigenes Gate nicht. **OBS-060 darf nicht beginnen.**

**Abgeschlossen:** OBS-050 – Gate Review II (gezielter Re-Review des
Korrekturlaufs `RUN-OBS-050-02_2026-08-18`, 2026-08-18) →
**`OBS-050 GATE PASS – OBS-060 MAY PROCEED`**. Der Punkt „OBS-050 – Gate
Review" ist damit abgehakt.

Kein vollständiger neuer Gate-Review: die im ersten Gate bereits bestandenen
Bereiche (Query-Layer, Settings, Apply-Kette, Manager, Worker, Löschfunktion,
Managerlebensdauer, Importrichtung, „Logging läuft ohne UI", Tabellenmodell,
Filterleiste, Detailansicht) sind nachweislich unverändert und wurden nicht
erneut auditiert. Der versionierte Anteil ist **stat-identisch** zum ersten
Gate (zehn Dateien, +475/−25); nach Änderungszeitpunkt sind allein
`ui/logs/log_page.py`, `tests/test_obs050_ui.py` und
`tests/test_obs050_contracts.py` berührt. RUN-01-Evidence und die
Gate-FAIL-Evidence sind unangetastet; W-2 ist in einer eigenen RUN-02-Datei
richtiggestellt.

**B-1 geschlossen.** Die gewählte **absteigende** Historiedarstellung ist
normativ gedeckt — `CONTRACTS §5.7` friert `ORDER BY id DESC` und
`AND id < :after_id` ein, `§8` `newest_first=True` als Default, und `§9.3`
verlangt das Nachladen am **Listenende**, das mit absteigender Anzeige genau
der ältere Rand ist. Eine aufsteigende Historieanzeige wird nirgends
gefordert; die entgegengesetzte Erwartung der ersten Gate-Probe ist damit
aufgehoben, **ohne** neue Contract-Entscheidung. Eigene Laufzeitprobe gegen
den echten Stack über **fünf** Seiten: streng absteigend, kein Richtungsbruch
an einer Seitengrenze, keine Duplikate, keine Auslassungen, letzte Seite ohne
Folgecursor; automatisches Nachladen am Listenende über das echte
Scrollbar-Ereignis mit demselben Ergebnis. Der Provider- und Keyset-Cursor ist
unverändert.

**B-2 geschlossen.** Jede Abfrage läuft durch den einen Trichter
`LogPage._issue(kind, …)`, der Anfrage-ID **und** Anfrageart in demselben
Schritt festhält; `_on_page_ready` verzweigt über diese Art und verbraucht sie
dabei. Die Ableitung aus `_live_cursor` existiert nicht mehr, und der Cursor
stammt in beiden Live-Fällen aus der **jüngsten** Zeile. Nachgemessen:
Live-Start auf leerem Store bleibt leer, der erste Tail ist aufsteigend und
duplikatfrei, der Cursor zeigt auf den neuesten Record, Folgetails setzen
dahinter fort, Filter ohne Treffer und Filterwechsel im Live-Modus sind
korrekt, der befüllte Normalfall unverändert — und ein absichtlich vergifteter
`_live_cursor` ändert die Deutung einer Antwort nicht mehr.

Die neun neuen Tests prüfen vollständige Anzeigesequenzen über den echten
`LogQueryController` und schließen damit W-1 an genau der Stelle, an der B-1
durchgerutscht war; das Double `FakeService` ist unverändert. Die Änderung in
`tests/test_obs050_contracts.py` bildet nur den neuen `_issue`-Trichter ab und
**schwächt keine Contract-Anforderung ab** — sie prüft dieselbe Zusicherung an
beiden Enden und ergänzt eine strukturelle Verschärfung.

Teststand dieses Reviews: `-k obs050` 179/179 unter `pytest` **und**
`unittest`; volle Suite 1137 passed / 1 vorbestehender, umgebungsbedingter
Fehlschlag (`lefx.interfaces`, außerhalb des Diffs). Ein in einem von drei
Läufen zusätzlich auftretender Fehlschlag
(`test_ui_widgets.py::TestTranscriptOverlay::test_realtime_replaces_text_and_final_fades`)
ist gezielt geprüft und als **lastabhängig flatterhaft, nicht als Regression**
eingeordnet: in zwei weiteren Vollläufen grün, die Datei allein zweimal grün,
und Testdatei wie `ui/overlay.py` stammen vom 2026-08-14, also außerhalb von
RUN-01 und RUN-02. `git diff --check` leer.

Details: `40_EVIDENCE/OBS-050/GATE-REVIEW-02_2026-08-18_CLAUDE/GATE_REVIEW.md`.
Die nicht blockierenden Beobachtungen N-1 bis N-7 des ersten Gates bleiben für
OBS-060 vorgemerkt.

**Genau ein lokaler Commit** für den gate-geprüften OBS-050-Endstand erstellt
(`feat(observability): complete OBS-050 local log view`); die acht bewusst
unversionierten Prompt- und Pipeline-Einträge unter `30_AUSFUEHRUNG/` sind
**nicht** aufgenommen. **Kein Push, kein Merge, kein Rebase, kein Tag, kein
PR.**

**Läuft als Nächstes:** OBS-060 – V1 Hardening, Evidence & Baseline –
Implementierung (`Prompts/OBS-060_IMPLEMENTIERUNGSAUFTRAG.md`). In diesem Lauf
nicht begonnen.

## Hinweis zum Ablageort dieser Datei

Diese Datei lag vor dem Korrekturlauf im Arbeitsbaum gelöscht vor, während im
nicht versionierten Verzeichnis
`30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` eine **leere** Zweitfassung
liegt. Wiederhergestellt wurde der kanonische Pfad mit den bisherigen
Häkchen; die Zweitfassung wurde nicht angefasst. Ein bewusster Umzug in das
V2-Verzeichnis ist offen (siehe
`runs/RUN-OBS-030-02_2026-08-17/RUN_LOG.md`, Abschnitt 6).
