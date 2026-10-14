# R03-UEBERNAHME – Freigabe-/Preflight-Evidenz

| Beleg | Inhalt / Prüfgrenze |
| --- | --- |
| [Freigabeoriginal](../00_PROMPT_ORIGINAL.md) | Tatsächlich erteilter Nutzerauftrag für PR #13, unveränderter Wortlaut |
| [R03-Report](../01_REPORT.md) | Identität, Status vor Merge, verbindlicher Squash- und Nachweisablauf |
| [Preflight-Metadaten](preflight.json) | Freigabe-Head, Base, ursprünglicher Review, SHA-gebundene grüne CI, administrativer Differenzumfang |
| [R02-Reviewbericht](../../R02-ABNAHME/01_REPORT.md) | Unabhängiger ROOT_PASS mit 7/7 Anforderungen, keine Findings |
| [R02-Index](../../R02-ABNAHME/EVIDENCE/INDEX.md) | Validierte Windows-/Server-/Build-/Regressionsbelege |
| [GitHub Actions 38531198371](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38531198371) | `completed/success` auf `84b72e11b64d0d6220fe239614301dfd569d8256`; letzter erfolgreicher CI-Lauf **vor** diesem Freigabe-Dokumentencommit |

**Prüfgrenze:** Diese Akte wird vor dem Merge versioniert. Sie enthält keinen erfundenen kanonischen Aggregatecommit. Nach dem Docs-Push sind die finale CI und der neue PR-Head nochmals zu prüfen. Nachmergebeleg wird aus Git/PR im Abschlussbericht an den Auftraggeber ermittelt und vom Folgepaket übernommen.
