# Bestehende Clientbereiche: erhalten, anpassen und ersetzen

Diese Übersicht betrachtet sowohl die vorhandene Featureentwicklung als auch den späteren V1-Release. Die Ausgangslinie ist der Featurestand; kompatible Releaseverbesserungen kommen im Baselinepaket hinzu. Details: [Branchbewertung](CLIENT_BRANCH_BEWERTUNG.md), [Migrationskarte](BASELINE_UND_MIGRATION.md).

| Bereich | Was erhalten bleibt | Was konkret geändert wird | Paket |
| --- | --- | --- | --- |
| Technische Plattform | Python 3.12, PySide6, Qt-Hauptthread, separater asyncio-Core, Win32-Hotkeys | sichere Übergaben und Generationguards; immutable Objekte als mögliche Lösung; keine neue Plattform | 000, 100 |
| Audio und Geräte | sounddevice-Capture, PCM16-Paketierung, Gerätelogik und Adapter | Sessionweiter kontinuierlicher Stream; Aufnahmebereitschaft/Deviceverlust statt Diktatstart-/stopgating | 010, 040 |
| Trigger-Vorarbeiten | zwei getrennte Quellen, ausdrückliche Flags vor altem mode, Ablehnung ist kein Verbindungsfehler | endgültiger Hello-/Commandvertrag, getrennte Laufzeitpausen, Controlrollen auch in Wake-only | 020, 050, 070 |
| WebSocket und Lifecycle | Generation-/Reconnectideen, Pendingkorrelation und Backofffoundation | /ws/v2, ausgehendes Hello, UUIDs, Commands/Acks; ready/start/stop/trigger_ack und Domainping ablösen | 010, 020 |
| Diktierzustand | Wunsch nach serverseitiger Autorität und korrekter Quellkorrelation | ein ActivationMirror; lokale Diktierfristen/extend und konkurrierende State-Machines entfernen | 030, 050, 100 |
| Segment-/Textverarbeitung | Finaltexte in Historie und Clipboardqueue; passives Interim, bewusstes Reinsert | UUID-/Activationherkunft, mehrere Segmente, alte Finals neben neuer Aufnahme, versionsfester Resync und Dedup | 030, 060 |
| Persistenz und Benutzerdaten | SQLite, bisherige Einträge/Attempts, Nutzerprofile; V1-Pfad-/CLIverbesserungen | transaktionale/idempotente Schema- und Configmigration mit Backup; kein stiller Reset | 000, 060, 070 |
| Feedback, Overlay, Sound und LED | bestehende Darstellungs-/Mapping-/LEFX-Ausgänge und Ausfallisolation | Domain-V2 als Zustandsautorität, gleicher Lifecycle für Manual/Wake, unabhängiger Backgrounddrain, kein Replayimpuls | 090 |
| Logs und Observability | SQLite-first-Logstream, Cursorstore, Redaction, Diagnose-UI und bounded Ingress | Tokenbootstrap an hello.accepted, korrekter Scope/Retentioncursor; kein Logtext als automatischer Final | 040, 090 |
| Einstellungen und Wake | lokale Präferenzen, Hotkey-Erfassung und vorhandene Flagmigration | echte Registry/Revisions-/Applypolicies, Katalogmehrfachauswahl, requested/effective, getrennte Session-/Adminseiten | 070, 080 |
| Neue Dienste | vorhandene Services und Komponenten werden weitergenutzt | neu: Wireparser, Mirror, Commandtracker, Settingsservice, Credential Manager und Finalresultservice | 010–080 |
| Packaging und Release | eindeutiger V1-Namespace, Ressourcen, VERSION/Commit, Build-/CI-/Publishguard | früh in Featurebasis integrieren; anschließend endgültigen V2-Build samt Kompatibilität neu qualifizieren | 000, 110 |
| Tests | Utility-/Audio-/Clipboard-/OBS-/GUI-/Buildtests; wertvolle Trigger-Race-/Feedbackassertions | alte Wire-/ID-/Timerannahmen einzeln ersetzen und nachweisen; keine pauschale Entfernung/Skipstrategie | alle |
| Branch- und Pakethistorie | kanonische Featurelinie, kumulativer Distributedverlauf, Releaseprovenienz | nachvollziehbare frühzeitige Portierung; später autorisierte Integration beider Historien | 000, Abschluss |

Die bereits implementierte Triggergrundidee reduziert Wiederentdeckungsarbeit, ersetzt aber die endgültige Wire-/Mirror-/Settingsumsetzung nicht. Vorhandene Komponenten werden weiterentwickelt; gerade der Lifecycle und seine Identitäten werden deutlich geändert. Neue Dienste sind gezielte Ergänzungen des vorhandenen Clients.

Ein fachlicher Test wird nur dann ersetzt, wenn seine neue Requirement und konkrete Nachfolgemethode benannt sind. Der Featuretest zum erneuten Streamstart nach Finish bleibt als offener Altbefund nachvollziehbar, bis kontinuierliches V2-Audio durch einen produktnahen Test belegt ist.
