# Herkunft und Bereitstellung der Workflowbewertung

Stand 2026-10-11. Dieser Belegsatz ist auf Auftrag des Nutzers vollständig im Client-V2-Workspace vorbereitet. Er ist noch nicht committet oder gepusht und soll gemeinsam mit dem AP-CV2-000-Korrekturlauf in den bestehenden PR #2 aufgenommen werden. Kein neuer normativer Planungszweig und keine unabhängige Paketabnahme. Die frühere externe Ablage wird für den weiteren Workflow nicht gebraucht.

## Inhalt und Herkunft

- [Bewertung und Empfehlungen](BEWERTUNG_UND_EMPFEHLUNG.md), [vollständiger Korrekturauftragsentwurf](KORREKTURPROMPT_AP_CV2_000.md).
- [Struktur-/Identitätsprüfung und gezielter Probe](workflow-audit.json), [PR-Snapshot](pr-snapshot.json), [PR-Beschreibungssnapshot](pr-body-snapshot.json).
- [Audit-/Reproskript](audit_workflow.py) und [Finalisierung der Bewertung](finalisiere_bewertung.py) als damalige Ausführungsprovenienz. Absolute Windows-/Repositorypfade in den Skripten gehören zur ursprünglichen Umgebung. Der Finalisierungscode schreibt unter anderem einen lokalen Verlaufseintrag. Die Skripte daher nicht blind ausführen oder auf einen neuen Stand anwenden.
- Synthetische Profile: [Corefehlerfall](SYNTHETISCHE_PROFILE/core-failure-v2.yaml), [erfolgreicher Gegenfall](SYNTHETISCHE_PROFILE/core-success-v2.yaml). Diese Dateien sind ausschließlich künstliche Testdaten; keine realen Anwenderprofile, keine private Mikrofonaufnahme oder Transkripthistorie. Der Probe verwendete echte AppConfig-Persistenz und tatsächliche Anwendungsmethoden mit simuliertem Hotkey-/Core-/Tray-Verhalten. Er ersetzt weder eine Hardwarebeobachtung noch eine vollständige Produktregression.
- [Erste Testfixture](SYNTHETISCHE_PROFILE/core-failure.yaml) ist ebenfalls erhalten: Sie verwendete irrtümlich eine mit dem Default-Reinsert-Hotkey kollidierende Belegung und scheiterte bereits an Konfigurationsvalidierung. Sie ist **kein** Produktfehlerrepro und kein weiterer bestandener Test. Danach wurde die gültige v2-Fixture verwendet; nur diese Ergebnisse stehen im Audit-JSON.

## Vorbereitung und spätere Veröffentlichung

Die zwölf ursprünglichen Auditdateien wurden zunächst byteidentisch übernommen. Die aktuelle Auftragsvorlage und diese Ablagehinweise wurden anschließend auf die workspaceinterne Übergabe umgestellt; das aktuelle [IMPORT_MANIFEST.json](IMPORT_MANIFEST.json) identifiziert den vorbereiteten Gesamtdateisatz. Die unveränderten früheren Fassungen sind im vollständigen historischen Themenarchiv erhalten. [Quellbestandsmanifest](HISTORIE/QUELLBESTAND_MANIFEST.json) dokumentiert jeden Originalpfad, Größe und SHA256. [README](README.md) erklärt die Archivteile und die Abgrenzung von der gültigen Planung.

Auditbefunde, PR-Snapshots und synthetische Profile behalten ihre damaligen Inhalte. Absolute Pfade in den alten Skripten und Belegen sind Herkunftsangaben, keine Pflicht zum Lesen oder Schreiben außerhalb des Clientrepositorys. Historische Skripte nicht erneut ausführen. Der [read-only-Bereitstellungsprüfer](pruefe_bereitstellung.py) benötigt ausschließlich diesen Workspace.

Der Korrekturagent verlinkt diesen Ordner aus Paketindex, eigener Runakte und Evidenzindex. Er sichert den tatsächlich erteilten menschlichen Auftrag separat und übernimmt die vorbereiteten Unterlagen einschließlich Archivteilen gemeinsam mit seinen Korrekturen auf `work/client-v2/ap-cv2-000` in PR #2. Die Vorbereitung selbst erzeugt keinen Commit, Push, weiteren PR, Featurecommit oder Paket-PASS. Nach dem Korrekturpush den vollständigen Dateisatz am tatsächlichen Remotecommit verifizieren und Bereitstellungsstatus sowie permanente Links ergänzen. Kein separat veröffentlichter Bewertungsstand.

Das Dateimanifest enthält seinen eigenen Hash wegen Selbstreferenz nicht. Textdateien besitzen zusätzlich LF-normalisierte SHA256 für Git-Zeilenendenkonvertierung; Archivteile werden stets bytegenau geprüft. Bei späteren Änderungen an den Ablage-/Transporthinweisen den aktuellen Dateisatz neu manifestieren, historische Auditbelege dabei unverändert lassen.
