# R06-Nachlauf · bereinigter Belegindex

Lokaler Basisordner `C:\Users\marco\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Nachweise\computer-use-2026-11-22`. Zeiten der Laufzeit-JSONL sind UTC, Zeiten im Bericht MEZ. Die Originale der Vorabnahme und deren SHA-256 bleiben über den bestehenden [Nachweisindex](../../01_NACHWEISINDEX.md), im Desktop-Index in der R06-Akte des angegebenen Worktrees erschlossen.

| ID | Herkunft und Inhalt | Lokaler Beleg |
|---|---|---|
| E01 | PowerShell- und Git-/GH-Bestandsaufnahme. Paketdateien, Git-/PR-Provenienz, Startprofil, Hash, Windows-Hardware, Launcher und Startprozess. | `testprofil-ausgang.config.yaml`, `bestand.json` |
| E02 | Aktueller technischer V2-Handshake der Kandidatenquellen und öffentlicher Health-Abruf. | `live-v2-result.json`, `bestand.json` |
| E03 | Computer Use. Leerer Notepad-Tab und lokal erzeugtes Qt-Testfeld, Fokus und nativer Hotkey. | `runtime-spur-bereinigt.jsonl` und Bedienprotokoll |
| E04 | Desktopkandidat, SQLite-Beobachtung mit lesendem Zugriff sowie selektiver Clientlog. Zwei Starts, Single-Instance, V2-Ready, LEFX, nativer Eingang und kontrollierter Shutdown im Erstlauf. | `runtime-spur-bereinigt.jsonl`, `client-log-auszug.json` |
| E05 | Zeit und Hash des gemeinsamen Cursors nach Erstlauf. Vergleich gegen Dateien nach Prozessisolierung. | `externer-cursor-nach-erstlauf.json`, `altprofil-vor-isoliertem-lauf.json`, `isolationsvergleich.json`, `repro-profilcursor.json`, `cursor-bestehende-tests.log` |
| E06 | Computer Use und zeitkorrelierter Realtime-/Final-/Paste-Beleg. Nur Metadaten, kein Fremdtext und keine Rohaufnahme. | `sapi-kurz-01.json`, `runtime-spur-bereinigt.jsonl`, `client-log-auszug.json` |
| E07 | Tatsächliche ReSpeaker-Pegelmessung in Einsekundenfenstern vor/während SAPI, ohne PCM-Dateien. | `mikrofonpegel-ohne-testwiedergabe.jsonl`, `mikrofonpegel-mit-testwiedergabe.jsonl`, `mikrofonpegel-nachprobe.jsonl`, `sapi-pegel-zeit.json` |
| E08 | Struktur-/Mustercheck für Credentials und Transkriptfelder in lokalen Testdiagnosen. | `diagnose-strukturcheck.json` |
| E09 | Prozessmessung für Onefile-Parent und Anwendungsprozess mit Basis und Folgemessung. | `soak-prozess.csv`, `soak-auswertung.json` |
| E10 | Ergänzende technische Proben an Kandidatenquellen. Katalog/Settings ohne Schlüssel oder Mutation. Ungültiger Pfad ohne Netzwerkverbindung. | `live-v2-settings-result.json`, `endpunkt-validierung.jsonl` |
| E11 | Tatsächlicher Windows-Desktop. Zugeschnittener Infobereich und ReSpeaker als Standardaufnahmegerät. Umfang der Ausschnitte enthält keine Kontoansicht. | `tray-ausschnitt-weit.png`, `windows-respeaker-eingang.png` |
| E12 | V2-Dialog. Trigger, Session, Admin-Guard, reales Readback, Wake-Katalog und reproduzierter Reload-Verlust. | `v2-lokale-trigger.png`, `v2-session.png`, `v2-admin-gesperrt.png`, `v2-reload-entwurf-5300.png`, `v2-reload-verlust-wiederholt.png`, `v2-session-apply-5200.png`, `v2-session-rollback-5000.png`, `v2-session-schreibschutz.png`, `v2-wake-katalog-jarvis.png` |
| E13 | Lokale Einstellungen und Audio-/Diagnosebetrieb. | `v2-respeaker-geraeteliste.png`, `v2-respeaker-uebernommen.png`, `v2-respeaker-pegel.png`, `v2-allgemein-clipboard.png`, `v2-darstellung-feedback.png`, `v2-logging-einstellungen.png`, `v2-diagnose-audiostarts.png` |
| E14 | GUI und native Windows-Registrierungen bei Konflikt, aus/an, Ersatzbelegung, negativem Alt-Hotkey und Rücknahme. | `v2-hotkeykonflikt.png`, `v2-hotkeys-deaktiviert.png`, `v2-hotkeys-f10-angenommen.png`, `v2-altbelegung-negativ.png`, `hotkeykonflikt-profilhash.json`, `hotkey-native-verlauf.jsonl`, `repro-hotkeymeldung.json` |
| E15 | Abschlusskontrolle nach regulärem Tray-Ausstieg, freigegebene Hotkeys, identisches Ausgangsprofil, null Prozesse. | `abschluss-kontrolle.json`, `hotkey-native-verlauf.jsonl`, `client-log-auszug.json` |

Ergebnisbilder mit fremden Editorreiter-Namen oder unkontrolliertem Diktattext wurden nicht gespeichert. Die direkte UI-Beobachtung wurde als Bedien- und Messspur dokumentiert. Die R06-Akte enthält ausschließlich redigierte Markdown-Nachweise.

### SHA-256 der lokalen Nachweise

Die maschinenlesbare Liste liegt als `beleg-sha256.json` im Nachweisordner. Die Bilder sind lokale Bildschirmnachweise. Git enthält nur diese Verweise und Prüfsummen.

| Datei | SHA-256 |
|---|---|
| `abschluss-kontrolle.json` | `b3b7cc2d462b0c83d5b9d32b4959f7646fafeea45e34c3eba04e4e0588f66327` |
| `bestand.json` | `9c495761e1c6115532baa224bbac71e9628529eb700effe9d4844417f81b6d48` |
| `client-log-auszug.json` | `fe05c4468b51c20b59127995207333921185822667f68c7c3358d70723965682` |
| `cursor-bestehende-tests.log` | `4809db9460eb30c5adca5b760fb3d3339f17a93d15b2e0c64c0f3c2f124d6499` |
| `diagnose-strukturcheck.json` | `0d1e7e77da6efaa69928eb683d333074b87101cd9f7f466616785125311cc570` |
| `endpunkt-validierung.jsonl` | `6713d3fd0b9c23b4d67db8e221e3af2acb825b08c415dc7a99ed4cf42307e2c8` |
| `externer-cursor-nach-erstlauf.json` | `3973d9c838c74d05c925624a429e63e552bdc03ba6f07d694c665b7194e7ccc3` |
| `hotkey-native-verlauf.jsonl` | `63fa937e44b9460d136358d346c05b2b5049262de693d7ce4d40e5c661dc80a4` |
| `hotkeykonflikt-profilhash.json` | `4a50f72f5e605bca9472a78b8f91c0676d9c8d880896b1375bbc273a95b227d2` |
| `isolationsvergleich.json` | `6d6a2f8a9a301cb5cca5a4160d75c0f51f01bd42f89be99933554c5f576383c4` |
| `live-v2-result.json` | `5810090395114a30150732f63a754a1092b1e090ab55fd7ee35192658afb625d` |
| `live-v2-settings-result.json` | `3a1a398a3c7dd1455f98bf3df768dd2e6ad543c24fa93dc2ffd7183a7e29dff6` |
| `mikrofonpegel-mit-testwiedergabe.jsonl` | `3accf6a7a961c6796d35ec0410844060c241a11a6ff80c5b3b95b1c3339c0841` |
| `mikrofonpegel-nachprobe.jsonl` | `45a5599687267504070aa3693bff3dd7a9c907afd9ff6c54dbba003afa7c6774` |
| `mikrofonpegel-ohne-testwiedergabe.jsonl` | `7b09f0bb22974e7649c133c7c6debb945d3c830ec0aa95d4af0c83b318fdd172` |
| `mikrofonpegel-reSpeaker-9-sapi.jsonl` | `bd46dc1ee3b112f0d37cc1d04569adde50328cf2b908fedf1195955315cd7a74` |
| `repro-hotkeymeldung.json` | `2e1260b36b1f11fc149b800783630d224af107068c5c1200d154aa9a793c2f76` |
| `repro-profilcursor.json` | `ff15b481d2df9250afea9043ee9fe73f0c1e46d3263aa8c45981c154925b1d1c` |
| `runtime-spur-bereinigt.jsonl` | `c7e2062fbc81c7460ea96c440ec525e3352d40bcaedaf6867f474d2777b55244` |
| `sapi-kurz-01.json` | `2f63eea9fe166bf5c1a5e53fdcba05caa9a423606632c19af9a2b40900630827` |
| `sapi-pegel-zeit.json` | `e499a51fcd94c85afa2a2fe46d1f0bdb09f255b4fd952e9f53ccac2dbf9e11b9` |
| `sapi-reSpeaker-9-zeit.json` | `476962300d716a174f733cc9a09db5fbbc0884c0856ea7cad39b1750cfb96303` |
| `soak-auswertung.json` | `3ac076c4768dd2cb57f1db16bc2b36e3253f312fac13f3cc35e1729411e3f718` |
| `soak-prozess.csv` | `5b073ebae85ed418b6433bb1bf6436d47edab13767556285a9a1d471d6f66014` |
| `tray-ausschnitt-weit.png` | `580dae2d98ed02fd4fff6e0faedff54a82abda8adffc2eac92864e579172b236` |
| `v2-admin-gesperrt.png` | `1155888723eaebf1e758d59c7668b4efd96df5694e0252808400282af85c001b` |
| `v2-allgemein-clipboard.png` | `7e3188d578674752a433f321bd136684cf9624ed0247b6477398aaae45c27fad` |
| `v2-altbelegung-negativ.png` | `8d87e3c4e451978d00c66385a90b4acca8d24cdd05f9108785f012d74eeed85d` |
| `v2-darstellung-feedback.png` | `6cf97be09a1e2746a069413c7a1b11b7b7e18d328723ff3fac985da26ba4f061` |
| `v2-diagnose-audiostarts.png` | `abad6c850c784088449573b5673b8c10ffa60e1d1ad0b6587adc3d2520b5db08` |
| `v2-hotkeykonflikt.png` | `33e7504d5bdddb05569c941ec70816af8155e02f6787790bff863a29f91f8f19` |
| `v2-hotkeys-deaktiviert.png` | `2e9dd8ba8b5f363a721400be2d75306bf453d61da998b2b73680e9d8088ccb44` |
| `v2-hotkeys-f10-angenommen.png` | `cc7187cea93a3c8058438af0dc68b46e2cbcd79a1b9af64192a151a83dc85cfb` |
| `v2-logging-einstellungen.png` | `8e281c0d69d41212c39e6841252f88eb2126c2e199ce56e7ae76f39fb138e3a3` |
| `v2-lokale-trigger.png` | `150cc05edec5acd897776355638084ad69bc54abbf9d628de422145fff2b0f51` |
| `v2-reload-entwurf-5300.png` | `c2c1d3cd6f29067caad12e914ec59e573edc31fc808b11497e36cb90772cf572` |
| `v2-reload-entwurf-verloren.png` | `957d717da86612fcdf925e6c45a6c19583d8381e8050307ff51cd67df6a851c6` |
| `v2-reload-verlust-wiederholt.png` | `996a21bb23deefa8d7df2d5dfabb9310f48c8c074c5a203e51c000a7c0cfc2d3` |
| `v2-respeaker-geraeteliste.png` | `2690c85c7fa8da45e367ab8ef74c59c7491316c78b9e17d452c595e6d380f493` |
| `v2-respeaker-pegel.png` | `d006cf2fba83ad32aa7fa98eadd1dfbe34b8e3568bfe55f63434df03b9f8b7be` |
| `v2-respeaker-uebernommen.png` | `198de6c4632328d2f9e5a03fa9090a3b22f34854d2cc287ebab7967beaeb8411` |
| `v2-session-apply-5200.png` | `7e36a8892e9216310abd26b3a84ec942eabec75133aeee883a525578c7c3003d` |
| `v2-session-rollback-5000.png` | `b113c07a92ed4d0a57f6140078d7f48e0f4cc5e64d03f35926f9b2f28e7840c5` |
| `v2-session-schreibschutz.png` | `2f071fd3c977e33c7a3f1ec8eb45f652d9042b8d3ef663c201f489e2dff56f2c` |
| `v2-session.png` | `65ba6ba2ae018acb1c32d0995a266468e4d00bda15918d831ce6564c83845967` |
| `v2-wake-katalog-jarvis.png` | `f0620695c53be813c17321d1088973703c8fbe5d13363d1c115a0f3b2c99410b` |
| `windows-respeaker-eingang.png` | `f5ca8e124c5bd628277487a0c505cbc353649b57424a223244b36855c05d44cc` |
