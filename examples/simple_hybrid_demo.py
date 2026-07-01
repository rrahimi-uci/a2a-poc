"""
Simple A2A-External Agent Bridge Example
Demonstrates how A2A agents can work with external agent systems (like AutoGen).
This example works without requiring AutoGen installation.
"""

import asyncio
import logging
import json
from typing import Dict, Any, Optional
import requests

import sys
import os

# Local simplified client for demo. Support both running this file as a script
# (``python examples/simple_hybrid_demo.py``) and importing it as a package
# module (``from examples.simple_hybrid_demo import ...``).
try:
    from examples.simple_a2a_client import SimpleA2AClient
except ImportError:  # pragma: no cover - script-relative fallback
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from simple_a2a_client import SimpleA2AClient

logger = logging.getLogger(__name__)


class MockAutoGenAgent:
    """
    Mock AutoGen agent that simulates code generation.
    In a real scenario, this would interface with actual AutoGen agents.
    """
    
    def __init__(self):
        self.name = "MockAutoGen_CodeGenerator"
        self.framework = "AutoGen (Simulated)"
        
    async def generate_code(self, request: str) -> str:
        """Simulate code generation based on request."""
        
        # Simulate processing delay
        await asyncio.sleep(1)
        
        # Generate mock code based on request content
        if "normal distribution" in request.lower():
            return self._generate_normal_distribution_code()
        elif "correlation" in request.lower():
            return self._generate_correlation_code()
        elif "statistics" in request.lower() or "mean" in request.lower():
            return self._generate_statistics_code()
        else:
            return self._generate_generic_analysis_code()
    
    def _generate_normal_distribution_code(self) -> str:
        return '''"""
AutoGen Generated Code: Normal Distribution Analysis
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def analyze_normal_distribution(mean=50, std=10, samples=1000):
    """Generate and analyze normal distribution samples."""
    
    # Generate random samples
    data = np.random.normal(mean, std, samples)
    
    # Calculate statistics
    sample_mean = np.mean(data)
    sample_std = np.std(data)
    
    # Create visualization
    plt.figure(figsize=(12, 8))
    
    # Histogram
    plt.subplot(2, 2, 1)
    plt.hist(data, bins=30, density=True, alpha=0.7, color='skyblue')
    plt.title(f'Normal Distribution (μ={mean}, σ={std})')
    plt.xlabel('Value')
    plt.ylabel('Density')
    
    # Q-Q plot
    plt.subplot(2, 2, 2)
    stats.probplot(data, dist="norm", plot=plt)
    plt.title('Q-Q Plot')
    
    # Box plot
    plt.subplot(2, 2, 3)
    plt.boxplot(data)
    plt.title('Box Plot')
    plt.ylabel('Value')
    
    # Statistics summary
    plt.subplot(2, 2, 4)
    plt.text(0.1, 0.8, f'Population μ: {mean}', transform=plt.gca().transAxes)
    plt.text(0.1, 0.7, f'Population σ: {std}', transform=plt.gca().transAxes)
    plt.text(0.1, 0.5, f'Sample mean: {sample_mean:.2f}', transform=plt.gca().transAxes)
    plt.text(0.1, 0.4, f'Sample std: {sample_std:.2f}', transform=plt.gca().transAxes)
    plt.text(0.1, 0.3, f'Sample size: {samples}', transform=plt.gca().transAxes)
    plt.axis('off')
    plt.title('Statistics Summary')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'sample_mean': sample_mean,
        'sample_std': sample_std,
        'population_mean': mean,
        'population_std': std
    }

# Example usage
if __name__ == "__main__":
    result = analyze_normal_distribution(mean=50, std=10, samples=1000)
    print("Analysis complete!")
    print(f"Results: {result}")'''
    
    def _generate_correlation_code(self) -> str:
        return '''"""
AutoGen Generated Code: Correlation Analysis
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import pandas as pd

def correlation_analysis(x_data, y_data):
    """Perform correlation analysis and visualization."""
    
    # Calculate correlation
    correlation_coef, p_value = stats.pearsonr(x_data, y_data)
    
    # Linear regression
    slope, intercept, r_value, p_val, std_err = stats.linregress(x_data, y_data)
    
    # Create visualization
    plt.figure(figsize=(12, 5))
    
    # Scatter plot with regression line
    plt.subplot(1, 2, 1)
    plt.scatter(x_data, y_data, alpha=0.7, color='blue')
    
    # Plot regression line
    line_x = np.array([min(x_data), max(x_data)])
    line_y = slope * line_x + intercept
    plt.plot(line_x, line_y, 'r-', alpha=0.8, linewidth=2)
    
    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.title(f'Correlation Analysis (r = {correlation_coef:.3f})')
    plt.grid(True, alpha=0.3)
    
    # Residuals plot
    plt.subplot(1, 2, 2)
    predicted_y = slope * np.array(x_data) + intercept
    residuals = np.array(y_data) - predicted_y
    plt.scatter(predicted_y, residuals, alpha=0.7, color='green')
    plt.axhline(y=0, color='red', linestyle='--', alpha=0.8)
    plt.xlabel('Predicted Values')
    plt.ylabel('Residuals')
    plt.title('Residuals Plot')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Print results
    print(f"Correlation coefficient: {correlation_coef:.4f}")
    print(f"P-value: {p_value:.4f}")
    print(f"Linear regression: y = {slope:.4f}x + {intercept:.4f}")
    print(f"R-squared: {r_value**2:.4f}")
    
    return {
        'correlation': correlation_coef,
        'p_value': p_value,
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2
    }

# Example usage
if __name__ == "__main__":
    # Sample data
    x = [1, 3, 5, 7, 9]
    y = [2, 5, 8, 11, 14]
    
    result = correlation_analysis(x, y)
    print("Correlation analysis complete!")'''
    
    def _generate_statistics_code(self) -> str:
        return '''"""
AutoGen Generated Code: Statistical Analysis
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

def comprehensive_statistics(data):
    """Perform comprehensive statistical analysis."""
    
    data = np.array(data)
    
    # Descriptive statistics
    statistics = {
        'mean': np.mean(data),
        'median': np.median(data),
        'mode': stats.mode(data)[0][0] if len(stats.mode(data)[0]) > 0 else None,
        'std_dev': np.std(data, ddof=1),
        'variance': np.var(data, ddof=1),
        'min': np.min(data),
        'max': np.max(data),
        'range': np.max(data) - np.min(data),
        'q1': np.percentile(data, 25),
        'q3': np.percentile(data, 75),
        'iqr': np.percentile(data, 75) - np.percentile(data, 25),
        'skewness': stats.skew(data),
        'kurtosis': stats.kurtosis(data)
    }
    
    # Create comprehensive visualization
    plt.figure(figsize=(15, 10))
    
    # Histogram
    plt.subplot(2, 3, 1)
    plt.hist(data, bins=10, density=True, alpha=0.7, color='lightblue', edgecolor='black')
    plt.title('Histogram')
    plt.xlabel('Values')
    plt.ylabel('Density')
    
    # Box plot
    plt.subplot(2, 3, 2)
    plt.boxplot(data)
    plt.title('Box Plot')
    plt.ylabel('Values')
    
    # Q-Q plot
    plt.subplot(2, 3, 3)
    stats.probplot(data, dist="norm", plot=plt)
    plt.title('Q-Q Plot (Normal)')
    
    # Time series (if applicable)
    plt.subplot(2, 3, 4)
    plt.plot(range(len(data)), data, 'o-', alpha=0.7)
    plt.title('Data Sequence')
    plt.xlabel('Index')
    plt.ylabel('Value')
    
    # Statistics summary
    plt.subplot(2, 3, 5)
    stats_text = f"""Statistics Summary:
Mean: {statistics['mean']:.2f}
Median: {statistics['median']:.2f}
Std Dev: {statistics['std_dev']:.2f}
Min: {statistics['min']:.2f}
Max: {statistics['max']:.2f}
Q1: {statistics['q1']:.2f}
Q3: {statistics['q3']:.2f}
Skewness: {statistics['skewness']:.3f}
Kurtosis: {statistics['kurtosis']:.3f}"""
    
    plt.text(0.1, 0.5, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='center')
    plt.axis('off')
    plt.title('Summary Statistics')
    
    # Distribution comparison
    plt.subplot(2, 3, 6)
    x = np.linspace(statistics['min'], statistics['max'], 100)
    normal_pdf = stats.norm.pdf(x, statistics['mean'], statistics['std_dev'])
    plt.plot(x, normal_pdf, 'r-', label='Normal Distribution')
    plt.hist(data, bins=10, density=True, alpha=0.5, color='lightblue', label='Data')
    plt.legend()
    plt.title('Distribution Comparison')
    plt.xlabel('Values')
    plt.ylabel('Density')
    
    plt.tight_layout()
    plt.show()
    
    return statistics

# Example usage
if __name__ == "__main__":
    # Sample data
    sample_data = [15, 23, 18, 32, 28, 19, 25, 31, 22, 27]
    
    results = comprehensive_statistics(sample_data)
    print("Statistical analysis complete!")
    for key, value in results.items():
        if value is not None:
            print(f"{key}: {value}")'''
    
    def _generate_generic_analysis_code(self) -> str:
        return '''"""
AutoGen Generated Code: Generic Data Analysis
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def generic_data_analysis(data):
    """Perform generic data analysis."""
    
    if isinstance(data, list):
        data = np.array(data)
    
    print("=== Data Analysis Report ===")
    print(f"Data shape: {data.shape}")
    print(f"Data type: {data.dtype}")
    print(f"Sample data: {data[:5] if len(data) > 5 else data}")
    
    # Basic statistics
    print("\n=== Basic Statistics ===")
    print(f"Mean: {np.mean(data):.4f}")
    print(f"Median: {np.median(data):.4f}")
    print(f"Standard Deviation: {np.std(data):.4f}")
    print(f"Min: {np.min(data):.4f}")
    print(f"Max: {np.max(data):.4f}")
    
    # Visualization
    plt.figure(figsize=(10, 6))
    
    plt.subplot(1, 2, 1)
    plt.hist(data, bins=15, alpha=0.7, color='lightgreen')
    plt.title('Data Distribution')
    plt.xlabel('Values')
    plt.ylabel('Frequency')
    
    plt.subplot(1, 2, 2)
    plt.plot(data, 'o-', alpha=0.7, color='blue')
    plt.title('Data Sequence')
    plt.xlabel('Index')
    plt.ylabel('Value')
    
    plt.tight_layout()
    plt.show()
    
    return {
        'mean': np.mean(data),
        'std': np.std(data),
        'summary': 'Generic analysis completed'
    }

# Example usage
if __name__ == "__main__":
    sample_data = np.random.randn(100)
    result = generic_data_analysis(sample_data)
    print(f"Analysis result: {result}")'''


class SimpleHybridOrchestrator:
    """
    Simple hybrid orchestrator demonstrating A2A + External Agent collaboration.
    Uses mock AutoGen agent to show the integration pattern.
    """
    
    def __init__(self, math_agent_url: str = "http://localhost:8001"):
        self.math_agent_url = math_agent_url
        self.a2a_client = SimpleA2AClient()
        self.mock_autogen = MockAutoGenAgent()
        
    async def solve_with_collaboration(self, problem: str) -> Dict[str, Any]:
        """
        Solve problem using A2A Math Agent + Mock AutoGen Code Agent.
        """
        print(f"🤝 COLLABORATIVE PROBLEM SOLVING")
        print(f"Problem: {problem}")
        print("-" * 50)
        
        result = {
            "problem": problem,
            "agents": [],
            "steps": [],
            "math_analysis": None,
            "generated_code": None,
            "final_solution": None
        }
        
        try:
            # Step 1: Mathematical analysis via A2A Protocol
            print("📊 Step 1: Mathematical Analysis (A2A Protocol)")
            math_result = await self._get_math_analysis(problem)
            result["math_analysis"] = math_result
            result["agents"].append("A2A Math Agent")
            result["steps"].append({
                "agent": "A2A Math Agent",
                "framework": "Custom A2A Protocol",
                "task": "Mathematical computation and analysis",
                "result_preview": math_result[:100] + "..." if len(math_result) > 100 else math_result
            })
            
            # Step 2: Code generation via Mock AutoGen
            print("💻 Step 2: Code Generation (Mock AutoGen)")
            code_request = f"Generate Python code for: {problem}\n\nMath results: {math_result}"
            code_result = await self.mock_autogen.generate_code(code_request)
            result["generated_code"] = code_result
            result["agents"].append("Mock AutoGen Agent")
            result["steps"].append({
                "agent": "Mock AutoGen Agent",
                "framework": "AutoGen (Simulated)",
                "task": "Python code generation and implementation",
                "result_preview": "Python code generated successfully"
            })
            
            # Step 3: Combine results
            result["final_solution"] = self._create_combined_solution(problem, math_result, code_result)
            
        except Exception as e:
            logger.error(f"Error in collaborative solving: {e}")
            result["error"] = str(e)
            
        return result
    
    async def _get_math_analysis(self, problem: str) -> str:
        """Get mathematical analysis from A2A Math Agent."""
        try:
            # Use simplified client that returns string directly
            result = await self.a2a_client.send_message(self.math_agent_url, problem)
            return result
                
        except Exception as e:
            return f"Failed to connect to A2A Math Agent: {str(e)}"
    
    def _create_combined_solution(self, problem: str, math_result: str, code_result: str) -> str:
        """Create a combined solution from both agents."""
        return f"""
🔬 COLLABORATIVE MULTI-AGENT SOLUTION 🔬

PROBLEM: {problem}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MATHEMATICAL ANALYSIS (A2A Protocol Agent):
{math_result}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💻 IMPLEMENTATION CODE (AutoGen-style Agent):

{code_result}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 COLLABORATION SUMMARY:
✅ A2A Agent: Provided precise mathematical calculations
✅ AutoGen Agent: Generated complete implementation code
✅ Integration: Seamless data flow between different agent frameworks
✅ Result: Complete analytical and practical solution

This demonstrates how agents from different platforms can collaborate effectively!
"""


async def demo_simple_hybrid():
    """Run a simple demo of the hybrid system."""
    print("🚀 SIMPLE HYBRID A2A-AUTOGEN DEMO")
    print("=" * 50)
    print("This demo shows basic interoperability between:")
    print("• A2A Protocol Agent (Math Agent)")
    print("• Mock AutoGen Agent (Code Generator)")
    print()
    
    orchestrator = SimpleHybridOrchestrator()
    
    # Test problems
    problems = [
        "Calculate mean and standard deviation of [12, 15, 18, 20, 22, 25, 28, 30] and create visualization code",
        "Find correlation between [(1,5), (2,7), (3,6), (4,8), (5,10)] and generate analysis script",
        "Analyze normal distribution with mean=100, std=15 and create simulation code"
    ]
    
    for i, problem in enumerate(problems, 1):
        print(f"\n🔬 EXAMPLE {i}:")
        print("-" * 30)
        
        try:
            result = await orchestrator.solve_with_collaboration(problem)
            
            print(f"✅ Agents used: {', '.join(result['agents'])}")
            print(f"✅ Steps completed: {len(result['steps'])}")
            
            for step in result['steps']:
                print(f"   • {step['agent']} ({step['framework']}): {step['task']}")
            
            print("\n🎯 Final Solution:")
            print(result['final_solution'])
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("=" * 50)
        
        # Small delay between examples
        await asyncio.sleep(1)


async def main():
    """Main function."""
    logging.basicConfig(level=logging.INFO)
    
    print("🌟 A2A-AUTOGEN INTEROPERABILITY EXAMPLE 🌟")
    print()
    print("This example demonstrates how A2A agents can work with")
    print("external agent frameworks like Microsoft AutoGen.")
    print()
    print("Features demonstrated:")
    print("• Cross-framework agent communication")
    print("• Protocol translation between different agent systems")  
    print("• Collaborative problem solving")
    print("• Code generation + mathematical analysis")
    print()
    
    await demo_simple_hybrid()
    
    print("\n✨ Simple hybrid demo complete!")
    print("\n🔧 To try with real AutoGen:")
    print("1. Run: python examples/setup_autogen.py")
    print("2. Set OpenAI API key")
    print("3. Run: python examples/hybrid_autogen_a2a.py")


if __name__ == "__main__":
    asyncio.run(main())
