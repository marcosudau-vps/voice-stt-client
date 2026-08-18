"""
``LogQueryService`` — the only query interface the UI knows (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §8 (the four methods) and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §10.3: *"LogProvider ist ein Protokoll;
LogQueryService ist eine REGISTRY, keine fest verdrahtete Liste. Ohne sie
muesste spaeter jeder Aufrufer um einen Parameter erweitert werden."*

The service adds exactly two things to a plain dict of providers, and both
are properties of a boundary rather than features:

* **It never raises either.** A provider is contractually non-throwing, but
  the *injected* object may be any implementation of the protocol, including
  a future remote provider. O-05 stops the logging failure domain here, at
  the last point before the Qt thread.
* **An unknown ``provider_id`` is a state, not an exception.** The UI keeps a
  provider id in its own state (a combo box, a restored setting); a provider
  that has gone away must show as ``UNAVAILABLE``, not crash the view.

Registration order is preserved, so ``providers()`` returns the local
provider first for as long as it is registered first — the UI needs a stable
default without inventing a ranking of its own.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Mapping, Optional, Tuple

from .base import (
    LogProvider,
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryPage,
)

DEFAULT_LIMIT = 200


class LogQueryService:
    """Registry over ``LogProvider`` implementations."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        # dict preserves insertion order; registration happens on the Qt or
        # main thread, queries on the query worker thread.
        self._providers: Dict[str, LogProvider] = {}

    def register(self, provider: LogProvider) -> None:
        provider_id = str(getattr(provider, "provider_id", "") or "")
        if not provider_id:
            raise ValueError("provider_id must be a non-empty string")
        with self._lock:
            self._providers[provider_id] = provider

    def unregister(self, provider_id: str) -> None:
        with self._lock:
            self._providers.pop(str(provider_id), None)

    def provider_ids(self) -> Tuple[str, ...]:
        with self._lock:
            return tuple(self._providers)

    def providers(self) -> Tuple[ProviderStatus, ...]:
        """§8: the status of every registered provider. Must answer without
        I/O — the UI calls it on every filter change (§8.1)."""
        with self._lock:
            registered = list(self._providers.items())
        statuses = []
        for provider_id, provider in registered:
            try:
                status = provider.status()
            except Exception as exc:  # noqa: BLE001 - O-05 boundary
                status = ProviderStatus(
                    provider_id, provider_id, ProviderState.ERROR, _short(exc)
                )
            statuses.append(status)
        return tuple(statuses)

    def query(
        self,
        provider_id: str,
        filter: QueryFilter,  # noqa: A002 - frozen parameter name (§8)
        cursor: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> QueryPage:
        provider = self._provider(provider_id)
        if provider is None:
            return _unavailable_page(provider_id, "unbekannter Provider")
        try:
            return provider.query(filter, cursor, limit)
        except Exception as exc:  # noqa: BLE001 - O-05: a provider defect is
            # a display state, never an exception in the Qt thread.
            return QueryPage(
                provider_id=str(provider_id),
                records=(),
                next_cursor=None,
                complete=False,
                status=ProviderStatus(
                    str(provider_id), str(provider_id), ProviderState.ERROR, _short(exc)
                ),
            )

    def fetch_raw(
        self, provider_id: str, record_id: str
    ) -> Optional[Mapping[str, Any]]:
        provider = self._provider(provider_id)
        if provider is None:
            return None
        try:
            return provider.fetch_raw(record_id)
        except Exception:  # noqa: BLE001 - O-05 boundary
            return None

    def _provider(self, provider_id: str) -> Optional[LogProvider]:
        with self._lock:
            return self._providers.get(str(provider_id))


def _short(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {str(exc)[:120]}"


def _unavailable_page(provider_id: str, detail: str) -> QueryPage:
    status = ProviderStatus(
        str(provider_id), str(provider_id), ProviderState.UNAVAILABLE, detail
    )
    return QueryPage(
        provider_id=str(provider_id),
        records=(),
        next_cursor=None,
        complete=False,
        status=status,
    )


__all__ = ["LogQueryService", "DEFAULT_LIMIT"]
