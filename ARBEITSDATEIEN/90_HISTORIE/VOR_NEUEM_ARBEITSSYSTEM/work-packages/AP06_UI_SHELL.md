# AP06 – Windows UI-Shell, Betriebsmodi und Einstellungen

> **Status:** Scope implementiert und mit 264 Tests verifiziert;
> Moduswechsel-Fix lokal und produktiv bestätigt, gesprochener
> Wake-Word-Bediennachweis offen  
> **Stand:** 28. Juli 2026  
> **Vorgänger:** AP05 Fehlerverhalten und stille Selbstheilung  
> **Nachfolger:** AP07 Feedback- und Eventsystem; danach AP08 Härtung und Polish

> **Nummerierungsnachtrag vom 2. August 2026:** ReSpeaker-LED bleibt im neuen
> AP07. Historische AP07-Verweise dieses abgeschlossenen Vertrags auf
> Hot-Plug, Sleep/Wake, DPI, Autostart, Packaging und allgemeine Langzeithärtung
> bezeichnen nun AP08.

## 1. Ziel

AP06 setzt eine dauerhaft im Hintergrund laufende Windows-Bedienoberfläche auf
den vorhandenen UI-neutralen `STTController`. Die Anwendung erhält Tray,
passives Overlay, native globale Hotkeys, eine thread-sichere Qt-/asyncio-
Brücke, Verlauf/Reinsertion und einen Single-Instance-Guard.

Der technische Erststand und der nachträglich abgestimmte Folgeumfang sind
implementiert. Der Folgeumfang ergänzt in demselben Paket:

- Hotkey- und Wake-Word-Betrieb auf Basis des produktiven sessionlokalen
  Serververtrags,
- den Einstellungsdialog,
- eine deklarative Metadatenebene über der weiterhin typisierten
  `AppConfig`,
- eine getrennte Registrierung konfigurierbarer Benutzeraktionen und
  globaler Hotkeys,
- ein konfigurierbares Hotkey-Diktatfenster mit serverseitiger VAD-
  Segmentierung,
- Verlaufspflege sowie konfigurierbares visuelles und akustisches Feedback.

Der vorhandene AP1–AP5-Core bleibt die fachliche Grundlage. Änderungen dort
sind nur zulässig, soweit die Integration der neuen AP06-Funktionen sie
nachweislich erfordert. Die UI implementiert weder WebSocket-, Audio-,
History-, Injection-, VAD- noch Reconnectlogik ein zweites Mal.

### 1.1 Kurzüberblick des konsolidierten Paketstands

| Bereich | Stand |
| --- | --- |
| Tray, Overlay, Core-Brücke, native Hotkeys, Single Instance | umgesetzt; aktueller Gesamtstand 264 Tests |
| Overlay-Signalfehler | behoben und regressionsgetestet |
| Session-Wake-Word-Contract | serverseitig produktiv und aus Clientsicht live verifiziert |
| Clientseitige Betriebsmoduswahl | implementiert; persistenter Maintainer, atomare Streamaktivierung und bestätigter Rollback verifiziert |
| Einstellungsdialog und Metadatenebene | implementiert und automatisiert geprüft |
| konfigurierbares Hotkey-Diktatfenster | implementiert; manuelle Prüfungen 1 bis 4 erfolgreich |
| Soundfeedback und erweiterter Overlay-Indikator | implementiert; verbindliches Grün-/Blau-/Gelb-/Rot-Konzept geprüft |
| ReSpeaker-LED, Hot-Plug, Sleep/Wake, DPI, Autostart, Packaging | AP07 beziehungsweise später |

Die frühere Sammlung einzelner Entscheidungsfragen ist kein zusätzlicher
Vertrag mehr. Ihre noch relevanten Ergebnisse sind in diesem Dokument
materialisiert; überholte Varianten werden nicht parallel weitergeführt.

## 2. Verbindliche Quellen

Vor Codeänderungen sind gemäß `AGENTS.md` zu lesen:

1. die sechs kanonischen Einstiegsdateien,
2. dieser Paketvertrag,
3. `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`,
4. `server-docs-for-client-development/README.md`,
5. `02-websocket-protokoll.md`,
6. `03-server-events-kurzreferenz.md`,
7. die einschlägigen Abschnitte aus
   `04-server-events-katalog-und-chronologie.md`,
8. `05-client-zustandsmodell.md`,
9. `09-betriebsmodi-und-serverkonfiguration.md`,
10. `session-wakeword-erweiterung.md`,
11. `app.py`, `config.yaml`, `requirements.txt`, `core/config.py`,
12. die öffentlichen Zustands-, Befehls-, Text- und Reinsertion-Schnittstellen
   aus `core/controller.py`, `core/history.py` und `core/reinsertion.py`,
13. alle tatsächlich geänderten UI-Module, ihre direkten Abhängigkeiten und
    zugehörigen Tests.

Der zurückgezogene ADR-001 ist keine aktive Quelle und wird nicht als
Pflichtlektüre verwendet. Der neue enge Sessionvertrag ersetzt die darin
verworfene breite Profilidee, ohne einen Admin-Service einzuführen.

## 3. Scope

### 3.1 Bereits umgesetzter technischer Erststand

- `QApplication` im Main Thread,
- `QSystemTrayIcon` mit persistentem Status, Bedienaktionen und Verlauf,
- passives, nicht fokussierbares Overlay für Realtime-/Finaltext und kurze
  unmittelbar benutzerrelevante Hinweise,
- asyncio-Core in genau einem separaten Thread,
- thread-sichere Core→Qt-Signale,
- thread-sichere Qt→Core-Befehle,
- native globale Windows-Hotkeys über `RegisterHotKey`,
- Single-Instance-Guard über einen benannten Win32-Mutex,
- grafische Reinsertion des letzten oder eines im Tray ausgewählten Eintrags,
- GUI-Start als regulärer Startpfad und erhaltener `--headless`-Diagnosepfad,
- Konfigurationsvalidierung für die bisherigen AP06-Werte,
- automatisierte Tests und sichere Windows-/Qt-Smoke-Tests.

### 3.2 Verbindlicher AP06-Folgeumfang

- Betriebsmodus `hotkey` mit `wakeWordEnabled=false`,
- Betriebsmodus `wake_word` mit `wakeWordEnabled=true`,
- Auswahl der vom Server veröffentlichten logischen Wake-Word-ID und der
  unterstützten sitzungslokalen Tuningwerte,
- verbindliche Prüfung der effektiven Auswahl aus
  `hello.sessionConfig` und `ready.sessionConfig`,
- kontrollierter Reconnect bei Modus- oder Sessionprofiländerung,
- Hotkey-Diktatfenster mit konfigurierbarem Initial-, Follow-up- und
  Verlängerungszeitraum,
- Einstellungsdialog mit deklarativ erzeugten Standardfeldern,
- typisierte Konfiguration als einzige Wertquelle und zusätzliche
  Darstellungsmetadaten als UI-Beschreibung,
- registrierte, konfigurierbare Aktionen mit globaler
  Hotkey-Kollisionsprüfung,
- per-user persistierte Einstellungen mit sicherer, atomarer Speicherung,
- statische Mikrofonwahl und ein bewusst gestarteter Mikrofontest,
- vollständigerer Transkriptverlauf im Dialog einschließlich bewusst
  bestätigtem Löschen einzelner beziehungsweise aller sichtbaren Einträge,
- konfigurierbares Soundfeedback aus explizit freigegebenen Projektassets,
- konfigurierbarer kleiner Overlay-/Statusindikator,
- gezielte Tests, Gesamtsuite und manuelle Windows-/Server-End-to-End-Prüfung.

## 4. Nicht-Ziele

AP06 implementiert ausdrücklich nicht:

- Mikrofon-Hot-Plug, Gerätewechsel oder automatisches Wiederöffnen,
- Windows-Sleep/Wake-Heilung,
- Multi-Monitor-/DPI-Feinschliff über eine solide Primärbildschirmpositionierung
  hinaus,
- Autostart, Packaging oder Installer,
- Adminoberfläche, Admin-Key-Speicherung oder Änderung serverweiter
  Konfiguration,
- beliebige serverseitige Recorder-/VAD-Overrides außerhalb des
  veröffentlichten Session-Create-Contracts,
- ein lokales VAD-Modell,
- gerätespezifische ReSpeaker-LED-Steuerung,
- generische Mikrofon-Gain-Steuerung ohne vom Gerät angebotene sichere
  Schnittstelle,
- lokalen STT-Fallback,
- Einfügung von Realtime-Text,
- neue Serverbefehle,
- modale Fehlerdialoge für passive Reconnectfehler.

ReSpeaker-LED, Geräte-Lifecycle, Sleep/Wake, Multi-Monitor/DPI, Autostart,
Packaging, Installer und Langzeit-/Stresstests bleiben AP07 beziehungsweise
einer späteren ausdrücklich beauftragten Hardwareintegration vorbehalten.

## 5. Bedienvertrag

### 5.1 Hotkeys

Der vorhandene Erststand besitzt folgende Defaults:

| Aktion | Tastenkombination |
| --- | --- |
| primäre Diktieraktion | `Ctrl+Shift+Space` |
| letztes Transkript erneut einfügen | `Ctrl+Alt+Space` |

Beide Hotkeys werden nativ mit Win32 `RegisterHotKey` und `MOD_NOREPEAT`
registriert. `pynput`, Qt-Shortcuts und Polling sind unzulässig.

Die primäre Diktieraktion ist künftig zustands- und modusabhängig:

| Modus/Zustand | Aktion |
| --- | --- |
| Hotkeymodus, `IDLE` | neues Diktatfenster starten |
| Hotkeymodus, Initial-/Follow-up-Wartephase | Wartefrist um den konfigurierten Zeitraum verlängern |
| Hotkeymodus, aktives Serversegment | Verlängerung für die anschließende Follow-up-Phase vormerken; die serverseitige VAD-Grenze selbst bleibt unverändert |
| Wake-Word-Modus, aktiv | kontinuierliche Streamingphase pausieren |
| Wake-Word-Modus, pausiert | kontinuierliche Streamingphase wieder starten |

Ein Start bei nicht bereitem Core wird sofort abgelehnt und nie vorgemerkt.
Ein Reconnect übernimmt weder einen alten Diktierwunsch noch eine laufende
Hotkey-Frist. ADR-002 bleibt uneingeschränkt gültig.

„Erneut drücken = verlängern“ ist der neue Default für die primäre
Diktieraktion im laufenden Hotkey-Diktatfenster. Alternative Aktionen
`finish`, `cancel_discard` und `ignore` bleiben als konfigurierbare Auswahl
zulässig. `cancel_discard` ist ein Notabbruch und nicht der normale
Abschlussweg; bereits vom Server finalisierte und eingefügte Segmente können
nicht zuverlässig zurückgenommen werden.

Der Reinsert-Hotkey ruft weiterhin ausschließlich `reinsert_last()` auf.
Zusätzliche Hotkeys werden nur für ausdrücklich registrierte Aktionen
angeboten, nicht automatisch für jedes boolesche Konfigurationsfeld.

Wenn eine Registrierung fehlschlägt:

- werden bereits in demselben Versuch registrierte AP06-Hotkeys wieder
  freigegeben,
- bleibt die Anwendung über Tray bedienbar,
- wird der Fehler geloggt und einmal kurz im Overlay angezeigt,
- entsteht keine wiederkehrende Meldungsschleife.

Das bisherige `<ctrl>+<shift>+space`-Format wird beim Laden als Legacyformat
akzeptiert; die aktive Konfiguration verwendet eine eindeutige
Win32-kompatible Schreibweise.

### 5.2 Hotkey-Diktatfenster und VAD

Im Hotkeymodus bleibt die VAD-Auswertung vollständig auf dem Server. Der Client
verwaltet darüber nur das Benutzer-Diktatfenster:

```text
IDLE
  → Hotkey
WAITING_FOR_FIRST_SPEECH
  → recording_started
SEGMENT_ACTIVE
  → recording_ended/final
FOLLOWUP_WAIT
  → weitere Sprache: SEGMENT_ACTIVE
  → Frist abgelaufen: stop und IDLE
```

Verbindliche Regeln:

- Der Initial-Timer beginnt erst nach bestätigtem `start`.
- Standard für `initial_speech_timeout` ist zunächst 15 Sekunden und bleibt
  konfigurierbar.
- `recording_started` beendet den Initial-Timer.
- `post_speech_silence_duration` beendet serverseitig nur ein bereits
  begonnenes Segment. Der Client bildet dafür keine zweite lokale VAD nach.
- Nach einem fertigen Segment darf die Streamingphase während eines
  konfigurierbaren `followup_window` offenbleiben. Weitere Sprache erzeugt ein
  neues Serversegment und damit gegebenenfalls einen weiteren Finaltext.
- Ein erneuter primärer Hotkey-Druck setzt beziehungsweise verlängert die
  clientseitige Frist um `hotkey_extension`, standardmäßig 15 Sekunden.
- Der genaue Startdefault des regulären `followup_window` wird im ersten
  manuellen AP06-Bedienlauf festgelegt und anschließend als sichtbarer
  Konfigurationsdefault dokumentiert. Er darf nicht als versteckte Konstante
  im Controller verbleiben.
- Finaltexte werden weiterhin sofort einzeln verarbeitet und nicht bis zum
  Ende des übergeordneten Diktatfensters gepuffert.
- Timer sind an Session-ID, Generation und Diktatversuch gebunden. Alte Timer
  dürfen nach Stop, Reconnect, Moduswechsel oder Shutdown nichts auslösen.

### 5.3 Betriebsmodi

| Merkmal | Hotkeymodus | Wake-Word-Modus |
| --- | --- | --- |
| Sessionparameter | `wakeWordEnabled=false` | `wakeWordEnabled=true` |
| Streaming | nur im Diktatfenster | nach Aktivierung kontinuierlich |
| Auslöser eines Segments | serverseitige VAD nach Clientstart | Wake Word, danach serverseitige VAD |
| primärer Hotkey | starten/verlängern | pausieren/fortsetzen |
| Segmentende | Server-VAD | Server-VAD |

Eine Änderung von Modus, Wake-Word-ID oder Session-Tuningwerten erfordert einen
kontrollierten Reconnect. Läuft dabei ein Diktat, wird es beendet und niemals
automatisch fortgesetzt. Die Anwendung muss dies vor dem Anwenden eindeutig
anzeigen; passive Reconnects bleiben weiterhin still.

Maßgeblich sind ausschließlich die effektiven Werte aus
`hello.sessionConfig` und `ready.sessionConfig`. Fallbacks, Warnungen und
ignorierte Felder werden ehrlich angezeigt. Ein deterministischer Fehler
`where=session_config` mit Close 1008 führt nicht zu einer blinden
Reconnectschleife; erst eine geänderte Konfiguration darf denselben Versuch
wiederholen.

### 5.4 Tray

Das Tray-Menü enthält mindestens:

- nicht anklickbare aktuelle Statuszeile,
- `Diktat starten` beziehungsweise `Diktat stoppen`,
- `Letztes Transkript erneut einfügen`,
- Untermenü `Verlauf` mit den jüngsten Einträgen,
- `Beenden`.

Das Verlaufsmenü wird beim Öffnen frisch über
`STTController.get_recent_entries()` bezogen. Ein Eintrag zeigt gekürzten,
einzeiligen Text und löst `reinsert_entry(entry_id)` aus. Leerer oder nicht
lesbarer Verlauf wird ehrlich dargestellt.

Das Tray zeigt keine Systembenachrichtigungen für passive Reconnectversuche.

### 5.5 Overlay und Feedback

Das Overlay ist:

- rahmenlos,
- immer im Vordergrund,
- nicht aktivierbar und nicht fokussierbar,
- für Mauseingaben transparent,
- ohne Taskbar-Eintrag,
- gemäß `overlay`-Konfiguration positioniert und dimensioniert.

Realtime ersetzt den sichtbaren Text vollständig. Finaltext ersetzt ebenfalls
den Text und blendet nach `fade_after` aus. Das Overlay selbst führt keine
Textinjektion aus.

Unmittelbare Benutzerfehler blinken einmal kurz:

- Netzwerk/Transport: gelb,
- Server, Timeout, Mikrofon oder Audio: gelb,
- Protokoll/sonstiger terminaler Aktionsfehler: rot.

Passive Reconnects lösen kein wiederholtes Overlay aus.

Der Folgeumfang ergänzt:

- einen kleinen, optionalen Statusindikator für bereit, wartet, hört zu,
  segmentaktiv, pausiert und gestört,
- optionale kurze Sounds für mindestens bereit, Diktatstart,
  Diktat-/Segmentabschluss, Verlängerung, Pause und aktionsbezogenen Fehler,
- Lautstärke beziehungsweise Soundaktivierung als Einstellung,
- keine blockierende Audiowiedergabe und keine Fehlereskalation, wenn ein
  Soundasset oder Ausgabegerät fehlt.

Es werden nur ausdrücklich ausgewählte, lizenzrechtlich geprüfte Dateien aus
`assets/sound_effects/` als Produktassets eingebunden. Die große
Sichtungssammlung wird nicht pauschal ausgeliefert oder automatisch
registriert. Eine ReSpeaker-LED-Implementierung gehört nicht in AP06; AP06
erhält jedoch eine klare Feedback-Schnittstelle, an die später ein
Hardwareadapter angeschlossen werden kann.

## 6. Statusdarstellung

Die UI verwendet ausschließlich `ControllerStatusSnapshot` und
`TransientEvent`.

| Zustand | Trayfarbe | Kurztext |
| --- | --- | --- |
| Hotkeymodus `READY` + `IDLE` | dunkelgrün | Wartet auf Hotkey |
| Hotkey-Diktat `STARTING` / Initialwarten | dunkelgrün mit weißem Rand | Wartet auf Sprache |
| Hotkey-Follow-up | dunkelgrün mit weißem Rand | Wartet auf Fortsetzung |
| Hotkey-Serversegment aktiv | hellgrün | Sprache wird aufgenommen |
| Wake-Word-Modus aktiv / `wakeword_wait` | dunkelblau | Wartet auf Wake Word |
| Wake Word erkannt / wartet auf Sprache | dunkelblau mit weißem Rand | Wartet auf Sprache |
| Wake-Word-Recorder aktiv | hellblau | Sprache wird aufgenommen |
| Wake-Word-Modus pausiert | grau | Wake Word pausiert |
| `STARTING` / `CONNECTING` / `NETWORK_UNAVAILABLE` | gelb | Verbinde / Netzwerk nicht verfügbar |
| `SERVER_BUSY` / `SERVER_UNAVAILABLE` | gelb | Server ausgelastet / nicht verfügbar |
| `MICROPHONE_UNAVAILABLE` | gelb | Mikrofon nicht verfügbar |
| `PROTOCOL_ERROR` | rot | Protokollfehler |
| `SHUTTING_DOWN` / `STOPPED` | grau | Wird beendet / Beendet |

Gelb kennzeichnet ausschließlich äußere Störungen, auf die der Client keinen
unmittelbaren Einfluss hat. Rot ist tatsächlichen internen oder
protokollarischen Fehlern vorbehalten. Der Tooltip darf Grund und nächsten
Retry knapp ergänzen. Statuswiederholungen erzeugen weder Popups noch
Ereignisfluten.

## 7. Threading- und Lifecycle-Vertrag

### 7.1 Main Thread

Im Qt-Main-Thread leben:

- `QApplication`,
- Tray, Menüs, Aktionen und Overlay,
- Qt-Signalempfänger,
- nativer Qt-Eventfilter für `WM_HOTKEY`.

### 7.2 Core-Thread

Ein separater Python-Thread besitzt:

- genau eine asyncio-Event-Loop,
- genau einen `STTController`,
- dessen vollständigen `run()`-/`shutdown()`-Lifecycle.

Kein Qt-Widget wird im Core-Thread erzeugt oder verändert.

### 7.3 Brücken

Core-Callbacks emittieren ausschließlich Qt-Signale mit unveränderlichen
Payloads. Qt-Befehle werden mit `asyncio.run_coroutine_threadsafe` oder
`loop.call_soon_threadsafe` in die besitzende Event-Loop übergeben.

Erforderliche Befehle:

- primäre Diktieraktion,
- explizites Starten, Beenden und optionales Verwerfen,
- Modus-/Sessionprofil anwenden und kontrolliert reconnecten,
- Settings laden, validieren und anwenden,
- Reinsert-last,
- Reinsert-by-ID,
- Verlauf laden und gezielt löschen,
- Shutdown.

Ein Befehl vor Core-Bereitschaft oder nach Shutdown wird lokal abgelehnt und
niemals später vorgemerkt.

### 7.4 Shutdown

Shutdown ist einmalig und idempotent:

1. keine neuen UI-Befehle annehmen,
2. Hotkeys abmelden,
3. Tray ausblenden,
4. `controller.shutdown()` im Core-Thread ausführen,
5. Core-Thread begrenzt abwarten,
6. Single-Instance-Mutex freigeben,
7. Qt beenden.

Ein hängender Shutdown wird geloggt; der Main Thread darf nicht unbegrenzt
blockieren.

## 8. Single Instance

Der erste Prozess hält einen benannten lokalen Win32-Mutex bis zum Shutdown.
Erkennt ein zweiter Prozess `ERROR_ALREADY_EXISTS`, startet er weder Core noch
Hotkeys oder Tray und beendet sich kontrolliert mit einem unterscheidbaren
Exitcode.

Tests verwenden ein Backend-Double; es wird kein zweiter realer
Produktprozess gestartet.

## 9. Konfiguration

### 9.1 Architekturentscheidung

`AppConfig` und ihre typisierten Unterobjekte bleiben die einzige fachliche
Wertquelle. AP06 führt keine generische `dict[str, Any]`-Konfiguration als
zweite Wahrheit ein.

Darüber liegt eine deklarative, unveränderliche Metadatenregistrierung. Eine
Definition beschreibt mindestens:

```text
key/path
label
description
setting_type
category/tab
group
show_in_dialog
advanced
order
constraints (min/max/step/options/unit)
apply_policy
sensitive
optional dependency/visibility condition
```

Der aktuelle Wert und der Default werden aus der typisierten Konfiguration
bezogen. Metadaten speichern keinen unabhängigen zweiten Laufzeitwert.

Zunächst unterstützte Standardtypen:

- `STRING`,
- `INTEGER`,
- `FLOAT`,
- `BOOLEAN`,
- `CHOICE`.

Der Dialog darf dafür wenige wiederverwendbare Standardeditoren bereitstellen.
Sonderfälle wie Mikrofonliste, Wake-Word-Katalog, Sounddatei oder Hotkey werden
über kleine ausdrücklich registrierte Editoren angebunden und nicht durch
ungeprüfte Typheuristiken erraten.

### 9.2 Änderungswirkung

Jede sichtbare Einstellung besitzt eine definierte `apply_policy`:

- `IMMEDIATE`,
- `HOTKEY_REREGISTER`,
- `AUDIO_RESTART`,
- `SESSION_RECONNECT`,
- `APP_RESTART`.

Vor dem Speichern wird eine vollständige Kandidatenkonfiguration erstellt und
validiert. Erst danach werden Datei und Laufzeit geändert. Scheitert
Registrierung, Audio-Neustart oder Reconnectvorbereitung, bleiben die zuletzt
gültigen Werte aktiv beziehungsweise werden atomar wiederhergestellt.

Modus- und Wake-Word-Änderungen sind `SESSION_RECONNECT`. Ein aktives Diktat
wird dabei kontrolliert beendet und nicht wiederaufgenommen. Der Dialog muss
diese unmittelbare Folge vor dem Anwenden benennen.

### 9.3 Persistenz

Die versionierte `config.yaml` dokumentiert weiterhin die sichtbaren
Projektdefaults. Benutzereinstellungen aus dem Dialog werden als
benutzerspezifische Override-Datei im lokalen Anwendungsdatenverzeichnis
gespeichert und nicht in das Repository zurückgeschrieben.

Die Ladereihenfolge lautet:

1. typisierte Code-/Projektdefaults,
2. versionierte `config.yaml`,
3. per-user Override.

Explizit an Tests oder Diagnosewerkzeuge übergebene Konfigurationspfade bleiben
unterstützt. Das Speichern erfolgt atomar über eine temporäre Datei und
anschließendes Ersetzen. Secrets werden weder in dieser Datei noch im Dialog
eingeführt.

### 9.4 Aktions- und Hotkeyregistrierung

Hotkeys binden an stabile Aktions-IDs, nicht unmittelbar an beliebige
`enabled`-Felder. Die erste Registrierung umfasst mindestens:

```text
dictation.primary
dictation.finish
dictation.cancel
history.reinsert_last
overlay.toggle
```

Nur ausdrücklich als global und benutzerbindbar markierte Aktionen erscheinen
im Hotkeyeditor. Doppelte Kombinationen, ungültige Kombinationen und
Registrierungskonflikte werden vor Übernahme erkannt. Eine teilweise
Neuregistrierung wird vollständig zurückgerollt.

Damit bleibt die spontane Idee erhalten, Funktionen schnell per Hotkey
erproben zu können, ohne jedes boolesche Setting automatisch zu einem
ungeprüften Laufzeitbefehl zu machen.

### 9.5 Einstellungsdialog

Der Dialog wird aus Tabs und Metadatengruppen aufgebaut:

| Tab | AP06-Inhalt |
| --- | --- |
| Verlauf | vollständigerer gespeicherter Verlauf, Reinsertion, einzelnes Löschen, alles Löschen mit Bestätigung |
| Allgemein | Aktions-Hotkeys, Textinjektion, History-, Clipboard- und Logging-Einstellungen |
| Verbindung & Betriebsmodus | Server-URL, Reconnectwerte, Hotkey/Wake Word, Wake-Word-ID und veröffentlichte Session-Tuningwerte, kontrollierter Reconnect |
| Geräte & Audio | statische Mikrofonwahl, unterstützte Basiswerte und manueller Mikrofontest |
| Erscheinungsbild & Feedback | Overlay, Realtime-Anzeige, Position, Farben, Schrift, Statusindikator und Sounds |

Nicht angezeigt werden ein Server-Administrationstab, ein Admin-Key, generische
Server-Engine-/Modelländerungen oder nicht unterstützte Hardwarewerte wie ein
vorgeblicher universeller Mikrofon-Gain.

### 9.6 Mindestvalidierung

- boolesche Felder sind tatsächlich boolesch,
- alle numerischen Werte sind endlich und innerhalb ihrer Grenzen,
- Betriebsmodus und Hotkeyaktion gehören zu den veröffentlichten Optionen,
- alle Aktions-Hotkeys sind syntaktisch gültig und kollisionsfrei,
- Wake-Word-Tuningwerte erfüllen den Serververtrag,
- Overlayposition, Dimensionen, Schriftgröße, Opazität, Fadezeit und Ränder
  sind gültig,
- Dateipfade werden weder als Secretkanal noch als beliebige
  Code-/URL-Ausführung behandelt,
- unbekannte per-user Felder werden kontrolliert behandelt und führen nicht zu
  einer stillen Teilübernahme einer ansonsten ungültigen Konfiguration.

## 10. Modulzuschnitt

Vorgesehen:

- `ui/presentation.py`: reine Status-/Textabbildung,
- `ui/core_bridge.py`: asyncio-Core-Thread und Qt-Signale,
- `ui/hotkeys.py`: Parser, Win32-Backend und nativer Eventfilter,
- `ui/single_instance.py`: Win32-Mutex-Guard,
- `ui/overlay.py`: passives Overlay,
- `ui/tray.py`: Tray, Menüs und Verlauf,
- `ui/settings_dialog.py` oder kleiner gleichwertiger Modulverbund:
  Dialog, Tabs und Standardeditoren,
- `core/settings_metadata.py`: UI-neutrale, deklarative
  Einstellungsdefinitionen ohne zweite Wertablage,
- `core/actions.py`: stabile Aktions-IDs und Bindungsmetadaten,
- ein kleiner UI-neutraler Diktatfenster-Automat im Controllerbereich,
- ein nicht blockierender Feedbackdienst mit austauschbaren Sinks für
  Overlay und Sound,
- `ui/application.py`: Composition Root und GUI-Lifecycle,
- `app.py`: Auswahl GUI beziehungsweise `--headless`.

Der Zuschnitt darf klein angepasst werden, solange Verantwortlichkeiten und
Threadgrenzen erhalten bleiben.

## 11. Testvertrag

Mindestens automatisiert zu prüfen:

### Konfiguration und Hotkeyparser

- Defaultwerte,
- Überlagerung von Projekt- und per-user Konfiguration,
- atomare Speicherung und Fehler-Rollback,
- vollständige Kandidatenvalidierung vor Laufzeitänderung,
- Metadatenschlüssel entsprechen genau einem typisierten Konfigurationspfad,
- alle Standardeditoren lesen und schreiben den korrekten Typ,
- Abhängigkeiten, Sichtbarkeit und `apply_policy`,
- Legacyformat,
- Modifier-/Key-Normalisierung,
- unbekannte, doppelte oder modifierlose Kombinationen,
- identische Action-Hotkeys,
- nur ausdrücklich freigegebene Aktionen sind bindbar,
- partielle Registrierung wird zurückgerollt,
- Unregister ist idempotent,
- `WM_HOTKEY` wird genau einer Aktion zugeordnet.

### Betriebsmodi, Sessionvertrag und Diktatfenster

- URL-Erzeugung kodiert jeden Queryparameter exakt einmal,
- Hotkeymodus fordert `wakeWordEnabled=false`,
- Wake-Word-Modus fordert `wakeWordEnabled=true`,
- effektive Handshakewerte, Fallbacks, Warnungen und ignorierte Felder werden
  ausgewertet,
- widersprechende effektive Werte verhindern eine fälschlich als erfolgreich
  gemeldete Modusaktivierung,
- `session_config`/1008 erzeugt keine blinde Reconnectschleife,
- Moduswechsel stoppt eine alte Session und hinterlässt keine Tasks,
- Initial-Timer startet erst nach bestätigtem `start`,
- `recording_started` beendet nur den passenden Initial-Timer,
- `recording_ended` öffnet die passende Follow-up-Phase,
- erneuter Hotkey verlängert nur die aktuelle Generation beziehungsweise
  merkt die Verlängerung für ihre Follow-up-Phase vor,
- alte Timer wirken nach Stop, Reconnect, Moduswechsel und Shutdown nicht,
- mehrere Finalsegmente eines Diktatfensters werden weiterhin jeweils genau
  einmal verarbeitet,
- unterbrochenes Diktat wird gemäß ADR-002 nicht fortgesetzt.

### Single Instance

- erster Guard erhält Besitz,
- zweiter Guard wird abgelehnt,
- Release genau einmal,
- Backendfehler werden kontrolliert behandelt.

### Core-Brücke

- Controller und Event-Loop leben im Workerthread, Qt im Main Thread,
- Snapshot, Feedback, Text und CommandResult gelangen als Signale zur UI,
- Coroutine-Befehle laufen in der besitzenden Loop,
- synchrone Reinsertion-/Historybefehle laufen ebenfalls im Core-Thread,
- Befehl vor Start/nach Stop wird abgelehnt,
- Shutdown ist idempotent und hinterlässt keinen Thread.

### Präsentation, Tray und Overlay

- jede Availability-/Dictation-Kombination besitzt definierte Darstellung,
- Modus, Pause, Initialwarten, Segment und Follow-up besitzen unterscheidbare
  Darstellungen,
- passive Reconnectstatus lösen keine Popupfunktion aus,
- Aktionslabel folgt Modus und Diktatfensterzustand,
- Verlauf ist newest-first, begrenzt, gekürzt und ID-gebunden,
- Löschen einzelner Einträge und „alles löschen“ besitzt eine eindeutige,
  getestete Deduplizierungssemantik,
- Realtime ersetzt Text und Final startet Fade,
- Overlayflags verhindern Fokus und Mauseingaben,
- Feedbackfarben unterscheiden Netzwerk/Mikrofon/Protokoll,
- deaktivierte Sounds spielen nichts,
- fehlendes Soundasset oder Ausgabegerät blockiert weder UI noch Core.

### Composition und Regression

- GUI-Start erzeugt Core nicht im Main Thread,
- fehlende Trayverfügbarkeit und Hotkeykonflikt werden kontrolliert behandelt,
- zweiter Prozess startet keine Komponenten,
- `--headless` bleibt nutzbar,
- alle 197 Vor-AP06-Tests bleiben grün,
- alle 239 Tests des technischen AP06-Erststands bleiben grün,
- `py_compile` und geeigneter Offscreen-Qt-Smoke-Test bestehen,
- ein realer Windows-Test belegt Settings-Persistenz, Hotkey-Neuregistrierung,
  Hotkeymodus bis zur Textinjektion sowie Wake-Word-Pause/Fortsetzung.

## 12. Abnahmekriterien

AP06 ist nur abgenommen, wenn:

- alle Scopepunkte implementiert sind,
- Qt ausschließlich im Main Thread bleibt,
- Core und asyncio ausschließlich im separaten Thread laufen,
- UI-Befehle keine Rennen oder spätere Vormerkung erzeugen,
- Hotkeys nativ und konfliktrobust sind,
- Hotkey- und Wake-Word-Modus den effektiven Serververtrag korrekt anwenden,
- Modus- und Profiländerungen kontrolliert reconnecten,
- das Hotkey-Diktatfenster ohne lokales VAD zuverlässig startet, verlängert
  und endet,
- Einstellungsdialog und Metadatenregistrierung keine zweite
  Konfigurationswahrheit erzeugen,
- ungültige Einstellungen und fehlgeschlagene Laufzeitübernahme die letzte
  gültige Konfiguration erhalten,
- Benutzereinstellungen nicht in die versionierte Projektkonfiguration
  zurückgeschrieben werden,
- der Einstellungsdialog die vereinbarten fünf Tabs bereitstellt,
- das Overlay keinen Fokus stiehlt,
- Soundfeedback optional, nicht blockierend und fehlertolerant ist,
- passive Reconnectfehler still bleiben,
- Reinsertion sowie die vereinbarte Verlaufspflege funktionieren,
- Single Instance vor Corestart greift,
- Shutdown keine Threads oder Hotkeys zurücklässt,
- neue und bestehende Tests grün sind,
- sichere Smoke-Tests getrennt dokumentiert sind,
- Roadmap, Task, Übersicht, Übergabe und README synchron sind,
- AP07 nicht vorweggenommen wurde.

## 13. Abnahme

Der technische AP06-Erststand wurde am 25. Juli 2026 umgesetzt und zunächst
abgenommen. Am 26. Juli wurde das Paket wieder geöffnet, weil die vollständige
gemeinsame Produkt-/Scopeabstimmung vor der Umsetzung übersprungen worden war.

- Die reguläre Anwendung startet als PySide6-GUI; der bisherige
  Diagnosebetrieb bleibt über `app.py --headless` erhalten.
- Qt, Tray, Overlay und nativer Eventfilter laufen ausschließlich im Main
  Thread. Ein separater nicht-daemonisierter Thread besitzt die asyncio-Loop
  und genau einen `STTController`.
- `Ctrl+Shift+Space` schaltet die Diktierung um;
  `Ctrl+Alt+Space` fügt den letzten Finaltext erneut ein.
- Tray, Verlaufsauswahl und Overlay greifen ausschließlich über die
  thread-sichere Core-Brücke auf den Controller zu.
- Ein nativer Win32-Mutex verhindert eine zweite Instanz, bevor Core,
  Hotkeys oder Tray gestartet werden.
- Hotkeykonflikt, fehlendes Tray, Core-Startfehler und Shutdown besitzen
  kontrollierte, getestete Pfade.

Die Vor-AP06-Baseline von 197 Tests blieb erhalten. Nach der
Overlay-Signalkorrektur bestanden 239 Tests; nach Folgeumfang und Härtung
bestehen 257 automatische Tests. Nach Umsetzung des verbindlichen
Indikatorfarbkonzepts bestanden 261 automatische Tests. Nach dem robusten
Moduswechsel-Fix bestehen **264 automatische Tests**.
Zusätzlich bestanden:

- `compileall` über sämtliche Python-Laufzeit- und Testmodule,
- ein nativer Windows-Smoke-Test für Mutex, `RegisterHotKey`,
  `WM_HOTKEY`-Dispatch und Ressourcenfreigabe,
- ein echter vollständiger AP06-Live-Smoke mit Qt-Tray, Mutex, Hotkeys,
  separatem Core-Thread und Serverzustand `READY`, ohne Diktatstart,
  Audioaufnahme oder Textinjektion.

Der sessionlokale Wake-Word-Contract, Einstellungsdialog, Metadatenebene,
Aktionshotkeys, per-user Persistenz, Verlaufspflege und Hotkey-Diktatfenster
sind implementiert. Ein sicherer Live-Smoke bestätigte am 28. Juli
`effectiveWakeWordEnabled=false` im Hotkeymodus und `true` mit
`hey_jarvis` im Wake-Word-Modus jeweils in `hello` und `ready`.

Der technische Abschlussnachweis steht unter
`docs/2026-07-28_AP06_FOLGEUMFANG_ABSCHLUSS/ABSCHLUSSBERICHT.md`.
Der anschließende reale Bedien-Smoke bestätigte die Prüfungen 1 bis 4 und
deckte zwei Clientfehler beim Laufzeit-Moduswechsel auf. Beide sind behoben:
Der Maintainer besteht nun während des gesamten Core-Lifecycles, ein
Wake-Word-Wechsel wird erst nach bestätigter Streamaktivierung erfolgreich
gemeldet, und ein Fehler stellt die letzte funktionierende Konfiguration
bestätigt wieder her.

Die frühere Sequenz bestand lokal drei Wiederholungen sowie Negativ- und
Reconnect-Härtung. Ein sicherer produktiver Test bestand zwei vollständige
Hotkey↔Wake-Word-Zyklen über die Sessiongenerationen 1 bis 5. Maßgeblicher
Fixnachweis:
`docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`.
Vor der formalen AP06-Abnahme bleibt nur der gesprochene Wake-Word-Test mit
echtem Mikrofon. AP07 wird vorher nicht begonnen.
