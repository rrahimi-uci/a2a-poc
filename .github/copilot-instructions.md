<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# A2A Multi-Agent Communication Project

This project implements a simplified version of the Agent-to-Agent (A2A) protocol for inter-agent communication. The system features two specialized agents that can communicate to solve complex problems collaboratively.

## Project Structure

- `common/`: Core A2A protocol implementation and base agent classes
- `agents/`: Specialized agent implementations (Math Agent, Data Analyst Agent)
- `examples/`: Demo orchestrator showing agent collaboration
- Individual startup scripts for each agent

## Key Components

### Math Agent (`agents/math_agent.py`)
- Handles mathematical computations, statistical analysis
- Capabilities: arithmetic, statistics, linear algebra, probability
- Runs on port 8001

### Data Analyst Agent (`agents/data_analyst_agent.py`) 
- Handles data visualization, analysis, and reporting
- Capabilities: plotting, correlation analysis, trend analysis
- Runs on port 8002

### Orchestrator (`examples/orchestrator.py`)
- Coordinates between agents to solve complex problems
- Determines which agents to use based on problem analysis
- Combines results from multiple agents

## A2A Protocol Features

- JSON-RPC 2.0 based communication
- Agent Cards for capability discovery
- Task-based interaction model
- Support for text messages and structured data

## Usage Patterns

When working with this codebase:
1. Agents communicate via HTTP using JSON-RPC 2.0 protocol
2. Each agent exposes capabilities through Agent Cards
3. Use the orchestrator for multi-agent problem solving
4. Follow the A2A protocol specifications for message formats
5. Handle async operations properly for agent communication

## Development Guidelines

- Follow the A2A protocol message formats strictly
- Use proper async/await patterns for agent communication  
- Handle errors gracefully in agent interactions
- Implement proper logging for debugging agent communications
- Use type hints for better code clarity
