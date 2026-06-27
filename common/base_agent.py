"""
Base Agent class with A2A protocol support.
"""

import asyncio
import logging
import aiohttp
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .a2a_protocol import (
    AgentCard, Message, Task, TaskStatus, TaskState, MessageRole,
    JSONRPCRequest, JSONRPCResponse, JSONRPCError, ErrorCodes,
    MessageSendParams, MessagePart
)

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for A2A-compatible agents."""
    
    def __init__(self, 
                 agent_id: str,
                 name: str, 
                 description: str,
                 port: int,
                 capabilities: Optional[List[str]] = None,
                 supported_content_types: Optional[List[str]] = None):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.port = port
        self.capabilities = capabilities or []
        self.supported_content_types = supported_content_types or ["text/plain"]
        self.app = FastAPI(title=f"{name} A2A Agent")
        self.tasks: Dict[str, Task] = {}
        self.setup_routes()
        
    def setup_routes(self):
        """Set up FastAPI routes for A2A protocol."""
        
        @self.app.get("/")
        async def get_agent_card():
            """Return the agent card (capability discovery endpoint)."""
            return self.get_agent_card().model_dump(mode="json")

        @self.app.get("/.well-known/agent.json")
        async def get_well_known_agent_card():
            """A2A-style well-known discovery path for the agent card."""
            return self.get_agent_card().model_dump(mode="json")

        @self.app.get("/health")
        async def health():
            """Lightweight liveness probe."""
            return {"status": "ok", "agent": self.name, "agentId": self.agent_id}

        @self.app.post("/")
        async def handle_jsonrpc(request: JSONRPCRequest):
            """Handle JSON-RPC requests."""
            try:
                if request.method == "message/send":
                    return await self._handle_message_send(request)
                elif request.method == "task/get":
                    return await self._handle_task_get(request)
                else:
                    error = JSONRPCError(
                        code=ErrorCodes.METHOD_NOT_FOUND,
                        message=f"Method not found: {request.method}"
                    )
                    return JSONRPCResponse(id=request.id, error=error.model_dump())
            except Exception as e:
                logger.error(f"Error handling request: {e}")
                error = JSONRPCError(
                    code=ErrorCodes.INTERNAL_ERROR,
                    message=str(e)
                )
                return JSONRPCResponse(id=request.id, error=error.model_dump())
    
    def get_agent_card(self) -> AgentCard:
        """Get the agent card for this agent."""
        return AgentCard(
            id=self.agent_id,
            name=self.name,
            description=self.description,
            connection={
                "url": f"http://localhost:{self.port}",
                "method": "http",
                "version": "1.0"
            },
            capabilities=self.capabilities,
            supportedContentTypes=self.supported_content_types
        )
    
    async def _handle_message_send(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle message/send requests."""
        try:
            params = MessageSendParams(**request.params)
            task = await self.process_message(params)
            return JSONRPCResponse(id=request.id, result=task.model_dump(mode="json"))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            error = JSONRPCError(
                code=ErrorCodes.TASK_FAILED,
                message=str(e)
            )
            return JSONRPCResponse(id=request.id, error=error.model_dump())
    
    async def _handle_task_get(self, request: JSONRPCRequest) -> JSONRPCResponse:
        """Handle task/get requests."""
        task_id = request.params.get("taskId")
        if not task_id or task_id not in self.tasks:
            error = JSONRPCError(
                code=ErrorCodes.INVALID_PARAMS,
                message="Task not found"
            )
            return JSONRPCResponse(id=request.id, error=error.model_dump())

        task = self.tasks[task_id]
        return JSONRPCResponse(id=request.id, result=task.model_dump(mode="json"))
    
    @abstractmethod
    async def process_message(self, params: MessageSendParams) -> Task:
        """Process an incoming message and return a task."""
        pass
    
    async def send_message_to_agent(self, 
                                   agent_url: str, 
                                   message: Message, 
                                   session_id: Optional[str] = None) -> Task:
        """Send a message to another agent."""
        request = JSONRPCRequest(
            method="message/send",
            params=MessageSendParams(
                message=message,
                sessionId=session_id
            ).model_dump(mode="json")
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                agent_url,
                json=request.model_dump(mode="json"),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Agent communication failed: {await response.text()}"
                    )
                
                result = await response.json()
                # A JSON-RPC response always carries an "error" key; it is only
                # an actual error when its value is non-null.
                if result.get("error") is not None:
                    raise HTTPException(
                        status_code=500,
                        detail=f"Agent returned error: {result['error']}"
                    )

                return Task(**result["result"])
    
    async def get_agent_card_from_url(self, agent_url: str) -> AgentCard:
        """Get agent card from another agent."""
        async with aiohttp.ClientSession() as session:
            async with session.get(agent_url) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"Failed to get agent card: {await response.text()}"
                    )
                
                result = await response.json()
                return AgentCard(**result)
    
    def start_server(self):
        """Start the agent server."""
        import uvicorn
        logger.info(f"Starting {self.name} on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


class A2AClient:
    """Client for communicating with A2A agents."""
    
    async def send_message(self, agent_url: str, message: Message, session_id: Optional[str] = None) -> Task:
        """Send a message to an agent."""
        request = JSONRPCRequest(
            method="message/send",
            params=MessageSendParams(
                message=message,
                sessionId=session_id
            ).model_dump(mode="json")
        )

        async with aiohttp.ClientSession() as session:
            async with session.post(
                agent_url,
                json=request.model_dump(mode="json"),
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Agent communication failed: {await response.text()}")
                
                result = await response.json()
                # A JSON-RPC response always carries an "error" key; it is only
                # an actual error when its value is non-null.
                if result.get("error") is not None:
                    raise Exception(f"Agent returned error: {result['error']}")

                return Task(**result["result"])
    
    async def get_agent_card(self, agent_url: str) -> AgentCard:
        """Get agent card from an agent."""
        async with aiohttp.ClientSession() as session:
            async with session.get(agent_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to get agent card: {await response.text()}")
                
                result = await response.json()
                return AgentCard(**result)
