# Konfigurationsreferenz

## Kurz und einfach erklärt

Mit der Konfiguration stellst du ein:

- ob das neue Diagnosesystem aktiv ist;
- wie viel es speichert;
- wie lange Daten bleiben;
- ob zusätzlich JSONL geschrieben wird;
- welche optionalen Inhalte gespeichert werden.

Einige Werte lassen sich im laufenden Programm ändern. Andere betreffen die Datenbank selbst und brauchen einen Neustart.

---

## 1. Struktur

Observability liegt unter dem bestehenden `logging`-Abschnitt:

```yaml
logging:
  level: INFO
  log_dir: ...
  max_bytes: 5242880
  backup_count: 3
  stdout: true
  json_format: true
  channel_levels: {}

  observability:
    enabled: true
    level: INFO
    store_enabled: true
    db_path:
    retention_days: 14
    max_entries: 200000
    max_db_bytes: 268435456
    queue_size: 8192
    batch_size: 200
    flush_interval_s: 0.5
    file_sink_enabled: false
    file_sink_dir:
    store_transcription_content: false
    store_raw_payload: true
```

---

## 2. Warum `logging.observability`

Die neuen Felder wurden additiv eingeführt.

```text
logging.level
logging.observability.level
```

stehen bewusst nebeneinander:

- klassisches Logging bleibt bestehen;
- Observability bekommt eine eigene strukturierte Aufnahmegrenze.

---

## 3. Nutzernahe Felder

| Key | Typ | Bedeutung | UI |
|---|---|---|---|
| `enabled` | bool | Observability an/aus | ja |
| `level` | Level | Mindestlevel | ja |
| `store_enabled` | bool | SQLite-Store aktiv | ja |
| `retention_days` | int | Altersgrenze | ja |
| `max_entries` | int | Mengengrenze | ja |
| `file_sink_enabled` | bool | JSONL-Sink | ja |
| `file_sink_dir` | string/null | Zielverzeichnis | ja |
| `store_transcription_content` | bool | Transkriptinhalt erlauben | ja |
| `store_raw_payload` | bool | Raw speichern | ja |

---

## 4. Config-only-Felder

Nicht als normale UI-Optionen vorgesehen:

```text
db_path
queue_size
batch_size
flush_interval_s
max_db_bytes
```

Das sind stärker betriebs-/implementierungsnahe Werte.

---

## 5. Apply-Semantik

### IMMEDIATE vorgesehen

Insbesondere:

```text
enabled
level
retention_days
max_entries
file_sink_enabled
file_sink_dir
store_transcription_content
store_raw_payload
```

### Restartgebunden

Insbesondere:

```text
store_enabled
db_path
```

Warum?

Ein aktiver Worker hält eine SQLite-Verbindung. Einen Store im laufenden Betrieb vollständig zu wechseln würde Flush, Close, Reopen und ggf. Migration zu einem neuen Runtime-Fehlerpfad machen.

---

## 6. Harte Apply-Regel

Eine reine Observability-Änderung darf nicht:

```text
session_changed
audio_changed
mode_changed
```

auslösen.

Folge:

```text
kein unnötiger STT-Reconnect
kein unnötiger Audio-Neustart
```

---

## 7. Bekannter Randfall `enabled=false → true`

Der Contract sah `enabled` als unmittelbar anwendbar.

Im akzeptierten V1-Stand gilt jedoch:

```text
Prozess startet mit enabled=false
→ Null-/No-op-Komposition
→ Worker/Store existieren nicht vollständig
→ später enabled=true aktiviert nicht automatisch alles
```

Das ist ein dokumentierter Folgepunkt, kein Grund, die ursprüngliche Semantik still umzudefinieren.

---

## 8. Level

Default:

```yaml
level: INFO
```

Handler und Ingress sollen konsistent von diesem Wert gespeist werden.

Ziel:

```text
DEBUG unter INFO
→ nicht unnötig normalisieren/persistieren
```

---

## 9. Queue

Default:

```yaml
queue_size: 8192
```

Die 75-%-Wasserstandsregel ist Teil der festgelegten Ingress-Policy und kein zusätzlicher User-Schieberegler.

---

## 10. Batching

```yaml
batch_size: 200
flush_interval_s: 0.5
```

Ziel:

- nicht jeden Record einzeln committen;
- trotzdem geringe Diagnoseverzögerung.

---

## 11. Retention

```yaml
retention_days: 14
max_entries: 200000
```

Beide Grenzen wirken.

---

## 12. Größenwarnung

```yaml
max_db_bytes: 268435456
```

Nur Warn-/Health-Signal, keine harte automatische Quota.

---

## 13. JSONL

```yaml
file_sink_enabled: false
file_sink_dir:
```

Eine Formatwahl gibt es in V1 nicht, weil der Observability-File-Sink nur JSONL unterstützt.

---

## 14. Inhaltseinstellungen

```yaml
store_transcription_content: false
store_raw_payload: true
```

Transkriptinhalt ist standardmäßig zurückhaltend konfiguriert; Raw unterliegt weiterhin Normalisierung/Redaction.

---

## 15. Diagnosehistorie löschen

Die UI bietet eine explizite Benutzeraktion.

Das Löschen ist keine versteckte Nebenwirkung eines Filter- oder Settingswechsels.

---

## 16. Rückwärtskompatibilität

Bestehende klassische Loggingfelder behalten ihre Bedeutung.

Die Observability-Unterstruktur wurde additiv ergänzt. Allgemeine ältere Config-Altlasten wurden im Logging-Paket bewusst nicht beiläufig mitrepariert.
