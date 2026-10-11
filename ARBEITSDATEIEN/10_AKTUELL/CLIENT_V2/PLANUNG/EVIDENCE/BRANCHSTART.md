> Historischer Nachweis der damaligen Vorbereitung. Keine aktuelle Branch-/Startanweisung. Maßgeblich sind [aktueller Prüfbericht](PRUEFBERICHT.md) und [Branchführung](../REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

# Startauftrag und Scope – 2026-10-11

Tatsächliche abschließende Nutzerpräzisierung im Originalwortlaut:

> Es soll kein eigener Planungs-Branch erstellt werden, sondern das soll gleichzeitig mit dem auch die Umsetzung umfassen. Nur der erste Commit auf diesem Branch soll dann nur die Planungsunterlagen enthalten. Von daraus können wir dann weitergehen: Paket 1 wurde abgeschlossen, da sind dann die Implementierungen von Paket 1 drin plus die aktualisierten Planungsunterlagen. Und da haben wir dann wieder für jedes Arbeitspaket quasi einen Commit mit Code + Unterlagen-Aktualisierungen. Bearbeitungen müssen auf untergeordneten Branches stattfinden damit es bei 1 Commit / Arbeitspaket garantiert werden kann

Aus dem unmittelbar vorherigen Nutzerauftrag: einen eigenen Branch herstellen und als dessen ersten Commit die vollständigen Planungsunterlagen sichern. Erteilter Scope hier: lokaler Branch und erster reiner Unterlagencommit; kein Push, kein Server-/Mainmerge und keine Paketimplementierung. Vom Agenten gewählte konkrete Ausgestaltung: `feat/client-v2`, Parent 8bab1b3, isolierter Clientworktree und `CLIENT_V2/PLANUNG` als gepflegte Quelle. Gleicher Dateibaum wie a80a6b1; frühere Vorarbeiten erhalten.

Weitere tatsächliche Nutzersteuerung: „Soweit ich das den Planunterlagen bisher entnehmen konnte, kann aber tatsächlich gegen den Server erst ganz am Ende getestet werden, oder? Oder können wir die einzelnen Arbeitspakete auf Richtigkeit und Funktionsfähigkeit testen? Das würde die Umsetzung wahrscheinlich deutlich vereinfachen, da wir nicht so ins Blinde hinein entwickeln müssten, sondern zwischendurch immer wieder Checkpoints hätten, an denen wir das messen beziehungsweise testen können.“ Die Unterlagen wurden dazu um die paketbezogenen Checkpoints ergänzt.
