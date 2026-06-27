"""Tests for the multi-agent orchestrator.

The orchestrator normally talks to agents over HTTP via ``A2AClient``. Here we
swap in an in-process client that routes messages straight to the real agent
objects, so we exercise the full routing/coordination logic without sockets.
"""

import asyncio

import pytest

from agents.data_analyst_agent import DataAnalystAgent
from agents.math_agent import MathAgent
from common.a2a_protocol import MessageSendParams
from examples.orchestrator import MultiAgentOrchestrator


class InProcessClient:
    """A2AClient stand-in that dispatches by URL to local agent instances."""

    def __init__(self, math_url: str, data_url: str):
        self._agents = {
            math_url: MathAgent(),
            data_url: DataAnalystAgent(),
        }

    async def send_message(self, agent_url, message, session_id=None):
        agent = self._agents[agent_url]
        return await agent.process_message(MessageSendParams(message=message))


@pytest.fixture()
def orchestrator() -> MultiAgentOrchestrator:
    orch = MultiAgentOrchestrator()
    orch.client = InProcessClient(orch.math_agent_url, orch.data_agent_url)
    return orch


def run(coro):
    return asyncio.run(coro)


def test_problem_analysis_routing(orchestrator):
    analysis = run(orchestrator._analyze_problem("Calculate the mean and plot a histogram"))
    assert analysis["needs_math"] is True
    assert analysis["needs_visualization"] is True


def test_math_plus_visualization_uses_both_agents(orchestrator):
    result = run(
        orchestrator.solve_problem(
            "Calculate the mean of [12, 15, 18, 20] and create a histogram"
        )
    )
    assert "Math Agent" in result["agents_used"]
    assert "Data Analyst Agent" in result["agents_used"]
    assert result["final_result"]
    assert "MATHEMATICAL ANALYSIS" in result["final_result"]


def test_data_only_problem(orchestrator):
    # "histogram" is a data/visualization keyword with no math-keyword overlap,
    # so the orchestrator routes straight to the Data Analyst Agent.
    result = run(orchestrator.solve_problem("Create a histogram for [1, 2, 2, 3, 3, 4]"))
    assert "Data Analyst Agent" in result["agents_used"]
    assert "Histogram" in result["final_result"]


def test_unrecognized_problem(orchestrator):
    result = run(orchestrator.solve_problem("tell me a joke"))
    assert "not recognized" in result["final_result"].lower()
