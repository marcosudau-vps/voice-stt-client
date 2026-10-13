# RealtimeSTT Windows Desktop Client V2

Windows-Client für `stt.voice.marcosudau.com`: Mikrofon-Audio über `/ws/v2`,
segmentbezogene Vorschau im Overlay und finale Texte über Clipboard + SendInput.
Die Weboberfläche `voice.marcosudau.com` ist kein Desktop-WebSocket-Endpunkt.

AP-CV2-000 bis AP-CV2-100 sind auf `feat/client-v2` übernommen. AP-CV2-110
qualifiziert den V2-only-Kandidaten; unabhängige Abnahme und menschliche
Übernahme sind getrennte Schritte. [Aktuelle Planung](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md),
[Workflowstatus](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

## Einrichtung und Start

Windows 10/11, Python 3.12; der qualifizierte EXE-Build verwendet 3.12.10.
In einer bestehenden Projektumgebung:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe -m voice_stt_client
.\venv\Scripts\python.exe -m voice_stt_client --headless
.\venv\Scripts\python.exe -m voice_stt_client --config C:\Pfad\client.yaml
.\venv\Scripts\python.exe -m voice_stt_client --version
```

Das installierte Wheel stellt `voice-stt-client` bereit. Die EXE unter
`dist/voice-stt-client.exe` benötigt keine lokale Python-Installation.
GUI und Headless verwenden dieselbe V2Runtime. Qt läuft im Main Thread,
asyncio im eigenen Core-Thread. Ein nativer Windows-Mutex verhindert doppelte
reguläre Instanzen; globale Hotkeys verwenden Win32.

## Bedienung

- Primary (`Ctrl+Shift+Space`): im Idle manuell aktivieren; bei offener Eingabe
  die konfigurierte Aktion ausführen (Refresh, Fertigstellen, Abbrechen oder keine).
- Secondary (`Ctrl+Shift+Enter`): die unabhängig konfigurierte zweite Aktion.
- Reinsertion (`Ctrl+Alt+Space`): letzten Finaltext erneut einfügen.
- Wake-Pause und Overlay-Hotkey sind optional. Rollen bleiben auch bei Wake-only
  registriert; global deaktivierte Hotkeys werden nicht registriert.
- Tray: Status, primäre Diktataktion, Mikrofonmute, Geräte-/Server-Reconnect,
  Verlauf, Einstellungen, Logs und Beenden.

Die V2-Einstellungen zeigen lokale Trigger/Hotkeys, schemaabhängige Sessionwerte
und Serververwaltung mit getrenntem Admin-Key. Lokale Unterseiten bieten Verlauf,
Audio, Clipboard/Darstellung, Feedback und Logging. Requested, Effective und
Serverdefaults bleiben getrennt sichtbar. Laufzeitpausen werden nicht gespeichert.
Änderungen mit neuer Verbindung verlangen cancel/finish/defer sowie eine getrennte
Entscheidung über ausstehende Ergebnisse (wait/discard).

Die Präsentation folgt der serverbestätigten Eingabephase unabhängig von Manual
oder Wake Word. Countdownanzeigen erteilen keine Commands. Hintergrundergebnisse
ersetzen keine aktive Vorschau. Realtime-Zwischentext wird niemals eingefügt.
Finals werden anhand ihrer Session-/Activation-/Segmentidentität genau einmal
reserviert, in der Historie gespeichert und serialisiert eingefügt. Reinsertion
ist ein eigener Auftrag. Unklare Pasteversuche werden nach Neustart nicht wiederholt.

## Daten und Migration

[Kompatibilität und Migration](docs/compatibility.md) beschreibt Profile,
Backups und die konkrete Client-/Servermatrix. `voice_stt_client/config.yaml`
liefert Paketdefaults. Benutzerwerte liegen unter `~/.voice-stt/client/`;
`VOICESTT_CLIENT_HOME`, `VOICESTT_CLIENT_CONFIG` und `--config` erlauben eine
explizite Auswahl. SQLite, Logs und Credentials gehören nicht ins Repository.
Der V2-Client hat keinen V1-Transportfallback.

## Tests und Build

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
$env:QT_QPA_PLATFORM = 'offscreen'
.\venv\Scripts\python.exe -m unittest discover -s tests -p 'test_*.py'
.\venv\Scripts\python.exe -m compileall -q voice_stt_client scripts tests
.\venv\Scripts\python.exe scripts/build.py --clean
.\venv\Scripts\python.exe -m build --sdist --wheel
.\venv\Scripts\python.exe -m twine check dist/*.whl dist/*.tar.gz
```

Source, Wheel, sdist und EXE führen dieselbe Versionsquelle `VERSION` und eine
Buildidentität. Veränderte Produktquellen melden `clientCommit=unknown`; ein
qualifizierter Build enthält seinen echten Quellcommit. Die Versionsnummer
1.0.0 allein ist keine V2-Releasefreigabe. GitHub Actions prüft vollständige Tests,
Builds, Ressourcen und installierte Wheel-GUI und stellt Kandidatenartefakte bereit.
Builds lösen keine Veröffentlichung, Tags oder Merges aus.

[Runtimevertrag](docs/protocol-v2-runtime.md), [Paketierung](docs/protocol-v2-release.md).
Abschließende Paarqualifikation AP-IV2-010 und reale ASR-/Wake-/Hardware-/Clipboard-
und Langlaufqualifikation AP-IV2-020 sowie Server-Distributed bleiben offen.
Historische V1-Protokollquellen unter `server-docs-for-client-development/` sind
Entwicklungsreferenzen und werden nicht als aktuelles Produktprotokoll paketiert.
