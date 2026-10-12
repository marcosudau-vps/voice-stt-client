# R01 – Evidenzindex

Status REVIEW_READY. Alle Resultate sind Selbstchecks; unabhängige Abnahme offen.

- [Windowsqualifikation](windows-validation.json): Basis `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0` plus exakter [Produktdiff](tested-product.patch), SHA256,185 Runtimequellhashes/normalisierte Gitblobs, OS/Python/Dependencyidentität, vollständige Commands/Exitcodes/106 und1339 Tests, Zeitstempel, alle Loghashes.
- [Vollständige Windows-Suite](windows-full-unittest.txt): unittest discover -s tests -p test_*.py -v;1339 PASS, keine Skips.
- [Gezielte Regression](targeted-unittest.txt): -W error -m unittest tests.test_v2_mirror tests.test_v2_transport tests.test_v2_protocol -v;106 PASS.
- [Echter Servercheckpoint](server-mirror-checkpoint.json): scripts/check_v2_server_transport.py --with-mirror am bytegleichen ada13b0-Export,35 PASS/46 Quellblobs; echte TCP/WS-/Domain-/Snapshotdaten, textfreie Mirrortrace und benannte Hardware/Model-/Bootstrapgrenzen. Exakte Pfade/Runtime im Windowsmanifest.
- [compileall](compileall.txt): -m compileall -q voice_stt_client scripts tests, Exit0 (leerer Erfolgslog).
- [Ausführbarer Qualifikationslauf](qualify_windows.py): vier obige Befehle, Runtime/Basis/Diff/Hashbindung; nur mit Clientprojektvenv. Export-/Servergitpfade sind tatsächliche Runparameter, keine Produktvoraussetzung.
- [35 Requirementmethoden](requirement-coverage.md), [maschinenlesbar](requirement-coverage.json): AST-/vorhandene Methodenzuordnung und Kandidatenbelege.
- [Vorher-Baseline](baseline-targeted.txt):61 PASS vor Produktänderung, Projektvenv, unittest tests.test_v2_protocol tests.test_v2_transport -v, Exit0.
- [Vorgängerübernahme](predecessor-canonicalization.json): PR #4, Parent/Single-Parent/Treegleichheit, R04-PASS und tatsächlicher Freigabewortlaut aus Git.
- [Startvertragshashes](start-contract-hashes.json): Paket/K-02/K-03/Manifest vor Planpflege.
- [Aktenprüfung](records-validation.json), [Abgabekonsistenz](handoff-validation.json): Status, Links, Produkt-/Gitblobgleichheit und unveränderte Requirementtexte.

Alle Testtexte synthetisch; keine Credentials, Nutzeraudios oder Laufzeitdatenbanken. Prüflogs sind bewusst versionierte Qualifikationsevidenz. Finale PR-/Head-/Treeidentität wird in der Git-/PR-Übergabe genannt.

[Veröffentlichter Implementierungsstand: exakter Produktdiff,185 Gitblobs und vier vollständige Loghashes](implementation-publication.json). PR-Verweise folgen im administrativen Abgabecommit.
