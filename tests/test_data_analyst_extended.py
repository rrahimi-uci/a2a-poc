"""Extended behavioural tests for the Data Analyst Agent.

Covers every analysis branch (visualisation, analysis, reporting, processing,
guidance), data extraction edge cases, statistic formatting and the public
``process_message`` contract. Annotated with Allure metadata.
"""

import asyncio

import allure
import numpy as np
import pandas as pd
import pytest

from agents.data_analyst_agent import DataAnalystAgent
from common.a2a_protocol import (
    Message,
    MessagePart,
    MessageRole,
    MessageSendParams,
    TaskState,
)


@pytest.fixture()
def agent() -> DataAnalystAgent:
    return DataAnalystAgent()


def run(coro):
    return asyncio.run(coro)


@allure.feature("Data Analyst Agent")
@allure.story("Visualisation")
class TestVisualisation:
    @allure.title("Histogram for a single-variable list")
    def test_histogram(self, agent):
        out = run(agent._perform_analysis("create histogram for [1,2,2,3,3,3,4]"))
        assert "Histogram" in out
        assert "7 data points" in out

    @allure.title("Histogram uses Y values for paired data")
    def test_histogram_paired(self, agent):
        out = run(agent._perform_analysis("histogram for [(1,10),(2,20),(3,30)]"))
        assert "Histogram" in out

    @allure.title("Scatter plot with a trend line and correlation")
    def test_scatter(self, agent):
        out = run(agent._perform_analysis("scatter plot for [(1,2),(2,4),(3,6)]"))
        assert "Scatter" in out
        assert "Correlation" in out
        assert "Trend line" in out

    @allure.title("Scatter requires paired data")
    def test_scatter_requires_pairs(self, agent):
        out = run(agent._perform_analysis("scatter plot for [1,2,3,4,5]"))
        assert "requires paired data" in out

    @allure.title("Line plot for a single-variable list")
    def test_line_single(self, agent):
        out = run(agent._perform_analysis("line plot for [1,2,3,4]"))
        assert "Line" in out

    @allure.title("Line plot for paired data")
    def test_line_paired(self, agent):
        out = run(agent._perform_analysis("line plot for [(1,2),(2,3),(3,5)]"))
        assert "Line" in out

    @allure.title("Box plot reports quartiles")
    def test_box(self, agent):
        out = run(agent._perform_analysis("box plot for [1,2,3,4,5,100]"))
        assert "Box" in out
        assert "IQR" in out

    @allure.title("Box plot uses Y values for paired data")
    def test_box_paired(self, agent):
        out = run(agent._perform_analysis("box plot for [(1,2),(2,8),(3,4)]"))
        assert "Box" in out

    @allure.title("Bar chart falls back to a basic description")
    def test_bar(self, agent):
        out = run(agent._perform_analysis("bar category chart for [1,2,3]"))
        assert "Visualization Created" in out

    @allure.title("Visualisation with no data returns format guidance")
    def test_visualisation_no_data(self, agent):
        out = run(agent._handle_visualization("please plot something"))
        assert "No data found for visualization" in out


@allure.feature("Data Analyst Agent")
@allure.story("Analysis")
class TestAnalysis:
    @allure.title("Correlation analysis on paired data")
    def test_correlation(self, agent):
        out = run(agent._perform_analysis("analyze correlation in [(1,5),(2,7),(3,6),(4,8)]"))
        assert "Correlation Analysis" in out
        assert "Correlation coefficient:" in out

    @allure.title("Correlation analysis works with negative coordinates")
    def test_correlation_negative(self, agent):
        out = run(agent._perform_analysis("analyze correlation in [(-1,-5),(2,7),(3,6)]"))
        assert "Correlation Analysis" in out

    @allure.title("Single-variable analysis reports skew interpretation")
    def test_single_variable(self, agent):
        out = run(agent._perform_analysis("analyze pattern in [10,15,12,18,20,16,14]"))
        assert "Skewness" in out
        assert "Quartiles" in out

    @allure.title("Small samples show N/A for skew/kurtosis instead of nan")
    def test_small_sample_na(self, agent):
        out = run(agent._perform_analysis("analyze trend in [1,2]"))
        assert "N/A" in out
        assert "nan" not in out.lower()

    @allure.title("Analysis with no data returns guidance")
    def test_analysis_no_data(self, agent):
        out = run(agent._handle_data_analysis("analyze the trend"))
        assert "No data found for analysis" in out


@allure.feature("Data Analyst Agent")
@allure.story("Reporting")
class TestReporting:
    @allure.title("Single-variable report")
    def test_single_report(self, agent):
        out = run(agent._perform_analysis("generate report for [10,15,12,18,20,16,14]"))
        assert "Data Analysis Report" in out
        assert "IQR" in out

    @allure.title("Paired-data report includes correlation and insights")
    def test_paired_report(self, agent):
        out = run(agent._perform_analysis("summary report for [(1,2),(2,4),(3,6),(4,8)]"))
        assert "Data Analysis Report" in out
        assert "Relationship Analysis" in out
        assert "Key Insights" in out

    @allure.title("Report with no data returns guidance")
    def test_report_no_data(self, agent):
        out = run(agent._handle_reporting("generate a report"))
        assert "I can generate reports" in out


@allure.feature("Data Analyst Agent")
@allure.story("Processing and guidance")
class TestProcessingGuidance:
    @allure.title("Data processing returns the services menu")
    def test_processing(self, agent):
        out = run(agent._perform_analysis("clean and transform my dataset"))
        assert "Data Processing Services" in out

    @allure.title("Unknown request returns the capabilities guide")
    def test_guidance(self, agent):
        out = run(agent._perform_analysis("hello there"))
        assert "Data Analyst Agent" in out


@allure.feature("Data Analyst Agent")
@allure.story("Data extraction")
class TestExtraction:
    @allure.title("Paired data is extracted as tuples")
    def test_pairs(self, agent):
        assert agent._extract_data("points [(1,2),(3,4)]") == [(1.0, 2.0), (3.0, 4.0)]

    @allure.title("Negative paired data is extracted as tuples")
    def test_negative_pairs(self, agent):
        assert agent._extract_data("[(-1,-2),(3,-4)]") == [(-1.0, -2.0), (3.0, -4.0)]

    @allure.title("JSON object input yields the first numeric list")
    def test_json_object(self, agent):
        assert agent._extract_data('data {"x": [1,2,3], "y": [4,5,6]}') == [1, 2, 3]

    @allure.title("Three or more bare numbers are extracted as a fallback")
    def test_bare_numbers(self, agent):
        assert agent._extract_data("values 4 8 15 16 23 42") == [4.0, 8.0, 15.0, 16.0, 23.0, 42.0]

    @allure.title("Too little data returns an empty list")
    def test_insufficient_data(self, agent):
        assert agent._extract_data("just 5") == []


@allure.feature("Data Analyst Agent")
@allure.story("Interpretation helpers")
class TestHelpers:
    @allure.title("Correlation strength/direction mapping")
    @pytest.mark.parametrize(
        "corr, expected",
        [
            (0.95, "very strong positive correlation"),
            (0.8, "strong positive correlation"),
            (0.6, "moderate positive correlation"),
            (0.4, "weak positive correlation"),
            (-0.1, "very weak negative correlation"),
        ],
    )
    def test_interpret_correlation(self, agent, corr, expected):
        assert agent._interpret_correlation(corr) == expected

    @allure.title("Skewness interpretation mapping")
    @pytest.mark.parametrize(
        "skew, fragment",
        [
            (0.1, "approximately symmetric"),
            (1.2, "right-skewed"),
            (-1.2, "left-skewed"),
            (float("nan"), "undefined"),
        ],
    )
    def test_interpret_skewness(self, agent, skew, fragment):
        assert fragment in agent._interpret_skewness(skew)

    @allure.title("Statistic formatting handles nan and None")
    def test_fmt_stat(self, agent):
        assert agent._fmt_stat(3.14159) == "3.1416"
        assert agent._fmt_stat(float("nan")) == "N/A"
        assert agent._fmt_stat(None) == "N/A"

    @allure.title("Chart type detection")
    @pytest.mark.parametrize(
        "text, expected",
        [
            ("show a histogram", "histogram"),
            ("scatter please", "scatter"),
            ("line trend", "line"),
            ("bar category", "bar"),
            ("box quartile", "box"),
            ("just draw it", "line"),
        ],
    )
    def test_determine_chart_type(self, agent, text, expected):
        assert agent._determine_chart_type(text) == expected

    @allure.title("Paired-data insights surface strong relationships")
    def test_generate_insights(self, agent):
        df = pd.DataFrame([(1, 10), (2, 30), (3, 50), (4, 70)], columns=["X", "Y"])
        insights = agent._generate_insights(df)
        assert "Strong relationship" in insights or "more variation" in insights

    @allure.title("Single-variable insights flag outliers and variability")
    def test_single_var_insights(self, agent):
        series = pd.Series([1, 1, 1, 1, 1, 1, 1, 100])
        out = agent._generate_single_var_insights(series)
        assert "outlier" in out.lower() or "variability" in out.lower()


@allure.feature("Data Analyst Agent")
@allure.story("Message contract")
class TestProcessMessage:
    @allure.title("process_message returns a COMPLETED task")
    def test_process_message_completed(self, agent):
        params = MessageSendParams(
            message=Message(role=MessageRole.USER, parts=[MessagePart(text="histogram for [1,2,3,4]")])
        )
        task = run(agent.process_message(params))
        assert task.status.state == TaskState.COMPLETED
        assert task.id in agent.tasks

    @allure.title("Errors during analysis produce an ERROR task")
    def test_process_message_error(self, agent, monkeypatch):
        async def boom(_text):
            raise RuntimeError("analysis exploded")

        monkeypatch.setattr(agent, "_perform_analysis", boom)
        params = MessageSendParams(
            message=Message(role=MessageRole.USER, parts=[MessagePart(text="x")])
        )
        task = run(agent.process_message(params))
        assert task.status.state == TaskState.ERROR
        assert "analysis exploded" in task.status.error
