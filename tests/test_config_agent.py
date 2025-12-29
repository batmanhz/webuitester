import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.core.config import settings
from backend.app.agent.core import Agent

def test_config_loading():
    print("--- Testing Config Loading ---")
    print(f"Provider: {settings.model.provider}")
    print(f"Model: {settings.model.name}")
    print(f"Base URL: {settings.model.base_url}")
    print(f"Thinking Enabled: {settings.model.thinking}")
    print(f"API Key Present: {bool(settings.model.api_key)}")
    
    if settings.model.provider == "zhipu" and settings.model.name == "glm-4.6v":
        print("✅ Config loaded correctly")
    else:
        print("❌ Config mismatch")

async def test_agent_init():
    print("\n--- Testing Agent Initialization ---")
    agent = Agent()
    print(f"Agent Client Base URL: {agent.client.base_url}")
    print(f"Agent Model: {agent.model}")
    
    if str(agent.client.base_url) == settings.model.base_url and agent.model == settings.model.name:
        print("✅ Agent initialized with config values")
    else:
        print(f"❌ Agent init mismatch. Client URL: {agent.client.base_url}")

if __name__ == "__main__":
    test_config_loading()
    asyncio.run(test_agent_init())
