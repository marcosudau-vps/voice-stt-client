"""Core-loop settings actions for a single dialog, using actual V2 services.

No Qt objects cross this boundary. Close invalidates the dialog lease. All
mutations check it before I/O and all results after awaits. Credentials stay
in this object only; published projections contain nonsecret metadata.
"""
from __future__ import annotations

import asyncio
import inspect
from copy import deepcopy
from dataclasses import asdict, dataclass, replace
from enum import StrEnum
from collections.abc import Mapping
import threading

from .activation_mirror import ACTIVATION_TERMINALS, freeze
from .command_tracker import TransportLost
from .credential_store import CredentialStore, credential_target
from .settings_service import SettingsError, NA_KEYS, UNSUPPORTED_SESSION
from .v2_controls import ControlConfig, ControlIntent
from .v2_profile import V2Profile, migrate_profile


class ApplyChoice(StrEnum):
    CANCEL = "cancel"
    FINISH = "finish"
    DEFER = "defer"


@dataclass(frozen=True)
class ApplyContext:
    generation: int
    session_id: str | None
    activation_id: str | None
    drain_ids: tuple[str, ...]


@dataclass(frozen=True)
class SettingsUIView:
    origin: str
    context: ApplyContext
    profile: Mapping
    schema: Mapping
    settings: object
    server_requested: Mapping
    server_effective: Mapping
    catalog: object
    admin_verified: bool
    credential_saved: bool
    credential_target: str
    metadata_error: str | None
    connected_triggers: Mapping
    connected_wake_ids: tuple[str, ...]


class SettingsUISession:
    """Create one per dialog lease, on the same loop as settings/controls.

    persist_profile(profile) is an explicit sync or async local transaction:
    register/validate controls and atomically persist, or raise without commit.
    The application composition supplies that port in AP100. This service
    never invents a successful save when the port is missing.
    """
    def __init__(self, settings, controls, mirror_connection, *, credential_store=None,
                 persist_profile=None, wait_timeout=30):
        if settings.session is not controls.session or controls.mirror_connection is not mirror_connection:
            raise ValueError("settings UI services must share one transport and mirror")
        if not 0 < wait_timeout <= 300:
            raise ValueError("invalid settings wait timeout")
        self.settings, self.controls, self.mirror = settings, controls, mirror_connection
        self.origin = settings.http.origin
        self.store = credential_store or CredentialStore()
        self.persist_profile = persist_profile
        self.wait_timeout = wait_timeout
        self.active = True
        self._key = None
        self._verified_generation = None
        self._credential_saved = False
        self._lock = asyncio.Lock()
        self._lease_lock = threading.RLock()

    def invalidate(self):
        with self._lease_lock:
            self.active = False
            self._key = None
            self._verified_generation = None

    def _guard(self, generation=None):
        if not self.active:
            raise SettingsError("dialog_closed")
        if self.settings.http.origin != self.origin:
            self._key = None
            self._verified_generation = None
            raise SettingsError("server_origin_changed")
        if generation is not None and generation != self.settings.session.generation:
            self._verified_generation = None
            raise TransportLost("settings UI context changed")

    def context(self):
        view = self.mirror.mirror.view
        binding = self.settings.session.binding
        drain = tuple(sorted(key for key, a in view.activations.items()
                             if key != view.input.activation_id and a.status not in ACTIVATION_TERMINALS))
        return ApplyContext(self.settings.session.generation, binding.session_id if binding else None,
                            view.input.activation_id, drain)

    def view(self):
        self._guard()
        generation = self.settings.session.generation
        view = self.mirror.mirror.view
        return SettingsUIView(self.origin, self.context(), freeze(asdict(self.settings.profile)),
            freeze(self.settings.schema), self.settings.report(), freeze(self.settings.server_requested),
            freeze(self.settings.server_effective), self.settings.catalog,
            self._key is not None and self._verified_generation == generation,
            self._credential_saved, credential_target(self.origin), self.settings.last_metadata_error,
            view.trigger.get("configured", freeze({})), tuple(view.effective_settings.get("wakeWord.selection", ())))

    async def load(self):
        self._guard()
        generation = self.settings.session.generation
        await self.settings.load_metadata()
        self._guard(generation)
        return self.view()

    async def load_credential(self):
        self._guard()
        generation = self.settings.session.generation
        key = await asyncio.to_thread(self.store.read, self.origin)
        with self._lease_lock:
            self._guard(generation)
            self._key = key
            self._credential_saved = key is not None
            self._verified_generation = None
        return self.view()

    async def verify(self, key=None, *, remember=False):
        self._guard()
        generation = self.settings.session.generation
        self._verified_generation = None
        candidate = key or self._key
        if not isinstance(candidate, str) or not candidate or "\r" in candidate or "\n" in candidate:
            raise SettingsError("admin_key_required")
        await self.settings.verify_admin(candidate)
        with self._lease_lock:
            self._guard(generation)
            self._key = candidate
            self._verified_generation = generation
        if remember:
            # Persistence failure leaves a verified process-memory key, never
            # a plaintext fallback. The UI displays the differentiated error.
            await asyncio.to_thread(self.store.save, self.origin, candidate)
            self._guard(generation)
            self._credential_saved = True
        return self.view()

    async def delete_credential(self):
        self._guard()
        generation = self.settings.session.generation
        self._key = None
        self._verified_generation = None
        await asyncio.to_thread(self.store.delete, self.origin)
        self._guard(generation)
        self._credential_saved = False
        return self.view()

    async def patch_server(self, changes):
        self._guard()
        generation = self.settings.session.generation
        if not self._key or self._verified_generation != generation:
            raise SettingsError("admin_check_required")
        try:
            await self.settings.patch_server(changes, admin_key=self._key)
        except SettingsError as error:
            if error.status in (401, 403):
                self._verified_generation = None
            raise
        self._guard(generation)
        return self.view()

    def _candidate(self, profile, repair_fields=()):
        if not isinstance(profile, dict):
            raise SettingsError("invalid_profile")
        candidate = V2Profile(**deepcopy(profile))
        # Migration provenance isn't an editable UI value. Only expressly
        # acknowledged, represented fields may be repaired; unknowns survive.
        candidate.unresolved = deepcopy(self.settings.profile.unresolved)
        candidate.retired = deepcopy(self.settings.profile.retired)
        for key in repair_fields:
            if key not in ("wake_words", "session.mode", "session.trigger_flags", "hotkey", *NA_KEYS):
                raise SettingsError("unsupported_profile_repair")
            if key in NA_KEYS and key not in candidate.desired_settings:
                raise SettingsError("profile_repair_value_required")
            candidate.unresolved.pop(key, None)
        candidate = migrate_profile({"v2_profile": asdict(candidate)}, self.settings.catalog)
        if candidate.issues or candidate.unresolved:
            raise SettingsError("profile_repair_required")
        candidate.require_ready()
        if self.settings.catalog is None or self.settings.catalog_stale:
            raise SettingsError("catalog_unavailable")
        self.settings.catalog.validate_selection(candidate.wake_word_ids,
            backend=self.settings.server_requested["wakeWord.inferenceBackend"], required=candidate.wake_word)
        for key in candidate.desired_settings:
            if key not in (*NA_KEYS, *UNSUPPORTED_SESSION):
                raise SettingsError("not_individually_startable")
            if key in UNSUPPORTED_SESSION and candidate.desired_settings[key] != self.settings.profile.desired_settings.get(key):
                raise SettingsError("not_individually_startable")
        changes = {key: value for key, value in candidate.desired_settings.items() if key in NA_KEYS}
        if changes:
            self.settings._validate_changes(changes, "session", changes)
        ControlConfig(**candidate.controls)
        return candidate

    async def apply_profile(self, profile, context, *, choice=None, drain_choice=None, repair_fields=()):
        """No destruction without a fresh, explicit, identity-bound choice.

        Defer persists a future-session wish and leaves input/drain untouched.
        Finish waits for actual terminals; cancel closes only the captured ID.
        Drain loss additionally needs 'discard', otherwise wait or reject.
        Timeouts retain the wish and current connection for a later retry.
        """
        async with self._lock:
            self._guard(context.generation)
            current = self.context()
            if current != context:
                raise SettingsError("apply_context_changed")
            candidate = self._candidate(profile, repair_fields)
            old = self.settings.profile
            # Saved/deferred intent may already differ from the current Hello.
            # Compare with the authoritative connection, not the saved profile.
            projected = self.view()
            reconnect = (candidate.manual, candidate.wake_word, tuple(candidate.wake_word_ids) if candidate.wake_word else ()) != (
                projected.connected_triggers.get("manual", old.manual),
                projected.connected_triggers.get("wakeWord", old.wake_word), projected.connected_wake_ids)
            choice = ApplyChoice(choice) if choice is not None else None
            if reconnect and current.activation_id and choice is None:
                raise SettingsError("activation_choice_required")
            if reconnect and current.drain_ids and choice != ApplyChoice.DEFER and drain_choice not in ("wait", "discard"):
                raise SettingsError("drain_choice_required")
            if self.persist_profile is None:
                raise SettingsError("profile_persistence_required")
            # Port must be transactional and return normally only on commit.
            async def persist_and_adopt():
                try:
                    result = self.persist_profile(deepcopy(candidate))
                    if inspect.isawaitable(result):
                        await result
                except Exception:
                    raise SettingsError("profile_persistence_failed") from None
                self.settings.profile = candidate
                self.controls.config = ControlConfig(**candidate.controls)
                self.settings._publish()
            # Async composition can marshal Win32 work to Qt and disk work to
            # a worker. Closing the dialog cannot interrupt an atomic commit
            # between persistence and adoption of the corresponding controls.
            commit = asyncio.create_task(persist_and_adopt())
            try:
                await asyncio.shield(commit)
            except asyncio.CancelledError:
                await commit
                raise
            self._guard(context.generation)
            if not reconnect:
                if self.settings.session.is_ready:
                    await self.settings.apply_session()
                    self._guard(context.generation)
                return self.view()
            if choice == ApplyChoice.DEFER or current.session_id is None:
                return self.view()
            binding = self.settings.session.binding
            view = self.mirror.mirror.view
            if not self.settings.session.is_ready or not view.operations_ready or view.snapshot_pending:
                raise SettingsError("apply_context_changed")
            desired_pauses = self.controls.pause_view
            try:
                # No new manual/wake activation while finishing/waiting. The
                # existing input remains open until the chosen command.
                await self.controls.set_pause("manual", True)
                await self.controls.set_pause("wakeWord", True)
                # Suppression acks request mirror clarification. Controlservice
                # deliberately refuses activation commands until that snapshot.
                await self.settings.refresh_session(binding)
                self._guard(context.generation)
                if self.context().activation_id != current.activation_id:
                    raise SettingsError("apply_context_changed")
                allowed_drains = set(current.drain_ids) | {current.activation_id}
                if set(self.context().drain_ids) - allowed_drains:
                    raise SettingsError("apply_context_changed")
                if current.activation_id:
                    action = "cancel" if choice == ApplyChoice.CANCEL else "finish"
                    intent = ControlIntent(context.generation, current.session_id, action, current.activation_id)
                    result = await self.controls.control(action, intent=intent)
                    if result is None or not result.ack.accepted:
                        raise SettingsError("activation_close_rejected")
                async def wait_safe():
                    while True:
                        self._guard(context.generation)
                        v = self.mirror.mirror.view
                        if self.settings.session.binding is not binding:
                            raise TransportLost("settings UI session lost")
                        if v.input.activation_id not in (None, current.activation_id):
                            raise SettingsError("apply_context_changed")
                        if set(self.context().drain_ids) - allowed_drains:
                            raise SettingsError("apply_context_changed")
                        if (v.operations_ready and not v.snapshot_pending and v.input.activation_id is None
                                and (drain_choice == "discard" or not self.context().drain_ids)):
                            return
                        await asyncio.sleep(.05)
                try:
                    await asyncio.wait_for(wait_safe(), self.wait_timeout)
                except TimeoutError:
                    raise SettingsError("drain_pending_retry") from None
                self._guard(context.generation)
                # Restore intent in transport memory before reconnect bootstrap.
                self.controls._desired = (desired_pauses.desired_manual, desired_pauses.desired_wake_word)
                self.settings.session.set_desired_suppression(*self.controls._desired)
                await self.settings.session.reconnect(binding, "user_settings_apply")
                return self.view()
            finally:
                # Also restore pauses after failure, cancellation or disconnect.
                await self.controls.set_pause("manual", desired_pauses.desired_manual)
                await self.controls.set_pause("wakeWord", desired_pauses.desired_wake_word)
