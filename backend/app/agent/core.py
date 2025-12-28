import json
import os
import asyncio
import base64
from typing import Optional, Any, List, Callable, Awaitable
from playwright.async_api import async_playwright, Page
from backend.app.models.test_case import TestCase
from backend.app.core.config import settings
from openai import AsyncOpenAI

class Agent:
    def __init__(self):
        # Load from config
        self.api_key = settings.model.api_key
        self.base_url = settings.model.base_url
        self.model = settings.model.name
        self.temperature = settings.model.temperature
        self.thinking = settings.model.thinking
        
        if not self.api_key:
            self.api_key = os.environ.get("OPENAI_API_KEY")

        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    async def execute_case(self, case: TestCase, log_callback: Optional[Callable[[dict], Awaitable[None]]] = None) -> bool:
        if not self.client:
            print("Error: OpenAI API Key not provided. Cannot execute.")
            return False

        async def emit(type: str, data: Any):
            if log_callback:
                await log_callback({"type": type, "data": data})

        async with async_playwright() as p:
            # Launch browser with Stealth Mode
            # Using headless=True for production, but keeping stealth args
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--start-maximized" 
                ]
            )
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)
            
            page = await context.new_page()
            
            try:
                msg = f"Navigating to {case.url}"
                print(msg)
                await emit("log", msg)
                
                await page.goto(case.url)
                try:
                    await page.wait_for_load_state("networkidle", timeout=5000)
                except:
                    print("Network idle timeout, continuing...")
                
                # Wait for page to settle (fix for Baidu input visibility issue)
                await page.wait_for_timeout(2000)
                
                # Initial screenshot
                screenshot = await page.screenshot(type="jpeg", quality=60)
                await emit("screenshot", base64.b64encode(screenshot).decode())

                await case.fetch_related("steps")
                steps = sorted(case.steps, key=lambda x: x.order)
                
                all_passed = True
                for step in steps:
                    msg = f"Executing step {step.order}: {step.instruction}"
                    print(msg)
                    await emit("step_start", {"step_id": str(step.id), "order": step.order})
                    await emit("log", msg)
                    
                    # 1. Capture Context
                    elements_summary = await page.evaluate("""() => {
                        const elements = document.querySelectorAll('button, a, input, textarea, select');
                        return Array.from(elements).map(el => {
                            let text = el.innerText || el.textContent || '';
                            text = text.slice(0, 50).replace(/\\s+/g, ' ').trim();
                            
                            const style = window.getComputedStyle(el);
                            const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                            
                            if (!isVisible) return null;

                            return {
                                tagName: el.tagName.toLowerCase(),
                                id: el.id,
                                className: el.className,
                                name: el.name,
                                type: el.type,
                                placeholder: el.placeholder,
                                text: text,
                                value: el.value,
                                "aria-label": el.getAttribute('aria-label')
                            }
                        }).filter(el => el !== null);
                    }""")
                    
                    context_str = json.dumps(elements_summary, indent=2)
                    
                    # 2. Construct Prompt
                    system_prompt = """
                    You are a web automation agent. You will receive a user instruction and a list of interactive elements on the page.
                    You need to output a JSON object describing the action to take using Playwright.
                    
                    Rules:
                    1. Use the EXACT selector from the "Page Elements" list. Do NOT invent selectors.
                    2. If the instruction implies searching (e.g., "input text"), look for input fields.
                    3. If the instruction implies submitting (e.g., "click search"), look for the submit button near the input.
                    4. For Baidu, the search input is usually #kw and the search button is #su.
                    5. Return ONLY the JSON object.
                    
                    Supported actions:
                    - {"action": "click", "selector": "..."} 
                    - {"action": "fill", "selector": "...", "value": "..."}
                    - {"action": "goto", "url": "..."}
                    - {"action": "wait", "seconds": 1}
                    """
                    
                    user_message = f"""
                    Instruction: {step.instruction}
                    Expected Result: {step.expected_result}
                    
                    Page Elements:
                    {context_str}
                    """
                    
                    # 3. Call LLM
                    # Capture screenshot right before calling LLM to provide fresh visual context
                    current_screenshot = await page.screenshot(type="jpeg", quality=60)
                    current_screenshot_b64 = base64.b64encode(current_screenshot).decode()
                    
                    extra_body = {}
                    if self.thinking:
                         extra_body["thinking"] = {"type": "enabled"}

                    await emit("log", "Thinking...")
                    
                    # Construct multimodal message
                    user_content = [
                        {
                            "type": "text", 
                            "text": user_message
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{current_screenshot_b64}"
                            }
                        }
                    ]
                    
                    response = await self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_content}
                        ],
                        response_format={"type": "json_object"},
                        temperature=self.temperature,
                        extra_body=extra_body if extra_body else None
                    )
                    
                    action_json = response.choices[0].message.content
                    if not action_json:
                        await emit("log", "Error: LLM returned empty response")
                        return False
                        
                    if action_json.startswith("```json"):
                        action_json = action_json.replace("```json", "").replace("```", "").strip()
                    elif action_json.startswith("```"):
                         action_json = action_json.replace("```", "").strip()
                        
                    action_data = json.loads(action_json)
                    await emit("log", f"Action: {json.dumps(action_data)}")
                    print(f"Agent Action: {action_data}")
                    
                    # 4. Execute Action
                    await self._perform_action(page, action_data)
                    
                    # Short wait for action effects (e.g. typing, clicking)
                    await page.wait_for_timeout(3000) 
                    
                    # If it was a click, maybe wait for network idle too
                    if action_data.get("action") == "click":
                        try:
                            # Use a short timeout for networkidle because sometimes clicks don't trigger network
                            await page.wait_for_load_state("networkidle", timeout=3000)
                        except:
                            pass # It's fine if it times out
                    
                    # Screenshot after step
                    screenshot = await page.screenshot(type="jpeg", quality=60)
                    await emit("screenshot", base64.b64encode(screenshot).decode())

                    # 5. Verification (Auto-Judge)
                    if step.expected_result:
                         # Capture context again for verification
                         # Include input values in the text for better verification
                         verify_elements = await page.evaluate("""() => {
                             // Helper to replace inputs with their values in a clone of body
                             const bodyClone = document.body.cloneNode(true);
                             
                             // Remove scripts and styles first to clean up noise
                             const scripts = bodyClone.querySelectorAll('script, style, noscript');
                             scripts.forEach(s => s.remove());

                             // Collect inputs separately to ensure they are captured even if hidden in bodyClone
                             let inputValues = [];
                             const originalInputs = document.querySelectorAll('input, textarea');
                             originalInputs.forEach(input => {
                                 if (input.value && input.value.trim() !== "") {
                                     // Check if visible
                                     const style = window.getComputedStyle(input);
                                     const isVisible = style.display !== 'none' && style.visibility !== 'hidden';
                                     inputValues.push(`Input [${input.id || input.name || 'unknown'}]: ${input.value} (Visible: ${isVisible})`);
                                 }
                             });
                             
                             return "Detected Inputs:\\n" + inputValues.join("\\n") + "\\n\\nPage Text:\\n" + document.body.innerText.slice(0, 5000); 
                         }""")
                         
                         system_verify_prompt = """
                         You are a QA Verification Agent.
                         You need to verify if the last action achieved the expected result based on the page content.
                         Return JSON: {"status": "passed" | "failed", "reason": "..."}
                         """
                         
                         user_verify_message = f"""
                         User Instruction: {step.instruction}
                         Expected Result: {step.expected_result}
                         Actual Page Content (truncated):
                         {verify_elements}
                         """
                         
                         await emit("log", "Verifying result...")
                         
                         v_extra_body = {}
                         if self.thinking:
                              v_extra_body["thinking"] = {"type": "enabled"}
                              
                         v_response = await self.client.chat.completions.create(
                             model=self.model,
                             messages=[
                                 {"role": "system", "content": system_verify_prompt},
                                 {"role": "user", "content": user_verify_message}
                             ],
                             response_format={"type": "json_object"},
                             extra_body=v_extra_body if v_extra_body else None
                         )
                         v_json = v_response.choices[0].message.content
                         v_data = json.loads(v_json)
                         
                         status = v_data.get("status", "passed")
                         reason = v_data.get("reason", "")
                         
                         if status == "failed":
                             await emit("log", f"Verification Failed: {reason}")
                             await emit("step_end", {"step_id": str(step.id), "status": "failed"})
                             all_passed = False
                             # Optional: Stop execution on failure?
                             # return False 
                         else:
                             await emit("log", "Verification Passed")
                             await emit("step_end", {"step_id": str(step.id), "status": "passed"})
                    else:
                        await emit("step_end", {"step_id": str(step.id), "status": "passed"})
                    
                if all_passed:
                    await emit("log", "Test Case execution completed successfully.")
                    return True
                else:
                    await emit("log", "Test Case execution failed.")
                    return False
                
            except Exception as e:
                msg = f"Error executing case {case.name}: {e}"
                print(msg)
                await emit("log", msg)
                import traceback
                traceback.print_exc()
                return False
            finally:
                await browser.close()

    async def _perform_action(self, page: Page, action_data: dict):
        action = action_data.get("action")
        selector = action_data.get("selector")
        
        try:
            # Create CDP session for low-level interaction (MCP style)
            session = await page.context.new_cdp_session(page)
            
            if action == "click":
                if selector:
                    # 1. Try Standard Playwright Click with reduced timeout
                    try:
                        print(f"[Action] Trying Level 1 (Playwright Click) on {selector}...")
                        # Reduced timeout to 2000ms to fail faster and switch to robust methods
                        await page.wait_for_selector(selector, state="attached", timeout=2000)
                        await page.click(selector, timeout=2000)
                        print(f"[Action] Level 1 (Playwright Click) SUCCESS")
                    except Exception as e:
                        print(f"[Action] Level 1 Failed: {e}")
                        
                        # 2. JS Click (Most robust for visibility issues)
                        print(f"[Action] Trying Level 2 (JS Click) on {selector}...")
                        js_selector = selector.replace("'", "\\'")
                        await page.evaluate(f"""() => {{
                            const el = document.querySelector('{js_selector}');
                            if (el) {{
                                el.click();
                            }} else {{
                                throw new Error("Element not found for JS click");
                            }}
                        }}""")
                        print(f"[Action] Level 2 (JS Click) SUCCESS")
            
            elif action == "fill":
                value = action_data.get("value")
                if selector and value is not None:
                    # 1. Try Standard Fill/Type with reduced timeout
                    try:
                        print(f"[Action] Trying Level 1 (Playwright Type) on {selector}...")
                        # Reduced timeout to 2000ms to fail faster
                        await page.wait_for_selector(selector, state="attached", timeout=2000)
                        await page.click(selector, timeout=1000) # Short timeout for focus click
                        # Type with 0 delay for instant input
                        await page.keyboard.type(value, delay=0)
                        print(f"[Action] Level 1 (Playwright Type) SUCCESS")
                    except Exception as e:
                        print(f"[Action] Level 1 Failed: {e}")
                        
                        # 2. JS Focus + CDP InsertText (True User Simulation)
                        try:
                            print(f"[Action] Trying Level 2 (CDP InsertText) on {selector}...")
                            js_selector = selector.replace("'", "\\'")
                            await page.evaluate(f"document.querySelector('{js_selector}').focus()")
                            await session.send("Input.insertText", {"text": value})
                            print(f"[Action] Level 2 (CDP InsertText) SUCCESS")
                        except Exception as cdp_e:
                            print(f"[Action] Level 2 Failed: {cdp_e}")

                    # 3. Always Force JS Fill (Safety Net)
                    print(f"[Action] Executing Level 3 (JS Force Fill) as Safety Net...")
                    js_selector = selector.replace("'", "\\'")
                    await page.evaluate(f"""(val) => {{
                       const el = document.querySelector('{js_selector}');
                       if (el) {{
                           el.value = val;
                           el.setAttribute('value', val);
                           el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                           el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                       }}
                    }}""", value)
                    print(f"[Action] Level 3 (JS Force Fill) Executed")

            elif action == "goto":
                url = action_data.get("url")
                if url:
                    await page.goto(url)
            elif action == "wait":
                seconds = action_data.get("seconds", 1)
                await page.wait_for_timeout(seconds * 1000)
            else:
                print(f"Unknown or no-op action: {action}")
        except Exception as e:
            print(f"Action Execution Error: {e}")
            raise e
