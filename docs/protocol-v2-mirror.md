# AP-CV2-030 – Mirror und Resync

Stand 2026-10-12. Der headless V2-Pfad verbindet `ActivationMirror` über
`V2MirrorConnection` mit `V2STTSession`. Die bestehende Anwendung wird in
CV2-100 komponiert. Start bleibt `.\venv\Scripts\python.exe -m voice_stt_client`.
Keine Config-/Datenmigration, neuen Credentials, Qt-, Clipboard-, History- oder
Hardwarewirkungen in diesem Paket. Das Serverpaar bleibt auf ada13b0 gepinnt.

```python
session = V2STTSession(config, bootstrap=actual_bootstrap)
connection = V2MirrorConnection(session)
connection.on_reduction = consume_reduction
await session.run()
# Shutdown: await connection.close()
```

Der Bootstrap ist weiterhin der explizite Audio-/Settingsport aus CV2-020.
CV2-040/070 liefern diese Services. Die Konstruktion des Mirrors ersetzt ihn
nicht. Adapter vor Transportstart installieren; genau ein Adapter je Transport.
Die synchronen Callbackports danach über `connection.on_reduction` bedienen;
ein erneutes Überschreiben von Transportcallbacks würde die Verdrahtung lösen.
Bereits vor Installation vorhandene Callbacks werden nach Reduktion aufgerufen.

## Reine API und sichere Veröffentlichung

`begin(generation, decoded_snapshot, monotonic_receipt)` setzt eine neue
admittierte Session auf. Nur strikt neuere lokale Generationen werden gebunden.
`consume(generation, decoded_event_or_snapshot, monotonic_receipt)` verwirft
fremde Sessions und alte Generationen. `disconnect(generation)` beendet die
lokale Projektion, erhält bereits bekannte Texte im unterbrochenen View und
markiert offene Ausgaben als `terminal_unknown`. Ein neuer Begin startet einen
neuen Ledger; der Ergebnisservice muss veröffentlichte Finals außerhalb dieses
Sessionledgers behalten. Kein Resume oder automatische Nachinjektion.

`view` ist ein immutable `MirrorView` mit eigenen unveränderlichen Maps von
`ActivationView`/`SegmentView`, getrennten requested/effective Maps, Revisionen,
Triggern, Audioavailability und Wakecapabilities. Frühere Views ändern sich
nicht durch spätere Reduktion. Mutation ausschließlich im owning asyncio-Core;
Qt erhält später diese Daten und führt keine Lifecycletransitions aus.

Jeder Aufruf gibt `Reduction(view, finals, events, effects)` zurück. Der View
steht bereits auf dem reduzierten Zustand, bevor der Adapter seine synchrone
`on_reduction`-Callbackfunktion aufruft. Sie darf nicht blockieren oder vom
Empfängertask aus einen Command awaiten. `finals` ist die einzige Freigabe für
den späteren Resultservice: immutable `FinalResult` mit session_id,
activation_id, segment_id, segment_sequence, text, event_id und event_seq.
Erstes Segmentterminal gewinnt; gleiche Texte verschiedener Segmente bleiben
verschiedene Ergebnisse. Leere completed-Texte sind gültige Terminaldaten.
History-/Injectionvalidierung folgt CV2-060.

`events` beschreibt sequenziell konsumierte Domainereignisse zur Diagnose und
späteren Feedbackanbindung. Es ist kein alternativer Finalhandler; Verbraucher
müssen Terminal-/Feedbackwirkungen über Projektion und eigene Eventguards
ableiten. Snapshot-Salvage publiziert vorhandene Textdaten über `finals`, ohne
alte Lifecycleereignisse als aktuelle Impulse erneut auszugeben. Texte und
Settings sind im repr unterdrückt. Vollständige Wireobjekte nicht loggen.

## Vordergrund, Terminalität und Settings

Input enthält genau idle, waiting_first_speech, segment_active, followup_wait
und closing_input. Eine neue serverseitige Activation B ersetzt ausschließlich
den Vordergrund; dadurch ist A nachweislich geschlossen, auch wenn sein
input_closed-Event später folgt. Close/Phase/Final für A verändern Input B nicht.
Activationterminal allein gibt Input nicht frei. Ein idle mit mehreren alten
drainenden Activations gibt Manual frei, sobald Transport und Mirror bereit,
Audio verfügbar und der manuelle Trigger effektiv sind.

Segmentidentitäten und Sequenzen sind unveränderlich; Konflikte degradieren
und verlangen einen Snapshot. recording_ended/accepted/interim nach Terminal
öffnen kein Segment erneut. Cancel-/Failedtombstones sperren unveröffentlichte
Finals, erhalten aber zuvor veröffentlichte Texte. Segmentvorschau wird nur
für die jeweilige Segment-ID ersetzt; `displayText` muss ein String sein,
ansonsten gilt Pflichtfeld `text`. Stabilisierung signalisiert kein Final.

Activationstart friert seine effectiveSettings ein. Spätere requested/effective
Sessionmaps ersetzen diese Startwerte nicht. settings.changed aktualisiert die
Revision und verlangt Snapshot/Settingsklärung; eine neue Katalogrevision
erzeugt `catalog_required`. HTTP-Schema-/Katalognachladen und Applyentscheidungen
sind CV2-070. Unbekannte valide Domainereignisse erhöhen den Eventcursor und
diagnostizieren `unknown_event`, ohne bekannte Payloadwirkung. stateVersion
darf gleich bleiben oder springen; nur eventSeq-Lücken verlangen Resync.

## Snapshot und begrenzter Resync

Annahme nur bei nicht älterer Stateversion, Eventsequenz und Settingsrevision.
Gleiche Stateversion mit höherer Sequenz ist gültig. Nur snapshotfähige Domains
werden ersetzt. Der Snapshot liefert keine Segmentliste und keinen Nutztext.
Fehlende Terminalbelege, verschwundene Pendingactivations und nachgewiesene
Terminalzähler ohne empfangene Segmente werden sichtbar als unvollständig
geführt. Zähler erzeugen niemals Texte, Segment-UUIDs oder angenommene Finals.

Seqgap bzw. ungültiges erwartetes Event setzt `resyncing`. Ein offener
Snapshotprozess, begrenzt auf 512 Events / 4 MiB UTF-8-JSON, zwei Versuche mit
je 5 Sekunden monotoner Snapshotdeadline. `MirrorLimits` erlaubt überprüfbare
lokale Anpassungen. Währenddessen prüft der Transport `domain_ready` sowohl
vor Annahme als auch unmittelbar vor dem Senden eines Activationcommands,
einschließlich bereits wartender Aufrufer. Snapshotcommands laufen durch den
vorhandenen CommandTracker, erzeugen eigene IDs und verwenden dessen
unveränderte Retry-/Acksemantik. Die Ackbestätigung ersetzt keinen Snapshot.

Gepufferte Payloads werden nach eventSeq sortiert. Bis einschließlich des
Snapshotcursors werden Segmenttexte und Terminaltombstones idempotent
nachgetragen, ohne Vordergrund oder Settings rückwärts anzuwenden. Neuere
Events werden ab diesem Cursor sequenziell reduziert. Eine weitere Lücke
fordert einen neuen begrenzten Snapshotprozess an. Überlauf oder wiederholter
Timeout erzeugt `incomplete` und `reconnect_required`; der Adapter schließt
genau die aktuelle Socketbindung kontrolliert. Keine Finals aus Logs rekonstruieren.

`clarify(generation, now)` fragt snapshotfähige Werte nach, ohne einen neuen
Foreground zu erfinden. Start ohne Deadline, closing_input-Ack, bestimmte
Recovery-Ackadvice und eventlose Settings-/Audio-/Suppressioncommands benutzen
diesen Pfad. Ackphasen werden nie in Input übernommen. `protocol_fault`
degradiert ohne geratenen Payload. Ohne installierten Mirror behält der
Transport seine bisherige strikte Protokollfehlersperre.

`tick(generation, now)` und `snapshot_wait(now)` bedienen ausschließlich lokale
Resynctimer. `Deadline.remaining(now)` berechnet Restzeit aus remainingMs und
lokalem Empfangsanker. Countdownablauf sendet keinen Timeout-/Finishcommand.
Lange Finalinferenz allein besitzt keinen lokalen Reconnecttimer.

Alle Eventfingerprints, Segmentidentitäten und Terminaldaten werden während
der Socket-Session erhalten, damit alte Resultate sicher dedupliziert bleiben.
Der Resyncpuffer ist separat begrenzt. Die gesamte Sessionledgergröße wächst
mit tatsächlich beobachteten Segmenten/Events; Retention ist hier kein
unbelegter automatischer Evictionmechanismus.

## Prüfpfad

`tests.test_v2_mirror` prüft reine Projektion, 18 Events, Snapshot-/Versions-/
Sessionguards, tatsächliche Transportanbindung, 60 zulässige Backgroundraces
und 24 Terminalpermutationen. Jeder Schritt besitzt ID-/Terminalinvarianten.
`scripts/check_v2_server_transport.py --with-mirror --server-root <Export>
--server-repository <Servergit>` erweitert den bestehenden echten TCP/WS-Harness:
reale Recordercallbacks, Segmente, Interims, Finals und gezielt verworfene
reale Events führen durch tatsächlichen Transport/Mirror/Tracker zu realen
Serversnapshots. Geladene Serverquellen werden gegen ada13b0 bytegeprüft.
Nur GateAwareRecorder/AutoScheduler ersetzen Hardware/Modelle; rohes PCM und
Audioavailability ersetzen noch ausstehende Clientaudio-/Settingsservices.
Keine Liveinstanz, Nutzeraufnahme, Clipboard oder ASRqualifikation. Die finale
getrennte Prozess-/Qt-/Hardwarequalifikation bleibt ihren Folgepaketen zugeordnet.
