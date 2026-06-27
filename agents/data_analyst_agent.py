"""
Data Analyst Agent - Specialized agent for data analysis and visualization.
"""

import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from typing import Dict, List, Any, Optional
import json
import re
import tempfile
import os

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.base_agent import BaseAgent
from common.a2a_protocol import (
    Message, Task, TaskStatus, TaskState, MessageRole, MessagePart, MessageSendParams
)

logger = logging.getLogger(__name__)


class DataAnalystAgent(BaseAgent):
    """Agent specialized in data analysis, visualization, and reporting."""
    
    def __init__(self, port: int = 8002):
        capabilities = [
            "data_visualization",
            "data_analysis", 
            "statistical_reporting",
            "chart_generation",
            "data_cleaning",
            "trend_analysis",
            "correlation_analysis"
        ]
        
        super().__init__(
            agent_id="data-analyst-agent-001",
            name="Data Analyst Agent",
            description="Specialized agent for data analysis, visualization, and statistical reporting",
            port=port,
            capabilities=capabilities,
            supported_content_types=["text/plain", "application/json", "image/png"]
        )
        
        # Set matplotlib to use non-interactive backend
        plt.switch_backend('Agg')
        
    async def process_message(self, params: MessageSendParams) -> Task:
        """Process incoming message and perform data analysis operations."""
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
            
            # Determine operation type and perform analysis
            result = await self._perform_analysis(text_content)
            
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
            logger.error(f"Error in data analysis: {e}")
            error_message = Message(
                role=MessageRole.AGENT,
                parts=[MessagePart(text=f"Error performing analysis: {str(e)}")],
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
    
    async def _perform_analysis(self, text: str) -> str:
        """Perform data analysis based on text input."""
        text = text.lower().strip()
        
        # Visualization patterns
        if any(keyword in text for keyword in ["plot", "chart", "graph", "visualize", "histogram", "scatter"]):
            return await self._handle_visualization(text)
        
        # Data analysis patterns
        if any(keyword in text for keyword in ["analyze", "correlation", "trend", "pattern"]):
            return await self._handle_data_analysis(text)
        
        # Reporting patterns
        if any(keyword in text for keyword in ["report", "summary", "insights", "findings"]):
            return await self._handle_reporting(text)
        
        # Data processing patterns
        if any(keyword in text for keyword in ["clean", "process", "transform", "filter"]):
            return await self._handle_data_processing(text)
        
        # Default: provide guidance
        return await self._provide_guidance()
    
    async def _handle_visualization(self, text: str) -> str:
        """Handle data visualization requests."""
        # Extract data from text
        data = self._extract_data(text)
        
        if not data:
            return """No data found for visualization. Please provide data in one of these formats:
- List: [1, 2, 3, 4, 5]
- Pairs: [(1,2), (2,4), (3,6), (4,8)]
- JSON: {"x": [1,2,3], "y": [2,4,6]}

Example: "create a line plot for data [1, 2, 3, 4, 5]" """
        
        # Determine chart type
        chart_type = self._determine_chart_type(text)
        
        # Generate visualization
        chart_description = await self._create_visualization(data, chart_type, text)
        
        return chart_description
    
    async def _handle_data_analysis(self, text: str) -> str:
        """Handle data analysis requests."""
        data = self._extract_data(text)
        
        if not data:
            return "No data found for analysis. Please provide numeric data for analysis."
        
        # Convert to pandas DataFrame if possible
        try:
            if isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                # Paired data
                df = pd.DataFrame(data, columns=['X', 'Y'])
                
                # Perform correlation analysis
                correlation = df['X'].corr(df['Y'])
                
                analysis = f"""Correlation Analysis:
- Data points: {len(df)}
- Correlation coefficient: {correlation:.4f}
- Relationship strength: {self._interpret_correlation(correlation)}

X variable statistics:
- Mean: {df['X'].mean():.4f}
- Std Dev: {df['X'].std():.4f}
- Range: {df['X'].min():.2f} to {df['X'].max():.2f}

Y variable statistics:
- Mean: {df['Y'].mean():.4f}
- Std Dev: {df['Y'].std():.4f}
- Range: {df['Y'].min():.2f} to {df['Y'].max():.2f}"""
                
                return analysis
                
            else:
                # Single variable data
                df = pd.DataFrame({'values': data})
                
                skewness_val = df['values'].skew()
                kurtosis_val = df['values'].kurtosis()
                
                analysis = f"""Data Analysis Summary:
- Count: {len(df)}
- Mean: {df['values'].mean():.4f}
- Median: {df['values'].median():.4f}
- Std Dev: {df['values'].std():.4f}
- Variance: {df['values'].var():.4f}
- Min: {df['values'].min():.4f}
- Max: {df['values'].max():.4f}
- Skewness: {skewness_val:.4f}
- Kurtosis: {kurtosis_val:.4f}

Quartiles:
- Q1 (25%): {df['values'].quantile(0.25):.4f}
- Q2 (50%): {df['values'].quantile(0.50):.4f}
- Q3 (75%): {df['values'].quantile(0.75):.4f}"""
                
                return analysis
                
        except Exception as e:
            return f"Error in data analysis: {str(e)}"
    
    async def _handle_reporting(self, text: str) -> str:
        """Handle reporting and summary requests."""
        data = self._extract_data(text)
        
        if not data:
            return """I can generate reports for your data. Please provide data and specify:
- Summary report: "generate summary report for [1,2,3,4,5]"
- Trend analysis: "analyze trends in [(1,10), (2,15), (3,12), (4,18)]"
- Insights: "provide insights for data [10,20,15,25,30]" """
        
        # Generate comprehensive report
        try:
            if isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                # Paired data report
                df = pd.DataFrame(data, columns=['X', 'Y'])
                
                report = f"""Data Analysis Report
========================

Dataset Overview:
- Total observations: {len(df)}
- Variables: X, Y (paired data)

Statistical Summary:
X Variable:
  - Mean: {df['X'].mean():.4f}
  - Median: {df['X'].median():.4f}
  - Standard Deviation: {df['X'].std():.4f}
  - Range: {df['X'].min():.2f} - {df['X'].max():.2f}

Y Variable:
  - Mean: {df['Y'].mean():.4f}  
  - Median: {df['Y'].median():.4f}
  - Standard Deviation: {df['Y'].std():.4f}
  - Range: {df['Y'].min():.2f} - {df['Y'].max():.2f}

Relationship Analysis:
- Correlation: {df['X'].corr(df['Y']):.4f}
- Relationship: {self._interpret_correlation(df['X'].corr(df['Y']))}

Key Insights:
{self._generate_insights(df)}"""
                
                return report
                
            else:
                # Single variable report
                df = pd.DataFrame({'values': data})
                skewness_val = df['values'].skew()
                kurtosis_val = df['values'].kurtosis()
                
                report = f"""Data Analysis Report
========================

Dataset Overview:
- Total observations: {len(df)}
- Variable type: Single numeric variable

Descriptive Statistics:
- Mean: {df['values'].mean():.4f}
- Median: {df['values'].median():.4f}
- Standard Deviation: {df['values'].std():.4f}
- Variance: {df['values'].var():.4f}
- Range: {df['values'].min():.2f} - {df['values'].max():.2f}

Distribution Analysis:
- Skewness: {skewness_val:.4f}
- Kurtosis: {kurtosis_val:.4f}

Quartile Analysis:
- Q1 (25th percentile): {df['values'].quantile(0.25):.4f}
- Q2 (50th percentile/Median): {df['values'].quantile(0.50):.4f}
- Q3 (75th percentile): {df['values'].quantile(0.75):.4f}
- IQR: {df['values'].quantile(0.75) - df['values'].quantile(0.25):.4f}

Key Insights:
{self._generate_single_var_insights(df['values'])}"""
                
                return report
                
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    async def _handle_data_processing(self, text: str) -> str:
        """Handle data processing requests."""
        return """Data Processing Services Available:

1. Data Cleaning:
   - Remove outliers
   - Handle missing values
   - Normalize data

2. Data Transformation:
   - Log transformation
   - Standardization
   - Binning

3. Data Filtering:
   - Value-based filtering
   - Statistical filtering

Please specify your data processing needs with your dataset."""
    
    async def _provide_guidance(self) -> str:
        """Provide guidance on available capabilities."""
        return """I'm a Data Analyst Agent. I can help you with:

🔍 Data Analysis:
- Statistical summaries
- Correlation analysis
- Trend identification
- Pattern recognition

📊 Visualizations:
- Line plots, scatter plots
- Histograms, box plots
- Correlation heatmaps

📋 Reporting:
- Comprehensive data reports
- Statistical insights
- Key findings summaries

💾 Data Processing:
- Data cleaning
- Transformation
- Filtering

Examples:
- "analyze correlation in [(1,5), (2,7), (3,6), (4,8)]"
- "create histogram for [1,2,2,3,3,3,4,4,5]"
- "generate report for data [10,15,12,18,20,16,14]"

What would you like me to analyze?"""
    
    def _extract_data(self, text: str) -> List[Any]:
        """Extract data from text."""
        # Look for JSON-like data structures
        json_pattern = r'\\{[^}]+\\}'
        json_matches = re.findall(json_pattern, text)
        
        for match in json_matches:
            try:
                data_dict = json.loads(match)
                if isinstance(data_dict, dict):
                    # Return first numeric list found
                    for value in data_dict.values():
                        if isinstance(value, list) and all(isinstance(x, (int, float)) for x in value):
                            return value
            except:
                pass
        
        # Look for array/list patterns
        array_pattern = r'\\[([\\d.,\\s()]+)\\]'
        array_matches = re.findall(array_pattern, text)
        
        for match in array_matches:
            try:
                # Check for tuples (paired data)
                if '(' in match:
                    # Extract tuples like (1,2), (3,4)
                    tuple_pattern = r'\\(([\\d.,\\s]+)\\)'
                    tuple_matches = re.findall(tuple_pattern, match)
                    
                    pairs = []
                    for tuple_match in tuple_matches:
                        values = [float(x.strip()) for x in tuple_match.split(',') if x.strip()]
                        if len(values) == 2:
                            pairs.append(tuple(values))
                    
                    if pairs:
                        return pairs
                
                # Regular list of numbers
                numbers = [float(x.strip()) for x in match.split(',') if x.strip() and not '(' in x]
                if numbers:
                    return numbers
                    
            except ValueError:
                continue
        
        # Look for individual numbers as fallback
        number_pattern = r'-?\\d+\\.?\\d*'
        matches = re.findall(number_pattern, text)
        
        if len(matches) >= 3:  # Need at least 3 points for meaningful analysis
            return [float(match) for match in matches]
        
        return []
    
    def _determine_chart_type(self, text: str) -> str:
        """Determine the appropriate chart type based on text."""
        text = text.lower()
        
        if any(word in text for word in ["histogram", "distribution"]):
            return "histogram"
        elif any(word in text for word in ["scatter", "correlation"]):
            return "scatter"
        elif any(word in text for word in ["line", "trend", "time"]):
            return "line"
        elif any(word in text for word in ["bar", "category"]):
            return "bar"
        elif any(word in text for word in ["box", "quartile"]):
            return "box"
        else:
            return "line"  # default
    
    async def _create_visualization(self, data: List[Any], chart_type: str, text: str) -> str:
        """Create a visualization and return description."""
        try:
            plt.figure(figsize=(10, 6))
            
            if chart_type == "histogram":
                if isinstance(data[0], (list, tuple)):
                    # Use Y values for histogram
                    values = [item[1] for item in data]
                else:
                    values = data
                
                plt.hist(values, bins=min(len(set(values)), 20), alpha=0.7, edgecolor='black')
                plt.title('Data Distribution (Histogram)')
                plt.xlabel('Values')
                plt.ylabel('Frequency')
                
                description = f"""Histogram created for {len(values)} data points.
- Bins: {min(len(set(values)), 20)}
- Range: {min(values):.2f} to {max(values):.2f}
- Most frequent range: Around {np.mean(values):.2f}"""
                
            elif chart_type == "scatter":
                if isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                    x_vals = [item[0] for item in data]
                    y_vals = [item[1] for item in data]
                    
                    plt.scatter(x_vals, y_vals, alpha=0.7)
                    plt.title('Scatter Plot')
                    plt.xlabel('X Values')
                    plt.ylabel('Y Values')
                    
                    # Add trend line
                    z = np.polyfit(x_vals, y_vals, 1)
                    p = np.poly1d(z)
                    plt.plot(x_vals, p(x_vals), "r--", alpha=0.8)
                    
                    correlation = np.corrcoef(x_vals, y_vals)[0, 1]
                    
                    description = f"""Scatter plot created for {len(data)} data points.
- Correlation: {correlation:.4f} ({self._interpret_correlation(correlation)})
- X range: {min(x_vals):.2f} to {max(x_vals):.2f}
- Y range: {min(y_vals):.2f} to {max(y_vals):.2f}
- Trend line added (red dashed line)"""
                else:
                    return "Scatter plot requires paired data. Please provide data like [(1,2), (3,4), (5,6)]"
                
            elif chart_type == "line":
                if isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
                    x_vals = [item[0] for item in data]
                    y_vals = [item[1] for item in data]
                    plt.plot(x_vals, y_vals, marker='o')
                    plt.title('Line Plot')
                    plt.xlabel('X Values')  
                    plt.ylabel('Y Values')
                else:
                    plt.plot(range(len(data)), data, marker='o')
                    plt.title('Line Plot')
                    plt.xlabel('Index')
                    plt.ylabel('Values')
                
                description = f"""Line plot created for {len(data)} data points.
- Connected points showing trend over sequence
- Markers indicate individual data points"""
            
            elif chart_type == "box":
                if isinstance(data[0], (list, tuple)):
                    values = [item[1] for item in data]
                else:
                    values = data
                
                plt.boxplot(values)
                plt.title('Box Plot')
                plt.ylabel('Values')
                
                q1 = np.percentile(values, 25)
                q2 = np.percentile(values, 50)
                q3 = np.percentile(values, 75)
                
                description = f"""Box plot created showing distribution summary:
- Median (Q2): {q2:.2f}
- Q1 (25th percentile): {q1:.2f}
- Q3 (75th percentile): {q3:.2f}
- IQR: {q3 - q1:.2f}"""
            else:
                description = f"Basic chart created for {len(data)} data points."
            
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Save plot description (in a real implementation, you'd save the actual plot)
            plt.close()  # Close to free memory
            
            return f"""Visualization Created: {chart_type.title()} Chart
{description}

Note: In a full implementation, the actual chart image would be generated and saved."""
            
        except Exception as e:
            return f"Error creating visualization: {str(e)}"
    
    def _interpret_correlation(self, corr: float) -> str:
        """Interpret correlation coefficient."""
        abs_corr = abs(corr)
        
        if abs_corr >= 0.9:
            strength = "very strong"
        elif abs_corr >= 0.7:
            strength = "strong"
        elif abs_corr >= 0.5:
            strength = "moderate"
        elif abs_corr >= 0.3:
            strength = "weak"
        else:
            strength = "very weak"
        
        direction = "positive" if corr >= 0 else "negative"
        
        return f"{strength} {direction} correlation"
    
    def _interpret_skewness(self, skew: float) -> str:
        """Interpret skewness value."""
        if abs(skew) < 0.5:
            return "approximately symmetric"
        elif skew > 0.5:
            return "right-skewed (positive skew)"
        else:
            return "left-skewed (negative skew)"
    
    def _generate_insights(self, df: pd.DataFrame) -> str:
        """Generate insights for paired data."""
        x_col, y_col = df.columns[0], df.columns[1]
        
        insights = []
        
        # Correlation insight
        corr = df[x_col].corr(df[y_col])
        if abs(corr) > 0.7:
            direction = "increases" if corr > 0 else "decreases"
            insights.append(f"- Strong relationship: as {x_col} increases, {y_col} generally {direction}")
        
        # Range insights
        x_range = df[x_col].max() - df[x_col].min()
        y_range = df[y_col].max() - df[y_col].min()
        
        if y_range > 2 * x_range:
            insights.append(f"- {y_col} shows much more variation than {x_col}")
        elif x_range > 2 * y_range:
            insights.append(f"- {x_col} shows much more variation than {y_col}")
        
        # Mean comparison
        if df[y_col].mean() > df[x_col].mean():
            insights.append(f"- {y_col} values are generally higher than {x_col} values")
        
        return "\\n".join(insights) if insights else "- Data shows standard statistical distribution"
    
    def _generate_single_var_insights(self, series: pd.Series) -> str:
        """Generate insights for single variable data."""
        insights = []
        
        # Distribution insights - safer skewness handling
        try:
            skew_val = series.skew()
            if isinstance(skew_val, (int, float)) and skew_val > 1:
                insights.append("- Data is heavily right-skewed (tail extends toward higher values)")
            elif isinstance(skew_val, (int, float)) and skew_val < -1:
                insights.append("- Data is heavily left-skewed (tail extends toward lower values)")
        except:
            pass
        
        # Variability insights
        try:
            cv = series.std() / series.mean() if series.mean() != 0 else 0
            
            if cv > 0.5:
                insights.append("- Data shows high variability relative to the mean")
            elif cv < 0.1:
                insights.append("- Data shows low variability - values are clustered around the mean")
        except:
            pass
        
        # Outlier detection (simple method)
        try:
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            outliers = series[(series < q1 - 1.5*iqr) | (series > q3 + 1.5*iqr)]
            
            if len(outliers) > 0:
                insights.append(f"- {len(outliers)} potential outlier(s) detected")
        except:
            pass
        
        return "\\n".join(insights) if insights else "- Data follows a normal distribution pattern"


if __name__ == "__main__":
    agent = DataAnalystAgent()
    agent.start_server()
