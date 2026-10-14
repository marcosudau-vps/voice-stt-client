# Client-V2-Kompatibilität und Migration

Stand 2026-10-13, AP-CV2-110. Der aktuelle Client startet ausschließlich V2Runtime
auf `/ws/v2`. V1-Controller, V1-WebSocket-/Headlessklassen, URL-Query-Steuerung,
lokale Diktattimer und STT-Feedbackfallback sind entfernt. Logs dienen Diagnose;
fachliche Autorität haben V2-Snapshot/Events und ihre Session-/Generationguards.

## AP-IV2-010 – festes Paar, 2026-10-14

Client `0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`: automatisierter Selbstcheck PASS,
REVIEW_READY. Clientprodukt bytegleich mit kanonischem Parent `43759d345b2b88354e4f3b383a4833731621d1e3`.
11 getrennte Prozessprüfungen, 17 Grenzfälle, sieben Socketsmokes,
Windows1354 und Server1964/14 qualifiziert.
`serverCommit=unknown` durch tatsächliches Prozess-/Quellmanifest kompensiert.
[Report und Skipgrenzen](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-010/RUNS/R01-UMSETZUNG/01_REPORT.md),
[Harness](protocol-v2-integration.md). Keine Produktmigration geändert.
Source-/Wheel-/Frozenbelege AP110 behalten ihre damalige Artefaktidentität.
Reale ASR-/Hardware-/Langlaufabnahme bleibt IV2-020.

## Profile und Daten

Paketdefaults kommen aus `voice_stt_client/config.yaml`. `--config` hat Vorrang
vor `VOICESTT_CLIENT_CONFIG`; `VOICESTT_CLIENT_HOME` setzt den Benutzerroot.
Explizite fehlende/unlesbare Profile brechen sichtbar ab. Ohne explizite Auswahl
kann `%LOCALAPPDATA%/RealtimeSTT Client/config.yaml` als Legacyprofil gelesen
werden. Lesen schreibt keine Datei. Bekannte `/ws/transcribe`-URLs werden am
selben Origin nach `/ws/v2` umgesetzt; alte Querywünsche steuern keine V2-Session.
Beliebige andere Routen erhalten keine automatische Umdeutung.

Migration berücksichtigt tatsächliche Benutzerwerte vor dem Layern der Defaults.
`session.mode`, Triggerflags, Wake-Aliase, Zeiten und Hotkeys werden in das
versionierte `v2_profile` überführt. Unbekannte/mehrdeutige Wünsche bleiben als
unresolved/retired mit Herkunft erhalten und verlangen sichtbare Korrektur.
Nach bestätigtem Bootstrap erfolgen Originalbackup `.pre-v2.bak` und atomare
Profilpersistenz auf einem Worker. Bereits versionierte Profile haben Vorrang vor
alten Mode-/Timerfeldern. Runpausen und Zugriffstokens werden nicht gespeichert.
Lokale Präferenzen und individuelle Soundpfade/Nullwerte bleiben erhalten.
Hotkeyersatz ist bis zum erfolgreichen Bootstrap vorläufig; Startfehler
stellen ursprüngliche Bindungen und Profilbytes wieder her.

Die V1-Historie wird transaktional mit SQLite-Backup nach Schema2 migriert.
Integer-Legacysegmente, IDs und Injektionsversuche bleiben lesbar; neue V2-Einträge
führen UUID-Herkunft. Pendingversuche nach Crash werden unknown und nicht erneut
gepastet. Existiert allein die alte Datenbank unter
`%LOCALAPPDATA%/RealtimeSTT_Client/transcript_history.db`, wird sie in situ gelesen.
Explizites `db_path` und `VOICESTT_CLIENT_HOME` haben Vorrang. Kein stiller Import
in eine ausdrücklich neue Datenbasis. [Resultvertrag](protocol-v2-results.md).

## Kompatibilitätsmatrix

Der konkrete Kandidatencommit und Artefakthashes stehen im
[AP110-Nachweis](../ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md).
Serverreferenz: `ada13b011e1d3829f78e7f389e3b927795a2b3be`; geprüfter V2-Clientcommit `cf42a2a9d96c1ebc88035817a5d529dfe04e4306`.

| Client / Endpoint | Ergebnis und Grenze |
| --- | --- |
| V1 `f625904795880ce71acec216e43678f9ec1656d0` + damaliger V1-Endpoint (historischer Server-SHA in AP110 nicht neu qualifiziert) | NOT_RUN in AP110. Historische V1-Belege bleiben ihrem Datum zugeordnet; kein neues PASS. |
| V2 AP110 Source/Wheel/Frozen + `/ws/v2` des gepinnten Servers | PASS (lokaler modellfreier Checkpoint) für Source, Wheel, sdist-Rebuild und Frozen. Native Windows-GUI, getrennte Prozesse, echte WS/HTTP-/Settings-/Mirror-/Desktopports; Recorder/ASR/Scheduler modellfrei. Keine reale ASR-/Hardwareabnahme. |
| V2 + V1-only Server | NOT_RUN gegen einen echten historischen V1-only Server (kein neu qualifizierter Server-SHA). Funktionale Negativtests PASS; inkompatibel: V1-URL wird im direkten Transport sichtbar BLOCKED; kein V1-Hello/Startfallback. Reguläre bekannte Profil-URL migriert auf V2 und benötigt dort einen V2-Server. Fehlender V2-Endpoint bleibt Fehler. |
| V1-Endpoint `/ws/transcribe` am neuen gepinnten Server | PASS nur für Raw-Admission hello/ready am Server ada13b0. Historischer V1-Client ist NOT_RUN; kein End-to-End-V1-PASS daraus ableiten. |

`serverCommit=unknown` bleibt unknown; es beweist keinen gepinnten Serverbuild.
Erst Git-/Dateiprüfung und tatsächlich empfangene Buildmetadaten binden den
lokalen Checkpoint. Reale Modelle, Mikrofon/USB, fremde Anwendung und Langlauf
werden in AP-IV2-020 qualifiziert. [Runtime](protocol-v2-runtime.md),
[Build-/Diagnoseports](protocol-v2-release.md).
