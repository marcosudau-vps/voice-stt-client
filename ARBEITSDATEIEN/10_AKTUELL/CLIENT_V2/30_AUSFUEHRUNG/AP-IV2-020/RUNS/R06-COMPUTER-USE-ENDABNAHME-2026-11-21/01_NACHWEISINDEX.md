# R06: Index der automatisierten Nachweise

Alle Originale liegen unverändert im Desktop-Testordner unter Nachweise. Git enthält lediglich lesbare, anonymisierte Textkopien. Original- und Git-SHA256 weichen wegen der Redaktion voneinander ab.

| Original | Git-Kopie | Original SHA256 | Git SHA256 |
|---|---|---|---|
| suite.stderr.log | [EVIDENCE/AUTOMATIK/unittest-1407-full-redacted.txt](EVIDENCE/AUTOMATIK/unittest-1407-full-redacted.txt) | 92b780d48b9ced0be94e0a72a5b267d66836ea9d03a80ae9c432497067760f81 | 779b504471c798971ee051aeaf3c19c996406e4171072fbc3bd20252b248ea93 |
| build-manifest.json | [EVIDENCE/AUTOMATIK/build-manifest.json](EVIDENCE/AUTOMATIK/build-manifest.json) | b4fbc70e6b4ccb2f891fb14fb0d2734d1b373ef29f447552492fe0bb2c52fa8d | 397b99d95779d5629ca8853b6ab8466cc5f236e73a163aadf365c538a2da90b7 |
| build.stderr.log | [EVIDENCE/AUTOMATIK/pyinstaller-build-redacted.txt](EVIDENCE/AUTOMATIK/pyinstaller-build-redacted.txt) | 9a0096fb7a859e3ccb3b140c8b3bea08d1ee999d70d9993ab7ed9b06a37ba8e2 | a0ada946bd7eeef839a0aed5c07027d58fd620b28b09548a79737c61fd4229a8 |
| build.stdout.log | [EVIDENCE/AUTOMATIK/build-stdout-redacted.txt](EVIDENCE/AUTOMATIK/build-stdout-redacted.txt) | d01e98df8edba10b0532365a29fc0bc90efb9ab0d0036d1560367d03b334b6c8 | d01e98df8edba10b0532365a29fc0bc90efb9ab0d0036d1560367d03b334b6c8 |
| live-v2-result.json | [EVIDENCE/AUTOMATIK/live-v2-result.json](EVIDENCE/AUTOMATIK/live-v2-result.json) | 742ee16b693c870da07d2bdf9f7315b2580edf88a97722ead24aab7ce8fcffc0 | 9ee066138ea9e4b33f72dd250a763bb950c1b2da858b3be527cdc9eb9993cf15 |
| live-v2-speech-result.json | [EVIDENCE/AUTOMATIK/live-v2-speech-result.json](EVIDENCE/AUTOMATIK/live-v2-speech-result.json) | d82ae11b7b14cac7fb1a3cf0d3890f8fa0865d69f982c5b213f0bf140da69121 | b0693e818441bac2f93641a87066af7ee80fc53dd9a3706374ad34cf7d263cb9 |
| live-v2-settings-result.json | [EVIDENCE/AUTOMATIK/live-v2-settings-result.json](EVIDENCE/AUTOMATIK/live-v2-settings-result.json) | 49264ba5d1055824e4e128e5686215e720bc427572756bf55d3adf75f0a6a82a | dd90c236f1c63d89635d68a181b0fd457c707206a1d7378b086c91d4c2f449d3 |
| live-v2-wake-reconnect-result.json | [EVIDENCE/AUTOMATIK/live-v2-wake-reconnect-result.json](EVIDENCE/AUTOMATIK/live-v2-wake-reconnect-result.json) | 30b752e773775cc6ab9ab1996f76399ad12191e325fe9149d7b80584f97bae5c | 24d2296b3169642d93f518468096736131cb6f533a3541071ba9abc83299208a |
| frozen-live-v2-report.json | [EVIDENCE/AUTOMATIK/frozen-live-v2-report.json](EVIDENCE/AUTOMATIK/frozen-live-v2-report.json) | cafa44991073c31dd96ae3bafef119e34bfb27f54a7575b91baa531e8c013744 | 63a958aa5a5a13cf02df4eb2fded59a3caf914da3aceab7beb05f11de4cb5746 |
| settings-roundtrip-result.json | [EVIDENCE/AUTOMATIK/settings-roundtrip-result.json](EVIDENCE/AUTOMATIK/settings-roundtrip-result.json) | a06bf8eafa1246cf5e9dca6085f7536b49697e2b8caf55c66cd77f8197e8f1a4 | 456be53dd1de05517d1d287bec3eb7bddfca01bc501db766d2083467b0eb937a |
| release-guard.log | [EVIDENCE/AUTOMATIK/release-guard.json](EVIDENCE/AUTOMATIK/release-guard.json) | 1529773672946789c7d8a4c48e57e8795de87dbaab8e4b4b60d4e052b2c4f817 | 9785e42359a50a4adc0b2500afdae4459ac1d589c7e77882d684bd6a8f684d3d |
| twine-check.log | [EVIDENCE/AUTOMATIK/twine-check.txt](EVIDENCE/AUTOMATIK/twine-check.txt) | 80a9eb60e4886751fc537edd6e0fb967b2cc005ccb3fbe5a5fa49ada0996027f | 8b59545c48b3924f39e146beb6a3415b10dfcfa3eac6f90c8ade817d0f8e102f |

## Absichtlich nicht in Git veröffentlicht

- EXE: SHA256 28cea377ee59b2342fd9f5fd2d10a93cc6e2a8a1df950a9a1efa3af216ab65f8, 77.414.876 Bytes.
- Synthetisches Sprachtestaudio: SHA256 4ea6171f8d8a747355edab60e393cf11c48b0751fa7a19d6e62a2503d161d910, WAV bleibt lokal.
- Wheel und sdist bleiben lokale Build-Artefakte; Hash und Validierung stehen im release-guard.json und twine-check.txt.

## Testlog-Einordnung

Der vollständige unittest-Log enthält auch durch Negativ-/Recoverytests absichtlich erzeugte Tracebacks und Failed-Meldungen. Entscheidend ist der abschließende Runnerstatus: Ran 1407 tests in 179.653s; OK. Es wurden 1407 test_-Startzeilen erkannt und keine FAIL-, ERROR- oder skipped-Teststatuszeilen. Der ursprüngliche Rohlog wurde nicht verändert.
