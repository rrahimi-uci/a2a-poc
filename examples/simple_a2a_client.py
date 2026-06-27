"""
Simplified A2A Client for Hybrid Demo
This is a minimal implementation for demonstration purposes.
"""

import asyncio
import aiohttp
import json
from typing import Optional, Dict, Any

class SimpleMessage:
    """Simple message class for demo."""
    def __init__(self, text: str):
        self.text = text

class SimpleA2AClient:
    """Simplified A2A client for hybrid demo."""
    
    async def send_message(self, agent_url: str, message_text: str) -> str:
        """Send a message to an A2A agent and get response."""
        
        # Create JSON-RPC request
        request = {
            "id": "demo-1",
            "jsonrpc": "2.0", 
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": message_text}]
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    agent_url,
                    json=request,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        return f"Error: HTTP {response.status} - {await response.text()}"
                    
                    result = await response.json()

                    # The "error" key is always present in a JSON-RPC response;
                    # only treat it as an error when the value is non-null.
                    if result.get("error") is not None:
                        return f"Agent error: {result['error']}"
                    
                    # Extract the response text
                    if "result" in result and "status" in result["result"]:
                        status = result["result"]["status"]
                        if "message" in status and "parts" in status["message"]:
                            return status["message"]["parts"][0].get("text", "No response text")
                    
                    return "Unknown response format"
                    
        except asyncio.TimeoutError:
            return "Timeout: Agent did not respond within 30 seconds"
        except Exception as e:
            return f"Communication error: {str(e)}"
