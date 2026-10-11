# AP-SV2-FIX – Bedingtes Serverkorrekturpaket während der Cliententwicklung

**Branch-/Unterlagenpflege:** Diese FIX-Instanz arbeitet im Serverrepository auf eigenem Serverarbeitsbranch vom festgehaltenen Distributed-Parent. Geprüfte Fixes werden nach menschlicher Sicherungsfreigabe kumulativ auf Server-Distributed übernommen; finales Serverfeature-Aggregat bleibt aufgeschoben. Clientblocker/Rebaseline werden auf dem gehaltenen Clientpaketbranch dokumentiert. [Branchreferenz](../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).



**Status:** CONDITIONAL / NICHT GESTARTET. **Stand:** 2026-10-11, Revision 10 (Branchführung/Planpflege).




**Rollen-Einstieg:** [Umsetzung](../SKILLS/voice-stt-client-v2-umsetzen/SKILL.md) bzw. [unabhängige Abnahme](../SKILLS/voice-stt-client-v2-abnehmen/SKILL.md). Das Paket beschreibt das fachliche Ergebnis; Start-/Abgabe-/Reviewablauf und Aktenvorlagen werden über den jeweiligen Skill geladen.

## Ziel und überprüfbarer Endzustand



Ein während der Umsetzung nachgewiesener Serverdefekt wird klein und prüfbar korrigiert, ohne den offenen Branch vorzeitig zu mergen.



## Voraussetzungen und Scope



- Abhängigkeiten: keine; Baselinegate bzw. expliziter Befund startet das Paket.

- Fachliche Ownership (genannte Modulorte sind Vorschläge): Nur Serverrepository; ein konkret belegter Defekt pro instanziiertem FIX-nnn. Clientfixes bleiben Clientpakete.

- Referenzserver: `ada13b011e1d3829f78e7f389e3b927795a2b3be`; Client-Ausführungslinie `a80a6b17b40751740f9c9d2aef9cad32b0470c0c`, kanonische Featurebasis `8bab1b3f4aa070d0756c305908def4d9ebc52582`; implementierbarer integrierter Start-SHA wird in CV2-000 erzeugt und geprüft. V1 `f625904795880ce71acec216e43678f9ec1656d0` ist Release-/Migrationsreferenz.

- Kontrakte: [K-01](../REFERENZ/KONTRAKTE/K-01_WIRE_AUDIO_COMMANDS.md), [K-02](../REFERENZ/KONTRAKTE/K-02_EVENTS_MIRROR_ERGEBNISSE.md), [K-03](../REFERENZ/KONTRAKTE/K-03_SETTINGS_WAKE_WORDS.md), [K-04](../REFERENZ/KONTRAKTE/K-04_LOGS_AUTH_RECOVERY.md).

- Anforderungen aus der [Traceability](../REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md): Befundabhängig: konkrete Requirement-IDs bei FIX-Instanziierung zuordnen.



## Umfang und Agentenläufe



Nur bei konkretem Serverbefund zusätzlich schätzen; keine vorab eingeplante Korrekturkette. Unabhängige Abnahme und ausdrückliche Auftraggeberfreigabe gelten auch für die konkretisierte Instanz.



Reviewer-PASS ist ein technischer Befund. Geprüfte Fixes werden nur mit passender ausdrücklicher Auftraggeberfreigabe auf Server-Distributed gesichert. Die kanonische Restübernahme erfolgt später zusammen mit dem finalen Serverdelta als ein Aggregat, nicht sofort je Fix. Ihre Freigabe erfolgt **ausschließlich durch einen ausdrücklichen Prompt des Auftraggebers**. Die kurze Übernahme führt nach dem menschlichen Prompt vorzugsweise der Umsetzer im bestehenden Lauf aus; alternativ ein ausdrücklich beauftragter Abschlussagent. Dafür ist kein dritter fachlicher Pflichtlauf geplant. [Umfangsmodell](../REFERENZ/PLANUNG/UMFANG_UND_AGENTENLAEUFE.md), [Agentenregelwerk](../REFERENZ/GOVERNANCE/AGENTEN_REGELWERK.md).



## Betroffene Dateien und Schnittstellen – vorgeschlagene Zuordnung



- `Erst bei Befund: ausdrücklich benannte Servermodule und direkte Tests`



Pfade sind repositoryrelativ. Bei Clientmodulen gilt der Paketnamensraum `voice_stt_client`. Mit „neu“ bezeichnete Dateien und Testmodule sind Umsetzungsvorschläge, keine Pflicht zur Neuanlage. Passende vorhandene Module/Tests dürfen erweitert werden; die fachlichen Lieferergebnisse und vollständigen Nachweise bleiben Pflicht. Die voice_stt_client-Pfade sind der von CV2-000 hergestellte Zielnamespace; der heutige Featurestand besitzt noch core/ui auf Toplevel. Notwendige Änderungen an gemeinsamen Dateien werden vor Start mit dem aktuellen Diff abgeglichen; fremde Änderungen bleiben erhalten.



## Umsetzungsspezifikation



Die fachlichen Wirkungen und Akzeptanzkriterien sind verbindlich. Interne Repräsentation, Dateinamen und Reihenfolge der folgenden Arbeitsschritte sind an den Bestand anpassbar: [Umsetzungsspielraum](../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md). Die Runakte folgt der [Paketablage mit Vorlagen](../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md).



1. Dieses Paket ist eine Vorlage und startet nicht automatisch. Als AP-SV2-FIX-001 etc. mit reproduzierbarem Trigger, betroffenem SHA, tatsächlicher/erwarteter Wireantwort und Requirementinstanz eröffnen.

2. Defekt gegen vorhandenen Vertrag von neuem Featurewunsch unterscheiden. NSStartoptionen/Replay sind explizite Vertragsänderungen, kein stiller Bugfix.

3. Failing Regression zuerst, minimale Serverkorrektur, vollständige schnelle Serversuite und relevante Clientintegration. Bestehenden V1-Kompatibilitätspfad prüfen.

4. Server-Archiv-/Aktionsregisteranforderungen des Repositories erfüllen. Neue SHA und geänderte Wire/Settings-/Vektoren in diesem Plan, Manifest und Matrix fortschreiben.

5. Keine Clientproduktdatei besitzt dieses Serverpaket; gegebenenfalls abhängigen Clientfix separat spezifizieren.

6. Serverbranch bleibt offen; Commit/Push/PR/Merge ausschließlich bei gültiger konkreter Freigabe. Nach Korrektur IV2-Gate für neue Commitkombination wiederholen.



## Liefergegenstände und Übergabe



- Konkrete FIXinstanz mit Scope/Tests/Repro.

- Revidierter Serverbaseline-/Kontrakt-/Integrationsnachweis.

- Entscheidungsreport, ob Änderung innerhalb V2additiv oder echter Contractwechsel.



Der Übergabereport nennt öffentliche Funktionen/Datentypen, Callbackreihenfolge, Generation-/Sessionguards, erzeugte Sideeffects, Konfigurations-/Datenmigration und verbleibende Einschränkungen. Folgepakete dürfen keine unausgesprochenen Annahmen aus Testdoubles übernehmen.



## Akzeptanzkriterien



- [ ] Befund ist reproduziert und einem konkreten Requirement zugeordnet.

- [ ] Defekt behoben mit Regression und ohne unbelegte angrenzende Umbauten.

- [ ] Neue Baseline und sämtliche betroffenen Dokumente/Fixtures konsistent.

- [ ] Kein vorzeitiger Merge oder verdecktes Clientfix.



## Konkrete Validierung



- Vorher FAIL/nachherPASS-Repro, vollständige Serversuite, V1/V2boundary und betroffene Crossrepo-Fälle.

- Bei Contractänderung alle betroffenen Decoder-/Mirror-/Settings-/Buildtests der Clientseite.



Siehe [Testplan](../REFERENZ/QUALIFIKATION/TEST_UND_ABNAHMEPLAN.md). Baseline-/Build-/Server-/Hardwareprüfungen werden gemäß Paketauftrag ausgeführt und ihr tatsächlicher Umfang im Report festgehalten.



Die Befehle mit geplanten `test_v2_*`-Namen zeigen die vorgesehene Testzuordnung. Entstehen die Nachweise in bestehenden oder anders benannten Modulen, werden Befehle, Matrix und Übergabe auf die tatsächlichen Methoden angepasst. Fehlende Pflichtabdeckung ist FAIL; ein fehlender vorgeschlagener Dateiname allein nicht. Tests werden vor Änderung als Baseline, nach Umsetzung gezielt und anschließend vollständig ausgeführt. Erforderliche Abhängigkeiten werden in der Projektvenv installiert. Hardware-/Goldenfälle werden separat protokolliert; fehlende Belege dürfen automatisierten PASS nicht in eine reale Gesamtabnahme umdeuten.



## Definition of Done



- [ ] Alle fachlichen Lieferergebnisse und Akzeptanzkriterien erfüllt; begründete interne Umsetzungsentscheidungen und tatsächliche Prüfmethoden dokumentiert.

- [ ] Alle zugeordneten Requirement-IDs einzeln mit Test-/Reportbeleg aktualisiert.

- [ ] Relevante Tests und vollständige Regressionsprüfung ohne unerklärte Fehler bestanden; Abweichungen/Skips einzeln eingeordnet.

- [ ] Neue Produktinterfaces und erforderliche Dokumentation einschließlich Kompatibilität/Startanleitung/Migrationsverhalten aktualisiert.

- [ ] `git diff --check` bestanden; keine Secrets, Nutzeraudio, Datenbanken oder Laufzeitlogs im Produktdiff.

- [ ] Report mit Start-/End-SHA bzw. überprüftem Workingtreediff, Runtime, Befehlen, Resultaten, Restrisiken und Übergabe geschrieben.



Ein Paket mit offenem Pflichtkriterium ist `CHANGES_REQUIRED` oder `BLOCKED`, niemals `ROOT_PASS`/`ACCEPTED`. Vollständige Selbstchecks ergeben `REVIEW_READY`; erst die unabhängige Abnahme ergibt ROOT PASS, die ausdrücklich freigegebene Sicherung auf Server-Distributed FIX_ACCEPTED. Die finale kanonische Serverpromotion bleibt bis zur gemeinsamen Qualifikation offen; FIX_ACCEPTED behauptet keine erfolgte Serverfeatureübernahme. Eine veränderte Serverbaseline verlangt die in diesem Plan beschriebene neue Kontrakt-/Integrationsprüfung.



## Grenzen, Fehler und Abschlussregel



Notwendige kleine Anschlussänderungen an gemeinsamen Dateien sind mit Begründung erlaubt; selbstständige Folgefeatures bleiben ihrem Paket zugeordnet. Eine Verlagerung ganzer Requirementowner wird vor PASS ausdrücklich abgestimmt. Produktfehler zuerst reproduzieren, gezielt korrigieren und alle betroffenen Tests wiederholen. Serveränderungen werden ausschließlich als eigene FIX-Instanz mit konkret benannten Dateien geführt; Qualifikationspakete ändern keinen Produktcode.



Ein einzelner Ausführungsrun bearbeitet das beauftragte Paket. Bericht und reviewbarer Diff werden immer fertiggestellt. Commit, Push, PR, Tag, Merge und Veröffentlichung erfolgen nur, wenn die konkrete Ausführung dafür autorisiert ist. Diese Planung erteilt dafür keine implizite Freigabe; die offene Serverbranch bleibt erhalten.

## Gemeinsamer Einstieg und Rückkehr

SERVER_FIX_REQUIRED blockiert das gehaltene Clientpaket und verweist auf die eine beauftragte servereigene FIX-Akte mit Status/Branch/Parent. Der gemeinsame Einstieg folgt dieser Linie bis zu tatsächlichem FIX_ACCEPTED auf Server-Distributed, dann zurück zum gehaltenen Clientpaket. Neue Server-SHA, betroffene Verträge/Quellen/Matrix und Tests am neuen Paar gemeinsam pflegen; kein automatisch freigegebenes Folge-AP. Auswahl, Serverrechte, Review-/Sicherungsphasen und Rückkehrbelege: [Sonderfallreferenz](../SKILLS/GEMEINSAM/references/SONDERFAELLE_UND_WIEDERAUFNAHME.md). Ohne Serverauftrag keine eigenmächtige Änderung; Clientfreigabe ist keine Serverfreigabe.
