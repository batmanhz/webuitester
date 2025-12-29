import asyncio
import os
import sys
from unittest.mock import MagicMock, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.agent.core import Agent

# Mock classes to avoid DB connection
class MockTestStep:
    def __init__(self, order, instruction, expected_result):
        self.order = order
        self.instruction = instruction
        self.expected_result = expected_result

class MockTestCase:
    def __init__(self, name, url, steps):
        self.name = name
        self.url = url
        self.steps = steps
    
    async def fetch_related(self, *args):
        pass

async def test_agent_execution():
    print("--- Starting Agent V1 Test ---")
    
    # Mock Data
    steps = [
        MockTestStep(1, "Type 'Playwright' into search box", "Search box filled"),
        MockTestStep(2, "Click Google Search", "Results appear")
    ]
    case = MockTestCase("Google Search Test", "https://www.google.com", steps)

    # Initialize Agent
    # Agent now uses config, so we mock settings if we want to bypass config
    # For this V1 test, we just want to verify logic with mocks.
    
    agent = Agent()
    
    # Mock the client completely
    agent.client = AsyncMock()
    
    # Mock responses
    mock_response_1 = MagicMock()
    mock_response_1.choices = [MagicMock(message=MagicMock(content='{"action": "fill", "selector": "[name=\'q\']", "value": "Playwright"}'))]
    
    mock_response_2 = MagicMock()
    mock_response_2.choices = [MagicMock(message=MagicMock(content='{"action": "click", "selector": "input[name=\'btnK\']"}'))]
    
    # Setup side effects
    agent.client.chat.completions.create = AsyncMock(side_effect=[mock_response_1, mock_response_2])

    # Execute
    print(f"Executing case: {case.name} on {case.url}")
    result = await agent.execute_case(case)
    
    print(f"Execution Result: {result}")
    
    if result:
        print("✅ Test Passed")
    else:
        print("❌ Test Failed")

if __name__ == "__main__":
    asyncio.run(test_agent_execution())
