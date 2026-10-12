# AP-CV2-030 / R01 – Umsetzung und Selbstqualifikation

Status **REVIEW_READY**, workflowPhase REVIEW_READY. Datum 2026-10-12, Europe/Berlin.
[Originalauftrag](00_PROMPT_ORIGINAL.md) · [Evidenzindex](EVIDENCE/INDEX.md) · [Paketakte](../../00_PAKET.md) · [tatsächliche 35 Requirementmethoden](EVIDENCE/requirement-coverage.md).

## Auftrag und Identität

Genau AP-CV2-030 umgesetzt. Kanonischer Parent `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0`, Paketbranch `work/client-v2/ap-cv2-030`, Base `feat/client-v2`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Arbeitsablage/Planrevision10 und Rollenregelversion7. Kandidaten-Gitrechte aus gesichertem workflowweitem AP000-Originalauftrag; aktueller menschlicher Prompt beauftragt AP030. Unabhängige Abnahme ist offen; diese Session erteilt keinen ROOT_PASS und startet kein Folgepaket.

Vorgänger AP020: tatsächlicher R04 ROOT_PASS, beide früheren Findings geschlossen, menschlicher Originalwortlaut und gemergter PR #4, genau ein Aggregate mit exaktem Parent und Baumgleichheit. [Gesicherte Git-/PR-Provenienz](EVIDENCE/predecessor-canonicalization.json). Veraltete aktuelle Steuerung und Namespaceangaben im beauftragten Planbereich nachgeführt; historische Reports/Originalprompts unverändert.

Die Qualifikation bindet Basis plus exakten [Produkt-/Testdiff](EVIDENCE/tested-product.patch), dessen SHA256,185 lokale Quelldateihashes und normalisierte Gitblobidentitäten. [Runtime und vollständige Befehle](EVIDENCE/windows-validation.json). Der eingereichte Head wird nach allen Akten aus Git ermittelt; er muss diesen Produkt-/Test-/Abhängigkeitsstand enthalten. Nachträge betreffen administrative Unterlagen und Belege.

## Ergebnis und technische Entscheidungen

Reiner `ActivationMirror` verarbeitet alle18 Events und bekannte additive Felder mit strikt getrennten Domainwirkungen. Immutable Input-/Activation-/Segment-/Settingsprojektionen, sessionweite Segmentidentitäten und erste Terminals; Finaldaten nur passend zur jeweiligen ID. Ein Foreground und mehrere drainende Hintergrundactivations, keine finalizing-Vordergrundphase. Terminal-vor-Close, Bstart-vor-Aclose und alte Finals beeinflussen ausschließlich passende IDs.

Snapshotannahme prüft Stateversion, Sequenzcursor und Sessionrevision. Nur snapshotfähige Domänen werden ersetzt. Empfangene und gepufferte Segmenttexte sowie Cancel-/Failedtombstones bleiben erhalten; gepufferte Lifecycleereignisse bis zum Snapshotcursor setzen keinen neuen Vordergrund zurück. Zähler erzeugen keine Texte; fehlende Terminalbelege und verschwundene Pendingactivations sind terminal_unknown/incomplete.

Separate `V2MirrorConnection` verwendet den tatsächlichen V2STTSession/CommandTracker. Resync sperrt Activationcommands bei Annahme und unmittelbar vor dem Senden, einschließlich schon wartender Commands. Genau ein Snapshotprozess,512 Events/4MiB UTF-8-JSON,2 Versuche mit je5s Monotonicdeadline; Overflow/Timeout markiert Verlust und schließt die aktuelle Bindung kontrolliert. Ack ersetzt keinen Snapshot und projiziert niemals eine Phase. Unbekannte valide Events zählen sequenziell; Stateversionssprung allein verlangt keinen Resync. Countdown aus Receiptanker/remainingMs, ohne lokalen Timeoutcommand oder Finalinferenztimer.

Öffentliche Funktionen, Datentypen, Callbackreihenfolge, Effekte, Guards und Retentiongrenzen vollständig in [API-Dokumentation](../../../../../../../docs/protocol-v2-mirror.md). Adapter auf owning Coreloop vor Transportstart installieren; Reduction publiziert nach Zustandsänderung, frühere Callbacks anschließend. Resultservice muss nur `finals` als Ergebnisfreigabe verwenden und veröffentlichte Daten außerhalb des neuen Sessionledgers behalten. Kein neuer Qt-/Clipboard-/Historypfad, keine Daten-/Konfigurationsmigration. Appkomposition CV2-100, Audio/Settingsports CV2-040/070.

## Tests und Selbstchecks

| Prüfung | Resultat / Beleg |
| --- | --- |
| Vorher-Baseline |61 Codec-/Transporttests PASS vor erster Produktänderung; [vollständiger Log](EVIDENCE/baseline-targeted.txt) |
| Gezielte Endregression, warnings as errors |106 Tests PASS, darunter45 Mirror-/Anbindungstests; [vollständiger Log](EVIDENCE/targeted-unittest.txt) |
| Generierte Ordnungsraces |60 gültige Backgroundinterleavings und24 Cancel-/Terminalpermutationen, Invarianten nach jedem Schritt; tatsächliche Methoden in Coverage/Log |
| Windows-Gesamtsuite |1339 Tests PASS, Exit0, keine Pflichtskips; [vollständiger Log](EVIDENCE/windows-full-unittest.txt) |
| Echter gepinnter Servercheckpoint |35 Fälle PASS,46 bytegeprüfte Original-Pythonquellen; [Identität/Checks/Trace](EVIDENCE/server-mirror-checkpoint.json) |
| compileall |PASS, Exit0; [Log](EVIDENCE/compileall.txt) |
| Diff-/Akten-/Link-/Quellenkonsistenz |PASS vor Abgabe; [Strukturprüfung](EVIDENCE/records-validation.json), [administrative Kontrolle](EVIDENCE/handoff-validation.json) |

Windows11 Build26300, AMD64, Python3.12.10 in Projektvenv; Qt offscreen. Exakte Zeiten, Dependencyversionen und vollständige Commands im Windowsmanifest. Gesamte bestehende Suite erhalten; keine V1-Assertions entfernt oder abgeschwächt.

Iterative Selbstkorrekturen im selben Run: initiale Verbindungstestfixtures auf tatsächlichen Snapshotcursor angepasst; ein zu früh ausgewählter Bootstrap-Snapshot im Harness durch den letzten bestätigten Snapshot ersetzt. Segmentidentitätskonflikte vor jeder Activationallocation geprüft, damit abgelehnte Zuordnungen keine Teilmutation hinterlassen. Bekannte additive Felder auf ihre Eventdomain begrenzt. Passende Negativassertions ergänzt und danach komplette Qualifikation erneut ausgeführt. Frühere1338-PASS-Läufe sind keine Abnahme des letzten korrigierten106/1339-Stands.

Servercheckpoint führt tatsächliche Clientkomponenten über TCP/WebSocket in die unveränderte Produktions-FastAPI-App, Admission, Activationcontroller und Ledger. Recording/Interim/Final-IDs, Startdeadline, realer Seqgap, echte Snapshotantwort, Payloadsalvage hinter Cursor und tatsächlich verlorener Finaltext geprüft. GateAwareRecorder/AutoScheduler ersetzen ausschließlich Hardware/Modelle; rohe synthetische PCM-Pakete und Audioavailability sind die benannte noch offene Clientaudio-/Settingsbootstrapgrenze. Deterministische Transporttests ergänzen Ack-/Terminalreordering und1011-Recovery. Keine produktive Instanz oder Nutzeraudiodaten; getrennte finale Prozess-/ASR-/Hardwarequalifikation bleibt späteren Paketen zugeordnet.

## Traceability, Grenzen und Übergabe

Alle FG-01..18 und SYNC-01..17 besitzen einzelne tatsächliche Methoden/Runbelege in [Coverage](EVIDENCE/requirement-coverage.md), Matrix und Requirements-JSON. Requirementtexte, Ownership, Verträge und originale sourceRefs unverändert. Requirements bleiben CLIENT OPEN bis unabhängiger Abnahme; SELF_CHECK_PASS/REVIEW_READY steht ausschließlich im Umsetzungsnachweis.

Die Abgabecheckliste ist vollständig selbst geprüft: fachliche Kriterien, Kandidatenbindung, vollständige Logs, alle18 Events/null/Versionsfälle, Tombstones, Bounds, realer Serverkontakt, APIs/Startgrenzen, Plan-/Status-/Aktenpflege und erlaubter Git-Scope. Pflicht-Hardware-/Credential-/Clipboardfälle dieses AP: keine; NOT_RUN in späteren Paketen, keine Gesamtabnahmebehauptung. Sessionledger/Fingerprints wachsen mit beobachteten Segmenten/Events und werden nicht automatisch verworfen; nur der Resyncpuffer besitzt die genannten Bounds.

Nächste Aktion: frische unabhängige Session prüft den vollständigen kumulativen PR und die gebundene Evidenz. Schreiben/Pushen auf diesem Paketbranch nach finaler Übergabe pausiert, writeOwner=null. Keine eigene technische Abnahme, kanonische Übernahme oder AP040-Implementierung.

Bereitstellung: [PR #5](https://github.com/marcosudau-vps/voice-stt-client/pull/5), OPEN/REVIEW_READY, Base `feat/client-v2`. Produkt-/Teststand in Commit `93acd2e6a589e04b266019f69e2bcad2998b8904`, Tree `822b72bfabf0f1e59769d98523b6c6ab784136f0` entspricht exakt der Qualifikation. [Gitblob-/Logabgleich](EVIDENCE/implementation-publication.json). Ein abschließender administrativer Commit ergänzt diese PR-Verweise; dessen tatsächliche finale SHA/Tree stehen in PR-Abgabe und Übergabe.
