Prüfbericht – CLIENT_V2 (Revision 9)
1. Gesamtbewertung
Qualität der Unterlagen
8,5 / 10

Meine Bewertung der Dokumentation und ihrer praktischen Anwendbarkeit – keine Abnahme des implementierten Clients.

Mein vorläufiges Gesamturteil: Die Planung ist weitgehend schlüssig, fachlich detailliert und grundsätzlich für die agentengestützte Umsetzung geeignet. Ich würde sie nicht neu aufsetzen. Vor dem ersten Umsetzungslauf empfehle ich allerdings einige gezielte Präzisierungen, insbesondere im Agentenworkflow und bei der Handhabung verpflichtender Prüfungen.
Was bereits gut gelöst ist
- Vollständige Paketstruktur: 12 Clientpakete, 2 Integrations-/Abnahmepakete und ein bedingtes Serverkorrekturpaket.
- Nachvollziehbare Abhängigkeiten: Die technische Reihenfolge von Protokoll, Transport und Mirror über Audio, Controls und Settings bis zur Gesamtlaufzeit ist sinnvoll.
- Klare fachliche Zuständigkeiten: Serverautorität, Clientzustände, Ereignisverarbeitung und Nebenwirkungen werden bewusst getrennt.
- Frühe Integrationsprüfungen: Der echte Server wird schon während der Entwicklung eingebunden und nicht erst am Ende.
- Unabhängige Reviews: Technischer PASS, menschliche Übernahmefreigabe und Git-Merge sind sauber getrennte Schritte.
- Entwicklungsspielraum: Modulnamen, interne Datenstrukturen und technische Detailentscheidungen sind ausdrücklich anpassbar. Das verhindert unnötige Starrheit.
Formal und technisch überprüft
983
Lokale Verweise gültig
19
JSON-Dateien lesbar
216
Anforderungen zugeordnet

Ich habe außerdem den tatsächlichen GitHub-Stand überprüft. feat/client-v2 steht auf Commit bfade9d0ffe1262ca25b05c9334dcacfcd3d3452. Er liegt genau einen Commit hinter dem beschriebenen Planungsstart und enthält ausschließlich Dokumentations-/Steuerungsänderungen. Das passt zur vorgesehenen Ausgangslage: AP-CV2-000 ist noch nicht implementiert.
Die Ausgangs-SHAs des Clients und die gepinnte Serverreferenz sind ebenfalls auf GitHub vorhanden.
Damit stimmt die dokumentierte Startkonstellation mit dem überprüften Repositoryzustand überein.
2. Festgestellte Schwachstellen
Ich habe die folgenden Punkte nach ihrer praktischen Bedeutung priorisiert. Dabei unterscheide ich bewusst zwischen einem echten Ablaufrisiko und einer bloßen redaktionellen Unschärfe.
Befund 1 – Wiederaufnahme unterbrochener Agentenläufe
Wichtig

ZUSTAENDE_UND_NAECHSTER_SCHRITT.md · START_UND_GRENZEN.md
Die Zustände IMPLEMENTATION_IN_PROGRESS und CORRECTION_IN_PROGRESS sind definiert. Eine laufende fremde Bearbeitung darf nicht ungefragt übernommen werden. Das ist richtig.
Die Lücke: Was geschieht, wenn eine Agentensession endgültig abbricht, ihr Branch und ihre Akten aber weiterhin eine laufende Bearbeitung melden?
Der neue Agent soll nicht anhand des Alters entscheiden, ob die Arbeit verlassen wurde. Gleichzeitig gibt es keine hinreichend konkrete Wiederaufnahmeregel.
Praktische Folge: „Mach den nächsten Schritt“ könnte dauerhaft nur melden, dass eine fremde Bearbeitung läuft.
Korrektur: Einen geregelten Recoverypfad ergänzen: vorhandene Commits und Akten prüfen, eine laufende Session nicht eigenmächtig verdrängen, bei nicht mehr erreichbarem Owner eine ausdrücklich autorisierte Übernahme ermöglichen und den Übergang dokumentieren. Kein automatischer Reset oder Force-Push.

Befund 2 – Serverkorrekturen im gemeinsamen Workflow
Wichtig

AP-SV2-FIX.md · AGENTEN_REGELWERK.md · gemeinsamer Next-Step-Skill
Der fachliche Ablauf für Serverkorrekturen ist vorhanden. Defekte werden nachgewiesen, getrennt korrigiert und gegen eine neue Serverbaseline geprüft.
Der gemeinsame Einstieg konzentriert sich jedoch auf Client-Paketbranches und Client-PRs. Es ist nicht ausreichend konkret geregelt, wie er eine blockierende Server-FIX-Instanz erkennt, deren eigenen Branch/Review verfolgt und anschließend zum unterbrochenen Clientpaket zurückkehrt.
Praktische Folge: Die Einzelanweisungen sind vorhanden, die automatische Rollenauswahl kann aber an dieser Ausnahme scheitern.
Korrektur: Einen ausdrücklichen Zustandsübergang für SERVER_FIX_REQUIRED beziehungsweise eine äquivalente blockierte Paketlinie ergänzen. Die Rückkehr zum Client muss die neue Server-SHA, betroffene Verträge und erneut erforderliche Tests berücksichtigen.

Befund 3 – Eindeutige Kandidatenauswahl
Präzisieren

WORKFLOW_STATUS.json · ZUSTAENDE_UND_NAECHSTER_SCHRITT.md
Es gibt das Feld selectedCandidate, und mehrere Kandidatenversuche sind grundsätzlich erlaubt. Die Dokumentation beschreibt aber nicht eindeutig genug, wann dieses Feld auf true gesetzt wird, wie ein Kandidat ausdrücklich ersetzt wird und wie eine solche Entscheidung zwischen zwei Paketbranches dokumentiert werden muss.
Außerdem ist das Branchmuster work/client-v2/<paket> für mehrere gleichzeitige Versuche nicht eindeutig.
Korrektur: Auswahl- und Ablöseregeln mit einem kurzen Zustandsbeispiel ergänzen, einschließlich eindeutiger Branchnamen für alternative Versuche.

Befund 4 – Windows- und Hardwareprüfungen
Präzisieren

AP-CV2-050 · AP-CV2-080 · AP-IV2-020 · TEST_UND_ABNAHMEPLAN.md
Die Abnahmekriterien sind inhaltlich gut. Reale Hotkeys, Windows Credential Manager, ReSpeaker, Clipboard und ASR werden nicht durch Fakes ersetzt.
Unklar bleibt die praktische Verantwortlichkeit, wenn ein Agent seine Arbeit in einer Umgebung ohne Zugriff auf den echten Windows-PC oder die Hardware erledigt.
Darf der Reviewer einen vom Auftraggeber auf Windows ausgeführten, vollständig dokumentierten Hardwaretest als Nachweis anerkennen? Welche Prüfungen muss er zwingend selbst wiederholen?
Korrektur: Für hardwareabhängige Prüfungen festlegen, wer sie ausführt, welche Belege erforderlich sind und wie der unabhängige Reviewer sie validiert. Fehlende Pflichtnachweise bleiben weiterhin blockierend.

Befund 5 – Änderungen nach bereits angenommenen Paketen
Präzisieren

BRANCH_UND_PLANPFLEGE.md · AP-SV2-FIX.md · IMPLEMENTIERUNGSPLAN.md
Die Planung erlaubt begründete Anschlussänderungen und eine Rebaseline bei verändertem Serververtrag.
Nicht abschließend geklärt ist der Sonderfall, dass eine notwendige Änderung ein bereits abgeschlossenes Arbeitspaket betrifft und kein geeignetes Folgepaket mehr offen ist.
Die Regel „ein Commit pro Paket“ sollte dabei nicht zu einer künstlichen Einschränkung werden.
Korrektur: Eine ausdrücklich beauftragbare Ausnahme für nachträgliche Korrekturen definieren, ohne alte PASS-Berichte oder Paketcommits umzuschreiben.

Befund 6 – Abschluss des letzten Pakets
Gering

ZUSTAENDE_UND_NAECHSTER_SCHRITT.md · WORKFLOW_STATUS.json
Nach einem Squash-Merge verbleibt der versionierte Status absichtlich beim bisherigen technischen PASS. Den tatsächlichen Abschluss ermittelt der nächste Agent aus Git.
Bei AP-IV2-020 existiert allerdings kein weiteres reguläres Paket, in dem die abschließende Statusfortschreibung untergebracht werden kann.
Korrektur: COMPLETED ausdrücklich als aus Git- und Abnahmebelegen abgeleiteten Endzustand definieren und festlegen, wo der abschließende Nachweis abgelegt wird. Dafür ist kein zusätzlicher Produktcommit erforderlich.

3. Kleinere Auffälligkeiten
Unterschiedliche Revisionsstände
In planning-baseline.json steht Revision 9 und roleSkillVersion: 4. Im package-manifest.json stehen dagegen noch Revision 6 und roleSkillVersion: 2.
Die fachlichen Paketzuordnungen stimmen trotzdem überein. Das ist also kein nachgewiesener inhaltlicher Fehler. Es sollte aber eindeutig erkennbar sein, ob diese Metadaten bewusst eingefrorene Strukturversionen oder veraltete Angaben sind.
Aufwandsschätzung
Die vorgesehenen 28–30 Agentensessions sind als optimistisches Grundmodell verständlich. Korrekturschleifen, zusätzliche Reviews, längere Wiederaufnahmen und gegebenenfalls eigene Abschlusssessions können die tatsächliche Zahl erhöhen.
Die Dokumentation berücksichtigt solche Ausnahmen bereits. Ich würde lediglich deutlicher von einer Basisschätzung statt einer erwarteten Gesamtzahl sprechen.
Dokumentationsumfang
Die Arbeitspaketdateien enthalten teilweise sehr viel wiederholten Standardtext. Das ist nicht falsch, führt aber zu zusätzlichem Pflegeaufwand.
Ich würde den Umfang jetzt nicht grundlegend reduzieren. Die fachlichen Details sind wertvoll. Wiederkehrende Git-, Abgabe- und Testregeln könnten bei einer späteren Überarbeitung stärker auf ihre zentralen Referenzdateien verweisen.

4. Einschätzung zur tatsächlichen Umsetzbarkeit
Bereich	Bewertung
Fachliche Zielarchitektur	Sehr gut
Protokoll- und Serververträge	Gut bis sehr gut
Paketaufteilung und Reihenfolge	Sehr gut
Teststrategie und Nachweisführung	Sehr gut
Flexibilität während der Implementierung	Gut
Automatische Auswahl des nächsten Agentenschritts	Gut, mit Ausnahmen
Git-/Review-/Übernahmeablauf	Sehr gut
Wiederaufnahme und Sonderfälle	Verbesserungsbedarf
Besonders positiv finde ich, dass die verpflichtenden Servercheckpoints bereits ab CV2-010 beziehungsweise CV2-020 einsetzen. Damit wird ein wesentliches Integrationsrisiko deutlich früher erkannt als bei einer reinen Implementierung aller Clientkomponenten mit anschließendem Gesamttest.
Der Plan verspricht dabei nicht, dass bereits bestandene Servertests automatisch die neue Clientimplementierung qualifizieren. Diese Unterscheidung ist fachlich wichtig und korrekt.
Die Prüfung des ZIP-Pakets und der Git-Referenzen ersetzt allerdings keinen vollständigen Test der zukünftigen Implementierung. Insbesondere die beschriebenen Ablauf- und Recovery-Sonderfälle habe ich anhand der Regeln bewertet, nicht mit tatsächlich durchgeführten Agentenläufen simuliert.
5. Meine abschließende Empfehlung
Die Planung kann als Umsetzungsgrundlage beibehalten werden.
Ich sehe keinen grundlegenden Architekturwiderspruch, der eine Neuplanung der Client-V2-Entwicklung erfordern würde.


Ich würde vor dem Start von AP-CV2-000 insbesondere Befund 1, 2 und 3 nachbessern. Diese betreffen genau die Funktion, die dir später viel Arbeit abnehmen soll: Du gibst „Mach den nächsten Schritt“ ein, und der Agent erkennt zuverlässig selbst, was zu tun ist.
Befund 4 und 5 sollten ebenfalls verbindlich geklärt werden, können aber mit einer kleinen Ergänzung des vorhandenen Regelwerks behandelt werden. Befund 6 und die Revisionsmetadaten sind eher redaktionelle Nacharbeiten.
Wichtig ist mir dabei: Ich würde weder zusätzliche Pflichtarbeitspakete einführen noch weitere obligatorische Agentenrollen oder Reviews verlangen. Die vorhandene Struktur genügt. Es geht um die Behandlung einiger Ausnahmefälle, nicht um zusätzliche Bürokratie.
Fazit: Fachlich ist der Plan bereits weit genug, um damit zu entwickeln. Für einen weitgehend selbstständig funktionierenden Agentenworkflow würde ich diese wenigen Lücken vorher schließen. Eine gezielte Revision 10 reicht dafür aus.