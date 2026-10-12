"""Run-local V2 controls. All mutable entry points belong to the core loop.

No clock, DictationWindow, VAD, capture stop, text or clipboard side effects.
Qt forwards immutable intents from its published MirrorView; it never reads
the mutable transport. Runtime composition is supplied by AP-CV2-100.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from enum import StrEnum

from . import protocol_v2 as p
from .config import HotkeyConfig, normalize_hotkey_spec


class ControlSlot(StrEnum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    WAKE_PAUSE = "wake_pause"


class ActiveAction(StrEnum):
    REFRESH = "refresh"
    FINISH = "finish"
    CANCEL = "cancel"
    NONE = "none"


@dataclass(frozen=True)
class ControlConfig:
    primary_key: str = "Ctrl+Shift+Space"
    primary_action: ActiveAction = ActiveAction.REFRESH
    secondary_key: str = ""
    secondary_action: ActiveAction = ActiveAction.FINISH
    wake_pause_key: str = ""
    reinsert_last_key: str = "Ctrl+Alt+Space"
    overlay_toggle_key: str = ""
    enabled: bool = True

    def __post_init__(self):
        if type(self.enabled) is not bool:
            raise ValueError("controls.enabled must be boolean")
        for name in ("primary_action", "secondary_action"):
            object.__setattr__(self, name, ActiveAction(getattr(self, name)))
        keys = []
        for name in ("primary_key", "secondary_key", "wake_pause_key", "reinsert_last_key", "overlay_toggle_key"):
            value = getattr(self, name)
            if not isinstance(value, str):
                raise ValueError("control keys must be strings")
            canonical = normalize_hotkey_spec(value) if value.strip() else ""
            object.__setattr__(self, name, canonical)
            if canonical:
                keys.append(canonical)
        if len(keys) != len(set(keys)):
            raise ValueError("all control and utility keys must differ")


class ControlMigrationConflict(ValueError):
    """Keep the original profile; UI must resolve slots before saving it."""

    def __init__(self, legacy):
        self.legacy = legacy
        super().__init__("Explicit finish and cancel bindings require a user choice of two control slots")


def migrate_hotkeys(legacy: HotkeyConfig) -> ControlConfig:
    """Pure conversion; never save/delete existing bindings on a conflict.

    Full profile persistence/dialog belongs to AP070/080. This adapter preserves
    explicit controls and utilities, including the legacy primary key alias.
    """
    legacy.validate()
    if legacy.finish_key and legacy.cancel_key:
        raise ControlMigrationConflict(legacy)
    return ControlConfig(primary_key=legacy.effective_toggle_key,
                         secondary_key=legacy.finish_key or legacy.cancel_key or "",
                         secondary_action=ActiveAction.CANCEL if legacy.cancel_key else ActiveAction.FINISH,
                         reinsert_last_key=legacy.reinsert_last_key or "",
                         overlay_toggle_key=legacy.overlay_toggle_key or "", enabled=legacy.enabled)


@dataclass(frozen=True)
class ControlIntent:
    generation: int
    session_id: str
    action: str
    activation_id: str | None


def plan_control(view, slot: ControlSlot, config: ControlConfig) -> ControlIntent | None:
    """Resolve one physical impulse from an immutable published server view."""
    slot = ControlSlot(slot)
    if slot == ControlSlot.WAKE_PAUSE:
        raise ValueError("wake pause uses the suppression API")
    if not view.operations_ready or view.session_id is None:
        return None
    phase = view.input.phase
    if phase == p.InputPhase.IDLE:
        if slot != ControlSlot.PRIMARY or not view.manual_available:
            return None
        action = "activate"
    else:
        action = config.primary_action if slot == ControlSlot.PRIMARY else config.secondary_action
        if action == ActiveAction.NONE or view.input.activation_id is None:
            return None
        if action == ActiveAction.REFRESH and phase in (p.InputPhase.WAITING_FIRST_SPEECH, p.InputPhase.CLOSING_INPUT):
            return None
    return ControlIntent(view.generation, view.session_id, str(action), view.input.activation_id)


@dataclass(frozen=True)
class PauseView:
    desired_manual: bool
    desired_wake_word: bool
    confirmed_manual: bool | None
    confirmed_wake_word: bool | None
    pending: bool


class V2ControlService:
    """Use actual transport/mirror; audio_ready supplies AP040's local barrier.

    Desired pauses survive device/network loss on this object, never persist.
    Confirmation comes from the mirror's authoritative snapshot, not the UI
    request or an old ack. Bootstrap's both-suppressed mask is independent.
    """

    def __init__(self, session, mirror_connection, *, config=None, audio_ready=lambda: False):
        if session.binding is not None or getattr(session, "_control_service", None) is not None:
            raise RuntimeError("attach one control service before run")
        session._control_service = self
        self.session, self.mirror_connection = session, mirror_connection
        self.config = config or ControlConfig()
        self.audio_ready = audio_ready
        self._activation_pending = False
        self._pause_task = None
        self._desired = (False, False)
        session.set_desired_suppression(*self._desired)

    @property
    def pause_view(self):
        binding, view = self.session.binding, self.mirror_connection.mirror.view
        confirmed = (None, None)
        if (self.session.is_ready and binding and view.operations_ready and not view.snapshot_pending
                and view.session_id == binding.session_id and view.generation == binding.generation):
            mask = view.trigger.get("suppressed", {})
            confirmed = (mask.get("manual"), mask.get("wakeWord"))
        return PauseView(*self._desired, *confirmed, confirmed != self._desired)

    async def press(self, slot):
        if ControlSlot(slot) == ControlSlot.WAKE_PAUSE:
            return await self.toggle_pause("wakeWord")
        intent = plan_control(self.mirror_connection.mirror.view, slot, self.config)
        return await self.execute(intent)

    async def control(self, action, *, intent=None):
        """Dedicated Finish/Cancel buttons may provide an already captured ID."""
        action = ActiveAction(action)
        if action not in (ActiveAction.FINISH, ActiveAction.CANCEL, ActiveAction.REFRESH):
            return None
        if intent is None:
            view = self.mirror_connection.mirror.view
            if view.input.activation_id is None:
                return None
            intent = ControlIntent(view.generation, view.session_id, str(action), view.input.activation_id)
        elif intent.action != action:
            raise ValueError("intent action mismatch")
        return await self.execute(intent)

    async def execute(self, intent):
        binding, view = self.session.binding, self.mirror_connection.mirror.view
        if (intent is None or self._activation_pending or not self.session.is_ready or binding is None
                or not view.operations_ready or view.snapshot_pending
                or intent.generation != binding.generation or intent.session_id != binding.session_id):
            return None
        if intent.action not in ("activate", "refresh", "finish", "cancel"):
            raise ValueError("invalid control action")
        if intent.action == "activate":
            if (intent.activation_id is not None or not view.manual_available
                    or self._desired[0] or not self.audio_ready()):
                return None
            fields = dict(action="activate", source="manual")
        else:
            if intent.activation_id is None:
                return None
            # Never retarget a queued old-A intent to B. Server answers stale_A.
            if (intent.action == "refresh" and intent.activation_id == view.input.activation_id
                    and view.input.phase in (p.InputPhase.WAITING_FIRST_SPEECH, p.InputPhase.CLOSING_INPUT)):
                return None
            fields = dict(action=intent.action, activationId=intent.activation_id)
        self._activation_pending = True
        try:
            return await self.session.request(p.CommandType.ACTIVATION, binding=binding, **fields)
        finally:
            self._activation_pending = False

    async def set_pause(self, source, paused):
        if source not in ("manual", "wakeWord") or type(paused) is not bool:
            raise ValueError("pause needs one source and a boolean")
        mask = list(self._desired)
        mask[0 if source == "manual" else 1] = paused
        self._desired = tuple(mask)
        # Persist the request in run memory before any I/O, including an
        # uncertain/lost ack. Transport reapplies it before READY on reconnect.
        self.session.set_desired_suppression(*self._desired)
        if not self.session.is_ready:
            return None
        if self._pause_task is None or self._pause_task.done():
            self._pause_task = asyncio.create_task(self._flush_pause(), name="v2-run-pause")
        return await asyncio.shield(self._pause_task)

    async def toggle_pause(self, source):
        if source not in ("manual", "wakeWord"):
            raise ValueError("unknown trigger source")
        return await self.set_pause(source, not self._desired[0 if source == "manual" else 1])

    async def _flush_pause(self):
        binding = self.session.binding
        while self.session.is_ready and self.session.binding is binding:
            desired = self._desired
            completion = await self.session.request(p.CommandType.SUPPRESSION, binding=binding,
                                                    manual=desired[0], wakeWord=desired[1])
            if not completion.ack.accepted or desired == self._desired:
                return completion
        return None

    async def close(self):
        # No orphan suppression task; transport cleanup owns uncertain outcomes.
        task = self._pause_task
        if task and not task.done():
            task.cancel()
        if task:
            await asyncio.gather(task, return_exceptions=True)
