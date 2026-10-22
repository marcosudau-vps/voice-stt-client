# LED-Muster und spätere Farbprofile – Untersuchung vom 18.10.2026

AP-IV2-020 / R01, Produkt `7bb564690911d52f6dfe884955ddeb6a27eea6ad`.
Die folgende Variante verändert ausschließlich das isolierte Both-Testprofil.
Farbprofile sind untersucht, aber ausdrücklich noch nicht implementiert.

## Auftrag und jetzt vorbereitete Vergleichsvariante

Der Auftraggeber möchte die Phasen nacheinander betrachten und ein durchgehendes,
von Farben unabhängiges Animationskonzept entwickeln. Der Aktivierungsblitz
gefällt und bleibt erhalten. Der bisher grüne Idle und der sehr langsam
umlaufende einzelne Wartepunkt gefallen nicht. Gewünscht für Warten: alle zwölf
LEDs, neun aufsteigende Stufen 10 bis 90 Prozent, danach dreimal 100 Prozent,
wesentlich schnellere Rotation, zunächst Weiß. Noch keine Farbprofilumstellung.

| Phase | Aktuelle Testvariante | Unverändert / noch offen |
| --- | --- | --- |
| Idle/Bereit | `ready_state`, Weiß statt Grün | Atmung und Helligkeit bleiben vorläufig; endgültiges Idle-Muster gemeinsam wählen |
| Aktivierung | bisheriger cyanfarbener Blitz | vollständige Aktivierungsregel unverändert |
| Warten auf erste Sprache | `palette_cycle`, weiße Helligkeitsrampe | 12 LEDs; 1,5 Umdrehungen/s als erster Vergleichswert |
| Nachsprechfenster | dieselbe rotierende Rampe | vorhandene 5000ms bleiben erhalten |
| Sprache, Verarbeitung, Ergebnis, Fehler, Warnung | bisherige Regeln | spätere Einzelbetrachtung; keine stillschweigende Änderung |

Die Rampe verwendet RGB-Kanäle `25,51,76,102,127,153,178,204,229,255,255,255`.
Das sind die gewünschten Stufen mit 8-Bit-Abrundung. `brightness=1.0`,
`speed=6.0`, `reverse=false`. LEFX `palette_cycle` hat eine Grundperiode von vier
Sekunden: 4/6 = 0,667s pro Runde. Bisheriges `waiting`: 3/0,28 = 10,714s.
Bei 30 FPS erfolgt der diskrete Positionswechsel ungefähr alle 55,6ms;
der vorhandene Effekt interpoliert nicht zwischen den LEDs.

Die globale Helligkeit bleibt **192/255**. „100 Prozent“ bedeutet hier volle
Musterhelligkeit innerhalb dieser vorhandenen Begrenzung. Optisch wahrgenommene
Helligkeit ist nicht linear und wurde nicht mit einem Lichtmessgerät gemessen.

Die wirksamen Phasenschlüssel sind `server.input.waiting`,
`server.input.followup` und `server.input.idle`. Es werden nur deren dauerhafte
LED-Zustände verändert. Bestehende Impulse, Sounds, App-Aktionen und insbesondere
`server.activation.started` bleiben erhalten. Der Feedback-Reducer projiziert
Phasenzustände ohne erneutes Abspielen von Sounds oder Aktivierungsimpulsen.

## Was heute bereits vorhanden ist

- `voice_stt_client/core/feedback_mapping.py`: deklarative Ereignisregeln mit
  LEFX-Verben, Effekt-/Presetnamen und Parametern. Die Parametergültigkeit prüft
  der echte LEFX-Katalog, nicht eine zweite clientseitige Schemaduplikation.
- `voice_stt_client/core/v2_feedback.py` und `feedback_reducer.py`: autoritative
  Phase → dauerhafter Zustand; Ereignisse → einmalige Impulse. Diese Trennung
  eignet sich für ein farbunabhängiges Musterkonzept.
- `voice_stt_client/core/led_controller.py`: explizites Laden der gebündelten
  Core-/Smartspeaker-Sets sowie zusätzlicher `led.effect_paths`. Quell- und
  Frozenbetrieb verwenden dieselbe Katalogstrategie. Die installierte Bibliothek
  enthält `palette_cycle`; eine neue Effektimplementierung ist dafür unnötig.
- `voice_stt_client/core/config.py`: typisierte lokale Konfiguration und
  `feedback_mappings`; bislang kein Farbprofilmodell oder aktiver Profilname.
- `voice_stt_client/ui/v2_application.py`: lokales Apply persistiert und
  ersetzt bei geänderten LED-/Feedbackeinstellungen den LED-Worker; bestehende
  Fehler-/Rollbackbehandlung sollte weiterverwendet werden.

Im Einstellungsdialog öffnet **„Lokale Geräte, Verlauf, Zwischenablage,
Darstellung und Diagnose …“** den lokalen Dialog. Unter **„Erscheinungsbild &
Feedback“** sind LED-Ausgabe/Grundhelligkeit, Sounds und Overlay vorhanden.
Ein vollständiger Editor für Effektparameter oder Farbprofile fehlt bislang.
Die Session-/Serververwaltungsseiten sind dafür fachlich nicht zuständig.

Es gibt aktuell **keine Client-Umgebungsvariable zur Farbprofilwahl**.
`VOICESTT_CLIENT_HOME` bzw. `VOICESTT_CLIENT_CONFIG` wählen den lokalen
Konfigurationskontext; sie sind kein Farbprofilsystem. Unbekannte zusätzliche
YAML-Wurzelfelder werden nicht durch bloßes Eintragen funktionsfähig.

## Konkrete Umsetzungsmöglichkeiten

1. **Bestehende Ereignisregeln konfigurieren:** funktioniert heute und ist der
   Weg dieser weißen Testvariante. Für jedes Ereignis müssen Farbparameter
   einzeln gepflegt werden. Das ist keine zentrale Profilumschaltung.
2. **LEFX-Presets verwenden:** wiederverwendbare Muster-/Farbkombinationen sind
   möglich. Ein Preset ersetzt aber keine konsistente Zuordnung aller Phasen
   eines Clients. Viele Farbkombinationen würden Musterdefinitionen duplizieren.
   Externe Katalogdateien erfordern zudem eindeutige Herkunft, Validierung und
   Build-/Laufzeitqualifikation. Für die jetzige Rampe nicht erforderlich.
3. **Empfohlen: lokale semantische Farbprofile plus Mustervorlagen.** Ein
   typisiertes Profil stellt Farben für Rollen bereit, etwa bereit, aktiv,
   Verarbeitung, Erfolg, Warnung und Fehler. Die Phasenvorlage bestimmt separat
   Effekt, räumliches Muster, Tempo, Dauer, Priorität und Helligkeitsverlauf.
   Ein kleiner Compiler erzeugt daraus die vorhandenen LEFX-Aufrufe. Transport,
   Serververtrag und Zustandsmaschine bleiben unverändert.

Beispiel eines möglichen zukünftigen Modells, noch kein gültiges heutiges YAML:

```yaml
led_theme:
  active_profile: neutral
  profiles:
    neutral:
      ready: '#FFFFFF'
      active: '#FFFFFF'
      processing: '#FFFFFF'
      success: '#FFFFFF'
      warning: '#FFFFFF'
      error: '#FFFFFF'
```

Für die Rampe erzeugt der Compiler aus `active` die zwölf Farben mittels
`scale_color(active, level)`. Ein einfaches Ersetzen aller Grautöne durch eine
einzige Farbe würde die Helligkeitsrampe zerstören. Andere Effekte verwenden
`color`, `colors`, `gradient` oder `secondary_color`; deshalb braucht jeder
Mustertyp eine ausdrückliche Farbbindung. Schwarze Masken, Transparenz und
Helligkeitsstufen dürfen nicht als beliebige Profilfarben behandelt werden.

Die noch gemeinsam festzulegende Musterfamilie sollte Bereitschaft ruhig,
aktive Eingabe deutlich bewegt und Verarbeitung erkennbar anders darstellen.
Fehler/Warnung müssen auch ohne Farberkennung unterscheidbar bleiben.
Das ist ein Entwurfsziel; die übrigen Muster werden hier nicht vorweggenommen.

## Änderungen und Prüfungen für eine spätere Produktumsetzung

- Typisierte Profildaten, Auswahl, Bereichsvalidierung und Default/Migration in
  `core/config.py`; klare Vorrangregel für bereits angepasste Benutzerregeln.
  Bestehende individuelle Einstellungen dürfen nicht still überschrieben werden.
- Muster/Farbrollen → vorhandene LEFX-Konfiguration übersetzen; kompilierte
  Aufrufe gegen den tatsächlich geladenen Katalog prüfen. Effekt-IDs, Tempo,
  Dauern, Prioritäten und globale Helligkeit bleiben vom Farbwechsel unabhängig.
- Lokaler UI-Selektor mit Vorschau, Übernehmen und Rückkehr zum vorherigen
  Profil; vorhandenen Apply-/Rollbackpfad weiterverwenden. Ein Farbwechsel
  darf keinen Aktivierungsblitz oder Sound erneut auslösen.
- Geräteverlust, Wiederanbindung, Reconnect und Neustart müssen den aktuellen
  Phasenzustand korrekt wiederherstellen. Hardware-Mute und ausgeschalteter
  Ring sind Sicherheitszustände und bleiben von Profilen unabhängig.
- Tests: identische zeitliche/räumliche Frames bei verschiedenen Grundfarben,
  Migration/benutzerdefinierte Regeln, unbekannte Profile, ungültige Farben,
  fehlende Effekte, Persistenz-/Applyfehler, Impulsfreiheit beim Umschalten,
  vollständige Windows-Regression sowie Source/Frozen-/ReSpeakernachweise.

Das wäre eine gesondert freizugebende Produktänderung außerhalb der jetzigen
reinen Konfigurationskalibrierung. Sie wurde auftragsgemäß nicht umgesetzt.

## Reproduktion, Nachweise und Rücknahme

Wiederverwendbarer Helfer:
[`led_waiting_variant.py`](EVIDENCE/human/led_waiting_variant.py).
Ohne `--apply` prüft er nur. Mit `--apply` verlangt er den nachweislich beendeten
eigenen Testclient, prüft Loopbackserver und unveränderte übrige Einstellungen,
erstellt ein lokales Bytebackup und ersetzt ausschließlich `client-both.yaml`.
`--output <JSON-Datei>` ist erforderlich. Danach den vorhandenen Teststarter
verwenden. Keine Aufnahme, private Gesamtkonfiguration oder History wird committed.

[SDK-Prüfung](EVIDENCE/led-white-variant/check.json),
[angewandte Variante mit Profilhash und lokalem Backuppfad](EVIDENCE/led-white-variant/applied.json).
Für Rücknahme: eigene Testinstanz beenden, dieses Bytebackup an die isolierte
Profiladresse zurückkopieren, dann neu starten. V1 und Server bleiben unberührt.

SDK-Frames und Konfigurationsisolation sind PASS. Reale Anbindung und Regression
werden gesondert im Evidenzordner dokumentiert. Tempo, Helligkeit und vorläufiger
Idle sind **noch nicht menschlich akzeptiert**. Die vollständigen AP-Pflichtfälle
bleiben offen; dies ist keine vollständige Hardwarequalifikation.
