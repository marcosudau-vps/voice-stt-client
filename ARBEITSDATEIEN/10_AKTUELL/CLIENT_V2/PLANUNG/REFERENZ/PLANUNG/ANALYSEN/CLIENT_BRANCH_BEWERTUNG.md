# Neubewertung der Clientbasis und Erhalt beider Entwicklungslinien

**Aktuelle Branchführung (Revision 9):** Neue Clientpakete laufen auf `feat/client-v2`, ausgehend von 8bab1b3 mit demselben Produktbaum wie a80a6b1. Der erste neue Commit enthält nur Unterlagen; AP-CV2-000 bleibt offen. Historische Distributed-/Featurebezeichnungen unten benennen die analysierten Ausgangsquellen. Kumulative Kandidaten liegen künftig auf untergeordneten Paketbranches, Code und Planpflege gehen als ein Paketaggregat gemeinsam ein. [Verbindliche Branchreferenz](../../GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

Stand: 2026-10-04, Revision 2. **Empfehlung: Feature-Linie fortsetzen; V1-Releaseverbesserungen vor der Wire-V2-Implementierung gezielt integrieren.** Die frühere Startannahme „f625904/main als neue V2-Linie“ ist damit abgelöst.

## 1. Unveränderliche Ausgangsstände

| Rolle | Ref / Commit | Befund |
| --- | --- | --- |
| Kumulativer Ausführungsstand | feat/einheitliche-triggerarchitektur-distributed; a80a6b17b40751740f9c9d2aef9cad32b0470c0c | Trigger-Vorarbeiten und charakterisierende Tests |
| Kanonischer Paketstand | feat/einheitliche-triggerarchitektur; 8bab1b3f4aa070d0756c305908def4d9ebc52582 | eigener Aggregateverlauf, gleicher vollständiger Gitbaum wie a80a6b1 |
| Nachträglicher V1-Release/main | f625904795880ce71acec216e43678f9ec1656d0 | voice_stt_client-Namespace, Release-/Pfad-/Hotkeyverbesserungen; zurückgenommene Trigger-Vorarbeiten |
| Gemeinsamer Vorfahr | 1b432c97e0be2985fc23e9e9a36b51cfeba7631b | beide späteren Linien gehen hier auseinander |

Featurebaum beider Branches: `471197bc6473b8fb10e908c3313093edd96b2253`. Gleicher Baum bedeutet gleiche Dateien, nicht identische Commitgeschichte und nicht „eine Branch ist Vorfahr der anderen“. Die Branchrollen werden deshalb weiterhin getrennt geführt.

Die dokumentierte Release-Strategie bestätigt: Feature-Branches für den nachträglichen V1-Release erhalten, später beide Historien in einem eigenen Integrationszweig zusammenführen, Änderungen dateiweise prüfen und erneut qualifizieren. Beleg: [Release-Kompatibilität am f625904-Commit](https://github.com/marcosudau-vps/voice-stt-client/blob/f625904795880ce71acec216e43678f9ec1656d0/docs/COMPATIBILITY.md). Diese Datei ist Produkt-/Provenienzbeleg; alle daraus benötigten Regeln stehen auch hier.

## 2. Was die Feature-Linie tatsächlich zusätzlich enthält

Der Vergleich zum gemeinsamen Vorfahren findet 17 geänderte Produkt-/Testdateien. Wesentliche konkrete Belege:

| Bereich | Vorarbeit | Behandlung für den endgültigen V2-Vertrag |
| --- | --- | --- |
| core/config.py | getrennte manual_trigger_enabled / wake_word_trigger_enabled; explizite Flags vor Legacy-mode; Prüfung mindestens einer Quelle | erhalten und auf neues persistiertes Profil/Hello abbilden; query_parameters nicht als V2-Kontrakt behalten |
| core/stt_session.py | TriggerAck, Pendingtrigger nach commandId/Generation, Behandlung von Triggerablehnung und Disconnect | Grundideen erhalten; Wiretypen, UUIDs, Resultcodes, Versions-/Snapshotlogik auf aktuelle Commands umstellen |
| core/controller.py | _server_owns_activation, Trennung von Streamstart und Activation, Ablehnung ohne unnötigen Reconnect, korreliertes Bedienfeedback | erhaltene fachliche Regeln auf Mirror-/Commandtrackerpfad übertragen; Capability-/V1-Fallback und lokale Lifecycleautorität ablösen |
| ui/application.py / settings_dialog.py | erste Triggerflag-/Bedienanpassungen | mit V1-Hotkey-Erfassung zusammenführen; endgültige Rollen, Wake-only-Controls und Settings-UI weiter implementieren |
| tests/test_trigger_lifecycle.py | Stream-/Activationtrennung, Continuous-Streaming, Triggerablehnung und Lifecyclefälle | Assertions einzeln nach V2 übertragen; alte ready/start/trigger_ack/extend-Erwartungen ersetzen |
| tests/test_trigger_feedback_contract.py | Ackbezogenes Feedback, Replay-Dedup, gleichzeitige Quellen | Verhalten beibehalten, Herkunft/Ordnungsregeln an Domain-V2 anpassen |
| tests/test_ap_cli_000_baseline_characterization.py | produktnahes Double zeigt erneuten Streamstart nach Finish trotz gegenteiliger Controllerkommentare | als reproduzierbarer Altbefund erhalten, bis echter V2-Continuous-Audiotest ihn nachweisbar ablöst |

**Diese Vorarbeit ist wertvoll, aber kein bereits fertiger V2-Client.** Die bestehende Wireseite spricht weiter über /ws/transcribe, serverseitiges Hello/ready, trigger/trigger_ack und alte Sessionquerys. Gegen den endgültigen Server sind /ws/v2, clientinitiiertes Hello, activation.command, command.ack, kanonische UUIDs, 18 Domainereignisse und Snapshot/Revisionen erforderlich. Besonders alte „extend“-Fälle dürfen nicht unverändert nachgezogen werden.

Ein grünes Double beweist nicht automatisch dauerhaften echten Audiofluss. Der charakterisierende Test hält genau diese Grenze fest. Ebenso ist die Gesamtzahl 1.192 gegenüber 1.147 kein Qualitätsranking; konkrete Assertions und Produktionspfade entscheiden.

## 3. Wertvolle V1-Releaseverbesserungen

Vor CV2-010 müssen die folgenden kompatiblen Verbesserungen qualifiziert in der Feature-Linie verfügbar sein:

- eindeutiger voice_stt_client-Namespace einschließlich Imports, Ressourcen und Installations-/Buildpfad;
- Benutzerordner ~/.voice-stt/client, Legacy-LocalAppData-Lesen, --config / VOICESTT_CLIENT_CONFIG;
- native Hotkey-Erfassung und konfliktgeprüfte Registrierung;
- VERSION-/Commitidentität, Paketressourcen, Releaseguard und aus CI stammende überprüfbare Artefakte;
- passende Bugfixes und Tests für Konfiguration, Historie, UI, Build und Utilities.

Die Übernahme geschieht pro Änderung/Assertion. Ein Release-Controller oder eine Release-Config darf die Triggerlogik nicht pauschal überschreiben. V1-Anwenderdokumentation wird bei V2 fachlich angepasst; veröffentlichte V1-Artefakte bleiben unverändert. Das spätere Packaginggate CV2-110 qualifiziert den endgültigen V2-Kandidaten; der Namespace wird bereits im Baselinepaket hergestellt.

## 4. Abwägung

| Option | Vorteile | Kosten / Risiken | Urteil |
| --- | --- | --- | --- |
| Neu auf main beginnen und Triggerteile erneut portieren | sofort moderner Namespace und Releasepolish | vorhandene Featureentwicklung muss rückwärts ausgewählt werden; kanonische Paketlinie verliert ihre natürliche Fortsetzung | möglich, hier nicht bevorzugt |
| Feature unverändert weiterentwickeln, Release erst ganz am Ende berücksichtigen | kleinste unmittelbare Vorbereitung | spätere Namespace-/Pfadmigration trifft dann bereits sämtliche neuen V2-Module; unnötig große Endintegration | Feature-Linie richtig, Übernahmezeitpunkt zu spät |
| Feature-Linie fortsetzen, erforderliche Releaseverbesserungen früh qualifizieren | vorhandene Regeln/Tests/Provenienz bleiben; neue V2-Module entstehen im endgültigen Namespace | CV2-000 enthält eine zusammenhängende frühe Integrations-/Baselineaufgabe | **empfohlen und als neue Planungsbasis geführt** |
| Beide Heads ungeprüft mergen und Konflikte nach „neuere Datei gewinnt“ lösen | kurzfristig wenig manuelle Auswahl | Triggerregression, doppelte Autorität, falsche Tests und verdeckte Datenmigration | keine zulässige Integrationsmethode |

Die erste Startannahme war bewusst mit Blick auf den geprüften Release und den Paketnamespace formuliert. Sie gewichtete die Feature-Vorarbeit und die ausdrücklich dokumentierte spätere Releaseintegration unzureichend. Die erneute Prüfung korrigiert diese Empfehlung; sie entwertet weder die V1-Qualifikation noch die Feature-Baseline.

## 5. Konkreter Start- und Integrationsauftrag

1. CV2-000 startet auf einem Paketbranch vom Dokumentstart auf `feat/client-v2`, gegründet auf kanonisch 8bab1b3 mit demselben Ausgangsbaum wie Distributed a80a6b1. Beide SHAs, Bäume, main f625904 und lokale WIP-Zustände sichern/inventarisieren.
2. Die separat qualifizierten V1-Verbesserungen auf einem isolierten Vorbereitungspfad portieren oder eine explizite Integrationsprobe verwenden; jede Konfliktauflösung ist dateiweise begründet. Eine Probe ist noch keine Freigabe, beide Historien in die kanonische Paketbranch zu mergen.
3. Produktschnittstellen und Tests nach voice_stt_client überführen, Triggerverhalten erhalten und die Feature-/Release-Assertions in einer Übernahmematrix verbinden.
4. Gesamtsuite, compileall, Ressourcen-/Import-/Versionschecks und frühe Packagingprüfungen ausführen; ROOT-Review des fertigen Kandidaten.
5. Den **erst dadurch entstehenden integrierten Start-SHA** und Baum festhalten. Vor CV2-010 ist dies Pflicht. Heute existiert dafür noch kein behaupteter Commit.
6. Weitere Fachläufe kumulativ auf dem jeweiligen untergeordneten Paketbranch; genau ein Code-/Plan-Aggregatecommit pro abgeschlossenem Paket auf `feat/client-v2`. Die beiden Entwicklungsgeschichten nicht umschreiben.
7. V1-main und V2 werden erst beim separat autorisierten Abschluss in einem eigenen Integrationszweig zusammengeführt und das konkrete Paar erneut qualifiziert. Kein Main-Merge während dieser Planungsrevision.

Alle Folgepakete verwenden Pfade unter voice_stt_client als **Ergebnis von CV2-000**, nicht als Behauptung über den heutigen a80a6b1-Baum.

## 6. Verifikation und offene Aussagegrenzen

Featureexport a80a6b1: **1.192 Tests OK, 84,649 s**, Python 3.12.10, Qt offscreen. Releaseexport f625904: zuvor **1.147 Tests OK, 84,729 s**. Beide Ergebnisse gelten für ihren eigenen Stand. Die integrierte Feature-/Releasebasis wurde noch nicht gebaut oder getestet.

[Maschinenlesbarer Branchvergleich](../../../EVIDENCE/client-branch-comparison.json) enthält SHAs, Bäume, Vorfahr, geänderte Dateien, existierende Testmethoden und die eigene Testgeltung. [Quellenmanifest](../../../EVIDENCE/source-manifest.json) unterscheidet Featurebelege und Releaseausgangsstellen anhand des jeweiligen Commits.
