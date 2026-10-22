# AP-IV2-020/R01 – Hardware-Mute, Wiedereinfügen und Wakepausen

20.10.2026, gleicher R01/Paketbranch/Draft-PR15. Gesamtpaket **BLOCKED**,
Workflow **IMPLEMENTATION_IN_PROGRESS**, kein REVIEW_READY. Produkt unverändert
`0f6c85e0ecf971e596aae1b7d265dad7132754e2`, Server
`67f3ce45f6ea1ff659382e40c194c70bd33d58ff`, Parent
`b80ed8b81ad92bd02ac32553883443d2b7673bcd`.
[Menschliche Antwort](ZUSATZPROMPTS/031_MUTE_REINSERT_FERTIG.md).

## Beide menschlichen Aufgaben PASS_SCOPED

Source-HEAD `fbd0d2a25a542f267e32e2ab3d7f9e9fa2cebf0d`, jeweils echter
ReSpeaker/Windows/Hotkey/ASR/Clipboardpfad. [Identitäten und Ergebnisse](EVIDENCE/mute-reinsert-20261020/attempts.json),
[Quellherkunft](EVIDENCE/mute-reinsert-20261020/source-identity.json),
[unveränderte vollständige Serverinfo](EVIDENCE/mute-reinsert-20261020/server-info-after.json).

Hardware-Mute, Versuch `f357a06f2c374bdb9e7d4fa528949f21`:
27,297s tatsächlich beobachtete Stummschaltung nach vorher verfügbarem Audio;
Paketstand konstant521. Zehn echte Primary-Hotkeycallbacks lösen keine Activation
aus. Nach Freigabe derselbe Session-/Generationskontext, kein automatischer Start;
erst bewusstes F8 öffnet Activation `5e51a6e5-d325-464d-b08c-48a01a3e7df4`.
F9/Finish, ein Final29Zeichen und genau eine passende native Einfügung30Zeichen
inklusive Leerzeichen,1080echte Audiopakete, Exit0, keine lokalen Issues,
unverändertes Profil. Aufnahmeende→Finalempfang500ms, Finalempfang→Paste75,215ms.
Kein Beleg für Hardware-Mute bei offenem Input/Wake/Frozen oder Altfinalkombination.

Wiedereinfügen, Versuch `7f1b086c43d7453196b9d61c4c724869`:
genau eine Activation `0c410762-9b08-4f33-86fd-73c30a2ecdd4`, ein Segment/Final49Zeichen,
ein Historyeintrag. Genau zwei native Einfügungen50Zeichen mit gleichem Hash:
eine automatisch, eine bewusst manuell. Beide Injectiondatensätze gehören zum
selben Historyeintrag, Status command_sent; Editor100Zeichen.1183Audiopakete,
Exit0, keine Issues/Profiländerung. Aufnahmeende→Finalempfang953ms,
Finalempfang→erste Paste70,681ms. Kein eigener F11-Callbackzähler vorhanden;
manueller DB-Auftrag, native Ausgaben und menschliche Bestätigung sind die Belege.
Eigener normal privilegierter Sourceeditor; keine erhöhte App/Clipboardrace/Crashqualifikation.
Diese Empfangszeiten sind keine isolierte serverseitige ASR-Latenz oder Gesamt-SLA.

## Autonom: aktive Wake-Modelle, Pausen und Recovery

[Zwei endgültige Fälle](EVIDENCE/mute-reinsert-20261020/pause-confirmed.json)
prüfen Alexa/Hey Jarvis mit autorisierten WAVs, echtem TLS und Produktions-
Controls/Settings/Mirror. Je drei Sessions/Generationen, sieben bestätigte
Pausenmasken, gewählte5000ms erhalten; manuelle Wiederverbindung und Abbruch
nur des eigenen TCP-Sockets. Positive Fixtures erzeugen bei Wakepause keinen
Start; Primary bleibt bei manueller Pause gesperrt. Unabhängiges Wiederfreigeben
erlaubt je zwei bewusste Wakeactivations und eine manuelle Activation; jeweils
Cancel und leerer Commandtracker. **PASS_SCOPED.** Kein native-Mikrofon-/
Hardware-Mute-/Runtime-/Frozen-Pausennachweis. Der erste erfolgreiche Lauf bleibt
[separat](EVIDENCE/mute-reinsert-20261020/pause-first.json).

## Neue überlagerte Fehlerfolge IV2-020-W02

Die Erweiterung derselben Folge mit erneut positivem Wakeaudio innerhalb der
letzten manuellen Aufnahme ist zweimal **FAIL**: nach serverbestätigtem Cancel
folgt bei ausschließlich digitaler Stille eine zusätzliche Alexa-Activation.
Erster Lauf438ms bis activation.started, Score0,873958051; Wiederholung390ms
bis activation.started/406ms bis wakeword.detected, identischer Score.
Keine neue Activate-Anforderung nach Cancel, kein weiterer positiver Stimulus.
[Erster Fehlerlauf](EVIDENCE/mute-reinsert-20261020/overlap-failed.json),
[unabhängige Wiederholung](EVIDENCE/mute-reinsert-20261020/overlap-repeat.json).

Das bestätigt die zusätzliche serverseitige Admission in dieser konkreten
Audio-/Pause-/Recoveryfolge. Die genaue Trennung von Recorderqueue, Modellzustand
und sicherer Audiogrenze ist noch nicht bewiesen. Keine allgemeine Behauptung,
dass jede manuelle Aufnahme betroffen sei; frühere W01-Schließung für Wake→
Timeout/Finish/Cancel wird nicht rückwirkend aufgehoben. **W02 bleibt offen.**
Der eng begrenzte lokale [Server-Issueentwurf](33_W02_SERVER_ISSUE_ENTWURF.md)
enthält reproduzierbaren Ablauf und Pin. Keine Serverproduktänderung, Promotion,
Infrastrukturaktion oder unaufgeforderte externe Issuenachricht.

Vereinfachte frische Sessions wurden zusätzlich verglichen: erster5sDiagnoselauf
enthält4PASS und2FAIL, weil bei beiden positiven Jarvisfällen der natürliche
Timeout schon vor dem geplanten Finish/Cancel lag. Diese beiden sind
**Hilfstest-Vorbedingungsfehler**, keine nachgewiesenen Produktdefekte.
[Ursprünglicher Lauf](EVIDENCE/mute-reinsert-20261020/boundary-first.json).
Die korrigierte reine Vergleichsdiagnose nutzt15000ms als vorhandenen legalen
Sessionparameter, damit das volle9sFixture und2sStille in die Aufnahme passen:
[sechs Fälle mit2sVorlauf](EVIDENCE/mute-reinsert-20261020/boundary-relaxed.json),
[vier Fälle ohne Zusatzvorlauf](EVIDENCE/mute-reinsert-20261020/boundary-immediate.json).
Alle zehn korrigierten Vergleichsfälle PASS_SCOPED. Ihre Ergebnisse ersetzen
weder den5000msBediennachweis noch die fehlgeschlagene
überlagerte Folge. Die Benutzerkonfiguration bleibt5000ms.

## Testhilfe, Evidenz und nächster Block

Dauerhafte Helfer unter tests/manual/v2: explizite Pause-/Grenzdiagnosen,
ausgewiesene digitale Kontrollstille und getrennte Ergebnissätze; **59Helfertests,
tatsächlicher Qt-Selbstcheck für BOTH, compileall und Diffcheck PASS**.
Nur Testhilfen/Dokumentation geändert. Produktquellhashes passen weiterhin;
bestehende vollständige1400Windows/0Skips/PASS/194,744s bleibt gebunden und wird
nicht als erneut ausgeführt ausgegeben. [Validierung](EVIDENCE/mute-reinsert-20261020/validation.json),
[Helferlog](EVIDENCE/mute-reinsert-20261020/helpers.log.gz), [Qt](EVIDENCE/mute-reinsert-20261020/qt.log.gz),
[alle Diagnoseresultate](EVIDENCE/mute-reinsert-20261020/probe-summary.json).

Nächster einzeln startbarer Block: normales F8/F9-Diktat in BOTH, direkte
Alexa+Nutzsprache, direkte Hey-Jarvis+Nutzsprache. Ausdrücklich gewählter
Testkandidat5000msFollow-up/320msPre-Roll, beide Quellen aktiv; alte Liveprofile
werden nicht rückwirkend als320msqualifiziert. Keine automatische Folgeaufgabe,
Vorablesen/Start/Wiederholen/Übernehmen bleiben. W02 wird durch diese einfachen
Bedienfälle nicht geschlossen. Weitere vollständige M-/Frozen-/Admin-/Fault-/
Watchdog-/30min100-Gates und T02/T03/O01 bleiben offen.

Eigene abgeschlossene Oberfläche regulär beendet,24Laufdateien privat im
Git-ignorierten Projektarchiv gesichert und per Datei hashgeprüft. Automatische
Freigabeprüfung verweigert Löschen des neuen beendeten Ordners mit „blocked by
policy“:22gesicherte beendete Aufräumreste. Alte Ziele nicht erneut versucht,
keine Umgehung. Öffentliche Exporte ohne PCM/Rohtranskript/DB/Credentialwerte.
[Archivbindung](EVIDENCE/mute-reinsert-20261020/private-archive-binding.json),
[Aufräumrest](EVIDENCE/mute-reinsert-20261020/cleanup.json),
[Exportmanifest](EVIDENCE/mute-reinsert-20261020/export-manifest.json).
