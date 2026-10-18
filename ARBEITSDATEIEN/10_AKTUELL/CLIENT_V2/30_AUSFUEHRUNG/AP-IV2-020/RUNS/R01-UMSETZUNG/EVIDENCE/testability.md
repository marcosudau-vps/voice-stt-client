# Phase A – Testfähigkeit, 2026-10-15

| Kategorie | Tatsächlich verfügbar / Grenzen |
| --- | --- |
| 1: vollständig autonom | Windows-Vollsuite, Python3.12.10, compileall, Paket-/Git-/Buildhashprüfung; bestehende modellfreie Prozess-/Race-/Queue-/Timeoutprüfungen |
| 2: durch Testautomatisierung | isolierter lokaler Modellserver, parameter-/LEFX-Inventar, redigierte Session-/Ressourcenmessung, eigener Prozess als Clipboardziel, Befehlswarteschlange und bewusst gestartete Sampleaufnahme vorbereitet |
| 3: echte Hardware ohne Bediener | ReSpeaker-Audiocapture 16000/mono/40ms (73 Pakete/3s, keine Drops/Overflows), USB2886:001a Firmware2.0.10/GPO-Read ohne Forceclaim; echter Credentialstore und Win32hotkeys; native GUI mit realem kontinuierlichem Audio sowie Frozenbootstrap |
| 4: echte Bedienung/Wahrnehmung | bewusst gesprochene Wakephrase mit Nutzsprachbeginn, natürliche ASRqualität, Mute-Taste/USBtrennung, LED-/Sound-/Overlay-/Traywahrnehmung, verschiedene Textziele/elevated UAC; Windows erlaubt dem Helfer aktuell keinen automatischen Vordergrundfokus, ein Klick aufs eigene Testziel ist erforderlich |
| 5: fehlende Voraussetzung | Pro16-Lizenzslots belegt; Testversuch beendet. CommunityDE64 real bereit. Echte positive Wake-/deutsche Goldenaufnahmen und menschliche Grenzannotation fehlen; 30min/100Aktivierungen am finalen Kalibrierstand noch nicht durchgeführt |

Windows11Pro26300; Benutzerkontext ohne angeforderte Adminerhöhung. PySide6/native
Win32, Mikrofon- und USBsteuerzugriff vorhanden. Docker Desktop/Linux lokal.
Qualifizierte EXE bekannt und gehasht. Server source-qualified ada13b0,555 exakt
verifizierte Blobs, eigenes Loopback18020 und separate Docker-Datenvolume.
ASR-/Wake-Modelle vorhanden; ONNX tatsächlich geladen und gemessen. VPS nur vor der
lokalen Steuerung lesend geprüft, danach keine weiteren VPS-Aktionen. V1-Installation,
Profile, produktiver lokaler Container und produktive Servereinstellungen unverändert.

Fremde Prozesse werden nicht beendet und USB nicht erzwungen übernommen. Reale
Fehlertests werden ausschließlich im Testclient/-server bzw. am angekündigten
ReSpeaker ausgeführt. Ein Injected-Adapterfehler zählt nicht als physischer USBverlust.
Rohsamples und Runtime-DBs liegen außerhalb Git; öffentliche Belege sind redigiert.

Der [gemeinsame Ablauf](../02_GEMEINSAMER_TESTABLAUF.md) bündelt menschliche Aktionen.
Die [Kalibrierung](../03_KALIBRIERUNG.md) trennt tatsächlich wirksame Einstellungen,
NA/NS-Autorität und technische Constructorgrenzen. Noch keine finalen Defaults gewählt.
