# Idle-Kalibrierung bestätigt und LED-Ausfall isoliert – 19.10.2026

Status **BLOCKED**, ausführbarer Workflow **IMPLEMENTATION_IN_PROGRESS**.
Derselbe R01/Paketbranch/Draft-PR15; Produkt0f6c85e unverändert, R11 CLOSED.
Kein REVIEW_READY, Eigenreview, Merge oder Servereingriff.

## Bestätigter Idle-Wert

[Originaler LED-only-Durchlauf](EVIDENCE/idle-confirmed-20261019/human-result.json):
Versuch0b01f5bf, realer ReSpeaker, selfCheck=false, deviceAvailableObserved=true,
20sBeobachtungszeit. Menschliche Wahl ausdrücklich **„Passt – weiß und angenehme
Mindesthelligkeit“**. [Zuordnung](EVIDENCE/idle-confirmed-20261019/assessment.json).
Vorschau-/Konfigurations-/Produktcontrollerhashes stimmten bei Auswertung mit
beobachteten Dateien überein. Nachträglich nur der Bestätigungskommentar der
Konfigurationsdatei aktualisiert; normalisierte Parameter bleiben identisch.

Damit ist die direkte Idle-Wahrnehmung **PASS_SCOPED / CALIBRATION_CONFIRMED**:
weiß`#FFFFFF`, Minimum0,30, Maximum1,0, Geschwindigkeit0,45/Periodendauer8,889s.
Globale Helligkeit bleibt192/255; Prozentangaben beziehen sich auf den Effekt.
Reproduzierbar gespeichert in`tests/manual/v2/calibration.yaml`, vom vorhandenen
Testprofilgenerator in das normale Feedbackmapping übernommen.
Keine Produkt-/Release-/Serverdefaults geändert und keine neuen Umgebungsvariablen.
Die gewählten Testwerte sind nach erneutem Profilaufbau wieder verfügbar;
V1-Einstellungen bleiben geschützt. Farbprofile weiterhin separates späteres Feature.

Es war keine Activation, Mikrofonaufnahme, Hotkeybedienung oder Serververbindung
für diesen Sichtnachweis nötig. Die frühere Rückmeldung ohne Zielübergang wird
nicht nachträglich umgedeutet; der jetzt bestätigte direkte Versuch ersetzt nur
diese konkrete Beleglücke. Gesamtes M-10, Wake-/Both-/Frozen-Parität und übrige
Feedbackphasen sind damit nicht pauschal abgenommen.

## Zusätzlich autonom: echter LED-only-Ausfall im Source-Desktop

Nach sauberem Ende der Vorschau wurde die unabhängige M-06-Unterprüfung vorbereitet:
eigener Source-Desktop mit echtem Mikrofon/Qt/LED/Core und dem ausgewählten
vorhandenen Pro-V2, Manual-only, Hotkeys/Sounds deaktiviert, keine Activation.
Kontrolliert nur den eigenen nativen LED-USB-Transport gestoppt; Audiointerface
und Server unverändert. Der tatsächliche Sinkcallback wird beobachtet und unverändert
an den Produktport weitergegeben; keine synthetische Domain-/Servermeldung.

Der [erste Probeausgang](EVIDENCE/idle-confirmed-20261019/led-first-smoke.json)
bleibt **FAIL**: die Hilfsprüfung verlangte zu Unrecht, dass der LED-Kanal nach6s
weiterhin ausgefallen sei. Er hatte sich bereits automatisch wiederverbunden.
Corewarnung war angekommen, Session und Audio blieben stabil. Das ist eine
falsche Testannahme, kein nachgewiesener zusätzlicher Produktfehler.

Der Beobachter behält nun kurzzeitige echte LED-Sinkwechsel über Pollgrenzen;
Prüfanforderung ist beobachteter LED-Ausfall mit isoliertem Audiopfad, nicht das
künstliche Verhindern funktionierender Recovery. Eine gezielte Helferregression
sichert Ausfall→Wiederherstellung zwischen zwei UI-Abfragen ab.

[Neuer tatsächlicher Probeausgang](EVIDENCE/idle-confirmed-20261019/led-pass-smoke.json):
**PASS_SCOPED**. LED-Verlust und automatische Wiederherstellung nativ beobachtet;
Core enthältled_unavailable. Session/Generation unverändert, weiterhin READY,
AudioAvailable=true/kein AudioLost in den1Hz-Proben.151weitere echte Audiopakete
(59→210) während des Beobachtungsfensters, kein zusätzlicher Trigger.
Vollständige erlaubte Wire-/Commandspur enthält während der Störung **keinen**
AudioAvailability-Command. [Nachauswertung](EVIDENCE/idle-confirmed-20261019/led-isolation-assessment.json).
Keine ältere Final-/Aufnahme-/Frozenbehauptung: das war eine kontrollierte native
LED-Kanalstörung bei idle, kein physisches Abziehen des gesamten Geräts.
M-06 während offenem Input/älteren Finals bleibt gesondert zu qualifizieren.

[Erneute lesende Serveridentität](EVIDENCE/idle-confirmed-20261019/server-identity-after.json):
Pinada13b0/gleiches Proimage57a7907b, passende Wheel-/Runtimequellbelege,
Wireunknown bleibt separat sichtbar. Keine Serverinstanz erstellt, kein Restart,
keine Modell-/Default-/Codeänderung. Alle eigenen Testprozesse beendet.

## Prüfungen und Restarbeit

[33Helfertests/Identität und Grenzen](EVIDENCE/idle-confirmed-20261019/validation.json)
PASS, compileall/diffcheck und Aktenkonsistenz geprüft. Unverändertes Produkt behält
seinen vollständigen1400Windows-/Buildnachweis; keine erneute Produktqualifikation
nur aufgrund einer Testhilfe erfunden. Aktueller Code ändert ausschließlich
Diagnose-/Testhilfen, Konfigurationskommentar und Unterlagen.

Aktuelle Checkliste:[07_TESTCHECKLISTE.md](07_TESTCHECKLISTE.md).
Weitere Pflichten bleiben: vollständige Controls-/Watchdog-/Runpausenmatrix;
komponierte Netz-/Logstore-/Pendingfinal- und Settingsfälle; Credential-/Adminnachweis;
Frozen und erhöhte Zielanwendung/Clipboard-/Prozessfehler; nach getrenntem W01-FIX
Wake-/Both-/Grenz-/30min100-Qualifikation. Dafür kein neuer allgemeiner Freigabeprompt.
Idle muss nicht erneut vom Menschen beurteilt werden, solange diese effektiven
Werte, das Muster und die zugrunde liegende Ausgabeimplementierung gleich bleiben.

Drei weitere beendete Laufordner sind vollständig im Projekt privat hashgesichert.
Die automatische Freigabeprüfung lehnte auch deren Entfernung mit ausschließlich
„blocked by policy“ ab. Insgesamt13beendete gesicherte externe Aufräumreste;
[Zuordnung](EVIDENCE/idle-confirmed-20261019/cleanup.json). Keine Umgehung und
keine erneuten Löschversuche bereits abgewiesener Ziele. Keine Rohsprache,
Transkript-/Logdatenbank oder Zugangsdaten öffentlich committed.
