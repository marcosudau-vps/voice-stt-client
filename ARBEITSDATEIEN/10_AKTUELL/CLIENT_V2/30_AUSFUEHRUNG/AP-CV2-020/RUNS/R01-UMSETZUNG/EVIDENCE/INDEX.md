# R01 – Evidenzindex

Status REVIEW_READY, PR #4. Getesteter Commit `7546298f26e00b83ad4c9510a9b8c1e7e6726fc3`, Tree `7bd496ef70a192781ff999b31695b3ef3fd72210`, Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Serverada13b0.
Projektvenv Python3.12.10, Windows11/AMD64, QT_QPA_PLATFORM=offscreen.

- [Qualifikationsmanifest](windows-validation.json): vollständige Befehle,
  Runtime/Abhängigkeiten, Start/Ende, Exitcodes, Testzahl, SHA256 der Logs.
- [Windowsvollsuite1290](windows-full-unittest.txt): unittest discover -s tests -p test_*.py, Exit0.
- [Gezielte57 Tests](targeted-transport-codec-unittest.txt): unittest Codec/Transport -v -W error, Exit0.
- [Servercheckpoint21](server-transport-checkpoint.json): tatsächlicher V2STTSession an
  gepinnter FastAPI-App via Loopback TCP/WS;46 Originalquellen bytegeprüft.
  GateAwareRecorder/AutoScheduler und benannter Clientbootstrap als Testgrenzen.
- [compileall](compileall.txt): vollständige Paket-/Script-/Testkompilation, leerer Log, Exit0 im Manifest.
- [Vorgängerübernahme](predecessor-canonicalization.json): R02-PASS, tatsächliches
  Freigabeoriginal, gemergter PR #3, Single-Parent/Einzelcommit/Treegleichheit.
- [Startvertragshashes](start-contract-hashes.json): AP020 und K-01/K-04 vor Pflege.
- [Baseline1263](baseline-full-unittest.txt), [Exit0](baseline-exit.txt): vor Produktänderung.
- [Historischer Transportstand27](targeted-iteration5.txt) und [Serverstand21](server-iteration4.txt).
- targeted-iteration1..4/server-iteration1..3: nachvollziehbare fehlgeschlagene
  Harnessprüfungen; keine finale Qualification. Ein historisches nachgestelltes
  Leerzeichen in targeted-iteration1 wurde entfernt, keine finale Pflichtlogänderung.

Finale Diff-/Akten-/PRprüfung und ausschließlich administrative Differenzen zum
getesteten Commit stehen im [administrativen Prüfbeleg](administrative-validation.json).
Der endgültige eingereichte SHA/Tree und dessen Remote-CI stehen im PR-Übergabekommentar.
Unabhängiger Review offen; keine ASR-/Hardware-/Qt-/Gesamtproduktabnahme behauptet.
