# R06 – Admin-Abnahme und Freigabeentscheidungen (24.11.2026)

## Ergebnis
25/25 technische Checks PASS_SCOPED am korrigierten Quellclient mit echter Qt-Windows-Oberfläche und realer Final-Testinstanz (Servercommit e95858e3c010a7e9324b49bb44fee349abe7128a, Instanz 8e183f934fe14c81b515815615ca5ea3). Nutzer autorisierte die konkrete gespiegelte voice-stt.env ausdrücklich; VOICESTT_ADMIN_API_KEY nur im lokalen Testprozess gelesen, kein Schlüsselwert in Chat, Beleg, YAML oder Logs. Kein produktiver anderer Origin, keine SSH-Verbindung.

- Ohne Verifikation gesperrt; falscher Schlüssel abgelehnt; Defaults unverändert.
- Gültiger Schlüssel über echten Clientdialog erfolgreich geprüft (No-change, keine Revisionserhöhung); Editor und Apply freigeschaltet.
- Reversible Änderung über Clientdialog: activation.followupTimeoutMs 3000 -> 3100 ms, Revision 0 -> 1; ausschließlich erwarteter Requested-Wert geändert. Neue Session bestätigt wirksamen Wert 3100.
- Stale Revision (409) und falscher Schlüssel (401/403) serverseitig abgelehnt, keine Mutation.
- Reconnect entzieht alte Adminfreigabe; erneute Verifikation erfolgreich.
- Rücksetzung über Clientdialog 3100 -> 3000 ms, Revision 1 -> 2. Vollständiger Vergleich aller Requested-/Effective-Defaults mit Ausgangssnapshot identisch; neue Session bestätigt 3000 ms. Revision bleibt ordnungsgemäß monoton erhöht. Kein Notfall-Rollback erforderlich.
- Echter Windows Credential Manager: Speichern/Lesen/Löschen eines synthetischen Testschlüssels unter isoliertem Test-Origin erfolgreich. Reale gespeicherte Credentials nicht verändert; keine dauerhafte Speicherung des realen Admin-Keys. Kein vollständiger realer UI-Vault-Roundtrip behauptet.
- Vorheriger abgelehnter Versuch mit anderer Schlüsselquelle bleibt als historischer Nachweis erhalten. Neue Schlüsselquelle erfolgreich. Absichtlich ungültiges Audio-Gerät für Adminlauf erzeugte erwartete Capture-Fehler; kein Mikrofon/Paste-Test. Prozess Exit 0, Core/Tray beendet, gemeinsamer Cursor unverändert.

## Freigabeentscheidungen des Auftraggebers
- Historische spontane Verbindungsabbrüche werden ausdrücklich nicht als Releaseblocker gewertet. V10-07 historischer FAIL bleibt nachvollziehbar; aktuelle Freigabedisposition ACCEPTED_RISK hinsichtlich damaliger Abrisse. Wiederholte alte Fallback-Meldungen korrigiert; repräsentative Langzeitprüfung bleibt separat offen. Keine vollständige technische Fehlerfreiheit behauptet.
- F12: Redistributionsfreigabe laut Auftraggeber geklärt; kein Releaseblocker (USER_APPROVED). Keine eigene rechtliche Freigabe behauptet.
- Adminfunktionen sind ausdrücklich Bestandteil des Releases. F10 sowie V08-17 bis V08-21 mit neuen Nachweisen bewertet; V08-18 technisch isolierter Vault-Teilnachweis; V08-21 serverseitiger Negativtest plus UI-Sperre bei ungültigem Key und Reconnect. Kein Ausschluss der Adminfunktionen.

## Rest
Native Notepad-Einfügung/Zielwechsel, repräsentativer 30–60-Minuten-Frozen-Dauerbetrieb, vollständige physische Bewertung geänderter Feedbackvarianten und abschließende unabhängige Gesamtfreigabe verbleiben. Kein Produktcode verändert, kein Commit/Push/Merge/Release. Belege: EVIDENCE/ADMIN_ABNAHME_2026-11-24. 
