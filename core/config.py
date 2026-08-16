"""
Configuration model for the RealtimeSTT client.

Loads settings from a YAML file with sensible defaults.
All paths are resolved relative to the application directory.
"""

from __future__ import annotations

import logging
import math
import os
import re
import tempfile
import dataclasses
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import yaml

from core.feedback_mapping import FeedbackMappingConfig, default_feedback_mappings

logger = logging.getLogger(__name__)

# Application directory: where app.py lives
APP_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = APP_DIR / "config.yaml"
LED_SINKS = ("respeaker", "simulator", "null")
"""Where LEFX puts its frames. 'simulator' needs the optional package installed."""
DEFAULT_LOCAL_APP_DIR = Path(os.environ.get("LOCALAPPDATA", APP_DIR)) / "RealtimeSTT Client"
DEFAULT_LOG_DIR = DEFAULT_LOCAL_APP_DIR / "logs"
DEFAULT_USER_CONFIG_PATH = (
    DEFAULT_LOCAL_APP_DIR / "config.yaml"
)

_HOTKEY_MODIFIER_ALIASES = {
    "ctrl": "Ctrl",
    "control": "Ctrl",
    "shift": "Shift",
    "alt": "Alt",
    "win": "Win",
    "windows": "Win",
    "super": "Win",
}
_HOTKEY_NAMED_KEYS = {
    "space": "Space",
    "enter": "Enter",
    "return": "Enter",
    "tab": "Tab",
    "escape": "Escape",
    "esc": "Escape",
    "backspace": "Backspace",
    "delete": "Delete",
    "del": "Delete",
    "insert": "Insert",
    "ins": "Insert",
    "home": "Home",
    "end": "End",
    "pageup": "PageUp",
    "pagedown": "PageDown",
    "up": "Up",
    "down": "Down",
    "left": "Left",
    "right": "Right",
}
_HOTKEY_MODIFIER_ORDER = ("Ctrl", "Alt", "Shift", "Win")


def normalize_hotkey_spec(value: str) -> str:
    """Validate and normalize a user-visible global hotkey specification."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("hotkey must be a non-empty string")

    cleaned = re.sub(r"<\s*([^>]+?)\s*>", r"\1", value.strip())
    raw_tokens = [token.strip() for token in cleaned.split("+")]
    if not raw_tokens or any(not token for token in raw_tokens):
        raise ValueError(f"invalid hotkey syntax: {value!r}")

    modifiers: set[str] = set()
    key: Optional[str] = None
    for raw_token in raw_tokens:
        token = raw_token.casefold().replace("_", "").replace("-", "")
        modifier = _HOTKEY_MODIFIER_ALIASES.get(token)
        if modifier is not None:
            if modifier in modifiers:
                raise ValueError(f"duplicate hotkey modifier: {modifier}")
            modifiers.add(modifier)
            continue

        if key is not None:
            raise ValueError("hotkey must contain exactly one non-modifier key")
        if len(raw_token) == 1 and raw_token.isalnum():
            key = raw_token.upper()
        elif re.fullmatch(r"f(?:[1-9]|1[0-9]|2[0-4])", token):
            key = token.upper()
        else:
            key = _HOTKEY_NAMED_KEYS.get(token)
            if key is None:
                raise ValueError(f"unsupported hotkey key: {raw_token!r}")

    if not modifiers:
        raise ValueError("global hotkey must contain at least one modifier")
    if key is None:
        raise ValueError("hotkey must contain exactly one non-modifier key")

    ordered = [name for name in _HOTKEY_MODIFIER_ORDER if name in modifiers]
    return "+".join((*ordered, key))


@dataclass
class ServerConfig:
    """WebSocket server connection settings."""

    url: str = "wss://stt.voice.marcosudau.com/ws/transcribe"
    health_url: str = "https://stt.voice.marcosudau.com/health"
    reconnect_min_delay: float = 0.5
    reconnect_max_delay: float = 30.0
    reconnect_jitter: float = 0.3
    server_busy_min_delay: float = 10.0
    ping_interval: float = 10.0
    ping_timeout_count: int = 3
    start_confirmation_timeout: float = 10.0
    hello_timeout: float = 5.0
    ready_timeout: float = 180.0

    def validate(self) -> None:
        """Validate server configuration ranges and consistency."""
        numeric_values = {
            "reconnect_min_delay": self.reconnect_min_delay,
            "reconnect_max_delay": self.reconnect_max_delay,
            "reconnect_jitter": self.reconnect_jitter,
            "server_busy_min_delay": self.server_busy_min_delay,
            "ping_interval": self.ping_interval,
            "start_confirmation_timeout": self.start_confirmation_timeout,
            "hello_timeout": self.hello_timeout,
            "ready_timeout": self.ready_timeout,
        }
        for name, value in numeric_values.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{name} must be a finite number")

        if (
            isinstance(self.ping_timeout_count, bool)
            or not isinstance(self.ping_timeout_count, int)
        ):
            raise ValueError("ping_timeout_count must be an integer >= 1")

        if self.reconnect_min_delay <= 0:
            raise ValueError("reconnect_min_delay must be > 0")
        if self.reconnect_max_delay < self.reconnect_min_delay:
            raise ValueError("reconnect_max_delay cannot be less than reconnect_min_delay")
        if self.reconnect_max_delay < self.server_busy_min_delay:
            raise ValueError("reconnect_max_delay cannot be less than server_busy_min_delay")
        if not (0.0 <= self.reconnect_jitter < 1.0):
            raise ValueError("reconnect_jitter must be >= 0.0 and < 1.0")
        if self.server_busy_min_delay <= 0:
            raise ValueError("server_busy_min_delay must be > 0")
        if self.ping_interval <= 0:
            raise ValueError("ping_interval must be > 0")
        if self.ping_timeout_count < 1:
            raise ValueError("ping_timeout_count must be >= 1")
        if self.start_confirmation_timeout <= 0:
            raise ValueError("start_confirmation_timeout must be > 0")
        if self.hello_timeout <= 0:
            raise ValueError("hello_timeout must be > 0")
        if self.ready_timeout <= 0:
            raise ValueError("ready_timeout must be > 0")


@dataclass
class EventStreamConfig:
    """Reliable `/ws/logs` transport limits without any access token data."""

    enabled: bool = True
    connect_timeout: float = 10.0
    handshake_timeout: float = 10.0
    replay_timeout: float = 60.0
    message_timeout: float = 30.0
    reconnect_min_delay: float = 0.5
    reconnect_max_delay: float = 30.0
    reconnect_jitter: float = 0.3
    max_message_size: int = 1024 * 1024
    queue_maxsize: int = 512
    cursor_persistence_enabled: bool = True
    cursor_path: Optional[str] = None

    def validate(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("event_stream.enabled must be a boolean")
        if not isinstance(self.cursor_persistence_enabled, bool):
            raise ValueError(
                "event_stream.cursor_persistence_enabled must be a boolean"
            )
        for name, value in {
            "connect_timeout": self.connect_timeout,
            "handshake_timeout": self.handshake_timeout,
            "replay_timeout": self.replay_timeout,
            "message_timeout": self.message_timeout,
            "reconnect_min_delay": self.reconnect_min_delay,
            "reconnect_max_delay": self.reconnect_max_delay,
            "reconnect_jitter": self.reconnect_jitter,
        }.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"event_stream.{name} must be a finite number")
        for name in (
            "connect_timeout", "handshake_timeout", "replay_timeout",
            "message_timeout", "reconnect_min_delay", "reconnect_max_delay",
        ):
            if getattr(self, name) <= 0:
                raise ValueError(f"event_stream.{name} must be > 0")
        if self.reconnect_max_delay < self.reconnect_min_delay:
            raise ValueError(
                "event_stream.reconnect_max_delay cannot be less than reconnect_min_delay"
            )
        if not 0.0 <= self.reconnect_jitter < 1.0:
            raise ValueError("event_stream.reconnect_jitter must be >= 0 and < 1")
        for name, value, minimum, maximum in (
            ("max_message_size", self.max_message_size, 1024, 64 * 1024 * 1024),
            ("queue_maxsize", self.queue_maxsize, 1, 100000),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not minimum <= value <= maximum
            ):
                raise ValueError(
                    f"event_stream.{name} must be between {minimum} and {maximum}"
                )
        if self.cursor_path is not None and (
            not isinstance(self.cursor_path, str) or not self.cursor_path.strip()
        ):
            raise ValueError("event_stream.cursor_path must be null or non-empty")
        if self.cursor_path is not None and not Path(self.cursor_path).expanduser().is_absolute():
            raise ValueError("event_stream.cursor_path must be an absolute path")

    @staticmethod
    def build_url(server_base_url: str, websocket_path: str) -> str:
        """Build a same-origin event URL from the server-confirmed path."""
        if not isinstance(server_base_url, str) or not server_base_url.strip():
            raise ValueError("server_base_url must be a non-empty string")
        base = urlsplit(server_base_url.strip())
        if base.scheme not in {"ws", "wss"} or not base.netloc:
            raise ValueError("server_base_url must be an absolute ws:// or wss:// URL")
        if base.username or base.password:
            raise ValueError("server_base_url must not contain credentials")
        if not isinstance(websocket_path, str) or not websocket_path.startswith("/"):
            raise ValueError("websocket_path must be an absolute server path")
        path = urlsplit(websocket_path)
        if path.scheme or path.netloc or path.query or path.fragment:
            raise ValueError("websocket_path must not change origin or contain a query")
        return urlunsplit((base.scheme, base.netloc, path.path, "", ""))


class OperatingMode(str, Enum):
    """Supported session-local operating modes."""

    HOTKEY = "hotkey"
    WAKE_WORD = "wake_word"


@dataclass
class SessionConfig:
    """Session-local recorder configuration exposed by the server."""

    mode: str = OperatingMode.HOTKEY.value
    manual_trigger_enabled: Optional[bool] = None
    wake_word_trigger_enabled: Optional[bool] = None
    wake_word_backend: Optional[str] = None
    wake_words: Optional[str] = "hey_jarvis"
    wake_word_inference_framework: Optional[str] = None
    wake_word_sensitivity: Optional[float] = None
    wake_word_activation_delay: Optional[float] = None
    wake_word_timeout: Optional[float] = None
    wake_word_buffer_duration: Optional[float] = None
    wake_word_followup_window: Optional[float] = None
    initial_speech_timeout: Optional[float] = None
    followup_timeout: Optional[float] = None
    extension_seconds: Optional[float] = None

    @property
    def effective_manual_trigger_enabled(self) -> bool:
        """Whether the hotkey may open an activation.

        An explicit flag always wins. Only when it is absent does the legacy
        ``mode`` field decide, and then exactly as the migration rule
        prescribes: ``hotkey`` means manual only, ``wake_word`` means wake word
        only. Defaulting to ``True`` here would silently migrate a wake-word
        installation to *both* triggers, which is forbidden.
        """
        if self.manual_trigger_enabled is not None:
            return bool(self.manual_trigger_enabled)
        return self.mode == OperatingMode.HOTKEY.value

    @property
    def effective_wake_word_trigger_enabled(self) -> bool:
        """Whether a wake word may open an activation."""
        if self.wake_word_trigger_enabled is not None:
            return bool(self.wake_word_trigger_enabled)
        return self.mode == OperatingMode.WAKE_WORD.value

    @property
    def wake_word_enabled(self) -> bool:
        """Alias kept for the existing consumers of the wake-word flag."""
        return self.effective_wake_word_trigger_enabled

    @property
    def migrated_from_legacy_mode(self) -> bool:
        """True while the session still relies on the old ``mode`` field."""
        return (
            self.manual_trigger_enabled is None
            and self.wake_word_trigger_enabled is None
        )

    @property
    def presentation_mode(self) -> str:
        """What the UI should show as the waiting state.

        Derived from the **effective trigger flags**, never from the legacy
        ``mode`` field: a session may well have the wake word enabled while
        ``mode`` still says ``hotkey``, and the UI would otherwise announce
        "waiting for hotkey" for a wake-word session.
        """
        if self.effective_wake_word_trigger_enabled:
            return OperatingMode.WAKE_WORD.value
        return OperatingMode.HOTKEY.value

    def validate(self) -> None:
        if self.mode not in {mode.value for mode in OperatingMode}:
            raise ValueError("session.mode must be 'hotkey' or 'wake_word'")
        optional_strings = {
            "session.wake_word_backend": self.wake_word_backend,
            "session.wake_words": self.wake_words,
            "session.wake_word_inference_framework": self.wake_word_inference_framework,
        }
        for name, value in optional_strings.items():
            if value is not None and (
                not isinstance(value, str) or not value.strip()
            ):
                raise ValueError(f"{name} must be null or a non-empty string")

        optional_numbers = {
            "session.wake_word_sensitivity": self.wake_word_sensitivity,
            "session.wake_word_activation_delay": self.wake_word_activation_delay,
            "session.wake_word_timeout": self.wake_word_timeout,
            "session.wake_word_buffer_duration": self.wake_word_buffer_duration,
            "session.wake_word_followup_window": self.wake_word_followup_window,
            "session.initial_speech_timeout": self.initial_speech_timeout,
            "session.followup_timeout": self.followup_timeout,
            "session.extension_seconds": self.extension_seconds,
        }
        for name, value in optional_numbers.items():
            if value is None:
                continue
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value < 0
            ):
                raise ValueError(f"{name} must be null or a finite number >= 0")
        if (
            self.wake_word_sensitivity is not None
            and self.wake_word_sensitivity > 1
        ):
            raise ValueError(
                "session.wake_word_sensitivity must be between 0 and 1"
            )
        for name, value in (
            ("session.manual_trigger_enabled", self.manual_trigger_enabled),
            ("session.wake_word_trigger_enabled", self.wake_word_trigger_enabled),
        ):
            if value is not None and not isinstance(value, bool):
                raise ValueError(f"{name} must be null or a boolean")

        if not self.effective_manual_trigger_enabled and (
            not self.effective_wake_word_trigger_enabled
        ):
            raise ValueError(
                "At least one trigger source (manual_trigger_enabled or "
                "wake_word_trigger_enabled) must be enabled"
            )

    def query_parameters(self) -> dict[str, str]:
        """Return the exact public WebSocket query contract for this session."""
        man_enabled = self.effective_manual_trigger_enabled
        ww_enabled = self.effective_wake_word_trigger_enabled
        values: dict[str, Any] = {
            "manualTriggerEnabled": man_enabled,
            "wakeWordTriggerEnabled": ww_enabled,
            "wakeWordEnabled": ww_enabled,
            "wakeWordBackend": self.wake_word_backend if ww_enabled else None,
            "wakeWords": self.wake_words if ww_enabled else None,
            "wakeWordInferenceFramework": self.wake_word_inference_framework if ww_enabled else None,
            "wakeWordSensitivity": self.wake_word_sensitivity if ww_enabled else None,
            "wakeWordActivationDelay": self.wake_word_activation_delay if ww_enabled else None,
            "wakeWordTimeout": self.wake_word_timeout if ww_enabled else None,
            "wakeWordBufferDuration": self.wake_word_buffer_duration if ww_enabled else None,
            "wakeWordFollowupWindow": self.wake_word_followup_window if ww_enabled else None,
            "initialSpeechTimeout": self.initial_speech_timeout,
            "followupTimeout": self.followup_timeout,
            "extensionSeconds": self.extension_seconds,
        }
        result: dict[str, str] = {}
        for key, value in values.items():
            if value is None:
                continue
            if isinstance(value, bool):
                result[key] = "true" if value else "false"
            else:
                result[key] = str(value)
        return result

    def build_url(self, base_url: str) -> str:
        """Merge the session contract into *base_url* without duplicate keys."""
        parts = urlsplit(base_url)
        session_values = self.query_parameters()
        query = [
            (key, value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
            if key not in session_values
        ]
        query.extend(session_values.items())
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment)
        )


@dataclass
class DictationWindowConfig:
    """Hotkey-mode timing driven by authoritative server VAD events."""

    initial_speech_timeout: float = 15.0
    followup_timeout: float = 3.0
    extension_seconds: float = 15.0
    timeout_warning_seconds: float = 3.0

    def validate(self) -> None:
        for name, value in {
            "dictation_window.initial_speech_timeout": self.initial_speech_timeout,
            "dictation_window.followup_timeout": self.followup_timeout,
            "dictation_window.extension_seconds": self.extension_seconds,
            "dictation_window.timeout_warning_seconds": self.timeout_warning_seconds,
        }.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or value <= 0
            ):
                raise ValueError(f"{name} must be a finite number > 0")



@dataclass
class AudioConfig:
    """Microphone and audio capture settings."""

    device: Optional[int] = None  # None = system default
    sample_rate: int = 16000  # preferred; will resample if device doesn't support
    channels: int = 1
    chunk_duration_ms: int = 40  # ~40ms chunks like the browser reference client
    dtype: str = "int16"

    @property
    def chunk_frames(self) -> int:
        """Number of frames per chunk based on sample rate and duration."""
        return int(self.sample_rate * self.chunk_duration_ms / 1000)


@dataclass
class TextInjectionConfig:
    """How recognized text is inserted into the target application."""

    # Strategy for final text: "clipboard" (Ctrl+V), "sendkeys" (char-by-char), "both"
    final_strategy: str = "clipboard"
    # Delay between clipboard set and Ctrl+V (ms) - some apps need time
    paste_delay_ms: int = 50
    # Whether to add a trailing space after each final segment
    append_space: bool = True
    # Whether to warn about elevated target windows
    warn_elevated: bool = True


@dataclass
class HotkeyConfig:
    """Global hotkey configuration."""

    enabled: bool = True
    # Kept for backwards compatibility with the technical AP06 first stage.
    mode: str = "actions"
    toggle_key: str = "Ctrl+Shift+Space"
    reinsert_last_key: str = "Ctrl+Alt+Space"
    finish_key: Optional[str] = None
    cancel_key: Optional[str] = None
    overlay_toggle_key: Optional[str] = None
    # Deprecated legacy field accepted when loading older configuration files.
    key: Optional[str] = field(default=None, repr=False)
    auto_start: bool = False

    @property
    def effective_toggle_key(self) -> str:
        return self.key if self.key else self.toggle_key

    def validate(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("hotkey.enabled must be a boolean")
        if self.mode not in {"toggle", "actions"}:
            raise ValueError("hotkey.mode must be 'toggle' or 'actions'")
        if not isinstance(self.auto_start, bool):
            raise ValueError("hotkey.auto_start must be a boolean")

        bindings = [
            self.effective_toggle_key,
            self.reinsert_last_key,
            self.finish_key,
            self.cancel_key,
            self.overlay_toggle_key,
        ]
        normalized = [
            normalize_hotkey_spec(value)
            for value in bindings
            if value is not None and value.strip()
        ]
        if len(normalized) != len(set(normalized)):
            raise ValueError("all configured action hotkeys must differ")


@dataclass
class OverlayConfig:
    """Floating overlay window settings."""

    enabled: bool = True
    # Position: "bottom_center", "top_right", "top_left", "bottom_right", "bottom_left"
    position: str = "bottom_center"
    # Overlay dimensions
    width: int = 600
    max_height: int = 100
    # Opacity (0.0 - 1.0)
    opacity: float = 0.85
    # How long to show after final text (seconds)
    fade_after: float = 2.0
    # Font size
    font_size: int = 14
    font_family: Optional[str] = None
    background_color: str = "#20242a"
    text_color: str = "#ffffff"
    # Offset from screen edge (pixels)
    margin: int = 60
    show_realtime_text: bool = True

    def validate(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("overlay.enabled must be a boolean")
        if not isinstance(self.show_realtime_text, bool):
            raise ValueError("overlay.show_realtime_text must be a boolean")
        if self.font_family is not None and (
            not isinstance(self.font_family, str)
            or not self.font_family.strip()
        ):
            raise ValueError("overlay.font_family must be null or non-empty")
        for name, value in {
            "overlay.background_color": self.background_color,
            "overlay.text_color": self.text_color,
        }.items():
            if not isinstance(value, str) or re.fullmatch(
                r"#[0-9a-fA-F]{6}", value
            ) is None:
                raise ValueError(f"{name} must use #RRGGBB format")
        allowed_positions = {
            "bottom_center",
            "top_right",
            "top_left",
            "bottom_right",
            "bottom_left",
        }
        if not isinstance(self.position, str) or self.position not in allowed_positions:
            raise ValueError(
                f"overlay.position must be one of {sorted(allowed_positions)}"
            )
        positive_ints = {
            "overlay.width": self.width,
            "overlay.max_height": self.max_height,
            "overlay.font_size": self.font_size,
        }
        for name, value in positive_ints.items():
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{name} must be a positive integer")
        if (
            isinstance(self.margin, bool)
            or not isinstance(self.margin, int)
            or self.margin < 0
        ):
            raise ValueError("overlay.margin must be a non-negative integer")
        numeric_values = {
            "overlay.opacity": self.opacity,
            "overlay.fade_after": self.fade_after,
        }
        for name, value in numeric_values.items():
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise ValueError(f"{name} must be a finite number")
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError("overlay.opacity must be between 0.0 and 1.0")
        if self.fade_after < 0:
            raise ValueError("overlay.fade_after must be >= 0")


@dataclass
class HistoryMemoryConfig:
    """In-memory transcript history limits.

    ``max_entries`` of 0 means an unlimited in-memory history.
    """

    max_entries: int = 5


@dataclass
class HistoryPersistentConfig:
    """Persistent (SQLite) transcript history settings.

    Semantics for the limit values (matching the implementation roadmap):

    * ``max_entries: 0`` disables cleanup by entry count.
    * ``retention_days: 0`` disables cleanup by age.
    * ``min_characters`` is the threshold above which a final transcript is
      persisted even before any injection attempt is made.
    * ``store_failed_injections`` controls whether entries that later turn out
      to be skipped or failed are (re-)persisted for recovery.
    * ``store_all`` persists every final transcript regardless of length. This
      is an extension point for later configuration and defaults to ``False``.
    """

    enabled: bool = True
    max_entries: int = 100
    retention_days: int = 0
    min_characters: int = 1000
    store_failed_injections: bool = True
    store_all: bool = False
    # Database location. ``None`` resolves to the platform default inside the
    # local application data directory (never inside the repository).
    db_path: Optional[str] = None


@dataclass
class HistoryConfig:
    """Transcript history configuration for final transcripts."""

    enabled: bool = True
    memory: HistoryMemoryConfig = field(default_factory=HistoryMemoryConfig)
    persistent: HistoryPersistentConfig = field(default_factory=HistoryPersistentConfig)


@dataclass
class ClipboardConfig:
    """Clipboard backup and restore settings."""

    restore_previous: bool = False
    restore_delay_ms: int = 300
    backup_max_bytes: int = 1048576
    open_retries: int = 5
    open_retry_delay_ms: int = 20


@dataclass
class FeedbackConfig:
    """Optional non-blocking UI feedback."""

    sounds_enabled: bool = False
    wake_word_sound: Optional[str] = None
    start_sound: Optional[str] = None
    stop_sound: Optional[str] = None
    complete_sound: Optional[str] = None
    cancel_sound: Optional[str] = None
    warning_sound: Optional[str] = None
    error_sound: Optional[str] = None
    timeout_tick_sound: Optional[str] = None

    def validate(self) -> None:
        if not isinstance(self.sounds_enabled, bool):
            raise ValueError("feedback.sounds_enabled must be a boolean")
        for name, value in {
            "feedback.wake_word_sound": self.wake_word_sound,
            "feedback.start_sound": self.start_sound,
            "feedback.stop_sound": self.stop_sound,
            "feedback.complete_sound": self.complete_sound,
            "feedback.cancel_sound": self.cancel_sound,
            "feedback.warning_sound": self.warning_sound,
            "feedback.error_sound": self.error_sound,
            "feedback.timeout_tick_sound": self.timeout_tick_sound,
        }.items():
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{name} must be null or a string")


@dataclass
class LedConfig:
    """LED output, driven by the LEFX V3 controller in a thread of this process.

    The client no longer speaks USB itself. What is configured here is which
    output LEFX drives, how hard it is driven, and how long it may take to stop
    — not firmware registers.

    ``brightness`` stays on its original 0..255 scale even though LEFX takes a
    fraction. The number is divided by 255 on the way out. Rescaling it to 0..100
    would have been tidier and would have silently made everybody's ring four
    times brighter on the next start.
    """

    enabled: bool = True
    sink: str = "respeaker"
    fps: float = 30.0
    vendor_id: int = 0x2886
    product_id: int = 0x001A
    brightness: int = 64
    usb_timeout_ms: int = 1000
    shutdown_timeout: float = 1.5
    effect_paths: list = field(default_factory=list)
    simulation_offer_after_s: float = 120.0

    @property
    def brightness_fraction(self) -> float:
        """``brightness`` as LEFX wants it: 0.0 to 1.0."""
        return max(0.0, min(1.0, self.brightness / 255.0))

    def validate(self) -> None:
        if not isinstance(self.enabled, bool):
            raise ValueError("led.enabled must be a boolean")
        if self.sink not in LED_SINKS:
            raise ValueError(f"led.sink must be one of {list(LED_SINKS)}")
        for name, value, minimum, maximum in (
            ("vendor_id", self.vendor_id, 0, 0xFFFF),
            ("product_id", self.product_id, 0, 0xFFFF),
            ("brightness", self.brightness, 0, 255),
            ("usb_timeout_ms", self.usb_timeout_ms, 50, 5000),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not minimum <= value <= maximum
            ):
                raise ValueError(
                    f"led.{name} must be an integer between {minimum} and {maximum}"
                )
        for name, value, minimum, maximum in (
            ("fps", self.fps, 1.0, 120.0),
            ("shutdown_timeout", self.shutdown_timeout, 0.1, 10.0),
        ):
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                or not minimum <= value <= maximum
            ):
                raise ValueError(f"led.{name} must be between {minimum} and {maximum}")
        if (
            isinstance(self.simulation_offer_after_s, bool)
            or not isinstance(self.simulation_offer_after_s, (int, float))
            or not math.isfinite(self.simulation_offer_after_s)
            or self.simulation_offer_after_s < 0
        ):
            raise ValueError(
                "led.simulation_offer_after_s must be 0 (never offer) or a "
                "positive number of seconds"
            )
        if not isinstance(self.effect_paths, list) or not all(
            isinstance(item, str) and item.strip() for item in self.effect_paths
        ):
            raise ValueError("led.effect_paths must be a list of directory paths")


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    log_dir: str = str(DEFAULT_LOG_DIR)
    # Max size per log file before rotation
    max_bytes: int = 5 * 1024 * 1024  # 5 MB
    backup_count: int = 3
    # Whether to also log to stdout
    stdout: bool = True
    # JSON Lines format for machine readability
    json_format: bool = True
    # Per-channel log levels (channel_name -> level)
    channel_levels: dict[str, str] = field(default_factory=dict)


@dataclass
class AppConfig:
    """Root configuration combining all sections."""

    server: ServerConfig = field(default_factory=ServerConfig)
    event_stream: EventStreamConfig = field(default_factory=EventStreamConfig)
    session: SessionConfig = field(default_factory=SessionConfig)
    dictation_window: DictationWindowConfig = field(
        default_factory=DictationWindowConfig
    )
    audio: AudioConfig = field(default_factory=AudioConfig)
    text_injection: TextInjectionConfig = field(default_factory=TextInjectionConfig)
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    overlay: OverlayConfig = field(default_factory=OverlayConfig)
    history: HistoryConfig = field(default_factory=HistoryConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    clipboard: ClipboardConfig = field(default_factory=ClipboardConfig)
    feedback: FeedbackConfig = field(default_factory=FeedbackConfig)
    led: LedConfig = field(default_factory=LedConfig)
    feedback_mappings: FeedbackMappingConfig = field(
        default_factory=default_feedback_mappings
    )

    def validate(self) -> None:
        """Validate configuration consistency."""
        self.server.validate()
        self.event_stream.validate()
        self.session.validate()
        self.dictation_window.validate()
        self.hotkey.validate()
        self.overlay.validate()
        self.feedback.validate()
        self.led.validate()
        self.feedback_mappings.validate()

    @classmethod
    def load(
        cls,
        path: Optional[Path] = None,
        *,
        user_path: Optional[Path] = None,
    ) -> AppConfig:
        """Load one explicit file or the project/user layered configuration."""
        if path is not None:
            return cls._load_single(Path(path))

        project_raw = cls._read_mapping(DEFAULT_CONFIG_PATH)
        override_path = Path(user_path) if user_path else DEFAULT_USER_CONFIG_PATH
        override_raw = cls._read_mapping(override_path)
        unknown = cls._unknown_paths(cls(), override_raw)
        if unknown:
            logger.error(
                "Ignoring complete user override %s because it contains "
                "unknown fields: %s",
                override_path,
                ", ".join(unknown),
            )
            override_raw = {}
        merged = cls._deep_merge(project_raw, override_raw)
        return cls._from_dict(merged)

    @classmethod
    def _load_single(cls, path: Path) -> AppConfig:
        return cls._from_dict(cls._read_mapping(path))

    @staticmethod
    def _read_mapping(path: Path) -> dict:
        if not path.exists():
            logger.info("No config file at %s, using defaults.", path)
            return {}
        try:
            with open(path, "r", encoding="utf-8") as handle:
                raw = yaml.safe_load(handle) or {}
        except Exception:
            logger.exception("Failed to load config from %s, using defaults.", path)
            return {}
        if not isinstance(raw, dict):
            logger.warning("Config root in %s is not a mapping.", path)
            return {}
        return raw

    @classmethod
    def _deep_merge(cls, base: dict, override: dict) -> dict:
        result = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and isinstance(result.get(key), dict):
                result[key] = cls._deep_merge(result[key], value)
            else:
                result[key] = value
        return result

    @classmethod
    def _unknown_paths(
        cls, model: Any, data: dict, prefix: str = ""
    ) -> list[str]:
        if not isinstance(data, dict) or not dataclasses.is_dataclass(model):
            return []
        field_names = {item.name for item in dataclasses.fields(model)}
        unknown: list[str] = []
        for key, value in data.items():
            path = f"{prefix}.{key}" if prefix else key
            if key not in field_names:
                unknown.append(path)
                continue
            nested_model = getattr(model, key)
            if isinstance(value, dict) and dataclasses.is_dataclass(nested_model):
                unknown.extend(cls._unknown_paths(nested_model, value, path))
        return unknown

    @classmethod
    def _from_dict(cls, data: dict) -> AppConfig:
        """Build config from a nested dictionary, ignoring unknown keys."""

        def _build(dc_class, section: dict):
            if not isinstance(section, dict):
                return dc_class()
            # Only pass keys that the dataclass actually has
            valid_fields = {f.name for f in dc_class.__dataclass_fields__.values()}
            filtered = {k: v for k, v in section.items() if k in valid_fields}
            return dc_class(**filtered)

        history_data = data.get("history", {})
        if isinstance(history_data, dict):
            memory_data = _build(HistoryMemoryConfig, history_data.get("memory", {}))
            persistent_data = _build(HistoryPersistentConfig, history_data.get("persistent", {}))
            enabled = history_data.get("enabled", True)
            history_cfg = HistoryConfig(enabled=enabled, memory=memory_data, persistent=persistent_data)
        else:
            history_cfg = HistoryConfig()

        cfg = cls(
            server=_build(ServerConfig, data.get("server", {})),
            event_stream=_build(EventStreamConfig, data.get("event_stream", {})),
            session=_build(SessionConfig, data.get("session", {})),
            dictation_window=_build(
                DictationWindowConfig, data.get("dictation_window", {})
            ),
            audio=_build(AudioConfig, data.get("audio", {})),
            text_injection=_build(TextInjectionConfig, data.get("text_injection", {})),
            hotkey=_build(HotkeyConfig, data.get("hotkey", {})),
            overlay=_build(OverlayConfig, data.get("overlay", {})),
            history=history_cfg,
            logging=_build(LoggingConfig, data.get("logging", {})),
            clipboard=_build(ClipboardConfig, data.get("clipboard", {})),
            feedback=_build(FeedbackConfig, data.get("feedback", {})),
            led=_build(LedConfig, data.get("led", {})),
            feedback_mappings=(
                FeedbackMappingConfig.from_mapping(data["feedback_mappings"])
                if "feedback_mappings" in data
                else default_feedback_mappings()
            ),
        )
        cfg.validate()
        return cfg

    def save(self, path: Optional[Path] = None) -> None:
        """Save current config atomically to YAML."""
        config_path = Path(path) if path else DEFAULT_CONFIG_PATH
        config_path.parent.mkdir(parents=True, exist_ok=True)

        data = self._to_plain_data(dataclasses.asdict(self))
        # asdict produces the dataclass fields, and for a LED call the fields
        # are not the schema: the verb is a key in the file, not a value. The
        # section writes itself instead, so a saved file loads again.
        data["feedback_mappings"] = self.feedback_mappings.to_mapping()
        data["hotkey"]["toggle_key"] = normalize_hotkey_spec(
            self.hotkey.effective_toggle_key
        )
        data["hotkey"].pop("key", None)
        temporary_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=config_path.parent,
                prefix=f".{config_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                yaml.safe_dump(
                    data,
                    handle,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
                handle.flush()
                os.fsync(handle.fileno())
                temporary_path = Path(handle.name)
            os.replace(temporary_path, config_path)
        finally:
            if temporary_path is not None and temporary_path.exists():
                temporary_path.unlink()
        logger.info("Configuration saved to %s", config_path)

    @classmethod
    def _to_plain_data(cls, value: Any) -> Any:
        if isinstance(value, Enum):
            return value.value
        if isinstance(value, dict):
            return {key: cls._to_plain_data(item) for key, item in value.items()}
        if isinstance(value, (list, tuple)):
            return [cls._to_plain_data(item) for item in value]
        return value

    def save_user(self, path: Optional[Path] = None) -> None:
        """Persist the validated user configuration outside the repository."""
        self.validate()
        self.save(Path(path) if path else DEFAULT_USER_CONFIG_PATH)
