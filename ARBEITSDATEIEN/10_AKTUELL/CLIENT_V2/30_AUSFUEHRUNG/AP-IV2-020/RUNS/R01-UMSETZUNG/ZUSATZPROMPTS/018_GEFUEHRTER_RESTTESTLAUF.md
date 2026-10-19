# Geführter Resttestlauf, 19.10.2026

Menschlicher Auftrag im selben R01:

> Okay, das bedeutet kurz und knapp: Was können wir jetzt als Nächstes machen? Kannst du vielleicht direkt die Tests für mich schon vorbereiten? Vielleicht auch so in einem durchgehenden Ablauf, alles was noch offen ist, was ich machen muss, dass ich mich da so durcharbeiten kann und du dann danach alles geschlossen prüfen kannst. Wieder wie mit dem vorgesehenen Oberfläche, wo genau steht, wo ich immer auf Weiter klicken kann. Also wie wir das bisher auch gemacht haben.

Umsetzung: wiederverwendbarer Qt-Ablauf mit vorher lesbaren Aufgaben, eigenen
Start-/Wiederholungs-/Weiterentscheidungen, echter Instrumentierung und späterer
gebündelter Agentenauswertung. Kein automatischer Folgestart und keine automatische
PASS-Wertung durch menschliches Übernehmen. Produktcode, Server und Pflichtgates
bleiben unverändert. Elf vorbereitete unabhängige Bedienaufgaben sind Teilnachweise;
die übrigen technischen und W01-abhängigen Pflichtanteile werden sichtbar offen geführt.

Technische Ablagefrage: projektinterne temporäre Umgebung kollidiert bei sechs
Windows-Regressionen mit der vorgeschriebenen echten Benutzerprofilgrenze.
Ein eigener expliziter menschlicher Entscheid über
`C:\Users\marco\.voice-stt\qualification\AP-IV2-020\` wurde angefragt;
die Anfrage allein erteilt keine externe Schreibfreigabe. Bestehende V1-Profile
bleiben geschützt. Maßgeblicher aktueller Entscheid steht im Bericht20.
