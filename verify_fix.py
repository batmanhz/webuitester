import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Match the config in core.py (Headless=False)
        browser = await p.chromium.launch(headless=False, args=["--no-sandbox", "--start-maximized"])
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        print("Navigating to Baidu...")
        await page.goto("https://www.baidu.com")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 1. Simulate Level 2: CDP InsertText (Chrome MCP style)
        print("Simulating Level 2 (CDP InsertText)...")
        session = await page.context.new_cdp_session(page)
        selector = "#kw"
        value = "杭州天气"
        js_selector = selector.replace("'", "\\'")
        
        try:
            await page.evaluate(f"document.querySelector('{js_selector}').focus()")
            # Small delay to ensure focus
            await page.wait_for_timeout(500)
            await session.send("Input.insertText", {"text": value})
            print("Level 2 Executed.")
        except Exception as e:
            print(f"Level 2 Failed: {e}")
        
        await page.wait_for_timeout(1000)

        # Check value after Level 2
        val_l2 = await page.evaluate(f"document.querySelector('{js_selector}').value")
        print(f"Value after Level 2: '{val_l2}'")

        if val_l2 != value:
            # 2. Simulate Level 3: JS Force Fill
            print("Level 2 failed or incomplete. Simulating Level 3 (JS Force Fill)...")
            
            await page.evaluate(f"""(val) => {{
                const el = document.querySelector('{js_selector}');
                if (el) {{
                    el.focus();
                    el.value = val;
                    el.setAttribute('value', val); 
                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                    el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                }} else {{
                    console.error("Element not found");
                }}
            }}""", value)
            print("Level 3 Executed.")
        
        # 3. Verification
        print("Extracting Page Content for Verification...")
        verify_elements = await page.evaluate("""() => {
             const inputs = document.querySelectorAll('input, textarea');
             let results = [];
             inputs.forEach(el => {
                 results.push(`Tag: ${el.tagName}, ID: ${el.id}, Name: ${el.name}, Value: '${el.value}', Visible: ${el.offsetParent !== null}`);
             });
             return results.join('\\n');
        }""")
        
        print("-" * 50)
        print("Detected Inputs:")
        print(verify_elements)
        print("-" * 50)
        
        if f"Value: '{value}'" in verify_elements:
             print("SUCCESS: Input value found in DOM.")
        else:
             print("FAILURE: Input value NOT found in DOM.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())