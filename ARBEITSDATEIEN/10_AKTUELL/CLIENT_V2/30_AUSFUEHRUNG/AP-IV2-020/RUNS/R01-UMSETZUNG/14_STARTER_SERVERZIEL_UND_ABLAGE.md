# Starter, Serverziel und Ablage – Prüfung vom 18.10.2026

AP-IV2-020/R01, unverändertes Clientprodukt7bb5646, Serverpinada13b0.
**IV2-020-T02: bestätigter Starter-/Kontextfehler, OPEN.**
Serverstopp/Reconnect und konkrete menschliche Einstellungsansicht teilweise
noch aufzuklären. W01/SERVER_FIX_REQUIRED bleibt unabhängig davon bestehen.

## Anlass und Grenzen dieser Prüfung

Der Auftraggeber berichtet: Server beendet/neu gestartet, Testclient zeigt
keinen Verbindungsverlust/Logeintrag; konkrete Serveradresse im Dialog nicht
auffindbar; nach Clientende meldet der Desktopstarter fehlendes
`C:\Users\marco\AppData\Local\VoiceSTT-Qualification\AP-IV2-020\client-both.yaml`.
Zusätzlich wird die Berechtigung zur Ablage außerhalb des Repositorys hinterfragt.

In diesem Prüfauftrag wurden keine Profile, Cachebestände oder Verknüpfungen
verändert und keine Clients/Server gestartet oder gestoppt. Neue Diagnoseakten
und die Kopie des beigefügten Screenshots liegen ausschließlich im Repository.
Keine privaten Gesamtprofile, Zugangsdaten, History oder Laufzeittexte exportiert.

## 1. Welchen Server die Testinstanz tatsächlich verwendete

Konfiguriert und vom Qualifikationsrunner vor dem Start auf genau dieses Ziel
geprüft: **`ws://127.0.0.1:18020/ws/v2`**, HTTP-Origin
**`http://127.0.0.1:18020`**. Container `voicestt-qualification-iv2-020`,
Hostbindung127.0.0.1:18020 → Container8010. Das ist ein eigener lokaler
Qualifikationsserver; weder der VPS noch ein anderer lokaler Server ist damit
gemeint. Profilhash entspricht dem im letzten Sessionstart gesicherten Hash.

Der letzte Sessiontrace zeigt nach erfolgreichem Bootstrap02:08:38 MESZ
durchgehend Generation1/ready. Die letzten Metriken04:59:58,143 MESZ zeigen
weiter ready, Audio/LED verfügbar, keine offenen Commands. Erst anschließend:

| MESZ | Ereignis |
| --- | --- |
| 04:59:58,436 | Transport `stopping` |
| 04:59:58,442 | Transport `closed` |
| 04:59:59,860 | reguläres `session_stopped` |

Im gehaltenen Trace gibt es **vor dem manuellen Clientende keinen erkannten
Transportverlust und keinen Reconnect**. Bei der Prüfung läuft der tatsächlich
gewählte Container weiterhin; Docker meldet Start17.10.18:26:22UTC und keinen
aktuellen Containerneustart. Diese Containerdaten beweisen nicht, dass niemals
ein einzelner Serverprozess intern beendet oder neu geladen wurde.

**Bewertung:** Ein weiterer Client-Reconnectdefekt ist aus diesem Versuch noch
nicht nachgewiesen. Welchen Server/Prozess der Mensch beendet hat und zu welcher
Zeit, muss abgeglichen werden. Container-/Dienstname oder verwendeter Befehl
wurde gebündelt erfragt. Ohne diesen Abgleich wäre die Aussage „der Client hat
den Ausfall seines Servers übersehen“ unbelegt. Es wird hier kein Serverausfall
zum Schein als bestanden bewertet. Der native Log-UI-Nachweis T01 bleibt offen;
fehlende neue Disconnectlogs allein sind bei nicht erkanntem Ausfall kein
separater Beweis eines Logdienstfehlers.

## 2. Serveranzeige und Konfiguration im Einstellungsdialog

Der äußere `V2SettingsDialog` besitzt oberhalb der Tabs ein `origin_label`.
`render()` setzt es auf `Server: ` plus `SettingsUIView.origin`. Es handelt sich
um die **HTTP-Origin**, nicht um den vollständigen WebSocketpfad. Die technische
Serveradresse wurde aus diesem äußeren Dialog also nicht vollständig entfernt.

Zwei reale Einschränkungen:

- Das Label wird leer konstruiert und erst bei einer erfolgreichen Viewlieferung
  gefüllt. Beim ersten fehlgeschlagenen Laden ohne View bleibt es leer.
- Der zusätzlich aufrufbare lokale `SettingsDialog(v2_local=True)` blendet
  `server.*`-Felder und den Tab „Verbindung & Betriebsmodus“ aus. Dort ist deshalb
  keine Serveradresseneinstellung vorhanden. In den untersuchten V2-Dialogen
  gibt es keinen vollständigen Editor für den WebSocket-Endpunkt.

Der **echte Qt-Dialog** wurde offscreen mit einer simulierten fehlgeschlagenen
ersten Bridgeantwort geprüft: Label vorher leer, nach Fehler ohne View weiter
leer, Fehlermeldung sichtbar. Keine echte Verbindung, Dateiänderung außerhalb
des Repositorys oder Credentialoperation. Das reproduziert einen konkreten
Anzeigemangel; es beweist nicht nachträglich, welchen Dialog/Ladezustand der
Mensch geöffnet hatte. Kein Screenshot seines Einstellungsfensters vorhanden.

Quellen: `ui/v2_settings_dialog.py` Konstruktor/`_receive`/`render`,
`ui/settings_dialog.py` V2-Filter, `core/settings_ui_service.py::SettingsUIView`.
Für eine Korrektur sollten konfiguriertes Ziel und tatsächlich verbundene
Identität getrennt und auch bei fehlgeschlagenem Laden sichtbar bleiben.

## 3. Screenshotfehler und tatsächlicher Speicherort

[Vom Menschen bereitgestellter Screenshot](EVIDENCE/launcher-context-20261018/human-starter-error.png).
Der Fehler entsteht beim **Lesen** des Profils, nicht beim Erstellen einer
neuen Profildatei durch diesen Klick. Der Startercode selbst liegt im Repository.

Der Starter konstruiert seinen Laufzeitpfad aus
`%LOCALAPPDATA%/VoiceSTT-Qualification/AP-IV2-020` und erwartet dort
`client-both.yaml`. Aus dem Codex-App-Kontext ist die Datei unter diesem logischen
Pfad lesbar. Ihre tatsächliche Auflösung ist jedoch:

```text
C:\Users\marco\AppData\Local\Packages\OpenAI.Codex_2p2nqsd0c76g0\LocalCache\Local\VoiceSTT-Qualification\AP-IV2-020\client-both.yaml
```

Dasselbe gilt für `active-session.json`. Windows-App-Kontext und normaler
Desktopstart haben dadurch unterschiedliche Dateisichten. Der außerhalb des
Codex-App-Kontexts gestartete Launcher meldet die logische Datei als fehlend,
während die vorhandene Datei im App-Cache liegt. **Bestätigter Ablage-/Kontextfehler
T02**, keine eigenmächtige Suche nach einem anderen Profil als „Reparatur“.

Der echte `start_client()` wurde zusätzlich mit einem nicht vorhandenen Profil
geprüft: `FileNotFoundError`, bevor `ensure_server()` oder `Popen()` aufgerufen
werden. Beim gezeigten fehlgeschlagenen Start ist damit noch kein nachfolgender
Server-/Clientstart durch diesen Codepfad erfolgt.

### Übersehene Testgrenze

Die bisherigen Starterprüfungen nutzten simulierte Profildateien, echte
Qt-Buttonklicks mit gemocktem Start und Starts aus dem Agentenkontext. Sie
belegten **keinen echten Doppelklickstart aus dem normalen Windows-Kontext**.
Die frühere Checklistenbehauptung eines vollständig nutzbaren Desktopstarters
wird daher zurückgenommen. Dass der Starter unter einem zusätzlichen
Startkontext scheitert, ist eine Lücke meiner damaligen Verifikation.

## 4. Woher der Pfad und die bisherige Autorisierungsannahme stammen

Der Implementierungsagent hat diesen AppData-Testbereich bei den autonomen
Vorbereitungen selbst gewählt und in die Qualifikationshelfer eingebaut.
Es ist kein vom Server vorgegebener Pfad und kein vom Nutzer ausdrücklich
benanntes Verzeichnis. Dort liegen isolierte Testprofile und Laufzeitdaten;
der reguläre V1-Anwendungsbereich wurde dafür nicht gewählt.

Der ursprüngliche Auftrag verlangt wörtlich:
„Verwende soweit erforderlich isolierte Testprofile und Testinstanzen.“
Später wurde ausdrücklich ein selbst bedienbarer Teststarter gewünscht.
Diese Aufträge wurden als Grundlage für die isolierte Laufzeitablage und den
Starter verstanden. **Eine ausdrückliche Freigabe für genau den genannten
AppData-/Package-Cache-Ordner wurde nicht eingeholt.** Ebenso war die konkrete
Desktopverknüpfung eine gewählte Umsetzung des gewünschten Starters, keine
gesondert vom Nutzer vorgegebene Dateiadresse. Technische Schreibmöglichkeit
ist kein Ersatz für eine menschlich festgelegte Ablagegrenze.

AGENTS verlangt zwar lokale Anwendungsdaten statt Repository für die persistente
SQLite-Historie und verlangt den Schutz produktiver V1-Daten. Daraus folgt aber
keine ausdrückliche Freigabe dieses speziellen Testordners. Die jetzige
menschliche Klarstellung zur Ablage wird beachtet: keine neue externe Datei,
kein Kopieren/Verschieben vorhandener Laufzeitdaten und keine Änderung der
Verknüpfung während dieser Diagnose. Vor einer Ablageumstellung ist der
verbindliche Zielbereich zu klären; keine privaten Profile/History blind ins Git.

## 5. Konkreter Korrekturweg, noch nicht ausgeführt

1. Eine eindeutig festgelegte Laufzeitablage und explizite Profil-/Homeparameter
   verwenden; denselben tatsächlich aufgelösten Pfad an alle Kindprozesse
   weitergeben. Keine implizite Codex-Package-Cache-Suche und kein leeres
   Ersatzprofil bei fehlender Datei. Kalibrierwerte und V1 müssen erhalten bleiben.
2. Im Starter den wirksamen Profilpfad, Serverhost/Port, Container und frischen
   Verbindungsstatus sichtbar machen. Fehlendes Profil verständlich melden.
3. Serveridentität im äußeren Einstellungsdialog unabhängig vom Bootstrapladen
   anzeigen; konfiguriertes Ziel und aktive Verbindung unterscheiden. Eine
   Produkteinstellung darf nicht beiläufig außerhalb des freigegebenen Scopes
   ergänzt werden.
4. Bisheriges Verhalten transparent machen: Bei gültigem Profil startet der
   bestehende Starter einen gestoppten **eigenen** Qualifikationscontainer nach
   Identitätsprüfung automatisch. Der fehlgeschlagene Profilzugriff liegt davor.
   Eine Änderung dieser Bedienung wäre bewusst festzulegen, nicht stillschweigend.
5. Nach Korrektur echten Windows-Doppelklickstart außerhalb des Agentenkontexts,
   laufende/fehlende Profile, Einstellungs-Ladefehler und kontrollierten Ausfall
   des **tatsächlich gewählten** Servers prüfen. Frühere Mockprüfungen ersetzen
   diese Abnahme nicht.

## Belege und Status

- [Pfadauflösung, Profilbindung, vollständige Statusfolge, Containerdaten und Autorisierungseinordnung](EVIDENCE/launcher-context-20261018/assessment.json)
- [Gezielte Ergebnisse: fehlendes Profil und leere Serveranzeige](EVIDENCE/launcher-context-20261018/probe.json)
- [Wiederverwendbarer, seiteneffektbegrenzter Prüfhelfer](EVIDENCE/human/probe_launcher_settings_context.py)

Keine Produktänderung, keine nachträglich behauptete Freigabe, kein neuer Build
und kein vollständiger PASS. T02 offen; T01, O01 und W01 bleiben erhalten.
