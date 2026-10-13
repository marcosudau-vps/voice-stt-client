# Client-V2-Kompatibilität und Migration

Stand 2026-10-13, AP-CV2-110. Der aktuelle Client startet ausschließlich V2Runtime
auf `/ws/v2`. V1-Controller, V1-WebSocket-/Headlessklassen, URL-Query-Steuerung,
lokale Diktattimer und STT-Feedbackfallback sind entfernt. Logs dienen Diagnose;
fachliche Autorität haben V2-Snapshot/Events und ihre Session-/Generationguards.

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
Serverreferenz: `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

| Client / Endpoint | Ergebnis und Grenze |
| --- | --- |
| V1 `f625904795880ce71acec216e43678f9ec1656d0` + damaliger V1-Endpoint | NOT_RUN in AP110. Historische V1-Belege bleiben ihrem Datum zugeordnet; kein neues PASS. |
| V2 AP110 Source/Wheel/Frozen + `/ws/v2` des gepinnten Servers | Lokaler Checkpoint: echte getrennte Prozesse, echte WS/HTTP-/Settings-/Mirror-/Desktopports; Recorder/ASR/Scheduler modellfrei. Details und tatsächlicher Status im AP110-Nachweis. |
| V2 + V1-only Server | Inkompatibel: V1-URL wird im direkten Transport sichtbar BLOCKED; kein V1-Hello/Startfallback. Reguläre bekannte Profil-URL migriert auf V2 und benötigt dort einen V2-Server. Fehlender V2-Endpoint bleibt Fehler. |
| V1-Endpoint `/ws/transcribe` am neuen gepinnten Server | Getrennt vom V2-Nachweis zu beurteilen; kein V1-Kompatibilitäts-PASS aus einem V2-Smoke ableiten. Tatsächlicher Routecheck im AP110-Nachweis. |

`serverCommit=unknown` bleibt unknown; es beweist keinen gepinnten Serverbuild.
Erst Git-/Dateiprüfung und tatsächlich empfangene Buildmetadaten binden den
lokalen Checkpoint. Reale Modelle, Mikrofon/USB, fremde Anwendung und Langlauf
werden in AP-IV2-020 qualifiziert. [Runtime](protocol-v2-runtime.md),
[Build-/Diagnoseports](protocol-v2-release.md).
