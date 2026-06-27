# A2A-AutoGen Hybrid Integration

This directory contains examples demonstrating interoperability between our custom A2A agent system and Microsoft's AutoGen framework.

## 🤝 Integration Overview

### What This Demonstrates
- **Cross-framework communication**: A2A agents working with AutoGen agents
- **Protocol translation**: Converting between different agent communication standards
- **Collaborative problem solving**: Combining specialized capabilities from different platforms
- **Best of both worlds**: Custom A2A precision + AutoGen's LLM-powered flexibility

### Architecture Pattern
```
┌─────────────────┐    A2A Protocol    ┌─────────────────┐
│   A2A Math      │◄─────────────────►│   Hybrid        │
│   Agent         │   JSON-RPC 2.0     │   Orchestrator  │
│   (Port 8001)   │                    │                 │
└─────────────────┘                    │                 │
                                       │                 │
┌─────────────────┐   AutoGen API      │                 │
│   AutoGen       │◄─────────────────►│                 │
│   Code Agent    │   Conversational   │                 │
│   (LLM-powered) │                    │                 │
└─────────────────┘                    └─────────────────┘
```

## 📁 Files in This Integration

### Core Examples
- **`simple_hybrid_demo.py`** - Basic working example (no AutoGen installation required)
- **`hybrid_autogen_a2a.py`** - Full AutoGen integration with LLM capabilities
- **`setup_autogen.py`** - Installation and setup script for AutoGen

### Supporting Files
- **`hybrid_config.json`** - Configuration for hybrid systems (created by setup)
- **`README_HYBRID.md`** - This documentation file

## 🚀 Quick Start

### Option 1: Simple Demo (No Installation Required)
```bash
# Start A2A Math Agent
python scripts/start_math_agent.py

# Run simple hybrid demo (uses mock AutoGen)
python examples/simple_hybrid_demo.py
```

### Option 2: Full AutoGen Integration
```bash
# Setup AutoGen and dependencies
python examples/setup_autogen.py

# Set OpenAI API key (required for AutoGen LLM features)
export OPENAI_API_KEY="your-openai-api-key"

# Start A2A Math Agent
python scripts/start_math_agent.py

# Run full hybrid demo
python examples/hybrid_autogen_a2a.py
```

### Option 3: VS Code Integration
1. Press `Ctrl/Cmd + Shift + P`
2. Type "Tasks: Run Task"
3. Select:
   - "Setup AutoGen Integration" (first time only)
   - "Run Simple Hybrid Demo"

## 🔧 How It Works

### 1. Problem Analysis
The hybrid orchestrator analyzes incoming problems to determine which agents are needed:
- **Mathematical computation** → A2A Math Agent
- **Code generation** → AutoGen Code Agent
- **Complex problems** → Both agents in sequence

### 2. Agent Coordination
```python
# A2A Math Agent (Custom Protocol)
math_result = await a2a_client.send_message(math_agent_url, message)

# AutoGen Agent (Conversational AI)
code_result = await autogen_agent.generate_code(request)

# Combine results
final_solution = combine_results(math_result, code_result)
```

### 3. Protocol Translation
The orchestrator handles translation between different agent protocols:
- **A2A Protocol**: JSON-RPC 2.0 messages
- **AutoGen**: Conversational chat format
- **Result Integration**: Unified response format

## 🎯 Example Workflows

### Workflow 1: Statistical Analysis + Code Generation
```
User Request: "Analyze normal distribution μ=50, σ=10 and create visualization code"

Step 1: A2A Math Agent
├── Input: Statistical analysis request
├── Process: Calculate distribution properties
└── Output: Mathematical results

Step 2: AutoGen Code Agent  
├── Input: Math results + code generation request
├── Process: Generate Python visualization code
└── Output: Complete implementation

Step 3: Integration
├── Combine mathematical analysis with implementation
└── Return comprehensive solution
```

### Workflow 2: Data Correlation + Implementation
```
User Request: "Find correlation in [(1,5), (2,7), (3,6)] and create analysis script"

A2A Agent: Calculates correlation coefficient, regression parameters
AutoGen Agent: Generates scatter plot, regression line, residuals code
Result: Mathematical analysis + complete visualization implementation
```

## 🛠️ Extending the Integration

### Adding New Agent Types
```python
class NewFrameworkAgent:
    """Integrate agents from other frameworks"""
    
    async def communicate_with_agent(self, request):
        # Implement protocol translation
        # Handle framework-specific communication
        # Return standardized response
        pass

# Add to orchestrator
orchestrator.add_agent("new_framework", NewFrameworkAgent())
```

### Custom Protocol Bridges
```python
class ProtocolBridge:
    """Bridge between different agent protocols"""
    
    def a2a_to_autogen(self, a2a_message):
        # Convert A2A message to AutoGen format
        pass
        
    def autogen_to_a2a(self, autogen_response):
        # Convert AutoGen response to A2A format
        pass
```

## 🔍 Troubleshooting

### Common Issues

**AutoGen Import Error**
```bash
# Solution: Install AutoGen
pip install pyautogen openai
```

**OpenAI API Key Missing**
```bash
# Solution: Set environment variable
export OPENAI_API_KEY="your-key-here"
```

**A2A Agent Connection Failed**
```bash
# Solution: Start Math Agent first
python scripts/start_math_agent.py
```

**Port Conflicts**
```bash
# Solution: Check if ports 8001-8002 are available
lsof -i :8001
lsof -i :8002
```

## 📊 Performance Considerations

### Latency Factors
- **A2A Communication**: ~10-50ms (local network)
- **AutoGen LLM Calls**: ~1-5 seconds (API dependent)
- **Protocol Translation**: ~1-5ms (negligible)

### Optimization Tips
1. **Cache LLM Responses**: Store common code patterns
2. **Parallel Processing**: Run independent agents concurrently
3. **Request Batching**: Combine multiple operations
4. **Fallback Modes**: Handle API failures gracefully

## 🌟 Benefits of Hybrid Approach

### Advantages
✅ **Specialized Precision**: A2A agents for exact mathematical computations  
✅ **LLM Flexibility**: AutoGen for creative code generation  
✅ **Framework Agnostic**: Works with multiple agent platforms  
✅ **Scalable Architecture**: Easy to add new agent types  
✅ **Best of Both Worlds**: Custom protocols + AI capabilities  

### Use Cases
- **Research & Development**: Prototype multi-agent systems
- **Educational**: Learn different agent architectures
- **Production**: Hybrid systems for complex problem solving
- **Integration**: Connect existing agent systems

## 📚 References

- [A2A Protocol Documentation](../docs/technical-architecture.html)
- [Microsoft AutoGen Documentation](https://microsoft.github.io/autogen/)
- [Multi-Agent Systems Patterns](https://en.wikipedia.org/wiki/Multi-agent_system)

---

**🎉 Happy Hybrid Agent Building!**

This integration demonstrates the power of combining different agent frameworks to create more capable and flexible multi-agent systems.
