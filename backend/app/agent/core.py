import json
import os
import asyncio
import base64
from typing import Optional, Any, Callable, Awaitable
from backend.app.models.test_case import TestCase
from backend.app.core.config import settings
from browser_use import Agent as BrowserUseAgent, ChatOpenAI
from browser_use.browser import BrowserProfile

class Agent:
    def __init__(self):
        # Load from config
        self.api_key = settings.model.api_key
        self.base_url = settings.model.base_url
        self.model = settings.model.name
        self.temperature = settings.model.temperature
        self.thinking = settings.model.thinking
        self.use_vision = settings.model.use_vision
        self._current_agent = None  # Hold reference to browser_use agent
        self._stop_event = asyncio.Event()
        
        if not self.api_key:
            self.api_key = os.environ.get("OPENAI_API_KEY")

    async def execute_case(self, case: TestCase, log_callback: Optional[Callable[[dict], Awaitable[None]]] = None, stop_event: Optional[asyncio.Event] = None) -> bool:
        if not self.api_key:
            print("Error: OpenAI API Key not provided. Cannot execute.")
            return False

        async def emit(type: str, data: Any):
            if log_callback:
                await log_callback({"type": type, "data": data})

        llm = self._setup_llm()
        browser_profile = self._setup_browser()
        task_prompt = await self._construct_task_prompt(case)
        
        await emit("log", f"Initializing Browser-Use Agent with task:\n{task_prompt}")

        agent = self._initialize_agent(task_prompt, llm, browser_profile)
        self._current_agent = agent

        return await self._run_agent_loop(agent, emit, stop_event)

    def _setup_llm(self):
        return ChatOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            model=self.model,
            temperature=self.temperature,
        )

    def _setup_browser(self):
        return BrowserProfile(
            headless=False,
        )

    async def _construct_task_prompt(self, case: TestCase) -> str:
        await case.fetch_related("steps")
        steps = sorted(case.steps, key=lambda x: x.order)
        
        task_prompt = f"Navigate to {case.url} and perform the following test steps:\n\n"
        for step in steps:
            task_prompt += f"Step {step.order}: {step.instruction}\n"
            if step.expected_result:
                task_prompt += f"  - Verification needed: {step.expected_result}\n"
        
        task_prompt += "\nIMPORTANT: Provide a detailed summary of actions and verifications."
        return task_prompt

    def _initialize_agent(self, task_prompt, llm, browser_profile):
        return BrowserUseAgent(
            task=task_prompt,
            llm=llm,
            browser_profile=browser_profile,
            use_vision=self.use_vision
        )

    async def _run_agent_loop(self, agent, emit, stop_event) -> bool:
        try:
            print("DEBUG: Agent execution starting...")
            await emit("log", "Agent execution started...")
            
            # Start the browser session to initialize watchdogs
            if agent.browser_session:
                print("DEBUG: Starting browser session...")
                await agent.browser_session.start()
                print("DEBUG: Browser session started.")
            
            max_steps = 30
            step_count = 0
            
            while step_count < max_steps:
                print(f"DEBUG: Starting step {step_count + 1}")
                if stop_event and stop_event.is_set():
                    await emit("log", "Stop requested by user. Terminating agent...")
                    break
                
                step_count += 1
                
                print("DEBUG: Calling agent.step()...")
                await agent.step()
                print("DEBUG: agent.step() returned.")
                
                if await self._process_step_data(agent, emit):
                    return True
            
            await emit("log", "Agent execution finished (Max steps reached or stopped).")
            return True

        except asyncio.CancelledError:
            print("DEBUG: Agent execution CancelledError caught.")
            await emit("log", "Agent execution cancelled.")
            return False
        except Exception as e:
            print(f"DEBUG: Agent execution Exception caught: {e}")
            import traceback
            traceback.print_exc()
            await emit("log", f"Agent execution failed: {str(e)}")
            return False
        finally:
            print("DEBUG: Agent execution finally block.")
            if agent.browser_session:
                try:
                    print("DEBUG: Stopping browser session...")
                    await agent.browser_session.stop()
                    print("DEBUG: Browser session stopped.")
                except Exception as e:
                    print(f"Error stopping browser session: {e}")

    async def _process_step_data(self, agent, emit) -> bool:
        # Extract and emit info from history
        if agent.history and hasattr(agent.history, 'history') and agent.history.history:
            last_step = agent.history.history[-1]
            
            await self._extract_screenshot(last_step, emit)
            return await self._extract_logs(last_step, emit)
        return False

    async def _extract_screenshot(self, last_step, emit):
        try:
            screenshot = None
            if hasattr(last_step, 'state') and last_step.state:
                # Check for direct screenshot
                if hasattr(last_step.state, 'screenshot') and last_step.state.screenshot:
                    screenshot = last_step.state.screenshot
                # Check for screenshot_path
                elif hasattr(last_step.state, 'screenshot_path') and last_step.state.screenshot_path:
                    screenshot_path = last_step.state.screenshot_path
                    if os.path.exists(screenshot_path):
                        with open(screenshot_path, "rb") as image_file:
                            screenshot = base64.b64encode(image_file.read()).decode('utf-8')
            
            if screenshot:
                await emit("screenshot", screenshot)
        except Exception as e:
            print(f"Error extracting screenshot: {e}")
            import traceback
            traceback.print_exc()

    async def _extract_logs(self, last_step, emit) -> bool:
        try:
            model_output = getattr(last_step, 'model_output', None)
            if model_output:
                # Thought
                thought = None
                if hasattr(model_output, 'current_state') and model_output.current_state:
                    thought = getattr(model_output.current_state, 'thought', None)
                
                if not thought and hasattr(model_output, 'thought'):
                    thought = model_output.thought
                    
                if thought:
                    await emit("log", f"[THOUGHT] {thought}")
                    
                # Actions
                actions = getattr(model_output, 'action', [])
                if actions:
                    for action in actions:
                        action_data = action.model_dump() if hasattr(action, 'model_dump') else str(action)
                        await emit("log", f"[ACTION] {action_data}")
                        
                        # Check for completion
                        if isinstance(action_data, dict) and 'done' in action_data:
                            await emit("log", f"Agent completed task: {action_data['done']}")
                            return True
                        if isinstance(action_data, str) and 'done' in action_data.lower():
                            return True
        except Exception as e:
            print(f"Error extracting logs: {e}")
        return False
