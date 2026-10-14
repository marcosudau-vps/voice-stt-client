# Client V2 – AP-IV2-010 / R02-ABNAHME / ROOT_PASS, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](../../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](../../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](../../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](../../30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](../../WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

**Unabhängiger R02-ROOT_PASS:** GATE-01..07 PASS, keine Findings, [Review](../../30_AUSFUEHRUNG/AP-IV2-010/RUNS/R02-ABNAHME/01_REPORT.md). **WAITING_FOR_APPROVAL**, kein Merge/AP-IV2-020.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Aktueller Paketstand, 2026-10-14

AP000 bis AP100 tatsächlich ACCEPTED; Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP110 nach unabhängigem [R02-Gesamt-Review](../../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) **ROOT_PASS / READY_FOR_CANONICALIZATION**, alle sieben FINAL-Requirements PASS. [Workflowstatus](../../WORKFLOW_STATUS.json). [Menschlicher R03-Übernahmeprompt](../../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) liegt vor; der tatsächliche Squash von PR #13 und die Git-/Treeverifikation stehen noch aus. AP-IV2-010 darf erst danach beginnen.

## Historischer Paketindex vor R02

# Aktueller Paketstand, 2026-10-13

AP000 bis AP100 tatsächlich ACCEPTED, kanonischer Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`.
[AP100-Promotionnachweis](../../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
AP110 REVIEW_READY nach vollständigem Selbstcheck; [R01-Report](../../30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md),
[Workflowstatus](../../WORKFLOW_STATUS.json). Nächste Aktion unabhängiger AP110-Review;
keine kanonische Übernahme oder AP-IV2-010 ohne PASS, menschlichen Prompt und echten Squash.

## Historischer Paketindex vor AP100-Übernahme

# Aktueller Paketstand – 2026-10-13

AP000 bis AP090 tatsächlich ACCEPTED; AP100 **ROOT_PASS / READY_FOR_CANONICALIZATION** nach [unabhängigem R05-Review](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md). F01 behoben und unabhängig geschlossen; technische 6/6 Anforderungen PASS. [Workflowstatus](../../WORKFLOW_STATUS.json). [Menschliche R06-Freigabe](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R06-UEBERNAHME/00_PROMPT_ORIGINAL.md) liegt vor. Squash-Merge nur nach finaler CI-/Head-/Baseprüfung; kein AP110 vor tatsächlicher kanonischer Übernahme.

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
