# AP-CV2-020 / R03 – Korrektur

Status **REVIEW_READY**, Workflow REVIEW_READY, 2026-10-12.
[Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md),
[R02-Findings](../R02-ABNAHME/01_REPORT.md), [PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4).

Übernommene Reviewspitze `71f757bcc2b699f2056d7cef3f8f7d9aa9ee2d37` per fetch/fast-forward;
Reviewnachtrag ausschließlich administrativ, vorher sauberer Workingtree.
Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Server ada13b0 unverändert.
Beauftragte Findings CV2-020-R02-F01/F02 sind dynamisch reproduziert und berechtigt.
Kein Finding zurückgewiesen; eine Gegenbegründung ist daher nicht erforderlich.

Skizze: HTTP-Upgrade-Ausnahmen explizit klassifizieren: temporär mit begrenztem
Backoff, Auth-/Konfigfehler sichtbar BLOCKED. 4408-Episodenzähler erst nach
vollständig erfolgreichem Bootstrap/READY zurücksetzen. Repros vor Produktfix,
gezielte Regression, neue kandidatengebundene vollständige Windowssuite samt
Servercheckpoint; danach erneutes unabhängiges Review. Keine Folgefeatures.

## Finding CV2-020-R02-F01

Vorher-Repro: echte Bibliotheksexceptions InvalidStatus (HTTP 408/5xx/429 und
Konfig-/Authcodes) entkommen dem Run; temporäre Fälle enden CLOSED statt
BACKOFF, dauerhafte Fälle liefern keinen BLOCKED-Abschluss. InvalidHandshake
und InvalidURI sind ebenfalls explizit geprüft. [Vollständiger Vorherlog](EVIDENCE/findings-before-fix.txt).

Fix: InvalidStatus vor InvalidHandshake fangen. 408 und 500–599 verwenden
normalen exponentiell begrenzten Backoff, 429 den Kapazitätsbackoff mindestens
10 s; andere HTTP-Statuscodes blockieren. Ungültiger Handshake/URI blockiert
mit fester Fehlerklasse. Keine Response-/Exceptiontexte in Diagnose oder
Status, keine automatische Auth-/Hoständerung. Bestehender Cleanup bleibt
unverändert; Upgradefehler besitzen noch keine Domainsession.

Neue Methoden in tests.test_v2_transport.Transport:
`test_http_upgrade_transient_errors_backoff_then_ready` (408/500/502/503/504,
erster BACKOFF vor zweitem Connect, READY, erfolgreicher Command, Cleanup),
`test_http_upgrade_rate_limit_has_capacity_backoff_and_bounded_stop` (429,
kein Hotloop, Stop während Backoff),
`test_http_upgrade_auth_configuration_and_invalid_handshake_block_once`
(301/400/401/403/404/405/426 sowie InvalidHandshake/InvalidURI; genau ein
Connect, BLOCKED, keine Pending-/Runner-/Receiverreste, keine Fehlermeldungssecrets).

## Finding CV2-020-R02-F02

Vorher-Repro: 4408→CONFIGURING→READY→1011→4408 endet BLOCKED statt erneutem
READY. Fix: `_silent_failures=0` unmittelbar vor READY nach erfolgreicher
Konfiguration einschließlich bestätigter Suppression. Admission allein setzt
den Zähler nicht zurück.

Neue Methode `Transport.test_4408_retry_budget_resets_only_after_ready_between_episodes`
prüft 4408→CONFIGURING (Budget noch verbraucht)→READY→1011→4408→READY,
TransportLost für den alten Pendingcommand, neue Session/generation,
stabile Prozess-ID, kein alter Callback und Cleanup aller vier Sockets.
Bestehende Methode `Transport.test_4408_only_one_retry_with_stable_process_run_id`
prüft weiterhin 4408→4408 ohne Erfolg als BLOCKED.

## Bisherige Prüfergebnisse

Vor Produktänderung 57 Codec-/Transporttests PASS; danach fünf Findingfälle
auf unverändertem Produktcode: EXPECTED_FAIL (7 Failures, 9 Errors), während
der vorhandene konsekutive 4408-Test weiterhin besteht. Nach gezieltem Fix
61 Codec-/Transporttests mit -W error PASS. Die folgende vollständige Commit-/Tree-gebundene Qualifikation ersetzt den bisherigen R01-Produktnachweis für den korrigierten Kandidaten; unabhängige Abnahme weiterhin offen.


## Neue kandidatengebundene Qualifikation

Getesteter Commit `98ab3c0fc5c935019d81d6d6acb1423185cb4793`, Tree `c394dbe3d75086132234cb987469ee6639647af6`. Workingtree vor Start sauber;
Windows 11 Build26300 / Python3.12.10 / Projektvenv, QT_QPA_PLATFORM=offscreen.
Alle Befehle, Start-/Endzeit, Laufzeiten, Runtime und SHA256 im
[Qualifikationsmanifest](EVIDENCE/windows-validation.json).

| Prüfung | Ergebnis | Vollständiger Beleg |
| --- | --- | --- |
| Relevante Vorher-Baseline am Reviewnachtrag71f757b |57 PASS, Exit0 | [Log](EVIDENCE/baseline-targeted.txt), [Metadaten](EVIDENCE/baseline-validation.json) |
| Dynamische Finding-Repros vor Produktfix | EXPECTED_FAIL, 7 Failures/9 Errors | [Log](EVIDENCE/findings-before-fix.txt), [vollständige originale Ausgabe/Befehl/Hash](EVIDENCE/findings-before-fix.json) |
| Codec-/Transport, -W error |61 PASS, Exit0 | [Log](EVIDENCE/targeted-transport-codec-unittest.txt) |
| Echte gepinnte FastAPI-App via TCP/WebSocket |21 PASS,46 bytegeprüfte Quellen, Exit0 | [Checkpoint](EVIDENCE/server-transport-checkpoint.json) |
| compileall voice_stt_client/scripts/tests |PASS, Exit0 | [Leerer Log](EVIDENCE/compileall.txt), [Exit](EVIDENCE/windows-validation.json) |
| Gesamte Windows-Clientsuite |1294 PASS, Exit0 | [Log](EVIDENCE/windows-full-unittest.txt) |

Keine Pflichtskips/Testabschwächungen. Der frühe Servercheck verwendet dieselben
offengelegten Hardware-/Modell-/Settingsbootstrapgrenzen wie R01; Serverquellen
und Serverbaseline unverändert. Neuer Kandidat requalifiziert, kein Serverfix.
Nur das lesbare historische Repro-TXT entfernt zwei nachgestellte Leerzeichen
(Zeilen1/8); die vollständige unveränderte originale Ausgabe steht zusätzlich
im JSON mit eigenem SHA256. Finale Pflichtlogs sind vollständig, ausschließlich
CRLF→LF normalisiert. [Zusätzlicher Fortsetzungsauftrag](ZUSATZPROMPTS/001_FORTSETZEN.md).

## Findingentscheidung und erneute Übergabe

| Finding | Eigene Entscheidung | Unabhängige Entscheidung |
| --- | --- | --- |
| CV2-020-R02-F01 | berechtigt, dynamisch reproduziert, gezielt korrigiert, neue Regression PASS | offener Recheck |
| CV2-020-R02-F02 | berechtigt, dynamisch reproduziert, gezielt korrigiert, neue Regression PASS | offener Recheck |

Keine unberechtigten Findings; kein Widerspruch und keine Umdeutung des R02-Urteils.
Die IDs bleiben bis zum unabhängigen Recheck offen. 28 individuelle Requirements
behalten CLIENT OPEN; ursprüngliche R01-Implementierungsbelege bleiben erhalten,
neue correctionEvidence nennt diesen qualifizierten Commit/Tree, tatsächliche
Methoden und R03. Matrix um betroffene neue HTTP-/4408-Methoden ergänzt.

Nach Qualifikation ausschließlich Akten-/Status-/Traceability-/Evidenznachträge.
Produkt-/Test-/testrelevanter Konfigstand muss beim eingereichten SHA identisch
sein; [administrative Abgabeprüfung](EVIDENCE/administrative-validation.json)
und finaler PR-Übergabekommentar weisen dies zusammen mit Remote-Identitäten nach.
Workingtree bei Übergabe sauber. PR #4 bleibt kumulativ; kanonischer Parent
91065f5f7715aa6653ec5335d9e757b6ef97a067 und Server
ada13b011e1d3829f78e7f389e3b927795a2b3be unverändert.

Kein Eigenreview/ROOT_PASS, Merge oder AP030. Frische unabhängige Session prüft
den vollständigen Parent-zu-Head-Kandidaten, beide R02-Findings und neuen Belege.
Appkomposition weiterhin CV2-100; ASR/Mikrofon/Qt/Clipboard und abschließende
Prozesspaar-/Hardwareabnahme bleiben zugeordneten Folgepaketen. Server-Distributed
offen. Schreibhoheit bei finaler SHA-/Treeübergabe zurückgegeben.
