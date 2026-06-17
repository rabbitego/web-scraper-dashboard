# Web Scraper & Dashboard

A Python web scraper that collects headlines from Hacker News, analyzes the data with Pandas, and displays interactive charts on a live dashboard.

## Features

- **Web Scraping** - Scrapes Hacker News for top headlines using BeautifulSoup
- **Data Storage** - Saves articles to CSV and JSON files
- **Data Analysis** - Analyzes source distribution, trending words, and title patterns
- **Live Dashboard** - Flask web app with interactive Plotly charts
- **Accumulating Data** - Each scrape adds to the dataset for richer analysis over time

## Tech Stack

- **BeautifulSoup4** - HTML parsing and web scraping
- **Requests** - HTTP requests
- **Pandas** - Data analysis and manipulation
- **Plotly** - Interactive charts and visualizations
- **Flask** - Web dashboard

## Quick Start

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/web-scraper-dashboard.git
cd web-scraper-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the Scraper (CLI)

```bash
# Scrape headlines and save to data/
python -m scraper.news_scraper
```

### Run the Analyzer

```bash
# Analyze collected data
python -m scraper.analyzer
```

### Launch the Dashboard

```bash
# Start the web dashboard
python -m dashboard.app
```

Open `http://localhost:5000` in your browser.

## Project Structure

```
web-scraper-dashboard/
├── scraper/
│   ├── news_scraper.py    # Scrapes Hacker News headlines
│   └── analyzer.py        # Analyzes scraped data with Pandas
├── dashboard/
│   └── app.py             # Flask web dashboard with Plotly charts
├── data/                  # Scraped data stored here (gitignored)
├── tests/
│   └── test_scraper.py    # Unit tests
├── requirements.txt
└── README.md
```

## Dashboard Preview

The dashboard shows:
- **Stats cards** - Total articles, unique sources, top source
- **Source distribution chart** - Which domains appear most
- **Trending words chart** - Most common words in headlines
- **Article list** - Latest scraped headlines with links

## Running Tests

```bash
pytest tests/ -v
```

## How It Works

1. The scraper sends a request to Hacker News and parses the HTML
2. It extracts article titles, URLs, and source domains
3. Data is saved to timestamped CSV/JSON files
4. The analyzer loads all CSV files and computes statistics
5. The dashboard scrapes fresh data on each visit and renders charts
