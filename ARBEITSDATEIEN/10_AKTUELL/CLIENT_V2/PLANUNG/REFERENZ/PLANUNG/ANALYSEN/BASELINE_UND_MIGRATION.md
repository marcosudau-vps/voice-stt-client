# Baselines, Client-Ist und Migrationskarte

**Aktuelle Branchführung (Revision 9):** Neue Clientpakete laufen auf `feat/client-v2`, ausgehend von 8bab1b3 mit demselben Produktbaum wie a80a6b1. Der erste neue Commit enthält nur Unterlagen; AP-CV2-000 bleibt offen. Historische Distributed-/Featurebezeichnungen unten benennen die analysierten Ausgangsquellen. Kumulative Kandidaten liegen künftig auf untergeordneten Paketbranches, Code und Planpflege gehen als ein Paketaggregat gemeinsam ein. [Verbindliche Branchreferenz](../../GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

## 1. Reproduzierbare Ausgangslage

Serverbranch remote geprüft am 2026-10-04: `feat/einheitliche-triggerarchitektur-distributed` zeigt auf `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Der zunächst vorhandene lokale Arbeitscheckout zeigte dagegen auf `70c4623`; deshalb wurde die Analyse aus einem `git archive` des ausdrücklich festgelegten Commits durchgeführt. Kein Produktcheckout wurde umgeschaltet oder verändert.

Clientstände:

| Ref / Arbeitsverzeichnis | SHA | Sachliche Rolle |
| --- | --- | --- |
| `origin/main`, V1-Release | `f625904795880ce71acec216e43678f9ec1656d0` | veröffentlichte Paketbasis mit `voice_stt_client`, Builds und 1.147 bestandenen Basistests |
| `origin/feat/einheitliche-triggerarchitektur-distributed` | `a80a6b17b40751740f9c9d2aef9cad32b0470c0c` | echte Trigger-/Command-/Feedbackvorarbeit mit zusätzlichen Tests; Produktmodule noch unter `core/`, `ui/` |
| `origin/feat/einheitliche-triggerarchitektur` | `8bab1b3f4aa070d0756c305908def4d9ebc52582` | kanonischer Paketstand mit identischem vollständigem Baum zu a80a6b1 |
| lokales `voice-stt-client/main` | `ef230f2979409b66fff4d7f444aea3b5c259cc85` | Branch `wip/led-sound-debugfeedback-sicherung`, nicht aktuelles main |
| lokales `workspaces/einheitliche-triggerarchitektur` | `8bab1b3...` plus umfangreiche lokale Änderungen | keine unveränderte Baseline; nicht als Produktquelle dieser Planung verwendet |

**Revidierte Empfehlung:** Feature-Linie fortsetzen (Execution a80a6b1, kanonisch 8bab1b3; gleicher Gitbaum). V1-main f625904 ist die notwendige Release-/Migrationsreferenz. CV2-000 integriert Namespace, Benutzerpfade/CLI, Hotkey-Erfassung und Buildpolish gezielt in die Featurebasis, erhält Triggercode/Assertions und qualifiziert den erst danach entstehenden integrierten Start-SHA. Keine Branchgeschichte umschreiben und keine lokalen Änderungen verlieren. Die ausführliche [Branchbewertung](CLIENT_BRANCH_BEWERTUNG.md) enthält Abwägung und überprüfte Belege.

## 2. Bestehende Komponenten und konkrete Lücken

Die Tabelle beschreibt die f625904-Releaseausgangsstellen und geplanten Zielpfade nach CV2-000. Der heutige Featurestand verwendet core/ui auf Toplevel und besitzt zusätzliche Triggerflags, TriggerAck/Pendingtrigger sowie Serverautoritäts-/Continuous-Stream-Vorarbeit; diese ist ausdrücklich zu erhalten beziehungsweise auf den finalen Vertrag zu migrieren. Siehe [Branchbewertung](CLIENT_BRANCH_BEWERTUNG.md).

| Bereich | Tatsächlicher Ist | Ziel / Paketowner |
| --- | --- | --- |
| `voice_stt_client/core/stt_session.py` | V1: serverseitiges hello, ready, start/stop, Querysession, Domainping; Integersegmentmodell | V2hello ausgehend, Commands/Acks, V2Mirror und Continuous-Audio; CV2-010/020/030/040 |
| `core/controller.py` im Paket | getrennte session.mode-Pfade, lokale Diktierfenster/Timeoutwarnings, Startversuche, bestehende Final-/Injektionspipeline | eine serverautorisierte Activationbedienung; CV2-050/060/100 |
| `core/config.py`, `core/settings_metadata.py`, Paket-`config.yaml` | Sessionmode, lokale Fensterfristen, wake_words als String; verschiedene Hotkeyfelder | versioniertes Triggerprofil, Serverwünsche getrennt, zwei Controlslots plus Wakepause; CV2-050/070/080 |
| `core/audio_capture.py` | bewährte Geräte-/PCM-Capture und Threadgrenze | Format beibehalten, stream lifetime an Session statt Diktat; CV2-040 |
| `core/history.py` | SQLite-UNIQUE(session_id, segment_id), segment_id INTEGER; Historie/Injectionversuche | additive Datenmigration mit Protokoll, UUIDsegment, Activation und Sequence; CV2-060 |
| `core/text_injector.py`, `core/reinsertion.py` | Clipboard/SendInput-Queue und bewusstes Wiedereinfügen | integrieren, keine neue Clipboardtechnologie; CV2-060/100 |
| `core/session_coordinator.py` | Dualsocketgeneration und Bootstrapverarbeitung an V1hello | hello.accepted binden, V2-Logbootstrap; CV2-040/100 |
| `core/event_protocol.py`, `event_stream.py`, `event_cursor_store.py` | zuverlässiger logProtocolVersion=2/sqlite_first-Pfad | Filter-/Instance-/Retentionverhalten prüfen, Tokenherkunft wechseln; CV2-040 |
| `core/event_normalizer.py`, `event_models.py`, `feedback_reducer.py`, `feedback_mapping.py` | normiertes Feedback aus Haupt-/Logstream und lokalen Events | Domain-V2 einzige Sessionzustandsquelle, Sideeffect-Dedup; CV2-090 |
| `core/observability/` | Ingress/Worker/SQLite/Query/Redaction vorhandener Logfoundation | behalten; neue Domain-/Commandkorrelation integrieren, kein Logging-Refactor; CV2-090/100 |
| `ui/hotkeys.py`, `ui/application.py`, `ui/core_bridge.py` | Win32-Registrierung, Qt/async-Brücke, feste Finish-/Cancelfelder | Rollen anhand Mirror, auch Wake-only; Registrierungstransaktion; CV2-050/100 |
| `ui/settings_dialog.py` | lokale/sessionabhängige Einstellungen, noch keine V2server-Revision/Credentialseite | schemaorientierte Session-/Adminseite, Applydialog; CV2-080 |
| `ui/presentation.py`, `ui/feedback.py`, `ui/overlay.py`, `ui/tray.py`, `ui/led_feedback.py` | etablierte Anzeige- und LEFX-Ausgänge | gemeinsame V2phasen; Hintergrundstate darf Vordergrund nicht verdrängen; CV2-090 |
| `core/version.py`, `app.py`, `pyproject.toml`, `scripts/build.py`, `.spec`, CI | releasefähiger Paketnamensraum und frozen smoke | erhalten und V2ressourcen/Kompatibilität qualifizieren; CV2-110 |

Die Kürzung `core/...`/`ui/...` innerhalb dieser Tabelle meint immer `voice_stt_client/core/...` bzw. `voice_stt_client/ui/...`. Neue Module werden ebenfalls im Paket erzeugt; Top-Level-`core`/`ui` werden nicht wieder eingeführt.

## 3. Geplante neue Schnittstellen

| Schnittstelle / vorgeschlagener Ort | Auftrag |
| --- | --- |
| `core/protocol_v2.py` oder kleines gleichnamiges Paket | Wiredatentypen, Decoder/Encoder, Result-/Eventvokabular; CV2-010 |
| `core/activation_mirror.py` | reiner Reducer mit Snapshot-/Resyncregeln; CV2-030 |
| `core/command_tracker.py` | unveränderte Retrypayloads, korrelierte Pendingabwicklung, Session-/Generationbinding; interne Struktur frei; CV2-020 |
| `core/settings_service.py` | HTTPschema/Katalog/Admin und gewünschte Sessionwerte; CV2-070 |
| `core/credential_store.py` | Windows Credential Manager, injected Fakebackend; CV2-080 |
| `core/final_results.py` | stabil zugeordnete Finaldaten und genau einmaliger Ergebniskonsum; konkrete Klasse frei; CV2-060 |

Die vorhandene Triggerkorrelation wird in diese V2-Dienste migriert; ihre alte Wire-/Capabilitylogik bleibt nicht parallel aktiv. Diese Modulnamen sind konkrete Planungsvorschläge. Ein Paket darf gleichwertige kleine Strukturen wählen, muss dann Migrationskarte, Traceability und Folgepaketübergabe konsistent anpassen. Keine zweite State-Machine oder Duplicate-Wireimplementation erzeugen.

## 4. Persistierte Datenmigration

**Konfiguration:** explizite Schemaversion (Name `config_schema_version` ist ein Vorschlag); Backup und deterministische Migration vor Schreiben. `session.mode=hotkey` → manual=true/wakeWord=false, `wake_word` → manual=false/wakeWord=true. Explizite vorhandene Triggerflags im tatsächlich verwendeten Featureprofil haben Vorrang; widersprüchliche oder triggerlose persistierte Profile verlangen einen sichtbaren Reparaturschritt. Ein Nutzerprofil wird nie durch Defaults unbemerkt überschrieben.

Wake-Stringliste über realen Katalog in kanonische IDs auflösen. Offline: gewünschte Rohwerte im Migrationsbericht erhalten, Admission gesperrt, bis IDs eindeutig geklärt sind. Lokale Diktierfristen in Sekunden exakt nach ms umrechnen: initial_speech_timeout → activation.initialSpeechTimeoutMs; followup_timeout → activation.followupTimeoutMs. `extension_seconds` besitzt keine neue Entsprechung und wird mit erklärtem nicht-kumulativem Refresh im Migrationsbericht stillgelegt. Lokale timeout_warning_seconds wird nicht in den serverseitigen Watchdogwarningwert umgedeutet.

**Hotkeys:** toggle_key → primary.key; separate bestehende Finish/Cancelcontrols nach Benutzerpräferenz in secondary und optional erhaltene dedizierte UIaktion überführen. Kollisionen/mehrere alte aktive Controls sichtbar auflösen. Overlaytoggle/reinsert bleiben getrennte Utilityaktionen. Globale Autorisierung darf nicht allein an manual hängen.

**Historie:** Sicherung außerhalb Repository, transaktionale Tabellenmigration mit idempotenter Schemaversion. Bestehende V1session/Integersegment-Einträge unverändert lesbar; neue V2UUIDs als TEXT, Protokollfeld und nullable neue Referenzfelder. Alten Einträgen keine erfundene Activation zuweisen. Unique(session, segment, ggf. protocol) und Injectionattempt-FKs erhalten. Migration bei Fehler rollback; Wiederholung nach Fehler oder Neustart erzeugt keine doppelten Einträge.

**Runtime:** Suppression, clientRunId, Pendingcommands, Sessiontokens und ReSpeaker-Verfügbarkeitszustände werden nicht als Startzustand persistiert. Credentials ausschließlich Credential Manager. UI-/Sound-/LEDprofile und bestehende Clipboard-/Autostart-/Fensterpräferenzen erhalten.

## 5. Zu ersetzende Testannahmen

Die bestehende vollständige Suite bleibt das Regressionsinstrument. V1hello/ready/start/stop-, timeline-, integersegment-, session.mode- und lokale Timererwartungen werden in den betroffenen Tests gezielt durch V2verträge ersetzt; sie dürfen nicht pauschal entfernt oder als skipped ausgeblendet werden. Für jede entfallende fachliche Assertion nennt der AP-Report die neue Requirement-ID und den neuen Test. Utility-, Clipboard-, Logstore-, Single-Instance- und Buildtests bleiben erhalten.

Testdoubles müssen das echte Hello, Event-vor-Ack, stale Acks, eventlose Commands, terminal-vor-close, overlap, Interimherkunft und Snapshot-ohne-Texte abbilden. Eine FakeSTTSession mit bloßem `start_streaming()`-Erfolg beweist keinen V2-Lifecycle.

## 6. Baselinebeleg

Immutable Clientexport f625904: vollständiger `unittest discover` mit Python 3.12.10, QT_QPA_PLATFORM=offscreen, **1.147 Tests, OK**. Dies belegt den vorhandenen V1stand. Zusätzlich wurde a80a6b1 mit **1.192 Tests OK, 84,649 s** vollständig geprüft. Keine dieser zwei Baselines ist bereits die noch herzustellende integrierte V2-Startbasis. V2funktion, neue Datenmigration, echte Hardware und neuer frozen Build wurden durch diese Planung noch nicht implementiert oder abgenommen.
