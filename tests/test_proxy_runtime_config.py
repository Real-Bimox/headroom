from headroom.proxy.runtime_config import ResolvedRuntimeConfig


def test_runtime_config_has_one_precedence_boundary() -> None:
    config = ResolvedRuntimeConfig.resolve(
        mode=None, stateless=False, telemetry=True, no_telemetry=True,
        environ={"HEADROOM_MODE": "token", "HEADROOM_STATELESS": "yes"},
    )
    assert config.mode == "token"
    assert config.stateless is True
    assert config.telemetry_enabled is False
