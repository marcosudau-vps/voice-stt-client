# Checkliste – unabhängige Paketabnahme

Den vollständigen Kandidaten prüfen, nicht nur einen letzten Korrekturcommit. Diese Liste steuert die Prüfung; Nachweise/Verdict gehören in einen eigenen Runreport.

## Identität und Scope

- [ ] Frische unabhängige Session, tatsächlicher Auftrag/Original-Prompt und geltende Paketfassung identifiziert.
- [ ] reviewed_sha bzw. Basis plus genaue Diffidentität, reviewed_tree, canonical_parent und server_sha geprüft; Paketresultat vollständig und fremde WIP geschützt.
- [ ] Paketziele, Requirementowner und DoD als fachliche Pflicht gelesen; vorgeschlagene Namen/Strukturen/Startwerte gemäß [Spielraum](../../GEMEINSAM/references/PLANUNGSSPIELRAUM.md) beurteilt.

## Funktion und Nachweise

- [ ] Tatsächlichen Code/Diff gegen zugehörige Vertragsabschnitte geprüft; nur benötigte Kontrakte über die Paketdatei öffnen.
- [ ] Jede Paketrequirement in [Matrix](../../../REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) und [Requirements-JSON](../../../REFERENZ/TRACEABILITY/requirements.json) mit konkretem Test bzw. manuellem Fall und Kandidatenbeleg abgeglichen; beide Darstellungen konsistent.
- [ ] Kritische Negativ-/Race-/Migrations-/Recoveryrepros selbst ausgeführt; vollständige betroffene Produktregression selbst grün geprüft. Client: gesamte Clientsuite; Serverfix: gesamte schnelle Serversuite plus betroffene Clientintegration.
- [ ] Zugeordnete Build-/Crossrepo-/Hardwarepflichten aus [Testplan](../../../REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md) geprüft, einschließlich Herkunft von Runtime, SHA-Paar, Build und notwendigen eigenen Smokes. Vorhandene Datei allein ist kein Erfolgsbeleg.
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

- [ ] Dem Paket zugeordnete [Zwischenchecks](../../../REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md) ausgeführt, tatsächlichen Clientpfad/Server-SHA/Testgrenzen belegt; kein fiktiver PASS durch bloße Servertests.

## Reviewunterlagen und Rückgabe

- [ ] PR-Base feat/client-v2, eingereichter Head und canonical_parent unverändert; Umsetzer pausiert. Eigener isolierter Worktree auf genau diesem Kandidaten; vollständigen Paketdiff geprüft.
- [ ] reviewed_sha/tree benennt den vor dem eigenen Docs-Commit geprüften Stand; Report/Findings und eigene Belege in neuer Rnn-ABNAHME-Akte gesichert.
- [ ] Bei ausdrücklicher Gitfreigabe ausschließlich Reviewakte/Belege und nötige administrative Status-/Traceability-/Steuerungsverweise commit/push auf den unveränderten Paketbranch. Keine Produkt-/Test-/Kontrakt-/fachlichen Spezifikationsänderungen; normale Fast-forward-Bereitstellung, kein Force-Push und kein zweiter Review-PR.
- [ ] Verdict, geprüften SHA, Report/Finding-IDs und Reviewunterlagen-Commit/aktuelle PR-Spitze übergeben; PR-Kurzfassung verlinkt den versionierten Report. Ohne Pushfreigabe lokale Akte und offene Bereitstellung melden.
- [ ] [PR-/SHA-Regeln](../../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md) eingehalten; technischer PASS erlaubt weder Übernahme noch nächsten Paketstart.

## Automatisch erkennbarer Reviewabschluss

- [ ] WORKFLOW_STATUS.json mit reviewedCommit/Report/Finding-IDs aktualisiert: CHANGES_REQUIRED oder ROOT_PASS/WAITING_FOR_APPROVAL; Schreibrecht zurückgegeben. [Zustandsregeln](../../GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md).
- [ ] Bei Zusatzreview eigene neue unabhängige Akte; alte Reports erhalten. Frühere offene Pflichtfindings konkret berücksichtigt/geschlossen; neuer negativer Befund blockiert die Übernahme trotz älterem PASS.
