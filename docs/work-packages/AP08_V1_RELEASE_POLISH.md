# AP08 – V1 Release-Polish

> Status: in Arbeit
> Stand: 2026-09-23
> Zuständig für: eng begrenzte Benutzer-, Pfad-, Hotkey-, Dokumentations- und Releasekorrekturen vor Client 1.0.0

## Ziel

Den bereits real gegen VoiceSTT Server 1.0.0 geprüften Windows-Client ohne
Umbau seines Audio-, WebSocket-, Event-, LED- oder Textinjektions-Cores für das
gemeinsame erste Release fertigstellen.

## Umfang

- Hotkeys im Einstellungsdialog über eine einzelne gedrückte
  Tastenkombination erfassen statt als freien String.
- Benutzerdaten standardmäßig unter `~/.voice-stt/client/` ablegen und die
  bestehende `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` weiterhin lesen,
  damit vorhandene Einstellungen nicht verloren gehen.
- einen expliziten Config-Pfad über CLI beziehungsweise Environment erlauben.
- eine reine Anwenderanleitung und eine vollständige Konfigurationsreferenz
  ergänzen.
- den bestehenden Windows-EXE-/GitHub-Releasepfad für Client 1.0.0
  vervollständigen und den noch fehlenden PyPI-Paketpfad vorbereiten.
- Release-Metadaten um den Quellcommit und den gemeinsam getesteten
  Server-1.0.0-Stand ergänzen.

## Zwischenstand 2026-09-23

Hotkey-Aufnahme, Benutzerpfade, Legacy-Fallback, Config-Override,
Anwenderhandbuch und Feldreferenz sind umgesetzt. Client `1.0.0` ist als
gemeinsamer Gegenpart zu Server `1.0.0` gesetzt. Die generischen
Top-Level-Pakete `core` und `ui` wurden in `voice_stt_client` migriert.
Wheel und sdist wurden gebaut und geprüft; die vollständige Clienttestsuite
und der neue Windows-EXE-Build sind grün. Offen bleibt der manuelle
Bedien-Smoke der neuen EXE vor dem Einfrieren des Release-Candidates.

## Technischer Nachweis

- 1132 Clienttests und `compileall` erfolgreich;
- Windows-Onefile-EXE 1.0.0 gebaut und per `--version` geprüft;
- lokales Artefakt `dist/voice-stt-client.exe`, SHA-256
  `aa8952085e5be785f324499627a8d008bdc2d05c265cd5b6b35643f55aeb0fb1`;
- Wheel/sdist: `twine check`, isolierte Installation, eindeutiger Namespace,
  Metadaten und Paketressourcen geprüft; Hashes im gemeinsamen
  `ARTIFACTS.md`;
- WebSocket-Smokes gegen den isolierten lokalen Kroko-Pro-Server und den per
  VPS-Loopback erreichbaren isolierten Kroko-Pro-Server jeweils mit `hello`,
  `ready`, echtem Pro-16-Modell und gültiger Pro-Lizenz erfolgreich. Der
  lokale Stack meldete außerdem die ursprünglich fünf eingebauten
  Wakeword-IDs; eine echte Audiodatei wurde auf beiden Systemen erfolgreich
  transkribiert. Später vom Nutzer ergänzte Wakewords wurden nicht erneut
  qualifiziert.

## Nicht-Ziele

- keine Änderung am Serverprotokoll;
- kein Refactoring des headless Core;
- keine noch nicht konkret benannten UI-Entfernungen;
- keine Änderung fachlicher Timings ohne vom Benutzer festgelegte Werte;
- kein Push, Tag oder Release ohne ausdrückliche Freigabe.

## Abnahme

- gezielte Config-, Hotkey-, Dialog-, Build- und Packagingtests;
- vollständige Clienttestsuite und `compileall`;
- frischer Windows-Onefile-Build mit `--version`-Smoke;
- manueller kurzer Bedien-Smoke der neuen Hotkey-Erfassung;
- Dokumentation, `task.md`, Roadmap und `ÜBERGABE.md` synchron.
