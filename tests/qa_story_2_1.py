import asyncio
from playwright.async_api import async_playwright, expect
import time

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("--- Starting Story 2.1 E2E QA Test ---")

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
        test_name = f"QA Test Case {int(time.time())}"
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

        # Save Creation
        print("   Saving new case...")
        await page.get_by_role("button", name="Save").click()
        
        # Verify redirect to edit mode (URL should contain UUID)
        # Note: Previous E2E assumed redirect to Home, but EditorView logic is:
        # router.push(`/case/${newCase.id}`)
        # So we expect URL to match /case/UUID
        # Relaxing condition to just check if URL changed from /new, and wait a bit
        print("   Waiting for redirection...")
        await page.wait_for_timeout(2000) # Give Vue router time to push
        
        current_url = page.url
        if "/case/new" in current_url:
             # Try waiting a bit longer using expect
             await expect(page).not_to_have_url("http://localhost:5173/case/new", timeout=10000)
        
        new_case_url = page.url
        print(f"   Saved and redirected to: {new_case_url}")
        
        if "/case/" not in new_case_url or "new" in new_case_url:
             raise Exception(f"Failed to redirect to edit page. Current URL: {new_case_url}")
        
        # 3. Update Case (Edit)
        print("3. Updating Case...")
        updated_name = test_name + " (Updated)"
        await page.get_by_placeholder("e.g. Login Flow").fill(updated_name)
        
        # Add Step 3
        await page.get_by_role("button", name="Add Step").click()
        await page.locator(".step-item").nth(2).locator("textarea").first.fill("Click Logout")
        
        # Save Update
        print("   Saving updates...")
        await page.get_by_role("button", name="Save").click()
        
        # Verify Success Message
        # Element Plus messages are usually in .el-message
        await expect(page.locator(".el-message--success")).to_be_visible()
        print("   Update success message visible.")

        # 4. Return to Home and Verify List
        print("4. Verifying List Update...")
        await page.goto("http://localhost:5173/")
        await expect(page.get_by_text(updated_name)).to_be_visible()
        print("   Updated case name found in list.")
        
        # 5. Delete Case
        print("5. Deleting Case...")
        # Since we are on Home View, we can find the Delete button in the row
        # Element Plus Table row structure is tricky, but we can find row by text and then find button inside
        # Or easier: click the Delete button in the row that contains updated_name
        
        row = page.get_by_text(updated_name).locator("xpath=../..") # Tricky to get row from cell
        # Let's try to get the row that contains the text
        # Using Playwright's filter
        row = page.locator("tr").filter(has_text=updated_name)
        
        # Click Delete button in that row
        await row.get_by_role("button", name="Delete").click()
        
        # Handle Confirm Dialog (Element Plus MessageBox)
        # It usually renders in body
        await expect(page.get_by_text("Are you sure you want to delete this test case?")).to_be_visible()
        await page.get_by_role("button", name="Delete", exact=True).click() # The confirm button
        
        # Verify Success Message
        await expect(page.get_by_text("Test case deleted")).to_be_visible()
        print("   Delete success message visible.")
        
        # Verify Removal from List
        await expect(page.get_by_text(updated_name)).not_to_be_visible()
        print("   Case removed from list.")
            
        print("   Data persistence verified.")

        print("--- QA Test Completed Successfully ---")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())