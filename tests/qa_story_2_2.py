import asyncio
import os
import sys
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.agent.core import Agent
from backend.app.core.config import settings

# Mock classes for TestCase/TestStep
class MockTestStep:
    def __init__(self, order, instruction, expected_result):
        self.id = "mock-id" # Added id
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

async def verify_story_2_2():
    print("==========================================")
    print("       QA Verification: Story 2.2         ")
    print("==========================================")

    # 1. Verify Configuration
    print("\n[1] Verifying Configuration...")
    print(f"    - Provider: {settings.model.provider}")
    print(f"    - Model: {settings.model.name}")
    print(f"    - Base URL: {settings.model.base_url}")
    print(f"    - Thinking Enabled: {settings.model.thinking}")
    
    if settings.model.provider != "zhipu" or "glm" not in settings.model.name:
        print("    ❌ Config Mismatch! Expected Zhipu/GLM.")
        return
    print("    ✅ Configuration loaded correctly.")

    # 2. Initialize Agent
    print("\n[2] Initializing Agent...")
    try:
        agent = Agent()
        if not agent.client:
            print("    ❌ Failed to initialize OpenAI client (missing API key?).")
            return
        print("    ✅ Agent initialized successfully.")
    except Exception as e:
        print(f"    ❌ Agent initialization failed: {e}")
        return

    # 3. Execute Test Case
    print("\n[3] Executing Real Test Case (Live Model)...")
    # Using www.baidu.com as requested
    test_url = "https://www.baidu.com"
    
    steps = [
        MockTestStep(1, "Type 'Playwright' in the search box", "Search box contains text"),
        MockTestStep(2, "Click the 'Baidu Search' button", "Results page loads")
    ]
    case = MockTestCase("QA Verification Test", test_url, steps)
    
    print(f"    Target: {test_url}")
    print(f"    Steps: {len(steps)}")
    
    try:
        result = await agent.execute_case(case)
        if result:
            print("\n    ✅ Test Execution Completed Successfully!")
        else:
            print("\n    ❌ Test Execution Failed (returned False).")
    except Exception as e:
        print(f"\n    ❌ Test Execution Threw Exception: {e}")

if __name__ == "__main__":
    asyncio.run(verify_story_2_2())
