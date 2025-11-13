import streamlit as st
import pandas as pd
import json
import time
import io
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page config
st.set_page_config(
    page_title="LinkedIn Profile Scraper",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 4rem;
        font-weight: bold;
        color: #2C3E50;
        text-align: center;
        margin-bottom: 2rem;
        padding: 1rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'profiles_data' not in st.session_state:
    st.session_state.profiles_data = None
if 'scraping_complete' not in st.session_state:
    st.session_state.scraping_complete = False

# Scraper class (embedded)
class LinkedInScraper:
    WAIT_FOR_ELEMENT_TIMEOUT = 5

    def __init__(self, driver):
        self.driver = driver
        self.profiles = []

    def wait_for_element_to_load(self, by=By.CLASS_NAME, name="pv-top-card", base=None):
        base = base or self.driver
        return WebDriverWait(base, self.WAIT_FOR_ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((by, name))
        )

    def is_signed_in(self):
        try:
            return "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url
        except:
            return False

    def scroll_to_half(self):
        self.driver.execute_script("window.scrollTo(0, Math.ceil(document.body.scrollHeight/2));")

    def scroll_to_bottom(self):
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

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
            
            time.sleep(8)
            
            return self.is_signed_in()
        except Exception as e:
            st.error(f"Login error: {e}")
            return False

    def scrape_profile(self, url, progress_callback=None):
        """Scrape a single LinkedIn profile"""
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
            # Get name
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
            
            return profile_data
            
        except Exception as e:
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
                
                for item in items[:5]:
                    try:
                        exp_data = self._parse_experience_item(item)
                        if exp_data:
                            experiences.append(exp_data)
                    except:
                        continue
            except:
                pass
                
        except Exception as e:
            pass
        
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
                
                for item in items[:5]:
                    try:
                        edu_data = self._parse_education_item(item)
                        if edu_data:
                            educations.append(edu_data)
                    except:
                        continue
            except:
                pass
                
        except Exception as e:
            pass
        
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


def convert_to_dataframe(profiles):
    """Convert profiles to DataFrame"""
    rows = []
    for profile in profiles:
        url = profile.get("url", "")
        name = profile.get("name", "")
        headline = profile.get("headline", "")
        location = profile.get("location", "")
        
        experiences = profile.get("experiences", [])
        educations = profile.get("educations", [])
        
        if not experiences and not educations:
            rows.append({
                "URL": url,
                "Name": name,
                "Headline": headline,
                "Location": location,
                "Position Title": "",
                "Company": "",
                "Work From": "",
                "Work To": "",
                "Duration": "",
                "Work Location": "",
                "Education Institution": "",
                "Degree": "",
                "Edu From": "",
                "Edu To": ""
            })
        else:
            max_rows = max(len(experiences), len(educations))
            
            for i in range(max_rows):
                exp = experiences[i] if i < len(experiences) else {}
                edu = educations[i] if i < len(educations) else {}
                
                rows.append({
                    "URL": url,
                    "Name": name,
                    "Headline": headline,
                    "Location": location,
                    "Position Title": exp.get("position_title", ""),
                    "Company": exp.get("company", ""),
                    "Work From": exp.get("from_date", ""),
                    "Work To": exp.get("to_date", ""),
                    "Duration": exp.get("duration", ""),
                    "Work Location": exp.get("location", ""),
                    "Education Institution": edu.get("institution", ""),
                    "Degree": edu.get("degree", ""),
                    "Edu From": edu.get("from_date", ""),
                    "Edu To": edu.get("to_date", "")
                })
    
    return pd.DataFrame(rows)


def create_visualizations(df, profiles):
    """Create data visualizations"""
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Profiles", len(profiles))
    
    with col2:
        total_exp = sum(len(p.get("experiences", [])) for p in profiles)
        st.metric("Total Experiences", total_exp)
    
    with col3:
        total_edu = sum(len(p.get("educations", [])) for p in profiles)
        st.metric("Total Education", total_edu)
    
    with col4:
        unique_locations = df["Location"].nunique()
        st.metric("Unique Locations", unique_locations)
    
    st.markdown("---")
    
    # Visualizations
    viz_col1, viz_col2 = st.columns(2)
    
    with viz_col1:
        st.subheader("📍 Location Distribution")
        location_counts = df[df["Location"] != ""]["Location"].value_counts().head(10)
        if not location_counts.empty:
            fig1 = px.bar(
                x=location_counts.values,
                y=location_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Location'},
                color=location_counts.values,
                color_continuous_scale='Blues'
            )
            fig1.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig1, width='stretch')
        else:
            st.info("No location data available")
    
    with viz_col2:
        st.subheader("🏢 Top Companies")
        company_counts = df[df["Company"] != ""]["Company"].value_counts().head(10)
        if not company_counts.empty:
            fig2 = px.pie(
                values=company_counts.values,
                names=company_counts.index,
                hole=0.4
            )
            fig2.update_layout(height=400)
            st.plotly_chart(fig2, width='stretch')
        else:
            st.info("No company data available")
    
    viz_col3, viz_col4 = st.columns(2)
    
    with viz_col3:
        st.subheader("🎓 Education Institutions")
        edu_counts = df[df["Education Institution"] != ""]["Education Institution"].value_counts().head(10)
        if not edu_counts.empty:
            fig3 = px.bar(
                x=edu_counts.values,
                y=edu_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Institution'},
                color=edu_counts.values,
                color_continuous_scale='Greens'
            )
            fig3.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig3, width='stretch')
        else:
            st.info("No education data available")
    
    with viz_col4:
        st.subheader("💼 Top Job Titles")
        title_counts = df[df["Position Title"] != ""]["Position Title"].value_counts().head(10)
        if not title_counts.empty:
            fig4 = px.bar(
                x=title_counts.values,
                y=title_counts.index,
                orientation='h',
                labels={'x': 'Count', 'y': 'Position'},
                color=title_counts.values,
                color_continuous_scale='Oranges'
            )
            fig4.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig4, width='stretch')
        else:
            st.info("No position data available")


# Main App
st.markdown('<p class="main-header">🔍 LinkedIn Profile Scraper</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Credentials
    st.subheader("🔐 LinkedIn Credentials")
    email = st.text_input("Email", placeholder="your.email@example.com")
    password = st.text_input("Password", type="password", placeholder="Your password")
    
    st.markdown("---")
    
    # URL Input Method
    st.subheader("📥 Input Method")
    input_method = st.radio("Choose input method:", ["Single URL", "Upload JSON File"])
    
    urls_to_scrape = []
    
    if input_method == "Single URL":
        single_url = st.text_input("LinkedIn Profile URL", placeholder="https://www.linkedin.com/in/username")
        if single_url:
            urls_to_scrape = [single_url.strip()]
    else:
        uploaded_file = st.file_uploader("Upload JSON file", type=['json'])
        if uploaded_file is not None:
            try:
                json_data = json.load(uploaded_file)
                urls_to_scrape = json_data.get("urls", [])
                st.success(f"✅ Loaded {len(urls_to_scrape)} URL(s)")
            except Exception as e:
                st.error(f"Error reading JSON: {e}")
    
    st.markdown("---")
    
    # Scrape Button
    scrape_button = st.button("🚀 Start Scraping", type="primary", use_container_width=True)
    
    st.markdown("---")
    st.caption("⚠️ Note: Web scraping may take several minutes. LinkedIn may require 2FA authentication.")

# Main Content
if scrape_button:
    if not email or not password:
        st.error("❌ Please provide LinkedIn credentials in the sidebar!")
    elif not urls_to_scrape:
        st.error("❌ Please provide at least one URL to scrape!")
    else:
        st.info("🔄 Starting scraping process...")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Setup Chrome
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(500)
        driver.set_script_timeout(500)
        
        scraper = LinkedInScraper(driver)
        
        try:
            # Login
            status_text.text("🔐 Logging in to LinkedIn...")
            if not scraper.login(email, password):
                st.error("❌ Login failed! Check your credentials or 2FA settings.")
                driver.quit()
            else:
                st.success("✅ Login successful!")
                
                # Scrape profiles
                profiles = []
                for i, url in enumerate(urls_to_scrape):
                    progress = (i + 1) / len(urls_to_scrape)
                    progress_bar.progress(progress)
                    status_text.text(f"📊 Scraping profile {i+1}/{len(urls_to_scrape)}...")
                    
                    profile_data = scraper.scrape_profile(url)
                    profiles.append(profile_data)
                    time.sleep(3)
                
                # Store in session state
                st.session_state.profiles_data = profiles
                st.session_state.scraping_complete = True
                
                progress_bar.progress(1.0)
                status_text.text("✅ Scraping complete!")
                st.success(f"🎉 Successfully scraped {len(profiles)} profile(s)!")
                
                driver.quit()
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error during scraping: {e}")
            driver.quit()

# Display Results
if st.session_state.scraping_complete and st.session_state.profiles_data:
    st.markdown("---")
    st.header("📊 Scraped Data")
    
    profiles = st.session_state.profiles_data
    df = convert_to_dataframe(profiles)
    
    # Visualizations
    with st.expander("📈 Data Visualizations", expanded=True):
        create_visualizations(df, profiles)
    
    st.markdown("---")
    
    # Data Table
    st.subheader("📋 Profile Data Table")
    
    # Add search/filter functionality
    search_col1, search_col2 = st.columns([3, 1])
    with search_col1:
        search_term = st.text_input("🔍 Search in data", placeholder="Search by name, company, location...")
    with search_col2:
        show_all = st.checkbox("Show all columns", value=False)
    
    # Filter dataframe based on search
    if search_term:
        mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
        filtered_df = df[mask]
        st.info(f"Found {len(filtered_df)} matching record(s)")
    else:
        filtered_df = df
    
    # Display dataframe
    if show_all:
        st.dataframe(filtered_df, width='stretch', height=400)
    else:
        # Show only key columns
        key_columns = ["Name", "Headline", "Location", "Company", "Position Title"]
        available_columns = [col for col in key_columns if col in filtered_df.columns]
        st.dataframe(filtered_df[available_columns], width='stretch', height=400)
        with st.expander("View Full Data"):
            st.dataframe(filtered_df, width='stretch', height=300)
    
    # Individual Profile Details
    st.markdown("---")
    st.subheader("👤 Individual Profile Details")
    
    profile_names = [p.get("name", "Unknown") for p in profiles]
    selected_profile = st.selectbox("Select a profile to view details:", profile_names)
    
    if selected_profile:
        profile = next((p for p in profiles if p.get("name") == selected_profile), None)
        
        if profile:
            detail_col1, detail_col2 = st.columns([1, 2])
            
            with detail_col1:
                st.markdown("**Basic Information**")
                st.write(f"**Name:** {profile.get('name', 'N/A')}")
                st.write(f"**Location:** {profile.get('location', 'N/A')}")
                st.write(f"**Profile URL:** [{profile.get('url', 'N/A')}]({profile.get('url', '#')})")
            
            with detail_col2:
                st.markdown("**Headline**")
                st.write(profile.get('headline', 'N/A'))
            
            # Experience Details
            st.markdown("**💼 Work Experience**")
            experiences = profile.get('experiences', [])
            if experiences:
                for idx, exp in enumerate(experiences, 1):
                    with st.expander(f"Experience {idx}: {exp.get('position_title', 'N/A')}", expanded=(idx==1)):
                        exp_col1, exp_col2 = st.columns(2)
                        with exp_col1:
                            st.write(f"**Position:** {exp.get('position_title', 'N/A')}")
                            st.write(f"**Company:** {exp.get('company', 'N/A')}")
                            st.write(f"**Location:** {exp.get('location', 'N/A')}")
                        with exp_col2:
                            st.write(f"**From:** {exp.get('from_date', 'N/A')}")
                            st.write(f"**To:** {exp.get('to_date', 'N/A')}")
                            st.write(f"**Duration:** {exp.get('duration', 'N/A')}")
            else:
                st.info("No experience data available")
            
            # Education Details
            st.markdown("**🎓 Education**")
            educations = profile.get('educations', [])
            if educations:
                for idx, edu in enumerate(educations, 1):
                    with st.expander(f"Education {idx}: {edu.get('institution', 'N/A')}", expanded=(idx==1)):
                        edu_col1, edu_col2 = st.columns(2)
                        with edu_col1:
                            st.write(f"**Institution:** {edu.get('institution', 'N/A')}")
                            st.write(f"**Degree:** {edu.get('degree', 'N/A')}")
                        with edu_col2:
                            st.write(f"**From:** {edu.get('from_date', 'N/A')}")
                            st.write(f"**To:** {edu.get('to_date', 'N/A')}")
            else:
                st.info("No education data available")
    
    # Download Buttons
    st.markdown("---")
    st.subheader("💾 Download Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV Download
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()
        
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"linkedin_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        # JSON Download
        json_data = json.dumps(profiles, indent=2, ensure_ascii=False)
        
        st.download_button(
            label="📥 Download JSON",
            data=json_data,
            file_name=f"linkedin_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        # Excel Download
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Profiles')
        excel_data = excel_buffer.getvalue()
        
        st.download_button(
            label="📥 Download Excel",
            data=excel_data,
            file_name=f"linkedin_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    # Additional Stats Section
    st.markdown("---")
    st.subheader("📈 Quick Statistics")
    
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        avg_exp = sum(len(p.get("experiences", [])) for p in profiles) / len(profiles) if profiles else 0
        st.metric("Avg. Experiences/Profile", f"{avg_exp:.1f}")
    
    with stat_col2:
        avg_edu = sum(len(p.get("educations", [])) for p in profiles) / len(profiles) if profiles else 0
        st.metric("Avg. Education/Profile", f"{avg_edu:.1f}")
    
    with stat_col3:
        profiles_with_exp = sum(1 for p in profiles if p.get("experiences", []))
        st.metric("Profiles with Experience", profiles_with_exp)
    
    with stat_col4:
        profiles_with_edu = sum(1 for p in profiles if p.get("educations", []))
        st.metric("Profiles with Education", profiles_with_edu)
    
    # Clear Data Button
    st.markdown("---")
    col_clear1, col_clear2, col_clear3 = st.columns([1, 1, 1])
    with col_clear2:
        if st.button("🗑️ Clear All Data & Start Over", type="secondary", use_container_width=True):
            st.session_state.profiles_data = None
            st.session_state.scraping_complete = False
            st.rerun()

else:
    # Welcome message
    st.info("""
    👋 **Welcome to LinkedIn Profile Scraper!**
    
    **How to use:**
    1. 🔐 Enter your LinkedIn credentials in the sidebar
    2. 📥 Choose to scrape a single URL or upload a JSON file with multiple URLs
    3. 🚀 Click "Start Scraping" and wait for the process to complete
    4. 📊 View visualizations and download the scraped data
    
    **JSON File Format:**
    ```json
    {
      "urls": [
        "https://www.linkedin.com/in/user1",
        "https://www.linkedin.com/in/user2"
      ]
    }
    ```
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>Made with ❤️ using Streamlit | ⚠️ Use responsibly and respect LinkedIn's Terms of Service</p>
    <p style='font-size: 12px; margin-top: 10px;'>
        <strong>Disclaimer:</strong> This tool is for educational purposes. 
        Ensure compliance with LinkedIn's terms and applicable data protection laws.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar footer with tips
with st.sidebar:
    st.markdown("---")
    with st.expander("💡 Tips & Troubleshooting"):
        st.markdown("""
        **Common Issues:**
        
        1. **Login Fails:**
           - Check credentials
           - Disable 2FA temporarily
           - Try from a known IP
        
        2. **Scraping Slow:**
           - Normal for many profiles
           - LinkedIn has rate limits
           - Be patient
        
        3. **Missing Data:**
           - Profile may be private
           - Data not available
           - Connection required
        
        **Best Practices:**
        - Scrape during off-peak hours
        - Limit to 10-20 profiles per session
        - Add delays between requests
        - Use from consistent IP address
        """)
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; font-size: 12px; color: #888;'>
        <p>Version 1.0.0</p>
        <p>Last Updated: Nov 2024</p>
    </div>
    """, unsafe_allow_html=True)