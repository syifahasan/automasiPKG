from playwright.sync_api import sync_playwright
import time

class SRKAutomation:
    def __init__(self):
        self.profile_path = r"E:\ChromeProfileAutomation"
        self.browser = None
        self.page = None
        self.playwright = None

    def automate_form(self, url, form_data):
        with sync_playwright() as playwright:
            self.playwright = playwright
            self.browser = playwright.chromium.launch(headless=False)
            self.page = self.browser.new_page()

            try:
                self.page.goto('https://webskrining.bpjs-kesehatan.go.id/skrining')
                
                print('\n🔍 Please solve the CAPTCHA in the browser window...')
                captcha_solution = input("Captcha Solution: ")
                self.page.fill('input[name="captchaCode_txt"]', captcha_solution)
            except Exception as e:
                print(f"❌ Error during CAPTCHA handling: {e}")
                return
            

if __name__ == "__main__":
    srk_automation = SRKAutomation()
    form_data = {
        None
    }
    srk_automation.automate_form('https://webskrining.bpjs-kesehatan.go.id/skrining', form_data)


