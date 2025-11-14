import base64
from playwright.sync_api import sync_playwright
from twocaptcha import TwoCaptcha

# Your 2Captcha API key
solver = TwoCaptcha("YOUR_2CAPTCHA_API_KEY")

def solve_botdetect_captcha(page, captcha_image_selector, captcha_input_selector):
    """
    Finds a BotDetect captcha, solves it using 2Captcha, and inputs the solution.
    """
    try:
        # Step 1: Find the captcha image element
        captcha_image = page.locator(captcha_image_selector)

        # Step 2: Capture the image as Base64
        # A standard BotDetect captcha is typically an <img> tag.
        # Playwright can capture the element's screenshot and return it as a buffer, which we convert to Base64.
        image_buffer = captcha_image.screenshot()
        image_base64 = base64.b64encode(image_buffer).decode('utf-8')

        # Step 3: Send the image to 2Captcha for solving
        print("Sending captcha image to 2Captcha...")
        result = solver.normal(file=image_base64)
        print(f"2Captcha solved the captcha: {result['code']}")
        
        captcha_text = result['code']
        
        # Step 4: Input the solved text into the corresponding field
        page.locator(captcha_input_selector).fill(captcha_text)

        return True
    
    except Exception as e:
        print(f"An error occurred while trying to solve the captcha: {e}")
        return False

# Main automation script
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=50)
    page = browser.new_page()

    # Navigate to the page with the captcha.
    # Replace this URL and selectors with the specific values for your target site.
    page.goto("https://webskrining.bpjs-kesehatan.go.id/skrining")

    # Example selectors for a BotDetect captcha.
    # You will need to inspect the target website's HTML to find the correct ones.
    captcha_image_selector = "img[id$='_CaptchaImage']"
    captcha_input_selector = "input[id$='captchaCode_txt']"

    # Fill in other form fields
    page.locator("#nik_txt").fill("nik")
    page.locator("#TglLahir_src").fill("tgl_lahir")

    # Call the function to solve the captcha
    success = solve_botdetect_captcha(page, captcha_image_selector, captcha_input_selector)
    
    if success:
        print("Captcha resolved, submitting form...")
        page.locator("#submit-button").click()

    # Wait for the result or close the browser
    page.wait_for_timeout(5000)
    browser.close()
