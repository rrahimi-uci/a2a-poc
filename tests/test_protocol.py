"""Unit tests for the A2A protocol data models."""

import json

from common.a2a_protocol import (
    AgentCard,
    ErrorCodes,
    JSONRPCRequest,
    Message,
    MessagePart,
    MessageRole,
    Task,
    TaskState,
    TaskStatus,
)


def test_message_defaults_and_ids():
    msg = Message(role=MessageRole.USER, parts=[MessagePart(text="hi")])
    assert msg.kind == "message"
    assert msg.role == MessageRole.USER
    assert msg.messageId  # auto-generated uuid
    assert msg.parts[0].text == "hi"
    assert msg.parts[0].kind == "text"


def test_task_is_json_serializable_including_timestamp():
    """Regression: Message.timestamp is a datetime; model_dump(mode='json')
    must produce a payload that json.dumps can serialize (this is what travels
    over the wire between agents)."""
    msg = Message(role=MessageRole.AGENT, parts=[MessagePart(text="done")])
    task = Task(messages=[msg], status=TaskStatus(state=TaskState.COMPLETED, message=msg))
    payload = task.model_dump(mode="json")
    # Should not raise:
    encoded = json.dumps(payload)
    assert "completed" in encoded
    assert payload["status"]["state"] == "completed"


def test_jsonrpc_request_defaults():
    req = JSONRPCRequest(method="message/send", params={"foo": "bar"})
    assert req.jsonrpc == "2.0"
    assert req.id  # auto uuid
    assert req.method == "message/send"


def test_agent_card_round_trips():
    card = AgentCard(
        id="x-1",
        name="X",
        description="desc",
        connection={"url": "http://localhost:9999"},
        capabilities=["a", "b"],
    )
    data = card.model_dump(mode="json")
    assert data["version"] == "1.0.0"
    assert data["capabilities"] == ["a", "b"]
    assert data["supportedContentTypes"] == ["text/plain"]


def test_error_codes_follow_jsonrpc_spec():
    assert ErrorCodes.METHOD_NOT_FOUND == -32601
    assert ErrorCodes.INVALID_PARAMS == -32602
    assert ErrorCodes.AGENT_UNAVAILABLE == -32001
