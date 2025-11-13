# LinkedIn Profile Scraper

A powerful Python-based LinkedIn profile scraper that extracts comprehensive profile data including personal information, work experience, and education details. The scraper saves data in both CSV and JSON formats for easy analysis.

## 🚀 Features

- **Automated Login**: Secure login with hardcoded credentials
- **Comprehensive Data Extraction**: 
  - Name, headline, location
  - Work experience (position, company, dates, duration, location)
  - Education (institution, degree, dates)
- **Multiple Output Formats**: CSV and JSON
- **Bulk Processing**: Process multiple profiles from a URL list
- **Error Handling**: Robust error handling with detailed logging
- **Configurable Timeouts**: Extended timeouts for reliable scraping

## 📋 Prerequisites

- Python 3.7 or higher
- Chrome browser installed
- ChromeDriver (automatically managed by Selenium)

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

### 1. Set Up Credentials
Edit the credentials in `Scrapper.py`:

```python
# === HARDCODED CREDENTIALS ===
EMAIL = "your-email@example.com"
PASSWORD = "your-password"
```

### 2. Create URLs Configuration
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

## 🚀 Usage

### Basic Usage
```bash
python Scrapper.py
```

### What Happens:
1. **Login**: Automatically logs into LinkedIn
2. **Profile Processing**: Visits each URL from `urls.json`
3. **Data Extraction**: Scrapes profile information
4. **Data Export**: Saves to `linkedin_profiles.csv` and `linkedin_profiles.json`

## 📁 Project Structure

```
linkedin-scraper/
├── Scrapper.py          # Main scraper script
├── object.py            # Data classes and base scraper
├── urls.json            # Profile URLs to scrape
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
- Check credentials in `Scrapper.py`
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

- **Headless Mode**: Uncomment headless option for faster execution
- **Batch Processing**: Process profiles in smaller batches


