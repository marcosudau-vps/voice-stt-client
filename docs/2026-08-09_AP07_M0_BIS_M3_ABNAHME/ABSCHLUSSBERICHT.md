# AP07 – Abnahme M0 bis M3

> **Stand:** 9. August 2026  
> **Ergebnis:** M0–M3 abgenommen; M4 / AP07-C1 ist der nächste zulässige Meilenstein  
> **Scope:** Servervorstufe, Produktivvertrag, Vertragskopie und Clientbaseline;
> keine vorgezogene Clientimplementierung aus M4 oder später

## 1. Repository- und Commitstand

Der Servercommit
`dedcdd93e836b2a9df4771da8514a09645c7674f` war lokal auf `main` vorhanden,
fehlte zunächst jedoch auf dem erreichbaren Remote. Der Push auf
`https://github.com/marcosudau-vps/voice-stt-server.git` wurde mit dem dafür
autorisierten Account durchgeführt. Anschließend wurden `HEAD` und
`origin/main` erneut abgerufen und auf denselben vollständigen Hash geprüft;
`main` ist mit `origin/main` synchron.

Zugangstoken und andere Secrets wurden weder ausgegeben noch in Dateien oder
Berichte übernommen.

## 2. M0 – Baselines und Quellen

Die verbindlichen Clientquellen, beide AP07-Paketdokumente, die einschlägigen
Serververtragsseiten sowie Servercode und -tests wurden gegen den aktuellen
Stand geprüft.

Die fehlende lokale Client-`venv` wurde mit Python 3.12 wiederhergestellt und
aus `requirements.txt` befüllt. Danach bestanden:

```text
Client: 264 Tests erfolgreich
Client: compileall über app.py, core, ui und tests erfolgreich
Server: 377 Tests erfolgreich, 13 übersprungen
Server: compileall über VoiceSTT, VoiceSTT_server, api_fastapi_server und tests erfolgreich
Server: git diff --check erfolgreich
```

Ein erster Server-Testlauf traf auf eine lokale Zugriffsblockade im globalen
pytest-Tempverzeichnis. Der unveränderte Teststand wurde daraufhin mit einem
isolierten `--basetemp` im Serverrepository wiederholt und vollständig grün
abgeschlossen. Dies war ein Umgebungsfehler, kein Produktfehler.

## 3. M1 – SQLite-first-Servervorstufe

Die vorhandene Serverimplementierung und ihr früherer Abschlussnachweis wurden
gegen den aktuellen Code und die aktuelle Gesamtsuite geprüft. Der Eventstore
vergibt den globalen Cursor beim SQLite-Commit; Live und Replay lesen
committete Events aus derselben kanonischen Quelle. Storeausfall-, Cursor-,
Retention-, Replay-/Live- und optionale Spiegelpfade sind durch die
Servertests abgedeckt.

Ein absichtlicher Eventstore-Ausfall wurde nicht am Produktivsystem ausgelöst.
Die geforderte kontrollierte Fehlerinjektion bleibt durch automatisierte Tests
belegt, ohne produktive Daten zu gefährden.

## 4. M2 – Produktivvertrag und Liveabnahme

Der produktive Server meldete:

- `/health`: HTTP 200, `ok=true`, `ready=true`, Eventstore `ready/available`;
- `hello.logAccess.available=true`;
- `logProtocolVersion=2`;
- `deliveryMode=sqlite_first`;
- `replayAvailable=true`;
- sessiongebundenen Zugriff ohne Token in der URL.

Zwei getrennte Transkriptionssessions wurden jeweils über einen eigenen
Sessiontoken an `/ws/logs` gebunden. Für beide Streams bestätigte der Server
`authorizationScope=session`, `allSessions=false` und `allChannels=false`.
Jeder Stream empfing ausschließlich das eigene live committete
`session.closed`; dieselbe Event-ID war in der HTTP-/SQLite-Historie vorhanden
und wurde nach Reconnect ab dem vorherigen Cursor mit `replay=true` erneut
geliefert.

Zusätzlich wurde die vorhandene kurze WAV-Referenz aus der Servertestsuite über
eine echte produktive `/ws/transcribe`-Session übertragen. Sie erzeugte ein
terminales `transcription.completed`. Dessen Event-ID und Cursor wurden
zwischen Live-Stream, `GET /api/logs/events` und Replay nach Reconnect
korreliert. Der Test gab weder Token noch Transkriptinhalt aus.

Damit sind SQLite-first-Reihenfolge, Sessionfilterung, Zwei-Session-Isolation,
terminales Transkriptionsereignis, HTTP-/Store-Korrelation und Replay
produktiv belegt.

## 5. M3 – Serververtrag im Client

Die aktive Vertragskopie unter `server-docs-for-client-development/` enthält
den produktiven SQLite-first-Vertrag einschließlich `/ws/logs`, `logAccess`,
Protokollversion 2, Replay-/Live-Übergang, Gap-/Cursorfehler,
Storedegradation und `transcription.discarded(reason=empty_final)`.

Die versionierten Seiten aus `docs/client-development/` des Serverrepositorys
entsprechen nach normalisierter Zeilenende-Prüfung vollständig der lokalen
Vertragskopie. Die zusätzliche lokale Datei `session-wakeword-erweiterung.md`
ist die eingebundene Kopie der vom Server-README referenzierten Datei
`docs/session-wakeword-erweiterung.md` und bleibt als Teil des bereits
verwendeten AP6-Sessionvertrags erhalten.

## 6. Ergebnis und Restgrenzen

M0, M1, M2 und M3 sind abgeschlossen. Die Clientkomponenten
`EventStreamTransport`, `EventProtocolProcessor`, `EventCursorStore`,
`SessionCoordinator`, `EventNormalizer` und `FeedbackReducer` existieren noch
nicht; dies ist der erwartete Eingangszustand vor M4.

Der nächste zulässige Umsetzungsschritt ist ausschließlich M4 / AP07-C1:
Clientmodelle, typisierte Konfiguration und Cursorpersistenz.

Der noch offene gesprochene AP6-Nachweis für `hey_jarvis` mit echtem Mikrofon
wird separat weitergeführt. Er wurde durch diese technische AP07-Abnahme weder
simuliert noch fälschlich als erledigt markiert.
