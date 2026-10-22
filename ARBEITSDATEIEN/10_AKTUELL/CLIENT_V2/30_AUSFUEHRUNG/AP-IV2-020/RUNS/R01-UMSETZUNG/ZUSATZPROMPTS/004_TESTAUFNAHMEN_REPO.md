# Menschliche Ergänzung: bewusst gesprochene Testaufnahmen versionieren

2026-10-15, gleicher AP-IV2-020/R01. Direkte Antwort des Auftraggebers auf den
sechsfachen, per Klick gestarteten Aufnahmeblock:

> Alle sechs Aufnahmen sind abgeschlossen. Aber ich habe den Hinweis gelesen, dass die nur lokal bleiben. Könntest du die vielleicht mit ins Repo packen? Beziehungsweise halt erst mal lokal, aber so, dass die beim nächsten Push mit in das Repo gepusht werden und wiederverwendet werden können von anderen Agentenläufen später. Genauso wie deine Testskripte oder Messskripte oder was du da auch immer verwendest.

Zweite direkte Antwort zur Durchführung und Fokus-/Samplezuordnung:

> nirgends sichtbar. hätte ich da reinklicken gemusst? Das habe ich mir nicht getan. Und zudem eben zu der ersten Aufnahme das Problem war, dass ich bereits vor Ablauf des drei Sekunden Timeouts am Anfang gesprochen habe. Deshalb ist Hey Jarvis nicht mit drauf. Und wenn dir das hilft: Im Verlauf meiner Zwischenablage ist der letzte Eintrag mit dem roten Ball. Und davor einmal "Alexa" und als drittletztes einmal die grüne Lampe steht neben dem Fenster.

## Konkrete Anwendung

Die sechs bewusst aufgenommenen neunsekündigen Test-WAVs werden bytegleich mit
Metadaten, SHA256, tatsächlicher Herkunft/Abweichung und wiederverwendbaren
Messskripten im Paketbranch versioniert und beim nächsten autorisierten Push
in denselben Draft-PR aufgenommen. Die bisherige lokale Ablage wird erhalten.

Diese ausdrückliche Nutzerfestlegung überschreibt für genau diese Testfixtures
die zuvor angekündigte Beschränkung auf lokale Audiodateien und konkretisiert
die Regel „keine privaten Sprachaufnahmen in Git“ der Hardware-Nachweisreferenz.
Andere private Aufnahmen, Laufzeit-History, Credentials und unaufgeforderte
Mikrofonmitschnitte bleiben ausgeschlossen. Keine Veröffentlichung allgemeiner
Benutzer-Sprachdaten aus den Live-Sitzungen.

`jarvis_pause.wav` enthält laut Auftraggeber keinen Wakeanteil, weil er vor dem
Countdownende gesprochen hat. Originaldatei/ursprünglicher Prompt bleiben
erhalten; tatsächlich ist diese Aufnahme Nutzsprache ohne Wake. Sie zählt als
Negativkontrolle, niemals als fehlgeschlagener positiver Jarvistest.

Beim ersten Live-Wakeversuch war das Testeditorfeld nicht fokussiert. Die
bestätigten `command_sent`-Versuche/Clipboardinhalte sind damit kein Nachweis
einer sichtbaren Einfügung. Kein Produktfehler allein aus dem leeren Editor.
