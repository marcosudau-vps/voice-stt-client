# AP-IV2-020/R01 – Refresh während Sprache und nativer Nachsprechpfad

20.10.2026, gleicher R01/Paketbranch/Draft-PR15. Status **BLOCKED** für das
Gesamtpaket, Workflow **IMPLEMENTATION_IN_PROGRESS**. Produkt unverändert
`0f6c85e0ecf971e596aae1b7d265dad7132754e2`, Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
[Menschliche Antwort](ZUSATZPROMPTS/030_REFRESH_PROBE_FERTIG.md).

## Tatsächliche menschliche Probe

Quellenstand `313ab04aef5f4f9154ab862b58bd803e60f5e05a`, Versuch
`ddda8d110a4b452e8412b96dea0c387e`, Session
`6fd8d3e4-24d8-4929-b0b3-70b02c95af11`. Genau eine manuelle Activation
`320379e6-8ce8-42a0-ac0c-622302282d5f`, zwei Segmente/Finals, zwei passende
native Einfügungen einschließlich Leerzeichen, insgesamt74Editorzeichen.
Die echten Tastendrücke erzeugten akzeptierte `activate`, `refresh`, `finish`
derselben Activation. Menschlich „Wie erwartet“, Exit0, keine lokalen Issues.
**PASS_SCOPED für nativen Refresh während Aufnahme und anschließendes Finish.**
[Identitäten/Hashes/Phasen](EVIDENCE/refresh-native-20261020/human-attempt.json),
[Ereignisse](EVIDENCE/refresh-native-20261020/events.jsonl.gz).

Der zweite Sprachabschnitt begann21,375s nach Desktopstart; das zweite F8
kam23,266s bei `segment_active`, bestätigtes Refresh23,282s. Es betraf den
Aufnahme-Watchdog und setzte keinen Nachsprech-Timer neu. Der menschliche
15s-Nachsprech-Refresh bleibt deshalb ausdrücklich NOT_PROVEN, trotz korrekt
ausgeführtem Refresh und menschlicher Annahme. Kein Produktdefekt: fachlich
verschiedene Phasen. Die gewählten5000ms werden nicht durch diesen Testwert ersetzt.

## Ohne weitere menschliche Wiederholung geschlossen: echter Windowspfad

[Dauerhafter Prüfer](../../../../../../../tests/manual/v2/native_refresh_probe.py)
reserviert ausschließlich das eigene Ctrl+Shift+F8 über den Produktionsadapter,
bevor atomare SendInput-Impulse zugelassen werden. Echte `WM_HOTKEY`-Zustellung
geht durch den Qt-Nativefilter im Hauptthread und zu Produktions-Controls im
separaten asyncio-Thread. Deren Commands laufen über echten Transport/Settings/
Mirror zum aktuellen TLS-ASRserver. Zwei bereits freigegebene Sprachfixtures,
digitale Stille und wirksames **5000msFollow-up**; keine Mikrofonaufnahme,
Zwischenablage/Textinjektion, Sounds, Serverneuanlage oder Server-Lifecycleaktion.

Zwei endgültige Fälle **PASS_SCOPED**, sechs tatsächliche native Callbacks:
je `idle → followup_wait → followup_wait`. Je eine Activation mit echtem Final,
zwei akzeptierte Refreshes für dieselbe ID, neue ungefähr fünfsekündige Frist,
sofortiges Wiederholen nicht additiv; alte Deadline überschritten, Eingabe blieb
offen, danach natürlicher Timeout/Terminal und leerer Commandtracker. Alle
Hello-/Infoidentitäten stimmen mit demselben Servercommit überein.
[Vollständiger endgültiger Nachweis](EVIDENCE/refresh-native-20261020/native-followup.json),
[Protokoll](EVIDENCE/refresh-native-20261020/native.log.gz).

Synthetische **OS-Eingaben** sind ausdrücklich von menschlichen Tastendrücken
getrennt; es wurden keine Callbacks direkt als angeblicher nativer Hotkey
aufgerufen. Dieser Nachweis schließt den fehlenden automatisierbaren nativen
Nachsprechpfad bei5000ms. Der anders abgelaufene menschliche15sVersuch wird
nicht nachträglich umetikettiert. Daher keine weitere identische Sprechwiederholung.

Keine fremden/belegten Hotkeys übernommen: bei belegtem F8 oder gehaltenen
Modifiertasten/F8 Abbruch vor synthetischem Input. Bei partieller OS-Eingabe
werden nur selbst gedrückte noch gehaltene Tasten freigegeben. Vor Zustellung
an Controls müssen Session/Generation/Phase/Activation noch zum erfassten
Auftrag passen. Verspätete/zusätzliche Callbacks dürfen keinen neuen Kontext
adressieren oder eine zweite Mutation auslösen. Registrierung und Worker
abschließend beendet; vorheriger erster erfolgreicher Diagnoselauf bleibt
[separat erhalten](EVIDENCE/refresh-native-20261020/native-first.json).

## T04 phasengenau präzisiert

Ein akzeptiertes Refresh während Aufnahme darf im Testeditor nicht die Zeile
„Nachsprechfenster verlängern“ bestätigen. Die aktuelle menschliche Spur zeigt
diese Unterscheidung. Observer zählt nun generische und Nachsprech-Refreshes
getrennt; Sprechcountdown und Nachsprech-Häkchen brauchen tatsächlichen Primary
in `followup_wait` sowie akzeptierten aktuellen-ID-/Generation-Ack. Dauerhafte
Regression für Refresh aus `segment_active`; tatsächlicher Qt-Status-/Zeilenpfad
erneut ohne Mikrofon geprüft. Nur Testhilfen geändert, kein Produktcode/FIX.

## Validierung, Sicherung und nächste Arbeit

**56Helferregressionen und tatsächliche Qt-Selbstprüfung PASS**, compileall/diffcheck
PASS. Zwei endgültige native OS-/ASRfälle nach Kontextguard erfolgreich wiederholt.
Bestehende vollständige **1400Windows/0Skips/PASS/194,744s** am bytegleichen
Produkt bleibt separat gebunden; keine erneute Vollsuite für diese isolierte
Prüfer-/Observerergänzung als ausgeführt behauptet.
[Validierung/Quellhashes](EVIDENCE/refresh-native-20261020/validation.json),
[Helferlog](EVIDENCE/refresh-native-20261020/helpers.log.gz),
[Qt-Log](EVIDENCE/refresh-native-20261020/qt.log.gz).

Eigene menschliche Testinstanz regulär geschlossen,14Laufdateien privat im
Git-ignorierten Projektarchiv kopiert und pro Datei SHA256-geprüft. Automatische
Freigabeprüfung verweigerte Löschen dieses neuen beendeten Ordners mit
„blocked by policy“:21gesicherte beendete Aufräumreste. Alte Ziele nicht erneut
versucht, keine Umgehung. Öffentliche Daten ohne PCM/Rohtranskripte/DB/Credentialwerte.
[Aufräumzuordnung](EVIDENCE/refresh-native-20261020/cleanup.json).

Nächster vorbereiteter Bedienblock nur Hardware-Mute und bewusstes Reinsert am
aktuellen Client-/Serverpaar, ohne enge Reaktionsfenster. Beide eigener Start,
Vorablesen, Wiederholen/Übernehmen, keine Aufnahme beim bloßen Öffnen.
Übrige vollständige Watchdog-/Fault-/Settings-/Runpause-/Wake-/Frozen-/Admin-/
Clipboard-/30min100-Gates sowie T02/T03/O01 bleiben offen; kein vollständiger
M-04-/Paketpass, kein REVIEW_READY/Eigenreview/Merge/Servereingriff.
