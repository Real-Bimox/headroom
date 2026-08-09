"""Regression tests for proxy optional-dependency diagnostics."""

from __future__ import annotations

from unittest.mock import patch

from headroom.proxy.dependencies import check_proxy_dependencies


def test_proxy_dependency_check_reports_http2_extra() -> None:
    """A missing h2 must recommend the proxy extra, not fail at httpx startup."""
    with patch("headroom.proxy.dependencies.find_spec", side_effect=lambda name: None if name == "h2" else object()):
        status = check_proxy_dependencies()

    assert status.missing == ("httpx[http2]",)
    assert status.install_hint == 'pip install "headroom-ai[proxy]"'


def test_proxy_dependency_check_is_ready_when_all_modules_exist() -> None:
    with patch("headroom.proxy.dependencies.find_spec", return_value=object()):
        assert check_proxy_dependencies().ready
