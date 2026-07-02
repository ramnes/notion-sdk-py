"""HTTP backend compatibility shim."""

import os
from types import ModuleType
from typing import Any, List, Tuple, Type

# Probed in priority order: httpx2 wins when both are installed.
_BACKENDS: List[ModuleType] = []

try:
    import httpx2 as _httpx2

    _BACKENDS.append(_httpx2)
except ImportError:
    pass

try:
    import httpx as _httpx

    _BACKENDS.append(_httpx)
except ImportError:
    pass

if not _BACKENDS:
    raise ImportError(
        "notion-client requires either 'httpx2' or 'httpx' to be installed. "
        "Install one with `pip install notion-client` (httpx) or "
        "`pip install notion-client[httpx2]` (httpx2)."
    )

# The active backend used for clients the SDK constructs on its own behalf.
# httpx2 is preferred; ``NOTION_HTTP_BACKEND`` (mainly for tests/CI) can force a
# specific backend even when both are installed, e.g. ``NOTION_HTTP_BACKEND=httpx``.
httpx: ModuleType = _BACKENDS[0]
_preferred = os.environ.get("NOTION_HTTP_BACKEND")
if _preferred is not None:
    _match = next((b for b in _BACKENDS if b.__name__ == _preferred), None)
    if _match is None:
        raise ImportError(
            f"NOTION_HTTP_BACKEND={_preferred!r} was requested, but that package "
            f"is not installed. Available: "
            f"{', '.join(b.__name__ for b in _BACKENDS)}."
        )
    httpx = _match


Client = httpx.Client
AsyncClient = httpx.AsyncClient
Request = httpx.Request
Response = httpx.Response
Headers = httpx.Headers


def _collect(name: str) -> Tuple[Type[BaseException], ...]:
    """Gather the named exception class from every installed backend."""
    found: List[Type[BaseException]] = []
    for backend in _BACKENDS:
        exc = getattr(backend, name, None)
        if isinstance(exc, type) and exc not in found:
            found.append(exc)
    return tuple(found)


HTTP_STATUS_ERRORS: Tuple[Type[BaseException], ...] = _collect("HTTPStatusError")
TIMEOUT_EXCEPTIONS: Tuple[Type[BaseException], ...] = _collect("TimeoutException")


def status_error_response(error: Any) -> Any:
    """Return a caught HTTP status error's ``.response``."""

    return error.response
