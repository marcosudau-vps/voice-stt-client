# Verantwortlichkeit und unabhängige Prüfung realer Nachweise

Stand 2026-10-11, Revision 10. Gilt für die dem aktuellen Paket zugeordneten Windows-/Hardware-/Modellfälle aus [Testplan](TEST_UND_ABNAHMEPLAN.md), [Checkpoints](INKREMENTELLE_CHECKPOINTS.md) und Paketdatei. Es werden keine neuen Pflichtfälle eingeführt. IV2-020 prüft die vollständige reale Matrix; frühere Pakete nur ihre zugeordneten Fälle.

## Durchführung

Der Umsetzer organisiert vor Abgabe die verpflichtenden Plattformnachweise. Er kann sie auf zugänglichem Windows selbst durchführen. Fehlt Zugriff, darf der Auftraggeber oder ein im tatsächlichen Auftrag benannter Bediener sie nach dem dokumentierten Testablauf ausführen. Das erfordert keine zusätzliche Agentenrolle. Der Reviewer darf vollständige Nachweise einer solchen Durchführung fachlich anerkennen; er bezeichnet sie ausdrücklich als **extern durchgeführt und unabhängig geprüft**, nicht als eigene Hardwaredurchführung.

Ein headless PASS ersetzt weder globale Windows-Hotkeys in CV2-050 noch reale Credential-Manager-Vorgänge in CV2-080 noch die realen Clipboard-/ReSpeaker-/ASRfälle in IV2-020. Fehlender Pflichtfall bleibt NOT_RUN/NOT_PROVEN und verhindert den Paket-PASS. Weder Auftraggeber noch Reviewer können ihn durch eine bloße Aussage als bestanden setzen.

## Minimaler Belegsatz je Pflichtfall

- Fall-/Requirement-ID, tatsächlicher Tester und Zeitpunkt; genaue Schritte, erwartetes und tatsächliches Resultat, PASS/FAIL mit Einschränkungen.
- Getestete Client-SHA/Tree; bei installiertem/frozen Produkt Build-/Artefaktidentität und SHA256, nachvollziehbar diesem Quellstand zugeordnet. Bei Serverbezug Server-SHA/Imageidentität, effektive Settings/Modellstand; Betriebssystem, relevante Hardware/Treiber und Rechtekontext.
- Geeignete überprüfbare Evidenz: beispielsweise redigierter Befehls-/Testlog, Wire-/Statusspur, beobachtbare Ausgabe oder gezielte Bildschirm-/Videoaufnahme. Die Belegform richtet sich nach dem Fall; kein Pflichtvideo für jeden Test. Allein „funktioniert bei mir“ ist unzureichend.
- Indexierter erreichbarer Belegpfad mit Herkunft und bei externen/binären Artefakten Hash. Secrets/Nutzerdaten redigieren; keine Rohcredentials, privaten Transkripte oder privaten Sprachaufnahmen in Git.

## Pflicht des unabhängigen Reviewers

1. Kandidaten-/Build-/Serveridentität und Vollständigkeit aller dem Paket zugeordneten Fälle selbst gegen Git, Artefakte und tatsächlichen Testablauf prüfen. Fachliche Änderungen nach der Durchführung erfordern Wiederholung der betroffenen Fälle; administrative Reviewunterlagen allein nicht.
2. Code/Diff, kritische automatisierbare Repros und vollständige vorgeschriebene Regression eigenständig prüfen/ausführen. Steht ein erforderlicher Plattformtest nur auf Windows zur Verfügung, dessen Ausführung auf einem erreichbaren Prüfhost anstoßen; bei fehlendem direkten Zugriff den tatsächlichen Bediener die vom Reviewer benannten Befehle/Fälle ausführen lassen. Vollständige Ausgabe und Runtimeidentität prüfen, Eigen- und Fremdausführung getrennt protokollieren. Unpassende Linux-Skips gelten nicht als Windows-Erfolg.
3. Reale Fremdbelege auf erwartete Wirkung, Fehler-/Nebenwirkungen, Identität und Widersprüche überprüfen. Eine vollständige Wiederholung sämtlicher Hardwarefälle ist nicht automatisch nötig. Bei eigener verfügbarer Hardware die für Befunde/kritische betroffene Änderungen notwendigen Smokes selbst wiederholen; bei fehlendem Zugriff konkrete Rückfragen oder gezielte Wiederholungen durch den Bediener verlangen, sofern die Belege nicht ausreichen. Bleibt eine Pflichtwirkung unbelegt, CHANGES_REQUIRED/BLOCKED statt PASS.
4. Im eigenen Reviewreport Quelle und Prüfentscheidung je externem Fall sowie selbst ausgeführte Prüfungen getrennt nennen. Keine Behauptung unabhängiger Durchführung, wenn lediglich fremde Evidenz geprüft wurde. Das unabhängige Urteil bleibt Revieweraufgabe; der spätere menschliche Übernahmeprompt bleibt davon getrennt.

Ein technisches Paketurteil ROOT_PASS darf auf so validierten echten Plattform-/Hardwarebelegen beruhen. ACCEPTED/CANONICALIZED bezeichnet weiterhin erst die tatsächlich menschlich freigegebene kanonische Übernahme. Diagnose und redigierte Belege werden in der bestehenden Paketakte geführt, ohne zweiten vollständigen Testkatalog.
