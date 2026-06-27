#!/usr/bin/env python3
"""Run the multi-agent orchestrator demo against already-running agents.

Prerequisites: start the Math Agent (port 8001) and Data Analyst Agent
(port 8002) first, e.g. with ``python scripts/launch_system.py`` or by
running each ``start_*_agent.py`` script in its own terminal.

Usage:
    python scripts/run_demo.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from examples.orchestrator import main as orchestrator_main  # noqa: E402


if __name__ == "__main__":
    asyncio.run(orchestrator_main())
