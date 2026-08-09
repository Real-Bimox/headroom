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


def eager_preload_enabled(environ: Mapping[str, str] | None = None) -> bool:
    """Whether optional compressor/model warmup may delay proxy readiness."""
    env = os.environ if environ is None else environ
    return _enabled(env.get("HEADROOM_EAGER_PRELOAD"))


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
        # An explicitly supplied empty mapping is meaningful in tests and for
        # embedded deployments: it must not silently fall back to process env.
        env = os.environ if environ is None else environ
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
