# AP-CV2-050 / R01-UMSETZUNG – REVIEW_READY

**Status:** REVIEW_READY. SELF_CHECK_PASS am 2026-10-12; unabhängige Abnahme offen.

## Auftrag und Startprovenienz

[Originalauftrag](00_PROMPT_ORIGINAL.md), [Paketvertrag](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-050.md), [Evidenzindex](EVIDENCE/INDEX.md). Planrevision10/Rollenregeln7, unveränderte fachliche Vertragsbasis [Hashes](EVIDENCE/start-contract-hashes.json). Repository marcosudau-vps/voice-stt-client, Base feat/client-v2, Kandidatenbranch work/client-v2/ap-cv2-050. Exakter kanonischer Parent `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`, Tree `fde6009d3d9c699a92f7cc0ef8a6452e4903c1e0`; Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

AP040 war in den Einstiegstexten noch ROOT_PASS, wurde aber tatsächlich in PR6 mit menschlicher Freigabe übernommen. Vor Paketstart R06-PASS, gesicherten Originalfreigabeprompt und tatsächliche Git-/PR-Provenienz geprüft: ein neuer Singleparentcommit vom AP030-Parent, Baumgleichheit zum finalen PR6-Head. [Übernahmenachweis](EVIDENCE/predecessor-canonicalization.json). AP050 stammt exakt davon, keine fremden Workingtreeänderungen. Gittransport für Paketbranch/PR durch workflowweiten Originalauftrag autorisiert; keine kanonische Übernahme beauftragt.

## Ergebnis und interne Entscheidungen

Neuer `core.v2_controls`-Service routet Primary/Secondary quellenneutral über tatsächlichen V2Transport/Mirror. Intentbindung konserviert Generation, Session und ursprüngliche Activation-ID; gemeinsame Pendingbarriere verhindert parallele Doppelcommands. Waiting-refresh/Closing-refresh sind wirkungslos, Closing-finish/cancel bleiben an die alte ID gebunden. Audio-ready, Manualeffectiveness, desired Manualpause und Configuring/Resync werden vor activate geprüft. Keine lokale Frist, kein VAD-Refresh, kein Capturestop oder Textzurücknehmen.

Zwei getrennte Runpausen werden vor I/O im Service/Transport gehalten; vollständige Masken werden geordnet gesendet. Keine optimistische Ackbestätigung: PauseView basiert auf aktueller autoritativer Mirrorprojektion. Bootstrap startet weiter beide unterdrückt und stellt die neueste Maske vor READY wieder her, auch bei Änderung während Ackwarten. Ein älterer Ack überschreibt keinen neueren Wunsch. Reconnect/Geräteverlust halten die Wünsche; neuer Prozess startet neue runId mit false/false.

`V2HotkeyManager` erweitert den etablierten Win32-/Qtpfad um unabhängige Rollen und Utilities, MOD_NOREPEAT, Modifier/VK-Validierung sowie atomaren Apply mit vollständigem Rollback. Bei zusätzlichem OS-Rollbackfehler sind keine Teilbindings aktiv; Fehler werden separat exponiert. Neue IDs werden nicht wiederverwendet. Keine manuelle Quelle ist für die Registrierung Voraussetzung. Gemeinsame Keynormalisierung lehnt nicht repräsentierbare Nicht-ASCII-Alphanumerik ab.

ControlConfig und reine Legacykonversion bewahren Alias, explizite Einzelcontrols, Utilities und enabled. Beide expliziten Finish/Cancelbindings erzeugen einen Konflikt mit unverändertem Originalprofil statt Verlust. Persistenz/Dialog bleiben AP070/080. Gemäß vorgeschlagener Modulzuordnung/Umsetzungsspielraum liegt der V2-Service separat von der funktionsfähigen V1-Komposition; die Gesamtverdrahtung ist AP100, Legacyabbau AP110. Die V2Steuerung verwendet keine Legacytimer. Kein Requirementowner verschoben, keine Serverquelle geändert.

## API- und Lifecycleübergabe

[Vollständige öffentliche API](../../../../../../../docs/protocol-v2-controls.md): ControlSlot/ActiveAction/ControlConfig/ControlIntent/PauseView, migrate_hotkeys/ControlMigrationConflict, plan_control, V2ControlService.press/control/execute/set_pause/toggle_pause/close; V2STTSession.set_desired_suppression; V2HotkeyManager.register/unregister/apply/role_ids/last_failure/rollback_failure.

Core-API im asyncio-Thread, Win32manager im Qt-Mainthread. Callback bindet vor Queueing auf unveränderlichem publiziertem MirrorView die ID, dann execute im Core. press ist nur Komfort im Core; Qt darf dessen Slot nicht ungebunden zeitversetzt schicken. Utilities separat. Service genau einmal vor run anschließen, lokale AP040-Audiobarriere explizit liefern, close Task joinen und Transportcleanup erhalten. Persistieren erst nach erfolgreichem Apply, Doppelbindkonflikt sichtbar auflösen. Bestehende Startanleitung `.\venv\Scripts\python.exe -m voice_stt_client` bleibt gültig, startet noch V1-Komposition.

## Tests und realer Zwischencheckpoint

Baseline vor erster Produktänderung: **160 Tests PASS** / 19.895s. Danach **19 neue AP050-Tests**, davon die vollständige **5Phasen × 4Aktionen × 2Slots × 2Quellen = 160 Unterfälle** im Phasenmatrixtest. Client-FakeWebSocketprüfungen verwenden echte Session/Tracker/Mirror und kontrollieren ausgehende Wirecommands, verlorene Acks, Bootstraprennen, Resync, staleA und Closing-no_change. Fakebackend prüft Teilregisterfehler und zusätzlichen Rollbackfehler. Zwei anfängliche Harnessfehler (zu spätes Attach, Snapshotfixture ohne tatsächlichen Reset) wurden vor Qualifikation korrigiert; keine Tests entfernt oder übersprungen.

Kandidatengebundene Windowsqualifikation: **297 gezielte Tests** (-W error) PASS/24.881s, **1397 gesamte Tests** PASS/114.920s, compileall und staged/unstaged git diff --check PASS. Windows11-10.0.26300-SP0, Python3.12.10 aus Projektvenv, PySide6 6.11.1, Qt offscreen. [Manifest mit vollständigen Befehlen/Exitcodes/Zeiten/Hashes](EVIDENCE/windows-validation.json), vollständige Logs im Index. Vor/nach dem Lauf Produkt-/Test-/Skriptquellen unverändert; exakter getesteter [Diff](EVIDENCE/tested-product.patch) gegen Parent plus qualifiedGitBlobs identifiziert den Kandidaten. Abgabeverweise sind nachgelagerte administrative Ergänzungen; tatsächliche Commit-/Tree-Identität wird aus Git in PR und finaler Übergabe genannt statt einer unmöglichen Selbst-SHA im Commit.

**79 tatsächliche TCP/WebSocket-Serverchecks PASS**, alle drei Basismodi manual-only/wake-only/beide: Activate, Controlphasen, getrennte/both-Pausen, kein Watchdogrefresh aus VAD, Segment max(alteFrist,now+refresh)/Followup now+timeout ohne Kumulierung, erfasstes Audio nach Finish, Cancel ohne Rücknahme veröffentlichter Finals, staleA lässt B unverändert, Deviceverlust/Sessionreconnect und Prozessneustart. **46 gepinnte produktive Serverquellblobs** vor/nach Lauf bytegeprüft. GateAwareRecorder/AutoScheduler/WakeHit ersetzen Modell-/VADausgaben, permissive Artifactprobe ersetzt Inferenz, kontrollierte Serverzeit prüft Fristen. Bootstrap verwendet benannte Settings/Audioanbindung; keine fertige App/echte ASR behauptet.

**16 tatsächliche native Windowschecks PASS**: reale RegisterHotKey-/UnregisterHotKey-Aufrufe, Qt-Nativefilter, echte WM_HOTKEY über SendInput, einmalige Rollen-/Utilitycallbacks bei gehaltenen Wiederholungen, fremder Besitzer/Fehler1409, vollständiger Rollback und alter Key funktioniert, erfolgreiche neue Registrierung und alte IDs ungültig, Cleanup. Eingabe synthetisch auf OS-Ebene, keine menschliche Hardware- oder Finaltextabnahme. Erwarteter1409-Negativlog separat vollständig gesichert.

Alle **CONTROL-01 bis CONTROL-14** einzeln in [Requirementbelegen](EVIDENCE/requirement-coverage.md), Traceabilitymatrix/requirements.json fortgeschrieben. Status bleibt CLIENT OPEN bis unabhängiger Abnahme. Keine fehlenden Paketpflichtfälle, kein eigener ROOT_PASS.

## Abgabe und verbleibende Gates

Akten-/Link-/Statusprüfung und veröffentlichter Gitblobabgleich vor Übergabe; Paket-PR mit Base feat/client-v2, exaktem Kandidaten und Aktenlinks. Nach vollständiger Bereitstellung Schreibrecht pausiert, nächster Schritt **frischer unabhängiger Review desselben Gesamtpaketkandidaten**. Keine Findings offen aus eigener Umsetzung, unabhängige Prüfung noch ausstehend. Kein Merge, AP060-Start, Release oder Server-Distributed-Abschluss.

Restgrenzen sind planmäßige Folgepakete: persistente Settings/Benutzerentscheidung AP070/080, vollständige Runtimekomposition AP100, Legacyabbau AP110, echte Mikrofon-/ASR-/Clipboardproduktabnahme AP-IV2-020. Die dokumentierten Testgrenzen sind keine dortigen PASS-Nachweise.
