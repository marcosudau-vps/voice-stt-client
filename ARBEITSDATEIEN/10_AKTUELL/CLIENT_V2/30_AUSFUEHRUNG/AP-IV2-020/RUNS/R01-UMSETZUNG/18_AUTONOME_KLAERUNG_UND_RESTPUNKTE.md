# Autonom erledigt und tatsächlich noch offen

19.10.2026 · AP-IV2-020 / R01 · gleicher Paketbranch / Draft-PR15.
Fortsetzung der [Testlückenliste17](17_TESTLUECKEN_UND_WIEDERHOLUNGEN.md).
Keine neue Serverinstanz, kein Clientstart, keine Änderung außerhalb des
Repositorys. Clientprodukt7bb5646 und Serverreferenzada13b0 unverändert.

## Erledigte eigenständige Arbeit

| Punkt aus Liste17 | Ergebnis der jetzigen Prüfung |
| --- | --- |
| B01 Modellmetadaten | **Neuer Offline-Nachweis PASS:** alle25 ONNX-Klassifikatoren mit dem installierten Projekt-ONNX-Runtime geöffnet; Größe, Inputframes und daraus berechnetes diagnostisches Rezeptivfeld stimmen mit den damaligen Kernmetadaten überein. Modelle und Manifest gegen tatsächliche Gitblobs des Serverpins geprüft; insgesamt555 Quell-/Assetdateien identisch. Die alte ungebundene Akte bleibt ausgeschlossen. TFLite-Health und historische Betriebsumgebung wurden nicht neu ausgeführt. |
| B02 frühe Admission/Watchdog | Erhaltene Codehistorie auch auf CRLF-Varianten durchsucht. Exakte damalige Admission-Helferversion nicht gefunden; kein nachträgliches PASS. Der vorhandene Media-Stall-PASS bleibt auf diesen Ablauf begrenzt. Rest ist ein kurzer **automatisierter Lauf am festgelegten Ziel**, nicht neue menschliche Sprachaufnahme. |
| B03 Aufnahmen, Wake-Replay und Scores | Alle sechs versionierten WAV-Hashes, sämtliche Inputhashes der Score-/Replayakten und vollständiger Scoretrace überprüft. Exakter Scorehelfer und exakter Replayhelfer für320/480ms erhalten; beim Replay prüft dieser die echte Admission aufada13b0. Späterer vollständiger Sechs-Fixture-Lauf am Produktd950 bei320ms samt Loghashes bestätigt. Frühere0/160ms-Helferversion nicht exakt erhalten; diese frühen Vergleichswerte bleiben begrenzt. Für einen neuen Variantenvergleich sind die WAVs verfügbar, keine erneute Aufnahme nötig. Alexa-Pause bleibt ohne genaue Wortannotation NOT_PROVEN. |
| B04 Sprach-/Nachsprech-/UX01-/UX02-Versuche | Die Berichte mit Session-/Activation-IDs, Profilhashes bzw. ursprünglichen Ack-Command-IDs verbunden. UX01-Schrittversuche enthalten zwei separate Sessions. Elf Fall-zu-Session-Verknüpfungen für zehn ausgewählte Akten gesichert.5000ms-Präferenz, bestätigte Leerzeichen und erfolgreiche native Ausgabe bleiben erhalten. |
| B05 Sound/LED/freie Erprobung | UX03-Hörbestätigung eindeutig der Sessionc585545f und Activation836ce7c8 zugeordnet; weißes LED-Muster und freie Erprobung ebenfalls den richtigen Sessions/Profilen zugeordnet. Stoppton samt Lautstärke/Dauer braucht keine vorsorgliche erneute Geschmacksabfrage. Die übrige Feedbackkalibrierung bleibt offen. |
| B06 Logstore-Fault | Exakte gehashte Helferbytes in Git gefunden. Der Helfer speichert die **tatsächlich inspizierte Image-ID**, keine bloß konstante Angabe. Diese stimmt mit dem555-Dateien-qualifizierten Image5aaa17e überein. Damit ist die historische Pinbindung dieses Faultlaufs geschlossen. STT-Unabhängigkeit belegt; tatsächliche Erholung des Logstreams weiterhin nicht belegt. Kein Container angelegt/gestartet. |
| B07 Verwaltungsakten | Report, Fallmatrix, Evidenzindex und Workflow um diese Auswertung ergänzt. Historische Zusammenfassungen werden weiterhin nicht als zusätzliche Testläufe gezählt. |
| B08 W01/TV | Session-/Activation-/Profilzuordnung erneut bestätigt. TV-Diktat nach `finish` bis zum Clientende **3764,208s ohne Final oder Terminal**; ein `transcription.accepted` vorhanden. Kein Cancel aufgezeichnet, keine reine Overlayursache bewiesen. Fehlendes historisches Live-PCM ist nicht nachträglich rekonstruierbar. |

Die ursprünglichen Session-/Beobachtungsdateien wurden nur gelesen. Die neue
[Auswertung](EVIDENCE/retained-closure-20261019/results.json) enthält ausschließlich
Hashes, IDs, Zeiten, Einstellungen und Zähler.24 Sessionakten untersucht,
16 Beobachtungsdateien zugeordnet: zehn über gemeinsame Command-IDs, sechs nur
über einen eindeutigen Startzeitabstand unter5s, ausdrücklich schwächer markiert.
Widersprechende Command-IDs werden niemals durch eine ähnliche Uhrzeit überstimmt.
Elf vorhandene gzip-Archive der UX01-/UX02-Ausgabeproben hashgeprüft.

**Grenze der Sessionklärung:** In diesen Sessions wurde die ursprüngliche
Admissionantwort mit Servercommit nicht archiviert. Sessionzuordnung und
gemeinsame555-Dateien-Buildkette sind jetzt konkret belegt; eine fehlende
unabhängige Einzelattestierung wird dadurch nicht erfunden. Für Abnahmeansprüche,
die genau diese erfordern, bleibt der technische Nachweis am endgültigen Zielpaar
nötig. Die vorhandenen menschlichen Beobachtungen werden nicht gelöscht.

Zusätzliche Auswertung der letzten freien Session: rund171min,10277 Ready-
Messpunkte,10–12 Tasks, Capturequeue0–1, Einfügequeue0. PrivateBytes127,2 bis283,5MB,
am Ende283,47MB. Nur11 Aktivierungen, davon10 terminal; das offene TV-Diktat bleibt
sichtbar. **Kein erfolgreicher Stabilitäts-/30min100-Nachweis** und keine
Behauptung einer nachgewiesenen Leckfreiheit.

## Danach tatsächlich noch offen

| Nr. | Offener Punkt | Was zum Weiterarbeiten fehlt / wer erforderlich ist |
| --- | --- | --- |
| 1 | **Verbindliches Serverziel und zulässige Testablage** | Entscheidung, welche bereits vorhandene Instanz wir verwenden sollen. Docker Desktop meldet bei rein lesender Prüfung **manuell pausiert**; nicht entpausiert. Danach Commit, Modelle und wirksame Konfiguration des gewünschten Ziels technisch prüfen. Keine Wiederanlage des entfernten Servers, keine Änderung des normalen Servers aus diesem Auftrag ableiten. |
| 2 | **W01: automatische Wake-Reaktivierung** | Separater Server-FIX zu [Issue7](https://github.com/marcosudau-vps/voice-stt-server/issues/7) muss beauftragt/abgenommen werden. Hier weiterhin keine Servercodefreigabe. Danach automatischer Modellreplay und gebündelte Livebestätigung; bei neuem Servercommit eigene Paarqualifikation. |
| 3 | **Ausbleibendes Final/Terminal nach Finish** | Am festgelegten Ziel Verarbeitungs-/Workerdiagnose mit Status-/Serverlogs und klar getrennten Finish-/Cancel-Fällen. Historischer Fall ist dokumentiert, Ursache ohne entfernte Laufzeit nicht sicher rekonstruierbar. Zuerst technische Diagnose; kurze menschliche Kontrolle erst danach. |
| 4 | **Technische Restläufe am endgültigen Paar** | Admission aller Modi, kontinuierlicher Watchdog statt nur Media-Stall, Logstream-Erholung, Netz-/Serververlust mit Pending/Preview und sichere Wiederverbindung. Fehlende Einzelattestierungen dabei direkt erfassen. Variantenreplays bei Bedarf mit vorhandenen WAVs. Überwiegend autonom, sobald Ziel/Korrekturstand feststehen; keine erneuten Aufnahmen allein wegen alter Helferlücken. |
| 5 | **Normaler Desktopstart und sichtbare Diagnose** | T02: deaktivierter Starter ist kein erfolgreicher Doppelklickstart. Erst nach Ziel/Ablage passender Startweg; T01-Log-UI und konkrete Serveranzeige danach im normalen Windows-Kontext prüfen. Ein gebündelter Benutzerblock. |
| 6 | **Gebündelte vollständige Windows-/Hardwarefälle** | Offene Teile M01–M11: Modi/Hotkeymatrix/Überlappung/Run-Pausen, reale USB-/Mute-/LED-Recovery, Settings/Credentials und Ausgabe in normalen/erhöhten Anwendungen. Vorhandene Teilbelege anrechnen; menschliche Bedienung nur für die realen Restaktionen. |
| 7 | **Endkalibrierung und Stabilitätsabschluss** | Wakeempfindlichkeit/Nutzsprachgrenze, restliche LED-Zustände, Overlay und Gesamtablauf gemeinsam bewerten;5000ms-Nachsprechen und akzeptierten Stoppton als Ausgangspunkt erhalten. Danach endgültige Konfiguration und betroffene Regression/Build-/Paarprüfungen sowie mindestens30min/100 Aktivierungen qualifizieren. |

Es verbleibt keine unentschiedene allgemeine „Aktenrecherche“ aus B01–B08:
erhaltene Belege sind zugeordnet, nicht rekonstruierbare Einzelbelege benannt und
konkreten Restläufen zugewiesen. Fehlende historische Antworten oder PCM lassen
sich nicht durch weitere Plausibilitätsbehauptungen ersetzen.

[Rein lesende Prüfung des zuvor bekannten lokalen Kandidaten](EVIDENCE/retained-closure-20261019/existing-server-candidate.json):
Docker-Daemon antwortet mit „Docker Desktop is manually paused“. Daher weder
Existenz noch aktueller Commit dieser Instanz neu bestätigt. Kein Entpausieren,
Starten oder Auswählen eines Containers vorgenommen.

**Status bleibt BLOCKED / SERVER_FIX_REQUIRED.** Keine M-Fall-Statusänderung,
kein REVIEW_READY, keine unabhängige Abnahme vorweggenommen.

## Reproduzierbarkeit und Validierung

[Auswertungsskript](EVIDENCE/human/resolve_retained_evidence.py),
[gezielte Zuordnungstests](EVIDENCE/human/test_retained_evidence.py),
[Ausführung/Hashes/komplette Logs](EVIDENCE/retained-closure-20261019/validation.json).
Fünf Tests schützen vor falscher Sessionverknüpfung. Neue echte Ausführung hier
ist ausschließlich die Offline-ONNX-Metadatenprüfung; weder Live-Inferenz noch
Hardware- oder Serverqualifikation behauptet. Kein Produkt-/Tests-/Skriptwechsel
gegenüber dem qualifizierten Produkt; neue Helfer ausschließlich im Evidenzbereich.
