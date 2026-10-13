# AP080 R01 – Evidenzindex

Eigenprüfung SELF_CHECK_PASS / REVIEW_READY; unabhängige Abnahme offen. Testdaten sind synthetisch, Produktionsgeheimnisse und Nutzerdaten werden nicht versioniert.

- [Start-/Quellenprovenienz](input-provenance.json), [AP070 tatsächliche Übernahme](predecessor-canonicalization.json).
- [Baseline90](baseline-unittest.txt).
- [Windowsmanifest mit Quellen-/Gitblob-/Loghashes und Runtime](windows-validation.json), [exakter Kandidatenproduktdiff, base64](tested-product.patch.base64).
- [Gezielte296, vollständiger Log](targeted-unittest.txt), [gesamte1513, vollständiger Log](windows-full-unittest.txt).
- [Bestehende reale Settings38](server-settings-checkpoint.json), [stderr](server-settings-checkpoint.json.stderr.txt).
- [Gepinnte Supplement55 ohne Skips](server-contracts.json), [vollständiger Supplement-Testlog](server-contracts.json.stderr.txt).
- [Reale UI27](server-ui-checkpoint.json), [stderr](server-ui-checkpoint.json.stderr.txt).
- [Native Windows-UI/Vault29](windows-credential-ui.json), [stderr](windows-credential-ui.json.stderr.txt), [sichtbarer Dialog](native-dialog.png).
- [compileall](compileall.txt), [individuelle UI-01…10-Coverage](requirement-coverage.md).
- [Qualifikationsrunner](qualify_windows.py), [Abgabeverifier](verify_handoff.py), [finale Akten-/Blobprüfung](handoff-verification.json).
- [PR #10](https://github.com/marcosudau-vps/voice-stt-client/pull/10), [erneute Veröffentlichungsprüfung](publication-verification.json). PR-Verweise sind rein administrativ; Pflichtlog-/Produktblobs bleiben unverändert.

Reproduktion aus Repositoryroot ausschließlich mit `.\venv\Scripts\python.exe`: Runner benötigt den im Manifest genannten SHA-verifizierten lokalen Serverexport, echten Windowsdesktop und die Projektvenv. Er qualifiziert den staged Produktdiff am Parent; nach Kandidatencommit überprüft der read-only Abgabeverifier unveränderte qualifizierte Gitblobs. Neue Qualifikation nach Produktänderungen erforderlich.

Die gepinnten Serverrouten, TCP HTTP/WS, Clientservices und lokale AppConfig-Persistenz sind real. Recorder/Scheduler/Artifactprobe sind modellfrei kontrolliert. Reale ASR, physisches Mikrofon, Wakeempirie und optimale Kalibrierung sind NOT_RUN/AP-IV2-020. Reguläre App-/Win32-Hotkeyverdrahtung bleibt AP100. Native Credentials sind isoliert und nach Lauf entfernt; kein Klartextfallback.

## Diagnosehistorie

[Erster fehlgeschlagener vollständiger Windowslauf](windows-full-unittest-failed.txt), [Faulthandler-Reproduktion](full-suite-debug.txt) und [weiterhin fehlgeschlagener GUI-Bereinigungsversuch](full-suite-gui-cleanup.txt) belegen die Access Violation im langen gemeinsamen Qtprozess. [Kombination aller Qt-/Control-/neuen UI-Suiten](qt-all-order-debug.txt) besteht mit 270 Tests. Die genaue frühere native Referenz ist nicht isoliert; jeder neue Qtfall führt daher unveränderte Assertions im eigenen begrenzten Projektvenv-Prozess aus. Kein Test wird geskippt. Anschließende komplette Kandidatenqualifikation ersetzt den fehlgeschlagenen Beleg. Diagnosebelege sind kein Pflicht-PASS. Kleine Zwischenläufe ohne vollständige Kandidatenbindung sind nicht Teil der Abgabeevidenz.
