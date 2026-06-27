"""
A2A Multi-Agent Communication System

This package provides a simplified implementation of the Agent-to-Agent (A2A) protocol
for inter-agent communication, featuring specialized agents that can collaborate
to solve complex problems.
"""

__version__ = "1.0.0"
__author__ = "A2A Development Team"

from .common.a2a_protocol import Message, Task, TaskStatus, TaskState, MessageRole, MessagePart
from .common.base_agent import BaseAgent

__all__ = [
    "Message",
    "Task", 
    "TaskStatus",
    "TaskState",
    "MessageRole",
    "MessagePart",
    "BaseAgent"
]
