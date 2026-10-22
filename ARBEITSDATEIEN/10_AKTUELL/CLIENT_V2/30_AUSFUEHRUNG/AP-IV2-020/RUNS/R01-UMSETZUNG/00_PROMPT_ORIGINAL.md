Herkunft: tatsächlicher menschlicher Auftrag im Codex-Chat, 2026-10-15.
Rolle: Umsetzer. Folgender Auftrag im Originalwortlaut (nur Markdown-Hardbreak-Leerzeichen am Zeilenende normalisiert):

# Umsetzungsauftrag – AP-IV2-020

Repository: `https://github.com/marcosudau-vps/voice-stt-client`
Ausgangsbranch: `feat/client-v2`
Arbeitspaket: `AP-IV2-020`

## 1. Verbindlicher Einstieg

Bitte übernimm die vollständige Umsetzung des Arbeitspakets **AP-IV2-020** ausgehend vom tatsächlich aktuellen Stand von `feat/client-v2`.

Lies zuerst:

`ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md`

Folge anschließend den dort verlinkten Vorgaben für Zustandserkennung, Rollenwahl, Umsetzung, Tests, Dokumentation, Evidenzführung und PR-Abgabe.

Insbesondere sind der Umsetzungsskill, die zugehörige Paketdefinition, die Hardware-Nachweisregeln, der Test- und Abnahmeplan sowie die gültigen AGENTS-Anweisungen maßgeblich.

Ermittle selbstständig die tatsächliche Git-Baseline, den abgeschlossenen Vorgänger AP-IV2-010, die zugehörige Übernahmeprovenienz und alle notwendigen Kandidatenidentitäten.

Nutze die bestehenden workflowweiten Git-Arbeitsfreigaben. Dieser Auftrag ermächtigt zur vollständigen Bearbeitung von AP-IV2-020 einschließlich Paketbranch, Kandidatencommits, Push und PR gegen `feat/client-v2` im dokumentierten Scope. Er erteilt ausdrücklich keine Freigabe zur kanonischen Übernahme, zu Releases, Tags oder zur Serverpromotion.

## 2. Besondere Ausgangslage

Der Auftraggeber arbeitet auf einem Windows-PC, an dem ein ReSpeaker angeschlossen und grundsätzlich funktionsfähig ist.

Die bisherige Client-Version V1 wird regelmäßig mit diesem Gerät verwendet. Die grundsätzliche Funktion von Mikrofon und ReSpeaker ist damit praktisch bekannt, ersetzt aber keine V2-Qualifikation.

Reale Hardwaretests und menschliche Bedienhandlungen sind bei Bedarf möglich. Der Auftraggeber soll dafür jedoch **erst eingebunden werden, nachdem der Agent alle ohne menschliche Mitwirkung möglichen Vorbereitungen und Prüfungen abgeschlossen hat**.

Die bestehende funktionsfähige V1-Installation, deren Einstellungen und produktiv verwendete Serverzustände sind vor unbeabsichtigten Änderungen zu schützen. Verwende soweit erforderlich isolierte Testprofile und Testinstanzen.

## 3. Phase A – Testfähigkeit feststellen

Prüfe zu Beginn systematisch, welche Voraussetzungen für die vollständige Durchführung von AP-IV2-020 bereits vorliegen.

Dazu gehören insbesondere:

- Verfügbarkeit der erforderlichen Windows-Ausführungsumgebung und Berechtigungen.
- Tatsächlicher Zugriff auf Mikrofon, ReSpeaker, USB- und LED-Funktionen.
- Verfügbarkeit des qualifizierten Clientbuilds und des kompatiblen Serverstands.
- Verfügbarkeit der echten ASR- und Wake-Word-Modelle.
- Ausführbarkeit der automatisierten Tests, Mess- und Diagnoseschnittstellen.
- Möglichkeiten für reale Windows-Hotkey-, Clipboard-, Credential-, Tray-, Sound- und Overlayprüfungen.
- Möglichkeiten für kontrollierte Netzwerk-, Geräte- und Prozessfehlertests.
- Möglichkeiten zur nachvollziehbaren Aufzeichnung von Timing-, Latenz-, Zustands- und Ressourcenmessungen.

Unterscheide ausdrücklich zwischen:

1. Vollständig selbstständig ausführbaren Tests.
2. Tests, die durch eigene Automatisierung ausführbar gemacht werden können.
3. Tests, die reale Hardware erfordern, aber ohne menschlichen Eingriff durchgeführt werden können.
4. Tests, die tatsächlich menschliche Bedienung oder Wahrnehmung benötigen.
5. Tests, deren Voraussetzungen momentan fehlen.

Entwickle für automatisierbare Prüfungen geeignete Hilfsmittel, soweit dies innerhalb des Paketauftrags zulässig und sinnvoll ist.

**Wichtig:** Das Fehlen eines direkten Hardwarezugriffs ist nicht automatisch ein Grund, das gesamte Arbeitspaket abzubrechen. Bereite die betreffenden Prüfungen für eine dokumentierte Durchführung durch den Auftraggeber vor.

## 4. Phase B – Maximale autonome Vorbereitung und Durchführung

Bearbeite anschließend eigenständig alle Aufgaben, für die keine menschliche Mitwirkung notwendig ist.

Dazu gehören insbesondere:

- Automatisierte Regressionen und Integrationstests.
- Prüfung des qualifizierten Client-/Serverbuilds.
- Vorbereitung und Durchführung zugänglicher Windows- und Modelltests.
- Aufbau erforderlicher Mess-, Diagnose- und Testhilfen.
- Automatisierbare Last-, Recovery-, Queue-, Timeout- und Stabilitätsprüfungen.
- Ermittlung der tatsächlich vorhandenen Konfigurationsparameter und ihrer effektiven Werte.
- Erstellung reproduzierbarer Abläufe für die realen Pflichtfälle M-01 bis M-12.
- Vorbereitung der erforderlichen Evidenz und Abnahmeprotokolle.

Nutze geeignete Automatisierung, um den später notwendigen menschlichen Aufwand möglichst gering zu halten.

Fasse insbesondere Testfälle zusammen, die dieselbe Hardwarekonfiguration oder dieselben manuellen Aktionen benötigen.

Unterbrich den Auftraggeber während dieser Phase nicht für einzeln durchführbare Kleinigkeiten, sofern du sie selbstständig vorbereiten oder bearbeiten kannst.

Echte Modell-/Hardwaretests dürfen nicht durch synthetische Tests ersetzt und anschließend als real bestanden bewertet werden.

## 5. Phase C – Gebündelte Zusammenarbeit mit dem Auftraggeber

Erst nach Abschluss der autonom möglichen Vorbereitung beginnt die gemeinsame Test- und Kalibrierungsphase.

Stelle dafür einen übersichtlichen, sinnvoll geordneten Ablauf bereit, der die verbleibenden menschlichen Aktionen bündelt.

Bevorzuge eine interaktive Durchführung, bei der du jeweils die nächste konkrete Aktion vorgibst, der Auftraggeber sie ausführt und du das Ergebnis unmittelbar prüfst und protokollierst.

Beispiele:

- Bestimmte Wake-Word-Phrasen sprechen.
- ReSpeaker oder Mikrofon kontrolliert trennen und wieder verbinden.
- Hardware-Mute betätigen.
- LED-Reaktionen beobachten.
- Soundfeedback beurteilen.
- Verhalten von Tray und Overlay prüfen.
- Textinjektionen in verschiedenen Windows-Anwendungen beobachten.
- Natürlichkeit und Verständlichkeit des gesamten Bedienablaufs bewerten.

Vermeide dabei unnötig viele einzelne Rückfragen. Bündele zusammengehörige Tests zu sinnvollen Testblöcken.

Verwende möglichst vorbereitete Diagnosen, sodass der Auftraggeber nicht selbst Logs suchen, Messwerte ermitteln oder Testberichte schreiben muss.

Bei fehlgeschlagenen Tests untersuche zunächst selbstständig die Ursache, bevor du weitere menschliche Maßnahmen anforderst.

## 6. Zusätzlicher Schwerpunkt – Gemeinsame Timing- und Default-Kalibrierung

Während der gemeinsamen Testphase soll ausdrücklich auch eine **systematische Feinabstimmung der tatsächlichen Bedienparameter und Default-Werte** erfolgen.

Das Ziel ist nicht nur eine formal funktionierende Anwendung, sondern ein zuverlässiges, flüssiges und angenehm bedienbares Gesamtsystem.

Untersuche zunächst eigenständig alle relevanten vorhandenen Timing- und Konfigurationsparameter, ihre Abhängigkeiten, Gültigkeitsbereiche, tatsächlichen Default-Werte sowie die Zuständigkeit von Client oder Server.

Berücksichtige dabei insbesondere, soweit im tatsächlichen System vorhanden und konfigurierbar:

- Wake-Word-Erkennung, Empfindlichkeit, Schwellenwerte und Cooldown.
- Zeitliche Grenzen zwischen Wakephrase und anschließender Nutzsprache.
- Pre-Roll, VAD, Sprachbeginn und Spracherkennungsende.
- Nachsprechzeit, Follow-up-Fenster und Wartezeiten zwischen Sprachsegmenten.
- Refresh-Verhalten, Timerverlängerung und Timeout-Grenzen.
- Daueraufnahme-Watchdog und Vorwarnzeiten.
- Reaktionszeiten von Hotkeys und manuellen Triggern.
- LED-Zustände, Animationen, Übergänge, Blinkfrequenzen und Anzeigedauern.
- Soundfeedback, dessen zeitliche Auslösung und Zusammenspiel mit LED- und UI-Feedback.
- Overlay-Anzeigezeiten, Zustandswechsel und visuelle Rückmeldungen.
- Relevante Queue-, Ack-, Retry-, Reconnect- und Recovery-Timeouts.

Diese Aufzählung beschreibt Prüfbereiche, nicht die Behauptung, dass jeder Parameter bereits als frei konfigurierbare Einstellung existiert.

### Vorgehensweise bei der Kalibrierung

1. Inventarisiere zunächst die tatsächlich vorhandenen Parameter einschließlich aktuellem Default, zulässigem Bereich, Client-/Serverautorität und technischer Wirkung.
2. Unterscheide technische Sicherheits-/Protokollgrenzen von Parametern, die hinsichtlich der Bedienqualität angepasst werden dürfen.
3. Ermittle anhand der bisherigen Implementierung und messbarer Ergebnisse sinnvolle Ausgangswerte.
4. Stelle bei den gemeinsam wahrnehmbaren Parametern gezielte Varianten zum Vergleich bereit.
5. Lass den Auftraggeber die Wirkung beurteilen, beispielsweise „zu kurz“, „zu lang“, „zu früh“, „zu spät“, „zu empfindlich“ oder „passt“.
6. Passe die relevanten Parameter an und überprüfe die Wirkung erneut.
7. Wiederhole dies, bis ein technisch zulässiger und vom Auftraggeber bestätigter Wert gefunden ist.
8. Dokumentiere Ausgangswert, getestete Varianten, Messwerte, gewählten Wert und Begründung.
9. Überprüfe nach jeder relevanten Änderung die betroffenen Integrations- und Regressionstests.

**Die menschliche Bewertung ist hier ausdrücklich erwünscht.** Beispielsweise kann ein LED-Feedback technisch korrekt ausgelöst werden, sich zeitlich aber trotzdem unpassend anfühlen. Solche Wahrnehmungen sollen unmittelbar in die Feinabstimmung einfließen.

Die endgültig gewählten Werte sollen nach Möglichkeit als sinnvolle, reproduzierbare Defaults oder im vorhandenen Konfigurationssystem übernommen werden, damit das kalibrierte Verhalten nicht nur während der Tests existiert.

### Grenzen der Anpassungen

Verändere keine festgeschriebenen Serverprotokolle, Sicherheitsgrenzen oder technischen Invarianten, nur um ein gewünschtes Timing zu erreichen.

AP-IV2-020 ist grundsätzlich als Qualifikationspaket ohne Produktcodeänderungen vorgesehen.

Reine Testkonfiguration und zulässige Einstellung vorhandener Parameter gehören zur Kalibrierung. Sollte die dauerhafte Übernahme abgestimmter Defaults eine Produktcodeänderung erfordern, dokumentiere die konkreten betroffenen Stellen und prüfe den zulässigen Änderungsweg.

Lege solche erforderlichen Änderungen dem Auftraggeber gebündelt zur Freigabe vor. Nimm sie nicht stillschweigend außerhalb des Paket-Scopes vor. Gegebenenfalls ist eine ausdrücklich freizugebende eng begrenzte Korrektur oder eine separate FIX-Instanz erforderlich.

Der Sinn dieser Regel ist, die Feinabstimmung möglichst vollständig im aktuellen Arbeitsablauf abzuschließen, ohne die bestehende Paket- und Abnahmestruktur unkontrolliert aufzuweichen.

## 7. Phase D – Finale Qualifikation und Dokumentation

Nach Abschluss der gemeinsamen Tests und Kalibrierung führst du wieder selbstständig alle verbleibenden Arbeiten durch.

Insbesondere:

- Abschließende Prüfung der gewählten Konfiguration und Default-Werte.
- Wiederholung aller von Änderungen betroffenen Tests.
- Vollständige vorgeschriebene Windows-Regression.
- Qualifikation des endgültigen Client-/Server-/Build-/Konfigurationsstandes.
- Prüfung aller realen Pflichtfälle und der 30-Minuten-/100-Activations-Anforderung.
- Auswertung der Wake-Word-, ASR-, Stabilitäts-, Ressourcen- und Recoverymessungen.
- Dokumentation der finalen Kalibrierungswerte mit deren Begründung.
- Vollständige Aktualisierung von Traceability, Testmatrix, Paketakte und Evidenzindex.
- Dokumentation verbleibender Einschränkungen und möglicher notwendiger Korrekturpakete.

Falls die Kalibrierung produkt- oder testrelevante Änderungen erzeugt hat, müssen die entsprechenden Nachweise zum tatsächlich endgültigen Stand passen. Eine Qualifikation des vorherigen Builds darf nicht ungeprüft übertragen werden.

Fehlende Pflichtbelege bleiben `NOT_RUN` beziehungsweise `NOT_PROVEN`; fehlerhafte Prüfungen werden als `FAIL` ausgewiesen. Behaupte keinen vollständigen PASS, solange Pflichtkriterien offen sind.

## 8. Abgabe und Arbeitsorganisation

Behalte grundsätzlich den vorgesehenen Workflow bei:

**Ein Umsetzungsagent, ein kumulativer Paket-PR und anschließend ein unabhängiger Abnahmelauf.**

Die Phasen A bis D sind interne Schritte desselben Umsetzungsauftrags und keine zusätzlichen Pflichtsessions.

Arbeite möglichst selbstständig und frage nur bei tatsächlich notwendigen menschlichen Handlungen, Entscheidungen, Zugriffsfreigaben oder technischen Blockern nach.

Die gemeinsame Hardware- und Kalibrierungsphase darf den laufenden Umsetzungsauftrag unterbrechen und anschließend in derselben noch offenen Agentensession fortgesetzt werden.

Der Agent bleibt für die Planung, technische Steuerung, Auswertung, vollständige Dokumentation und PR-Abgabe verantwortlich. Menschlich durchgeführte Prüfungen sind mit ihrer tatsächlichen Herkunft auszuweisen.

Erstelle bei erfüllten Abgabekriterien den vorgesehenen Paket-PR gegen `feat/client-v2` und melde `REVIEW_READY` mit allen erforderlichen Identitäten, Testnachweisen, Messwerten und Belegverweisen.

Falls unverzichtbare Pflichtfälle offenbleiben, melde stattdessen den zutreffenden blockierten Zustand mit konkreten Restaufgaben. Eine unvollständige Realqualifikation darf nicht als abgeschlossen dargestellt werden.

Kein Eigenreview, kein automatischer Merge und kein Start weiterer Arbeitspakete.

## 9. Erste Rückmeldung

Beginne mit der regulären Zustandserkennung und der Testfähigkeitsanalyse.

Melde danach kompakt:

- Festgestellte Baseline und Voraussetzungen.
- Welche realen Testmöglichkeiten dem Agenten zur Verfügung stehen.
- Welche Prüfungen autonom ausgeführt werden können.
- Welche menschlichen Handlungen voraussichtlich erforderlich sein werden.
- Welche Kalibrierparameter festgestellt wurden und wie ihre Abstimmung geplant ist.
- Konkrete technische Blocker, falls vorhanden.

**Beginne danach ohne erneute allgemeine Freigabe mit allen autonom möglichen Arbeiten.**

Fordere die Beteiligung des Auftraggebers erst dann an, wenn die dafür notwendige Vorbereitung abgeschlossen ist und ein sinnvoll gebündelter interaktiver Test- und Kalibrierungsablauf bereitsteht.

Ziel ist ein vollständig qualifizierter, gemeinsam feinabgestimmter V2-Client bei möglichst geringer manueller Belastung des Auftraggebers.
