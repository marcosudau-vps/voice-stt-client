# Manueller Bedien-Smoke für die formale AP06-Abnahme

Bitte in PowerShell im Projektordner ausführen:

```powershell
cd P:\DockerProjekte\RealtimeSTT_client
.\venv\Scripts\python.exe app.py
```

Öffne anschließend Notepad und stelle den Textcursor hinein.

## 1. Hotkey und Initial-Timeout

1. Prüfe im Einstellungsdialog, dass der Modus `hotkey` ist.
2. Drücke `Ctrl+Shift+Space`.
3. Sprich absichtlich nicht.
4. Warte mindestens 16 Sekunden.

Erwartung: Das Diktat endet unauffällig. Im Tray steht wieder „Bereit“; es
wird kein Text eingefügt.

## 2. Normaler Hotkeypfad

1. Drücke `Ctrl+Shift+Space`.
2. Sage: `Dies ist der AP sechs Abschlusstest.`
3. Bleibe anschließend ruhig.

Erwartung: Realtime-Text erscheint nur im Overlay. Nach Finalisierung und
Follow-up-Ablauf erscheint der Finaltext genau einmal in Notepad.

## 3. Follow-up mit zwei Segmenten

1. Starte erneut per Hotkey.
2. Sage: `Dies ist der erste Abschnitt.`
3. Pausiere ungefähr eine Sekunde.
4. Sage: `Dies ist der zweite Abschnitt.`
5. Bleibe ruhig.

Erwartung: Beide finalen Segmente werden jeweils genau einmal eingefügt; das
Diktat endet nach dem letzten Follow-up-Fenster.

## 4. Manuelle Verlängerung

1. Starte erneut.
2. Sage: `Vor der Denkpause.`
3. Drücke während der Aufnahme oder direkt danach noch einmal
   `Ctrl+Shift+Space`.
4. Pausiere ungefähr 6 Sekunden.
5. Sage: `Nach der verlängerten Denkpause.`

Erwartung: Der zweite Hotkeydruck stoppt nicht, sondern verlängert. Der zweite
Satz wird noch in demselben Diktatfenster verarbeitet.

## 5. Moduswechsel

1. Öffne im Tray `Einstellungen …`.
2. Wähle `wake_word`; `hey_jarvis` muss als Wake Word eingetragen sein.
3. Klicke `Anwenden` und bestätige den angekündigten Reconnect.

Erwartung: Die Anwendung erreicht wieder „Wake Word aktiv“. Es erscheint kein
Reconnect-Popup und keine Schleife aus Fehlermeldungen.

## 6. Wake Word, Pause und Fortsetzung

1. Sage: `Hey Jarvis`.
2. Diktiere: `Dies ist der Wake Word Abschlusstest.`
3. Warte auf den Finaltext.
4. Pausiere Wake Word über die primäre Tray-/Hotkeyaktion.
5. Sage erneut `Hey Jarvis` und einen Satz.
6. Aktiviere Wake Word wieder und wiederhole den Satz.

Erwartung: Vor der Pause wird genau einmal Text eingefügt. Während der Pause
erfolgt keine Aufnahme/Einfügung. Nach erneuter Aktivierung funktioniert der
Pfad wieder.

## 7. Persistenz

1. Beende die Anwendung über das Tray.
2. Starte sie erneut:

```powershell
.\venv\Scripts\python.exe app.py
```

3. Öffne den Einstellungsdialog.

Erwartung: Der zuletzt gewählte Modus und geänderte Einstellungen sind
erhalten. Die versionierte Projektdatei `config.yaml` wurde nicht verändert;
die Benutzerwerte liegen unter
`%LOCALAPPDATA%\RealtimeSTT Client\config.yaml`.

## Rückmeldung

Bitte für jeden Abschnitt `1` bis `7` entweder `OK` oder den beobachteten
Fehler nennen. Falls die Konsole Fehler ausgibt, die Ausgabe ab dem ersten
relevanten Status bis zum Fehler mitsenden.
