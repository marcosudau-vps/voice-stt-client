Führe einen gezielten Korrekturlauf für OBS-030 durch.

Arbeitsbereich:
P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur

Ausgangspunkt ist der fehlgeschlagene unabhängige Gate-Review von OBS-030.

Lies zuerst vollständig:

1. die für OBS-030 maßgeblichen normativen Freeze-Dokumente,
2. das Work Package OBS-030,
3. den ursprünglichen OBS-030-Implementierungsauftrag,
4. den tatsächlichen aktuellen Produktcode und die OBS-030-Tests,
5. insbesondere den vollständigen Gate-Review:

ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\40_EVIDENCE\OBS-030\GATE-REVIEW-01_2026-08-17_CLAUDE\GATE_REVIEW.md

Verlasse dich nicht nur auf die Zusammenfassungen oder den vorherigen Abschlussbericht.

## Ziel

Behebe die im Gate-Review nachgewiesenen OBS-030-Mängel vollständig und bringe OBS-030 erneut in einen Zustand:

OBS-030 IMPLEMENTED – READY FOR REVIEW

Es handelt sich um einen Korrekturlauf, nicht um einen neuen Architekturentwurf und nicht um die Implementierung von OBS-040 oder späteren Work Packages.

## Verbindlich zu beheben

### B-1 – Worker-Fehlerisolation

Behebe die fehlende Fehlerisolation auf Schleifenebene in `core/observability/worker.py`.

Insbesondere muss sichergestellt sein:

- Eine unerwartete `Exception` innerhalb eines Worker-Durchlaufs darf den Worker-Thread nicht still beenden.
- Der Fehler muss über den vorgesehenen Observability-internen Fehlerpfad behandelt werden.
- `worker_errors` muss korrekt erhöht werden.
- Der Health-State muss entsprechend den normativen Vorgaben auf `FAILED_WORKER` bzw. den dort tatsächlich vorgeschriebenen Zustand wechseln.
- Producer dürfen nach einem irreparabel ausgefallenen Worker nicht weiter Records scheinbar erfolgreich akzeptieren, die anschließend dauerhaft stranden.
- Kein ungefilterter `threading`-Traceback darf den vorgesehenen G-2/G-4-Notausgang umgehen.
- Alle realen Exception-Pfade innerhalb der Worker-Schleife sind einzubeziehen; insbesondere auch Fehler außerhalb bereits vorhandener enger `try`-Blöcke wie der im Gate-Review genannte Pfad um `dataclasses.replace(...)`.

Implementiere dafür gezielte Fehler-/Fault-Injection-Tests. Ein Test muss nachweisen, dass eine künstlich ausgelöste unerwartete Worker-Ausnahme weder unbemerkt bleibt noch Records weiterhin scheinbar erfolgreich angenommen werden.

### B-2 – Evidence-Konsistenz

Die bestehende OBS-030-Evidence behauptet Verhalten, das der geprüfte Code nicht geliefert hat.

Nach der technischen Korrektur:

- alle betroffenen Aussagen in `CONTRACT_COVERAGE.md`, `TEST_RESULTS.md`, `RESULT.md`, `RUN_LOG.md` und sonstiger OBS-030-Evidence gegen den tatsächlichen Code und die tatsächlich ausgeführten Tests prüfen,
- falsche Aussagen korrigieren,
- keine bestehende Gate-FAIL-Historie löschen oder umschreiben,
- den Korrekturlauf als neuen Run dokumentieren.

Die historische Evidence des fehlgeschlagenen Gate-Reviews bleibt erhalten.

### B-3 – P-8 / Pfadgrenzen

Implementiere die in `CONTRACTS §4.3 P-8` vorgeschriebene Pfadbeschränkung vollständig.

Insbesondere:

- `db_path`
- `file_sink_dir`

dürfen keinen aufgelösten Pfad außerhalb des Benutzerprofils akzeptieren.

Die Prüfung muss gegen den tatsächlich aufgelösten/normalisierten Pfad erfolgen und darf nicht durch `..`, absolute Pfade oder andere triviale Pfadformen umgangen werden.

Füge positive und negative Tests hinzu, einschließlich mindestens:

- gültiger Pfad innerhalb des Benutzerprofils,
- absoluter Pfad außerhalb,
- `..`-Escape,
- relevante Windows-Pfadfälle.

Keine unnötige Settings-/UI-Implementierung aus OBS-050 vorziehen.

## W-1 bis W-7 vollständig entscheiden

Lies die vollständigen W-1 bis W-7 aus `GATE_REVIEW.md`.

Für jeden einzelnen Punkt:

1. gegen die normativen Freeze-Dokumente und WP-OBS-030 prüfen,
2. feststellen, ob er
   - ein verpflichtender OBS-030-Fehler,
   - eine zulässige Implementierungsentscheidung,
   - oder eindeutig Scope eines späteren Work Packages ist,
3. diese Entscheidung mit konkreter Contract-/Architecture-Referenz dokumentieren.

Wenn ein Punkt innerhalb OBS-030 normativ erforderlich ist:
→ jetzt korrigieren und testen.

Wenn er ausdrücklich einem späteren Work Package gehört oder nach den eingefrorenen Contracts kein Fehler ist:
→ nicht vorsorglich implementieren; stattdessen sauber dokumentieren.

Besonders sorgfältig prüfen:

- W-1: Verhalten des JSONL-Sinks bei defektem SQLite-Store. Prüfe, ob Store und Sink laut Contracts unabhängig degradieren müssen oder ob das aktuelle Verhalten zulässig ist.
- W-2: `logging.retention_pressure`. Prüfe, ob dies nach den normativen Contracts als kanonischer interner Record erzeugt werden muss und nicht lediglich als stderr-Diagnose.

W-3 bis W-7 dürfen nicht ignoriert werden, nur weil sie im Kurzbericht nicht vollständig wiedergegeben wurden. Maßgeblich ist das vollständige Gate-Review-Dokument.

## Scope-Schutz

Keine Implementierung von OBS-040 oder OBS-050 vorziehen.

Änderungen an bestehenden Dateien außerhalb des unmittelbaren OBS-030-Scopes nur dann, wenn sie für die nachgewiesene OBS-030-Korrektur zwingend erforderlich sind. Solche Änderungen explizit begründen.

Kein Refactoring ohne konkreten Bezug zu einem Gate-Befund.

## Tests

Mindestens:

- alle neuen gezielten Korrekturtests,
- komplette OBS-030-Testsuite,
- vollständige Client-Testsuite,
- unabhängige Fault-Injection für Worker-Ausfall,
- Pfadgrenzen P-8,
- Store-/Sink-Fehlerisolation entsprechend der Entscheidung zu W-1,
- Retention-Pressure entsprechend der Entscheidung zu W-2,
- Backpressure/Drop-Recovery,
- Shutdown,
- SQLite-Dedupe/Persistenz/Retention,
- `git diff --check`.

Der bekannte `lefx.interfaces`-Umgebungsfehler sowie der im Gate-Review dokumentierte intermittierende `test_core_bridge`-Befund dürfen nicht einfach pauschal als irrelevant übernommen werden. Prüfe bei einem erneuten Auftreten, ob sie gegenüber dem dokumentierten Ausgangszustand unverändert und tatsächlich außerhalb des Diffs liegen.

## Run und Evidence

Lege einen neuen Korrekturlauf an:

ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\runs\RUN-OBS-030-02_2026-08-17\

Mindestens:

- RUN_LOG.md
- RESULT.md
- RUN_REPORT.md
- OUTPUT_INDEX.md

Neue bzw. korrigierende Evidence unter:

ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\40_EVIDENCE\OBS-030\RUN-02_2026-08-17\

Dokumentiere dort insbesondere:

- welche Gate-Befunde behoben wurden,
- Entscheidung und Begründung zu W-1 bis W-7,
- Testresultate,
- Fault-Injection-Ergebnisse,
- finalen Diff-/Scope-Abgleich.

Aktualisiere am Ende:

- CURRENT_STATE.md
- LOG_VERLAUF.md append-only
- LOGGING_V1_CHECKLISTE.md

OBS-030 Gate Review bleibt weiterhin offen. Der Korrekturlauf darf den Gate-Punkt nicht selbst als bestanden markieren.

## Git

Kein Commit.
Kein Push.
Kein Merge.
Kein Rebase.
Kein Tag.
Kein PR.

Der lokale Commit darf erst nach einem erneuten unabhängigen Gate-Review mit PASS erstellt werden.

## Abschluss

Nur wenn alle verpflichtenden Korrekturen umgesetzt und die erforderlichen Tests erfolgreich abgeschlossen sind:

OBS-030 CORRECTED – READY FOR RE-REVIEW

Liefere am Ende einen kompakten Abschlussbericht mit:

- B-1/B-2/B-3 jeweils: konkrete Korrektur + Testnachweis,
- W-1 bis W-7 jeweils: FIXED / DEFERRED / NOT A DEFECT mit Begründung,
- Teststand,
- geänderte Dateien,
- offene Punkte,
- `git status --short`,
- Bestätigung: kein Commit/Push.

Beginne nicht mit OBS-040.