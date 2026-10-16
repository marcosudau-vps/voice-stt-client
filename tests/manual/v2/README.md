# Wiederverwendbarer manueller V2-Testclient

Start im Repository mit der **Projektumgebung** (Python3.12, PySide6):

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2 --preview
.\venv\Scripts\python.exe -m tests.manual.v2 --cases manual
.\venv\Scripts\python.exe -m tests.manual.v2 --cases jarvis alexa --prepare-seconds 8
```

`--preview` zeigt nur die Oberfläche; Mikrofon/Client/Modelle bleiben aus.
Alle Schritte sind vorher sichtbar. Aktuell: blau hervorgehoben, kommende:
abgedunkelt, erledigte: Häkchen. Der separat lesbare Satz leuchtet beim Sprechen
grün auf. Rechts stehen Countdown oder verstrichene Wartezeit. Nach tatsächlicher
Client-/Audiobereitschaft bleiben standardmäßig **acht Sekunden Bereitmachen**;
`--prepare-seconds 0..30` ändert ausschließlich diese Testvorbereitung.
Serverfristen werden angezeigt und dadurch nicht verlängert.

Jede Aufgabe und jede Wiederholung benötigt einen eigenen Start. **Abbrechen**
beendet den eigenen Client regulär. Nach dem Versuch selbst **Wiederholen** oder
**Übernehmen** wählen. Erst nach Übernehmen wird die nächste Vorschau angeboten.
Die Clients laufen nacheinander, mit eindeutigen Attempt-IDs. Übernehmen/Exit0
ist keine automatische technische PASS-Wertung. Alle Versuche bleiben erhalten;
beim Wiederholen bleiben nur zuvor übernommene Aufgabentexte im Ziel erhalten.
Hotkeys kurz drücken und alle Tasten wieder loslassen.

## Voraussetzungen für echte Tests

Die vorhandene AP-IV2-020-Testumgebung wird wiederverwendet: isolierte Profile
`%LOCALAPPDATA%/VoiceSTT-Qualification/AP-IV2-020/client-{manual,wake}.yaml`,
eigene History/Cursor/Logs und lokaler Server auf Port18020 mit gepinntem
Servercommit `ada13b011e1d3829f78e7f389e3b927795a2b3be`, echten ASR-/Wake-Modellen
und ReSpeaker. Der Launcher startet oder verändert keinen Server und richtet
keine V1-Installation um. Profile bei Bedarf mit
`venv/Scripts/python.exe scripts/qualify_v2_session.py prepare` erzeugen;
vorhandene Testprofile werden dabei erhalten. Keine VPS-Instanz verwenden.

Die eigentlichen Transporte, Audio, Qt/Win32-Ausgaben und Controls bleiben
Produktkomponenten; `observed_session.py` ergänzt passive Diagnosen und schützt
das eigene Testziel gegen Einfügungen in fremde Fenster. Laufzeittext bleibt
lokal, exportierte Ereignisse enthalten nur IDs/Timing/Hashes.

Standardmäßig liegen Ergebnisse außerhalb Git unter dem lokalen `trials/`-
Verzeichnis. `--evidence <neues-Verzeichnis>` wählt explizit einen anderen Ort.
Öffentliche Nachweise vor dem Commit auf Herkunft/Datenschutz prüfen; keine
private History oder Zugangsdaten übernehmen. Nur die separat ausdrücklich
freigegebenen sechs Sprachfixtures des R01 sind im Repository versioniert.

## Prüfung der Testhilfen ohne Hardware

```powershell
.\venv\Scripts\python.exe -m unittest discover -v -s tests/manual/v2 -p test_*.py
$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m tests.manual.v2 --self-check
```

Diese Prüfungen simulieren Controllergrenzen bzw. bedienen echte Qt-Widgets,
erbringen aber keine realen Mikrofon-/ASR-/Hotkey-/Abnahmenachweise. Alte
AP-IV2-020-Einstiege unter EVIDENCE leiten kompatibel auf diesen gepflegten
Code weiter. Historische Versuchshashes bleiben an ihren Gitständen erhalten.
