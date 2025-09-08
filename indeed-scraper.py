import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time, random, json, os
from datetime import datetime

class MonsterJobScraper:
    COOKIE_FILE = "cookies.json"

    def __init__(self):
        self.driver = None
        self.setup_driver(headless=False)

    def setup_driver(self, headless=False):
        options = uc.ChromeOptions()
        options.add_argument('--no-first-run')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-infobars')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--user-agent=' + self.get_random_user_agent())

        if headless:
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')

        self.driver = uc.Chrome(options=options, version_main=140, headless=headless)

    # ----------------- Cookies -----------------
    def load_cookies(self):
        if os.path.exists(self.COOKIE_FILE):
            with open(self.COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                cookie.pop("sameSite", None)
                cookie.pop("expiry", None)
                try:
                    self.driver.add_cookie(cookie)
                except Exception:
                    continue
            self.driver.refresh()

    def save_cookies(self):
        with open(self.COOKIE_FILE, "w") as f:
            json.dump(self.driver.get_cookies(), f)

    # ----------------- Helpers -----------------
    def get_random_user_agent(self):
        return random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        ])

    def human_delay(self, short=False, long=False):
        if short:
            time.sleep(random.uniform(0.5, 4))
        elif long:
            time.sleep(random.uniform(5, 20))
        else:
            time.sleep(random.uniform(2, 8))

    def human_like_send_keys(self, element, text):
        for char in text:
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.3))
            if char in [' ', '.', '@', '_']:
                time.sleep(random.uniform(0.2, 0.7))

    def maybe_extra_pause(self, chance=0.3):
        if random.random() < chance:
            time.sleep(random.uniform(3, 10))

    def human_scroll(self):
        scroll_steps = random.randint(1, 3)
        for _ in range(scroll_steps):
            offset = random.randint(200, 500)
            self.driver.execute_script(f"window.scrollBy(0, {offset});")
            time.sleep(random.uniform(1, 4))
        if random.random() < 0.5:
            self.driver.execute_script("window.scrollBy(0, -200);")
            time.sleep(random.uniform(1, 3))

    # ----------------- Login -----------------
    def is_logged_in(self):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "[aria-label='My Account']")
            return True
        except NoSuchElementException:
            return False

    def login(self, username, password):
        print("➡️ Opening Monster homepage...")
        self.driver.get("https://www.monster.com")
        self.human_delay(long=True)

        self.load_cookies()
        self.human_delay()

        if self.is_logged_in():
            print("✅ Already logged in via cookies.")
            return

        print("❌ Not logged in. Proceeding with manual login...")
        try:
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[./span[text()='Log in']]"))
            )
            login_button.click()
            self.human_delay()

            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "Input_Email"))
            )
            password_field = self.driver.find_element(By.ID, "passwordInput")
            login_button_submit = self.driver.find_element(By.CSS_SELECTOR, "[name='Input.Button']")

            self.human_like_send_keys(username_field, username)
            self.human_delay(short=True)
            self.human_like_send_keys(password_field, password)
            self.maybe_extra_pause()  # hesitation before submit
            login_button_submit.click()

            WebDriverWait(self.driver, 10).until(EC.url_changes(self.driver.current_url))
            print("✅ Login successful, saving cookies...")
            self.save_cookies()

        except Exception as e:
            print(f"❌ Login failed: {e}")
            raise

    # ----------------- Scraping -----------------
    def scrape_monster_jobs(self, job_title="software engineer", location="New York"):
        print(f"\n🔍 Scraping Monster for '{job_title}' in '{location}'...")

        # Step 1: Go back to homepage after login
        self.driver.get("https://www.monster.com")
        self.human_delay(long=True)   # long human-like delay
        self.human_scroll()

        # Step 2: Enter job title and location
        try:
            search_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "q2"))  # job title input
            )
            location_field = self.driver.find_element(By.ID, "where2")  # location input

            search_field.clear()
            self.human_like_send_keys(search_field, job_title)
            self.human_delay(short=True)

            location_field.clear()
            self.human_like_send_keys(location_field, location)
            self.human_delay(short=True)

            # Click search button
            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-bi-id='search-button']")
            search_button.click()
            self.human_delay(long=True)  # wait for results to load

        except Exception as e:
            print(f"❌ Error setting up search: {e}")
            return []

        # Step 3: Scrape job cards
        jobs = []
        try:
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id^='svx-job-card-component']"))
            )
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-test-id^='svx-job-card-component']")
            print(f"Found {len(job_cards)} job cards on the page.")

            for i, card in enumerate(job_cards[:10], 1):
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("aria-label")
                    company = card.find_element(By.CSS_SELECTOR, "[data-test-id='svx-job-card-company-name']").text
                    location_text = card.find_element(By.CSS_SELECTOR, "[data-test-id='svx-job-card-location']").text

                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location_text,
                        'source': 'Monster',
                        'scraped_at': datetime.now().isoformat()
                    })
                    print(f"[{i}] {title} at {company}")
                    self.human_delay(short=True)
                    if random.random() < 0.2:
                        self.human_scroll()
                except Exception as e:
                    print(f"Skipping job card {i}: {e}")
                    continue

        except Exception as e:
            print(f"❌ Error during scraping: {e}")

        print(f"✅ Scraped {len(jobs)} jobs.")
        return jobs


    # ----------------- Results -----------------
    def save_results(self, jobs):
        if not jobs:
            print("No jobs to save.")
            return
        filename = f"monster_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved results to {filename}")

    # ----------------- Lifecycle -----------------
    def open(self):
        print("➡️ Opening Monster homepage...")
        self.driver.get("https://www.monster.com")
        self.human_delay(2, 4)

        # Try loading cookies
        if os.path.exists(self.COOKIE_FILE):
            print("🔑 Loading cookies from file...")
            with open(self.COOKIE_FILE, "r") as f:
                cookies = json.load(f)
            for cookie in cookies:
                cookie.pop("sameSite", None)   # remove unsupported fields
                cookie.pop("expiry", None)
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ Could not add cookie {cookie.get('name')}: {e}")
            self.driver.refresh()
            self.human_delay(3, 5)

        # Check login status
        if self.is_logged_in():
            print("✅ Logged in via cookies.")
            return
        else:
            print("⚠️ Cookies invalid or expired, performing manual login...")
            self.login('jaideepgrover147@gmail.com', 'Jaideep@123')
            print("✅ Manual login completed, cookies updated.")

    def close(self):
        if self.driver:
            try:
                self.save_cookies()
            except Exception:
                pass
            self.driver.quit()


# --- Main Execution ---
if __name__ == "__main__":
    scraper = MonsterJobScraper()
    try:
        scraper.open()
        jobs = scraper.scrape_monster_jobs("Administrative Assistant", "Remote")
        scraper.save_results(jobs)
    finally:
        time.sleep(10)
        scraper.close()
