# Dein Ablauf als Auftraggeber

Stand 2026-10-11, Workflowrevision 10. Ein gemeinsamer Einstieg ermittelt künftig Paket, Rolle und Kandidat selbst. Du brauchst keine manuelle Übergabe mit SHA-/Reportlisten.

## Was du liest und beauftragst

Lies einmal diesen Leitfaden. Bei fachlichen Fragen Paketziel im [Paketindex](../../ARBEITSPAKETE/README.md) oder dessen Spezifikation öffnen; vor Übernahme Ergebnis/offene Punkte des unabhängigen Reviews lesen. Technische Tests, Kontrakte und Traceability sind Agentenaufgabe.

Nach dem ersten Umsetzungsauftrag beauftragst du jeweils eine frische Session:

> Mach den nächsten Schritt.

Wenn der Projektkontext den Einstieg noch nicht erkennt, einmal den Pfad zum [gemeinsamen Skill](../../SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md) ergänzen. Eine globale Skillinstallation oder ein weiteres Modell für den Prompt ist nicht erforderlich.

Der Agent prüft offene Paket-PRs/Branches, Arbeitsakten und kanonischen Gitverlauf. Er entscheidet gemäß [Zustandsreferenz](../../SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md): neues AP umsetzen, eingereichten Kandidaten unabhängig prüfen oder verlangte Korrekturen umsetzen. Er nennt den ermittelten Einstieg und führt diese eine Aktion vollständig aus. Die Rollen-Skills/Checklisten bleiben seine fachlichen Arbeitsanweisungen.

## Was du anschließend machst

- Bei REVIEW_READY oder CHANGES_REQUIRED genügt ein neuer Auftrag „Mach den nächsten Schritt“. Die nötigen Kandidaten-/Reportangaben ermittelt der Agent selbst.
- Bei ROOT_PASS liest du Reviewurteil und Grenzen. Ohne deine ausdrückliche Übernahmefreigabe wartet der Ablauf.
- Für die Übernahme kannst du sagen: „Übernimm das aktuell unabhängig bestandene Paket ausdrücklich als genau einen Squash-Commit auf feat/client-v2 gemäß dem Übernahmeablauf.“ Der Agent identifiziert den einen aktuellen Kandidaten, sichert deinen Originalprompt und prüft Head/Base/CI. Detaillierte [Übernahmevorlage](../../SKILLS/voice-stt-client-v2-abnehmen/assets/PROMPT_UEBERNAHME.md) nur bei Bedarf.
- Nach belegter Übernahme genügt wieder „Mach den nächsten Schritt“. Der neue Agent erkennt den kanonischen AP-Commit als Abschluss und startet das nächste Paket von diesem Stand.
- Du kannst ausdrücklich „Mach noch ein unabhängiges Review des aktuellen Kandidaten“ beauftragen. Das Zusatzreview hat Vorrang, startet frisch und erhält eine eigene Akte. Erst wenn alle Pflichtbefunde geklärt sind, ist die Übernahme wieder möglich.

Der ausführende Agent darf nicht seine eigene Arbeit unabhängig abnehmen. Eine weitere frische Session muss unabhängig von der Umsetzung sein. Der Ablauf startet keine zusätzlichen Chats von selbst.

## Was du nicht zusammensuchen musst

AP-ID, nächste Rolle, Kandidaten-SHA, kanonischen Parent, Server-SHA, PR-URL, Report-/Evidenzpfade und Finding-IDs ermitteln die Agenten aus ihren gepflegten Akten. Jede Abgabe enthält Zustand und nächste Aktion. Alte Reviews bleiben erhalten; tatsächlicher Git-/PR-Stand ist maßgeblich bei veralteten Nachmerge-Statusfeldern. Die [Kurzvorlage](../../SKILLS/voice-stt-client-v2-naechster-schritt/assets/PROMPT_NAECHSTER_SCHRITT.md) genügt für Folgeaufträge.

Bei mehreren konkurrierenden aktiven Kandidaten, widersprüchlichen Belegen oder nicht erreichbarer Arbeit meldet der Agent genau diese Lücke. Das lässt sich nicht zuverlässig aus einem bloßen Zeitstempel erraten. Verworfenes wird als SUPERSEDED erhalten. Main, Serverfeature, Tags, Releases und Cleanup bleiben eigene Aufträge.

Nutzen beide Agenten denselben GitHub-Account, kann dieser seinen eigenen PR nicht formal genehmigen ([GitHub-Dokumentation](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews)). Der versionierte unabhängige Reviewreport dokumentiert unsere technische Abnahme. Tatsächliche GitHub-Branchregeln gegebenenfalls zusätzlich erfüllen.

## Erster Umsetzungsauftrag von der veröffentlichten Basis

Die vollständige Planung und alle Skills liegen zusammen auf `feat/client-v2`. Verwende dessen aktuellen Checkout; AP-CV2-000 ist noch offen. Der Agent prüft den tatsächlichen Remote-/Gitstand und legt seinen Paketbranch von dieser Basis an. Unterlagen nicht aus früheren Arbeitsbranches oder externen Archiven nachkopieren.

Für den ersten Auftrag steht die [Startvorlage](../../SKILLS/voice-stt-client-v2-naechster-schritt/assets/PROMPT_ERSTER_UMSETZUNGSAUFTRAG.md) bereit. Sie beauftragt den nächsten Schritt und erlaubt zugleich workflowweit Kandidaten-Commits, normale Paketbranch-Pushes, Paket-PR-Pflege und ausschließlich administrative Review-Commits. Erst wenn du diese Vorlage tatsächlich als Prompt erteilst, wird ihr Originalwortlaut als workAuthorization gesichert. Danach genügt „Mach den nächsten Schritt“. Die Vorlage selbst und der Planungsveröffentlichungsauftrag sind keine zukünftige Kandidaten- oder Übernahmefreigabe.

Details bei Bedarf: [PR-/Reviewübergabe](../../SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md), [Branchführung](BRANCH_UND_PLANPFLEGE.md).

## Sonderfälle, bei denen du eine Entscheidung gibst

„Mach den nächsten Schritt“ setzt keine fremde aktive Session außer Kraft und wählt keinen anderen Versuch. Bei endgültigem Abbruch kannst du die Übernahme der unterbrochenen Linie ausdrücklich erlauben; bei mehreren Versuchen den gewünschten Kandidaten mit Branch bestimmen. Ein nachgewiesener Serverdefekt benötigt einen Auftrag für den konkreten Server-FIX und später dessen eigene Sicherungsfreigabe auf Server-Distributed. [Wiederaufnahme, Auswahl und Serverrückkehr](../../SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md).

Reale Windows-/Hardwarefälle kannst du selbst nach dem dokumentierten Ablauf durchführen, wenn ein Agent keinen Zugriff hat. Der Reviewer validiert deine vollständigen Belege unabhängig; [Nachweisregeln](../QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md). Nach dem letzten Paket wird COMPLETED aus Git/Abnahme ermittelt, mit Nachmerge-Beleg in seiner Paketakte. Spätere notwendige Zusatzkorrekturen sind ausdrücklich beauftragbar; frühere PASS-Berichte/Commits bleiben erhalten.
