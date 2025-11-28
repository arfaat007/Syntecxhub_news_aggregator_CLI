# 📰 News Aggregator CLI

A Python-based News Aggregator tool that fetches the latest headlines from multiple news sources, stores them in a local SQLite database, and allows querying or exporting articles in different formats.

This tool currently supports:
- 📎 BBC News scraping (BeautifulSoup)
- 🔑 NewsAPI integration (optional API key required)
- 🗃 Article storage using SQLite
- 🔍 Querying by Source, Keyword, and Date
- 📤 Export to JSON, CSV, or Excel

---

## 🚀 Features

- Fetch real-time news headlines
- Automatically remove duplicate articles
- Store articles persistently with a timestamp
- Flexible search filters
- Export data for analysis or reporting

---

## 🛠️ Technologies Used

| Component | Technology |
|----------|------------|
| Web Scraping | BeautifulSoup4 |
| API Integration | NewsAPI |
| Database | SQLite |
| CLI Interface | argparse |
| Export Formats | JSON, CSV, Excel (Pandas) |

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/arfaat007/news-aggregator.git
cd news-aggregator


🔧 Usage
1️⃣ Fetch Articles

Fetch BBC News only:

python news_aggregator.py fetch


Fetch using NewsAPI:

python news_aggregator.py fetch --api-key YOUR_API_KEY


Fetch with keyword filtering:

python news_aggregator.py fetch --api-key YOUR_API_KEY --keyword technology

2️⃣ Query Articles

Filter by source:

python news_aggregator.py query --source "BBC"


Filter by keyword:

python news_aggregator.py query --keyword "AI"


Filter by date (YYYY-MM-DD):

python news_aggregator.py query --date 2025-01-01

3️⃣ Export Articles

Export to JSON (default):

python news_aggregator.py export


Export to CSV:

python news_aggregator.py export --format csv --output articles.csv


Export to Excel:

python news_aggregator.py export --format excel --output news.xlsx

📂 File Structure
📁 news-aggregator
├── 📄 news_aggregator.py
├── 📄 requirements.txt
└── README.md

🔐 API Key (Optional)

Create a free API key at:
https://newsapi.org/

📝 Future Enhancements

More news sources (CNN, Reuters, etc.)

GUI/Web Dashboard

Automated daily fetch scheduler

ML-powered duplicate detection
