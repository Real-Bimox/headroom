"""Tests for ``headroom wrap hermes``."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from headroom.cli import wrap as wrap_mod
from headroom.cli.main import main


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_wrap_hermes_preserves_args_and_upstream(
    runner: CliRunner, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    captured: dict[str, Any] = {}

    def fake_launch_tool(**kwargs: Any) -> None:
        captured.update(kwargs)

    with patch.object(wrap_mod.shutil, "which", return_value="/usr/bin/hermes"):
        with patch.object(wrap_mod, "_launch_tool", side_effect=fake_launch_tool):
            result = runner.invoke(
                main,
                ["wrap", "hermes", "--port", "9012", "--hermes-api-url", "https://llm.test/v1", "--", "-z", "work"],
            )

    assert result.exit_code == 0, result.output
    assert captured["binary"] == "/usr/bin/hermes"
    assert captured["args"] == ("-z", "work")
    assert captured["port"] == 9012
    assert captured["openai_api_url"] == "https://llm.test/v1"
    assert captured["agent_type"] == "hermes"


def test_wrap_hermes_requires_upstream(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("HEADROOM_HERMES_API_URL", raising=False)
    with patch.object(wrap_mod.shutil, "which", return_value="/usr/bin/hermes"):
        result = runner.invoke(main, ["wrap", "hermes"])
    assert result.exit_code != 0
    assert "Hermes upstream API URL is required" in result.output


def test_wrap_hermes_missing_binary(runner: CliRunner) -> None:
    with patch.object(wrap_mod.shutil, "which", return_value=None):
        result = runner.invoke(main, ["wrap", "hermes", "--hermes-api-url", "https://llm.test/v1"])
    assert result.exit_code != 0
    assert "'hermes' not found" in result.output
