# Traceability – Entscheidung zu Umsetzung und Nachweis

**Status:** Vollständigkeitsaudit PLAN-EXEC-002, fortgeschrieben durch die
Root-Abnahme von `AP-SRV-050` (2026-08-27); 130 eindeutige Summary- und
Einzelanforderungen, AP-Zuordnung verbindlich. Konkrete Testdateien und
gepushte Nachweis-SHAs werden bei AP-Start beziehungsweise Abnahme in
`AUSFUEHRUNGSSTATUS.md` geführt, damit fachlicher Planungsstatus und
Ausführungsgate getrennt bleiben.

Die fachlichen Details und offenen Teilfragen stehen in
`../PLANUNG/ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`. Diese Tabelle dient nur
als kompakter Verlustschutz.

| ID | Anforderung / Entscheidung | Planungsstatus | AP | Nachweis |
|---|---|---|---|---|
| CORE-01 | Ein gemeinsamer serverseitiger Lifecycle | BESTÄTIGT | SRV-010, INT-010 | Lifecycle-E2E |
| CORE-02 | Manual/Hotkey und Wake Word sind Triggerquellen, keine Betriebsmodi | BESTÄTIGT | SRV-010, CLI-020 | Config-/Architekturtest |
| CORE-03 | First Trigger wins; genau eine offene Activation | BESTÄTIGT | SRV-010 | Collision-/Race-Test |
| CORE-04 | Weitere Trigger öffnen und mergen keine zweite Quelle | BESTÄTIGT | SRV-010 | Negativ-/Collision-Test |
| CORE-05 | Server ist Lifecycle-Autorität; Client spiegelt | BESTÄTIGT | SRV-040, CLI-010 | Snapshot-/Mirror-Tests |
| CORE-06 | Sessiongebundener kontinuierlicher Audiostream | BESTÄTIGT | CLI-010 | Multi-Activation-E2E |
| CORE-07 | Lokales VAD ist keine Manual-Aufnahmeautorität | BESTÄTIGT | CLI-010, CLI-050 | Architektur-/Integrationstest |
| CORE-08 | Source-neutrales UI-/Tray-/LED-/Sound-Feedback | BESTÄTIGT | CLI-040 | Paarvergleich Manual/Wake Word |
| CORE-09 | `session.mode` besitzt keine Runtime-Autorität | BESTÄTIGT | SRV-070, CLI-050 | Config-/AST-Test |
| CORE-10 | Lock endet nach sicherem Eingabeschluss; Hintergrund-Finalisierung blockiert nicht | BESTÄTIGT | SRV-010, SRV-020, CLI-010 | Drain-/Lock-Test |
| CORE-11 | Eine Activation darf mehrere serielle Sprachsegmente enthalten | BESTÄTIGT | SRV-010, SRV-020 | Mehrsegment-/Follow-up-E2E |
| CORE-12 | Serververlust verwirft Activation; Geräteverlust cancelt sie ohne Sessionende | BESTÄTIGT | SRV-030, CLI-020, INT-010 | Server-/Device-Reconnect-E2E |
| CORE-13 | Vordergrundphasen und Hintergrundledger sind getrennt; alte Finals bleiben korrekt zugeordnet/geordnet | BESTÄTIGT | SRV-020, CLI-010 | Multi-Activation-/Out-of-order-E2E |
| WW-01 | Build-Katalog; atomare Sessionauswahl; nur angenommene Auswahl wird geladen | BESTÄTIGT | SRV-060 | Katalog-/Admission-/Ressourcentest |
| WW-02 | Kanonische IDs und tolerante explizite Aliase | CONTRACT FROZEN | SRV-060 | Normalisierungs-/Kollisionstests |
| WW-03 | Ein oder mehrere aktive Wake Words; gemeinsame Empfindlichkeit | CONTRACT FROZEN | SRV-050, SRV-060 | Config-/Detection-Tests |
| WW-04 | Erster akzeptierter Treffer latched bis Unlock; höchstens ein Detection-Ereignis; Zusatzregel messdatenabhängig | CONTRACT FROZEN / KALIBRIERUNG | SRV-060 | Score-Trace-/Audio-/Debounce-Test |
| WW-05 | Wake Word während Activation ohne direkte Triggerwirkung | BESTÄTIGT | SRV-060 | Negativtest plus VAD-Test |
| WW-06 | Pause übersteht Reconnect, nicht den Programmneustart | BESTÄTIGT | CLI-020 | Reconnect-/Restart-Test |
| WW-07 | ReSpeaker-Hardware-Mute bleibt clientseitig und unabhängig | BESTÄTIGT | CLI-020 | Geräte-/Clienttest |
| WW-08 | Wake Word nicht transkribieren, unmittelbar folgende Sprache erhalten | BESTÄTIGT / KALIBRIERUNG | SRV-060 | Audio-Grenz-/Sprachflusstest |
| HK-01 | Zwei Activation-Hotkeys plus optionaler dritter Wake-Pause-Hotkey | BESTÄTIGT | CLI-020 | Config-/Controller-E2E |
| HK-02 | Follow-up-Reset; Watchdog initial 600 s, Refresh mindestens 180 s Rest; nie kumulativ | BESTÄTIGT | SRV-030, CLI-020 | Phasen-/Clock-/Mehrfachdruck-Test |
| HK-03 | Finish-/Cancel-Phasenmatrix, Exactly-once-Event und Cancel ohne Textrücknahme | BESTÄTIGT | SRV-020, SRV-030, CLI-020 | Phasen-/Terminal-/Replay-/Event-E2E |
| HK-04 | Feste `Active = Finish`- und kumulative Extend-Semantik sind ungültig | ÜBERHOLT | – | Negativprüfung alter Solltests |
| SET-01 | Server ist letzte Autorität; Session- und admin-geschützte Serverwerte | BESTÄTIGT | SRV-050, CLI-030 | Scope-/Auth-/Effective-Value-Tests |
| SET-02 | Apply-Policy je Wert; laufende Activations behalten ihren Start-Snapshot | CONTRACT FROZEN | SRV-050, CLI-030 | Live-/Next-Activation-/Reconnect-/Snapshot-Tests |
| SET-03 | Admin-Key im Credential Manager, UI-Löschung, kein Klartext-Fallback | BESTÄTIGT | CLI-030 | Auth-/Credential-/UI-Tests |
| SET-04 | Settings-Fundament und Triggerdomäne jetzt; fachfremde Vollmigration später | BESTÄTIGT | SRV-050, CLI-030 | Architektur-/Scope-Review |
| SAFE-01 | Watchdog 600/180/30 s, Activation-Ende und reguläre Audioverarbeitung | BESTÄTIGT | SRV-030, CLI-040 | Fake-Clock-/Warn-/Abschluss-/Resultat-E2E |
| A-01 | Phasen, Übergänge, Lock-Freigabe und Recovery | CONTRACT FROZEN | SRV-010, SRV-030 | State-Machine-/Fault-Tests |
| A-02 | Snapshot/Sequenz-Resync; Client erfindet kein Idle | CONTRACT FROZEN | SRV-040, CLI-010 | Reconnect-/Eventverlust-E2E |
| A-03 | Server-resolved Timing- und Konfigurationsautorität | CONTRACT FROZEN | SRV-050, CLI-030 | Contract-/Config-Tests |
| A-04 | IDs, Idempotenz, Replay und stale-Regeln | CONTRACT FROZEN | SRV-030, SRV-040, CLI-010 | gemeinsame Wire-Vektoren plus Protocol-/Replay-Tests |
| A-05 | Protokoll v2, klarer Cut, Browser später, Versions-/Commitmatrix | CONTRACT FROZEN | SRV-070, CLI-050, INT-010 | Wire-Schema, gemeinsame Vektoren, Handshake-/Kompatibilitätstest |
| A-06 | Persistierte Basis; getrennte laufzeitweite Suppression; kein Pause-all | CONTRACT FROZEN | SRV-040, CLI-020 | Restart-/Reconnect-/Admission-/UI-Test |

## Granularisierte Einzelanforderungen

Die obere Tabelle bleibt der kompakte fachliche Index. Die folgenden Zeilen
zerlegen die zuvor teilweise gebündelten Aussagen so weit, dass bei der
AP-Abnahme kein einzelner Contractpunkt in einem Sammelnachweis verschwinden
kann.

### Activation, Phasen und Hintergrundverarbeitung

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| CORE-14 | Live-Transkription läuft während der Aufnahme; Final darf früh anlaufen, wird aber erst segmentbezogen definitiv veröffentlicht | CONTRACT FROZEN | SRV-020, CLI-040 | Early-Final-/Publication-E2E |
| CORE-15 | Follow-up-Fenster und Final-Inferenz dürfen parallel laufen | CONTRACT FROZEN | SRV-020, CLI-010 | Parallelitäts-/Fake-Clock-Test |
| CORE-16 | Eine neue Activation darf beginnen, während ältere Activations im Hintergrund drainen | CONTRACT FROZEN | SRV-010, SRV-020, CLI-010 | Overlap-/Multi-Activation-E2E |
| CORE-17 | Bereits veröffentlichter oder eingefügter Text wird durch späteren Cancel, Disconnect oder Recovery nicht zurückgenommen | BESTÄTIGT | SRV-020, CLI-040, INT-010 | Publish-then-cancel-/Disconnect-E2E |
| PHASE-01 | Der Vordergrund kennt exakt `idle`, `waiting_first_speech`, `segment_active`, `followup_wait`, `closing_input` | CONTRACT FROZEN | SRV-010, CLI-010 | Enum-/State-Machine-Test |
| PHASE-02 | `finalizing` ist kein blockierender Vordergrundzustand, sondern Hintergrund-`draining` | CONTRACT FROZEN | SRV-010, SRV-020, CLI-010 | Architektur-/Lock-Test |
| PHASE-03 | In `waiting_first_speech` darf der Anwender weiterhin das erste Sprachsegment beginnen; `refresh` ist dort unzulässig | BESTÄTIGT | SRV-010, SRV-030, CLI-020 | First-Speech-/Negativtest |
| PHASE-04 | `idle` wird erst nach geschlossenem Gate/Recorder, registrierten Segmentausgängen und registriertem Close-Ereignis veröffentlicht | CONTRACT FROZEN | SRV-010, SRV-020, SRV-030 | Closing-Barrier-/Fault-Test |
| PHASE-05 | `closing_input` besitzt einen defensiven Recovery-Timeout und erreicht auch bei Gate-/Recorderfehlern wieder `idle` | CONTRACT FROZEN | SRV-030 | Recovery-/Fault-Injection-Test |

### Segmentledger, Ergebnisse und Reihenfolge

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| LEDGER-01 | Jedes angenommene Segment besitzt genau einen terminalen Zustand `completed`, `discarded`, `cancelled` oder `failed` | CONTRACT FROZEN | SRV-020 | Terminal-Cardinality-Test |
| LEDGER-02 | Leere Final-Transkription endet als `discarded(reason=empty_final)` | CONTRACT FROZEN | SRV-020, CLI-040 | Empty-Final-Test |
| LEDGER-03 | Queue-Limit, Sessionende, Inferenzfehler und Recovery erzeugen maschinenlesbare Segmentterminals | CONTRACT FROZEN | SRV-020, SRV-030 | Queue-/Fault-/Disconnect-Test |
| LEDGER-04 | Nach Eingabeschluss gilt vor dem Activation-Terminal `acceptedSegmentCount == terminalSegmentCount` | CONTRACT FROZEN | SRV-020 | Ledger-Invarianten-Test |
| LEDGER-05 | Pro Activation entsteht nach vollständigem Drain genau ein terminales Activation-Ereignis | CONTRACT FROZEN | SRV-020, SRV-040 | Exactly-once-Eventtest |
| LEDGER-06 | `segmentSequence` steigt innerhalb der Session streng monoton | CONTRACT FROZEN | SRV-020 | Sequence-Test |
| LEDGER-07 | Nutzresultate werden pro Session in `segmentSequence`-Reihenfolge veröffentlicht; Fehler/Discard füllen Sequenzlücken | CONTRACT FROZEN | SRV-020, CLI-010 | Out-of-order-/Hole-Fill-E2E |
| LEDGER-08 | Delayed Finals verwenden unveränderliche Job-IDs und niemals einen globalen Current-Activation-Zeiger | CONTRACT FROZEN | SRV-020 | Old-Final/New-Activation-Race-Test |

### Timer, Refresh und Daueraufnahme-Schutz

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| TIME-01 | `initialSpeechTimeoutMs` ist sessionkonfigurierbar, Default 15000 ms, Apply `next_activation` | CONTRACT FROZEN | SRV-030, SRV-050, CLI-030 | Schema-/Fake-Clock-Test |
| TIME-02 | `followupTimeoutMs` ist sessionkonfigurierbar, Default 3000 ms, Apply `next_activation` | CONTRACT FROZEN | SRV-030, SRV-050, CLI-030 | Schema-/Fake-Clock-Test |
| TIME-03 | `refresh` in `followup_wait` setzt die Deadline auf `now + followupTimeoutMs` und spart kein Zeitguthaben an | BESTÄTIGT | SRV-030, CLI-020 | Mehrfach-Refresh-/Clock-Test |
| TIME-04 | Segment-Watchdog startet standardmäßig mit 600000 ms und warnt 30000 ms vor Ablauf | BESTÄTIGT | SRV-030, CLI-040 | Warning-/Expiry-Test |
| TIME-05 | `refresh` in `segment_active` setzt `max(currentDeadline, now + 180000 ms)` und verkürzt keine längere Restzeit | BESTÄTIGT | SRV-030, CLI-020 | Early-/Late-Refresh-Test |
| TIME-06 | VAD-Aktivität setzt den Daueraufnahme-Watchdog nicht zurück | BESTÄTIGT | SRV-030 | Dauer-Sprache-/Fake-Clock-Test |
| TIME-07 | Jede wirksame Timeränderung erhält eine neue `timerRevision`; stale Timer verändern keinen neueren Zustand | CONTRACT FROZEN | SRV-030 | Stale-Callback-Race-Test |
| TIME-08 | Watchdog-Ablauf verarbeitet erfasstes Audio, schließt die ganze Activation und öffnet kein Follow-up | BESTÄTIGT | SRV-030, SRV-020, CLI-040 | Watchdog-End-to-End-Test |

### Commands, Trigger und Suppression

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| CMD-01 | Der Desktop-Client sendet `activate` ausschließlich mit `source=manual`; `wake_word` entsteht nur serverintern | CONTRACT FROZEN | SRV-040, CLI-020 | Positiv-/Negativ-Wire-Vektor |
| CMD-02 | `refresh`, `finish` und `cancel` enthalten die vom Client beobachtete `activationId` | CONTRACT FROZEN | SRV-030, SRV-040, CLI-020 | Payload-/Stale-ID-Test |
| CMD-03 | `activate` ist nur in `idle` zulässig; offene und schließende Phasen antworten `activation_locked` | CONTRACT FROZEN | SRV-010, SRV-030 | Phasenmatrix-Test |
| CMD-04 | `finish` und `cancel` sind in jeder offenen Phase zulässig und erzeugen bei Annahme ein korreliertes Lifecycle-Ereignis | BESTÄTIGT | SRV-030, SRV-040, CLI-020 | Phasen-/Eventmatrix-Test |
| CMD-05 | Ein identischer `commandId`-Replay liefert dasselbe Ack und keine zweite Wirkung | CONTRACT FROZEN | SRV-030, SRV-040, CLI-010 | Replay-/Exactly-once-Test |
| CMD-06 | Derselbe `commandId` mit anderem Payload wird `command_id_conflict` | CONTRACT FROZEN | SRV-030, SRV-040 | Conflict-Vektor |
| CMD-07 | Falsche `sessionId`/alte `activationId` werden `stale_session`/`stale_activation` und verändern keinen Zustand | CONTRACT FROZEN | SRV-030, SRV-040, CLI-010 | Stale-Command-Test |
| CMD-08 | Jedes syntaktisch erkennbare Clientcommand erhält genau ein `command.ack` mit den verbindlichen Statusfeldern | CONTRACT FROZEN | SRV-040, CLI-010 | Ack-Schema-/Cardinality-Test |
| TRIGGER-01 | Manual und Wake Word sind getrennt suppressierbar; es gibt keine zusätzliche Pause-all-Aktion | BESTÄTIGT | SRV-040, CLI-020 | Suppression-API-/UI-Test |
| TRIGGER-02 | Laufzeitsuppression übersteht Reconnect, neue Session und Geräteverlust derselben `clientRunId` | BESTÄTIGT | SRV-040, CLI-020 | Reconnect-/Device-Test |
| TRIGGER-03 | Ein Programmneustart erzeugt neue `clientRunId` und startet ohne alte Suppression | BESTÄTIGT | CLI-020 | Restart-Test |
| TRIGGER-04 | Dauerhaft gespeicherte Basiskonfiguration besitzt mindestens einen Trigger; zur Laufzeit sind null effektive Trigger erlaubt | BESTÄTIGT | CLI-020, SRV-040 | Persistenz-/Admission-Test |
| TRIGGER-05 | Primary-, Secondary- und optionaler Wake-Pause-Hotkey sind lokal konfigurierbar; Active-Aktionen sind `refresh|finish|cancel|none` | BESTÄTIGT | CLI-020 | Mapping-/Controller-Test |
| TRIGGER-06 | Kollidierende oder identische physische Hotkeybelegungen dürfen nie zwei Commands auslösen; konkrete UI-/Validierungsregel wird vor CLI-020 festgelegt | TECHNISCH OFFEN | CLI-020 | Konfliktmatrix-/Dispatchtest |

### Wire, Snapshot und Kompatibilität

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| WIRE-01 | `hello` ist die erste Nachricht und handelt ausschließlich Protokollversion 2 für diesen Cut aus | CONTRACT FROZEN | SRV-040, CLI-010 | Handshake-Vektor |
| WIRE-02 | Sessionauswahl und Suppressionsmaske werden vor Audio-/Triggerfreigabe atomar validiert | CONTRACT FROZEN | SRV-040, SRV-060, CLI-010 | Admission-/Early-Audio-Negativtest |
| WIRE-03 | Keine gemeinsame Version erzeugt `protocol.incompatible`, keine `sessionId` und keine teilweise aktive Session | CONTRACT FROZEN | SRV-040, CLI-050 | Inkompatibilitäts-E2E |
| WIRE-04 | Sessionadmissionfehler liefern `session.rejected` mit feldbezogenen, nicht geheimen Fehlern | CONTRACT FROZEN | SRV-040, SRV-060, CLI-010 | Reject-Schema-Test |
| WIRE-05 | Events tragen `eventId`, streng steigende `eventSeq`, `stateVersion` und Zeitstempel; Client dedupliziert Replays | CONTRACT FROZEN | SRV-040, CLI-010 | Event-Replay-/Sequence-Test |
| WIRE-06 | Eine Eventlücke versetzt die Ableitung in `resyncing` und fordert Snapshot an; Client erfindet kein `idle` | CONTRACT FROZEN | SRV-040, CLI-010 | Gap-/Resync-Test |
| WIRE-07 | Snapshot enthält Vordergrund, Pending-Activations, Trigger, Audio, Effective Settings und Wake-Capabilities | CONTRACT FROZEN | SRV-040, CLI-010 | Snapshot-Schema-/Mirror-Test |
| WIRE-08 | Client übernimmt nur Snapshot derselben Session mit nicht kleinerer `stateVersion` | CONTRACT FROZEN | CLI-010 | Stale-Snapshot-Test |
| WIRE-09 | Additive unbekannte Felder derselben v2 werden ignoriert; unbekannte Nachrichtentypen erzeugen keine erfundene Zustandsänderung | CONTRACT FROZEN | SRV-040, CLI-010 | Forward-Field-/Unknown-Type-Test |
| WIRE-10 | Handshake-/Transportfehler verwenden die festgelegten Close-Codes 4400/4406/4408/4409 beziehungsweise 1011 | CONTRACT FROZEN | SRV-040, CLI-010 | Close-Code-Test |
| WIRE-11 | Server, Client und Integration verwenden dieselben maschinenlesbaren Positiv-/Negativvektoren | CONTRACT FROZEN | SRV-040, CLI-010, INT-010 | Vektorparität in beiden Suites |
| WIRE-12 | Jede Activation besitzt neben `activationId` eine sessionsweit steigende `activationSequence`; Pending-Snapshots sind danach sortiert | CONTRACT FROZEN | SRV-010, SRV-040, CLI-010 | Multi-Activation-Snapshot-Test |
| WIRE-13 | `activation.input_closed.causedByCommandId` korreliert Finish/Cancel; nicht commandbasierte Abschlüsse tragen `null` | CONTRACT FROZEN | SRV-030, SRV-040, CLI-010 | Command-/Event-Korrelationstest |

### Wake-Word-Einzelverträge

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| WW-09 | Alle im Build enthaltenen und nicht global deaktivierten Wake Words sind über einen versionierten Katalog abfragbar | BESTÄTIGT | SRV-060, CLI-030 | Catalog-API-/Disable-Test |
| WW-10 | Aliasnormalisierung verwendet Unicode-Trim und case-insensitive Vergleich; nur explizite Aliase dürfen etwa „Hey“ weglassen | CONTRACT FROZEN | SRV-060 | Alias-/Collision-Test |
| WW-11 | Unbekannte, deaktivierte oder nicht ladbare Wake-Word-ID lehnt die gesamte Sessionauswahl ohne Teilfallback ab | BESTÄTIGT | SRV-060 | Atomic-Admission-Test |
| WW-12 | Nur die für eine angenommene Session gewählten Wake-Word-Modelle werden initialisiert | BESTÄTIGT | SRV-060 | Resource-/Initialization-Test |
| WW-13 | `wakeword.detected` enthält kanonische ID, Score und die dadurch akzeptierte `activationId`; Rohscores bleiben Diagnose | CONTRACT FROZEN | SRV-060, SRV-040 | Event-/No-Raw-Domain-Test |
| WW-14 | Sensitivity ist gemeinsam für alle Session-Wake-Words konfigurierbar; zusätzliche Mehrfach-Chunk-Regel nur nach Messdaten | BESTÄTIGT / KALIBRIERUNG | SRV-050, SRV-060 | Score-Trace-/Config-Test |
| WW-15 | Wake-Word-Cooldown und Pre-Roll sind serverautoritativ konfigurierbar; 0 ms Pre-Roll ist zulässig | BESTÄTIGT | SRV-060, CLI-030 | Schema-/Boundary-Test |
| WW-16 | Nach dem ersten akzeptierten Treffer bleibt Detection bis zum Eingabeschluss gelatcht und erzeugt kein Mehrfachereignis | BESTÄTIGT | SRV-060 | One-Utterance-/Latch-Test |
| WW-17 | Leere Wake-Auswahl ist nur bei `trigger.wakeWord=false` zulässig; Suppression ersetzt keine Sessionauswahl | CONTRACT FROZEN | SRV-040, SRV-060, CLI-030 | Handshake-/UI-Negativtest |
| WW-18 | Konkreter Cooldown-Default/-Bereich wird aus Score-/Audio-Evidence festgelegt, nicht vom Agenten erfunden | KALIBRIERUNG OFFEN | SRV-000, SRV-060 | Calibration-Report plus Config-Test |
| WW-19 | Konkreter Pre-Roll-Default/-Bereich wird anhand des Wake-/Sprachgrenztests festgelegt; 0 ms bleibt zulässig | KALIBRIERUNG OFFEN | SRV-000, SRV-060 | Audio-Grenzreport plus Config-Test |

### Settings, Authentifizierung und Anwendung

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| SET-05 | Jede serververwaltete Einstellung publiziert Scope, Auth, Typ, Constraints, Default, Requested, Effective, Apply-Policy und Revision | CONTRACT FROZEN | SRV-050, CLI-030 | Metadata-Schema-Test |
| SET-06 | Sessionwerte dürfen während der Session geändert werden; Server validiert und bestätigt allein den gültigen Effective Value | BESTÄTIGT | SRV-050, CLI-030 | Patch-/Validation-E2E |
| SET-07 | Eine laufende Activation behält ihren bestätigten `effectiveSettings`-Snapshot unverändert | BESTÄTIGT | SRV-010, SRV-050, CLI-030 | Mid-Activation-Change-Test |
| SET-08 | Reconnectpflichtige Änderung während Activation bietet: sofort abbrechen, nach Eingabeschluss reconnecten oder manuell später | BESTÄTIGT | CLI-030 | Drei-Wege-Dialog-/Controller-Test |
| SET-09 | Serverweite Änderungen benötigen Admin-Key; öffentlich abfragbare Schemas/Effective Values enthalten keine Secrets | BESTÄTIGT | SRV-050, CLI-030 | Auth-/Redaction-Test |
| SET-10 | Admin-Key kann im Windows Credential Manager angelegt, ersetzt und per UI gelöscht werden | BESTÄTIGT | CLI-030 | Credential-Lifecycle-Test |
| SET-11 | `QSettings` hält nur nicht geheime Metadaten; es gibt keinen Klartext-Fallback für den Admin-Key | BESTÄTIGT | CLI-030 | Registry-/Secret-Negativtest |
| SET-12 | `server_restart` wird nur für technisch unvermeidbare fundamentale Serverwerte verwendet | BESTÄTIGT | SRV-050 | Apply-Policy-Review/Test |
| SET-13a | Server-API stellt v2-Settings-Schema und Serverwerte/-Patch an den eingefrorenen Endpunkten bereit | CONTRACT FROZEN | SRV-050 | HTTP-Settings-Contract-Test |
| SET-13b | Server-API stellt den versionierten Wake-Word-Katalog über `GET /api/v2/wake-words` bereit | CONTRACT FROZEN | SRV-060 | Catalog-HTTP-Contract-Test |

### Gerät, Feedback, Recovery und Verlustschutz

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| DEVICE-01 | Physische Hotkeys, ReSpeaker-Verbindung, Hardware-Mute und Gerätekonfiguration bleiben Clientverantwortung | BESTÄTIGT | CLI-020, CLI-050 | Architektur-/Importgrenzen-Test |
| DEVICE-02 | Server kennt nur den generischen Status `audioAvailable`, nicht ReSpeaker- oder Mute-Details | BESTÄTIGT | SRV-040, CLI-020 | Wire-/Negativfeld-Test |
| DEVICE-03 | `audioAvailable=false` cancelt eine offene Activation, lässt Session und vorhandenes Hintergrundledger bestehen | BESTÄTIGT | SRV-030, CLI-020, INT-010 | Device-Loss-E2E |
| DEVICE-04 | Client versucht Geräte-Reconnect ohne automatisches Ende der Serversession | BESTÄTIGT | CLI-020 | Device-Reconnect-Test |
| DEVICE-05 | Server-/Sessionverlust beendet offene Activation; Reconnect beginnt in neuer Session `idle` ohne Fortsetzung | BESTÄTIGT | SRV-030, CLI-010, INT-010 | Server-Reconnect-E2E |
| FEED-01 | Sämtliche UI-, Tray-, Overlay-, Sound- und LED-Zuordnung bleibt Clientkonfiguration | BESTÄTIGT | CLI-040 | Responsibility-/Config-Test |
| FEED-02 | Server sendet zuverlässige source-neutrale Domain-Events, aus denen der Client Feedback ableitet | BESTÄTIGT | SRV-040, CLI-040 | Manual-/Wake-Paarvergleich |
| FEED-03 | Watchdog-Vorwarnung ist als Event verfügbar und kann clientseitig dargestellt werden | BESTÄTIGT | SRV-030, CLI-040 | Warning-Feedback-E2E |
| SAFE-02 | Kein Queue-Trim oder Recoverypfad darf Audio ohne terminales Ledgerereignis entfernen | CONTRACT FROZEN | SRV-020, SRV-030 | Queue-Pressure-/Fault-Test |
| SAFE-03 | Ohne aktive Anwenderentscheidung wird erfasste Sprache nur bei technisch unvermeidbarem Verlust verworfen | BESTÄTIGT | SRV-020, SRV-030 | Loss-Reason-Audit/Test |

### Cut, Dokumentation und Ausführungsprozess

| ID | Einzelanforderung | Status | AP | Nachweis |
|---|---|---|---|---|
| COMPAT-01 | Desktop-Client und Server vollziehen einen klaren v2-Cut ohne Legacy-Triggeradapter im neuen Runtimepfad | BESTÄTIGT | SRV-070, CLI-050 | Dead-Code-/Handshake-Test |
| COMPAT-02 | Browserclient wird später nachgezogen und blockiert diesen Arbeitsblock nicht | BESTÄTIGT | SRV-070, INT-010 | Scope-/Build-Review |
| COMPAT-03 | Kompatibilitätsmatrix enthält Desktopversion/-commit, Serverversion/-commit und Protokollversion | BESTÄTIGT | INT-010 | getesteter Matrixeintrag |
| COMPAT-04 | Nur ein tatsächlich getestetes und gepushtes Client-/Server-Commitpaar wird als kompatibel freigegeben | EXECUTION FROZEN | INT-010 | GitHub-SHAs plus E2E-Protokoll |
| PROC-01 | `AP-SRV-*` ändert nur Serverprodukt und serverseitige AP-Akte; `AP-CLI-*` nur Clientprodukt und clientseitige AP-Akte | EXECUTION FROZEN | alle SRV/CLI | Diff-/Ownership-Prüfung |
| PROC-02 | Jedes AP archiviert unveränderten Originalprompt, Agentenbericht, Endabnahme und notwendige Evidence im eigenen Ordner | EXECUTION FROZEN | alle APs | AP-Aktenprüfung |
| PROC-03 | Der Implementierungsagent aktualisiert kanonische Produktdokumentation im selben AP | EXECUTION FROZEN | alle SRV/CLI | Code-/Dokumentabgleich |
| PROC-04 | Agent erstellt lokalen AP-Commit; bei Befund wird derselbe ungepushte Commit amended | EXECUTION FROZEN | alle SRV/CLI | Git-History-/Gate-Prüfung |
| PROC-05 | Endabnahme ergänzt `ABNAHME.md` im selben Commit und pusht erst nach vollständigem PASS auf GitHub | EXECUTION FROZEN | alle SRV/CLI | Commit-/Remote-SHA-Prüfung |
| PROC-06 | Folge-APs starten ausschließlich auf der gepushten, als Dependency vermerkten Vorgänger-SHA | EXECUTION FROZEN | alle APs | Prompt-Metadaten-/SHA-Prüfung |
| PROC-07 | Maximal ein GPT-Implementierungsagent und ein Claude-Code-CLI-Lauf arbeiten parallel; nie zwei desselben Anbieters | EXECUTION FROZEN | alle APs | Run-/Zeitachsenprüfung |

## Root-Korrektur der AP-Zuordnung (2026-08-27, AP-SRV-050 Root PASS)

Mit der Root-Abnahme von `AP-SRV-050` ist die Paketownership rund um den
Wake-Word-Katalog verbindlich korrigiert. Die fachliche Semantik der
Anforderungen bleibt unverändert; nur die AP-Zuordnung wurde berichtigt.

- `SET-13` ist aufgeteilt: `SET-13a` (v2-Settings-Schema, Serverwerte/-Patch,
  `AP-SRV-050`) und `SET-13b` (versionierter Wake-Word-Katalog über
  `GET /api/v2/wake-words`, `AP-SRV-060`). Dadurch steigt die Zahl eindeutiger
  Anforderungen von 129 auf 130.
- `WW-09` führt `SRV-050` nicht mehr; serverseitig ist der Katalog eindeutig
  `SRV-060`.
- `WW-15` führt `SRV-050` nicht mehr, weil `AP-SRV-050` bewusst keine nicht
  eingefrorenen Cooldown-/Pre-Roll-Keys erfunden hat.
- `WW-18` und `WW-19` führen `SRV-050` nicht mehr; die Kalibrierung bleibt bei
  `SRV-000` und `SRV-060`.

Die übrigen AP050-Zuordnungen bleiben unverändert bestehen, insbesondere
`SET-01/02/04/05/06/07/09/12`, `A-03`, `TIME-01/02` sowie `WW-03` und `WW-14`
als Sensitivity-/Settingsfundament.

## Überholte Traceability-Aussagen

Die frühere Zeile `Hotkey Active = Finish` ist kein gültiges universelles
Soll mehr. Sie wird ersetzt durch HK-01 und HK-02. Ebenso darf ein Test, der
kumulative Extension-Sekunden erwartet, nicht als Nachweis des neuen
Zielbilds gelten.

## Pflege

- Während der Umsetzung AP- und Nachweiszuordnung präzisieren, nicht
  rückwirkend fachliche Semantik aus Tests ableiten.
- Ein Gate darf später nur schließen, wenn die zugehörigen automatischen und
  gegebenenfalls manuellen Nachweise tatsächlich vorliegen.
