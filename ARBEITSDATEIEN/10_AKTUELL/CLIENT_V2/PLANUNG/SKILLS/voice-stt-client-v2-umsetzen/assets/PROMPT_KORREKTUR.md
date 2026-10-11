# Auftragsschablone – Korrektur im selben PR

> Lies den Umsetzungsskill unter {{SKILL_MD_PFAD}} einschließlich Korrekturablauf und korrigiere {{AP_ID}} anhand von {{REVIEWREPORT_UND_FINDING_IDS}} im Paket-PR {{PR_URL}}. Repo/Checkout: {{REPOPFAD}}, Paketbranch {{PAKETBRANCH}}. Aktuelle Spitze mit Reviewunterlagen: {{REVIEW_DOCS_HEAD}}.
>
> Übernimm zunächst die Reviewunterlagen per Fetch/Fast-forward; sichere eine neue Korrekturakte. Erlaubt sind lokale Kandidaten-Commits, normale Pushes auf genau diesen Paketbranch und Aktualisierung dieses PRs/Übergabekommentare. Kein Force-Push, keine kanonische Übernahme.
>
> Behebe die beauftragten Findings samt nötigen Anschlussstellen, führe Repros und vollständige betroffene Regression aus, aktualisiere Traceability/Planpflege. Liefere einen neuen kumulativen REVIEW_READY-Kandidaten mit SHA und Belegen und pausiere wieder für den unabhängigen Review.

Vorlage, erst der erteilte menschliche Prompt ist Gitfreigabe. Bei rein lokalem Auftrag Rechte entsprechend ersetzen. Lesepfad: [Umsetzungsskill](../SKILL.md).
