# {{AP_ID}} – Paketakte

Vorlage, noch kein ausgeführtes Paket.

- Paket/Ziel: {{AP_ID, PAKETDATEI, KURZES_ZIEL}}
- Planstand: {{PLANPFAD, VERSION/DATUM, RELEVANTE_DATEIHASHES_ODER_PLANCOMMIT}}
- Repository/Paketbranch: {{WERTE}}; Paket-PR: {{URL_ODER_LOKALE_BEREITSTELLUNG}}
- Kanonisches Ziel: feat/client-v2; canonical_parent: {{SHA}}
- Referenzserver: {{SHA}}; Clientstart: {{SHA_ODER_NOCH_OFFEN}}
- Eingereichter Kandidat: {{SHA/TREE}}; aktuelle Branchspitze: {{AUS_GIT_ERMITTELBAR}}
- Technischer Status: {{PLANNED / IN_PROGRESS / REVIEW_READY / CHANGES_REQUIRED / ROOT_PASS / BLOCKED}}
- Maßgeblicher unabhängiger Review: {{REPORTLINK}}; reviewed_sha/tree: {{WERTE}}
- Tatsächlicher menschlicher Übernahmeprompt: {{LINK_ODER_NOCH_NICHT_ERTEILT}}
- Kanonischer Abschluss: {{NOCH_OFFEN_ODER_GEMERGTER_PR_UND_EINDEUTIGER_AP_COMMIT}}

## Runs

| Run / Rolle / Datum | Original-Prompt | Report | Evidenzindex |
| --- | --- | --- | --- |
| {{RUN_ID}} | {{RELATIVER_PFAD}} | {{RELATIVER_PFAD}} | {{RELATIVER_PFAD}} |

## Offene Punkte und nächste Aktion

{{BEFUNDE_ODER_KEINE; QUELLREPORT/FINDING_IDS; KONKRETE_NAECHSTE_AKTION; AKTUELLER_SCHREIBER_UMSETZER_ODER_REVIEWER}}

Vor tatsächlichem Merge bleibt Status ROOT_PASS, auch wenn die Freigabe gesichert ist. Danach belegen gemergter PR und geprüfter eindeutiger AP-Commit ACCEPTED. Eigene Reviewunterlagen-/Aggregate-SHA erst aus Git ableiten und in der Übergabe melden; keinen Selbst-SHA oder zweiten Aufräumcommit verlangen. Der nächste Paketbranch sichert den tatsächlichen Vorgängerabschluss. Serverfix: FIX_ACCEPTED / Server-Distributed von späterer Serverfeature-Aggregation trennen.

## Workflowübergabe

Strukturierte Zustandsdatei: {{LINK_AUF_WORKFLOW_STATUS_JSON}}.
workflowPhase: {{BELEGTER_ZUSTAND}}; nächste Aktion: {{AKTION}}; tatsächliche Arbeitsfreigabe: {{ORIGINALQUELLE_ODER_KEINE}}.
Zusätzliche unabhängige Reviews als eigene Runs oben verlinken; offene Pflichtfindings aus allen gültigen Reviews berücksichtigen.

## Nur bei einem tatsächlichen Sonderfall

Kandidatenauswahl/Ablösung: {{ID_QUELLE_ALTE_UND_NEUE_LINIE_ODER_ENTFALLEN}}.
Wiederaufnahme: {{UEBERGABEAUFTRAG_VORHERIGER_OWNER_GESICHERTER_STAND_NEUER_RUN_ODER_ENTFALLEN}}.
Server-FIX/Rückkehr: {{REPOSITORY_FIX_STATUSPFAD_GEHALTENER_CLIENT_NEUE_SERVER_SHA_ODER_ENTFALLEN}}.
Letzter Nachmerge-Nachweis: {{NACH_ABSCHLUSS_PFAD_ODER_ENTFALLEN}}.

Diese Angaben nur bei Bedarf führen; keine leeren Runordner/zusätzlichen Pflichtsessions anlegen.
