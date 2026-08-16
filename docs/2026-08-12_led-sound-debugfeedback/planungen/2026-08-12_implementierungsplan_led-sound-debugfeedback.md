# Implementierungsplan: LED-, Sound- und Debug-Feedback

**Stand:** 12. August 2026  
**Status:** implementiert und technisch abgenommen; siehe Abschnitt 11  
**Priorität:** akut / höchstes aktuelles Arbeitspaket  
**Federführendes Repository:** `voice-stt-client`

## 1. Kurzentscheidung

Der erste Umsetzungsschritt bleibt bewusst im Desktop-Client. Der Server und der
LEFX-V3-Controller werden für Vertrags-, Integrations- und Hardwaretests benutzt,
aber vorerst nicht geändert.

Die akute Umsetzung besteht aus vier zusammengehörenden Teilen:

1. Die vorhandenen, aber nie ausgelösten Client-Lifecycle-Ereignisse werden
   zuverlässig und genau einmal in den Feedbackpfad eingespeist. Dadurch erhält
   der LED-Ring beim Programmstart endlich seinen dauerhaften Grundzustand.
2. Genau acht ausgewählte, lizenzierte und nichtsprachliche Soundassets werden als eingebaute
   Programmressourcen ausgeliefert, robust aufgelöst und für den aktuellen
   Entwicklungsstand aktiviert.
3. Das bestehende deklarative Ereignismapping wird vorübergehend deutlich
   auffälliger eingestellt: heller, kontrastreicher und bei mehr fachlich
   interessanten Ereignissen sichtbar beziehungsweise hörbar.
4. Einige eng verwandte, risikoarme Nebenfehler werden mitgenommen: die zu oft
   eingeblendete Eventstream-Warnung, der beim LED-Neuaufbau verlorene
   Mute-Callback und eine datensparsame Ereignis-/Feedbackspur im Log.

Es wird für diesen akuten Schritt **keine neue allgemeine Profil- oder
Einstellungsarchitektur** gebaut. Die bestehende `feedback_mappings`-Konfiguration
ist bereits die richtige Schaltstelle. Sie wird zunächst als gut beobachtbare
Entwicklungskonfiguration genutzt. Eine gemäßigte Alltagsabstimmung folgt erst,
wenn die komplette Ereigniskette praktisch belegt ist.

## 2. Gesicherte Ausgangslage

| Bereich | Befund | Konsequenz |
| --- | --- | --- |
| LED-Lifecycle | `client.lifecycle.started` und `client.lifecycle.stopping` existieren in Enum, Konfiguration und Dokumentation, werden vom produktiven Client aber nicht ausgelöst. | Primäre Ursache im Client beheben. |
| LED-Engine | Der echte ReSpeaker bestand alle 13 Hardwareziele. Ein dreisekündiger `ready_state` erzeugte 65 Renderdurchläufe und 21 verschiedene Ringframes. | Kein vorsorglicher Umbau des Controllers. |
| Frameübertragung | Nur geänderte Frames werden per USB übertragen; das ist beabsichtigt. Die Engine rendert weiter. | Keine künstlichen identischen USB-Frames erzwingen. |
| Sichtbarkeit | Globale Helligkeit `64/255` zusammen mit intern gedämpften Ready-Farben ist praktisch sehr dunkel. | Für die Diagnosephase deutlich erhöhen. |
| Sound | In Projekt- und wirksamer Benutzerkonfiguration steht `sounds_enabled: false`; alle sieben Pfade sind `null`. | Das Ausbleiben ist derzeit erwartbares Konfigurationsverhalten. |
| Soundadapter | Es gibt nur ein `QSoundEffect`, dessen Quelle bei jedem Cue gewechselt und vorher gestoppt wird. | Zuerst reale Wiedergabe belegen; schnelle Cue-Folgen gezielt testen und nur bei nachgewiesenem Verlust begrenzt härten. |
| Sound-Paketierung | Die PyInstaller-Spezifikation enthält keine Sounds. Relative benutzerdefinierte Pfade werden nicht an einem stabilen Anwendungsroot aufgelöst. | Ausgewählte Assets bündeln und Pfadauflösung definieren. |
| Sound-Sammlung | Die Rohsammlung unter `assets/sound_effects/` ist vollständig ignoriert. Nur der Home-Assistant-Voice-PE-Teil enthält lokal eine eindeutige CC-BY-4.0-Lizenz. | Nur geprüfte Auswahl übernehmen; Rohsammlung bleibt ignoriert. |
| Reconnect-Hinweis | `client.event_stream.degraded` ist als technischer Tray-Zusatz gedacht, besitzt aber zusätzlich eine Overlay-Warnwirkung. | Overlay-Wirkung entfernen, Tray-Notiz erhalten. |
| Laufende Version | Der gestartete Client kommt derzeit aus `P:\DockerProjekte\voice-stt-client`, die zu ändernde kanonische Kopie liegt im Projektroot. Beide hatten bei der Untersuchung denselben Commit. | Abnahme zwingend aus der geänderten kanonischen Kopie; Startziel danach eindeutig festlegen. |

Festgehaltene Ausgangscommits:

- Client: `467a6b699b47`
- Server: `13c162950b94`
- LED-Controller: `aa2f14bd13dd`

## 3. Zielbild der Diagnosephase

Nach der Umsetzung gilt:

- Spätestens kurz nach erfolgreichem Clientstart zeigt der ReSpeaker einen
  hellen, animierten und dauerhaft erkennbaren Bereitschaftszustand.
- Wake Word, Aufnahme, Verarbeitung, Erfolg, Abbruch, Warnung und Fehler sind
  visuell klar unterscheidbar.
- Die acht Sound-Cues sind ohne lokale absolute Entwicklungspfade sowohl aus
  dem Repository als auch aus dem gebauten Programm abspielbar.
- Fachlich wichtige Liveereignisse erzeugen bewusst reichlich Feedback. Replay
  erzeugt weiterhin keine alten Lichtpulse oder Sounds.
- Technische Reconnect-Zwischenzustände dürfen im Ring und Log erkennbar sein,
  erzeugen aber nicht bei jedem normalen Neuverbinden das störende Overlay
  „Event-Feedback vorübergehend eingeschränkt“.
- Für jeden Feedbackentscheid steht im Debuglog eine kompakte Spur ohne Audio-
  oder Transkriptinhalt. So kann später insbesondere die doppelte Texteinfügung
  mit Ereignis-ID und Korrelation untersucht werden.
- Beim Beenden wird der Ring zuverlässig dunkel, auch wenn der eigentliche
  Lifecycle-Feedbackauftrag nicht mehr rechtzeitig verarbeitet werden kann.

## 4. Umfang und Reihenfolge

### Paket A – Arbeitskopie, Baseline und Gerätebesitz sichern

1. Den laufenden Client-Prozessbaum wie vom Projektinhaber erlaubt beenden, damit
   ReSpeaker und Audioausgabe für die Abnahme exklusiv verfügbar sind.
2. Vor Änderungen Status und Commit aller drei Repositories protokollieren und
   fremde lokale Änderungen unangetastet lassen.
3. Die vollständige Clienttestsuite, `compileall` und die bestehenden
   Konfigurations-/Feedbacktests als Implementierungsbaseline erneut ausführen.
4. Den Client für alle Entwicklungs- und Hardwareläufe ausschließlich aus
   `P:\GithubRepos\marcosudau-vps\voice-stt-client` starten.
5. Den tatsächlichen Autostart-/Shortcut-Pfad ermitteln. Er wird erst nach
   erfolgreicher Abnahme auf die kanonische beziehungsweise gebaute Version
   umgestellt; ein bloßes Ändern des falschen Checkouts gilt nicht als Lösung.

**Eingangstor:** Baseline grün, Gerät frei, genau eine bekannte Clientinstanz.

### Paket B – Lifecycle und LED-Grundzustand reparieren

1. `client.lifecycle.started` nach erfolgreichem Core-/Bridge-Start genau einmal
   veröffentlichen. Es darf weder vor einsatzbereitem Feedbackpfad noch bei
   fehlgeschlagenem Start gesendet werden.
2. Die daraus aufgelöste Regel muss wirklich am Qt-/LED-Adapter ankommen:
   `init_event` als Liveimpuls, danach `ready_state` als dauerhafter Zustand.
3. `client.lifecycle.stopping` genau einmal vor dem Adapterabbau auslösen. Die
   Shutdown-Reihenfolge wird so gestaltet, dass der konfigurierte Abschluss
   angewendet werden kann; `LedFeedback.shutdown()` bleibt trotzdem die harte,
   zeitlich begrenzte Garantie für `output off`.
4. Start und Shutdown bleiben idempotent. Ein zweiter `start()`- oder
   `shutdown()`-Aufruf erzeugt kein zweites Lifecycle-Feedback.
5. Beim Ersetzen von `LedFeedback` nach Reconnect oder Sinkwechsel den bereits
   vorhandenen `on_device_mute_changed`-Callback erneut übergeben. Danach wird
   die Mute-Leitung wieder durch den neuen Worker beobachtet.
6. Die Diagnosehelligkeit zunächst von `64` auf ungefähr `192/255` setzen. Die
   exakte Helligkeit wird am Gerät geprüft; sie darf für diese Phase auffällig,
   aber nicht blendend oder flackernd schmerzhaft sein.

**Automatisierte Nachweise:**

- erfolgreicher Start → genau ein `CLIENT_LIFECYCLE_STARTED`;
- Startfehler → kein Started-Ereignis;
- doppelter Start → weiterhin genau eines;
- Shutdown → genau ein Stopping-Ereignis und LED-Abschaltung;
- LED-Regelreihenfolge `init_event → ready_state`;
- LED-Reconnect/Sinkwechsel behält Failure- und Mute-Callbacks;
- vorhandene Thread- und Shutdown-Tests bleiben grün.

**Ausgangstor:** Der Ring startet am echten Gerät ohne vorheriges fachliches
Serverereignis und bleibt in einem klar erkennbaren Ready-Zustand aktiv.

### Paket C – Acht auslieferbare, nichtsprachliche Soundassets herstellen

1. Für den ersten integrierten Satz ausschließlich die lokal vorhandene Quelle
   `home-assistant-voice-pe_sounds` verwenden, weil für sie die Lizenz
   nachgewiesen ist: Home Assistant Voice Preview Edition Sounds, Clayton
   Charles Tapp, CC BY 4.0.
2. Die Kandidaten auf der realen Windows-Standardausgabe nacheinander anhören.
   Die Auswahl richtet sich zunächst nach Unterscheidbarkeit, nicht nach
   Eleganz. Naheliegende Ausgangskandidaten sind:

   | Cue | Kandidat für die Hörprobe |
   | --- | --- |
   | `wake_word` | `wake_word_triggered.flac` |
   | `start` | `center_button_press.flac` oder `mute_switch_off.flac` |
   | `stop` | `center_button_double_press.flac` oder `mute_switch_on.flac` |
   | `complete` | `timer_finished.flac` oder `easter_egg_tada.mp3` |
   | `cancel` | `center_button_double_press.flac` |
   | `warning` | `jack_disconnected.flac` |
   | `error` | `mute_switch_off.flac` |
   | `timeout_tick` | `easter_egg_tick.mp3` |

3. Die acht final gewählten Dateien mit reproduzierbaren `ffmpeg`-Befehlen in
   ein für `QSoundEffect` robustes PCM-WAV-Format konvertieren. Sehr lange
   Warn-/Fehlertöne werden auf einen markanten kurzen Abschnitt begrenzt; Pegel
   und Stille am Anfang werden vereinheitlicht.
4. Nur diese acht erzeugten WAV-Dateien unter einem neuen, versionierten
   Produktpfad wie `assets/feedback_sounds/debug/` ablegen. Die komplette
   Rohsammlung unter `assets/sound_effects/` bleibt ignoriert und wird niemals
   pauschal hinzugefügt.
5. Lizenz, Quelle, Änderungen/Konvertierung und Zuordnung in einer kleinen
   `LICENSES.md` beziehungsweise `ATTRIBUTION.md` neben den Assets festhalten.
6. Vor dem Commit explizit mit `git status --ignored` und `git diff --stat`
   nachweisen, dass keine übrige Sammlung versehentlich aufgenommen wurde.

**Ausgangstor:** exakt acht verwendete WAVs plus Attribution sind versioniert;
kein ungeklärtes oder unbenutztes Soundasset wird verfolgt.

### Paket D – Soundpfade, Paketierung und Wiedergabe robust machen

1. Eine zentrale Soundasset-Auflösung ergänzen:

   - absolute benutzerdefinierte Pfade bleiben unterstützt;
   - `~` bleibt unterstützt;
   - ausgelieferte relative Pfade werden stabil gegen den Anwendungsroot und im
     PyInstaller-Build gegen dessen Ressourcenroot aufgelöst;
   - ein zufälliges aktuelles Arbeitsverzeichnis darf das Ergebnis nicht ändern.

2. Die acht WAVs in `voice-stt-client.spec` als Daten aufnehmen. Der
   Build-Smoke muss zusätzlich prüfen, dass alle acht Ressourcen enthalten
   und durch Qt ladbar sind.
3. Die Repository-Standardkonfiguration mit den acht eingebauten Pfaden und
   `sounds_enabled: true` versehen.
4. Die existierende Benutzerkonfiguration unter `%LOCALAPPDATA%` nicht komplett
   überschreiben. Für die Abnahme wird eine Sicherung erstellt und nur der
   `feedback`-Abschnitt gezielt auf den Debugsatz gesetzt. Damit überstimmt die
   alte Kombination aus `false` und sieben `null`-Werten die neue
   Projektkonfiguration nicht weiter.
5. `SoundFeedback.apply_config()` muss eine geänderte Auswahl ohne Neustart
   übernehmen und seine einmaligen Fehlerphasen sauber zurücksetzen.
6. Eine schnelle Sequenz `wake → start → stop → complete` real testen. Falls das
   vorhandene Stoppen und Neuladen eines einzigen `QSoundEffect` dabei Cues
   nachweislich verschluckt, wird der Adapter minimal auf vorgeladene Cue-Player
   oder eine kleine begrenzte FIFO umgestellt. Keine unbeschränkte Audioqueue.
7. Einen kleinen manuellen Diagnoselauf bereitstellen, der alle acht Cues mit
   Namen und ausreichendem Abstand abspielt. Das ersetzt vorerst die größere
   gewünschte Feedback-Konfigurationsseite mit Preview-Schaltflächen.

**Automatisierte Nachweise:**

- relative, absolute, `~`- und fehlende Pfade;
- Source- und Frozen-Ressourcenroot;
- Sound deaktiviert bleibt still;
- jeder konfigurierte Cue wird dem richtigen Asset und seiner Lautstärke
  zugeordnet;
- fehlendes Asset und Qt-Backendfehler bleiben nicht fatal und werden nur
  begrenzt gemeldet;
- Rekonfiguration räumt alte Quellen/Fehlerphasen korrekt auf;
- Replay und unveröffentlichte Entscheidungen spielen weiterhin keinen Sound.

**Ausgangstor:** Alle acht Cues sind aus Source und gebauter EXE auf dem realen
Windows-Ausgabegerät hörbar.

### Paket E – Bewusst auffälliges Ereignismapping

Die bestehende YAML-Tabelle bleibt die einzige fachliche Zuordnung. Für die
Diagnosephase wird sie ungefähr nach folgender Matrix erweitert beziehungsweise
verstärkt:

| Ereignisgruppe | LED in der Diagnosephase | Sound |
| --- | --- | --- |
| Client gestartet | auffälliger Init-Impuls, danach heller animierter Ready-Zustand | kurzer Start-/Ready-Cue |
| Wake Word erkannt | deutlicher Wake-Impuls, danach klarer Wartezustand | `wake_word` |
| Hotkey akzeptiert | eigener kurzer Impuls plus Wartezustand | optional `wake_word`, wenn die Doppelmarkierung praktisch hilfreich ist |
| Aufnahme gestartet | kräftiger, eindeutig anderer Aufnahmezustand | `start` |
| Aufnahme beendet | klarer Wechsel in Verarbeitung | `stop` |
| Transkription gestartet | Verarbeitung bleibt sichtbar; kein unnötiges Zurücksetzen | zunächst kein zusätzlicher Ton, falls direkt auf `stop` folgend |
| Transkription abgeschlossen | langer grüner Erfolgspuls, danach Ready | `complete` |
| Leer verworfen/abgebrochen | klarer Ablehnungs-/Abbruchpuls, danach Ready | `cancel` |
| Transkription abgelehnt/fehlgeschlagen | langer roter Fehlerpuls, danach Ready | `error` |
| Aktion blockiert/Diktat unterbrochen | deutlich gelb/orange, danach sinnvoller Grundzustand | `warning` |
| Letzte Sekunden des Nachsprechfensters | ablaufender Grün-Gelb-Rot-Ring | `timeout_tick`, bei früher neuer Sprache sofort stoppen |
| Mikrofon verloren/wieder da | dauerhafter eigener Reconnect-Zustand / deutlicher Recovery-Puls | `warning` / optional `complete` |
| Texteinspeisung akzeptiert/erfolgreich | kurze, unterschiedliche Impulse ohne dauerhaften Zustand zu zerstören | zunächst LED-only, damit `completed` nicht sofort akustisch überfahren wird |
| Texteinspeisung fehlgeschlagen | roter Fehlerpuls | `error` |
| TTS gestartet/gestoppt | Speaking-Zustand / Rückkehr zu Ready | nur ergänzen, wenn diese Events im aktuellen Ablauf auftreten |
| Eventstream connecting/replaying/live | höchstens kurze Diagnoseimpulse und Logspur; fachlichen Diktatzustand nicht überschreiben | standardmäßig still |
| Eventstream degraded | technische Tray-Notiz und Logspur | kein Routine-Warnton |
| LED nicht verfügbar | Tray/Overlay und Log, naturgemäß kein LED-Selbsthinweis | optional `warning` |
| Sound fehlgeschlagen | Tray/Overlay und Log | kein Sound, um Rekursion zu verhindern |

Die endgültigen Effektziele werden nur aus dem bereits verifizierten LEFX-Katalog
gewählt. Unbekannte Ziele müssen weiterhin den Start mit einer klaren
Konfigurationsmeldung verhindern. Dauerzustände dürfen von Diagnoseimpulsen nicht
verloren gehen; nach einem Impuls muss der vorherige Zustand zurückkehren.

**Ausgangstor:** Ein vollständiger Diktatdurchlauf lässt sich ohne Logansicht grob
am Ring und an den Tönen nachvollziehen.

### Paket F – Eng verwandte Low-Hanging-Fruits

#### F1. Reconnect-Warntext nicht mehr bei normalen Übergängen einblenden

- Die `app: indicator.warning`-Wirkung von
  `client.event_stream.degraded` aus dem Standardmapping entfernen.
- Die technische Eventstream-Notiz im Tray/Tooltip erhalten.
- Fachliche Transportausfälle, Mikrofonfehler und echte blockierte Aktionen
  bleiben sichtbar und hörbar.
- Regressionstest: `CONNECTING → REPLAYING → LIVE` zeigt kein Warnoverlay;
  echter fachlicher Fehler tut es weiterhin.

Das ist die kleinstmögliche Korrektur und wahrt die bestehende AP07-Entscheidung,
dass Eventstreamdegradation technische Zusatzinformation ist.

#### F2. Kompakte Feedback-Entscheidungsspur

Für jede veröffentlichte beziehungsweise verworfene Entscheidung eine
strukturierte Debugzeile vorsehen mit:

- kanonischem Ereignisnamen;
- Quelle (`event_stream`, `stt_fallback`, `local`);
- Event-/Korrelations-ID, soweit vorhanden;
- Generation/Session in gekürzter oder unkritischer Form;
- `publish`, `duplicate`, `replay` und sichtbarem Reducerzustand;
- ausgewähltem Sound-Cue sowie LED-Verben/Zielen.

Nicht protokolliert werden Audio, Transkripttext, Tokens oder vollständige
Nutzdaten. Die Spur ist die risikoarme Vorarbeit für die später gewünschte
Logseite und hilft bei der getrennten Untersuchung doppelter Texteinspeisungen.

#### F3. Mute-Beobachtung nach LED-Neuaufbau

Der bereits in Paket B genannte Callback-Verlust wird mitbehoben, weil er direkt
im ohnehin anzufassenden LED-Lifecycle liegt und isoliert testbar ist.

## 5. Bewusst nicht Bestandteil dieses akuten Pakets

| Thema aus `Fehler_Änderungen.md` | Entscheidung | Begründung |
| --- | --- | --- |
| Text wird teilweise doppelt eingefügt | Noch keine Verhaltensänderung; nur Diagnose-/Korrelationsspur vorbereiten. | Ohne reproduzierten Pfad wäre ein Eingriff in Deduplizierung oder Injection zu riskant. Separates Diagnosepaket unmittelbar nach stabilem Feedback. |
| Große Feedback-Einstellungsseite mit In-App/Sound/LED-Unterseiten und Preview | Später. | Größerer UX-/Konfigurationsumbau; der kleine Cue-Diagnoselauf deckt die akute Abnahme ab. |
| Wake-Word-Mehrfachauswahl | Später. | Eigenes Server-/Client-Vertrags- und UI-Thema. |
| Logseite | Später; jetzt nur strukturierte Datei-Logs. | UI, Filterung, Datenschutz und Laufzeitbegrenzung brauchen ein eigenes Paket. |
| Server-Administration | Später. | Nicht mit Gerätefeedback gekoppelt. |
| Hotkey- und Wake-Word-Modi zu Hybridbetrieb zusammenführen | Nur Hintergrundinformation berücksichtigen. | Der bereitgestellte Betriebsmodi-Bericht beschreibt einen größeren künftigen Umbau; er soll laut Auftrag jetzt nicht umgesetzt werden. |

Die Diagnosekonfiguration darf die spätere Hybridisierung nicht erschweren:
Ereignisse bleiben deshalb kanonisch und triggerneutral. Es wird keine neue
Hotkey- oder Wake-Word-spezifische zweite Feedbacklogik eingeführt.

## 6. Erwartete Dateien und Repositorygrenzen

Voraussichtlich betroffen im Client:

- `ui/application.py` – Lifecycle-Auslösung, Feedbackspur, Adapterreihenfolge;
- `ui/feedback.py` – stabile Assetauflösung und gegebenenfalls begrenzte
  Wiedergabehärtung;
- `ui/led_feedback.py` – nur falls für eine testbare Shutdown-/Flush-Garantie
  erforderlich;
- `core/config.py` – ausschließlich falls der Ressourcenroot nicht sauber im
  Soundadapter gekapselt werden kann;
- `config.yaml` – Debughelligkeit, Soundpfade und auffälliges Mapping;
- `voice-stt-client.spec` – acht Soundressourcen;
- `assets/feedback_sounds/debug/` – acht WAVs plus Attribution;
- `scripts/` – reproduzierbare Assetkonvertierung oder Cue-Diagnoselauf;
- passende Tests in `tests/test_ui_application.py`,
  `tests/test_feedback_ui.py`, `tests/test_config.py`,
  `tests/test_feedback_mapping.py` und gegebenenfalls LED-Tests;
- Feedback-Guides, Roadmap/Übergabe und Abnahmenachweis nach erfolgreichem Lauf.

Im Server- und LED-Controller-Repository sind zunächst keine Produktivänderungen
geplant. Falls ein Abnahmetor dort einen reproduzierbaren Defekt zeigt, wird die
Ursache mit einem separaten Befund und einem kleinen Folgepatch behandelt, nicht
vorsorglich in diesem Paket versteckt.

## 7. Test- und Abnahmematrix

### 7.1 Automatisiert

Nach jedem Teilpaket fokussierte Tests, am Ende vollständig:

1. vollständige Clienttestsuite mit `voice-stt-client\venv\Scripts\python.exe`;
2. `compileall` über Anwendung, Core, UI, Skripte und Tests;
3. Konfigurations-, Mapping-, UI-, Sound-, LED- und Bridge-Tests mit Warnungen
   als Fehler, soweit die bestehende Teststruktur dies vorsieht;
4. PyInstaller-Onefile-Build und Versions-/Ressourcen-Smoke;
5. `git diff --check` und Kontrolle der tatsächlich verfolgten Sounddateien;
6. vollständige No-Hardware-Suite des LED-Controllers als Regression;
7. vollständige Serversuite beziehungsweise die kanonische Projektbaseline,
   obwohl dort keine Änderung vorgesehen ist, bevor der Live-E2E-Lauf beginnt.

Fehlschläge werden iterativ bis zu einer grünen Gesamtsuite debuggt. Teständerung
und Produktivänderung müssen gemeinsam nachvollziehbar bleiben; bestehende Tests
werden nicht nur passend gemacht, sondern gegen das gewünschte Verhalten
geschärft.

### 7.2 Echter ReSpeaker

1. Client beendet, exklusiven USB-Besitz prüfen.
2. Reinen LED-Diagnoselauf für alle im Mapping verwendeten Ziele ausführen.
3. Client starten, ohne eine Diktieraktion auszulösen:
   Init sichtbar, Ready spätestens nach kurzer Startphase dauerhaft sichtbar.
4. Ready mindestens zehn Minuten beobachten:
   Animation läuft, keine unerwartete Dunkelphase, kein unbeschränktes Queue-
   Wachstum, keine wiederholten USB-Fehlermeldungen.
5. Wake/Hotkey, Aufnahme, Verarbeitung, Erfolg, Abbruch, Warnung und Fehler
   gezielt auslösen und sichtbare Reihenfolge protokollieren.
6. Gerät trennen/wiederverbinden sowie manuellen Reconnect/Sinkwechsel prüfen;
   danach funktionieren LED und Mute-Taste weiterhin.
7. Client beenden: Ring wird innerhalb des konfigurierten Shutdown-Zeitfensters
   dunkel und das Gerät freigegeben.

### 7.3 Echter Sound

1. Windows-Standardausgabegerät und Lautstärke protokollieren.
2. Alle acht Cues über den Diagnoselauf einzeln hören und gegen den ausgegebenen
   Namen bestätigen.
3. Schnelle Cue-Folge testen und auf Abbruch/Verschlucken achten.
4. Ein fehlendes Asset absichtlich konfigurieren: genau eine begrenzte Meldung,
   Client und Diktat bleiben funktionsfähig.
5. Source-Start und gebaute EXE identisch prüfen.

### 7.4 Live-Ende-zu-Ende

Mit dem vorhandenen Live-Server, ohne Änderungen auf dem VPS:

1. Client startet und erreicht Eventstream `LIVE`.
2. Einen vollständigen Wake-Word-Durchlauf ausführen.
3. Einen vollständigen Hotkey-Durchlauf ausführen.
4. Je Durchlauf Serverereignis, normalisierte Cliententscheidung, LED-Auftrag,
   Soundauftrag und Texteinspeisung über IDs/Korrelation nebeneinanderstellen.
5. Eventstream kurz unterbrechen und wiederherstellen:
   Tray-Zusatz sichtbar, kein wiederholtes Warnoverlay, keine Replay-Sounds oder
   Replay-Lichtpulse, keine doppelte fachliche Wirkung.
6. Mindestens einen Abbruch- und einen Fehlerpfad auslösen.

## 8. Verbindliche Abnahmekriterien

Das akute Paket ist erst abgeschlossen, wenn alle folgenden Punkte erfüllt sind:

- Der Clientstart allein aktiviert den echten LED-Ring zuverlässig.
- Der Ready-Zustand bleibt animiert und mit der gewählten Diagnosehelligkeit gut
  sichtbar; die Engine wird nicht durch künstliche Dauer-USB-Frames verändert.
- Jeder der acht Sound-Cues ist aus Source und Build hörbar.
- Im Repository befinden sich genau die verwendeten acht Sounds plus
  Lizenznachweis, nicht die Rohsammlung.
- Ein realer Wake-Word- und ein realer Hotkey-Durchlauf zeigen die erwartete
  LED-/Sound-Reihenfolge.
- Replay löst keine alten Impulse aus.
- Normale Eventstream-Reconnects erzeugen nicht mehr wiederholt das störende
  Warnoverlay.
- LED-Reconnect und Sinkwechsel verlieren die Mute-Beobachtung nicht.
- Shutdown bleibt zeitlich begrenzt, Ring dunkel und USB-Gerät frei.
- Client-, Server- und LED-Regressionen sowie Build sind grün.
- Der tatsächlich im Alltag gestartete Client verweist auf die abgenommene
  Fassung, nicht auf einen unveränderten Zweitcheckout.
- Ergebnis, Testbefehle, Messwerte, gewählte Sounds und bekannte Restpunkte sind
  in einem Abschlussbericht unter `zusammenarbeit/berichte/` dokumentiert.

## 9. Empfohlene Commitfolge

Um Ursache und Wirkung prüfbar zu halten:

1. Lifecycle-/LED-Startfix plus Tests;
2. acht lizenzierte, nichtsprachliche Soundassets, Resolver und Paketierung plus Tests;
3. auffälliges Diagnosemapping und Reconnect-Warnkorrektur;
4. Callback-/Diagnoselog-Low-Hanging-Fruits;
5. Dokumentation, Build- und echter E2E-Abnahmenachweis.

Die Schritte dürfen während der Entwicklung lokal zusammenlaufen, sollen aber
inhaltlich so getrennt bleiben, dass ein problematischer Sound- oder Mappingteil
zurückgenommen werden kann, ohne den ursächlichen LED-Lifecycle-Fix zu verlieren.

## 10. Direkt anschließende Folgearbeit

Nach erfolgreicher Abnahme folgt als eigenes Paket:

1. die Diagnosematrix anhand der beobachteten echten Ereignisfolgen auf eine
   ruhigere Alltagskonfiguration reduzieren;
2. doppelte Texteinspeisungen mit der neuen Korrelationsspur reproduzieren und
   ursächlich beheben;
3. erst danach die größere Feedback-Konfigurationsseite und Logansicht planen;
4. die bereitgestellte Hybridmodus-Planung zu einem getrennten, server- und
   clientübergreifenden Arbeitspaket ausarbeiten.

## 11. Umsetzungsergebnis vom 12. August 2026

Der Plan wurde im Client-Repository umgesetzt. Server und LED-Controller
blieben produktiv unverändert. Die wesentlichen Nachweise:

- Lifecycle-Auslösung, auffälliges Mapping, robuste vorgeladene Soundplayer,
  PyInstaller-Ressourcen und datensparsame Feedbackspur sind implementiert.
- Acht ausschließlich nichtsprachliche Cues sind ausgewählt, reproduzierbar
  erzeugt, attribuiert und im Build enthalten.
- Der gewünschte Drei-Sekunden-Countdown verwendet im Hotkey- und Wake-Word-
  Modus autoritative Timer, spielt `timeout_tick` und zeigt den vorhandenen
  selbst rendernden LEFX-`countdown_ring`.
- Client: 451 Tests und `compileall` erfolgreich.
- Server: 378 Tests, 13 Skips und 78 Subtests erfolgreich.
- LED-Controller: 1.519 Nicht-Hardware-Tests erfolgreich; ein unabhängiger
  Windows-Test ist wegen seines `os.kill(pid, 0)`-Fehlers separat dokumentiert.
- Acht Sounds wurden über das echte Qt-Backend abgespielt. Der Countdown wurde
  am echten ReSpeaker mit frühem Clear und vollständigem Ablauf geprüft.
- Build 0.2.0: 73.747.530 Byte, SHA-256
  `0b43f3da0ed61304087a32d952ce1c42011f42a717b22c7027ac3888f8f8b7ac`.

Der vollständige, jederzeit übernehmbare Arbeitsstand liegt unter
`zusammenarbeit/arbeitsstaende/2026-08-12_led-sound-debugfeedback_uebergabestand.md`.
