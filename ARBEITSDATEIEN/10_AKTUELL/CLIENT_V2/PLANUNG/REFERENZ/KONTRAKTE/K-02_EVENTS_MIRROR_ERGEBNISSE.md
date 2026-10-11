# K-02 – Events, ActivationMirror, Snapshot und Ergebnisverarbeitung

Geltung: exakte Serverfelder und Serverlimits sind verbindlich; interne Clientrepräsentationen sind Vorschläge, lokale technische Werte begründbar anpassbare Startwerte gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Produktverhalten und Schutzwirkungen bleiben Pflicht.

## 1. Getrennte Modelle

`TransportState` beschreibt Verbindung und lokale Konfiguration (`disconnected`, `connecting`, `handshaking`, `configuring`, `ready`, `resyncing`, `blocked`, `reconnecting`). Dies sind Clientzustände. Der serverautoritative Vordergrund besitzt exakt `idle`, `waiting_first_speech`, `segment_active`, `followup_wait`, `closing_input`. Eine Map von Activations und eine Map von Segmenten bilden parallel den Hintergrund ab. `finalizing` ist keine Vordergrundphase und blockiert keinen neuen Trigger.

Alle Reducereingänge sind an lokale Socketgeneration und `sessionId` gebunden. Mutation erfolgt ausschließlich im asyncio-Core; Qt erhält unveränderliche Präsentationssnapshots und führt keine Lifecycletransitions aus.

## 2. Gemeinsame Eventhülle

Pflicht: `type`, `protocolVersion=2`, `sessionId`, kanonische `eventId`, `eventSeq` int ≥ 1, `stateVersion` int ≥ 0, `occurredAtUnixMs` Unixzeit-ms. Reihenfolge ausschließlich über `eventSeq`; Wallclock ist Anzeige/Diagnose. Nicht jedes Event erhöht `stateVersion`, und eventlose Zustandsänderungen können diese erhöhen. Eine höhere `stateVersion` ohne Eventlücke verlangt keinen Resync.

Bei gültiger Hülle werden unbekannte additive Eventtypen in der Sequenz weitergezählt und diagnostiziert, ihre Fachpayloads ändern keinen bekannten Zustand. Unbekannte Nachrichtentypen ohne Eventhülle werden ignoriert. Eine ungültige Hülle eines erwarteten Events ist ein Protokollfehler: sichtbar degradieren und Snapshotklärung, niemals unter einer geratenen Identität verarbeiten.

## 3. Vollständiger Eventkatalog

`A` = `activationId`. `S` = zusätzlich `segmentId`, `segmentSequence`, alle drei unveränderlich pro Segment. Feldnamen in dieser Tabelle sind Wirefelder.

| Event | Fachpayload | Spiegel-/Nebenwirkung |
| --- | --- | --- |
| `activation.started` | A, `activationSequence`, `primarySource`, `inputPhase=waiting_first_speech`, `effectiveSettings` | neue Activation und Vordergrund setzen; Startsettings für A einfrieren |
| `activation.phase_changed` | A kann null sein, `previousPhase`, `inputPhase`, `deadlineAtUnixMs`, `remainingMs` | passende Vordergrundphase/Deadline aktualisieren; gleicher Phasenname kann Refresh sein |
| `activation.input_closed` | A, `reason`, `causedByCommandId` UUID/null, `acceptedSegmentCount` | A als inputClosed markieren; Vordergrund nur zurücksetzen, falls dessen ID A ist |
| `activation.completed` | A, `acceptedSegmentCount`, `terminalSegmentCount` | A terminal; keine neue Textinjektion und kein blindes Vordergrund-Idle |
| `activation.cancelled` | wie completed plus `reason` | A terminal cancelled; vorher veröffentlichte Texte erhalten |
| `activation.failed` | wie completed plus `reason` | A terminal failed, Grund anzeigen |
| `activation.trigger_suppressed` | `source=manual`, `reason=trigger_suppressed` | Diagnose/ggf. einmaliges Bedienfeedback; keine zweite State-Machine |
| `segment.recording_started` | A+S | Segment anlegen, Herkunft festhalten |
| `segment.recording_ended` | A+S, `reason` | Stufe recorded, sofern kein Terminal bekannt |
| `transcription.accepted` | A+S | Stufe accepted; keine Textinjektion |
| `transcription.interim` | A+S, `text`, optionale Stabilisierung | nur Vorschau dieses Segments ersetzen |
| `transcription.completed` | A+S, `text` | erstes Terminal, Vorschau entfernen, Final-Pipeline einmal freigeben |
| `transcription.discarded` | A+S, `reason` | erstes Terminal discarded, Vorschau entfernen, keine Injektion |
| `transcription.failed` | A+S, `reason` | erstes Terminal failed, Vorschau entfernen, keine Injektion |
| `watchdog.warning` | A, `segmentId`/`segmentSequence` ggf. null, `deadlineAtUnixMs`, `remainingMs` | einmaliges Warnfeedback, Countdown; keine lokale Finalisierung |
| `wakeword.detected` | A, `wakeWordId`, `score` ggf. null, `primarySource=wake_word` | zusätzliche Quellendiagnose; Activation existiert bereits |
| `wakeword.availability_changed` | `catalogRevision`, `availableWakeWordIds` | Capabilities aktualisieren, vollständigen HTTP-Katalog bei neuer Revision laden |
| `settings.changed` | `settingsRevision`, `scope=session`, `changedKeys` sortiert, `applyPolicy` | Sessionrevision aktualisieren, gewünschte/wirksame Werte nachladen |

`transcription.interim`, `watchdog.warning`, `activation.trigger_suppressed` erhöhen `stateVersion` nicht. Eine Settings-Transaktion mit mehreren Policygruppen erhöht sie nur im ersten Event. Die übrigen publizierten Zustandsereignisse erhöhen sie.

Optionale Interimfelder: `recordingId`, `sequence`, `rawText`, `displayText`, `stableText`, `stableDelta`, `unstableText`, `committedStableText`, `committedStableDelta`, `visualStableText`, `visualUnstableText`, `consensusText`, `consensusUnstableText`, `consensusDisplayText`, `publicConsensusAligned`, `internalRevision`, `isOutlier`, `stablePrefixConflict`, `commitReason`, `stableNormalizedOffset`, `timing`. Keines ist Pflicht. Server-Skizzen können vereinfachte Typen enthalten; bekannte optionale Zusatzfelder defensiv behandeln, unbekannte akzeptieren. Die minimale korrekte Darstellung verwendet `text`; vorhandenes geeignetes `displayText` darf die Vorschau steuern. Stabilisierung ist kein Finalsignal.

## 4. Snapshotvertrag

```text
type=session.snapshot, protocolVersion, serverVersion, serverCommit,
sessionId, stateVersion, lastEventSeq, settingsRevision,
input, pendingActivations, trigger, audioAvailable,
requestedSettings, effectiveSettings, wakeWordCapabilities
```

In `hello.accepted.snapshot` entfällt nur `type`. Snapshot ist ein Read ohne `eventId`/`eventSeq`.

| Block | Vollständige Struktur |
| --- | --- |
| `input` | `phase`, `activationId`, `primarySource`, `deadlineAtUnixMs`, `remainingMs`, `closeRequested` |
| `pendingActivations[]` | `activationId`, `activationSequence`, `inputClosedReason`, `processingState=draining`, `acceptedSegmentCount`, `terminalSegmentCount`; aufsteigend nach activationSequence |
| `trigger` | `configured`, `suppressed`, `effective`; je `manual`/`wakeWord` Bool |
| `requestedSettings`, `effectiveSettings` | vollständige Maps aller 16 Sessionkeys, K-03 |
| `wakeWordCapabilities` | `catalogRevision`, `availableWakeWordIds` |

In `idle`: ID, Source, Deadline und Restzeit null, closeRequested false. closeRequested ist genau in closing_input true. Pendingliste enthält nur inputClosed, noch drainende Activations; terminale Records entfernt der Server aus seinem Ledger. Die offene Activation steht ausschließlich im `input`-Block. Der Snapshot enthält **keine Segmentliste und keine Texte**.

Snapshotannahme: aktuelle Generation und Session, `stateVersion >= mirror.stateVersion`, außerdem `lastEventSeq >=` bereits verarbeitetem Sequenzstand. Gleich hohe Stateversion mit höherer Sequenz ist gültig, etwa nach Interims. Ein älterer Snapshot erfüllt eine Resyncanforderung nicht. Nicht zurücksetzen und begrenzt neu anfordern.

Beim Ersetzen nur snapshotfähige Domänen ersetzen; empfangene Segmenttexte, Terminal-Dedup und Injektionshistorie erhalten. Verschwinden aus `pendingActivations` beweist, dass keine weitere Drainarbeit im Serversnapshot offen ist, aber liefert **keinen** Terminaltyp und keinen fehlenden Text. Status deshalb `terminal_unknown` / „Ergebnis unvollständig“, falls der konkrete Terminalnachweis fehlt.

## 5. Ordnungs- und Racevertrag

1. Events von Commandtransitions kommen vor dem Ack; Ack kann alt sein.
2. `activation.started` kommt vor `wakeword.detected` derselben Activation.
3. Activation-Terminal darf vor `activation.input_closed` kommen. Vordergrundfreigabe hängt an Close oder Snapshot, nicht am Terminal.
4. `activation.started(B)` darf vor `activation.input_closed(A)` kommen. Close A verändert input B nicht.
5. Beim Cancel darf `transcription.discarded(S)` vor `segment.recording_ended(S)` und `transcription.accepted(S)` kommen. Erstes Terminal gewinnt; spätere Zwischenstufen machen S nicht wieder nichtterminal.
6. Finale Nutztexte erscheinen pro Session in Segmentsequence-Reihenfolge. Fehler-/Discardterminals können Lücken bereits bekannt machen; sie blockieren spätere vollständige Finals nicht.
7. Ältere Finals gehören stets zu ihren mitgesendeten IDs. Kein Mapping über „aktuelle Activation“, UI-Diktierzustand oder jüngste Recording-ID.
8. Nach Terminal sendet der Server kein neues Interim für dasselbe Segment. Clientguard erhält das Terminal trotzdem gegen künstliche/replayte/stale Eingänge.

`activation.input_closed.reason`: `finished`, `cancelled`, `timed_out`, `segment_watchdog_timeout`; interne Session-/Recoverygründe als nicht leere Diagnosewerte tolerieren. `causedByCommandId` ist nur bei ausdrücklichem Finish/Cancel gesetzt; bei Geräteverlust null. Unbekannte zusätzliche Reasons sind darstellbar, ohne sie als Erfolg zu interpretieren.

## 6. Deduplizierung und Resync

Normalfall: Session prüfen; Events mit `eventSeq <= lastEventSeq` als bereits konsumierte ignorieren; nächste Sequenz anwenden. Eine ID erneut bei widersprüchlichem Inhalt oder ein wechselnder Activationbezug desselben Segments ist ein Protokollbefund, keine neue Veröffentlichung.

Lücke: Zustand `resyncing`, neue Activationcommands sperren, genau eine offene Snapshotanforderung, Events puffern. Beim aktuellen Snapshot:

1. snapshotfähigen Spiegel ersetzen, erhaltene Segmentdaten nicht löschen;
2. gepufferte Events nach `eventSeq` ordnen;
3. Events bis einschließlich `snapshot.lastEventSeq`: enthaltene Segment-/Textpayloads idempotent nachtragen, Lifecycle nicht nochmals rückwärts anwenden;
4. spätere Events ab dem Snapshotcursor normal reduzieren; erneute Lücke startet neuen begrenzten Resync;
5. fehlen konkrete Segment-/Terminaltexte, unvollständige Ausgabe markieren, nicht aus Zählern erzeugen;
6. Puffer freigeben und Operationsbereitschaft erst nach konsistentem Zustand herstellen.

Erhaltene Cancel-/Failed-Activationterminals im Puffer bleiben als lokale terminale Tombstones gespeichert, auch wenn der Snapshot die Activation nicht mehr enthält. Sie verhindern spätere widersprüchliche Nutztexte; sie setzen den Vordergrund nicht zurück. Ein wirklich vorher veröffentlichter Finaltext wird durch späteres Cancel nicht entfernt.

Technische Clientstartwerte: Resyncpuffer 512 Events oder 4 MiB, Snapshotdeadline 5 s, zwei Snapshotversuche je Resync. Konkrete Werte und begrenzte Wiederholungsstrategie dürfen mit belegtem Last-/Fehlertest angepasst werden. Überlauf oder wiederholter Timeout wird als unvollständige Ausgabe protokolliert und kontrolliert reconnectet. Dies sind Client-Sollwerte, keine Garantien des Servers. Transkriptionslatenz löst für sich keinen Reconnect aus.

## 7. Ergebnis- und Historienvertrag

Finalhandler übernimmt stabil zugeordnete Finaldaten mit `sessionId`, `activationId`, `segmentId`, `segmentSequence`, `text`, `eventId`, `eventSeq`. Eine immutable `FinalResult`-Klasse ist ein Vorschlag; vorhandene sichere Repräsentationen sind zulässig. Nebenwirkungen werden geordnet und konkurrenzsicher im bestehenden Core-/Queuepfad verarbeitet. Automatische Verarbeitung genau einmal je Segment; textuelle Gleichheit verschiedener Segmente ist kein Dedupkriterium.

Pipeline: Terminal-Dedup → Finaltextprüfung → Historieneintrag → Injectionversuch reservieren → bestehende Clipboard-/SendInput-Queue → Ergebnisstatus speichern → quellenneutrales Feedback. Leerer completed-Text ist erlaubt, wird als leeres Ergebnis ohne Injektion geführt; `discarded(reason=empty_final)` ist der normale Serverpfad. Historyfehler blockieren Audio/Mirror nicht; ein UI-Hinweis und der vorhandene Speicherausfallpfad bleiben erhalten. Die Prozess-Dedup darf nicht vom optionalen Historienmodus abhängen.

Dedupkey `(sessionId, segmentId)`; Reihenfolge `segmentSequence`; Activationbezug als eigenes Feld. Beim Schemawechsel V1-Historie mit Integersegmenten lesen, V2 mit UUID-Strings speichern. V1 und V2 explizit über gespeicherte Protokollherkunft unterscheiden (`protocol_version` als vorgeschlagener Feldname); V1-IDs nicht nachträglich in erfundene Server-UUIDs umwandeln. Migration transaktional, Backup vorher, Einträge und Injectionversuche erhalten, zweiter Start idempotent.

At-most-once im laufenden Prozess und bei persistiertem Abschluss lässt sich prüfen. Transaktionale Exactly-once-Zustellung an ein fremdes Windowsfenster ist nicht möglich. Ein nach Crash unklarer Versuch wird angezeigt, ohne automatische Nachinjektion. Textziel bleibt die beim tatsächlichen Queueeinsatz fokussierte Anwendung gemäß vorhandenem Clipboardvertrag; eine neue Zielpinningfunktion wird nicht eingeführt.

## 8. Quellen

Server `protocol_v2/{events,snapshot,session,connection}.py`, `segment_ledger.py`, `server.py`, `VoiceSTT/core/realtime_callbacks.py`; Tests für Contract, Races, stateVersion, Terminalrecovery und Realtimeherkunft. Clientbaseline `stt_session.py`, `controller.py`, `history.py`, `text_injector.py`, `reinsertion.py`. Alle Pfade gelten relativ zum im [Quellenmanifest](../../EVIDENCE/source-manifest.json) festgelegten Repository.
