# ADR-003 – ReSpeaker XVF3800 über isolierte USB-Control-Transfers

Status: in Teilen abgelöst durch
[ADR-004](ADR-004_LED_AUSGABE_UEBER_LEFX_V3.md) (2026-08-10)  
Datum: 2026-08-09

> **Was noch gilt:** der Replay-Schutz (eine einmalige Meldung wird nie aus
> einer Wiedergabe nachgespielt), die Regel einer einzigen Meldung je
> zusammenhängender Fehlerphase, der zeitlich begrenzte Shutdown und der
> Grundsatz, dass der Client ohne LED-Gerät vollständig funktionsfähig bleibt.
>
> **Was nicht mehr gilt:** der eigene USB-Adapter, die vier Firmware-Modi, die
> zehn `LedEffectId`-Wirkungen und die Isolation des nativen Aufrufs in einem
> eigenen Prozess. Die LED-Ausgabe läuft seit ADR-004 ausschließlich über den
> eingebetteten LEFX-V3-Controller.

## Kontext

AP07-M9 benötigt einen ausfallisolierten LED-Adapter. Auf dem Zielsystem wurde
ein `reSpeaker XVF3800 4-Mic Array` mit USB `VID_2886/PID_001A`, separatem
`reSpeaker Control`-Interface, DFU- und HID-Schnittstellen festgestellt. Der
read-only Aufruf des offiziellen Windows-Hosttools meldete Firmware `2.0.10`
und Control-Interface 3.

Die offizielle
[XVF3800-Host-Control-Dokumentation](https://github.com/respeaker/reSpeaker_XVF3800_USB_4MIC_ARRAY/blob/master/host_control/README.md)
und die
[Seeed-Python-Dokumentation](https://wiki.seeedstudio.com/respeaker_xvf3800_python_sdk/)
beschreiben Vendor-Control-Transfers und die Befehle `LED_EFFECT`,
`LED_BRIGHTNESS`, `LED_SPEED` und `LED_COLOR`. Das untersuchte offizielle
Repository enthielt am Commit
`e4c2073e1470180746580a6ba5468c9bf45026e1` keine eindeutige Lizenzdatei für
die Python-Referenzimplementierung.

## Entscheidung

- Der Client verwendet eine kleine eigene Implementierung der dokumentierten
  USB-Protokollwerte und kopiert keinen Herstellercode und keine
  Herstellerbinärdatei.
- USB-Zugriff erfolgt über `pyusb` (BSD) und `libusb-package` (Pythoncode
  Apache-2.0, gebündelte libusb-Laufzeit LGPL-2.1). Beide unterstützen Python
  3.12 und werden durch PyInstaller samt `libusb-1.0.dll` gebündelt.
- Der Hardwareadapter kennt ausschließlich die bereits typisierten
  `LedEffectId`-Wirkungen. Die Zuordnung von Server-/Clientevents zu diesen
  Wirkungen bleibt allein im YAML-Abschnitt `feedback_mappings`.
- Ein einzelner daemonisierter Worker besitzt den USB-Zugriff. Es existiert
  höchstens ein ausstehendes Update; neue Updates ersetzen ältere noch nicht
  ausgeführte Updates.
- Vor dem nativen Backendzugriff prüft der Client das konkrete VID/PID-Paar
  über `CM_Get_Device_ID_List` mit Enumerator- und Present-Filter. Die
  Filtersemantik folgt der
  [Microsoft-CfgMgr32-Dokumentation](https://learn.microsoft.com/en-us/windows/win32/api/cfgmgr32/nf-cfgmgr32-cm_get_device_id_lista).
- Der native USB-Zugriff läuft in einem wiederverwendeten, abbrechbaren
  Hilfsprozess. Prozessstart, Pipefehler und hängende Backendaufrufe werden
  innerhalb des konfigurierten Shutdownbudgets normalisiert; der Hauptclient
  und sein LED-Worker bleiben beendbar.
- `success_pulse`, `warning_pulse` und `error_pulse` sind nur bei einem echten
  Liveimpuls kurzzeitig. Replay beziehungsweise der atomare Wechsel zu `LIVE`
  darf sie nicht nachträglich abspielen.
- Nach einem Impuls wird der letzte persistente Effekt wiederhergestellt.
- Fehler werden pro zusammenhängender Fehlerphase einmal als
  `client.led.unavailable` gemeldet. Der Client bleibt mit Nulladapter und ohne
  ReSpeaker vollständig funktionsfähig.
- Shutdown ist zeitlich begrenzt und setzt, soweit das Gerät noch erreichbar
  ist, `LED_EFFECT=off`. Es werden niemals `SAVE_CONFIGURATION`,
  `CLEAR_CONFIGURATION`, DFU- oder Firmwarebefehle verwendet.

## Alternativen

- Das offizielle `xvf_host.exe` als Unterprozess beziehungsweise gebündelte
  DLLs wurden verworfen: unnötiger Prozessstart pro Effekt und keine klare
  Lizenzgrundlage für eine Weiterverteilung aus dem Herstellerrepository.
- Direkt kopierter Hersteller-Pythoncode wurde wegen der fehlenden eindeutigen
  Lizenz verworfen.
- Eine unbeschränkte Hardwarequeue wurde wegen veralteter Lichtzustände bei
  schneller Ereignisfolge verworfen.
- Allgemeines USB-Hot-Plug- oder Sleep/Wake-Management bleibt AP08; M9 versucht
  nach einem späteren Update lediglich erneut, das konkrete Gerät zu öffnen.

## Folgen

- Neue direkte Laufzeitabhängigkeiten sind `pyusb` und `libusb-package`.
- Python 3.12 kann auf dem Zielhost bei seinen WMI-basierten
  Plattformabfragen hängen. Der verzögerte `libusb-package`-Backendaufbau und
  PyInstallers isolierte Analyse-/Onefile-Prozesse erhalten deshalb eine eng
  begrenzte Windows-Plattforminitialisierung, bevor sie Abhängigkeiten laden.
- `LedConfig` macht Aktivierung, VID/PID, Helligkeit, Geschwindigkeit sowie
  USB- und Shutdown-Timeout typisiert konfigurierbar.
- Der reale Hardware-Smoke deckte `idle_hotkey`, `idle_wake_word`,
  `waiting_for_speech`, `recording`, `finalizing`, `unavailable` sowie
  `success_pulse → recording → off` ohne Fehler ab.
- Die erneute M10-Hardwareprüfung deckte den verzögerten Backendaufbau auf,
  verifizierte anschließend fünf reale Effekte, abschließendes `off` und einen
  Prozessabschluss ohne Waisen.
- Die Onefile-Analyse enthält `usb.core`, `libusb_package`,
  `libusb_package/libusb-1.0.dll` und den Multiprocessing-Runtime-Hook; der
  Windows-Build und Versions-Smoke sind erfolgreich.

## Betroffene Dokumente und Tests

- `ui/led_feedback.py`
- `core/config.py`, `config.yaml`, `core/settings_metadata.py`
- `ui/application.py`, `voice-stt-client.spec`, `requirements.txt`
- `tests/test_led_feedback.py`
- `tests/manual_test_ap07_led_hardware.py`
- `scripts/pyinstaller_runtime_platform.py`, `scripts/pyinstaller_site/`
- `scripts/build.py`, `tests/test_build_script.py`
- `tests/test_config.py`, `tests/test_ui_application.py`,
  `tests/test_feedback_reducer.py`
