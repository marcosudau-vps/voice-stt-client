# Verbindliche Zustandserkennung und nächste Aktion

Stand 2026-10-11, Workflowrevision 10. Quelle für den [gemeinsamen Einstieg](../../voice-stt-client-v2-naechster-schritt/SKILL.md) und die Zustandspflege beider Rollen. Kein neuer Hintergrunddienst, kein zusätzlicher Agentenlauf.

## Wo der Agent den aktuellen Stand findet

Die strukturierte Übersicht liegt im aktiven Clientarbeitsblock als [WORKFLOW_STATUS.json](../../../../WORKFLOW_STATUS.json). Sie wird auf jedem Paketbranch mit den Arbeitsakten gepflegt. Normative Felder und Zustände sind unten definiert; eine Datei allein beweist keinen PASS oder Merge.

Da feat/client-v2 nur einen Commit je abgeschlossenem AP erhält, kann seine Statuskopie laufende Paketarbeit nicht enthalten. Deshalb immer **zuerst offene Paket-PRs mit Base feat/client-v2 und deren Headbranches**, zusätzlich erreichbare lokale/entfernte work/client-v2-Paketbranches und deren Status/Runakten prüfen. Lokale, noch nicht gepushte Abgaben berücksichtigen, wenn sie im erreichbaren Arbeitsbereich liegen. Fehlende Zugriffsrechte oder nicht bereitgestellte fremde lokale Arbeit konkret melden; keinen ausgedachten aktuellen Stand einsetzen.

Reine historische Vorbereitungsbranches ohne activePackage, candidateBranch, selectedCandidate oder Ausführungsakte sind keine aktiven Paketkandidaten; ihre alten Planungsstände nicht in den aktuellen Clientplan zurückkopieren.

Danach kanonischen Gitverlauf und Paketfolge im [Manifest](../../../EVIDENCE/package-manifest.json) abgleichen. Priorität ist eine noch offene aktive Paketlinie vor einem neuen Paket. Nicht allein den jüngsten Commit, Zeitstempel, PR-Kommentar oder den bisherigen Feature-Status als nächsten Auftrag interpretieren. Ein ausgewählter Kandidat bleibt bis Annahme/Verwerfung maßgeblich. Bei mehreren Versuchen genau eine aktive ausgewählte Linie; verworfene Kandidaten als SUPERSEDED kennzeichnen, nicht löschen. Mehrere konkurrierende ausgewählte Linien ohne eindeutigen Auswahl-/Ablösebeleg sind ein Konflikt, keine freie Auswahl. Ein ausdrücklich als ungewählt dokumentierter Alternativversuch ersetzt die gewählte Linie nicht.

Bei nicht freigegebenem writeOwner hat dessen aktive Schreibhoheit Vorrang, auch beim Review. Vor Rollenbeginn den Schreibanspruch in der erreichbaren Akte und beim Remoteablauf im freigegebenen Übergabekanal bekanntmachen; aktuelle Schreibansprüche in PR-Übergabekommentaren berücksichtigen, ohne daraus PASS oder Mergefreigaben abzuleiten. Eine nur lokal uncommittierte Statusdatei ist für entfernte Agenten keine sichtbare Koordination. Ist die Schreibhoheit nicht eindeutig geklärt, keinen parallelen Run starten. Abbruch/Übergabe, Auswahlwechsel und Serverfix-Rückkehr gemäß [Sonderfallreferenz](SONDERFAELLE_UND_WIEDERAUFNAHME.md) behandeln; fehlende menschliche Übergabe nicht durch Altersannahmen ersetzen. Eine verlinkte blockierende Server-FIX-Linie vor neuem Client-AP verfolgen.

## Abgleich vor der Rollenwahl

Aktuelle Remote-/PR-Spitze mit lokalem HEAD und getrackter/ungetrackter Vorarbeit abgleichen; Abweichungen erhalten und zuordnen, Reviewspitze vor Korrektur sicher übernehmen. Die ausgewählte Paketlinie ist die aktuelle Quelle. Ihre aktiven Angaben in WORKFLOW_STATUS.json, package-manifest.json, Paketkopf und Paketindex müssen übereinstimmen; abgeschlossene Runreports behalten ihre damaligen Zustände. Bei Widersprüchen Herkunft und Quelle klären und aktive Angaben berichtigen. Keinen PASS, Übernahmeschritt oder Paketstart aus einer veralteten Kopie ableiten. Gitprovenienz, unabhängiger PASS und menschliche Freigabe bleiben erforderlich.

## Zustände und eindeutige Aktionen

Paketstatus und workflowPhase sind getrennt: ROOT_PASS ist das technische Urteil, WAITING_FOR_APPROVAL die nächste Workflowentscheidung. Die vorhandenen Paketstatusnamen bleiben erhalten.

| workflowPhase | Belegte Voraussetzung | Aktion bei „Mach den nächsten Schritt“ |
| --- | --- | --- |
| READY_FOR_IMPLEMENTATION | Kein offenes früheres Paket; Vorgänger tatsächlich übernommen bzw. erster Planungsstart vorhanden | Nächstes serielles AP als Umsetzer vollständig bearbeiten |
| IMPLEMENTATION_IN_PROGRESS | Aktiver Umsetzungsrun ohne vollständige Abgabe | Fremde aktive Arbeit nicht übernehmen; dokumentierte Übergabe/Wiederaufnahme prüfen, sonst warten |
| REVIEW_IN_PROGRESS | Eigener unabhängiger Reviewrun hält die Schreibhoheit | Übergabe oder ausdrücklich autorisierte Wiederaufnahme prüfen, keinen parallelen Review beginnen |
| REVIEW_READY | Vollständiger festgehaltener Kandidat mit Selbstchecks eingereicht | Frischer unabhängiger Review auf ermitteltem exaktem SHA |
| CHANGES_REQUIRED | Maßgeblicher Review mit offenen Pflichtfindings | Korrekturlauf gegen diese Findings; der tatsächlich erteilte Kurzauftrag beauftragt die Korrektur |
| CORRECTION_IN_PROGRESS | Korrektur läuft, noch keine vollständige neue Abgabe | Wie aktive Umsetzung: nicht parallel in fremde Arbeit eingreifen |
| WAITING_FOR_APPROVAL | Vollständiger unabhängiger ROOT_PASS; kein neuer offener Befund; menschliche Übernahme noch nicht freigegeben | PASS und ausstehende Freigabe melden, keine Übernahme/kein Folgepaket |
| READY_FOR_CANONICALIZATION | Passender tatsächlicher menschlicher Übernahmeprompt plus gültiger PASS vorhanden | Freigegebene Einzelübernahme nach Identitäts-/CI-Prüfung durchführen |
| CANONICALIZED | Ein sauberer AP-Commit auf feat/client-v2 tatsächlich vorhanden, Review/Freigabe/Provenienz nachvollziehbar | Abschlussübersicht beim nächsten Paket nachführen; nächstes serielles AP starten |
| SERVER_FIX_REQUIRED | Clientpaket durch reproduzierbaren Serverdefekt blockiert; FIX-Verweis vorhanden | Beauftragte verlinkte Serverlinie bearbeiten/prüfen; ohne Serverauftrag konkrete Freigabelücke melden |
| READY_FOR_DISTRIBUTED_PROMOTION | Nur Server-FIX: gültiger Review plus menschliche Sicherungsfreigabe | Geprüften Serverfix im freigegebenen Verfahren auf Server-Distributed sichern |
| FIX_ACCEPTED | Nur Server-FIX: Sicherung samt neuer Distributed-SHA tatsächlich nachgewiesen | Zum gehaltenen Clientpaket zurückkehren und neues Paar prüfen |
| BLOCKED | Konkrete fehlende Pflichtvoraussetzung oder widersprüchliche Identitäten | Ursache/Owner/auflösende Aktion melden; keine fiktive Weiterentwicklung |
| COMPLETED | Alle regulären APs und notwendigen Zusatzfixes tatsächlich angenommen; keine offenen Pflichtbefunde | Endzustand aus Git/Abnahmebelegen ableiten, Nachmerge-Abschlussnachweis in letzter Paketakte sichern; kein zusätzlicher Featurecommit |
| SUPERSEDED | Kandidat ausdrücklich verworfen/ersetzt | Als Herkunft erhalten, nicht als offene aktive Arbeit auswählen |

Ein Auftrag wählt eine Aktion. Selbstkorrekturen bis zur vollständigen Abgabe gehören dazu; Eigenreview und automatischer Start mehrerer APs nicht. Ein abgeschlossener Implementierungsrun kann nicht anschließend als unabhängiger Reviewer seiner eigenen Arbeit auftreten. Bei unbekannter Herkunft oder eigener Mitwirkung frischen unabhängigen Reviewer anfordern.

## Was die Statusdatei enthält

Pflichtfelder: schemaVersion, workflowPhase, packageStatus, activePackage, nextPackage, canonicalBranch, canonicalParent, candidateBranch, pullRequest, selectedCandidate, lastRun, reviewedCommit, reviewReport, openFindingIds, humanApproval, writeOwner, blockingReason, nextAction, workAuthorization und repository. Die ergänzenden Felder candidateSelection, recovery und relatedServerFix sind im initialen Stand null; bei tatsächlich betroffenen Fällen nach untenstehender Regel befüllen.

- repository: tatsächliches Client- oder Serverrepository. Erst dieses und die ausgewählte Paketlinie bestimmen die Rollen-/Zielbranchprüfungen; bei Serverfix gilt die Server-Distributed-Zielrolle statt feat/client-v2.
- candidateSelection: bei ausgewählter Linie candidateId/source/reason und gegebenenfalls previousBranch; Auswahlquelle ist ein tatsächlicher Auftrag/Entscheidungsbeleg. Bei Anfang ohne Paket null. [Auswahl-/Ablöseregeln](SONDERFAELLE_UND_WIEDERAUFNAHME.md).
- recovery: bei tatsächlicher Wiederaufnahme Verweis auf Übergabeoriginal und neuen Run mit altem/neuem Owner und gesichertem Ausgangsstand; sonst null.
- relatedServerFix: bei Serverblocker FIX-ID, repository, branch, statusPath und returnClient mit AP/Branch/Parent; vor Instanziierung unbekannte Werte offen lassen, nicht erfinden. Maßgeblicher FIX-Zustand liegt in der Serverakte.
- canonicalParent: tatsächlicher angenommener Ausgangscommit. Ausschließlich im initialen Unterlagenstart ist null mit canonicalParentRef=feat/client-v2 zulässig, um die unmögliche Selbst-SHA zu vermeiden. Vor jeder Paketbearbeitung den tatsächlichen HEAD aus Git ermitteln und die volle SHA im Paketbranch setzen; ein laufender Kandidat mit null-Parent ist unvollständig. activePackage/nextPackage: IDs aus Paketfolge, nicht frei geschätzt.
- candidateBranch/pullRequest: ausgewählter Arbeitsbranch und PR-URL. Der eigene finale Commit-SHA wird beim Start des nächsten Agenten aus dem konkreten Ref ermittelt; keine unmögliche Selbst-SHA in derselben Commitdatei. Reviewreport benennt hingegen den bereits existierenden reviewedCommit.
- lastRun: Run-ID, Rolle, Report- und Evidenzpfad. reviewReport/reviewedCommit/openFindingIds: tatsächliches unabhängiges Urteil und noch offene Befunde. Historische Reviews bleiben in der Paketakte verlinkt.
- humanApproval: Referenz auf tatsächlich erteilten Originalprompt mit freigegebenem Paket/PR/Head/Parent; null bedeutet keine Übernahmefreigabe. Keine Vorlage und kein Reviewerurteil hier einsetzen.
- writeOwner: aktueller Run/Session oder null nach Übergabe; blockierende aktive Arbeit nicht wegen ihres Alters als verlassen erklären.
- workAuthorization: tatsächlich erteilte, gegebenenfalls workflowweit geltende Kandidaten-Gitrechte samt Originalquelle. Bereits gültige Freigaben nutzen. Ohne Quelle keine automatische Commit-/Push-/PR-Erlaubnis; lokaler Diff/Report weiterhin möglich. Eine dokumentierte allgemeine Arbeitsfreigabe erlaubt niemals kanonische Übernahme.
- blockingReason/nextAction: konkrete Lücke oder unmittelbar nächste erlaubte Aktion. Gleiche Statusworte in JSON, Paketindex und Runreport verwenden; kein zweites vollständiges Test-/Findingregister in der Übersicht.

Die initiale Statusdatei beschreibt nur die jetzt belegte Planungsbereitschaft: AP-CV2-000 offen, kein PR/Review/Freigabeprompt und kein Produkt-PASS. Sie ist kein erfundener Ausführungsrun.

## Wer wann aktualisiert

1. **Umsetzer bei Start:** ausgewählte Paketlinie, Parent, Gitrechte/Quelle, IN_PROGRESS/IMPLEMENTATION_IN_PROGRESS und writeOwner festhalten. Tatsächlichen Original-Kurzauftrag sichern und gewählte Aktion im Report nennen.
2. **Umsetzer vor Abgabe:** Selbstchecks/Matrix/Planpflege und Belege fertigstellen; REVIEW_READY, Kandidatenref/PR und letzte Runakte setzen, writeOwner für Review zurückgeben. Ganze Abgabe im erlaubten Scope bereitstellen. Keine Folgephase allein aus einer Chatnachricht behaupten.
3. **Reviewer bei Start:** REVIEW_IN_PROGRESS und eigene Schreibhoheit setzen, neue eigene Runakte, geprüften SHA und Findings sichern. Bei Pflichtbefunden CHANGES_REQUIRED; bei vollständigem PASS ROOT_PASS/WAITING_FOR_APPROVAL. Reviewunterlagen und Zustandsverweise im selben beauftragten Docs-Commit auf Paketbranch, Schreibrecht zurückgeben.
4. **Korrekturagent:** bisherigen Reviewstand übernehmen, CORRECTION_IN_PROGRESS setzen; neue Abgabe wieder REVIEW_READY. Einen früheren PASS nach fachlicher Änderung nicht fortschreiben.
5. **Abschlussagent nach menschlichem Prompt:** Originalfreigabe sichern, READY_FOR_CANONICALIZATION mit Identität setzen, erlaubten administrativen Nachtrag prüfen und genau eine Übernahme ausführen. Vor tatsächlichem Merge keinen ACCEPTED-/CANONICALIZED-Erfolg eintragen.
6. **Nächster Agent nach Merge:** eindeutigem AP-Commit in feat/client-v2 vertrauen, wenn Paketidentität und verlinkte PASS-/Freigabeprovenienz stimmen. Darin enthaltenes READY_FOR_CANONICALIZATION logisch als CANONICALIZED erkennen. Abschluss-SHA/Beleg aus Git/PR ergänzen und die neue Paketstatusdatei auf dem neuen Paketbranch fortschreiben. Kein zweiter Status-Aufräumcommit auf feat/client-v2.

Vor jedem Rollenstart und jeder Abgabe Zustandsdatei, Paketindex, Report und tatsächliche Refs abgleichen. Ein fehlender veralteter Nachmerge-Status wird aus belegter Übernahme nachgeführt; fehlende Tests/Freigaben werden niemals nachträglich erfunden. Laufende Zustände können uncommittiert sein; nur tatsächlich bereitgestellte Akten sind für einen entfernten Agenten sichtbar. Fehlende Bereitstellung offen ausweisen.

## Ausdrücklich zusätzliches unabhängiges Review

„Mach noch ein unabhängiges Review“ überschreibt die Standardauswahl, auch nach ROOT_PASS. Eine neue frische Session prüft den aktuellen gewählten Kandidaten und erstellt Rnn-ABNAHME; kein alter Report wird ersetzt. Kein zusätzlicher Pflichtlauf, nur auf tatsächlichen Auftrag.

Während dieses Reviews keine Übernahme. Danach gilt das neueste fachlich gültige unabhängige Urteil für den aktuellen Kandidaten, **unter Berücksichtigung aller noch offenen früheren Findings**. Ein neuer PASS darf alte Pflichtbefunde nicht ohne dokumentierte Prüfung/Schließung verdrängen. Neuer Pflichtbefund → CHANGES_REQUIRED und vorheriger PASS als nicht ausreichend kennzeichnen. Zusatzreview bestanden und Befunde geklärt → WAITING_FOR_APPROVAL. Eine inzwischen überholte Freigabe/Head-Identität nicht automatisch erweitern; bei später erteilter passender Übernahmefreigabe erneut den Abschlussweg wählen.

Technische Abnahme, unabhängige Session und menschliche Freigabe bleiben erforderlich. [PR-/SHA-Übergaberegeln](PR_UND_REVIEW_UEBERGABE.md) und [Startgrenzen](START_UND_GRENZEN.md) gelten weiter.

## Abschluss und nachträgliche Korrekturen

COMPLETED wird auch ohne weiteres Paket aus belegten kanonischen Abschlüssen abgeleitet. Nachmerge-Nachweis in der letzten Paketakte sichern; kein zweiter kanonischer Paketcommit. Bei notwendiger nachträglicher Korrektur und fehlendem passenden Folgepaket ist eine ausdrücklich beauftragte FIX-Instanz möglich. Einzelheiten und Rückkehrregeln: [Sonderfallreferenz](SONDERFAELLE_UND_WIEDERAUFNAHME.md).
