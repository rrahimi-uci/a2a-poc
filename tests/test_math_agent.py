"""Tests for the Math Agent's computation logic."""

import asyncio

import pytest

from agents.math_agent import MathAgent


@pytest.fixture()
def agent() -> MathAgent:
    return MathAgent()


def run(coro):
    return asyncio.run(coro)


def test_statistics(agent):
    out = run(agent._perform_calculation("calculate mean of [1, 2, 3, 4, 5]"))
    assert "Mean: 3.0000" in out
    assert "Standard Deviation:" in out
    assert "\\n" not in out  # newlines must be real, not the literal escape


def test_arithmetic(agent):
    out = run(agent._perform_calculation("compute 2 + 3 * 4"))
    assert "= 14.0" in out


def test_arithmetic_with_functions(agent):
    out = run(agent._perform_calculation("calculate sqrt(16)"))
    assert "4.0" in out


def test_safe_eval_rejects_arbitrary_code(agent):
    # __import__ / attribute access must not be evaluable.
    with pytest.raises(ValueError):
        agent._safe_eval("__import__('os').system('echo hi')")


def test_safe_eval_basic_math(agent):
    assert agent._safe_eval("2 ** 10") == 1024.0
    assert agent._safe_eval("10 % 3") == 1.0


def test_extract_numbers_from_list(agent):
    assert agent._extract_numbers("data is [1, 2, 3.5]") == [1.0, 2.0, 3.5]


def test_normal_distribution_summary(agent):
    # Note: phrasing avoids the words "mean"/"std", which route to the
    # statistics branch (checked before the probability branch).
    out = run(agent._perform_calculation("gaussian distribution 100 15"))
    assert "Normal Distribution Analysis" in out
    assert "μ = 100" in out


def test_empty_statistics_message(agent):
    out = run(agent._perform_calculation("calculate the mean"))
    assert "No numeric data" in out
