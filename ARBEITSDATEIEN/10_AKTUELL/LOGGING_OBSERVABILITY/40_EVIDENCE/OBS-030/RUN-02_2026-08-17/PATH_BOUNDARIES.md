# PATH_BOUNDARIES – OBS-030 RUN-02 (B-3 / CONTRACTS §4.3 P-8)

## Norm

```text
P-8   Store und Sinks liegen unterhalb von %LOCALAPPDATA%\RealtimeSTT Client\
      und erben damit die Benutzer-ACL. Es wird KEIN eigenes Verzeichnis mit
      abweichenden Rechten angelegt und KEIN Pfad ausserhalb des
      Benutzerprofils akzeptiert. Ein konfigurierter absoluter Pfad wird
      gegen das Benutzerprofil geprueft.
      Vorbild: EventStreamConfig.validate verlangt bereits einen absoluten
      Pfad.
```

Zusätzlich `R-7` (Store und Sinks liegen im Benutzerprofil) und
`CONTRACTS §5.1` (`logging.observability.db_path` adressiert genau den in
OBS-030 gebauten Store).

## Umsetzung

### 1. Konfigurationsebene – `core/config.py`

```text
user_profile_roots()        -> die zulaessigen Wurzeln:
                               %USERPROFILE%, $HOME, Path.home(),
                               DEFAULT_LOCAL_APP_DIR
is_inside_user_profile(p)   -> True, wenn der AUFGELOESTE Pfad in einer
                               dieser Wurzeln liegt
_validate_user_profile_path -> ValueError, wenn nicht
```

Aufgelöst wird mit `os.path.realpath` (kollabiert `..`, `.`, Symlinks und
Windows-Junctions) und verglichen mit `os.path.normcase` (Groß-/Kleinschreibung
und `/`-vs-`\` unter Windows). Damit ist die Prüfung nicht durch eine bloß
andere Schreibweise desselben Ziels zu umgehen.

`LoggingObservabilityConfig.validate()` prüft `db_path` **und**
`file_sink_dir`, unabhängig davon, ob `file_sink_enabled` gerade `True` ist —
ein ungültiger Wert soll nicht latent in der Konfiguration liegen bleiben.
`AppConfig.validate()` ruft diese Methode bereits (CONTRACTS §10.2).

`DEFAULT_LOCAL_APP_DIR` ist immer zulässig, auch in seiner Rückfallform
(`APP_DIR / "RealtimeSTT Client"`, wenn `LOCALAPPDATA` fehlt) — es **ist** der
eingefrorene Standardort.

### 2. Laufzeitebene – `core/observability/manager.py`

`ObservabilityManager._resolve_profile_path()` wiederholt die Prüfung.

**Begründung, warum die Validierung allein nicht genügt:** `app.py::main()`
ruft `AppConfig.load()` und baut den Manager direkt daraus; ein
`AppConfig.validate()` steht dort **nicht**. Eine Prüfung ausschließlich in
`validate()` wäre im echten Startpfad wirkungslos gewesen — genau der Zustand,
den das Gate beanstandet hat.

Verhalten bei einem abgelehnten Pfad: Der Pfad wird **nicht akzeptiert**, es
wird der eingefrorene Standardort verwendet, und genau eine ratenbegrenzte
stderr-Zeile erscheint:

```text
[observability] path_outside_user_profile: logging.observability.db_path is
outside the user profile (CONTRACTS §4.3 P-8) and was not accepted; using the
default location
```

Kein Abbruch der Anwendung (O-01: Logging besitzt keine Runtime-Autorität) und
keine stille Übernahme des fremden Pfads.

## Nachweise

`tests/test_obs030_path_boundaries.py` — 23 Tests, alle grün.

| Fall | Erwartung | Test |
|---|---|---|
| Standardort `%LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3` | akzeptiert | `test_positive_db_path_inside_the_profile_is_accepted` |
| `<log_dir>/observability` im Profil | akzeptiert | `test_positive_file_sink_dir_inside_the_profile_is_accepted` |
| `~/…` (Tilde-Expansion ins Profil) | akzeptiert | `test_positive_tilde_expands_into_the_profile` |
| `None` (= Standardpfad) | akzeptiert | `test_positive_none_means_default_location` |
| `..`, das **innerhalb** des Profils bleibt | akzeptiert | `test_positive_dotdot_that_stays_inside_is_accepted` |
| Temp-Verzeichnis der Testsuite | akzeptiert (Vorbedingung) | `test_positive_temp_dir_used_by_the_test_suite_is_inside` |
| absoluter Pfad außerhalb (`<Anchor>\obs030-outside-user-profile\…`) | `ValueError` | `test_negative_absolute_db_path_outside_the_profile`, `…file_sink_dir…` |
| `C:\ProgramData\somewhere-else\observability.sqlite3` (Beispiel des Gate-Reviews) | `ValueError` | `test_negative_programdata_is_the_gate_review_example` |
| `..`-Escape aus dem Profil heraus | `ValueError` | `test_negative_dotdot_escape_is_rejected` |
| relativer Pfad `observability.sqlite3` | `ValueError` | `test_negative_relative_path_is_rejected` |
| leerer/whitespace-Pfad | `ValueError` | `test_negative_empty_string_is_rejected` |
| laufwerksrelativ `C:observability.sqlite3` (Windows) | `ValueError` | `test_negative_drive_relative_windows_path_is_rejected` |
| UNC `\\server\share\observability.sqlite3` (Windows) | `ValueError` | `test_negative_unc_path_is_rejected` |
| Profil eines **anderen** Benutzers | `ValueError` | `test_negative_windows_temp_of_another_user_is_rejected` |
| Groß-/Kleinschreibung (Windows) | akzeptiert | `test_case_insensitive_on_windows` |
| `/`-Separatoren (Windows) | akzeptiert | `test_forward_slashes_are_normalised_on_windows` |
| Manager: `db_path` außerhalb → Standardort | Fallback | `TestManagerRefusesForeignPaths::test_db_path_outside_…` |
| Manager: `file_sink_dir` außerhalb → Standardort | Fallback | `TestManagerRefusesForeignPaths::test_file_sink_dir_outside_…` |
| Manager: gültiger Pfad bleibt unverändert | unverändert benutzt | `TestManagerRefusesForeignPaths::test_accepted_path_inside_…` |

Laufzeitprobe: siehe `FAULT_INJECTION.md`, Abschnitt „B-3".

## Angepasster Bestandstest (ausdrücklich begründet)

`tests/test_obs030_config.py::TestSaveLoadRoundTrip::test_non_default_observability_values_survive_save_and_load`
benutzte `file_sink_dir="C:/tmp/obs-sink"` und verlangte anschließend
`loaded.validate()` **ohne** Ausnahme. Genau dieser Pfad ist der Fall, den P-8
verbietet; der Test hätte die Auflage dauerhaft blockiert.

Geändert wurde ausschließlich der verwendete Pfadwert (jetzt
`DEFAULT_LOCAL_APP_DIR / "obs-sink"`), nicht die Prüfabsicht: Der Test belegt
weiterhin den Save→Load-Roundtrip nicht-vorbelegter Werte inklusive
`file_sink_dir`. Der entfernte Fall lebt als **Negativtest** weiter
(`test_negative_absolute_file_sink_dir_outside_the_profile`).

Es handelt sich um einen Test aus dem gescheiterten RUN-01 desselben Work
Packages, nicht um einen vorbestehenden Produkttest; die Regel „die
vollständige bestehende Client-Suite bleibt grün, ohne dass ein bestehender
Test geändert wird" (`ARCH §12`) ist davon nicht berührt — kein Test außerhalb
von `tests/test_obs030_*.py` wurde angefasst.

## P-9 / M-11 – Status unverändert

`P-9` (`-wal`/`-shm` im selben Verzeichnis) bleibt wie in RUN-01 als
Testbeobachtung abgesichert
(`test_obs030_sqlite_store.py::test_wal_journal_mode_and_pragmas`). Weil der
Zielpfad jetzt garantiert im Benutzerprofil liegt und SQLite die Geschwister
immer neben der Datei anlegt, ist die ACL-Aussage von P-9 damit erfüllt. Eine
zusätzliche Laufzeitprüfung wurde **nicht** eingebaut — sie steht in keinem
Freeze-Dokument als Laufzeitauflage und wäre eine Erweiterung ohne Auftrag.
`M-11` (einmaliges `icacls`-Protokoll als Abnahmebeleg) ist eine
Abnahmeauflage und bleibt bei der V1-Abnahme (OBS-060).
