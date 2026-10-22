# Auftrag: AP-IV2-020 – R03-KORREKTUR (Review-F02 + GitHub-Issue #16)

## Repository und Arbeitsgrundlage

- **Repository:** `marcosudau-vps/voice-stt-client`
- **Arbeitsbranch:** `work/client-v2/ap-iv2-020`
- **Pull Request:** https://github.com/marcosudau-vps/voice-stt-client/pull/15
- **PR-Zielbranch:** `feat/client-v2`
- **Aktueller Ausgangscommit:** `2ba23544d18773f3ac02075ada5544b4c8ef8e47`
- **Arbeitspaket:** `AP-IV2-020`
- **Neuer Run:** `R03-KORREKTUR`

Lies zuerst:

1. `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md`
2. Den dort verlinkten Umsetzungsskill und dessen Korrekturablauf.
3. `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R02-ABNAHME/01_REPORT.md`
4. GitHub-Issue https://github.com/marcosudau-vps/voice-stt-client/issues/16
5. Nur die unmittelbar relevanten Code-, Test- und Vertragsabschnitte sowie geltende `AGENTS.md`.

Prüfe den tatsächlichen Remote-HEAD und übernimm die Reviewcommits per Fast-forward. Arbeite ausschließlich auf dem bestehenden Paketbranch und im bestehenden PR. Erhalte die historischen R01-/R02-Unterlagen.

**Dieser Auftrag erteilt die Freigabe für eng auf die folgenden zwei Probleme begrenzte Clientcode-, Test- und Dokumentationskorrekturen auf dem Paketbranch.**

## Aufgabe A: Offenes Reviewfinding R02-F02 beheben

**Finding:** `IV2-020-R02-F02`

Prüfe die sessiongebundenen Activation-/Segment-/Sequenz-/Deduplikationsregister in `voice_stt_client/core/activation_mirror.py` sowie die Terminalverwaltung in `voice_stt_client/core/final_results.py`.

Problem: In einer lange verbundenen Session können abgeschlossene Einträge ohne nachgewiesene Begrenzung anwachsen. Der bisherige 100-Activation-Test enthält mehrere Reconnects und weist deshalb keine stabile Retention innerhalb einer einzigen fortlaufenden Session nach.

**Erforderliches Ergebnis:**

- Verhindere unkontrolliertes Speicher- und Projektionswachstum über viele Activations in derselben Session.
- Bewahre korrektes Verhalten für offene und verzögert eintreffende Finals, Out-of-order-Ereignisse, Replay, Gap-Recovery sowie Unknown-outcome-Situationen.
- Verhindere doppelte Historyeinträge, Textinjektionen und andere Exactly-once-Verletzungen.
- Wähle die technisch einfachste sichere Lösung. Die konkrete Retentionstrategie und Grenzwerte darfst du selbst fachlich begründet festlegen.
- Falls du nach Codeanalyse nachweisen kannst, dass bereits eine wirksame Grenze existiert, dokumentiere den Nachweis, statt unnötigen Code umzubauen.

**Minimaler Testnachweis:** Ein gezielter deterministischer Test mit mehreren hundert Activations **ohne Session-Reconnect**, der die tatsächlich gehaltenen Zustände und die Duplikatsicherheit überprüft. Ergänze nur die weiteren Regressionen, die für die gewählte Korrektur notwendig sind.

## Aufgabe B: GitHub-Issue #16 beheben

https://github.com/marcosudau-vps/voice-stt-client/issues/16

Problem: Der bestehende EventStream-Happy-Path-Test koppelt fachlich korrekte Handshake-/Replay-/Live-Verarbeitung an sehr kurze reale Zeitbudgets und synchrone Cursor-Dateisystemoperationen. Bei einer Verzögerung entstehen Replay-Timeout, fehlerhafte Wiederverwendung einer verbrauchten Fake-Verbindung und schließlich ein äußerer Test-Timeout.

**Erforderliches Ergebnis:**

- Mache den betroffenen Test zuverlässig und unabhängig von zufälliger Windows-Runner- oder Dateisystemlatenz.
- Erhalte die fachlichen Assertions zu Handshake, Replay, Live-Verarbeitung, Cursorfortschritt, Stop und Authentifizierung.
- Stelle sicher, dass unerwartete Reconnects im Test eindeutig und frühzeitig diagnostiziert werden, statt eine irreführende Fehlerkaskade auszulösen.
- Die im Issue beschriebene Trennung von funktionalem Semantiktest und echter Disk-I/O ist **ein unverbindlicher Lösungsvorschlag**, keine vorgeschriebene Architektur.
- Erhöhe Timeouts nicht einfach pauschal und verwende keine CI-Retries als eigentliche Fehlerbehebung.
- Ändere produktive EventStream-/Persistenzlogik nur, wenn ein eigenständiger konkreter Fehler dies notwendig macht.

**Minimaler Testnachweis:** Gezielte erfolgreiche Regression, die insbesondere eine kontrolliert verzögerte Cursoroperation beziehungsweise Runner-Verzögerung abdeckt. Der Test muss aufgrund korrekter Zustandsübergänge bestehen, nicht aufgrund günstigen Timings.

## Effizienzvorgaben – ausdrücklich wichtig

Der bisherige Projektverlauf enthielt zu viele wiederholte Nachweis- und Korrekturschleifen. Arbeite diesmal konsequent nach dem Prinzip:

**So wenig zusätzliche Arbeit und Evidenz wie möglich, so viel wie für eine technisch belastbare Korrektur nötig.**

Daraus folgen verbindliche Grenzen für diesen Auftrag:

1. **R02-F01 ist durch den Reviewer zurückgenommen.** Keine weitere Bearbeitung dieses Findings, keine neue 30-Minuten-/100-Activation-Qualifikation, keine physischen USB-/ReSpeaker-Wiederholungen und keine neuen menschlichen Sprachtests.
2. Bereits erfolgreich qualifizierte Windows-, Realmodell-, Wake-, Clipboard-, Frozen-, Server- und Hardwarebelege **wiederverwenden**, sofern die Änderungen deren Aussage nicht konkret beeinträchtigen.
3. Keine vorsorglichen Refactorings, neuen Testframeworks, zusätzlichen Testoberflächen oder allgemeinen Architekturüberarbeitungen.
4. Keine mehrfachen nahezu identischen Evidenzpakete, Hashsammlungen, Tagesberichte oder nach jeder kleinen Änderung erneut vollständigen Nachweiskataloge erstellen.
5. Zuerst die betroffenen Stellen korrigieren, dann gezielte Regressionen ausführen, **danach einmal regulär die vollständige Windows-Clientsuite und CI** für den endgültigen Kandidaten qualifizieren. Die bestehenden verpflichtenden Windows-Nachweisregeln bleiben gültig; führe darüber hinaus keine redundanten zusätzlichen Vollsuiten durch.
6. Falls ein Test fehlschlägt, die konkrete Ursache untersuchen und korrigieren. Keine endlosen Wiederholungen, nur um irgendwann ein grünes Ergebnis zu erhalten.
7. Kein Serverfix, keine neue Serverinstanz und keine Änderung am Serververtrag, solange nicht ein konkret reproduzierter neuer Fehler dies zwingend erforderlich macht. Bei einer solchen Scopeüberschreitung zunächst den Befund melden.

## Minimale Dokumentation und Übergabe

Lege unter

`ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R03-KORREKTUR/`

nur die erforderliche Runakte an:

- `00_PROMPT_ORIGINAL.md` – diesen Auftrag unverändert.
- `01_REPORT.md` – knappe Beschreibung der Ursachen, Änderungen, Testergebnisse und verbliebenen Risiken.
- `EVIDENCE/INDEX.md` – direkte Links zu relevanten Tests, Commit, CI-Lauf und gegebenenfalls den nach Projektregel tatsächlich benötigten Logs.

Pflege die aktuellen Workflow- und Traceability-Statusangaben konsistent, ohne historische Berichte umzuschreiben. Nutze vorhandene Evidenz, statt sie erneut zu erzeugen oder zu duplizieren.

Committiere und pushe den korrigierten Stand auf `work/client-v2/ap-iv2-020`. Verwende weiterhin PR #15. Dokumentiere den Bezug zu Issue #16; der Issue soll nicht voreilig allein aufgrund der Codeänderung als verifiziert geschlossen werden.

Melde zum Schluss kurz:

- Was wurde für R02-F02 geändert?
- Was wurde für Issue #16 geändert?
- Welche gezielten Tests und welche vollständige CI wurden bestanden?
- Welcher Commit und Tree sind der neue Prüfkandidat?
- Gibt es tatsächlich noch offene Risiken?

Übergib danach **REVIEW_READY** zur frischen unabhängigen Abnahme. Führe **kein Eigenreview, keinen Merge, kein Release und kein Folgearbeitspaket** aus.

**Ziel ist ein funktional sauberer, regressionsgeprüfter Korrekturstand – nicht die Produktion möglichst vieler Evidenzdateien.**
