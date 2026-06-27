#!/usr/bin/env python3
"""Start the Math Agent A2A server.

Usage:
    python scripts/start_math_agent.py [--port 8001]
"""

import argparse
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.math_agent import MathAgent  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Start the A2A Math Agent")
    parser.add_argument("--port", type=int, default=8001, help="Port to listen on (default: 8001)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    agent = MathAgent(port=args.port)
    print(f"🧮 Math Agent starting on http://localhost:{args.port}")
    print(f"   Agent card: http://localhost:{args.port}/")
    agent.start_server()


if __name__ == "__main__":
    main()
