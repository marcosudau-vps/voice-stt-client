# Entscheidungen und offene Punkte

**Stand:** 2026-08-25

**Phase:** fachliche Entscheidungen abgeschlossen / technischer Contract-Freeze

**Zweck:** zentrale Arbeitsdatei für alles, was vor der endgültigen
Zielbild- und Implementierungsplanung geklärt werden muss.

## 1. Geltung und Status

Diese Datei sammelt die im laufenden Dialog getroffenen oder vorbereiteten
Entscheidungen. Bei Widersprüchen zu älteren Planungs-, Zielbild- oder
Analyseartefakten gilt vorläufig diese Datei. Beim Plan-Freeze werden die
bestätigten Inhalte in `ZIELBILD.md` konsolidiert; erst danach werden
Arbeitspakete und Nachweise verbindlich zugeordnet.

Statusbegriffe:

- **BESTÄTIGT:** bestehende Kernrichtung, die weiterhin gelten soll.
- **BESPROCHEN:** fachlich gewünschte Richtung aus der aktuellen
  Entscheidungsrunde; noch in das konsolidierte Zielbild zu übernehmen.
- **OFFEN:** benötigt noch eine bewusste Entscheidung oder Präzisierung.
- **ÜBERHOLT:** ältere Aussage, die nicht mehr als Soll verwendet werden darf.

## 2. Weiterhin gültige Kernentscheidungen

| ID | Status | Entscheidung |
|---|---|---|
| CORE-01 | BESTÄTIGT | Es gibt genau einen serverseitigen Activation-, Recording-, VAD- und Finalisierungspfad. |
| CORE-02 | BESTÄTIGT | Manual/Hotkey und Wake Word sind gleichwertige Triggerquellen im Idle, keine Betriebsmodi. |
| CORE-03 | BESTÄTIGT | Der erste akzeptierte Activation-Trigger gewinnt; er öffnet genau eine Activation. |
| CORE-04 | BESTÄTIGT | Während der Activation öffnet ein weiterer Trigger keine zweite Activation und wechselt nicht die Triggerquelle. |
| CORE-05 | BESTÄTIGT | Der Server ist Autorität über den fachlichen Activation-Lifecycle; der Client spiegelt diesen Zustand. |
| CORE-06 | BESTÄTIGT | Der Audiostream ist an die Session und nicht an eine einzelne Activation gebunden. |
| CORE-07 | BESTÄTIGT | Lokales VAD darf keine unabhängige Manual-Aufnahmeautorität bilden. |
| CORE-08 | BESTÄTIGT | UI, Tray, LED und Sound stellen Lifecycle-Zustände grundsätzlich source-neutral dar. |
| CORE-09 | BESTÄTIGT | `session.mode` darf keine Runtime-Autorität besitzen. |
| CORE-10 | BESTÄTIGT | Neue Activations werden nach Schließen des Eingabefensters und Rückkehr des Vordergrundzustands nach `idle` zugelassen; ausstehende Final-Transkriptionen älterer Activations blockieren nicht. |

### CORE-11 – Mehrere Sprachsegmente innerhalb einer Activation

**Status: BESTÄTIGT / HEUTIGES VERHALTEN BEIBEHALTEN**

- Eine Activation darf null, ein oder mehrere **aufeinanderfolgende**
  Sprachsegmente enthalten.
- Nach dem VAD-Ende eines Segments wechselt sie in `followup_wait`. Beginnt
  dort erneut Sprache, startet ein weiteres Segment derselben Activation;
  `activationId` und ursprüngliche Triggerquelle bleiben erhalten.
- Segmente derselben Activation laufen nicht gleichzeitig. Der bestehende
  serverseitige Textpfad verarbeitet sie seriell.
- Erst Follow-up-Timeout, `finish`, `cancel`, Watchdog oder ein
  Fehler-/Recoverypfad schließt das Eingabefenster der Activation. Das Ende
  eines einzelnen Segments löst den Activation-/Trigger-Lock noch nicht.
- Nach dem Schließen des Eingabefensters wird der Vordergrund wieder `idle`
  und der Lock freigegeben, sobald Aufnahme/Gate geschlossen und alle
  Segmentjobs oder Verwerfungsterminals dauerhaft registriert sind. Noch
  laufende Final-Transkriptionen werden im Hintergrund nachgereicht.

### CORE-13 – Vordergrundzustand und Hintergrundverarbeitung

**Status: BESTÄTIGT**

- Die triggerrelevante Vordergrund-State-Machine und die Verarbeitung bereits
  angenommener Segmente sind getrennte Zustandsräume.
- Vordergrundphasen sind `idle`, `waiting_first_speech`, `segment_active`,
  `followup_wait` und der kurze technische Übergang `closing_input`.
- `finalizing` ist keine triggerblockierende Vordergrundphase. Eine
  geschlossene Activation darf als Hintergrundobjekt `draining` bleiben, bis
  jedes angenommene Segment genau einen terminalen Ausgang besitzt.
- Mehrere ältere Activations dürfen gleichzeitig beziehungsweise seriell in
  der Final-Pipeline ausstehen, während bereits eine neue Activation geöffnet
  ist. Jedes Ergebnis bleibt unveränderlich an seine ursprüngliche
  `activationId`, `segmentId` und Reihenfolgenummer gebunden.
- Final-Ergebnisse werden innerhalb einer Session in angenommener
  Segmentreihenfolge veröffentlicht; Fehler- und Verwerfungsterminals lösen
  die Reihenfolge ebenfalls auf und dürfen spätere Ergebnisse nicht dauerhaft
  blockieren.

### CORE-12 – Verbindungs- und Geräteverlust

**Status: BESTÄTIGT**

- Bricht die Serververbindung während einer Activation ab, wird diese
  Activation verworfen. Bereits veröffentlichter Text bleibt bestehen,
  unveröffentlichte Ergebnisse werden nicht in eine neue Session übernommen.
- Nach automatischem Reconnect beginnt eine neue Session im stabilen Idle;
  eine teilweise unterbrochene Activation wird niemals fortgesetzt.
- Der Verlust der ReSpeaker-/Audiogeräteverbindung beendet die Serversession
  nicht. Der Client versucht weiter, das Gerät wieder zu verbinden.
- Tritt der Geräteverlust während einer Activation ein, wird diese sofort
  gecancelt. Nach Geräte-Reconnect bleibt dieselbe Serversession verwendbar,
  sofern die Serververbindung selbst fortbesteht.

## 3. Wake Words

### WW-01 – Modelle und Serverkatalog

**Status: BESTÄTIGT**

- Wake-Word-Modelle werden mit dem jeweiligen Server-Build ausgeliefert.
  Ein Build kann eine kleine Auswahl oder den vollständigen vorgesehenen
  Katalog enthalten.
- Alle im Build enthaltenen und nicht global deaktivierten Modelle bilden den
  auswählbaren Serverkatalog, sofern ihre Artefakte grundsätzlich validiert
  und ladbar sind. Sie müssen dafür nicht alle gleichzeitig als
  Inferenzmodelle initialisiert sein.
- Einzelne enthaltene Modelle können serverseitig per Konfiguration global
  deaktiviert werden.
- „Verfügbar“ bedeutet: im Build enthalten, ladbar und nicht global
  deaktiviert.
- Der verfügbare Katalog muss – wie andere serverseitig aufgelöste
  Konfigurationswerte – vom Client abgefragt werden können.
- Pro Session wählt der Client ein oder mehrere Wake Words aus diesem
  verfügbaren Katalog aus. Nur diese ausgewählten Modelle werden beim Start
  der Session geladen/initialisiert und sind für die Session aktiv.
- Die Dateigröße eines Modells ist kein belastbarer Wert für seinen
  Laufzeitspeicher: Inferenzruntime, entpackte Tensoren, Featuremodelle,
  Zustandsbuffer und Allocator-Overhead kommen hinzu. Die Zielentscheidung
  vermeidet unnötige Modelle; konkrete RAM-/Startzeitbudgets werden mit ein,
  drei und der erwarteten Maximalzahl aktiver Modelle gemessen.
- Der aktuelle Server besitzt bereits einen passenden Ansatzpunkt: Die
  aufgelösten Session-Modellpfade werden an genau die für die Session erzeugte
  OpenWakeWord-Instanz übergeben. Katalog/Disable/Admission müssen diesen
  selected-only Pfad verbindlich machen und gegen Fallbacks absichern.

**Admission-Regel:** Enthält die Sessionauswahl mindestens eine unbekannte,
global deaktivierte oder nicht ladbare ID, wird die gesamte Auswahl atomar
abgelehnt. Es gibt weder Teilerfolg noch stillen Fallback auf andere Modelle.
Die Ablehnung nennt alle problematischen IDs maschinenlesbar.

**Nur noch technisch festzulegen:** Format und Versionierung des
Katalog-/Admission-Vertrags. Dafür ist keine weitere fachliche
Benutzerentscheidung erforderlich.

### WW-02 – Namen, IDs und tolerante Eingabe

**Status: BESPROCHEN**

- Intern und im Protokoll besitzt jedes Modell eine stabile kanonische ID.
- Benutzereingaben und Konfigurationswerte werden mindestens
  groß-/kleinschreibungsunabhängig aufgelöst.
- Explizite Aliase dürfen eine natürliche Kurzform abbilden, zum Beispiel
  `jarvis` auf den Anzeigenamen `Hey Jarvis`.
- Nach der Auflösung arbeitet das System nur noch mit der kanonischen ID; im
  UI kann weiterhin der Anzeigename erscheinen.

**Noch offen:** genaue Normalisierung, Aliasquelle und Verhalten bei
Alias-Kollisionen. Empfehlung: keine heuristische Entfernung beliebiger
Wörter, sondern normalisierte, explizit katalogisierte Aliase; Kollisionen
machen den betroffenen Alias ungültig.

### WW-03 – Aktive Wake Words und Empfindlichkeit

**Status: BESPROCHEN**

- Je Session darf genau ein Wake Word oder eine Liste mehrerer Wake Words
  aktiv sein – entsprechend der Sessionkonfiguration.
- Für alle in einer Session aktiven Wake Words gilt eine gemeinsame,
  konfigurierbare Empfindlichkeit.
- Der Server validiert und veröffentlicht den tatsächlich aufgelösten Wert.

**Noch offen:** Wertebereich, Default, Granularität der Konfiguration
(global oder zusätzlich je Session) und Verhalten bei einem vom Modell nicht
unterstützten Wert.

### WW-04 – Verbindliches Detection-Ereignis

**Status: BESPROCHEN**

- Das akzeptierte Ereignis muss eindeutig angeben, welches kanonische Wake
  Word erkannt wurde.
- Eine tatsächlich akzeptierte Wake-Word-Äußerung erzeugt fachlich genau ein
  verbindliches `wake_word_detected`-Ereignis und höchstens einen
  Activation-Versuch. Nicht akzeptierte Kandidaten erzeugen kein solches
  fachliches Ereignis.
- Wiederholte Rohdetektionen aus demselben Audiobereich werden vor dem
  fachlichen Ereignis gebündelt oder unterdrückt.
- Cooldown/Rearm ist ein konfigurierbares Timing. Es ist kein Ersatz für eine
  saubere Bündelung derselben Äußerung.
- Diagnose darf Rohdetektionen sichtbar machen, muss sie aber klar vom
  akzeptierten fachlichen Ereignis trennen.
- Der heutige OpenWakeWord-Adapter wertet je Audiotakt den jeweils neuesten
  Score aus; ein einzelner Score oberhalb des Schwellwerts reicht dort für
  einen Treffer. Bei mehreren gleichzeitigen Kandidaten gewinnt aktuell der
  höchste Score. Eine zusätzliche Mehrfach-Chunk-Bestätigung existiert in der
  Integrationsschicht nicht.
- Der aktuelle Recorder setzt nach einem Treffer zwar
  `wakeword_detected = True`, führt die Detection in den Folgechunks aber ohne
  entsprechenden Guard weiter aus und kann den Callback bei anhaltend hohem
  Score erneut aufrufen. Das erklärt den gemeldeten Mehrfachsignalpfad
  technisch.

**Noch offen:** genaue Bestätigungs-, Debounce-/Rearm-Regel und erforderliche
Eventfelder gegen Fehlalarme. Verbindlich ist bereits: Der erste akzeptierte
Treffer setzt sofort einen fachlichen Latch; bis zum Unlock wird keine weitere
Wake-Word-Detection akzeptiert oder als fachliches Ereignis veröffentlicht.
Eine willkürliche Forderung nach fünf oder zehn aufeinander folgenden
Treffern wird nicht vorab festgelegt: Bei etwa 32 ms pro aktuellem Audiochunk
würde sie zusätzliche Latenz erzeugen. Zuerst werden Scoreverläufe realer
positiver und negativer Audiodaten aufgezeichnet. Eine kleine Mehrheitsregel
wie `2 aus 3` wird nur bei belegtem Bedarf zusätzlich eingeführt.

### WW-05 – Verhalten während einer Activation

**Status: BESPROCHEN**

- Nach Annahme einer Activation ist bis zum Unlock keine semantische
  Wake-Word-Auswertung für die Triggersteuerung erforderlich.
- Ein währenddessen gesprochenes Wake Word hat keine direkte Trigger-,
  Finish-, Cancel- oder Refresh-Wirkung.
- Das gesprochene Audio bleibt normales Activation-Audio. Wenn VAD darin
  Sprache erkennt, wirkt diese Sprache wie jede andere Sprache auf den
  Inaktivitätstimer.
- Es wird weder eine zweite Quelle in die laufende Activation gemerged noch
  ein weiteres fachliches `wake_word_detected` benötigt.

### WW-06 – Pause, Reconnect und Neustart

**Status: BESPROCHEN**

- Wake-Word-Pause ist ein Laufzeit-Bedienzustand, der einen automatischen
  Reconnect übersteht.
- Admission und Reconnect müssen den gewünschten Pausenzustand ohne
  unbeabsichtigtes Aktivierungsfenster wiederherstellen.
- Bei einem vollständigen Neustart der Client-Anwendung startet Wake Word
  immer aktiv; die Laufzeitpause wird nicht persistent gespeichert.
- In einer Wake-Word-only-Konfiguration darf das Pausieren vorübergehend zu
  null wirksamen Activation-Triggern führen.

**Bedienentscheidung:** Es gibt einen dritten, separat konfigurierbaren
Hotkeyplatz für Pause/Fortsetzen der Wake-Word-Erkennung. Er darf ungebunden
bleiben; Tray-Bedienung kann zusätzlich bestehen.

**Noch offen:** Besitzer und Protokollrepräsentation des reconnect-festen
Laufzeitzustands sowie konkrete Default-Tastenkombination und
Konfliktvalidierung.

### WW-07 – ReSpeaker-Mute

**Status: BESPROCHEN**

- Hardware-/Firmware-Mute des ReSpeaker bleibt eine rein clientseitige
  Gerätefunktion: Mikrofon stumm, Mute-LED an, LED-Ring aus.
- Der Server muss diesen Gerätezustand nicht kennen.
- Hardware-Mute und Wake-Word-Pause sind voneinander unabhängige Zustände.
- Bei Hardware-Mute kommt kein verwertbares Mikrofonsignal an; daraus folgt
  ohne zusätzliche Serverlogik auch keine Wake-Word-Erkennung.

### WW-08 – Pre-Roll und Feedback

**Status: BESTÄTIGT / TIMINGWERTE OFFEN**

- Audio-Pre-Roll ist in Millisekunden konfigurierbar; `0` bedeutet kein
  Pre-Roll.
- Das erkannte Wake Word selbst darf nicht Teil des Nutztranskripts werden.
  Direkt anschließende Sprache im selben Sprachfluss muss dagegen vollständig
  zum Transkript gehören und darf am Satzanfang nicht abgeschnitten werden.
- Detector-History und für die Transkription freigegebener Audioanfang müssen
  deshalb getrennt behandelt und über reale Audiodaten fein abgestimmt werden.
- Zuverlässige Zustands- und Detection-Signale werden server-/protokollseitig
  bereitgestellt. Die konkrete optische und akustische Darstellung bleibt im
  Feedback-System des Clients konfigurierbar.

**Noch offen:** exakter Bezugspunkt, Obergrenze und Default der Audiofreigabe
nach der Wake-Word-Grenze.

## 4. Hotkeys und Activation-Steuerung

### HK-01 – Konfigurierbare Rollen

**Status: BESPROCHEN**

- Der primäre Hotkey hat im Idle bei aktiviertem Manual-Trigger immer die
  Wirkung `activate`.
- Während einer Activation erhält derselbe Hotkey eine konfigurierbare
  Steueraktion: `refresh`, `finish`, `cancel` oder `none`.
- Zusätzlich gibt es einen zweiten, separat belegbaren Activation-Control-
  Hotkey. Im Idle hat er standardmäßig keine Wirkung; während einer
  Activation ist seine Aktion ebenfalls konfigurierbar.
- Ein dritter, separat konfigurierbarer Hotkeyplatz ist ausschließlich für
  Pause/Fortsetzen der Wake-Word-Erkennung vorgesehen. Er kann ungebunden
  bleiben und ist keine dritte Activation-Control-Aktion.
- Sinnvolle Ausgangsbelegung für den Plan-Freeze:
  primärer Hotkey = `refresh`, zweiter Hotkey = `finish`, `cancel` zunächst
  ungebunden; der dritte Hotkeyplatz toggelt Wake-Word-Pause, sofern ihm eine
  Taste zugewiesen wurde. Die konkreten Tasten bleiben konfigurierbar.
- Eine globale nackte Escape-Taste sollte nicht ungeprüft als fester Default
  registriert werden, weil sie in vielen Anwendungen eigene Bedeutung hat.
- Ist Manual als Activation-Quelle deaktiviert, startet der primäre Hotkey im
  Idle nichts. Activation-Control darf aber weiterhin eine durch Wake Word
  gestartete Activation steuern.

**Noch offen:** endgültige Default-Tasten, zulässige Mehrfachbelegungen,
Konfliktvalidierung und Verhalten bei identischen Belegungen.

### HK-02 – Nicht kumulatives `refresh`

**Status: BESPROCHEN**

`refresh` ist ausdrücklich keine Zeitgutschrift und nicht kumulativ:

```text
neue Deadline = Zeitpunkt der letzten gültigen Interaktion
               + konfigurierter Inaktivitäts-Timeout
```

Bei zehn Sekunden Timeout bedeutet dreimaliges Drücken nicht dreißig
Sekunden. Jeder gültige Druck setzt lediglich denselben Timer auf zehn
Sekunden ab diesem Druck zurück – analog zu neu erkannter Sprache durch VAD.

- Nur in `followup_wait` ersetzt `refresh` Generation oder Deadline des
  laufenden Inaktivitäts-/Follow-up-Timers.
- In `waiting_first_speech` gilt `refresh` ausdrücklich nicht.
- Während `segment_active` setzt `refresh` ausschließlich den separaten
  Daueraufnahme-Sicherheitswatchdog. Dessen initiale Deadline beträgt zehn
  Minuten; nach menschlicher Interaktion gilt mindestens drei Minuten Restzeit:
  `max(bisherige Deadline, refresh-Zeitpunkt + 180 s)`. Ein früher Druck darf
  die längere initiale Restzeit nicht verkürzen. Es beeinflusst dort keinen
  Follow-up-Timer und darf keine spätere Verlängerung ansparen.
- Es gibt im Zielmodell kein `pending_extension` und kein über mehrere
  Interaktionen addiertes Zeitguthaben.
- In `closing_input`, `idle` und für bereits im Hintergrund drainende
  Activations ist `refresh` wirkungslos beziehungsweise wird definiert
  abgelehnt.

### HK-03 – `finish` und `cancel`

**Status: BESTÄTIGT / PHASENMATRIX FACHLICH EINGEFROREN**

- `finish`: Eingabe für die Activation schließen, eine gegebenenfalls aktive
  Aufnahme geordnet beenden und alle bereits angenommenen Segmente regulär
  finalisieren/verarbeiten. Der Trigger-Lock wird nach dem sicheren
  Eingabeschluss freigegeben; auf vollständige Segment-Terminals wird dafür
  nicht gewartet.
- `cancel`: Eingabe sofort schließen, laufende bzw. ausstehende Verarbeitung
  dieser Activation abbrechen oder deren Veröffentlichung zuverlässig
  unterdrücken und alle noch ausstehenden Ergebnisse verwerfen.
- Jedes angenommene Segment erhält auch bei Fehler, Queue-Verwurf oder Cancel
  genau einen terminalen Ausgang; kein Finalisierungszähler darf hängen.
- Jeder **akzeptierte** `finish`- oder `cancel`-Command erzeugt unabhängig von
  vorhandenen Segmenten ein korreliertes fachliches Lifecycle-Ereignis. Ein
  Command-Ack allein ersetzt dieses Ereignis nicht.

Verbindliche Phasenmatrix:

| Phase | `finish` | `cancel` |
|---|---|---|
| `idle` | `not_active`; kein Lifecycle-Ereignis | `not_active`; kein Lifecycle-Ereignis |
| `waiting_first_speech` | Activation ohne Transkript schließen; genau ein korreliertes Finish-Ereignis | Activation ohne Transkript abbrechen; genau ein korreliertes Cancel-Ereignis |
| `segment_active` | nach `closing_input`, Aufnahme geordnet beenden, Job dauerhaft zuordnen, danach `idle`; Final läuft im Hintergrund | nach `closing_input`, Aufnahme stoppen, Verwerfung registrieren, danach `idle` |
| `followup_wait` | Eingabe sofort schließen und nach `idle`; angenommene Verarbeitung läuft im Hintergrund weiter | Eingabe schließen, unveröffentlichte Resultate terminal verwerfen und nach `idle` |
| `closing_input` | idempotente Zustands-/Ack-Rückmeldung; keine zweite Transition und kein zweites Lifecycle-Ereignis | idempotente Zustands-/Ack-Rückmeldung; keine zweite Transition und kein zweites Lifecycle-Ereignis |

Exactly-once-/Retry-Regel:

- Wiederholung derselben `commandId` liefert dasselbe Ack, erzeugt aber kein
  zweites Lifecycle-Ereignis.
- Ein späterer Finish-/Cancel-Command nach bereits erfolgter Transition erhält
  eine definierte Antwort wie `already_input_closed` oder `stale_activation` und
  erzeugt ebenfalls kein zusätzliches Lifecycle-Ereignis.
- „Immer ein Event“ bedeutet genau ein Ereignis pro neu angenommener
  Zustandsänderung – auch ohne vorhandenes Segment –, nicht ein Ereignis pro
  Tastendruck oder Netzwerk-Retry.

Cancel-Grenze:

- Bereits vor Annahme des Cancel veröffentlichter oder vom Client eingefügter
  Text wird nicht zurückgenommen.
- Ab Annahme des Cancel darf kein weiteres Nutzresultat dieser Activation
  veröffentlicht oder eingefügt werden.
- Laufende Inferenz darf technisch zu Ende rechnen, wenn sie nicht sicher
  abbrechbar ist; ihre Veröffentlichung wird dann zuverlässig unterdrückt und
  das Segment erhält dennoch genau einen verwerfenden terminalen Ausgang.

**Nur noch technisch festzulegen:** konkrete Wire-Eventnamen/-felder und
Fehlercodes. Die fachliche Wirkung und Idempotenz sind vollständig entschieden.

### HK-04 – Überholte Aussagen

**Status: ÜBERHOLT**

- „Der normale Hotkey bedeutet während jeder Activation immer `finish`.“
- „Der normale Diktat-Hotkey darf `extend` niemals auslösen.“
- „Mehrfaches Extend darf Sekunden aufsummieren oder für später ansparen.“
- „Ein während der Activation erkanntes Wake Word wird als weitere Quelle
  derselben Activation gemerged.“

Diese Aussagen dürfen nicht mehr als Implementierungs- oder Test-Soll
verwendet werden.

## 5. Settings-Control-Plane

### SET-01 – Serverautorität und Einstellungsscope

**Status: BESTÄTIGT**

- Letzte Autorität über server- und sessionswirksame Einstellungen ist immer
  der Server. Nur vom Server validierte und bestätigte Werte sind wirksam.
- Sessionwerte – insbesondere Wake-Word-Auswahl, Sensitivity und
  Activation-Timings – dürfen pro Session von den Serverdefaults abweichen.
- Serverweite Defaults und globale Funktionen wie Modellaktivierung oder
  globales Wake-Word-Disable sind admin-geschützte Servereinstellungen.
- Der Client darf beide Klassen über eine Server-API abfragen und verändern.
- Rein lokale Geräte-/Bedienfunktionen bleiben clientseitig. Dazu gehören
  Serveradresse/TLS-Verbindungsdaten, Admin-Credential, physische
  Hotkeybelegungen, Audio-/ReSpeaker-Gerätewahl, Hardware-Mute,
  Windows-Autostart, Fenster-/Tray-Verhalten, Textinjektion sowie die gesamte
  Feedbackkonfiguration für In-App-, Tray-, Overlay-, Sound- und LED-Feedback.
- Der Server kennt keine physische Hotkey-Semantik. Der Client übersetzt
  Tastendrücke in fachliche Commands wie `activate`, `refresh`, `finish` oder
  `cancel`; nur deren zustandsabhängige Wirkung gehört dem Server.
- Der Server kennt keine ReSpeaker-spezifischen Zustände. Für den fachlich
  nötigen Activation-Abbruch genügt ein generisches Signal wie
  `audio_available=false`; Geräteart, Mute-LED und Wiederverbindung bleiben
  Clientverantwortung.
- Der Server veröffentlicht zuverlässige Domain-Events; wie der Client daraus
  Farbe, Text, Sound oder LED-Verhalten ableitet, ist ausschließlich
  Clientverantwortung.

### SET-02 – Änderbarkeit und Apply-Policy

**Status: BESTÄTIGT / EINZELWERTE NOCH ZUZUORDNEN**

- Sessionwerte dürfen auch während einer bestehenden Session geändert werden,
  wenn ihre Apply-Policy das erlaubt.
- Ein Wert, der einen Session-Reconnect benötigt, wird nicht in die alte
  Session hineingezwungen. Er wird über eine neue Session wirksam.
- Der Server veröffentlicht je Einstellung mindestens Scope, Auth-Anforderung,
  Datentyp/Wertebereich, Default, effektiven Wert und Apply-Policy.
- Eine laufende Activation besitzt einen unveränderlichen Snapshot ihrer
  wirksamen Einstellungen. Änderungen beeinflussen sie niemals rückwirkend.
- Die Detailmatrix verwendet `live`, `next_activation`,
  `next_session/reconnect` oder `server_restart`. `server_restart` bleibt auf
  fundamental unvermeidbare Serverparameter beschränkt.
- Erfordert eine Änderung während einer Activation einen Reconnect, fragt der
  Client vor dem Apply:
  1. sofort reconnecten und die Activation abbrechen;
  2. Activation regulär beenden und danach automatisch reconnecten;
  3. Änderung vormerken und erst bei einem später manuell ausgelösten
     Reconnect anwenden.
- Ohne ausdrückliche Auswahl wird eine laufende Activation niemals allein
  wegen einer Einstellungsänderung gecancelt.

### SET-03 – Servereinstellungen und Admin-Authentifizierung im Client

**Status: BESTÄTIGT**

- Der Einstellungsdialog erhält eine eigene Seite für serverweite
  Einstellungen.
- Ohne Admin-Authentifizierung ist die Bearbeitung gesperrt. Ein Feld für den
  Admin-Key schaltet sie nach erfolgreicher Serverprüfung frei.
- Der Admin-Key darf auf ausdrücklichen Wunsch dauerhaft gespeichert werden.
  Er wird dafür im Windows Credential Manager abgelegt, nicht in YAML oder als
  normaler Registrywert über `QSettings`.
- Die Client-UI kann den gespeicherten Key anlegen, ersetzen und vollständig
  löschen. `QSettings` darf nur nicht geheime Metadaten wie die
  „dauerhaft speichern“-Auswahl oder einen Credential-Verweis halten.
- Ist der Credential-Speicher nicht verfügbar, bleibt der Key nur im Speicher
  der laufenden Anwendung; es gibt keinen unsicheren Klartext-Fallback.
- Der vorhandene Serverunterbau aus öffentlicher `/api/config`-Abfrage,
  Admin-Key-Prüfung und geschützten Änderungsendpunkten wird ausgebaut statt
  parallel neu erfunden.

### SET-04 – Abgrenzung dieses Arbeitsblocks

**Status: EMPFEHLUNG FÜR PLAN-FREEZE**

- Dieser Arbeitsblock implementiert das gemeinsame Settings-Vertragsfundament,
  alle Trigger-/Wake-Word-/Timing-Einstellungen sowie die gesperrte
  Servereinstellungsseite als tragfähige Erweiterungsbasis.
- Die vollständige Migration fachfremder Einstellungsdomänen bleibt im
  späteren Settings-Arbeitsblock, nutzt dann aber denselben Contract und
  dieselbe UI-Infrastruktur.

### SAFE-01 – Schutz vor versehentlicher Daueraufnahme

**Status: BESTÄTIGT / EXAKTE WERTEBEREICHE OFFEN**

- `segment_active` besitzt einen großzügigen, serverautoritativen und pro
  Session konfigurierbaren Sicherheitswatchdog. Der bestätigte Default beträgt
  zehn Minuten; der genaue zulässige Wertebereich wird im Settings-Contract
  festgelegt.
- VAD-Aktivität setzt diesen Watchdog nicht zurück, weil dauerhafte Sprache
  etwa von einem Fernseher gerade der abzusichernde Fehlerfall ist.
- Ein gültiges `refresh` in `segment_active` gilt als menschliches
  Anwesenheitssignal. Die neue Deadline ist
  `max(bisherige Deadline, Zeitpunkt + 180 Sekunden)`: drei Minuten ab letzter
  Interaktion, ohne Verkürzung einer noch längeren Restzeit und ohne
  kumulatives Zeitguthaben.
- Eine konfigurierbare Vorwarnung mit 30 Sekunden Default erzeugt ein
  zuverlässiges Signal für das Client-Feedback.
- Bei Ablauf endet die gesamte Activation; sie fällt nicht in
  `followup_wait` zurück und benötigt für eine neue Aufnahme einen neuen
  Trigger.
- Das bis zum Ablauf erfasste Segment wird wie bei `finish` regulär
  verarbeitet. Der Schutzablauf darf die investierte Sprechzeit nicht ohne
  aktive Anwenderentscheidung verwerfen.
- Queue-Grenzen sind ebenfalls großzügige Schutzgrenzen. Ein Erreichen darf
  niemals still Segmente verlieren; jedes verworfene Segment behält seinen
  terminalen Ausgang.

Übergreifender Schutzgrundsatz: Aufgenommenes Audio wird ohne aktive
Anwenderentscheidung nur verworfen, wenn Verarbeitung oder sichere
Weiterführung technisch nicht mehr möglich oder nachweisbar unvertretbar ist.
Der Verwerfungsgrund muss dann sichtbar und terminal nachverfolgbar sein.

## 6. Noch zu härtende Architekturverträge

### A-01 – Exakte Serverphasen

**Status: BESTÄTIGT / WIREDETAILS IM TECHNISCHEN CONTRACT**

- Kanonische triggerrelevante Phasen: `idle`, `waiting_first_speech`,
  `segment_active`, `followup_wait`, `closing_input`.
- Der Lock gilt in allen Phasen außer `idle` und endet erst nach sicherem
  Eingabeschluss, nicht bereits beim bloßen VAD-Aufnahmeende.
- Hintergrundzustände geschlossener Activations sind davon getrennt;
  `draining` blockiert keine neue Activation.
- Exits, Timeouts, Recovery und Wire-Abbildung werden im technischen Contract
  festgeschrieben.

### A-02 – Client-Resynchronisierung

**Status: TECHNISCH EINGEFROREN**

- Der Client erfindet nie selbst `idle`; bei Eventlücke wechselt sein Mirror
  auf `resyncing` und fordert `session.snapshot` an.
- `eventSeq`, `stateVersion` und `sessionId` schützen gegen Lücken und stale
  Zustände.
- Reconnect erzeugt eine neue Session in `idle`; alte Activations werden
  niemals fortgesetzt. Die Laufzeit-Suppressionsmaske wird atomar im neuen
  Handshake übergeben.

### A-03 – Timings und Konfigurationsautorität

**Status: TECHNISCH EINGEFROREN / KALIBRIERWERTE MESSDATENABHÄNGIG**

- Der Server veröffentlicht für jeden Wert Scope, Auth, Default, Wertebereich,
  Requested/Effective Value, Apply-Policy und `settingsRevision`.
- Der Server bleibt Autorität für alle Activation-/VAD-/Wake-Timings; der
  Client besitzt keine konkurrierenden Deadlinewerte.
- Verbindliche Activation-/Watchdogwerte und Bereiche stehen im technischen
  Contract. Wake-Word-Grenzwerte dürfen nur innerhalb des Contracts anhand
  der vorgesehenen Audio-/Score-Messungen kalibriert werden.

### A-04 – Protokollidentitäten und Idempotenz

**Status: TECHNISCH EINGEFROREN**

- `protocolVersion`, `clientRunId`, `sessionId`, `activationId`, `segmentId`,
  `segmentSequence`, `commandId`, `eventId`, `eventSeq`, `stateVersion` und
  `settingsRevision` besitzen die im technischen Contract definierte
  Owner-/Lebensdauer.
- Command-Replay, Payloadkonflikt, Eventdeduplizierung, stale IDs und
  Snapshotannahme sind für Protokollversion 2 festgelegt.

### A-05 – Legacy und Browser

**Status: BESTÄTIGT**

- Der Browserclient wird später auf die neue Architektur nachgezogen und
  setzt für diesen Arbeitsblock keine Kompatibilitätsanforderung.
- Der Desktop-Client ist der maßgebliche Konsument dieses Umbaus.
- Im Repository wird eine versionierte Kompatibilitätsmatrix geführt, aus der
  unterstützte Desktop-Client-/Server-/Protokollversionen sowie nach
  Möglichkeit konkrete Commitgrenzen hervorgehen.
- Die Migration ist ein klarer Protokollschnitt. Client und Server werden
  koordiniert auf die neue Version umgestellt; alte Runtime- und
  Legacy-Adapter werden nicht mitgeschleppt.
- Nicht passende Versionen erhalten beim Handshake eine klare
  Inkompatibilitätsmeldung und starten keine teilweise funktionsfähige Session.

### A-06 – Effektive Triggerkonfiguration

**Status: TECHNISCH EINGEFROREN**

- Eine dauerhaft gespeicherte Basiskonfiguration muss mindestens eine
  funktionsfähige Triggerquelle enthalten. `manual=false` und
  `wake_word=false` werden nicht persistent als Startkonfiguration akzeptiert.
- Während der Client-Programmlaufzeit darf ein bewusster Laufzeitzustand mit
  null effektiven Triggern entstehen.
- Manual und Wake Word besitzen getrennte Laufzeit-Suppressionszustände. Eine
  zusätzliche Wrapper-Aktion „alle Trigger pausieren“ wird nicht eingeführt.
- Dieser Laufzeitzustand übersteht Server-Reconnect, neue Session,
  Serververbindungsverlust und Geräteverlust/-Reconnect, solange dieselbe
  Client-Anwendung läuft.
- Ein vollständiger Client-Neustart verwirft die Laufzeitsperren und beginnt
  wieder mit der funktionsfähigen Basiskonfiguration.
- Basiskonfiguration und reconnect-feste Laufzeit-Suppressionsmaske müssen im
  Snapshot klar getrennt sichtbar sein.
- Activation-Control-Hotkeys bleiben unabhängig von
  `manual_trigger_enabled` verfügbar, damit auch eine durch Wake Word
  gestartete Activation gesteuert werden kann.

## 7. Nachweisbare Ist-Abweichungen

- Der ältere Server-Follow-up-Pfad verwendet bereits Generationen und
  ersetzt damit laufende Timer.
- Der neue `ActivationController` im Server-Workspace addiert aktuell
  `extension_seconds` in `_pending_extension` und lässt Tests dieses
  kumulative Verhalten erwarten. Das widerspricht HK-02 und wird als
  `FIND-010` nachverfolgt.
- Mehrfach ausgelöste Wake-Word-Detection-Signale pro gesprochener Äußerung
  sind als beobachtetes Verhalten gemeldet. Der Adapterbefund „ein neuester
  Score über Schwellwert genügt, keine Mehrfach-Chunk-Regel“ und der fehlende
  Detection-Guard nach gesetztem `wakeword_detected` sind als technischer
  Mehrfachsignalpfad bestätigt (`FIND-011`).

## 8. Plan-Freeze

Fachliche Härtungsrunde und technischer Contract-Freeze sind abgeschlossen.
`TECHNISCHER_CONTRACT_FREEZE.md` konkretisiert Phasen, Hintergrundledger,
Timer, IDs, Wire, Snapshot, Settings, Wake Words, Kompatibilität und Recovery.
`IMPLEMENTIERUNGSPLAN.md` zerlegt die Umsetzung strikt in getrennte
`AP-SRV-*`- und `AP-CLI-*`-Pakete; `AP-INT-*` ändert keinen Produktcode.

Die Umsetzung kann mit den Baselinepaketen und anschließend AP-SRV-010
beginnen. Neue fachliche Rückfragen sind nur erforderlich, wenn die
Implementierung eine bislang nicht beschriebene Nutzerwirkung aufdeckt.
