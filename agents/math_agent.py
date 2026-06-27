"""
Math Agent - Specialized agent for mathematical computations and statistical analysis.
"""

import ast
import logging
import math
import operator
import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, List, Any, Optional
import json
import re

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.base_agent import BaseAgent
from common.a2a_protocol import (
    Message, Task, TaskStatus, TaskState, MessageRole, MessagePart, MessageSendParams
)

logger = logging.getLogger(__name__)


class MathAgent(BaseAgent):
    """Agent specialized in mathematical computations and statistical analysis."""
    
    def __init__(self, port: int = 8001):
        capabilities = [
            "arithmetic_operations",
            "statistical_analysis", 
            "data_calculations",
            "mathematical_functions",
            "linear_algebra",
            "probability_distributions"
        ]
        
        super().__init__(
            agent_id="math-agent-001",
            name="Math Agent",
            description="Specialized agent for mathematical computations, statistical analysis, and data calculations",
            port=port,
            capabilities=capabilities,
            supported_content_types=["text/plain", "application/json"]
        )
    
    async def process_message(self, params: MessageSendParams) -> Task:
        """Process incoming message and perform mathematical operations."""
        message = params.message
        
        # Create task
        task = Task(
            messages=[message],
            status=TaskStatus(state=TaskState.WORKING),
            contextId=params.contextId,
            sessionId=params.sessionId,
            metadata=params.metadata
        )
        
        # Store task
        self.tasks[task.id] = task
        
        try:
            # Extract text from message parts
            text_content = " ".join([part.text for part in message.parts if part.kind == "text"])
            
            # Determine operation type and perform calculation
            result = await self._perform_calculation(text_content)
            
            # Create response message
            response_message = Message(
                role=MessageRole.AGENT,
                parts=[MessagePart(text=result)],
                contextId=task.contextId,
                taskId=task.id
            )
            
            # Update task with result
            task.messages.append(response_message)
            task.status = TaskStatus(
                state=TaskState.COMPLETED,
                message=response_message
            )
            
        except Exception as e:
            logger.error(f"Error in math calculation: {e}")
            error_message = Message(
                role=MessageRole.AGENT,
                parts=[MessagePart(text=f"Error performing calculation: {str(e)}")],
                contextId=task.contextId,
                taskId=task.id
            )
            
            task.messages.append(error_message)
            task.status = TaskStatus(
                state=TaskState.ERROR,
                message=error_message,
                error=str(e)
            )
        
        # Update stored task
        self.tasks[task.id] = task
        return task
    
    async def _perform_calculation(self, text: str) -> str:
        """Perform mathematical calculations based on text input."""
        text = text.lower().strip()
        
        # Statistical analysis patterns
        if any(keyword in text for keyword in ["mean", "average", "statistics", "std", "variance"]):
            return await self._handle_statistics(text)
        
        # Basic arithmetic patterns
        if any(op in text for op in ["+", "-", "*", "/", "^", "**", "calculate", "compute"]):
            return await self._handle_arithmetic(text)
        
        # Linear algebra patterns
        if any(keyword in text for keyword in ["matrix", "vector", "dot product", "determinant"]):
            return await self._handle_linear_algebra(text)
        
        # Probability distributions
        if any(keyword in text for keyword in ["normal", "gaussian", "probability", "distribution"]):
            return await self._handle_probability(text)
        
        # Default: try to extract and evaluate mathematical expressions
        return await self._extract_and_evaluate(text)
    
    async def _handle_statistics(self, text: str) -> str:
        """Handle statistical analysis requests."""
        # Extract numbers from text
        numbers = self._extract_numbers(text)
        
        if not numbers:
            return "No numeric data found for statistical analysis. Please provide a list of numbers."
        
        data = np.array(numbers)
        
        result = {
            "count": len(data),
            "mean": float(np.mean(data)),
            "median": float(np.median(data)),
            "std_dev": float(np.std(data)),
            "variance": float(np.var(data)),
            "min": float(np.min(data)),
            "max": float(np.max(data)),
            "range": float(np.max(data) - np.min(data))
        }
        
        # Format response
        response = f"""Statistical Analysis Results:
- Count: {result['count']}
- Mean: {result['mean']:.4f}
- Median: {result['median']:.4f}
- Standard Deviation: {result['std_dev']:.4f}
- Variance: {result['variance']:.4f}
- Min: {result['min']:.4f}
- Max: {result['max']:.4f}
- Range: {result['range']:.4f}"""
        
        return response
    
    async def _handle_arithmetic(self, text: str) -> str:
        """Handle basic arithmetic operations."""
        # Extract mathematical expressions
        expressions = self._extract_expressions(text)
        
        if not expressions:
            return "No mathematical expressions found. Please provide calculations like '2 + 3' or 'sqrt(16)'."
        
        results = []
        for expr in expressions:
            try:
                # Safe evaluation of mathematical expressions
                result = self._safe_eval(expr)
                results.append(f"{expr} = {result}")
            except Exception as e:
                results.append(f"{expr} = Error: {str(e)}")
        
        return "Calculation Results:\\n" + "\\n".join(results)
    
    async def _handle_linear_algebra(self, text: str) -> str:
        """Handle linear algebra operations."""
        # For this example, we'll do a simple matrix operation
        if "matrix" in text:
            # Extract matrices from text (simplified example)
            matrices = self._extract_matrices(text)
            
            if len(matrices) >= 2:
                try:
                    A = np.array(matrices[0])
                    B = np.array(matrices[1])
                    
                    # Perform matrix multiplication if dimensions allow
                    if A.shape[1] == B.shape[0]:
                        result = np.dot(A, B)
                        return f"Matrix multiplication result:\\n{result.tolist()}"
                    else:
                        return f"Matrix dimensions incompatible for multiplication: {A.shape} and {B.shape}"
                        
                except Exception as e:
                    return f"Error in matrix operation: {str(e)}"
            
            return "Please provide two matrices for linear algebra operations."
        
        return "Linear algebra operation not recognized. Try 'multiply matrix [[1,2],[3,4]] and [[5,6],[7,8]]'."
    
    async def _handle_probability(self, text: str) -> str:
        """Handle probability and distribution calculations."""
        if "normal" in text or "gaussian" in text:
            # Extract mean and std dev
            numbers = self._extract_numbers(text)
            
            if len(numbers) >= 2:
                mean, std = numbers[0], numbers[1]
                
                # Generate some sample values
                samples = np.random.normal(mean, std, 1000)
                
                result = {
                    "distribution": "Normal",
                    "mean": mean,
                    "std_dev": std,
                    "sample_mean": float(np.mean(samples)),
                    "sample_std": float(np.std(samples)),
                    "95_percentile": float(np.percentile(samples, 95)),
                    "5_percentile": float(np.percentile(samples, 5))
                }
                
                return f"""Normal Distribution Analysis:
- Parameters: μ = {result['mean']}, σ = {result['std_dev']}
- Sample Mean: {result['sample_mean']:.4f}
- Sample Std Dev: {result['sample_std']:.4f}
- 95th Percentile: {result['95_percentile']:.4f}
- 5th Percentile: {result['5_percentile']:.4f}"""
            
            return "Please provide mean and standard deviation for normal distribution."
        
        return "Probability calculation not recognized. Try 'normal distribution with mean 0 and std 1'."
    
    async def _extract_and_evaluate(self, text: str) -> str:
        """Extract and evaluate mathematical expressions from text."""
        # Look for mathematical expressions
        expressions = self._extract_expressions(text)
        
        if expressions:
            results = []
            for expr in expressions:
                try:
                    result = self._safe_eval(expr)
                    results.append(f"{expr} = {result}")
                except Exception as e:
                    results.append(f"{expr} = Error: {str(e)}")
            
            return "Results:\\n" + "\\n".join(results)
        
        return """I can help with various mathematical operations:
- Basic arithmetic: '2 + 3 * 4', 'sqrt(16)', 'sin(pi/2)'
- Statistics: 'calculate mean of [1, 2, 3, 4, 5]'
- Linear algebra: 'multiply matrix [[1,2],[3,4]] and [[5,6],[7,8]]'
- Probability: 'normal distribution with mean 0 and std 1'

What calculation would you like me to perform?"""
    
    def _extract_numbers(self, text: str) -> List[float]:
        """Extract numbers from text."""
        # Look for arrays/lists first
        array_pattern = r'\\[([\\d.,\\s]+)\\]'
        array_match = re.search(array_pattern, text)
        
        if array_match:
            number_text = array_match.group(1)
            numbers = [float(x.strip()) for x in number_text.split(',') if x.strip()]
            return numbers
        
        # Look for individual numbers
        number_pattern = r'-?\\d+\\.?\\d*'
        matches = re.findall(number_pattern, text)
        return [float(match) for match in matches]
    
    def _extract_expressions(self, text: str) -> List[str]:
        """Extract mathematical expressions from text."""
        # Simple patterns for mathematical expressions
        patterns = [
            r'[\\d+\\-*/^()\\s.]+[=]?[\\d+\\-*/^()\\s.]*',
            r'sqrt\\([\\d+\\-*/^()\\s.]+\\)',
            r'sin\\([\\d+\\-*/^()\\s.]+\\)',
            r'cos\\([\\d+\\-*/^()\\s.]+\\)',
            r'tan\\([\\d+\\-*/^()\\s.]+\\)',
            r'log\\([\\d+\\-*/^()\\s.]+\\)',
            r'exp\\([\\d+\\-*/^()\\s.]+\\)'
        ]
        
        expressions = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            expressions.extend(matches)
        
        # Filter out simple numbers and clean up
        cleaned = []
        for expr in expressions:
            expr = expr.strip()
            if any(op in expr for op in ['+', '-', '*', '/', '^', '(', 'sqrt', 'sin', 'cos', 'tan', 'log', 'exp']) and len(expr) > 1:
                cleaned.append(expr.replace('^', '**'))  # Python uses ** for power
        
        return cleaned
    
    def _extract_matrices(self, text: str) -> List[List[List[float]]]:
        """Extract matrices from text."""
        # Look for matrix patterns like [[1,2],[3,4]]
        matrix_pattern = r'\\[\\[([\\d.,\\s]+)\\](?:,\\s*\\[([\\d.,\\s]+)\\])*\\]'
        
        # Simplified: look for any array-like structures
        arrays = re.findall(r'\\[([\\d.,\\s]+)\\]', text)
        
        matrices = []
        for array in arrays:
            row = [float(x.strip()) for x in array.split(',') if x.strip()]
            matrices.append([row])  # Single row matrix
        
        return matrices
    
    # Operators allowed in AST-based math evaluation
    _SAFE_OPS = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.FloorDiv: operator.floordiv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    # Named functions / constants allowed in expressions
    _SAFE_NAMES: Dict[str, Any] = {
        'sqrt': np.sqrt,
        'sin': np.sin,
        'cos': np.cos,
        'tan': np.tan,
        'log': np.log,
        'exp': np.exp,
        'pi': np.pi,
        'e': np.e,
        'abs': abs,
        'pow': pow,
        'round': round,
    }

    def _safe_eval(self, expression: str) -> float:
        """Safely evaluate mathematical expressions using AST parsing."""
        expression = expression.replace('^', '**')  # Python power operator
        try:
            tree = ast.parse(expression, mode='eval')
            result = self._eval_node(tree.body)
            return float(result)
        except Exception:
            raise ValueError(f"Invalid mathematical expression: {expression}")

    def _eval_node(self, node: ast.AST) -> float:
        """Recursively evaluate an AST node (no eval/exec)."""
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp):
            op = self._SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(self._eval_node(node.left), self._eval_node(node.right))
        if isinstance(node, ast.UnaryOp):
            op = self._SAFE_OPS.get(type(node.op))
            if op is None:
                raise ValueError(f"Unsupported operator: {type(node.op).__name__}")
            return op(self._eval_node(node.operand))
        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise ValueError("Only simple function calls are allowed")
            func = self._SAFE_NAMES.get(node.func.id)
            if func is None:
                raise ValueError(f"Unknown function: {node.func.id}")
            args = [self._eval_node(a) for a in node.args]
            return func(*args)
        if isinstance(node, ast.Name):
            val = self._SAFE_NAMES.get(node.id)
            if val is None:
                raise ValueError(f"Unknown name: {node.id}")
            return val
        raise ValueError(f"Unsupported expression element: {type(node).__name__}")


if __name__ == "__main__":
    agent = MathAgent()
    agent.start_server()
