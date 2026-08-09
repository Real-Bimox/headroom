"""Runtime dependency checks for commands that start the proxy.

The package deliberately keeps the proxy stack optional for library users.  A
CLI command must therefore check the *installed* environment before importing
the server, rather than failing later with an unrelated ``ImportError``.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec


_PROXY_MODULES = {
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "httpx": "httpx",
    "h2": "httpx[http2]",
}


@dataclass(frozen=True)
class ProxyDependencyStatus:
    """The proxy runtime dependencies visible to the current interpreter."""

    missing: tuple[str, ...]

    @property
    def ready(self) -> bool:
        return not self.missing

    @property
    def install_hint(self) -> str:
        return 'pip install "headroom-ai[proxy]"'


def check_proxy_dependencies() -> ProxyDependencyStatus:
    """Return missing proxy dependencies without importing optional packages."""
    missing = tuple(
        distribution for module, distribution in _PROXY_MODULES.items() if find_spec(module) is None
    )
    return ProxyDependencyStatus(missing=missing)
