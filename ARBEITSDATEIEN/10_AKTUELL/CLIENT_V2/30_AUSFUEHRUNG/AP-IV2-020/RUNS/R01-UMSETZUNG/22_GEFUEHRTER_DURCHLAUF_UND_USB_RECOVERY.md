# Geführter Durchlauf und USB-Recovery R11 – 19.10.2026

Status **BLOCKED**, ausführbarer Workflow **IMPLEMENTATION_IN_PROGRESS**.
Derselbe R01/Paketbranch/Draft-PR15; keine unabhängige Abnahme, kein REVIEW_READY.

## Herkunft und Auswertung

Mensch: „Durchlauf fertig.“ Alle11 Aufgaben bearbeitet,15 Versuche,14 echte
Activations. Start/Repeat/Übernehmen sind Bedienentscheidungen, keine automatischen
PASS-Urteile. Sourceprodukt7bb5646, Helfercommitf8bef5d; kein Frozen-Nachweis.
[Einzelergebnisse](EVIDENCE/guided-results-20261019/task-assessment.json),
[alle Versuche einschließlich menschlicher Anmerkungen](EVIDENCE/guided-results-20261019/attempts.json),
[Identität](EVIDENCE/guided-results-20261019/identity.json).

| Aufgabe | Tatsächlicher Teilnachweis / Rest |
|---|---|
| finish | **PARTIAL_PASS**: Ein Final exakt einmal nativ; kein F9-Callback, Timeout statt Finish. Finish im Mute-/Reconnect-/Reinsert-Teil separat belegt. |
| followup | **PARTIAL_PASS**: Zwei Segmente derselben Activation, zwei exakte Einfügungen; wirksame Nachsprechfrist5000ms. F9 fehlt, vier Sekunden akustische Pause nicht separat gemessen. |
| cancel | **PASS_SCOPED**: F9/cancel während Aufnahme bestätigt; cancelled/input_closed, kein Paste bis nach10s und anschließendem Stop. |
| refresh | **PARTIAL_PASS**: F8/refresh in followup_wait bestätigt, zweites Segment und zwei Einfügungen. Kein Abschluss vor Stop, keine Verlängerung über die ursprüngliche Deadline bewiesen. |
| none | **PASS_SCOPED**: Nativer F9-Callback in waiting_first_speech; kein mutierender Secondary-Command, natürlicher Timeout, kein Paste. |
| feedback | **NOT_PROVEN**: Übernommener letzter Versuch ohne F8/Activation; ältere Wiederholungen enthalten Aktivierungen, aber keine zugeordnete übernommene Wahrnehmung. |
| mute | **PASS_SCOPED**: Audioverfügbarkeit13s aus; F8 währenddessen ohne Activation; nach Hardwarefreigabe eine Activation, bestätigtes Finish und eine exakte native Einfügung. Kein Beleg für getrennte Run-Pausen. |
| usb | **FAIL**: Physische Trennung: Capture/Senden ab417 stehen geblieben, AudioAvailable bliebtrue; kein Eingabeschluss, auch nach Anstecken. R11 technisch korrigiert, physische Wiederholung am neuen Produkt offen. |
| reconnect | **PASS_SCOPED**: Bewusster Client-Reconnect: Generation1→2/neue Session, Bootstrap vor Audio, danach F8/Sprache/F9finish und eine exakte Einfügung. Kein Netzfehler mit offenem Final. |
| reinsert | **PASS_SCOPED**: Ein Final, genau ein nativer reinsert_last-Hotkey; eine automatic- und eine manual-Injection, zwei erwartete Hashes einschließlich Leerzeichen. |
| settings | **PARTIAL_PASS**: Mensch öffnete Logansicht und beschrieb Serverfilter/Raw;57 echte Client-/LED-Records, Logstreamlive,0Serverrecords/0Raw wie Testkonfiguration. UI-Abnahme laut Auswahl ungewiss. |

Alle vorhandenen ASR-Finals stimmen über Event-ID und Text-Hash mit der privaten
History überein; sämtliche beobachteten Einfügungen stimmen mit dem zugehörigen
Historytext plus Leerzeichen überein. Abbruch/None/USB ohne Paste werden dabei
nicht als fehlgeschlagener Textvergleich gewertet. Native UI-Fortschritte sind in
[operator-events](EVIDENCE/guided-results-20261019/operator-events.jsonl) mit Herkunft
`observed_client_events` belegt; fehlendes F9 bleibt ohne Häkchen. T03 ist damit
funktional nativ belegt; eine ausdrückliche visuelle Gesamtbestätigung fehlt weiter.
Maximal13 Core-Tasks,483323904PrivateBytes, Injectionqueue0 in den1Hz-Samples.
Kein durchgehender30min/100-Activations-Stabilitätsnachweis:15 getrennte Clients,
14Activations, teilweise unterbrochene/fehlgeschlagene Aufgaben.

## Log-Beobachtung

[Store-/Verbindungsbefund](EVIDENCE/guided-results-20261019/log-observation.json):
52Client- und5LED-Records, keine Serverrecords. Logstream tatsächlich
subscribing→replaying→live; damit ist keine defekte Serververbindung nachgewiesen.
Der Server-Facet wird durch `MultiSelectButtons.update_available` ohne passende
Serverrecords deaktiviert. `store_raw_payload=false` im isolierten Testprofil
bewirkt0Rawwerte; die Detailansicht zeigt dann den vorgesehenen Platzhalter.
Das ist kein nachgewiesener Produktfehler. T01 bleibt wegen ungewisser menschlicher
Gesamtbewertung und fehlendem realem Serverpayload-UI-Beleg offen.

## R11: stillstehender Windows-Audiotreiber

[Physischer Screenshot](EVIDENCE/guided-results-20261019/Screenshot_test8.png)
und USB-Versuch605a2e3 belegen Aufnahmezustand ohne Abschluss. USB-Abbruch im
LED-Port18:16:54lokal; Audio-Capture und Sender bleiben ab417 stehen, während
AudioAvailable weitertrue ist. Wiederanschluss18:19:50 ohne Audioerholung;
Ende erst beim bewussten Testclientstop. Das ist **FAIL**, keine Testlücke.
Der dargestellte600s-Segmentwatchdog war noch nicht abgelaufen; der fehlende
15s-Sprachbeginn-Timeout erklärt sich durch bereits laufendes Segment und wird
nicht zusätzlich als falscher Servertimeout behauptet.

Ursache: Die vorhandene Recovery prüfte `is_running` und `stream.active`.
Der Windows-Port blieb scheinbar aktiv, obwohl keine Callbacks mehr ankamen.
Die ausdrückliche Reconnect-/Recovery-Ausnahme umfasst Audio-/Media-/Hardware-
Recovery und die unmittelbare Behebung weiterer bewiesener zusammenhängender
Fehler; daher Korrektur im selben R01 ohne neue Scope-Ausweitung.

Zwei neue Regressionen zunächst rot: echter AudioCapture/Media/Transport, nur
Treibergrenze simuliert. Danach Fortschrittskontrolle des vorhandenen Capture-
Zählers: nach2s Stillstand lokale Barriere, bestätigtesaudioAvailable=false vor
nativem Stop, bestehender serialisierter Neustart. Frist nach Start zurückgesetzt;
Null-PCM ist Fortschritt. Keine synthetischen Audioframes, zusätzlichen Commands
zur Activation oder Änderungen am Serverwatchdog/Protokoll/Benutzerpräferenzen.
Alte Callback-Epochen bleiben gesperrt. Kein Architekturumbau.

Neues Produkt **0f6c85e0ecf971e596aae1b7d265dad7132754e2**.
[Qualifikationsdaten](EVIDENCE/usb-stall-20261019/assessment.json):46Baseline,
2gezielt rote/48grüne Audio-/Recoverytests, vollständige1400Windows-Tests/0Skips,
28Helfertests, Qt-Statuspolling-Selbstcheck, compileall/diffcheck PASS.
Neue EXE/Wheel/sdist mit sauberer Buildidentität; Frozen-GUI-/Ressourcenprobe PASS.
Echter Source-Desktop-/Audio-Vorcheck am ausgewählten Pro-V2 PASS.
Kontrollierter nativer Treiberstillstand mit echtem ReSpeaker und Server bestätigt
false→true ohne neue Activation: Source3,375s, installiertesWheel3,593s.
Diese injizierten Fehler sind **kein physischer USB-PASS**. R11 bleibt
FIXED_TECHNICAL_PASS_PHYSICAL_USB_REPEAT_PENDING. Alte Realnachweise werden nicht
als vollständige Qualifikation des korrigierten Produkts übertragen; reale
Frozen-/Serverpaar- und betroffene Final-/Bediennachweise bleiben offen.

[Servernachprüfung](EVIDENCE/usb-stall-20261019/server-post-human-identity.json)
findet dasselbe Proimage57a7907b und Pinada13b0 wie vor dem Durchlauf; installierte
vier relevanten Runtimequellen passen weiterhin. Wirewertunknown bleibt sichtbar.
Das belegt zeitlich geklammerte Deploymentidentität, keine kontinuierliche
Integritätsattestierung aller Dateien. Kein Serverstart/-stop, keine Promotion.

## Konkrete Restarbeit und Aufräumen

Als nächster menschlicher Block nur **USB und Feedback** am korrigierten Source-
Client, jede Aufgabe mit eigenem Start/Wiederholen/Übernehmen. Vollständiger Ablauf
und Satz bleiben vorher sichtbar. `--tasks usb feedback` vermeidet Wiederholung
der gesamten alten Liste. Danach erneut Auswertung, kein automatischer nächster
Clientstart. Weitere M-Phasen, Run-Pausen, unabhängige Netz-/Logfehler, Settings bei
Aufnahme, Credentials/Admin, Frozen-/erhöhte Zielanwendung/Clipboardfehler sowie
W01-bedingte Wake-/Both-/100Activations-Gates bleiben gemäßBericht19/20 offen.

Alle154Dateien des menschlichen Laufs und die abgeschlossenen autonomen Läufe
liegen privat hashgeprüft unter `build/ap-iv2-020-suite/private-archive/` im Projekt.
Öffentlich nur erlaubte Metadaten, Hashes, der bewusste Screenshot und Testlogs;
keine Transkript-Datenbank, Rohsprache oder Zugangsdaten committed.
[Aufräumprotokoll](EVIDENCE/usb-stall-20261019/cleanup.json): automatische
Freigabeprüfung verweigerte die Entfernung auch des neuen menschlichen Laufordners
und der fünf neuen autonomen Laufordner mit ausschließlich „blocked by policy“.
Zusammen mit dem bereits blockierten früheren Regressionsordner bleiben7gesicherte,
beendete Ordner extern bestehen. Keine Umgehung, keine erneuten Löschversuche für
diese abgewiesenen Ziele und keine Behauptung vollständiger Bereinigung.
