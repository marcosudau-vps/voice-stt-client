"""Stable UI-neutral action identifiers and hotkey binding metadata."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ActionId(str, Enum):
    DICTATION_PRIMARY = "dictation.primary"
    DICTATION_FINISH = "dictation.finish"
    DICTATION_CANCEL = "dictation.cancel"
    HISTORY_REINSERT_LAST = "history.reinsert_last"
    OVERLAY_TOGGLE = "overlay.toggle"


@dataclass(frozen=True)
class ActionDefinition:
    action_id: ActionId
    label: str
    global_bindable: bool
    config_path: str


ACTION_DEFINITIONS = (
    ActionDefinition(
        ActionId.DICTATION_PRIMARY,
        "Diktat starten / Zeit verlängern",
        True,
        "hotkey.toggle_key",
    ),
    ActionDefinition(
        ActionId.DICTATION_FINISH,
        "Diktat sofort abschließen",
        True,
        "hotkey.finish_key",
    ),
    ActionDefinition(
        ActionId.DICTATION_CANCEL,
        "Diktat verwerfen",
        True,
        "hotkey.cancel_key",
    ),
    ActionDefinition(
        ActionId.HISTORY_REINSERT_LAST,
        "Letztes Transkript erneut einfügen",
        True,
        "hotkey.reinsert_last_key",
    ),
    ActionDefinition(
        ActionId.OVERLAY_TOGGLE,
        "Overlay ein-/ausblenden",
        True,
        "hotkey.overlay_toggle_key",
    ),
)

ACTION_BY_ID = {definition.action_id: definition for definition in ACTION_DEFINITIONS}

