from playwright.sync_api import sync_playwright, Page, expect

def verify_dashboard(page: Page):
    """
    This test verifies that the new Principal Dashboard is rendered correctly.
    """
    # 1. Arrange: Go to the principal dashboard page.
    page.goto("http://localhost:3000/principal/dashboard")

    # 2. Act: Wait for a key element to be visible.
    # We'll wait for the "Departments" heading.
    departments_heading = page.get_by_role("heading", name="Departments")
    expect(departments_heading).to_be_visible()

    # 3. Assert: Check if the stat cards are present.
    expect(page.get_by_text("Total HODs")).to_be_visible()
    expect(page.get_by_text("Total Faculty")).to_be_visible()
    expect(page.get_by_text("Total Students")).to_be_visible()
    expect(page.get_by_text("Total Events")).to_be_visible()

    # 4. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/verification.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        verify_dashboard(page)
        browser.close()

if __name__ == "__main__":
    main()
