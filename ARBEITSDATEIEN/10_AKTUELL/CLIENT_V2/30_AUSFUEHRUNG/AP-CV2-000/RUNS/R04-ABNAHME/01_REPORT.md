# AP-CV2-000 / R04-ABNAHME – unabhängige fachliche Folgesichtung

**Datum:** 2026-10-11 (Europe/Berlin). **Verdict: BLOCKED (fehlender unabhängiger Windows-Prüflauf), keine neuen Produktfindings.** Das frühere Finding `CV2-R02-F01` ist nach unabhängiger Quellcodeprüfung **fachlich geschlossen** und durch vorhandene grüne Windows-CI-/Selbsttests gestützt. Kein `ROOT_PASS`, da kein vom Reviewer selbst ausgeführter oder veranlasster vollständiger Windows-Prüflauf vorliegt.

## Auftrag, Scope und Identitäten

[Originalwortlaut](00_PROMPT_ORIGINAL.md) – Auftraggeber ordnete an, Arbeitsunterlagen/Workflow-Dateien und ihre Korrekturen **nicht inhaltlich zu bewerten**, sondern als gegeben hinzunehmen. Prüfung beschränkt sich deshalb auf Produktcode, betroffene Produkt-Regressionstests, Gitprovenienz und Nachweise; rein administrative Statusaktualisierung ist kein Urteil über diese Unterlagen.

- Repo/PR: [marcosudau-vps/voice-stt-client #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2); Base `feat/client-v2`, Head `work/client-v2/ap-cv2-000`.
- **reviewed_sha** `cd872d4bfa8eccd0167337cbab16a572ca70bfd4`; **reviewed_tree** `6aff2fa629b0c01fde502c345e7e31035cee0926`; **canonical_parent** `050e776cf316eb332177294db0c0a2719c2b4415`.
- **server_sha** `ada13b011e1d3829f78e7f389e3b927795a2b3be` auf Server-Distributed, unverändert.
- R02 vor Korrektur: `8b1c4c157b6b431dac6af69e2e264d0c37579bef`, F01; R03 Code-/Test-Korrektur: `210c2ae14355d22e9b25172cf47a1bcf94860300`; final eingereichter Kandidat `cd872d4bfa8eccd0167337cbab16a572ca70bfd4` fügt Akten-/Bereitstellungsnachtrag hinzu.
- Gesamtkandidat PR #2: die bestehende integrierte Clientbasis im Namespace `voice_stt_client` plus R03-Korrektur. Bestehender V1-Transport bleibt; keine V2-Kompatibilität und kein reales Gesamt-Hardwaregate beansprucht. Vollständige Quell-/Testinventare stammen aus R01/R03, wurden vom Reviewer nicht auf einem vollständigen isolierten Checkout automatisch neu verglichen.

## Ergebnis: CV2-R02-F01 geschlossen

**Requirement:** BASE-05 / BASE-08 (Bestand der Benutzerpräferenzen, Hotkey-/Konfigurationsintegration).

Im zuvor beanstandeten Ablauf schrieb `_register_startup_hotkeys` das Ersatzhotkeyprofil **vor** `bridge.start()`. Im korrigierten `voice_stt_client/ui/application.py` setzt der Registrierungshelfer nur `self._startup_hotkey_suggestion`. Erst nach erfolgreichem `bridge.start()` erfolgt `self.config.save_user()`. Bei negativem Corestart und beim Speichern-Fehler werden provisorische Hotkeys abgemeldet und ursprüngliches Hotkey-Objekt/Manager wiederhergestellt; bei Speicherfehler stoppt der bereits gestartete Core. Bei deaktivierten bzw. Wake-only-Hotkeys entstehen keine Ersatzregistrierungen. Die fünf neuen `StartupPersistence`-Methoden prüfen Dateiinhalt, Ursprungsbindung, Registrierungszustand, erfolgreiche Persistenz, Wiederholungsstart und Fehlerrollback. Fachliche Abdeckung gegen R02-Expected ist schlüssig. 

**Bewertung F01:** `CLOSED_STATIC_RECHECK_WITH_EXTERNAL_CI`. Diese Aussage ist eine echte unabhängige statische Prüfung plus Auswertung des Windows-CI-Laufs; sie ist **kein** behaupteter eigener Win32-/Qt-Testlauf. Keine weiteren konkreten Produktfehler im gezielten R03-Änderungsdiff entdeckt.

## Test-/Nachweisstand

| Prüfung | Status | Beleg/Grenze |
| --- | --- | --- |
| Git-Parent/Head/Tree & PR-Testmerge | PASS | [Evidenz](EVIDENCE/INDEX.md) |
| R03-Codekorrektur F01 (statischer Kontrollfluss) | PASS | aktueller Quellcode, Änderung von R02 zu R03 |
| Neue fünf Regressionstests (Test-Assertions/Negativfälle) | PASS als Review der Testfälle | Reviewer hat Methoden gelesen; Ausführung nur fremd belegt |
| Bestehende [Windows-CI #38163179818](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38163179818) | PASS – **fremde Durchführung unabhängig verifiziert** | 1233 Tests, Windows-EXE, Qt, compileall, Packaging/Installsmokes; Testmerge-Tree stimmt mit Kandidat überein |
| Vorher-Fail-Nachher-Pass | PASS – fremder R03-Reprobeleg gesichtet | R03-Repro-Log vor Fix 4 FAIL; finaler gezielter Test 12 PASS |
| Reviewer-eigene volle Windows-Regression | **NOT_RUN** | Kein Windows-Checkout/Projektvenv im zugänglichen Reviewer-Rechner; keine eigene oder veranlasste passende Durchführung |
| Physische Windows-/ASR-/LED-/Clipboard-/V2-Server-E2E | SKIPPED_EXPECTED | laut AP000-Paketgrenze späteren Paketen zugeordnet |
| Änderungen an Arbeitsunterlagen/Workflow-Dateien | **NICHT BEWERTET auf Auftraggeberwunsch** | Als vorgegeben übernommen, keine fachliche Freigabe dieser Änderungen erteilt |

## BASE-Anforderungen (fachliche Abgrenzung)

BASE-01/06/07/10: Remote-Provenienz der Branches und SHA-/Tree-Paare nachvollzogen; keine kanonische Übernahme. BASE-02/03/04/09/12: vollständige Trigger-/Feedback-/Produktregression und Packaging durch R01/R03 sowie aktuelle CI umfangreich belegt, aber ohne eigene komplette Ausführung **NOT_PROVEN als unabhängige Gesamtqualifikation**. BASE-05/08: konkretes R02-Finding durch Quellcode-/Assertion-Recheck fachlich geschlossen. BASE-11: Reviewer-Folgesichtung/Report vorhanden, unabhängige Volltestvoraussetzung jedoch offen. Keine Requirementkriterien umdefiniert und keine Pflicht-Skips zu PASS umgedeutet.

## Fehlende Voraussetzung und nächste Aktion

**BLOCKER R04-T01 (kein neuer Produktfinding):** Für `ROOT_PASS` fehlt der in der Abnahmecheckliste verlangte unabhängig ausgeführte oder vom Reviewer veranlasste **vollständige Windows-Clientsuite** auf exakt `cd872d4bfa8eccd0167337cbab16a572ca70bfd4`, aus isoliertem Checkout mit Python 3.12.10-Projektvenv und vollständigem Log einschließlich kritischer R02-F01-Tests. Eine grüne, vom Umsetzer bereits ausgelöste CI wird als Drittbeleg akzeptiert, aber nicht als eigene Ausführung umetikettiert. Dieser Reviewzugriff erlaubt GitHub-Dateien/CI-Protokolle, jedoch keinen Windows-Ausführungshost; lokaler Container ist Linux/Python 3.13.5 und hat keinen GitHub-Netzzugang. 

**Owner der nächsten Aktion:** Auftraggeber bzw. verfügbarer Windows-Prüfhost/Revieweragent mit tatsächlicher Ausführungsfähigkeit. Der Testweg muss von einem unabhängigen Reviewer angefordert/ausgeführt und mit tatsächlichem Client-SHA, Runtime und vollständigem Befehlslog belegt werden, vorzugsweise `.\\venv\\Scripts\\python.exe -m unittest discover -s tests -v` plus `.\\venv\\Scripts\\python.exe -m unittest tests.test_startup_hotkey_persistence -v`. Danach kann die technische ROOT-Abnahme anhand der eigenen vollständigen Belege erfolgen; kein Produktkorrekturauftrag aus F01 nötig, solange kein neuer Fehler auftritt. Ein separater menschlicher Übernahmeprompt bleibt erforderlich.

**Übergabestatus:** `BLOCKED`; offene Produkt-Finding-IDs `[]`, technischer Nachweisblocker `R04-T01`. Kein Merge, kein AP-CV2-010 und keine Änderungen an Produkt-, Test-, Workflow-, Vertragsspezifikationsdateien.

[Evidenzindex](EVIDENCE/INDEX.md) enthält die genaue Herkunft aller geprüften Belege.
