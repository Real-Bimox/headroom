"""Tests for OpenAI chat/completions effort routing and turn classification."""

from __future__ import annotations

from headroom.proxy.output_shaper import (
    OutputShaperSettings,
    route_openai_chat_effort,
    shape_openai_chat_request,
)
from headroom.proxy.output_turn_policy import (
    TurnKind,
    classify_openai_chat_messages,
)

_ENABLED = OutputShaperSettings(enabled=True)


# ---------------------------------------------------------------------------
# classify_openai_chat_messages
# ---------------------------------------------------------------------------


def test_classify_empty_messages() -> None:
    assert classify_openai_chat_messages([]) == TurnKind.UNKNOWN


def test_classify_user_text_is_new_ask() -> None:
    msgs = [{"role": "user", "content": "hello"}]
    assert classify_openai_chat_messages(msgs) == TurnKind.NEW_USER_ASK


def test_classify_trailing_tool_messages_is_mechanical() -> None:
    msgs = [
        {"role": "user", "content": "read the file"},
        {"role": "assistant", "content": "", "tool_calls": [{"id": "tc_1"}]},
        {"role": "tool", "tool_call_id": "tc_1", "content": "file contents here"},
    ]
    assert classify_openai_chat_messages(msgs) == TurnKind.MECHANICAL_CONTINUATION


def test_classify_multiple_tool_messages_is_mechanical() -> None:
    msgs = [
        {"role": "assistant", "content": "", "tool_calls": [{"id": "tc_1"}, {"id": "tc_2"}]},
        {"role": "tool", "tool_call_id": "tc_1", "content": "output 1"},
        {"role": "tool", "tool_call_id": "tc_2", "content": "output 2"},
    ]
    assert classify_openai_chat_messages(msgs) == TurnKind.MECHANICAL_CONTINUATION


def test_classify_user_after_assistant_is_new_ask() -> None:
    msgs = [
        {"role": "assistant", "content": "done"},
        {"role": "tool", "tool_call_id": "tc_1", "content": "output"},
        {"role": "user", "content": "now do something else"},
    ]
    assert classify_openai_chat_messages(msgs) == TurnKind.NEW_USER_ASK


def test_classify_tool_error_is_error_continuation() -> None:
    msgs = [
        {"role": "assistant", "content": "", "tool_calls": [{"id": "tc_1"}]},
        {"role": "tool", "tool_call_id": "tc_1", "content": '{"error": "permission denied"}'},
    ]
    assert classify_openai_chat_messages(msgs) == TurnKind.ERROR_CONTINUATION


def test_classify_system_only_is_unknown() -> None:
    msgs = [{"role": "system", "content": "you are helpful"}]
    assert classify_openai_chat_messages(msgs) == TurnKind.UNKNOWN


# ---------------------------------------------------------------------------
# route_openai_chat_effort
# ---------------------------------------------------------------------------


def test_route_chat_effort_lowers_on_mechanical_turn() -> None:
    body = {"reasoning_effort": "high"}
    labels = route_openai_chat_effort(body, TurnKind.MECHANICAL_CONTINUATION, _ENABLED)
    assert labels == ["output_shaper:chat_reasoning_effort:high->low"]
    assert body["reasoning_effort"] == "low"


def test_route_chat_effort_noop_on_new_user_ask() -> None:
    body = {"reasoning_effort": "high"}
    labels = route_openai_chat_effort(body, TurnKind.NEW_USER_ASK, _ENABLED)
    assert labels == []
    assert body["reasoning_effort"] == "high"


def test_route_chat_effort_noop_when_absent() -> None:
    body: dict = {}
    labels = route_openai_chat_effort(body, TurnKind.MECHANICAL_CONTINUATION, _ENABLED)
    assert labels == []
    assert "reasoning_effort" not in body


def test_route_chat_effort_noop_when_already_low() -> None:
    body = {"reasoning_effort": "low"}
    labels = route_openai_chat_effort(body, TurnKind.MECHANICAL_CONTINUATION, _ENABLED)
    assert labels == []
    assert body["reasoning_effort"] == "low"


def test_route_chat_effort_medium_to_low() -> None:
    body = {"reasoning_effort": "medium"}
    labels = route_openai_chat_effort(body, TurnKind.MECHANICAL_CONTINUATION, _ENABLED)
    assert labels == ["output_shaper:chat_reasoning_effort:medium->low"]
    assert body["reasoning_effort"] == "low"


# ---------------------------------------------------------------------------
# shape_openai_chat_request (integration)
# ---------------------------------------------------------------------------


def test_shape_chat_request_applies_effort_and_verbosity() -> None:
    body = {
        "messages": [
            {"role": "user", "content": "read foo"},
            {"role": "assistant", "content": "", "tool_calls": [{"id": "tc_1"}]},
            {"role": "tool", "tool_call_id": "tc_1", "content": "file contents"},
        ],
        "reasoning_effort": "high",
    }
    result = shape_openai_chat_request(body, _ENABLED)
    assert result.changed is True
    assert any("chat_reasoning_effort" in lbl for lbl in result.labels)
    assert body["reasoning_effort"] == "low"


def test_shape_chat_request_no_effort_on_user_ask() -> None:
    body = {
        "messages": [
            {"role": "user", "content": "what is 2+2?"},
        ],
        "reasoning_effort": "high",
    }
    result = shape_openai_chat_request(body, _ENABLED)
    assert body["reasoning_effort"] == "high"


def test_shape_chat_request_disabled_is_noop() -> None:
    body = {
        "messages": [
            {"role": "assistant", "content": ""},
            {"role": "tool", "tool_call_id": "tc_1", "content": "output"},
        ],
        "reasoning_effort": "high",
    }
    disabled = OutputShaperSettings(enabled=False)
    result = shape_openai_chat_request(body, disabled)
    assert result.changed is False
    assert body["reasoning_effort"] == "high"
