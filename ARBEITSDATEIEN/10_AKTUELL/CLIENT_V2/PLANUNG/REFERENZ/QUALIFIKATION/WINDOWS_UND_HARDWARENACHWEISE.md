# Verantwortlichkeit und unabhängige Prüfung realer Nachweise

Stand 2026-10-11, Revision 10. Gilt für die dem aktuellen Paket zugeordneten Windows-/Hardware-/Modellfälle aus [Testplan](TEST_UND_ABNAHMEPLAN.md), [Checkpoints](INKREMENTELLE_CHECKPOINTS.md) und Paketdatei. Es werden keine neuen Pflichtfälle eingeführt. IV2-020 prüft die vollständige reale Matrix; frühere Pakete nur ihre zugeordneten Fälle.

## Durchführung

Die vollständige Windows-Clientsuite gehört verbindlich in den Umsetzungs- bzw. Korrekturlauf. Vor REVIEW_READY muss ihr grüner Nachweis im Paket-PR vorliegen. Ein unabhängiger Review in einer ChatGPT-Session ist zulässig und erfordert keine erneute Windows-Vollsuite durch den Reviewer oder einen von ihm beauftragten Prüfhost. Der Reviewer prüft den Kandidaten fachlich und die Gültigkeit des vorhandenen Testnachweises; die unabhängige Entscheidung wird nicht durch eine zweite identische Testausführung hergestellt.

Für die Vollsuite enthält die bestehende Runakte den getesteten Commit bzw. Basis plus eindeutigen Diff, Windows-/Python-/Runtimeidentität, vollständigen Befehl mit Testauswahl, Exitcode, Testzahl und vollständigen erreichbaren Log. Der eingereichte Kandidat muss denselben Produkt-, Test- und testrelevanten Konfigurations-/Abhängigkeitsstand enthalten. Rein administrative Nachträge sind durch ihren Diff belegbar und erfordern keinen neuen Volltest. Nach fachlichen oder testrelevanten Änderungen qualifiziert der Umsetzer den neuen Stand erneut. Ein bloßes grünes CI-Symbol ohne erreichbaren, zum Kandidaten passenden Nachweis genügt nicht.

Der Umsetzer organisiert vor Abgabe die verpflichtenden Plattformnachweise. Er kann sie auf zugänglichem Windows selbst durchführen. Fehlt Zugriff, darf der Auftraggeber oder ein im tatsächlichen Auftrag benannter Bediener sie nach dem dokumentierten Testablauf ausführen. Das erfordert keine zusätzliche Agentenrolle. Der Reviewer darf vollständige Nachweise einer solchen Durchführung fachlich anerkennen; er bezeichnet sie ausdrücklich als **extern durchgeführt und unabhängig geprüft**, nicht als eigene Hardwaredurchführung.

Ein headless PASS ersetzt weder globale Windows-Hotkeys in CV2-050 noch reale Credential-Manager-Vorgänge in CV2-080 noch die realen Clipboard-/ReSpeaker-/ASRfälle in IV2-020. Fehlender Pflichtfall bleibt NOT_RUN/NOT_PROVEN und verhindert den Paket-PASS. Weder Auftraggeber noch Reviewer können ihn durch eine bloße Aussage als bestanden setzen.

## Minimaler Belegsatz je Pflichtfall

- Fall-/Requirement-ID, tatsächlicher Tester und Zeitpunkt; genaue Schritte, erwartetes und tatsächliches Resultat, PASS/FAIL mit Einschränkungen.
- Getestete Client-SHA/Tree; bei installiertem/frozen Produkt Build-/Artefaktidentität und SHA256, nachvollziehbar diesem Quellstand zugeordnet. Bei Serverbezug Server-SHA/Imageidentität, effektive Settings/Modellstand; Betriebssystem, relevante Hardware/Treiber und Rechtekontext.
- Geeignete überprüfbare Evidenz: beispielsweise redigierter Befehls-/Testlog, Wire-/Statusspur, beobachtbare Ausgabe oder gezielte Bildschirm-/Videoaufnahme. Die Belegform richtet sich nach dem Fall; kein Pflichtvideo für jeden Test. Allein „funktioniert bei mir“ ist unzureichend.
- Indexierter erreichbarer Belegpfad mit Herkunft und bei externen/binären Artefakten Hash. Secrets/Nutzerdaten redigieren; keine Rohcredentials, privaten Transkripte oder privaten Sprachaufnahmen in Git.

## Pflicht des unabhängigen Reviewers

1. Kandidaten-/Build-/Serveridentität und Vollständigkeit aller dem Paket zugeordneten Fälle selbst gegen Git, Artefakte und tatsächlichen Testablauf prüfen. Fachliche Änderungen nach der Durchführung erfordern Wiederholung der betroffenen Fälle; administrative Reviewunterlagen allein nicht.
2. Vollständigen Code-/Testdiff unabhängig prüfen und die vorhandenen Windows-Vollsuitenbelege auf Kandidatenbezug, Vollständigkeit, Ergebnis sowie unerlaubte Skips/Testabschwächungen kontrollieren. Keine routinemäßige Wiederholung der Windows-Vollsuite verlangen. Bei konkretem neuem Fehlerverdacht, widersprüchlichen/unvollständigen Belegen oder geändertem Teststand gezielte Repros bzw. nötige erneute Qualifikation an den Umsetzer zurückgeben. Eigene ausführbare Prüfungen sind ergänzend möglich; unpassende Linux-Skips gelten nicht als Windows-Erfolg.
3. Reale Fremdbelege auf erwartete Wirkung, Fehler-/Nebenwirkungen, Identität und Widersprüche überprüfen. Eine vollständige Wiederholung sämtlicher Hardwarefälle ist nicht automatisch nötig. Bei eigener verfügbarer Hardware die für Befunde/kritische betroffene Änderungen notwendigen Smokes selbst wiederholen; bei fehlendem Zugriff konkrete Rückfragen oder gezielte Wiederholungen durch den Bediener verlangen, sofern die Belege nicht ausreichen. Bleibt eine Pflichtwirkung unbelegt, CHANGES_REQUIRED/BLOCKED statt PASS.
4. Im eigenen Reviewreport Quelle und Prüfentscheidung je externem Fall sowie selbst ausgeführte Prüfungen getrennt nennen. Keine Behauptung unabhängiger Durchführung, wenn lediglich fremde Evidenz geprüft wurde. Das unabhängige Urteil bleibt Revieweraufgabe; der spätere menschliche Übernahmeprompt bleibt davon getrennt.

Ein technisches Paketurteil ROOT_PASS darf auf so validierten echten Plattform-/Hardwarebelegen beruhen. ACCEPTED/CANONICALIZED bezeichnet weiterhin erst die tatsächlich menschlich freigegebene kanonische Übernahme. Diagnose und redigierte Belege werden in der bestehenden Paketakte geführt, ohne zweiten vollständigen Testkatalog.

Im Reviewreport Windows-Vollsuite als **im Umsetzungslauf durchgeführt, Nachweis unabhängig geprüft** ausweisen. Die eigene Wiederholung darf NOT_RUN sein, ohne den PASS zu blockieren, wenn der vorgeschriebene Test selbst nachweislich bestanden ist. Fehlt dagegen der gültige Vollsuitennachweis, bleibt das Pflichtkriterium offen. Historische R02/R04-Urteile behalten ihren damaligen Wortlaut; die neue Aufgabenverteilung gilt ab dieser Nutzerfestlegung.
