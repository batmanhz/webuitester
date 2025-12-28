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
        
        # 1. Simulate the Force Fill logic from core.py
        print("Simulating Force Fill...")
        selector = "#kw"
        value = "杭州天气"
        js_selector = selector.replace("'", "\\'")
        
        await page.evaluate(f"""(val) => {{
            const el = document.querySelector('{js_selector}');
            if (el) {{
                el.value = val;
                el.setAttribute('value', val); 
                el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            }} else {{
                console.error("Element not found");
            }}
        }}""", value)
        
        # 2. Simulate the Verification Extraction logic from core.py
        print("Extracting Page Content for Verification...")
        verify_elements = await page.evaluate("""() => {
             // Cloned nodes do NOT retain .value property for inputs unless explicitly set via attribute
             // So we must iterate ORIGINAL inputs, get their values, and update the CLONE.
             // OR, easier: just iterate original inputs and replace them in a temporary structure?
             // No, we need full text.
             
             // Let's try a better approach:
             // 1. Clone body
             const bodyClone = document.body.cloneNode(true);
             
             // 2. Get all original inputs
             const originalInputs = document.querySelectorAll('input, textarea');
             // 3. Get all cloned inputs (they should match in order if DOM structure didn't change during clone)
             const clonedInputs = bodyClone.querySelectorAll('input, textarea');
             
             for (let i = 0; i < originalInputs.length; i++) {
                 const original = originalInputs[i];
                 const clone = clonedInputs[i];
                 
                 // If original has a value, we want to show it in clone
                 if (original.value) {
                     // We replace the input with a SPAN to ensure it's rendered as text
                     const span = document.createElement('span');
                     span.textContent = ` [Input Value: ${original.value}] `;
                     
                     // Replace the input in the clone with this span
                     if (clone && clone.parentNode) {
                        clone.replaceWith(span);
                     }
                 }
             }
             
             // Baidu puts <style> tags inside body sometimes, or scripts. 
             // textContent includes script/style content which is noise.
             // We should remove scripts and styles from clone first.
             const scripts = bodyClone.querySelectorAll('script, style');
             scripts.forEach(s => s.remove());
             
             // Use textContent instead of innerText to bypass visibility checks
             return bodyClone.textContent.replace(/\\s+/g, ' ').slice(0, 5000); 
        }""")
        
        print("-" * 50)
        # Check if our target string exists
        # Note: Baidu might be hiding the input in mobile view or some weird structure, 
        # or innerText doesn't capture it because of CSS visibility on parent?
        # Let's verify if we can find ANY input value
        if "[Input Value:" in verify_elements:
             print("Found SOME input values.")
        
        if f"[Input Value: {value}]" in verify_elements:
            print("SUCCESS: Input value successfully captured in verification text!")
            # Print snippet around the value
            idx = verify_elements.find(f"[Input Value: {value}]")
            start = max(0, idx - 50)
            end = min(len(verify_elements), idx + 50)
            print(f"Context snippet: ...{verify_elements[start:end]}...")
        else:
            print("FAILURE: Input value NOT found in verification text.")
            print("Dump (first 500 chars):", verify_elements[:500])
            
        print("-" * 50)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
