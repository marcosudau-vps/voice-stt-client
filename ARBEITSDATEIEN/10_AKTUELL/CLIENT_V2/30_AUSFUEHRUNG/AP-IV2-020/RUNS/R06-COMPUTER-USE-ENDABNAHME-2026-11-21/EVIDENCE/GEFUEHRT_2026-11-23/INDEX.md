# Geführter Desktop-Nachlauf · Belege

Die Dateien enthalten technische Metadaten, gekürzte Sitzungs-/Aktivierungskennungen und zwei Screenshots der isolierten Einstellungen. Rohprofil, Ereignisdatenbank, Audios und Debug-Dateien verbleiben lokal unter 'Nachweise/Folge-20261123-203715'. Die Zeitspuren benutzen ISO-Zeitstempel. Uhrzeiten im Bericht sind MEZ.

| Datei | Belegt |
|---|---|
| [Laufzeitspur](laufzeitspur.jsonl) | Native Hotkeys, Fensterentscheidungen, Aufnahme, Final, Pause und Reconnect bis zum regulären App-Stopp. |
| [Reizprotokoll](reize.jsonl) | Beginn und Ende der lokalen WAV-Wiedergaben. |
| [Editorereignisse](editor-ereignisse.jsonl) | Zeit, Länge und Fingerabdruck der eingefügten Zeichenfolgen. |
| [Final- und Paste-Metadaten](final-paste-metadaten.json) | History und Einfügeversuche, einmaliger echter Wake-Aufruf mit Ergebnisvergleich nach Wortpositionen. |
| [Idle-Schnitt](relay-cut-1.json) und [aktiver Schnitt](relay-cut-2.json) | Ausschließlich Verbindungen des Test-Relay geschlossen. [Aufnahmezeit beim zweiten Schnitt](cut-2.json) |
| [Dritter geplanter Schnitt](relay-cut-3.json) | Kontrollierter Sitzungswechsel nach dem ausstehenden Langfinal. |
| [Final-Instanz nach dem Ausfall](final-health-verlauf.jsonl) | Wieder erreichbare Testinstanz, Gesundheitsstatus und Server-Commit. |
| [Offline-Session](offline-session.jpg) und [Offline-Trigger](offline-trigger.jpg) | Fehlende Sessionwerte bei dennoch bejahter Wirksamkeit der Trigger im lokalen Register. |
| [Ressourcenstichproben](prozess-stichproben.jsonl) und [Auswertung](ressourcen-auswertung.json) | 62 ab 20:55 MEZ erhobene Messungen des App-Prozesses. |
| [Clipboard-Ersatz](clipboard-bestaetigt.json) | Explizit genehmigter Ersatz des zwischenzeitlich formatierten Clipboards durch Testtext. |
| [Abschluss](abschluss-kontrolle.json) und [Nachkontrolle](abschluss-nachkontrolle.json) | Hashvergleich der äußeren Dateien, wiederhergestellte Testkopie, App-/Relay-Ausstieg sowie Zustand des Onefile-Startprozesses. |
| [Onefile-Exitwarnung](onefile-exit-warning.jpg) und [Endkontrolle nach OK](abschluss-nach-ok.json) | Temporäres Entpackverzeichnis konnte nicht entfernt werden. Prozess nach Bestätigung beendet. |
| [Prüfsummen](sha256.json) | SHA-256 der Belegdateien dieses Ordners. |
