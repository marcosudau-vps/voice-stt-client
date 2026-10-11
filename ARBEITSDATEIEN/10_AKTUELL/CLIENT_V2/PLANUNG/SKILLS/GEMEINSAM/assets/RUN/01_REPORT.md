# {{AP_ID}} / {{RUN_ID}} – {{ROLLE}}report

Vorlage, noch kein Ausführungs-/Abnahmenachweis. Rollenabschnitte nur soweit zutreffend ausfüllen.

## 1. Auftrag und Identität

Original-Prompt: {{PFAD}}. Scope: {{ZIEL_UND_ABGRENZUNG}}. Planstand: {{VERSION_DATEIHASHES}}. Tatsächliche Gitfreigabe: {{RECHTE_ODER_KEINE}}.

Repo/Checkout: {{WERTE}}; Paketbranch/PR: {{WERTE}}; canonical_parent: {{SHA}}; server_sha: {{SHA}}; Start-SHA/Tree: {{WERTE}}. Geprüfter/eingereichter Kandidat: {{SHA/TREE_ODER_GENAUER_DIFF_MIT_BASIS}}. Fremde WIP/Schutz: {{WERTE}}.

Vorgängercheck: {{PASS_REPORT, MENSCHLICHE_FREIGABE, KANONISCHER_AGGREGATECOMMIT/PR_ODER_AP000_PLANUNGSSTART}}. Aktuelles Schreibrecht: {{UMSETZER_ODER_REVIEWER}}.

## 2. Ergebnis und Entscheidungen

Status/Verdict: {{REVIEW_READY / CHANGES_REQUIRED / ROOT_PASS / BLOCKED}}.
{{KONKRETES_ERGEBNIS, BETROFFENE_DATEIEN, BEGRUENDETE_LOKALE_ENTSCHEIDUNGEN}}

Tatsächliche Interfaces/Guards und Übergabe an Folgepaket: {{NUR_RELEVANTE_STELLEN}}. Fachliche Vertrags-/Zieländerungen mit ausdrücklicher Entscheidungsreferenz; interne Vorschläge mit Begründung.

## 3. Requirements und Prüfungen

| Requirement / DoD | Tatsächliche Methode / manueller Fall | Beleg / Runtime / Befehl | Ergebnis |
| --- | --- | --- | --- |
| {{ID}} | {{METHODE_ODER_FALL}} | {{EVIDENZLINK}} | {{PASS / FAIL / NOT_RUN / NOT_PROVEN / SKIPPED_EXPECTED}} |

Regressions-/Build-/Crossrepoübersicht: {{BEFEHLE, RUNTIME, TESTANZAHL, SKIPS, ZEIT, SHA_PAAR}}. Evidenzindex: {{PFAD}}. Ein Nachweis darf mehrere Requirements abdecken.

## 4. Findings / Korrekturzuordnung

| Finding / Schwere | Wirkung / Repro / expected-actual | Requirement | Owner / geforderter Nachweis / Korrekturbeleg |
| --- | --- | --- | --- | --- |
| {{ID_ODER_KEINE}} | {{INHALT}} | {{IDs}} | {{WERTE}} |

Korrekturrun verweist auf ursprüngliche Finding-IDs und neue Belege; abgeschlossene Reviewreports unverändert erhalten.

## 5. Unabhängiges Review – nur ABNAHME

reviewed_sha: {{EINGEREICHTER_SHA_VOR_REVIEWDOCS_COMMIT}};
reviewed_tree: {{TREE}};
canonical_parent: {{SHA}};
server_sha: {{SHA}}.

Eigene Prüfungen: {{BEFEHLE_BELEGE}}. Kriterienvollständigkeit: {{ERGEBNIS}}.
Technisches Verdict/Begründung: {{ROOT_PASS / CHANGES_REQUIRED / BLOCKED}}.
Zulässige Reviewunterlagen: {{NEUE_RUNAKTE_UND_ADMINISTRATIVE_VERWEISE}}.

Eigene spätere Docs-Commit-ID aus Git in der Übergabe nennen; sie ist nicht automatisch ein erneut geprüfter Produkt-SHA. ROOT_PASS erlaubt keinen Merge.

## 6. Menschliche Übernahme – nur bei erteiltem Prompt

Freigabeoriginal: {{PFAD}}; PR-Head bei Freigabe: {{SHA}}; canonical_parent: {{SHA}}; unabhängiger PASS: {{REPORT_SHA_TREE}}. Erlaubter administrativer Nachtrag: {{DIFF_ODER_KEINER}}. Erforderliche CI: {{PR_HEAD_ODER_TESTMERGE_SHA_BASE_UND_ERGEBNIS}}.

Vor Merge tatsächlichen Status ROOT_PASS erhalten. Danach Aggregate-SHA/Parent/Tree, Mergestatus und Baumabgleich aus Git/PR ermitteln und dem Auftraggeber melden. Dieser Nachmerge-Beleg wird mit dem nächsten Paket gesichert; kein zweiter Vorgängercommit. Alte Verdicts nicht umschreiben.

## 7. Übergabe

{{PR_URL, TATSAECHLICHER_KANDIDAT_SHA, REVIEWREPORT/FINDINGS, DOCS_COMMIT_ODER_AGGREGATE_AUS_GIT, NAECHSTE_AKTION, OFFENE_GRENZEN}}.
Steuerungslog-Meilenstein: {{ID_ODER_BEI_NOCH_OFFENEM_RUN_AUSSTEHEND}}.

## Automatische Wiedereinstiegsermittlung

Ermittelte Aktion/Quelle des Kurzauftrags: {{ZUSTAND_AP_KANDIDAT_ROLLE}}.
Workflowphase vor/nach dem Run: {{WERTE}}; Statusdatei: {{PFAD}}; unmittelbar nächste erlaubte Aktion: {{AKTION}}.
Arbeitsfreigabe und menschliche Übernahmefreigabe getrennt referenzieren. Kein eigener finaler Commit-SHA in derselben Commitdatei.

## Nur bei einem tatsächlichen Sonderfall

{{UEBERGABE_ODER_AUSWAHLENTSCHEIDUNG_GESICHERTER_AUSGANG_UND_REFERENZ_ODER_ENTFALLEN}}.
{{SERVER_FIX_QUELLAKTE_NEUES_PAAR_UND_RUECKKEHR_ODER_ENTFALLEN}}.
Eigene Plattformdurchführung: {{BELEGE_ODER_KEINE}}; extern durchgeführt/selbst validiert: {{FALL_TESTER_IDENTITAET_PRUEFENTSCHEIDUNG_ODER_KEINE}}.
Letzter Nachmerge-Abschluss separat im NACH_ABSCHLUSS-Beleg sichern; abgeschlossenen Report erhalten.
