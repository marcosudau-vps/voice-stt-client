# Gesamtimplementierungsplan – Desktop-Client auf Server V2 nachziehen

**Aktuelle Branchführung (Revision 9):** Neue Clientpakete laufen auf `feat/client-v2`, ausgehend von 8bab1b3 mit demselben Produktbaum wie a80a6b1. Der erste neue Commit enthält nur Unterlagen; AP-CV2-000 bleibt offen. Historische Distributed-/Featurebezeichnungen unten benennen die analysierten Ausgangsquellen. Kumulative Kandidaten liegen künftig auf untergeordneten Paketbranches, Code und Planpflege gehen als ein Paketaggregat gemeinsam ein. [Verbindliche Branchreferenz](../GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

Stand 2026-10-11, Revision 9. Fachliche Baselineanalyse vom 2026-10-04/05. Fachliche Ziele und Nachweise spezifiziert; interne Umsetzung anpassbar gemäß [Umsetzungsspielraum](../../SKILLS/GEMEINSAM/references/PLANUNGSSPIELRAUM.md); Implementierung noch nicht begonnen. Server: `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Clientlinie: Distributed a80a6b1 und kanonischer Featurestand 8bab1b3; V1-main f625904 ist Integrationsreferenz. Der getestete integrierte Start-SHA entsteht in CV2-000.

## 1. Ziel, Umfang und feste Entscheidungen

Der Windowsclient implementiert ausschließlich `/ws/v2` und ersetzt seine V1-/Mode-/lokale Diktierfensterautorität durch einen serverautoritativen ActivationMirror. Die bestehende Audio-/Clipboard-/SQLite-/PySide6-/Win32-/LEFX-/Observabilityfoundation wird gezielt integriert. Vorhandene Nutzerdaten und lokale Präferenzen werden migriert.

Logging/Observability und die Feedback-/Mapping-/Adapterfoundation werden weitergenutzt; die dortigen Pakete ändern nur notwendige V2-Eingänge, Identitäten und Bootstrapanschlüsse. Der Hauptumbau betrifft die Kommunikation und ihren serverautoritativen Lifecycle.

Der Gesamtplan umfasst Transport, Commands, Vordergrund-/Hintergrundzustand, Vorschau/Finals, Audio und Recovery, Controls/Suppression, Session- und Servereinstellungen, sichere Credentials, alle Feedbackausgänge, Runtimeverdrahtung, Build und reale Qualifikation. Die bereits fertiggestellte Serverimplementierung wird als Baseline verwendet. Ein belegter Serverdefekt während Cliententwicklung erhält ein eigenes Korrekturpaket; die Branch bleibt bis zur späteren ausdrücklichen Mergeentscheidung offen.

Die fachlichen Entscheidungen stehen vollständig im [Zielbild](ZIELBILD.md), die finalen Details in [K-01 bis K-04](../KONTRAKTE/README.md). Der Plan verlangt insbesondere IDbezogene alte Finals, event-vor-Ack-Toleranz, Snapshotresync ohne fiktive Textwiederherstellung, kontinuierliches Audio und einen Settingsbootstrap ohne Aktivierungsfenster.

## 2. Paketübersicht

| Paket | Konkretes Ergebnis | Fachläufe ca. | Status |
| --- | --- | --- | --- |
| [AP-CV2-000](../../ARBEITSPAKETE/AP-CV2-000.md) | Featurelinie mit Releasepolish/Namespace und Gesamttests integrieren | 1 | PLANNED |
| [AP-CV2-010](../../ARBEITSPAKETE/AP-CV2-010.md) | Wiredatentypen/Parser/Encoder und aktuelle Contractfixtures | 1 | PLANNED |
| [AP-CV2-020](../../ARBEITSPAKETE/AP-CV2-020.md) | Hello, Close-/Backoffregeln, Sessionbound Commands/Acks | 1 (ggf. 2) | PLANNED |
| [AP-CV2-030](../../ARBEITSPAKETE/AP-CV2-030.md) | Mirror mit IDguards, Backgrounddrain und Resyncpuffer | 1 (ggf. 2) | PLANNED |
| [AP-CV2-040](../../ARBEITSPAKETE/AP-CV2-040.md) | Continuous-Audio, Device-Recovery, V2logbootstrap | 1 | PLANNED |
| [AP-CV2-050](../../ARBEITSPAKETE/AP-CV2-050.md) | zwei Controlrollen, Wakepause, atomare Hotkeys und Run-Suppression | 1 | PLANNED |
| [AP-CV2-060](../../ARBEITSPAKETE/AP-CV2-060.md) | Finalresultservice, UUID-Historymigration und Injectiondedup | 1 | PLANNED |
| [AP-CV2-070](../../ARBEITSPAKETE/AP-CV2-070.md) | Configmigration, Katalog/HTTP-/Settingsservice und Bootstrap | 1 | PLANNED |
| [AP-CV2-080](../../ARBEITSPAKETE/AP-CV2-080.md) | Settings-/Admin-UI, Credential Manager, Apply-/Drainentscheidung | 1 | PLANNED |
| [AP-CV2-090](../../ARBEITSPAKETE/AP-CV2-090.md) | quellenneutrales Feedback, Overlay und Diagnosehooks | 1 | PLANNED |
| [AP-CV2-100](../../ARBEITSPAKETE/AP-CV2-100.md) | tatsächlich startbare App/Core/Qtverdrahtung | 1 | PLANNED |
| [AP-CV2-110](../../ARBEITSPAKETE/AP-CV2-110.md) | Legacyabbau, Builds/Ressourcen/Version und Kompatibilität | 1 | PLANNED |
| [AP-IV2-010](../../ARBEITSPAKETE/AP-IV2-010.md) | echte Prozessintegration am fixierten SHA-Paar | 1 | PLANNED |
| [AP-IV2-020](../../ARBEITSPAKETE/AP-IV2-020.md) | reale Windows-/ASR-/USB-/Feedback-/Clipboardabnahme | 1 | PLANNED |
| [AP-SV2-FIX](../../ARBEITSPAKETE/AP-SV2-FIX.md) | bei Bedarf konkrete Serverkorrektur FIX-nnn | befundabhängig | CONDITIONAL |

Die Richtwerte zählen Fachsessions einschließlich ihrer Tests/Reports, ohne Korrekturen. Hinzu kommt pro regulärem Paket ein unabhängiger Abnahmelauf: insgesamt **14 Umsetzungsläufe + 14 unabhängige Abnahme-/Abschlussläufe = regulär 28 Agentensessions; bei konkretem Bedarf maximal 30 ohne Korrekturen**. Aufteilung und Annahmen: [Umfangsmodell](UMFANG_UND_AGENTENLAEUFE.md). Das bedingte Serverfixpaket ist nicht in der Summe enthalten.

## 3. Verbindliche serielle Ausführungsfolge

**000 → 010 → 020 → 030 → 040 → 050 → 060 → 070 → 080 → 090 → 100 → 110 → IV2-010 → IV2-020**.

Das nächste Paket startet erst nach unabhängigem ROOT PASS, ausdrücklicher Auftraggeberfreigabe und gesicherter kanonischer Übernahme seines Vorgängers. Jedes Paket wird regulär in einem vollständigen Umsetzungslauf bearbeitet. Zusätzliche Fachläufe entstehen nur bei konkretem Restumfang oder Befund; technische Arbeitsschritte sind keine automatisch getrennten Sessions. Die technischen Voraussetzungen bleiben in den Paketdateien prüfbar, ersetzen aber keine serielle Abnahme.

Die konkreten Teilaufträge stehen in jeder AP-Datei. Das [Agentenregelwerk](../GOVERNANCE/AGENTEN_REGELWERK.md) trennt Selbstchecks, Distributed-Reviewkandidat, unabhängige Abnahme und genau einen kanonischen Aggregatecommit. Aufwand wird nach CV2-000 und jeder Übergabe nachgeschätzt; Korrekturen, Serverfixes und Hardwarewartezeiten kommen zusätzlich hinzu.

## 4. Paketübergreifende Übergaben

| Übergabe | Inhalt / Empfänger |
| --- | --- |
| Wire → Transport/Mirror | exakte Datentypen, valid/invalid fixtures, Null-/Unknownregel |
| Transport → Mirror/Settings | Generation-/Sessioncallbacks, Pending-API, event-before-ack, Snapshotresponse |
| Mirror → Controls/Results/Feedback/UI | sicher veröffentlichte Input-, Activation-, Segment- und Settingsprojektionen, Resync-/Incompleteflags |
| Audio/Recovery → Settings/Runtime | config-ready barrier, echte availability, Logaccess und Run-Suppressionwunsch |
| Settingsservice → UI/Runtime | gewünschte vs. wirksame Werte, Revisionsräume, pending/unsupported, Bootstrapabschluss |
| Results → Feedback/UI | erstes Terminal, dedupkey, history-/injectionstatus, Crashunklarheit |
| UI/Feedback → Runtime | async-safe Requests/Presentation, keine lokale Aufnahmeautorität |
| Build → Gates | Client-SHA, Server-SHA/Builddigest, Ressourcenhashs und reproduzierbare Befehle |

Jeder AP-Report nennt die tatsächlich erzeugte API und ihre Guards. Modulnamen, interne Übergabetypen und sichere Repräsentationen sind Vorschläge. Änderungen werden kurz begründet und nur in tatsächlich betroffenen Folgepaketstellen/Testzuordnungen nachgeführt; keine Zusatzfreigabe für Routineentscheidungen. [Paketablage und Vorlagen](../../SKILLS/GEMEINSAM/references/PAKETABLAGE_UND_VORLAGEN.md) definieren den schlanken Reportumfang.

## 5. Gates und Fortschritt

- **G0 / Startbereit:** CV2-000 angenommen, Clientstartbasis getestet; SHAs und Arbeitscheckout klar.
- **G1 / Headless-Vertrag:** CV2-010/020/030/040 angenommen; Handshake, ID-/Sequenz-/Recoveryverhalten als Core belastbar.
- **G2 / Produktintegration:** CV2-050..100 angenommen; Controls, Settings, Results, Feedback und Qt tatsächlich verdrahtet; volle Clientregression.
- **G3 / Auslieferbarer Kandidat:** CV2-110 angenommen; executable/wheel/frozen/UI-Smokebelege; keine Veröffentlichung.
- **G4 / Commitpaar:** IV2-010 angenommen; volle schnelle Serversuite und volle Clientsuite, echte Prozessoberflächen.
- **G5 / Real qualifiziert:** IV2-020 angenommen; Pflicht-Hardware-/ASR-/Credential-/Clipboard-/Dauerfälle gelaufen. Offene Wakekalibrierung verhindert eine uneingeschränkte Wakequalifikationsbehauptung.

Eine bestandene Teilabnahme hebt die offenen Grenzen aus [Server-Ist](ANALYSEN/SERVER_IST_UND_GRENZEN.md) nicht auf. Die [Traceability](../TRACEABILITY/TRACEABILITY_MATRIX.md) führt pro Requirement den geplanten Owner und Test; tatsächlicher Clientnachweis beginnt überall offen.

## 6. Befunde und Serveränderungen

Jeder unerwartete Fall erhält ID, Repro, Baselines, expected/actual, betroffene Requirement und Einstufung. Ein Vertragsmissverständnis korrigiert Plan und ggf. Client. Ein belegter Clientdefekt erhält einen Paketkorrekturlauf. Ein Serverdefekt wird als AP-SV2-FIX-nnn konkretisiert. Neue Features wie Domainreplay oder individuell konfigurierbare Wake-Engine-Startparameter benötigen ausdrücklich neue Kontraktspezifikation.

Nach Serverkorrektur: neue SHA, Quellenmanifest und betroffene Fixtures/Settingswerte aktualisieren; geänderte Requirements neu prüfen; Integration des neuen Paars wiederholen. Bis dahin ist die vorherige Commitkombination weiterhin die einzige belegte. Auf main erfolgt durch diesen Plan kein Merge.

## 7. Startauftrag

Der erste Implementierungsauftrag ist AP-CV2-000. Er setzt die Feature-Linie fort, integriert erforderliche V1-Releaseverbesserungen vor neuen V2-Modulen und stellt eine vollständig geprüfte integrierte Basis bereit. Anschließend ist AP-CV2-010 ohne fachliche Zusatzplanung ausführbar. Vor Umsetzung jedes späteren Pakets sind dessen Abhängigkeiten und letzter Prüfstand erneut zu lesen.

## 8. Messbare Zwischenstände

Jedes Paket besitzt einen [inkrementellen Checkpoint](../QUALIFIKATION/INKREMENTELLE_CHECKPOINTS.md). Ab CV2-020 wird der tatsächliche neue Clienttransport gegen einen isolierten modellfreien Server am gepinnten SHA geprüft, danach der Verbund schrittweise erweitert. IV2-010 wiederholt und vervollständigt diese Prüfungen am finalen Commitpaar; echte Modell-/Hardwareabnahme in IV2-020. Die Checks gehören zu den bestehenden Paketläufen, Aufwand und Paketfolge bleiben gleich.
