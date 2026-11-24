# R06 – Abschluss der technischen Anwenderabnahme (24.11.2026)

## Entscheidung: GO mit dokumentierten Restrisiken
Der Auftraggeber hat nach Kenntnis des letzten Dauerlaufbefunds ausdrücklich die bisherige Prüfung als ausreichend akzeptiert und die Beendigung der technischen Abnahme beauftragt. Kein weiterer ununterbrochener 30–60-Minuten-Lauf oder erneuter Sicht-/Hörtest gefordert. Das ursprüngliche Dauerlaufkriterium wird für diese Abnahme durch die dokumentierten repräsentativen kombinierten Nachweise und die ausdrückliche Ausnahmeentscheidung ersetzt. Historische Befunde und ursprüngliche Sollkriterien bleiben unverändert erhalten.

Auftraggeberbestätigung: „Lass uns das jetzt so abschließen, weil ich denke, dass das genug getestet. Sind jetzt keine neuen Probleme irgendwie aufgetreten. Und ich denke, das ist so ausreichend“.

## Kandidat und Nachweise
- Korrigierter lokaler Frozen-Kandidat SHA-256 07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe; lokaler Arbeitsstand auf Basis 17fce388e747daf37b97e96ed1fcf6421338873d, dirty. Final-Testserver e95858e3c010a7e9324b49bb44fee349abe7128a.
- Korrekturlauf: 1414 Tests erfolgreich; weitere gezielte Regressionen, native Qt-/Windows-Tests, akustische Kurzserien (eine vollständige Serie 10/10), Langdiktat 209 s mit sieben Finals; manuelle Sicht-/Hörbeobachtung sowie echter Wake-Trigger vom Auftraggeber bestätigt (Berichte 10–18).
- Native Neubelegung, LED-/Soundkonfiguration, Frozen-Start und Idle-Ressourcenmessung (19–20); Admin-Freischaltung, Änderungs-/Rücksetztransaktion auf Final-Testinstanz, 25/25 technische Checks (21–22). Adminfunktionen im Freigabeumfang; Redistributionsfreigabe durch Auftraggeber bestätigt.
- Native Notepad- und Zielwechselprüfung 13/13 technische Checks, beide Finals exakt eingefügt, Clipboard wiederhergestellt (23–24).
- Letzter Frozen-Dauerlauf (26): 1110,09 s (18 min 30 s), 12 echte Aktivierungen, 12 abgeschlossene Finals, 12 exakte Einfügungen einschließlich Clipboard-Restore, keine Duplikate. Private MiB 465,664 -> 478,660 (+12,996), Spitze 478,660, mittlere Prozess-CPU 4,785 % eines logischen Kerns. Keine alten irreführenden Fallback-Meldungen. Kein Nachweis eines Speicherlecks aus diesem begrenzten Intervall.

## Abgrenzung und akzeptierte Restrisiken
- ASR-Textqualität: 6/12 akustische Sollmarker vollständig; alle 12 Serverfinals korrekt in den Zieltext übernommen. Der Client transkribiert nicht selbst. Modell/akustische Teststrecke sind mögliche Ursachen der Markerabweichungen, keine gesicherte Ursachenanalyse; clientseitige Audioerfassung und Transport bleiben Teil der Systemkette. Kein nachgewiesener Fehler der Texteinfügung. Keine Behauptung vollständiger ASR-Qualifikation.
- Dauerlauf endete ACTIVATION_TIMEOUT mit audio_send_failed/network_lost und erfolglosen Reconnectversuchen; Server-Readback am Ende nicht verfügbar. Anbietertrennung laut Auftraggeber plausible, unbestätigte Ursache. Shutdown musste erzwungen werden (Exit 1, ein _MEI-Rest, eine ERROR-Zeile); kein sauberer Exit in diesem speziellen Lauf. Frühere saubere Frozen-Exits und kontrollierte Recovery belegt; Restbefund nicht releaseblockierend gemäß ausdrücklicher Abschlussentscheidung. Kein nachträgliches Umdeuten des Dauerlaufs in einen vollständigen PASS.
- Noch nicht vollständig physisch bestätigte geänderte Feedbackvarianten und sonstige PASS_SCOPED-Grenzen: technische Nachweise und frühere Nutzerbeobachtungen akzeptiert, keine weitere Abnahmerunde gefordert.
- V10-01 und V10-07 ACCEPTED_RISK; F09 PASS_SCOPED mit akzeptiertem verkürztem repräsentativem Nachweis; F12 USER_APPROVED. Alle verbleibenden Teilnachweise werden vom Auftraggeber im vorliegenden Umfang akzeptiert.

## Abschluss
136 Kriterien: 65 historisch PASS, 65 PASS_SCOPED, 2 ACCEPTED_RISK, 1 USER_APPROVED, 3 N/A; 0 BLOCKIERT und 0 aktuelle FAIL-Dispositionen. Keine ausstehenden Anwender-/Laufzeitprüfungen als Freigabeblocker. Maßgebliche Matrix: 28_FINALER_ABNAHMESTATUS_2026-11-24.md. Das ist die abschließende technische Anwenderabnahme mit Auflagen, keine Behauptung 133 uneingeschränkt technisch bestandener Kriterien.

Unabhängiger paketbezogener Review/kanonische Übernahme nach AGENTS.md bleibt getrennte formale Release-/Integrationsaufgabe. Kein neuer ROOT_PASS, kein Commit, Push, Merge, Tag, Veröffentlichung oder Produktcodeänderung in diesem Abschlussschritt. Historische Workflow-/Reviewentscheidungen bleiben unangetastet. Die Abnahme ist auf Auftraggeberseite abgeschlossen; der lokale Kandidat und die Nachweise sind zur formalen Weiterverarbeitung bereit.

## Abnahmebescheinigung und Gültigkeit

- [PDF-Abnahmebescheinigung](Voice-STT-Client-V2_Abnahmebescheinigung_2026-11-24.pdf)
- [Commitbindung und gezielte Regressionstests](29_GUELTIGKEIT_DER_RELEASE_FREIGABE_2026-11-24.md)
