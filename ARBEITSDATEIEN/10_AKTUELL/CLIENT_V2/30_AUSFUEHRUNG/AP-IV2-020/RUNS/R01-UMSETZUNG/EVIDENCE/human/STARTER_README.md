# Klickbarer Starter der isolierten V2-Testinstanz

Auf diesem Windows-PC liegt die Verknüpfung **V2-Testinstanz** auf dem Desktop.
Sie öffnet `test_instance_launcher.py` mit der Projektumgebung. Alternativ
`Start-V2-Testinstanz.cmd` in diesem Ordner doppelklicken.

- **Testinstanz starten** startet den vorhandenen Both-Testclient mit Logdienst.
- **CLIENT BEREIT** erscheint erst bei frischer Runtime-/Mikrofonbereitschaft.
- Bei laufender Qualifikationsinstanz bleibt der Startknopf gesperrt.
- **Einstellungen der laufenden Testinstanz öffnen** öffnet deren Dialog.
- Den Client über dessen Tray beenden. Schließen des Starters beendet ihn nicht.
- Keine Änderung von Wake-Schwellen, Nachsprechzeiten oder sonstigen Defaults.

Verwendet werden ausschließlich das vorhandene lokale `client-both.yaml` unter
`%LOCALAPPDATA%/VoiceSTT-Qualification/AP-IV2-020` und der vorhandene Testcontainer
`voicestt-qualification-iv2-020`. Ein gestoppter Container wird nach Prüfung von
Qualifikationslabel, exakter Image-ID und Loopback-Portbindung gestartet; es wird
kein Container angelegt oder aktualisiert. Docker Desktop muss verfügbar sein.
V1, VPS und andere Container werden nicht bedient. Der vorhandene Client-Mutex
bleibt die abschließende Instanzsperre auch bei konkurrierenden Startversuchen.

Der Starter läuft aus dem aktuellen Checkout, nicht aus einer Release-EXE.
Die vorhandene Runidentität und die passiven Ereignis-/Scorebeobachtungen bleiben
aktiv. Neue Startlogs liegen nur lokal in `launcher-logs/`; diese können private
Laufzeittexte enthalten und gehören nicht ungeprüft ins Repository.

Gezielte Regression: `venv/Scripts/python.exe -m unittest discover -s <dieser-Ordner>
-p test_instance_launcher_checks.py -v` mit `QT_QPA_PLATFORM=offscreen`.
Sie prüft den echten Qt-Startknopf sowie Doppelstart-, Profil-, Container- und
Prozessgrenzen ohne echten Serverstart, Audioaufnahme oder Textinjektion.
