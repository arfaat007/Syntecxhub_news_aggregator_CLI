import argparse
import json
import sqlite3
import csv
from datetime import datetime
from typing import List, Dict
import requests
from bs4 import BeautifulSoup
import pandas as pd

class NewsAggregator:
    def __init__(self, db_path='news.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                source TEXT NOT NULL,
                url TEXT UNIQUE,
                date TEXT,
                description TEXT,
                fetched_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def fetch_bbc_news(self) -> List[Dict]:
        """Scrape BBC News headlines"""
        articles = []
        try:
            url = 'https://www.bbc.com/news'
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(response.content, 'html.parser')
            
            headlines = soup.find_all('h2', {'data-testid': 'card-headline'})
            
            for headline in headlines[:20]:
                link = headline.find_parent('a')
                title = headline.get_text().strip()
                article_url = link['href'] if link else ''
                
                if article_url and not article_url.startswith('http'):
                    article_url = f'https://www.bbc.com{article_url}'
                
                articles.append({
                    'title': title,
                    'source': 'BBC News',
                    'url': article_url,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'description': ''
                })
        except Exception as e:
            print(f"Error fetching BBC News: {e}")
        
        return articles
    
    def fetch_newsapi(self, api_key: str, query: str = None) -> List[Dict]:
        """Fetch news from NewsAPI"""
        articles = []
        try:
            base_url = 'https://newsapi.org/v2/top-headlines'
            params = {
                'apiKey': api_key,
                'language': 'en',
                'pageSize': 20
            }
            
            if query:
                params['q'] = query
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if data.get('status') == 'ok':
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'source': article.get('source', {}).get('name', 'Unknown'),
                        'url': article.get('url', ''),
                        'date': article.get('publishedAt', '')[:10],
                        'description': article.get('description', '')
                    })
        except Exception as e:
            print(f"Error fetching NewsAPI: {e}")
        
        return articles
    
    def deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        seen_titles = set()
        unique_articles = []
        
        for article in articles:
            title_lower = article['title'].lower().strip()
            if title_lower not in seen_titles and title_lower:
                seen_titles.add(title_lower)
                unique_articles.append(article)
        
        return unique_articles
    
    def store_articles(self, articles: List[Dict]):
        """Store articles in SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stored_count = 0
        for article in articles:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO articles (title, source, url, date, description, fetched_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    article['title'],
                    article['source'],
                    article['url'],
                    article['date'],
                    article['description'],
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ))
                if cursor.rowcount > 0:
                    stored_count += 1
            except Exception as e:
                print(f"Error storing article: {e}")
        
        conn.commit()
        conn.close()
        print(f"Stored {stored_count} new articles")
    
    def query_articles(self, source: str = None, keyword: str = None, date: str = None) -> List[Dict]:
        """Query articles from database with filters"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT title, source, url, date, description FROM articles WHERE 1=1"
        params = []
        
        if source:
            query += " AND LOWER(source) LIKE ?"
            params.append(f"%{source.lower()}%")
        
        if keyword:
            query += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
            params.extend([f"%{keyword.lower()}%", f"%{keyword.lower()}%"])
        
        if date:
            query += " AND date = ?"
            params.append(date)
        
        query += " ORDER BY date DESC, id DESC"
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in results:
            articles.append({
                'title': row[0],
                'source': row[1],
                'url': row[2],
                'date': row[3],
                'description': row[4]
            })
        
        return articles
    
    def export_to_json(self, articles: List[Dict], filename: str):
        """Export articles to JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(articles)} articles to {filename}")
    
    def export_to_csv(self, articles: List[Dict], filename: str):
        """Export articles to CSV"""
        if not articles:
            print("No articles to export")
            return
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'source', 'url', 'date', 'description'])
            writer.writeheader()
            writer.writerows(articles)
        print(f"Exported {len(articles)} articles to {filename}")
    
    def export_to_excel(self, articles: List[Dict], filename: str):
        """Export articles to Excel"""
        if not articles:
            print("No articles to export")
            return
        
        df = pd.DataFrame(articles)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Exported {len(articles)} articles to {filename}")

def main():
    parser = argparse.ArgumentParser(description='News Aggregator CLI')
    parser.add_argument('command', choices=['fetch', 'query', 'export'], help='Command to execute')
    parser.add_argument('--source', help='Filter by source name')
    parser.add_argument('--keyword', help='Filter by keyword')
    parser.add_argument('--date', help='Filter by date (YYYY-MM-DD)')
    parser.add_argument('--api-key', help='NewsAPI key for fetching')
    parser.add_argument('--format', choices=['json', 'csv', 'excel'], default='json', help='Export format')
    parser.add_argument('--output', help='Output filename')
    
    args = parser.parse_args()
    aggregator = NewsAggregator()
    
    if args.command == 'fetch':
        print("Fetching news articles...")
        articles = []
        
        # Fetch from BBC
        print("Fetching from BBC News...")
        articles.extend(aggregator.fetch_bbc_news())
        
        # Fetch from NewsAPI if key provided
        if args.api_key:
            print("Fetching from NewsAPI...")
            articles.extend(aggregator.fetch_newsapi(args.api_key, args.keyword))
        
        # Deduplicate and store
        articles = aggregator.deduplicate(articles)
        print(f"Found {len(articles)} unique articles")
        aggregator.store_articles(articles)
    
    elif args.command == 'query':
        print("Querying articles...")
        articles = aggregator.query_articles(args.source, args.keyword, args.date)
        print(f"\nFound {len(articles)} articles:\n")
        
        for i, article in enumerate(articles[:10], 1):
            print(f"{i}. [{article['source']}] {article['title']}")
            print(f"   Date: {article['date']}")
            print(f"   URL: {article['url']}\n")
        
        if len(articles) > 10:
            print(f"... and {len(articles) - 10} more")
    
    elif args.command == 'export':
        print("Exporting articles...")
        articles = aggregator.query_articles(args.source, args.keyword, args.date)
        
        if not args.output:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            args.output = f"news_export_{timestamp}.{args.format}"
        
        if args.format == 'json':
            aggregator.export_to_json(articles, args.output)
        elif args.format == 'csv':
            aggregator.export_to_csv(articles, args.output)
        elif args.format == 'excel':
            aggregator.export_to_excel(articles, args.output)

if __name__ == '__main__':
    main()