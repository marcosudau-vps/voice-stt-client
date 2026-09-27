# Debug feedback sounds

These eight PCM-WAV files are derived from the
[Home Assistant Voice Preview Edition Sounds](https://github.com/esphome/home-assistant-voice-pe/tree/dev/sounds)
by Clayton Charles Tapp, licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

The source files were converted to mono, 48 kHz, signed 16-bit PCM WAV,
trimmed to short diagnostic cues and loudness-normalized. The transformations
do not change the license.

| Shipped file | Source file |
| --- | --- |
| `wake_word.wav` | `wake_word_triggered.flac` |
| `start.wav` | `center_button_press.flac` |
| `stop.wav` | `mute_switch_on.flac` |
| `complete.wav` | `timer_finished.flac` |
| `cancel.wav` | `center_button_double_press.flac` |
| `warning.wav` | `jack_disconnected.flac` |
| `error.wav` | `mute_switch_off.flac` |
| `timeout_tick.wav` | `easter_egg_tick.mp3` |

The exact reproducible conversion commands are in
`scripts/build_debug_feedback_sounds.ps1`. The source collection itself is a
local, ignored working set and is not part of this repository.
