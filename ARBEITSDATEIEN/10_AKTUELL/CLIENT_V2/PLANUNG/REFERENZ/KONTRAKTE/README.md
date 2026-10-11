# Finale Kontrakte der Planungsbaseline

Server: `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Der Begriff „final“ bedeutet hier: auf diesen Commit bezogene, umsetzungsreife Referenz. Er verhindert keine ausdrücklich dokumentierte Korrektur während der Cliententwicklung.

| Kontrakt | Inhalt |
| --- | --- |
| [K-01 Wire, Audio und Commands](K-01_WIRE_AUDIO_COMMANDS.md) | `/ws/v2`, Hello, UUIDs, Commands, 15 Resultcodes, Byteformat, Close-Verhalten |
| [K-02 Events, Spiegel und Ergebnisse](K-02_EVENTS_MIRROR_ERGEBNISSE.md) | 18 Events, Snapshot, Versionen, Races, Resync, Final-Pipeline |
| [K-03 Settings und Wake Words](K-03_SETTINGS_WAKE_WORDS.md) | 18 Registryfelder / 16 Sessionfelder, REST-Antworten, Apply-Lücken, Katalog |
| [K-04 Logs, Auth und Recovery](K-04_LOGS_AUTH_RECOVERY.md) | separate Logsequenz, Bootstrapberechtigung, HTTP-Auth, Geräte- und Sessionverlust |

[Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md) unterscheidet Serververtrag, Produktanforderung, interne Lösungsvorschläge und lokale technische Startwerte. Die Kontrakte enthalten diese unterschiedlichen Arten ausdrücklich; die Bezeichnung „final“ friert keinen internen Modulplan ein.

Wirefeldnamen sind exakt und unverändert zu übernehmen. Unbekannte additive Felder bleiben toleriert; unbekannte Events werden nur für Sequenzfortschritt verarbeitet, wenn ihre gemeinsame Hülle gültig ist. Unbekannte Nachrichtentypen ohne Eventhülle erzeugen keine Zustandsänderung.

Die JSON-Dateien unter `VEKTOREN/` sind Ergänzungen, keine vollständige Schemavalidierung. Die Servervektoren stammen bytegleich aus dem festgelegten Commit. Settingsmetadaten werden aus der tatsächlichen Registry exportiert; Client-Szenarien sind neue Prüfspezifikationen mit erwarteten Wirkungen. Keine Erwartung eines neuen Tests darf ein nicht vorhandenes Serverfeature als implementiert ausgeben.

Nachweise sind im [Quellenmanifest](../../EVIDENCE/source-manifest.json) mit Repository, Pfad, SHA und Prüfsumme festgehalten. Die vier Kontrakte enthalten alle für die Umsetzung benötigten Regeln; das Öffnen externer Planungsunterlagen ist nicht erforderlich.
