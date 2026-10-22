# AP-IV2-020 / R03-KORREKTUR

22.10.2026. Korrektur von IV2-020-R02-F02 und separat [Issue #16](https://github.com/marcosudau-vps/voice-stt-client/issues/16). Kein Eigenreview. R02-F01 bleibt WITHDRAWN_BY_REVIEWER.

## Ausgang und Identität

Reviewspitze `2ba23544d18773f3ac02075ada5544b4c8ef8e47` nach Fetch mit tatsächlichem Remote-/PR-Head abgeglichen und sauber von `29fb0e1` fast-forward übernommen. Bestehender Branch `work/client-v2/ap-iv2-020`, PR15, Base/kanonischer Parent unverändert `b80ed8b81ad92bd02ac32553883443d2b7673bcd`.

Geprüfter Code-/Testcommit: `09b16c0f79e3251d3854112a38129527c79029c1`, Tree `21d5efbba4e1c7d06f36eabb6ae919416d6b6e58`. Nachfolgende Run-/Status-/Lognachträge sind administrativ. Der finale eingereichte Head/Tree wird aus dem Paketbranch bzw. PR ermittelt und in der Übergabe genannt; keine unmögliche Selbst-SHA im eigenen Commit.

Server unverändert `67f3ce45f6ea1ff659382e40c194c70bd33d58ff` / Tree `74f37cad84c5be9e74d880a4b10c3d9623de7da3`, historischer Vertragsursprung ada13b0. Keine Serveraktion.

## R02-F02: Ursache und Korrektur

Die vier Mirrormaps und das Resultservice-Terminalregister wuchsen bis Sessionende. Baseline: 86 relevante Tests PASS; der neue Retentiontest überschreitet mit dem ursprünglichen Mirror bereits bei Activation65 die behauptete 64er-Grenze. Die alte Reconnectmessung begrenzt diese Register innerhalb einer Session nicht.

Der Mirror verdichtet ausschließlich ein vollständig belegtes, abgeschlossenes Activationpräfix hinter monotone Activation-/Segmentsequenzmarken. Die letzten64 Activations bleiben mit Segmentdetails sichtbar. Ausstehende/fehlende Terminals, unbekannte Herkunft/Outcomes, unvollständige Records, Vordergrund und die Finals der gerade veröffentlichten Reduction verhindern vorzeitige Entfernung. Leere Cancel-/Failed-Tombstones bleiben vorsichtshalber erhalten. Retirierte Segmentereignisse und Starts erzeugen keine erneuten Fachereignisse/Finals. Unbekannte Lifecycle-IDs nach Retention verlangen Snapshotklärung, statt einen abgelaufenen Cancelzustand als offen zu rekonstruieren.

Eventfingerprints:1024 jüngste Identitäten plus höchstens512 geschützte Pufferidentitäten. Verbrauchte Wiresequenzen bleiben über last_event_seq gesperrt. Nicht verdichtbare Activation-/Segmentregister haben ein Budget von1024 Records, plus höchstens dem auslösenden Record. Überlauf wird ausdrücklich `session_retention_overflow`, unvollständig und RECONNECT_REQUIRED; kein stilles Entfernen offener Finals und kein ASR-Alterstimer. Die bestehenden Resync-/Reconnectpfade führen diesen Zustand aus.

Der Resultservice entfernt nur Terminals außerhalb der Mirrorprojektion. Eine monotone Final-Publikationsmarke verhindert Nebenwirkungen aus alten Reductionobjekten auch ohne History, nach Historylöschung oder unbekanntem Pasteabschluss. SQLite-/Clipboard-/Queueverhalten unverändert.

Nachweise:600Activations, eine Generation/Session,600Historyeinträge/600kontrollierte Einfügungen; nach Abschluss jeweils höchstens64 Activations/Segmente/Sequenz-/Resultterminals, höchstens1024 Fingerprints. Alte Wireevents, frische Hüllen für retirierte Segmentsequenzen und alte Reductions bleiben inert. Weitere gezielte Fälle:200 neuere Activations bei ausstehendem Altfinal, Gap-/Snapshot-Salvage mit erhaltener autoritativer Finalidentität, Cancel/Failed/leer/Interim, Unknown-outcome ohne Retry sowie sichtbarer Budgetüberlauf bei offenen bzw. unbekannten Zuständen.

## Issue #16: Ursache und Korrektur

Der Semantiktest verwendete100ms-Protokollfristen mit echter synchroner Cursorpersistenz und gab beim Reconnect denselben bereits verbrauchten Socket zurück. Seine ursprünglichen Assertions bleiben erhalten: Subscribe/Token nur im ersten Frame, Socketoptionen, Replay/Live, Cursor3→24 samt Binding, Generation1 und sauberer Stop/Socketclose.

Nur dieser Semantikpfad verwendet nun einen In-Memory-Cursor und testlokale logische Protokollzeit. Reale Runner-/Commitlatenz verbraucht keine fachliche100ms-Frist. Der echte äußere10s-Sicherheitswatchdog bleibt aktiv; echte Persistenz-/Fehler-/Replay- und Timeout-/Shutdowntests bleiben getrennt unverändert. Regression mit zweimal kontrolliert280ms blockierender Cursoroperation besteht über korrekte Zustandsübergänge. Ein unerwarteter BACKOFF bricht den Test vor Socketwiederverwendung mit der ursprünglichen Fehlerursache ab; eigener Negativtest mit ungültigem JSON. Keine produktive EventStream-/Persistenz- oder CI-Änderung, keine Retries.

## Tests und Wiederverwendung

- Baseline86 PASS; gezielte Regression152 PASS/0Skips, plus3 gezielte Anschlussprüfungen und7 finale Spacing-/Retentionprüfungen PASS.
- Ein Fehler der neuen Unknown-outcome-Testsimulation wurde vor der Vollsuite behoben: `unknown` ist kein direkt schreibbarer Finishstatus; die Regression verwendet den vorhandenen SQLite-Outcomefehler-/Restartpfad. Kein Produktdefekt daraus abgeleitet.
- Erste lokale Vollsuite:1407Tests/79Module, ein reproduzierbarer Anschlussfehler in test_text_injector_spacing: Der Publikationsguard lieferte beim Duplicate keine bisherige `deduplicated`-Rückmeldung. Diese Callbacksemantik wurde im Produkt erhalten, ohne erneute History-/Pastewirkung. Genau deshalb wurde der endgültige Code erneut vollqualifiziert; kein Wiederholen auf unverändertem Rotstand. Endgültiger Lauf: **1407 PASS/0Skips/79Module**, Exit0, exakte Discovery-/Ausführungsmenge; vollständige Logs im [Evidenzindex](EVIDENCE/INDEX.md).
- R01-[konsolidierter Abschluss40](../R01-UMSETZUNG/40_REVIEW_READY_UND_KONSOLIDIERTE_QUALIFIKATION.md) samt realen Hardware-/Modell-/Wake-/Clipboard-/Frozen-/Serverbelegen bleibt mit seinen ursprünglichen Identitäten/Methodengrenzen gültige komplementäre Evidenz. Die Korrektur betrifft die Runtime-Retention und Testzeitführung; keine neue EXE-/Hardwarequalifikation behauptet. Build-/Frozen-Smokes laufen regulär in CI. Kein neuer Dauer-/USB-/Sprachtest.

## Grenzen und Übergabe

Kein bekannter offener Produktfehler im Korrekturscope. Absichtlich konservative Grenze: dauerhaft ungeklärte ältere Records pinnen das Präfix; bei Ressourcenerschöpfung erfolgt sichtbare Unvollständigkeit/Recovery statt stiller Ergebnisverluste oder unbeschränktem Speicher. Die Dedupmarken nutzen die verbindlichen unveränderlichen, sessionweit steigenden Sequenzen; künstliches Umschreiben sämtlicher Identitäten/Sequenzen ist kein Wire-Replay. Unbekannter nativer Pasteausgang bleibt unbekannt und wird nicht automatisch nachinjiziert.

Vorhandene historische Fehlläufe, W02-Disposition und ursprünglicher ReSpeaker-Autopasteausfall bleiben erhalten. Historische observations in WORKFLOW_STATUS werden ausdrücklich als historische Beobachtungen mit Verweis auf die konsolidierte Schlussbewertung kenntlich gemacht.

Nach grüner Vollqualifikation: REVIEW_READY für frische unabhängige Gesamt-Nachabnahme mit Fokus F02/#16; der Implementierer beansprucht keine unabhängige Findingschließung. Issue16 bleibt offen. Kein Merge, Release oder Folgepaket; Paketbranch nach Übergabe pausiert.

Die vollständige CI wird nach dem einzigen abschließenden Push am unveränderten Code-/Teststand geprüft. Exakter PR-Head/Tree, CI-Run-URL und Ergebnis stehen anschließend in der PR-Übergabe; dadurch entsteht kein weiterer Docs-Push mit einer redundanten CI-Vollsuite allein zum Sichern der selbst erst durch diesen Push entstehenden Run-ID. REVIEW_READY wird erst nach tatsächlich grüner CI an die frische Session übergeben.

Aufräumen: Die automatische Freigabeprüfung lehnte das Entfernen der beiden neu erzeugten Ordner `isolated-suite-fa5aa8cf3a5c` und `isolated-suite-237e34e75a26` unter dem vorhandenen AP020-Qualifikationsverzeichnis mit „blocked by policy“ ab. Beide temporären Ordner bleiben erhalten; kein Einfluss auf Produkt-/Testergebnis.
