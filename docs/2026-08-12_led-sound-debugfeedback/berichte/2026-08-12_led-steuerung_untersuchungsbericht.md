# Untersuchungsbericht: ReSpeaker-LED-Steuerung

**Datum:** 12. August 2026  
**Untersuchungsart:** Repository-übergreifende Codeanalyse, lokale Laufzeitdiagnose, automatisierte Tests und Test am echten ReSpeaker XVF3800  
**Untersuchte Repositories:**

| Repository | Commit | Rolle |
| --- | --- | --- |
| `voice-stt-server` | `13c162950b944dc715fdd81983a7465f8eb0fd79` | STT-Server und Erzeuger fachlicher Transkriptionsereignisse |
| `voice-stt-client` | `467a6b699b470df4a7bb15e1c81126c37036facd` | Windows-Desktop-Client, Eventreduktion und LEFX-Integration |
| `led_controller_respeaker-v3` | `aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0` | LEFX-Engine, Effekte, Renderloop und ReSpeaker-USB-Sink |

Der VPS wurde nicht benötigt und nicht verändert. Der lokal laufende Desktop-Client, seine lokalen Logs und das echte USB-Gerät wurden mit Freigabe des Nutzers untersucht.

## Kurzfazit

Die LED-Engine ist nicht grundsätzlich defekt. Sie rendert nach dem Start des `ControllerService` fortlaufend und der echte ReSpeaker akzeptiert Ringmodus und Farbframes. Die primäre, im Code reproduzierbare Ursache für den beobachteten Eindruck „LED-Steuerung funktioniert nicht“ liegt im Desktop-Client:

> Die konfigurierten Ereignisse `client.lifecycle.started` und `client.lifecycle.stopping` werden im ausführbaren Clientcode nirgends erzeugt.

Dadurch werden beim normalen Programmstart weder `init_event` noch `ready_state` an LEFX übergeben. Weil LEFX absichtlich erst beim ersten LED-Befehl gestartet wird, läuft bis zu einem späteren LED-relevanten Ereignis auch kein Renderthread. Der Ring bleibt nach dem Start so, wie ihn die vorherige Sitzung hinterlassen hat – üblicherweise dunkel.

Die lokale Loghistorie bestätigt dieses Verhalten: Der ReSpeaker wurde am 12.08.2026 um 16:40:15 verbunden, der LEFX-Service aber erst um 16:43:53 gestartet, also erst rund 3 Minuten und 38 Sekunden später. Ein korrekt verdrahtetes `client.lifecycle.started` hätte den Service direkt beim Start aktiviert.

Der Anfangsverdacht ist damit teilweise richtig einzuordnen:

- Die Engine besitzt eine fortlaufende Renderloop.
- Der Hardware-Sink sendet absichtlich nur geänderte Frames.
- Unter realer USB-Last wurden nicht die konfigurierten 30 FPS erreicht, aber fortlaufend unterschiedliche Animationsframes übertragen.
- Das entscheidende Problem ist zunächst, dass der Client beim Start überhaupt keinen LED-Zustand aktiviert.

## Tatsächlicher Datenfluss

```text
voice-stt-server
  erzeugt fachliche Events, z. B. transcription.recording_started
        │
        ▼
voice-stt-client / EventStream + STT-Fallback
  normalisiert auf CanonicalEventType
        │
        ▼
FeedbackReducer + feedback_mappings aus config.yaml
  erzeugt LedCall(set_state / emit_event / ...)
        │
        ▼
LedFeedback-Worker
  serialisiert die Befehle
        │
        ▼
InProcessLedController
  startet ControllerService beim ersten Befehl
        │
        ▼
LEFX ControllerService / lefx-render
  rendert best-effort mit konfigurierten 30 FPS
        │
        ▼
ReSpeakerFrameSink
  setzt LED_EFFECT=5 und sendet geänderte LED_RING_COLOR-Frames
        │
        ▼
UsbTransport / XVF3800-Firmware
```

Der Server spricht den LED-Controller nicht direkt an. Er liefert nur die fachlichen Ereignisse. Die Entscheidung, was der Ring anzeigen soll, liegt vollständig im Desktop-Client und im LEFX-Effektkatalog.

## Befunde nach Priorität

### P1 – Start- und Stoppereignisse sind tote Konfiguration

In [`voice-stt-client/config.yaml`](../../voice-stt-client/config.yaml) sind folgende Regeln vorhanden:

```yaml
client.lifecycle.started:
  led: [{emit_event: init_event}, {set_state: ready_state}]
client.lifecycle.stopping:
  led: {clear_state: primary}
```

Die beiden Ereignistypen existieren außerdem in [`core/event_models.py`](../../voice-stt-client/core/event_models.py). Eine vollständige Suche über den ausführbaren Code zeigt aber keine Stelle, die einen dieser Typen an `report_local_feedback()` oder direkt an die Feedback-Engine übergibt. Außer Enum, YAML und Dokumentation gibt es keine Verwendung.

[`ui/application.py`](../../voice-stt-client/ui/application.py) startet Tray, Hotkeys und Core, meldet anschließend jedoch kein `CLIENT_LIFECYCLE_STARTED`. Beim Beenden wird `LedFeedback.shutdown()` aufgerufen, ohne vorher `CLIENT_LIFECYCLE_STOPPING` zuverlässig durch die Feedbackkette zu schicken.

**Auswirkung:**

- Kein sichtbarer Initialisierungseffekt beim Programmstart.
- Kein automatischer `ready_state`.
- LEFX startet wegen seines Lazy-Start-Vertrags erst beim ersten späteren LED-Befehl.
- Ein Benutzer kann einen verbundenen und vom Client exklusiv geöffneten ReSpeaker sehen, während der Ring trotzdem dunkel bleibt.

**Bewertung:** sehr hohe Wahrscheinlichkeit, direkt ursächlich für den beobachteten Startzustand.

### P1 – Die bestehende Testsuite deckt genau diese Integrationslücke nicht ab

Der Hardware-Smoke [`tests/manual_test_ap07_led_hardware.py`](../../voice-stt-client/tests/manual_test_ap07_led_hardware.py) übergibt `LedCall`-Objekte direkt an `LedFeedback`. Damit validiert er Katalog, Queue, Engine, USB-Sink und Gerät, umgeht aber die Stelle, an der das Problem sitzt: die Erzeugung des Lifecycle-Ereignisses durch die echte Anwendung.

Auch die automatisierten UI- und Feedbacktests prüfen Mappings und bereits erzeugte `FeedbackDecision`-Objekte, aber nicht die Ende-zu-Ende-Aussage:

> `DesktopApplication.start()` muss genau einmal `client.lifecycle.started` auslösen und dadurch den LED-Startzustand aktivieren.

Deshalb können alle vorhandenen Tests grün sein, obwohl der Ring nach einem echten Programmstart dunkel bleibt.

### P2 – Exklusiver USB-Besitz ist korrekt, aber betrieblich irreführend

Vor dem Hardwaretest wurde folgendes reale Verhalten festgestellt:

- Das Gerät wurde über VID/PID gefunden.
- Ein zweiter Prozess erhielt beim ersten `VERSION`-Read `USBError [Errno 13] Access denied`.
- Der bereits laufende Client unter `P:\DockerProjekte\voice-stt-client\app.py` hielt den libusb-/WinUSB-Zugriff exklusiv.
- Nach dem gezielten Beenden dieses Clientprozesses meldete `lefx-respeaker probe` das Gerät sofort als erreichbar.

Das ist für einen exklusiven USB-Control-Endpunkt grundsätzlich erwartbar. Es erzeugt aber eine problematische Kombination mit dem P1-Fehler: Der Client kann das Gerät besitzen, ohne einen Startzustand zu rendern, während jedes Diagnosewerkzeug nur „Access denied“ sieht.

Zusätzlich klassifizierte `lefx-respeaker claim -n` den echten `voice-stt-client/app.py`-Prozess als „unrelated USB software“ und hätte ihn ohne `--include-unrelated` nicht freigegeben. Im Client ist `force_claim` bewusst nicht konfigurierbar. Das schützt andere Prozesse, erschwert aber die Diagnose.

**Bewertung:** nicht die Ursache innerhalb der einzigen laufenden Clientinstanz, aber ein erheblicher Diagnose- und Mehrinstanz-Fallstrick.

### P2 – Die Renderloop läuft fortlaufend, 30 FPS sind jedoch nur ein Zielwert

[`lefx/interfaces/service.py`](../../led_controller_respeaker-v3/packages/led-controller-version-3/src/lefx/interfaces/service.py) besitzt eine echte Dauerschleife:

- Intervall `1 / fps`;
- `render_once()` in jeder Iteration;
- Warten nur für die verbleibende Framezeit;
- Fehler einer Iteration beenden die Schleife nicht.

[`lefx/device/respeaker/sink.py`](../../led_controller_respeaker-v3/packages/led-controller-version-3/src/lefx/device/respeaker/sink.py) sendet dagegen absichtlich nur bei Änderung:

- `LED_EFFECT=5` einmal pro Verbindungssitzung;
- `LED_RING_COLOR` nur, wenn sich das Tupel der zwölf RGB-Werte vom zuletzt gesendeten unterscheidet;
- nach Reconnect werden Modus und Frame erneut vollständig gesendet.

Das ist bei statischen Zuständen korrekt: Die Firmware hält den zuletzt geschriebenen Frame. Bei animierten Effekten entstehen weiterhin neue Frames.

**Reale Messung mit `ready_state`, 30 FPS konfiguriert, 3 Sekunden:**

| Messwert | Ergebnis |
| --- | ---: |
| gezählte Engine-Renderings | 65 |
| `LED_EFFECT`-Writes | 1 |
| `LED_RING_COLOR`-Writes | 21 |
| unterschiedliche gesendete Ringframes | 21 |
| Sink verfügbar | ja |
| Servicefehler | keiner |

Damit lief die Engine effektiv mit rund 22 Renderings pro Sekunde und übertrug rund 7 unterschiedliche Hardwareframes pro Sekunde. Die Differenz entsteht durch synchrone USB-Schreibzugriffe und durch die Farbauflösung: Bei einer langsamen Atemanimation ergeben mehrere Renderzeitpunkte nach Rundung denselben RGB-Frame und werden korrekt zusammengefasst.

**Bewertung:** Der Verdacht „keine dauerhafte Renderloop“ ist widerlegt. „30 FPS werden physisch nicht durchgehend erreicht“ ist dagegen richtig. Das erklärt keine vollständig dunkle Ausgabe, kann aber die wahrgenommene Animationsqualität beeinflussen.

### P2 – Externe Änderung des Firmwaremodus wird nicht erkannt

Der Sink merkt sich intern `_ring_mode=True`, sobald `LED_EFFECT=5` einmal erfolgreich geschrieben wurde. Er prüft den Modus nicht aus der Firmware zurück und setzt ihn nur nach einer erkannten neuen USB-Verbindung erneut.

Sollte eine andere Software bei bestehender Verbindung den Firmwaremodus verändern, läuft LEFX weiter und schreibt gegebenenfalls neue `LED_RING_COLOR`-Puffer, ohne `LED_EFFECT=5` erneut zu behaupten. Die Farben könnten dann unsichtbar bleiben, obwohl Sinkstatus und Writes erfolgreich aussehen.

Auf dem Rechner läuft außerdem `ReSpeakerMicrophoneArrayApp.exe`. Im Test war sie nicht der exklusive libusb-Halter und verhinderte den erfolgreichen Hardware-Smoke nicht. Ein aktueller konkreter Konflikt ist damit nicht belegt; das fehlende periodische oder ereignisbasierte Reassert bleibt dennoch ein Robustheitsrisiko.

### P3 – Die konfigurierte Helligkeit ist für manche Zustände sehr niedrig

Der Clientwert `brightness: 64` wird global auf `64 / 255 ≈ 25 %` skaliert. `ready_state` besitzt zusätzlich eine eigene Spitzenhelligkeit von `55 %` und eine minimale Helligkeit von `16 %`.

Damit liegt der sichtbare `ready_state` effektiv nur ungefähr zwischen 4 % und 14 % der unskalierten RGB-Leistung. Unter heller Umgebung kann der Ring dadurch deutlich schwächer wirken als erwartet. Das ist keine Erklärung für eine vollständig ausbleibende Animation, verstärkt aber den Eindruck „funktioniert nicht“.

### P3 – Der vereinbarte Threadbesitz wird an zwei Stellen umgangen

Die Integrationsplanung fordert, dass ausschließlich der LED-Worker LEFX aufruft. Im aktuellen Code gibt es Ausnahmen:

- `LedFeedback.set_device_mute()` ruft Controller und `set_output()` synchron im aufrufenden Thread auf.
- `DesktopApplication._on_device_mute_changed()` ruft `self.led_feedback.controller.set_output(...)` direkt aus dem Qt-Pfad auf.

Transport und Controller enthalten Locks, weshalb die Tests keinen unmittelbaren Fehler zeigen. Die Implementierung widerspricht dennoch ihrem eigenen Ownership-Vertrag und kann USB-Latenz in den Qt-Thread tragen oder sich mit Render-/Mutezugriffen überlagern.

Bei einem Austausch des LED-Backends in `_replace_led_feedback()` wird außerdem der Callback `on_device_mute_changed` nicht wieder gesetzt. Nach Reconnect oder Sinkwechsel folgt der neue Adapter deshalb physischen Mute-Änderungen nicht mehr wie die ursprüngliche Instanz.

**Bewertung:** nicht primär für den dunklen Start verantwortlich, aber vor einer allgemeinen Härtung zu korrigieren.

### P3 – Zwei Arbeitskopien erhöhen das Betriebsrisiko

Der tatsächlich gestartete Client kam aus `P:\DockerProjekte\voice-stt-client`, während die gemeinsame aktuelle Arbeitskopie unter `P:\GithubRepos\marcosudau-vps\voice-stt-client` liegt. Beide befanden sich zum Untersuchungszeitpunkt auf demselben Commit, daher entstand heute kein Versionsunterschied.

Der Desktop-Launcher verweist aber weiterhin auf die erste Kopie. Künftige Änderungen in der neuen Projektwurzel wirken daher nicht automatisch auf das tatsächlich gestartete Programm. Das sollte vor einer Fehlerbehebung vereinheitlicht oder wenigstens ausdrücklich dokumentiert werden.

## Bewertung des Servers

Im Servercode sind die für LEDs relevanten fachlichen Ereignisse vorhanden und werden auf die vom Client erwarteten Protokollnamen abgebildet, unter anderem:

- `wakeword.detected`;
- `transcription.recording_started`;
- `transcription.recording_ended`;
- `transcription.started`;
- `transcription.completed` und die terminalen Fehler-/Abbruchvarianten.

[`core/event_normalizer.py`](../../voice-stt-client/core/event_normalizer.py) kennt dieselben Namen. Der Client besitzt zusätzlich einen STT-WebSocket-Fallback, falls der separate Eventstream noch nicht live ist. Die vorhandenen Tests für Normalisierung, Reducer, Eventstream und Fallback waren erfolgreich.

Es wurde kein Hinweis gefunden, dass der STT-Server die LED-Ausgabe verhindert. Der Startzustand ist ohnehin ein lokales Client-Lifecycle-Ereignis und hängt nicht vom Server ab.

## Reale Hardware- und Testnachweise

### ReSpeaker XVF3800

- PnP-Gerät vorhanden und ohne Windows-Gerätefehler.
- Control Interface `MI_03` als `reSpeaker Control` vorhanden.
- Nach Freigabe durch den alten Client war `VERSION` lesbar.
- Der Client-Hardware-Smoke löste alle 13 tatsächlich verwendeten Ziele auf und führte sie über `LedFeedback` aus.
- Sink meldete durchgehend verfügbar; keine USB-/LEFX-Ausfälle.
- Sauberer Shutdown setzte die Ausgabe aus und schloss den Transport.
- Vier nicht-interaktive Hardwaretests des Controller-Repositories bestanden.
- Zwei Tests für manuelles Abziehen/Wiederanstecken wurden erwartungsgemäß übersprungen, da `LEFX_INTERACTIVE=1` nicht gesetzt war.

### Automatisierte Tests

| Bereich | Ergebnis |
| --- | --- |
| Client, fokussiert auf LED/Mapping/Reducer/UI/CoreBridge | **90 bestanden** |
| Client, vollständige Suite mit `-W error` | **435 bestanden** |
| LEFX/Controller, vollständige hardwarefreie Suite | **1.523 Tests, 0 Fehler, 0 Fehlschläge, 3 Skips** |
| LEFX/Controller, echte Hardwaretests | **4 bestanden, 2 interaktive Skips** |

Für die Controller-Suite wurden die vorgesehenen Effektarchive lokal gebaut. Ein erster fokussierter Lauf mit `-W error` deckte zusätzlich eine ungeschlossene Simulator-Socket-Ressource im Fehlerpfad auf. Ohne die verschärfte Warnungsbehandlung bestehen die Tests; der Befund ist unabhängig von der ReSpeaker-LED-Ursache, sollte aber separat bereinigt werden.

## Empfohlener Behebungsplan

### 1. Lifecycle-Verkabelung im Client korrigieren

Der Client muss nach erfolgreich aufgebauter UI-/Core-Verkabelung genau einmal `CLIENT_LIFECYCLE_STARTED` durch die kanonische Feedbackkette schicken. Beim geordneten Beenden muss `CLIENT_LIFECYCLE_STOPPING` so verarbeitet werden, dass der LED-Worker den Aufruf noch ausführt, bevor seine Queue geleert und der Controller geschlossen wird.

Wichtig ist eine definierte Reihenfolge. Ein nur asynchron eingereihtes Stoppereignis direkt vor `LedFeedback.shutdown()` kann wieder verloren gehen, weil `shutdown()` die Queue leert.

### 2. Ende-zu-Ende-Regressionstest ergänzen

Mindestens folgende Aussagen sollten automatisiert werden:

1. `DesktopApplication.start()` erzeugt einmal `client.lifecycle.started`.
2. Das Mapping führt zu `init_event` und anschließend `ready_state`.
3. Der LEFX-Service wird dadurch gestartet.
4. Ein zweiter Startaufruf erzeugt kein Duplikat.
5. Der Shutdown verarbeitet `client.lifecycle.stopping`, bevor die LED-Queue geschlossen wird.

Der Test darf nicht erst bei einem vorgefertigten `FeedbackDecision` beginnen, weil genau dort die heutige Lücke liegt.

### 3. Diagnosefähigkeit verbessern

Im Clientstatus beziehungsweise Diagnosemenü sollten mindestens sichtbar werden:

- Sink `available/detail`;
- LEFX-Service `running`;
- `render_count`;
- USB-Verbindungsstatus und letzter Fehler;
- Zeitpunkt des letzten tatsächlich gesendeten Frames;
- optional Anzahl verworfener/koaleszierter Frames.

Damit lässt sich künftig sofort unterscheiden: kein LED-Befehl, Engine steht, Gerät nicht erreichbar oder Hardwareframe wird gesendet.

### 4. USB-/Renderverhalten erst danach optimieren

Wenn die Animation nach Behebung des Startfehlers sichtbar, aber zu ruckelig ist:

- Renderloop und USB-Schreiben über eine „latest frame“-Mailbox entkoppeln, damit ein langsamer USB-Transfer nicht die Szenenzeit anhält;
- alternativ die konfigurierte FPS-Zahl auf einen realistisch erreichbaren Wert abstimmen;
- prüfen, ob `LED_EFFECT=5` bei längerer Laufzeit periodisch oder nach einem geeigneten Modusindikator erneut gesetzt werden sollte;
- einen instrumentierten 10- bis 30-minütigen Hardwarelauf mit Render-, Write- und Latenzmetriken ergänzen.

Ein blindes Senden jedes identischen statischen Frames ist nicht die bevorzugte Lösung: Es erhöht USB-Last, ohne den sichtbaren Zustand zu verbessern.

### 5. Nebenbefunde härten

- Alle Controllerzugriffe konsequent über den LED-Worker führen.
- `on_device_mute_changed` beim Austausch von `LedFeedback` erhalten.
- Prozessklassifikation für den echten `voice-stt-client` im Claim-Werkzeug verbessern.
- Launcher auf die künftig kanonische Arbeitskopie umstellen.
- Für Sichttests vorübergehend `brightness: 128` oder höher verwenden, ohne dies zwingend zum Produktdefault zu machen.

## Schlussbewertung

Die drei Repositories passen protokollseitig grundsätzlich zusammen. Serverereignisse, Clientmapping, LEFX-Effekte, USB-Transport und ReSpeaker-Firmwarepfad funktionieren isoliert und gemeinsam, sobald ein LED-Befehl tatsächlich eingereicht wird.

Der erste zu behebende Fehler liegt an der Grenze zwischen Anwendungslifecycle und Feedbacksystem des Desktop-Clients. Solange `client.lifecycle.started` nicht erzeugt wird, kann ein korrekt verbundener, exklusiv geöffneter und technisch funktionierender ReSpeaker nach dem Start dunkel bleiben. Die niedrigere reale Framerate und die Change-Detection sind wichtige Sekundärbefunde, aber nicht die Hauptursache der vollständig fehlenden Startanzeige.
