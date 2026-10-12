# Arbeitspakete – Index und Liefergrenzen

Rollen-Einstieg: [Umsetzung](../SKILLS/voice-stt-client-v2-umsetzen/SKILL.md) oder [unabhängige Abnahme](../SKILLS/voice-stt-client-v2-abnehmen/SKILL.md). Nur die Datei des beauftragten Pakets und dessen fachliche Referenzen lesen; die Skills laden den passenden Arbeitsablauf.

AP-CV2-000 bis AP-CV2-020: ACCEPTED (AP020 `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0`, [PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4), [Nachmergebeleg](../../30_AUSFUEHRUNG/AP-CV2-030/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json)). AP-CV2-030: ROOT_PASS / WAITING_FOR_APPROVAL ([Paketakte](../../30_AUSFUEHRUNG/AP-CV2-030/00_PAKET.md), [R02-Bericht](../../30_AUSFUEHRUNG/AP-CV2-030/RUNS/R02-ABNAHME/01_REPORT.md)); spätere Pakete PLANNED.

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
