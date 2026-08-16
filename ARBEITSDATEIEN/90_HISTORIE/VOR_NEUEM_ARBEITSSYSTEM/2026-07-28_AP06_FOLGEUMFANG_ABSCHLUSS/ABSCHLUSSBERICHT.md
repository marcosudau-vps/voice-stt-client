# Abschlussbericht – AP06 Folgeumfang

> **Datum:** 28. Juli 2026  
> **Ergebnis:** gesamter vereinbarter Codeumfang implementiert und technisch
> gehärtet  
> **Automatische Abnahme:** 257 Tests erfolgreich  
> **Formale Produktabnahme:** ein zusammenhängender realer Bedien-Smoke durch
> den Benutzer steht noch aus

## 1. Auftrag und Ergebnis

Der am 27. Juli konsolidierte AP06-Folgeumfang wurde auf dem bestehenden
technischen UI-Erststand umgesetzt. AP1–AP5 wurden nicht neu implementiert.
AP7-Funktionen wurden nicht vorweggenommen.

Umgesetzt sind:

- Hotkey- und Wake-Word-Betrieb über den sessionlokalen Serververtrag,
- sichere Queryerzeugung und Prüfung der effektiven Handshakekonfiguration,
- deterministische Behandlung von `session_config`/1008 ohne Reconnectstorm,
- kontrollierter Session-Reconnect bei Modus-/Profiländerungen,
- Hotkey-Diktatfenster über den autoritativen Server-VAD-Ereignissen,
- typisierte Konfiguration plus deklarative Metadaten,
- stabile Aktions-IDs und konfigurierbare native globale Hotkeys,
- atomare per-user Persistenz mit Kandidatenvalidierung und Rollback,
- Einstellungsdialog mit fünf Tabs,
- statische Mikrofonwahl und nicht blockierender manueller Mikrofontest,
- Verlaufspflege mit definierter Lösch-/Deduplizierungssemantik,
- optionales, fehlertolerantes Soundfeedback und erweiterte Statusdarstellung.

## 2. Betriebsmodus- und Serververtrag

`SessionConfig` kennt die Modi `hotkey` und `wake_word`.

Hotkey:

```text
wakeWordEnabled=false
```

Wake Word:

```text
wakeWordEnabled=true
wakeWords=hey_jarvis
```

Optionale veröffentlichte Tuningwerte werden URL-kodiert und jeder
Queryschlüssel wird höchstens einmal erzeugt. Im Hotkeymodus werden
Wake-Word-Detailfelder nicht unnötig mitgesendet.

Der Client prüft `effectiveWakeWordEnabled` sowohl in `hello.sessionConfig`
als auch in `ready.sessionConfig`. Eine fehlende, typfalsche oder
widersprechende Bestätigung gilt nicht als erfolgreicher Moduswechsel.
`fallbacks`, `warnings` und `ignoredFields` werden sichtbar protokolliert.

Ein harter `session_config`-Fehler blockiert weitere Verbindungsversuche bis
`reconfigure()` eine tatsächlich neue, lokal validierte Konfiguration
übernimmt. Bei einer Änderung aus dem Dialog wird ein aktives Diktat beendet
und niemals fortgesetzt. Bestätigt der Server die Kandidatenkonfiguration
nicht, stellt der Core die vorherige Konfiguration wieder her.

## 3. Hotkey-Diktatfenster

Der Client führt kein lokales VAD aus. Der Ablauf ist:

1. primärer Hotkey sendet `start`,
2. erst nach bestätigtem Serverstatus beginnt der Initial-Timer,
3. `recording_started` beendet nur den Timer derselben Session und Generation,
4. `recording_ended` öffnet das Follow-up-Fenster,
5. ein weiterer primärer Hotkeydruck verlängert das aktuelle Fenster oder
   merkt die Verlängerung für die kommende Follow-up-Phase vor,
6. nach Ablauf sendet der Client `stop` und beendet die lokale Audioaufnahme.

Defaults:

- Initial-Sprach-Timeout: 15 Sekunden,
- Follow-up: 3 Sekunden,
- manuelle Verlängerung: 15 Sekunden.

Timer tragen Token, Session-ID und Generation. Stop, Cancel, Reconnect,
Moduswechsel, Shutdown und ein neuer Timer entwerten alte Tasks. Ein
unterbrochenes Diktat bleibt gemäß ADR-002 beendet.

Im Wake-Word-Modus wird der Hintergrundstream nach heilbaren Reconnects neu
aktiviert. Eine bewusste Pause des Benutzers wird nicht automatisch aufgehoben.

## 4. Einstellungen und Transaktionen

`AppConfig` bleibt die einzige fachliche Wertquelle. Die unveränderlichen
`SettingDefinition`-Objekte beschreiben nur:

- Pfad, Label und Beschreibung,
- Typ (`STRING`, `INTEGER`, `FLOAT`, `BOOLEAN`, `CHOICE`),
- Tab/Gruppe/Reihenfolge,
- Grenzen, Optionen und Sichtbarkeit,
- Änderungswirkung (`IMMEDIATE`, `HOTKEY_REREGISTER`, `AUDIO_RESTART`,
  `SESSION_RECONNECT`, `APP_RESTART`).

Vor jeder Übernahme wird eine vollständige tiefe Kopie erstellt und
`validate()` ausgeführt. Der Einstellungsdialog besitzt:

1. Verlauf,
2. Allgemein,
3. Verbindung & Betriebsmodus,
4. Geräte & Audio,
5. Erscheinungsbild & Feedback.

Projektdefaults bleiben in `config.yaml`. Benutzereinstellungen werden unter
`%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` atomar gespeichert. Ein
unbekanntes Override-Feld verwirft den gesamten Override, damit keine stille
Teilübernahme erfolgt.

Hotkey-Neuregistrierung ist vollständig oder gar nicht: Der alte Satz wird
abgemeldet, der Kandidat vollständig registriert und bei jedem Konflikt wieder
auf den alten Satz zurückgerollt. Dasselbe Grundprinzip gilt für Audio- und
Sessionübernahme.

## 5. Verlauf und Feedback

Der Dialog zeigt einen größeren newest-first-Verlauf und bietet Reinsertion,
Einzellöschung sowie „Alles löschen“ mit Bestätigung. SQLite-Attempts werden
per Foreign-Key-Kaskade gelöscht. Die bereits gesehene Identität
`(session_id, segment_id)` bleibt im laufenden Prozess reserviert; ein
erneutes Serverduplikat wird daher nicht nach dem Löschen neu eingefügt.

Soundfeedback ist standardmäßig deaktiviert. Konfigurierte lokale Assets
werden über `QSoundEffect` nicht blockierend abgespielt. Fehlende Dateien oder
Audioprobleme blockieren weder UI noch Core. Es wurde bewusst kein
lizenzunklarer Sound als aktiver Default festgelegt.

## 6. Während der Härtung gefundene und behobene Probleme

1. Die erste Geräteauswahl erwartete `id`/`max_input_channels`, während
   `AudioCapture.list_devices()` tatsächlich `index`/`channels` liefert.
   Ohne Korrektur wären reale Mikrofone im Dialog unsichtbar geblieben.
2. Ein Session-Konfigurationsfehler hätte zunächst noch einen Backoff-Zyklus
   abgewartet. Der Runloop wechselt nun unmittelbar in den blockierten Zustand.
3. Ein erneuter primärer Hotkey während `STARTING` war zuerst wirkungslos.
   Die Verlängerung wird nun vorgemerkt und nach bestätigtem Start auf den
   Initial-Timer angerechnet.
4. Unbekannte Benutzer-Override-Felder wären durch die bestehende
   tolerante Deserialisierung still ignoriert worden. Nun wird der gesamte
   Override verworfen.
5. Der produktive Server lehnte `wakeWordEnabled=true` ohne Modell-ID ab:
   `session_config: ... kein verfügbares OpenWakeWord-Standardmodell`.
   Der bekannte logische Name `hey_jarvis` wurde deshalb als sichtbarer
   Projektdefault festgelegt. Der anschließende Live-Smoke war erfolgreich.
6. Ein laufender Settings-Apply könnte beim Programmende eine noch nicht
   bestätigte Kandidatendatei hinterlassen. Shutdown rollt einen ausstehenden
   Apply nun vor dem Core-Stopp zurück.

## 7. Geänderte Laufzeit- und Testdateien

Neu:

- `core/actions.py`
- `core/settings_metadata.py`
- `ui/settings_dialog.py`
- `ui/feedback.py`
- `tests/test_ap06_followup.py`
- `tests/manual_test_ap06_modes.py`

Wesentlich erweitert:

- `core/config.py`
- `core/stt_session.py`
- `core/controller.py`
- `core/history.py`
- `ui/core_bridge.py`
- `ui/hotkeys.py`
- `ui/application.py`
- `ui/tray.py`
- `ui/overlay.py`
- `ui/presentation.py`
- `config.yaml`
- `tests/test_ui_widgets.py`

Synchronisierte aktive Dokumentation:

- `README.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/PROJEKTUEBERSICHT.md`
- `docs/work-packages/AP06_UI_SHELL.md`
- `docs/work-packages/AP06_UI_SHELL_FOLGEUMFANG_AUSFUEHRUNGSAUFTRAG.md`
- `task.md`
- `ÜBERGABE.md`

## 8. Automatische Prüfungen

Baseline vor Änderung:

```text
Ran 239 tests
OK
```

Neue gezielte Härtung:

```text
Ran 18 tests
OK
```

Geprüft werden unter anderem:

- URL-Eindeutigkeit und Kodierung,
- effektiver Modus, Warnungen/Fallbacks und Moduswiderspruch,
- pausierter Reconnect bei Konfigurationsfehler,
- Layering und atomarer Schreibfehler-Rollback,
- vollständiges Verwerfen unbekannter Overrides,
- Metadatenpfade und typsichere Kandidaten,
- Initial-, Segment- und Follow-up-Phase,
- Verlängerung und stale Timeline-Events,
- nicht verfügbares Audiogerät ohne Laufzeitmutation,
- Verlaufslöschung bei erhaltener Deduplizierung,
- optionale Aktionshotkeys,
- fünf Tabs und Standardeditoren.

Vollständige Regression:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Ergebnis:

```text
Ran 257 tests
OK
```

Zusätzlich:

- `py_compile`: Exit-Code 0,
- Offscreen-Qt-Settings-Smoke: `QT_SETTINGS_SMOKE_OK`,
- Health/WebSocket-Test: `ALL TESTS PASSED`,
- sicherer Modus-Live-Smoke:

```text
✓ hotkey: effectiveWakeWordEnabled=False
✓ wake_word: effectiveWakeWordEnabled=True
AP06 MODE CONTRACT LIVE SMOKE PASSED
```

Der Live-Modus-Smoke sendet weder `start` noch Audio und führt keine
Textinjektion aus.

## 9. Noch fehlender realer Bediennachweis

Die Implementierung und alle ausführbaren automatischen/ungefährlichen
Live-Tests sind abgeschlossen. Nicht autonom prüfbar war die neue
Bediensemantik mit echter Sprache und der fokussierten Zielanwendung.

Der Benutzer muss noch den Katalog in
`MANUELLER_BEDIENDSMOKE.md` durchführen und die Ausgaben beziehungsweise
Beobachtungen zurückmelden. Bis dahin lautet der präzise Status:

> AP6-Codeumfang technisch abgeschlossen; formale Produktabnahme wartet auf
> den realen Mikrofon-/Hotkey-/Wake-Word-/Persistenz-Smoke.

## 10. Bewusst außerhalb AP6

- ReSpeaker-LED-Steuerung,
- Mikrofon-Hot-Plug und automatische Geräteheilung,
- Windows-Sleep/Wake,
- Multi-Monitor-/DPI-Härtung,
- Autostart und Packaging,
- Admin-API oder Admin-Key,
- lokales VAD oder lokaler STT-Fallback,
- Realtime-Textinjektion,
- Langzeit- und Belastungstests.
