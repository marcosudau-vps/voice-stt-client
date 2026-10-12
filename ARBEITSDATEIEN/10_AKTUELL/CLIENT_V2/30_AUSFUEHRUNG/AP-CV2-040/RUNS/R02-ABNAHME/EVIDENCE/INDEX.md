# AP-CV2-040 / R02 – Evidenzindex

**Urteil: CHANGES_REQUIRED**, fachlich geprüfter SHA `79cffe19b103cfcc325f5c15a7532da763ff3f9c`, Tree `1449c1b71015d978349826891644565b3711e17a`, Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Quelle: unabhängiger Review über commitgebundene GitHubdateien und GitHub-PR-/Commit-/Blobmetadaten; kein lokaler Checkout.

- [R02-Report](../01_REPORT.md) – ausführliches Urteil, Scope, zwei Pflichtfindings mit Expected/Actual, Testlücken und Rückgabe.
- [R02-Originalauftrag](../00_PROMPT_ORIGINAL.md) – tatsächlicher Nutzerwortlaut und verifizierte fortgeltende Review-Gitrechte.
- [R01-Windowsmanifest](../../R01-UMSETZUNG/EVIDENCE/windows-validation.json) – Testidentität, Windows/Python/Qt-Runtime, vollständige Kommandos, Exitcodes und Blobs.
- [R01-Windows-Vollsuitenlog](../../R01-UMSETZUNG/EVIDENCE/windows-full-unittest.txt) – 1367 PASS, keine dokumentierten Skips.
- [R01-Zieltestlog](../../R01-UMSETZUNG/EVIDENCE/targeted-unittest.txt) – 222 PASS.
- [R01-Servercheckpoint](../../R01-UMSETZUNG/EVIDENCE/server-audio-checkpoint.json) – 41 PASS, 46 gepinnte Serverquellen.
- [R01-Requirementabdeckung](../../R01-UMSETZUNG/EVIDENCE/requirement-coverage.md) – alle 23 AUDIO-/LOG-IDs mit konkreten Testmethoden.
- [R01-Produktdiff](../../R01-UMSETZUNG/EVIDENCE/tested-product.patch) – exakte qualifizierte Produktänderungen; SHA256 `5d87fe46852c8ee3ecdffed5604e1ce144f93f0cb8aa441fb321408a617963d4`.
- [R01-Paketabgabeprüfung](../../R01-UMSETZUNG/EVIDENCE/submission-validation.json) – Struktur-, Link-, Diff- und Quellenbindung vor Review.
- [Prüfdatei v2_media.py, eingefroren](https://github.com/marcosudau-vps/voice-stt-client/blob/79cffe19b103cfcc325f5c15a7532da763ff3f9c/voice_stt_client/core/v2_media.py) – tatsächliche Fundstellen F01/F02.
- [Kandidat-Commit](https://github.com/marcosudau-vps/voice-stt-client/commit/79cffe19b103cfcc325f5c15a7532da763ff3f9c) – Gitidentität/Tree; [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6) – PRdiff und Metadaten.

**Prüfherkunft/Ergebnis:** Elf geänderte Produkt-/Test-/Skriptdateien per GitHub PR Files API mit `qualifiedGitBlobs` verglichen: **11/11 MATCH**. Windows- und Serverläufe wurden in R01 durchgeführt und ausschließlich unabhängig aus Fremdbelegen geprüft (eigene Wiederholung: NOT_RUN). Zwei Fehlerfälle sind anhand von Codekontrollfluss nachgewiesen; geforderte dynamische Repros durch Korrekturagent **NOT_RUN**. Physische Hardware/ASR gemäß Paketgrenze **NOT_PROVEN**, nicht nachträglich als bestanden ausgegeben.

Referenzen bleiben ausdrücklich auf den fachlich geprüften SHA vor dem neuen, ausschließlich administrativen Reviewcommit bezogen. Kein neuer Testlog und kein selbst erzeugtes Messergebnis vorgetäuscht.
