# Ausführungsauftrag – AP06 Folgeumfang

> **Status:** ausgeführt; technischer Abschluss nachgewiesen  
> **Stand:** 28. Juli 2026  
> **Vertrag:** `docs/work-packages/AP06_UI_SHELL.md`  
> **Auftraggeber:** Benutzerauftrag vom 28. Juli 2026

## Auftrag

Setze den noch offenen, konsolidierten AP06-Folgeumfang vollständig um. Der
technische Erststand bleibt Grundlage und wird nicht neu implementiert.

Verbindlich einzubeziehen sind:

- Hotkey- und Wake-Word-Betrieb über den produktiven Session-Create-Contract,
- Auswertung der effektiven Handshakekonfiguration und deterministischer
  Session-Konfigurationsfehler,
- Hotkey-Diktatfenster mit serverseitiger VAD, Initial- und Follow-up-Timern,
- typisierte Konfiguration, deklarative Einstellungsmetadaten und
  benutzerspezifische atomare Persistenz,
- registrierte Aktionen und kollisionssichere globale Hotkeys,
- Einstellungsdialog mit den fünf im Paketvertrag festgelegten Tabs,
- statische Mikrofonwahl und manueller Mikrofontest,
- Verlaufspflege,
- optionales Sound- und Overlayfeedback.

## Schutzgrenzen

- Keine ReSpeaker-LED-Implementierung.
- Keine Geräte-Hot-Plug-, Sleep/Wake-, DPI-, Autostart- oder Packagingarbeit.
- Keine Admin-API, keine Admin-Keys und keine serverweiten Änderungen.
- Kein lokales VAD und keine Realtime-Textinjektion.
- Keine automatische Wiederaufnahme eines durch Reconnect unterbrochenen
  Diktats.
- Keine vorsorgliche Neuimplementierung funktionierender AP1–AP5-Komponenten.

## Pflichtablauf

1. Pflichtquellen und betroffene Module lesen.
2. 239-Test-Baseline und Syntaxprüfung reproduzieren.
3. In kleinen, einzeln getesteten Schichten implementieren.
4. Race-, Timer-, Rollback-, Reconnect- und Fehlergrenzen gezielt härten.
5. Gesamtsuite, Syntaxprüfung und sichere Qt-/Windows-Smokes ausführen.
6. Manuelle beziehungsweise echte Server-/Mikrofonprüfungen klar von
   automatisierten Prüfungen trennen.
7. `task.md`, Roadmap, Projektübersicht, Übergabe, README, Konfigurationsbeispiel
   und Paketvertrag synchronisieren.
8. Einen datierten ausführlichen Abschlussbericht mit Dateien, Tests,
   Restgrenzen und belegtem Endstand anlegen.
9. AP06 erst nach erfolgreicher Verifikation als abgeschlossen markieren und
   danach stoppen.

## Abgabe

Die Abgabe nennt:

- implementierte Bedien- und Zustandssemantik,
- neue beziehungsweise geänderte öffentliche Schnittstellen,
- alle geänderten Dateien,
- gezielte Testläufe und Gesamttestzahl,
- Ergebnisse der lokalen Smoke-Tests,
- nicht automatisierbare manuelle Restprüfungen,
- bekannte, ausdrücklich außerhalb AP06 liegende Grenzen.
