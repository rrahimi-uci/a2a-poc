"""Tests for the simplified A2A client and the mock-AutoGen hybrid demo.

Network-dependent paths run against a real in-thread uvicorn server; the
JSON-RPC error/odd-shape branches run against a tiny purpose-built server.
"""

import asyncio
import socket
import threading
import time

import allure
import pytest
import requests
import uvicorn
from fastapi import FastAPI

from agents.math_agent import MathAgent
from common.a2a_protocol import Message, MessagePart, MessageRole
from common.base_agent import A2AClient
from examples.simple_a2a_client import SimpleA2AClient
from examples.simple_hybrid_demo import MockAutoGenAgent, SimpleHybridOrchestrator


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def _serve(app, port):
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    deadline = time.time() + 15
    while time.time() < deadline:
        try:
            requests.get(f"http://127.0.0.1:{port}/", timeout=1)
            return server
        except requests.RequestException:
            time.sleep(0.1)
    raise RuntimeError("server did not start")


@pytest.fixture(scope="module")
def math_url():
    port = _free_port()
    server = _serve(MathAgent(port=port).app, port)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True


@pytest.fixture(scope="module")
def quirky_url():
    """A server whose POST / returns a JSON-RPC error, and a second path that
    returns a result with no 'status' key (the 'Unknown response format' case)."""
    app = FastAPI()

    @app.get("/")
    async def root():
        return {"ok": True}

    @app.post("/error")
    async def error():
        return {"jsonrpc": "2.0", "id": "1", "result": None, "error": {"code": -32002, "message": "boom"}}

    @app.post("/weird")
    async def weird():
        return {"jsonrpc": "2.0", "id": "1", "result": {"no_status": True}, "error": None}

    port = _free_port()
    server = _serve(app, port)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True


@allure.feature("SimpleA2AClient")
@allure.story("Happy path")
@allure.title("Successful message round-trip returns the agent's text")
def test_simple_client_success(math_url):
    out = asyncio.run(SimpleA2AClient().send_message(math_url, "calculate mean of [2,4,6]"))
    assert "Mean: 4.0000" in out


@allure.feature("SimpleA2AClient")
@allure.story("Error handling")
class TestSimpleClientErrors:
    @allure.title("Non-200 responses are reported")
    def test_http_error(self, math_url):
        # POST /health is not allowed -> 405.
        out = asyncio.run(SimpleA2AClient().send_message(f"{math_url}/health", "hi"))
        assert out.startswith("Error: HTTP")

    @allure.title("Connection failures are reported")
    def test_connection_error(self):
        out = asyncio.run(SimpleA2AClient().send_message("http://127.0.0.1:1/", "hi"))
        assert "Communication error" in out

    @allure.title("JSON-RPC error payloads are surfaced")
    def test_agent_error(self, quirky_url):
        out = asyncio.run(SimpleA2AClient().send_message(f"{quirky_url}/error", "hi"))
        assert "Agent error" in out

    @allure.title("Unexpected response shapes are handled gracefully")
    def test_unknown_shape(self, quirky_url):
        out = asyncio.run(SimpleA2AClient().send_message(f"{quirky_url}/weird", "hi"))
        assert out == "Unknown response format"


@allure.feature("A2AClient")
@allure.story("JSON-RPC error branch")
@allure.title("A2AClient raises when the response carries a JSON-RPC error")
def test_a2a_client_raises_on_jsonrpc_error(quirky_url):
    client = A2AClient()
    msg = Message(role=MessageRole.USER, parts=[MessagePart(text="hi")])
    with pytest.raises(Exception, match="boom"):
        asyncio.run(client.send_message(f"{quirky_url}/error", msg))


@allure.feature("BaseAgent")
@allure.story("JSON-RPC error branch")
@allure.title("BaseAgent.send_message_to_agent raises on a JSON-RPC error")
def test_base_agent_raises_on_jsonrpc_error(quirky_url):
    caller = MathAgent(port=9997)
    msg = Message(role=MessageRole.USER, parts=[MessagePart(text="hi")])
    with pytest.raises(Exception, match="boom"):
        asyncio.run(caller.send_message_to_agent(f"{quirky_url}/error", msg))


@allure.feature("Hybrid demo")
@allure.story("Mock AutoGen agent")
class TestMockAutoGen:
    @allure.title("Code generation dispatches by request keyword")
    @pytest.mark.parametrize(
        "request_text, marker",
        [
            ("analyze the normal distribution", "Normal Distribution"),
            ("compute the correlation", "Correlation Analysis"),
            ("calculate statistics / mean", "Statistical Analysis"),
            ("do something else entirely", "Generic Data Analysis"),
        ],
    )
    def test_generate_code_branches(self, monkeypatch, request_text, marker):
        async def _no_sleep(_seconds):
            return None

        monkeypatch.setattr(asyncio, "sleep", _no_sleep)
        code = asyncio.run(MockAutoGenAgent().generate_code(request_text))
        assert marker in code


@allure.feature("Hybrid demo")
@allure.story("Hybrid orchestrator")
class TestHybridOrchestrator:
    @allure.title("Collaboration combines A2A math output with generated code")
    def test_solve_with_collaboration(self, monkeypatch):
        orch = SimpleHybridOrchestrator()

        class FakeClient:
            async def send_message(self, url, text):
                return "Mean: 42"

        async def _no_sleep(_seconds):
            return None

        monkeypatch.setattr(asyncio, "sleep", _no_sleep)
        orch.a2a_client = FakeClient()
        result = asyncio.run(orch.solve_with_collaboration("compute statistics for [1,2,3]"))

        assert result["agents"] == ["A2A Math Agent", "Mock AutoGen Agent"]
        assert "Mean: 42" in result["final_solution"]
        assert result["generated_code"]

    @allure.title("A2A math failures are reported, not raised")
    def test_math_failure_is_caught(self):
        orch = SimpleHybridOrchestrator()

        class BoomClient:
            async def send_message(self, url, text):
                raise ConnectionError("down")

        orch.a2a_client = BoomClient()
        out = asyncio.run(orch._get_math_analysis("anything"))
        assert "Failed to connect" in out

    @allure.title("Combined solution embeds both agents' contributions")
    def test_combined_solution(self):
        orch = SimpleHybridOrchestrator()
        combined = orch._create_combined_solution("P", "MATHRESULT", "CODERESULT")
        assert "MATHRESULT" in combined
        assert "CODERESULT" in combined
