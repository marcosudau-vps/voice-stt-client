# Aktueller Paketstand – 2026-10-13

AP000 bis AP090 tatsächlich ACCEPTED; AP100 **ROOT_PASS / WAITING_FOR_APPROVAL** nach [unabhängigem R05-Review](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md). F01 behoben und unabhängig geschlossen; technische 6/6 Anforderungen PASS. [Workflowstatus](../../WORKFLOW_STATUS.json). Kein Merge/AP110 vor ausdrücklicher menschlicher Freigabe und tatsächlicher kanonischer Übernahme.

# Arbeitspakete – Index und Liefergrenzen

Rollen-Einstieg: [Umsetzung](../SKILLS/voice-stt-client-v2-umsetzen/SKILL.md) oder [unabhängige Abnahme](../SKILLS/voice-stt-client-v2-abnehmen/SKILL.md). Nur die Datei des beauftragten Pakets und dessen fachliche Referenzen lesen; die Skills laden den passenden Arbeitsablauf.

AP-CV2-090 nach [R02-PASS](../../30_AUSFUEHRUNG/AP-CV2-090/RUNS/R02-ABNAHME/01_REPORT.md), menschlicher Freigabe und PR-#11-Merge tatsächlich ACCEPTED. Historische AP100-Quellen: [R02-Selbstnachweise](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md) und der neuere [R03-Findingreport](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md).

| Paket | Endzustand | Abhängigkeiten |
| --- | --- | --- |
| [AP-CV2-000](AP-CV2-000.md) | Feature-/Releaseintegration und qualifizierte Clientstartbasis | – |
| [AP-CV2-010](AP-CV2-010.md) | V2-Wiredatentypen, Parser, Encoder und Contractfixtures | AP-CV2-000 |
| [AP-CV2-020](AP-CV2-020.md) | V2transport, Hello und korrelierte Commands | AP-CV2-010 |
| [AP-CV2-030](AP-CV2-030.md) | ActivationMirror, Hintergrundledger und Resync | AP-CV2-010, AP-CV2-020 |
| [AP-CV2-040](AP-CV2-040.md) | Continuous-Audio, Geräte-Recovery und Logbootstrap | AP-CV2-020, AP-CV2-030 |
| [AP-CV2-050](AP-CV2-050.md) | Hotkeyrollen, Trigger-Suppression und manuelle Controls | AP-CV2-030, AP-CV2-040 |
| [AP-CV2-060](AP-CV2-060.md) | Final-Pipeline, UUID-Historie und sichere Textinjektion | AP-CV2-030 |
| [AP-CV2-070](AP-CV2-070.md) | Konfigurationsmigration und serverautoritativer Settingsservice | AP-CV2-020, AP-CV2-030 |
| [AP-CV2-080](AP-CV2-080.md) | Trigger-/Server-Settings-UI, Applyentscheidungen und Credential Manager | AP-CV2-050, AP-CV2-060, AP-CV2-070 |
| [AP-CV2-090](AP-CV2-090.md) | Quellenneutrales Feedback, Overlay und lokale Observability | AP-CV2-030, AP-CV2-050, AP-CV2-060 |
| [AP-CV2-100](AP-CV2-100.md) | Vollständige Runtimeintegration und Lifecycleverdrahtung | AP-CV2-040, AP-CV2-050, AP-CV2-060, AP-CV2-070, AP-CV2-080, AP-CV2-090 |
| [AP-CV2-110](AP-CV2-110.md) | Legacyabbau, Paketressourcen, Kompatibilität und Build | AP-CV2-100 |
| [AP-IV2-010](AP-IV2-010.md) | Integration der festgeschriebenen Client- und Servercommits | AP-CV2-110 |
| [AP-IV2-020](AP-IV2-020.md) | Reale Windows-, ASR-, Hardware- und Produktabnahme | AP-IV2-010 |
| [AP-SV2-FIX](AP-SV2-FIX.md) | Bedingtes Serverkorrekturpaket während der Cliententwicklung | – |

Jede Paketdatei enthält Ziel, fachliche Ownership, Eingangsvoraussetzungen, einen Umsetzungsvorschlag, Lieferergebnisse, messbare Akzeptanz, Testauftrag, Definition of Done und Übergabe-/Gitregeln. Geplante Datei-/Testnamen sind Vorschläge; [Umsetzungsspielraum](../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md) und [Paketablage/Vorlagen](../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) gelten paketübergreifend. Die Paket-ID wird im Ausführungsreport und bei jedem Traceabilitybeleg geführt.

Die Ausführung erfolgt streng seriell. Fachlaufzahlen und Teilung stehen in jeder AP-Datei sowie im [Umfangsmodell](../REFERENZ/PLANUNG/UMFANG_UND_AGENTENLAEUFE.md). Jedes Paket wird unabhängig geprüft; erst ROOT PASS und die gesicherte kanonische Aggregateübernahme geben den nächsten Start frei. [Agentenregelwerk](../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md).


## Historische PR-Verweise zu AP060

Frühere AP060-Kandidatenidentität und PR werden bei vollständiger Abgabe in Paketakte und PR-Beschreibung angegeben.


[PR #8](https://github.com/marcosudau-vps/voice-stt-client/pull/8) gegen feat/client-v2. Früherer vor CI-Selbstkorrektur qualifizierter Umsetzungscommit `66b6e39daa86855ae1314025bc06344eb55f7d39`, Tree `fbe3931c3b68efa510bee1e35db4b77ad7a83f27`. Nachfolgende Veröffentlichungsverweise sind rein administrativ; endgültige eingereichte SHA/Tree stehen in aktueller PR-Beschreibung und finaler Übergabe.


Maßgeblich nach CI-Selbstkorrektur: aktuelles Windowsmanifest mit getesteter Basis 66f44e0 plus staged Pfadalias-Testkorrektur, vollständig neu qualifiziertem Testblob und allen 195 qualifizierten Produktblobs. Finale Kandidaten-SHA/Tree stehen in PR und Übergabe.


Aktuell R03: F01-Dokumentnamen korrigiert; [Korrekturreport](../../30_AUSFUEHRUNG/AP-CV2-060/RUNS/R03-KORREKTUR/01_REPORT.md). R04-ROOT_PASS erteilt; Produktqualifikation unverändert gültig, Übernahmefreigabe ausstehend.


[AP060 R05 Freigabeoriginal und Übernahmeakte](../../30_AUSFUEHRUNG/AP-CV2-060/RUNS/R05-UEBERNAHME/00_PROMPT_ORIGINAL.md): Konditionierte menschliche Mergefreigabe ist nach CI38276463113 gültig; rein administrativer Nachtrag muss vor Squash erneut CI-bestanden sein. Kein CANONICALIZED vor tatsächlichem Merge.
