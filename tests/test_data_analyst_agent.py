"""Tests for the Data Analyst Agent's analysis logic."""

import asyncio

import pytest

from agents.data_analyst_agent import DataAnalystAgent


@pytest.fixture()
def agent() -> DataAnalystAgent:
    return DataAnalystAgent()


def run(coro):
    return asyncio.run(coro)


def test_correlation_analysis(agent):
    out = run(agent._perform_analysis("analyze correlation in [(1,5), (2,7), (3,6), (4,8)]"))
    assert "Correlation Analysis" in out
    assert "Correlation coefficient:" in out
    assert "\\n" not in out


def test_single_variable_report(agent):
    out = run(agent._perform_analysis("generate report for data [10, 15, 12, 18, 20, 16, 14]"))
    assert "Data Analysis Report" in out
    assert "Skewness" in out
    assert "Quartile" in out


def test_histogram_visualization(agent):
    out = run(agent._perform_analysis("create histogram for [1,2,2,3,3,3,4]"))
    assert "Histogram" in out
    assert "7 data points" in out


def test_scatter_requires_pairs(agent):
    out = run(agent._perform_analysis("scatter plot for [(1,2),(2,4),(3,6)]"))
    assert "Scatter" in out
    assert "Correlation" in out


def test_interpret_correlation(agent):
    assert agent._interpret_correlation(0.95) == "very strong positive correlation"
    assert agent._interpret_correlation(-0.8) == "strong negative correlation"
    assert agent._interpret_correlation(0.1) == "very weak positive correlation"


def test_extract_paired_data(agent):
    data = agent._extract_data("points [(1,2), (3,4)]")
    assert data == [(1.0, 2.0), (3.0, 4.0)]


def test_guidance_when_no_keywords(agent):
    out = run(agent._perform_analysis("hello there"))
    assert "Data Analyst Agent" in out
