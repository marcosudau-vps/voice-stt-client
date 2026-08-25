# Finaler Implementierungsplan – Einheitliche Triggerarchitektur

**Status:** READY FOR IMPLEMENTATION

**Stand:** 2026-08-25

**Normative Grundlagen:**

1. `ZIELBILD.md`
2. `TECHNISCHER_CONTRACT_FREEZE.md`
3. `PROTOKOLL_V2_WIRE_SCHEMA.md` samt `VERTRAGSVEKTOREN/`
4. `ENTSCHEIDUNGEN_UND_OFFENE_PUNKTE.md`
5. belegte Ist-Analysen unter `ANALYSEN/`

Der operative Parallel-, Modell- und Abnahmeablauf steht ergänzend in
`AUSFUEHRUNGS_WORKFLOW.md`.

## 1. Ziel und Abgrenzung

Desktop-Client und Server werden auf einen gemeinsamen serverautoritativen
Activation-Lifecycle mit Protokollversion 2 umgestellt. Manual und Wake Word
sind nur Triggerquellen. Der Vordergrund wird nach sicherem Eingabeschluss
wieder bedienbar, während Final-Ergebnisse älterer Activations korrekt
zugeordnet im Hintergrund nachgereicht werden.

Der Arbeitsblock umfasst:

- Server-State-Machine, Segmentledger, Timer, Commands, Events und Snapshot;
- Wake-Word-Katalog, selected-only Initialisierung, Detection-Latch und
  Audioübergang;
- Settings-Contract für die Triggerdomäne und erweiterbare Adminseite;
- Desktop-Client-Mirror, kontinuierlichen Stream, Hotkeys, Suppression,
  Geräteverfügbarkeit, Settings und Feedback;
- klaren Protokoll-Cut, Kompatibilitätsmatrix und Gesamtvalidierung.

Nicht enthalten:

- Nachzug des Browserclients;
- Vollmigration fachfremder Einstellungsdomänen;
- neue Feedbackhardware oder Änderung des LED-Controller-Protokolls;
- Namespace-Ideen.

## 2. Umsetzungsregeln

- Jedes AP besitzt einen kleinen, prüfbaren Endzustand und genau einen finalen
  Commit im betroffenen Produktrepository. Der Agent erstellt ihn lokal; die
  Endabnahme lässt Befunde vor dem Push per Amend korrigieren, ergänzt ihre
  Abnahme im selben Commit und pusht erst nach PASS.
- `AP-SRV-*` ändert ausschließlich das Server-Repository.
- `AP-CLI-*` ändert ausschließlich das Desktop-Client-Repository.
- `AP-INT-*` führt nur koordinierte Integration/Abnahme und gemeinsame
  Dokumentation aus, aber ändert keinen Produktcode. Ein Integrationsbefund
  wird über ein neues, eindeutig als Server oder Client eingeordnetes
  Korrektur-AP behoben.
- Server und Client dürfen zwischen APs vorübergehend nur auf dem
  Feature-Branch inkompatibel sein; jeder solche Zwischenstand wird im
  AP-Report genannt.
- Kein AP schließt mit roten Tests, ungeklärten Terminalverlusten oder
  verschwiegenen Flakes.
- Nach jedem AP laufen die fokussierten Tests und die vollständige Suite jedes
  geänderten Repositorys. Fehler werden innerhalb desselben APs behoben.
- Vor einem Commit werden ausschließlich AP-eigene Änderungen gestagt.
- Originalprompt, Agentenbericht, Endabnahme und notwendige Evidence liegen im
  repositorylokalen AP-Ordner und sind Bestandteil desselben AP-Commits.
- Observability-Felder (`sessionId`, `activationId`, `segmentId`, `commandId`,
  `eventId`) werden mit der jeweiligen Funktion umgesetzt, nicht nachträglich
  in einem Parallelpfad ergänzt.
- Produktdokumentation, repositoryeigene Fortschritts-/Übergabedokumente und
  der strukturierte AP-Bericht werden im selben AP durch den ausführenden
  Agenten aktualisiert. Dokumentation ist Teil der Akzeptanz und kein späteres
  Sammelpaket.
- Normativer Contract, zentrale Gate-Status, Traceability und freigegebene
  Client-/Server-Commitpaare bleiben Eigentum der Endabnahme. Agents dürfen
  diese Unterlagen nicht eigenmächtig umdeuten.

## 3. Arbeitspaketübersicht

| AP | Ziel | Repository | Abhängigkeit |
|---|---|---|---|
| AP-SRV-000 | Serverbaseline und ersetzte Server-Solltests | Server | – |
| AP-SRV-010 | Domainmodell und Vordergrund-State-Machine | Server | SRV-000 |
| AP-SRV-020 | Segmentledger, Hintergrund-Drain und Ergebnisordnung | Server | SRV-010 |
| AP-SRV-030 | Commands, Timer, Watchdog und Recovery | Server | SRV-010, SRV-020 |
| AP-SRV-040 | Protokoll v2, Handshake, Events und Snapshot | Server | SRV-010–030 |
| AP-SRV-050 | Settings-Control-Plane und Servermetadaten | Server | SRV-040 |
| AP-SRV-060 | Wake-Word-Katalog, Detection und Audiogrenze | Server | SRV-030, SRV-050 |
| AP-SRV-070 | Server-Legacyabbau und Protokollgrenze | Server | SRV-060 |
| AP-CLI-000 | Clientbaseline und ersetzte Client-Solltests | Client | – |
| AP-CLI-010 | Transport, ActivationMirror und Continuous Stream | Client | SRV-040, CLI-000 |
| AP-CLI-020 | Hotkeys, Suppression und Audioverfügbarkeit | Client | SRV-060, CLI-010 |
| AP-CLI-030 | Settings-UI, Credential Manager und Apply-Dialog | Client | SRV-050, CLI-010 |
| AP-CLI-040 | Source-neutrales Feedback und Hintergrundresultate | Client | CLI-010–030 |
| AP-CLI-050 | Client-Legacyabbau, Protokollgrenze und Build | Client | CLI-040 |
| AP-INT-010 | Koordinierter v2-Vertragstest | kein Produktcode | SRV-070, CLI-050 |
| AP-INT-020 | Gesamt-, Last- und Hardwareabnahme | kein Produktcode | INT-010 |

## 4. Arbeitspakete

### AP-SRV-000 – Serverbaseline und Charakterisierung

**Ziel:** Der aktuelle Server-Ist-Stand ist reproduzierbar, und Servertests mit
bewusst überholtem Soll werden vor Produktänderungen identifiziert.

**Scope:**

- vollständige Server-Suite als Baseline ausführen;
- bestehende Servertests zu Source-Merge, kumulativer Extension,
  blockierendem `finalizing` und Legacy-Modus inventarisieren;
- vorhandenen Mehrsegment-, Early-Final-, Queue- und Eventablauf mit
  deterministischen Charakterisierungstests sichern;
- Score-/Audio-Evidence-Harness für Wake-Word-Kalibrierung vorbereiten.

**Akzeptanzkriterien:**

- Baseline-Ergebnisse und bekannte Flakes sind dokumentiert.
- Jeder zu ersetzende Alt-Solltest ist dem neuen Contractabschnitt zugeordnet.
- Noch kein Produktverhalten wurde verändert.

**Validierung:**

- Server: `python -m pytest`
- `git diff --check` im Server-Repository

### AP-CLI-000 – Clientbaseline und Charakterisierung

**Ziel:** Der aktuelle Desktop-Client-Ist-Stand ist reproduzierbar, und
Clienttests mit überholtem Trigger-Soll sind vor Produktänderungen markiert.

**Scope:**

- vollständige Client-Suite als Baseline ausführen;
- Tests zu lokalem Diktat-/Follow-up-Lifecycle, `session.mode`, kumulativer
  Extension, Streamstart pro Activation und Source-Merge inventarisieren;
- Fake-Session-/Feedback-/Hotkey-Testhilfen gegen den v2-Contract abgrenzen.

**Akzeptanzkriterien:**

- Baseline-Ergebnis und bekannte Clientflakes sind dokumentiert.
- Jeder zu ersetzende Clienttest ist einem Contractabschnitt zugeordnet.
- Noch kein Produktverhalten wurde verändert.

**Validierung:**

- Client: `python -m pytest`
- `git diff --check` im Client-Repository

### AP-SRV-010 – Server-Domainmodell und Vordergrund-State-Machine

**Ziel:** Der Server besitzt genau einen triggerrelevanten Vordergrundslot mit
den fünf Contractphasen; Hintergrundverarbeitung ist kein Teil dieses Slots.

**Scope:**

- `ActivationController` auf `idle`, `waiting_first_speech`,
  `segment_active`, `followup_wait`, `closing_input` umbauen;
- Source-Merge und neue Activation während eines offenen Eingabefensters
  entfernen;
- Activation-Settings-Snapshot und stabile IDs einführen;
- Gate- und Recorderübergänge an die State Machine binden;
- alte `finalizing`-Triggerautorität entfernen.

**Akzeptanzkriterien:**

- First Trigger wins bei parallelem Manual/Wake-Race deterministisch.
- Kein zweiter Trigger ändert Quelle oder ID der offenen Activation.
- Follow-up kann mehrere serielle Segmente derselben Activation öffnen.
- `idle` kann zusammen mit älteren drainenden Activations bestehen.
- Jede nichtterminale Vordergrundphase besitzt Exit und Recovery-Timeout.

**Validierung:**

- Unit-Tests aller Übergänge und ungültigen Commands;
- Race-Tests mit wiederholten parallelen Triggern;
- vollständige Server-Suite.

### AP-SRV-020 – Segmentledger und Hintergrund-Drain

**Ziel:** Finaljobs bleiben unabhängig vom aktuellen Vordergrund eindeutig
zugeordnet und liefern vollständige, geordnete Terminals.

**Scope:**

- unveränderlichen Jobkontext mit Activation-/Segment-ID, Sequence und
  Settings-Snapshot einführen;
- Pending-Activation-Registry statt Korrelation über „current activation“;
- genau ein Segmentterminal für completed/discarded/cancelled/failed;
- Reorder-Buffer für Veröffentlichung je Session;
- Queue-Trim, leere Finals und Workerfehler in das Ledger integrieren;
- Activationterminal nach vollständigem Segmentledger erzeugen.

**Akzeptanzkriterien:**

- Alte Finalresultate behalten ihre ID, obwohl eine neue Activation läuft.
- Resultate werden in `segmentSequence`-Reihenfolge publiziert.
- Fehler/Discard lösen die Sequenzstelle auf.
- `acceptedSegmentCount == terminalSegmentCount` gilt für reguläre, Cancel-,
  Queue-, Worker- und Session-Close-Pfade.
- Kein Ledgerobjekt bleibt nach Recovery unbegrenzt pending.

**Validierung:**

- Out-of-order-Fake-Inferenztests;
- Multi-Activation-/Multi-Segment-E2E;
- Queue-Overflow- und Worker-Exception-Tests;
- vollständige Server-Suite.

### AP-SRV-030 – Commands, Timer, Watchdog und Recovery

**Ziel:** Alle Steueraktionen und Zeitabläufe folgen exakt dem Contract und
sind gegen Replay und stale Callbacks gehärtet.

**Scope:**

- `activate|refresh|finish|cancel` samt Phase-/Activation-ID-Validierung;
- Command-Replaycache und Payload-Konflikterkennung;
- Follow-up-Reset ohne `extensionSeconds`/`pending_extension`;
- Segment-Watchdog 600/180/30 Sekunden und Warning-Event;
- monotone Deadlines, `timerRevision` und stale Guards;
- `closing_input`-Recovery sowie generisches `audioAvailable=false`;
- Finish-/Cancel-Events und Verwerfungsgrenze.

**Akzeptanzkriterien:**

- Dreifaches Refresh kumuliert keine Zeit.
- Frühes Watchdog-Refresh verkürzt die Initialdeadline nicht.
- Watchdog-Ende verarbeitet Audio und öffnet kein Follow-up.
- Derselbe `commandId` wirkt genau einmal; abweichender Replaypayload scheitert.
- Stale Timer/Commands verändern keine neuere Activation.
- Lockfreigabe wartet auf sicheren Eingabeschluss, nicht auf Final-Inferenz.

**Validierung:**

- Fake-Clock-Tests aller Deadlines und Warnungen;
- Finish-/Cancel-Phasenmatrix und Command-Replaytests;
- Fault-Tests für Recorder-/Gate-Fehler;
- vollständige Server-Suite.

### AP-SRV-040 – Protokoll v2, Handshake, Events und Snapshot

**Ziel:** Der Contract ist über einen versionierten, resynchronisierbaren
Wire-Pfad vollständig nutzbar.

**Scope:**

- Versionsaushandlung und frühe Inkompatibilitätsablehnung;
- v2-Commands/Acks und Domain-Events;
- `eventId`, `eventSeq`, `stateVersion`, `settingsRevision`;
- Snapshot aus Vordergrund, Pending-Ledger, Triggern und Effective Settings;
- Eventlücken-/Snapshotrequest-Pfad;
- strukturierte Observability-Korrelation.

**Akzeptanzkriterien:**

- Keine gemeinsame Protokollversion erzeugt keine Session.
- Snapshot rekonstruiert Idle plus Pending-Activations korrekt.
- Verlorenes Event wird per Sequenzlücke erkannt und resynchronisiert.
- Logical Events sind exactly-once; Transportduplikate sind deduplizierbar.
- Alle Contractfelder werden schema- und integrationstestseitig geprüft.

**Validierung:**

- Protocol-/Schema-/Handshake-Tests gegen
  `VERTRAGSVEKTOREN/protocol-v2-vectors.json`;
- Eventverlust-, Replay- und Snapshot-E2E;
- vollständige Server-Suite.

### AP-SRV-050 – Settings-Control-Plane

**Ziel:** Triggerrelevante Session- und Serverwerte besitzen einen
serverautoritativen Metadaten-, Validierungs- und Apply-Vertrag.

**Scope:**

- Settingsschema mit Scope/Auth/Constraints/Default/Requested/Effective/Apply;
- v2-REST-Endpunkte und Session-Patch;
- Activation-Timings einschließlich Watchdog;
- serverweite Defaults und Adminschutz;
- Settingsrevision und unveränderlicher Activation-Snapshot;
- Grundlage für spätere fachfremde Settingsdomänen.

**Akzeptanzkriterien:**

- Ungültige Änderungen werden atomar und maschinenlesbar abgelehnt.
- Laufende Activation ändert ihren Snapshot nicht.
- `next_activation`, `next_session` und `server_restart` sind unterscheidbar.
- Öffentliche Reads benötigen keinen Admin-Key; Server-Patches schon.
- Kein Secret erscheint in Antwort, Log oder Event.

**Validierung:**

- Scope-/Auth-/Validation-/Revisiontests;
- Concurrent-Patch- und stale-Revision-Tests;
- vollständige Server-Suite.

### AP-SRV-060 – Wake-Word-Katalog und Detection

**Ziel:** Wake Words sind als Build-Capability zuverlässig auswählbar und
erzeugen genau ein verbindliches Ereignis pro akzeptierter Äußerung.

**Scope:**

- versionierten Build-Katalog, globale Disableliste und explizite Aliase;
- atomare Sessionadmission und selected-only Modellinitialisierung;
- gemeinsame Sensitivity und Effective Values;
- Latch bis Eingabeschluss, Rohscorediagnose und Eventbündelung;
- Cooldown/Rearm sowie Audio-Pre-Roll/-Grenze;
- Score-/Audio-Charakterisierung; `2 aus 3` nur bei belegtem Bedarf;
- RAM-/Startzeitmessung mit 1, 3 und Maximalzahl ausgewählter Modelle.

**Akzeptanzkriterien:**

- Problematische ID lehnt die ganze Auswahl ohne Fallback ab.
- Alias-Kollision wird erkannt statt heuristisch gewählt.
- Nur ausgewählte Modelle werden initialisiert.
- Eine Äußerung erzeugt genau ein `wakeword.detected` mit kanonischer ID.
- Wake Word fehlt im Nutztext, unmittelbar folgende Sprache bleibt erhalten.
- Ressourcen- und Latenzmesswerte sind dokumentiert.

**Validierung:**

- Katalog-/Alias-/Admission-/Resource-Tests;
- aufgezeichnete positive/negative Audiosamples und Score-Traces;
- Pre-Roll-/Satzanfang-E2E;
- vollständige Server-Suite.

### AP-CLI-010 – Clienttransport, ActivationMirror und Continuous Stream

**Ziel:** Der Desktop-Client spiegelt ausschließlich v2-Serverzustand und
besitzt keinen konkurrierenden lokalen Activation-Lifecycle.

**Scope:**

- v2-Handshake, Commands, Acks, Events, Sequenzprüfung und Snapshot;
- `ActivationMirror` mit `resyncing` statt erfundenem Idle;
- kontinuierlichen Audiostream an die Session binden;
- lokale Dictation-/Follow-up-State-Machine und Mode-Autorität entfernen;
- verspätete Finalresultate nach ID/Sequence behandeln.

**Akzeptanzkriterien:**

- Eine Session startet den Audiostream höchstens einmal.
- Serverzustand ist die einzige Quelle für Bedienphase und Feedbackinput.
- Eventlücke löst Snapshot aus; stale Snapshot/Event wird ignoriert.
- Idle mit älteren Pending-Activations wird korrekt dargestellt.
- Resultate verschiedener Activations werden nicht verwechselt.

**Validierung:**

- Client-Unit-/Transport-/Mirror-Tests;
- Fake-Server-E2E für Replay, Lücke und Reconnect unter Wiederverwendung von
  `VERTRAGSVEKTOREN/protocol-v2-vectors.json`;
- vollständige Client-Suite.

### AP-CLI-020 – Hotkeys, Trigger-Suppression und Gerät

**Ziel:** Lokale Bedienung wird sauber in semantische Commands übersetzt und
übersteht Reconnect gemäß Client-Laufzeitvertrag.

**Scope:**

- zwei Activation-Hotkeys mit konfigurierbaren Active-Aktionen;
- dritten optionalen Wake-Pause-Hotkey;
- Phase-/Activation-ID-sicheren Dispatch;
- getrennte Manual-/Wake-Suppression ohne Pause-all-Wrapper;
- `clientRunId` und atomare Reconnectübergabe;
- ReSpeaker/Mute lokal, generisches `audioAvailable` an Server;
- Geräte-Reconnect ohne Sessionabbruch.

**Akzeptanzkriterien:**

- Control-Hotkeys funktionieren auch bei deaktiviertem Manual-Trigger.
- Keine Belegung erzeugt unbeabsichtigt zwei Commands.
- Suppression übersteht Reconnect, nicht den Programmneustart.
- Null effektive Trigger sind nur laufzeitweit möglich.
- Geräteverlust cancelt die offene Activation, nicht die Session.

**Validierung:**

- Hotkey-Konflikt-/Phasen-/Reconnecttests;
- Device-loss-Fakes und realer ReSpeaker-Smoke;
- vollständige Client-Suite. Serverseitige Vertragsabweichungen werden als
  Befund an ein separates `AP-SRV-*` zurückgegeben.

### AP-CLI-030 – Settings-UI und Credential Manager

**Ziel:** Session- und Servereinstellungen sind verständlich, sicher und gemäß
Apply-Policy änderbar.

**Scope:**

- UI aus serverseitigem Settingsschema und Effective Values;
- eigene gesperrte Servereinstellungsseite;
- Windows Credential Manager mit Anlegen/Ersetzen/Löschen;
- `QSettings` nur für nicht geheime Metadaten;
- Reconnectdialog mit den drei bestätigten Wegen;
- Pending-/Effective-/Fehlerdarstellung;
- Wake-Word-Katalog und Mehrfachauswahl.

**Akzeptanzkriterien:**

- Ohne erfolgreiche Adminprüfung bleiben Serveränderungen gesperrt.
- Key kann gespeichert, ersetzt und über UI gelöscht werden.
- Ohne Credential Store gibt es nur Session-Speicherung und keinen Klartext.
- Eine laufende Activation wird nie ohne bewusste Auswahl abgebrochen.
- Reconnect-/Next-Activation-Wirkung wird korrekt angezeigt.

**Validierung:**

- Credential-Adaptertests mit Fake und Windows-Integrationstest;
- Settings-/Dialog-/Auth-/Reconnect-UI-Tests;
- vollständige Client-Suite. Serverseitige Vertragsabweichungen werden als
  Befund an ein separates `AP-SRV-*` zurückgegeben.

### AP-CLI-040 – Feedback und Hintergrundresultate

**Ziel:** UI, Tray, Overlay, Sound und LED leiten Feedback source-neutral aus
zuverlässigen Domainzuständen ab, ohne die Bedienung durch Draining zu sperren.

**Scope:**

- FeedbackReducer auf v2-Events und Snapshot;
- `ready` trotz Pending-Activations;
- separate nichtblockierende Anzeige für Hintergrundverarbeitung bei Bedarf;
- Watchdogwarnung und Abschlussfeedback;
- Deduplication von Replayevents;
- geordnete Finalresultat-/Textinjektionsübergabe.

**Akzeptanzkriterien:**

- Manual und Wake erzeugen bei gleichem Zustand dasselbe Feedback.
- Draining zeigt niemals fälschlich „Aufnahme blockiert“.
- Eventreplay erzeugt keinen doppelten Sound/LED-Impuls/Text.
- Watchdogwarnung verschwindet bei Refresh oder Abschluss zuverlässig.
- Finaltexte werden in Serverreihenfolge genau einmal an die Injektion gegeben.

**Validierung:**

- Reducer-/Replay-/Pairvergleich-Tests;
- UI-/Tray-/Sound-Fakes und LED-Smoke;
- vollständige Client-Suite.

### AP-SRV-070 – Server-Legacyabbau und Protokollgrenze

**Ziel:** Im Server bleibt nur der neue Runtimepfad aktiv; inkompatible Clients
scheitern vor der Sessionadmission.

**Scope:**

- serverseitige `session.mode`-Autorität, Source-Merge, alte
  Wake-Follow-up-Autorität und v1-Triggeradapter entfernen;
- widersprechende Servertests löschen oder durch v2-Vertragstests ersetzen;
- serverseitige Settingsnamen auf den Activation-Lifecycle migrieren;
- Serverversion/Commit/Protokollbereich im Handshake veröffentlichen.

**Akzeptanzkriterien:**

- AST-/Textprüfung findet im Server keine Runtime-Autorität der entfernten
  Konzepte.
- Protokoll-v1-Clients öffnen keine teilweise Serversession.
- Vollständige Serverfunktion ist über v2 getestet.

**Validierung:**

- Negativ-/Compatibility-/Migrationstests;
- vollständige Server-Suite;
- `git diff --check` und Server-Dead-Code-Prüfung.

### AP-CLI-050 – Client-Legacyabbau, Protokollgrenze und Build

**Ziel:** Im Desktop-Client bleibt nur der v2-Servermirror; alte lokale
Activation-Autorität und Legacy-UI sind entfernt.

**Scope:**

- lokalen Hotkey-Recorder, lokale Follow-up-State-Machine,
  `session.mode`-Runtimeautorität und alte Protokolladapter entfernen;
- widersprechende Clienttests ersetzen;
- Settingsnamen von Hotkey-Diktat auf Activation-Lifecycle migrieren;
- verständliche Inkompatibilitätsanzeige aus v2-Handshakefehlern;
- Desktop-Build und Start-Smoke absichern.

**Akzeptanzkriterien:**

- AST-/Textprüfung findet im Client keine entfernte Runtime-Autorität.
- Ein inkompatibler Server führt zu einer klaren Meldung, nicht zu einer
  teilweise aktiven UI.
- Der Desktop-Client funktioniert ausschließlich über v2 vollständig.
- Das Desktop-Artefakt baut und startet.

**Validierung:**

- vollständige Client-Suite;
- PyInstaller-Build und Start-Smoke;
- `git diff --check` und Client-Dead-Code-Prüfung.

### AP-INT-010 – Koordinierter v2-Vertragstest

**Ziel:** Festgeschriebene Server- und Clientcommits erfüllen gemeinsam den
v2-Contract, ohne in diesem AP Produktcode zu ändern.

**Scope:**

- Server- und Clientcommit in `docs/compatibility.md` eintragen;
- automatisierte Cross-Repository-E2E gegen reale Prozesse ausführen;
- Handshake, Snapshot, Events, Commands, Settings und Reconnect prüfen;
- Befunde eindeutig als Server-, Client- oder Contractbefund klassifizieren.

**Akzeptanzkriterien:**

- Die festgehaltene Commitkombination besteht alle Contract-E2E.
- Kein Produktcode wurde in diesem AP geändert.
- Jeder Fehler verweist auf ein separates `AP-SRV-*` oder `AP-CLI-*`; nach
  dessen Abschluss wird AP-INT-010 vollständig wiederholt.
- Kompatibilitätsmatrix enthält konkrete getestete Versionen und Commits.

**Validierung:**

- vollständige Server- und Client-Suite unverändert gegen die festgehaltenen
  Commits;
- Cross-Repository-v2-E2E einschließlich aller gemeinsamen Positiv- und
  Negativvektoren aus `VERTRAGSVEKTOREN/protocol-v2-vectors.json`;
- `git diff --check` in beiden Repositories.

### AP-INT-020 – Gesamt- und reale Abnahme

**Ziel:** Der koordinierte Endzustand ist unter Normalbetrieb, Races, Fehlern,
Last und realer Hardware belastbar nachgewiesen. Dieses AP ändert keinen
Produktcode.

**Pflichtszenarien:**

- Manual-only, Wake-only, beide und null effektive Trigger zur Laufzeit;
- gleichzeitiger Trigger, mehrere Segmente, Refresh/Finish/Cancel je Phase;
- Idle mit einer und mehreren ausstehenden alten Final-Transkriptionen;
- Out-of-order-Finals, Fehler, Empty Final, Queue-Limit und Workerabbruch;
- Initial-/Follow-up-/Closing-/Watchdogtimer einschließlich stale Races;
- Server-Reconnect, Eventverlust, Geräteverlust, Mute und ReSpeaker-Reconnect;
- mehrere Wake Words, unbekannte/deaktivierte ID, Pause/Restart, Pre-Roll;
- Settings live/next Activation/reconnect/Admin/Credential-Löschung;
- kompatibler und inkompatibler Handshake;
- Client-Build und realer Tray-/Overlay-/Sound-/LED-/Textinjektions-Smoke.

**Akzeptanzkriterien:**

- Alle automatischen Server- und Clienttests bestehen wiederholt.
- Kein angenommener Segmentjob fehlt im Terminalledger.
- Keine Activation bleibt ohne definierten Exit hängen.
- Keine alte ID, kein stale Timer und kein Replay beeinflusst einen neueren
  Zustand.
- Ressourcen- und Latenzwerte liegen innerhalb der vor dem AP dokumentierten
  Abnahmebudgets oder besitzen eine ausdrücklich akzeptierte Abweichung.
- Desktop-Artefakt baut und startet erfolgreich.
- Zielbild, Contract, Compatibility und Betriebsdokumentation entsprechen dem
  tatsächlich abgenommenen Code.
- Jeder Produktcodebefund wird in ein separates Server- oder Client-Korrektur-
  AP überführt; danach wird diese Gesamtprüfung von vorn wiederholt.

**Validierung:**

- Server: `python -m pytest`
- Client: `python -m pytest`
- wiederholte Race-/Timeout-/Fault-Suites;
- Client-Build über die vorhandene PyInstaller-Spec;
- manueller Hardware-/UI-Smoke mit protokollierter Checkliste;
- `git diff --check` in beiden Repositories.

## 5. Kritischer Pfad

```text
AP-SRV-000 → SRV-010 → SRV-020 → SRV-030 → SRV-040
                                              └→ SRV-050 → SRV-060 → SRV-070

AP-CLI-000 ────────────────────────────────→ CLI-010 ────────────────┐
                                              ├→ CLI-030 ───────────┤
                            SRV-060 ─────────→ CLI-020 ──────────────┴→ CLI-040 → CLI-050

SRV-070 + CLI-050 → INT-010 → INT-020
```

Client-Produktarbeit beginnt erst gegen den getesteten Server-Wire-Contract
aus AP-SRV-040. Danach können AP-SRV-050 und AP-CLI-010 parallel laufen,
anschließend AP-SRV-060 und AP-CLI-030 sowie danach AP-SRV-070 und AP-CLI-020.
Die vollständigen Ausführungswellen und Modellempfehlungen stehen in
`AUSFUEHRUNGS_WORKFLOW.md`. Kein Server-AP besitzt Clientproduktdateien und
kein Client-AP besitzt Serverdateien.

## 6. Startempfehlung

Nach separater Sicherung des Planungsstands startet Welle 1 parallel mit
AP-SRV-000 auf der GPT-Lane und AP-CLI-000 auf der Claude-Sonnet-Lane. Die
konkreten Aufträge werden unmittelbar vorher aus
`../ARBEITSPAKETE/AUFTRAGSVORLAGE.md` mit aktuellen HEAD-SHAs erzeugt. Es gibt
keinen Grund für eine weitere breite Architektur- oder Bedienrunde; neue
Rückfragen werden nur eröffnet, wenn ein AP eine echte, bisher nicht
entschiedene Nutzerwirkung aufdeckt.
