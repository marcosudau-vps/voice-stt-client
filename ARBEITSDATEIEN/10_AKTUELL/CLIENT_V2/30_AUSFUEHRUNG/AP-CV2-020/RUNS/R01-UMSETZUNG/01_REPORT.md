# AP-CV2-020 / R01 – Umsetzung

Status **IN_PROGRESS**. Start 2026-10-11, Fortsetzung/Qualifikation 2026-10-12 (Europe/Berlin).
[Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md).

Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Branch `work/client-v2/ap-cv2-020`, Server ada13b0.
Keine fremde WIP, kein offener Paket-PR. AP010-R02-PASS und tatsächliche
menschliche Freigabe/Einzel-Squash vor Start geprüft; [Nachmergebeleg](EVIDENCE/predecessor-canonicalization.json).
Workflowweite Kandidaten-Gitrechte aus dem AP000-Originalauftrag, keine
kanonische Übernahme, Tags/Releases/Serveränderung oder Cleanup beauftragt.

## Ausgangssuite und Umsetzungsskizze

Vor erster Produktänderung vollständige Windowsbaseline:1263 Tests OK,96.614s,
Exit0; [vollständiger Log](EVIDENCE/baseline-full-unittest.txt), [Exit](EVIDENCE/baseline-exit.txt).
Skizze: Hello mit temporär gesperrten Triggern; injizierter Bootstrap und
Freigabe nach Acks; sessiongebundener Pendingtracker mit bytegleichem Retry;
Watermarks schützen Event-vor-Ack; bounded Cancellation/Close/Backoff.

## Ergebnis und Schnittstellen

V2STTSession/V2TransportConfig/SessionBinding/TransportStatus; CommandTracker,
CommandCompletion/AckAdvice und lokale CommandFailure-Untertypen.
[Vollständiger API-/Callback-/Guardvertrag](../../../../../../../docs/protocol-v2-transport.md).
Alle Methoden auf dem asyncio-Coreloop, kein Qt-/Threadzugriff. Callbacks in
Empfangsreihenfolge; alte Bindings/Fremdsessions verworfen, keine Domainphase
aus altem Ack. Snapshotreplay bleibt sichtbar. Ereignislose Acks tragen
Originalpayload und projectable-Flag an den späteren Mirror.

Separate V2-Klasse statt halber Umstellung des bestehenden STTSession/Core;
CV2-030/040/050/070 verwenden deren Schnittstellen, CV2-100 komponiert die App.
Neue Default-URL /ws/v2, typed Legacy-URL-Sperre ohne Profilschreiben/Hostwechsel.
Keine History-/Credentialmigration, neue Audioqueue oder Ergebnisinjektion.
Bestehendes Logging über ClientEventEmitter, kompakt ohne Token/Text/PCM.

## Iterative Prüfungen

27 gezielte Transporttests PASS mit -W error. Alle15 Resultcodes, Serialisierung,
Replay/alte Acks, Fremdsession/Generation, Bootstrap/PCMguards, Kapazität,
4408/Close-/Backoffregeln, stille Annahme, abgebrochene/blockierte Sends,
Shutdown-Cancellation, Close-Abort und Loggingausfall. Fake-Ackwait injiziert
deterministisch einen Timeout ohne echte Wartezeit. Der Snapshot-Replaytest
verwendet100ms statt10ms, damit Windows-Timer/Debugloop die gültige Antwort
nicht überholen; Produktdefaults bleiben5s.

Erste Testharnessfehler: BACKOFF war im Startwait nicht zugelassen; Fakeacks
lagen unter dem Fixture-Snapshot und wurden korrekt nicht projectable. Fake
Initialversion auf0 wie beim echten Server gesetzt. Serverharness verwendete
zunächst den falschen Countvergleich für die reale Sessions-Liste; berichtigt.
Windows-Archiveexport hatte CRLF; alle239 Pythondateien aus Gitblobbytes neu
bereitgestellt und geladene Quellen vor/nach Check byteverifiziert. Keine
Serverproduktänderung. Testlogs der Iterationen bleiben in der Akte.

Echter Loopback-WebSocketcheckpoint21 Fälle mit unveränderter gepinnter
FastAPI-App, GateAwareRecorder/AutoScheduler als Hardware-/Modellgrenze.
Hello/Admission, konfigurierte Sperre, Availability-/Suppressionacks,
Snapshotkorrelation, Activate/Finish, Capacity-/Settingsablehnung und Cleanup.
Noch offene Clientsettings-/Audiointegration ist ausdrücklich Testadapter.
Vollständige kandidativen Windowslogs und finale Identität folgen vor Abgabe.

## Offene Grenzen

Kein Eigenreview/ROOT_PASS. Vollständige Runtimekomposition, ASR, Mikrofon,
Hardware/Qt/Clipboard und finale Prozesspaarqualifikation bleiben ihren
Folgepaketen zugeordnet. Server-Distributed bleibt unverändert und offen.
