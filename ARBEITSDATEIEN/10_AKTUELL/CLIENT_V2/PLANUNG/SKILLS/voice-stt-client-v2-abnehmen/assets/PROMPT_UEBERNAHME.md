# Menschlicher Auftrag – einen Paket-PR übernehmen

> Ich gebe die Übernahme von {{AP_ID}} ausdrücklich frei. PR {{PR_URL}}, Paketbranch {{PAKETBRANCH}}, aktuelle PR-Spitze bei dieser Freigabe {{PR_HEAD_SHA}}, kanonischer Parent {{CANONICAL_PARENT}} auf feat/client-v2. Unabhängiger ROOT_PASS: Report {{REPORTPFAD}}, reviewed_sha/tree {{REVIEWED_SHA_UND_TREE}}.
>
> Lies den Übernahmeablauf unter {{UEBERNAHME_MD_PFAD}}. Erlaubt sind das Sichern dieses tatsächlich erteilten Prompts und nötiger rein administrativer Abschlussverweise in der Paketakte durch einen normalen Paketbranch-Commit/Push sowie anschließend genau ein Squash-Merge dieses PRs nach feat/client-v2. Prüfe den administrativen Nachtrag, finalen Head, unveränderten Parent, erforderliche CI und Baumgleichheit. Keine neuen Produkt-/Test-/Kontraktänderungen und keine Kriterienänderung aus diesem Auftrag.
>
> Melde den tatsächlichen Aggregate-SHA/Parent/Tree, Merge-/Prüfergebnis und nächste Paket-ID. Kein Main-/Serverfeature-Merge, Auto-Merge, Rebase, Tag, Release oder Cleanup.

Diese Vorlage wird vorzugsweise an den ausführenden Agenten gegeben. Rechte gelten erst durch den tatsächlich erteilten menschlichen Prompt. Der benannte PR-Head darf danach ausschließlich um den ausdrücklich erlaubten Freigabe-/Abschlussnachtrag fortschreiten. Andere Änderungen benötigen eine neue passende Prüfung/Freigabe. Wenn konkrete CI-Vorgaben nicht aus dem Paket hervorgehen, ergänzen.

[Übernahmeablauf](../references/UEBERNAHME.md). Für ausdrücklich gewünschte lokale Aggregation den Gitabsatz konkret ersetzen; nicht zugleich lokal übernehmen und den PR erneut squash-mergen.
