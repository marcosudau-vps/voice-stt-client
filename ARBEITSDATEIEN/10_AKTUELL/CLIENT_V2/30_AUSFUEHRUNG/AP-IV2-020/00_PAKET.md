# AP-IV2-020 – reale Windows-, Modell- und Hardwarequalifikation

Status **BLOCKED**, Workflow **IMPLEMENTATION_IN_PROGRESS** für unabhängige Restprüfungen, 2026-10-19.
Gesamtabnahme durch offenen W01 und weitere Realgates weiterhin blockiert.
Rolle: ein Umsetzer, R01-UMSETZUNG. Schreibhoheit: Codex in dieser Session.
Branch `work/client-v2/ap-iv2-020`, Base `feat/client-v2`, tatsächlicher Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
Serverbasis `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Clientprodukt erhält ausdrücklich freigegebene enge Recoverykorrekturen; neue Qualifikation erforderlich.

[Vertrag](../../PLANUNG/ARBEITSPAKETE/AP-IV2-020.md), Planung Revision 10,
Rollenregelversion 7. Keine Produktcodeänderung ohne gesonderte Freigabe.
Keine kanonische Übernahme, Releases, Tags oder Serverpromotion beauftragt.

- [Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md)
- [Laufender Report](RUNS/R01-UMSETZUNG/01_REPORT.md)
- [Evidenzindex](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md)

AP-IV2-010 nach unabhängigem R02-ROOT_PASS und menschlichem R03-Prompt
tatsächlich per PR14-Squash übernommen. Nachmergebeleg in dieser Akte.
Reale Pflichtfälle bleiben bis zur Durchführung NOT_RUN/NOT_PROVEN.

Zehn technische Reconnect-/Recoveryfindings behoben; [Audit und neue Qualifikation](RUNS/R01-UMSETZUNG/05_RECONNECT_AUDIT.md).
Keine fachliche Abgabe. R01-Schreibhoheit bleibt für autorisierte Fortsetzung erhalten.

Kumulativer [Draft-PR #15](https://github.com/marcosudau-vps/voice-stt-client/pull/15), Base feat/client-v2.
IN_PROGRESS, kein REVIEW_READY; R01 behält Schreibhoheit für die genehmigte Fortsetzung.

## Scope-Ausnahme bei Fortsetzung R01 (2026-10-15)

Der [menschliche Fortsetzungsauftrag](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/002_RECONNECT_AUDIT_FREIGABE.md) erlaubt eng auf Client-Reconnect/Recovery begrenzte Produktcode- und Testkorrekturen einschließlich weiterer nachgewiesener zusammenhängender Fehler. Dies ersetzt die ursprüngliche Produktcode-Sperre ausschließlich in diesem Scope. Derselbe R01, Paketbranch und Draft-PR #15 bleiben aktiv. Neue Produktidentität erfordert neue Windows-, Build- und Paarqualifikation; bisherige Nachweise bleiben historische Evidenz. Keine Servercodeänderung, Protokoll-/Sicherheitsänderung, Promotion, Release, Tags oder kanonische Übernahme freigegeben. Keine unabhängige Abnahme vorweggenommen.

## Zusätzliche Produktausnahme UX01, gleicher R01

[Ausdrücklich freigegeben](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/006_UX01_FREIGABE.md): bestehende Einstellung Leerzeichen anhängen wirksam machen, rohe Finals/History/Deduplizierung erhalten, dauerhafte Regressionen und neue Produkt-/Buildqualifikation. Produkt17261e6, neue [Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/ux01/INDEX.md). Keine sonstige Erweiterung der ursprünglichen Qualifikationsausnahme. Reale Pflichtfälle bleiben bis zur vollständigen Durchführung offen.

## Zusätzliche Produktausnahmen UX02 und UX03, gleicher R01

UX02 ist [ausdrücklich freigegeben](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/012_UX02_FREIGABE.md)
und am Produktd95043e technisch sowie physisch belegt: begrenztes Warten auf
freigegebene Modifiertasten vor nativer Einfügung, keine künstlichen Key-Ups.

UX03 ist durch den [direkten Fixauftrag vom18.10.2026](RUNS/R01-UMSETZUNG/09_UX03_CLOSE_SOUND.md)
freigegeben: fehlenden Beendigungston an serverbestätigtem Eingabeschluss
korrigieren, einschließlich Regression und neuer Kandidaten-/Buildqualifikation.
Produkt7bb5646, [Belege](RUNS/R01-UMSETZUNG/EVIDENCE/ux03-close-sound/assessment.json).
Kein Server-/Wirewechsel. Die ergänzte [Sound-/LED-/Triggerübersicht](RUNS/R01-UMSETZUNG/10_FEEDBACK_UEBERSICHT.md)
unterscheidet wirkliche V2-Ausgaben von lediglich deklarierten Regeln.

## Serverblocker IV2-020-W01

[Livebefund, echter Modellrepro und konkreter Korrekturweg](RUNS/R01-UMSETZUNG/12_WAKE_REAKTIVIERUNG_W01.md). Serverfix noch nicht beauftragt/instanziiert; Clientprodukt/Parent unverändert. Kein REVIEW_READY.

## Testlückenliste nach Infrastrukturentfernung, 19.10.2026

[Liste17](RUNS/R01-UMSETZUNG/17_TESTLUECKEN_UND_WIEDERHOLUNGEN.md) trennt
bereits abgedeckte enge Prüfungen, zuerst aus Belegen zu klärende Zuordnungen,
erforderliche praktische Nachprüfungen und die schon vorher offenen M01–M12.
Vier ausgeschlossene Frühakten besitzen spätere scopegleiche Wiederholungen;
keine rückwirkende Heilung, kein neuer M-PASS. Keine Serverwiederanlage beauftragt.

## Autonome Belegklärung durchgeführt, 19.10.2026

[Bericht18: Ergebnisse und sieben tatsächliche Restpunkte](RUNS/R01-UMSETZUNG/18_AUTONOME_KLAERUNG_UND_RESTPUNKTE.md).
25 neue Offline-Metadatenprüfungen PASS, sechs Fixtures und elf Archive identisch,
elf konkrete Fall-/Sessionverknüpfungen, Logfault-Imagebindung geschlossen.
Frühe nicht rekonstruierbare Runner und fehlende Admissionantworten ausdrücklich
begrenzt. Kein neuer Server-/Clientlauf, kein M-PASS; W01 und Zielentscheidung offen.

## Reihenfolgeentscheidung und vorhandenes V2-Ziel,19.10.2026

[Menschliche Präzisierungen017](RUNS/R01-UMSETZUNG/ZUSATZPROMPTS/017_W01_AUFSCHUB_UND_V2_TESTZIEL.md):
unabhängige Clientarbeiten zuerst; W01 später als gesonderter Server-FIX, betroffene
Realgates weiter vor vollständiger AP020-Annahme. [Fallabgrenzung19](RUNS/R01-UMSETZUNG/19_W01_BLOCKIERUNGSUMFANG_UND_TESTZIEL.md).
Pro-/Normal-V2 unter /ws/v2 erreichbar und Build-/aktuelle Image-/Quell-/Wheel-
Identitäten dem Serverpin zugeordnet.180s diagnostische Wartegrenzen. Kein neuer
Server-/Produktstand, keine Serverproduktfreigabe und keine voreilige Paketabnahme.

## Zusatznachweis 19.10.2026 – R11 im freigegebenen Recovery-Scope

[Durchlauf und USB-Korrektur](RUNS/R01-UMSETZUNG/22_GEFUEHRTER_DURCHLAUF_UND_USB_RECOVERY.md): reale USB-Abweichung reproduziert, eng begrenzt korrigiert, neues Produkt0f6c85e und1400Windows-Tests PASS. Kein Abschluss der offenen Realgates.

## Physische R11-Schließung und Idle-Kalibrierung,19.10.2026

[Bericht23](RUNS/R01-UMSETZUNG/23_USB_BESTAETIGT_UND_IDLE_KALIBRIERUNG.md): R11 physisch erfolgreich geschlossen. Weitere Pflichtgates unverändert offen; neue gewünschte Idle-Untergrenze30% nur Testkonfiguration, Sichtbestätigung ausstehend. Paket weiter BLOCKED, kein REVIEW_READY.

## Idle bestätigt / LED-only-Isolation,19.10.2026

[Bericht25](RUNS/R01-UMSETZUNG/25_IDLE_BESTAETIGT_UND_LED_ISOLATION.md): menschliche direkte Idle-Kalibrierung30/100% bestätigt, zusätzlicher kontrollierter LED-only-Ausfall bei idle ohne Audio-/Sessionwirkung PASS_SCOPED. Gesamte M-/Frozen-/Wakequalifikation weiter offen; Paketstatus BLOCKED, gleicher R01/PR15.
