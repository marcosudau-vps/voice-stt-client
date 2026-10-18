# IV2-020-O01 – TV-Kontext, Hotkey und Hintergrundanzeige

18.10.2026, AP-IV2-020/R01. **Dokumentierter Realbefund / OPEN_INVESTIGATION**.
Kein bestätigter Overlayfehler nach Cancel. Clientprodukt7bb5646 und
Serverada13b0 unverändert; Paket bleibt wegen W01 BLOCKED/SERVER_FIX_REQUIRED.

## Menschliche Meldung

Der Auftraggeber meldet eine erneute ungewollte Aktivierung bei laufendem
Fernseher. Sprache wurde aufgenommen, anschließend sollte ein Hotkey abbrechen.
Das Overlay zeigt danach „Bereit“ und ein Diktat in Hintergrundverarbeitung,
das Tray wieder „Bereit“. Der sichtbare Zustand stammt aus menschlicher
Beobachtung; der Agent hat keinen aktuellen Screenshot erhoben. TV-Inhalt,
Mikrofon-PCM und Transkripttext werden nicht als Evidenz gespeichert.

## Gesicherter Ablauf, lokale Zeit MESZ

Session `b1482c4a-1b6c-43ba-b0d6-d1ef6b8d5f7d`, Generation1;
Activation `8788ef78-1bd9-417d-8b85-4f6cb9ce15c5`;
Segment `60da1174-b802-40a4-a38b-3a351f56fb6d`, Sequenz1.

| Zeit | Belegtes Ereignis |
| --- | --- |
| 03:57:03,553 | serverseitige Activation, Quelle `wake_word` |
| 03:57:03,566 | Alexa-Treffer, Score **0,834204912185669** |
| 03:57:06,644 | Sprachsegment startet; danach mehrere Realtime-Interims |
| 03:57:14,418 | primärer Hotkey; `refresh` bestätigt/applied |
| 03:57:15,093 | primärer Hotkey erneut; `refresh` bestätigt/applied |
| 03:57:15,601 | sekundärer Hotkey empfangen |
| 03:57:15,630 | Eingabe geschlossen, Grund **`finished`** |
| 03:57:15,660 | sekundäres Command **`finish`** bestätigt/applied |
| 03:57:15,641 serverseitig / ,700 Clientempfang | `transcription.accepted` für das Segment |
| 03:57:15,707 Clientempfang | Snapshot bestätigt Vordergrund `idle` |

Für diese Activation gibt es im aufgezeichneten Verlauf **kein `cancel`**,
kein `activation.cancelled` und bis zum gesicherten Beobachtungsende auch kein
`transcription.completed/failed/discarded` oder Activation-Terminal.
Zum Evidenzzeitpunkt blieb der Abschluss mindestens **299,7 Sekunden** nach
Eingabeschluss unbelegt. Transport/Audio/LED waren ready, Befehls-/Injektionsqueue
leer; elf Activations, davon zehn terminal. Der lokale Servercontainer lief
ohne Neustart und ohne gesetztes Container-OOM-Killed-Flag. Das schließt einen
Fehler eines einzelnen Workers oder einen verlorenen Abschluss nicht aus.

[Gefilterte Ereignisse, Textlängen/-hashes, Bindings, letzter Metrikstand](EVIDENCE/tv-wake-finish-20261018/live-analysis.json).
Keine private TV-Transkription wurde ausgegeben oder committed.

## 1. Unerwünschter Wake-Treffer bestätigt, akustische Ursache offen

Die Aktivierung stammt aus dem Server und nennt Alexa. Der laufende Fernseher
ist menschlich berichteter Kontext; ohne PCM ist nicht feststellbar, welche
Tonfolge den Treffer ausgelöst hat. Der vorherige Eingabeschluss lag rund
41 Minuten zurück. Dies ist **keine unmittelbar anschließende Reaktivierung**
wie W01; beide Fälle dürfen nicht ungeprüft dieselbe Ursache erhalten.

Der Score liegt unter dem bislang nur vorgeschlagenen Wert0,85. Dieser hätte
den konkreten protokollierten Treffer nicht zugelassen. Daraus folgt weder
eine qualifizierte neue Schwelle noch eine allgemeine Fehlerbehebung; die
positiven Wakephrasen, unmittelbare Nutzsprache und W01 bleiben separat zu prüfen.

## 2. Abbruchabsicht und tatsächliche Konfiguration weichen ab

Das isolierte Profil ist nachweislich so konfiguriert:

- Strg+Umschalt+F8: primär, bei offenem Diktat **Refresh**.
- Strg+Umschalt+F9: sekundär, bei offenem Diktat **Fertigstellen (`finish`)**.

`finish` beendet die Audioeingabe regulär und lässt akzeptierte Sprache im
Hintergrund weiterverarbeiten. `cancel` verwirft unveröffentlichte Ergebnisse.
Der gedrückte Hotkey wurde entsprechend seiner tatsächlichen Belegung korrekt
verarbeitet. Die menschliche Abbruchabsicht ist damit dokumentiert, ein
fehlgeschlagenes Cancel jedoch nicht nachgewiesen.

Für echten Abbruch ist im V2-Einstellungsdialog unter **„Lokale Trigger &
Bedienung“ → „Sekundäre Aktion bei offenem Diktat“ → „Abbrechen“** die vorhandene
Konfigurationsmöglichkeit verfügbar. Aktuell steht dort „Fertigstellen“.
Die Belegung wurde im Rahmen dieser Diagnose nicht verändert.

Quellen: `core/v2_controls.py::plan_control`,
`ui/v2_settings_dialog.py` (Auswahl Refresh/Fertigstellen/Abbrechen/Keine Aktion).

## 3. Bereit plus Hintergrundauftrag ist zunächst konsistent

`core/activation_mirror.py` markiert `activation.input_closed` als geschlossene
Eingabe mit Status `draining`, solange kein Activation-Terminal vorliegt.
`core/v2_feedback.py::project_feedback` zählt solche Activations als pending.
`ui/presentation.py::presentation_for_v2_snapshot` zeigt für Vordergrund-idle
„Bereit“ und ergänzt bei pending die Hintergrundverarbeitung im Tooltip.

`ui/tray.py` verwendet den kurzen Status für den Menüeintrag, aber den
vollständigen Text als Tooltip. `ui/overlay.py::_update_v2_status` zeigt diesen
vollständigen Tooltiptext. Beide erhalten dieselbe Präsentation; unterschiedlich
langer Text bedeutet hier keinen widersprüchlichen Lifecyclezustand.

Die länger anhaltende Anzeige passt zu einem **noch nicht terminal bestätigten
Verarbeitungsauftrag**. Dass dieser nach fast fünf Minuten noch offen ist,
ist ein gesonderter Verdacht im Verarbeitungs-/Abschlussweg, kein bestätigter
reiner UI-Anzeigefehler. Seine Ursache bleibt **NOT_PROVEN**. Einzeln zu prüfen:
Worker/Final-Inferenz, Zuordnung/Publication des Terminals und Snapshotinhalt.
Die aktuell vorhandenen Beobachter speichern Snapshot-Pendingeinträge nicht
vollständig; diese Diagnose darf keinen genauer bekannten Serverjobzustand
behaupten. Keine laufende Session wurde zur künstlichen Bereinigung neu gestartet.

## Prüfungen und Restaufgaben

[Gezielte bestehende Feedback-/Controlregression](EVIDENCE/tv-wake-finish-20261018/feedback-controls-regression.json),
[vollständiger Log](EVIDENCE/tv-wake-finish-20261018/feedback-controls-regression.txt.gz): **59 Tests PASS**.
Enthalten sind Ready mit Hintergrunddrains, Cancel-/Late-Result-Schutz und
Qt-Overlay-/Tray-Ausgabe. Keine Produkt-/Testsuiteänderung; kein neuer Build.
Diese modellfreien Regressionen erklären den Clientvertrag und ersetzen keine
Livequalifikation des offenen Serverabschlusses.

- Vor erneuter Sprachprobe bewusst zwischen Fertigstellen und Abbrechen wählen.
- Offenen Finalauftrag weiter untersuchen; Terminal/Snapshot/Workerpfad mit
  datensparsamer zusätzlicher Beobachtung eingrenzen, bevor ein Produktfix benannt wird.
- Unerwünschte TV-/Hintergrundtreffer als eigene Negativkalibrierung behandeln.
- Ein tatsächlich bestätigtes Cancel später gezielt auf Pendingabbau prüfen.

Der neue Befund wird lokal im Clientpaket gesichert. Das vorhandene Server-Issue7
betrifft den gesondert reproduzierten W01-Rearmfehler. Für O01 wurde kein neuer
Serverfix und keine Ergänzung an externe Issues beauftragt oder vorgenommen.
