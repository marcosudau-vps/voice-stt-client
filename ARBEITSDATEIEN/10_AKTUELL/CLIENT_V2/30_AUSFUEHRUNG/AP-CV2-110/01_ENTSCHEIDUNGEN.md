# AP110 – Entscheidungen R01

- Nur ausführbare V1-Autoritäten und ihre ersetzten Tests abbauen. Alte
  Config-/Historyreader und reine Darstellungstypen bleiben lesbar.
- Sourceidentität wird für Wheel/sdist/frozen gestempelt; Dirty meldet unknown.
- Durch erhaltene OBS-/Starttests reproduzierte Anschlusskorrekturen:
  Loggingapply isoliert Fehler; GUI-Startfehler stellt ursprüngliche Keys wieder her.
- Logs dürfen auch vor dem ersten Domain-Snapshot keinen Lifecycle konstruieren.
- Native Qt-/Desktopprobe verwendet ungültiges Audiodevice, temporäre Daten,
  deaktivierte Keys/LED/Playback. Tatsächliche Clientservices bleiben unverändert.
- V1-Routecheck ist Admission, kein neuer PASS des historischen V1-Clients.
