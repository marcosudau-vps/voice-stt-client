# RUN REPORT

```text
Status         ABGESCHLOSSEN
Run-ID         RUN-OBS-000-01_2026-08-15_CLAUDE
Work Package   OBS-000 -- Plan Freeze & Baseline
Workstream     OBS
Prompt         30_AUSFUEHRUNG/prompts/PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md
Datum          2026-08-15
Modell         Claude Opus 5
```

---

# 1. Abschlussentscheidung

```text
OBS-000 PASS

OBS-010 READY FOR IMPLEMENTATION
OBS-020 READY FOR IMPLEMENTATION

OBS-010 READINESS REVIEW: PASS  (nach drei eingearbeiteten Korrekturen)
```

---

# 2. Ausgangszustand

## 2.1 Arbeitsbereich

Die Struktur unter `ARBEITSDATEIEN/AP_THEMA_LOGGING/` war vollständig
vorbereitet. Abweichend von der Erwartung des Auftrags lagen **alle acht**
erwarteten Analysedateien bereits unter `10_ANALYSE/CLAUDE_VORARBEIT/`, dazu
eine neunte (`00_README_UND_ABSCHLUSSBEWERTUNG.md`). Die in Auftrag §4
beschriebene Kopieraktion war damit gegenstandslos.

`00_NORMATIV/` war leer, wie vorgesehen. Der Gesamtplan trug
`status: DRAFT_REVIEW` und einen ausdrücklichen Vorbehalt: „noch nicht
`FROZEN`, solange die Audits nicht eingearbeitet sind".

## 2.2 Produktcode

```text
voice-stt-client              feat/einheitliche-triggerarchitektur
                              HEAD 178d32bd, 22 nicht committete Eintraege
voice-stt-server              feat/einheitliche-triggerarchitektur
                              HEAD 13c16295, 24 Eintraege
led_controller_respeaker-v3   feat/einheitliche-triggerarchitektur
                              HEAD aa2f14bd, sauber
```

Der Workspace selbst ist **kein** Git-Repository; `ARBEITSDATEIEN/` unterliegt
keiner Versionskontrolle. Details:
`40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md`.

## 2.3 Ausgangslage der Vorarbeit

Die Vorarbeit endete mit `DECISIONS REQUIRED` (Abschlussbewertung) bzw.
`READY AFTER MINOR CORRECTIONS` (adversariales Review). Offen waren nach eigener
Einschätzung: eine blockierende Entscheidung (Paketname), fünf
Bestätigungsfragen, vier einzuarbeitende Defekte, zwei Vereinfachungen und
**eine Informationslücke** (`IMPLEMENTATION_ROADMAP.md` ungeprüft).

---

# 3. Gefundene Quellen

Vollständig in `10_ANALYSE/CLAUDE_VORARBEIT/SOURCE_MANIFEST.md` und
`40_EVIDENCE/OBS-000/EV-01_QUELLEN_UND_HASHES.md`.

| Kategorie | Ergebnis |
|---|---|
| erwartete Pflichtdateien | **9 von 9** vorhanden, davon eine über die Erwartung hinaus |
| fehlende Pflichtdatei | **keine** |
| Integrität gegen `90_ARCHIV/analyse_code_integration.zip` | **byteidentisch**, alle neun |
| mehrfach vorhandene Dateien | acht, **alle byteidentisch** — keine Auswahlentscheidung nötig |
| ursprünglicher Ablageort | `analyse_code_integration/` existiert nur noch als ZIP im Archiv |
| kopiert / verschoben / gelöscht | **nichts** — die Ablage war bereits korrekt |

Zusätzlich gelesen: die drei Grundlagen unter `00_GRUNDLAGEN/`, der vollständige
Gesamtplan mit allen 15 Work-Package-Dateien, `START_HIER.md`, `AGENTS.md` und
— als ausdrücklich unverbindliche Ideenquelle — `ErsterEntwurf_Logging.md`.
Aus letzterem wurde **keine** Aussage übernommen, die eine neuere Analyse
überschreibt.

---

# 4. Durchgeführte Arbeiten

1. Arbeitsregeln, Gesamtplan, alle Work Packages und alle Grundlagen gelesen.
2. Quellenlage über SHA-256 gesichert, Varianten verglichen, Manifest erstellt.
3. **Dreizehn gezielte Codeprüfungen** am realen Client durchgeführt — nur dort,
   wo eine Freeze-Entscheidung sonst nicht belastbar gewesen wäre (`EV-02`).
   Zwei davon haben die Vorarbeit **korrigiert**.
4. Die letzte Informationslücke (`W-16`) geschlossen.
5. Alle Entscheidungen geschlossen, alle Widersprüche aufgelöst.
6. Drei normative Freeze-Artefakte angelegt.
7. Gesamtplan, Work-Package-Index, Freeze-Checkliste, Traceability-Matrix und
   acht Work-Package-Dateien aktualisiert.
8. Vier Evidence-Dateien erstellt.
9. Adversarialen Readiness-Review von OBS-010 durchgeführt; drei gefundene
   Lücken sofort in die Verträge eingearbeitet.
10. `LOG_VERLAUF.md` um einen Meilensteineintrag ergänzt.

**Keine neue breite Analyse begonnen.** Keine Zeile Produktcode, Testcode oder
Produktconfig verändert.

---

# 5. Erzeugte und geänderte Dateien

## Neu

| Datei | Zweck |
|---|---|
| `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md` | Invarianten, Endzustand, Komponenten, Nebenläufigkeit, Failure Domain, Hot-Path-Regeln, Zukunftsgrenzen |
| `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md` | CanonicalRecord, Normalizer, Redaction, SQLite, Query, UI, Konfiguration, Hookliste |
| `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` | 39 geschlossene Entscheidungen, Widerspruchsregister, WP-Grenzkorrektur |
| `10_ANALYSE/CLAUDE_VORARBEIT/SOURCE_MANIFEST.md` | Herkunft, Hashes, Autoritätseinstufung |
| `40_EVIDENCE/OBS-000/EV-01_QUELLEN_UND_HASHES.md` | Prüfsummen und Archivvergleich |
| `40_EVIDENCE/OBS-000/EV-02_GEZIELTE_CODEPRUEFUNGEN.md` | 13 Codeprüfungen mit Kommandos und Ausgaben |
| `40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md` | Git-Baseline der drei Repositories, Verbotseinhaltung |
| `40_EVIDENCE/OBS-000/EV-04_PLANKONSISTENZ.md` | Konsistenzcheck Planung ↔ Freeze |

## Geändert

| Datei | Änderung |
|---|---|
| `00_NORMATIV/README.md` | Freeze-Stand, Autoritätsreihenfolge, Änderungsregel |
| `20_PLANUNG/…/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md` | Status `FROZEN_BASELINE`; Autoritätsmodell; Invariante O-14; WP-Titel; OBS-000 abgehakt; Korrekturen in OBS-020/030/040/050/060/120; Startreihenfolge; Vorbehalt ersetzt |
| `20_PLANUNG/…/01_WORKPACKAGE_INDEX.md` | Statuswerte, Abhängigkeiten, Abbildung 14 → 6 |
| `20_PLANUNG/…/02_OBS000_FREEZE_CHECKLIST.md` | vollständig abgehakt, je Punkt mit Fundstelle |
| `20_PLANUNG/…/03_TRACEABILITY_MATRIX.md` | O-14 ergänzt, Vertragsspalte, zwölf neue Nachweispflichten |
| `20_PLANUNG/…/README.md` | Startreihenfolge, Freeze-Stand, Hinweis zur Doppelablage |
| `workpackages/WP-OBS-010` | vollständig ausgearbeitet, `READY` |
| `workpackages/WP-OBS-020` | vollständig ausgearbeitet, `READY`, Titelkorrektur |
| `workpackages/WP-OBS-030` | Titelkorrektur, D-2/D-4/AR-5/AR-6 eingearbeitet |
| `workpackages/WP-OBS-040` | Hookvorgaben, Verbote, N-07 als Hauptnachweis |
| `workpackages/WP-OBS-050` | Ringbufferwegfall, Abhängigkeitskorrektur, Configauflage |
| `workpackages/WP-OBS-060` | Isolationsnachweis, acht Mutationschecks, manuelle Abnahme |
| `workpackages/WP-OBS-110` | Capability-Übergabe, `sensitive`-Auflage |
| `workpackages/WP-OBS-120` | Provider-Reihenfolge, `ProviderCapabilities`, HTTP-Auflage |
| `workpackages/WP-OBS-140` | Klarstellung, dass die `lefx.*`-Regel schon in V1 greift |
| `ARBEITSDATEIEN/LOG_VERLAUF.md` | ein Meilensteineintrag |

---

# 6. Geschlossene Entscheidungen

Vollständig mit Begründung in `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md`.
Übersicht:

| Gruppe | Anzahl | Kernpunkte |
|---|---:|---|
| blockierend | 1 | Paketname `core/observability/` |
| Datenmodell | 12 | CanonicalRecord, `transcription_id`, `activation_id` diagnostisch, Dedupe-Schlüssel, Enum-Versionierung, `unfreeze`, 64-KiB-Grenze |
| Defaults und Betrieb | 9 | Transkript `false`, Raw `true` außer `performance`, Retention 14/200.000, nur JSONL, `hello`-Whitelist, stiller Fatalfehler, `client.log` bleibt, Level-Default |
| Abweichungen von benannten Anforderungen | 4 | Ringbuffer entfällt, eine Queue, kein `ProviderCapabilities`, Löschfunktion neu |
| aus diesem Run | 8 | Priorität `not replayed`, `LOGGER_CHANNEL_MAP`, Protokollfehlerhook, Managerlebensdauer, `deduplicated`, plus die drei aus dem Readiness-Review |
| nach Teil B verschoben | 5 | Capability-Modell, Providerreihenfolge, HTTP-Fähigkeit, `host`/Multi-Host, LedAdapter |

**Vier davon ändern eine ausdrücklich benannte Anforderung der Entwürfe** und
sind in `DECISIONS §4` zusammengestellt — jeweils mit den Rückdrehkosten, damit
sie ohne erneutes Nachlesen überprüfbar sind. Der sichtbarste:

> **Der Memory-Ringbuffer aus Zielbild §17 und Abgrenzung §3.11/§3.12 entfällt.**
> Die geforderte *Live-Ansicht* bleibt vollständig erfüllt; nur die *Bauform*
> ändert sich zu einer tailenden Store-Abfrage. Nebengewinn: eine Abstraktion
> weniger, die UI wird vom Worker entkoppelt, und bei totem Worker zeigt die
> Ansicht ehrlich keine neuen Zeilen, statt Daten anzuzeigen, die nie
> gespeichert wurden.

---

# 7. Verbliebene Entscheidungen

```text
Blockierende offene Entscheidungen:   KEINE
Offene Widersprueche:                 KEINE
Offene Informationsluecken:           KEINE
```

Fünf Punkte sind **bewusst** nach Teil B verschoben (`DECISIONS §6`). Sie
berühren keinen V1-Codepfad; V1 trifft jeweils die dort benannte Vorkehrung.
Sie sind damit **nicht** offen im Sinne des Freeze-Kriteriums.

---

# 8. Widersprüche und ihre Auflösung

19 Widersprüche, vollständig im Register `DECISIONS §7`. Die fünf wichtigsten:

| # | Widerspruch | Auflösung |
|---|---|---|
| W-3 | Zielbild und Abgrenzung fordern einen Ringbuffer | gestrichen, Funktion bleibt erfüllt — als Abweichung eigens ausgewiesen |
| W-13 | `mode=ro` für Leser ↔ WAL erlaubt das nicht allgemein | `PRAGMA query_only = ON` |
| W-16 | Die Roadmap galt als ungeprüft | **geprüft, kein Widerspruch** (`EV-02 / C-13`) |
| W-17 *(neu)* | Die Wasserstandsregel sollte replayte Records verwerfen, stufte sie aber als HIGH ein | `not replayed` in die Prioritätsregel |
| W-18 *(neu)* | Zwei Nummernkreise für dieselbe Arbeit | verbindliche Abbildung 14 → 6 |

Drei Widersprüche (W-17, W-18, W-19) wurden **in diesem Run neu gefunden**.

---

# 9. Gezielte Codeprüfungen

Dreizehn, vollständig in `EV-02`. Elf haben die Vorarbeit **bestätigt**, zwei
haben sie **korrigiert**:

```text
C-03  Das Verbot des Controller-Hooks ist schaerfer als beschrieben.
      EventStreamTransport._dispatch faengt eine durchschlagende Ausnahme mit
      except BaseException, ruft reject_event(result) und wirft weiter.
      Ein werfender Beobachter wuerde das Event also AKTIV VERWERFEN.
      -> except Exception im Beobachterwrapper ist Pflicht, nicht Vorsicht.
      -> BaseException darf dort nicht gefangen werden (CancelledError).

C-05  Defekt D-1 ist schwerer als beschrieben.
      EventProtocolResult.payload ist rekursiv eingefroren in DREI Typen:
      MappingProxyType, tuple UND frozenset. Das adversariale Review nennt
      nur die ersten beiden. json.dumps kennt keinen davon.
      -> unfreeze() muss alle drei behandeln.
      -> D-1 bleibt damit auch ein Sicherheitsbefund.
```

Ein Nebenbefund mit Zukunftswirkung: Der Client hat **keinen HTTP-Client**.
Für OBS-120 ist das eine benannte Auflage (`FD-B3`).

---

# 10. Tests und Evidence

OBS-000 ist ein Architekturgate. Es wurden **keine** Tests ausgeführt und es
**können** keine ausgeführt werden — es existiert noch kein Logging-Code.

Die Evidence besteht aus nachprüfbaren Erhebungen:

| Datei | Inhalt |
|---|---|
| `EV-01` | SHA-256 aller Quellen, Archivvergleich |
| `EV-02` | 13 Codeprüfungen mit Kommando, Ausgabe und Bewertung |
| `EV-03` | Git-Baseline der drei Repositories, Einhaltung der Verbote |
| `EV-04` | Konsistenzcheck: kein gestrichener Mechanismus ohne Streichungsvermerk |

---

# 11. Blocker

**Keine.**

Ein Punkt ist als **Vorbedingung von OBS-010** festgehalten, nicht als Blocker
dieses Gates:

```text
RISIKO R-3   Der Arbeitsbaum von voice-stt-client traegt 22 nicht committete
             Aenderungen, darunter alle Dateien, auf deren Zeilennummern die
             Analysen verweisen (controller.py, stt_session.py, config.py,
             settings_metadata.py, ui/application.py, ui/settings_dialog.py).

             EV-02 / C-01 belegt ueber die Zeilenzahlen, dass die Vorarbeit
             gegen GENAU diesen Baum entstanden ist -- die Verweise sind also
             gueltig, aber nur solange er unveraendert bleibt.

             AUFLAGE  Vor Beginn von OBS-010 ist der Zustand festzuschreiben,
                      durch einen Commit oder durch eine ausdrueckliche
                      Bestaetigung, dass der Baum unveraendert bleibt.
                      OBS-000 darf nicht committen -- die Auflage gehoert
                      deshalb an OBS-010.

             Die inhaltliche Gueltigkeit des Freezes ist NICHT betroffen:
             kein eingefrorener Vertrag haengt an einer Zeilennummer.
```

Zwei weitere, unkritische Beobachtungen zur Ablage stehen in `EV-04 §4`: die
veraltete Plankopie unter `05_DRAFTS_UNGEPRUEFT/` und die doppelte
Entwurfsablage unter `20_PLANUNG/`.

---

# 12. Gate-Empfehlung

```text
G-OBS-000 PASS
```

**Begründung.** Das Freeze-Kriterium lautet: `PASS`, wenn kein Coding-Agent mehr
eine grundlegende Logging-Architekturentscheidung treffen muss. Alle 22 Punkte
der Freeze-Checkliste sind geschlossen, dazu acht in diesem Run hinzugekommene.
19 Widersprüche sind aufgelöst, keiner offen. Die letzte Informationslücke ist
geprüft und geschlossen. Die normativen Artefakte enthalten die vollständige
Endarchitektur; Teil A ist als erste Implementierungsstufe klar abgegrenzt, und
keine offene Architekturentscheidung ist als scheinbar final versteckt — die
vier Abweichungen von benannten Anforderungen und die fünf nach Teil B
verschobenen Punkte stehen jeweils in einem eigenen, überschriebenen Abschnitt.

---

# 13. OBS-010 Readiness Review

Durchgeführt gemäß Auftrag §14, adversarial.

| Prüffrage | Ergebnis |
|---|---|
| Scope eindeutig? | **ja.** Acht Dateien namentlich, jede mit Vertragsverweis. |
| Verborgene Architekturentscheidung? | **drei gefunden** — siehe unten. Nach Einarbeitung: keine. |
| Dateien/Komponenten konkret genug? | **ja.** Feldliste, Signaturen und DDL stehen im Vertrag, nicht im Paket. |
| Positive Tests? | **ja**, neun benannte Fälle. |
| Negative Tests? | **ja**, sieben benannte Fälle. |
| Mutations-/False-Positive-Proofs bei kritischen Contracts? | **war eine Lücke.** Alle acht Mutationschecks lagen in OBS-060 — ein grüner Redaction-Test in OBS-010, der auch ohne Redaction grün bliebe, wäre wertlos gewesen. **Zwei Checks vorgezogen.** |
| Spätere Admin-/History-/LED-Erweiterung verbaut? | **nein.** `ProviderStatus` ist eine frozen dataclass mit Defaults (Capabilities additiv), `QueryFilter` trägt bereits alle Serverfelder, der Cursor ist opak, `producer_kind="led"` existiert, `AUTH_REQUIRED` existiert. |

## Die drei gefundenen Lücken – alle geschlossen

```text
FD-R6  scope war fuer producer_kind "led" und "other" UNDEFINIERT.
       Die Regel nannte nur Server und Client. Ein lefx.*-Record ohne
       Session haette keinen definierten scope gehabt.
       -> "instance".  Vertrag: CONTRACTS §1.3

FD-R7  component eines CONTROLFRAMES war undefiniert.
       Die Regel "Namensraumpraefix von type" ist nur fuer Serverevents
       formuliert; auf "client.eventstream.gap" angewandt ergaebe sie
       "client" -- als Filterwert nutzlos.
       -> fest "eventstream".  Vertrag: CONTRACTS §3.2

FD-R8  Die Signatur from_log_record(..., session_id, generation) liess offen,
       WER diese Werte liefert. Die naheliegende Antwort -- der Handler liest
       den aktuellen Sessionzustand -- waere FALSCH: der Handler laeuft auf
       sechs Threads, darunter dem PortAudio-Callbackthread und dem
       Qt-Mainloop. Eine solche Abfrage waere nicht thread-sicher oder
       braeuchte ein Lock im Hot Path -- und waere eine Kopplung des Loggings
       an die Runtime, also ein Verstoss gegen O-01.
       -> ausschliesslich aus record.__dict__ (bestehender extra-Vertrag),
          sonst None. Der Handler haelt KEINE Referenz auf Controller,
          Session oder Coordinator.
       -> Das ist zugleich der inhaltliche Grund, warum es die strukturierte
          Client-Observation-API ueberhaupt gibt.
       Vertrag: CONTRACTS §3.1
```

```text
OBS-010 READINESS REVIEW: PASS
```

**OBS-010 wurde nicht implementiert.**

---

# 14. Nächster empfohlener Schritt

```text
1. Die vier Abweichungen aus DECISIONS §4 zur Kenntnis nehmen -- insbesondere
   den Wegfall des Ringbuffers, weil er eine ausdruecklich benannte
   Anforderung des Zielbilds beruehrt. Ein Veto ist jederzeit ueber
   DECISION REQUIRED moeglich; die Rueckdrehkosten stehen dort.

2. Vorbedingung von OBS-010 erfuellen: den Arbeitsbaum von voice-stt-client
   festschreiben (Commit oder Bestaetigung).

3. OBS-010 starten.
   Es ist nach der Modellstrategie des Plans ein gut geeignetes Paket fuer ein
   guenstigeres Modell: die Architektur ist vollstaendig entschieden, die
   Feldliste steht Feld fuer Feld, und das Paket legt ausschliesslich neue
   Dateien an. Der einzige Punkt, der aufmerksames Arbeiten verlangt, ist der
   Test N-01 (unfreeze gegen einen echten eingefrorenen Payload).

4. OBS-020 kann unmittelbar folgen.
   OBS-040 und OBS-050 sind spaeter parallelisierbar.
```

---

# 15. Einhaltung der Arbeitsregeln

| Regel aus `PRM-OBS-000-01 §12` | Status |
|---|---|
| keine Produktcodeänderung | eingehalten |
| keine Produkt-Testcodeänderung | eingehalten |
| keine aktive Produktconfig geändert | eingehalten |
| keine Triggerarchitektur repariert | eingehalten |
| keine Logging-Implementierung begonnen | eingehalten |
| kein Commit / Push / Merge / Rebase / Tag / PR | eingehalten |
| die drei Produktrepositories nur lesend | eingehalten |

Sämtliche Schreibvorgänge liegen unterhalb von
`ARBEITSDATEIEN/AP_THEMA_LOGGING/` sowie in `ARBEITSDATEIEN/LOG_VERLAUF.md`.
