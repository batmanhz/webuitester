import asyncio
from playwright.async_api import async_playwright, expect
import time

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("--- Starting Story 2.1 E2E Test ---")

        # 1. Access Home Page
        print("1. Accessing Home Page...")
        await page.goto("http://localhost:5173/")
        await expect(page).to_have_title("frontend") 
        
        # Verify List View components
        print("   Verifying Home View components...")
        await expect(page.get_by_role("heading", name="Test Cases")).to_be_visible()
        await expect(page.get_by_role("button", name="New Case")).to_be_visible()

        # 2. Create New Case
        print("2. Creating New Case...")
        await page.get_by_role("button", name="New Case").click()
        
        # Verify Editor URL
        await expect(page).to_have_url("http://localhost:5173/case/new")
        print("   Navigated to New Case Editor.")

        # Fill Form
        test_name = f"E2E Test Case {int(time.time())}"
        test_url = "https://example.com"
        
        print(f"   Filling form: Name='{test_name}', URL='{test_url}'")
        await page.get_by_placeholder("e.g. Login Flow").fill(test_name)
        await page.get_by_placeholder("https://example.com").fill(test_url)

        # Add Steps
        print("   Adding steps...")
        # Step 1 (Default one)
        await page.locator(".step-item").first.locator("textarea").first.fill("Open Homepage")
        await page.locator(".step-item").first.locator("textarea").nth(1).fill("Homepage loaded")
        
        # Step 2
        await page.get_by_role("button", name="Add Step").click()
        await page.locator(".step-item").nth(1).locator("textarea").first.fill("Click Login")
        await page.locator(".step-item").nth(1).locator("textarea").nth(1).fill("Login modal appears")

        # Save
        print("   Saving...")
        await page.get_by_role("button", name="Save").click()

        # 3. Verify Redirection and List Update
        print("3. Verifying List Update...")
        await expect(page).to_have_url("http://localhost:5173/")
        await expect(page.get_by_text(test_name)).to_be_visible()
        await expect(page.get_by_text(test_url)).to_be_visible()
        print("   New case found in list.")

        # 4. View/Edit Case
        print("4. Verifying View/Edit...")
        await page.get_by_text(test_name).click()
        
        # Verify Data Loading
        await expect(page.get_by_placeholder("e.g. Login Flow")).to_have_value(test_name)
        await expect(page.get_by_placeholder("https://example.com")).to_have_value(test_url)
        
        # Verify Steps
        count = await page.locator(".step-item").count()
        if count != 2:
            raise Exception(f"Expected 2 steps, found {count}")
        
        step1_instruction = await page.locator(".step-item").first.locator("textarea").first.input_value()
        if step1_instruction != "Open Homepage":
             raise Exception(f"Step 1 instruction mismatch. Got: {step1_instruction}")
             
        print("   Data loaded correctly.")

        print("--- Test Completed Successfully ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
