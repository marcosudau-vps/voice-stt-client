"""Server-authoritative V2 settings, catalog and bootstrap on the core loop.

HTTP is stdlib/to_thread, TLS verified, same-origin and without redirects.
Immutable reports distinguish local wishes, requested, effective and pending.
No Qt, credential persistence, activation decisions or automatic reconnects.
"""
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, replace
from http.client import IncompleteRead
import json
import math
import ssl
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, build_opener, HTTPSHandler, HTTPRedirectHandler

from . import protocol_v2 as p
from .command_tracker import CommandFailure, TransportLost
from .v2_profile import V2Profile, migrate_profile
from .v2_transport import V2TransportState


NA_KEYS = (
    "activation.initialSpeechTimeoutMs", "activation.followupTimeoutMs",
    "activation.segmentWatchdogInitialMs", "activation.segmentWatchdogRefreshMs",
    "activation.segmentWatchdogWarningMs", "activation.closingRecoveryTimeoutMs",
    "wakeWord.sensitivity", "wakeWord.minConsecutivePredictionFrames", "wakeWord.cooldownMs",
    "wakeWord.preRollMs", "wakeWord.detectorGain",
)
UNSUPPORTED_SESSION = ("wakeWord.noiseSuppressionEnabled", "wakeWord.vadThreshold")
SUPPRESSION_KEYS = ("runtimeSuppression.manual", "runtimeSuppression.wakeWord")
SERVER_KEYS = ("wakeWord.inferenceBackend", "wakeWord.globalDisabledIds")
SESSION_KEYS = (*NA_KEYS, *UNSUPPORTED_SESSION, "wakeWord.selection", *SUPPRESSION_KEYS)
SERVER_DEFAULT_KEYS = (*NA_KEYS, *UNSUPPORTED_SESSION, *SERVER_KEYS)


class SettingsError(ValueError):
    """Safe machine-readable failure; never includes URL/body/key/exception."""

    def __init__(self, code, *, status=None):
        self.code, self.status = code, status
        super().__init__(code)


def _int(value):
    return type(value) is int and value >= 0


def _identity(value):
    if not isinstance(value, dict) or type(value.get("protocolVersion")) is not int or value["protocolVersion"] != 2:
        raise SettingsError("invalid_http_protocol")


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


@dataclass(frozen=True)
class HttpResponse:
    status: int
    body: dict


class SettingsHTTP:
    """One bounded blocking worker at a time, including after owner timeout.

    Timeout/cancellation cannot cancel a native urllib call. Its task is kept,
    so repeated requests cannot accumulate workers or blindly retry PATCHes.
    """

    def __init__(self, websocket_url: str, *, timeout=5, max_bytes=1024 * 1024):
        try:
            parts = urlsplit(websocket_url)
            if (parts.scheme not in ("ws", "wss") or not parts.hostname or parts.username or parts.password
                    or parts.query or parts.fragment or parts.path != "/ws/v2"):
                raise ValueError
            port = parts.port
        except ValueError:
            raise SettingsError("invalid_http_origin") from None
        # Plain HTTP is only for an explicit loopback harness/local server.
        if parts.scheme == "ws" and parts.hostname not in ("127.0.0.1", "localhost", "::1"):
            raise SettingsError("tls_required")
        if type(timeout) not in (float, int) or not math.isfinite(timeout) or timeout <= 0:
            raise SettingsError("invalid_http_timeout")
        if type(max_bytes) is not int or not 1 <= max_bytes <= 4 * 1024 * 1024:
            raise SettingsError("invalid_http_limit")
        self.origin = urlunsplit(("https" if parts.scheme == "wss" else "http", parts.netloc, "", "", ""))
        self.timeout, self.max_bytes = timeout, max_bytes
        self._lock = asyncio.Lock()
        self._worker = None

    async def request(self, method, path, *, body=None, admin_key=None):
        if method not in ("GET", "PATCH", "POST") or path not in (
                "/api/v2/settings/schema", "/api/v2/settings/server", "/api/v2/wake-words", "/api/v2/wake-words/refresh"):
            raise SettingsError("unsupported_http_route")
        async with self._lock:
            if self._worker is not None:
                try:
                    await asyncio.wait_for(asyncio.shield(self._worker), self.timeout)
                except TimeoutError:
                    raise SettingsError("http_worker_busy") from None
                except (SettingsError, OSError):
                    pass
                self._worker = None
            self._worker = asyncio.create_task(asyncio.to_thread(self._request, method, path, body, admin_key))
            try:
                return await asyncio.wait_for(asyncio.shield(self._worker), self.timeout)
            except TimeoutError:
                raise SettingsError("http_outcome_unknown" if method != "GET" else "http_timeout") from None
            finally:
                if self._worker.done():
                    self._worker = None

    def _request(self, method, path, body, admin_key):
        headers = {"Accept": "application/json"}
        if admin_key is not None:
            headers["X-VoiceSTT-Admin-Key"] = admin_key
        data = None if body is None else json.dumps(body, allow_nan=False).encode("utf-8")
        if data is not None:
            headers["Content-Type"] = "application/json"
        try:
            opener = build_opener(_NoRedirect(), HTTPSHandler(context=ssl.create_default_context()))
            request = Request(self.origin + path, data=data, headers=headers, method=method)
            try:
                response = opener.open(request, timeout=self.timeout)
            except HTTPError as error:
                response = error
            with response:
                status = response.code
                if 300 <= status < 400:
                    raise SettingsError("http_redirect_forbidden", status=status)
                # Error documents may be HTML, empty, or truncated by a proxy.
                # Status is authoritative; never require a success schema here.
                # In particular a failed PATCH is returned once, never retried.
                if status != 200:
                    return HttpResponse(status, {})
                content = response.read(self.max_bytes + 1)
                if len(content) > self.max_bytes:
                    raise SettingsError("http_response_too_large", status=status)
                try:
                    result = json.loads(content)
                except (ValueError, UnicodeError):
                    raise SettingsError("invalid_http_json", status=status) from None
                if not isinstance(result, dict):
                    raise SettingsError("invalid_http_shape", status=status)
                return HttpResponse(status, result)
        except SettingsError:
            raise
        except (URLError, OSError, ValueError, IncompleteRead) as error:
            if isinstance(error, ssl.SSLCertVerificationError) or (
                    isinstance(error, URLError) and isinstance(error.reason, ssl.SSLCertVerificationError)):
                raise SettingsError("http_tls_verification_failed") from None
            raise SettingsError("http_outcome_unknown" if method != "GET" else "http_unavailable") from None


@dataclass(frozen=True)
class Setting:
    key: str
    scope: str
    auth: str
    type: str
    constraints: Mapping
    default_value: object
    apply_policy: p.ApplyPolicy
    description: str = ""

    @classmethod
    def parse(cls, entry):
        try:
            if (not isinstance(entry, dict) or entry["scope"] not in ("session", "server", "client_local")
                    or entry["auth"] not in ("session", "admin") or entry["type"] not in ("int", "float", "bool", "string", "string_list")
                    or not isinstance(entry["key"], str) or not isinstance(entry["constraints"], dict)):
                raise ValueError
            return cls(entry["key"], entry["scope"], entry["auth"], entry["type"], p._freeze(entry["constraints"]),
                       p._freeze(entry["defaultValue"]), p.ApplyPolicy(entry["applyPolicy"]), entry.get("description", ""))
        except (KeyError, ValueError, TypeError):
            raise SettingsError("invalid_schema_entry") from None

    def validate(self, value):
        valid = {
            "int": type(value) is int,
            "float": type(value) in (int, float) and math.isfinite(value),
            "bool": type(value) is bool,
            "string": isinstance(value, str),
            "string_list": isinstance(value, list) and all(isinstance(x, str) for x in value),
        }[self.type]
        if not valid:
            raise SettingsError("invalid_type")
        c = self.constraints
        if self.type in ("int", "float") and ("min" in c and value < c["min"] or "max" in c and value > c["max"]):
            raise SettingsError("out_of_range")
        allowed = c.get("allowedValues", c.get("allowed"))
        if allowed is not None and value not in allowed:
            raise SettingsError("value_not_allowed")
        if self.type == "string_list" and len(value) < c.get("minItems", 0):
            raise SettingsError("too_few_items")


@dataclass(frozen=True)
class WakeCatalog:
    revision: int
    entries: Mapping

    @classmethod
    def parse(cls, body):
        _identity(body)
        revision = body.get("catalogRevision")
        if not _int(revision) or not isinstance(body.get("wakeWords"), list):
            raise SettingsError("invalid_catalog")
        entries = {}
        for entry in body["wakeWords"]:
            if (not isinstance(entry, dict) or not all(isinstance(entry.get(k), str) and entry[k] for k in ("id", "displayName", "artifactVersion"))
                    or entry.get("catalogRevision") != revision or type(entry.get("available")) is not bool
                    or not isinstance(entry.get("aliases"), list) or not all(isinstance(x, str) for x in entry["aliases"])
                    or not isinstance(entry.get("backends"), dict) or set(entry["backends"]) != {"onnx", "tflite"}
                    or entry["id"] in entries):
                raise SettingsError("invalid_catalog_entry")
            if not entry["available"] and not isinstance(entry.get("unavailableReason"), str):
                raise SettingsError("invalid_catalog_reason")
            for backend in entry["backends"].values():
                if not isinstance(backend, dict) or type(backend.get("available")) is not bool:
                    raise SettingsError("invalid_catalog_backend")
                if not backend["available"] and not isinstance(backend.get("unavailableReason"), str):
                    raise SettingsError("invalid_catalog_backend_reason")
            # Publish documented fields only; no server-internal artifact paths.
            entries[entry["id"]] = {key: deepcopy(entry[key]) for key in (
                "id", "displayName", "aliases", "artifactVersion", "available", "catalogRevision", "backends", "unavailableReason") if key in entry}
            entries[entry["id"]]["backends"] = {name: {key: value[key] for key in ("available", "unavailableReason") if key in value}
                                                   for name, value in entry["backends"].items()}
        return cls(revision, p._freeze(entries))

    def resolve(self, words):
        if not isinstance(words, (list, tuple)):
            raise SettingsError("invalid_wake_selection")
        resolved = []
        for word in words:
            if not isinstance(word, str) or not word.strip():
                raise SettingsError("invalid_wake_selection")
            normalized = word.strip().casefold()
            # Exact canonical IDs take precedence over display/alias collisions.
            hits = [word.strip()] if word.strip() in self.entries else [key for key, entry in self.entries.items()
                if normalized in {x.strip().casefold() for x in (key, entry["displayName"], *entry["aliases"])}]
            if len(hits) != 1:
                raise SettingsError("wake_selection_ambiguous_or_unknown")
            if hits[0] not in resolved:
                resolved.append(hits[0])
        return tuple(resolved)

    def validate_selection(self, ids, *, backend="auto", required=False):
        if backend not in ("auto", "onnx", "tflite"):
            raise SettingsError("invalid_wake_backend")
        if not isinstance(ids, (list, tuple)) or required and not ids:
            raise SettingsError("wake_selection_required")
        common = {"onnx", "tflite"} if backend == "auto" else {backend}
        for key in ids:
            if not isinstance(key, str) or key not in self.entries:
                raise SettingsError("wake_selection_not_canonical")
            entry = self.entries[key]
            if not entry["available"]:
                raise SettingsError("wake_selection_unavailable")
            common &= {name for name, value in entry["backends"].items() if value["available"]}
        if ids and not common:
            raise SettingsError("wake_selection_no_common_backend")
        return tuple(dict.fromkeys(ids))


@dataclass(frozen=True)
class SettingsReport:
    generation: int
    session_id: str | None
    session_revision: int | None
    server_revision: int | None
    desired: Mapping
    requested: Mapping
    effective: Mapping
    pending: Mapping
    unsupported: Mapping
    catalog_revision: int | None
    catalog_stale: bool


class SettingsService:
    """Attach once before run, then supply bootstrap to V2MediaConnection.

    prepare loads schema/server/catalog before each Hello and resolves migrated
    aliases. Availability events mark the catalog stale immediately and schedule
    a guarded refresh. Every post-await publication checks binding/generation.
    Session PATCH is NA-only; NS selection is saved for a future Hello, NS
    Noise/VAD preferences are reported unsupported, and suppression is control.
    """

    def __init__(self, session, profile: V2Profile, *, http=None, snapshot_timeout=5):
        if session.binding is not None or session.prepare is not None:
            raise RuntimeError("attach settings before transport run")
        if type(snapshot_timeout) not in (float, int) or not math.isfinite(snapshot_timeout) or snapshot_timeout <= 0:
            raise SettingsError("invalid_snapshot_timeout")
        self.session, self.profile = session, profile
        self.http = http or SettingsHTTP(session.config.url)
        self.snapshot_timeout = snapshot_timeout
        self.schema = {}
        self.server_revision = None
        self.server_requested, self.server_effective = {}, {}
        self.catalog = None
        self.catalog_stale = True
        self._catalog_target_revision = 0
        self._snapshot = None
        self._snapshot_serial = 0
        self._changed = asyncio.Event()
        self._session_lock, self._metadata_lock, self._server_lock = asyncio.Lock(), asyncio.Lock(), asyncio.Lock()
        self._refresh_task = None
        self._session_refresh_task = None
        self._refresh_requested = False
        self.last_metadata_error = None
        self.on_report = None
        old_accepted, old_message, old_lost = session.on_accepted, session.on_message, session.on_lost

        def accepted(binding):
            self._snapshot = binding.accepted.snapshot
            self._snapshot_serial += 1
            self._changed.set()
            if old_accepted:
                old_accepted(binding)
            self._publish()

        def message(binding, value):
            if binding is not session.binding:
                return
            if isinstance(value, p.Snapshot):
                if self._snapshot is None or (value.stateVersion >= self._snapshot.stateVersion
                        and value.settingsRevision >= self._snapshot.settingsRevision):
                    self._snapshot = value
                    self._snapshot_serial += 1
                    self._changed.set()
                    self._publish()
            elif isinstance(value, p.Event) and value.type == p.EventType.WAKE_AVAILABILITY:
                self._catalog_target_revision = max(self._catalog_target_revision, value.payload["catalogRevision"])
                self.catalog_stale = True
                self._publish()
                if self._refresh_task is None or self._refresh_task.done():
                    self._refresh_task = asyncio.create_task(self._refresh_after_availability(binding))
            elif isinstance(value, p.Event) and value.type in (
                    p.EventType.SETTINGS_CHANGED, p.EventType.INPUT_CLOSED, p.EventType.ACTIVATION_STARTED):
                # Requested/effective maps are complete only in a snapshot.
                # Re-read after input closes, including automatic timeout closes.
                self._refresh_requested = True
                if self._session_refresh_task is None or self._session_refresh_task.done():
                    self._session_refresh_task = asyncio.create_task(self._refresh_after_event(binding))
            if old_message:
                old_message(binding, value)

        def lost(binding):
            self._snapshot = None
            self._catalog_target_revision = 0
            self._changed.set()
            if self._refresh_task:
                self._refresh_task.cancel()
            if self._session_refresh_task:
                self._session_refresh_task.cancel()
            if old_lost:
                old_lost(binding)
            self._publish()

        session.on_accepted, session.on_message, session.on_lost = accepted, message, lost
        session.prepare = self.prepare

    def _guard(self, generation, binding=None):
        if self.session.generation != generation or binding is not None and self.session.binding is not binding:
            raise TransportLost("stale settings response")

    async def _get(self, path):
        response = await self.http.request("GET", path)
        if response.status != 200:
            raise SettingsError("http_read_failed", status=response.status)
        return response.body

    async def load_metadata(self, *, binding=None):
        generation = self.session.generation
        async with self._metadata_lock:
            self._guard(generation, binding)
            schema = await self._get("/api/v2/settings/schema")
            server = await self._get("/api/v2/settings/server")
            catalog = await self._get("/api/v2/wake-words")
            self._guard(generation, binding)
            try:
                schema = p._thaw(p.decode_settings_schema(schema).payload)
            except p.ProtocolError:
                raise SettingsError("invalid_schema") from None
            parsed = [Setting.parse(x) for x in schema["settings"]]
            definitions = {x.key: x for x in parsed}
            if len(definitions) != len(parsed) or not set((*SESSION_KEYS, *SERVER_KEYS)).issubset(definitions):
                raise SettingsError("incomplete_schema")
            revision, requested, effective = self._parse_server(server)
            if (schema.get("serverCommit"), schema.get("serverVersion")) != (server.get("serverCommit"), server.get("serverVersion")):
                raise SettingsError("server_identity_changed")
            parsed_catalog = WakeCatalog.parse(catalog)
            if parsed_catalog.revision < self._catalog_target_revision:
                raise SettingsError("stale_catalog_response")
            self.schema, self.server_revision = definitions, revision
            self.server_requested, self.server_effective = requested, effective
            # Retain the immutable cache object for an unchanged revision.
            if self.catalog is None or self.catalog.revision != parsed_catalog.revision:
                self.catalog = parsed_catalog
            self.catalog_stale = False
            self.last_metadata_error = None
            self._publish()

    @staticmethod
    def _parse_server(body):
        try:
            parsed = p.decode_server_settings(body)
            body = p._thaw(parsed.payload)
        except p.ProtocolError:
            raise SettingsError("invalid_server_settings")
        requested, effective = {}, {}
        try:
            for entry in body["settings"]:
                key = entry["key"]
                if key in requested:
                    raise ValueError
                requested[key], effective[key] = entry["requestedValue"], entry["effectiveValue"]
        except (KeyError, TypeError, ValueError):
            raise SettingsError("invalid_server_values") from None
        if not set(SERVER_DEFAULT_KEYS).issubset(requested):
            raise SettingsError("incomplete_server_defaults")
        return body["settingsRevision"], requested, effective

    async def _refresh_after_availability(self, binding):
        try:
            for attempt in range(2):
                try:
                    await self.load_metadata(binding=binding)
                    return
                except SettingsError as error:
                    if error.code != "stale_catalog_response" or attempt:
                        raise
        except (SettingsError, TransportLost):
            if self.session.binding is binding:
                self.last_metadata_error = "catalog_refresh_failed"
                self.catalog_stale = True
                self._publish()

    async def _refresh_after_event(self, binding):
        try:
            while self._refresh_requested:
                self._refresh_requested = False
                await self.refresh_session(binding)
        except (SettingsError, CommandFailure, TimeoutError, OSError):
            if self.session.binding is binding:
                self.last_metadata_error = "session_read_required"
        finally:
            if self._session_refresh_task is asyncio.current_task():
                self._session_refresh_task = None

    async def prepare(self, session):
        try:
            await self.load_metadata()
        except SettingsError as error:
            if (error.code in ("http_unavailable", "http_timeout", "http_worker_busy")
                    or error.code == "http_read_failed" and error.status is not None
                    and (error.status in (408, 429) or 500 <= error.status < 600)):
                # Only idempotent metadata GETs reach this boundary. The
                # transport owns bounded backoff and a fresh preflight/Hello.
                raise OSError("settings_metadata_temporarily_unavailable") from None
            raise
        # Only unresolved wake aliases are automatically repairable by metadata.
        profile = migrate_profile({"v2_profile": self.profile.__dict__}, self.catalog)
        profile.require_ready()
        ids = self.catalog.validate_selection(profile.wake_word_ids,
            backend=self.server_requested["wakeWord.inferenceBackend"], required=profile.wake_word)
        self.profile = profile
        # Keep the user's inactive selection in the profile; the Hello contract
        # forbids IDs when Wake is disabled. Re-enabling uses the retained wish.
        return replace(session.config, manual=profile.manual, wake_word=profile.wake_word,
                       wake_word_ids=ids if profile.wake_word else ())

    def report(self):
        binding, snapshot = self.session.binding, self._snapshot
        requested = snapshot.payload["requestedSettings"] if snapshot else {}
        effective = snapshot.payload["effectiveSettings"] if snapshot else {}
        desired = deepcopy(self.profile.desired_settings)
        desired["wakeWord.selection"] = list(self.profile.wake_word_ids)
        unsupported = {key: "not_individually_startable_use_server_default" for key in desired if key in UNSUPPORTED_SESSION}
        unsupported.update({key: "not_a_session_preference" for key in desired if key not in (*NA_KEYS, *UNSUPPORTED_SESSION, "wakeWord.selection")})
        pending = {key: value for key, value in desired.items() if key not in unsupported
                   and p._thaw(effective.get(key)) != value}
        return SettingsReport(self.session.generation, binding.session_id if binding else None,
            snapshot.settingsRevision if snapshot else None, self.server_revision,
            p._freeze(desired), p._freeze(requested), p._freeze(effective), p._freeze(pending), p._freeze(unsupported),
            self.catalog.revision if self.catalog else None, self.catalog_stale)

    def _publish(self):
        if self.on_report:
            self.on_report(self.report())

    def set_desired(self, changes):
        """Validate the entire NA bundle before updating local intent, no wire."""
        if not isinstance(changes, dict) or not changes:
            raise SettingsError("empty_settings_patch")
        merged = deepcopy(self.profile.desired_settings)
        merged.update(deepcopy(changes))
        self._validate_changes(changes, "session", merged)
        self.profile.desired_settings = merged
        self._publish()

    def select_wake_words(self, values):
        """Canonicalize a future-Hello wish; never sends a selection patch."""
        if self.catalog is None or self.catalog_stale:
            raise SettingsError("catalog_unavailable")
        ids = self.catalog.resolve(values)
        self.catalog.validate_selection(ids, backend=self.server_requested["wakeWord.inferenceBackend"], required=self.profile.wake_word)
        self.profile.wake_word_ids = list(ids)
        self._publish()

    def _validate_changes(self, changes, scope, merged):
        if not self.schema or not isinstance(changes, dict) or not changes:
            raise SettingsError("settings_metadata_required")
        permitted = NA_KEYS if scope == "session" else SERVER_DEFAULT_KEYS
        for key, value in changes.items():
            if key not in self.schema:
                raise SettingsError("unknown_key")
            if key in SUPPRESSION_KEYS:
                raise SettingsError("read_only_runtime_authority")
            if key in UNSUPPORTED_SESSION and scope == "session":
                raise SettingsError("not_individually_startable")
            if key not in permitted:
                raise SettingsError("wrong_scope")
            self.schema[key].validate(value)
        bundle = deepcopy(self.server_requested if scope == "server" else p._thaw(self._snapshot.payload["requestedSettings"]) if self._snapshot else
                          {key: p._thaw(value.default_value) for key, value in self.schema.items() if value.scope == "session"})
        bundle.update(merged)
        for key, value in bundle.items():
            if key in self.schema:
                for other in self.schema[key].constraints.get("lessThanKeys", ()):
                    if other in bundle and value >= bundle[other]:
                        raise SettingsError("cross_field_conflict")

    async def refresh_session(self, binding=None):
        binding = binding or self.session.binding
        if binding is None:
            raise TransportLost("settings session unavailable")
        self._guard(binding.generation, binding)
        serial = self._snapshot_serial
        self._changed.clear()
        await self._command(binding, p.CommandType.SNAPSHOT_REQUEST)
        async def wait():
            while self._snapshot_serial <= serial:
                self._guard(binding.generation, binding)
                await self._changed.wait()
                self._changed.clear()
            self._guard(binding.generation, binding)
            return self._snapshot
        try:
            return await asyncio.wait_for(wait(), self.snapshot_timeout)
        except TimeoutError:
            raise SettingsError("settings_snapshot_timeout") from None

    async def _command(self, binding, kind, **fields):
        if self.session.status.state == V2TransportState.CONFIGURING:
            result = await self.session.bootstrap_command(binding, kind, allow_rejection=kind == p.CommandType.SETTINGS_PATCH, **fields)
        else:
            result = await self.session.request(kind, binding=binding, **fields)
        self._guard(binding.generation, binding)
        return result

    async def apply_session(self, binding=None):
        """At most one conflict recomputation with a fresh transport commandId."""
        binding = binding or self.session.binding
        if binding is None:
            raise TransportLost("settings session unavailable")
        async with self._session_lock:
            self._guard(binding.generation, binding)
            for attempt in range(2):
                snapshot = await self.refresh_session(binding)
                desired = deepcopy(self.profile.desired_settings)
                changes = {key: value for key, value in desired.items() if key in NA_KEYS
                           and p._thaw(snapshot.payload["requestedSettings"].get(key)) != value}
                if not changes:
                    return self.report()
                self._validate_changes(changes, "session", desired)
                result = await self._command(binding, p.CommandType.SETTINGS_PATCH,
                    baseSettingsRevision=snapshot.settingsRevision, changes=changes)
                if result.ack.result == p.AckResult.SETTINGS_REVISION_CONFLICT:
                    if attempt == 0:
                        continue
                    raise SettingsError("settings_revision_conflict")
                if not result.ack.accepted:
                    raise SettingsError("session_settings_rejected")
                confirmed = await self.refresh_session(binding)
                if confirmed.settingsRevision < result.ack.settingsRevision or any(
                        p._thaw(confirmed.payload["requestedSettings"].get(key)) != value for key, value in changes.items()):
                    raise SettingsError("settings_not_confirmed")
                # New wishes received during an await are pending, not claimed applied.
                return self.report()

    async def bootstrap(self, session, binding):
        """Media owns availability first; transport restores desired pauses last."""
        try:
            report = await self.apply_session(binding)
        except SettingsError as error:
            if error.code == "settings_snapshot_timeout":
                raise TimeoutError("settings_snapshot_timeout") from None
            raise
        # Startup cannot have an open activation under the two suppression bits.
        if report.pending and any(key in NA_KEYS for key in report.pending):
            raise SettingsError("bootstrap_settings_not_effective")

    async def read_server(self):
        generation = self.session.generation
        body = await self._get("/api/v2/settings/server")
        self._guard(generation)
        revision, requested, effective = self._parse_server(body)
        self.server_revision, self.server_requested, self.server_effective = revision, requested, effective
        self._publish()
        return p._freeze(body)

    async def patch_server(self, changes, *, admin_key):
        """Single explicit admin transaction. Any error reloads; never auto-retry.

        Call again only after a deliberate user transaction. An uncertain PATCH
        outcome is returned as an error even if the read finds the desired value.
        """
        async with self._server_lock:
            generation = self.session.generation
            await self.read_server()
            self._validate_changes(changes, "server", changes)
            revision = self.server_revision
            try:
                response = await self.http.request("PATCH", "/api/v2/settings/server",
                    body={"baseSettingsRevision": revision, "changes": deepcopy(changes)}, admin_key=admin_key)
                self._guard(generation)
                body = response.body
                if response.status != 200:
                    raise SettingsError({401: "admin_unauthorized", 403: "admin_disabled", 409: "settings_revision_conflict",
                        422: "server_settings_rejected", 500: "server_persistence_failed"}.get(response.status, "server_patch_failed"), status=response.status)
                try:
                    parsed = p.decode_settings_patch_response(body, revisionScope=p.RevisionScope.SERVER)
                except p.ProtocolError:
                    raise SettingsError("invalid_server_patch_response")
                if not parsed.accepted:
                    raise SettingsError("server_settings_rejected")
            except SettingsError as failure:
                try:
                    await self.read_server()
                except SettingsError:
                    self.last_metadata_error = "server_read_required"
                raise failure
            await self.read_server()
            if self.server_revision < body["settingsRevision"] or any(self.server_requested.get(key) != value for key, value in changes.items()):
                raise SettingsError("server_patch_not_confirmed")
            return p._freeze(body)

    async def verify_admin(self, admin_key):
        """Guarded no-change transaction, with one conflict reread/recheck.

        Select the value *after* the read, under the server transaction lock.
        Never reuse an earlier value in patch_server (its reread could turn a
        stale keycheck into a write). Public reads alone are not authentication.
        """
        async with self._server_lock:
            generation = self.session.generation
            for attempt in range(2):
                await self.read_server()
                revision = self.server_revision
                key = next(key for key in SERVER_DEFAULT_KEYS if key in self.server_requested)
                value = deepcopy(self.server_requested[key])
                response = await self.http.request("PATCH", "/api/v2/settings/server",
                    body={"baseSettingsRevision": revision, "changes": {key: value}}, admin_key=admin_key)
                self._guard(generation)
                if response.status == 409 and attempt == 0:
                    continue
                if response.status != 200:
                    raise SettingsError({401: "admin_unauthorized", 403: "admin_disabled", 409: "settings_revision_conflict",
                        422: "server_settings_rejected", 500: "server_persistence_failed"}.get(response.status, "server_patch_failed"), status=response.status)
                try:
                    parsed = p.decode_settings_patch_response(response.body, revisionScope=p.RevisionScope.SERVER)
                except p.ProtocolError:
                    raise SettingsError("invalid_server_patch_response") from None
                if (not parsed.accepted or parsed.result != p.AckResult.NO_CHANGE
                        or parsed.settingsRevision != revision or response.body.get("changedKeys")
                        or response.body.get("values", {}).get(key) != value):
                    raise SettingsError("admin_check_not_no_change")
                return revision

    async def close(self):
        tasks = [task for task in (self._refresh_task, self._session_refresh_task) if task]
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
