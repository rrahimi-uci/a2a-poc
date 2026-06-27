"""
Multi-Agent Orchestrator - Demonstrates A2A communication between Math and Data Analyst agents.
"""

import asyncio
import logging
from typing import List, Dict, Any
import json

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.base_agent import A2AClient
from common.a2a_protocol import Message, MessagePart, MessageRole

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """Orchestrator that coordinates between Math and Data Analyst agents."""
    
    def __init__(self, 
                 math_agent_url: str = "http://localhost:8001",
                 data_agent_url: str = "http://localhost:8002"):
        self.math_agent_url = math_agent_url
        self.data_agent_url = data_agent_url
        self.client = A2AClient()
        
    async def solve_problem(self, problem_description: str) -> Dict[str, Any]:
        """
        Solve a complex problem by coordinating between Math and Data Analyst agents.
        
        Args:
            problem_description: Description of the problem to solve
            
        Returns:
            Dictionary containing the solution process and results
        """
        logger.info(f"Starting problem solving: {problem_description}")
        
        solution_process = {
            "problem": problem_description,
            "steps": [],
            "final_result": None,
            "agents_used": []
        }
        
        try:
            # Step 1: Analyze the problem and determine which agents to use
            analysis = await self._analyze_problem(problem_description)
            solution_process["steps"].append({
                "step": "Problem Analysis",
                "result": analysis
            })
            
            # Step 2: If mathematical computation is needed, use Math Agent
            if analysis["needs_math"]:
                math_result = await self._get_math_analysis(problem_description)
                solution_process["steps"].append({
                    "step": "Mathematical Analysis",
                    "agent": "Math Agent",
                    "result": math_result
                })
                solution_process["agents_used"].append("Math Agent")
                
                # Step 3: If we have math results and need visualization, use Data Analyst
                if analysis["needs_visualization"] and math_result:
                    viz_request = self._create_visualization_request(problem_description, math_result)
                    viz_result = await self._get_data_analysis(viz_request)
                    solution_process["steps"].append({
                        "step": "Data Visualization",
                        "agent": "Data Analyst Agent",
                        "result": viz_result
                    })
                    solution_process["agents_used"].append("Data Analyst Agent")
                    solution_process["final_result"] = self._combine_results(math_result, viz_result)
                else:
                    solution_process["final_result"] = math_result
                    
            # Step 2 Alternative: If only data analysis is needed
            elif analysis["needs_data_analysis"]:
                data_result = await self._get_data_analysis(problem_description)
                solution_process["steps"].append({
                    "step": "Data Analysis",
                    "agent": "Data Analyst Agent", 
                    "result": data_result
                })
                solution_process["agents_used"].append("Data Analyst Agent")
                solution_process["final_result"] = data_result
                
            else:
                solution_process["final_result"] = "Problem type not recognized. Please specify if you need mathematical computation or data analysis."
                
        except Exception as e:
            logger.error(f"Error in problem solving: {e}")
            solution_process["error"] = str(e)
            solution_process["final_result"] = f"Error occurred: {str(e)}"
            
        return solution_process
    
    async def _analyze_problem(self, problem: str) -> Dict[str, bool]:
        """Analyze the problem to determine which agents are needed."""
        problem_lower = problem.lower()
        
        # Keywords that suggest mathematical computation
        math_keywords = [
            "calculate", "compute", "solve", "equation", "formula", "math",
            "statistics", "mean", "average", "sum", "product", "derivative",
            "integral", "probability", "distribution", "correlation", "regression"
        ]
        
        # Keywords that suggest data analysis/visualization
        data_keywords = [
            "plot", "chart", "graph", "visualize", "histogram", "scatter",
            "analyze data", "trend", "pattern", "report", "insights",
            "correlation", "distribution", "summary"
        ]
        
        needs_math = any(keyword in problem_lower for keyword in math_keywords)
        needs_data_analysis = any(keyword in problem_lower for keyword in data_keywords)
        needs_visualization = any(keyword in problem_lower for keyword in ["plot", "chart", "graph", "visualize", "histogram", "scatter"])
        
        return {
            "needs_math": needs_math,
            "needs_data_analysis": needs_data_analysis,
            "needs_visualization": needs_visualization
        }
    
    async def _get_math_analysis(self, problem: str) -> str:
        """Get mathematical analysis from Math Agent."""
        try:
            message = Message(
                role=MessageRole.USER,
                parts=[MessagePart(text=problem)]
            )
            
            task = await self.client.send_message(self.math_agent_url, message)
            
            if task.status.state.value == "completed" and task.status.message:
                return task.status.message.parts[0].text
            else:
                return f"Math Agent error: {task.status.error or 'Unknown error'}"
                
        except Exception as e:
            logger.error(f"Error communicating with Math Agent: {e}")
            return f"Failed to get math analysis: {str(e)}"
    
    async def _get_data_analysis(self, problem: str) -> str:
        """Get data analysis from Data Analyst Agent."""
        try:
            message = Message(
                role=MessageRole.USER,
                parts=[MessagePart(text=problem)]
            )
            
            task = await self.client.send_message(self.data_agent_url, message)
            
            if task.status.state.value == "completed" and task.status.message:
                return task.status.message.parts[0].text
            else:
                return f"Data Analyst Agent error: {task.status.error or 'Unknown error'}"
                
        except Exception as e:
            logger.error(f"Error communicating with Data Analyst Agent: {e}")
            return f"Failed to get data analysis: {str(e)}"
    
    def _create_visualization_request(self, original_problem: str, math_result: str) -> str:
        """Create a visualization request based on the math result."""
        return f"""Based on the mathematical analysis below, please create appropriate visualizations:

Original Problem: {original_problem}

Mathematical Results:
{math_result}

Please extract any numeric data from the mathematical results and create suitable charts or plots."""
    
    def _combine_results(self, math_result: str, viz_result: str) -> str:
        """Combine results from both agents into a comprehensive solution."""
        return f"""Comprehensive Analysis Results:

MATHEMATICAL ANALYSIS:
{math_result}

DATA VISUALIZATION & INSIGHTS:
{viz_result}

This solution was created through collaboration between specialized agents:
- Math Agent: Performed calculations and statistical analysis
- Data Analyst Agent: Created visualizations and provided data insights"""


async def main():
    """Main function to demonstrate the multi-agent system."""
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = MultiAgentOrchestrator()
    
    # Example problems to solve
    problems = [
        "Calculate the mean and standard deviation of the dataset [12, 15, 18, 20, 22, 25, 28, 30] and create a histogram",
        "Find the correlation between these data points: [(1,5), (2,7), (3,6), (4,8), (5,10)] and visualize the relationship",
        "Analyze the statistical properties of the normal distribution with mean 100 and standard deviation 15",
        "Generate a summary report for the sales data: [450, 520, 380, 610, 720, 890, 560, 440, 650, 780]"
    ]
    
    print("🤖 Multi-Agent Problem Solving System")
    print("=" * 50)
    
    for i, problem in enumerate(problems, 1):
        print(f"\n{i}. Problem: {problem}")
        print("-" * 40)
        
        try:
            result = await orchestrator.solve_problem(problem)
            
            print(f"Agents Used: {', '.join(result['agents_used'])}")
            print(f"Steps Completed: {len(result['steps'])}")
            print("\nFinal Result:")
            print(result['final_result'])
            
        except Exception as e:
            print(f"Error solving problem: {e}")
        
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
