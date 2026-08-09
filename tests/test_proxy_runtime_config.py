from headroom.proxy.runtime_config import ResolvedRuntimeConfig, eager_preload_enabled


def test_runtime_config_has_one_precedence_boundary() -> None:
    config = ResolvedRuntimeConfig.resolve(
        mode=None, stateless=False, telemetry=True, no_telemetry=True,
        environ={"HEADROOM_MODE": "token", "HEADROOM_STATELESS": "yes"},
    )
    assert config.mode == "token"
    assert config.stateless is True
    assert config.telemetry_enabled is False


def test_runtime_config_honors_explicit_empty_environment() -> None:
    config = ResolvedRuntimeConfig.resolve(
        mode=None, stateless=False, telemetry=False, no_telemetry=False, environ={}
    )
    assert config.mode == "cache"
    assert config.stateless is False


def test_eager_preload_is_explicit_opt_in() -> None:
    assert eager_preload_enabled({}) is False
    assert eager_preload_enabled({"HEADROOM_EAGER_PRELOAD": "1"}) is True
