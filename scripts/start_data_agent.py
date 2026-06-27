#!/usr/bin/env python3
"""Start the Data Analyst Agent A2A server.

Usage:
    python scripts/start_data_agent.py [--port 8002]
"""

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.data_analyst_agent import DataAnalystAgent  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the A2A Data Analyst Agent")
    parser.add_argument("--port", type=int, default=8002, help="Port to listen on (default: 8002)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    agent = DataAnalystAgent(port=args.port)
    print(f"📊 Data Analyst Agent starting on http://localhost:{args.port}")
    print(f"   Agent card: http://localhost:{args.port}/")
    agent.start_server()


if __name__ == "__main__":
    main()
