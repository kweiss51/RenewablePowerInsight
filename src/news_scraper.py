"""
Energy News Scraper
Scrapes Google News and Bing for hot energy topics
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import os
from typing import List, Dict
import feedparser
from newspaper import Article
import re

class EnergyNewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.energy_keywords = [
            'renewable energy', 'solar power', 'wind energy', 'battery storage',
            'electric vehicles', 'hydrogen fuel', 'geothermal energy', 'hydroelectric',
            'energy transition', 'carbon neutral', 'green energy', 'clean energy',
            'energy storage', 'nuclear power', 'biomass energy', 'energy efficiency',
            'smart grid', 'energy policy', 'climate change', 'sustainability'
        ]
        
    def scrape_google_news(self, keyword: str, max_articles: int = 10) -> List[Dict]:
        """Scrape Google News RSS feed for energy topics"""
        articles = []
        try:
            # Google News RSS URL
            url = f"https://news.google.com/rss/search?q={keyword.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_articles]:
                article_data = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': getattr(entry, 'summary', ''),
                    'source': 'Google News',
                    'keyword': keyword,
                    'scraped_at': datetime.now().isoformat()
                }
                articles.append(article_data)
                
        except Exception as e:
            print(f"Error scraping Google News for '{keyword}': {e}")
            
        return articles
    
    def scrape_bing_news(self, keyword: str, max_articles: int = 10) -> List[Dict]:
        """Scrape Bing News for energy topics"""
        articles = []
        try:
            url = f"https://www.bing.com/news/search?q={keyword.replace(' ', '+')}&format=rss"
            
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_articles]:
                article_data = {
                    'title': entry.title,
                    'link': entry.link,
                    'published': entry.published,
                    'summary': getattr(entry, 'summary', ''),
                    'source': 'Bing News',
                    'keyword': keyword,
                    'scraped_at': datetime.now().isoformat()
                }
                articles.append(article_data)
                
        except Exception as e:
            print(f"Error scraping Bing News for '{keyword}': {e}")
            
        return articles
    
    def extract_article_content(self, url: str) -> Dict:
        """Extract full article content using newspaper3k"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            return {
                'content': article.text,
                'authors': article.authors,
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'top_image': article.top_image,
                'keywords': article.keywords
            }
        except Exception as e:
            print(f"Error extracting content from {url}: {e}")
            return {}
    
    def get_trending_topics(self) -> List[Dict]:
        """Get all trending energy topics from multiple sources"""
        all_articles = []
        
        print("🔍 Scraping energy news from multiple sources...")
        
        for keyword in self.energy_keywords:
            print(f"  📰 Searching for: {keyword}")
            
            # Scrape Google News
            google_articles = self.scrape_google_news(keyword, max_articles=5)
            all_articles.extend(google_articles)
            
            # Scrape Bing News
            bing_articles = self.scrape_bing_news(keyword, max_articles=5)
            all_articles.extend(bing_articles)
            
            # Rate limiting
            time.sleep(1)
        
        # Remove duplicates based on title similarity
        unique_articles = self.remove_duplicates(all_articles)
        
        print(f"✅ Found {len(unique_articles)} unique articles")
        return unique_articles
    
    def remove_duplicates(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            # Normalize title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article['title']).lower().strip()
            
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    def save_articles(self, articles: List[Dict], filename: str = None):
        """Save articles to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/energy_articles_{timestamp}.json"
        
        os.makedirs("data", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(articles)} articles to {filename}")
        return filename

if __name__ == "__main__":
    scraper = EnergyNewsScraper()
    articles = scraper.get_trending_topics()
    scraper.save_articles(articles)
