# AP-CV2-110 R01 – Evidenz

**Status:** REVIEW_READY. Vollständiger Selbstcheck PASS, unabhängiger Review offen.
[PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base feat/client-v2, Head work/client-v2/ap-cv2-110.
Qualifizierter Produktcommit `cf42a2a9d96c1ebc88035817a5d529dfe04e4306`, Tree `985986edaef2a1a6fc37091756d13b988adddc7e`,
Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Runtime Windows11 Build26300 x64, Projektvenv Python3.12.10.

[Originalauftrag](../00_PROMPT_ORIGINAL.md), [Report](../01_REPORT.md),
[Startprovenienz](start-provenance.json), [Windowsmanifest](windows-validation.json),
[Gitblobbindung einschließlich .gitattributes](candidate-blobs.txt),
[251 V1-Ersatzverantwortungen](legacy-test-successors.json).

Erzeugender Befehl aus dem Projektroot:
`venv/Scripts/python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/run_qualification.py`.
[Orchestrator](run_qualification.py); vollständige argv/cwd/Commit/Exitcode/Dauer/
Testzahlen pro Fall im JSON und Logkopf. [SHA256 aller aktuellen gzip/Rohbytes](full-log-manifest.json).
Gzip bewahrt vollständige Bytes; kein Kürzen/Whitespacebereinigen.

| Erzeugender Fall | Ergebnis | Vollständiger Log |
| --- | --- | --- |
| windows-full | 0 / PASS / 1353 Tests | [windows-full.txt.gz](windows-full.txt.gz) |
| windows-targeted | 0 / PASS / 234 Tests | [windows-targeted.txt.gz](windows-targeted.txt.gz) |
| compileall | 0 / PASS | [compileall.txt.gz](compileall.txt.gz) |
| server-runtime | 0 / PASS | [server-runtime.txt.gz](server-runtime.txt.gz) |
| pyinstaller-clean | 0 / PASS | [pyinstaller-clean.txt.gz](pyinstaller-clean.txt.gz) |
| python-distributions | 0 / PASS | [python-distributions.txt.gz](python-distributions.txt.gz) |
| twine-check | 0 / PASS | [twine-check.txt.gz](twine-check.txt.gz) |
| release-guard | 0 / PASS | [release-guard.txt.gz](release-guard.txt.gz) |
| wheel-install | 0 / PASS | [wheel-install.txt.gz](wheel-install.txt.gz) |
| sdist-wheel-rebuild | 0 / PASS | [sdist-wheel-rebuild.txt.gz](sdist-wheel-rebuild.txt.gz) |
| rebuilt-wheel-install | 0 / PASS | [rebuilt-wheel-install.txt.gz](rebuilt-wheel-install.txt.gz) |
| source-version | 0 / PASS | [source-version.txt.gz](source-version.txt.gz) |
| source-native-probe | 0 / PASS | [source-native-probe.txt.gz](source-native-probe.txt.gz) |
| wheel-version | 0 / PASS | [wheel-version.txt.gz](wheel-version.txt.gz) |
| wheel-native-probe | 0 / PASS | [wheel-native-probe.txt.gz](wheel-native-probe.txt.gz) |
| rebuilt-wheel-version | 0 / PASS | [rebuilt-wheel-version.txt.gz](rebuilt-wheel-version.txt.gz) |
| rebuilt-wheel-native-probe | 0 / PASS | [rebuilt-wheel-native-probe.txt.gz](rebuilt-wheel-native-probe.txt.gz) |
| frozen-version | 0 / PASS | [frozen-version.txt.gz](frozen-version.txt.gz) |
| frozen-native-probe | 0 / PASS | [frozen-native-probe.txt.gz](frozen-native-probe.txt.gz) |
| diff-check | 0 / PASS | [diff-check.txt.gz](diff-check.txt.gz) |

[Getrennter Produktionsserver](release-server.json), [vollständiger Serverlog](release-server.txt.gz):
bytegeprüfte ada13b0-Quellen, acht empfangene aktuelle Hellos, V1-Raw-Admission.
[Source](source-probe.json), [Wheel](wheel-probe.json),
[sdist-Rebuild](rebuilt-wheel-probe.json), [Frozen](frozen-probe.json): native Windows-
Qt/Settingsdialog/Corethread, Config/Icon/JSONs/Sounds, Helloidentität und
Snapshot/Settingsrevision. Alle installed/frozen PackageRoots außerhalb Checkout.
Qt-Soundprüfpfad und Audioausgabegerät stehen im JSON; Playback NOT_RUN.
Audioavailable=false, kein Capture/Paste/Keys/LED. Recorder/ASR/Scheduler modellfrei;
kein physischer Hardware-/ASR-/Fremdanwendungs-/Langlauf-PASS.

Baseline [1581 PASS am isolierten unveränderten Parent](baseline-isolated-windows.txt.gz),
[Archivpfad](baseline-isolated-path.txt). [Ungültiger erster Versuch](baseline-windows.txt.gz)
mit 8 durch eigene laufende Sourceänderungen beeinflussten Fehlern erhalten;
ausschließlich der isolierte PASS gilt als Baseline.

CI-01 [fehlgeschlagener Lauf](ci-01-failure.txt.gz), [Repro](ci-01-repro.json),
[RED/GREEN](ci-01-red-green.txt.gz), [ausführbarer Repro](reproduce_ci01.py).
Aufruf mit Projektvenv aus Root und `PYTHONPATH=.`; tatsächlicher Gitcheckout unter
autocrlf=true. CI-02 [fehlgeschlagener Lauf](ci-02-failure.txt.gz),
[Timeout-/Decoder-/FAIL-JSON-Regressionen](ci-02-repro.json).
CI-03 [Produktkandidaten-CI PASS](ci-03-success.json), [vollständiger Log](ci-03-success.txt.gz).
Frühere lokale Nachweise [Q01](QUALIFICATION-01/windows-validation.json),
[Q02](QUALIFICATION-02/windows-validation.json) samt eigenen Rohlogs/Hashes erhalten;
sie qualifizieren die ursprünglichen, mittlerweile korrigierten Kandidaten.

| Lokales Artefakt unter dist | Bytes | SHA256 |
| --- | --- | --- |
| `voice_stt_client-1.0.0-py3-none-any.whl` | 1185970 | `00073cd4f5b1f1b1e20e433380bb1422cff4f3e0d64a7230d1578fd8f1efbeec` |
| `voice_stt_client-1.0.0.tar.gz` | 1148781 | `99f0231e69d52cbaa5eae3834ccfa9ee39d8002cb64191dbe0fb8f233c981345` |
| `voice-stt-client.exe` | 75579676 | `dccc449d227e7e3580bbdfa333f7386ac6070f007eee29c40971f863375c6f5d` |

Lokale Binärprodukte nicht im Gitdiff. CI baut eigene commitgestempelte Kandidaten
und lädt sie als GitHub-Actions-Artefakt hoch; diese anderen Hashes nicht mit den
lokalen Artefakten vermischen. [Aktenprüfung](work-record-validation.json) und
[administrativer Gitblob-/Log-/Artefakthashabgleich](administrative-delta.json) PASS.
Finale tatsächliche PR-Spitze/Tree/CI extern im PR, danach Umsetzungsschreiben pausiert.
