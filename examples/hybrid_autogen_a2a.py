"""
AutoGen-A2A Hybrid Orchestrator - Demonstrates interoperability between A2A agents and AutoGen agents.

This example shows how our A2A Math Agent can work together with an AutoGen-based 
Code Generator Agent to solve complex problems that require both mathematical 
computation and code generation.
"""

import asyncio
import logging
import os
from typing import List, Dict, Any, Optional
import json

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.base_agent import A2AClient
from common.a2a_protocol import Message, MessagePart, MessageRole

# AutoGen imports
try:
    import autogen
    from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
    AUTOGEN_AVAILABLE = True
except ImportError:
    AUTOGEN_AVAILABLE = False
    print("⚠️  AutoGen not available. Install with: pip install pyautogen")

logger = logging.getLogger(__name__)


class AutoGenCodeAgent:
    """
    AutoGen-based Code Generation Agent that can create Python code solutions.
    This agent uses Microsoft's AutoGen framework with LLM capabilities.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        if not AUTOGEN_AVAILABLE:
            raise ImportError("AutoGen is required. Install with: pip install pyautogen")
            
        # Configuration for OpenAI API (you can replace with other LLM providers)
        self.config_list = [
            {
                "model": "gpt-3.5-turbo",
                "api_key": api_key or os.getenv("OPENAI_API_KEY", "your-api-key-here")
            }
        ]
        
        # Create AutoGen agents
        self.assistant = AssistantAgent(
            name="code_generator",
            system_message="""You are an expert Python programmer specializing in data analysis and mathematical computing.
            Your role is to:
            1. Generate clean, efficient Python code
            2. Create data analysis scripts
            3. Implement mathematical algorithms
            4. Write code that works with numpy, pandas, matplotlib
            5. Provide well-documented code with explanations
            
            Always return executable Python code when requested.""",
            llm_config={"config_list": self.config_list}
        )
        
        self.user_proxy = UserProxyAgent(
            name="user_proxy",
            human_input_mode="NEVER",
            max_consecutive_auto_reply=1,
            code_execution_config={
                "work_dir": "autogen_workspace",
                "use_docker": False  # Set to True if you have Docker available
            }
        )
        
    async def generate_code(self, request: str) -> str:
        """
        Generate Python code using AutoGen's conversational AI.
        
        Args:
            request: Description of what code to generate
            
        Returns:
            Generated Python code as string
        """
        try:
            # Initiate conversation between agents
            chat_result = self.user_proxy.initiate_chat(
                self.assistant,
                message=f"""Generate Python code for the following request:
                
{request}

Please provide clean, executable Python code with comments explaining the logic.""",
                clear_history=True
            )
            
            # Extract the generated code from the conversation
            if hasattr(chat_result, 'chat_history'):
                for message in reversed(chat_result.chat_history):
                    if 'code' in message.get('content', '').lower():
                        return message.get('content', '')
            
            # Fallback: return last assistant message
            return chat_result.summary if hasattr(chat_result, 'summary') else "Code generation completed"
            
        except Exception as e:
            logger.error(f"AutoGen code generation failed: {e}")
            return f"Error generating code: {str(e)}"


class HybridA2AAutoGenOrchestrator:
    """
    Hybrid orchestrator that combines A2A Math Agent with AutoGen Code Agent.
    Demonstrates interoperability between different agent frameworks.
    """
    
    def __init__(self, 
                 math_agent_url: str = "http://localhost:8001",
                 openai_api_key: Optional[str] = None):
        self.math_agent_url = math_agent_url
        self.a2a_client = A2AClient()
        
        # Initialize AutoGen agent if available
        if AUTOGEN_AVAILABLE:
            try:
                self.autogen_agent = AutoGenCodeAgent(api_key=openai_api_key)
                self.autogen_enabled = True
            except Exception as e:
                logger.warning(f"AutoGen agent initialization failed: {e}")
                self.autogen_enabled = False
        else:
            self.autogen_enabled = False
            
    async def solve_hybrid_problem(self, problem_description: str) -> Dict[str, Any]:
        """
        Solve a problem using both A2A Math Agent and AutoGen Code Agent.
        
        Args:
            problem_description: Complex problem requiring both math and code
            
        Returns:
            Dictionary containing the collaborative solution
        """
        logger.info(f"Starting hybrid problem solving: {problem_description}")
        
        solution_process = {
            "problem": problem_description,
            "agents_used": [],
            "steps": [],
            "final_result": None,
            "code_generated": None,
            "math_results": None
        }
        
        try:
            # Step 1: Mathematical Analysis using A2A Math Agent
            print("🔢 Step 1: Mathematical Analysis (A2A Math Agent)")
            math_result = await self._get_a2a_math_analysis(problem_description)
            solution_process["math_results"] = math_result
            solution_process["agents_used"].append("A2A Math Agent")
            solution_process["steps"].append({
                "step": "Mathematical Analysis",
                "agent": "A2A Math Agent",
                "framework": "Custom A2A Protocol",
                "result": math_result
            })
            
            # Step 2: Code Generation using AutoGen
            if self.autogen_enabled:
                print("💻 Step 2: Code Generation (AutoGen Agent)")
                code_request = self._create_code_request(problem_description, math_result)
                code_result = await self._get_autogen_code(code_request)
                solution_process["code_generated"] = code_result
                solution_process["agents_used"].append("AutoGen Code Agent")
                solution_process["steps"].append({
                    "step": "Code Generation",
                    "agent": "AutoGen Code Agent", 
                    "framework": "Microsoft AutoGen",
                    "result": code_result
                })
                
                # Step 3: Combine results
                solution_process["final_result"] = self._combine_hybrid_results(
                    problem_description, math_result, code_result
                )
            else:
                solution_process["final_result"] = f"""Mathematical Analysis Complete:
{math_result}

Note: AutoGen code generation was not available. Install AutoGen for full hybrid functionality."""
                
        except Exception as e:
            logger.error(f"Error in hybrid problem solving: {e}")
            solution_process["error"] = str(e)
            solution_process["final_result"] = f"Error occurred: {str(e)}"
            
        return solution_process
    
    async def _get_a2a_math_analysis(self, problem: str) -> str:
        """Get mathematical analysis from A2A Math Agent."""
        try:
            message = Message(
                role=MessageRole.USER,
                parts=[MessagePart(text=problem)]
            )
            
            task = await self.a2a_client.send_message(self.math_agent_url, message)
            
            if task.status.state.value == "completed" and task.status.message:
                return task.status.message.parts[0].text
            else:
                return f"A2A Math Agent error: {task.status.error or 'Unknown error'}"
                
        except Exception as e:
            logger.error(f"Error communicating with A2A Math Agent: {e}")
            return f"Failed to get A2A math analysis: {str(e)}"
    
    async def _get_autogen_code(self, code_request: str) -> str:
        """Get code generation from AutoGen Agent."""
        if not self.autogen_enabled:
            return "AutoGen agent not available"
            
        try:
            # Run AutoGen code generation in a separate thread to avoid blocking
            import concurrent.futures
            
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                code_result = await loop.run_in_executor(
                    executor, 
                    self.autogen_agent.generate_code,
                    code_request
                )
            
            return code_result
            
        except Exception as e:
            logger.error(f"Error with AutoGen code generation: {e}")
            return f"Failed to generate code: {str(e)}"
    
    def _create_code_request(self, original_problem: str, math_result: str) -> str:
        """Create a code generation request based on the math analysis."""
        return f"""Based on the mathematical analysis below, generate Python code that:

1. Implements the mathematical calculations
2. Creates visualizations of the results
3. Provides a complete solution script

Original Problem: {original_problem}

Mathematical Analysis Results:
{math_result}

Please generate clean, executable Python code with:
- Necessary imports (numpy, pandas, matplotlib, etc.)
- Function definitions for calculations
- Visualization code
- Example usage
- Comments explaining each step"""
    
    def _combine_hybrid_results(self, problem: str, math_result: str, code_result: str) -> str:
        """Combine results from both A2A and AutoGen agents."""
        return f"""🤖 HYBRID MULTI-FRAMEWORK AGENT SOLUTION 🤖

PROBLEM: {problem}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MATHEMATICAL ANALYSIS (A2A Custom Protocol Agent):
{math_result}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 GENERATED CODE SOLUTION (Microsoft AutoGen Agent):
{code_result}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 FRAMEWORKS COLLABORATION:
✅ A2A Protocol: Custom agent-to-agent communication
✅ Microsoft AutoGen: LLM-powered conversational AI agents
✅ Interoperability: Seamless data flow between different agent platforms

This solution demonstrates how agents from different frameworks can collaborate:
- A2A Agent: Specialized mathematical computation with custom protocol
- AutoGen Agent: LLM-powered code generation with conversational AI
- Result: Combined analytical and implementation solution"""


async def demo_hybrid_system():
    """Demonstrate the hybrid A2A-AutoGen system."""
    print("🚀 HYBRID A2A-AUTOGEN MULTI-AGENT SYSTEM DEMO")
    print("=" * 60)
    
    # Check if required components are available
    if not AUTOGEN_AVAILABLE:
        print("⚠️  AutoGen not installed. Limited functionality available.")
        print("   Install with: pip install pyautogen")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("⚠️  OpenAI API key not set. AutoGen will use placeholder.")
        print("   Set OPENAI_API_KEY environment variable for full functionality.")
    
    orchestrator = HybridA2AAutoGenOrchestrator(openai_api_key=api_key)
    
    # Example problems that benefit from both math analysis and code generation
    hybrid_problems = [
        "Calculate statistical properties of a normal distribution with mean 50 and std 10, then generate Python code to simulate and visualize 1000 samples",
        
        "Find the correlation coefficient for data points [(1,2), (3,5), (5,8), (7,11), (9,14)] and create code to plot the regression line",
        
        "Compute the mean and variance of [15, 23, 18, 32, 28, 19, 25, 31] and generate a complete analysis script with histogram and summary statistics",
        
        "Analyze the mathematical properties of fibonacci sequence up to 20 terms and create code to generate and visualize the sequence"
    ]
    
    for i, problem in enumerate(hybrid_problems, 1):
        print(f"\\n{i}. HYBRID PROBLEM:")
        print(f"   {problem}")
        print("-" * 60)
        
        try:
            result = await orchestrator.solve_hybrid_problem(problem)
            
            print(f"🤖 Agents Used: {', '.join(result['agents_used'])}")
            print(f"📝 Steps Completed: {len(result['steps'])}")
            
            for step in result['steps']:
                print(f"   • {step['step']} via {step['framework']}")
            
            print("\\n🎯 FINAL HYBRID SOLUTION:")
            print(result['final_result'])
            
        except Exception as e:
            print(f"❌ Error solving hybrid problem: {e}")
        
        print("=" * 60)
        
        # Add delay between problems to avoid API rate limits
        await asyncio.sleep(2)


async def main():
    """Main function to run the hybrid demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🌟 A2A-AUTOGEN INTEROPERABILITY DEMONSTRATION 🌟")
    print()
    print("This demo shows how different agent frameworks can work together:")
    print("• A2A Protocol: Custom agent communication for specialized tasks")
    print("• Microsoft AutoGen: LLM-powered conversational agents")
    print("• Hybrid Approach: Best of both worlds")
    print()
    
    await demo_hybrid_system()
    
    print("\\n✨ Hybrid agent system demonstration complete!")
    print("\\n🔧 To enable full functionality:")
    print("1. Install AutoGen: pip install pyautogen")
    print("2. Set OpenAI API key: export OPENAI_API_KEY='your-key'")
    print("3. Start A2A Math Agent: python scripts/start_math_agent.py")
    print("4. Run this demo: python examples/hybrid_autogen_a2a.py")


if __name__ == "__main__":
    asyncio.run(main())
