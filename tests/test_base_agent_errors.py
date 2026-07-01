"""Tests for BaseAgent's JSON-RPC error wrapping (in-process via TestClient)."""

import allure
from fastapi.testclient import TestClient

from common.a2a_protocol import (
    Message,
    MessagePart,
    MessageRole,
    MessageSendParams,
    Task,
    TaskState,
    TaskStatus,
)
from common.base_agent import BaseAgent
from common.a2a_protocol import ErrorCodes


class _FaultyAgent(BaseAgent):
    """Agent whose processing always fails, to exercise the error path."""

    def __init__(self):
        super().__init__("faulty-001", "Faulty", "always fails", port=8999, capabilities=["fail"])

    async def process_message(self, params: MessageSendParams) -> Task:
        raise RuntimeError("processing failed")


class _OkAgent(BaseAgent):
    def __init__(self):
        super().__init__("ok-001", "Ok", "always ok", port=8998, capabilities=["ok"])

    async def process_message(self, params: MessageSendParams) -> Task:
        reply = Message(role=MessageRole.AGENT, parts=[MessagePart(text="ok")])
        task = Task(messages=[params.message, reply], status=TaskStatus(state=TaskState.COMPLETED, message=reply))
        self.tasks[task.id] = task
        return task


def _send(text="hello"):
    return {
        "id": "1",
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {"message": {"role": "user", "parts": [{"kind": "text", "text": text}]}},
    }


@allure.feature("BaseAgent")
@allure.story("JSON-RPC error wrapping")
@allure.title("A failing process_message becomes a TASK_FAILED error response")
def test_message_send_failure_returns_task_failed():
    client = TestClient(_FaultyAgent().app)
    body = client.post("/", json=_send()).json()
    assert body["error"]["code"] == ErrorCodes.TASK_FAILED
    assert "processing failed" in body["error"]["message"]


@allure.feature("BaseAgent")
@allure.story("JSON-RPC success")
@allure.title("task/get returns a stored task after message/send")
def test_task_get_round_trip():
    client = TestClient(_OkAgent().app)
    task_id = client.post("/", json=_send()).json()["result"]["id"]
    got = client.post(
        "/", json={"id": "g", "jsonrpc": "2.0", "method": "task/get", "params": {"taskId": task_id}}
    )
    assert got.json()["result"]["id"] == task_id


@allure.feature("BaseAgent")
@allure.story("JSON-RPC error wrapping")
@allure.title("task/get without a taskId returns INVALID_PARAMS")
def test_task_get_missing_id():
    client = TestClient(_OkAgent().app)
    body = client.post("/", json={"id": "g", "jsonrpc": "2.0", "method": "task/get", "params": {}}).json()
    assert body["error"]["code"] == ErrorCodes.INVALID_PARAMS
