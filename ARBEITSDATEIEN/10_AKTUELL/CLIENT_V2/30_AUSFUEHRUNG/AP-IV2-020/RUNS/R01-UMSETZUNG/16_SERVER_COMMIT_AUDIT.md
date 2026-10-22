# Historischer Servercommit-Audit für AP-IV2-020

18.10.2026, auf ausdrücklichen menschlichen Auftrag nach Entfernung der
zusätzlichen Serverinstanz. **Keine neue Serverausführung.**

## Gültigkeitsregel

Für jeden Test gegen die zusätzliche Instanz muss der verwendete Serverstand
dem vorgeschriebenen Stand entsprechen. **Abweichender Servercommit oder
abweichender Serverproduktinhalt macht den Test als Nachweis für dieses Ziel
ungültig.** Nicht belegbare Einzelzuordnungen werden nicht als erfolgreiche
Serverqualifikation anerkannt. Originalbefunde/Logs bleiben unverändert erhalten.

Der verbindliche Referenzserver in
`PLANUNG/ARBEITSPAKETE/AP-IV2-020.md` ist:

`ada13b011e1d3829f78e7f389e3b927795a2b3be`

Der Name eines Containers, ein Imagename mit `ada13b0` und eine durch
Umgebungsvariable gesetzte Versionsangabe genügen allein nicht als Beweis.

## Unabhängig erneut geprüfter Inhalt

Die erhaltenen Quellbytes wurden erneut rein lesend gegen den echten Gitbaum
dieses Commits im Serverrepository geprüft: pro Datei Git-Blob-SHA1 gegen den
Baumeintrag sowie SHA256 für den Abgleich der historischen Nachweismanifeste.
**555 Gitblobs, keine Abweichung.** Kein Export/Checkout/neuer Server angelegt.

Der historische [lokale Serverbuild](EVIDENCE/local-server-build.json) bindet:

- diese555 geprüften Dateien an Image
  `sha256:5aaa17e9963fea4c3109027a2ce141b2037b5eadfe7cbd91ff39a9f15626ff20`;
- eine zusätzlich damals im laufenden Container vorgenommene Inhaltsprüfung
  mit555 Dateien und leerer Mismatchliste;
- Container `e743d3c6edd64d4b2afbb130765597b6acd0e7fe6b43a4d91d1985f79fdb81f1`,
  Port18020 und das separat gespeicherte Konfigurationsmanifest.

Diese Container-/Imageidentität stimmt mit der zuletzt vor Entfernung
gesicherten [Istaufnahme](EVIDENCE/launcher-context-20261018/assessment.json)
überein. Die [Serverinventare](EVIDENCE/real-server-inventory.json) und
[native Inventarwiederholung](EVIDENCE/recovery-audit/native/real-server-inventory.json)
melden denselben Commit über Schema/Serverdefaults. Die zusätzliche Instanz
war damit historisch **inhaltlich dem vorgeschriebenen Pin zugeordnet**;
ein anderer Serverproduktcommit wurde in dieser Kette nicht gefunden.

Das beweist nicht die Gleichheit aller Modelleinstellungen oder aller
Betriebsbedingungen mit dem vom Menschen normalerweise verwendeten Server.
Gleicher Commit ersetzt keine Konfigurations-/Modell-/Buildqualifikation.

## Vollständiges Akteninventar und Befund

Der Auditor hat sämtliche zum Auditzeitpunkt vorhandenen **363 JSON-Akten**
im R01-Evidenzbereich indexiert, mit Dateihash und allen expliziten
Servercommitfeldern. Darin enthaltene Server-Quellmanifeste wurden gegen den
erneut geprüften Gitinhalt verglichen. Komplette Listen stehen im
[maschinenlesbaren Inventar](EVIDENCE/server-identity-audit-20261018/inventory.json).
Die Zahl bezeichnet Akten, nicht363 unabhängige Testfälle.

| Nachweisart | Anzahl Akten/Manifeste | Commitbewertung |
| --- | ---: | --- |
| Explizite vollständige oder relevante Server-Quellmanifeste | 56 | alle Inhalte stimmen mit dem Pin überein |
| Tatsächlich aufgezeichnete Serverantworten im Inventar bzw. nativen Runtimebericht | 10 | gemeldeter Commit stimmt mit dem Pin überein |
| Commit nur als deklarierter Wert, keine eigene Laufzeit-/Quellattestierung in dieser Akte | 24 | allein nicht ausreichend als Serverqualifikation |
| Kein eigener Serveridentitätsnachweis in dieser Akte | 273 | keine eigenständige Serverqualifikation; nach Testart unterscheiden |
| Festgestellter abweichender Commit oder abweichendes Server-Quellmanifest | 0 | keine inhaltliche Commitabweichung gefunden |

Zusätzlich wurden bei sieben technischen Laufakten die aufgezeichneten
Runnerhashes mit in Git erhaltenem Code verglichen. Für drei davon ist die
Prüfung der echten Admission auf den PIN so zusätzlich belegt: ursprüngliche
Audio-Pipeline, native Audio-Pipeline und der Recovery-Auditlauf. Diese drei
Commitdeklarationen haben damit einen konkret geprüften Begleitbeleg; bei den
übrigen vier ergibt diese zusätzliche Prüfmethode NOT_PROVEN. Die vollständigen
Zuordnungen/Codecommits/Hashes stehen unter `historicalAdmissionGuardChecks` im
Inventar. Nicht auffindbare bzw. nicht passend gebundene historische Runnerbytes
wurden nicht durch heutige Codeannahmen ersetzt.

Die56 Quellprüfungen umfassen den Build, die vier vollständigen Paarläufe,
die50 Prozessfallakten und den gezielten W01-Quellausschnitt. Für Teilmanifeste
gilt die Bestätigung nur für die dort erfassten Dateien, nicht für einen
beliebigen vollständigen Serverdeploy.

## Zuordnung der durchgeführten Testgruppen

| Testgruppe | Konkrete Belegbindung | Gültige Aussage / Grenze |
| --- | --- | --- |
| Windows-Clientregressionen, gezielte Unit-/Qt-/Controltests | kandidatengebundene Clientquellen, vollständige Logs | serverfreie Teile bleiben für ihren tatsächlichen Scope gültig; keine reale Serverqualifikation daraus ableiten |
| Server-Vollsuite, Prozess-/Grenztests und Socketsmokes der vier Paarläufe | `recovery-audit/pair`, `ux01/pair`, `ux02/pair`, `ux03-close-sound/pair`, jeweils `validation.json` mit erneut bestätigten Serverhashes | Pin inhaltlich bestätigt; Ergebnisse gelten für ihren damaligen Client-/Serverstand, keine Übertragung auf anderes Produkt |
| Prozessfallakten, zusätzlich ursprüngliche zehn Akten im Evidenzroot | je `.server.sourceHashes`, insgesamt50 Akten | importierte Serverquelldateien dem Pin zugeordnet; Recorder-/Modellausgaben sind testgesteuert und keine echten Modell-/Hardwarebelege |
| Native EXE-/Wheel- und frühe Frozen-Runtimeberichte | acht `*native-runtime.json`/`frozen-runtime.json` mit `network.serverCommit` bzw. `desktop.serverCommit` | tatsächlicher Admission-/Runtime-Commit aufgezeichnet und passend; mit historischer Buildidentität verknüpft, kein vollständiger M-Fall-PASS |
| Realadmission, Audio-/Golden-ASR-, Wake-/Ressourcen-/Watchdog-/Recoveryläufe | gemeinsamer Build555/Image/Port18020 plus jeweilige JSON-/Docker-Aufrufe, Inventare und Logs | historische gemeinsame Serverbasis dem Pin zugeordnet; eine konstante `serverCommit`-Zeile allein ist keine unabhängige Einzelattestierung |
| Menschliche Sprach-/Nachsprech-/Hotkey-/Feedbackversuche | Session-/Activation-/Konfigurations-/Clientidentitäten und gemeinsame Testinfrastruktur; nicht jede Einzelakte bewahrt eine eigene Serverantwort auf | Beobachtung bleibt erhalten; fehlende Einzelbindung nicht nachträglich erfinden, vollständige Server-/Hardwareabnahme daraus weiterhin NOT_PROVEN |
| Aufnahmen/Fixturemanifest | Audiohash und tatsächliche Herkunft | serverunabhängige Eingabe bleibt wiederverwendbar; Aufnahme allein qualifiziert keinen Server |
| SDK-LED-Frames, Clipboard-/Modifiertastenprobe und Testeditor | jeweiliger tatsächlich isolierter Prüfpfad | serverfreie Anteile nicht durch fehlende Serverangabe entwerten; integrierte Aussagen benötigen dieselbe Bindung wie andere Realtests |
| W01-Rearm-Replay und TV-/Finishbeobachtung | veröffentlichte Befunde, historischer gemeinsamer Build, W01-Quellhashes, Ereignisidentitäten | Befund bleibt dokumentiert; fehlendes historisches Live-PCM und Einzelattestierung bleiben sichtbar, kein Vollqualifikations-PASS |

Die modellfreien Prozessfixtures enthalten teilweise `serverCommit=unknown`
in aufgezeichneten Wireantworten. Diese Werte werden ausdrücklich im Inventar
gezählt und nicht verschwiegen. Die tatsächlich importierten Serverdateien sind
dort separat gehasht und dem Pin zugeordnet. `unknown` ist somit kein Nachweis
eines anderen Quellcommits, aber auch kein erfolgreicher realer
Runtime-Identitätsnachweis. Diese Fälle bleiben Modellfrei-/Protokolltests.

## Früheres Image: fünf Ergebnisse ausdrücklich nicht qualifikationsgültig

Die zeitliche Zuordnung trennt das ältere entfernte Image
`b617cfa7edeff3981c59e52adc36e04289c230561f437ed0a4dd1b76cb509de9`
vom später vollständig quellgeprüften Image5aaa17e. Für das ältere Image liegt
kein gleichwertiger historischer555-Dateien-Laufzeitabgleich vor.

Die erhaltene ältere `source/`-Variante weicht bei459 von555 Dateien auf
Byteebene von `source-exact/` ab. Alle diese Unterschiede verschwinden nach
CRLF/LF-Normalisierung; darüber hinaus wurde in der erhaltenen Variante keine
Quelltextabweichung gefunden. Das ist kein Beweis eines anderen Produktcommits,
ersetzt aber die fehlende genaue historische Runtimezuordnung nicht.

Folgende frühe Docker-Modellläufe vor dem neuen quellgeprüften Build sind
**als erforderliche Serverqualifikation ungültig / Identität NOT_PROVEN**:

| Ursprüngliche Akte | Beginn UTC14.10.2026 | Rohresultat |
| --- | --- | --- |
| `real-wake-artifacts.json` | 22:46:09 | PASS |
| `real-wake-resources.json` | 22:46:10 | PASS |
| `real-golden-asr.json` | 22:46:22 | FAIL |
| `real-wake-negative.json` | 22:46:32 | PASS |
| `real-golden-asr-stable.json` | 22:47:15 | PASS |

[Explizite Ausschlussliste mit Quelldifferenzen](EVIDENCE/server-identity-audit-20261018/early-image-exclusions.json).
Jede dieser fünf Akten hat im Auditindex einen `qualificationUseOverride`.
Original-PASS/FAIL ist ausschließlich historischer Messbefund. Spätere
`*-exact`-Läufe und erneute Qualifikationen werden anhand ihrer eigenen Belege
beurteilt; ein späterer Pinbeleg heilt keinen früher ungebundenen Lauf.

## Konsequenz für Gültigkeit und Abnahme

- **Kein abweichender Serverproduktcommit wurde gefunden.** Die vorhandenen
  Quell- und Laufzeitbelege bestätigenada13b0 für die dokumentierte zusätzliche
  Instanz und die explizit gebundenen technischen Prüfungen.
- Die24 Akten mit bloßer Commitdeklaration sind **als eigenständiger
  Servercommit-Qualifikationsnachweis ungültig**. Sie dürfen nur gemeinsam mit
  einer belastbaren Zuordnung verwendet werden; ohne diese bleibt der konkrete
  serverabhängige Anspruch **NOT_PROVEN**. Ihre tatsächlichen Beobachtungen
  werden nicht gelöscht oder zu bestandenen Pflichtfällen umgedeutet.
- Für die273 Akten ohne eigenen Servernachweis gilt ebenfalls: soweit eine
  serverabhängige Qualifikationsbehauptung betroffen ist und keine geprüfte
  Bindung vorliegt, ist sie **nicht abnahmewirksam**. Darunter befinden sich
  jedoch auch reine Client-/Build-/Hilfsmittel-/Rohaufnahme-/Administrationsakten,
  die gar keinen eigenen Serverclaim erheben. Fehlendes Feld macht diese nicht
  zu fehlgeschlagenen Clienttests.
- Die vollständigen M-01..M-12 und30min/100Activations waren ohnehin offen und
  bleiben NOT_RUN/NOT_PROVEN; kein REVIEW_READY oder neues Produkt-PASS.
- Die Entfernung der Instanz macht bestehende Hashbelege nicht nachträglich
  falsch. Eine erneute Laufzeitprüfung dieser entfernten Instanz wurde jedoch
  nicht durchgeführt und ist nicht ohne neuen Auftrag zulässig.
- Vor Fortsetzung: tatsächliches menschlich gewünschtes Serverziel, dessen
  verbindlicher Commit und Konfiguration feststellen. Ein abweichender Zielstand
  benötigt neue gültige Nachweise; alte Prüfungen werden nicht übertragen.

[Wiederverwendbarer Auditor](EVIDENCE/human/audit_server_commit_evidence.py).
Er startet oder verändert keinen Server und schreibt ausschließlich den
angegebenen Bericht im Repository. Diese zusätzliche Sicht ersetzt nicht die
historischen Originalberichte; sie begrenzt deren Qualifikationsverwendung.
