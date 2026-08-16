# LOGGING_QUERY_UI_ADMIN_BOUNDARIES

Deckt Auftragsabschnitte **13, 14, 15, 16**.
Keine UI gebaut, keine Admin-Funktion implementiert, kein Produktcode geändert.

---

# 13. Settings-Architektur

## 13.1 Ist-Zustand

| Baustein | Ort | Eigenschaften |
|---|---|---|
| Typisiertes Konfigmodell | `core/config.py` | 14 Dataclasses unter `AppConfig`; `validate()` delegiert an 9 Untermodelle (`:826-836`) |
| Laden | `AppConfig.load` (`:838-862`) | Projekt-`config.yaml` + Benutzer-Override aus `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml`, tief gemischt |
| **Unbekannte Felder** | `_unknown_paths` (`:894-910`) | Enthält der Benutzer-Override **irgendein** unbekanntes Feld, wird der **gesamte** Override verworfen und nur geloggt (`:853-860`) |
| Speichern | `save` / `save_user` (`:958-1011`) | atomar (Tempfile + fsync + `os.replace`), validiert vorher |
| Metadaten | `core/settings_metadata.py` | `SETTING_DEFINITIONS`, 40 Einträge, je mit `path` (Punktnotation), `label`, `description`, `setting_type`, `category` (= Tab), `group`, `order`, `apply_policy`, optional `minimum/maximum/step/options/unit/visible_when/editor/sensitive` |
| Kandidatenbildung | `build_candidate` (`:72-79`) | `deepcopy` + `set_config_value` je Pfad + `candidate.validate()` |
| Dialog | `ui/settings_dialog.py` | Fünf Tabs, aus `category` erzeugt (`:57-63`, `:110-159`); Editoren aus `setting_type`/`editor` (`:161-223`) |
| Dynamische Sichtbarkeit | `_update_visibility` (`:225-241`) | genau **eine** Abhängigkeit je Definition (`visible_when=(pfad, wert)`) |
| Apply-Kette | `apply_changes` (`:266-309`) → `DesktopApplication._apply_settings` (`ui/application.py:509`) → `save_user()` → `CoreBridge.apply_runtime_config` (`ui/core_bridge.py:224`) → `STTController.apply_runtime_config` (`core/controller.py:1141`) → `CommandResult` → `_complete_settings_apply` (`ui/application.py:548`) | Rollback vorhanden (`_rollback_pending_settings`, `:617`) |
| Apply-Policies | `ApplyPolicy` (`settings_metadata.py:21-26`) | `IMMEDIATE`, `HOTKEY_REREGISTER`, `AUDIO_RESTART`, `SESSION_RECONNECT`, `APP_RESTART` |
| Runtime-Apply im Core | `controller.apply_runtime_config` (`:1141-1283`) | Behandelt ausdrücklich: `server`, `session`, `audio`, `event_stream`, `feedback_mappings`, `history`; alles Übrige wird über `_install_runtime_config` (`:1285-1297`) nur ins `self.config`-Objekt übernommen |
| Reconnect | über `session.reconfigure` + `_wait_for_reconfigured_session` (`:1299-1319`) | mit vollständigem Rollback auf die alte Konfiguration |
| Validierung | zweistufig: `build_candidate` → `validate()` im Dialog, danach erneut `candidate.validate()` im Controller (`:1143`) | – |

**Befund S-1.** Das Metadatenmodell ist rein deklarativ und tabbasiert. Ein
neuer Bereich kostet **keinen** neuen Dialogcode: es genügen neue
`SettingDefinition`-Einträge mit einer neuen `category` und ein Eintrag in
`SettingsDialog.TAB_NAMES`.

**Befund S-2.** `logging.level` existiert bereits als Einstellung mit
`ApplyPolicy.APP_RESTART` (`settings_metadata.py:134-139`). Es ist der einzige
Logging-Eintrag.

**Befund S-3 (Kompatibilitätsfalle).** `_unknown_paths` verwirft den
**kompletten** Benutzer-Override, sobald ein Feld unbekannt ist. Wer eine neue
Version startet, ist unproblematisch (die Felder sind dort bekannt). Wer aber
nach dem Speichern einer neuen Konfiguration **eine ältere Clientversion**
startet, verliert alle Benutzereinstellungen still bis auf eine `logger.error`-
Zeile. Das ist heute schon so; das Logging-Vorhaben verschärft es lediglich
um weitere Felder. **Nur dokumentieren, nicht reparieren** (Auftrag §21).

**Befund S-4.** `SettingDefinition` hat bereits ein Feld `sensitive: bool`
(`settings_metadata.py:46`), das von keiner Definition und von keinem
UI-Code ausgewertet wird. Es ist der vorgesehene Platz für einen späteren
Admin-Key und muss dann auch tatsächlich wirken (Maskierung, kein Speichern in
`config.yaml`, keine Aufnahme in `changes`-Logs).

## 13.2 Empfehlung: Konfigurationsmodell

```yaml
# config.yaml -- bestehender Abschnitt bleibt UNVERAENDERT
logging:
  level: INFO
  log_dir: ...
  max_bytes: 5242880
  backup_count: 3
  stdout: true
  json_format: true
  channel_levels: {}

  # NEU: eigener Unterabschnitt, damit "Logging" fuer den Nutzer EIN Thema
  # bleibt, der bestehende RotatingFileHandler aber unangetastet bleibt.
  observability:
    enabled: true
    level: INFO                      # Mindestlevel fuer den Unified-Weg
    store_enabled: true              # SQLite-Historie
    db_path:                         # null = Standardpfad
    retention_days: 14
    max_entries: 200000
    max_db_bytes: 268435456
    live_buffer_size: 2000
    queue_high_size: 1024
    queue_low_size: 8192
    batch_size: 200
    flush_interval_s: 0.5
    file_sink_enabled: false
    file_sink_format: jsonl          # jsonl | text
    file_sink_dir:                   # null = <log_dir>/observability
    store_transcription_content: false
    store_raw_payload: true
```

**Warum ein Unterabschnitt und kein eigener Top-Level-Abschnitt.**

```text
+ Ein Nutzer, der "Logging" sucht, findet alles an einem Ort.
+ `logging.level` (bestehend) und `logging.observability.level` stehen
  sichtbar nebeneinander; ihre Verschiedenheit ist die eigentliche Botschaft.
+ Keine Semantikänderung an einem existierenden Feld -- ein bestehendes
  Benutzer-config.yaml bleibt gültig, weil nur Felder HINZUKOMMEN.
- Der Pfad `logging.observability.retention_days` ist etwas lang. Für
  `settings_metadata` irrelevant, weil dort ohnehin mit Punktpfaden gearbeitet
  wird (`get_config_value`/`set_config_value` sind beliebig tief).

Verworfene Alternative: die bestehenden Felder `logging.max_bytes`,
`backup_count`, `json_format` für den neuen Datei-Sink umzudeuten. Das würde
die Bedeutung vorhandener Benutzerwerte still ändern -- genau das, was ein
Migrationsschritt nicht darf.
```

## 13.3 Empfehlung: UI-Ort

**Ausdrückliche Trennung, wie im Auftrag verlangt:**

| Gegenstand | Ort | Begründung |
|---|---|---|
| **Logging Configuration** | **Sechster Tab „Logging & Diagnose" im bestehenden `SettingsDialog`** | Passt exakt in das vorhandene Metadatenmuster (S-1). Kostet nur neue `SETTING_DEFINITIONS`-Einträge und einen Eintrag in `TAB_NAMES`. Die Sichtbarkeitslogik (`visible_when`) genügt für die Abhängigkeiten (Datei-Sink-Felder nur wenn `file_sink_enabled`, Retention nur wenn `store_enabled`). |
| **Log View** | **Eigenes, nicht-modales Fenster `LogWindow`**, erreichbar über das Tray-Menü **und** über einen Knopf im Logging-Tab | Fünf Gründe unten. |
| **Health-Anzeige** | Statuszeile **im LogWindow**, nicht im Settings-Dialog | Ein Zustand gehört zur Ansicht, nicht zur Konfiguration. |

```text
Warum die Logansicht KEIN Settings-Tab ist:

 1. Der SettingsDialog ist ein QDialog mit Apply/Close-Buttonbox
    (settings_dialog.py:100-108). "Übernehmen" auf einer Abfrageseite ist
    bedeutungslos; "Schließen" verwirft nichts.
 2. Er wird einmal erzeugt und dauerhaft gehalten
    (`self.settings_dialog`, ui/application.py:486-498). Eine Logansicht mit
    laufender Live-Aktualisierung würde dann dauerhaft im Hintergrund
    abfragen, obwohl sie unsichtbar ist.
 3. Diagnose geschieht typischerweise WÄHREND man Einstellungen ändert.
    Beides im selben modalen Fenster erzwingt ein Entweder-oder.
 4. Der Dialog ist auf 820x620 ausgelegt (`:75`). Eine Logtabelle mit
    zwölf Spalten und Detailbereich braucht eine eigene, frei skalierbare
    und speicherbare Geometrie.
 5. Der bestehende „Verlauf"-Tab (Transkripthistorie) zeigt, wohin das
    führt: eine QTableWidget in einem Settingsdialog, die bei jedem Öffnen
    über `request_history(500)` neu befüllt wird (ui/application.py:499).
    Für 200.000 Logzeilen ist dieses Muster nicht tragfähig.
```

## 13.4 Anbindung an die Apply-Kette

```text
Neue SettingDefinition-Einträge, Kategorie "Logging & Diagnose":

  logging.observability.enabled                     BOOLEAN  IMMEDIATE
  logging.observability.level                       CHOICE   IMMEDIATE
  logging.observability.store_enabled               BOOLEAN  APP_RESTART
  logging.observability.retention_days              INTEGER  IMMEDIATE
  logging.observability.max_entries                 INTEGER  IMMEDIATE
  logging.observability.live_buffer_size            INTEGER  IMMEDIATE
  logging.observability.file_sink_enabled           BOOLEAN  IMMEDIATE
  logging.observability.file_sink_format            CHOICE   IMMEDIATE   visible_when=(file_sink_enabled, True)
  logging.observability.file_sink_dir               STRING   IMMEDIATE   visible_when=(file_sink_enabled, True)
  logging.observability.store_transcription_content BOOLEAN  IMMEDIATE
  logging.observability.store_raw_payload           BOOLEAN  IMMEDIATE
  logging.observability.db_path                     STRING   APP_RESTART  show_in_dialog=False

Warum store_enabled und db_path APP_RESTART:
  Ein laufender Worker hält eine offene SQLite-Verbindung. Diese im Betrieb
  zu wechseln erfordert Flush, Close, Reopen und Migration -- ein
  Fehlerpfad, den V1 nicht braucht. Alles Übrige ist ein Feld im
  Konfigobjekt und sofort wirksam.

Verdrahtung, rein additiv:

  core/controller.py::apply_runtime_config  (:1141)
      nach `self._install_runtime_config(...)` (:1190) EINE Zeile:
          self.observability.apply_config(candidate.logging.observability)
      `apply_config` ist nicht werfend und liefert nichts zurueck; ein
      Fehler dort darf das Apply-Ergebnis nicht beeinflussen.

  ui/application.py::_complete_settings_apply  (:548)
      keine Aenderung noetig.

Wichtig: `apply_runtime_config` unterscheidet heute `session_changed`,
`audio_changed` und `mode_changed` (:1146-1160). Eine reine
Observability-Änderung darf KEINE dieser Flags setzen und damit keinen
Reconnect und keinen Audio-Neustart auslösen. Die Prüfung erfolgt über
`candidate.logging != old_config.logging`, ohne Einfluss auf
`session_changed`.
```

---

# 14. LogView gegen die bestehende PySide-Architektur

## 14.1 Ist-Zustand der UI

| Aspekt | Befund | Beleg |
|---|---|---|
| Tabs | `QTabWidget`, fünf Tabs, aus `SETTING_DEFINITIONS.category` erzeugt | `settings_dialog.py:84-89` |
| **Models** | **Es existiert kein einziges `QAbstractItemModel`/`QAbstractTableModel`** | Repository-weit |
| Views | Nur `QTableWidget` (itembasiert), für die Transkripthistorie | `settings_dialog.py:326-334`, befüllt in `set_history_entries` (`:349-362`) |
| `QTableView` | **wird nirgends verwendet** | – |
| Thread→UI | Ausschließlich Qt-Signale mit `Qt.ConnectionType.QueuedConnection` | `ui/core_bridge.py:26-35`, verbunden in `ui/application.py:173-189` |
| Core→UI-Datenweg | `CoreBridge._submit_sync` führt die Arbeit **auf dem asyncio-Loop** aus und liefert das Ergebnis über ein Signal | `ui/core_bridge.py:243-283` |
| Polling-Muster | `QTimer` alle 10 s für die LED-Verfügbarkeit | `ui/application.py:121-125` |
| Styling | Kein Stylesheet, kein Theme; Qt-Standard | – |
| Such-/Filtermuster | **existiert nicht** | – |
| Dialog-Lifetime | Einmal erzeugt, gehalten, `show()`/`raise_()`/`activateWindow()` | `ui/application.py:486-502` |
| Tray-Menü | `TrayController` mit Callback-Slots im Konstruktor | `ui/application.py:104-120` |

**Befund U-1.** Für die Logansicht gibt es **kein** wiederverwendbares
Anzeigemuster. `QTableWidget` ist itembasiert: `set_history_entries` erzeugt
je Zelle ein `QTableWidgetItem` (`:352-361`). Bei 500 Historieneinträgen ist
das vertretbar, bei Logdaten nicht. Ein `QAbstractTableModel` + `QTableView`
ist hier die erste Einführung dieses Musters im Repository und muss deshalb
ausdrücklich begründet und klein gehalten werden.

**Befund U-2.** Das Repository hat ein sauberes, konsequentes Muster für den
Thread-Übergang (`CoreBridge`: Arbeit auf dem Fremd-Thread, Ergebnis per
Queued Signal). Der Query-Layer muss demselben Muster folgen, darf aber **nicht**
über `CoreBridge` laufen: `CoreBridge` gehört dem Core-Loop, und eine
SQLite-Leseabfrage hat dort nichts zu suchen (sie würde den Loop blockieren,
auf dem Audio und WebSocket liegen).

## 14.2 Empfohlene Module und Klassen

```text
ui/logs/
├── log_window.py         LogWindow(QWidget)         eigenes Fenster, Tray-Eintrag
├── log_page.py           LogPage(QWidget)           Komposition: Filter + Tabelle + Detail
├── log_table_model.py    LogTableModel(QAbstractTableModel)
├── log_filter_bar.py     LogFilterBar(QWidget)      -> Signal filter_changed(QueryFilter)
├── log_detail_view.py    LogDetailView(QWidget)     Felder + details + raw JSON
└── log_query_controller.py
                          LogQueryController(QObject)
                              Signale: page_ready(QueryPage), query_failed(str)
                              haelt einen ThreadPoolExecutor(max_workers=1)
                              und ruft LogQueryService darauf auf

core/observability/query/
├── base.py               LogProvider, QueryFilter, QueryPage, ProviderStatus,
│                         LogRecordView          (siehe §15)
├── local.py              LocalLogProvider       (SQLite, read-only Verbindung)
└── service.py            LogQueryService        (Provider-Registry + Fassung)
```

| Klasse | Verantwortung | ausdrücklich NICHT |
|---|---|---|
| `LogTableModel` | Hält **eine** Liste von `LogRecordView` (die geladenen Seiten), liefert `data()`/`headerData()`/`rowCount()`; `append_page()`, `prepend_live()`, `reset()` | kennt kein SQLite, keinen Provider, keinen Filter |
| `LogQueryController` | Qt-Objekt, das Abfragen auf einem eigenen Worker ausführt und Ergebnisse per Queued Signal liefert; entprellt Filteränderungen (300 ms) | kennt keine Widgets |
| `LogQueryService` | Provider-Registry, wählt Provider anhand `QueryFilter.provider_id`, aggregiert `ProviderStatus` | kennt kein Qt |
| `LocalLogProvider` | Übersetzt `QueryFilter` in die Keyset-Abfrage aus `LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md §9.6` | kennt kein Qt, keinen Ringbuffer |
| `LogFilterBar` | Widgets für Producer, Channel, Level, Typ, Freitext, Zeitbereich, Session/Activation/Segment; sendet einen fertigen `QueryFilter` | führt keine Abfrage aus |
| `LogDetailView` | Zeigt alle Felder eines Records, `details` als Baum, `raw` als eingerücktes JSON; lädt `raw_json` **bei Bedarf nach** | – |
| `LogPage` | Verdrahtet die vier Teile, hält den Live-Modus | keine Datenhaltung |
| `LogWindow` | Fenstergeometrie, Titel, Schließverhalten (`hide()` statt `close()`) | – |

## 14.3 Die geprüften Punkte

| Punkt | Empfehlung V1 | Begründung |
|---|---|---|
| **Live Updates** | `QTimer` (250 ms) im `LogPage`, der `ObservabilityIngress.live_since(marker)` abfragt und nur neue Records anhängt. **Kein Signal je Record.** | Ein Signal je Record ist bei Burst-Last eine Flut über `QueuedConnection` in den Qt-Loop – genau das Frequenzproblem aus Audit §4.1, nur in der UI. Vorbild für Polling: `_led_watch` (`ui/application.py:121-125`). |
| **Pagination** | Keyset über `id`, „Weitere laden"-Knopf **und** automatisches Nachladen beim Erreichen des Listenendes; Seitengröße 200 | Kein `OFFSET` (siehe Schema §9.6). |
| **History** | Zwei Modi mit einem Umschalter: **Live** (Ringbuffer, folgt) und **Historie** (Provider-Abfrage). Kein Mischbetrieb in V1 | Ein Mischbetrieb müsste Live-Records gegen die gerade geladene Seite deduplizieren und beim Filterwechsel neu einordnen. Das ist der teuerste Teil einer Logansicht und für V1 nicht nötig. |
| **Auto-scroll** | Umschaltbar, standardmäßig **an**; schaltet sich automatisch ab, sobald der Nutzer nach oben scrollt, und über den Knopf wieder ein | – |
| **Selection/Details** | Einfachauswahl; `LogDetailView` unterhalb der Tabelle (`QSplitter`) | – |
| **Raw JSON** | Nur im Detailbereich, **nachgeladen** über `SELECT raw_json FROM logs WHERE id = ?` | `raw_json` ist das größte Feld; es in jeder Listenzeile mitzuladen würde die Seitenabfrage vervielfachen (§9.6). |
| **Spalten V1** | `Zeit (received_at)`, `Quelle (producer_kind)`, `Channel`, `Level`, `Typ`, `Component`, `Meldung` – sieben. Session/Activation/Segment nur im Detail und als Filter | Zwölf Spalten sind auf einem Laptopdisplay unlesbar. Die IDs sind Filterkriterien, keine Lesespalten. |
| **Kontextaktionen** | Kontextmenü auf einer Zeile: „nur diese Session", „nur diese Activation", „nur dieses Segment", „nur diesen Eventtyp" – setzt jeweils den Filter | Direkt aus Zielbild §36; billig, weil es nur `QueryFilter` befüllt. |
| **Styling/Farben** | V1: nur Zeilenfarbe nach `level` (WARNING/ERROR/CRITICAL), sonst keine | Zielbild §43 nennt „komplexe Farbregeln" ausdrücklich als spätere Ausbaustufe. |
| **Export** | **nicht in V1** | Zielbild §43. |

## 14.4 Thread-Grenzen der Ansicht

```text
Qt-Mainthread
   LogWindow / LogPage / LogFilterBar / LogTableModel / LogDetailView
   QTimer 250 ms  ->  Ingress.live_since()  (nur Speicherzugriff unter Lock)
        │
        │ Signal filter_changed(QueryFilter)   (direkt, gleicher Thread)
        ▼
LogQueryController (QObject, lebt im Qt-Thread)
        │  submit -> ThreadPoolExecutor(max_workers=1)
        ▼
Query-Worker-Thread
        LogQueryService -> LocalLogProvider -> eigene SQLite-Verbindung
                           file:...observability.sqlite3?mode=ro   (uri=True)
        │
        │ Ergebnis per QMetaObject.invokeMethod / Signal (QueuedConnection)
        ▼
Qt-Mainthread: LogTableModel.append_page(...)

Damit gilt:
  * Die UI kennt weder SQLite noch den Ringbuffer-Typ (Invariante O-10).
  * Der LoggingWorker und der Query-Worker teilen KEINE Verbindung; WAL
    erlaubt gleichzeitiges Lesen und Schreiben.
  * Der Core-asyncio-Loop wird von der Logansicht NICHT berührt. CoreBridge
    bleibt unverändert.
```

---

# 15. Query Provider Interface

```python
# core/observability/query/base.py   (Entwurf, nicht implementiert)

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional, Protocol, Sequence


class ProviderState(str, Enum):
    AVAILABLE     = "available"
    AUTH_REQUIRED = "auth_required"
    UNAVAILABLE   = "unavailable"
    ERROR         = "error"


@dataclass(frozen=True)
class ProviderCapabilities:
    """Was ein Provider kann. Die UI blendet danach Filter aus,
    statt Abfragen zu stellen, die sicher scheitern."""
    filter_fields: frozenset[str]      # Namen aus QueryFilter, die wirken
    supports_text_search: bool = False
    supports_time_range: bool = True
    supports_raw_payload: bool = False # kann `raw` nachliefern
    max_limit: int = 500
    scopes: frozenset[str] = frozenset({"session"})   # session|instance|global


@dataclass(frozen=True)
class ProviderStatus:
    provider_id: str
    display_name: str
    state: ProviderState
    capabilities: ProviderCapabilities
    detail: str = ""                   # kurz, redigiert, fuer die Statuszeile


@dataclass(frozen=True)
class QueryFilter:
    """Rein deklarativ. Kein Provider darf sie veraendern."""
    producer_kinds: tuple[str, ...] = ()
    producer_ids:   tuple[str, ...] = ()
    instance_ids:   tuple[str, ...] = ()
    channels:       tuple[str, ...] = ()
    levels:         tuple[str, ...] = ()
    types:          tuple[str, ...] = ()      # exakte Typen
    type_prefix:    Optional[str]   = None    # z. B. "client.trigger."
    components:     tuple[str, ...] = ()
    scopes:         tuple[str, ...] = ()

    session_id:      Optional[str] = None
    generation:      Optional[int] = None
    activation_id:   Optional[str] = None
    segment_id:      Optional[int] = None
    command_id:      Optional[str] = None
    correlation_id:  Optional[str] = None
    transcription_id: Optional[str] = None
    event_id:        Optional[str] = None

    since:  Optional[str] = None      # ISO-8601 UTC, inklusive
    until:  Optional[str] = None      # ISO-8601 UTC, exklusive
    text:   Optional[str] = None      # Freitext ueber message/type/component

    include_replayed: bool = True
    newest_first: bool = True


@dataclass(frozen=True)
class LogRecordView:
    """Was die UI sieht. Bewusst NICHT das Speichermodell:
    `provider_id` ist Herkunft der ABFRAGE, nicht des Ereignisses,
    und `raw` ist optional, weil Listen es nicht laden."""
    provider_id: str
    record_id: str
    received_at: str
    source_timestamp: Optional[str]
    producer_kind: str
    producer_id: str
    instance_id: str
    scope: str
    channel: str
    level: str
    type: Optional[str]
    component: Optional[str]
    session_id: Optional[str]
    generation: Optional[int]
    activation_id: Optional[str]
    segment_id: Optional[int]
    transcription_id: Optional[str]
    command_id: Optional[str]
    event_id: Optional[str]
    correlation_id: Optional[str]
    server_cursor: Optional[int]
    replayed: bool
    message: Optional[str]
    details: Mapping[str, Any] = field(default_factory=dict)
    raw: Optional[Mapping[str, Any]] = None
    cursor: str = ""      # opaker Paginierungsschluessel DIESES Records


@dataclass(frozen=True)
class QueryPage:
    provider_id: str
    records: tuple[LogRecordView, ...]
    next_cursor: Optional[str]     # None = keine weitere Seite
    complete: bool                 # False, wenn der Provider abgeschnitten hat
    status: ProviderStatus


class LogProvider(Protocol):
    """Vier Methoden. Mehr braucht V1 nicht, und mehr wuerde spaetere
    Provider zwingen, Dinge zu implementieren, die sie nicht koennen."""

    @property
    def provider_id(self) -> str: ...

    def status(self) -> ProviderStatus:
        """Muss ohne Netz-/DB-Zugriff antworten koennen (gecacht)."""

    def query(
        self,
        filter: QueryFilter,
        cursor: Optional[str] = None,
        limit: int = 200,
    ) -> QueryPage:
        """Blockierend. Wird IMMER auf einem Worker-Thread gerufen.
        Darf nicht werfen: Fehler kommen als QueryPage mit
        status.state == ERROR und leeren records zurueck."""

    def fetch_raw(self, record_id: str) -> Optional[Mapping[str, Any]]:
        """Nachladen des Rohpayloads fuer die Detailansicht.
        None, wenn der Provider das nicht kann (capabilities)."""
```

```python
# core/observability/query/service.py

class LogQueryService:
    """Die einzige Schnittstelle, die die UI kennt."""
    def register(self, provider: LogProvider) -> None: ...
    def providers(self) -> tuple[ProviderStatus, ...]: ...
    def query(self, provider_id: str, filter: QueryFilter,
              cursor: Optional[str] = None, limit: int = 200) -> QueryPage: ...
    def fetch_raw(self, provider_id: str, record_id: str
                  ) -> Optional[Mapping[str, Any]]: ...
```

## 15.1 Warum genau so – und was bewusst fehlt

| Entscheidung | Begründung |
|---|---|
| `cursor: Optional[str]`, **opak** | Der lokale Provider kodiert die `id`, ein `ServerHistoryProvider` würde `afterCursor` kodieren (der Server liefert `nextCursor`, `structured-logging.md:200-203`). Ein typisierter Integer-Cursor würde eines von beidem falsch abbilden. |
| `query()` wirft **nie** | Ein Providerfehler ist ein Anzeigezustand, kein Programmfehler. Entspricht dem Repository-Muster (`history.get_persistent_entries` liefert `[]` bei Fehler, `history.py:690-692`). |
| `status()` ohne I/O | Die UI ruft es bei jedem Filterwechsel; ein Netzzugriff dort würde die Oberfläche anhalten. |
| `ProviderCapabilities.filter_fields` | Der `ServerHistoryProvider` kann nur, was `/api/logs/events` unterstützt: `channels`, `events`, `sessionId`, `transcriptionId`, `from`, `to`, `afterCursor`, `limit≤1000` (`structured-logging.md:186-195`). Er kann **kein** `activation_id`, **kein** `command_id` und **keinen** Freitext. Ohne Capabilities würde die UI Filter anbieten, die dort still ignoriert werden. |
| `max_limit` im Provider | Server: 1000 (`structured-logging.md:195`). Lokal: frei. Die UI muss die kleinere Grenze respektieren. |
| `scopes` in den Capabilities | Der Desktop-Client kann über `/ws/logs` und `/api/logs/*` **nur** die eigene Session lesen (`server.py:6537-6544`). `global` wird erst mit Admin-Auth verfügbar. Der Zustandswechsel `AUTH_REQUIRED → AVAILABLE` betrifft dann genau dieses Feld. |
| **Kein** `subscribe()`/`stream()` im Provider | Live läuft über den Ingress-Ringbuffer, nicht über einen Provider. Ein Provider ist eine Abfrage-, keine Abonnementschnittstelle. Ein späterer serverseitiger Live-Modus wäre ein zweiter Adapter am Ingress, kein Provider. |
| **Kein** `count()` | Eine Gesamtzahl über 200.000 Zeilen kostet einen vollen Scan und wird für Keyset-Pagination nicht gebraucht. |
| **Kein** `delete()`/`clear()` im Provider | Retention ist Sache des Stores, nicht der Abfrageschicht. Eine Löschfunktion in der Abfrageschnittstelle wäre für Remote-Provider ohnehin unzulässig. |

---

# 16. Admin-/Server-Control-Grenze

## 16.1 Ist-Zustand am Code

| Baustein | Befund | Beleg |
|---|---|---|
| Admin-Key serverseitig | `settings.admin_api_key` oder Umgebungsvariable `VOICESTT_ADMIN_API_KEY`; Vergleich mit `secrets.compare_digest` | `server.py:5956-5962` |
| Übertragung | Header `X-VoiceSTT-Admin-Key` **oder** `Authorization: Bearer …` | `server.py:5965-5968`, `:6351-6356` |
| Kein Key konfiguriert | Adminzugriff nur von `127.0.0.1`/`::1`/`localhost`; remote ausdrücklich verboten | `server.py:5978-5984`, `:6363-6371` |
| Aushandlung | `GET /api/config` liefert `"adminAuthRequired": bool` | `server.py:5953` |
| Session-Log-Token | Header `X-VoiceSTT-Log-Token`, geprüft über `service.validate_log_access(token, session_id)`; 24 h gültig, prozesslokal | `server.py:6372-6377`, `:5043-5053` |
| Scope-Auflösung HTTP | `_log_access_scope()` liefert `{"admin": bool, "sessionId": …}` | `server.py:6349-6377` |
| Scope-Auflösung WS | derselbe Key darf als `accessToken` im `subscribe`-Frame stehen; dann `is_admin=True`, `allSessions` und `system` erlaubt | `server.py:6511-6544` |
| Nicht-Admin-Beschränkung | Channels hart auf `{audit, performance, transcription}`; `sessionId` erzwungen | `server.py:6399-6407`, `:6537-6544` |
| History-Endpunkte | `GET /api/logs/events`, `/api/logs/sessions/{id}`, `/api/logs/transcriptions/{id}` | `structured-logging.md:178-203` |
| Antwortfelder | `authorizationScope`, `allSessions`, `oldestCursor`, `latestCursor`, `retentionCursor`, `nextCursor`, `deliveryMode` | `structured-logging.md:200-203` |
| **Capability-Modell** | Es gibt **kein** benanntes Capability-Modell für Adminrechte. Was existiert, ist `sessionCapabilities` in `hello`/`ready` — Fähigkeiten der **Session** (u. a. `activationTriggers`), nicht Rechte eines Administrators | `server.py:5063`, clientseitig `stt_session.py:572-586` |
| Bundled Browserclient | In diesem Worktree **179 Zeilen**, ohne `/ws/logs`, ohne `logAccess`, ohne Admin-Drawer. Die in `docs/structured-logging.md:282-288` beschriebene Admin-Schublade existiert im Code **nicht** | `app_browserclient/client.js`, `index.html` |
| Client-Seite | **Kein Admin-Code.** `voice-stt-client/AGENTS.md` schließt einen Admin-Service für die aktuelle Entwicklungsphase ausdrücklich aus | `AGENTS.md`, Abschnitt „Verbindliche Technologieentscheidungen" |

**Befund A-1.** Es gibt clientseitig **nichts**, womit V1 kollidieren könnte.
Die Grenze muss ausschließlich gegen den **serverseitigen** Contract gezogen
werden, und der ist stabil und dokumentiert.

**Befund A-2.** Der Server kennt kein benanntes Capability-Set für Admins,
sondern nur den binären Zustand „admin ja/nein" plus die abgeleiteten
Erweiterungen (`allSessions`, `allChannels`, Channel `system`). Das im
Zielbild §27 skizzierte Capability-Modell (`globalLogsRead`, `historyLogsRead`,
…) hat **heute keine Entsprechung im Server**. Es müsste entweder serverseitig
eingeführt oder clientseitig aus dem binären Adminstatus abgeleitet werden.
Das ist eine echte offene Entscheidung (siehe `LOGGING_OPEN_DECISIONS.md`,
OD-09), aber **keine, die V1 blockiert** — solange V1 keine Auth-Schnittstelle
baut.

## 16.2 Verbindliche Integrationsgrenzen für V1

```text
BESTAETIGT:

  LoggingCore
      kennt keinen Admin-Key, kein Token, keinen Header, keine URL.
      Er kennt: CanonicalLogRecord, LogStore, Sinks, Health.
      Er importiert NICHTS aus core/server_control/ und nichts aus
      core/stt_session.py.
      Er sieht den Session-Log-Token auch NICHT indirekt: der Hook aus
      Audit §2.4 liefert SessionContext und EventProtocolResult;
      `SessionContext.log_access` traegt zwar den Token, wird vom
      Normalizer aber ausdruecklich NIE gelesen -- nur `generation`,
      `session_id`, `event_state`, `unavailable_code`.

  ServerHistoryProvider   (NICHT in V1)
      darf spaeter eine ServerControlConnection nutzen.
      Er implementiert LogProvider (§15) und sonst nichts.
      Er meldet ProviderState.AUTH_REQUIRED, solange keine bestaetigte
      Berechtigung vorliegt, und AVAILABLE danach. Der Zustandswechsel
      ist das EINZIGE, was Auth fuer den Query-Layer bedeutet.

  ServerControlConnection (NICHT in V1)
      besitzt Auth und Capabilities. Sie ist die einzige Stelle, an der
      ein Admin-Key existiert, und sie liegt in einem EIGENEN Paket
      core/server_control/, nicht unter core/observability/.

WAS V1 DESHALB NICHT BAUEN DARF:

  * kein Feld, keine Config-Option und kein Settings-Eintrag fuer einen
    Admin-Key;
  * keine HTTP-Schicht im Client (heute existiert keine -- der Client
    spricht ausschliesslich WebSocket; `server.health_url` ist konfiguriert,
    wird aber nirgends aufgerufen);
  * keine Provider-Registry, die Provider fest verdrahtet statt sie zu
    registrieren (sonst muesste sie fuer den zweiten Provider umgebaut
    werden);
  * kein Filterfeld in der UI, das nur ein Remote-Provider beantworten
    koennte;
  * kein "alle Sessions"-Schalter, auch nicht deaktiviert.

WAS V1 VORSORGLICH RICHTIG MACHT:

  * LogProvider.status() liefert ProviderState -- AUTH_REQUIRED ist von
    Anfang an ein gueltiger Wert, auch wenn ihn V1 nie erzeugt;
  * ProviderCapabilities.scopes enthaelt in V1 nur {"session","instance"};
  * QueryFilter enthaelt bereits die Felder, die der Server-Endpunkt kennt
    (session_id, transcription_id, types, since/until), damit der spaetere
    Provider sie nicht nachruesten muss;
  * QueryPage.next_cursor ist ein opaker String und passt damit sowohl auf
    die lokale `id` als auch auf `nextCursor` des Servers;
  * SettingDefinition.sensitive (settings_metadata.py:46) bleibt unbenutzt,
    ist aber der vorgesehene Ort -- und muss, WENN er benutzt wird, zuerst
    tatsaechlich wirken (Befund S-4).
```

## 16.3 Was der Client heute schon hätte, aber nicht nutzt

| Vorhanden | Ort | Für später relevant |
|---|---|---|
| `hello.logAccess.historyPath` (`/api/logs/events`) | vom Server geliefert (`structured-logging.md:213`) | Der Client **verwirft** dieses Feld heute: `DualSessionCoordinator._build_access` liest nur `websocketPath`, `accessToken`, `serverInstanceId`, `logProtocolVersion`, `deliveryMode`, `replayAvailable`, `oldestCursor`, `latestCursor` (`session_coordinator.py:286-306`). Ein späterer `ServerHistoryProvider` **für die eigene Session** braucht keinen Admin-Key, sondern nur diesen Pfad und den vorhandenen Session-Token. |
| `EventStreamAccess.oldest_cursor` / `latest_cursor` | `event_protocol.py:63-64` | Erlauben es, dem Nutzer zu zeigen, wie viel Serverhistorie es überhaupt gibt. |
| `sessionCapabilities` | `stt_session.py:572-586` | Vorbild für ein Capability-Muster, das der Client bereits versteht. |

> **Wichtige Folgerung.** Der naheliegendste zweite Provider ist **nicht** der
> Admin-Provider, sondern ein `SessionHistoryProvider`, der mit dem bereits
> vorhandenen Session-Token `/api/logs/sessions/{sessionId}` abfragt. Er braucht
> **keine** Admin-Authentifizierung. Das sollte die V2-Planung wissen, bevor sie
> mit dem Admin-Key beginnt.
