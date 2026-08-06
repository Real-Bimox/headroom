"""Tests for the Qwen Code provider runtime helpers."""

from __future__ import annotations

from headroom.providers.qwen import (
    CODING_PLAN_API_URL,
    CODING_PLAN_ENV_KEY,
    TOKEN_PLAN_API_URL,
    TOKEN_PLAN_ENV_KEY,
    api_key_env_for_plan,
    build_launch_env,
)
from headroom.providers.qwen.runtime import default_api_url


def test_coding_plan_constants() -> None:
    assert CODING_PLAN_API_URL == "https://coding-intl.dashscope.aliyuncs.com/v1"
    assert CODING_PLAN_ENV_KEY == "BAILIAN_CODING_PLAN_API_KEY"


def test_token_plan_constants() -> None:
    assert TOKEN_PLAN_API_URL == "https://token-plan.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
    assert TOKEN_PLAN_ENV_KEY == "DASHSCOPE_API_KEY"


def test_api_key_env_for_plan_coding() -> None:
    assert api_key_env_for_plan("coding") == "BAILIAN_CODING_PLAN_API_KEY"


def test_api_key_env_for_plan_token() -> None:
    assert api_key_env_for_plan("token") == "DASHSCOPE_API_KEY"


def test_api_key_env_for_plan_unknown_defaults_to_coding() -> None:
    assert api_key_env_for_plan("anything") == "BAILIAN_CODING_PLAN_API_KEY"


def test_default_api_url_coding() -> None:
    assert default_api_url("coding") == CODING_PLAN_API_URL


def test_default_api_url_token() -> None:
    assert default_api_url("token") == TOKEN_PLAN_API_URL


def test_build_launch_env_sets_openai_base_url() -> None:
    env, display = build_launch_env(8787, environ={})

    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:8787/v1"
    assert display == ["OPENAI_BASE_URL=http://127.0.0.1:8787/v1"]


def test_build_launch_env_custom_port() -> None:
    env, _display = build_launch_env(9999, environ={})
    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:9999/v1"


def test_build_launch_env_applies_project_prefix() -> None:
    env, _display = build_launch_env(8787, environ={}, project="my-project")
    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:8787/p/my-project/v1"


def test_build_launch_env_preserves_existing_env() -> None:
    """Existing environment variables are carried through."""
    env, _display = build_launch_env(
        8787,
        environ={"BAILIAN_CODING_PLAN_API_KEY": "sk-test", "HOME": "/home/user"},
    )
    assert env["BAILIAN_CODING_PLAN_API_KEY"] == "sk-test"
    assert env["HOME"] == "/home/user"
    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:8787/v1"
