# ADR-001 – Betriebsmodi für direkte Hotkey-Diktierung und Wake Word

Status: zurückgezogener Entwurf; nicht bindend — **abgelöst 2026-08-14**

Datum: 2026-07-25

> **Abgelöst.** Die hier offen gelassene Architekturfrage ist inzwischen
> entschieden: Es gibt keine Betriebsmodi mehr, sondern eine Session mit
> zwei unabhängig aktivierbaren Triggerquellen und einem
> serverautoritativen Activation-Modell. Maßgeblich ist die einheitliche
> Triggerarchitektur, dokumentiert in
> [`server-docs-for-client-development/09-betriebsmodi-und-serverkonfiguration.md`](../../server-docs-for-client-development/09-betriebsmodi-und-serverkonfiguration.md)
> sowie serverseitig in `docs/einheitliche-triggerarchitektur.md`.
> Dieses Dokument bleibt als historischer Beleg erhalten.

Dieser Entwurf hielt einen zwischenzeitlichen Lösungsansatz fest. Die darin
vorgesehene per-Session-Umschaltung über Serverprofile würde nach Prüfung des
Servers eine grundlegende Umgestaltung seiner Architektur erfordern und wird
deshalb nicht weiterverfolgt. Die dafür kurzzeitig eingeführte lokale Option
`session.mode` wurde wieder entfernt.

Die übergeordnete Produkt- und Architekturfrage ist ausdrücklich noch offen,
weil eine Alternativlösung geprüft werden soll. Bis zu dieser Klärung darf
dieses Dokument weder als Architekturentscheidung noch als
Implementierungsauftrag verwendet werden. Der verworfene Serverentwurf liegt
unter
`docs/archive/2026-07-25_SERVER_SESSION_PROFILE_SPECIFICATION_VERWORFEN.md`.

## Kontext

Zum Zeitpunkt des damaligen Diagnoselaufs war der RealtimeSTT-Server mit
`hey_jarvis` als Wake Word konfiguriert. Ein `start`-Befehl führte deshalb
nicht unmittelbar zur Diktieraufnahme, sondern zunächst in `wakeword_wait`.
Der Lauf bestätigte, dass Wake-Word-Erkennung, Aufnahme, Realtime-Text und
Finaltext technisch funktionieren. Danach wurde das Wake Word auf dem Server
global deaktiviert.

Für den Desktop-Client werden zwei unterschiedliche Nutzungssituationen benötigt:

- eine bewusst per globalem Hotkey gestartete, unmittelbare Diktieraufnahme,
- eine dauerhaft laufende Hintergrundsession, die erst durch ein Wake Word freigegeben wird.

Der produktive WebSocket-Vertrag bietet derzeit keine per-Session-Umschaltung des Wake Words. Die administrative Serverkonfiguration wirkt serverweit beziehungsweise auf neue Sessions und darf nicht mit einem Admin-Schlüssel in den normalen Desktop-Client verlagert werden.

## Zurückgezogener Vorschlag

Der Entwurf sah für den späteren Client zwei konfigurierbare Betriebsarten vor:

1. **Direkter Hotkey-Modus:** Der Aufnahme-Hotkey gibt die Diktieraufnahme ohne zusätzliches Wake Word frei. Dieser Modus wird zuerst umgesetzt.
2. **Dauerhafter Wake-Word-Modus:** Eine Session läuft ständig im Hintergrund und überträgt Audio kontinuierlich. Das konfigurierte Wake Word gibt die Aufnahme frei. Dieser Modus folgt später.

Die Betriebsart sollte eine ausdrückliche Produkteinstellung sein und nicht
indirekt aus einem zufällig aktiven Server-Wake-Word abgeleitet werden.

Als technische Umsetzung wurde eine sichere serverseitige Trennung erwogen,
beispielsweise eine per-Session-Option, ein Session-Profil oder ein separater
Endpunkt. Die konkret spezifizierte Sessionprofil-Variante ist verworfen.

Unabhängig von der noch offenen Alternativlösung bleibt `wakeword_wait` ein
gültiger Zustand des vorhandenen Serverprotokolls. Der Client darf keine
erfolgreiche direkte Freigabe vortäuschen.

## Alternativen

### Immer Wake Word verlangen

Verworfen als alleiniger Modus, weil der bewusst betätigte Aufnahme-Hotkey ohne zweite Sprachfreigabe funktionieren soll.

### Wake Word serverweit deaktivieren

Verworfen als Clientlösung, weil dadurch der parallele dauerhafte Wake-Word-Betrieb nicht sauber konfigurierbar wäre und eine normale Desktop-Anwendung keine administrative Serverkonfiguration steuern soll.

### Nur direkten Hotkey-Modus vorsehen

Verworfen, weil die dauerhaft aktive, freisprechbare Hintergrundsession ein ausdrücklich gewünschter späterer Anwendungsfall ist.

## Historisch vorgesehene Folgen

- AP4 sollte Controllerzustände und Befehle offen für beide Betriebsarten
  halten, aber weder Hotkey noch eine erfundene Serverumschaltung
  implementieren.
- Der damalige Entwurf ordnete AP5 Reconnect, Ping-Härtung und eine
  Wiederaufnahme des Diktierwunsches zu. Der Wiederaufnahmeanteil ist
  inzwischen ausdrücklich durch ADR-002 ersetzt.
- AP6 sollte den globalen Hotkey und eine grafische/operative Modusauswahl
  implementieren.
- Der Wake-Word-Modus muss Audio auch in `wakeword_wait` kontinuierlich übertragen.
- Dokumentation und Tests müssen direkte Hotkey-Freigabe und Wake-Word-Freigabe künftig getrennt benennen.

## Aktueller Umgang

- Keine Modusoption in `config.yaml` oder `core/config.py`.
- Kein Sessionprofil oder Wake-Word-Override im Clientprotokoll.
- Keine vorweggenommene Modusauswahl in AP4 oder AP6.
- Die alternative Lösung und ihre Auswirkungen werden erst nach der
  ausstehenden Besprechung verbindlich dokumentiert.

Nachtrag vom 25. Juli 2026: Die historische Aussage dieses zurückgezogenen
Entwurfs, AP5 müsse einen Diktierwunsch nach Reconnect wiederaufnehmen, ist
durch ADR-002 ausdrücklich ersetzt. Der Transport heilt sich; das
unterbrochene Diktat endet und wird nicht automatisch fortgesetzt.
