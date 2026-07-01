# 🍳 A2A Protocol Cookbook

Practical, copy-pasteable recipes for using this project **as a library** — to
embed agents, talk to them over the A2A protocol, build your own agents, and
orchestrate several together.

Every recipe below is self-contained and was verified against the test suite's
Python environment.

> **Install first**
> ```bash
> pip install -e .            # from a checkout
> # or, once published:  pip install a2a-protocol-demo
> ```
> Importable packages: `common` (protocol + base agent), `agents` (Math & Data
> Analyst), `config` (defaults).

---

## Table of contents

1. [Call an agent in-process (no server)](#1-call-an-agent-in-process-no-server)
2. [Run an agent as an HTTP server](#2-run-an-agent-as-an-http-server)
3. [Talk to a running agent with `A2AClient`](#3-talk-to-a-running-agent-with-a2aclient)
4. [Discover an agent's capabilities (Agent Card)](#4-discover-an-agents-capabilities-agent-card)
5. [Build your own agent](#5-build-your-own-agent)
6. [Orchestrate multiple agents](#6-orchestrate-multiple-agents)
7. [Use the Math & Data agents directly](#7-use-the-math--data-agents-directly)
8. [Construct raw JSON-RPC requests](#8-construct-raw-json-rpc-requests)
9. [Cross-framework / hybrid agents](#9-cross-framework--hybrid-agents)
10. [Testing & Allure reports](#10-testing--allure-reports)

---

## 1. Call an agent in-process (no server)

The fastest way to use an agent is to instantiate it and call
`process_message` directly — no sockets, no ports.

```python
import asyncio
from agents.math_agent import MathAgent
from common.a2a_protocol import Message, MessagePart, MessageRole, MessageSendParams

agent = MathAgent()

params = MessageSendParams(
    message=Message(role=MessageRole.USER,
                    parts=[MessagePart(text="calculate mean of [10, 20, 30]")])
)
task = asyncio.run(agent.process_message(params))
print(task.status.state)                       # TaskState.COMPLETED
print(task.status.message.parts[0].text)        # Statistical Analysis Results...
```

---

## 2. Run an agent as an HTTP server

```python
from agents.math_agent import MathAgent

if __name__ == "__main__":
    MathAgent(port=8001).start_server()          # serves on http://0.0.0.0:8001
```

Or from the shell:

```bash
python scripts/start_math_agent.py     # :8001
python scripts/start_data_agent.py     # :8002
```

Endpoints exposed by every agent:

| Method & path | Purpose |
|---|---|
| `GET /` | Agent Card (capability discovery) |
| `GET /.well-known/agent.json` | A2A-standard discovery path |
| `GET /health` | Liveness probe |
| `POST /` | JSON-RPC 2.0 (`message/send`, `task/get`) |

---

## 3. Talk to a running agent with `A2AClient`

```python
import asyncio
from common.base_agent import A2AClient
from common.a2a_protocol import Message, MessagePart, MessageRole

async def main():
    client = A2AClient()
    msg = Message(role=MessageRole.USER,
                  parts=[MessagePart(text="calculate mean of [2, 4, 6]")])
    task = await client.send_message("http://localhost:8001", msg)
    print(task.status.message.parts[0].text)

asyncio.run(main())
```

`A2AClient` raises on transport errors and on JSON-RPC error responses, so wrap
calls in `try/except` for production use.

---

## 4. Discover an agent's capabilities (Agent Card)

```python
import asyncio
from common.base_agent import A2AClient

async def main():
    card = await A2AClient().get_agent_card("http://localhost:8001")
    print(card.name)              # "Math Agent"
    print(card.capabilities)      # ['arithmetic_operations', 'statistical_analysis', ...]
    print(card.connection["url"]) # "http://localhost:8001"

asyncio.run(main())
```

Or without a running server, straight off an agent object:

```python
from agents.math_agent import MathAgent
print(MathAgent().get_agent_card().model_dump(mode="json"))
```

---

## 5. Build your own agent

Subclass `BaseAgent` and implement the single async `process_message` method.
You inherit the HTTP surface, discovery, health check and JSON-RPC handling for
free.

```python
from common.base_agent import BaseAgent
from common.a2a_protocol import (
    Task, TaskStatus, TaskState, Message, MessagePart, MessageRole, MessageSendParams,
)

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
        return Task(
            messages=[params.message, reply],
            status=TaskStatus(state=TaskState.COMPLETED, message=reply),
        )

if __name__ == "__main__":
    EchoAgent().start_server()
```

**Tip:** store long-running tasks in `self.tasks[task.id] = task` so clients can
poll them later via the `task/get` method.

---

## 6. Orchestrate multiple agents

The `MultiAgentOrchestrator` inspects a problem, routes it to the Math and/or
Data Analyst agents, and combines their answers.

```python
import asyncio
from examples.orchestrator import MultiAgentOrchestrator

async def main():
    orch = MultiAgentOrchestrator(
        math_agent_url="http://localhost:8001",
        data_agent_url="http://localhost:8002",
    )
    result = await orch.solve_problem(
        "Calculate the mean of [12, 15, 18, 20] and create a histogram"
    )
    print(result["agents_used"])    # ['Math Agent', 'Data Analyst Agent']
    print(result["final_result"])

asyncio.run(main())
```

**Testing the orchestrator without sockets:** swap in a client that dispatches
to in-process agent objects (this is exactly what the test suite does):

```python
from agents.math_agent import MathAgent
from agents.data_analyst_agent import DataAnalystAgent
from common.a2a_protocol import MessageSendParams

class InProcessClient:
    def __init__(self, math_url, data_url):
        self._agents = {math_url: MathAgent(), data_url: DataAnalystAgent()}
    async def send_message(self, url, message, session_id=None):
        return await self._agents[url].process_message(MessageSendParams(message=message))

orch = MultiAgentOrchestrator()
orch.client = InProcessClient(orch.math_agent_url, orch.data_agent_url)
```

---

## 7. Use the Math & Data agents directly

Both agents expose their skills through natural-language prompts.

```python
import asyncio
from agents.math_agent import MathAgent
from agents.data_analyst_agent import DataAnalystAgent

math = MathAgent()
data = DataAnalystAgent()

print(asyncio.run(math._perform_calculation("multiply matrix [[1,2],[3,4]] and [[5,6],[7,8]]")))
print(asyncio.run(math._perform_calculation("determinant of matrix [[1,2],[3,4]]")))
print(asyncio.run(math._perform_calculation("gaussian distribution 100 15")))

print(asyncio.run(data._perform_analysis("analyze correlation in [(1,5),(2,7),(3,6),(4,8)]")))
print(asyncio.run(data._perform_analysis("generate report for [10,15,12,18,20,16,14]")))
```

Supported Math prompts: arithmetic (`2 + 3 * 4`, `sqrt(16)`), statistics
(`mean of [...]`), linear algebra (`multiply matrix ...`, `determinant of ...`),
and normal-distribution summaries.

Supported Data Analyst prompts: histograms / scatter / line / box charts,
correlation analysis, single- and paired-variable reports, and data-processing
guidance.

---

## 8. Construct raw JSON-RPC requests

Anything that speaks HTTP can call an agent. The envelope is plain JSON-RPC 2.0:

```bash
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -d '{
    "id": "1",
    "jsonrpc": "2.0",
    "method": "message/send",
    "params": {
      "message": {"role": "user", "parts": [{"kind": "text", "text": "calculate mean of [1,2,3,4,5]"}]}
    }
  }'
```

A **successful** response always includes `"error": null` alongside `result` —
do not treat the presence of the `error` *key* as a failure; only a non-null
value is an error.

---

## 9. Cross-framework / hybrid agents

`examples/simple_hybrid_demo.py` shows an A2A agent collaborating with a mock
AutoGen code-generation agent — the pattern for letting agents on *different*
frameworks interoperate over A2A.

```python
import asyncio
from examples.simple_hybrid_demo import SimpleHybridOrchestrator

async def main():
    orch = SimpleHybridOrchestrator(math_agent_url="http://localhost:8001")
    result = await orch.solve_with_collaboration(
        "Calculate statistics for [12, 15, 18, 20] and create visualization code"
    )
    print(result["final_solution"])

asyncio.run(main())
```

For the real, LLM-powered AutoGen version:

```bash
pip install -e ".[autogen]"
export OPENAI_API_KEY="sk-..."
python examples/hybrid_autogen_a2a.py
```

---

## 10. Testing & Allure reports

The suite runs fully in-process and is fast (`~0.6s`):

```bash
pip install -e ".[dev]"
pytest                                   # run tests
pytest --cov --cov-report=term-missing   # with coverage (fails under 90%)
```

Generate a rich [Allure](https://allurereport.org/) report:

```bash
pytest --alluredir=allure-results        # collect results
allure serve allure-results              # open the report (needs the Allure CLI)
```

Tests are grouped with `@allure.feature` / `@allure.story` / `@allure.title`,
so the report reads as living documentation of every agent behaviour.
