# Physischer USB-Nachweis und Feedback-Kalibrierung – 19.10.2026

Status **BLOCKED**, Workflow **IMPLEMENTATION_IN_PROGRESS**.
Gleicher R01/Paketbranch/Draft-PR15. Produkt unverändert0f6c85e; Änderungen
nur an Testkonfiguration, Helferprüfungen und Dokumentation. Kein REVIEW_READY.

## Neuer menschlicher Durchlauf

[Identität](EVIDENCE/usb-feedback-repeat-20261019/identity.json) und
[Auswertung beider Versuche samt unveränderten menschlichen Anmerkungen](EVIDENCE/usb-feedback-repeat-20261019/assessment.json).
Helfercommit4dc3db2,97Produkt-/Ressourcenhashes identisch zum korrigierten Produkt.
Beide Aufgaben einzeln selbst gestartet und mit „Wie erwartet“ übernommen;
anschließend menschlich „Durchlauf fertig.“. Herkunft klar getrennt:
physische Handlungen/Wahrnehmung durch Marco, Instrumentierung/Auswertung Codex.
Alle eigenen Clientprozesse sauber beendet, Exit0.

### R11 geschlossen für den nachgewiesenen Clientfehler

USB-Versuch52c55bce: physischer LED-USB-Ausfall18:56:36lokal, Capturestillstand
ab484Chunks. Neuer Fortschrittswächter greift18:56:38. AudioUnavailable-ACK
16:56:38.844UTC; Server kündigt alte Activation
`4f869c48-f42b-4e97-967d-2a0e4f2a3f95` mitcancelled/input_closed ab.
Keine Einfügung aus dieser verworfenen Aufnahme.

Reales Capture-Neuöffnen18:56:58; AudioAvailable-ACK16:56:58.734UTC,
LED-USB wieder verfügbar18:56:59. Nach bewusster neuer F8-Bedienung16:57:04.754
entsteht neue Activation`da685aad-2122-4b18-8378-6dc652991103`. F9/finish wird
16:57:10.217 bestätigt, input_closed=finished; ein Final und ein nativer Paste.
History/Event-ID/Text-Hash passen, Einfügung53Zeichen einschließlich Leerzeichen.
Kein automatischer neuer Trigger, keine vermischten Activations; dieselbe gültige
Session/Generation bleibt bestehen. Maximal11Tasks,471261184PrivateBytes,
Injectionqueue0 in82Messproben. Mensch bestätigt erwartetes Verhalten.

**IV2-020-R11 CLOSED**: gezielte rote/grüne Regression,1400Windows-Tests,
Source-/Wheel-Stillstandsprüfung und jetzt physische USB-Recovery am korrigierten
Sourceprodukt erfolgreich. Damit **M-06-Teilfall USB/Audio PASS_SCOPED** und
neues Manual-Finish/Einmalinjektion am korrigierten Stand belegt. Der komplette
M-06-Fall (einschließlich separat isoliertem LED-Ausfall) und Frozen-Hardware-
Qualifikation werden dadurch nicht geschlossen. Keine Übertragung alter
7bb5646-Prüfungen auf0f6c85e ohne Einzelnachweis.

### Feedback bestätigt, gezielter Idle-Wunsch

Versuch17944fe3: genau ein bewusstes F8/Manualactivate16:59:06.512UTC,
keine Sprache/kein ASR-Final, natürlicher input_closed=timed_out16:59:21.562.
Mensch bestätigt Timings und funktionierendes Feedback im aktuellen Auftrag;
Farbprofile ausdrücklich erst als separates späteres Feature.
[Wörtliche menschliche Bewertung](EVIDENCE/usb-feedback-repeat-20261019/human-feedback-note.md).
Dies schließt den bisherigen leeren Feedbackversuch durch einen tatsächlichen
No-Speech-Durchlauf ab: **M-10-Teilfall manuelles Start/Warten/Timeout-Feedback
PASS_SCOPED**. Keine Wake-/Both-/Frozen-Parität daraus.

Zwei spätere Clipboard-Paste-Ereignisse im Editor stehen keinem V2-Final gegenüber:
History0, Injectionattempts0. Sie werden als nicht zugeordnete Clipboardaktivität
bewahrt, nicht als STT-Ausgabe oder Doppelungsfehler bewertet. Kein Inhalt dieser
Einfügungen öffentlich exportiert.

## Idle-Puls: vorhandene Einstellung statt Produktänderung

Wunsch: Ring nie ganz dunkel, Puls von30bis100%, kein violetter Eindruck am Minimum.
[Inventar und Vergleich](EVIDENCE/usb-feedback-repeat-20261019/idle-calibration.json):
`ready_state` unterstützt bereits `min_brightness` und `brightness` jeweils0..1.
Bisherige weiße Testkonfiguration nutzte die Effektdefaults Minimum0,16/Maximum0,55,
Geschwindigkeit0,45 (Periodendauer8,889s). Sie ging rechnerisch bereits nicht auf0;
die Beobachtung „fast aus/violett“ bleibt echte menschliche Wahrnehmung, ihre
physische Ursache wird ohne weitere Farbmessung nicht als bewiesen dargestellt.

Neu reproduzierbar unter `tests/manual/v2/calibration.yaml`:
`color=#FFFFFF`, `min_brightness=0.30`, `brightness=1.0`, Geschwindigkeit unverändert.
Der bestehende Teststarter übernimmt diese Werte in
`feedback_mappings.events.server.input.idle.led` beim`ready_state`-Aufruf.
Gesamthelligkeit bleibt192/255.30/100% sind deshalb relative Effektintensitäten,
keine Behauptung absoluter physischer Lichtleistung. Client-/LEFX-Einstellung;
keine Serverautorität, neue Umgebungsvariable, Sicherheitsgrenze oder Produktdefault.

Die native Bibliotheksberechnung mit tatsächlich geladenem Effekt wurde über
121Zeitpunkte/einen vollständigen Atemzyklus und alle12LEDs geprüft: Basisframes
stets gleicheRGB-Kanäle, Minimum76/76/76, Maximum255/255/255 vor globaler Skalierung.
Damit ist ein violetter Basisfarbwert nicht nachgewiesen. Kurze andere überlagerte
Übergangseffekte werden durch die reine Idle-Änderung nicht pauschal umgefärbt;
kein Farbprofil vorweggenommen. Neuer30/100%-Vergleich bleibt bis Sichtprüfung
**NOT_RUN / CALIBRATION_PENDING**. Sämtliche alten Timingurteile bleiben ihrer
bisherigen Konfiguration zugeordnet.

## Technische Nachweise und nächste Aktion

29Helfertests samt echtem LED-Bibliotheksrenderer PASS; compileall und
Dokumentkonsistenz geprüft. Die erneut vollständig ausgeführte Windows-Regression
besteht mit1400Tests/0Skips in194,615s, vollständige Logs im Evidenzordner. Keine neue
EXE erforderlich: Produkt-/Ressourcenbytes bleiben vollständig identisch,
bisherige0f6c85e-Artefakte und Buildhashes unverändert. Neue Testkonfiguration
qualifiziert deren Wahrnehmung ausdrücklich erst nach dem neuen Vergleich.

Lesende Servernachprüfung findet erneut Proimage57a7907b und Pinada13b0;
Wheel-/installierte relevante Quellbelege stimmen. Wireunknown bleibt sichtbar,
keine durchgehende Vollintegritätsbehauptung. Kein Serverstart/-stop, keine
Servercode-/Modell-/Defaultänderung, kein Deployment.

Nächste menschliche Aufgabe ausschließlich Feedback/Idle, mit eigenem Start,
vorher sichtbaren Schritten und Wiederholung. USB muss wegen dieser LED-Einstellung
nicht erneut getrennt werden. Danach Wahrnehmung auswerten und Konfiguration
gegebenenfalls über denselben zulässigen Weg nachstellen. W01 sowie weitere
Phasen-/Runpausen-/Netz-/Settings-/Credential-/Frozen-/Clipboard-/100Activations-
Pflichten bleiben gemäßBericht19/20 offen. Paket weiter BLOCKED.

Der beendete Durchlauf ist mit27Dateien privat hashgeprüft im Projekt archiviert;
öffentlich nur ausgewählte Metadaten/Hashes und die bewusst eingetragene Bewertung.
Die automatische Freigabeprüfung lehnte auch die Löschung dieses beendeten
Bedienlaufs und des neu gesicherten Regressionsordners mit „blocked by policy“ ab.
Damit bleiben9beendete/hashgesicherte Ordner extern bestehen; genaue Zuordnung
in[cleanup.json](EVIDENCE/usb-feedback-repeat-20261019/cleanup.json). Ältere abgewiesene
Ziele wurden nicht erneut angefasst; keine Umgehung und keine behauptete Bereinigung.
