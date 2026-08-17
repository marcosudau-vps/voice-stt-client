Führe den zweiten unabhängigen Gate-Review für OBS-030 vollständig durch.

Arbeitsbereich:

P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur

Verbindlicher Gate-Auftrag:

ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\Prompts\OBS-030_GATE_REVIEW.md

Dies ist ein unabhängiger Re-Review nach:

1. ursprünglicher OBS-030-Implementierung,
2. erstem Gate-FAIL,
3. Korrekturlauf RUN-OBS-030-02,
4. anschließendem eng begrenzten Cleanup zweier nicht autorisierter Änderungen.

Prüfe ausschließlich den tatsächlichen Repositoryzustand, Code, Diff, Tests und Evidence.

Verlasse dich NICHT auf:
- den ursprünglichen Abschlussbericht,
- den Korrekturbericht,
- die Stellungnahme des Implementierungsagents,
- den Cleanup-Bericht.

Diese Unterlagen dürfen als Hinweise dienen, ersetzen aber keine eigene Prüfung.

## Prüfgrundlage

Lies die vorgeschriebene Pflichtlektüre und insbesondere:

- LOGGING_ARCHITEKTUR_FREEZE_V1.md
- LOGGING_CONTRACTS_FREEZE_V1.md
- LOGGING_DECISIONS_FREEZE_V1.md
- WP-OBS-030
- ursprünglichen OBS-030-Implementierungsauftrag
- ersten Gate-Review mit FAIL
- RUN-OBS-030-02 und dessen Evidence
- den abschließenden Cleanup-Nachweis

Prüfe den gesamten OBS-030-Endstand seit dem letzten bereits freigegebenen lokalen Commit, nicht nur den letzten Cleanup-Diff.

---

# A. Ursprüngliche Blocker erneut unabhängig prüfen

## B-1 – Worker-Fehlerisolation

Verifiziere am tatsächlichen Code und durch eigene Fault-Injection:

- unerwartete Exceptions innerhalb der Worker-Schleife beenden den Worker nicht still,
- `worker_errors` reagiert korrekt,
- interne Fehler nutzen ausschließlich den vorgesehenen isolierten/ratenbegrenzten Fehlerpfad,
- kein ungefilterter `threading`-Traceback,
- endgültiger Worker-Ausfall führt zu `FAILED_WORKER`,
- nach endgültigem Ausfall liefert der Ingress keine scheinbar erfolgreichen `True`-Submits mehr,
- bereits eingereihte Queue-Reste werden korrekt behandelt,
- alle realistischen Exception-Pfade einschließlich der früher beanstandeten Stellen sind erfasst.

Prüfe außerdem ausdrücklich die gewählte Schwelle für einen endgültigen Worker-Ausfall nach mehreren aufeinanderfolgenden Fehlern.

Falls beispielsweise eine Schwelle von fünf Fehlern implementiert ist:
- nachweisen, dass sie normativ gedeckt ist,
- oder als nicht autorisierte neue Semantik beanstanden.

Nicht allein deshalb akzeptieren, weil Tests dafür existieren.

## B-2 – Evidence-Konsistenz

Prüfe:

- stimmen aktuelle RUN-02-Evidence, Tests und Produktcode tatsächlich überein?
- sind frühere falsche Aussagen eindeutig als historisch widerlegt erkennbar?
- wurden keine Gate-FAIL-Befunde gelöscht oder nachträglich verschleiert?

## B-3 – P-8

Prüfe die Pfadgrenzen selbst gegen den real aufgelösten Benutzerprofilpfad.

Mindestens:

- gültiger Profilpfad,
- absoluter Fremdpfad,
- `..`-Escape,
- Fremdprofil,
- Windows-Laufwerkspfad,
- UNC-Pfad,
- relevante Separator-/Normalisierungsfälle.

Prüfe sowohl Config-Grenze als auch tatsächliche Pfadauflösung im produktiven Managerpfad.

---

# B. W-1 bis W-7 erneut prüfen

Prüfe sämtliche W-1 bis W-7 aus dem ersten Gate-Review unabhängig.

Besonders:

## W-1 – Store-/Sink-Isolation

Bei defektem SQLite-Store muss anhand der normativen Vorgaben geklärt und praktisch geprüft werden, ob ein weiterhin funktionsfähiger JSONL-Sink unabhängig weiterarbeiten muss.

Keine bloße Übernahme der RUN-02-Interpretation.

## W-2 – `logging.retention_pressure`

Prüfe Feld für Feld, ob der erzeugte Record den normativen Vorgaben entspricht und nur an der vorgesehenen Flanke entsteht.

## W-3

Prüfe die dokumentierte Lücke zu nicht zugeordneten Verwürfen.

Nicht eigenmächtig einen neuen Counter verlangen oder akzeptieren.

## W-4 bis W-7

Alle ursprünglichen Befunde erneut gegen Code, Runtime-Verhalten und Normgrundlage prüfen.

---

# C. Besondere Entscheidungsfrage: ARCH §8.3 „nur verwerfen und zählen“

Der vorherige Korrekturlauf hatte dafür eigenmächtig `dropped_failed` eingeführt.

Diese Erweiterung wurde vor diesem Review wieder vollständig entfernt.

Prüfe nun ausschließlich anhand des bereits eingefrorenen Vertrags:

ARCH §8.3 verlangt nach endgültigem Worker-Ausfall:

„nur verwerfen und zählen“

ARCH §7.3 und CONTRACTS §11.2 enthalten gleichzeitig einen ausdrücklich eingefrorenen Zählersatz ohne eigenen `dropped_failed`-Counter.

Entscheide unabhängig:

### Variante 1
Der bestehende Contract ist eindeutig so auszulegen, dass die aktuelle Implementierung ohne neuen Counter vollständig normkonform ist.

Dann begründe diese Auslegung präzise anhand der bestehenden Normtexte.

### Variante 2
Die Norm verlangt zwingend die Zählung jedes nach `FAILED_WORKER` neu abgewiesenen Records, aber keiner der eingefrorenen Counter bildet diese Ursache korrekt ab.

Dann liegt ein echter Contract-Widerspruch bzw. DECISION-REQUIRED-Bedarf vor.

In diesem Fall:

- KEIN Gate PASS erzwingen,
- KEINEN neuen Counter selbst implementieren,
- KEINE Freeze-Datei selbst erweitern,
- OBS-030 als BLOCKED bzw. entscheidungsbedürftig ausweisen,
- die kleinstmögliche benötigte Architekturentscheidung exakt formulieren.

Der Reviewer darf nicht durch eine eigene Contract-Erweiterung den Konflikt selbst auflösen.

---

# D. Freeze-Integrität

Prüfe, dass der im Korrekturlauf eingetragene `DR-OBS-030-01` tatsächlich vollständig aus `LOGGING_DECISIONS_FREEZE_V1.md` entfernt wurde und keine andere normative Freeze-Datei unautorisiert verändert wurde.

Vergleiche die normative Grundlage soweit rekonstruierbar mit dem Zustand vor RUN-OBS-030-02.

Offene Entscheidungen dürfen in Run-/Evidence-Unterlagen dokumentiert sein, aber nicht bereits als beschlossene Norm ausgegeben werden.

---

# E. Historische RUN-01-Evidence

Drei RUN-01-Dateien wurden nachträglich um klar markierte Korrekturvermerke ergänzt.

Prüfe unabhängig:

- ursprünglicher Text tatsächlich unverändert?
- Nachträge eindeutig abgesetzt und datiert?
- keine ursprüngliche Aussage gelöscht oder ersetzt?
- Gate-FAIL-Historie vollständig erhalten?
- Rekonstruierbarkeit ausreichend?

Da keine eindeutige normative Evidence-Regel für solche Nachträge existiert, unterscheide zwischen:

- tatsächlicher Manipulation/Verschleierung,
- transparentem Korrekturvermerk,
- rein organisatorischem Verbesserungspunkt.

Nur ein materielles Evidence-Problem darf daraus einen Gate-Blocker machen.

---

# F. Checkliste und Steuerungsdateien

Prüfe:

- `LOGGING_V1_CHECKLISTE.md` vollständig und konsistent,
- frühere Häkchen erhalten,
- OBS-030 Gate noch nicht vorzeitig abgehakt,
- CURRENT_STATE korrekt,
- LOG_VERLAUF append-only,
- keine unzulässige Rekonstruktion oder Zweitfassung als kanonischer Stand übernommen.

---

# G. Eigene Tests

Führe unabhängig mindestens aus:

- komplette OBS-030-Tests,
- OBS-010 + OBS-020 + OBS-030,
- vollständige Client-Suite,
- Worker-Fault-Injection,
- Backpressure/Recovery,
- Shutdown mit Queue-Resten,
- Store-Ausfall,
- Sink-Ausfall,
- Store-/Sink-Isolation,
- SQLite-Dedupe,
- Persistenz über Neustart,
- Retention,
- Migration,
- P-8,
- Retention-Pressure,
- `git diff --check`,
- `git status --short`,
- vollständige Scope-Prüfung des Diffs.

Bekannte vorbestehende Testfehler nur dann akzeptieren, wenn ihr Vorbestand und ihre Unabhängigkeit vom OBS-030-Diff tatsächlich erneut nachgewiesen werden.

---

# Gate-Entscheidung

Es gibt nur drei zulässige Ergebnisse:

## PASS

`OBS-030 GATE PASS – OBS-040 MAY PROCEED`

Nur wenn:

- alle ursprünglichen Blocker geschlossen sind,
- keine neue nicht autorisierte Contract-Änderung vorhanden ist,
- die offene §8.3-Zählfrage entweder eindeutig aus dem bestehenden Freeze lösbar ist oder nachweislich keinen OBS-030-Blocker darstellt,
- Scope, Tests und Evidence belastbar sind.

## FAIL

Wenn eine konkrete implementierte Anforderung weiterhin falsch ist.

## BLOCKED / DECISION REQUIRED

Wenn die Implementierung technisch korrekt sein kann, aber der eingefrorene Contract eine für die Abnahme notwendige Entscheidung nicht eindeutig zulässt.

In diesem Fall keine eigene Architekturentscheidung treffen.

---

# Lokaler Commit ausschließlich bei PASS

Bei FAIL oder BLOCKED:

- keinen Commit erstellen,
- OBS-040 nicht freigeben,
- konkrete verbleibende Blocker bzw. den exakten Entscheidungsbedarf dokumentieren.

Nur bei eindeutigem GATE PASS:

1. alle Gate-/Evidence-/Steuerungsaktualisierungen abschließen,
2. OBS-030 Gate in der zentralen Checkliste abhaken,
3. vollständigen `git status` prüfen,
4. den gesamten zu OBS-030 gehörenden Commit-Umfang kontrollieren,
5. fachfremde oder unklare Dateien ausschließen,
6. genau einen lokalen Commit für den vollständig geprüften OBS-030-Endstand erstellen.

Commit-Message:

feat(observability): complete OBS-030 persistence and worker

Danach ausgeben:

- Gate-Ergebnis,
- Entscheidung/Auslegung zu ARCH §8.3 „verwerfen und zählen“,
- B-1/B-2/B-3 Status,
- W-1 bis W-7 Status,
- finaler Teststand,
- Commit-Hash bei PASS,
- `git status --short`,
- ausdrücklich: `OBS-040 MAY PROCEED` oder nicht.

Kein Push.
Kein Merge.
Kein Rebase.
Kein Tag.
Kein PR.
Keine OBS-040-Implementierung beginnen.
