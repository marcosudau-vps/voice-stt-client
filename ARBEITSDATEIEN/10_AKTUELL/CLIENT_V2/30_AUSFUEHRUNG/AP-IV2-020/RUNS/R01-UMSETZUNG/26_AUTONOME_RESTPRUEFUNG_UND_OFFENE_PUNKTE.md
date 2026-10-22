# AP-IV2-020/R01 – autonome Restprüfung und konkrete Restarbeit

19.10.2026, gleicher Umsetzer/R01, Branch `work/client-v2/ap-iv2-020`, Draft-PR15
gegen `feat/client-v2`. Status **BLOCKED**, Workflow **IMPLEMENTATION_IN_PROGRESS**.
Kein REVIEW_READY, Eigenreview, Merge, Release oder Servereingriff.
[Auftrag025](ZUSATZPROMPTS/025_RESTPUNKTE_UND_AUTONOME_ERLEDIGUNG.md).

## Jetzt autonom erledigt

Produkt unverändert `0f6c85e0ecf971e596aae1b7d265dad7132754e2`, Start-HEAD
`181ad2ccff18aeb9756c99c3f8cd2b83ec1cc1c1`, kanonischer Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`. Neue Dateien sind Testhilfen,
keine Produktkorrektur. Ausgangs33Helfertests PASS, neue36Helfertests PASS.

**Echter Windows-Credentialspeicher PASS_SCOPED:** Zwei zufällige eigene
`.invalid`-Origins, Speichern/Lesen, Ersetzen, drei frische Leseprozesse,
Origintrennung, Löschen und Lesen nach Löschen. Bestehende reale Servertargets
werden weder gelesen noch geändert. Testwerte nur im Prozess und stdin-Pipe,
keine Werte/Hashes der Werte in Dateien oder Prozessargumenten. Beide eigenen
Einträge abschließend entfernt und ihre Abwesenheit erneut geprüft.
[Ergebnis](EVIDENCE/autonomous-rest-20261019/repeat-credentials.json).
Das belegt den nativen Storelebenszyklus, nicht richtige/falsche Adminauthentifizierung,
Qt-Dialog/Export oder den Frozenprozess; M-09 bleibt insgesamt NOT_PROVEN.

**Run-Pausen/Recovery bei idle PASS_SCOPED:** Tatsächliche Source-Runtime,
Produkt-HTTP/WebSocket/Mirror/Settings/Controls/PortAudio mit realem ReSpeaker
am vorhandenen Pro-V2. Manual- und Wake-Suppression einzeln und zusammen
serverbestätigt. Ein Primary-Versuch bei Manualpause wird lokal blockiert.
Zwei manuelle Reconnects und ein Abbruch ausschließlich des eigenen nativen
TCP-Transports erzeugen neue Sessions/Generationen; beide gewünschten Masken
werden vor Freigabe wieder bestätigt. Im stärkeren Wiederholungslauf nach jedem
Reconnect mindestens25zusätzliche echte Audiopakete abgewartet.
Simuliertes Mute-Signal: echtes AudioUnavailable/Available und Pausen erhalten.
Neue tatsächliche Runtime lädt dasselbe isolierte Profil und startet ohne alte
Run-Pause. Gewählte Nachsprechzeit durchgehend5000ms; keine neue Aktivierung,
kein Pasteversuch, keine Pendingcommands an Messpunkten, reguläre Shutdowns
ohne Cleanupfehler. [Ergebnis](EVIDENCE/autonomous-rest-20261019/repeat-runtime.json).

Der erste Lauf war bereits für die Pausenmasken PASS; er wartete nach dem
Reconnect noch nicht auf zusätzliche Audiopakete. Er bleibt mit seiner damaligen
Quellidentität erhalten; nur die stärkere Wiederholung begründet den zusätzlichen
Audiofortschrittsanspruch. Keine historische Evidenz überschrieben.

Wake war in beiden Runtimes **nicht konfiguriert**. Ein echter Wake-Suppression-
Command ist keine Qualifikation einer laufenden Wakeengine. Software-Mute ist
kein menschlicher Hardware-Mute-Nachweis. Keine Aufnahme/Finals, kein realer
Serverneustart, keine UI-/Frozen-/Hotkeywirkung und kein Dauertest aus dieser Probe.
M-05/M-07 bleiben insgesamt NOT_PROVEN. Kurzzeitmetriken sind kein Leakbeweis
für30Minuten/100Activations.

[Lesende Servernachprüfung](EVIDENCE/autonomous-rest-20261019/server-identity-after.json):
Serverpin `ada13b011e1d3829f78e7f389e3b927795a2b3be`, Proimage
`sha256:57a7907b36389e09ce978efe0ceb18997f34eb729a0b29143bade01e96eb0078`,
passende Wheel-/Git-/vier Runtimequellbelege. Wirecommit weiterhin `unknown`;
voller writable-Layervergleich NOT_PROVEN. Ziel ausschließlich
`wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`,180s diagnostische
Open-/HTTP-/Bootstrapgrenzen, Protokoll-/Ackgrenzen unverändert.

## Konkret noch offen

| Block | Fehlender Pflichtnachweis | Nächste Durchführung und notwendige Beteiligung |
|---|---|---|
| Diktat/Steuerung, M-01/04 | Mehrsegment-/Altfinal-Neuaufnahme-Überlappung, vollständige Refresh/Finish/Cancel/NONE-/Phasenmatrix, reales Watchdog warning→expiry mit ASR | Agent steuert und wertet aus; Mensch spricht bewusste Proben/bedient echte Hotkeys. Watchdog benötigt zulässige tatsächliche Serverwerte; keine ungefragte globale Änderung. |
| Kombinierte Fehler/Settings, M-05/06/07/08 | Runpausen mit tatsächlich aktivierter Wakeengine; LED-only während offenem Input/Altfinal, Netzausfall bei Preview/Pendingfinal, Logstoreausfall, Settings cancel/finish/vormerken und Drain | Agent bereitet gezielte Fehler und Transaktionen vor; Mensch nur für bewusste Sprache/USB-/Muteaktionen. Neuer Idle-Nachweis ersetzt diese Kombinationen nicht. Serverrestart benötigt abgestimmte Bedienung des bestehenden Servers; Agent stoppt ihn nicht eigenständig. |
| Native Windows-/Frozenfälle, M-09/10/11 | Richtiger/falscher Admincheck, Dialog-/Exportnachweis, endgültiges Frozen-/Serverpaar mit Tray/Overlay/Feedback, erhöhte Zielanwendung, Clipboardkonflikt, Reinsert/Prozessabbruch nahe Paste | Agent misst und prüft; echter gültiger Adminzugang muss im vorgesehenen Dialog vorhanden sein, nie im Chat. UAC/erhöhte Zielanwendung und abschließende Wahrnehmung brauchen den Menschen. Overlayänderungswunsch/sonstige Feedbackphasen noch abschließend bewerten. |
| W01 / Wake / Dauer, M-02/03/12 | Wiederholte Wake-/Both-Aufrufe, Trigger-Rennen, Nutzsprachgrenzen/Schwellwert und mindestens30Minuten/100gemischte Activations mit Ressourcen-/Recoveryauswertung | Zuerst gesonderter Server-FIX zu Issue7, anschließend am neuen belegten Paar echte Sprach-/Bedienblöcke und Dauersession. Kein Clientworkaround oder W01-PASS aus Manual-only. |
| Abschluss | Aufräumen, finale Gesamtmatrix/Traceability und REVIEW_READY | Benötigte Nachweise zuerst erfüllen; danach Agentensicherung und unabhängige Abnahme. Automatisch abgelehnte Löschungen bleiben gesonderter technischer Rest. |

**Nicht erneut offen:** UX01/UX02/UX03, R11 physische USB-Recovery,
Stoppton-Lautstärke/-Dauer und bestätigter direkter weißer Idle-Puls30–100%.
Keine erneute Idle-Beurteilung bei unveränderten Werten/Muster/Ausgabecode.
Fünf Sekunden Follow-up bleiben die menschlich gewählte Konfiguration;
Farbprofile bleiben ausdrücklich späteres separates Feature.

M-01..M-12 bleiben fallgenau NOT_RUN/NOT_PROVEN, bis ihre vollständigen
Unterfälle tatsächlich belegt sind; erfolgreiche Teilfälle sind separat
abgelegt. W01 blockiert die zugehörigen Wake-/Daueransprüche und die volle
Paketannahme, **nicht** die vorgezogenen unabhängigen Clientprüfungen.

## Wiederholbarkeit und Sicherung

[Dauerhafter Prüfer](../../../../../../../tests/manual/v2/autonomous_rest.py),
[Regressionen](../../../../../../../tests/manual/v2/test_autonomous_rest.py),
[Befehle/Grenzen](../../../../../../../tests/manual/v2/README.md),
[Evidenz/Validierung](EVIDENCE/autonomous-rest-20261019/validation.json).
Identitäten und vollständige Windows-/Helferlogs werden vor Kandidatenabgabe
gesichert. Laufzeit nur im genehmigten `.voice-stt/qualification/AP-IV2-020`;
Profile/DBs ausschließlich privat Git-ignoriert archiviert, öffentlich nur
erlaubte Metadaten/Zähler/Hashes, kein PCM/Transkript-/Credentialinhalt.


Vollständige erneute Windows-Regression: **1400Tests,0Skips,PASS,197,106s**;
36Helfertests PASS. Vollständige Logs und Laufzeitidentität in der neuen Evidenz.
Compileall, Diffprüfung und Aktenvalidator PASS. Nachvollziehbare Exportmanifeste
binden die privaten Archive und öffentlichen Metadaten; beide Testprozesse beendet.

Zwei neue vollständig privat hashgesicherte beendete Laufordner konnten ebenfalls
nicht entfernt werden: automatische Freigabeprüfung verweigerte den nativen,
auf den genehmigten Namensraum und geprüfte Archive begrenzten Löschbefehl mit
„blocked by policy“. Insgesamt **15** externe Aufräumreste. Keine erneuten Versuche
bereits abgelehnter Ziele und keine Umgehung. Die beiden Credential-Testeinträge
sind dagegen nachweislich aus dem Windows-Vault entfernt.
[Aufräumbeleg](EVIDENCE/autonomous-rest-20261019/cleanup.json).
