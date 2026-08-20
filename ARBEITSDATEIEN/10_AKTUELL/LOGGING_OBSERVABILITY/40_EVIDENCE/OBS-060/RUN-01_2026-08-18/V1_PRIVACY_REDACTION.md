# OBS-060 – V1_PRIVACY_REDACTION

Run: `RUN-OBS-060-01_2026-08-18`
Skript: `probe_obs060_privacy.py` — vollständige Ausgabe in
`output/probe_obs060_privacy.out.txt` (exit 0)

Geprüft gegen `LOGGING_CONTRACTS_FREEZE_V1.md` §4 (R-1…R-12), §4.3
(Dateirechte P-8/P-9), §4.4 sowie `FD-D1`, `FD-D5` und `FD-C12`.

**Prüfprinzip.** Nicht „funktioniert die Redaction-Funktion" — das ist
OBS-010-Unittestgebiet. Sondern: **überlebt irgendetwas Sensibles die ganze
Kette und landet auf der Platte?** Jede Prüfung liest deshalb die **Dateien**:
`observability.sqlite3`, deren `-wal`/`-shm`-Begleiter und die JSONL-Dateien des
Sinks, als ein durchsuchbarer Bytestrom.

---

## 1. Secrets (R-3)

Eingespeist über drei verschiedene Wege: flach in `details`, verschachtelt über
drei Ebenen mit abweichenden Schreibweisen (`accessToken`, `API-KEY`,
`Password`), und in einem URL-Querystring.

| Wert | auf der Platte? |
|---|---|
| `access_token` | **nein** |
| `authorization` (Bearer) | **nein** |
| `api_key` | **nein** |
| `password` | **nein** |
| `cookie` | **nein** |
| `admin_key` | **nein** |

```text
[PASS] S-1.0 die Records wurden wirklich geschrieben          (rows=3)
[PASS] S-1.7 die Redaction-Markierung IST vorhanden — die Werte wurden gesehen und ersetzt
[PASS] S-1.8 kein Querystring hat eine URL überlebt (R-8)
```

S-1.7 ist wichtiger, als es aussieht: `[redacted]` **muss** vorkommen. Wäre es
nicht da, könnte das „kein Secret gefunden" auch daher rühren, dass gar nichts
geschrieben wurde. Die Schlüsselvergleiche laufen normalisiert
(Kleinschreibung, ohne `_` und `-`), deshalb greifen sie auch bei `API-KEY` und
`accessToken`.

## 2. Transcript-Policy (FD-D1, R-10)

Gesprochener Satz: *„dies ist ein streng vertraulicher diktierter satz"*,
eingespeist gleichzeitig als `message` („Final [seg=7]: …") und in drei
Detailfeldern (`text`, `displayText`, `stableText`).

```text
[PASS] S-2.1 bei store_transcription_content=false steht der Satz nirgends auf der Platte
[PASS] S-2.2 stattdessen überlebt die Zeichenzahl (R-10)
[PASS] S-2.3 der Record selbst existiert — redigiert wird der Inhalt, nicht der Record
[PASS] S-2.4 bei store_transcription_content=true IST der Inhalt gespeichert
```

S-2.4 ist die Gegenprobe: der Schalter ist wirklich der Schalter, und S-2.1
misst nicht bloß, dass ohnehin nichts ankommt. Der Default ist `false`
(`FD-D1`).

## 3. Keine Audio-Payloads

```text
[PASS] S-3.1 kein PCM-artiger Bytelauf hat die Platte erreicht
[PASS] S-3.2 1000 Audiopakete erzeugten höchstens das 5-s-Aggregat (rows=1)
```

Strukturell abgesichert durch `ARCH §8.6`: der Hot Path erhöht nur `int`-Zähler,
und das Aggregat entsteht im Worker aus einer **read-only**-Registry. Es gibt
keinen Pfad, über den ein Audiopuffer in einen Record gelangen könnte — es wird
nie einer übergeben.

## 4. Benutzerpfade (R-9)

```text
[PASS] S-4.1 die Benutzerprofilwurzel taucht nicht auf der Platte auf  (C:\Users\marco)
[PASS] S-4.2 sie wurde durch ~ ersetzt
```

Geprüft sowohl in `message` als auch in `details`. Damit verschwindet auch der
Benutzername aus dem gespeicherten Pfad.

## 5. 64-KiB-Grenze für `raw` (FD-C12)

Ein Serverrecord mit 80 KiB `payload` **und** einem Secret darin:

```text
[PASS] S-5.1 der übergroße Record wurde gespeichert
[PASS] S-5.2 die raw-Payload wurde durch die Kürzungsmarke ersetzt
             ({'_truncated': True, '_bytes': 81964})
[PASS] S-5.3 und das Secret darin ging mit ihr
[PASS] S-5.4 die 80-KiB-Payload steht nirgends auf der Platte
```

Der Record bleibt erhalten, nur seine Payload wird durch die Marke ersetzt —
die Diagnoseinformation „hier war etwas zu Großes, und zwar 81 964 Bytes" bleibt
lesbar.

## 6. Dateirechte – M-11 (P-8/P-9)

`WP-OBS-060` verlangt, die effektiven Rechte von Store und Sink **einmalig zu
protokollieren**. Hier ist dieses Protokoll:

```text
store:     …\s6\observability.sqlite3
  NT-AUTORITÄT\SYSTEM:(I)(F)
  VORDEFINIERT\Administratoren:(I)(F)
  EIGENTÜMERRECHTE:(I)(F)

sink dir:  …\s6\sink
  NT-AUTORITÄT\SYSTEM:(I)(OI)(CI)(F)
  VORDEFINIERT\Administratoren:(I)(OI)(CI)(F)
  EIGENTÜMERRECHTE:(I)(OI)(CI)(F)

sink file: …\s6\sink\observability-2026-08-18.jsonl
  NT-AUTORITÄT\SYSTEM:(I)(F)
  VORDEFINIERT\Administratoren:(I)(F)
  EIGENTÜMERRECHTE:(I)(F)
```

Gelesen mit `icacls`. Alle Einträge sind **geerbt** (`(I)`), und es gibt
**keinen** Eintrag für `Jeder`/`Everyone`, `Benutzer`/`Users` oder
`Authentifizierte Benutzer`: Zugriff haben nur SYSTEM, die
Administratorengruppe und der Eigentümer. Das Logging setzt selbst keine ACL —
es legt die Dateien innerhalb des Benutzerprofils an und erbt dessen Rechte.

**P-8** („kein Pfad außerhalb des Benutzerprofils akzeptiert") ist zusätzlich im
Code verankert: `ObservabilityManager._resolve_profile_path` prüft jeden
konfigurierten Pfad erneut, auch wenn `LoggingObservabilityConfig.validate()`
ihn schon abgelehnt hätte, und fällt bei einem Verstoß auf den eingefrorenen
Standardort zurück — mit **einer** ratenbegrenzten stderr-Zeile, ohne die
Anwendung abzubrechen.

**Einschränkung, ausdrücklich benannt:** Das Protokoll oben stammt aus einem
Verzeichnis unterhalb von `%LOCALAPPDATA%\Temp`, weil die Probe in einem
temporären Baum arbeitet. Der reale Ablageort ist
`%LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3` — dasselbe
Benutzerprofil, dieselbe Vererbungskette, also dieselben effektiven Rechte. Ein
Abgleich am realen Pfad gehört in die manuelle Abnahme M-11 auf einem
Installationssystem.

## 7. Was strukturell nicht lecken kann

- **Der Leser schreibt nie.** `PRAGMA query_only = ON` auf jeder
  Leserverbindung (`CONTRACTS §5.4`, D-2), belegt durch Mutation M-8 und den
  Test `test_the_reader_connection_cannot_write`.
- **Der Leser legt die Datei nie an.** `LocalLogProvider` prüft `exists()`,
  bevor er verbindet — sonst hätte `sqlite3.connect` eine leere Datenbank
  erzeugt, also ein Schreiben durch die Abfrageschicht (O-14).
- **Kein Freitext in SQL.** Jeder Filterwert wird als Platzhalter gebunden,
  LIKE-Muster werden escaped (`CONTRACTS §5.7`).
- **`hello` nur über eine Whitelist** (`FD-D5`): der Payload trägt nachweislich
  Sessiontokens, und die Whitelist lässt sie gar nicht erst in einen Record.
