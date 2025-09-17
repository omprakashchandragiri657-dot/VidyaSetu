from playwright.sync_api import sync_playwright, Page, expect
import time

def verify_dashboard_login(page: Page):
    """
    This test verifies that a principal can log in and see the new dashboard.
    """
    # 1. Arrange: Go to the login page.
    page.goto("http://localhost:3000/login")

    # 2. Act: Fill in the login form and submit.
    # Use the correct label "Email / Username"
    page.get_by_label("Email / Username").fill("principal-aits@gmail.com")
    page.get_by_label("Password").fill("1245@CSIT")
    page.get_by_role("button", name="Login").click()

    # Wait for the redirection to the principal's dashboard
    page.wait_for_url("**/principal/dashboard", timeout=15000)

    # 3. Assert: Wait for a key element on the dashboard to be visible.
    departments_heading = page.get_by_role("heading", name="Departments")
    expect(departments_heading).to_be_visible()

    # Give the page a moment to fully render any final elements
    time.sleep(2)

    # 4. Screenshot: Capture the final result for visual verification.
    page.screenshot(path="jules-scratch/verification/principal_dashboard_final.png")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            verify_dashboard_login(page)
            print("Verification script ran successfully.")
        except Exception as e:
            print(f"An error occurred during verification: {e}")
            # Take a screenshot even on failure for debugging
            page.screenshot(path="jules-scratch/verification/error_screenshot.png")
        finally:
            browser.close()

if __name__ == "__main__":
    main()
