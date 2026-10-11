# R01 – Evidenzindex

Status **REVIEW_READY**. Parent `1cf076bd2ed56929b1a3780bc140da51348a8295`, getesteter Commit `9838558173b6bd88d4620b20d4e2e9d832e814c7`, Tree `c3a0b826e5d9614ad6dfb80b51815af77f8090bf`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Windowsruntime und vollständige Kommandos im [Qualifikationsrecord](windows-validation.json). Synthetische Daten; keine Nutzertranskripte oder produktiven Credentials.

| Artefakt | Erzeugung / Identität / Ergebnis |
| --- | --- |
| [predecessor-canonicalization.json](predecessor-canonicalization.json) | Tatsächliche Git-/PR-#2- und Parent/Treeprüfung:1 Single-Parent-Aggregat, PASS/Freigabe gelesen, PASS. |
| [start-contract-hashes.json](start-contract-hashes.json) | SHA256 verbindlicher Startquellen auf kanonischem Parent, unveränderte Quellen nachvollziehbar. |
| [baseline-full-unittest.txt](baseline-full-unittest.txt) | Projektvenv, Windows/offscreen, vor erster Codeänderung `-m unittest discover -s tests -p 'test_*.py'`:1233 OK95.998s; kein separat gespeicherter Shell-Exitcode. |
| [windows-validation.json](windows-validation.json) | Python-subprocess auf sauberem Commit9838558173b6bd88d4620b20d4e2e9d832e814c7; Laufzeit, genaue argv, Zeiten, Exitcodes, Testzahlen und SHA256 der vier vollständigen Logs. PASS. |
| [targeted-protocol-unittest.txt](targeted-protocol-unittest.txt) | `-m unittest tests.test_v2_protocol -v`:30 PASS, Exit0. |
| [server-contract-checkpoint.json](server-contract-checkpoint.json) | `scripts/check_v2_server_contract.py --server-root <ada13b0-Gitbytesexport> --server-repository <Serverrepo>`:188 PASS, Exit0,17 einzeln gehashte Originalquellen. Echter Clientcodec/Serverparser, modellfrei; Grenzen im Report. |
| [compileall.txt](compileall.txt) | `-m compileall -q voice_stt_client scripts tests`:Exit0, erwartete leere Ausgabe; Exitbeleg/Leerdateihash im Qualifikationsrecord. |
| [windows-full-unittest.txt](windows-full-unittest.txt) | `-m unittest discover -s tests -p 'test_*.py'`:1263 PASS93.640s, Exit0, kompletter stdout/stderr. |
| [administrative-validation.json](administrative-validation.json) | `git diff --check`; gemeinsamer Aktenprüfer mit geänderten Markdowndateien und tatsächlich abgerufenem PRbody; Postqualifikationsdiff nur administrativ. PASS. |
| [remote-first-publication.json](remote-first-publication.json) | GitHub-Dateiblobs commitgebunden mit lokalen Gitbytes verglichen; qualifizierte Produktidentität und Onlineverfügbarkeit der Abgabe. PASS. |

Alle Loghashes beziehen sich auf UTF8-LF-Gitbytes; komplette stdout+stderr, allein CRLF nach LF umgesetzt. Originalvektoren separat [mit Provenienz](../../../../../../../../tests/contracts/protocol-v2-provenance.json). Finale eingereichte SHA/Tree und finale CI aus PR-/Gitübergabe, administrative Nachträge gegen getesteten Commit vergleichen. Keine eigene unabhängige Abnahme.
