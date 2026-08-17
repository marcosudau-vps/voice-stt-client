"""
Redaction rules for the canonical record (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §4 (rules R-1..R-12) and
``LOGGING_DECISIONS_FREEZE_V1.md`` (FD-C11, FD-C12). Pure functions, no I/O,
no Qt, no sqlite3.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from types import MappingProxyType
from typing import Any, Mapping, Optional
from urllib.parse import urlsplit, urlunsplit

# --- Rule R-3 ---------------------------------------------------------------
# Key-based redaction. Keys are compared case-insensitively and without any
# ``_`` / ``-``. A hit replaces the value on every nesting level with
# "[redacted]". Value heuristics are forbidden (R-3).

SENSITIVE_KEYS = frozenset({
    "authorization",
    "token",
    "accesstoken",
    "apikey",
    "adminkey",
    "password",
    "secret",
    "cookie",
    "credential",
})

# --- Rule R-10 --------------------------------------------------------------
# Transcript content fields. Kept by character count when
# ``store_transcription_content`` is disabled.

TRANSCRIPT_KEYS = frozenset({
    "text",
    "displayText",
    "rawText",
    "stableText",
    "unstableText",
    "committedStableText",
    "visualUnstableText",
})

_REDACTED_VALUE = "[redacted]"

# Rule R-12 bounds.
MAX_DEPTH = 16
MAX_NODES = 500


def unfreeze(
    value: Any,
    *,
    max_depth: int = MAX_DEPTH,
    max_nodes: int = MAX_NODES,
) -> Any:
    """``MappingProxyType -> dict``, ``tuple -> list``, ``frozenset -> sorted
    list``, recursively (CONTRACTS §4.1, FD-C11).

    Required before every serialization: ``json.dumps`` understands neither
    ``MappingProxyType`` nor ``tuple`` nor ``frozenset``. A blob
    ``default=str`` on the container level would collapse the whole payload
    into one string and defeat the key-based redaction — therefore
    ``unfreeze`` runs always first. Depth/node bounds follow R-12 and cut +
    mark pathological structures.
    """
    budget = _Budget(max_depth, max_nodes)
    return _unfreeze_value(value, budget, 0)


def _unfreeze_value(value: Any, budget: _Budget, depth: int) -> Any:
    if not budget.account():
        return _truncated("max_nodes")
    if isinstance(value, Mapping):
        if depth >= budget.max_depth:
            return _truncated("max_depth")
        return {
            str(key): _unfreeze_value(item, budget, depth + 1)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        if depth >= budget.max_depth:
            return _truncated("max_depth")
        return [_unfreeze_value(item, budget, depth + 1) for item in value]
    if isinstance(value, (set, frozenset)):
        if depth >= budget.max_depth:
            return _truncated("max_depth")
        return [
            _unfreeze_value(item, budget, depth + 1)
            for item in sorted(value, key=lambda item: _leaf_to_str(item))
        ]
    if _is_primitive(value):
        return value
    return _leaf_to_str(value)


def _key_normalized(key: Any) -> str:
    return str(key).lower().replace("_", "").replace("-", "")


def _is_primitive(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


class _Budget:
    __slots__ = ("max_depth", "max_nodes", "nodes")

    def __init__(self, max_depth: int, max_nodes: int) -> None:
        self.max_depth = max_depth
        self.max_nodes = max_nodes
        self.nodes = 0

    def account(self) -> bool:
        self.nodes += 1
        return self.nodes <= self.max_nodes


def _leaf_to_str(value: Any) -> str:
    """Leaf fallback with guards: a throwing ``__str__``/``__repr__`` must
    never escape the redaction layer (WP failure/edge case)."""
    try:
        return str(value)
    except Exception:  # noqa: BLE001 - redaction must never raise
        pass
    try:
        return repr(value)
    except Exception:  # noqa: BLE001
        return "<unrenderable>"


def _redacted_transcript(value: Any, budget: _Budget) -> str:
    """R-10 replacement keeping the character count of the content."""
    if isinstance(value, str):
        return f"[redacted:{len(value)} chars]"
    total = 0
    def _count(item: Any) -> None:
        nonlocal total
        if not budget.account():
            return
        if isinstance(item, Mapping):
            for sub in item.values():
                _count(sub)
        elif isinstance(item, (list, tuple, set, frozenset)):
            for sub in item:
                _count(sub)
        else:
            total += len(_leaf_to_str(item))
    _count(value)
    return f"[redacted:{total} chars]"


def _sanitize_url(value: str) -> str:
    """R-8: any URL loses query and fragment before storage."""
    if not isinstance(value, str):
        return value
    try:
        parts = urlsplit(value)
    except ValueError:
        return value
    if not parts.scheme:
        return value
    try:
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except ValueError:
        return value


_URL_RE = re.compile(r"(?i)\b(?:https?|wss?|ftp)://[^\s<>\"']+")


def _sanitize_urls_in_text(text: str) -> str:
    """R-8 for embedded URLs inside free text (e.g. target_url messages)."""
    if not isinstance(text, str):
        return text
    def _replace(match: re.Match) -> str:
        return _sanitize_url(match.group(0))
    return _URL_RE.sub(_replace, text)


def shorten_user_paths(text: str, user_profile: Optional[object] = None) -> str:
    """R-9: shorten the user profile root to ``~``, including in tracebacks.

    ``user_profile`` may be a path-like (defaults to ``Path.home()``). All
    occurrences are replaced case-insensitively.
    """
    if not isinstance(text, str):
        return text
    profile = Path(user_profile).expanduser() if user_profile is not None else Path.home()
    variants: list[str] = []
    for variant in (str(profile), str(profile).replace("\\", "/"), profile.as_posix()):
        if variant and variant not in variants:
            variants.append(variant)
    for variant in variants:
        if variant in ("/", ".", "") or len(variant) < 3:
            continue
        text = re.sub(re.escape(variant), "~", text, flags=re.IGNORECASE)
    return text


def _truncated(reason: str) -> dict[str, Any]:
    return {"_truncated": True, "_reason": reason}


def _redact_value(
    value: Any,
    *,
    store_transcription_content: bool,
    user_profile: Optional[object],
    budget: _Budget,
    depth: int,
) -> Any:
    if not budget.account():
        return _truncated("max_nodes")
    if isinstance(value, Mapping):
        if depth >= budget.max_depth:
            return _truncated("max_depth")
        out: dict[str, Any] = {}
        for key, item in value.items():
            norm_key = _key_normalized(key)
            if norm_key in SENSITIVE_KEYS:
                out[key] = _REDACTED_VALUE
            elif not store_transcription_content and key in TRANSCRIPT_KEYS:
                out[key] = _redacted_transcript(item, budget)
            else:
                out[key] = _redact_value(
                    item,
                    store_transcription_content=store_transcription_content,
                    user_profile=user_profile,
                    budget=budget,
                    depth=depth + 1,
                )
        return out
    if isinstance(value, (list, tuple, set, frozenset)):
        if depth >= budget.max_depth:
            return _truncated("max_depth")
        if isinstance(value, (set, frozenset)):
            items = sorted(value, key=lambda item: _leaf_to_str(item))
        else:
            items = list(value)
        return [
            _redact_value(
                item,
                store_transcription_content=store_transcription_content,
                user_profile=user_profile,
                budget=budget,
                depth=depth + 1,
            )
            for item in items
        ]
    if isinstance(value, str):
        redacted = _sanitize_url(value)
        return shorten_user_paths(redacted, user_profile)
    if _is_primitive(value):
        return value
    return _leaf_to_str(value)


def redact_mapping(
    value: Mapping[str, Any],
    *,
    store_transcription_content: bool = False,
    user_profile: Optional[object] = None,
    max_depth: int = MAX_DEPTH,
    max_nodes: int = MAX_NODES,
) -> Mapping[str, Any]:
    """Key-based recursive redaction of a mapping (rules R-3, R-8, R-9, R-10,
    R-12). Returns a new plain dict; the input is never mutated.

    The input must be a Mapping — a scalar or list ``details`` object is a
    contract violation and raises (the normalizer never raises and converts
    this into ``None``/``malformed``). The result is JSON-serializable without
    relying on ``default=`` for containers: leaves that are not JSON
    primitives are converted with the guarded ``str``/``repr`` fallback
    (R-11, leaf-only fallback).
    """
    if not isinstance(value, Mapping):
        raise ValueError("redact_mapping requires a mapping")
    budget = _Budget(max_depth, max_nodes)
    result = _redact_value(
        value,
        store_transcription_content=store_transcription_content,
        user_profile=user_profile,
        budget=budget,
        depth=0,
    )
    if isinstance(result, Mapping):
        return result
    return {"_unsupported": True}


def redact_text(
    text: str,
    *,
    store_transcription_content: bool = False,
    user_profile: Optional[object] = None,
) -> str:
    """R-10 (unstructured log text), R-8 (embedded URLs) and R-9 (paths)
    for free text — e.g. ``record.getMessage()``.

    Template recognition is intentionally limited to the real production
    transcription lines (``core/stt_session.py`` "Final/Realtime [seg=…]",
    ``core/controller.py`` "…existing=%r, new=%r", WP N-02). No value
    heuristic (R-3).
    """
    redacted = shorten_user_paths(text, user_profile)
    redacted = _sanitize_urls_in_text(redacted)
    if store_transcription_content:
        return redacted
    redacted = _TRANSCRIPT_LINE_RE.sub(_replace_line_content, redacted)
    redacted = _EXISTING_RE.sub(_replace_repr, redacted)
    redacted = _NEW_RE.sub(_replace_repr, redacted)
    return redacted


_TRANSCRIPT_LINE_RE = re.compile(
    r"^(?P<prefix>(?:Final|Realtime)\s+\[seg=\d+\]:\s*)(?P<content>.*)$",
    flags=re.MULTILINE,
)
_QUOTED_REPR_RE = (
    r"(?:'(?:\\.|[^'\\])*')"
    r'|(?:"(?:\\.|[^"\\])*")'
)
_EXISTING_RE = re.compile(r"(?P<pre>existing=)(?P<val>" + _QUOTED_REPR_RE + ")")
_NEW_RE = re.compile(r"(?P<pre>new=)(?P<val>" + _QUOTED_REPR_RE + ")")


def _replace_line_content(match: re.Match) -> str:
    content = match.group("content")
    return f"{match.group('prefix')}[redacted:{len(content)} chars]"


def _repr_length(token: str) -> int:
    """Character count of a Python-repr'd string token."""
    try:
        decoded = ast.literal_eval(token)
    except Exception:  # noqa: BLE001
        decoded = None
    if isinstance(decoded, str):
        return len(decoded)
    if len(token) >= 2 and token[0] == token[-1] and token[0] in ("'", '"'):
        return len(token) - 2
    return len(token)


def _replace_repr(match: re.Match) -> str:
    value = match.group("val")
    length = _repr_length(value)
    return f"{match.group('pre')}'[redacted:{length} chars]'"