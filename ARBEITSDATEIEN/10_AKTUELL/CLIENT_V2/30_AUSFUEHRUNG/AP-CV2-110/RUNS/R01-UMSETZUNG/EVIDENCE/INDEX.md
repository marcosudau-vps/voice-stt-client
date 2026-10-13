# AP-CV2-110 R01 – Evidenz

**Status:** REVIEW_READY. Vollständige Selbstchecks PASS, unabhängiger Review offen.
Produktkandidat `2b4bb7869f6659434d37d1a7d8b0cba5ba3bd259`, Tree `d9a30deafd7c66143e376931f21d96f6b02aabc4`, Parent `62ca35a01fb88b37e16b7003e26c2f9110c131f3`,
Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Runtime Windows11 Build26300 x64, Projektvenv Python3.12.10.

[Originalprompt](../00_PROMPT_ORIGINAL.md), [Report](../01_REPORT.md),
[Start-/Vorgängerbeleg](start-provenance.json), [Windowsmanifest](windows-validation.json),
[Gitblobbindung](candidate-blobs.txt), [V1-Ersatzfälle](legacy-test-successors.json).

Erzeugender Orchestrator: [run_qualification.py](run_qualification.py),
Projektroot und `venv/Scripts/python.exe`; full/targeted unittest, compileall,
check_v2_server_runtime, build.py --clean, build --sdist --wheel, twine check,
client_release_guard candidate --expected-commit, pip --target und sdist-Rebuild,
--version/--verify-gui-runtime --verification-server für alle vier Produkte.
Vollständige argv/cwd/Commit/Exitcode/Dauer/Testzahl stehen pro Fall im JSON und
am Anfang des vollständigen Rohlogs. [Loghashes](full-log-manifest.json) führen
SHA256 sowohl der gzip-Datei als auch der unveränderten entpackten Bytes.
Gzip dient der bytegleichen Sicherung, kein Kürzen oder Whitespacebereinigen.

| Erzeugender Fall | Exit / Ergebnis | Vollständiger Log |
| --- | --- | --- |
| windows-full | 0 / PASS / 1348 Tests | [windows-full.txt.gz](windows-full.txt.gz) |
| windows-targeted | 0 / PASS / 229 Tests | [windows-targeted.txt.gz](windows-targeted.txt.gz) |
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

Zusätzlich [release-server.txt.gz](release-server.txt.gz) und
[release-server.json](release-server.json): separater gepinnter FastAPI-Prozess,
Quellenhashes, acht tatsächlich empfangene Hellos, V1-Raw-Admission hello/ready.
[Source](source-probe.json), [Wheel](wheel-probe.json),
[sdist-Rebuild](rebuilt-wheel-probe.json), [Frozen](frozen-probe.json) dokumentieren
nativen Desktop, Einstellungen, Corethread, Config, Icon, acht Sounds und JSONs.
Alle installed/frozen PackageRoots außerhalb Checkout. Audioavailable=false,
keine Capture, registrierten Keys oder Paste. Separate echte HTTP-/WSports;
Modell-/Recorder-/Schedulergrenzen explizit, keine Hardware-/ASR-Gesamtabnahme.

Baseline: [isolierter unveränderter Parent](baseline-isolated-windows.txt.gz),
1581 PASS; [Checkoutpfad](baseline-isolated-path.txt).
[Ungültiger erster Versuch](baseline-windows.txt.gz) vollständig erhalten,
8 durch laufende Sourceänderungen beeinflusste Fehler, kein gültiger Baseline-PASS.

| Lokales Artefakt unter dist | Bytes | SHA256 |
| --- | --- | --- |
| `voice_stt_client-1.0.0-py3-none-any.whl` | 1185338 | `dc8f1ab383294a995121dbfc17210de4c19294100b2a89257096c70a1f91030c` |
| `voice_stt_client-1.0.0.tar.gz` | 1148131 | `f3621a1fb7c215390d3717981de013285b7f04b06f1e4a2e1928e2f468f6a9b2` |
| `voice-stt-client.exe` | 75578275 | `bdb237aa30d7bf381a4169a2566b936d4f550e046b5967ae652545b2dd8528e2` |

Binärprodukte sind lokale Buildausgaben und nicht im Gitdiff. CI stellt ihre
separat neu gebauten Kandidaten als GitHub-Actions-Artefakt des endgültigen PR-Heads
bereit; dessen andere Buildstempel/ZIPhashes nicht mit diesen lokalen Hashes vermischen.
Finale Head-/Tree-/CIidentität und administrative Gitblobgleichheit werden in der
Abgabeverifikation bzw. tatsächlichen PR-Kurzfassung festgehalten.
