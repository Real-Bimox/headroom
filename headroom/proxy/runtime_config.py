"""Small, side-effect-free resolution layer for proxy process settings.

CLI parsing, environment lookup, and server construction used to each make
their own decisions.  Keep the precedence rules in one object so wrappers,
the CLI, and future config-file support share the same boundary.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

from headroom.proxy.modes import PROXY_MODE_CACHE, normalize_proxy_mode


def _enabled(value: str | None) -> bool:
    return (value or "").lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class ResolvedRuntimeConfig:
    """Process-wide settings resolved before constructing ``ProxyConfig``."""

    mode: str
    stateless: bool
    telemetry_enabled: bool | None

    @classmethod
    def resolve(
        cls,
        *,
        mode: str | None,
        stateless: bool,
        telemetry: bool,
        no_telemetry: bool,
        environ: Mapping[str, str] | None = None,
    ) -> "ResolvedRuntimeConfig":
        env = environ or os.environ
        resolved_telemetry: bool | None = None
        if telemetry:
            resolved_telemetry = True
        if no_telemetry:
            resolved_telemetry = False
        return cls(
            mode=normalize_proxy_mode(mode or env.get("HEADROOM_MODE") or PROXY_MODE_CACHE),
            stateless=stateless or _enabled(env.get("HEADROOM_STATELESS")),
            telemetry_enabled=resolved_telemetry,
        )
