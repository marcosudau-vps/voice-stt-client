# AP-IV2-020 / R01 – REVIEW_READY, 22.10.2026

Der kumulative Kandidat ist für die unabhängige Abnahme bereit. Alle Pflichtwirkungen sind in der [konsolidierten Matrix](EVIDENCE/review-ready-20261022/qualification-matrix.json) mit tatsächlicher Testgrenze zusammengeführt. Kein ROOT_PASS, keine kanonische Übernahme. R01 pausiert weitere Änderungen am Paketbranch. Der frische Reviewer beurteilt den vollständigen kumulativen Diff und die Nachweise unabhängig.

## Identität und Herkunft

Branch `work/client-v2/ap-iv2-020`, [kumulativer Draft-PR15](https://github.com/marcosudau-vps/voice-stt-client/pull/15), Base `feat/client-v2`. Kanonischer Parent `b80ed8b81ad92bd02ac32553883443d2b7673bcd`; Vorgänger AP-IV2-010 mit unabhängigem PASS, menschlicher Freigabe und tatsächlichem PR14-Squash im ursprünglichen R01-Startbeleg nachgewiesen. Start dieser Ergänzung: Commit `344f8693a83b0f0cc6dbd8afd8d5a60e6d7a00e4`, Tree `604062ea3de62375dcee257308eb2b1d0497f32d`. Endidentität kommt nach Commit aus Git in die PR-Übergabe; kein selbstreferenzieller SHA.

Produkt unverändert `0f6c85e0ecf971e596aae1b7d265dad7132754e2`. Qualifizierte normale EXE `dist-iv2-020-usb/voice-stt-client.exe`, SHA256 `e20059f6dff1279cb23fb01576d447fb285aa94cb270d71968b8430a063a15fc`; eingebettete Produktzuordnung in Bericht38. Kein neuer Produktbuild aus diesen reinen Test-/Ablageänderungen erforderlich.

Tatsächlich ausgewähltes Ziel `wss://pro.v2.voice-stt-server.marcosudau.com/ws/v2`; [öffentliche Info](EVIDENCE/review-ready-20261022/server-info.json): Server `67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, sauberer Tree `74f37cad84c5be9e74d880a4b10c3d9623de7da3`, Version2.0.0/pro. Vor-/Nachinfo der neuen Realfälle identisch, Instanz `14e6ff8dc2704f7298924b0d1de5cd1b`. Historischer Vertragspin ada13b0 bleibt Herkunft, nicht die aktuelle Deploymentidentität. Keine Serveranlage, Servermutation, Promotion oder V1-Änderung in diesem Abschluss.

## Abschließende technische Ergänzungen

**Native Hardware/Altfinal/Pausen:** [ReSpeaker-Nachweis](EVIDENCE/review-ready-20261022/native-pending-directsound.json) PASS_SCOPED. Echter DirectSound-Endpunkt9/44100Hz,135 native Callbacks vor tatsächlichem Streamabbruch. Bei7,125s A-final ausstehend und B geöffnet; B bei7,172s abgebrochen, A-final bei7,953s genau einmal erhalten. Session/Generation bleiben gleich; tatsächliches Reopen, keine Eigenaktivierung; manuelle/BOTH-Runpausen überstehen beide Recoveryvarianten. PCM und Clipboard bewusst kontrollierte Testgrenzen, kein physischer Kabelzug in diesem Zusatzfall. Physische USB-/Mute-/LED-Nachweise aus Bericht23/25/32 bleiben eigenständige reale Belege.

**Normale finale EXE/Overlap:** [vollständiger Durchlauf](EVIDENCE/review-ready-20261022/frozen-native-overlap-complete.json) und [reale Ereignisse](EVIDENCE/review-ready-20261022/frozen-final-events.json) PASS_SCOPED. Unveränderte EXE, echter Windows-Stereomix/PortAudio, Wiedergabe autorisierter menschlicher Sprachfixture, echter Server/ASR, native sichtbare Einfügung. Vier native F8/F9-Impulse je6/6Events; A `3c1cef94-5a24-4def-8a26-fcb439d2ad44` final bei B `21c33ada-07aa-4e80-acf8-f2d188974730` in segment_active. Zwei Finals/Historyeinträge,248 sichtbare Zeichen stimmen exakt zur History mit Leerzeichen. Keine zweite Ausgabe desselben Finals, Clipboard restauriert. Das ist kein akustischer ReSpeaker-Nachweis; dafür bestehen separate reale Proben. Ein Pixelbild des Overlays genau im Overlapmoment wurde nicht aufgenommen; nachvollziehbare Zustands-/Ereignisspur und Qt-Regressionen belegen die Zuordnung.

**Normaler Desktopstarter/T02:** [Windows-Shell-Nachweis](EVIDENCE/review-ready-20261022/desktop-launch-assessment.json) PASS_SCOPED: dauerhaftes Repo-Programm `tests/manual/v2/Start-GuidedTests.vbs` öffnet den geführten Starter über normalen Windows-Openverb. Sichtbares richtiges Pro-V2-Ziel, normale Tokens Integrity8192/UIAccess0/AppContainer0, kein Produktclient ohne Startklick. Pin-Datei verbindlich, kein Loopback-/V1-Fallback. Agent hat den Desktopstart ausgeführt; kein menschlicher Doppelklick behauptet. Beide Probe-GUIs beendet. T01/Logging/Verlauf/Feedback waren bereits menschlich ausdrücklich bestätigt.

## Vollständige Matrix und Testmethoden

| Fälle | Tatsächliche Wirkung und Beleg |
|---|---|
| M-01 bis M-04 | Manual/Wake/BOTH, Segmente, Abschlusswettläufe, Slots/NONE/Kollision/Refresh/Watchdog; Bericht30/31/34/37 und Matrix. |
| M-05/M-06 | Runpausen, Restart/Reconnect, reale USB-/Mute-/LED-Verluste plus neuer nativer Altfinal-/Recoverybeleg oben; Bericht23/25/32/37. |
| M-07/M-08 | Preview-/Pending-Final-Netzfehler, tatsächlicher SQLite-Schreiblock; Settings Cancel/Finish/Defer/Drain; Bericht37. |
| M-09 | Tatsächlicher Credentialstore create/replace/delete und positiver Admin-Guard, Generationwechsel/Neuprüfung, keine globalen Defaults/Vaultänderung; Bericht37/38. |
| M-10 | Normale finale EXE Manual/Alexa/Jarvis mit tatsächlichen Outputs, reale Hardware-/Feedbackproben sowie neuer EXE-A-final/B-speech-Nachweis; Bericht38 und oben. |
| M-11 | Native Unicode-/Konflikt-/Crash-/Reinsertfälle, unklarer Ausgang ohne Auto-Retry, eigener erhöhter UAC-Zielprozess; Bericht37/38. |
| M-12 | Tatsächliche1800,015s/100 abgeschlossene Aktivierungen,34Manual/33Alexa/33Jarvis,100Finals/History/kontrollierte Ausgaben, drei Recoveryaktionen; Bericht35 und separate reale Hardware-/Recoverybelege. |

Ausführung durch Codex auf tatsächlichem Windows, menschliche frühere Sprach-/Hardware-/Wahrnehmungsaktionen jeweils im Ursprungsbeleg gekennzeichnet. Diese Gesamtbewertung ist **zusammengesetzt aus komplementären realen Teilfällen am gleichen Produkt**. Bericht38/39 hatten zusätzlich eine erneute physische/Frozen-Dauerrunde als Restgrenze geführt. Der Paketvertrag fordert einen30min/100-Lauf und echte Hardware-/Frozen-Fälle, keinen zweiten vollständigen100er-Frozenlauf. Der vorhandene echte Modell-Dauerlauf plus die separaten physischen und neuen nativen/Frozen-Belege erfüllen aus Umsetzungsbewertung die Pflichtwirkungen. Keine Behauptung, alle100 seien Live-Mikrofonaufnahmen gewesen oder alle Gerätefehler seien physische Kabelzüge im selben Dauerlauf. Der Reviewer prüft diese Zuordnung ausdrücklich; keine fachliche Requirement gestrichen oder künstlicher Hardware-PASS aus Adaptern.

Dauerressourcen: warm393,16→402,71MiB (+9,54; Maximum402,97),Tasks9..14,keine CaptureDrops. Sessionretention25 wird durch gezielte Wiederverbindungen erklärt; keine daraus erfundene generelle Leckfreiheitsgarantie. Reale Latenzen/ASRqualität und Golden-/Wakegrenzen stehen in Bericht35/37 und den Rohmessungen; keine garantierte Server-SLA oder universelle TV-Fehlalarmfreiheit. Höhere Wakeanforderungen0,75/2,0,85/2,0,90/2 nur verglichen;3/5Frames verfehlen Jarvis, daher nicht übernommen.

## Windows-Regression, Fehlläufe und Kandidatenbindung

[Vollständige Bewertung](EVIDENCE/review-ready-20261022/review-final-windows-assessment.json): **1400/1400 exakte entdeckte Test-IDs,0Skips,79Module PASS**. Vollständige Logs komprimiert unter EVIDENCE/review-ready-20261022/windows/, zusätzlich vollständige34er-Settings-Modulwiederholung im seriellen Lauf. Kein Modul/ID ausgeschlossen. Windows/Python, Befehle, Ausgangsstand und Diffbindung in [Validation](EVIDENCE/review-ready-20261022/validation.json); Laufbefehle/Exitcodes auch in der ursprünglichen Modulbewertung.

Erste monolithische Qt-Ausführung endete mit nativem Decoder-AccessViolation, zweite hing. Unter Modulprozessisolation vollständige Suite erfolgreich. Ein34er-Settingsmodul traf unter Parallelbelastung ein2s-Fakeserverlimit, komplette unveränderte Wiederholung seriell grün. Initialer Logparser ordnete mehrzeilige unittest-Beschreibungen falsch zu; durch echte TextTestRunner-Regression korrigiert und exaktes1400er-IDset erneut gegen vollständige Logs bewertet. Originalfehler/Logs erhalten. Einziges bestehendes Core-Testmodul geändert: Fake-ACK-Zeit im Watchdogtest parametrierbar und begrenzt auf wirklichen Recoveryzustand warten; produktive Grenzen/Assertions unverändert. Diese Änderung war vor den finalen Modulprüfungen enthalten.

**83Helfertests/0Skips/3,949s und compileall PASS**, [vollständiger Helferlog](EVIDENCE/review-ready-20261022/review-final-helpers.log.gz). Neue Helfer korrigieren Starttimer (kein Zeitablauf vor bewusstem Start), gezielte Overlapsteuerung und das Abwarten beider echten Finals; normale Desktopprüfung belegt den finalen Launcher. Keine Produktänderung seit0f6c85e. Sämtliche tatsächlichen Diagnoseversuche samt Grenzen in [Attempt-Disposition](EVIDENCE/review-ready-20261022/helper-attempt-dispositions.json); nicht pauschal als erfolgreiche Erstversuche dargestellt.

## Kalibrierung und bekannte Grenzen

Reproduzierbar über vorhandene Profilkonfiguration in `tests/manual/v2/calibration.yaml`: Nachsprechfenster5000ms (menschlich statt3000 gewünscht und bestätigt),Pre-Roll320ms,Idle weiß30–100% der Effektintensität. Bestehende Wakewerte0,5/1 bleiben; aktive12LED-Rampe/Rotation und menschlich bestätigter Stoppton in bisherigen Profilbelegen. Keine frei erfundenen Parameter oder globale Serverdefaults, kein V1-Profil verändert. Weitere Wahrnehmungsbewertung auf ausdrücklichen Nutzerwunsch abgeschlossen; bestehende Beobachtungen erhalten.

W01 am korrigierten Server konkret verifiziert geschlossen. W02 **CLOSED_BY_HUMAN_DISPOSITION_NOT_REPRODUCED**; zwei historische Fehler erhalten, kein identifizierter kausaler Fix behauptet. Historische ungebundene menschliche Erfolgsmeldung bleibt HUMAN_REPORTED_SUCCESS_UNBOUND, zählt nicht als Abnahmetest. Der damals fehlende technische EXE-Nachweis ist durch die identifizierte autonome neue Prüfung ersetzt.

Ein früherer ReSpeaker-Durchlauf erkannte korrekt, fügte automatisch aber nicht sichtbar ein; Ursache nicht bewiesen. Späterer bewusster Reinsert und normale EXE-Ausgaben sind separat erfolgreich, ohne erfundene Ursachenheilung. Bei erhöhtem UAC-Ziel waren4/4 SendInput-Events akzeptiert, sichtbar0Zeichen: command_sent ist keine Einfügegarantie, keine automatische Wiederholung. Keine allgemeine Zusicherung für jede fremde Anwendung/Rechtekombination. Keine offenen reproduzierten Pflichtbefunde aus den aktuellen Abschlussdurchläufen; unabhängige Bewertung dieser Grenzen bleibt erforderlich.

## Ablage, Scope und Übergabe

[Aufräumreceipts](EVIDENCE/review-ready-20261022/cleanup.json): alle18letzten eigenen Runtimeordner nach Hashvergleich ins Projektarchiv übernommen und sicher entfernt; genehmigter externer AP-IV2-020-Namensraum leer. Frühere Bereinigungen bleiben in ihren datierten Akten, keine Doppelzählung. Für Review benötigte redigierte Resultate/Vollogs/Helfer im Repo; private Datenbanken/Audio bleiben außerhalb Git im Projektbuildarchiv. Admin-Key nur zur autorisierten Laufzeit gelesen, nicht in argv/Vault/Repo übernommen. Git-Diff-/Akten-/Hash-/Secretprüfung vor Commit, Ergebnis in Bereitstellungsnachweis/PR.

Die bereits ausdrücklich genehmigten Client-Recovery- und UX01/02/03-Ausnahmen sind in Paketakte und Originalfreigaben gesichert. Keine zusätzliche Produkt-/Serverkorrektur, kein Refactor. Keine Migration von V1-Daten. Bestehende Callback-/Session-/Generation-/Deduplizierungsverträge unverändert; neue Dateien sind Testhilfen und redigierte Belege.

Nächste Aktion: frische unabhängige Abnahmesession prüft exakt den eingereichten PR-Head gegen Parent, gesamten kumulativen Code-/Testdiff und diese Fremdnachweise. Kein Eigenreview, keine automatische Folgepaketarbeit, kein Merge/Release/Tag. Menschliche Übernahme bleibt nach unabhängigem PASS separat erforderlich.
