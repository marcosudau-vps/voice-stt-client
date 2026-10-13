# AP-CV2-110 / R01-UMSETZUNG

**Status:** REVIEW_READY (vollständiger Selbstcheck; unabhängige Abnahme offen).
Stand 2026-10-13. Abgabe erst nach grüner CI der endgültigen PR-Spitze.

## Identität, Auftrag und Voraussetzungen

[Originalauftrag](00_PROMPT_ORIGINAL.md), [Startprovenienz](EVIDENCE/start-provenance.json).
Branch `work/client-v2/ap-cv2-110`, Base `feat/client-v2`, kanonischer Parent
`62ca35a01fb88b37e16b7003e26c2f9110c131f3`. AP100 ist über PR12 nach unabhängigem R05-PASS und menschlichem
R06-Auftrag tatsächlich übernommen: ein Parent, identischer Baum zum finalen
AP100-Head. Server `ada13b011e1d3829f78e7f389e3b927795a2b3be` bleibt unverändert.

Qualifizierter Produkt-/Test-/Buildkandidat **`2b4bb7869f6659434d37d1a7d8b0cba5ba3bd259`**, Tree **`d9a30deafd7c66143e376931f21d96f6b02aabc4`**.
Die spätere PR-Spitze enthält ausschließlich administrative Dokument-/Evidenznachträge;
[Gitblobmanifest](EVIDENCE/candidate-blobs.txt) und Abgabeverifikation binden sie an
exakt diesen Produktstand. Finale Head-/Treeidentität wird aus dem PR/Gitref ermittelt
und in der externen PR-Kurzfassung genannt; keine unmögliche Selbst-SHA.

## Ergebnis und notwendige Anschlusskorrekturen

Ausführbare V1-Controller-, Session-, Headless-, Ready/Start/Stop/Timeline-/Mode-/
Extend-/Timer- und STT-Feedbackfallbackautoritäten entfernt. Shared Statusenums,
CommandResult und reine alte Darstellungstypen bleiben datentragend; sie starten
keinen Transport. CoreBridge verwendet standardmäßig V2Runtime. Gemeinsamer
Desktoprahmen enthält keine zweite V1-Settings-/Hotkey-/Feedbacksteuerung.

Config-/Historyreader bleiben erhalten; veraltete Session-/Timer-/Hotkeywerte
können ein vorhandenes V2-Profil nicht überstimmen. Packaged Default ist `/ws/v2`
ohne lokale Diktattimer; lokale Settings zeigen nur tatsächliche lokale Präferenzen.
V2-Settingsdialog enthält Session/Server/Lokal mit asynchroner Geräteabfrage.
Loggingstatus erreicht den eingebetteten lokalen Dialog. Diagnose vor dem ersten
Domain-Snapshot erzeugt keine erfundene Lifecycleansicht.

Regressionen zeigten zwei Produktlücken: defektes Loggingapply durfte lokale
Persistenz/Transport nicht scheitern lassen; ein fehlgeschlagener GUI-Start
musste außer Profilbytes auch den vorläufig ersetzten Hotkeymanager zurücksetzen,
damit Retry die ursprünglichen Bindungen versucht. Beide minimal korrigiert und
mit tatsächlicher Runtime/GUI unter Faultinjection geprüft. Logging bleibt
beobachtend, die AP100-Auditkorrelation bleibt erhalten.

## Release, Ressourcen und Identität

`setup.py` stempelt sourceCommit/clientCommit/version/dirty in Wheel und sdist;
sdist-Rebuild ohne `.git` bewahrt den Originalstempel. Frozen Build bekommt denselben
Stempel. Source prüft nur sein echtes Gitroot und dirty Produktdateien; dirty/fehlende
Identität meldet unknown. Kein fremdes übergeordnetes Gitrepo oder Envwert als Identität.
V2TransportConfig verwendet diese Identität im tatsächlichen Hello. VERSION bleibt
1.0.0, kein veröffentlichter V2-Release. Serverunknown bleibt ausdrücklich unbelegt.

Drei bytegleiche gepinnte V2-Fixture-/Schema-/Provenienz-JSONs, Config, acht WAVs,
LEFXressourcen und bestehender Qt-/EXE-Iconpfad sind paketiert. Wheel/sdist enthalten
nur den Namespace voice_stt_client, keine core/ui-Aliase, Simulatoren, Tests,
Akten, Credentials oder Runtime-DBs. Frozen-PYZ: 788 Module, V2Runtime enthalten,
keine core/ui/tests/fastapi/starlette/Simulatorimporte. Negativfälle prüfen auch
verbotene Archiveinträge, dirty Identität und unterschiedliche Commitstempel.

## Tests, Iterationen und Beweisgrenzen

Windows11 Build26300 x64, Projektvenv Python3.12.10; Befehle/Runtime/Exitcodes/
Testzahlen und vollständige Logs im [Evidenzindex](EVIDENCE/INDEX.md) und
[Windowsmanifest](EVIDENCE/windows-validation.json).

| Prüfung | Tatsächliches Resultat |
| --- | --- |
| Unveränderte Parent-Baseline, isoliertes Gitarchive | 1581 Tests PASS, 183.004s |
| Gesamte aktuelle Clientsuite | 1348 Tests PASS, keine Skips, 175.609s Testlauf |
| Gezielte Release/Runtime/Feedback/OBS/Eventstream/Buildtests | 229 Tests PASS |
| compileall und git diff --check | PASS |
| Tatsächlicher komponierter Runtime-/Servercheckpoint | 17 Checks PASS; bytegeprüfter ada13b0-Server |
| PyInstaller --clean und EXE Ressourcen-/Versions-/Qt-Smoke | PASS |
| sdist + wheel, twine check, Releaseguard erwartete SHA | PASS |
| Wheelinstall und sdist-Wheelrebuild außerhalb Checkout | PASS |
| Source/Wheel/Rebuild/Frozen native Windows-GUI mit getrenntem Server | 4 PASS; 8 serverseitig empfangene Hellos |

Ein zuerst gestarteter Baselineversuch war ungültig: Imports wurden während des
Laufs durch eigene Folgeänderungen beeinflusst (8 Fehler). Der vollständige Log
bleibt erhalten; ausschließlich der isolierte unveränderte 1581-PASS gilt als
Baseline. Zwischenstände 1347 Tests zeigten erwartete noch nicht portierte
V1-Assertions und anschließend zwei Eventstreamtests mit alter Log-Lifecycle-
Erwartung. Cursor-/Reconnect-/Replayassertions wurden erhalten; Logs sind nun
Diagnose, fachliches Exactly-once kommt aus Domainreduktion. Abschließender Lauf
ist ausschließlich der gesicherte Kandidat, keine Sourceänderung während der Suite.

[251 Ersatzzuordnungen](EVIDENCE/legacy-test-successors.json) nennen jeden logisch
entfernten/umbenannten V1-Test und tatsächliche methodengenau geprüfte V2-Verantwortung.
Einzelne V1-Wire-/Mode-/Timer-/Fallbackwirkungen sind absichtlich pensioniert,
keine Behauptung identischen V1-Verhaltens. Erhaltene Clipboard/OBS/History/Audio/
Singleinstance-/Nativekey-/Threadutilities laufen in der gesamten Regression.
FINAL-03..09 sind einzeln in Requirements/Matrix belegt, CLIENT OPEN bleibt bis
zur unabhängigen Abnahme bestehen.

Der installierte/frozen Checkpoint verwendet tatsächliche Clientdienste und echte
HTTP-/WS-/Settings-/Snapshotports in separaten Prozessen außerhalb Checkout.
Native Qtplattform windows, sichtbarer Einstellungsdialog, getrennter Corethread,
Config, acht QSoundEffect-Readyassets ohne Playback, Icon und drei JSONs sind belegt.
Audio bewusst unavailable (ungültiges Device), globale Keys/LED/Playback deaktiviert;
keine Aufnahme/Paste/Benutzerdaten. Server-Recorder/ASR/Scheduler sind benannte
Modellgrenzen, alle importierten Serverquellen gegen ada13b0 bytegeprüft.
Kein physischer Mikrofon-/USB-/ASR-/Wahrnehmungs-/Fremdanwendungs-/Langlauf-PASS;
diese Gates gehören AP-IV2-020. Vollständiges Crossrepo-Gate gehört AP-IV2-010.

## Kompatibilität und Übergabeports

[Kompatibilitätsmatrix](../../../../../../../docs/compatibility.md): V2 Source/
Wheel/Frozen plus ada13b0 V2 PASS im benannten modellfreien Checkpoint. Historischer
V1-Client plus V1-Server NOT_RUN (historischer Server-SHA nicht neu qualifiziert).
V2 plus echter V1-only Server NOT_RUN, funktionale Negativfälle für V1-Route/404
PASS und keine Fallbacksteuerung. Neuer Server `/ws/transcribe`: Raw-Admission
hello/ready PASS, ausdrücklich kein End-to-End-PASS eines historischen V1-Clients.

[Runtimevertrag](../../../../../../../docs/protocol-v2-runtime.md) und
[Releaseports](../../../../../../../docs/protocol-v2-release.md) führen die echten
öffentlichen Datentypen/Methoden. Bootstrap: Hello mit beiden Suppressionen →
Audioavailability → Settingsrestore/Snapshot → bestätigte Runpausen → READY;
kein PCM davor. Controls/Results vor Runtime/Feedback; Historyreservation vor
Clipboard/SendInput. Session/Generation/Activation/Settingsrevision bleiben
gebunden, keine Retargetierung alter Intents. Logs ändern weder Phasen noch Paste.
Qt Mainthread, async Corethread, Audio-/Clipboard-/LEFXworker; native Cleanupgrenzen
und bounded Shutdown unverändert. Loggingfehler nur diagnostisch. V1-Historyschema
und Profile mit Backup/atomarer Persistenz; Runpausen/Tokens niemals gespeichert.

## Abgabe und nächste Aktion

Alle fachlichen Selbstchecks bestanden; Dokument-/Link-/Statusprüfung und finale
PR-CI werden vor tatsächlicher Abgabe geprüft und extern referenziert. Kandidaten-
Commit/normaler Push/Paket-PR ausschließlich im fortgeltend menschlich autorisierten
Scope. Keine Tags, Veröffentlichung, kanonische Übernahme, Serverpromotion oder
Folgepaketimplementierung. Ab REVIEW_READY-Übergabe Branchschreiben pausiert.
Nächste Aktion: frischer unabhängiger Gesamt-Review AP110 auf der endgültigen
PR-Spitze; keine Eigenabnahme. AP-IV2-010 startet erst nach unabhängiger Abnahme,
menschlicher Freigabe und tatsächlicher kanonischer AP110-Übernahme.
