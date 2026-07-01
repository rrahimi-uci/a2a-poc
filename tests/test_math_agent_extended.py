"""Extended behavioural tests for the Math Agent.

These cover the calculation branches, the (previously broken) linear-algebra
path, probability, expression extraction and the public ``process_message``
contract. Tests are annotated with Allure metadata so they group cleanly in an
Allure report (``pytest --alluredir=allure-results``).
"""

import asyncio

import allure
import pytest

from agents.math_agent import MathAgent
from common.a2a_protocol import (
    Message,
    MessagePart,
    MessageRole,
    MessageSendParams,
    TaskState,
)


@pytest.fixture()
def agent() -> MathAgent:
    return MathAgent()


def run(coro):
    return asyncio.run(coro)


@allure.feature("Math Agent")
@allure.story("Linear algebra")
class TestLinearAlgebra:
    @allure.title("Matrix multiplication produces the correct product")
    def test_matrix_multiplication(self, agent):
        # Regression: rows must be grouped into one matrix, not treated as
        # separate single-row matrices.
        out = run(agent._perform_calculation("multiply matrix [[1,2],[3,4]] and [[5,6],[7,8]]"))
        assert "Matrix multiplication result" in out
        assert "[19.0, 22.0]" in out
        assert "[43.0, 50.0]" in out

    @allure.title("Incompatible matrix dimensions are reported")
    def test_incompatible_dimensions(self, agent):
        out = run(agent._perform_calculation("multiply matrix [[1,2,3]] and [[4,5]]"))
        assert "incompatible" in out.lower()

    @allure.title("Determinant of a square matrix")
    def test_determinant(self, agent):
        out = run(agent._perform_calculation("determinant of matrix [[1,2],[3,4]]"))
        assert "Determinant" in out
        assert "-2.0000" in out

    @allure.title("Determinant requires a square matrix")
    def test_determinant_non_square(self, agent):
        out = run(agent._perform_calculation("determinant of matrix [[1,2,3],[4,5,6]]"))
        assert "square matrix" in out.lower()

    @allure.title("Determinant with no matrix asks for input")
    def test_determinant_missing_matrix(self, agent):
        out = run(agent._handle_linear_algebra("determinant please"))
        assert "square matrix" in out.lower()

    @allure.title("Single matrix is not enough for multiplication")
    def test_single_matrix_multiplication(self, agent):
        out = run(agent._handle_linear_algebra("matrix [[1,2],[3,4]]"))
        assert "two matrices" in out.lower()

    @allure.title("Unrecognised linear-algebra request")
    def test_unrecognised_linear_algebra(self, agent):
        out = run(agent._handle_linear_algebra("vector magic"))
        assert "not recognized" in out.lower()


@allure.feature("Math Agent")
@allure.story("Statistics")
class TestStatistics:
    @allure.title("Statistics over a list of numbers")
    def test_statistics(self, agent):
        out = run(agent._perform_calculation("statistics for [2, 4, 6, 8]"))
        assert "Mean: 5.0000" in out
        assert "Range: 6.0000" in out

    @allure.title("Statistics with negative numbers")
    def test_statistics_negative(self, agent):
        out = run(agent._perform_calculation("variance of [-2, -1, 0, 1, 2]"))
        assert "Mean: 0.0000" in out

    @allure.title("Statistics with no data returns guidance")
    def test_statistics_no_data(self, agent):
        out = run(agent._handle_statistics("compute the average"))
        assert "No numeric data" in out


@allure.feature("Math Agent")
@allure.story("Arithmetic")
class TestArithmetic:
    @allure.title("Order of operations is respected")
    def test_precedence(self, agent):
        assert "= 14.0" in run(agent._perform_calculation("compute 2 + 3 * 4"))

    @allure.title("Power operator ^ is translated to **")
    def test_power_operator(self, agent):
        assert agent._safe_eval("2 ^ 8") == 256.0

    @allure.title("Supported operators and functions evaluate")
    @pytest.mark.parametrize(
        "expr, expected",
        [
            ("10 // 3", 3.0),
            ("10 % 3", 1.0),
            ("-5 + 2", -3.0),
            ("+7", 7.0),
            ("abs(-9)", 9.0),
            ("round(3.14159)", 3.0),
            ("pow(2, 5)", 32.0),
            ("sqrt(81)", 9.0),
        ],
    )
    def test_safe_eval_operators(self, agent, expr, expected):
        assert agent._safe_eval(expr) == expected

    @allure.title("Constants pi and e resolve")
    def test_constants(self, agent):
        assert abs(agent._safe_eval("pi") - 3.14159) < 1e-3
        assert abs(agent._safe_eval("e") - 2.71828) < 1e-3

    @allure.title("Arithmetic with no expression returns guidance")
    def test_arithmetic_no_expression(self, agent):
        out = run(agent._handle_arithmetic("calculate"))
        assert "No mathematical expressions" in out

    @allure.title("Invalid expression is reported per-expression, not raised")
    def test_arithmetic_division_by_zero(self, agent):
        out = run(agent._perform_calculation("compute 5 / 0"))
        assert "Error" in out


@allure.feature("Math Agent")
@allure.story("Safe evaluation")
class TestSafeEval:
    @allure.title("Arbitrary code execution is rejected")
    def test_rejects_dunder_import(self, agent):
        with pytest.raises(ValueError):
            agent._safe_eval("__import__('os').system('echo hi')")

    @allure.title("Attribute access is rejected")
    def test_rejects_attribute_access(self, agent):
        with pytest.raises(ValueError):
            agent._safe_eval("(1).__class__")

    @allure.title("Unknown function name is rejected")
    def test_rejects_unknown_function(self, agent):
        with pytest.raises(ValueError):
            agent._safe_eval("destroy(1)")

    @allure.title("Unknown free name is rejected")
    def test_rejects_unknown_name(self, agent):
        with pytest.raises(ValueError):
            agent._safe_eval("foo")


@allure.feature("Math Agent")
@allure.story("Probability")
class TestProbability:
    @allure.title("Normal distribution summary with parameters")
    def test_normal_distribution(self, agent):
        out = run(agent._perform_calculation("gaussian distribution 100 15"))
        assert "Normal Distribution Analysis" in out
        assert "μ = 100" in out

    @allure.title("Normal distribution without parameters prompts for them")
    def test_normal_missing_params(self, agent):
        out = run(agent._handle_probability("normal distribution"))
        assert "provide mean and standard deviation" in out.lower()

    @allure.title("Non-normal probability request returns guidance")
    def test_probability_other(self, agent):
        out = run(agent._handle_probability("probability of something"))
        assert "not recognized" in out.lower()


@allure.feature("Math Agent")
@allure.story("Expression extraction")
class TestExpressionExtraction:
    @allure.title("Default branch evaluates a bare expression")
    def test_extract_and_evaluate(self, agent):
        out = run(agent._extract_and_evaluate("(2 + 3) * 4"))
        assert "20.0" in out

    @allure.title("Default branch with no expression returns the help text")
    def test_extract_and_evaluate_help(self, agent):
        out = run(agent._extract_and_evaluate("hello"))
        assert "I can help with various mathematical operations" in out

    @allure.title("Numbers without brackets are extracted individually")
    def test_extract_numbers_individual(self, agent):
        assert agent._extract_numbers("the values 3 and 7 and 9") == [3.0, 7.0, 9.0]


@allure.feature("Math Agent")
@allure.story("Message contract")
class TestProcessMessage:
    @allure.title("process_message returns a COMPLETED task and stores it")
    def test_process_message_completed(self, agent):
        params = MessageSendParams(
            message=Message(role=MessageRole.USER, parts=[MessagePart(text="calculate mean of [1,2,3]")])
        )
        task = run(agent.process_message(params))
        assert task.status.state == TaskState.COMPLETED
        assert task.id in agent.tasks
        assert "Mean: 2.0000" in task.status.message.parts[0].text

    @allure.title("Errors during processing produce an ERROR task")
    def test_process_message_error(self, agent, monkeypatch):
        async def boom(_text):
            raise RuntimeError("kaboom")

        monkeypatch.setattr(agent, "_perform_calculation", boom)
        params = MessageSendParams(
            message=Message(role=MessageRole.USER, parts=[MessagePart(text="x")])
        )
        task = run(agent.process_message(params))
        assert task.status.state == TaskState.ERROR
        assert "kaboom" in task.status.error
