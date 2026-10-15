# V2-Finalresultate und Historyschema – AP-CV2-060

Stand 2026-10-12. Der Resultservice konsumiert ausschließlich vom ActivationMirror emittierte Finals. Snapshotsegmentlisten und Logereignisse sind keine Ausgabesource. Appkomposition folgt in AP-CV2-100; `.\venv\Scripts\python.exe -m voice_stt_client` verwendet weiterhin die bestehende Komposition.

## Integration und Reihenfolge

`STTController.attach_v2_results(connection: V2MirrorConnection)` genau einmal vor Sessionadmission aufrufen. Er bindet einen `V2ResultService` an vorhandene History und serielle `TextInjectionQueue`. Alternativ `V2ResultService(history, queue, connection)` für headless Integration. `consume(Reduction)` wird synchron im Core in Serverpublikationsfolge aufgerufen. Mehrere salvagierte Finals einer Reduction werden nach event_seq geordnet. Parallele fremde Aufrufer müssen die Reductionfolge bewahren; der interne Lock verhindert doppelte Sideeffects, rekonstruiert aber keine beliebig umsortierten Aufrufe.

`ResultOutcome` ist unveränderlich: status, final (`FinalResult`), generation, entry_id, reason, is_conflict. FinalResult enthält session_id, activation_id, segment_id, segment_sequence, event_id, event_seq und text. Der Controller liefert diese Herkunft auch in `FinalProcessingResult`. Herkunft folgt dem Final und bleibt bei einer anderen Vordergrundactivation erhalten; der Legacy-Cancel-Schalter unterdrückt veröffentlichte V2-Finals nicht.

Der Service verarbeitet und reserviert zuerst, ruft danach `on_result(outcome)` synchron außerhalb seines Locks auf und dann den zuvor angeschlossenen Reductioncallback. `on_attempt_result(attempt)` läuft im Injectionworker nach Abschluss des gespeicherten Versuchs. Weil der Worker parallel arbeitet, besteht keine garantierte Gesamtordnung zwischen Result- und Attemptcallback. Callbackfehler werden isoliert. Qt-Verbraucher müssen wie bisher in den UI-Thread marshallen.

Erster Terminalzustand eines Segments ist endgültig. Nur nichtleerer completed-Text darf automatisch ausgeben. Dedup gilt pro Session/Segment unabhängig von History enabled und Rotation; gleiche Texte verschiedener Segmente bleiben getrennte Ergebnisse. Der aktuelle Sessionledger bleibt bis neuer Generation oder close erhalten. Falsche Session, frühere Generation und bereits getrennte Verbindung werden verworfen. `close()` sperrt neue Reductions; bereits angenommene Jobs werden beim regulären Queuestopp fertig abgearbeitet. Cancel und Disconnect löschen keine veröffentlichten Texte.

## SQLite-Migration und Speicherung

Vor der V1-Migration erstellt History eine SQLite-Backupkopie `<Datenbankname>.v1-backup.sqlite` im selben Verzeichnis; eine vorhandene Kopie wird nicht überschrieben. Die SQLite-Backup-API erfasst auch WAL-Inhalte. BEGIN IMMEDIATE und transaktionales DDL ermöglichen Rollback zum alten Schema. Ein zweiter Start migriert oder ändert das Schema nicht erneut. Eine unbekannte neuere Schemaversion wird unverändert abgewiesen.

Schema user_version=2: segment_id TEXT und protocol_version (1/2), activation_id, segment_sequence, event_id, event_seq, primary_source, activation_sequence. Legacy-Segmentnummern werden im Python-API weiter als int gelesen; protocol_version=1 und neue Herkunftsfelder NULL. IDs, Zeitstempel, Text und Attempts bleiben erhalten. Unique ist protocol_version/session_id/segment_id; Attempts behalten FK und ON DELETE CASCADE. Es werden keine Legacy-UUIDs erfunden. Datenbankpfad und History-/Persistenz-/Retentionspräferenzen bleiben bestehen.

`reserve_injection(entry, source)` mit source automatic oder manual liefert einen PENDING-Versuch vor Clipboard/SendInput; `finish_injection(attempt_id, status, error_message)` finalisiert denselben Versuch. `enqueue_reserved(entry)` und `enqueue_manual(entry)` bilden diesen Vertrag ab. V2-Automatik und bewusstes Reinsert verwenden ihn. Gefilterte oder deaktivierte Historie reserviert prozesslokal gemäß Nutzerpräferenz; dauerhaftes Crashtracking ist dann nicht verfügbar. Fehlgeschlagene Ausgabe kann gemäß bestehender Speicherregel nachträglich mit vollständiger Herkunft aufgenommen werden.

Bei notwendiger Persistenz und fehlgeschlagener Reservierung findet keine Einfügung statt: Queuefehler injection_reservation_failed und History.last_error sind sichtbar. Mirror und Audio bleiben verfügbar. Pendingversuche werden beim Wiederöffnen als unknown markiert; keine automatische Wiederholung. Bei Statuscommitfehler bleibt der Versuch unknown im Speicher bzw. pending auf Datenträger bis Wiederöffnung. Pendingversuche sind bis Abschluss von automatischer Retention ausgenommen. Bewusste Löschung bleibt endgültig und wird vom Worker nicht rückgängig gemacht.

## Textinjektion und Grenzen

Bestehende Clipboard-/SendInputmechanik, Konflikterkennung und Restore bleiben erhalten. SendInputfehler, einschließlich möglicher Blockierung durch ein höher privilegiertes Ziel, werden als failed protokolliert. Es gibt keine neue Privilegienanhebung oder Zielkontrolle. command_sent bezeichnet einen abgesandten Einfügebefehl, keinen Beweis der Übernahme durch eine fremde Anwendung. Reinsert ist eine neue ausdrückliche Benutzernebenwirkung mit source=manual.

Ergänzung AP-IV2-020/UX01, 2026-10-15: Die bestehende Einstellung
`text_injection.append_space` (Default True, „Leerzeichen anhängen“) ergänzt
ausschließlich im Clipboard-Ausgabetext ein Leerzeichen, wenn der nichtleere
Originaltext noch nicht mit Whitespace endet. Vorhandene Leerzeichen, Tabs und
Zeilenumbrüche bleiben exakt erhalten. Bei False wird der Originaltext exakt
ausgegeben. Dies gilt auch für bewusst angeforderte Wiedereinfügung.
Finaltext, unveränderlicher Queuejob, Historytext/-länge, Herkunft und
Deduplizierung behalten den Originaltext. Der Clipboard-Restorevertrag gilt
unverändert. [Freigabe und Nachweise](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/ux01/INDEX.md).

[Runakte](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/01_REPORT.md): echte temporäre SQLite-Dateien, fünf Prozessabbrüche und gepinnter Server über TCP/WebSocket bis zum echten Clientworker. Recorder-/Modellergebnisse und Clipboard/SendInput sind benannte Testadapter. Echte Mikrofon-/ASR-/Fokus-/Anwendungsabnahme folgt in AP-IV2-020. API-Keys und Nutzeraudio bleiben außerhalb der Repositorybelege.
