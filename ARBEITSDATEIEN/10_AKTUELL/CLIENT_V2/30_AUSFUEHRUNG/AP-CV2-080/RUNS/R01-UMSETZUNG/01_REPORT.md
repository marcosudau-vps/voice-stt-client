# AP-CV2-080 / R01-UMSETZUNG – REVIEW_READY

Stand 2026-10-12. Eigenprüfung **SELF_CHECK_PASS / REVIEW_READY**, unabhängige Abnahme offen. Kein eigener ROOT_PASS und keine Übernahmefreigabe. Nach Abgabe Paketbranch für Umsetzungsänderungen pausiert; kein automatischer AP090-Start.

## Auftrag und Startprovenienz

[Originalauftrag](00_PROMPT_ORIGINAL.md), [Next-step-Skill](../../../../PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md), [Umsetzungsskill](../../../../PLANUNG/SKILLS/voice-stt-client-v2-umsetzen/SKILL.md), [Paketvertrag](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-080.md). Pflichtlektüre, echte Git-/PR-Provenienz und bestehende relevante Baseline vor Codeänderung geprüft; Eingangsquellen [mit Hashes gebunden](EVIDENCE/input-provenance.json).

Kanonischer Parent `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`, Branch `work/client-v2/ap-cv2-080`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. [AP070-Nachweis](EVIDENCE/predecessor-canonicalization.json): tatsächlicher unabhängiger R02-PASS, menschlicher R03-Mergeprompt, PR9 MERGED, genau ein Single-Parent-Aggregat auf `473a75d02fb6d00e5664af4328dadaa44da5191a` und Baumgleichheit zum finalen Pakethead `ca90f6a2c1214a78d5edfdc51f4d3e7f37110797`. Ausgangsarbeitsbaum sauber, Branch vom gefetchten origin/feat/client-v2 erstellt. Vorläuferberichte bleiben unverändert.

Kandidatencommits, normale Paketbranch-Pushes und Paket-PR gegen feat/client-v2 sind durch den [workflowweiten Originalauftrag](../../../AP-CV2-000/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md) autorisiert. Kanonische Übernahme erfordert einen neuen ausdrücklichen menschlichen Prompt nach unabhängigem PASS.

## Ergebnis und Umsetzung

Vor Implementierung 90 relevante Baseline-Tests bestanden. Skizze: sichere originbezogene Credentialadapter und echte Adminprüfung; begrenzte Corelease mit Apply-/Drainentscheidungen; queued Qtbridge und differenzierte UI; Fault-/Thread-/Migrationstests; gepinnter realer HTTP/WS-Checkpoint einschließlich Windowsvault und sichtbarer Oberfläche; gesamte Regression und Abgabeakten.

Die neue Oberfläche zeigt lokale Trigger/Controls, Sessionwerte und gesperrte Serververwaltung getrennt. Manuell und Wake sind gleichzeitig möglich; Auswahl kommt aus dem kanonischen Katalog, beide Activeaktionen und optionaler Pauseslot sind editierbar. Mindestens eine Triggerquelle und gültige Wakeauswahl sind erforderlich. Vorhandene lokale Seiten bleiben über `SettingsDialog(v2_local=True)` nutzbar; dieser Modus entfernt die alten Mode-/Trigger-/Servergruppen.

Schema liefert Typen, Grenzen, Units, Defaultquelle, Revisionen und Applypolicies. Wunsch/requested/effective/pending bleiben getrennt sichtbar. Calibration pending ist ausdrücklich keine Empfehlung. NS-Noise/VAD ist auf Sessionseite read-only mit Adminhinweis. Leerer Katalog, unavailable/fehlende gespeicherte IDs und Ladefehler bleiben sichtbar; Inspect aktualisiert Wirksamkeit ohne Entwurfsverlust.

`SettingsService.verify_admin` liest vor einem No-change-PATCH einen tatsächlich vorhandenen aktuellen Default samt Revision. Nur ein unveränderter bestätigter No-change-Beleg entsperrt; GET und gespeicherter Key sind kein Authbeweis. Ein Revisionskonflikt wird einmal mit neu gelesenem Wert geprüft. 401/403/409/422/Persistenzfehler sind unterscheidbar. Passwortfeld wird beim Absenden geleert. `CredentialStore` verwendet die nativen Windows-Generic-Credential-APIs mit normalisiertem Originhash und Create/Replace/Delete. QSettings enthält ausschließlich Target/Saved-Metadaten, bei Adapterausfall höchstens Prozessspeicher, ohne Klartextfallback.

`SettingsUISession` verwendet die vorhandenen tatsächlichen Settings-/Controls-/Mirror-/Sessioninstanzen im vorhandenen asyncio-Thread. `V2SettingsBridge` begrenzt Requests, erzeugt je Öffnung eine neue Lease und liefert unveränderliche Projektionen über queued Qt-Signale. Close invalidiert synchron vor Taskcancellation; Epoch, Request-ID, Origin, Generation und Sessionkontext sperren alte Replies/Sideeffects. Ein bereits abgesandter HTTPwrite kann bei Close einen unbekannten Ausgang haben; später neu lesen, keine automatische Schreibwiederholung.

Apply validiert und persistiert zuerst über einen ausdrücklich angeschlossenen atomaren Profilport. Persistenzfehler verändern weder Profil noch Commands. NA-Werte werden mit tatsächlichem Snapshot bestätigt. Reconnect wird gegen die tatsächlich verbundene Trigger-/Wakeauswahl berechnet: auch ein bereits vorgemerktes Profil verlangt bei erneutem Apply die ausdrückliche Entscheidung. Activation bietet Cancel, Finish oder Vormerken; Hintergrunddrain verlangt zusätzlich Warten oder ausdrücklich akzeptierten Verlust. Kein Default gewährt Zerstörung. Vormerken speichert ausschließlich den Wunsch, ohne automatische spätere Reconnectaktion.

Für unmittelbaren Reconnect werden beide Trigger temporär unterdrückt, die Suppression im Mirror bestätigt, danach nur die erfasste ActivationID fertiggestellt/abgebrochen. Neue Activation/Drain-IDs erzwingen eine neue Entscheidung. Warten beobachtet tatsächlichen Inputschluss und terminale Ergebnisse; Timeout lässt Verbindung bestehen und stellt die vorherige Pauseintention wieder her. Reconnect verwendet den vorhandenen Sessionpfad, ohne lokale Activationautorität.

Migrierte Konflikte werden nur nach expliziter Bestätigung für bekannte reparierbare Felder aufgelöst; unbekannte Konflikte und retired provenance bleiben erhalten. Die öffentlichen Funktionen/Typen, Callbackreihenfolge, Persistenzport und Sideeffects stehen in [protocol-v2-settings-ui.md](../../../../../../../docs/protocol-v2-settings-ui.md). [UI-01…10 sind einzeln belegt](EVIDENCE/requirement-coverage.md); unabhängiger Requirementstatus bleibt CLIENT OPEN.

## Nachgewiesene Korrekturen und Abgrenzung

Im tatsächlichen Servercheckpoint reproduziert: ein deaktivierter Wake-Trigger mit retained Wake-IDs erzeugte zuvor ein verbotenes Hello und `invalid_server_protocol`. Der kleine AP070-Servicefix sendet bei Wake=false eine leere Wireauswahl, erhält jedoch die lokalen IDs für späteres Wiederaktivieren. Regression prüft beides samt tatsächlich validem Hello; keine vorsorgliche Coreüberarbeitung.

Die Suppression muss vor einem Controlscommand im Mirror bestätigt sein; ein ursprünglicher Checkpointrun zeigte die fehlende aktuelle Sicht. Der Applypfad liest jetzt den tatsächlichen Snapshot vor dem erfassten Finish/Cancel. Der lange gemeinsame Windows-Testprozess reproduzierte eine native Access Violation bei erneutem QApplication-Pumpen nach den älteren GUI-/headless-Suiten. Die neue UI allein und die kombinierte Qt-/Controls-/UI-Suite mit 270 Tests bestehen. Explizite Mainthread-GC/DeferredDelete-Bereinigung allein beseitigte den Vollsuite-Absturz nicht; die genaue frühere native Referenz bleibt nicht isoliert. Deshalb führt jeder neue Qt-Oberflächenfall sämtliche unveränderten Assertions in einem begrenzten frischen Projektvenv-Prozess mit eigener QApplication aus; kein Fall entfällt. Eigene DeferredDelete-Bereinigung bleibt ausdrücklich. Corefälle und reale Server-/Windowscheckpoint prüfen weiterhin dieselben Instanzen und echte Threadgrenzen. Fehlgeschlagene vollständige Diagnosebelege sind getrennt erhalten; sie werden nicht als PASS gewertet.

Der reale Checkpointrunner hatte zudem eine reproduzierte Reihenfolgerace: Future-complete ging der queued gerenderten Projektion voraus; der folgende Entwurf konnte durch den noch eintreffenden Load zurückgesetzt werden. Der Runner wartet nun ausdrücklich auf genau die ausgelieferte Reply-ID statt nur auf Future-busy=false. Die fachlichen Assertions und tatsächlichen UI-/Corepfade bleiben erhalten.

Modulaufteilung in UIservice/Bridge/Dialog statt vorgeschlagener Erweiterung des V1-Corebridge ist eine interne Umsetzung, kein Wechsel der Anforderungsownership. Reguläre Appkomposition und koordinierte atomare Qt-/Win32-Hotkeyregistrierung bleiben AP100. Die Persistenzcallback-Schnittstelle muss dort mit dem vorhandenen Hotkey-Rebind-/Rollbackpfad verbunden werden; ein unkoordinierter direkter Qtzugriff aus dem Corethread ist unzulässig. AP080 liefert editier-/validierbare Controls und einen tatsächlich verwendeten AppConfig-Persistenzport im Checkpoint. Die reguläre App wird nicht heimlich umgestellt.

Checkpoint: gepinnte Produktions-FastAPI-Routen auf isoliertem localhost-TCP, tatsächlicher SettingsHTTP/-Service, V2Session/Mirror/Controls, reales PCM-Ingest und reale protokollgebundene Activation-/Drainentscheidungen. Modellfreie kontrollierte Recorder-/Scheduler-/Artifactprobe erlaubt reproduzierbare Terminalbedingungen ohne ASRmodell; kein Kontakt zum produktiven STTserver und keine Serverproduktänderung. Native Windowsvault-Lifecycle erfolgt gegen einen isolierten originbezogenen Testtarget mit Cleanup; sichtbare HWND/Mausinteraktionen plus Screenshot sind wirklich ausgeführt. Physischer Mikrofon-/Wake-/ASRnachweis und optimale Kalibrierung bleiben AP-IV2-020; Server-Distributed offen.

## Validierung

Windows11, Python3.12 aus Projektvenv; Qt im Mainthread, asyncio separater Thread. [Manifest](EVIDENCE/windows-validation.json) enthält tatsächliche Befehle, Runtime/Dependencies, Exitcodes, Dauer, vollständige Loghashes, Sourcehashes, qualifizierte Gitblobs sowie den genauen binären staged Produktdiff am kanonischen Parent. Finaler Head wird außerhalb des erzeugenden Commits in der PR-Handoffbeschreibung identifiziert. Nach Qualifikation keine Produkt-/Teständerungen; [Abgabeverifier](EVIDENCE/verify_handoff.py) prüft Blob-/Log-/Requirement-/Aktenbindung erneut.

| Prüfung | Ergebnis |
| --- | --- |
| Baseline vor erster Codeänderung | 90 PASS |
| Neue UI-/Credential-/Apply-/Guardfälle | 53 Tests, enthalten in gezielter und vollständiger Suite |
| Gezielte Regression mit `-W error` | 296 PASS |
| Bestehender realer Settingscheckpoint | 38 Checks PASS |
| Gepinnte Settings-/Wake-Supplementtests | 55 PASS, 0 Skips |
| Neuer realer Offscreen-UIcheckpoint | 27 Checks PASS |
| Native sichtbare Windows-UI/Vault | 29 Checks PASS, Screenshot vorhanden |
| Vollständige Windows-Clientsuite | 1513 PASS |
| compileall, diff/cached --check | PASS |
| Relative Links, Aktenstatus, Methoden/Fälle, Kandidatenblobs | PASS, gesonderte Abgabeevidenz |

## Abgabe und Stop

Vollständige Logs und Grenzen im [Evidenzindex](EVIDENCE/INDEX.md). Review auf dem endgültigen veröffentlichten PR-Head gegen genau diese qualifizierten Produktblobs. Reviewer darf commitgebunden Code und Windowsbelege prüfen; erneute Windowsvollsuite ist keine Pflicht. Pflichtbefunde als CHANGES_REQUIRED zurückgeben. Unabhängiger PASS und menschliche Übernahme sind offen; kein Merge, keine Folgepaketimplementierung. Workflowstatus/Manifest/Paketindex/Traceability und operative Einstiege sind auf REVIEW_READY gepflegt.
