"""Tests for `headroom wrap qwen` command."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from headroom.cli import wrap as wrap_mod
from headroom.cli.main import main
from headroom.providers.qwen import CODING_PLAN_API_URL, TOKEN_PLAN_API_URL


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_wrap_qwen_launch_coding_plan(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Qwen Code launches with coding plan defaults."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(main, ["wrap", "qwen"])

    assert result.exit_code == 0, result.output
    env = captured["env"]
    assert isinstance(env, dict)
    assert captured["tool_label"] == "QWEN"
    assert captured["agent_type"] == "qwen"
    assert captured["openai_api_url"] == CODING_PLAN_API_URL
    assert env["OPENAI_BASE_URL"] == "http://127.0.0.1:8787/v1"


def test_wrap_qwen_token_plan(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--plan token selects the token-plan upstream URL."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(main, ["wrap", "qwen", "--plan", "token"])

    assert result.exit_code == 0, result.output
    assert captured["openai_api_url"] == TOKEN_PLAN_API_URL


def test_wrap_qwen_custom_port(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Custom --port is reflected in OPENAI_BASE_URL."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(main, ["wrap", "qwen", "--port", "9999"])

    assert result.exit_code == 0, result.output
    assert captured["port"] == 9999
    assert captured["env"]["OPENAI_BASE_URL"] == "http://127.0.0.1:9999/v1"


def test_wrap_qwen_custom_api_url_overrides_plan(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--qwen-api-url overrides the plan default."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(
                    main,
                    ["wrap", "qwen", "--qwen-api-url", "https://custom.example.com/v1"],
                )

    assert result.exit_code == 0, result.output
    assert captured["openai_api_url"] == "https://custom.example.com/v1"


def test_wrap_qwen_with_project_name(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Project name is encoded in OPENAI_BASE_URL."""
    project_dir = tmp_path / "my-project"
    project_dir.mkdir()
    monkeypatch.chdir(project_dir)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            result = runner.invoke(main, ["wrap", "qwen", "--port", "7000"])

    assert result.exit_code == 0, result.output
    assert captured["env"]["OPENAI_BASE_URL"] == "http://127.0.0.1:7000/p/my-project/v1"


def test_wrap_qwen_passes_args(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Extra args after -- are forwarded to the qwen binary."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(
                    main, ["wrap", "qwen", "--", "-m", "qwen3-coder-plus"]
                )

    assert result.exit_code == 0, result.output
    assert captured["args"] == ("-m", "qwen3-coder-plus")


def test_wrap_qwen_not_found(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Error message when qwen binary is not found."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    with patch.object(wrap_mod.shutil, "which", return_value=None):
        result = runner.invoke(main, ["wrap", "qwen"])

    assert result.exit_code == 1
    assert "Error: 'qwen' not found in PATH" in result.output


def test_wrap_qwen_no_proxy(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--no-proxy flag prevents proxy startup."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(main, ["wrap", "qwen", "--no-proxy"])

    assert result.exit_code == 0, result.output
    assert captured["no_proxy"] is True


def test_wrap_qwen_learn_memory(
    runner: CliRunner,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """--learn and --memory flags are forwarded."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("HEADROOM_CONTEXT_TOOL", raising=False)

    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:  # noqa: ANN003
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="qwen"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            with patch.object(wrap_mod, "_project_name_from_cwd", return_value=None):
                result = runner.invoke(main, ["wrap", "qwen", "--learn", "--memory"])

    assert result.exit_code == 0, result.output
    assert captured["learn"] is True
    assert captured["memory"] is True
