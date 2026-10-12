# Evidenz AP-CV2-050 / R01-UMSETZUNG

[Report](../01_REPORT.md), [Originalauftrag](../00_PROMPT_ORIGINAL.md). Status **REVIEW_READY**, kein eigener ROOT_PASS.

| Beleg | Inhalt |
| --- | --- |
| [VorgÃ¤ngerÃ¼bernahme](predecessor-canonicalization.json) | TatsÃ¤chlicher PR6-Merge, PASS-/Freigabequelle, Singleparent/Commitzahl/Baumgleichheit |
| [Vertragshashes](start-contract-hashes.json) | AP050/K01â€“K04 vor UmsetzungsÃ¤nderung |
| [Vorher-Baseline](baseline.txt) | 160 Tests PASS auf Parent `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f` |
| [Windowsmanifest](windows-validation.json) | Runtime, vollstÃ¤ndige Befehle, Exitcodes, Zeiten, Loghashes, sourceHashes, Gitblobs |
| [Exakter Produktdiff](tested-product.patch) | Getestete sieben Produkt-/Test-/SkriptÃ¤nderungen gegen Parent, SHA256 im Manifest |
| [Gezielte Suite](targeted-unittest.txt) | 297 Tests PASS, -W error |
| [Servercheckpoint](server-controls-checkpoint.json) / [stderr](server-controls-checkpoint.json.stderr.txt) | 79 PASS; 46 unverÃ¤nderte Quellblobs Server `ada13b011e1d3829f78e7f389e3b927795a2b3be` vor/nach Lauf geprÃ¼ft |
| [Native Hotkeys](windows-hotkeys.json) / [stderr](windows-hotkeys.json.stderr.txt) | 16 PASS; echter Win32backend/Qtfilter/SendInput einschlieÃŸlich Registerfehler1409 und Rollback |
| [Compileall](compileall.txt) | Exit0, leerer vollstÃ¤ndiger Log |
| [Windowsvollsuite](windows-full-unittest.txt) | 1397 Tests PASS, keine Testskips |
| [Requirementabdeckung](requirement-coverage.md) | CONTROL-01 bis CONTROL-14 mit tatsÃ¤chlichen Methoden/Checknamen |
| [Qualifikationsrunner](qualify_windows.py) | Reproduzierbare sequentielle Befehle; Quellbestand vor/nach Testlauf unverÃ¤ndert |
| [Abgabeverifikation](submission-validation.json) | 192/192 qualifizierte Gitblobs und verÃ¶ffentlichte Loghashes identisch; 14 Methodenbelege, Aktenlinks und Diffcheck PASS |

Qualifikation 2026-10-12 13:23:00â€“13:25:37 UTC auf Windows11 Build26300, Projektpython3.12.10, PySide6 6.11.1, websockets17.0.1, FastAPI0.135.4, uvicorn0.44.0; Qt offscreen. Alle Befehle/absolute Laufzeitpfade stehen im Manifest. Runner: `.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/EVIDENCE/qualify_windows.py`.

Server: isolierter loopback TCP/WebSocket mit produktivem gepinntem Servercode, GateAwareRecorder/AutoScheduler aus dessen Tests sowie kÃ¼nstlichem WakeHit und Artifactprobe statt Inferenz. Kontrollierte monotone Serverzeit prÃ¼ft nichtkumulative Fristen. GerÃ¤teverlust ist serverseitiges audioAvailable=false plus Reconnect, keine neue Hardwareabnahme. Native HotkeyprÃ¼fung verwendet echte Betriebssystemregistrierung und Nachrichten; SendInput ersetzt menschliches DrÃ¼cken. Keine vollstÃ¤ndige Appkomposition/ASR/ClipboardprÃ¼fung, wie fÃ¼r diesen Zwischencheckpoint vorgesehen.

stderr der HotkeyprÃ¼fung enthÃ¤lt den **erwarteten** RegisterHotKey-Konflikt1409; das Skript bestÃ¤tigt danach vollstÃ¤ndigen Rollback und tatsÃ¤chlichen Weiterbetrieb. Andere Warnungen/Fehler im vollstÃ¤ndigen Unitlog sind die erwarteten Negativpfade der bestehenden Suite; Exit0 und 1397/1397, keine unerklÃ¤rten Fehler. Logs werden vollstÃ¤ndig als UTF-8/LF ohne nachgestellte Leerzeichen gesichert; Hashes sind auf genau diese versionierte Ausgabe bezogen. Runtime-sourceHashes erfassen lokale Bytes, Gitblobs identifizieren normalisierte verÃ¶ffentlichte Quellen. SpÃ¤tere reine AktennachtrÃ¤ge Ã¤ndern die qualifizierten Produktblobs nicht; der Bereitstellungsabgleich wird vor Ãœbergabe gesichert.

[PR #7](https://github.com/marcosudau-vps/voice-stt-client/pull/7), qualifizierter vollständiger Commit `ee1f1a7bb0a55112b61a3cab9c34be561aae274e`, Tree `f1613cb4ecf3292e6442f38c4704162b940c5fea`. [Abgabeverifikation](submission-validation.json) belegt identische Produktblobs und Logs.
