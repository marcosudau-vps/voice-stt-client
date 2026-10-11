# Paketakten, Original-Prompts und Vorlagen

Stand: 2026-10-11, Strukturversion 1, Rollenworkflow Revision 9. Gilt einheitlich für Client-, Integrations- und konkrete Serverfixpakete. Die folgenden Ablagen sind Arbeitsakten außerhalb dieses Planordners. Planung und Paketakten werden gemeinsam im jeweiligen Paketbranch versioniert und mit dem Paketaggregat übernommen. Hier werden ausschließlich Vorgaben und kopierbare Vorlagen bereitgestellt; noch keine Implementierungs- oder Abnahmeakte wird als ausgeführt angelegt.

## 1. Verzeichnisstruktur

Basis im aktiven Clientcheckout: `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/`. Damit bleibt die zentrale Zuordnung „Planung unter 20, Ausführung unter 30“ erhalten. Die Evidenz eines Runs liegt direkt in seiner Akte; keine zweite Belegkopie unter `40_EVIDENCE` anlegen. Ein dort benötigter zentraler Index verweist lediglich auf das Original.

```text
30_AUSFUEHRUNG/
└── AP-CV2-030/                 # ebenso AP-IV2-010 oder AP-SV2-FIX-001
    ├── 00_PAKET.md             # Ziel, Planstand, Status, Run-/Review-/Übernahmeverweise
    ├── 01_ENTSCHEIDUNGEN.md    # nur wenn dauerhafte/paketübergreifende Entscheidungen entstehen
    └── RUNS/
        ├── R01-UMSETZUNG/
        │   ├── 00_PROMPT_ORIGINAL.md
        │   ├── 01_REPORT.md
        │   ├── ZUSATZPROMPTS/  # nur bei weiterer Steuerung; 001_....md, 002_....md
        │   └── EVIDENCE/
        │       ├── INDEX.md
        │       ├── tests.txt
        │       └── ...        # Wiretraces, Diff-/Build-/Migrationsbelege nach Bedarf
        ├── R02-ABNAHME/
        │   ├── 00_PROMPT_ORIGINAL.md
        │   ├── 01_REPORT.md    # unabhängiger Review, Findings, Verdict, Kandidatenidentität
        │   └── EVIDENCE/
        │       ├── INDEX.md
        │       └── ...
        └── R03-KORREKTUR/     # ausschließlich bei tatsächlichem Befund
            └── ...           # gleiche minimale Runstruktur
```

Runnummern sind pro Paket fortlaufend und stellen keine erwartete Laufzahl dar. Nach Korrektur folgt eine frische Abnahmesession mit neuer Nummer. Für mehrere getrennte FIX-Instanzen werden getrennte Paketordner angelegt. Ordner/Dokumente entstehen erst, wenn ihr Inhalt benötigt wird; keine leeren Korrektur-, Analyse-, Build- oder Freigabeordner vorproduzieren.

## 2. Vier Pflichtartefakte je tatsächlich ausgeführtem Run

1. **Paketindex `00_PAKET.md`**, einmal pro Paket: genaue Auftragseinheit, Referenz auf diese eigenständige Planung, relevante Planversion/Dateihashes, kanonischer Parent, Paketbranch/PR-URL, Kandidaten-/Reviewidentitäten, aktueller Status und Links auf alle Runs. Status ist eine Übersicht; der verlinkte unabhängige Reviewreport ist die Quelle des Verdicts.
2. **`00_PROMPT_ORIGINAL.md`**, je Run: der tatsächlich erteilte Auftrag im Originalwortlaut, getrennt von Herkunftsmetadaten wie Datum, Rolle und verwendeter Vorlagenversion. Nachträgliche Steuerung unter `ZUSATZPROMPTS` chronologisch und unverändert sichern. Ein ausgefüllter, noch nicht versandter Entwurf ist kein Original-Prompt.
3. **`01_REPORT.md`**, je Run: Auftrag/Scope, Start-/Endzustand, Ergebnis, relevante Entscheidungen, Requirements mit konkreten Testmethoden/Beleglinks, Testübersicht, offene Punkte und Übergabe. Beim Review enthält derselbe Report das unabhängige Verdict und Findings; kein zusätzliches ABNAHME-Dokument mit doppeltem Inhalt.
4. **`EVIDENCE/INDEX.md`**, je Run: Belegliste mit Zweck, erzeugendem Befehl/Test, Bezug auf SHA/Tree oder Workingtreediff, Runtime/Konfiguration und Ergebnis. Build-/Binär-/externe Belege mit SHA256; reine Textbelege benötigen keine separate Hashdatei, wenn ihr geprüfter Gitstand eindeutig ist.

Original-Prompt und Report dürfen auf die vorliegende eigenständige Planung verweisen. Sie müssen keine Kopie aller Kontrakte enthalten. Ist die Planung während des Runs veränderlich, sichern relevante Dateihashes und bei fachlichem Änderungsbedarf ein kleiner Ausgangssnapshot den Auftrag; kein vollständiges Quellenarchiv pro Run.

Ein Original-Prompt enthält keine tatsächlichen Secrets oder Nutzeraudiodaten. Sollte ein Auftrag solche Daten enthalten, wird ausschließlich eine als redigiert gekennzeichnete Kopie abgelegt; keine fälschliche Behauptung bytegleicher Originaltreue. Bestehende externe, vertrauliche Belege bekommen einen zulässigen Pfad/Identitätsnachweis im Index.

## 3. Übernahmefreigabe und Abschluss

Nach unabhängigem PASS bleibt das Paket `ROOT_PASS`, bis der Auftraggeber die kanonische Übernahme per ausdrücklichem Prompt erlaubt. Dieser Prompt wird als Original gesichert: bei noch offener Abnahme-/Abschlusssession unter deren `ZUSATZPROMPTS`, bei neuer Session als `00_PROMPT_ORIGINAL.md` eines `Rnn-UEBERNAHME`.

Die kurze Abschlussaktion sichert vor dem Merge die tatsächliche Freigabe und administrative Übernahmeverweise auf dem Paketbranch, soweit erlaubt. Vor Merge bleibt der technische Status ROOT_PASS. Nach Merge tatsächlichen Aggregate-SHA/Tree, Parent, CI-/Merge-/Transportresultat melden; der eindeutige Gitcommit und gemergte PR belegen ACCEPTED. Dieser Nachmerge-Abschluss wird mit dem nächsten Paket gesichert, ohne zweiten Commit des Vorgängers. Das technische Reviewurteil wird nicht umgeschrieben; abgeschlossene Reports erhalten. Fehlgeschlagene oder nicht autorisierte Übernahme bleibt offen.

Damit entstehen regulär zwei Sessions pro Paket. Eine dritte Session ist durch diese Ablage weder vorgeschrieben noch eine zusätzliche fachliche Umsetzung. Ein Steuerungslog-Meilenstein wird genau einmal je abgeschlossenem relevanten Run/Gate geschrieben; Fortsetzungsnachrichten innerhalb derselben noch offenen Session erzeugen nicht automatisch neue Runnummern.

## 4. Vorlagen

- [Vorlagenindex und Verwendung](../assets/README.md).
- [Gemeinsame Promptbausteine](PROMPT_BAUSTEINE.md).
- [Umsetzungsprompt](../../voice-stt-client-v2-umsetzen/assets/PROMPT_UMSETZUNG.md).
- [Unabhängiger Abnahmeprompt](../../voice-stt-client-v2-abnehmen/assets/PROMPT_ABNAHME.md).
- [Korrekturprompt](../../voice-stt-client-v2-umsetzen/assets/PROMPT_KORREKTUR.md).
- [Übernahmeprompt](../../voice-stt-client-v2-abnehmen/assets/PROMPT_UEBERNAHME.md).
- [Paketindex](../assets/PAKETAKTE/00_PAKET.md), [Entscheidungen bei Bedarf](../assets/PAKETAKTE/01_ENTSCHEIDUNGEN.md).
- [Runreport](../assets/RUN/01_REPORT.md), [Original-Prompt-Hülle](../assets/RUN/00_PROMPT_ORIGINAL.md), [Evidenzindex](../assets/RUN/EVIDENCE/INDEX.md).

Die kurzen Promptvorlagen führen zum jeweiligen Rollen-Skill, der die wiederkehrenden Regeln und Checklisten lädt. Vor Benutzung werden nur Paket, nötige Kandidaten-/Repopfade und tatsächlich erlaubte Git-Schritte eingesetzt; Baselines und Pflichtnachweise werden über die Skillverweise ermittelt. Vorlagen erteilen selbst keine Gitfreigabe; diese muss im tatsächlichen Auftrag vom Auftraggeber kommen. Platzhalter bleiben in Entwürfen zulässig, im erteilten Auftrag werden sie ausgefüllt oder ausdrücklich als offen gekennzeichnet.

## 5. Varianten und Aufwand

Clientumsetzung: Code-/Regression-/Migrationsevidenz. Integration: tatsächliches SHA-Paar, Prozess-/Wirebelege. Reale Abnahme: Hardware-/Modell-/Buildkonfiguration und manuelle Nachweise. Serverfix: reproduzierter Defekt und neue Serverbaseline. Die Verzeichnisstruktur bleibt gleich; die Belegarten richten sich nach dem Paket.

Es gibt keinen Pflichtsatz von Unterordnern für jede Testart und keine mehrfachen Listen identischer Prüfresultate. Bereits gesicherte Belege verlinken, unveränderte Grundlagen übernehmen, neue Nachweise für tatsächliche Änderungen erzeugen. Ergänzende Analysen, Traces oder große Builds sind erlaubt, wenn sie den Review erleichtern.

## 6. Reviewakte auf dem Paketbranch

Reviewer sichert seine neue Abnahmeakte im ausdrücklich erlaubten Scope per Docs-Commit/Push auf dem Paketbranch, während der Umsetzer pausiert. Eigener isolierter Reviewworktree; keine Produkt-/Test-/Kontraktänderungen. Im Report die tatsächlich geprüfte Kandidaten-SHA nennen, den späteren eigenen Docs-Commit in der Übergabe aus Git ableiten. Umsetzer übernimmt diese Spitze vor Korrektur. Maßgebliche Findings stehen im versionierten Report, der PR verlinkt ihn. [Schreib-/SHA-/CI-Regeln](PR_UND_REVIEW_UEBERGABE.md).

## Zustand als Pflichtübergabe

Alle Rollen pflegen die [Workflowzustände](ZUSTAENDE_UND_NAECHSTER_SCHRITT.md) im branchbezogenen WORKFLOW_STATUS.json sowie konsistente Paket-/Runverweise vor Abgabe. Neue Agenten entdecken offene Paketlinien selbst; der Auftraggeber überträgt keine SHA-/Reportlisten. Zusätzliche unabhängige Reviews erhalten jeweils einen neuen Run. Nachmerge-Status wird aus belegtem Featurecommit erkannt und im nächsten Paket gesichert.
