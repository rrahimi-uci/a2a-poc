"""Shared pytest fixtures.

Tests run fully in-process using FastAPI's ``TestClient`` (Starlette + httpx),
so no agents need to be launched on real ports. This keeps the suite fast and
deterministic and lets it run unchanged in CI.
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_analyst_agent import DataAnalystAgent  # noqa: E402
from agents.math_agent import MathAgent  # noqa: E402


@pytest.fixture(scope="session")
def math_agent() -> MathAgent:
    return MathAgent(port=8001)


@pytest.fixture(scope="session")
def data_agent() -> DataAnalystAgent:
    return DataAnalystAgent(port=8002)


@pytest.fixture()
def math_client(math_agent) -> TestClient:
    return TestClient(math_agent.app)


@pytest.fixture()
def data_client(data_agent) -> TestClient:
    return TestClient(data_agent.app)


def _jsonrpc_message(text: str, request_id: str = "test-1") -> dict:
    """Build a JSON-RPC ``message/send`` payload for the given text."""
    return {
        "id": request_id,
        "jsonrpc": "2.0",
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": text}],
            }
        },
    }


@pytest.fixture()
def jsonrpc_message():
    """Factory fixture that builds JSON-RPC ``message/send`` payloads."""
    return _jsonrpc_message
