# Geführte unabhängige Bedienprüfungen

19.10.2026 · gleicher AP-IV2-020/R01, Paketbranch und Draft-PR15.
Produktquellen bleiben identisch zu7bb5646; keine neue Produktausnahme.

## Vorbereitet

Gepflegte [Testprogramme und Startanleitung](../../../../../../../tests/manual/v2/README.md).
Der neue Qt-Ablauf zeigt die vollständigen Schritte vorher, den Testsatz groß/grün,
den aktuellen Schritt blau und vergangene Schritte mit Häkchen. Nach echter
Bereitschaft zehn Sekunden Vorbereitung. Jeder Versuch braucht einen eigenen
Start; anschließend Wiederholen, Übernehmen/Weiter oder ausdrücklich offen lassen.
Schrittwechsel erfolgen selbstbestimmt. Ende/Wiederholung wartet auf den eigenen
Clientprozess; es werden weder Server noch fremde Programme beendet.

| Aufgabe | Menschliche Bedienung | Teilnachweis |
| --- | --- | --- |
| 1 | F8, Satz, F9 Finish | M-01/04/11, getrennte O01-Untersuchung |
| 2 | Zwei Sätze mit etwa4s Pause | Mehrsegmente, Follow-up5000ms |
| 3 | F9 Cancel mitten in Sprache | Echte Abbruchsemantik, kein fälschlich als Cancel gewertetes Finish |
| 4 | F8 Refresh in Follow-up | Gleiche Activation, wirkliche Zeitverlängerung |
| 5 | F9 None | Keine mutierende Zweittastenwirkung |
| 6 | Schweigen, LED/Sound/Overlay beobachten | Manual-Phasen, Timeout/Stoppton und konkrete Kalibrierungsnotiz |
| 7 | Hardware-Mute ein/aus | Mute, Rückkehr ohne unbeabsichtigten Trigger |
| 8 | USB während Aufnahme trennen/wieder verbinden | Geräteverlust/Cancel/Recovery, danach neues Diktat |
| 9 | Nur eigenen Client reconnecten | Neue Session/Generation und anschließendes Diktat |
| 10 | Ein ASR-Final, ein bewusstes Reinsert | Genau eine ausdrücklich zusätzliche Einfügung |
| 11 | Einstellungen/Verlauf/Logging öffnen, echte Logs ansehen | T01/T02 und sichtbares Ziel/Feedback |

F8/F9/F11 meint immer Strg+Umschalt plus jeweilige Funktionstaste. F9 ist je
Aufgabe im isolierten Profil ausdrücklich Finish/Cancel/None. Kein Wake-Modell
wird ausgewählt. Bestehendes Pro-V2-Ziel /ws/v2, kein lokaler Ersatzserver,
kein Modellwechsel oder Default-PATCH. Diagnostische HTTP/Open/Admission/
Bootstrapgrenzen180s; feste Protokollinvarianten unverändert.

Der echte ObservabilityManager wird Runtime, Bridge und Desktop gemeinsam
übergeben. Der Produktdesktop arbeitet mit echten Audio-, Qt-, Win32-, LED-,
Sound-, History- und Clipboardkomponenten; lediglich die native Zieleinfügung
ist zusätzlich auf das eigene fokussierte Testfeld begrenzt. Source-Ausführung
ist ausdrücklich kein Frozen-Build-Nachweis. UI-Heartbeatverlust beendet den
eigenen Client; Entscheidungen und Wiederholungen bleiben mit Attempt-ID erhalten.
Exportierte Wirebeobachtung enthält nur erlaubte Metadaten/Hashes, keine Tokens
oder PCM. Tatsächlicher Text/History/Logstore bleibt private Testlaufzeit.

## Autonome Prüfungen und technischer Zwischenstand

- Vorherige zehn Helferregressionen unverändert PASS.
- Sechs neue Helferregressionen PASS; Qt-Vorschau und explizites Weiter ohne
  Client-/Audiostart PASS. Beim Selbsttest entdeckte Überschriften-/Schritt-
  Propertykollision korrigiert und dauerhaft im Qt-Selbsttest abgesichert.
- Echte vorhandene APIs dreimal200; tatsächlicher Source-Desktop/ReSpeaker
  mit abgeschaltetem Wake/Controls/Sound/LED fünf Sekunden stabil READY und
 135 gesendete Audioframes im wiederholten Precheck. Null Activations.
  Erstes Settingsreport Follow-up3000ms, anschließend tatsächliche Bestätigung
  des isolierten Wunsches5000ms. Keine Übertragung alter Community-ASR-Ergebnisse.
- Unicodeausgabe des instrumentierten Prozesses für Windows-Logdateien explizit
  UTF-8 gesetzt; wiederholter Precheck ohne vorherige Encodingfehler.
- Die komplette unveränderte Windows-Produktsuite lief mit1398Tests; die rein
  projektinterne TEMP-/Profilumgebung erzeugt fünf FAIL/einen ERROR. Alle sechs
  betreffen explizite Benutzerprofil-/Historypfadgrenzen bzw. daraus folgende
  ausbleibende Fixture-Datensätze. Dieser Lauf ist **FAIL**, kein grüner Vollnachweis.
  Der reale Starter speicherte zugleich40 echte Logzeilen über seinen Defaultpfad;
  das ist kein Ersatz für die fehlgeschlagenen expliziten Pfadprüfungen.

Die Pfadregeln werden nicht abgeschwächt. Die separat angefragte dedizierte
Windows-Benutzerprofilablage ist bis zu einer tatsächlichen menschlichen Antwort
nicht autorisiert. Externe Dateien wurden hierfür noch nicht angelegt.
Evidenzexport/abschließende Regression und Öffnen des startfähigen Realablaufs
stehen bis zur konkreten Ablageentscheidung aus.

## Offen, durch diesen Ablauf nicht pauschal geschlossen

W01/Issue7, wiederholte Wake-/Both-Folgen, Wake-Parität und gemischte30min/100
bleiben zurückgestellt. Weitere Controls-/Watchdog-Kombinationen, getrennte
Run-Pausen/Neustart, isolierter LED-/Logausfall, Netzverlust mit Preview/Pending,
Sessionänderungen Cancel/Finish/Defer, native Credentials/Adminprüfung sowie
elevated Ziel/Clipboardkonflikt/Crash/Frozen benötigen die jeweiligen eigenen
Vorbereitungen und Evidenzen. Die Oberfläche zeigt diese Restanteile ausdrücklich.

Menschliches Übernehmen, Prozess-Exit0 oder eine fehlerfreie Helferprüfung schließen
weder einen ganzen M-Fall noch T01/T02/W01. Die nachfolgende Agentenauswertung
prüft Herkunft, Identität, tatsächliche Wire-/Command-/Paste-/Ressourcenspuren und
Wahrnehmung zusammen. Gesamtabnahme bleibt BLOCKED, Workflow unabhängig weiter
IMPLEMENTATION_IN_PROGRESS, kein REVIEW_READY und kein Eigenreview.
