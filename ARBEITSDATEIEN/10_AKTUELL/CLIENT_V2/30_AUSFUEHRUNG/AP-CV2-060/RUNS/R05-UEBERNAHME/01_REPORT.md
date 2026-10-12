# AP-CV2-060 / R05-UEBERNAHME – vorgezogene Übergabeakte

**Gate:** unabhängig geprüfter R04-ROOT_PASS, ausdrückliche menschliche Freigabe unter [00_PROMPT_ORIGINAL.md](00_PROMPT_ORIGINAL.md), exakte CI des zu diesem Zeitpunkt aktuellen PR-Heads erfolgreich.

## Eingangsidentität

- PR #8: https://github.com/marcosudau-vps/voice-stt-client/pull/8
- Base `feat/client-v2`, kanonischer Parent `ce95c66a7a3b4440faaa33289351871a040ebe19`; gegenwärtig keine konkurrierende Übernahme.
- Produktbezogen geprüfter Kandidat `1d81bb0230cfc5a099b7870488f6b42cd4735d5a`, Tree `f3342625d63ec0c296d62d03decb54ea93fd983b`. [R04-Abnahme](../R04-ABNAHME/01_REPORT.md) = ROOT_PASS, alle RESULT-01…RESULT-13, F01 unabhängig CLOSED, null offene Pflichtfindings.
- PR-Head zum Zeitpunkt der menschlichen Freigabe `8eb26bae17b46651014d28183f5a9135f36b72af`, Tree `63bb387684b76cf1b650bbcb618ea6e7ce168860`; ausschließlich administrative R04-Nachträge seit der fachlichen Review-SHA. GitHub [CI38276463113](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38276463113) = completed/success, alle Tests, EXE-, Wheel-, Distribution-Smokes grün. PR open, mergeable true, Base SHA = kanonischer Parent.
- CI-/Testgrenzen gemäß R04; keine erneute eigene Windows-Vollsuite erforderlich.
- Gepinnte Serverbaseline `ada13b011e1d3829f78e7f389e3b927795a2b3be` unverändert.

## Bewilligte Abschlussaktion

Menschliches „Bitte führe den Merge durch“ bezeichnet das aktuell bestandene AP060 und den ausdrücklich genannten PR #8. Der Originalwortlaut ist versioniert. Workflowstatus vor Übernahme: `packageStatus=ROOT_PASS`, `workflowPhase=READY_FOR_CANONICALIZATION`, keine vorherige produktive Freigabeänderung.

Die vorliegende separate Akte sowie ausschließlich administrative Paket-/Statusverweise sind der notwendige Freigabenachtrag. Der daraus entstehende PR-Head darf **erst nach erfolgreicher CI dieses neuen Heads** per GitHub-Squash übernommen werden. Vor Merge Remotehead, kanonischen Parent, vollständigen rein administrativen Review→Finaldiff und Mergeability erneut abgleichen. Die Checkout- und Mergevoraussetzungen werden über den tatsächlichen PR/GitHub-Nachweis hergestellt.

Nach GitHub-Merge: einziges Squash-Aggregat mit Parent `ce95c66a7a3b4440faaa33289351871a040ebe19`; Aggregatbaum muss mit der unmittelbaren finalen PR-Spitze übereinstimmen. Neue kanonische SHA und Mergezeit über GitHub prüfen, nicht in diesen vor dem Merge erzeugten Commit hineinschreiben. Tatsächliches CANONICALIZED/ACCEPTED wird später im Nachfolgepaket anhand der gemergten PR und Gitobjekte festgehalten. Kein weiterer Reparatur-/Aufräumcommit auf `feat/client-v2`.
