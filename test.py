import csv
import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from object import Experience, Education, Scraper

# === HARDCODED CREDENTIALS ===
EMAIL = ""
PASSWORD = ""

# === Load URLs from urls.json ===
def load_urls_from_json():
    try:
        with open("urls.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        urls = data.get("urls", [])
        if not isinstance(urls, list):
            print("Invalid urls.json: 'urls' must be a list")
            return []
        return [u.strip() for u in urls if isinstance(u, str) and u.strip()]
    except FileNotFoundError:
        print("urls.json not found. Create it with {\"urls\": [ ... ]}")
        return []
    except Exception as e:
        print(f"Failed to read urls.json: {e}")
        return []


class LinkedInScraper(Scraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.profiles = []

    def login(self, email, password):
        """Login to LinkedIn"""
        self.driver.get("https://www.linkedin.com/login")
        time.sleep(3)
        
        try:
            username_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            username_field.send_keys(email)
            
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            submit_button.click()
            
            print("Logging in...")
            time.sleep(8)
            
            if self.is_signed_in():
                print("✓ LOGIN SUCCESS!")
                return True
            else:
                print("✗ Login failed! Check credentials or 2FA.")
                return False
        except Exception as e:
            print(f"✗ Login error: {e}")
            return False

    def scrape_profile(self, url):
        """Scrape a single LinkedIn profile"""
        print(f"\n→ Scraping: {url}")
        self.driver.get(url)
        time.sleep(5)
        
        profile_data = {
            "url": url,
            "name": None,
            "headline": None,
            "location": None,
            "experiences": [],
            "educations": []
        }
        
        try:
            # Get name and location
            try:
                name = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                ).text
                profile_data["name"] = name
            except:
                profile_data["name"] = "N/A"
            
            # Get headline
            try:
                headline = self.driver.find_element(
                    By.XPATH, 
                    "//div[contains(@class, 'text-body-medium')]"
                ).text
                profile_data["headline"] = headline
            except:
                profile_data["headline"] = "N/A"
            
            # Get location
            try:
                location = self.driver.find_element(
                    By.XPATH, 
                    "//span[contains(@class, 'text-body-small') and contains(@class, 'inline')]"
                ).text
                profile_data["location"] = location
            except:
                profile_data["location"] = "N/A"
            
            # Scroll to load more content
            self.scroll_to_half()
            time.sleep(2)
            self.scroll_to_bottom()
            time.sleep(2)
            
            # Get experiences
            profile_data["experiences"] = self.get_experiences(url)
            
            # Get education
            profile_data["educations"] = self.get_educations(url)
            
            print(f"✓ Scraped: {profile_data['name']}")
            return profile_data
            
        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            profile_data["error"] = str(e)
            return profile_data

    def get_experiences(self, base_url):
        """Get experience details"""
        experiences = []
        try:
            exp_url = base_url.rstrip('/') + "/details/experience"
            self.driver.get(exp_url)
            time.sleep(3)
            
            main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
            self.scroll_to_bottom()
            time.sleep(2)
            
            try:
                main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
                items = main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item")
                
                for item in items[:5]:  # Limit to 5 experiences
                    try:
                        exp_data = self._parse_experience_item(item)
                        if exp_data:
                            experiences.append(exp_data)
                    except:
                        continue
            except:
                pass
                
        except Exception as e:
            print(f"  Warning: Could not fetch experiences - {e}")
        
        return experiences

    def _parse_experience_item(self, item):
        """Parse a single experience item"""
        try:
            position = item.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
            elements = position.find_elements(By.XPATH, "*")
            
            if len(elements) < 2:
                return None
            
            position_details = elements[1]
            position_details_list = position_details.find_elements(By.XPATH, "*")
            
            if not position_details_list:
                return None
            
            position_summary = position_details_list[0]
            outer_positions = position_summary.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
            
            # Extract basic info
            position_title = ""
            company = ""
            work_times = ""
            location = ""
            
            if len(outer_positions) >= 2:
                try:
                    position_title = outer_positions[0].find_element(By.TAG_NAME, "span").text
                except:
                    pass
                try:
                    company = outer_positions[1].find_element(By.TAG_NAME, "span").text
                except:
                    pass
                if len(outer_positions) >= 3:
                    try:
                        work_times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                    except:
                        pass
                if len(outer_positions) >= 4:
                    try:
                        location = outer_positions[3].find_element(By.TAG_NAME, "span").text
                    except:
                        pass
            
            # Parse dates
            from_date = ""
            to_date = ""
            duration = None
            
            if work_times and "·" in work_times:
                parts = work_times.split("·")
                times = parts[0].strip()
                duration = parts[1].strip() if len(parts) > 1 else None
                
                time_parts = times.split(" ")
                if len(time_parts) >= 2:
                    from_date = " ".join(time_parts[:2])
                if len(time_parts) >= 4:
                    to_date = " ".join(time_parts[3:])
            
            return {
                "position_title": position_title or "N/A",
                "company": company or "N/A",
                "from_date": from_date,
                "to_date": to_date,
                "duration": duration,
                "location": location
            }
        except:
            return None

    def get_educations(self, base_url):
        """Get education details"""
        educations = []
        try:
            edu_url = base_url.rstrip('/') + "/details/education"
            self.driver.get(edu_url)
            time.sleep(3)
            
            main = self.wait_for_element_to_load(by=By.TAG_NAME, name="main")
            self.scroll_to_bottom()
            time.sleep(2)
            
            try:
                main_list = self.wait_for_element_to_load(name="pvs-list__container", base=main)
                items = main_list.find_elements(By.CLASS_NAME, "pvs-list__paged-list-item")
                
                for item in items[:5]:  # Limit to 5 educations
                    try:
                        edu_data = self._parse_education_item(item)
                        if edu_data:
                            educations.append(edu_data)
                    except:
                        continue
            except:
                pass
                
        except Exception as e:
            print(f"  Warning: Could not fetch education - {e}")
        
        return educations

    def _parse_education_item(self, item):
        """Parse a single education item"""
        try:
            position = item.find_element(By.CSS_SELECTOR, "div[data-view-name='profile-component-entity']")
            elements = position.find_elements(By.XPATH, "*")
            
            if len(elements) < 2:
                return None
            
            position_details = elements[1]
            position_details_list = position_details.find_elements(By.XPATH, "*")
            
            if not position_details_list:
                return None
            
            position_summary = position_details_list[0]
            outer_positions = position_summary.find_element(By.XPATH, "*").find_elements(By.XPATH, "*")
            
            institution_name = ""
            degree = ""
            from_date = ""
            to_date = ""
            
            if outer_positions:
                try:
                    institution_name = outer_positions[0].find_element(By.TAG_NAME, "span").text
                except:
                    pass
                
                if len(outer_positions) > 1:
                    try:
                        degree = outer_positions[1].find_element(By.TAG_NAME, "span").text
                    except:
                        pass
                
                if len(outer_positions) > 2:
                    try:
                        times = outer_positions[2].find_element(By.TAG_NAME, "span").text
                        if times and "-" in times:
                            time_parts = times.split()
                            if "-" in time_parts:
                                dash_idx = time_parts.index("-")
                                if dash_idx > 0:
                                    from_date = time_parts[dash_idx - 1]
                                if dash_idx < len(time_parts) - 1:
                                    to_date = time_parts[-1]
                    except:
                        pass
            
            return {
                "institution": institution_name or "N/A",
                "degree": degree or "N/A",
                "from_date": from_date,
                "to_date": to_date
            }
        except:
            return None

    def save_to_csv(self, filename="linkedin_profiles.csv"):
        """Save scraped data to CSV with detailed experience and education"""
        if not self.profiles:
            print("No profiles to save!")
            return
        
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "URL", "Name", "Headline", "Location",
                "Position Title", "Company", "Work From", "Work To", "Duration", "Work Location",
                "Education Institution", "Degree", "Edu From", "Edu To"
            ])
            
            # Data rows - one row per experience/education combination
            for profile in self.profiles:
                url = profile.get("url", "")
                name = profile.get("name", "")
                headline = profile.get("headline", "")
                location = profile.get("location", "")
                
                experiences = profile.get("experiences", [])
                educations = profile.get("educations", [])
                
                # If no experience or education, still write one row with basic info
                if not experiences and not educations:
                    writer.writerow([
                        url, name, headline, location,
                        "", "", "", "", "", "",
                        "", "", "", ""
                    ])
                else:
                    # Create rows for each experience
                    max_rows = max(len(experiences), len(educations))
                    
                    for i in range(max_rows):
                        # Experience data
                        exp = experiences[i] if i < len(experiences) else {}
                        position = exp.get("position_title", "")
                        company = exp.get("company", "")
                        work_from = exp.get("from_date", "")
                        work_to = exp.get("to_date", "")
                        duration = exp.get("duration", "")
                        work_location = exp.get("location", "")
                        
                        # Education data
                        edu = educations[i] if i < len(educations) else {}
                        institution = edu.get("institution", "")
                        degree = edu.get("degree", "")
                        edu_from = edu.get("from_date", "")
                        edu_to = edu.get("to_date", "")
                        
                        writer.writerow([
                            url, name, headline, location,
                            position, company, work_from, work_to, duration, work_location,
                            institution, degree, edu_from, edu_to
                        ])
        
        print(f"\n✓ CSV saved: {filename}")

    def save_to_json(self, filename="linkedin_profiles.json"):
        """Save scraped data to JSON"""
        if not self.profiles:
            print("No profiles to save!")
            return
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, indent=2, ensure_ascii=False)
        
        print(f"✓ JSON saved: {filename}")


def main():
    print("=" * 60)
    print("LinkedIn Profile Scraper")
    print("=" * 60)
    
    # Load URLs
    urls = load_urls_from_json()
    if not urls:
        print("\n✗ No URLs found in urls.json. Exiting.")
        return
    
    print(f"\n✓ Loaded {len(urls)} URL(s) from urls.json")
    
    # Setup Chrome
    print("\n→ Starting Chrome...")
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")  # Uncomment to run headless
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
    
    driver = webdriver.Chrome(options=chrome_options)
    # Increase HTTP-related timeouts
    driver.set_page_load_timeout(500)
    driver.set_script_timeout(500)
    scraper = LinkedInScraper(driver)
    
    try:
        # Login
        if not scraper.login(EMAIL, PASSWORD):
            print("\n✗ Login failed. Exiting.")
            driver.quit()
            return
        
        # Scrape profiles
        print(f"\n→ Scraping {len(urls)} profile(s)...")
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}]", end=" ")
            profile_data = scraper.scrape_profile(url)
            scraper.profiles.append(profile_data)
            time.sleep(3)  # Be polite
        
        # Save results
        print("\n" + "=" * 60)
        scraper.save_to_csv("linkedin_profiles.csv")
        scraper.save_to_json("linkedin_profiles.json")
        
        print("\n✓ DONE! Check linkedin_profiles.csv and linkedin_profiles.json")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        driver.quit()
        print("\n→ Browser closed.")


if __name__ == "__main__":
    main()
