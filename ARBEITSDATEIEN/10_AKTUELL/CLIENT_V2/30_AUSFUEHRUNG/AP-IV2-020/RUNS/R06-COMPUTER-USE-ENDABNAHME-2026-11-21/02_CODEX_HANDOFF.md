# R06 – Übergabe an Codex / Computer Use

## Ziel und verbindliche Prüfgrenze

Die technische Vorprüfung unter [00_AUTOMATIK_VORPRUEFUNG.md](00_AUTOMATIK_VORPRUEFUNG.md) ist **PASS, aber keine vollständige Endabnahme**. Prüfe die noch offenen echten Windows-, Hardware- und UX-Fälle anhand der übergebenen 139-Punkte-Checkliste. Keine Wiederholung der gesamten 1.407 automatischen Tests ohne konkreten neuen Fehlerverdacht. Bei neuen automatisierbaren Fehlern diese trotzdem gezielt reproduzieren und dokumentieren.

## Konkrete Pfade

| Zweck | Absoluter Pfad |
|---|---|
| **Codex-Session starten in** | `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\v2-final-automatik-nachweise-20261121` |
| **V2-Desktop-Testpaket** | `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme` |
| V2-Startskript | `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\START-V2-Finalabnahme.cmd` |
| Geprüfte V2-Test-EXE | `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\voice-stt-client.exe` |
| Isoliertes Testprofil | `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Testprofil\config.yaml` |
| Originalnachweise | `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Nachweise` |
| R06-Arbeitsakte | `ARBEITSDATEIEN\10_AKTUELL\CLIENT_V2\30_AUSFUEHRUNG\AP-IV2-020\RUNS\R06-COMPUTER-USE-ENDABNAHME-2026-11-21` |
| Originalquellen-Checkout | `P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\v2-protokoll-abnahme-20261121` |
| Lokale isolierte Buildumgebung | `P:\GithubRepos\marcosudau-vps\voice-stt-client\build-output\v2-protokoll-abnahme-20261121` |

**Zielserver:** `wss://final.v2.voice-stt-server.marcosudau.com/ws/v2`, erwarteter Server-Commit `e95858e3c010a7e9324b49bb44fee349abe7128a`.

**Wichtige Unterscheidung:** Der getestete Client-/EXE-Produktcommit lautet `9f9fdf2b19f99a6d4f255d76b6cfa9ef3de493b2`. **Der Dokumentations-Commit auf dem Codex-Worktree ist ein anderer SHA**, den Codex via `git rev-parse HEAD` ermitteln muss. Eine aktualisierte Dokumentationsakte erzeugt keinen neuen getesteten Build.

## Vor dem ersten GUI-Test

1. `AGENTS.md`, `.agents/skills/arbeitsstruktur/SKILL.md`, die R06-Akte, `ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md` und die Qualifikationsregeln `PLANUNG/REFERENZ/QUALIFIKATION/WINDOWS_UND_HARDWARENACHWEISE.md` lesen.
2. Git-Head des Arbeitsverzeichnisses und eventuelle fremde Änderungen erfassen; nichts überschreiben.
3. Die EXE-SHA256 muss `28cea377ee59b2342fd9f5fd2d10a93cc6e2a8a1df950a9a1efa3af216ab65f8` sein.
4. Die V2-Testkonfiguration auf `/ws/v2` prüfen. V1-`/ws/transcribe` gilt nicht als Erfolg.
5. Den bislang laufenden alten Voice-STT-Client nur **regulär** beenden, sofern keine aktive Aufnahme oder Pasteaktion besteht. Kein hartes Beenden laufender Nutzervorgänge.
6. Die 139 Einzelfälle aus dem beigefügten Codex-Hauptprompt systematisch durchführen und pro Fall mit konkreter Evidenz dokumentieren.

## Prüfbereiche und Evidenz

1. **Normaler Windows-Desktopbetrieb:** EXE, Tray, Fenster, Overlays, Statuswechsel, Single-Instance.
2. **ReSpeaker XVF3800:** USB, reale Aufnahme, Mute, Gerätewechsel/-verlust/-rückkehr.
3. **Diktierpfade:** Aktivieren, Streaming, Finish, Cancel, Refresh, wiederholte Finaltranskripte.
4. **Wake Words:** Wake-only, manuell-only, kombiniert, Konfiguration/Recovery, Stille/Fehlauslösungen.
5. **Hotkeys:** Native globale Registrierung, Belegung, Kollisionen, Reinsert.
6. **Clipboard/History:** echte `SendInput`-Einfügung in Testeditor und zweites Testfeld, Exactly-once, Clipboard-Restoration.
7. **LED und Sound:** ReSpeaker-LED, LEFX, Helligkeit und tatsächlich hörbare Rückmeldungen.
8. **Einstellungen:** lokale Settings, V2 Session und Serververwaltung, Validierung, Persistenz, Reload/Rollback.
9. **Berechtigungen:** Admin-Guard ohne Credentials muss schützen; legitime Adminschritte nur im erlaubten Scope.
10. **Recovery/Robustheit:** Verbindungsabriss, Fehleranzeigen, Neustarts, Shutdown.
11. **Langzeittest:** mindestens 30–60 Min., zehn kurze Diktate, längere Aufnahme, CPU-/RAM- und Logkontrolle.
12. **Abschlussfreigabe:** PASS/FAIL/BLOCKIERT/N/A und GO/NO-GO je Kriterium mit Quellen.

## Nachweis- und Schreibregeln

- Hake **nur** tatsächlich ausgeführte, erfolgreiche Tests als `[x]` ab. Ein nicht beobachteter physischer LED- oder Audiotest bleibt `BLOCKIERT`/`NOT_RUN`.
- Pro Test dokumentieren: Test-ID, Zeit, Tester/Automatisierung, beobachteter Zustand, Soll/Ist, Screenshot/Log/Spur, Status und technische Limitierung.
- Keine privaten Mikrofonaudios, Transkripthistorien, Credentials, Modell-Dateien oder ausführbaren Binärdateien in Git.
- Keine Änderungen an Produktdateien, Testwerten oder alten R01–R05-Akten. Keine unautorisierten Änderungen an produktiven Servern oder globalen Windows-Einstellungen.
- **Kein Commit, Push, Merge, Release oder Serverpromotion durch Codex ohne separaten ausdrücklichen Auftrag.**
- Auch nach real bestandenen Tests ist eine unabhängige Review-/Übernahmefreigabe nach Repository-Regeln erforderlich.

## Von Codex zu erstellende Dateien (nur dieser R06-Run)

- `03_MANUELLE_CHECKLISTE.md` – 139 Checkboxen mit echten Ergebnis-/Beleg-IDs.
- `04_COMPUTER_USE_ERGEBNIS.md` – chronologisches Testprotokoll.
- `05_OFFENE_BEFUNDE.md` – priorisierte Fehler, Blockaden, Reproduktion.
- `06_GESAMTURTEIL.md` – technische Abnahme versus manuelle Prüfung sowie Freigabegates.
- `EVIDENCE/COMPUTER_USE/` – ausschließlich bereinigte, test-ID-zuordenbare Belege.

Originale Bild-/Log-/Audio-Nachweise mit privaten Details können zusätzlich unter `%USERPROFILE%\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Nachweise\computer-use-2026-11-21` gespeichert werden. Sie bleiben lokal, falls sie sensible Informationen enthalten. Die bestehende `EVIDENCE/AUTOMATIK`-Akte **nicht überschreiben**.
