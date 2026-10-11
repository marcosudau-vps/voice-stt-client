---
name: voice-stt-client-v2-naechster-schritt
description: Ermittle aus dem dokumentierten Voice-STT-Client-V2-Stand den nächsten Schritt und führe Umsetzung, Korrektur oder unabhängigen Review mit dem passenden Rollen-Skill aus; kanonische Übernahme nur nach menschlicher Freigabe.
---

# Voice-STT Client V2 – nächster Schritt

Gemeinsamer Einstieg für „Mach den nächsten Schritt“. Der Auftraggeber muss keine Paket-ID, Rolle, Kandidaten-SHA oder Berichtsliste zusammensuchen. Ermittle diese Werte selbst aus dem aktuellen Repository, Paketbranches/PRs und versionierten Arbeitsakten. Repo/Arbeitsblock muss erreichbar sein; die große Planung ist keine pauschale Pflichtlektüre.

1. Lies [Zustände, Erkennung und Pflege](../GEMEINSAM/references/ZUSTAENDE_UND_NAECHSTER_SCHRITT.md), gültige AGENTS und aktuelle Steuerungseinstiege. Prüfe Git-Iststand und offene Paketlinien; nicht nur den lokalen Checkout oder letzten Logeintrag betrachten.
2. Ermittle genau eine nächste Aktion. Eine ausdrückliche menschliche Anweisung wie „noch ein unabhängiges Review“ hat Vorrang. Prüfe Quellen und Voraussetzungen; Statusfelder erteilen keine Gitrechte.
3. Melde kurz: erkannter Zustand, AP-ID, Kandidat/Branch und gewählte Rolle. Danach die Aktion vollständig ausführen, ohne nur einen Plan zurückzugeben.
4. Umsetzung/Korrektur: [Umsetzungsskill](../voice-stt-client-v2-umsetzen/SKILL.md). Unabhängiger Review, auch Zweitreview: [Abnahmeskill](../voice-stt-client-v2-abnehmen/SKILL.md). Menschlich freigegebener Abschluss: [Übernahmeablauf](../voice-stt-client-v2-abnehmen/references/UEBERNAHME.md).
5. Vor Abgabe den neuen Zustand, Referenzen, Belege und nächste Aktion nach der Zustandsreferenz sichern. Innerhalb eines Auftrags genau die ermittelte fachliche Aktion ausführen; nicht anschließend die eigene Umsetzung prüfen oder automatisch das Folgepaket beginnen.

ROOT_PASS ohne menschliche Freigabe bedeutet Warten. Mehrdeutiger/unbelegter Stand oder aktive fremde Bearbeitung bedeutet konkrete Lücke melden, keine Rolle erraten. Eine unabhängige Abnahme darf deine eigene Vorarbeit nicht prüfen; dann ist eine frische unabhängige Session erforderlich.

Kurzauftrag: [Vorlage](assets/PROMPT_NAECHSTER_SCHRITT.md). Die aktuellen Unterlagen sind Bestandteil der veröffentlichten Startbasis. Beim ersten Umsetzungsauftrag tatsächlich erlaubte Kandidaten-Gitrechte und deren Quelle sichern; [Startvorlage](assets/PROMPT_ERSTER_UMSETZUNGSAUFTRAG.md). Danach werden Rechte aus der gesicherten menschlichen Arbeitsfreigabe übernommen, statt bei jedem Run erneut abgefragt. Main, Tags, Releases und Cleanup bleiben gesonderte Aufträge.
