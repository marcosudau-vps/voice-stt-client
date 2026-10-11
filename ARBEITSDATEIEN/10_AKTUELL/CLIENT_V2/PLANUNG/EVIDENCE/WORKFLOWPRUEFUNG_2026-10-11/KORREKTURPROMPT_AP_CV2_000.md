# Korrekturauftrag AP-CV2-000 einschließlich gezielter Workflow-Nachschärfung

Diese Vorlage wird erst durch tatsächlichen Versand als menschlicher Auftrag verbindlich.

```text
Bitte führe den nächsten Korrekturlauf für AP-CV2-000 aus und erledige
darin die nachstehenden kleinen Workflow-Nachschärfungen mit.

Repository: https://github.com/marcosudau-vps/voice-stt-client
Paket-PR: https://github.com/marcosudau-vps/voice-stt-client/pull/2
Paketbranch: work/client-v2/ap-cv2-000
Kanonische Abschlusslinie: feat/client-v2
Lokaler Checkout: P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\client-v2

Verbindlicher Einstieg, relativ zum Repository:
ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md

Lies die gültigen AGENTS, Zustandsregeln, den Umsetzungsskill samt
Korrekturreferenz und die aktuelle Paket-/Reviewakte. Prüfe die echte
lokale und veröffentlichte Branch-/PR-Spitze. Die letzte bekannte
Reviewspitze ist 2dc251d; der maßgebliche Zustand ist CHANGES_REQUIRED.
Übernimm bei sauberem Checkout zuerst die Reviewunterlagen per
Fast-forward. Kein Zurücksetzen auf einen alten Einreichungsstand.

0. Vorbereitete Bewertung und Belege in denselben Paket-PR aufnehmen

Der vollständige Belegsatz liegt bereits in diesem Client-V2-Workspace:
ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/

Lies dort README.md, BEWERTUNG_UND_EMPFEHLUNG.md und IMPORT_HINWEISE.md.
Prüfe IMPORT_MANIFEST.json mit dem beiliegenden read-only-Prüfer:
.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11/pruefe_bereitstellung.py

Der Ordner ist vorbereitete, noch nicht committete Vorarbeit für diesen
Korrekturlauf. Er darf bei der Synchronisierung mit der Reviewspitze
nicht verworfen werden. Übernimm den gesamten Ordner einschließlich
HISTORIE-Archivteilen und Manifesten zusammen mit deinen Korrekturen
in den bestehenden Paketbranch und PR #2. Kein separater Veröffentlichungs-
lauf, kein weiterer PR und kein Dokumentcommit auf feat/client-v2.
Vorhandene Änderungen inventarisieren und gezielt zuordnen; fremde
Änderungen nicht überschreiben oder blind stagen.

Die Archivteile enthalten den vollständigen früher extern abgelegten
Themenbestand als historische Provenienz. Ihre Pfade und Hashes sind in
HISTORIE/QUELLBESTAND_MANIFEST.json erfasst. Die drei Teile sind der Reihe
nach Byte für Byte zu einem ZIP zusammensetzbar; jedes Teil bleibt unter
der GitHub-Dateigrenze. Zur Arbeit nur die aktuelle Bewertung und die
aktiven Client-V2-Unterlagen lesen. Alte Pläne, Skripte und absolute
Herkunftspfade im Archiv sind keine aktuellen Regeln oder Abhängigkeiten.
Die in HISTORIE/.gitignore enthaltene Ausnahme gilt nur für diesen Satz.

Bewertung, Rohbelege und synthetische Profile als damaligen Prüfstand
erhalten; historische Audit-/Finalisierungsskripte nicht blind ausführen.
Die fehlerhafte erste Testfixture ist ausdrücklich kein Produktrepro.
Keine echten Benutzerprofile, Zugangsdaten oder privaten Laufzeitdaten
zusätzlich aufnehmen. Neue Arbeitsunterlagen nur im Clientrepository
ablegen; ein Zugriff auf die frühere externe Ablage ist nicht erforderlich.

Verlinke diesen Datensatz aus Paketindex, neuer Runakte und deren
EVIDENCE/INDEX.md. Sichere den tatsächlich erteilten menschlichen Auftrag
separat als 00_PROMPT_ORIGINAL.md; dieser Auftragsentwurf ersetzt ihn nicht.
Der vorbereitete Steuerungseintrag liegt hier separat als
VERLAUFSEINTRAG_VORBEREITET.md. Übernimm ihn nach dem Fast-forward in
ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md, sodass die Vorbereitung mit
dokumentiert ist. Bis dahin sind alle getrackten Dateien unverändert;
die Vorarbeit blockiert die Synchronisierung mit der Reviewspitze nicht.

Aktualisiere bei der Abgabe README/BEREITSTELLUNG und das Dateimanifest
auf den tatsächlich übernommenen Satz. Nach dem normalen Korrekturpush
alle Belegpfade und den Originalauftrag am tatsächlichen Remotecommit
prüfen: Textdateien per LF-normalisiertem SHA256, Archivteile bytegenau.
Nenne Commit und permanente GitHub-Links auf Bewertung, Manifest und
Korrekturauftrag in der PR-Übergabe. Nur lokale oder ignorierte Dateien
gelten nicht als online bereitgestellt. Bis dahin keine Veröffentlichung
behaupten. Der veröffentlichte Belegsatz gehört zum selben kumulativen
Paketkandidaten und später zu dessen einem freigegebenen AP-Aggregat.

1. Produktfinding korrigieren

Bearbeite CV2-R02-F01 aus R02-ABNAHME. Reproduziere den Fall:
Hotkeykonflikt, erfolgreich registrierter Ersatz, danach fehlgeschlagener
Corestart. Das bisherige Benutzerprofil darf beim fehlgeschlagenen Start
nicht mit dem Ersatzhotkey überschrieben bleiben. Wähle eine möglichst
kleine Lösung; erfolgreiche Starts, deaktivierte Hotkeys und Wake-only
müssen weiterhin funktionieren. Ergänze einen deterministischen
Regressionstest mit isoliertem Profil und den erforderlichen Gegenfällen.

Die Speicherreihenfolge war bereits im V1-Release vorhanden. Dokumentiere
dies als übernommenen Bestandsfehler; keine allgemeine Hotkey- oder
Feedback-Neugestaltung und keine zusätzliche V2-Fachimplementierung.

2. Aktuelle Arbeitsunterlagen konsistent machen

Korrigiere in
ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md
die drei R02-Links: dort müssen sie mit RUNS/R02-ABNAHME/... beginnen,
nicht nochmals mit 30_AUSFUEHRUNG/AP-CV2-000/....

Gleiche den aktuellen Paketstatus in WORKFLOW_STATUS.json,
PLANUNG/EVIDENCE/package-manifest.json, Paketdatei und Paketindex ab.
Das Manifest steht nach R02 noch auf REVIEW_READY statt CHANGES_REQUIRED.
Pflege Zustände während deiner Korrektur und zur erneuten Einreichung
gemäß Workflow. Aktualisiere auch die PR-Kurzfassung; alte Einreichungs-
und Reviewstände als historische Provenienz erhalten.
Alte abgeschlossene R01-/R02-Reports und Belege nicht umschreiben.

3. Bestehende Regeln gezielt präzisieren

Die folgenden Pfade sind relativ zum Planordner
ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/:

a) SKILLS/voice-stt-client-v2-abnehmen/references/ABNAHMECHECKLISTE.md:
   Ergänze vor den fachlichen Prüfschritten einen kurzen Prüfstart:
   isolierten Kandidatencheckout und den tatsächlich nutzbaren Testweg
   verifizieren. Lokales geeignetes Windows oder vom Reviewer veranlasster
   geeigneter Prüfhost sind zulässig; SHA/Base, Runtime, Befehle und
   vollständige Logs müssen nachvollziehbar sein. Eine bloße Sichtung
   vorhandener grüner CI ist keine Behauptung eigener Testdurchführung.
   Bei fehlender Voraussetzung konkrete Lücke und nächsten Testweg melden;
   statische Teilprüfung darf Findings liefern, aber keinen ROOT_PASS.
   Kein zusätzlicher Agentenlauf oder neue Abnahmephase hierfür.

b) SKILLS/GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md:
   Präzisiere: Vor Rollenwahl aktuelle Remote-/PR-Spitze und lokale
   Abweichungen abgleichen. Die gewählte Paketlinie ist maßgeblich;
   aktive WORKFLOW_STATUS-, Manifest-, Paketkopf- und Indexzustände müssen
   zueinander passen. Historische Runreports behalten ihre damaligen
   Zustände. Bei Widerspruch Quelle klären, keinen PASS oder Paketstart
   aus einer veralteten Kopie ableiten. Bestehende Git-/Nachmerge- und
   menschliche Freigaberegeln beibehalten.

c) SKILLS/GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md und beide
   Rollenchecklisten ABGABECHECKLISTE.md / ABNAHMECHECKLISTE.md:
   Ergänze die Prüfung vor jeder Abgabe: aktive Statusangaben und
   PR-Kurzfassung abgleichen, neue/geänderte relative Aktenlinks vom
   tatsächlichen Quelldokument aus auflösen, referenzierte Originalprompts,
   Reports und Evidenz tatsächlich bereitstellen. Auch der Reviewer muss
   seinen Docs-Commit strukturell prüfen. Alte Belege bleiben erhalten.

Stelle dafür einen kleinen gemeinsamen V2-Aktenprüfer unter
SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py bereit und verlinke den
Aufruf in beiden Checklisten. Prüfe mindestens referenzierte Dateipfade,
relative Aktenlinks und Konsistenz des aktiven Paket-/Manifeststatus.
Keine Festverdrahtung auf AP-CV2-000 oder ausschließlich REVIEW_READY.
Qualifiziere ihn mit einem korrekten Zustand sowie den tatsächlich
gefundenen Fehlfällen: gebrochener Link und widersprüchlicher Status.
Der historische R01-check_records.py bleibt als damaliger Beleg erhalten;
der alte allgemeine Blockvalidator darf keine V2-widrige Struktur erzwingen.
Kein Workflowdienst, keine neue Dokumenthierarchie oder Pflichtrolle.

4. Qualifikation und Abgabe

Führe gezielte Repros/Gegenfälle, die vollständige Clientsuite und die
gemäß Änderung erforderlichen Packaging-/Smokes aus. Prüfe die aktuelle
Aktenstruktur mit dem gemeinsamen V2-Prüfer. Pflege betroffene Planung,
Requirements/Matrix und nötige Versionsmetadaten konsistent; keine neuen
Requirements oder Arbeitspakete ohne fachlichen Bedarf.

Lege eine neue Korrekturakte mit diesem tatsächlichen Originalprompt an.
Berichte je Finding Repro, Änderung und neuen Nachweis; liefere exakten
Kandidatenstand, Test-/CI-Ergebnisse und ehrliche Grenzen. Vollständige
Selbstqualifikation ergibt REVIEW_READY, keinen selbst erteilten ROOT_PASS.
Die fehlenden unabhängigen Reviewnachweise erfüllt der folgende Reviewer.

Die dokumentierte workflowweite Kandidatenfreigabe gilt weiter:
Kandidaten-Commits, normale Paketbranch-Pushes und Aktualisierung desselben
PR #2 sind erlaubt. Alles bleibt kumulativ auf dem Paketbranch und geht
später gemeinsam in den einen freigegebenen AP-Aggregatcommit ein.
Kein separater Dokumentcommit auf feat/client-v2, kein Merge dorthin,
kein Eigenreview oder Folgepaketstart. Nach Abgabe Schreibrecht für
die frische unabhängige Abnahme zurückgeben. Server-/Main-Promotion,
Tags, Releases, Force-Push und Cleanup sind nicht beauftragt.
```
