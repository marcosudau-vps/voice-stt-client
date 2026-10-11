# Tatsächlicher Serverstand und Konsequenzen für den Client

Alle Aussagen gelten für `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Normative Schnittstellendetails stehen vollständig in [K-01](../../KONTRAKTE/K-01_WIRE_AUDIO_COMMANDS.md), [K-02](../../KONTRAKTE/K-02_EVENTS_MIRROR_ERGEBNISSE.md), [K-03](../../KONTRAKTE/K-03_SETTINGS_WAKE_WORDS.md), [K-04](../../KONTRAKTE/K-04_LOGS_AUTH_RECOVERY.md).

## 1. Implementierte Architektur

| Autorität | Servermodule | Bedeutung für den Client |
| --- | --- | --- |
| Activation/Vordergrund | `api_fastapi_server/activation.py`, `activation_commands.py` | first trigger wins, fünf Phasen, IDs und Fristen vom Server |
| Recordergate/VAD | `VoiceSTT/core/activation_control.py`, kontrollierter Recorderpfad in `api_fastapi_server/server.py` | kein lokaler Aufnahme-/VADabschluss |
| Segmentledger | `api_fastapi_server/segment_ledger.py` | eingefrorene Herkunft, Hintergrunddrain, geordnete Finals und Terminals |
| V2transport | `api_fastapi_server/protocol_v2/` | clientinitiierter Hello, Commandcache, Events, Snapshot |
| Settings | `api_fastapi_server/settings_control.py` | getrennte Session-/Serverrevisionen, Apply und persistierte Defaults |
| Wakecatalog/Detection | `VoiceSTT/core/wakeword_catalog.py`, `wake_detection.py`, `wake_audio_boundary.py`, `api_fastapi_server/wake_admission.py` | kanonische atomare Auswahl, selected-only, Hitgruppierung, Audioübergang |
| Realtimeherkunft | `VoiceSTT/core/realtime_callbacks.py`, Recorder-/Transkriptionspfad | Resultate bleiben an ursprüngliches Recording-/Segment gebunden, stale Beobachtungen verworfen |
| Diagnosehistory | `VoiceSTT_server/event_logging.py` | separater committed SQLitepfad, Logbootstrap, Scope-/Retentioncursor |

## 2. Für die Planung entscheidende Abgleichsergebnisse

| Sachverhalt | Tatsächlicher Stand | Verbindliche Clientkonsequenz |
| --- | --- | --- |
| Protokollcut | V2 separat auf `/ws/v2`; `/ws/transcribe` bleibt dauerhafter V1-Kompatibilitätspfad für vorhandene Clients/Browser | neuer Desktop ausschließlich V2; kein Fallback und keine Server-V1-Löschung im Clientpaket |
| Realtime | `transcription.interim` mit stabiler Segmentherkunft ist implementiert | Vorschau weiter anbieten, Terminalguard und keine Interiminjektion |
| Logzugriff | `hello.accepted.logAccess` ist implementiert; Resyncsnapshot ohne Token | vorhandenen Dualsocket pflegen, Bootstrap auf Annahmenachricht umstellen |
| Audio | uint32LE-Metadatenlänge + UTF8JSON + PCM16; ohne Magic/Flags | vorhandenen Encoder weiterverwenden und streng validieren |
| Event-/Ackordnung | Event-vor-Ack; Finishingack kann älter sein | Pendingabschluss und aktuelle Phase trennen |
| Eingabeschluss | Terminal-vor-Close und Neuactivation-vor-Altclose sind möglich | sämtliche Updates ID-bezogen |
| Resync | Snapshot besitzt keine Segmenttexte und keine Domainreplayfunktion | Puffertexte erhalten, tatsächlichen Verlust sichtbar machen |
| Silence-Timings | Serverautorität; 6 Timingkeys und weitere Wakekeys | lokale Diktierfensterautorität vollständig ablösen |
| Registryform | 18 Schemafelder, 16 Sessionwerte, 15 Serverdefaults; requested/effective nicht in Schemaeintrag | verschiedene Responseformen korrekt zusammenführen |
| NS-Settings | Sessionpatch akzeptiert Auswahl/Noise/VAD als requested, ohne Sessionneuaufbau; Hello enthält nur Trigger/Auswahl/Suppression | Auswahl via Hello; Noise/VAD nur wirksamer Serverdefaultpfad |
| Authprüfung | Admin-Guard bei Mutationsrouten, öffentliche GETs | No-change-PATCH als Keyprüfung; Credential Manager |
| Terminalrecovery | irreparable Domainsession schließt aktiv mit 1011 und gibt Slot frei | nicht auf weitere Nachricht warten, neue Session |
| Logcursor | global/filtered und scopebezogene Retention | Cursorlücke ist kein Domain-Eventgap; keinen gemeinsamen Reducer verwenden |

## 3. Verbleibende Grenzen

**L-01 – Domaintexte nicht replaybar.** Ein fehlendes `transcription.completed` lässt sich mit Snapshot allein nicht nachliefern. Auch eine teilweise Loghistory darf nicht als automatisch injizierbares Final interpretiert werden. Das Integrationsgate prüft sichtbare Unvollständigkeit statt unerfüllbarer Wiederherstellung.

**L-02 – Individuelle Wake-Engine-Startoptionen fehlen.** `noiseSuppressionEnabled` und `vadThreshold` sind NS-Keys, aber kein Hello nimmt individuelle Startwerte entgegen. Für ein künftig anderes Produktziel braucht es ein separat freigegebenes Serverpaket mit Versionierung, Admission und Tests. Der Client wird auf die vorhandene Oberfläche gebaut.

**L-03 – Aliaspatchinkonsistenz.** `wakeWord.selection`-Patch kann Aliase unverändert speichern, Hello verlangt kanonische IDs. Client löst lokal auf und sendet nur IDs. Kein Pflichtserverfix für die Clientumsetzung.

**L-04 – Wakekalibrierung.** Die Schemawerte mit calibration=pending besitzen noch keine vollständige reale positive Kalibrierung. Audioübergang operational über qualified-hit-trailing-edge, keine garantierte lexikalisch perfekte Wakewortentfernung. Das reale Gate bleibt für diese Eigenschaft nachweispflichtig.

**L-05 – Keine Anwendungs-Auth auf Audio-WS.** Der Serverguard schützt Administration und Logzugriff, nicht `/ws/v2`. Der Client erfindet keinen Authparameter. Produktionszugang muss ggf. separat per Proxy/Netzwerk bereitgestellt werden.

**L-06 – Final-Inferenzlatenz und Kapazität.** Angenommene Session garantiert nicht sofort einen freien Sprecherslot oder eine schnelle Inferenz. Limits, Lazy-Modellreload, Failureterminals und Hintergrunddrain müssen darstellbar bleiben. Foreground darf dafür nicht künstlich finalizing bleiben.

**L-07 – Numerische Commandversion-Toleranz.** `parse_command` akzeptiert neben Integer `2` auch Float `2.0`; Bool ist abgelehnt. Die Hello-Versionsliste ist dagegen strikt ganzzahlig. Der Client schreibt ausschließlich Integer `2`. Diese nachgewiesene Parserabweichung erfordert für die geplante Clientumsetzung keinen Serverfix.

## 4. Belegmethodik und Grenzen dieser Prüfung

Gitremotes und SHAs wurden abgeglichen. Analyse und Testdaten stammen aus Commitexporten, nicht aus verändertem Workingtree. Die Protocol-, Settings- und Recoveryreferenzen wurden mit ihren tatsächlichen Parsern/Projektoren verglichen. Maschinenlesbare Registry/Vokabularbelege wurden direkt aus dem Code exportiert. Die Quellpfade und Testnamen sind im lokalen [Manifest](../../../EVIDENCE/source-manifest.json) und [Server-Testkatalog](../../../EVIDENCE/server-test-catalog.json) festgehalten.

Gezielter Lauf: 307 Servertests plus 299 erfolgreiche Subtests, ein zunächst übersprungener optionaler Vergleichstest. Dieser Bytevergleich wurde anschließend mit dem exportierten Vertragsvektor separat ausgeführt und bestand ebenfalls. Es wurde keine vollständige modellabhängige Serverqualifikation oder Produktionshardwareabnahme neu durchgeführt. Die Aussage „vorläufiger Serverfinalstand“ ist die vorgegebene Baselineentscheidung des Auftraggebers, keine durch die Planung neu erteilte Releasefreigabe.
