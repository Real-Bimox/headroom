"""Runtime helpers for Qwen Code integrations."""

from __future__ import annotations

import os
from collections.abc import Mapping

from headroom.providers.codex import proxy_base_url as codex_proxy_base_url
from headroom.proxy.project_context import with_project_prefix

CODING_PLAN_API_URL = "https://coding-intl.dashscope.aliyuncs.com/v1"
TOKEN_PLAN_API_URL = "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"

CODING_PLAN_ENV_KEY = "BAILIAN_CODING_PLAN_API_KEY"
TOKEN_PLAN_ENV_KEY = "DASHSCOPE_API_KEY"

_VALID_PLANS = ("coding", "token")


def api_key_env_for_plan(plan: str) -> str:
    """Return the API-key environment variable name for *plan*."""
    if plan == "token":
        return TOKEN_PLAN_ENV_KEY
    return CODING_PLAN_ENV_KEY


def default_api_url(plan: str) -> str:
    """Return the default upstream API URL for *plan*."""
    if plan == "token":
        return TOKEN_PLAN_API_URL
    return CODING_PLAN_API_URL


def build_launch_env(
    port: int,
    environ: Mapping[str, str] | None = None,
    project: str | None = None,
) -> tuple[dict[str, str], list[str]]:
    """Build environment variables for Qwen Code through the local proxy.

    Qwen Code uses an OpenAI-compatible client. Its base URL is overridable
    via the standard ``OPENAI_BASE_URL`` environment variable, so we point it
    at the local proxy. The proxy forwards the request — including the
    ``Authorization: Bearer`` token from the plan-specific API-key env var —
    to the real upstream configured by ``--openai-api-url``.

    ``project`` (the wrap launch directory) is encoded as a ``/p/<name>``
    base-URL prefix so the proxy can attribute savings per project.
    """
    env = dict(environ or os.environ)
    base_url = with_project_prefix(codex_proxy_base_url(port), project)
    env["OPENAI_BASE_URL"] = base_url
    return env, [f"OPENAI_BASE_URL={base_url}"]
