# Konkrete Reviewkorrektur

Nur bei menschlichem Korrekturauftrag lesen; Umsetzungsskill und Abgabecheckliste gelten weiter.

1. PR, aktuelle Paketbranch-Spitze einschließlich Reviewunterlagen und beauftragte Finding-IDs prüfen. Sauberen Checkout fetch/fast-forward aktualisieren; fremde WIP schützen. Keine Korrektur auf einem alten Stand, der die Reviewakte verliert.
2. Reviewreport/Requirements lesen und eigene Rnn-KORREKTUR-Akte anlegen; bisherige Prompts und abgeschlossene Reports erhalten.
3. Befunde reproduzieren, Ursache gezielt beheben und nötige Anschlussstellen prüfen. Keine unbeauftragten Folgefeatures.
4. Je Finding Repro, Änderung und tatsächlichen neuen Nachweis verknüpfen. Gezielt und anschließend vollständige betroffene Produktregression ausführen. Betroffene Matrix-/Testzuordnungen und Übergaben aktualisieren; bisherigen PASS für fachlich veränderten Kandidaten nicht fortschreiben.
5. [Abgabecheckliste](ABGABECHECKLISTE.md) erfüllen; im erlaubten Scope kumulativ commit/push und denselben Paket-PR aktualisieren. Neuen SHA/Tree und Belege als REVIEW_READY melden, danach wieder für den Review pausieren.

Der neue unabhängige Review startet frisch und prüft das gesamte Paket mit Fokus auf Veränderungen. [SHA-/Schreibübergabe](../../GEMEINSAM/references/PR_UND_REVIEW_UEBERGABE.md). REVIEW_READY ist kein Eigen-PASS.
