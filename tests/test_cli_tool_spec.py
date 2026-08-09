from headroom.cli.tool_spec import ToolSpec


def test_tool_spec_selects_first_available_executable() -> None:
    spec = ToolSpec("demo", "DEMO", ("missing", "present"), "the demo CLI")
    assert spec.find_binary(lambda name: "/bin/present" if name == "present" else None) == "/bin/present"
    assert "missing/present" in spec.missing_message()
