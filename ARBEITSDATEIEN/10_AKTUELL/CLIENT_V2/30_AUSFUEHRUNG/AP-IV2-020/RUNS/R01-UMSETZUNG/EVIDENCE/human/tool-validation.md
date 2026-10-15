# Testhilfen der gemeinsamen Phase

`observed_session.py --self-check`: Identitätsallowlist, effektiver Follow-up,
Text nur als Hash/Länge, Tokens ausgeschlossen PASS. Echter anschließender Wake-
Durchgang mit unangetasteter Produktkette, IDs/Scores korrekt beobachtet.

`record_wake_samples.py --self-check`: synthetischer WAV-Schreibertest PASS;
keine Modell-/Hardwareaussage daraus. Danach sechs echte per Klick gestartete
Aufnahmen, jeweils144000 Samples, reale Pegel, kein gemeldeter Inputoverflow.

`score_real_wake.py --self-check`: Frame-Serialisierung PASS. Echter Aufruf
im isolierten Container auf /qualified erfolgreich, sechs reale WAVs,
unveränderte ONNX-Inferenz/Tracker. Helfer nur unter /tmp; kein Serverproduktdiff.

`replay_real_samples.py`: erster Start durch korrekt restriktive Pfadprüfung
vor WS-Aufbau abgewiesen, weil nur Eingaben statt auch erlaubter Basis über
Windows-Junctions aufgelöst waren. Beide Seiten werden nun aufgelöst; weiterhin
nur der lokale Samplesroot erlaubt. Danach echte Manual-ASR der ersten Aufnahme
erfolgreich: vollständiger vereinbarter Nutzsatz, kein Wakewort im ASR-Resultat.
Das ist kein phonetischer Beweis für fehlendes Wakeaudio. Vollständiger Wake-
Replaylauf am echten Server läuft separat, ohne native Textinjektion.

Ein Folgeaufruf320ms wurde zunächst von der zu eng auf0/80/160 gesetzten
Test-CLI vor Sessionaufbau abgewiesen. Test-CLI jetzt0..1000ms begrenzt,
Server validiert weiterhin sein unverändertes NA-Feld.320/480ms anschließend
erfolgreich real ausgeführt. Keine Produktfehler aus Hilfsmittelabbrüchen abgeleitet.

Nach menschlich bestätigtem Ende aller sechs Aufnahmen wurde ausschließlich
der eigene RecorderPID10600 nach Commandlineprüfung beendet; alle Hashes
erneut geprüft. Aktive V2-/V1-Prozesse wurden dabei nicht beendet.

Passiver Desktopbeobachter um optionale Fokuswartebarriere und bounded-stop
erweitert: startet Audio erst nach frischem foreground-State des eigenen
Testeditors; nach zwei Terminalactivations plus3s läuft die vorhandene Qt-Stop-
Schnittstelle. Zusätzlicher begrenzter Testwatcher, kein Produktcode. Syntax und
Serializer-Selbstcheck PASS; echte bounded Liveprüfung steht noch aus.
