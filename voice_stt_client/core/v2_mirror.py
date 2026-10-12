"""Asyncio adapter for the pure mirror and the actual V2 command tracker.

Install before run. Existing callbacks run after reduction. on_reduction is the
single publication port for future Controls/Results/Feedback/UI consumers.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
import time

from websockets.exceptions import ConnectionClosed

from . import protocol_v2 as p
from .activation_mirror import ActivationMirror, MirrorState, Reduction
from .command_tracker import AckAdvice, CommandFailure
from .v2_transport import V2STTSession, V2TransportState, _Blocked


class V2MirrorConnection:
    def __init__(self, session: V2STTSession, mirror: ActivationMirror | None = None, *, clock=time.monotonic):
        if session.binding is not None or session.domain_ready is not None:
            raise RuntimeError("attach mirror once before transport admission")
        self.session, self.mirror, self.clock = session, mirror or ActivationMirror(), clock
        self.on_reduction: Callable[[Reduction], None] | None = None
        self._changed = asyncio.Event()
        self._task: asyncio.Task | None = None
        self._request_revision = 0
        old_accepted, old_message = session.on_accepted, session.on_message
        old_lost, old_completion = session.on_lost, session.on_completion
        old_fault = session.on_protocol_fault

        def accepted(binding):
            self._publish(self.mirror.begin(binding.generation, binding.accepted.snapshot, self.clock()))
            if old_accepted:
                old_accepted(binding)

        def message(binding, value):
            self._publish(self.mirror.consume(binding.generation, value, self.clock()))
            if old_message:
                old_message(binding, value)

        def completion(value):
            # No Ack field ever replaces foreground. Eventless changes and
            # ambiguous closing/recovery outcomes are clarified by snapshot.
            if (value.advice in (AckAdvice.CLOSING, AckAdvice.SNAPSHOT, AckAdvice.SETTINGS_CONFLICT)
                    or value.ack.accepted and value.command.type in (
                        p.CommandType.SUPPRESSION, p.CommandType.AUDIO_AVAILABILITY, p.CommandType.SETTINGS_PATCH)):
                self._publish(self.mirror.clarify(value.generation, self.clock()))
            if old_completion:
                old_completion(value)

        def fault(binding):
            self._publish(self.mirror.protocol_fault(binding.generation, self.clock()))
            if old_fault:
                old_fault(binding)

        def lost(binding):
            if self._task:
                self._task.cancel()
            self._publish(self.mirror.disconnect(binding.generation))
            if old_lost:
                old_lost(binding)

        session.on_accepted, session.on_message = accepted, message
        session.on_completion, session.on_lost, session.on_protocol_fault = completion, lost, fault
        session.domain_ready = lambda: self.mirror.view.operations_ready

    def _publish(self, reduction):
        if "snapshot_required" in reduction.effects:
            self._request_revision += 1
        self._changed.set()
        if self.on_reduction:
            self.on_reduction(reduction)
        if (reduction.view.snapshot_pending or reduction.view.state == MirrorState.RECONNECT_REQUIRED):
            if self._task is None or self._task.done():
                self._task = asyncio.create_task(self._pump(), name="v2-mirror-resync")

    async def _pump(self):
        binding = self.session.binding
        if binding is None:
            return
        sent_revision = -1
        try:
            while self.session.binding is binding:
                view = self.mirror.view
                if view.state == MirrorState.RECONNECT_REQUIRED:
                    await self.session.reconnect(binding, "mirror_resync_failed")
                    return
                if not view.snapshot_pending:
                    return
                self._changed.clear()
                if sent_revision != self._request_revision:
                    sent_revision = self._request_revision
                    if self.session.status.state == V2TransportState.CONFIGURING:
                        await self.session.bootstrap_command(binding, p.CommandType.SNAPSHOT_REQUEST)
                    else:
                        await self.session.request(p.CommandType.SNAPSHOT_REQUEST, binding=binding)
                    continue
                # The Ack may arrive before/after a snapshot and is not its proof.
                try:
                    await asyncio.wait_for(self._changed.wait(), self.mirror.snapshot_wait(self.clock()))
                except TimeoutError:
                    pass
                result = self.mirror.tick(binding.generation, self.clock())
                self._publish(result)
        except (CommandFailure, TimeoutError, OSError, ConnectionClosed, _Blocked):
            if self.session.binding is binding:
                await self.session.reconnect(binding, "mirror_snapshot_command_failed")
        finally:
            # Do not let completion of an old-generation task clear a newer task.
            if self._task is asyncio.current_task():
                self._task = None

    async def close(self):
        """Stop transport and join the adapter's bounded snapshot task."""
        await self.session.stop()
        if self._task:
            self._task.cancel()
            await asyncio.gather(self._task, return_exceptions=True)
