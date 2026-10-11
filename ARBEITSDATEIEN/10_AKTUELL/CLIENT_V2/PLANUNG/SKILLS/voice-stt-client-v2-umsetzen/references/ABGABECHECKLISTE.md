# Abgabecheckliste – Umsetzung und Korrektur

Vor REVIEW_READY diese Liste gegen das beauftragte Paket prüfen. Sie ist eine Arbeitscheckliste; die Resultate mit Links stehen im Runreport. Keine zweite vollständige Ergebnisliste erforderlich. Ein ungeklärtes Pflichtkriterium bleibt offen.

## Funktionsumfang und Code

- [ ] Paketziele, zugeordnete Requirements und DoD vollständig erfüllt; selbstständige Folgefeatures nicht versteckt übernommen.
- [ ] Notwendige gemeinsame Anschlussänderungen nachvollziehbar; vorhandene Logging-/Feedback-/Audio-/UI-Komponenten und Nutzerpräferenzen erhalten.
- [ ] Kontrakt, ID-/Session-/Generationguards und Fehler-/Shutdownverhalten der betroffenen Bereiche geprüft; keine lokale zweite Lifecycle-Autorität.
- [ ] Fachliche Änderungen/Schema- oder Credentialfragen ausdrücklich entschieden; interne Umsetzungsvorschläge und angepasste Startwerte kurz begründet.

## Tests und Belege

- [ ] Relevante Vorher-Baseline dokumentiert, gezielte Repros/Negativ-/Race-/Migrationsfälle bestanden und entdeckte Fehler iterativ behoben.
- [ ] Nach Produktänderung vollständige Clientregression grün, compileall und git diff --check bestanden; bei Serverfix zusätzlich vollständige schnelle Serversuite und betroffene Integration. Konkrete Befehle und Runtime im Report.
- [ ] Paketabhängige Build-/Crossrepo-/reale Pflichtfälle nach [Testplan](../../../REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md) ausgeführt. PASS/FAIL/NOT_RUN/NOT_PROVEN/SKIPPED_EXPECTED getrennt; kein Pflichtskip als Erfolg.
- [ ] [Traceability-Matrix](../../../REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) und [Requirements-JSON](../../../REFERENZ/TRACEABILITY/requirements.json) konsistent: jede Paket-ID mit tatsächlicher Methode/manuellem Fall, Runbeleg und Kandidatenbezug. CLIENT OPEN nicht selbst zur unabhängig angenommenen Abnahme hochstufen; Implementierungsbelege separat ergänzen.
- [ ] Ersetzte V1-Assertions jeweils fachlichem Nachfolger zugeordnet. Kein vorgeschriebener Funktionsfall entfallen; anders benannte Testdatei zulässig.
- [ ] EVIDENCE/INDEX.md enthält erzeugende Befehle/Fälle, Identität/Konfiguration, Ergebnisse und erforderliche Artefakthashes; keine fiktiven oder nur leeren Belege.

## Dokumentation, Akte und Übergabe

- [ ] Erforderliche Produktdokumentation und tatsächlich betroffene Plan-/Folgepaketstellen aktualisiert; reale APIs und Guards nachvollziehbar übergeben.
- [ ] Tatsächlich erteilter Original-Prompt gesichert, spätere Steuerung separat; eigener Report vollständig und Paketindex aktuell gemäß [Runablage](../../GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md).
- [ ] Kandidat-SHA/Tree/Parent/Serverbaseline oder überprüfbarer Basis-SHA plus genauer Diff identifiziert; fremde WIP und ausgeschlossene Laufzeit-/Nutzerdaten nicht im Produktdiff.
- [ ] Reviewstatus ehrlich: vollständige Selbstchecks REVIEW_READY, offene Pflichtbefunde konkret dokumentiert. Kein eigener ROOT_PASS und keine kanonische Übernahme ohne unabhängigen PASS und Auftraggeberprompt.
- [ ] Kandidaten-Commit/Push/PR ausschließlich im ausdrücklich erteilten Scope; kumulative Paketbranch-Herkunft gesichert. Genau einen Meilenstein für diesen relevanten Run schreiben.

Weitere Details nur bei Bedarf: [Regelwerksreferenz](../../../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md). Die Liste verlangt keine zusätzlichen Sessions, Berichtdateien oder künstlichen Testmodule.

- [ ] Kandidat einschließlich Plan-/Matrix-/Aktenpflege auf dem untergeordneten Paketbranch; Abschlusslinie `feat/client-v2` enthält keine Bearbeitungscommits. Erwarteter Paketparent dokumentiert.

- [ ] Dem Paket zugeordnete [Zwischenchecks](../../../REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md) ausgeführt, tatsächlichen Clientpfad/Server-SHA/Testgrenzen belegt; kein fiktiver PASS durch bloße Servertests.

## PR und Schreibübergabe

- [ ] Vorgänger-PASS, menschliche Freigabe und tatsächlichen Aggregatecommit gemäß [Startcheck](../../GEMEINSAM/references/START_UND_GRENZEN.md) geprüft; Paketparent entspricht aktuellem feat/client-v2-Stand. Kein voreiliger Folgepaketstart.
- [ ] Bei PR-Freigabe PR-Base feat/client-v2, korrekten Headbranch und tatsächlichen Kandidaten-SHA/Tree nach allen Abgabeunterlagen nennen; Report/Evidenz verlinkt, Workingtree sauber. Fehlende PR-Rechte/Bereitstellung offen melden.
- [ ] Nach Korrektur Reviewunterlagen zuerst fetch/fast-forward übernommen; keine alten Reports überschrieben und kein veralteter PASS fortgeschrieben.
- [ ] [PR-/Reviewübergabe](../../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md) gelesen. Ab REVIEW_READY Paketbranch-Änderungen/Pushes für den unabhängigen Review pausieren. Kein Auto-Merge.

## Automatisch erkennbare nächste Aktion

- [ ] WORKFLOW_STATUS.json, Paketindex und Report konsistent: AP/Parent/Kandidatenref/PR, letzter Run, offene Findings, freigegebenes Schreibrecht und nächste Aktion gemäß [Zustandsregeln](../../GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md).
- [ ] Vollständige neue Abgabe als REVIEW_READY bereitgestellt; früherer PASS nach fachlicher Änderung nicht weitergeführt. Tatsächliche Arbeitsfreigabe referenziert, keine vorweggenommene menschliche Übernahmefreigabe.
