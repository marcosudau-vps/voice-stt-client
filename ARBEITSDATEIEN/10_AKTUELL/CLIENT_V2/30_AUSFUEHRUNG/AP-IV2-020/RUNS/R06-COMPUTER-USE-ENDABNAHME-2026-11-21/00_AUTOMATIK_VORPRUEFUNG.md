# R06 – Automatisierte V2-Vorabnahme vom 21.11.2026

**Technisches Prüfurteil: PASS für die hier tatsächlich durchgeführten automatischen Prüfungen.**
**Gesamt-Endabnahme: OFFEN. Merge, Release und Serverpromotion: NICHT FREIGEGEBEN.**

## Gegenstand und Identität

| Merkmal | Nachgewiesener Wert |
|---|---|
| Repository | `marcosudau-vps/voice-stt-client` |
| Geprüfter Produkt- und EXE-Quellcommit | `9f9fdf2b19f99a6d4f255d76b6cfa9ef3de493b2` |
| Zugehöriger Produktbranch | `feat/client-v2` |
| Dokumentationszweig | `work/client-v2/ap-iv2-020-r06-vorabnahme` |
| Server-Commit | `e95858e3c010a7e9324b49bb44fee349abe7128a` |
| Testserver | `voice-stt-server-v2-final-test` |
| WebSocket | `wss://final.v2.voice-stt-server.marcosudau.com/ws/v2` |
| Health | `https://final.v2.voice-stt-server.marcosudau.com/health` |
| Clientversion | `1.0.0` (keine Releasefreigabe) |
| Umgebung | Windows-PC `CSL-DESKTOP-PC`; Python 3.12.10, PySide6 6.12.0, PyInstaller 6.21.0 |
| Desktop-Test-EXE | 77.414.876 Bytes; SHA256 `28cea377ee59b2342fd9f5fd2d10a93cc6e2a8a1df950a9a1efa3af216ab65f8` |

**Wichtig:** Dieser nachträglich angelegte Dokumentationszweig verändert den geprüften **Produktstand nicht**. Sein neuer Commit-Hash ist ein Dokumentations-Commit und darf nicht als neue EXE-/Client-Buildidentität dargestellt werden. Die ältere, V1-sprechende EXE aus `feat/einheitliche-triggerarchitektur-distributed` ist ausdrücklich nicht Prüfkandidat.

## Tatsächlich bestandene automatische Prüfungen

| ID | Prüfung und belastbarer Nachweis | Urteil |
|---|---|---|
| AUTO-01 | Sauberer Quellstand `9f9fdf2`; Buildmanifest `sourceClean=true` und identischer Commit in Frozen-EXE | **PASS** |
| AUTO-02 | Vollständige Windows-Unittest-Suite: **1.407 Tests** aus 97 Modulen, `Ran 1407 tests in 179.653s`, finale Ausgabe `OK`; keine Teststatus `FAIL`, `ERROR` oder `skipped` | **PASS** |
| AUTO-03 | PyInstaller-Onefile-Build; eingefrorene `voice-stt-client.exe`; Qt-/GUI-/Ressourcenprobe einschließlich Settings/Icons/Sounds/Corethread | **PASS** |
| AUTO-04 | Desktop-EXE-SHA gegen Buildmanifest und Release-Guard erneut abgeglichen | **PASS** |
| AUTO-05 | Wheel und sdist gebaut; `twine check` für beide bestanden; Release-Kandidatenguard für EXE, Wheel und sdist bestanden | **PASS** |
| AUTO-06 | Reale `/ws/v2`-Verbindung aus `V2STTSession`: `hello` → `hello.accepted`, Protocol-Version 2, kanonische Session-ID, erwarteter Server-Commit | **PASS** |
| AUTO-07 | Audioverfügbarkeits-/Settings-Bootstrap, Session-Snapshot `applied` und beide Ready-Zustände verifiziert | **PASS** |
| AUTO-08 | Reale Kroko-Pro-Transkription über V2 mit synthetischer deutscher SAPI-Stimme: **293 PCM-Pakete**, `activate` und `finish` bestätigt, Finaltranskript abgeschlossen | **PASS** |
| AUTO-09 | Live-`SettingsUISession` mit **19 Schemafeldern** und **25 Wake-Words**; Serverdefault-Schreibversuch ohne Adminfreigabe korrekt als `admin_check_required` abgewiesen | **PASS** |
| AUTO-10 | `manual=true` plus `wakeWord=true` gleichzeitig serverseitig bestätigt; kontrollierter Reconnect Generation 1→2 mit neuer Session-ID und unveränderten Triggern | **PASS** |
| AUTO-11 | Persistenz lokaler Konfiguration im **separaten Scratch-Profil**: Hotkeys, Wake-Wahl, Overlay, Audio, Feedback, Textinjektion und LED-Helligkeit | **PASS** |
| AUTO-12 | Zusätzlicher Kontrollabruf des Testserver-Health-Endpunkts: HTTP 200 und `ready=true`; Desktop-EXE-Fingerprint erneut bestätigt | **PASS** |

Der reale V2-Sprachtest gab dieses Finaltranskript zurück:

> Guten Morgen! Dies ist ein Test der neuen Spracherkennung. Version zwei. Die Verbindung funktioniert.

Es wurden die Events `activation.started`, `activation.phase_changed`, `segment.recording_started`, `segment.recording_ended`, `transcription.accepted`, `activation.input_closed`, `transcription.completed` und `activation.completed` beobachtet. Kein `transcription.failed`. Diese Aussage bezieht sich auf **synthetisches Audiomaterial**, nicht auf einen physischen Mikrofonmitschnitt.

### Interpretation von Fehlermeldungen im vollständigen Testlog

Die vollständige Suite enthält absichtlich ausgeführte Negativ-/Recoverytests für simulierte DB-Ausfälle, Clipboard-Störungen und andere Fehlerpfade. Deshalb finden sich im Log Meldungen wie `Failed to save history entry` und erwartete Tracebacks. **Sie sind nicht mit einem gescheiterten Testlauf zu verwechseln.** Die finale Runnerausgabe lautet `OK`; 1.407 `test_`-Startzeilen wurden anhand des Originalprotokolls erneut gezählt. Vollständige redigierte Logs und JSON-Belege sind über [01_NACHWEISINDEX.md](01_NACHWEISINDEX.md) erschlossen.

### Abgrenzung der Frozen-GUI-Probe

Die EXE-GUI-Probe erfolgte mit `QT_QPA_PLATFORM=offscreen` und kontrolliert nicht verfügbarem Audioeingang, um den bestehenden Desktopclient nicht zu stören. Sie bestätigt die GUI-/V2-Bootstrapfähigkeit **nicht** aber reale Mikrofonaufnahme, globale Hotkeys oder Soundwiedergabe. Die tatsächlichen Probe-Marker lauten `audioCaptured=false`, `globalKeysRegistered=false`, `playbackTest=NOT_RUN`.

## Offene reale Prüfungen – kein stillschweigendes PASS

Diese Prüfungen sind für die **konkrete finale V2-Desktop-EXE** noch nicht durch den neuen automatischen Prüflauf nachgewiesen:

1. Regulärer Desktopstart/Tray/Overlay/Fokus; bestehende Altclient-Instanz vorher kontrolliert beenden.
2. Echte ReSpeaker-XVF3800-Mikrofonaufnahme, Geräte-Mute und physisches Device-Recovery.
3. Tatsächliche Wake-Word-Erkennung, Wake-Fehlauslösungen, Stille und Kombinationsbetrieb mit manuellem Trigger.
4. Globale Win32-Hotkeys, Umbelegung, Konflikte und Reinsert.
5. Clipboard-/`SendInput`-Texteinfügung in zwei echte Zielanwendungen, History und Exactly-once-Verhalten.
6. Tatsächliche ReSpeaker-LED-Animation sowie hörbare Start-/Stop-/Feedback-Sounds.
7. Sicht- und Bedienprüfung sämtlicher lokaler, Session- und Server-Einstellungen; Reload, Validierung, Rollback.
8. Reconnect / Netzabbrüche / Cancel / Refresh / Finish im tatsächlich laufenden Desktopclient.
9. Legitime Adminprüfung und Serververwaltung innerhalb des genehmigten Scopes; **keine ungefragte Serverdefault-Mutation**.
10. **30–60 Minuten** ununterbrochener praktischer Betrieb, mindestens zehn Diktate, lange Aufnahme, Ressourcen-/Logkontrolle.
11. Separate Lizenz-/Redistributions- und Releaseentscheidung, insbesondere zum Kroko-Pro-Modell.

Ältere Arbeitsakten aus `R01` bis `R05` bleiben als historische Nachweise bestehen; für diese abschließende neue Buildidentität werden fehlende Realbelege nicht ohne nachvollziehbare Kandidatenzuordnung als bestanden ausgegeben.

## Freigabe- und Schreibregeln

- **Kein bislang bekannter Fehler aus den tatsächlich ausgeführten automatischen Prüfungen.** Das schließt unbekannte Fehler und noch nicht ausgeführte Szenarien nicht aus.
- Die praktische Abnahme ist **OFFEN**, bis ihre Test-IDs mit reproduzierbaren Computer-Use-/Hardwarebelegen beurteilt sind.
- Für eine kanonische Übernahme sind zusätzlich die projektinternen unabhängigen Review- und menschlichen Freigaberegeln zu beachten (`AGENTS.md` und Qualifikationsreferenz).
- **Kein automatischer Merge nach `feat/client-v2` oder `main`, kein Release, keine produktive Serveränderung.** Ein Dokumentations-Pull-Request kann zur unabhängigen Sichtung erstellt werden.
- Sensible Rohdaten, ausführbare Dateien, Modellbinärdateien und synthetisches Audio wurden **nicht** in Git hochgeladen. Originale verbleiben lokal; [01_NACHWEISINDEX.md](01_NACHWEISINDEX.md) hält Hashes fest.

## Codex-Folgeauftrag

Startverzeichnis: `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\v2-final-automatik-nachweise-20261121`.

Isolierter GUI-Testordner: `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme`.

Details zu den Dokumentationsorten und den zu ergänzenden realen R06-Belegen: [02_CODEX_HANDOFF.md](02_CODEX_HANDOFF.md).

**Kurzurteil: TECHNISCHE VORABNAHME PASS; PRAKTISCHE ENDABNAHME OFFEN; MERGE/RELEASE NO-GO.**
