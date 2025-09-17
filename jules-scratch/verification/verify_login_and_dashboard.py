from playwright.sync_api import sync_playwright, Page, expect

def verify_dashboard_login(page: Page):
    """
    This test verifies that a principal can log in and see the new dashboard.
    """
    # 1. Arrange: Go to the login page.
    page.goto("http://localhost:3000/login")

    # 2. Act: Fill in the login form and submit.
    page.get_by_label("Email").fill("principal-aits@gmail.com")
    page.get_by_label("Password").fill("1245@CSIT")
    page.get_by_role("button", name="Login").click()

    # After login, the app should redirect. We'll go directly to the dashboard
    # to be sure we land on the correct page for the test.
    page.goto("http://localhost:3000/principal/dashboard")

    # 3. Assert: Wait for a key element on the dashboard to be visible.
    departments_heading = page.get_by_role("heading", name="Departments")
    expect(departments_heading).to_be_visible(timeout=10000) # Increased timeout

    # 4. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/principal_dashboard.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        verify_dashboard_login(page)
        browser.close()

if __name__ == "__main__":
    main()
