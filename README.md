# A2A Multi-Agent Communication System

A Python implementation demonstrating agent-to-agent (A2A) communication where two specialized agents collaborate to solve complex problems. This project showcases how AI agents can work together using a standardized communication protocol.

## 🤖 Agents

### Math Agent
**Port:** 8001  
**Capabilities:**
- Mathematical computations (arithmetic, algebra)
- Statistical analysis (mean, std dev, correlation)
- Probability distributions
- Linear algebra operations

### Data Analyst Agent  
**Port:** 8002  
**Capabilities:**
- Data visualization (plots, charts, histograms)
- Statistical reporting and insights
- Correlation analysis
- Trend identification

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment (recommended)

### Installation

1. **Clone and set up the environment:**
```bash
cd A2Acommunication
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
pip install -r requirements.txt
```

2. **Start the agents (in separate terminals):**

**Terminal 1 - Math Agent:**
```bash
source venv/bin/activate
python scripts/start_math_agent.py
```

**Terminal 2 - Data Analyst Agent:**
```bash
source venv/bin/activate  
python scripts/start_data_agent.py
```

3. **Run the demo (in a third terminal):**
```bash
source venv/bin/activate
python scripts/run_demo.py
```

**Alternative - Launch Complete System:**
```bash
source venv/bin/activate
python scripts/launch_system.py
```

## 📋 Example Problems

The system can solve problems like:

1. **Statistical Analysis + Visualization:**
   ```
   "Calculate the mean and standard deviation of [12, 15, 18, 20, 22, 25, 28, 30] and create a histogram"
   ```

2. **Correlation Analysis:**
   ```
   "Find the correlation between [(1,5), (2,7), (3,6), (4,8), (5,10)] and visualize the relationship"
   ```

3. **Distribution Analysis:**
   ```
   "Analyze the statistical properties of normal distribution with mean 100 and std dev 15"
   ```

## 🏗️ Architecture

```
┌─────────────────┐    A2A Protocol    ┌──────────────────┐
│   Math Agent    │◄─────────────────►│ Data Analyst     │
│   (Port 8001)   │   JSON-RPC 2.0    │   Agent          │
│                 │                    │ (Port 8002)      │
└─────────────────┘                    └──────────────────┘
         ▲                                        ▲
         │                                        │
         │            ┌─────────────────┐        │
         └────────────│  Orchestrator   │────────┘
                      │  (Coordinator)  │
                      └─────────────────┘
```

### Communication Flow

1. **Problem Analysis:** Orchestrator analyzes the problem to determine which agents are needed
2. **Agent Selection:** Routes requests to Math Agent, Data Analyst Agent, or both
3. **Collaborative Processing:** Agents communicate via A2A protocol to share results
4. **Result Integration:** Orchestrator combines outputs into comprehensive solutions

## 🔧 A2A Protocol Features

- **JSON-RPC 2.0** based communication
- **Agent Cards** for capability discovery
- **Task-based** interaction model  
- **Async messaging** support
- **Error handling** and status reporting

### Message Format Example
```json
{
  "id": "unique-request-id",
  "jsonrpc": "2.0", 
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{"kind": "text", "text": "Calculate mean of [1,2,3,4,5]"}]
    }
  }
}
```

## 📁 Project Structure

```
A2Acommunication/
├── agents/                    # Agent implementations
│   ├── math_agent.py         # Mathematical computation agent
│   └── data_analyst_agent.py # Data analysis & visualization agent
├── common/                    # A2A protocol core
│   ├── a2a_protocol.py       # Protocol definitions
│   └── base_agent.py         # Base agent class
├── config/                    # Configuration files
│   ├── __init__.py           # Default configuration
│   └── settings.ini          # System settings
├── docs/                      # Documentation
│   └── technical-architecture.html # Technical architecture docs
├── examples/                  # Demo and examples
│   └── orchestrator.py       # Multi-agent coordinator
├── scripts/                   # Startup and management scripts
│   ├── start_math_agent.py   # Math agent startup script
│   ├── start_data_agent.py   # Data analyst startup script
│   ├── launch_system.py      # Complete system launcher
│   └── run_demo.py           # Demo runner
├── tests/                     # Test files
│   └── test_system.py        # System integration tests
├── .vscode/                   # VS Code configuration
│   └── tasks.json            # Development tasks
├── requirements.txt           # Dependencies
└── README.md                 # This file
```

## 🛠️ Development

### Adding New Agents

1. **Inherit from BaseAgent:**
```python
from common.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self, port: int):
        super().__init__(
            agent_id="my-agent-001",
            name="My Agent", 
            description="My custom agent",
            port=port,
            capabilities=["my_capability"]
        )
```

2. **Implement process_message:**
```python
async def process_message(self, params: MessageSendParams) -> Task:
    # Process the incoming message
    # Return a Task with results
```

### Testing Individual Agents

You can test agents directly via HTTP:

```bash
# Get agent card
curl http://localhost:8001/

# Send a message
curl -X POST http://localhost:8001/ \\
  -H "Content-Type: application/json" \\
  -d '{
    "id": "test-1",
    "jsonrpc": "2.0",
    "method": "message/send", 
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "text", "text": "Calculate 2 + 2"}]
      }
    }
  }'
```

## 🎯 Use Cases

- **Educational:** Learn about multi-agent systems and A2A protocol
- **Research:** Experiment with agent collaboration patterns
- **Development:** Build more complex multi-agent applications
- **Integration:** Connect with other A2A-compatible agents

## � Testing

**Run system tests:**
```bash
source venv/bin/activate
python tests/test_system.py
```

**VS Code Integration:**
- Press `Ctrl/Cmd + Shift + P`
- Type "Tasks: Run Task"
- Select from available tasks:
  - Launch Math Agent
  - Launch Data Analyst Agent
  - Launch Complete System
  - Run Demo
  - Test System

## �🔍 Troubleshooting

**Agents not starting:**
- Check if ports 8001/8002 are available
- Ensure virtual environment is activated
- Verify all dependencies are installed

**Communication errors:**
- Confirm both agents are running
- Check firewall settings
- Review agent logs for error details

**Demo not working:**
- Make sure agents start successfully first
- Check terminal output for specific error messages
- Verify network connectivity between agents

## 📚 Learn More

- [A2A Protocol Documentation](https://a2a-protocol.org/)
- [A2A GitHub Repository](https://github.com/a2aproject/A2A)
- [Agent Communication Patterns](https://en.wikipedia.org/wiki/Multi-agent_system)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable  
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes. Check the A2A protocol license for production use.

---

**Happy Agent Building! 🤖✨**
