# AP-IV2-020/R01 – autonome Restprüfung und tatsächliche Freigabereste

21.10.2026, gleicher Umsetzer/R01/Paketbranch/Draft-PR15. Status **BLOCKED**,
Workflow **IMPLEMENTATION_IN_PROGRESS**. [Auftrag](ZUSATZPROMPTS/035_REST_AUTONOM_ERLEDIGEN.md).
Ausgangs-HEAD `cd9c4ae9e911ec7e0b4b8b917e31aa5d6865179a`, kanonischer Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`. Produkt unverändert
`0f6c85e0ecf971e596aae1b7d265dad7132754e2`; keine Produkt-/Defaultänderung.

## Ergebnis der autonomen Durchführung

[Belegsammlung](EVIDENCE/technical-rest-20261021/),
[abschließender Kombinationslauf](EVIDENCE/technical-rest-20261021/technical-final-all/result.json),
[Windows-/Helferregression](EVIDENCE/technical-rest-20261021/technical-final-regression/result.json).
Alle 29 Kombinationsfälle PASS_SCOPED, keine Pendingcommands/Cleanupfehler.
Die schärferen zeitlich kalibrierten Rennen und Überlappungen sind separat belegt.

| Prüfung | Ergebnis und Grenze |
|---|---|
| Settings während tatsächlicher Aufnahme | cancel/finish/vormerken jeweils bestanden. Ohne explizite Wahl kein Persistieren; alter Input/alte Effectivewerte bleiben bei Vormerken bestehen. Nach gewolltem Reconnect Wake-only,5000msFollow-up/320msPre-Roll, keine Autoaktivierung. |
| Idle mit ausstehendem Final | Tatsächlichen ASRfinal unverändert eine Sekunde an der geordneten Empfangsgrenze verzögert. Fehlende Drainwahl blockiert ohne Diskänderung; Warten bewahrt genau einen alten Final vor Reconnect. |
| Verbindungsabbruch bei Preview/Final | Tatsächliches Interim durchgelassen bzw. tatsächlichen ASRfinal durch den eigenen Transportfehler zurückgehalten. Eigener Socketabbruch, neue Session; keine alte Ausgabe/Autoaktivierung, bewusstes neues Diktat liefert genau einen neuen Final. Kein Serverstopp. |
| Wake-only / Controls | Beide echten Modelle nacheinander, manueller Idlestart blockiert, aktives Primary-Cancel funktioniert trotz deaktiviertem Manualtrigger. |
| Eng benachbarte Wake-/Manualtrigger | Kalibrierte zwei Fälle: Manual gewinnt, Wake gewinnt. Manueller Aufruf15ms vor bzw.110ms nach erster beobachteter Admission; jeweils ein Gewinner/ein Final. Erfolgreiches Refresh nach Wake zählt nicht als zweiter manueller Start. |
| Controls | Alle18Fälle aus waiting/recording/followup × refresh/finish/cancel × primary/secondary bestanden. Bestehende NONE-Dreiphasen- und echte separate Hotkeykollision bleiben zugeordnet; keine neue identische Bedienprobe. |
| Altfinal während neuer Sprache | Drei tatsächliche ASRpaare; bei Empfang des alten Finals ist jeweils B mit anderer Activation-ID in segment_active. Zwei getrennte Finals/Adapterausgaben. Keine künstliche Wireverzögerung/-umordnung in dieser Probe. |
| Lokaler Logstore separat | Eigene echte SQLite-Datenbank11,015s durch konkurrierende Schreibtransaktion blockiert. DEGRADED_STORE/store_errors=1 tatsächlich beobachtet; Core ready, ein gebundener Final/eine Adapterausgabe, keine Pendingcommands; Worker sauber beendet. |
| LED-only bei offenem Input | Echter nativer USB-LEDtransport gestoppt, reale Mikrofonaufnahme unverändert. Dieselbe Session/Generation/Activation, weiterhin ready,150zusätzliche echte Audiopakete, LEDausfall sichtbar und LEDpfad wieder verfügbar. Kein physisches Abziehen/älterer Pendingfinal daraus ableiten. |
| Native Einfügung / Clipboardkonflikt / Prozessabbruch | Produktionsqueue/-History/-Win32backend, eigener separater Worker und eigener fokussierter Qt-Editor. Normale Unicodeeinfügung exakt, fremde Clipboardsperre bounded failed/keine Ausgabe. Worker direkt vor und nach tatsächlichem SendInput beendet: danach durable unknown, keine automatische Wiederholung, vor Paste leer/nach Paste exakt ein Text. Kein erhöhtes Ziel. |
| Admin | Falscher Schlüssel am echten Pro-V2-Ziel zurückgewiesen, keine globale Defaultmutation. Gültiger Schlüssel im exakt passenden Vault fehlt: richtiger Guardcheck NOT_RUN_MISSING_CREDENTIAL. Kein Geheimnis ausgegeben/gespeichert. |
| Normal gestartete endgültige EXE | SHA256 e20059f6dff1279cb23fb01576d447fb285aa94cb270d71968b8430a063a15fc aus dist-iv2-020-usb, nicht die veraltete dist-EXE. Tatsächlicher Produktprozess/PortAudio-ReSpeakerstream/Settingsbootstrap ready im normalen Windowslauf. Eigenes Manual-only-Profil, kein Autostart. Der native Tray liefert dem Computer-Use-Werkzeug kein ansteuerbares Fenster: sicht-/hörbarer EXE-/Diktatnachweis NOT_PROVEN. Eigene Prozesse danach kontrolliert beendet; kein behaupteter sauberer GUI-Shutdown. |

Die Runtimeprüfungen nutzen Produktionsruntime, Controls, Mirror, Settings,
Media/AudioCapture, TLS, echte freigegebene Sprachfixtures und reale Servermodelle.
PCM an der PortAudio-Grenze und Clipboardbackend sind dort kontrollierte Adapter.
Die gesonderten nativen Clipboard- und LEDproben verwenden dagegen die echte
Windows-/USBhardware. Keine Übertragung eines Adapter-PASS auf physische oder
Frozen-Sprach-/Feedbacknachweise.

## Identitäten, Reproduzierbarkeit und Regression

Verwendetes Ziel ausschließlich `wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`.
Alle ausgewerteten Vorher-/Nachherinfos stabil: Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, sauberer Baum
`74f37cad84c5be9e74d880a4b10c3d9623de7da3`, Version2.0.0/pro,
Instanz `14e6ff8dc2704f7298924b0d1de5cd1b`. Echte Hello-SHAs in den
Runtimefällen zusätzlich geprüft. Frozen-Idle: zeitgleiche Info am tatsächlich
konfigurierten TLSziel plus produktives Ready/Audiolog; kein zusätzlich
abgegriffener Frozen-Hello-Body behauptet.

Neue komplette Windows-Suite: **1400Tests,0Skips,PASS,241,656s**.
Helfersuite **73Tests,0Skips,PASS**, Qt-Selbstprüfung und drei Prüfungen des
retirierten Starters PASS. compileall PASS. Produkt-/Buildquellen gegenüber
0f6c85e unverändert; kein neuer Build erforderlich. Source-/Helferherkunft,
vollständige komprimierte Logs und exportierte Beobachtungen liegen im Index.
Später ergänzter Logstorehelfer wurde tatsächlich am Server ausgeführt und
anschließend kompiliert; er verändert weder Produkt noch bestehende Helfertests.

Dauerhafte Helfer: remote_runtime_probe, technical_rest_probe,
logstore_runtime_probe, native_rest_probe; Befehle in tests/manual/v2/README.md.
Der abschließende 29-Fälle-Lauf bindet die endgültige Runtime-Helferfassung;
frühere Diagnoseläufe sind ergänzend/historisch und werden nicht hochgestuft.

## Ressourcenbefund

18weitere echte Sprach-/Cancelaktivierungen in drei Sessions, jeweils sechs
pro Generation: zehn Tasks, null Pendingcommands; pro Session sechs bewusst
aufbewahrte Activation-/Segment-/Terminaleinträge. Nach jedem Reconnect alle
alten Activationobjekte per weakref freigegeben und alle drei neuen Register leer.
Tracemalloc zeigt unter anderem Testbeobachtungen/JSONdaten, TLS-/Kompressionspuffer
und aktuelle Sessionmodelle. Diese erklären Wachstumsklassen, **nicht exakt jeden
Byte** der früheren9,54MiB. Privatebytes sind außerdem kein Maß nur für lebende
Pythonobjekte. Der vollständige30min100-Lauf aus Bericht35 bleibt sein eigener
Messnachweis. Kein universeller Leckfreiheitsbeweis und keine ungeprüfte
Übertragung auf beliebig lange Sessions ohne Reconnect; sessiongebundene
Deduplizierungs-/Modellretention ist im Produkt vorgesehen und hier sichtbar.

## Erhaltene Fehlversuche der Testhilfen

- Settingspilot: geladene AppConfig hatte noch den Migration-Snapshot vor der
  Rezeptänderung. Speichern und neu laden korrigiert; Regression schützt nun
  tatsächliche Runtime-Effectivewerte. Kein Produktverlust von Pre-Roll bewiesen.
- Gleichzeitige Starts kollidierten mit einem sekundengenauen Ordnernamen;
  UUIDzusatz eingeführt. Keine Änderung eines bestehenden fremden Ordners.
- Erste adaptive Rennprobe lag406/562ms nach dem tatsächlichen Wake und verfehlte
  deshalb die vorab verlangte300msNähe. FAIL bleibt erhalten; neue Messung mit
  warmem1,78sOffset belegt beide Reihenfolgen tatsächlich.
- Erster nativer Einfügelauf bestand die vier Produktfälle, stellte aber die
  vorherige Zwischenablage nicht zurück. Der Sequenzvergleich allein war zu eng;
  erneuter Lauf zeigt eigene Textbytes bei veränderter Sequenz522→525. Die Hilfe
  darf bei gesperrt gelesenem, weiterhin eigenem Testtext ebenfalls restaurieren.
  Neuer Lauf einschließlich Sicherung PASS. Ursprünglicher Clipboardinhalt des
  ersten Versuchs wurde nicht gespeichert und kann nicht nachträglich restauriert
  werden; dieser Fehler der Testhilfe bleibt ausdrücklich erhalten.
- Logstorepilot verlangte fälschlich schon beim ersten SQLitefehler FAILED_STORE.
  Bestehende Schutzlogik meldet zuerst DEGRADED_STORE; Ausfallzähler und actual
  Datenbanksperre werden nun korrekt geprüft. Ursprünglicher Timeout bleibt FAIL.
- Aufräumprüfung berücksichtigt jetzt auch technische Probeberichte und
  ausführbaren Prozess/Erstellungszeitraum statt eines alleinigen, unter Windows
  wiederverwendbaren PIDwerts. Alle Einzelhash-/Pfad-/Archivprüfungen bleiben.

## Fallgenaue Restmatrix – keine erneute allgemeine Testserie

| Gate | Jetzt belegt | Tatsächlich noch offen |
|---|---|---|
| M-01 | Bestehendes natives Source-Hotkey-/Zweisegment-/Finishdiktat plus neuer Source-ASR-Nachweis Start vor Altfinal/Altfinal während B-Sprache. | Kein erneuter identischer Sourcefall; Frozenanteil gehört M-10. |
| M-02/03/04 | Bestehende echte Positiv-/BOTH-/Nutzsprach-/Rearmfälle, neue Wake-only-Controls, beide engen Renngewinner, vollständige Servicephasenmatrix/NONE und native Registrierungs-/Refreshbelege. | Source-/Adaptergrenzen bei Frozenpaarvergleich ausdrücklich berücksichtigen. |
| M-05/06 | Bestätigte physische Grund-USB-Recovery/Hardwaremute; getrennte Runpausen mit aktiven Wake-Modellen über Recovery/Neustartbelege; neuer nativer LED-only-Ausfall bei offenem Input. | Physische Verlust-/Pausenkombination mit älterem noch ausstehendem Final nicht vollständig belegt. Nicht durch denselben normalen USBgrundtest ersetzen. |
| M-07/08 | Aktuelle echte Preview-/Pendingfinal-Netzfehler, Settingsentscheidungen/Drain und tatsächliche separate Logstoresperre bestanden. | Kein zusätzlicher identischer Source-Diktatblock nötig; kein eigenmächtiger Serverrestart. |
| M-09 | Falscher Guardcheck ohne Defaultmutation; vorhandene native Vaultspeicher-/Origin-/Ersetzen-/Löschbelege. | Gültiger Admincheck am passenden Pro-V2-Origin; Schlüssel ausschließlich im vorgesehenen sicheren Dialog verfügbar machen. |
| M-10 | Qualifizierte EXE startet nativ/real audio ready; Assets/Identität belegt; Altfinal/B-Sprache Source dreimal bestanden. | Endgültige EXE: echter Manual-/Wake-Paarvergleich sowie Tray/Overlay/Sound/LED im Bedienlauf; offener Overlaywunsch und abschließende Wahrnehmung. Kein PASS aus bloßer Dateigleichheit. |
| M-11 | Normale native Einfügung/Reinsert, aktueller realer Clipboardkonflikt und Prozessabbruch vor/nach Paste bestanden. | Erhöhte Zielanwendung/UIPI. Agent läuft ohne Elevation; UAC ist eine menschliche Handlung. |
| M-12 | Zusammenhängender30min100-Realmodelllauf, positive/negative Fixtures, Nutzsprachgrenzen, Watchdog und neue Ressourcenprofilierung. | Physische/Frozen-Übertragbarkeit und restliche Umwelt-/Kalibrierungsbeurteilung offen; kein weiterer identischer Replaydauerlauf gefordert. Allgemeine TV-Falschakzeptanzrate nicht aus kleinem Negativfixture behaupten. |
| T02/T03/O01 | Alter unsicherer Starter nachweislich deaktiviert; aktuelle getrennte Profile funktionieren. T03: echte Ereignisübergänge/Regressionen belegt. O01: aktuelle Cancel-/Pending-/Überlappungsfälle bestanden. | T02-Abnahme des Ersatzstarts außerhalb Agentenkontext und T03-Wahrnehmung im finalen Bedienblock bündeln. O01-Historie bleibt ohne nachgewiesene damalige Ursache; keine nachträglich bewiesene Produktkorrektur behaupten. |

**W02 bleibt CLOSED_BY_HUMAN_DISPOSITION_NOT_REPRODUCED**, keine erneute
Untersuchung/Freigabebedingung. T02/T03 werden durch technische Teilbelege nicht
voreilig vollständig geschlossen. 5000msFollow-up und320msPre-Roll bleiben die
bestehende Testkonfiguration;0,90/2Frames bleibt nur geprüfter Kandidat.

Menschliche Resthandlungen daher als **ein Abschlussblock** bündeln: sicherer
Adminzugang, UAC/erhöhtes Ziel und finale EXE-/Hardware-/Wahrnehmungsfälle mit
Restkalibrierung. Jede Aufgabe vorher lesbar, eigener Start/Wiederholen/Weiter.
Keine erneute allgemeine Freigabe, keine Wiederholung bereits belegter
Standarddiktate. Ohne diese Pflichtbelege bleibt das Paket BLOCKED; unabhängige
Abnahme und spätere ausdrückliche kanonische Übernahme werden nicht vorweggenommen.

Computer-Use-Vorgabe für UAC: [guidance.md](C:/Users/marco/.codex/plugins/cache/openai-bundled/computer-use/26.1013.40934/docs/guidance.md)
verlangt „Do not act on security or privacy permission requests.“
Das ist eine Handlungsgrenze für den Agenten, kein fehlender allgemeiner Auftrag.

## Aufräumen und Abgabe

Alle19hier neu angelegten Laufzeitordner inklusive Fehlversuchen, Frozen-
Entpackordnern, Profilen, Logs und Test-History wurden vollständig privat im
ignorierten build/ap-iv2-020-suite/private-archive hashgesichert und anschließend
mit erneuter Einzeldateiprüfung entfernt. Genehmigter C:-Namensraum ist leer.
Öffentlich nur redigierte Zähler/Ereignishashes/Identitäten und Testlogs;
keine privaten Profile/History-/Credentialdaten ins Git. Frühere26Entfernungen
bleiben ihrem Lauf zugeordnet; keine erneute Löschung/Änderung von V1-Daten.
Kumulativer Draft-PR15 wird aktualisiert; kein Eigenreview/Merge/Release/Tag.
