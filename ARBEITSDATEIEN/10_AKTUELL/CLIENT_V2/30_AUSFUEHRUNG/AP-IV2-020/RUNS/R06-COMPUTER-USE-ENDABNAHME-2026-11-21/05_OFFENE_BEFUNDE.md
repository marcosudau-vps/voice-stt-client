# R06-Nachlauf · offene Befunde und Testgrenzen

## B01 · Hoch · Produktfehler bei der Profilisolation

**Status offen.** Ein normaler V2-Start über den gelieferten Launcher setzt Client-Home und Config getrennt. Beim anschließenden manuellen Diktat schrieb der Kandidat trotzdem `%LOCALAPPDATA%\RealtimeSTT Client\e vent_cursor.json`. Der globale Cursor bekam im Zeitfenster der Testaktivierung die Bindung an den Final-Testhost, den Pfad `/ws/logs` und Protokoll 2. Der Dateizeitpunkt folgt dem V2-Ereignisempfang. Die erste Laufzeitspur enthält außerdem „Ignoring event cursor with a different server binding“. Der frühere Cursorinhalt wurde vor dem ersten Start nicht gesichert und ist daher nicht exakt wiederherstellbar. Alte Konfigurationen und Historien wurden nicht bearbeitet.

**Reproduktion und Ursache.** Bei explizitem `VOICESTT_CLIENT_HOME` und ohne `event_stream.cursor_path` baut `V2Runtime` den `DualSessionCoordinator` mit aktivierter Cursorpersistenz. Der Coordinator reicht `None` an `EventCursorStore` weiter. Dessen Standardpfad wird aus `LOCALAPPDATA\RealtimeSTT Client` gebildet, und `commit()` ersetzt die Datei atomar. Im Wiederholungslauf mit demselben Build und einem nur für den Prozessbaum gesetzten `LOCALAPPDATA` entstand nach V2-Ereignissen der erwartete Cursor an der entsprechend umgelenkten Position. Der gemeinsame Cursor behielt seine nach dem Erstlauf erfasste Prüfsumme. Die Prozessisolation ist eine Testmaßnahme. Die gezielte Offline-Reproduktion mit getrenntem Client-Home überschreibt einen vorbereiteten synthetischen Alt-Cursor. Bei explizitem Profil-Cursorpfad bleibt der synthetische Alt-Cursor stabil. 18 bestehende Tests zu Cursor und Coordinator liefen grün. Eine Korrektur des Kandidaten steht aus.

## B02 · Hoch · Akustische Testquelle nicht eindeutig isoliert

**Status offen.** Strg+Umschalt+Leertaste löste in einem bewusst fokussierten lokalen Qt-Editor um 00:21:50 eine native Aktivierung aus. Realtime wurde ab 00:21:52 erkannt. Die synthetische deutsche Teststimme lief erst von 00:21:57 bis 00:22:05. Der Server beendete die Aktivierung per Timeout, erzeugte um 00:22:26 ein nichtleeres Final, und ein einziger Win32-Paste erreichte das Qt-Feld. Der eingefügte Text entsprach nicht dem vorgesehenen Testtext. Ein getesteter SAPI-Standardausgang und ein vorhandenes ReSpeaker-Eingangssignal belegen allein keine akustische Kopplung des gewünschten Satzes.

**Gegenprobe.** ReSpeaker Index 1 gemessen, 12 Einsekundenwerte ohne SAPI und 12 mit pausiert beginnender SAPI, keine gespeicherten PCM-/WAV-Daten. Schon ohne Testwiedergabe traten anhaltende Eingangspegel und im produktiven Test Realtime vor dem Testsatz auf. Ursprung des Fremdtons und ausreichende SAPI-Kopplung bleiben unbewiesen. Kein Produkt-ASR-Defekt wird aus diesem kontaminierten Stimulus abgeleitet. Die native Diktatfunktion übertrug den Mikrofoneingang der Aktivierungsprobe an die ausgewiesene Final-Testinstanz. Der unbekannte Inhalt wurde weder als Rohaufnahme gespeichert noch in die Akte kopiert oder erneut eingefügt. Der Paste lief mit `restore_previous=false`. Die ursprüngliche Zwischenablage war für diesen Versuch nicht gesichert. Das kurze Final ist nach Ausgangspolicy unter 1.000 Zeichen nur im Arbeitsspeicher. Das erklärt die leere SQLite-Historie bei genau einem erfolgreichen Einfügeversuch.

## B03 · Hoch · Tray-Zugriff und GUI-Prüfgrenze

**Status offen.** Der verwendete Computer-Use-Pfad liefert auswählbare Fenster. Explorer und Windows-Einstellungen wurden gelistet, ein Tray- oder Taskleistenfenster war nicht auswählbar. Die Prüfung per Explorer-/Shell-Sichtung ergab kein zugängliches Tray-Element. Der Benutzer konnte den Erstlauf über das Tray regulär beenden. Nach Benutzerübergabe um 00:50 wurde der Clientdialog erreichbar. Alle drei V2-Register und fünf lokalen Register konnten anschließend direkt bedient werden. Tray-Tooltip, ein vollständiger Settings-/Feedback-Durchlauf und physische Effekte bleiben offen. Für Starttests wurde das unveränderte Startskript über die Shell aufgerufen. Der Computer-Use-Skill untersagt das indirekte Aufrufen von CMD-Skripten durch die Explorer-Bedienung.

## B04 · Hoch · Physische Beobachtung fehlt

**Status offen.** Keine physische Betätigung von ReSpeaker-Mute oder USB-Stecker. Sichtbare LED-Muster und subjektiv hörbare Feedbacktöne sind trotz LEFX- und Sound-Konfigurationsreferenz offen. Das Log belegt die Initialisierung des LED-Controllers.

## B05 · Offen · Admin- und Löschoperationen

Kein Admin-Key oder separater Autorisierungsauftrag. V08-17 bis V08-21 sind N/A in diesem Lauf. Adminfreigabe bleibt separat offen. Der Computer-Use-Skill verlangt für UI-Datenlöschung Bestätigung unmittelbar vor der Aktion. Ein eindeutig dafür erzeugter eigener Testverlauf lag ohnehin nicht vor.

## B06 · Hoch · Kontrollierter Netz-/Geräteausfall offen

Für den GUI-Prozess stand kein eingerichteter isolierter Netzwerkabriss mit Rücknahme zur Verfügung. Rechnernetz und Firewall blieben bestehen. Die neue Session nach regulärem Prozessneustart ist belegt. Ein gezielter Abriss samt Recovery während Idle und Aufnahme bleibt zu prüfen. Der ungültige Pfad blockiert im Transporttest vor der ersten Verbindung. Die sichtbare Reaktion der laufenden EXE bleibt offen.

## B07 · Offen · Produkt- und Redistributonsfreigabe

Separate Produkt-, Lizenz- und Veröffentlichungsfreigabe fehlt. Die bestehende Vorabnahme bestätigt Build-Artefakte und technische Funktionsfähigkeit im belegten Scope.

## B08 · Hoch · Reload verwirft ungespeicherten Sessionentwurf

**Status offen, zweimal in der Desktop-EXE reproduziert.** Unter Session „Warten auf Eingabeschluss“ von 5000 ms auf 5200 ms ändern, ohne Apply „Serverwerte und Katalog neu laden“ anklicken, Auftragsabschluss abwarten. Der Entwurf steht wieder auf 5000 ms. Dieselbe Folge mit 5300 ms liefert dasselbe Resultat. GUI meldet lediglich „Serverwerte geladen.“ Ein separater regulärer Apply auf 5200 ms und die Rücknahme auf 5000 ms funktionierten.

**Ursache.** In `V2SettingsDialog._receive()` setzt jede erfolgreiche Antwort vom Typ `load` die Reset-Flagge. `render(reset=True)` füllt bereits vorhandene Editorwerte und Katalogauswahl erneut aus dem gespeicherten Profil. Eine Entwurfsprüfung oder Rückfrage liegt im Reload-Pfad nicht vor. Praktisch nachgewiesen ist der Verlust des Sessionwerts.

## B09 · Mittel · Hotkey-Doppelbelegung meldet irreführend einen Migrationskonflikt

**Status offen.** Im aktuellen V2-Profil ist die Primärbelegung Strg+Umschalt+Leertaste. Dieselbe Kombination als sekundären Hotkey eintragen, zu Session wechseln und „Trigger und Sessionwünsche übernehmen“ anklicken. Die GUI meldet, das migrierte Profil benötige eine bestätigte Korrektur. Sie nennt die Doppelbelegung und die zwei betroffenen Felder nicht. Das Apply wird korrekt abgewiesen. YAML-Hash unverändert und beide bestehenden nativen Bindungen erhalten.

**Ursache und Gegenprobe.** `ControlConfig` erkennt das Duplikat. `migrate_profile()` reduziert es auf `invalid_trigger_profile`. `SettingsUISession._candidate()` liefert darauf `profile_repair_required`. Die Oberfläche zeigt dafür den generischen Migrationstext. Die gezielte Offline-Reproduktion liefert denselben Fehlercode und denselben Text.
