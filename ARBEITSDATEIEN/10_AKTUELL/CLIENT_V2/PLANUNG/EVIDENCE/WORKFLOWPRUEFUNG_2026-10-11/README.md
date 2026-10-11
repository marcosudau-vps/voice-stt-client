# Belegsatz im Korrekturkandidaten R03

Der vollständige Satz (22 Dateien, drei Archivteile, 6355 historische Quelldateien) ist mit R03 im bestehenden Paketbranch/PR #2 veröffentlicht. Tatsächliche Erstpublikation am Commit `210c2ae14355d22e9b25172cf47a1bcf94860300`: alle 117 erforderlichen Pfade online abgerufen und SHA256-geprüft, Texte LF-normalisiert und Archivteile bytegenau. [Versionierter Erstnachweis](../../../30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/EVIDENCE/remote-first-publication.json), [Remoteprüfer](../../../30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/EVIDENCE/verifiziere_remote.py).

Dieser administrative Nachtrag aktualisiert README/BEREITSTELLUNG/Manifest und sichert den tatsächlich erzeugten Erstnachweis. Seine endgültige Spitze wird nach Push nochmals vollständig überprüft; tatsächliche finale SHA/Tree, Remoteprüfung und CI in der PR-Übergabe. Kein selbst behaupteter zukünftiger Nachweis. Bewertung, Rohbelege, synthetische Profile und Archive sind erhalten; historische Skripte werden nicht ausgeführt.

## Historischer Vorbereitungsstand

# Workflowprüfung und Korrekturübergabe – 2026-10-11

Dieser Ordner enthält die ergänzende Bewertung des ersten Umsetzungs-/Reviewablaufs und die lokal vorbereitete Übergabe an den nächsten AP-CV2-000-Korrekturlauf. **Noch nicht committet oder gepusht.** Er gehört beim nächsten Korrekturlauf vollständig in den bestehenden [Paket-PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2) auf `work/client-v2/ap-cv2-000`; `feat/client-v2` bleibt bis zur unabhängigen Abnahme und menschlichen Übernahmefreigabe unverändert.

## Einstieg für den Korrekturagenten

1. [Korrekturauftrag](KORREKTURPROMPT_AP_CV2_000.md) vollständig lesen. Verbindlich wird der Entwurf durch den tatsächlichen menschlichen Auftrag.
2. [Bewertung und Empfehlungen](BEWERTUNG_UND_EMPFEHLUNG.md), [Herkunft und Grenzen](IMPORT_HINWEISE.md) sowie die aktuelle R02-Reviewakte lesen.
3. [Dateimanifest](IMPORT_MANIFEST.json) und [lokalen Bereitstellungsnachweis](BEREITSTELLUNG.json) prüfen; den gesamten Ordner zusammen mit den Korrekturen in denselben Paket-PR aufnehmen.

Die operative Grundlage bleibt der [Nächster-Schritt-Skill](../../SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md). Externe Ordner werden für Umsetzung, Review, Dokumentpflege und Übergabe nicht benötigt. Neue Arbeitsunterlagen ausschließlich im Clientrepository anlegen. Den tatsächlich erteilten Originalprompt in der eigenen Runakte sichern und diesen Belegsatz aus Paket-/Run-/Evidenzindex relativ verlinken; keine zweite Kopie des Belegsatzes pflegen.

Der [vorbereitete Steuerungseintrag](VERLAUFSEINTRAG_VORBEREITET.md) wird erst nach dem Fast-forward in den aktiven Verlauf übernommen. Alle getrackten Dateien sind unverändert; der lokale Belegsatz bleibt dabei erhalten.

## Erhaltener historischer Themenbestand

[Quellbestandsmanifest](HISTORIE/QUELLBESTAND_MANIFEST.json) und [Archivteil 1](HISTORIE/WORKFLOW_TOOLS_THEMENSTAND_2026-10-11.zip.001), [Teil 2](HISTORIE/WORKFLOW_TOOLS_THEMENSTAND_2026-10-11.zip.002) und [Teil 3](HISTORIE/WORKFLOW_TOOLS_THEMENSTAND_2026-10-11.zip.003) sichern den zuvor extern abgelegten Themenordner `EINHEITLICHE_TRIGGERARCHITEKTUR` einschließlich ursprünglicher Planung, Zwischenrevisionen, Veröffentlichungsbelegen, Quellkopien und früheren Serverakten. Die Teile ergeben in numerischer Reihenfolge byteweise zusammengesetzt das vollständige ZIP; jeder Teil bleibt unter 100 MiB. Insgesamt sind 6.355 Originaldateien gesichert. Jeder Archivpfad ist mit Größe und SHA256 erfasst und gegen den Archivinhalt geprüft. Die Originaldateien bleiben erhalten.

Dieses Archiv ist **historische Provenienz, keine operative Pflichtlektüre und keine zweite gültige Planung**. Es wird nicht bei jedem Agentenlauf entpackt. Alte Anweisungen, absolute Pfade, Momentaufnahmen, generierte Laufzeit-/Testdateien und Skripte behalten ihre damalige Bedeutung und steuern den aktuellen Workflow nicht. Die neue Client-V2-Planung und die tatsächliche Git-/PR-Spitze sind maßgeblich. Die entpackten Auditbelege dieses Ordners sind unmittelbar lesbar; die alte externe Ablage hat für den weiteren Ablauf keine Rolle.

Die ZIP-Ausnahme in `HISTORIE/.gitignore` gilt ausschließlich für dieses konkrete Provenienzarchiv. Beim Korrekturpush die Archivteil-Gitblobs bytegenau und die Textbelege anhand der LF-normalisierten Manifesthashes am tatsächlichen Remotecommit prüfen. Erst dieser Transport macht den Belegsatz online verfügbar; dann den Bereitstellungsstatus und permanente GitHub-Links aktualisieren.
