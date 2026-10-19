# Geführte manuelle V2-Tests

Aktueller Einstieg, 19.10.2026, derselbe AP-IV2-020/R01:

```powershell
.\venv\Scripts\python.exe -m tests.manual.v2.guided_suite
# oder aus dem Projekt:
.\tests\manual\v2\Start-GuidedTests.ps1
```

**Aktuell Vorschau:** Für echte Läufe ist eine dedizierte Windows-Profilablage
angefragt, noch nicht freigegeben. Erst nach der tatsächlichen Freigabe startet
`--profile-runtime` beziehungsweise `Start-GuidedTests.ps1 -ProfileRuntime`
den bedienbereiten Ablauf. Ohne dieses explizite Argument bleibt Start deaktiviert.

Das Fenster startet zunächst **nur die Aufgabenliste**, keinen Sprachclient.
Alle Schritte und Sätze stehen vorher da. Jede Aufgabe benötigt einen eigenen
**Start**. Nach wirklicher Client-/Audiobereitschaft folgen zehn Sekunden
Vorbereitung. Der aktuelle Schritt ist blau, der Testsatz groß/grün; vergangene
Schritte werden abgehakt. **Schritt erledigt** bewegt die Markierung in deinem
Tempo. **Versuch beenden** stoppt nur diesen Testclient regulär. Danach Ergebnis
auswählen und **Wiederholen**, **Übernehmen → Weiter** oder **Offen lassen → Weiter**.
Die nächste Aufgabe beginnt erst mit dem nächsten Startklick. **Übernehmen ist
kein technisches PASS.** Alle Versuche, auch Wiederholungen, bleiben erhalten.

Die elf Aufgaben bündeln Finish, zwei Segmente/Follow-up, Cancel, Refresh,
None, Feedback/Timeout, Hardware-Mute, USB-Recovery, manuellen Client-Reconnect,
bewusstes Reinsert und Einstellungen/Verlauf/Logs. F8/F9/F11 im Ablauf meint
immer **Strg+Umschalt+F8/F9/F11**. F9 ist pro Aufgabe ausdrücklich Finish, Cancel
oder None; das jeweilige isolierte Profil legt dies vor dem Start fest.
Keine automatisch gestarteten Wake-Versuche, keine rohen Audioaufnahmen.

## Ziel und Isolation

Verwendet wird ausschließlich das vom Auftraggeber ausgewählte vorhandene
`wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`; die alternative Normal-V2-
Adresse ist im URL-Validator explizit zugelassen, aber kein automatischer Fallback.
Serverpin: `ada13b011e1d3829f78e7f389e3b927795a2b3be`, nach separater
[Deployment-/Image-/Quellprüfung](../../../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
Der Draht meldet weiterhin `unknown`; die datierte externe Zuordnung wird nicht
als live vom Server gemeldeter Commit ausgegeben. Pro16-ASR ist ein neues Testpaar.

Der Helfer legt **keinen Server an**, startet/stoppt keinen Server, wechselt keine
Modelle und patcht keine Serverdefaults. Sessionwünsche: Manual an, Wake aus,
Follow-up 5000 ms. Der gewünschte vorläufig weiße LED-Ring mit zwölf leuchtenden
LEDs/Speed6 und weißem Idle wird als Testkonfiguration reproduziert. HTTP,
Connect, Admission und Bootstrap erhalten diagnostisch je180s; keine feste
Wire-/Sicherheitsgrenze und kein Produktdefault wird geändert.

Vorschau-/Helferdaten liegen in **`build/ap-iv2-020-suite/`**, bewusst
Git-ignorierte Testlaufzeit im Projekt. Für vertragskonforme Realläufe und die
expliziten Pfadtests der Produktsuite ist ausschließlich die gesondert angefragte
**`%USERPROFILE%/.voice-stt/qualification/AP-IV2-020/`** als Profil-/TEMP-/Log-/
Test-Historyablage vorbereitet. Ohne konkrete Freigabe dort nichts anlegen.
Keine V1-Konfiguration und keine AppData-Profile werden geladen oder verändert.
ReSpeaker wird vor jedem Versuch erneut gewählt; kein stiller Ersatz durch ein
anderes Mikrofon. Native Einfügung bleibt auf das eigene fokussierte Testfeld
begrenzt. Qt läuft im Main Thread, der Produkt-Core im separaten asyncio-Thread.
Ein echter gemeinsamer ObservabilityManager versorgt Runtime, Bridge und Desktop.

`build/ap-iv2-020-suite/active-suite.json` führt zum aktuellen Lauf. Dort stehen
`report.json` (alle menschlichen Entscheidungen), `identity.json` und je Attempt
`profile.yaml`, `events.jsonl`, `status.json`, `process.log`, isolierte Logs/History
und `test-editor.txt`. Öffentliche Belege erst nach Auswertung und Redigierung
exportieren; Laufzeittext, Datenbanken und Credentials bleiben unversioniert.
Ereignisbeobachter exportiert IDs, Zeiten und Texthashes, keine Logzugangstokens.
Ein verwaister Client stoppt bei ausbleibendem UI-Heartbeat nach15s; ein Versuch
hat einen30min-Schutz. Schließen des Fensters wartet auf reguläres Clientende.

## Ehrliche Grenzen

Die Oberfläche zeigt separat offene Pflichtanteile. Insbesondere bleiben
W01/Issue7, wiederholte Wake-/Both-Folgen, Wake-Parität und der gemischte
30min/100-Lauf zurückgestellt. Die elf Bedienaufgaben sind **Teilprüfungen**,
keine vollständige Abdeckung von M-01 bis M-12. Faulttests mit offenen Finals,
isolierter LED-/Logstörung, Run-Pausen, Sessiontransaktionen, Credentials,
elevated Ziel/Clipboardkonflikt/Crash und Frozen-Build brauchen ihre eigenen
Vorbereitungen/Nachweise. Sie werden nicht durch Klicks auf Weiter geschlossen.

## Helferprüfungen

```powershell
.\venv\Scripts\python.exe -m unittest discover -v -s tests/manual/v2 -p test_*.py
$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m tests.manual.v2.guided_suite --self-check
```

`preflight_suite --profile-runtime` prüft nach derselben Ablagefreigabe zusätzlich echte GET-APIs und fünf Sekunden tatsächliche
Audioübertragung im Manual-only-Produktdesktop, ohne Controls/LED/Sound oder
Activation. Das ist kein menschlicher Bedien- oder Frozen-Nachweis.

Die älteren Module `__main__`, `human_test_editor`, `stepped_wake_trial` und
`observed_session` bleiben historische reproduzierbare Einstiege. Sie erwarten
die **entfernte** lokale Port18020-/AppData-Umgebung und sind für den aktuellen
Durchlauf nicht zu benutzen. `scripts/qualify_v2_session.py prepare` nicht erneut
ausführen; es gehört zur stillgelegten Infrastruktur. Die sechs ausdrücklich
freigegebenen Sprachfixtures bleiben unverändert versioniert.
