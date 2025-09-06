import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import json
from datetime import datetime

class AlternativeJobScraper:
    def __init__(self):
        self.driver = None
        # You should also add headless=False here for better debugging
        self.setup_driver(headless=False) 
        
    def setup_driver(self, headless=False):
        """Setup undetected Chrome driver"""
        options = uc.ChromeOptions()
        options.add_argument('--no-first-run')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-extensions')
        
        # Add headless option here to control from __init__
        self.driver = uc.Chrome(options=options, version_main=140, headless=headless)
        
    def human_delay(self, min_sec=2, max_sec=5):
        """Human-like delays"""
        time.sleep(random.uniform(min_sec, max_sec))
        
    def scrape_glassdoor_jobs(self, job_title="software engineer", location="New York"):
        """Scrape Glassdoor - usually more lenient than Indeed"""
        print(f"🔍 Scraping Glassdoor for '{job_title}' in '{location}'...")
        
        try:
            # Navigate to Glassdoor
            url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={job_title.replace(' ', '%20')}&locT=C&locId=1132348"
            self.driver.get(url)
            self.human_delay(3, 6)
            
            jobs = []
            
            # Wait for job listings
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test='job-link']"))
            )
            
            # Extract job data
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, "[data-test='job-link']")[:20]
            
            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "[data-test='job-title']").text
                    company = card.find_element(By.CSS_SELECTOR, "[data-test='employer-name']").text
                    location = card.find_element(By.CSS_SELECTOR, "[data-test='job-location']").text
                    
                    try:
                        salary = card.find_element(By.CSS_SELECTOR, "[data-test='detailSalary']").text
                    except:
                        salary = "Not specified"
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'source': 'Glassdoor',
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    continue
                    
            print(f"✅ Found {len(jobs)} jobs on Glassdoor")
            return jobs
            
        except Exception as e:
            print(f"❌ Error scraping Glassdoor: {e}")
            return []
            
    def scrape_ziprecruiter_jobs(self, job_title="software engineer", location="New York"):
        """Scrape ZipRecruiter - often easier than Indeed"""
        print(f"🔍 Scraping ZipRecruiter for '{job_title}' in '{location}'...")
        
        try:
            # Navigate to ZipRecruiter
            url = f"https://www.ziprecruiter.com/Jobs/{job_title.replace(' ', '-')}/{location.replace(' ', '-').replace(',', '')}"
            self.driver.get(url)
            self.human_delay(3, 6)
            
            jobs = []
            
            # Wait for job listings
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='job_result']"))
            )
            
            # Extract job data
            job_card_parent = self.driver.find_elements(By.CSS_SELECTOR, "[data-testid='job_result']")
            job_cards = job_card_parent.find_elements(By.TAG_NAME, "div")[:20]
            for card in job_cards:
                try:
                    title = card.find_element(By.CSS_SELECTOR, "h2 a").text
                    company = card.find_element(By.CSS_SELECTOR, "[data-testid='company-name']").text
                    location = card.find_element(By.CSS_SELECTOR, "[data-testid='job-location']").text
                    
                    try:
                        salary = card.find_element(By.CSS_SELECTOR, "[data-testid='job-salary']").text
                    except:
                        salary = "Not specified"
                    
                    jobs.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'salary': salary,
                        'source': 'ZipRecruiter',
                        'scraped_at': datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    continue
                    
            print(f"✅ Found {len(jobs)} jobs on ZipRecruiter")
            return jobs
            
        except Exception as e:
            print(f"❌ Error scraping ZipRecruiter: {e}")
            return []
    def human_like_send_keys(self,element, text):
        print(element, text)
        for char in text:
            element.send_keys(char)
            # Introduce a small, random delay (e.g., between 0.05 and 0.2 seconds)
            time.sleep(0.10) 
    def login_if_needed(self, username, password):
        print("Checking page title...")
        time.sleep(10)
        # Selects an <a> tag that has a child <span> with the exact text 'Log In'
        element = self.driver.find_element(By.XPATH, "//a[./span[text()='Log in']]")
        if element:
            print("Page title indicates login is required. Proceeding with login...")
            element.click()
            try:
                # Wait for the username and password fields to be present.
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "Input_Email"))
                )
                password_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "passwordInput"))
                )
                login_button = self.driver.find_element(By.CSS_SELECTOR, "[name='Input.Button']") # Assuming the button has this ID

                # Fill in the fields and click the button
                # username_field.send_keys(username)
                self.human_like_send_keys(username_field, username)
                self.human_like_send_keys(password_field, password)
                # password_field.send_keys(password)
                time.sleep(2)  # A short delay for human-like behavior
                login_button.click()

                print("Login credentials sent. Waiting for page to redirect...")

                # Wait for the URL to change to confirm a successful login
                # You can also wait for a unique element on the post-login page
                WebDriverWait(self.driver, 10).until(
                    EC.url_changes(self.driver.current_url)
                )

                if "Add Contact Information" in self.driver.title:
                    print('onboarding page acheived')
                    time.sleep(5)
                    element = self.driver.find_element(By.CSS_SELECTOR, "[data-testid='cancel-onboarding-iconbutton']")

                    element.click()
                print("logging done")

            except Exception as e:
                print(f"An error occurred during login: {e}")
                
        else:
            print("Login not required. Page title does not contain 'Login' or 'Sign In'.")

            
    def scrape_monster_jobs(self, job_title="software engineer", location="New York"):
        """Scrape Monster.com - usually very scraper-friendly"""
        print(f"🔍 Scraping Monster for '{job_title}' in '{location}'...")
        
        try:
            # Navigate to Monster
            url = f"https://www.monster.com/jobs/search?q={job_title.replace(' ', '%20')}&where={location.replace(' ', '%20')}"
            
            self.driver.get(url)
            
            # ADDED: Pause after page navigation
            print("Pausing for 15 seconds to allow for manual inspection after page navigation.")
            self.login_if_needed("jaideepgrover147@gmail.com", "Jaideep@123")
            jobs = []
            
            # Wait for job listings
            WebDriverWait(self.driver, 50).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='svx-job-card-component-0']"))
            )
            
            # ADDED: Pause after elements are located
            print("Pausing for 15 seconds to allow for manual inspection after elements are found.")
            time.sleep(15)
            
            # Extract job data
            job_card_parent = self.driver.find_elements(By.CSS_SELECTOR, ".indexmodern__StyledJobCardsContainer-sc-9vl52l-42.hRDWlh")[0]
            job_cards = job_card_parent.find_elements(By.TAG_NAME, "div")
            print(len(job_cards))
            for card in job_cards:
                try:
                    title_ = card.find_element(By.CSS_SELECTOR, "h3")
                    title = title_.get_attribute("aria-label")
                    print(title)
                    
                    jobs.append({
                        'title': title,
                        # 'company': company,
                        # 'location': location,
                        # 'salary': salary,
                        # 'source': 'Monster',
                        # 'scraped_at': datetime.now().isoformat()
                    })
                    apply_button = card.find_element(By.CSS_SELECTOR, "[data-testid='apply-button']")
                    apply_button.click()
                    
                except Exception as e:
                    continue
            parent_tab = self.driver.current_window_handle
            all_tabs = self.driver.window_handles        
            for handle in all_tabs:
                time.sleep(5)
                if handle != parent_tab:
                    self.driver.switch_to.window(handle)
                    print("Already logged in. Proceeding with scraping.")
                        
            return jobs
            
        except Exception as e:
            print(f"❌ Error scraping Monster: {e}")
            return []
            
    def scrape_all_sites(self, job_title="software engineer", location="New York"):
        """Scrape multiple job sites and combine results"""
        print("🚀 Starting multi-site job scraping...")
        
        all_jobs = []
        
        # Scrape each site
        sites_to_scrape = [
            ('Monster', self.scrape_monster_jobs),
            # ('ZipRecruiter', self.scrape_ziprecruiter_jobs),
            # ('Glassdoor', self.scrape_glassdoor_jobs)
        ]
        
        for site_name, scrape_function in sites_to_scrape:
            try:
                print(f"\n📄 Scraping {site_name}...")
                site_jobs = scrape_function(job_title, location)
                all_jobs.extend(site_jobs)
                
                # Delay between sites
                self.human_delay(5, 10)
                
            except Exception as e:
                print(f"❌ Failed to scrape {site_name}: {e}")
                continue
                
        return all_jobs
        
    def save_results(self, jobs):
        """Save results to JSON file"""
        if not jobs:
            print("No jobs found to save")
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alternative_jobs_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 Results saved to {filename}")
        self.print_summary(jobs)
        
    def print_summary(self, jobs):
        """Print scraping summary"""
        print("\n" + "="*60)
        print("                 JOB SCRAPING SUMMARY")
        print("="*60)
        print(f"Total jobs found: {len(jobs)}")
        
        # Group by source
        by_source = {}
        for job in jobs:
            source = job.get('source', 'Unknown')
            by_source[source] = by_source.get(source, 0) + 1
            
        print("\nJobs by source:")
        for source, count in by_source.items():
            print(f"  {source}: {count} jobs")
            
        if jobs:
            print(f"\n📋 Sample Jobs:")
            for i, job in enumerate(jobs[:5], 1):
                print(f"\n{i}. {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Location: {job['location']}")
                print(f"   Source: {job['source']}")
                
    def close(self):
        """Close the driver"""
        if self.driver:
            self.driver.quit()

# Usage example
if __name__ == "__main__":
    scraper = AlternativeJobScraper()
    
    try:
        # Scrape multiple job sites
        all_jobs = scraper.scrape_all_sites(
            job_title="Administrative Assitant",
            location="Remote"
        )
        
        # Save results
        scraper.save_results(all_jobs)
        
    except Exception as e:
        print(f"Scraping failed: {e}")
        
    finally:
        print("\nKeeping browser open for 30 seconds...")
        time.sleep(30)
        scraper.close()
        
    print("\n" + "="*60)
    print("INSTALLATION: pip install undetected-chromedriver selenium")
    print("="*60)