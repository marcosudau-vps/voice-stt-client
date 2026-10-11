# Umfang und Agentenläufe pro Arbeitspaket

Stand 2026-10-11, Planrevision 10; Aufwandsmodell Version 3 (fachlich unverändert). **Regelfall: ein vollständiger Umsetzungslauf je Paket, anschließend ein unabhängiger Abnahmelauf.** Die Facharbeit nutzt die bestehenden Clientkomponenten. Technische Schritte innerhalb eines Pakets sind keine automatisch getrennten Sessions.

| Paket | Umsetzung im Regelfall | Unabhängige Abnahme / Abschluss | Schwerpunkt |
| --- | ---: | ---: | --- |
| [AP-CV2-000](../../ARBEITSPAKETE/AP-CV2-000.md) | 1 | 1 | Feature-/Releaseinventar und Übernahmematrix; Namespace, Releasepolish und Triggererhalt integrieren |
| [AP-CV2-010](../../ARBEITSPAKETE/AP-CV2-010.md) | 1 | 1 | Datentypen, Decoder und Commands/Acks/Events; Audioencoder, Vertragsvektoren und Negativfixtures |
| [AP-CV2-020](../../ARBEITSPAKETE/AP-CV2-020.md) | 1 (ggf. 2) | 1 | Verbindung, Hello, Bootstrapzustände und Close-/Backoffregeln; Commandtracker, Ack-/Retry-/Generationguards und Transporttests |
| [AP-CV2-030](../../ARBEITSPAKETE/AP-CV2-030.md) | 1 (ggf. 2) | 1 | Foreground-/Activation-/Segmentreducer; Snapshot, Resyncpuffer, Verluststatus und Tombstones |
| [AP-CV2-040](../../ARBEITSPAKETE/AP-CV2-040.md) | 1 | 1 | Audio-/Deviceintegration und vorhandenen Logbootstrap anpassen |
| [AP-CV2-050](../../ARBEITSPAKETE/AP-CV2-050.md) | 1 | 1 | Hotkeyrollen, Controlrouting und atomare Registrierung; Run-Suppression und Phasen-/Restartmatrix |
| [AP-CV2-060](../../ARBEITSPAKETE/AP-CV2-060.md) | 1 | 1 | UUID-Historymigration und Finalresult-/Dedupservice; Injectionattempts, Crashunklarheit und Queue-/Reinsertintegration |
| [AP-CV2-070](../../ARBEITSPAKETE/AP-CV2-070.md) | 1 | 1 | Persistierte Configmigration und HTTP-/Katalogservice; Settingsrevisionen, Patch/Applypolicies und Bootstrap |
| [AP-CV2-080](../../ARBEITSPAKETE/AP-CV2-080.md) | 1 | 1 | Settings-/Katalog-/Requested-effective-Oberfläche; Credential Manager, Adminprüfung und Apply-/Drainentscheidungen |
| [AP-CV2-090](../../ARBEITSPAKETE/AP-CV2-090.md) | 1 | 1 | bestehendes Feedback an V2-Eingänge/Herkunft anpassen |
| [AP-CV2-100](../../ARBEITSPAKETE/AP-CV2-100.md) | 1 | 1 | Tatsächliche App/Core/Qtverdrahtung und Readymarkierung; Integrierte Fehler-/Shutdown-/Rollbacktests mit realen Klassen |
| [AP-CV2-110](../../ARBEITSPAKETE/AP-CV2-110.md) | 1 | 1 | Gezielter Legacyabbau, Version-/Ressourcen-/Kompatibilitätsabgleich; Executable/wheel/sdist und Installations-/GUIsmokes |
| [AP-IV2-010](../../ARBEITSPAKETE/AP-IV2-010.md) | 1 | 1 | Echte Client-/Serverprozessintegration mit WS/HTTP/Logs; Komplette Race-/Settings-/Recoverymatrix und Paarqualifikation |
| [AP-IV2-020](../../ARBEITSPAKETE/AP-IV2-020.md) | 1 | 1 | Reale Windows-/ASR-/Bedien-/Clipboard-/Credential-Prüfung; ReSpeaker/USB/Wakepositive-/Negativ-/Nutzsprachgrenze |
| [AP-SV2-FIX](../../ARBEITSPAKETE/AP-SV2-FIX.md) | befundabhängig | separat | Nur bei einem konkreten reproduzierbaren Serverbefund separat schätzen |

**Basisschätzung ohne Korrekturen: 14 Umsetzungssessions + 14 unabhängige Abnahmesessions = 28 Agentensessions.** Ein zusätzlicher Umsetzungslauf kommt allenfalls bei Transport oder Mirror/Resync in Betracht, wenn sich während der Umsetzung ein konkreter Bedarf zeigt; damit **28–30 Basissessions**. Dies ist keine Prognose der Gesamtzahl einschließlich Korrekturen, Zusatzreviews, Wiederaufnahmen, Serverfixes oder gesondert beauftragter Abschluss-/Ausnahmesessions.

Die Hälfte der regulären Sessions entfällt auf die ausdrücklich gewünschte unabhängige Abnahme pro Paket. Das ist keine zusätzliche Verdoppelung der Implementierung. Ein Review umfasst technische Prüfung und PASS-/Befundbericht. Nach ausdrücklichem Auftraggeberprompt übernimmt vorzugsweise der Umsetzer die kurze kanonische Abschlussaktion im bestehenden Lauf; alternativ ein ausdrücklich beauftragter Abschlussagent. Diese Übernahme wird nicht pauschal als dritte Fachsession pro Paket eingeplant.

Korrekturläufe und erforderliche erneute Reviews kommen nur nach tatsächlichem Befund hinzu. Es wird kein Vorrat von drei oder vier Korrekturen je Paket geplant. Eine belastbare Zahl dafür gibt es vorab nicht. User-/Hardware-/CIwartezeit und Usage-Reset-Fortsetzungen eines noch offenen Runs sind keine neuen Umsetzungspakete. Das bedingte Serverfixpaket wird erst bei einem konkreten Defekt zusätzlich geschätzt.

## Warum die Schätzung kleiner ist

Die erste Aufteilung behandelte Parser, Tests, Serviceverdrahtung und Fehlerfälle zu oft als eigenständige Agentenaufträge. Hier steht das Ziel weitgehend fest, und ein vollständiger Paketlauf kann diese Arbeit zusammen durchführen.

Logging, Observability, Feedbackreducer, Mapping, LED-/Soundadapter, GUIgrundlagen, Clipboard und Audiofoundation sind vorhandener Bestand. Ihr System wird nicht neu gebaut. Geändert werden die nötigen Kommunikations-/Identitäts-/Bootstrapanschlüsse. Neue fachliche Arbeit konzentriert sich auf endgültigen V2-Transport, Commands/Acks, serverautoritativen Mirror, Resync, Ergebnisidentität und Settingsvertrag.

Auch Namespace-/Releaseübernahme in CV2-000 ist ein zusammenhängender Integrationsauftrag, keine automatisch dreistufige Kampagne. Die übrigen Pakete werden grundsätzlich in einer gut formulierten Session vollständig umgesetzt und getestet. Ein langer Run darf fortgesetzt werden, statt künstlich neue Läufe zu erzeugen.

## Praktische Ausführung

1. Genau einen vollständigen Paketprompt mit Zielen, erlaubten Dateien, Kontrakten, Tests und DoD erstellen.
2. Gezielte Tests, vollständige Regression und Dokumentation gehören in denselben Umsetzungslauf.
3. Danach frischer unabhängiger Abnahmelauf; kein Eigen-PASS des Umsetzers.
4. Reviewer liefert PASS oder konkrete Befunde. Die Übernahmefreigabe kommt **ausschließlich per Prompt des Auftraggebers**.
5. Erst nach dieser Freigabe den einen Aggregatecommit/Push ausführen und das Paket schließen.
6. Ein zusätzlicher Fachlauf wird mit realem Restumfang oder Befund begründet, niemals allein mit der vorhandenen Liste technischer Unteraufgaben.

Die AP-Dateien beschreiben Arbeitsschritte innerhalb eines Pakets. [Implementierungsplan](IMPLEMENTIERUNGSPLAN.md) und [Agentenregelwerk](../GOVERNANCE/AGENTEN_REGELWERK.md) verwenden diese schlanke Zählweise.
