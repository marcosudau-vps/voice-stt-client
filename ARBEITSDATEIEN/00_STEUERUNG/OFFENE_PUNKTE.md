# OFFENE PUNKTE - globale Inbox

Neue, noch keinem Work Package zugeordnete Themen zunaechst hier erfassen.

Regel:

Fund -> Blocker des aktiven Gates?
- JA: in das aktive Work Package aufnehmen.
- NEIN: spaeterem Work Package oder der Inbox zuordnen.

## Befunde aus der Reorganisation (2026-08-17, kein OBS-010-Blocker)

- Der frühere Ordner `docs/2026-08-12_led-sound-debugfeedback` existiert im aktiven
  Client nicht mehr und ist über die vollständige Git-Historie dieses Repos
  (`git log --all --follow --diff-filter=A`) nicht auffindbar — kein Commit hat diesen
  Pfad je angelegt. Er wurde daher nicht rekonstruiert (keine Erfindung von Inhalten).
  Nebenbefund: ein gleichnamiger, nicht git-versionierter Ordner existiert separat unter
  dem ehemaligen `marcosudau-vps\zusammenarbeit\2026-08-12_led-sound-debugfeedback`
  (jetzt im Legacy-Bereich `_LEGACY_BEFORE_REORG_20260817\marcosudau-vps\zusammenarbeit\`
  erhalten) — dieser wurde nicht ungefragt als Ersatz übernommen.