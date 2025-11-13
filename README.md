# LinkedIn Profile Scraper

A powerful Python-based LinkedIn profile scraper that extracts comprehensive profile data including personal information, work experience, and education details. The scraper is available in two formats: a **command-line script** (`Scrapper.py`) and a **web-based Streamlit application** (`app.py`) with interactive visualizations. Both save data in CSV, JSON, and Excel formats for easy analysis.

## 🚀 Features

- **Two Interface Options**:
  - **CLI Script** (`Scrapper.py`): Command-line interface for automated batch processing
  - **Web App** (`app.py`): Interactive Streamlit web interface with visualizations
- **Automated Login**: Secure login with credentials (hardcoded in CLI, input in web app)
- **Comprehensive Data Extraction**: 
  - Name, headline, location
  - Work experience (position, company, dates, duration, location)
  - Education (institution, degree, dates)
- **Multiple Output Formats**: CSV, JSON, and Excel (Excel only in web app)
- **Interactive Visualizations** (Web App Only):
  - Location distribution charts
  - Top companies pie chart
  - Education institutions bar chart
  - Job titles analysis
  - Quick statistics dashboard
- **Bulk Processing**: Process multiple profiles from a URL list or single URL input
- **Error Handling**: Robust error handling with detailed logging
- **Configurable Timeouts**: Extended timeouts for reliable scraping
- **Search & Filter**: Search functionality in the web app data table

## 📋 Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- ChromeDriver (automatically managed by Selenium)
- Streamlit (for web app): `pip install streamlit`

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd linkedin-scraper
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```


## ⚙️ Configuration

### For CLI Script (Scrapper.py)

#### 1. Set Up Credentials
Edit the credentials in `Scrapper.py`:

```python
# === HARDCODED CREDENTIALS ===
EMAIL = "your-email@example.com"
PASSWORD = "your-password"
```

#### 2. Create URLs Configuration
Create a `urls.json` file with LinkedIn profile URLs:
```json
{
  "urls": [
    "https://www.linkedin.com/in/example-profile-1",
    "https://www.linkedin.com/in/example-profile-2",
    "https://www.linkedin.com/in/example-profile-3"
  ]
}
```

### For Web App (app.py)

**No configuration needed!** The web app provides:
- **Interactive credential input** in the sidebar (no hardcoding required)
- **Flexible URL input**: Enter single URL or upload JSON file directly in the UI
- **No file editing required**: Everything is configured through the web interface

## 🚀 Usage

### Option 1: Command-Line Interface (CLI)

Run the scraper script directly:

```bash
python Scrapper.py
```

**What Happens:**
1. **Login**: Automatically logs into LinkedIn using hardcoded credentials
2. **Profile Processing**: Visits each URL from `urls.json`
3. **Data Extraction**: Scrapes profile information
4. **Data Export**: Saves to `linkedin_profiles.csv` and `linkedin_profiles.json`

### Option 2: Web Application (Streamlit)

Launch the interactive web interface:

```bash
streamlit run app.py
```

The app will open in your default web browser (typically at `http://localhost:8501`).

**Web App Features:**
1. **Interactive UI**: User-friendly interface with sidebar configuration
2. **Flexible Input**: 
   - Enter a single LinkedIn profile URL
   - Upload a JSON file with multiple URLs
3. **Real-time Progress**: Progress bar and status updates during scraping
4. **Data Visualizations**: 
   - Location distribution charts
   - Top companies analysis
   - Education institutions overview
   - Job titles statistics
5. **Data Exploration**: 
   - Searchable data table
   - Individual profile details viewer
   - Quick statistics dashboard
6. **Export Options**: Download data as CSV, JSON, or Excel files
7. **Session Management**: Data persists in session until cleared

**Web App Workflow:**
1. Enter your LinkedIn credentials in the sidebar
2. Choose input method (Single URL or Upload JSON File)
3. Click "Start Scraping"
4. View visualizations and explore the scraped data
5. Download data in your preferred format

## 📁 Project Structure

```
linkedin-scraper/
├── Scrapper.py          # CLI scraper script
├── app.py               # Streamlit web application
├── object.py            # Data classes and base scraper
├── urls.json            # Profile URLs to scrape (for CLI)
├── requirements.txt     # Python dependencies
├── linkedin_profiles.csv    # Output CSV file
├── linkedin_profiles.json   # Output JSON file
├── Grok.py             # Alternative scraper (legacy)
└── README.md           # This file
```

## 📊 Output Format

### CSV Output
The CSV file contains detailed information with columns:
- URL, Name, Headline, Location
- Position Title, Company, Work From, Work To, Duration, Work Location
- Education Institution, Degree, Edu From, Edu To

### JSON Output
The JSON file contains structured data:
```json
[
  {
    "url": "https://www.linkedin.com/in/example",
    "name": "John Doe",
    "headline": "Software Engineer at Tech Company",
    "location": "San Francisco, CA",
    "experiences": [
      {
        "position_title": "Software Engineer",
        "company": "Tech Company",
        "from_date": "Jan 2022",
        "to_date": "Present",
        "duration": "2 yrs",
        "location": "San Francisco, CA"
      }
    ],
    "educations": [
      {
        "institution": "University Name",
        "degree": "Bachelor of Science",
        "from_date": "2018",
        "to_date": "2022"
      }
    ]
  }
]
```

## 🔧 Configuration Options

### Timeout Settings
The scraper uses extended timeouts for reliability:
- Page load timeout: 500 seconds
- Script timeout: 500 seconds
- Element wait timeout: 10 seconds

### Browser Options
- User agent spoofing
- Headless mode (optional)
- No sandbox mode for compatibility

## 📝 Example urls.json

Here's a complete example of the `urls.json` file with real LinkedIn profiles:

```json
{
  "urls": [
    "https://www.linkedin.com/in/satya-nadella",
    "https://www.linkedin.com/in/sundarpichai",
    "https://www.linkedin.com/in/jeffweiner08",
    "https://www.linkedin.com/in/reidhoffman",
    "https://www.linkedin.com/in/williamhgates",
  ]
}
```

**Note**: Copy this content into your `urls.json` file to get started with real profiles. You can modify the list to include any LinkedIn profiles you want to scrape.

## ⚠️ Important Notes

### Legal and Ethical Considerations
- **Respect LinkedIn's Terms of Service**
- **Use responsibly**: Don't overload LinkedIn's servers
- **Rate limiting**: Built-in delays between requests
- **Personal use**: Intended for personal research and analysis

### Best Practices
- Use a dedicated LinkedIn account for scraping
- Keep the number of profiles reasonable (< 100 per session)
- Run during off-peak hours
- Monitor for rate limiting or blocking

## 🐛 Troubleshooting

### Common Issues

**Login Failed**
- **CLI**: Check credentials in `Scrapper.py`
- **Web App**: Verify credentials entered in sidebar
- Verify 2FA is disabled or handle manually
- Check for LinkedIn security challenges

**ChromeDriver Issues**
- Ensure Chrome browser is installed
- Update Chrome to the latest version
- ChromeDriver is managed automatically by Selenium

**Element Not Found**
- LinkedIn may have updated their HTML structure
- Check console output for specific errors
- Some profiles may have privacy settings that block scraping

**Timeout Errors**
- Increase timeout values if needed
- Check internet connection
- LinkedIn may be experiencing slow response times

## 📈 Performance Tips

- **Headless Mode**: Web app runs in headless mode by default for faster execution
- **Batch Processing**: Process profiles in smaller batches (< 20 profiles per session recommended)
- **Web App**: Use the search functionality to quickly find specific profiles in large datasets
- **Visualizations**: Web app provides instant insights without manual data analysis

## 🎨 Web App Screenshots & Features

The Streamlit web application (`app.py`) provides:

- **📊 Interactive Dashboard**: Real-time metrics and statistics
- **📈 Data Visualizations**: 
  - Bar charts for locations and education
  - Pie charts for company distribution
  - Horizontal bar charts for job titles
- **🔍 Search Functionality**: Filter and search through scraped data
- **💾 Multiple Export Formats**: CSV, JSON, and Excel downloads
- **👤 Profile Details**: Expandable sections for individual profile information
- **📱 Responsive Design**: Works on different screen sizes


