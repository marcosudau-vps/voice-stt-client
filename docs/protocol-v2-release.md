# AP-CV2-110 – Paketierung und Diagnoseports

`VERSION` bleibt die Semverquelle. `setup.py` stempelt schemaVersion1,
version, clientCommit, sourceCommit und sourceDirty in
`voice_stt_client/build_identity.json` für Wheel und sdist. Beim Wheel-Rebuild
außerhalb Git übernimmt das sdist seinen Originalstamp. PyInstaller verwendet
denselben Stamp. Nur ein sauberer Produktstand trägt den echten Gitcommit;
Dirty oder fehlende Git-/Buildmetadaten liefern unknown. Installierte Pakete
lesen kein Git aus einem übergeordneten Checkout und übernehmen keine
Commitbehauptung aus Umgebungsvariablen.

`V2TransportConfig` verwendet Version und Commit als Hello-Defaults. Ein
expliziter Testtransport darf eigene Werte setzen. Empfangener Servercommit
bleibt unverändert; unknown ist kein Provenienznachweis.

Produktnamespace ist ausschließlich `voice_stt_client`. Enthalten sind
Config, drei gepinnte V2-JSON-Fixtures samt Schema/Vektoren/Provenienz, acht WAVs,
Buildidentität sowie die bestehenden LEFX-Kataloge im Frozenprodukt.
Icons entstehen durch den vorhandenen Qt-Painter. Simulator, Serverframeworks,
Secrets, Tests/Audits, lokale Datenbanken und Laufzeitlogs werden nicht exportiert.
Migrationreader und reine alte Darstellungstypen bleiben lesbar; sie haben keine
Runtime-, Timer-, Transport- oder Fallbackautorität. Normale Starts verwenden
V2DesktopApplication/V2Runtime. Der gemeinsam genutzte Desktop-/Threadshell hat
keine V1-Komposition mehr.

`scripts/build.py --clean` prüft Ressourcenarchive und startet Version sowie
Qt-/Soundprobe außerhalb des Checkouts. `client_release_guard.py candidate`
prüft genau EXE/Wheel/sdist, Ressourcenmenge, Namespace und übereinstimmende
saubere Identitäten; `--expected-commit` bindet die Artefakte an den Kandidaten.
Der Kandidatenmodus benutzt keine PyPI-Verbindung und veröffentlicht nichts.

Versteckter Port `--verify-gui-runtime --verification-output <json>` lädt echte
Qt-Widgets/Icon und QSoundEffect-Ressourcen ohne Playback. Optional
`--verification-server ws://127.0.0.1:<port>/ws/v2` verbindet echten Transport,
Settings und Mirror, dann den tatsächlichen Desktop/Core-Thread/Settingsdialog.
Andere Hosts oder Routen werden abgewiesen. Desktopprobe: eigener nativer Mutex,
temporäre Historie/Profilpfade, deaktivierte globale Keys/LED/Playback, absichtlich
nicht vorhandenes Audiodevice. Kein Capture und keine Textinjektion.
Native Windows-Qt und offscreen werden getrennt im Nachweis gekennzeichnet.

`scripts/check_v2_release_server.py` läuft separat mit bytegeprüften Quellen
von ada13b0. Nur Recorder/ASR/Scheduler sind modellfreie Testgrenzen. Ready-/Stop-
Dateien, Watchdog und Cleanup begrenzen die Laufzeit. Der Serverreport speichert
empfangene Helloidentitäten und Quellhashes, keine Credentials oder Rawframes.
Diese Belege prüfen Build-/Integrationsfähigkeit, keine reale ASR-/Hardwarequalität.

Lokaler Loggingapply ist ausfallisoliert; eine fehlende/werfende optionale
Ingressfunktion darf Produktpersistenz und Ergebnis nicht steuern. Nach einem
fehlgeschlagenen GUI-Start wird die ursprüngliche Hotkeykonfiguration ohne
erneuten OS-Registrierungsversuch wiederhergestellt. V2-Lifecyclefeedback entsteht
nur aus Mirrorreduktionen; auch vor der ersten Admission sind Logs diagnostisch.
