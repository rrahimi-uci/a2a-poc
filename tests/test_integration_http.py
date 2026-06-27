"""End-to-end integration test over a real HTTP socket.

This is the only test that exercises ``A2AClient`` against a live ``uvicorn``
server, so it guards the JSON-RPC response parsing (a successful response still
carries an ``error: null`` key — the client must not treat that as an error).
"""

import asyncio
import socket
import threading
import time

import pytest
import requests
import uvicorn

from agents.math_agent import MathAgent
from common.a2a_protocol import Message, MessagePart, MessageRole
from common.base_agent import A2AClient


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def live_math_url():
    port = _free_port()
    agent = MathAgent(port=port)
    server = uvicorn.Server(uvicorn.Config(agent.app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait until the server is accepting requests.
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            if requests.get(f"{url}/health", timeout=1).status_code == 200:
                break
        except requests.RequestException:
            time.sleep(0.1)
    else:
        pytest.fail("Live agent server did not start in time")

    yield url
    server.should_exit = True


def test_agent_card_over_http(live_math_url):
    card = requests.get(live_math_url, timeout=5).json()
    assert card["id"] == "math-agent-001"


def test_successful_response_has_null_error(live_math_url):
    """Regression guard for the response shape the client depends on."""
    payload = {
        "id": "1",
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {"message": {"role": "user", "parts": [{"kind": "text", "text": "calculate mean of [2,4]"}]}},
    }
    body = requests.post(live_math_url, json=payload, timeout=5).json()
    assert body["error"] is None
    assert body["result"]["status"]["state"] == "completed"


def test_a2a_client_round_trip(live_math_url):
    """A2AClient must parse a successful response as success, not an error."""
    client = A2AClient()
    msg = Message(role=MessageRole.USER, parts=[MessagePart(text="calculate mean of [10, 20, 30]")])
    task = asyncio.run(client.send_message(live_math_url, msg))
    assert task.status.state.value == "completed"
    assert "Mean: 20.0000" in task.status.message.parts[0].text
