## AP-IV2-020/R01 – klickbarer Teststarter, 18.10.2026

Isolierte Both-Instanz mit Logdienst erneut bereit; dauerhaftes Startfenster mit
Desktopverknüpfung **V2-Testinstanz** hinzugefügt. Start-/Doppelstart-, Profil- und
Containergrenzen sowie echter Qt-Klick gezielt geprüft (5 PASS). Erneute volle
Windows-Regression1390 PASS/0 Skips, Managerbootstrap-Retry PASS; frühere
Speicherfehlernachweise erhalten. Nur Testhilfen,
kein Produkt-/Build- oder Kalibrierwertwechsel. [Anleitung](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/human/STARTER_README.md).
Zwei separate Alexa-Fehlalarme vom17.10. um21:20 gesichert; Scores0,767/0,646,
null Sprachsegmente, akustischer Auslöser nicht bewiesen. Echte positive
Vergleichsversuche und übrige Realgates weiter offen; kein REVIEW_READY.
Overlayklarstellung: Der V2-Statuspfad blendet nicht über `fade_after: 2.0` aus;
dieser Dateiwert ist kein wirksamer V2-Anzeigedauerregler. T01-Manager real aktiv,
sichtbare menschliche Bestätigung der Logansicht weiterhin offen.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – IN_PROGRESS, UX02 technisch und real geschlossen, 16.10.2026

Produkt d95043e nach freigegebener Modifierkorrektur:1390 Windows-Tests/0 Skips,1964 Servertests/14 erwartete optionale Skips,11 Prozessfälle,17 Grenztests,7 Socketsmokes PASS. EXE/Wheel/sdist und native Produkt-/Serverlaufzeit erneut qualifiziert; reale Recovery, ReSpeaker-Desktop-Neustart und sechs Modellreplays neu gebunden. Physische Modifierprobe PASS:250ms tatsächliche Halte-/Freigabe, exakte einmalige native Ausgabe/menschlich bestätigt; UX02 CLOSED. Zusätzlich realer Manual-F8→Sprache→F9-Pfad PASS: ein erkannter Final exakt nativ eingefügt/menschlich bestätigt. Freie isolierte Both-Instanz für LED/Sound/Overlay aktiv. Genannte Einstellungstabs über zweiten lokalen Dialog vorhanden; Teststarter-Logmanagerlücke T01 festgestellt, Korrektur vorbereitet/gezielt geprüft, native Bestätigung nach abgestimmtem Neustart offen. Übrige Realgates/Kalibrierung weiter offen. Kein REVIEW_READY, gleicher R01/Paketbranch/PR15.

### Vorheriger Zwischenstand

## AP-IV2-020/R01 – BLOCKED durch UX02, 16.10.2026

[Testclient](tests/manual/v2/README.md) fertig: feste Schritte, wandernder Fokus, Countdown8s, eigener Start/Wiederholen/Abbrechen. Zehn Helferprüfungen/Qt und volle1378Windows-Regression PASS. Manuelle F8/F9-Steuerung PASS, Zieleinfügung FAIL (Shift gehalten). Produktausnahme noch nicht freigegeben; Produkt17261e6 unverändert. Derselbe R01/Branch/Draft-PR15; kein REVIEW_READY. [Aktueller Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md).

### Vorheriger datierter Zwischenstand

## AP-IV2-020/R01 – bestätigte einzelne Wake-Aufgaben, 16.10.2026

Beide direkten Nutzsätze im eigenen Editor vollständig und mit Leerzeichen, tatsächlich getrennt gestartet, Quellhashbindung an Produkt17261e6 exakt. UX01 geschlossen. F9 nicht als Finish quittiert, beide Fenster per Timeout; gezielter Manual-F8/F9-Test mit Satzvorschau/eigenem Start vorbereitet. Vollständige M-Fälle bleiben offen. Technische Qualifikation unverändert grün; keine Produktänderung.

## AP-IV2-020/R01 – autonomer neuer Stand17261e6 qualifiziert

Windows1378 ohne Skips, Server1964/14 erwartete optionale Skips,11 Prozessfälle,17 Grenzen und7/7 Smokes PASS. Neue EXE/Wheel/sdist, Frozen/Wheel-Runtime, reale ReSpeaker-Recovery, HTTP/Ack/Restart/Shutdown und native Hotkeys/Credentials PASS. UX01 wartet noch auf echte native Ausgabebestätigung mit aktivierter Einstellung. Vorbereiteter Ein-Klick-Block: native Probe und zwei kurze geführte Wake-Sätze. Alle vollständigen M-Gates und30min100 bleiben offen; kein REVIEW_READY.

## AP-IV2-020/R01 – UX01 zusätzlich freigegeben, 2026-10-15

- Bestehende Einstellung Leerzeichen anhängen im gemeinsamen Ausgabepfad umgesetzt; autoritative Texte/History unverändert.
- Fünf dauerhafte komponierte Regressionen: vorher drei rote Fehler, danach gezielte100 PASS. Volle Windows-/Build-/Paarqualifikation läuft.
- Mensch bestätigt beide Wake-Nutzsätze vollständig; technische Zielevidenz teilweise wegen Fokuswechsel. Reale Pflichtgates bleiben offen.

<!-- AP-IV2-020-PHASE-C-20261015 -->
AP-IV2-020/R01 IN_PROGRESS: reale Manual-/Followupvergleiche dokumentiert,5000ms
menschlich passend; isolierte Manual/Wake/Both-Profile gespeichert. M01-Overlap offen.
Hostcommitreserve nach echtem PowerShell-OOM durch menschliches Schließen unbenötigter
Apps wiederhergestellt (10,7GiB). Erster Wakeversuch ausgewertet; sechs echte WAVs
auf ausdrücklichen Wunsch versioniert. PreRoll320ms erhält im Modellreplay beide
direkten Nutzsätze; frische Liveprüfung mit Fokusbarriere folgt.
IV2-020-UX01: append_space=true wirkungslos, außerhalb Recoveryfreigabe; noch kein Fix.
[Belege](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md).
Kein vollständiger M-PASS oder REVIEW_READY.

# AP-IV2-020 – IN_PROGRESS, Phase C vorbereitet, 2026-10-15

Kanonischer Parent `b80ed8b` unverändert, Vorgänger AP010 tatsächlich ACCEPTED.
Paketbranch `work/client-v2/ap-iv2-020`, kumulativer Draft-PR #15, derselbe R01.
Ausdrücklich freigegebener Reconnect-/Recovery-Audit abgeschlossen: zehn technische
Findings behoben. Produktcommit `41ca761`, neue EXE/Wheel/sdist sauber gebunden.
1373 Windows-Tests ohne Skips, 11 Prozessfälle, alle sieben Server-Smokes PASS;
1964 Server-Unit-Tests PASS/14 ausgewiesene optionale Skips. Echter ReSpeaker- und
Desktop-Reconnect, HTTP-/Ackausfall, drei Neustarts, Shutdown und Frozen-GUI grün.
M-Fälle, echte Wakepositive/Nutzsprachgrenze, Wahrnehmung/Kalibrierung und30min100
bleiben NOT_RUN/NOT_PROVEN. Nächste Aktion: gemeinsamer erster Sprach-/Windowsblock.
[Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/01_REPORT.md), [gemeinsamer Testablauf](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/02_GEMEINSAMER_TESTABLAUF.md).
V1/VPS geschützt; Server nur lokal. Kein REVIEW_READY, Eigenreview, Merge oder Release.

## Vorheriger datierter Stand

# Client V2 – AP-IV2-010 / R01-UMSETZUNG / REVIEW_READY, 2026-10-14

[PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14), Branch `work/client-v2/ap-iv2-010`, Base `feat/client-v2`.
AP000 bis AP110 tatsächlich ACCEPTED; kanonischer Parent/unverändertes Clientprodukt
`43759d345b2b88354e4f3b383a4833731621d1e3`. [AP110-Nachmergeprovenienz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).
Qualifiziertes Paar `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`;
finale PR-Spitze ergänzt ausschließlich administrative Belege/Unterlagen.

Windows **1354 PASS**, schnelle Serverpytest-unit-Suite **1964 PASS / 14 SKIPPED_EXPECTED**,
**11** echte Prozessprüfungen, **17** Grenztests, **7/7** Socketsmokes,
compileall/diffcheck PASS. 28 automatisierte Szenarien geprüft, keine Produktänderung.
[Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/00_PAKET.md), [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Nächste Aktion: frischer unabhängiger Gesamtreview auf finalem PR14-Head nach grüner
finaler CI. Ab tatsächlicher Übergabe Schreiben/Pushes pausiert. Kein Eigenreview,
Merge, Serverpromotion oder AP-IV2-020-Start. Reale Modell-/Hardware-/Wahrnehmungsgates
und Server-Distributed offen. Start bleibt `venv/Scripts/python.exe -m voice_stt_client`.

<!-- IV2-010-CURRENT-END -->

## Historischer Stand vor AP-IV2-010

# Client V2 – AP-CV2-110 / R03-UEBERNAHME / READY_FOR_CANONICALIZATION, 2026-10-14

[Paket-PR #13](https://github.com/marcosudau-vps/voice-stt-client/pull/13), Base `feat/client-v2`, Head `work/client-v2/ap-cv2-110`.

Aktiver Arbeitsblock [CLIENT_V2](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/README.md);
[Einstieg Planung](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).
AP000 bis AP100 tatsächlich ACCEPTED auf feat/client-v2; letzter kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100-PASS, menschlicher R06-Auftrag und wirklicher PR12-Squash
[verifiziert](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/start-provenance.json).

AP110 auf `work/client-v2/ap-cv2-110`: ausführbare V1-Autoritäten entfernt,
Migrationreader und Utilities erhalten, Source/Wheel/sdist/Frozen mit belegter
Helloidentität und nativer Windows-GUI qualifiziert. Windows **1353 PASS**,
gezielte **234 PASS**, Servercheckpoint **17 PASS**, compileall/diffcheck und
alle Build-/Ressourcen-/Installationschecks PASS. Getesteter Produktcommit
`cf42a2a9d96c1ebc88035817a5d529dfe04e4306`; finale PR-Spitze ergänzt ausschließlich administrative Unterlagen.
[Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/01_REPORT.md), [vollständige Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Kompatibilität](docs/compatibility.md), [Runtime](docs/protocol-v2-runtime.md).

Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.
Bekannte Legacy-Profile und History werden mit Backup migriert; kein V1-Fallback.
Builds liegen lokal unter dist, kein veröffentlichter Release. Keine realen
ASR-/Mikrofon-/USB-/Fremdanwendungs-/Wahrnehmungsgates behauptet.

**Aktueller Reviewabschluss (2026-10-14):** [AP110 R02 unabhängiger ROOT_PASS](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R02-ABNAHME/01_REPORT.md) auf `44cf9a8fd1669242c00997966addc3667d448aa0`; FINAL-03 bis FINAL-09 technisch PASS, keine offenen Pflichtfindings. **ROOT_PASS** mit menschlicher **R03-Freigabe** – finale Git-/CI-Prüfung und Squash stehen aus. Kein AP-IV2-010-Start zuvor.

**Übernahmefreigabe 2026-10-14:** [R03-Originalprompt](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md) und [R03-Abschlussablauf](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R03-UEBERNAHME/01_REPORT.md) dokumentiert. Aktuelle Phase **READY_FOR_CANONICALIZATION**; unabhängiger R02-ROOT_PASS unverändert. Nach finaler CI und Head-/Baseprüfung ist der einzelne Squash-Merge von PR #13 erlaubt. Ohne belegten GitHub-Merge noch nicht ACCEPTED; kein Release/Tag/Servermerge/AP-IV2-010.

---

## Historischer AP100-Stand vor dessen tatsächlicher kanonischer Übernahme

# Client V2 – AP-CV2-100 / R05-ABNAHME / ROOT_PASS, 2026-10-13

AP-CV2-000 bis AP-CV2-090 auf `feat/client-v2` ACCEPTED; letzter kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der aktuelle AP-CV2-100-Paketbranch `work/client-v2/ap-cv2-100` ([PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)) wurde unabhängig am Kandidaten `0d45f8e9d3b484631da80be28f31c86ea85ab002` / Tree `aa8e3146f7e05e67694fc2027d712c62ce44cebe` geprüft: **technischer ROOT_PASS**, 6/6 Paketrequirements erfüllt, `CV2-100-R03-F01` geschlossen.

[R05-Abnahmebericht](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md), [unabhängige Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/EVIDENCE/INDEX.md), [R04-Korrekturbelege](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Extern qualifizierte Windows11-Suite **1581 PASS**, gezielte Tests **210 PASS**, **17** echte gepinnte Client-/Servercheckpoints am Server `ada13b0`, GitHub-Actions-CI **38394758805** erfolgreich auf dem geprüften Kandidaten. Reviewer hat diese Belege unabhängig geprüft, aber keine eigene Windows-/Hardwaretestausführung vorgenommen.

**Nächster Schritt: WAITING_FOR_APPROVAL.** Ausdrückliche menschliche Freigabe des Squash-Merges von PR #12 erforderlich, davor aktueller PR-Head, unveränderte Base, ausschließlich administrative R05-Nachträge sowie finale CI prüfen. Kein Merge und kein Start von AP-CV2-110 durch dieses Review.

---

## Historischer R04-Stand vor unabhängigem R05-Review

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json), [Runtimeinterfaces](docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

## Historischer Stand vor AP-CV2-020

# Aktueller Client-V2-Stand – AP-CV2-010, 2026-10-11

AP-CV2-000 ist nach unabhängigem PASS und menschlicher Freigabe über PR #2 als `1cf076bd2ed56929b1a3780bc140da51348a8295` übernommen. AP-CV2-010 ist nach unabhängigem R02-Review ROOT_PASS in [PR #3](https://github.com/marcosudau-vps/voice-stt-client/pull/3) auf `work/client-v2/ap-cv2-010`: reiner V2-Codec, Datentypen und Vertragsfixtures. Windowsvollsuite1263, Codec30 und gepinnter Servercheckpoint188 PASS; menschliche Übernahmefreigabe als nächste Aktion, Schreibhoheit pausiert; [R02-Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/RUNS/R02-ABNAHME/01_REPORT.md). Runtime bleibt bis zur Transportintegration auf ihrem bisherigen Pfad; keine Datenmigration. [Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md), [Codecvertrag](docs/protocol-v2-codec.md). Historische Einstiege unten bleiben ihrem Datum zugeordnet.

# Aktueller Client-V2-Korrekturstand R03 – 2026-10-11

AP-CV2-000 **REVIEW_READY** in [PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2), Branch `work/client-v2/ap-cv2-000`, Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [R03-Report](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md) und [Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json) sind der aktuelle Übergabestand.

F01: Hotkeyersatz wird erst nach erfolgreichem Corestart gespeichert; fehlgeschlagener Start erhält Profil und ursprüngliche Hotkeys. 1233 Gesamttests PASS, Packaging-/Installations-/Frozen-Smokes bestanden. Projektvenv Python 3.12.10. Nächste Aktion: frischer unabhängiger Vollreview einschließlich eigener Windows-Gesamtregression. Schreibrecht nach Übergabe pausiert; kein ROOT_PASS, Übernahmeprompt oder Folgepaketstart. Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`; V1-Transport und spätere V2-/Hardwaregates bleiben offen.

## Historischer Einstieg vor R03

# Client V2 – Arbeitsstand, 2026-10-11

Aktiver Block CLIENT_V2, Planung Revision 10. AP-CV2-000 **REVIEW_READY** auf `work/client-v2/ap-cv2-000`, Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [Aktueller Einstieg](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Paketakte](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md), [Runreport](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md).

Feature-/Releaseintegration in `voice_stt_client`, Präferenzen/Legacydaten erhalten. Gesamte pytest-/Unittestregression je 1221 Tests grün, Wheel und sdist außerhalb Source qualifiziert. Start `.\venv\Scripts\python.exe -m voice_stt_client`; Details zu Profilen und Pfaden in [Kompatibilität](docs/compatibility.md). Projektvenv Python 3.12.10; lokale venv-Verknüpfung zur bestehenden Clientumgebung.

Nächste Aktion: frische unabhängige Abnahme des vollständigen Kandidaten. Schreibrecht des Umsetzers nach Abgabe pausiert; kein unabhängiger PASS, menschlicher Übernahmeprompt oder kanonischer AP-Commit. Server ada13b0/Distributed bleibt offen; Transport noch V1 und bekannter Streamstartfehler dokumentiert. Keine V2-/Live-ASR-/Hardwareabnahme. AP-CV2-010 startet erst nach tatsächlicher kanonischer Übernahme.

---

Die folgende datierte Vorfassung bleibt historische Provenienz; ihre Next-/Freeze-/Branchanweisungen steuern Client V2 nicht.

# Arbeitsstand und Aufgaben – RealtimeSTT Windows Desktop Client

> **Status:** aktiver Tracker  
> **Stand:** 25. August 2026, nach Root-PASS von AP-SRV-020
> **Aktiver Arbeitsblock:** Einheitliche Triggerarchitektur `[IMPLEMENTIERUNG]`
> **Abgenommen:** AP-SRV-000, AP-CLI-000, AP-SRV-010 und AP-SRV-020
> **Nächster Schritt:** AP-SRV-030 (Commands, Timer, Watchdog und Recovery); AP-CLI-010 wartet auf AP-SRV-040
> **Kanonischer Wiedereinstieg:** `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/NACHVERFOLGUNG/WIEDEREINSTIEG.md`
> **Separater Restpunkt:** AP6-Wake-Word-Bediennachweis mit echtem Mikrofon (unverändert, siehe AP7 unten)
> **Repository/Release:** öffentliches GitHub-Repository und geprüfte Windows-CI-/Release-Strecke eingerichtet

## AP-CLI-000 – Clientbaseline und Charakterisierung (Einheitliche Triggerarchitektur) `[BASELINE VERIFIZIERT]`

Der bisherige AP1–AP8-Tracker unten bleibt als Ist-Stand-Historie erhalten und
beschreibt den Client vor der Migration auf die einheitliche
Triggerarchitektur. Für den aktiven Umbau ist ab sofort
`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/` maßgeblich
(Einstieg über `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`).

- Start-HEAD `db102fdc6dd70e4de798a363608d1e7412533dd7` auf
  `feat/einheitliche-triggerarchitektur` reproduzierbar getestet: **1192
  Tests** grün
  (`P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe -m pytest`,
  geteilte Projektumgebung; dieser Worktree besitzt keine eigene lokale
  venv), zweimal ohne Flake wiederholt.
- Baselinekorrektur (kein Soll-Verhaltenswechsel): `tests/test_obs010_normalizer_server.py`
  importierte `test_event_protocol` ohne Paketpräfix; das funktioniert nur
  unter `unittest discover -s tests`, nicht unter der vom Auftrag
  vorgeschriebenen `pytest`-Baseline, weil `tests/__init__.py` `tests` zu
  einem Package macht und `pytest` dadurch das Repository-Root statt
  `tests/` auf den Importpfad legt. Ohne diese Ein-Zeilen-Korrektur bricht
  `python -m pytest` die gesamte Sammlung mit einem Kollisionsfehler ab.
  Import auf `from tests.test_event_protocol import (...)` korrigiert.
- Neuer Charakterisierungstest
  `tests/test_ap_cli_000_baseline_characterization.py` belegt reproduzierbar
  einen in `PLANUNG/ANALYSEN/LEGACY_AND_DEAD_CODE_MAP.md` (§17.2, Fund 7)
  bereits beschriebenen, aber bis dahin nicht dauerhaft reproduzierbaren
  Befund: Mit einem `set_streaming`, das wie `core/stt_session.py:622-625`
  auch `state.streaming_requested` setzt, sendet die zweite Activation nach
  einem `finish` erneut `start`, obwohl der Inline-Kommentar in
  `core/controller.py:1123-1125` „der Stream bleibt bestehen" behauptet. Die
  vorhandenen Doubles (`FakeSTTSession`, `StreamCountingSession`) verdecken
  das, weil sie `set_streaming` nicht produktionsgetreu abbilden. Kein
  Produktcode wurde geändert; die Klärung, welche Seite (Kommentar oder
  Flag) korrekt ist, bleibt AP-CLI-010.
- Governanceabweichung nachgewiesen und korrigiert: `AGENTS.md` verwies auf
  `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` und
  `docs/IMPLEMENTATION_ROADMAP.md`; beide Dateien wurden am 17. August 2026
  (Commit `f3908cf`) nach
  `ARBEITSDATEIEN/90_HISTORIE/VOR_NEUEM_ARBEITSSYSTEM/` verschoben. Verweise
  in `AGENTS.md`, `README.md`, `ÜBERGABE.md` und `docs/PROJEKTUEBERSICHT.md`
  zeigen jetzt auf die aktuellen Nachfolger (`.agents/skills/arbeitsstruktur/SKILL.md`
  beziehungsweise `PLANUNG/` des aktiven Arbeitsblocks).
- Vollständiges Inventar überholter Trigger-Solltests, ihrer
  Contract-/Folge-AP-Zuordnung sowie kritischer Ist-Helfer:
  `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/ARBEITSPAKETE/AP-CLI-000/runs/01_BASELINE/REPORT.md`.
- Keine sonstige Produktverhaltensänderung; keine v2-Transport- oder
  ActivationMirror-Vorwegnahme.

## Historischer AP1–AP8-Tracker (Stand 12. August 2026, vor der Triggermigration)

## Phase 1 – Headless Audio-/WebSocket-Core `[VORHANDEN; LIVE UND AUTOMATISIERT TEILVERIFIZIERT]`

- [x] `core/audio_capture.py`: Mono-PCM16-Aufnahme, bevorzugt 16 kHz, 40-ms-Pakete
- [x] `core/stt_session.py`: WebSocket-Handshake, Protokollzustand, Audioübertragung und Transport-Reconnect
- [x] `app.py`: headless Verdrahtung und Konsolenausgabe von Realtime-/Finaltext
- [x] Live-Smoke-Test am 25. Juli 2026 für Health, `hello`, `ready` und `pong`
- [x] manueller Diagnose-End-to-End-Test am 25. Juli 2026 mit temporär korrigierter Thread-Brücke und „Hey Jarvis“: Wake Word, Aufnahme, Realtime und echter Finaltext erfolgreich; 733/733 Pakete gesendet, keine volle Clientqueue
- [x] thread-sichere Übergabe aus dem Audio-Verarbeitungsthread an die asyncio-Queue am 25. Juli 2026 dauerhaft in `app.py` korrigiert: Übergabe über `loop.call_soon_threadsafe`, kein Audio vor erfolgreich gesendetem `start`, sichere Drop-Grenzen bei Stop/Loop-Ende/Queue-Vollstand
- [x] `tests/test_app.py`: 10 Regressionstests für Event-Loop-Bindung, Fremdthread-Übergabe, Start-Gating und Shutdown-/Überlastgrenzen
- [x] manueller Wiederholungstest mit dem dauerhaft korrigierten regulären `app.py` am 25. Juli 2026: Server-Wake-Word deaktiviert, direkte Realtime-Ausgaben und Finaltext `Test eins, zwei, drei, Test.` erfolgreich
- [x] früheren breiten Sessionprofilentwurf nach damaliger Serverprüfung
  verworfen und aus dem Client entfernt
- [x] verworfene Serverprofil-Spezifikation nach `docs/archive/2026-07-25_SERVER_SESSION_PROFILE_SPECIFICATION_VERWORFEN.md` archiviert
- [x] neuer enger Session-Create-Contract des Servers am 26. Juli 2026 live
  verifiziert: Hotkey/Wake Word pro Session, logische Wake-Word-IDs,
  Tuningwerte, sichtbare Fallbacks und Isolation
- [x] Einbindung des neuen Session-Create-Contracts im konsolidierten
  AP6-Paketvertrag festgelegt; Implementierung bleibt Phase 6
- [x] Resume-Frage verbindlich entschieden: Ein unterbrochenes Diktat ist
  beendet; kein automatischer Neustart und kein Audio-Replay nach Reconnect
- [x] zuverlässige Ping-Miss-Erkennung umgesetzt und im AP5-Vertrag abgesichert

Hinweis: Es existieren weder `core/audio_processor.py` noch `core/stt_client.py`. `AudioCapture` liefert bereits `int16`; lokales Resampling ist nicht implementiert.

## Phase 1.5 – Transkript-Historie (AP1) `[ABGESCHLOSSEN]`

- [x] `core/history.py`: RAM- und selektive SQLite-Speicherung finaler Transkripte und Einfügeversuche
- [x] Deduplizierung über `(session_id, segment_id)`
- [x] `tests/test_history.py`: 30 Tests erfolgreich
- [x] Einbindung in den realen Finalevent-Pfad in AP4 umgesetzt

## Phase 2 – Textinjektion (AP2) `[ABGESCHLOSSEN]`

- [x] `core/text_injector.py`: serialisierte FIFO-Queue, Clipboard und `SendInput`
- [x] definierter Queue-Lifecycle und nicht-daemonisierter Worker
- [x] `tests/test_text_injector.py`: 41 Tests mit Test-Backend erfolgreich
- [x] manueller Notepad-Smoke-Test am 25. Juli 2026: `command_sent`, Text im fokussierten Notepad erschienen und vorheriger Clipboard-Inhalt wiederhergestellt
- [x] Einbindung in den realen Finalevent-Pfad in AP4 umgesetzt

## Phase 3 – Erneutes Einfügen (AP3) `[ABGESCHLOSSEN]`

- [x] `core/reinsertion.py`: `TranscriptReinsertionService`
- [x] Memory-first-Auflösung, SQLite-Fallback und definierte Resultatstatus
- [x] `tests/test_reinsertion.py`: 26 Tests erfolgreich
- [x] Controller-Anbindung in AP4 umgesetzt (Korrekturrunde 3 abgeschlossen)
- [x] Hotkey, Tray-Menü und Verlaufsauswahl in AP6 umgesetzt

## Phase 4 – Controller-Integration (AP4) `[ABGESCHLOSSEN]`

- [x] Integrationsgrundlage unter `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md` erstellt
- [x] vollständiger operativer Ausführungs- und Reviewauftrag unter `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md` erstellt
- [x] E-01 bis E-04 für AP4 umgesetzt: History-before-enqueue, getrennte Fehlersemantik, rohes `final`-Event als autoritative Identität, keine Hotkeys
- [x] E-05 für AP4 abgegrenzt: Audio-Thread-Brücke vor AP4 korrigiert; Ping-Miss-Erkennung und endgültige Reconnect-Semantik an AP5 übergeben
- [x] E-07 getrennt und nicht blockierend evaluiert: AP4 nimmt keine Betriebsmodus- oder Wake-Word-Override-Lösung vorweg
- [x] Vollständig exception-sicheren Run-Lifecycle umgesetzt (`try/finally` um `_loop` & `start_queue()`, schrittweise Task-Aufnahme)
- [x] Cancellation-geschützten gemeinsamen Shutdown umgesetzt (`asyncio.shield()`)
- [x] Aufnahmeübergänge atomar serialisiert (`asyncio.Lock`, `_start_dictation_locked`, `_stop_dictation_locked`)
- [x] Vulnerable Lifecycle-Rennen zusätzlich unabhängig abgesichert: partieller Task-Start, Queue-Start-Rollback, Cancellation-geschützter Shutdown, Shutdown gegen Aufnahmeübergang und Finalannahme gegen Closing
- [x] Tests und Typimporte in `app.py` und `tests/test_controller.py` bereinigt; neue Race-Tests verwenden Events statt willkürlicher Wartezeiten
- [x] Kanonische Dokumentation synchronisiert

## Phase 5 – Fehlerverhalten und Selbstheilung (AP5) `[ABGESCHLOSSEN]`

- [x] Produktentscheidung unter `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md` angenommen
- [x] verbindlichen Paketvertrag unter `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md` erstellt
- [x] operativen Ausführungsauftrag unter `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG_AUSFUEHRUNGSAUFTRAG.md` erstellt
- [x] Diktat bei Sessionverlust endgültig beenden; kein Resume und kein Audio-Replay
- [x] Start nur bei `READY`, ohne Vormerkung, und erst nach Serverstatus derselben Session bestätigen (Timeout 10 Sekunden)
- [x] stillen unbegrenzten Reconnect mit gedeckeltem Backoff (30s max einschließlich konfiguriertem Jitteranteil 0,3), CloseCode 1013 Spezialbehandlung (10s min) und sauberer Shutdown-Unterbrechung umgesetzt
- [x] Ping-Miss-Erkennung korrigiert (max 1 ausstehender Ping, ohne RTT-Kaschierung) und deterministisch getestet
- [x] Backoff-Reset ausschließlich beim ersten gültigen `pong` einer Session
- [x] persistente UI-neutrale Zustände (`AvailabilityState`, `DictationState`, `ControllerStatusSnapshot`) und sparsame Feedbackereignisse (`TransientEvent`) bereitstellen
- [x] Session-, Audio-, Task- und Queuegrenzen über Reconnects und Session-Generationen hinweg abgesichert
- [x] Antigravity-Erstimplementierung kritisch nachgeprüft und Race Conditions bei Startbestätigung, Disconnect während `STARTING`, Ping/Pong, Timeout-Reconnect sowie Session-/Audiogrenzen korrigiert
- [x] vollständige AP5- und Regressionstests durchgeführt (197 Tests grün)
- [x] echter `STTSession`-Live-Smoke-Test gegen den produktiven Server ohne Audio erfolgreich: `hello → ready → gültiger pong → sauberer stop`
- [x] Abnahme und Selbstfertigstellung unter `docs/2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md` dokumentiert

## Phase 6 – UI-Shell, Betriebsmodi und Einstellungen (AP6) `[FIX VERIFIZIERT – WAKE-WORD-BEDIENNACHWEIS OFFEN]`

- [x] verbindlichen Paketvertrag und Ausführungsauftrag unter
  `docs/work-packages/AP06_UI_SHELL*.md` erstellt
- [x] Vor-AP6-Baseline erneut ausgeführt: 197 Tests in 5,530 Sekunden
- [x] PySide6-`QApplication` im Main Thread
- [x] `QSystemTrayIcon` mit Status, Bedienaktionen und dynamischem Verlauf
- [x] passives, nicht fokussierbares und maustransparentes Overlay
- [x] Qt-Signalbrücke vom Core zur UI
- [x] thread-sichere Befehlsbrücke von Qt zum asyncio-Core
- [x] globale Hotkeys via Win32 `RegisterHotKey` mit Konflikt-Rollback
- [x] Reinsertion über Hotkey, Tray und ID-gebundene Verlaufsauswahl
- [x] nativer Win32-Single-Instance-Guard vor dem Corestart
- [x] GUI als regulärer Start; Diagnosepfad über `app.py --headless`
- [x] gezielte AP6-Härtung: 74 Tests erfolgreich
- [x] Gesamtsuite nach erster AP6-Umsetzung: 238 Tests in 6,181 Sekunden erfolgreich
- [x] `py_compile`, nativer Win32-Smoke und vollständiger AP6-Live-Smoke mit
  echtem Tray, Mutex, Hotkeys, separatem Core-Thread und Server-`READY`
  erfolgreich
- [x] Abnahme dokumentiert unter
  `docs/2026-07-25_AP06_ABNAHME/ABNAHMEBERICHT.md`
- [x] Overlay-Signalfehler vom 26. Juli behoben: Core-Payload
  `(segment_id, text, is_final)` wird explizit auf `(text, is_final)` adaptiert
- [x] Regressionstest für die reale CoreBridge→Overlay-Verdrahtung ergänzt
- [x] aktualisierte Server-Client-Dokumentation aus dem Server-Repository nach
  `server-docs-for-client-development/` synchronisiert
- [x] produktiven Session-Wake-Word-Contract aus Clientperspektive geprüft:
  `hello`/`ready`, Hotkey- und Wake-Session, parallele Isolation,
  Startstatus, Soft-Fallbacks und Close 1008 bei hartem Konfigurationsfehler
- [x] aktuelle `STTSession` mit `wakeWordEnabled=false` und
  `wakeWordEnabled=true&wakeWords=hey_jarvis` jeweils bis `READY` geprüft
- [x] Serverauffälligkeit bei Contract-Integration clientseitig gehärtet:
  Hotkey-Session meldet vor `start` wiederholt
  `state=voice` bei `activeClientId=null`; echte Startbestätigung besitzt
  `activeClientId == sessionId`
- [x] `error.where=session_config` bei Integration als deterministischen
  Konfigurationsfehler behandeln und keine blinde Reconnectschleife starten
- [x] Gesamtsuite nach Overlay-Fix: 239 Tests in 6,726 Sekunden erfolgreich;
  `py_compile` erfolgreich
- [x] endgültigen AP6-Folgeumfang am 27. Juli mit dem Benutzer konsolidiert und
  im bestehenden Paketvertrag materialisiert; die frühere Frageliste ist keine
  parallele Quelle mehr
- [x] operativen Folgeauftrag aus
  `docs/work-packages/AP06_UI_SHELL.md` erstellen und vor der ersten
  Codeänderung als Umsetzungsgrundlage freigeben
- [x] typisierte Betriebsmodus- und Session-Wake-Word-Konfiguration ergänzt
- [x] gewünschte Queryparameter sicher erzeugt und effektive
  `hello`-/`ready.sessionConfig` einschließlich Warnungen, Fallbacks und
  1008-Fehlersemantik auswerten
- [x] Hotkey- und Wake-Word-Modus einschließlich kontrolliertem
  Modus-Reconnect implementieren
- [x] Hotkey-Diktatfenster mit 15s Initial-Timeout, konfigurierbarem
  Follow-up-Fenster und 15s Standardverlängerung implementieren; keine lokale
  VAD nachbauen
- [x] Startdefault des regulären Follow-up-Fensters auf 3s festgelegt und in
  Bedienlauf festlegen und anschließend in `config.yaml`, Metadaten,
  Tests und Dokumentation identisch materialisieren
- [x] deklarative Einstellungsmetadaten über der typisierten `AppConfig`
  implementieren; keinen zweiten unabhängigen Wertespeicher einführen
- [x] per-user Override-Konfiguration atomar laden/speichern und sichere
  Apply-/Rollback-Policies umsetzen
- [x] Aktionsregistrierung und frei konfigurierbare, kollisionssichere globale
  Hotkeys implementieren
- [x] Einstellungsdialog mit den Tabs Verlauf, Allgemein,
  Verbindung/Betriebsmodus, Geräte/Audio und Erscheinungsbild/Feedback
  implementieren
- [x] statische Mikrofonwahl und manuellen Mikrofontest angebunden; Hot-Plug und
  automatische Geräteheilung nicht vorwegnehmen
- [x] Verlaufspflege einschließlich definierter Lösch- und
  Deduplizierungssemantik umsetzen
- [x] optionales nicht blockierendes Soundfeedback und kleinen
  Overlay-/Statusindikator umsetzen; nur ausgewählte lizenzgeprüfte Assets
  verwenden
- [x] 18 gezielte neue Härtungstests, vollständige Regression (257 Tests),
  `py_compile`, Offscreen-Qt und sicherer Live-Vertragstest beider Modi
  erfolgreich; der frühere native Windows-Smoke bleibt gültig
- [x] manuelle Bedienprüfungen 1 bis 4 erfolgreich: Hotkey-End-to-End,
  Initial-Timeout, Folgeaufnahme und Verlängerung
- [x] Moduswechselprüfung 5 korrigiert: persistenter Maintainer besteht
  unabhängig vom Startmodus und armt den Stream beim Hinwechsel automatisch
- [x] Rückwechsel korrigiert: Moduswechsel lassen den Maintainer ruhen, sein
  Lifecycle endet nur noch durch den gemeinsamen Core-Shutdown
- [x] atomaren Aktivierungsvertrag ergänzt: Wake-Word-Apply erst nach neuer
  `READY`-Generation und serverbestätigtem Streamstart erfolgreich
- [x] bestätigten Rollback bei Reconnect- oder Streamaktivierungsfehler ergänzt
- [x] frühere Fehlerfolge lokal dreifach, mit Aktivierungsfehler und
  Reconnect-Härtung sowie produktiv in zwei vollständigen Wechselzyklen
  erfolgreich provoziert
- [ ] gesprochenes `hey_jarvis` mit echtem Mikrofon nach dem Fix einmal
  manuell bestätigen
- [x] neues Tray-Farbkonzept umgesetzt: Hotkey dunkel-/hellgrün, Wake Word
  dunkel-/hellblau, weißer Sprachwarte-Rand, Gelb nur für äußere Störungen,
  Rot nur für tatsächliche Fehler
- [x] Fehleranalyse und Client-/Server-Abgrenzung unter
  `docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md`
  dokumentiert
- [x] Implementierung und lokale/produktive Fixverifikation unter
  `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md` dokumentiert
- [x] AP6-Dokumentation nach tatsächlicher Implementierung erneut
  synchronisieren und erst dann abschließen

## Phase 7 – Feedback- und Eventsystem (AP7) `[M0–M9 ABGENOMMEN – M10 IN ARBEIT]`

- [x] Debug-Feedback-Korrektur vom 12. August 2026 `[ABGENOMMEN]`
  - [x] unveränderte Clientbaseline: 435 Tests in 22,513 Sekunden erfolgreich
  - [x] `client.lifecycle.started`/`stopping` im produktiven GUI-Lifecycle
    genau einmal veröffentlichen und LED-Startzustand real belegen
  - [x] Mute-Beobachtung bei LED-Reconnect/Sinkwechsel erhalten
  - [x] genau acht lizenzierte, rein nichtsprachliche, gebündelte PCM-WAV-Cues mit stabiler
    Source-/PyInstaller-Pfadauflösung bereitstellen
  - [x] Tickton plus selbst rendernden LED-Countdown in den letzten drei
    Sekunden des Hotkey- und Wake-Word-Follow-up-Fensters ergänzen
  - [x] vorübergehend auffälliges LED-/Sound-Mapping und höhere
    Diagnosehelligkeit aktivieren
  - [x] Eventstream-Degradation als technische Tray-Notiz ohne wiederholtes
    Warnoverlay behandeln
  - [x] datensparsame Feedback-Entscheidungsspur für Event-/Korrelationsanalyse
  - [x] 151 fokussierte und 451 vollständige Clienttests, `compileall`,
    Onefile-Build, acht reale Qt-Sounds sowie ReSpeaker-Countdown vollständig
    und vorzeitig beendet abnehmen

- [x] bisherige Diskussion in eine verbindliche Gesamtplanung konsolidiert
- [x] historische Zwischenstände nach
  `docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/`
  verschoben
- [x] Paketvertrag unter
  `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md` erstellt
- [x] detaillierten Meilensteinplan unter
  `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md` erstellt
- [x] M0: Server-/Clientbaselines und Aktionsdokumentation vorbereitet
- [x] M1: Server-EventHub und Store auf SQLite-first umgebaut und durch die
  Servergesamtsuite abgenommen
- [x] M2: `/ws/logs`, Cursorfehler, Empty-Final, Deployment und Liveabnahme;
  `transcription.completed` produktiv zwischen Live, HTTP/SQLite und Replay
  korreliert, Zwei-Session-Scope zusätzlich belegt
- [x] M3: produktiven Serververtrag nach
  `server-docs-for-client-development/` synchronisieren
- [x] M4: immutable Clientmodelle, typisierte Eventstream-Konfiguration,
  strikt validiertes YAML-Mapping für `server.*`- und lokale
  `client.*`-Ereignisse sowie atomaren, endpointgebundenen Cursorstore
- [x] M4-Abnahme: 32 fokussierte Tests, vollständige Regression mit 285 Tests
  und `compileall` erfolgreich; keine UI- oder WebSocketkopplung vorgezogen
- [x] M5: isolierten `/ws/logs`-Transport mit getrenntem Reconnect, Replay,
  Ping/Pong und cancellation-sicherem Shutdown sowie strikten
  Protokollprocessor implementiert
- [x] M5-Abnahme: 23 fokussierte Tests einschließlich `-W error`, vollständige
  Regression mit 308 Tests und `compileall` erfolgreich
- [x] M6: gemeinsamen `DualSessionCoordinator` und generationgebundenen
  `SessionContext` integrieren; `hello.logAccess` nur für dieselbe aktuelle
  STT-Session übernehmen, alte Tokens/Events bei Reconnect invalidieren und
  beide Transporte gemeinsam deterministisch beenden
- [x] M6-Abnahme: 14 neue Race-/Lifecycle-Prüfungen, 59 relevante Tests mit
  `-W error`, vollständige Regression mit 322 Tests und `compileall`
  erfolgreich; Audio-, Finaltext-, Historien- und Injectionpfad unverändert
- [x] M7: exakte Server- und lokale Clientevents normalisieren; reinen Reducer,
  impulsfreies Replay, Ein-Quellen-Regel und duplikatsicheren STT-Fallback
  integrieren
- [x] M7-Abnahme: 30 fokussierte Tests, 183 relevante Tests mit `-W error`,
  vollständige Regression mit 352 Tests, `compileall` und `git diff --check`
  erfolgreich
- [x] M8: veröffentlichte Reducerausgaben queued an Qt, Tray und Overlay
  anbinden; sieben YAML-konfigurierbare Sound-Cues integrieren und alte
  Command-Sounds entfernen
- [x] M8-Abnahme: 13 neue Tests, 232 relevante Tests mit `-W error`, vollständige
  Regression mit 365 Tests, `compileall`, `git diff --check`, Offscreen-Qt-
  Zustandsprüfung und realer Qt-Soundbackend-Smoke erfolgreich
- [x] M9: ReSpeaker XVF3800 über eigenen minimalen USB-Adapter und Nulladapter
  integrieren; Updates koaleszieren, Pulse zurückführen, Fehler drosseln und
  Shutdown sicher begrenzen
- [x] M9-Abnahme: 13 neue Tests, 254 relevante Tests mit `-W error`, vollständige
  Regression mit 378 Tests, realer Firmware-/LED-Smoke, `compileall`,
  `git diff --check` und PyInstaller-Onefile-Build mit libusb erfolgreich
- [ ] M10: automatische und reale End-to-End-Fehlerkampagne `[IN ARBEIT]`
  - [x] Servergesamtsuite zweimal stabil: je 379 Tests, 13 Skips und 78
    Subtests; `compileall` und `git diff --check` grün
  - [x] Clientgesamtsuite nach der Härtung zweimal stabil: je 396 Tests; 227 fokussierte
    AP07-Tests mit `-W error`, `compileall` und `git diff --check` grün
  - [x] sichere Live-Smokes für beide Sessionmodi, zwei Laufzeitmoduswechsel,
    sessiongebundenen `/ws/logs`-Replay/LIVE-Pfad und Adapterausfälle grün
  - [x] Prüfbericht und vollständige 13-Punkte-Matrix unter
    `docs/2026-08-09_AP07_M10_FEHLERKAMPAGNE/PRUEFBERICHT.md`
  - [x] isolierte lokale Store-/Retention-/WebSocket-Kampagne sowie echter
    Neustart über zwei Betriebssystemprozesse mit persistiertem SQLite-Store
  - [x] realer ReSpeaker-Smoke mit fünf Effekten, abschließendem `off` und
    ohne verwaisten Hilfsprozess
  - [x] PyInstaller-Onefile-Build 0.1.0 einschließlich Multiprocessing,
    libusb und `--version`-Smoke
  - [ ] erneuter realer Hotkey-Gesamtlauf mit sichtbarem AP07-Feedback
  - [ ] gesprochener Wake-Word-/Follow-up-Gesamtlauf mit sichtbarem Feedback
  - [ ] sichtbare Disconnect-/Reconnect-Beobachtung während gesprochenem Diktat
  - [ ] realer Langlauf mit Latenz-/Ressourcenbeobachtung
  - [ ] reale stille Aufnahme für terminales `discarded`
- [ ] M11: Dokumentation und operative Gesamtabnahme

## Phase 8 – Härtung und Polish (AP8) `[OFFEN]`

- [ ] allgemeine Reconnect- und Langzeit-Stresstests über AP7 hinaus
- [ ] Mikrofonverlust, Hot-Plug und Gerätewechsel behandeln
- [ ] Windows-Sleep/Wake und tatsächlichen Audiowiederanlauf absichern
- [ ] Multi-Monitor- und DPI-Handling
- [ ] Autostart und weitergehendes Packaging-/Release-Polish; reproduzierbarer
  PyInstaller-Basisbuild, Commit-CI und taggesteuertes GitHub-Release sind
  bereits vorbereitet
- [x] öffentliche Repository-Basis und Laufzeitdatei-Hygiene: Secrets,
  Datenbanken, Caches, Buildausgaben, rohe Exporte und nicht freigegebene
  Sound-Sichtungssammlung werden nicht versioniert
- [ ] vollständige Release-, End-to-End- und Bedienprüfungen

## Repository-, CI- und Release-Vorbereitung `[ABGESCHLOSSEN]`

- [x] öffentliches Repository
  `https://github.com/marcosudau-vps/voice-stt-client` angelegt
- [x] `.gitignore` und `.gitattributes` für Secrets, lokale Laufzeitdaten,
  Buildausgaben und nicht veröffentlichte Rohsammlungen ergänzt
- [x] `VERSION` als einzige Release-Versionsquelle eingeführt; Startparameter
  `--version` und Windows-Dateiversion stimmen überein
- [x] `scripts/build.py` und `voice-stt-client.spec` bauen und prüfen eine
  fensterlose PyInstaller-Onefile-EXE
- [x] `.github/workflows/ci.yml` führt auf normalen Pushes und Pull Requests
  Tests, `compileall`, EXE-Build und Smoke aus und lädt die EXE als Artefakt hoch
- [x] `.github/workflows/release.yml` prüft Tags erneut und erstellt ein
  GitHub-Release mit versionierter EXE und SHA-256-Datei
- [x] `scripts/release.py` bestimmt die nächste Version, rollt lokale
  Prüffehler zurück, wartet auf grünes CI für exakt den Release-Commit und
  taggt erst danach; kein Sync in ein zweites Repository
- [x] lokaler PyInstaller-Build für `0.1.0`: 73.299.320 Byte,
  SHA-256 `ddea29ee62e0a8ba56063d0702b3d1e81c78b4c94db1d93e96bc2fb47e834f37`

---

## Test-Zusammenfassung

Zuletzt am 12. August 2026 ausgeführt (Vor-AP6-Baseline war 197 Tests):

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Ergebnis: **451 Clienttests erfolgreich**; `compileall` über `app.py`,
`core/`, `ui/`, `scripts/` und `tests/` ebenfalls erfolgreich. Die aktuelle
Servergesamtsuite bestand mit **378 Tests bei 13 Skips und 78 Subtests**. Der AP07-Livevertrag wurde mit zwei isolierten
Sessions sowie einem echten Audiofixture-Ereignis geprüft. Details siehe
`ÜBERGABE.md` und
`docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/2026-08-09_AP07_M0_BIS_M3_ABNAHME_ABSCHLUSSBERICHT.md`.

- AP1 Historie: 30
- AP2 Text-Injection-Queue: 41
- AP3 Reinsertion: 26
- Controller-Integration, Lifecycle und AP5-Härtung: 64
- Config-Prüfung: 19
- AP07-M4 Eventmodelle, YAML-Mapping und Cursorstore: 13
- AP07-M5 EventStreamTransport und Protokollprocessor: 23
- AP07-M6 Dual-SessionCoordinator und Race-Integration: 12
- AP07-M7 Normalisierung, Reducer und Controller-Integration: 30
- AP07-M8 Qt-, Tray-, Overlay- und Soundintegration: 13
- AP07-M9 ReSpeaker-USB-LED-Adapter und Replay-Härtung: 13
- Session-, Backoff- und Ping/Pong-Härtung: 18
- `app.py` Audio-Thread-Brücke und DI-Isolation: 10
- native Hotkeys: 6
- Single Instance: 3
- Präsentation, Tray und Overlay: 14
- Qt-/asyncio-Core-Brücke: 6
- GUI-Komposition und Startfehler: 8
- AP6-Folgeumfang (Modi, Einstellungen, Diktatfenster): 22
- Build-, Versions- und Releaseautomation: 7

Nicht durch diesen Lauf geprüft sind ein absichtlich ausgelöster realer
Netzabbruch während eines Mikrofon-Diktats, Mikrofonverlust/Hot-Plug/Sleep-Wake,
Langzeitbetrieb sowie Multi-Monitor-/DPI-Verhalten. Diese Härtung bleibt
ausdrücklich AP8. AP7 besitzt eine eigene Dual-WebSocket- und
Eventstrom-Fehlerkampagne.
