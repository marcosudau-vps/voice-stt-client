---
name: voice-stt-client-v2-umsetzen
description: Setze ein beauftragtes Voice-STT-Client-V2-Paket oder konkrete Reviewkorrekturen um und liefere einen geprüften Paket-PR mit Traceability und Runbelegen.
---

# Voice-STT Client V2 – ausführender Agent

Einstieg für Umsetzung und beauftragte Korrekturen. Du lieferst den vollständigen Paketkandidaten; die unabhängige Abnahme übernimmt eine frische andere Session. Nach einem späteren menschlichen Übernahmeprompt kannst du auch den Paketabschluss ausführen. Der Umsetzungsauftrag allein erlaubt diesen Abschluss nicht.


Bei einem Auftrag „Mach den nächsten Schritt“ zuerst den [gemeinsamen Einstieg](../voice-stt-client-v2-naechster-schritt/SKILL.md) verwenden; Paket/Rolle/Kandidat aus dem dokumentierten Stand ermitteln. Der erteilte Kurzauftrag gilt für die dadurch bestimmte fachliche Aktion. Vor jeder Abgabe [Zustandsübersicht](../GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) samt Belegverweisen und nächster Aktion pflegen. Gitrechte aus tatsächlichem Prompt bzw. gesicherter fortgeltender Arbeitsfreigabe; Übernahme weiterhin separat.

## Was du beim Start liest und prüfst

1. [Start und Grenzen](../GEMEINSAM/references/START_UND_GRENZEN.md): Auftrag, Repositoryregeln, Baseline und **nachweislich übernommener Vorgänger**.
2. Nur die beauftragte Datei im [Paketindex](../../ARBEITSPAKETE/README.md), ihre Requirements/DoD, erforderlichen Vertragsabschnitte und tatsächlich berührten Quellen.
3. [Umsetzungsspielraum](../GEMEINSAM/references/PLANUNGSSPIELRAUM.md) und [Runablage](../GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md).
4. Beim ersten PR-/Übergabeschritt [PR und Reviewübergabe](../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md). Gesamtplanung und alte Analysen nur bei konkreter Fachfrage öffnen.

Prüfe den aktuellen kanonischen Parent vor Änderungen. Bearbeite Code und Unterlagen ausschließlich auf dem beauftragten Paketbranch bzw. isoliertem Worktree. Fremde WIP schützen. Fehlende Vorgängerübernahme stoppt abhängige Implementierung; keinen ACCEPTED-Status erfinden.

## Was du umsetzt und nachweist

Setze das vollständige beauftragte Paket um. Logging, Feedback, Audio, UI und Ausgabe passend weiterverwenden. Interne Klassen, Dateinamen, Testaufteilung und lokale technische Startwerte sind begründbar anpassbar; Produktziele, Serververtrag und Pflichtnachweise gelten.

Vor Produktänderungen relevante Baseline dokumentieren. Danach gezielte Tests und vollständige betroffene Regression ausführen und Fehler iterativ beheben. Clientcode: gesamte Clientsuite, compileall und Diffprüfung. Serverfix: gesamte schnelle Serversuite und betroffene Clientintegration. Zugeordnete Build-/Hardwarefälle im [Testplan](../../REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md); frühe Serverprüfungen gemäß [Checkpoints](../../REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md). Reine Dokumentänderungen brauchen Konsistenzprüfung und ergeben keine Produktabnahme.

Für jede Paketrequirement tatsächliche Testmethode/manuellen Fall und Kandidaten-/Runbeleg in [Matrix und Requirements](../../REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) pflegen. Keine erfundenen Testnamen als Erfolgsbelege, kein eigenes ROOT_PASS. Original-Prompt, Report, Evidenzindex, notwendige Plan-/Produktdokumentation und einen Steuerungsmeilenstein sichern.

## Was du abgibst

Die [Abgabecheckliste](references/ABGABECHECKLISTE.md) vollständig durchgehen. Im erlaubten Git-Scope Kandidaten committieren/pushen und einen PR **nach feat/client-v2** bereitstellen. Änderungen nach Selbstchecks kumulativ; kein Force-Push und keine Zwischencommits auf dem kanonischen Branch.

Übergabe: AP-ID, REVIEW_READY, PR-URL, Paketbranch, Kandidaten-SHA/Tree, kanonischer Parent, Server-SHA, Report/Evidenzindex und offene Grenzen. Danach während des unabhängigen Reviews Änderungen und Pushes auf diesem Paketbranch pausieren.

## Was du nach der Abgabe machst

- Bei menschlichem Korrekturauftrag: [Korrekturablauf](references/KORREKTUR.md), Reviewunterlagen zunächst fetch/fast-forward übernehmen, neue Runakte, Findings beheben, denselben PR erneut REVIEW_READY melden. Keine Eigenabnahme.
- Nach ROOT_PASS: auf menschlichen Übernahmeprompt warten. Erst dann [Übernahmeablauf](../voice-stt-client-v2-abnehmen/references/UEBERNAHME.md) lesen, Freigabe sichern, finale Identität/CI prüfen und genau einen freigegebenen Squash-Merge durchführen. Keine neue fachliche Session vorgeschrieben.
- Ohne Commit/Push/PR-Freigabe: geprüften lokalen Diff und Akte liefern, ausstehende Bereitstellung nennen.

Vorlagen bei Beauftragung: [Umsetzung](assets/PROMPT_UMSETZUNG.md), [Korrektur](assets/PROMPT_KORREKTUR.md), [Übernahme](../voice-stt-client-v2-abnehmen/assets/PROMPT_UEBERNAHME.md). Details bei Bedarf: [Regelwerk](../../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md). Vorlagen sind erst durch den tatsächlich erteilten menschlichen Prompt Gitfreigaben.
