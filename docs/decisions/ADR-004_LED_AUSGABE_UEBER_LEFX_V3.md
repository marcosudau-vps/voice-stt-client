# ADR-004 – LED-Ausgabe über den eingebetteten LEFX-V3-Controller

Status: angenommen  
Datum: 2026-08-10  
Löst ab: [ADR-003](ADR-003_RESPEAKER_XVF3800_USB_LED_ADAPTER.md) in den Punkten
USB-Zugriff, Prozessisolation und Wirkungskatalog. Was ADR-003 zum Replay-Schutz
und zur einmaligen Fehlermeldung festgelegt hat, gilt unverändert weiter.

## Kontext

ADR-003 gab dem Client einen eigenen USB-Adapter mit vier Firmware-Modi und
zehn typisierten `LedEffectId`-Wirkungen. Das war für AP07-M9 angemessen: Es
brauchte eine ausfallisolierte Anzeige und sonst nichts.

Inzwischen existiert **LEFX V3** (`led-controller-version-3`) als eigenständiges,
veröffentlichtes System: ein Effektschema mit drei Lebenszyklusformen, ein
Katalog aus 36 Effekten und 71 Presets, eine Engine mit Ebenen-Komposition und
eine Gerätezuordnung über Ports. Derselbe Kern läuft eingebettet in einem
Thread, in einem eigenen Prozess oder als Dienst.

Zwei Systeme, die denselben LED-Ring ansteuern, sind eines zu viel — ein
WinUSB-Handle ist exklusiv, ein Parallelbetrieb ist technisch ausgeschlossen.
Und die zehn Wirkungen des Clients deckten rund ein Sechstel dessen ab, was der
Katalog kann.

## Entscheidung

- Die LED-Ausgabe läuft **ausschließlich** über `lefx.interfaces.ControllerService`,
  eingebettet im Client-Prozess. Der Client fasst den LED-Teil des Geräts nicht
  mehr selbst an. Das Audiogerät bleibt davon unberührt.
- Der bisherige direkte Adapter entfällt **ersatzlos**. Es gibt keinen
  Konfigurationsschalter zurück und keinen Parallelbetrieb.
- `feedback_mappings` steigt auf **`schema_version: 2`**. Eine Regel nennt ein
  LEFX-Verb (`set_state`, `clear_state`, `emit_event`, `set_output`) und den
  Effekt oder das Preset, das es adressiert. Mehrere Aufrufe pro Regel werden
  als Liste geschrieben und der Reihe nach ausgeführt.
- **Es gibt keine automatische Migration von Schema 1.** Der Wertevorrat ist ein
  anderer; zu raten, welcher Katalogeintrag mit `recording` gemeint war, würde
  stillschweigend ändern, was der Ring zeigt. Schema 1 wird mit einer Meldung
  abgelehnt, die den neuen Weg nennt.
- **Effektparameter werden im Client nicht validiert.** Geprüft wird die Form:
  bekanntes Verb, genau eines, nicht leeres Ziel, `config` ist ein Mapping. Ob
  ein Parameter zulässig ist, entscheidet der Katalog. Eine zweite Kopie jedes
  Effektschemas im Client wäre in dem Moment veraltet, in dem ein Set
  aktualisiert wird.
- **Nur ein Thread ruft LEFX auf.** Ein Befehl rendert im aufrufenden Thread,
  und ein Rendern kann auf einem USB-Transfer stehen. Der bestehende
  `LedFeedback`-Worker bleibt die einzige Aufrufstelle; aus dem Qt-Thread wird
  nie aufgerufen.
- Die Warteschlange fasst zusammen, was zusammengefasst werden darf: Ein
  neuerer Zustand überholt einen noch nicht ausgeführten Zustand desselben
  Slots. **Meldungen werden nie verworfen** — jede ist eine eigene Aussage.
- **Der Sink ist die Instanz für Verfügbarkeit**, nicht der Rückgabewert eines
  Befehls. Weder der reSpeaker- noch der Simulator-Sink wirft aus `apply_frame`;
  beide melden über `status()`. Ein zurückgekehrter Befehl sagt nur, dass LEFX
  ihn angenommen hat.
- Beim Start wird **jedes** in `feedback_mappings` genannte Ziel gegen den
  geladenen Katalog aufgelöst. Ein unbekanntes Ziel ist ein Konfigurationsfehler
  und bricht den Start ab; **fehlende Hardware ist keiner** und darf den Start
  nie verhindern. Zur Laufzeit ersetzt nur eine geprüfte Konfiguration eine
  bereits geprüfte.
- Im gefrorenen Build wird die Entdeckung über Entry Points **umgangen**: Der
  Sink wird direkt instanziiert, die Katalogpfade werden explizit übergeben. Ein
  Onefile-Build trägt keine Distributionsmetadaten.
- Der Simulator ist ein **Diagnosewerkzeug**. Er liegt in `requirements-dev.txt`
  und wird vom Build ausdrücklich ausgeschlossen.

## Die Stummschaltung des Geräts

Am Gerät gemessen, nicht aus der Dokumentation abgeleitet. Firmware 2.0.10,
Build `ua-io16-sqr`:

- **Lesen funktioniert.** `GPO_READ_VALUES[1]` ist `X0D30` — der Funktions­zustand
  der Stummschaltung, nicht der Tastenzustand. Er liest gleich, egal wer ihn
  gesetzt hat, und ist damit die eine belastbare Auskunft darüber, ob das
  Mikrofon stumm ist.
- **Der Tastendruck erledigt alle drei Dinge auf einmal:** `X0D30` geht auf 1
  (Mute-LED an, Mikrofon in Hardware stumm) und `X0D33` fällt auf 0 — das ist
  die Stromversorgung des WS2812-Rings. Die normalen LEDs gehen also von selbst
  aus, ohne Zutun der Anwendung.
- **Die Stummschaltung wirkt wirklich.** Der aufgenommene Pegel fällt beim
  Tastendruck von mehreren hundert auf 1.
- **Lesen und Schreiben adressieren dieselben Pins verschieden.**
  `GPO_READ_VALUES` liefert fünf Pegel *in einer Reihenfolge* — X0D30 ist
  Position 1. `GPO_WRITE_VALUE` will dagegen die **Pin-Nummer**, für X0D30 also
  30. Wer die Position schreibt, bekommt keinen Fehler: Der Befehl wird über USB
  angenommen und bewirkt nichts, auf jedem Pin. Das sieht aus wie eine Firmware,
  die Hostzugriffe verweigert, und ist doch nur eine falsche Adresse. Nachgewiesen
  an den gefahrlosen Pins X0D11 und X0D39, die sich mit ihrer Nummer sauber
  setzen und zurücksetzen lassen.
- **Der Schreibzugriff schaltet Mute-LED und Mikrofon**, genau wie die
  Dokumentation es sagt. `GPO_WRITE_VALUE [30, 1]` bringt X0D30 auf 1, die LED
  leuchtet, der Pegel fällt flach auf 1 — im Wechsel viermal gemessen, offen
  gegen gesetzt: 71 / 1 / 155 / 1. Die Leitung hält, solange sie gesetzt ist.

  Eine frühere Messung schien das Gegenteil zu zeigen und war ein Messfehler:
  `AudioCapture` puffert bis zu 200 Blöcke, und das Leeren der Ergebnisliste
  leert nicht die Warteschlange. Gemessen wurde Ton von *vor* dem
  Stummschalten. Wer das nachmisst, muss nach dem Setzen eine Sekunde warten,
  bevor er Pegel zählt.

Daraus folgt die Aufteilung:

| | Wer kann es | Wie |
| --- | --- | --- |
| Gerät stummschalten (LED + Mikrofon) | Taste **und** Client | `GPO_WRITE_VALUE [30, 1]` |
| Zustand erkennen | der Client | `X0D30` im Sekundentakt auf dem Worker-Thread |
| Client stummschalten | der Client | Pakete im Verarbeitungsthread verwerfen |

Der Menüeintrag setzt deshalb `X0D30` — das schaltet Mute-LED und Mikrofon am
Gerät — und verwirft zusätzlich die Audiopakete im Client. Die zweite Hälfte ist
kein Ersatz, sondern die Zusicherung, die auch dann noch gilt, wenn der ReSpeaker
gar nicht angeschlossen ist: Ohne Gerät gibt es keine Leitung zu ziehen, und
stumm muss es trotzdem sein.

`set_device_mute` liest nach dem Schreiben zurück, statt sich auf den
Rückgabewert des Befehls zu verlassen; ist das Gerät nicht erreichbar, sagt der
Menüeintrag „nur Client", weil die LED dann dunkel bleibt und sonst der Eindruck
entstünde, es sei nichts passiert.

Umgekehrt folgt der Client der Leitung: Wird am Gerät stummgeschaltet, zieht die
Anwendung nach — Mikrofon aus, Häkchen im Tray, Ring aus. Ohne das würden Gerät
und Anwendung auseinanderlaufen, mit dunklem Ring und weiterlaufendem Datenstrom.

## Alternativen

- **Beide Wege parallel halten**, mit Konfigurationsschalter: verworfen. Zwei
  gepflegte Pfade für eine Anzeige, und der Rückweg hätte am direkten Adapter
  ohnehin Anpassungen gebraucht, die niemand mehr wollte.
- **`LedEffectId` behalten und im Adapter übersetzen**: verworfen. Billiger, aber
  friert den Client dauerhaft auf zehn Wirkungen ein; Overlays, Slots und Presets
  blieben unerreichbar, und es gäbe für immer zwei Vokabulare.
- **LEFX als eigener Prozess** statt eingebettet: verworfen für diesen Schritt.
  Der schmale Port (`core/led_controller.py`) hält den Weg offen — eine zweite
  Implementierung über `ControllerClient` berührt weder YAML noch Reducer.
- **Effektparameter im Client mitvalidieren**: verworfen, siehe oben.

## Folgen

- Neue Laufzeitabhängigkeit `led-controller-version-3==3.0.3`. `pyusb` und
  `libusb-package` entfallen als direkte Abhängigkeiten und kommen transitiv.
- **Die Prozessisolation aus ADR-003 entfällt.** Ein hängender USB-Aufruf kann
  nicht mehr per Prozessabbruch beendet werden. Abgefedert durch den
  USB-Timeout, der upstream von 100 000 ms auf 1 000 ms gesenkt wurde — erst
  dadurch bekommt die vorhandene Selbstheilungsschleife überhaupt eine Chance —
  und dadurch, dass `LedFeedback.shutdown()` einen nicht endenden Worker meldet.
- Drei zusätzliche Daemon-Threads: `lefx-render`, `respeaker-usb-monitor` und
  kurzlebige Verbindungsrückrufe.
- Der Ring kann echte Animationen zeigen und verbindet sich nach einem
  Kabelverlust selbstständig wieder — beides konnte der Vorgänger nicht.
- Effekte werden zur Laufzeit aus den `.lefxset`-Archiven importiert. Was sie
  importieren, muss im gefrorenen Build als `hiddenimports` stehen; derzeit
  `colorsys`, `math`, `random`. **Diese Liste ist bei Set-Updates mitzuführen.**
- `LedConfig` ist neu geschnitten: `sink`, `fps`, `effect_paths` und
  `simulation_offer_after_s` kommen dazu, `speed` entfällt. `brightness` behält
  seine 0..255-Skala und wird für LEFX durch 255 geteilt — eine Umskalierung
  hätte stillschweigend die Helligkeit aller bestehenden Konfigurationen
  geändert.
- Der Binärzuwachs beträgt rund 258 KB, weil FastAPI, Starlette, Pydantic und
  Uvicorn ausgeschlossen sind. Möglich wurde das durch eine Upstream-Änderung:
  `lefx.interfaces` löst `create_app` verzögert auf, und `API_PREFIX` liegt in
  einem eigenen abhängigkeitsfreien Modul.

## Betroffene Dokumente und Tests

- `core/feedback_mapping.py`, `core/led_controller.py`, `core/config.py`,
  `core/settings_metadata.py`
- `ui/led_feedback.py`, `ui/application.py`, `ui/tray.py`
- `config.yaml`, `requirements.txt`, `requirements-dev.txt`,
  `voice-stt-client.spec`
- `tests/test_feedback_mapping.py`, `tests/test_led_feedback.py`,
  `tests/test_config.py`, `tests/test_ui_application.py`,
  `tests/test_event_stream.py`
- `tests/manual_test_ap07_led_hardware.py`,
  `tests/manual_test_ap07_led_disconnect.py`,
  `tests/manual_test_ap07_led_endurance.py`,
  `tests/manual_test_ap07_adapter_failures.py`
- `docs/work-packages/LEFX_V3_LED_CONTROLLER_INTEGRATION_PLANUNG.md`
