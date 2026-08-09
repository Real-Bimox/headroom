"""Strict wrapper lifecycle used by managed factory launches."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from click import ClickException

from headroom.cli import wrap as wrap_mod


def test_strict_port_rejects_existing_proxy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEADROOM_STRICT_PORT", "1")
    monkeypatch.setenv("HEADROOM_SESSION_TOKEN", "session-a")
    helpers = Mock()
    helpers._find_persistent_manifest.return_value = None
    helpers._check_proxy.return_value = True
    with patch.object(wrap_mod, "_live_wrap_module", return_value=helpers):
        with pytest.raises(ClickException, match="strict port 19001 is already occupied"):
            wrap_mod._ensure_proxy(19001, False)
    helpers._find_available_port.assert_not_called()


def test_strict_port_requires_session_token(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("HEADROOM_STRICT_PORT", "1")
    monkeypatch.delenv("HEADROOM_SESSION_TOKEN", raising=False)
    with pytest.raises(ClickException, match="HEADROOM_SESSION_TOKEN"):
        wrap_mod._ensure_proxy(19001, False)


def test_proxy_death_forces_nonzero_even_when_child_exits_zero(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("HEADROOM_STRICT_PORT", "1")
    monkeypatch.setenv("HEADROOM_SESSION_TOKEN", "session-a")
    proxy = Mock()
    proxy_states = iter([None, 9])
    proxy.poll.side_effect = lambda: next(proxy_states, 9)
    child = Mock()
    child.poll.side_effect = [None, 0]
    child.wait.return_value = 0
    with patch.object(wrap_mod, "_ensure_proxy", return_value=(proxy, 19001)):
        with patch.object(wrap_mod, "_register_proxy_client"):
            with patch.object(wrap_mod, "_unregister_proxy_client"):
                with patch.object(wrap_mod.subprocess, "Popen", return_value=child):
                    with pytest.raises(SystemExit) as exc:
                        wrap_mod._launch_tool(
                            binary="codex", args=(), env={}, port=19001, no_proxy=False,
                            tool_label="CODEX", env_vars_display=[], agent_type="codex",
                        )
    assert exc.value.code != 0
    assert exc.value.code == 70
