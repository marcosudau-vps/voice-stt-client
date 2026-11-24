# R06 – automatische Restabnahme 24.11.2026

## Gesamturteil
Weiterer substantieller Fortschritt, keine pauschale Release-Freigabe. PASS_SCOPED bedeutet ein bestandener explizit begrenzter Nachweis; er ersetzt keine noch geforderte physische oder Frozen-E2E-Prüfung. Ausgangsmatrix 09 und Korrekturdokumente 10–12 bleiben unverändert. Aktuelle Kriterienmatrix: 14_STATUS_RESTABNAHME_2026-11-24.md.

Kandidat: lokaler korrigierter Quellstand HEAD 17fce388e747daf37b97e96ed1fcf6421338873d mit bisherigem uncommittetem Produktdiff. Korrigierte EXE SHA256 07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe. Pinned Server in Quellruntime-Proben e95858e3c010a7e9324b49bb44fee349abe7128a; Frozen-Normalstart belegt konfigurierte Final-URL und Ready, kein eigener Hello-Pin im JSON. Keine Produkt- oder Serveränderungen, keine Administration, kein Commit/Push. Alle Testprozesse beendet.

## Neue Ergebnisse

### Reales akustisches Langdiktat – V03-09, Teil V10-03
- 208,985 s synthetische WAV über echte Realtek-Lautsprecher und ReSpeaker, produktive V2Runtime, isoliertes Profil, MockInjectionBackend.
- 7 eindeutige Finalsegmente, 7 Einfügeaufträge, 2741 Zeichen; 1 Servergeneration, durchgehend Ready in 5-s-Stichproben, gleiche Aktivierung bis Ende der Wiedergabe. Finalisierung abgeschlossen; direkt folgendes Kurzdiktat mit Sollmarkern genau einmal.
- Keine vollständige Wortgenauigkeitsmessung, kein nativer Paste, keine Frozen-E2E. Frühere Langfinal-Abweichung in diesem Lauf nicht reproduziert. PASS_SCOPED.
- Belege: acoustic-long-retest.json/.py. Vorherige Zehner-Serie: Bericht 12.

### Akustische Trigger-Matrix – V03-13, V04-07/08/09/10/12, V07-10
- Manual-only: Wake-Wort ohne Aktivierung/Paste, manuelles Final mit Sollmarkern und einem Auftrag.
- Wake-only: manueller Start abgelehnt, 6 s Idle, normale synthetische Sprache und pausiertes Wake ohne Aktivierung/Paste. Zwei getrennte erfolgreiche Wake-Aufrufe mit je einem Final und einem Auftrag.
- Hybrid: 6 s Idle, gewöhnliche Sprache, pausiertes Wake negativ; zwei getrennte erfolgreiche Wake-Finals, danach manuelles Final. Alle drei Modi PASS_SCOPED, echter Lautsprecher/Mikrofonpfad, keine menschlichen Live-Aufrufe, kein realer Clipboard-Paste. LEDs deaktiviert, Audio/Transkription funktionieren.
- Belege: acoustic-trigger-{manual,wake,hybrid}.json und acoustic-trigger-matrix.py.

### Native Qt: Verlauf und lokale Einstellungen
34/34 Checks (native-desktop-history-retest-2.json): synthetische Einträge, korrekte Reihenfolge/IDs, spezifische Wiedereinfügung (MockInjectionBackend), bestätigtes Löschen genau des ausgewählten Eintrags, bestätigtes Leeren ausschließlich der isolierten Testdaten; Kapazität und Clipboard-Restore übernommen und gespeichert; 8 Tabs in je zwei Fenstergrößen; regulärer Tray-Quit und Cursor unverändert.
- Erste Probe: KeyError auf nicht angebotenem history.enabled-Feld; die Wiederholung überprüft die tatsächlich exponierten Settings.
- Metadaten/Editoren enthalten weder history.enabled, history.persistent.enabled noch text_injection.paste_delay_ms. Korrekte Einordnung anhand 03_MANUELLE_CHECKLISTE: V06-12 ausdrücklich nur falls GUI angeboten -> N/A für GUI-Schalter; V06-06 verlangt Verzögerung bzw. Clipboard-Einstellungen, deshalb fehlender Delay-Editor allein kein FAIL. Clipboard-Wirkung im nativen fremden Ziel bleibt offen. V08-10 Kapazität gespeichert, Wirkung auf Aufbewahrung separat.
- Native Paste-Prüfungen normal und append-space konnten Ziel nicht sicher in Vordergrund bringen, NOT_RUN, Clipboard unangetastet. Kein Produktfehler. native-paste-{normal,space}.json.

### Aktives Profil-Apply
18/18 Checks, native-active-apply-retest-2.json/.py. Native Qt-Dialog, realer Server, kontrollierter kontinuierlicher Null-PCM-Stream am PortAudio-Rand, MockInjectionBackend. Modal ohne Vorauswahl, Abbrechen ohne Änderung/Verlust, Vormerken bei offener Aktivierung/alter Session, expliziter Cancel mit Reconnect auf Hybrid, expliziter Finish mit Reconnect auf Manual-only, Persistenz. Erste Probe hatte fehlende Replay-Callbacks und Watchdog-Neustarts; Wiederholung mit kontinuierlichem 40ms-Feed bestanden. Keine echte Sprache in diesem speziellen Apply-Test.

### Gerätewahl und Vorschau
17/17 Checks, native-device-preview-retest-2.json/.py. Ungültiger Audioindex sichtbar erhalten, keine Capture; GUI-Apply auf echten ReSpeaker, Abwarten der serverseitig bestätigten manual_available-Freigabe und der Qt-Publikation; reales akustisches Kurzdiktat mit vor der Einfügung sichtbarem Soll-Zwischentext, genau ein Sollfinal/Mockauftrag; Wechsel zum Windows-Standardgerät und zweite entsprechende Probe PASS; Persistenz und Shutdown.
Erste Probe nach lokalem Audio-Ready zu früh gestartet; ohne bestätigte serverseitige Freigabe Timeout. Kein reproduzierbarer dauerhafter Fehler nach synchronisiertem Retest. PortAudio-Fehler für ungültiges Gerät erscheinen wiederholt mit Stacktrace, keine Crashs; Rate-Limiting bleibt prüfenswert.

### Frozen-Normalstart/Fehlerpfad
- Gültiger Final-Endpunkt, korrigierte EXE normal gestartet, Windows Qt-Trayfenster, connecting/accepting/configuring/ready, zweite EXE Exit 2, erste lief weiter, WM_QUIT an genau identifizierten eigenen Qt-GUI-Thread, Exit 0, app.stopping/lifecycle.stopping, keine _MEI-Reste, Profil/Cursor unverändert. Deliberately invalid input, Hotkeys/LED aus, kein physischer Paste; kein Tray-Menüklick. frozen-valid-desktop.json und -2.py.
- Ungültiger V2-Pfad in eigenem Profil: tatsächliche EXE Exit 5, invalid_http_origin und fataler Corestart im Log, keine _MEI-Reste, Profil/Cursor unverändert. Kein endloser Block, aber kein dauerhaft bedienbares Fehlerfenster; ob dies dem geforderten verständlichen Fehler für Endanwender entspricht separat bewerten. Korrekte URL in separatem Testprofil danach mit erfolgreichem Frozen-Normalstart geprüft. frozen-invalid-endpoint.json/.py; source probe native-invalid-endpoint-retest.json.

## Noch offene Abnahme-Grenzen
- Durchgehender 30–60-minütiger repräsentativer Frozen-Desktoplauf mit 10 korrekten nativen Pastes, langem Diktat, Fokuswechsel, CPU/RAM, Loganalyse und anschließendem Restart. Die akustischen Einzeltests sind kein Ersatz.
- Native EXE mit echtem Eingabegerät/Hotkeys, sichere Testeditor-Fokussierung (Qt/Notepad), reale Clipboard-Wirkung, tatsächlicher Start-Doppelklick/Tray-Hover, regulärer Tray-Quit mit allen Ressourcen.
- Physische LED-/Ton-/Mute-/USB-Wirkung und echte Wake-Stimme, Sichtbarkeit/Lesbarkeit aller UI-Elemente bei realer Skalierung; frühere physische Belege bleiben gültig im alten Kandidatenumfang.
- Laufzeitpause-Reset bei tatsächlichem vollständigen Neustart, Reconnect-/Recovery- und Persistenzgegenprobe am vollständigen Frozen-Desktop. Historischer gemeinsamer Cursor-Verlust kann nicht rückwirkend ungeschehen gemacht werden, neue Isolation bestanden.
- Adminfunktionen nicht autorisiert, separate Freigabe/Scopeentscheidung; unabhängiges Review und Produkt-/Redistributionsfreigabe.

## Nachweise
EVIDENCE/AUTOMATISCHE_RESTABNAHME_2026-11-24/ enthält ausgeführte Skripte und JSONs inklusive Fehlversuchen. Sämtliche Laufzeitordner und Rohlogs lokal unter Nachweise/korrektur-2026-11-23. Keine privaten Clipboard-Daten oder Rohtranskripte exportiert. Native Qt-Zählungen sind überlappende Einzelchecks, keine 69 neuen Abnahmekriterien. Historische Fehler bleiben sichtbar. Aktueller Gesamtstatus BLOCKED_PENDING_DESKTOP_RETEST_AND_REVIEW.
