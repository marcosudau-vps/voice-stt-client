# ADR-002 – Stille Selbstheilung und Ende eines Diktats bei Transportverlust

Status: angenommen; verbindlich  
Datum: 2026-07-25  
Gültig ab: Planung und Umsetzung von AP5

## Entscheidung in einem Satz

Der Client stellt seine Transportverbindung bei vorübergehenden Störungen
unauffällig und zeitlich unbegrenzt wieder her; ein dabei unterbrochenes Diktat
ist jedoch endgültig beendet, sein Audio wird verworfen und nach dem Reconnect
niemals automatisch fortgesetzt.

## Kontext

Der Windows-Client soll dauerhaft im Hintergrund laufen. Netzwerk-,
Server- oder Ping-Störungen dürfen deshalb weder die Anwendung dauerhaft
stilllegen noch den Benutzer mit wiederkehrenden Dialogen belästigen.

Ein Transport-Reconnect erzeugt laut Serververtrag eine neue WebSocket-Session.
Die neue Session besitzt einen neuen Lebenszyklus und darf weder alte
Audiopakete noch einen impliziten alten Aufnahmeauftrag übernehmen. Eine
automatische Fortsetzung wäre außerdem für den Benutzer überraschend: Die
Aufnahme könnte zu einem späteren Zeitpunkt ohne erneute bewusste Aktion wieder
beginnen.

## Verbindliche Entscheidung

### 1. Transport und Diktat sind getrennte Lebenszyklen

- Der Transport darf und soll sich im Hintergrund selbst heilen.
- Ein Diktat ist an genau die Session gebunden, in der es gestartet wurde.
- Verliert diese Session während `starting` oder `active` ihre
  Verwendbarkeit, endet das Diktat.
- Die neue Session beginnt immer ohne übernommenen Diktierwunsch.
- Zum Start eines weiteren Diktats ist eine neue ausdrückliche Benutzeraktion
  erforderlich.

### 2. Kein Audio über Sessiongrenzen

- Nicht gesendete Audiopakete der alten Session werden verworfen.
- Es gibt keinen Offline-Puffer und kein Replay nach einem Reconnect.
- Realtime-Zwischentext wird nie zu einem künstlichen Finaltext hochgestuft.
- Ein echter Finaltext, den der Server vor dem Abbruch vollständig geliefert
  hat, wird weiterhin regulär verarbeitet.

### 3. Stille, unbegrenzte Transportwiederherstellung

- Solange die Anwendung läuft und nicht heruntergefahren wird, versucht sie
  nach wiederherstellbaren Fehlern zeitlich unbegrenzt einen Reconnect.
- Die Versuche erfolgen mit begrenztem exponentiellem Backoff und Jitter.
- Wiederholte passive Fehler erzeugen keine modalen Dialoge, Popups oder
  Benachrichtigungsstürme.
- Die spätere UI darf den dauerhaften Zustand dezent darstellen, etwa durch
  einen Tray-Indikator.
- Die erfolgreiche Selbstheilung ist still; sie startet kein Diktat.

### 4. Sichtbares Feedback nur bei unmittelbarer Benutzerrelevanz

Ein kurzes, UI-neutrales Feedbacksignal wird erzeugt, wenn:

- der Benutzer ein Diktat anfordert, der Start aber aktuell blockiert ist,
- ein angeforderter Start nicht bestätigt wird oder fehlschlägt,
- ein laufendes Diktat durch eine Störung beendet wird.

AP5 liefert nur Status- und Ereignissignale. Farben, Animationen und die
Darstellung im Tray oder Overlay gehören zu AP6. Passive Reconnectversuche
erzeugen kein wiederholtes Benutzerfeedback.

### 5. Kein verzögerter Benutzerbefehl

Ein Startversuch, während der Transport nicht `READY` ist, wird sofort und
ehrlich abgelehnt. Er wird nicht vorgemerkt und nach einem späteren Reconnect
nicht unerwartet ausgeführt.

Die bestehende headless Startautomatik beim allerersten Programmstart darf als
interne Startoption erhalten bleiben. Sie ist kein Benutzerbefehl und darf
insbesondere nach dem Abbruch eines Diktats nicht erneut ausgelöst werden.

### 6. Stop während eines Reconnects

Da ein unterbrochenes Diktat bereits beendet ist, ist `stop_dictation` während
eines Reconnects idempotent. Der Befehl darf die Hintergrundheilung des
Transports nicht abbrechen.

### 7. Zuständigkeit von AP5 und AP7

AP5 behandelt Transport-, Protokoll-, Server- und Pingfehler sowie die
UI-neutrale Zustandsbasis.

Die tatsächliche Wiederherstellung nach Mikrofonverlust, Hot-Plug,
Gerätewechsel sowie Windows-Sleep/Wake gehört verbindlich zu AP7. AP5 darf
dafür Erweiterungspunkte und reservierte Statusgründe vorsehen, aber diese
spätere Geräte- und Betriebssystemlogik nicht vorwegnehmen.

## Begründung

Die Entscheidung kombiniert zwei Ziele, ohne ihre Semantik zu vermischen:

1. Der dauerhaft laufende Client erholt sich zuverlässig und unauffällig.
2. Eine Aufnahme bleibt eine bewusste, zeitlich klar begrenzte
   Benutzerhandlung.

Damit wird verhindert, dass Audio aus verschiedenen Sessions vermischt wird,
ein alter Aufnahmeauftrag überraschend wieder aktiv wird oder die
Hintergrundanwendung bei längerem Netzausfall störende Meldungen wiederholt.

## Verworfene Alternativen

### Diktat nach Reconnect automatisch fortsetzen

Verworfen. Dies würde einen alten Benutzerwunsch über eine Sessiongrenze
tragen, könnte zu unerwarteter späterer Aufnahme führen und widerspricht der
Servervorgabe, altes Audio nicht in eine neue Session einzuspielen.

### Audiopakete lokal puffern und später nachsenden

Verworfen. Zeitpunkt, Segmentzuordnung und Spracheingabekontext wären nicht
mehr verlässlich. Zusätzlich entstünden unbeschränkte Speicher- und
Latenzrisiken.

### Nach mehreren Fehlern dauerhaft aufgeben

Verworfen. Der Client soll dauerhaft im Hintergrund verfügbar sein und nach
der Behebung eines externen Problems selbstständig wieder `READY` werden.

### Für jeden Reconnectfehler einen Dialog anzeigen

Verworfen. Passive Infrastrukturstörungen sollen die Arbeit nicht
unterbrechen. Sichtbares Feedback ist auf eine unmittelbar betroffene
Benutzeraktion oder ein abgebrochenes aktives Diktat begrenzt.

## Folgen für die Umsetzung

- AP5 muss den bestehenden Wunschzustand und die Startautomatik so korrigieren,
  dass kein Benutzerstart über einen nicht bereiten Transport hinweg
  gespeichert wird.
- `start` gilt erst nach einer passenden serverseitigen Statusbestätigung als
  erfolgreich.
- Die Audioqueue wird bei Sessionende, fehlgeschlagenem Start und
  Diktatabbruch geleert.
- Ping-Misses müssen zuverlässig erkannt werden und bei Überschreiten der
  Schwelle einen Transport-Reconnect auslösen.
- Der Controller erhält persistente, UI-neutrale Zustandsinformationen sowie
  sparsame transiente Feedbackereignisse.
- AP6 bildet diese Informationen später auf Tray und Overlay ab.
- AP7 ergänzt Mikrofon-, Geräte- und Sleep/Wake-Heilung.

Die vollständigen Zustände, Zeitgrenzen, Fehlertaxonomie und Abnahmekriterien
stehen im verbindlichen Paketvertrag
`docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md`.
