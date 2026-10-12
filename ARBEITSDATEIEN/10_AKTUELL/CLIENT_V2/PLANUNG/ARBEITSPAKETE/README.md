# Arbeitspakete â€“ Index und Liefergrenzen

Rollen-Einstieg: [Umsetzung](../SKILLS/voice-stt-client-v2-umsetzen/SKILL.md) oder [unabhÃ¤ngige Abnahme](../SKILLS/voice-stt-client-v2-abnehmen/SKILL.md). Nur die Datei des beauftragten Pakets und dessen fachliche Referenzen lesen; die Skills laden den passenden Arbeitsablauf.

AP-CV2-000 bis AP-CV2-040 sind **ACCEPTED** (AP040 kanonischer Commit `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`, [Abschlussbeleg](../../30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json)). AP-CV2-050: **REVIEW_READY**, [R01-Report](../../30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/01_REPORT.md),1397 Windows/297 gezielte Tests,79 Server-/16 native Checks PASS. NÃ¤chste Aktion frischer unabhÃ¤ngiger Review; Paketbranch ab Ãœbergabe pausiert, kein Merge/AP060-Start. SpÃ¤tere Pakete PLANNED.

| Paket | Endzustand | AbhÃ¤ngigkeiten |
| --- | --- | --- |
| [AP-CV2-000](AP-CV2-000.md) | Feature-/Releaseintegration und qualifizierte Clientstartbasis | â€“ |
| [AP-CV2-010](AP-CV2-010.md) | V2-Wiredatentypen, Parser, Encoder und Contractfixtures | AP-CV2-000 |
| [AP-CV2-020](AP-CV2-020.md) | V2transport, Hello und korrelierte Commands | AP-CV2-010 |
| [AP-CV2-030](AP-CV2-030.md) | ActivationMirror, Hintergrundledger und Resync | AP-CV2-010, AP-CV2-020 |
| [AP-CV2-040](AP-CV2-040.md) | Continuous-Audio, GerÃ¤te-Recovery und Logbootstrap | AP-CV2-020, AP-CV2-030 |
| [AP-CV2-050](AP-CV2-050.md) | Hotkeyrollen, Trigger-Suppression und manuelle Controls | AP-CV2-030, AP-CV2-040 |
| [AP-CV2-060](AP-CV2-060.md) | Final-Pipeline, UUID-Historie und sichere Textinjektion | AP-CV2-030 |
| [AP-CV2-070](AP-CV2-070.md) | Konfigurationsmigration und serverautoritativer Settingsservice | AP-CV2-020, AP-CV2-030 |
| [AP-CV2-080](AP-CV2-080.md) | Trigger-/Server-Settings-UI, Applyentscheidungen und Credential Manager | AP-CV2-050, AP-CV2-060, AP-CV2-070 |
| [AP-CV2-090](AP-CV2-090.md) | Quellenneutrales Feedback, Overlay und lokale Observability | AP-CV2-030, AP-CV2-050, AP-CV2-060 |
| [AP-CV2-100](AP-CV2-100.md) | VollstÃ¤ndige Runtimeintegration und Lifecycleverdrahtung | AP-CV2-040, AP-CV2-050, AP-CV2-060, AP-CV2-070, AP-CV2-080, AP-CV2-090 |
| [AP-CV2-110](AP-CV2-110.md) | Legacyabbau, Paketressourcen, KompatibilitÃ¤t und Build | AP-CV2-100 |
| [AP-IV2-010](AP-IV2-010.md) | Integration der festgeschriebenen Client- und Servercommits | AP-CV2-110 |
| [AP-IV2-020](AP-IV2-020.md) | Reale Windows-, ASR-, Hardware- und Produktabnahme | AP-IV2-010 |
| [AP-SV2-FIX](AP-SV2-FIX.md) | Bedingtes Serverkorrekturpaket wÃ¤hrend der Cliententwicklung | â€“ |

Jede Paketdatei enthÃ¤lt Ziel, fachliche Ownership, Eingangsvoraussetzungen, einen Umsetzungsvorschlag, Lieferergebnisse, messbare Akzeptanz, Testauftrag, Definition of Done und Ãœbergabe-/Gitregeln. Geplante Datei-/Testnamen sind VorschlÃ¤ge; [Umsetzungsspielraum](../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md) und [Paketablage/Vorlagen](../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) gelten paketÃ¼bergreifend. Die Paket-ID wird im AusfÃ¼hrungsreport und bei jedem Traceabilitybeleg gefÃ¼hrt.

Die AusfÃ¼hrung erfolgt streng seriell. Fachlaufzahlen und Teilung stehen in jeder AP-Datei sowie im [Umfangsmodell](../REFERENZ/PLANUNG/UMFANG_UND_AGENTENLAEUFE.md). Jedes Paket wird unabhÃ¤ngig geprÃ¼ft; erst ROOT PASS und die gesicherte kanonische AggregateÃ¼bernahme geben den nÃ¤chsten Start frei. [Agentenregelwerk](../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md).

[PR #7](https://github.com/marcosudau-vps/voice-stt-client/pull/7) gegen feat/client-v2. Vollständiger qualifizierter Umsetzungscommit `ee1f1a7bb0a55112b61a3cab9c34be561aae274e`, Tree `f1613cb4ecf3292e6442f38c4704162b940c5fea`. Nachfolgende PR-Verweise rein administrativ; finale eingereichte Spitze steht SHA-/Tree-genau in aktueller PR-Beschreibung und finaler Übergabe.
