<div align="center">

# 🤖 A2A Protocol — Multi-Agent Communication

### Specialized AI agents that collaborate to solve problems, over a clean JSON-RPC 2.0 **Agent-to-Agent (A2A)** protocol.

[![CI](https://github.com/rrahimi-uci/a2a-poc/actions/workflows/ci.yml/badge.svg)](https://github.com/rrahimi-uci/a2a-poc/actions/workflows/ci.yml)
[![Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://rrahimi-uci.github.io/a2a-poc/)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-147%20passing-brightgreen.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen.svg)](tests/)
[![Code style](https://img.shields.io/badge/protocol-JSON--RPC%202.0-orange.svg)](https://www.jsonrpc.org/specification)

**[📖 Documentation & Live Site](https://rrahimi-uci.github.io/a2a-poc/)** ·
**[🏗️ Architecture](ARCHITECTURE.md)** ·
**[🚀 Quick Start](#-quick-start)** ·
**[🧪 Tests](#-testing)**

</div>

---

## ✨ What is this?

This project is a small, **readable reference implementation** of the
**Agent-to-Agent (A2A) protocol** — a pattern where independent, specialized
AI agents expose their capabilities and **talk to each other over HTTP using
JSON-RPC 2.0**. Instead of one monolithic model doing everything, work is
split across focused agents that a coordinator stitches together.

Two agents ship out of the box:

| Agent | Port | Specializes in |
|-------|:----:|----------------|
| 🧮 **Math Agent** | `8001` | Arithmetic, statistics, linear algebra, probability distributions |
| 📊 **Data Analyst Agent** | `8002` | Correlation analysis, distributions, visualizations, reports |

A **Multi-Agent Orchestrator** analyzes an incoming problem, decides which
agent(s) it needs, routes the work, and combines the results into a single
answer.

> 💡 **Why it matters:** the same discovery + messaging pattern lets agents
> built on *different frameworks* interoperate. The included
> [hybrid demo](examples/) shows an A2A agent collaborating with a
> Microsoft **AutoGen**-style agent.

---

## 🏗️ Architecture

```
                         ┌──────────────────────────┐
                         │   Multi-Agent             │
            ┌───────────►│   Orchestrator            │◄───────────┐
            │            │   (analyze · route ·      │            │
            │            │    combine)               │            │
            │            └──────────────────────────┘            │
            │ JSON-RPC 2.0                          JSON-RPC 2.0  │
            ▼                                                     ▼
  ┌────────────────────┐                          ┌────────────────────┐
  │   🧮 Math Agent     │   A2A Protocol (HTTP)    │ 📊 Data Analyst     │
  │   :8001             │◄────────────────────────►│   Agent  :8002      │
  │   FastAPI service   │                          │   FastAPI service   │
  └────────────────────┘                          └────────────────────┘
```

Every agent publishes an **Agent Card** at `GET /` (and the conventional
`GET /.well-known/agent.json`) describing its identity, capabilities and
connection info — so agents can discover one another at runtime.

➡️ **Full design, sequence diagrams, and extension guide:
[ARCHITECTURE.md](ARCHITECTURE.md)**

---

## 🚀 Quick Start

### Prerequisites
- Python **3.9+**

### 1. Install

```bash
git clone https://github.com/rrahimi-uci/a2a-poc.git
cd a2a-poc

python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt    # or: pip install -e ".[dev]"
```

### 2. Run the whole system with one command

```bash
python scripts/launch_system.py
```

This boots both agents, waits until they're healthy, then runs the
orchestrator demo. That's the fastest way to see agents collaborating.

### 3. …or run the pieces separately

```bash
# Terminal 1
python scripts/start_math_agent.py        # → http://localhost:8001

# Terminal 2
python scripts/start_data_agent.py        # → http://localhost:8002

# Terminal 3
python scripts/run_demo.py                # orchestrator demo
```

---

## 📋 Example problems

The orchestrator can handle prompts like:

```text
"Calculate the mean and standard deviation of [12, 15, 18, 20, 22, 25, 28, 30] and create a histogram"
"Find the correlation between [(1,5), (2,7), (3,6), (4,8), (5,10)] and visualize it"
"Analyze the normal distribution with mean 100 and standard deviation 15"
"Generate a summary report for the sales data: [450, 520, 380, 610, 720, 890]"
```

### Talk to an agent directly (raw JSON-RPC)

```bash
# Discover capabilities
curl http://localhost:8001/

# Send a message
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "1",
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": { "role": "user", "parts": [{ "kind": "text", "text": "calculate mean of [1,2,3,4,5]" }] }
    }
  }'
```

---

## 🔌 The A2A Protocol

- **Transport:** HTTP · **Envelope:** [JSON-RPC 2.0](https://www.jsonrpc.org/specification)
- **Methods:** `message/send`, `task/get`
- **Discovery:** Agent Cards at `/` and `/.well-known/agent.json`
- **Model:** task-based, async-friendly, with structured error codes

```json
{
  "id": "unique-request-id",
  "jsonrpc": "2.0",
  "method": "message/send",
  "params": {
    "message": {
      "role": "user",
      "parts": [{ "kind": "text", "text": "Calculate mean of [1,2,3,4,5]" }]
    }
  }
}
```

---

## 📁 Project structure

```
a2a-poc/
├── common/                     # Core protocol + base agent
│   ├── a2a_protocol.py         #   Pydantic models (Message, Task, AgentCard, …)
│   └── base_agent.py           #   FastAPI BaseAgent + A2AClient
├── agents/                     # Specialized agents
│   ├── math_agent.py
│   └── data_analyst_agent.py
├── examples/                   # Orchestrator + AutoGen hybrid demos
│   ├── orchestrator.py
│   ├── simple_hybrid_demo.py
│   └── hybrid_autogen_a2a.py
├── scripts/                    # Runnable entry points
│   ├── start_math_agent.py
│   ├── start_data_agent.py
│   ├── run_demo.py
│   ├── launch_system.py
│   └── smoke_test.py           # live-server HTTP smoke test
├── tests/                      # Fast in-process pytest suite
├── docs/                       # GitHub Pages site (landing + architecture)
├── config/                     # Settings & defaults
├── ARCHITECTURE.md
├── pyproject.toml
└── requirements.txt
```

---

## 🧪 Testing

The suite runs **fully in-process** (FastAPI `TestClient`) — no servers to
launch, fast and deterministic. **147 tests, ~93% coverage:**

```bash
pip install -e ".[dev]"   # or: pip install -r requirements-dev.txt
pytest                                   # run everything (~0.6s)
pytest --cov --cov-report=term-missing   # coverage report (gate: 90%)
```

Generate an [Allure](https://allurereport.org/) report (tests are grouped by
feature/story/title):

```bash
pytest --alluredir=allure-results
allure serve allure-results              # requires the Allure CLI
```

Want a real over-the-wire check? Start the agents, then:

```bash
python scripts/smoke_test.py
```

---

## 🛠️ Build your own agent

```python
from common.base_agent import BaseAgent
from common.a2a_protocol import Task, TaskStatus, TaskState, Message, MessagePart, MessageRole, MessageSendParams

class EchoAgent(BaseAgent):
    def __init__(self, port: int = 8003):
        super().__init__(
            agent_id="echo-agent-001",
            name="Echo Agent",
            description="Repeats whatever it is told.",
            port=port,
            capabilities=["echo"],
        )

    async def process_message(self, params: MessageSendParams) -> Task:
        text = " ".join(p.text for p in params.message.parts)
        reply = Message(role=MessageRole.AGENT, parts=[MessagePart(text=f"You said: {text}")])
        return Task(messages=[params.message, reply],
                    status=TaskStatus(state=TaskState.COMPLETED, message=reply))

if __name__ == "__main__":
    EchoAgent().start_server()
```

See [ARCHITECTURE.md](ARCHITECTURE.md#extending-the-system) for the full guide.

---

## 🤝 Hybrid / cross-framework demo

`examples/simple_hybrid_demo.py` runs without any extra setup and shows an A2A
agent cooperating with a mock AutoGen code-generation agent. For the real,
LLM-powered version:

```bash
pip install -e ".[autogen]"
export OPENAI_API_KEY="sk-..."
python examples/hybrid_autogen_a2a.py
```

---

## 📚 Learn more

- 🌐 **[Project site & docs](https://rrahimi-uci.github.io/a2a-poc/)**
- 🍳 **[Cookbook — recipes for using it as a library](COOKBOOK.md)**
- 🏗️ **[Architecture deep-dive](ARCHITECTURE.md)**
- 🔗 [A2A Protocol project](https://a2a-protocol.org/) · [JSON-RPC 2.0 spec](https://www.jsonrpc.org/specification)

## 🤲 Contributing

Issues and pull requests are welcome! Fork → branch → add tests → open a PR.

## 📄 License

Released under the [MIT License](LICENSE).

---

<div align="center">

**Built to make multi-agent collaboration easy to understand.** 🤖✨

</div>
