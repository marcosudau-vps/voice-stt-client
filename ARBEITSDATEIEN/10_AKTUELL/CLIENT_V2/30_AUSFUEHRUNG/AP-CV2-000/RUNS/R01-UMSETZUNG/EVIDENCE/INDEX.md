# Evidenzindex – AP-CV2-000 / R01-UMSETZUNG

Windows, Python 3.12.10 aus der bestehenden Projektvenv (lokale `venv`-Junction). Pythonbefehle verwenden ausschließlich `.\venv\Scripts\python.exe`. Tests Qt offscreen, PYTHONUTF8=1. Featureparent `050e776cf316eb332177294db0c0a2719c2b4415`; Featurekanonisch 8bab1b3/Distributed a80a6b1 (gleicher Tree); Release f625904; Server unverändert ada13b0. Kandidat: final eingereichter Head `work/client-v2/ap-cv2-000`, vollständiger Parentdiff. Git-/PR-SHA/Tree werden nach Sicherung aller Unterlagen separat in Übergabe und Identitätsnachtrag aufgelöst.

Die Logs gehören zu dem in beiden Installationsmanifeste gehashten Produktstand; `qualify_sources.py` vergleicht sie mit Source. Spätere administrative Aktenpflege verändert diese Produktbytes nicht. Keine Nutzerlaufzeitlogs, Secrets, Datenbanken oder Sprachaufnahmen als Evidenz.

Für die Git-Diffprüfung sind abschließende Leerzeilen und Zeilenend-Leerzeichen der Toollogs normalisiert; fachliche Ausgabe bleibt erhalten. Nach finaler README-Pflege wurden beide Distributionen erneut gebaut und in getrennte `*-final-installed`-Tempziele installiert, damit auch die Paketmetadaten dem Kandidaten entsprechen.

| Datei | Erzeugung / Zweck | Ergebnis |
| --- | --- | --- |
| [start-status.txt](start-status.txt) | `git status --short --branch`, `git rev-parse HEAD` vor Änderungen | sauberer Featurecheckout; keine fremde Änderung |
| [start-remote.txt](start-remote.txt) | `git ls-remote --heads origin`; offene PRs mit `gh pr list` geprüft | Feature050e776, keine offenen Paket-PRs; alte Linien geschützt |
| [source-identities.txt](source-identities.txt) | Git rev-parse (Commit/Tree) der drei Quellen und merge-base | Featuretrees identisch; getrennter Release und gemeinsame Basis |
| [plan-hashes.txt](plan-hashes.txt) | `Get-FileHash -Algorithm SHA256` relevanter Revision-10-Auftragsquellen | Auftragshashes vor Umsetzung gesichert |
| [baseline-feature.txt](baseline-feature.txt) | clean Gitarchiv 050e776, Projektpython `-m pytest -q` | PASS 1192 / 98.03s |
| [baseline-release.txt](baseline-release.txt) | clean Gitarchiv f625904, Projektpython `-m pytest -q` | FAIL Sammlung: alter unpräfixt importierter test_event_protocol |
| [baseline-release-unittest.txt](baseline-release-unittest.txt) | unverändertes Releasearchiv, `-m unittest discover -s tests -v` | PASS 1147 / 94.012s |
| [UEBERNAHMEMATRIX.md](UEBERNAHMEMATRIX.md) | dreiweg-dateiweise Portierung gemeinsame Basis/Feature/Release; Namespace-normalisiert | alle Produktmodule/Tests mit Regel; fünf Assertionnachfolger einzeln zugeordnet |
| [assertion-inventory.json](assertion-inventory.json) | Python-AST Klassen-/Testmethodennamen der drei Stände vergleichen | keine Release-Methode fehlt; fünf Feature-Nachfolger explizit |
| [integration-first.txt](integration-first.txt) | erster kombinierter `-m pytest -q` | 1211 PASS, drei FAIL; Ressourcennamespace/Nullableflag-Roundtrip korrigiert |
| [integration-repros.txt](integration-repros.txt) | `-m pytest -q tests/test_cv2_000_integration.py` vor Fixes | drei FAIL, drei PASS; Startup-/Editor-/CI-Fix begründet |
| [focused-tests.txt](focused-tests.txt) | gezielte Config/Prefs/Hotkey/History/UI/Trigger/Build-/Releaseguardtests | PASS 184 / 8.16s; späterer Env-Negativtest zusätzlich in Gesamtsuite |
| [tests-pytest.txt](tests-pytest.txt) | final `-m pytest -q` | PASS 1221 / 95.19s, keine Skips |
| [tests-unittest.txt](tests-unittest.txt) | final `-m unittest discover -s tests -v` | PASS 1221 / 95.823s, keine Skips |
| [final-checks.txt](final-checks.txt) | compileall, diff --check, deterministische Arbeitsstrukturprüfungen | tatsächliche Endresultate im Log |
| [structure-check.txt](structure-check.txt) | allgemeines Test-Arbeitsstruktur.ps1 | PASS 0 Fehler/0 Warnungen |
| [block-check-baseline.txt](block-check-baseline.txt), [block-check.txt](block-check.txt) | älteres Test-Arbeitsblock.ps1 auf unverändertem Parent und integriertem Stand | tatsächlicher FAIL 6/7; SKIPPED_EXPECTED als nicht V2-anwendbar: aktueller Vertrag verlangt 30_AUSFUEHRUNG und eigenes Aktenmodell; Erklärung im Report |
| [record-check.txt](record-check.txt) | Projektpython [check_records.py](check_records.py) | V2-spezifische Akten-/Link-/Requirement-/Statusprüfung, tatsächliches Resultat im Log |
| [packaging-build.txt](packaging-build.txt) | `-m build --sdist --wheel` (isoliertes Backend) | PASS; dist voice_stt_client-1.0.0 Wheel/sdist |
| [packaging-check.txt](packaging-check.txt) | `-m twine check dist/*.whl dist/*.tar.gz` | beide PASS |
| [wheel-install.txt](wheel-install.txt), [sdist-install.txt](sdist-install.txt) | `-m pip install --no-deps --target <je eigenes Tempziel> <Artefakt>` | beide installiert; sdist backendgebaut |
| [wheel-smoke.txt](wheel-smoke.txt), [sdist-smoke.txt](sdist-smoke.txt) | Projektpython [installed_smoke.py](installed_smoke.py) mit Zielargument, CWD `%TEMP%`, PYTHONPATH ausschließlich Installationsziel | PASS: installierter Namespace, keine core/ui-Shims, Config, alle acht gültigen WAVs, Attribution, Metadatenentrypoint/Version, app GUIimportsmoke; SHA256 jedes Produktfiles |
| [source-preservation.txt](source-preservation.txt) | Projektpython [qualify_sources.py](qualify_sources.py) | PASS: core/Trigger nur Namespaceänderungen, Featuredefaults/Abhängigkeiten erhalten, Assets bytegleich, Wheel-/sdist-Manifeste identisch und gleich Source |
| [frozen-build.txt](frozen-build.txt) | `scripts/build.py --dist-dir dist-feedback-rc-cv2-000` | PASS: EXE 75.424.770 Bytes, Version1.0.0, Frozen Versions-/Qt-Importsmoke ohne Server/Mikrofon |
| [artifact-hashes.txt](artifact-hashes.txt) | `Get-FileHash -Algorithm SHA256` Wheel/sdist/EXE | Binäridentitäten; Binaries bleiben uncommitted im ignored Distverzeichnis |

Saubere Baselinearchive und getrennte Installationsziele liegen lokal unter `%TEMP%/voice-stt-cv2-000-*`, ohne historische Worktrees zu verändern. Die Quellenarchive entstanden über `git archive <SHA>` und tar-Auspacken; keine Übernahme einer alten Vorbereitungsablage. Nicht ausgeführt: echte V2-Verbindung, physische Mikrofon-/ASR-/Clipboard-/Hotkey-/LED-/Soundwahrnehmung. Sie sind keine AP000-Pflichtfälle und bleiben späteren Paketen zugeordnet. Der AP000-Zwischencheckpoint verlangt die integrierte Clientbasis und besteht in Selbstchecks; keine unabhängige ROOT-Abnahme vorweggenommen.
