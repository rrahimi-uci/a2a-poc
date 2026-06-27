"""
A2A Protocol implementation for agent-to-agent communication.
This is a simplified version of the A2A protocol compatible with Python 3.9.
"""

from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
import uuid
from datetime import datetime


class MessageRole(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class TaskState(str, Enum):
    PENDING = "pending"
    WORKING = "working"
    COMPLETED = "completed"
    ERROR = "error"
    INPUT_REQUIRED = "input_required"


class MessagePart(BaseModel):
    kind: Literal["text"] = "text"
    text: str


class Message(BaseModel):
    kind: Literal["message"] = "message"
    messageId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    parts: List[MessagePart]
    contextId: Optional[str] = None
    taskId: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


class TaskStatus(BaseModel):
    state: TaskState
    message: Optional[Message] = None
    error: Optional[str] = None


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    kind: Literal["task"] = "task"
    messages: List[Message] = Field(default_factory=list)
    status: TaskStatus
    contextId: Optional[str] = None
    sessionId: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentCard(BaseModel):
    """Agent Card describing an agent's capabilities and connection info."""
    id: str
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Unknown"
    homepage: Optional[str] = None
    connection: Dict[str, Any]  # Connection details like URL, port
    capabilities: List[str] = Field(default_factory=list)
    supportedContentTypes: List[str] = Field(default_factory=lambda: ["text/plain"])
    
    
class MessageSendParams(BaseModel):
    message: Message
    sessionId: Optional[str] = None
    contextId: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class JSONRPCRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    jsonrpc: Literal["2.0"] = "2.0"
    method: str
    params: Dict[str, Any]


class JSONRPCResponse(BaseModel):
    id: str
    jsonrpc: Literal["2.0"] = "2.0"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class JSONRPCError(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None


# Error codes following JSON-RPC 2.0 specification
class ErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    
    # A2A specific error codes
    AGENT_UNAVAILABLE = -32001
    TASK_FAILED = -32002
    COMMUNICATION_ERROR = -32003
