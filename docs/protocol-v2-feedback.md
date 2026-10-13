# Appanschluss AP100, 2026-10-13

Reguläre Runtimeverdrahtung jetzt umgesetzt; [tatsächliche Appports und Thread-/Persistenzregeln](protocol-v2-runtime.md). Frühere AP100-offen-Angaben unten sind historischer Stand des jeweiligen Pakets.

# V2-Feedback – AP-CV2-090

Der bestehende `FeedbackEngine` erhält validierte `Reduction`-Objekte vom
`ActivationMirror`. Logereignisse und der V1-Fallback werden nach dem ersten
akzeptierten V2-Mirror ausschließlich diagnostisch behandelt. Sie dürfen keine
Runtimezustände rekonstruieren. Die reguläre Appkomposition bleibt AP-CV2-100.

## Öffentliche Ports und Reihenfolge

`FeedbackEngine.handle_reduction(reduction)` liefert zuerst eine permanente
`FeedbackDecision`, danach deduplizierte Ereignisentscheidungen. Alle tragen
denselben unveränderlichen `FeedbackSnapshot`. `persistent=True` enthält nur
dauerhafte LEDcalls und Appmapping; danach enthalten Ereignisse nur LEDpuls/
Overlaycalls und den vorhandenen Soundcue. Bei unveränderter LEDregel entfällt
deren erneute Ausgabe, die UI bekommt weiterhin den neuen Snapshot.

`V2FeedbackConnection(mirror, engine, observability=...)` wird nach Controls/Results und vor
`transport.run()` angeschlossen. Es ruft zuerst den vorherigen
`mirror.on_reduction`-Callback, dann den Feedbackpfad und `on_decision` auf.
Ausgabeexceptions werden isoliert und in `engine.adapter_failures` gezählt.
`close()` invalidiert und löst nur diesen Port; Session und Audio gehören dem
bisherigen Owner. Port vor dem Mirror schließen. Ein vorheriger Corecallback
behält seine bisherige Fehlersemantik.

`V2FeedbackOutput(tray=..., overlay=..., sound=..., led=...)` lebt im Qt-Mainthread.
Der Core emittiert `decision_received`; die explizit queued Verbindung ruft den
Slot `apply` im Mainthread auf. `apply` direkt ausschließlich dort verwenden.
Es verwendet die vorhandenen `SoundFeedback.play`- und
`LedFeedbackBridge.submit(calls, live=...)`-Schnittstellen. LEFX-/Null-/Simulation
bleiben erhalten. Tray, Overlay, Sound und LED werden einzeln gegen Exceptions
geschützt; `failure` meldet jede Kategorie einmal. Bestehende Adapter-
Fehlersignale ebenfalls auf stabile Kategorien abbilden. `close()` sperrt schon
queued Ausgaben; Sound/LEDowner anschließend regulär schließen.

`update_connection` projiziert den Logzustand sekundär.
`update_v2_issues(issues)` ersetzt ausschließlich bekannte Kategorien:
`history_unavailable`, `injection_failed`, `key_rejected`, `sound_failed`,
`led_unavailable`, `action_blocked`. Leeres Tuple räumt diese Diagnosen auf.
Ausgabeadapterfehler lösen keinen weiteren Warnsound aus.

## Autorität, Darstellung und Guards

`FeedbackSnapshot` enthält Generation, Session, Revision, Inputphase,
Foregroundactivation, Audio-/Manualavailability, Suppression, Backgroundpending,
Unvollständigkeit, Diagnosen, relative Deadline und segmentgebundene Vorschauen.
`primary_source` ist nur Diagnose. Manual und Wake nutzen denselben Phasenkey.
Idle plus Drain bleibt bereit. Alte Finals dürfen ihren Completecue ausgeben,
aber keinen dauerhaften Zustand und keine fremde Vorschau überschreiben.

Der Engineguard verwirft ältere Generationen, fremde Sessions derselben
Generation sowie rückläufige Eventsequenz/Stateversion. Ein bereits
disconnected Generationstand kann nicht durch eine alte Reduction reanimiert
werden. Eine neue Generation setzt Zustands- und Dedupekontext zurück.
Qtguard verwirft ältere Generation-/Session-/Revisionstände. Ereignisidentitäten
sind auf Engine- und Ausgabeseite begrenzt; keine unbeschränkte Replayliste.

`TranscriptOverlay.apply_feedback_snapshot` zeigt die jüngste Vorschau der
Foregroundactivation, als PlainText und getrennt vom Statuslabel. Terminal-
und Late-interimschutz kommen aus dem tatsächlichen Mirror. Bis zu 128
Vorschauen mit je maximal 16384 Zeichen werden kopiert; Resultat-/Historytext
wird nicht gekürzt. `presentation_for_v2_snapshot(snapshot, now=...)` erzeugt
den quellenneutralen Trayzustand mit getrennten Drain-/Fehlerhinweisen.

`FeedbackSnapshot.remaining_ms(now)` benutzt die vorhandene monotone relative
Deadline. Unixdeadline ist keine lokale Autorität. Watchdogcountdown gilt nur
für die aktive Aufnahmephase; Followup verwendet wieder seine Inputdeadline.
Der Overlaytimer aktualisiert nur Text und erzeugt weder Finish noch Cancel.
Das tatsächliche Audio-/Controls-/Resultatverhalten bleibt bei seinen Services.

## Mapping, Profile und Observability

Schema2 bleibt erhalten. `migrate_v2_feedback_mapping` ergänzt fehlende Keys:
`server.activation.started`, `server.input.waiting`, `server.input.followup`
aus `client.hotkey.accepted`; `server.input.idle` aus
`server.transcription.discarded`; `server.input.closing` aus
`server.transcription.started`. Explizite V2keys gewinnen. Alte benutzerdefinierte
Regeln und Soundpräferenzen bleiben byte-/werttreu erhalten; `migration_report`
nennt ergänzte Regeln und diagnostisch zurückgestellte Wake-detected-Regeln.
Parsing ist rein im Speicher, ohne heimlichen YAMLwrite. Persistieren über den
bisherigen Konfigurationsport schreibt die erweiterten Keys; schema1 bleibt
sichtbar reparaturpflichtig. Profilmigration und Originalbackup bleiben AP070.

Der Engine besitzt ausschließlich `on_observation(type, **fields)` als optionalen
non-throwing Callback und importiert keine Loggingmodule. Der V2-Port verbindet
den Ingress und stellt den vorherigen Callback bei `close()` wieder her.
`client.domain.observed` und `client.feedback.decision` benutzen den bestehenden
`ClientEventEmitter`/Ingress. Correlation enthält Session, Generation,
Activation, Domainsegment-UUID und bei input_closed `causedByCommandId`.
Allowlist enthält IDs/Sequenz/Phase/Zähler; keine Texte, Tokens, Settings oder
beliebigen additiven Wirefelder. Snapshotrepr unterdrückt Vorschautext.
Domain-/Diagnose-/Adapterzähler bleiben einfache Zähler auf dem Producer.

Die vorhandenen OBSmodel-/Query-/Ingresssegmenttypen akzeptieren zusätzlich
nichtleere Domain-UUIDstrings. Legacyinteger bleiben gültig. SQLite INTEGER-
Affinity speichert nichtnumerische UUIDs bereits als TEXT; keine DBmigration.
Lokale Filter und gemischte Keyset-Sortierung erhalten beide Typen. Der
Logviewer erhält vollständige UUIDs auch aus Kontextaktionen; halb eingegebene
IDs bleiben unbeschränkt. Seine Live-/Tabellensortierung stimmt mit SQLite
überein (NULL, Legacyinteger, UUIDtext). Opaque
Logsegmentlabels werden niemals zu Domainidentität, auch bei gleichen Bytes.

## Nachweis und verbleibende Gates

Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`; er schaltet die
reguläre App noch nicht automatisch auf diese V2ports um. Der echte lokale
Servercheckpoint verwendet Produktions-FastAPI, Domain-/Log-TCP-WebSockets,
SQLite-Replay, Controls, Mirror und reale Qtwidgets am gepinnten Server ada13b0.
Deterministisches PCM, Recorder/ASRscheduler und physische Sound-/LEDausgänge
sind kontrollierte Grenzen. Hardware-/ASR-/Wahrnehmungsqualifikation bleibt
AP-IV2-020, Appverdrahtung AP100; Server-Distributed bleibt offen.

[Runreport und Windowsbelege](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/01_REPORT.md).
