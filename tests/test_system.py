#!/usr/bin/env python3
"""
Simple test to verify the A2A system is working
"""

import asyncio
import requests
import json
import time
import sys
import os

# Add the project root to the path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from agents.math_agent import MathAgent
from agents.data_analyst_agent import DataAnalystAgent
import threading


def start_agent(agent_class, port):
    """Start an agent in a separate thread"""
    agent = agent_class(port=port)
    agent.start_server()


async def test_agent_communication():
    """Test basic agent communication"""
    print("🧪 Testing A2A Agent Communication")
    print("=" * 40)
    
    # Test Math Agent
    print("\\n1. Testing Math Agent...")
    try:
        # Test agent card
        response = requests.get("http://localhost:8001", timeout=5)
        if response.status_code == 200:
            card = response.json()
            print(f"✅ Math Agent Card: {card['name']}")
        else:
            print("❌ Failed to get Math Agent card")
            return False
            
        # Test calculation
        message = {
            "id": "test-1",
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Calculate mean of [1, 2, 3, 4, 5]"}]
                }
            }
        }
        
        response = requests.post("http://localhost:8001", json=message, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Math Agent calculation successful")
            print(f"   Result preview: {result['result']['status']['message']['parts'][0]['text'][:100]}...")
        else:
            print("❌ Math Agent calculation failed")
            return False
            
    except Exception as e:
        print(f"❌ Math Agent test failed: {e}")
        return False
    
    # Test Data Analyst Agent  
    print("\\n2. Testing Data Analyst Agent...")
    try:
        # Test agent card
        response = requests.get("http://localhost:8002", timeout=5)
        if response.status_code == 200:
            card = response.json()
            print(f"✅ Data Analyst Agent Card: {card['name']}")
        else:
            print("❌ Failed to get Data Analyst Agent card")
            return False
            
        # Test analysis
        message = {
            "id": "test-2", 
            "jsonrpc": "2.0",
            "method": "message/send",
            "params": {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "analyze data [10, 20, 15, 25, 30]"}]
                }
            }
        }
        
        response = requests.post("http://localhost:8002", json=message, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print("✅ Data Analyst Agent analysis successful")
            print(f"   Result preview: {result['result']['status']['message']['parts'][0]['text'][:100]}...")
        else:
            print("❌ Data Analyst Agent analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ Data Analyst Agent test failed: {e}")
        return False
    
    print("\\n🎉 All tests passed! A2A system is working correctly.")
    return True


def main():
    """Main test function"""
    print("🚀 A2A Multi-Agent System Test")
    print("This test will start both agents and verify communication")
    print("Press Ctrl+C to stop at any time\\n")
    
    # Start agents in background threads
    print("Starting agents...")
    
    math_thread = threading.Thread(target=start_agent, args=(MathAgent, 8001), daemon=True)
    data_thread = threading.Thread(target=start_agent, args=(DataAnalystAgent, 8002), daemon=True)
    
    math_thread.start()
    data_thread.start()
    
    # Wait for agents to start
    print("Waiting for agents to initialize...")
    time.sleep(3)
    
    # Run tests
    try:
        success = asyncio.run(test_agent_communication())
        if success:
            print("\\n✨ Test completed successfully!")
            print("\\n📝 Next steps:")
            print("1. Run 'python scripts/start_math_agent.py' in one terminal")
            print("2. Run 'python scripts/start_data_agent.py' in another terminal") 
            print("3. Run 'python scripts/run_demo.py' to see the full orchestrator demo")
            print("   OR run 'python scripts/launch_system.py' to start everything at once")
        else:
            print("\\n❌ Tests failed. Check the error messages above.")
            
    except KeyboardInterrupt:
        print("\\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\\n💥 Test failed with error: {e}")


if __name__ == "__main__":
    main()
