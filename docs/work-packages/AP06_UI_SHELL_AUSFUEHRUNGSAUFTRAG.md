# Ausführungsauftrag – AP06 Windows UI-Shell

> **Status:** technischer Erstauftrag ausgeführt; fachlicher Folgeumfang offen  
> **Stand:** 27. Juli 2026  
> **Vertrag:** `docs/work-packages/AP06_UI_SHELL.md`

> **Nummerierungsnachtrag vom 2. August 2026:** Die in diesem historischen
> Auftrag genannten „AP07-Grenzen“ sind nach der Neuplanung geteilt: AP07 ist
> das Feedback- und Eventsystem einschließlich ReSpeaker-LED; allgemeine
> Härtung und Polish folgen als AP08.

> **Nicht erneut ausführen:** Dieser Auftrag dokumentiert ausschließlich den
> abgeschlossenen technischen Erststand vom 25. Juli. Seine damaligen
> Schutzgrenzen gegen Modus- und Settingsfunktionen gelten nicht als Grenze
> des inzwischen konsolidierten AP06-Folgeumfangs. Vor weiteren
> Codeänderungen ist aus dem fortgeschriebenen Paketvertrag ein neuer, klar
> benannter Folgeauftrag abzuleiten.

## Auftrag

Setze ausschließlich AP06 vollständig um. Verwende den bestehenden
`STTController` als fachliche Grenze und implementiere PySide6-Tray, passives
Overlay, native Win32-Hotkeys, Qt-/asyncio-Brücke, Reinsertion und
Single-Instance-Lifecycle gemäß Paketvertrag.

## Pflichtreihenfolge

1. Pflichtlektüre und Originalquellen aus dem Paketvertrag lesen.
2. Vor-AP06-Gesamtsuite reproduzieren.
3. Relevante vorhandene Schnittstellen und Tests vollständig prüfen.
4. UI-Module mit Tests in kleinen Schritten implementieren.
5. Gezielte Qt-/Win32-/Threadingtests ausführen.
6. Gesamtsuite, `py_compile` und sichere Smoke-Tests ausführen.
7. Dokumentation synchronisieren.
8. AP06 abschließen und stoppen; AP07 nicht beginnen.

## Schutzgrenzen

- Keine fachliche Neuimplementierung oder vorsorgliche Refaktorierung des
  AP1–AP5-Core.
- Keine Modus-, Wake-Word-, Admin- oder Serverkonfigurationsfunktion.
- Keine Geräte-, Sleep/Wake-, Packaging- oder Autostartarbeit.
- Keine modalen Meldungsschleifen.
- Keine Realtime-Textinjektion.
- Keine produktiven Secrets oder Laufzeitdaten in Tests.

## Abgabe

Die Abgabe nennt:

- geänderte und neue Dateien,
- umgesetzte Thread- und Bediengrenzen,
- gezielte Testbefehle und Ergebnisse,
- Gesamttestzahl,
- Art und Ergebnis der Smoke-Tests,
- bewusst offene AP07-Grenzen.

## Ausführungsergebnis

Der Auftrag wurde am 25. Juli 2026 vollständig ausgeführt. Sämtliche
Scopepunkte und Abnahmekriterien des AP06-Paketvertrags sind erfüllt.
Die Gesamtsuite umfasst 238 erfolgreiche Tests; Syntaxprüfung, nativer
Win32-Ressourcentest und echter Qt-/Core-Brücken-Smoke-Test waren ebenfalls
erfolgreich. Nach der Overlay-Korrektur umfasst die Suite 239 Tests. Der
technische Erstauftrag bleibt als Beleg abgeschlossen; AP06 wurde für die
nachgeholte fachliche Scopeabstimmung wieder geöffnet. Diese Abstimmung ist
seit 27. Juli im Paketvertrag konsolidiert; die Umsetzung ist nicht Bestandteil
dieses historischen Erstauftrags. AP07 wurde nicht begonnen.

Vollständiger Nachweis:
`docs/2026-07-25_AP06_ABNAHME/ABNAHMEBERICHT.md`.
