"""Extended tests for the MultiAgentOrchestrator coordination logic.

Uses an in-process client that routes to real agent objects (no sockets), plus
fault-injecting clients to exercise the error-handling branches.
"""

import asyncio

import allure
import pytest

from agents.data_analyst_agent import DataAnalystAgent
from agents.math_agent import MathAgent
from common.a2a_protocol import MessageSendParams
from examples.orchestrator import MultiAgentOrchestrator


class InProcessClient:
    """A2AClient stand-in that dispatches by URL to local agent instances."""

    def __init__(self, math_url: str, data_url: str):
        self._agents = {math_url: MathAgent(), data_url: DataAnalystAgent()}

    async def send_message(self, agent_url, message, session_id=None):
        agent = self._agents[agent_url]
        return await agent.process_message(MessageSendParams(message=message))


class BoomClient:
    """Client whose send_message always raises (transport failure)."""

    async def send_message(self, *args, **kwargs):
        raise ConnectionError("agent unreachable")


@pytest.fixture()
def orchestrator() -> MultiAgentOrchestrator:
    orch = MultiAgentOrchestrator()
    orch.client = InProcessClient(orch.math_agent_url, orch.data_agent_url)
    return orch


def run(coro):
    return asyncio.run(coro)


@allure.feature("Orchestrator")
@allure.story("Routing")
class TestRouting:
    @allure.title("A math + visualisation problem uses both agents")
    def test_math_and_visualisation(self, orchestrator):
        result = run(orchestrator.solve_problem("Calculate the mean of [12,15,18,20] and create a histogram"))
        assert result["agents_used"] == ["Math Agent", "Data Analyst Agent"]
        assert "MATHEMATICAL ANALYSIS" in result["final_result"]

    @allure.title("A math-only problem stops after the Math Agent")
    def test_math_only(self, orchestrator):
        result = run(orchestrator.solve_problem("Calculate 2 + 2"))
        assert result["agents_used"] == ["Math Agent"]
        assert "Data Analyst Agent" not in result["agents_used"]

    @allure.title("A data-only problem routes to the Data Analyst Agent")
    def test_data_only(self, orchestrator):
        result = run(orchestrator.solve_problem("Create a histogram for [1,2,2,3,3,4]"))
        assert "Data Analyst Agent" in result["agents_used"]
        assert "Histogram" in result["final_result"]

    @allure.title("An unrecognised problem yields a helpful message")
    def test_unrecognised(self, orchestrator):
        result = run(orchestrator.solve_problem("tell me a joke"))
        assert "not recognized" in result["final_result"].lower()

    @allure.title("Problem analysis flags the right capabilities")
    def test_analyze_problem(self, orchestrator):
        analysis = run(orchestrator._analyze_problem("Calculate the mean and plot a scatter"))
        assert analysis["needs_math"] is True
        assert analysis["needs_visualization"] is True
        assert analysis["needs_data_analysis"] is True


@allure.feature("Orchestrator")
@allure.story("Error handling")
class TestErrorHandling:
    @allure.title("Transport failures are caught and surfaced in the result")
    def test_transport_failure(self, orchestrator):
        orchestrator.client = BoomClient()
        result = run(orchestrator.solve_problem("Calculate the mean of [1,2,3]"))
        # The orchestrator swallows the per-agent error and reports it as text.
        assert "Failed to get math analysis" in result["final_result"]

    @allure.title("A failing data agent is reported in a data-only flow")
    def test_data_agent_failure(self, orchestrator):
        orchestrator.client = BoomClient()
        result = run(orchestrator.solve_problem("Create a histogram for [1,2,3]"))
        assert "Failed to get data analysis" in result["final_result"]


@allure.feature("Orchestrator")
@allure.story("Result composition")
class TestComposition:
    @allure.title("Visualisation request embeds the original problem and math result")
    def test_visualization_request(self, orchestrator):
        req = orchestrator._create_visualization_request("orig problem", "math result here")
        assert "orig problem" in req
        assert "math result here" in req

    @allure.title("Combined result includes both agents' sections")
    def test_combine_results(self, orchestrator):
        combined = orchestrator._combine_results("MATH", "VIZ")
        assert "MATHEMATICAL ANALYSIS" in combined
        assert "DATA VISUALIZATION" in combined
        assert "MATH" in combined and "VIZ" in combined
