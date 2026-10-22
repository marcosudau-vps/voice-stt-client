# AP-IV2-020/R01 – Admin, UAC und EXE-Abschlussproben

Status **BLOCKED** / IMPLEMENTATION_IN_PROGRESS,22.10.2026. Gleicher Paketbranch
und kumulativer Draft-PR15; kein Eigenreview, Merge oder Servereingriff.
Ausgangskandidat a97ede1cf9b15a8b157ef548096ce1c37c93f509,
Baum25e79adfe9d93f56e8c8acb89b18c7fdba078cd9, kanonischer
Parent b80ed8b81ad92bd02ac32553883443d2b7673bcd.

Produkt unverändert0f6c85e0ecf971e596aae1b7d265dad7132754e2;
normale qualifizierte EXE aus dist-iv2-020-usb, SHA256
e20059f6dff1279cb23fb01576d447fb285aa94cb270d71968b8430a063a15fc.
Server67f3ce45f6ea1ff659382e40c194c70bd33d58ff,
sauberer Baum74f37cad84c5be9e74d880a4b10c3d9623de7da3,
Pro2.0.0, Instanz14e6ff8dc2704f7298924b0d1de5cd1b.
Vor-/Nachinformationen identisch. Ausschließlich das vereinbarte Pro-V2-Ziel.

[Menschliche Festlegung](ZUSATZPROMPTS/036_ADMIN_UAC_UND_WAHRNEHMUNGSABSCHLUSS.md)
stellt Adminquelle/UAC bereit und beendet weitere subjektive
Wahrnehmungsabfragen. [Fehlerrückmeldung](ZUSATZPROMPTS/037_MINIMALER_EXE_TEST_UND_WIEDERHOLUNG.md)
begründet die vereinfachte Testhilfe. Keine neuen Produktänderungen.

## Nachweise und Grenzen

Die [Einzelberichte](EVIDENCE/final-probes-20261022/runs.json) erhalten auch
Fehlversuche. Private History/Profile/Originalclipboarddaten bleiben außerhalb
Git im ignorierten privaten Archiv. Öffentliche Editor-Baselines enthalten
nur Zeichenanzahl und SHA256, keine Nutztexte.

| Prüfung | Tatsächliches Ergebnis |
| --- | --- |
| Positiver Admincheck | PASS_SCOPED: echter Guard am richtigen Origin, Generationwechsel invalidiert Verifikation, erneuter Check erfolgreich; Defaults/Vault unverändert, In-Memory-Key gelöscht, kein Key in eigenen Dateien. |
| Erhöhtes Ziel/UAC | Mensch bestätigte eigenes erhöhtes Qt-Ziel. Medium-Quelle, Ziel elevated, keine sichtbare Einfügung/keine empfangene Taste. Native API meldet trotzdem4/4Events. Produktionsstatus command_sent bedeutet ausschließlich APIannahme, ausdrücklich keine Einfügebestätigung; keine automatische Wiederholung. |
| Erster UAC-Helferversuch | FAIL erhalten: Testannahme, dass Windows zwingend0Events/failed liefern müsse, war falsch. Zweiter instrumentierter Lauf PASS_SCOPED für API-/Statusvertrag und beobachtete Berechtigungsgrenze; kein erfolgreiches Elevated-Paste behauptet. |
| Menschlicher ReSpeaker-/EXE-Versuch | ASR und persistente History enthalten den gesprochenen Satz korrekt. Automatischer Versuch command_sent/4Events, richtiger eigener Ziel-PID, aber Editor0Zeichen. Sichtbare Einfügung FAIL; Gesamtlauf durch Fokusverlust abgebrochen. Ursache nicht bewiesen, keine Produktkorrektur behauptet. |
| Native Sourcekontrolle | Normalfall, echte Clipboard-Sperre, Prozessabbruch vor/nach SendInput und unknown/kein Autoretry erneut PASS_SCOPED; Originalformate wiederhergestellt. |
| EXE-Wiedereinfügen ohne erneute Sprache | Genau derselbe private Testtext über echtes F11 sichtbar korrekt eingefügt,38Zeichen. Beide Prozesse Medium-integrity8192, UIAccess/AppContainer0. Gesamtbericht weiterhin NOT_PROVEN für nicht ausgeführte Sprachfälle; bewusster Reinsert separat bestanden. |
| Erste autonome Akustikversuche | Defaultlautsprecherprobe lieferte am ReSpeaker keine verwertbare Sprache: TIMEOUT. Stereomix mit ungeeignetem16k/Mono-Rezept: Captureabbruch/TIMEOUT. Beides kein ersatzweiser Hardware-PASS. |
| EXE mit Windows-Stereomix im nativen Format | PASS_SCOPED für drei echte Modell-/Audio-/Windows-Einfügepfade: Manual, Alexa, Hey Jarvis;3Finals/3Historyeinträge/3exakte sichtbare Übernahmen des jeweiligen ASRtexts,2Wakehits. Echtes PortAudio44100Hz/2Kanäle und wahrheitsgemäße Wiremetadaten, kein PCM-/Clipboardmock. Anderes Eingabegerät, kein ReSpeaker-PASS. |

Stereomix-Jarvisprobe enthält eine ASR-Wortabweichung gegenüber dem bewussten
Referenzsatz. Die Einfügung übernimmt exakt den ASRtext; PASS_SCOPED bezieht
sich auf Lifecycle/Einfügung, nicht auf perfekte Transkriptionsqualität.
Der erste automatische ReSpeaker-Pastefehler ist durch erfolgreiche Source-,
Reinsert- und Stereomixproben nicht ursächlich aufgeklärt.

## Dauerhafte Testhilfe und minimale menschliche Aktion

tests/manual/v2/frozen_acoustic_probe.py startet ausschließlich die oben
gehashte normale EXE und eigene Profile im genehmigten Namensraum. Im
menschlichen Modus erst nach Startklick, keine Aufnahme vor dem Klick.
Alle Schritte und der grüne Satz vorher sichtbar; Verbindung abwarten und
acht Sekunden Vorbereitung, dann leuchtende Sprechzeile. Eine Wake-Aufgabe
benötigt keine F8/F9-Tasten. Keine automatische Folgeaufgabe. Bei fehlender
Einfügung kann der idle Versuch unabhängig vom Erfolg beendet und wiederholt
werden; fehlgeschlagene History wird nicht zur Pflichtausgabe des nächsten
Versuchs. Doppelte Wiederholungen desselben Falls ersetzen keinen anderen Fall.

Vorbereitet: frozen-live-minimal-ready, genau ein Alexa-Satz über ReSpeaker.
Noch nicht ausgeführte Vorbereitung bleibt NOT_RUN/NOT_PROVEN. Der eigene
Editor wartet auf Start; Client/Mikrofon laufen vor diesem Klick nicht.
Nach Erfolg beendet der Helfer die eigene EXE und sich selbst; keine erneute
subjektive Feedbackbewertung erforderlich. Danach Ergebnisse automatisch
auswerten und auch dieses Profil archivieren/entfernen.

## Regression und Abgabegrenze

80Helfertests/0Skips PASS, Qt-Selfcheck PASS, compileall PASS. Vier neue
Versuchsbewertungsregressionen verhindern vergiftete Retry-Baselines und
falschen Gesamt-PASS durch Wiederholung nur eines Falls; drei Adminlesetests
prüfen Literalwerte, fehlende Variable und mehrzeilige Ablehnung ohne Keyecho.
Die vollständige kandidatengebundene Windows-Suite aus
[Bericht37](37_AUTONOME_RESTQUALIFIKATION_UND_MENSCHLICHE_GRENZEN.md)
bleibt gültig:1400Tests/0Skips/241,656s. Produkt-/Buildquellen bytegleich,
kein neuer Produktbuild. Neue Helferstände sind gehasht; die Erstversuche
identifizieren ihren damaligen Helfer über die Laufidentität, nicht pauschal
über den zuletzt überarbeiteten Helferquelltext.

Adminrest geschlossen. UAC-/APIgrenze nun beobachtet. Weitere subjektive
Kalibrierung gemäß Mensch beendet; bestehende5000ms/320ms und LED-Testwerte
unverändert, keine Übernahme strengerer Wakevarianten als Default.
Aktuelle ReSpeaker-EXE-Probe, technische Restgrenzen der
[fallgenauen Matrix](EVIDENCE/final-probes-20261022/qualification-matrix.json)
und abschließende Aktenprüfung bleiben vor REVIEW_READY erforderlich.
M-05/06-Pendingfinal-/Hardwarekombination, M-10-Frozen-Altfinal/Baufnahme und
physische Dauer-/Umweltgrenzen sind durch einen Stereomixvergleich nicht
automatisch vollständig bewiesen. W02 bleibt menschlich geschlossen.

Zehn beendete eigene Laufzeitordner einschließlich aller Fehlversuche privat
hashgesichert und mit dem geprüften PowerShell-Skript entfernt; leeres
Helfer-TEMP-Verzeichnis ebenfalls entfernt. Nur die ausdrücklich vorbereitete
noch nicht gestartete menschliche Probe bleibt bis zu ihrer Durchführung.
Keine V1-Daten/Serverdefaults geändert. Cleanupbelege im Evidenzverzeichnis.
