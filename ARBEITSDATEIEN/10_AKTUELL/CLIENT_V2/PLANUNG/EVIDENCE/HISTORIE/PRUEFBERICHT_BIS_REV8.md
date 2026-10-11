# Historischer Prüfbericht bis Revision 8

Diese unveränderten fachlichen Ergebnisse und damaligen Abläufe sind Provenienz. Ihre damaligen Branch-/Bereitstellungsanweisungen gelten nicht für neue Läufe. Aktueller Prüfstand: [Revision 9](../PRUEFBERICHT.md). Relative Links wurden an die Archivposition angepasst.

# Prüfbericht der eigenständigen Client-V2-Planung



Aktuelle Dokumentprüfung: **2026-10-05, Revision 5**. Quellen-/Produkttestprüfung: 2026-10-04. Ergebnis: **Planungsgrundlage erstellt und geprüft; V2-Clientumsetzung und Produktabnahme offen.**



## 1. Baselines und Untersuchungsumfang



| Produkt | Unveränderlicher Untersuchungsstand | Verfahren |

| --- | --- | --- |

| Server | `ada13b011e1d3829f78e7f389e3b927795a2b3be` auf `feat/einheitliche-triggerarchitektur-distributed` | Remote abgeglichen, Commit per Gitarchive exportiert, Quellen gegen Gitblobs geprüft |

| Client-Release-/Migrationsreferenz | `f625904795880ce71acec216e43678f9ec1656d0` / `origin/main` am Prüftag | Releasequellen per Gitarchive exportiert; vollständige V1-Testsuite auf diesem Export |

| Fortgesetzte Client-Featurelinie | `a80a6b17b40751740f9c9d2aef9cad32b0470c0c` Distributed und `8bab1b3f4aa070d0756c305908def4d9ebc52582` kanonisch | gleicher vollständiger Baum, konkreter Triggercode-/Testvergleich und vollständige Featuretestsuite |



Die [Baselineanalyse](../../REFERENZ/PLANUNG/ANALYSEN/BASELINE_UND_MIGRATION.md) benennt außerdem den abweichenden lokalen Checkout. Die frühere Startannahme auf dem Clientrelease wurde nach erneuter Prüfung korrigiert: Featurelinie fortsetzen, notwendige Releaseverbesserungen vor neuen Wiremodulen integrieren. AP-CV2-000 stellt den tatsächlich geprüften integrierten Start her; dafür existiert heute noch kein Commit. Bestehende Produktworkingtrees wurden nicht zurückgesetzt oder umgeschrieben. Kein Produktcode, Commit, Push oder Merge entstand in dieser Planungsaufgabe.



Die [202 Quell-/Testdateien](../source-manifest.json) sind mit Repository, vollem Commit, Pfad, SHA256 und gepintem GitHub-Link erfasst. Für die lokalen Exporte wurde zusätzlich der Gitblobhash mit dem jeweiligen Commit verglichen. Gitarchive hatte bei 72 Textdateien Windows-Zeilenenden angewendet; ausschließlich diese Zeilenenden wurden nach Inhaltsvergleich auf die originalen Gitblobbytes zurückgeführt. Anschließend wurden die Belege neu exportiert und die Fixtureprüfung erneut ausgeführt. Das Manifest ist eine Liste der relevanten Belege, keine Behauptung einer vollständigen formalen Analyse jeder Repositorydatei.



## 2. Erzeugte Planungsgrundlage



- 12 Clientpakete, zwei Integrations-/Abnahmepakete und eine bedingte Serverkorrekturvorlage; jede Paketdatei enthält Scope, Ownership, Abhängigkeiten, konkrete Spezifikation, Liefergegenstände, Akzeptanzkriterien, Tests und Definition of Done.

- 216 Requirements mit eindeutigem Paketowner, eigenständigem Kontrakt und geplantem Nachweis; 612 direkte Quellenbindungen. Die Runtimeintegration hat eigene Anforderungen und bleibt kein unzugeordneter Sammelschritt.

- Vier vollständige Schnittstellenreferenzen für Wire/Audio/Commands, Domainereignisse/Snapshot/Ergebnisse, Settings/Wake sowie Logs/Auth/Recovery.

- Direkt exportiertes Settingsschema, Serverdefaults und Protokollvokabular; bytegleiche Server-Vertragsvektoren und 30 zusätzliche, ausdrücklich noch nicht ausgeführte Abnahmeszenarien.

- Eigenständiges Zielbild, Migrationskarte, Ablauf-/Gateplanung, Teststrategie und Entscheidungs-/Risikoregister.



Alle lokalen Dokumentlinks bleiben innerhalb dieser Planungsgrundlage. Quellcode-/GitHub-Verweise dienen dem Nachweis; Ziele, Verhalten, Grenzen und Umsetzungskriterien sind in den Dokumenten selbst beschrieben. Die 17 vorhandenen Planungsdateien wurden vor und nach Erstellung per SHA256 und Dateiinventar verglichen und sind unverändert.



## 3. Tatsächlich ausgeführte Tests



| Prüfung | Ergebnis | Geltung |

| --- | --- | --- |

| Gesamte Client-Releasebaseline: `unittest discover -s tests -p test_*.py` | **1.147 Tests OK**, 84,729 s | vollständige vorhandene V1-Suite am Clientbaselinecommit |

| Gezielte Server-Vertrags-/Race-/Settings-/Boundary-/Recovery-Suite mit pytest | **307 bestanden, 299 Subtests bestanden**, 244,90 s; ein optionaler Bytevergleich zunächst übersprungen | konkrete unten genannte Servermodule am festgelegten SHA |

| Separater Bytevergleich mit gesetztem `VOICESTT_PROTOCOL_V2_VECTORS` | **1 bestanden** | exportierte Planungskopie entspricht der Serverfixture |

| Erneuter vollständiger Contractdateilauf nach Byteabgleich, einschließlich aktiviertem Fixturevergleich | **69 bestanden, 39 Subtests bestanden**, 13,25 s | `test_protocol_v2_contract.py` an den Gitblobbytes; Wiederholung, keine addierte Gesamtzahl |

| Dokument-/JSON-/Quellen-/Abhängigkeitsprüfung | **PASS**, maschinenlesbares [Prüfergebnis](../validation-results.json) | Integrität und Konsistenz dieser Planung |

| Gesamte Client-Featurebaseline: `unittest discover -s tests -p test_*.py` | **1.192 Tests OK**, 84,649 s | a80a6b1, noch nicht finaler V2-Wireclient |

| Direkte Parserbeobachtung | **PASS**: Commandversion `2.0` toleriert, Bool abgelehnt | dokumentierte Server-Ist-Präzisierung L-07 |



Die Serverprüfung führte genau diese Dateien aus:



```text

tests/unit/test_protocol_v2_contract.py

tests/unit/test_protocol_v2_e2e.py

tests/unit/test_protocol_v2_races.py

tests/unit/test_protocol_v2_state_version.py

tests/unit/test_protocol_v2_settings.py

tests/unit/test_protocol_v2_terminal_recovery.py

tests/unit/test_protocol_v1_v2_boundary.py

tests/unit/test_settings_control_plane.py

```



Der separate Bytevergleich verwendet `test_protocol_v2_contract.py::ContractVectorFileTests::test_the_vendored_copy_matches_the_planning_original`. Der [Server-Testkatalog](../server-test-catalog.json) enthält darüber hinaus existierende relevante Testmethoden; ein Katalogeintrag behauptet keine Ausführung.



Runtime: Python 3.12.10, Windows; Clienttests mit `QT_QPA_PLATFORM=offscreen`. Für den Server wurde eine isolierte temporäre Testvenv mit vorhandenen Systempaketen und ergänztem `halo`/`httpx` eingesetzt. Ein erster Versuch mit der Clientvenv scheiterte an fehlendem `halo`; nach Behebung der Testumgebung bestand der oben ausgewiesene Lauf. Produktvenvs und Produktdependencydateien wurden dafür nicht verändert.



Die Integritätsprüfung umfasst JSONsyntax einschließlich dokumentierter JSONbeispiele, lokale Links, eindeutige IDs, Owner-/Testzuordnung, Szenarioreferenzen, zyklusfreie Paketabhängigkeiten, Übereinstimmung von Matrix und Requirements-JSON, tatsächliche Server-Testnamen, Quellhashes/Gitblobs, Registry-/Vokabularexporte, vollständige Dokumentation der Event-/Command-/Result-/Settingsnamen sowie Erhalt der vorhandenen Dateien. Die Prüfschritte sind im maschinenlesbaren Ergebnis gezählt.



## 4. Inhaltliche Abgleichsergebnisse



Die [Server-Ist-Analyse](../../REFERENZ/PLANUNG/ANALYSEN/SERVER_IST_UND_GRENZEN.md) beschreibt alle Befunde einschließlich ihrer Clientkonsequenz. Die wichtigsten sind:



1. Server-V2 ist ein separater Endpoint; die V1-Kompatibilität des Servers bleibt bestehen. Realtimeinterims und Logbootstrap sind bereits implementiert.

2. Serverautorität ersetzt lokale Diktierfenstersteuerung. Event-vor-Ack, Terminal-vor-Close und neue Activation vor altem Close erfordern ID- und Versionsguards.

3. Snapshotresync liefert keine verlorenen Texte und ersetzt kein Domainreplay. Gepufferte Finals bleiben erhalten; tatsächliche Verluste werden sichtbar.

4. Settingsschema, Serverread, Patch und Snapshot besitzen unterschiedliche Formen und Revisionsscopes. Next-Activation-/Next-Session-Wirkung wird explizit behandelt.

5. Individuelle NS-Startoptionen für Wake-Noise/VAD fehlen im Hello. Der Plan verspricht dafür keine funktionslose per-Client-Speicherung.

6. Logzugriff und Adminauth haben getrennte Vertrauensbereiche. Öffentliches GET beweist keinen gültigen Adminkey.

7. Wakekalibrierung und reale Nutzsprachgrenze bleiben nachweispflichtig. Die Planung unterscheidet implementierten Audiomechanismus von real belegter Qualität.



## 5. Noch nicht ausgeführte Abnahmen



**NOT_RUN:** neue V2-Clienttests, vollständige schnelle Serversuite, Cross-Repository-Prozessintegration, Releasebuilds, echte Modelle/Goldenfälle, Win32-/Clipboard-/Credential-Manager-Abnahme sowie Mikrofon-/ReSpeaker-/Wakekalibrierung. Diese Aufgaben sind als Pflichtnachweise in CV2-100/110 und IV2-010/020 eingeplant.



Die bestandene V1-Suite beweist die Ausgangsbasis; sie beweist keine V2-Umsetzung. Die gezielte Serversuite beweist die getesteten Kontrakte, keine vollständige Produktionsqualifikation. Sämtliche 216 Clientrequirements bleiben daher `CLIENT OPEN`; das bedingte Serverfixpaket erzeugt erst bei einem reproduzierten Befund eine konkrete Instanz.



Startpunkt der Umsetzung ist [AP-CV2-000](../../ARBEITSPAKETE/AP-CV2-000.md). Ein anderes Startrepo oder eine neue Serverbaseline verlangt den dort beschriebenen erneuten Abgleich.



## 6. Revision 2: Branchstrategie, Aufwand und Agentenregeln



Die [Branchbewertung](../../REFERENZ/PLANUNG/ANALYSEN/CLIENT_BRANCH_BEWERTUNG.md) ersetzt die frühere main-Startannahme anhand des tatsächlichen Release-Strategiebelegs, 17 geänderter Feature-Produkt-/Testdateien und beider vollständig geprüften Baselines. Der gleiche Gitbaum von Distributed/kanonisch ist geprüft; keine historische Branch wurde umgeschrieben. Der integrierte Start-SHA ist ausdrücklich offen.



Die Paketübersicht verwendet Fachlauf-Richtwerte statt einer Abhängigkeitsspalte: **14 vollständige Umsetzungsläufe plus 14 unabhängige Abnahme-/Abschlussläufe; regulär 28, bei konkretem Zusatzbedarf höchstens 30 Sessions ohne Korrekturen**. Jedes AP enthält die sinnvolle Teilung.



Die vom Auftraggeber bestätigten Regeln stehen im [Agentenregelwerk](../../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md): seriell, unabhängiger Paketreview, kumulative Distributed-Kandidaten, kanonisch erst nach ROOT PASS genau ein Aggregatecommit/Push. Die operative Ausgestaltung ist als Arbeitsfassung gekennzeichnet. Kandidaten, Paket-PASS, Promotion und Main-/Releasefreigabe werden getrennt behandelt.



README, Gesamtplan, Baseline-/Migrationskarte, alle Paketdateien, Traceability/Requirements, Szenariobaselines, Ausführungsworkflow, Testplan, Entscheidungen/Risiken und Evidence wurden konsistent fortgeschrieben. Serverkontrakte und bestehende Planungsunterlagen bleiben unverändert. Es erfolgte keine Produktimplementierung oder Gitpromotion.



## 7. Umfangskorrektur und endgültige Freigabeinstanz



Die zu vorsichtige Vorabteilung in mehrere Fachsessions je Paket wurde korrigiert. Technische Unteraufgaben gehören regulär in den einen vollständigen Paketlauf; bestehende Logging-/Feedbacksysteme werden an V2 angeschlossen und nicht neu implementiert. Zusatzläufe entstehen nur bei tatsächlichem Bedarf.



Bestätigt ist außerdem: unabhängiger Reviewer meldet den technischen PASS; ausschließlich ein anschließender ausdrücklicher Prompt des Auftraggebers autorisiert den einen kanonischen Aggregatecommit/Push. Die kurze freigegebene Übernahme kann die noch offene Abnahme-/Abschlusssession beenden und ist kein vorab eingeplanter dritter Fachlauf. Main-Merge/Release bleiben separat.





## 8. Revision 4: Umsetzungsspielraum, Paketakten und Promptvorlagen



Stand 2026-10-05. Die Planung wurde vollständig auf unnötig starre interne Vorgaben geprüft. [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md) dokumentiert die konkreten Befunde und unterscheidet unveränderlichen Serververtrag, verbindliches Produktergebnis, interne Umsetzungsvorschläge und begründbar anpassbare technische Startwerte.



Alle 15 Paketdateien, Gesamtplan, Zielbild, Kontrakttexte, Testplan, Matrix/Requirements, Workflow und Regelwerk wurden konsistent angepasst. Keine vorgeschriebene Neuanlage wegen Dateinamen; keine FAIL-Bewertung allein wegen vorgeschlagener Testmodule; interne Maps/Klassen/SQLite-Namen und UI-Anordnung sind frei. Fachliche Testabdeckung, Daten-/Credentialschutz, begrenztes Runtimeverhalten und vollständige Regression bleiben Pflicht. Server-Ist-Werte, SHAs und Vertragsvektoren wurden nicht geändert.



Die [Paketablage](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) definiert eine einheitliche kleine Runstruktur mit Original-Prompt, einem Report und Evidenzindex, einem Paketindex sowie optionalen Entscheidungen/Zusatzprompts. Vier vollständige Rollenpromptvorlagen und passende Strukturvorlagen sind vorhanden. Keine leeren Implementierungsakten und keine neuen Pflichtsessions wurden erzeugt; Aufwand und ausdrückliche menschliche Übernahmefreigabe bleiben wie bestätigt.



Validierung: Dokument-/Link-/JSON-/Matrix-/Owner-/Quellen-/Exportkonsistenz und spezifische Konsistenzprüfungen für Spielraum, Vorlagen und Aktenstruktur. Aktueller Status und Prüfumfang stehen im [Prüfergebnis](../validation-results.json). Bereits ausgewiesene Produkttestresultate stammen von der vorherigen Baselineprüfung; diese reine Dokumentrevision führte keine neuen Produkttests oder V2-Abnahmen aus. Alte Planungsdateien bleiben erhalten. Kein Produktcode, Commit, Push oder Merge.


## 9. Revision 5: Rollen-Skills und praktische Dokumentstruktur

Die aktive Planung ist physisch in Rollenabläufe, Paketdateien und fachliche Hintergrundreferenzen gegliedert. Zwei Projekt-Skills sind die Einstiege für Umsetzung/Korrektur und unabhängige Abnahme/menschlich autorisierte Übernahme. Die große Planung, vollständige Regelwerksdetails und Untersuchungsanalysen werden bei Bedarf geladen; Anforderungen/DoD und passende Kontrakte bleiben paketbezogene Pflichtreferenzen.

Getrennte Abgabe-/Abnahmechecklisten enthalten Pflichtumfang zu Tests, Traceability, Produktdokumentation, Übergaben, Original-Prompts, Evidenz, Kandidatenidentität und Gitgrenzen. Auftragsvorlagen verweisen auf die Rollen-Skills und wiederholen nicht alle Arbeitsregeln. Aktenvorlagen liegen zentral, alle Quellen/Vertragsbelege und ursprünglichen Planungsdateien bleiben erhalten.

Dokumentation der Pfadmigration und Inhaltsintegrität: [Reorganisationsmanifest](../reorganisation.json). Die Prüfung umfasst interne Links, Erreichbarkeit über Einstiege, Paket-/Requirementzuordnung, Skillfrontmatter, konkrete Rollenlesepfade und unveränderte gepinnte Quellen/Vektoren. Neue Produktabnahmen wurden durch diese Dokumentorganisation nicht durchgeführt.

## 10. Revision 6: gemeinsame Client-Abschlusslinie

Planung vollständig ins Clientrepository übernommen, eigenständige Einstiege/Skills erhalten. `feat/client-v2` beginnt am kanonischen Featurestand 8bab1b3; Treegleichheit mit a80a6b1 erneut gegen Git geprüft. Erste Revision ausschließlich Unterlagen, keine V1-Portierung und kein CV2-000-PASS. Neue Branchreferenz regelt Paketisolation, Code-/Planaggregation, exakten Parent, einen Single-Parent-Commit und Fast-forward-Übernahme. Server-Distributed bleibt offen bis zur getrennt freigegebenen finalen Restaggregation.

[Importmanifest](../import-manifest.json) sichert die unveränderte externe Vorfassung. [Startauftrag](../BRANCHSTART.md) hält den tatsächlichen Nutzerauftrag fest. Historische Prüfergebnisse oben bleiben ihrem jeweiligen Lauf zugeordnet. Aktuelle Dokument-/Quellen-/Vektoren-/Matrix-/Skillprüfung: [Prüfergebnis](../validation-results.json). Produktcode bleibt byteidentisch zur Basis; daher keine neuen Produktabnahmen durch diese Revision. Kein Remote-Push oder Servermerge.

Revision 6 präzisiert außerdem paketweise Zwischenprüfungen: Clientcodec gegen echte Serverquellen ab CV2-010, tatsächlicher Socket-Smoke ab CV2-020, danach kumulative Services/Runtime. Die vorhandenen modellfreien Servertesthilfen wurden im gepinnten Quellstand geprüft; der neue Clientharness wird erst im beauftragten CV2-020 umgesetzt. Keine neuen APs/Sessions oder bereits bestandenen Clientsmokes behauptet. [Checkpointreferenz](../../REFERENZ/QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md).

## 11. Revision 7: konkrete Rollen und Paket-PRs

Rollenworkflow aktualisiert: Auftraggeberleitfaden, Umsetzer-/Reviewer-Skills, Checklisten und Prompt-/Aktenvorlagen. Kumulative Paket-PRs nach feat/client-v2; Reviewer-Belege als erlaubte Docs-Commits auf pausiertem Paketbranch; unabhängiger PASS und späterer menschlicher Übernahmeprompt; genau ein Squash-Commit je Paket. Vorgängerstart prüft tatsächliche Git-/PR-Provenienz, nicht nur Status. CI-Vorabidentität für GitHub-Squash passend präzisiert.

[Umfang und Prüfung](../ROLLENWORKFLOW_REV7.md), [Maschinenlesbares Ergebnis](../rollenworkflow-validation.json). Unterlagenkandidat auf work/client-v2/rollenworkflow; bisheriger Startcommit b0525e6 unverändert, kein neuer AP-/Produkt-PASS. Quellen, Kontrakte, Vektoren, 216 Requirements, Paketumfang und Aufwand erhalten. Vor erstem Paket in dessen Arbeitsbranch übernehmen; kein zusätzlicher kanonischer Planungscommit.

## 12. Revision 8: nächster Schritt und zusätzliche unabhängige Reviews

[Gemeinsamer Einstieg](../../SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md) und [Zustandsregeln](../../SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) ergänzt; WORKFLOW_STATUS.json initialisiert ohne erfundene Ausführung. Neue Agenten ermitteln Rolle/AP/Kandidat aus offenen Paketlinien und Git-/PR-/Aktenprovenienz selbst. Alle Rollen müssen Zustände und nächste Aktion pflegen. Optional ausdrücklich weiteres unabhängiges Review; alte Berichte/Findings erhalten. Menschliche Übernahmefreigabe bleibt erforderlich.

[Auftrag/Umfang/Prüfsituationen](../ZUSTANDSWORKFLOW_REV8.md). Maschinenlesbares Ergebnis: EVIDENCE/workflow-next-step-validation.json. Dokumentkandidat weiterhin auf work/client-v2/rollenworkflow, kein kanonischer Zwischencommit und kein Produkt-PASS.
