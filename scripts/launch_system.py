#!/usr/bin/env python3
"""Launch the complete A2A system: both agents plus the orchestrator demo.

Starts the Math Agent and Data Analyst Agent in background threads, waits for
them to become healthy, then runs the orchestrator demo. Press Ctrl+C to stop.

Usage:
    python scripts/launch_system.py
"""

import asyncio
import logging
import os
import sys
import threading
import time

import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_analyst_agent import DataAnalystAgent  # noqa: E402
from agents.math_agent import MathAgent  # noqa: E402
from examples.orchestrator import main as orchestrator_main  # noqa: E402

MATH_PORT = 8001
DATA_PORT = 8002


def _serve(agent_cls, port: int) -> None:
    agent_cls(port=port).start_server()


def _wait_for(port: int, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if requests.get(f"http://localhost:{port}/health", timeout=2).status_code == 200:
                return True
        except requests.RequestException:
            time.sleep(0.5)
    return False


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    print("🚀 Launching A2A multi-agent system...")

    threading.Thread(target=_serve, args=(MathAgent, MATH_PORT), daemon=True).start()
    threading.Thread(target=_serve, args=(DataAnalystAgent, DATA_PORT), daemon=True).start()

    print("⏳ Waiting for agents to become healthy...")
    if not (_wait_for(MATH_PORT) and _wait_for(DATA_PORT)):
        print("❌ Agents did not start in time. Check that ports 8001/8002 are free.")
        sys.exit(1)

    print("✅ Both agents are up. Running orchestrator demo...\n")
    try:
        asyncio.run(orchestrator_main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user.")


if __name__ == "__main__":
    main()
