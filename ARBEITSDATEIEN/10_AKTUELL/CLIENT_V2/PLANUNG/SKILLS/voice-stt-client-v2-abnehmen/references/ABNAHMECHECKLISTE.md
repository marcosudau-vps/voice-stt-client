# Checkliste – unabhängige Paketabnahme

Den vollständigen Kandidaten prüfen, nicht nur einen letzten Korrekturcommit. Diese Liste steuert die Prüfung; Nachweise/Verdict gehören in einen eigenen Runreport.

## Prüfstart im selben Abnahmerun

- [ ] Zugriff auf den exakten Kandidaten und vollständigen Parentdiff verifiziert: eigener isolierter Checkout oder commitgebundener GitHub-Zugriff in ChatGPT. Fehlenden/abgeschnittenen Codezugriff konkret melden.
- [ ] Vollständigen grünen Windows-Vollsuitennachweis aus Umsetzung/Korrektur mit SHA/Diff, Runtime, Befehl, Exitcode, Testzahl und vollständigen Logs identifiziert. Eine eigene Windows-Laufzeit oder Wiederholung der Suite ist keine Reviewvoraussetzung. Vorhandene Ausführung als unabhängig geprüften Fremdbeleg kennzeichnen; fehlende/ungültige Pflichtnachweise blockieren PASS.

## Identität und Scope

- [ ] Frische unabhängige Session, tatsächlicher Auftrag/Original-Prompt und geltende Paketfassung identifiziert.
- [ ] reviewed_sha bzw. Basis plus genaue Diffidentität, reviewed_tree, canonical_parent und server_sha geprüft; Paketresultat vollständig und fremde WIP geschützt.
- [ ] Paketziele, Requirementowner und DoD als fachliche Pflicht gelesen; vorgeschlagene Namen/Strukturen/Startwerte gemäß [Spielraum](../../GEMEINSAM/references/PLANUNGSSPIELRAUM.md) beurteilt.

## Funktion und Nachweise

- [ ] Tatsächlichen Code/Diff gegen zugehörige Vertragsabschnitte geprüft; nur benötigte Kontrakte über die Paketdatei öffnen.
- [ ] Jede Paketrequirement in [Matrix](../../../REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) und [Requirements-JSON](../../../REFERENZ/TRACEABILITY/requirements.json) mit konkretem Test bzw. manuellem Fall und Kandidatenbeleg abgeglichen; beide Darstellungen konsistent.
- [ ] Kritische Negativ-/Race-/Migrations-/Recoveryfälle in Code/Tests und Ergebnissen geprüft; Windows-Vollsuite anhand der Umsetzungsbelege unabhängig validiert. Keine routinemäßige erneute Ausführung. Konkrete Zweifel oder Testlücken als Finding mit verlangtem Repro/Nachweis zurückgeben. Serverfix: schnelle Serversuite plus betroffene Clientintegration weiterhin nachweisen.
- [ ] Zugeordnete Build-/Crossrepo-/Hardwarepflichten aus [Testplan](../../../REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md) geprüft, einschließlich Runtime, SHA-Paar, Build und nachgewiesenen Smokes. Keine routinemäßige eigene Windows-Wiederholung; notwendige Ergänzungen bei konkreten Beleglücken verlangen. Vorhandene Datei allein ist kein Erfolgsbeleg.
- [ ] Daten-/Configmigration, Nebenwirkungen, Thread-/IDguards, Fehler/Shutdown, lokale Bounds und erhaltene Logging-/Feedback-/UI-Funktionen soweit betroffen konkret geprüft.
- [ ] Tests nicht durch breite Skips, entfernte Assertions oder tolerante Fakes entwertet; Tests für unveränderte Komponenten bleiben Teil der Regression.
- [ ] PASS/FAIL/NOT_RUN/NOT_PROVEN/SKIPPED_EXPECTED sauber getrennt; keine offenen Pflichtnachweise als kosmetische Restpunkte abgetan.

## Bericht und Entscheidung

- [ ] Erforderliche Produktdokumentation und tatsächliche Folgepaketübergaben vollständig; keine geheimen oder unzulässigen Daten im Diff/Belegsatz.
- [ ] Eigener [Report/Evidenzindex](../../GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) enthält Identität, selbst ausgeführte Prüfungen, Requirementnachweise und offene Findings mit ID, Wirkung, Repro, Owner und geforderter Prüfung.
- [ ] ROOT_PASS nur bei erfüllten Pflichtkriterien; sonst CHANGES_REQUIRED oder konkrete BLOCKED-Voraussetzung. Ohne Produktänderung darf der Reviewer technische Belege/Status ergänzen; kein versteckter Produktfix.
- [ ] Bei PASS Matrix/Paketindex mit tatsächlichem unabhängigen Runbeleg aktualisiert; Reviewurteil auf geprüften Kandidaten bezogen. Ein administrativer Report-/Statusnachtrag darf keine unreviewte Produkt-, Test- oder Vertragsänderung verbergen.
- [ ] Genau ein Meilenstein für den relevanten Review/Gate; kanonische Übernahme bleibt ohne ausdrücklichen Auftraggeberprompt offen. Kein automatischer Folgepaketstart.

Der Umsetzer führt vorzugsweise die später menschlich freigegebene Übernahme aus. Nur wenn diese Abschlussaktion ausdrücklich dir beauftragt wird: [Übernahmeablauf](UEBERNAHME.md). Fehlgeschlagene Übernahme darf technischen PASS nicht als ACCEPTED darstellen.

- [ ] Code und aktualisierte Unterlagen zusammen geprüft; Kandidaten auf Paketbranch, kanonisches Ziel `feat/client-v2`, exakter Paketparent und eine spätere Einzelaggregation nachvollziehbar. Keine Vorabpromotion des Servers.

- [ ] Dem Paket zugeordnete [Zwischenchecks](../../../REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md) anhand tatsächlicher Durchführung/Nachweise geprüft; Clientpfad/Server-SHA/Testgrenzen belegt; kein fiktiver PASS durch bloße Servertests.

## Reviewunterlagen und Rückgabe

- [ ] PR-Base feat/client-v2, eingereichter Head und canonical_parent unverändert; Umsetzer pausiert. Exakten Kandidaten per isoliertem Worktree oder commitgebundenem GitHub-Zugriff und vollständigem Paketdiff geprüft.
- [ ] reviewed_sha/tree benennt den vor dem eigenen Docs-Commit geprüften Stand; Report/Findings und eigene Belege in neuer Rnn-ABNAHME-Akte gesichert.
- [ ] Bei ausdrücklicher Gitfreigabe ausschließlich Reviewakte/Belege und nötige administrative Status-/Traceability-/Steuerungsverweise commit/push auf den unveränderten Paketbranch. Keine Produkt-/Test-/Kontrakt-/fachlichen Spezifikationsänderungen; normale Fast-forward-Bereitstellung, kein Force-Push und kein zweiter Review-PR.
- [ ] Verdict, geprüften SHA, Report/Finding-IDs und Reviewunterlagen-Commit/aktuelle PR-Spitze übergeben; PR-Kurzfassung verlinkt den versionierten Report. Ohne Pushfreigabe lokale Akte und offene Bereitstellung melden.
- [ ] [PR-/SHA-Regeln](../../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md) eingehalten; technischer PASS erlaubt weder Übernahme noch nächsten Paketstart.

## Automatisch erkennbarer Reviewabschluss

- [ ] WORKFLOW_STATUS.json mit reviewedCommit/Report/Finding-IDs aktualisiert: CHANGES_REQUIRED oder ROOT_PASS/WAITING_FOR_APPROVAL; Schreibrecht zurückgegeben. [Zustandsregeln](../../GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md).
- [ ] Bei Zusatzreview eigene neue unabhängige Akte; alte Reports erhalten. Frühere offene Pflichtfindings konkret berücksichtigt/geschlossen; neuer negativer Befund blockiert die Übernahme trotz älterem PASS.

- [ ] Bei realen Fremdbelegen Tester, Build-/SHA-Paar, Ablauf und tatsächliche Wirkungsbelege geprüft; eigene Prüfungen und extern validierte Durchführung getrennt berichtet. Pflichtlücken blockieren PASS.
- [ ] Bei Server-FIX die tatsächlich verlinkte Serverakte/Zielrolle angewendet; kein Client-PR-Basecheck an einem Serverkandidaten. Bei Recovery/Wechsel tatsächliche Übergabe-/Auswahlquelle geprüft.

## Aktenprüfung vor jeder Abgabe

- [ ] WORKFLOW_STATUS, Manifest, Paketkopf und Index mit der tatsächlich aktuellen PR-Kurzfassung synchronisiert; Originalprompts, Reports und Evidenz vollständig bereitgestellt. Neue/geänderte relative Links aus dem Quelldokument aufgelöst; historische Belege erhalten. Auch Review-Dokumentcommits strukturell prüfen.
- [ ] [Gemeinsamen read-only-Aktenprüfer](../../GEMEINSAM/scripts/pruefe_arbeitsakten.py) bei lokal verfügbarem Checkout ausgeführt; geänderte weitere Markdownunterlagen über `--paths` ergänzen. Bei ChatGPT-Review ohne lokalen Checkout dieselben Status-/Datei-/Linkprüfungen anhand commitgebundener GitHub-Dateien nachweisen und den Prüfweg im Report nennen. Keine Windows-Venv für die Reviewer-Aktenprüfung voraussetzen. Aktuelle PR-Kurzfassung gemäß [Übergabereferenz](../../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md) abgleichen. Lokaler Aufruf:

```powershell
.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py
```
