"""
Energy News Data Collector
Enhanced scraper for collecting training data for our custom LLM
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import os
from typing import List, Dict, Tuple
import feedparser
from newspaper import Article
import re
import pandas as pd
from pathlib import Path
import hashlib
from urllib.parse import urljoin, urlparse
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NewsArticle:
    """Data class for news articles"""
    title: str
    content: str
    url: str
    published_date: str
    source: str
    keywords: List[str]
    category: str
    scraped_at: str
    content_hash: str
    word_count: int
    quality_score: float

class EnergyDataCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Expanded energy keywords for comprehensive coverage
        self.energy_keywords = [
            # Core renewable energy
            'renewable energy', 'solar power', 'wind energy', 'hydroelectric',
            'geothermal energy', 'biomass energy', 'tidal energy', 'wave energy',
            
            # Technology and innovation
            'battery storage', 'energy storage', 'lithium battery', 'hydrogen fuel',
            'fuel cell', 'smart grid', 'microgrid', 'energy efficiency',
            'carbon capture', 'nuclear fusion', 'thorium reactor',
            
            # Electric mobility
            'electric vehicles', 'EV charging', 'electric cars', 'battery technology',
            'charging infrastructure', 'autonomous vehicles', 'electric trucks',
            
            # Policy and markets
            'energy policy', 'carbon tax', 'renewable portfolio standard',
            'net metering', 'feed-in tariff', 'energy transition', 'decarbonization',
            'climate change', 'paris agreement', 'carbon neutral', 'net zero',
            
            # Industries and companies
            'tesla energy', 'solar panels', 'wind turbines', 'energy companies',
            'utility companies', 'renewable investment', 'green bonds',
            'ESG investing', 'sustainable finance',
            
            # Regional and global trends
            'offshore wind', 'floating solar', 'agrivoltaics', 'energy independence',
            'grid modernization', 'demand response', 'virtual power plant'
        ]
        
        # Energy news sources (RSS feeds and websites)
        self.news_sources = {
            'rss_feeds': [
                'https://www.greentechmedia.com/rss',
                'https://www.renewableenergyworld.com/feeds/rss',
                'https://www.utilitydive.com/rss/',
                'https://www.energycentral.com/rss',
                'https://www.pv-magazine.com/feed/',
                'https://www.windpowermonthly.com/rss',
                'https://www.energystoragenews.com/feed/',
                'https://electrek.co/feed/',
                'https://cleantechnica.com/feed/',
                'https://www.energy.gov/rss/energy-news-rss'
            ],
            'google_news': 'https://news.google.com/rss/search?q={}&hl=en-US&gl=US&ceid=US:en',
            'bing_news': 'https://www.bing.com/news/search?q={}&format=rss'
        }
        
        # Data storage paths
        self.raw_data_path = Path('training_data/raw')
        self.processed_data_path = Path('training_data/processed')
        self.raw_data_path.mkdir(parents=True, exist_ok=True)
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        # Quality thresholds
        self.min_word_count = 100
        self.max_word_count = 5000
        self.min_quality_score = 0.6
        
    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash for deduplication"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def assess_content_quality(self, article: Dict) -> float:
        """Assess the quality of article content for training"""
        score = 0.0
        content = article.get('content', '')
        title = article.get('title', '')
        
        # Length check
        word_count = len(content.split())
        if self.min_word_count <= word_count <= self.max_word_count:
            score += 0.3
        
        # Title quality
        if len(title.split()) >= 4 and len(title) < 200:
            score += 0.2
        
        # Energy relevance
        energy_terms = sum(1 for keyword in self.energy_keywords[:20] 
                          if keyword.lower() in content.lower())
        if energy_terms >= 3:
            score += 0.3
        elif energy_terms >= 1:
            score += 0.1
        
        # Content structure
        if '\n' in content and len(content.split('\n')) >= 3:
            score += 0.1
        
        # Language quality (basic checks)
        if content.count('.') >= 3 and content.count('?') <= content.count('.'):
            score += 0.1
        
        return min(score, 1.0)
    
    def scrape_rss_feeds(self, max_articles_per_feed: int = 50) -> List[NewsArticle]:
        """Scrape articles from RSS feeds"""
        articles = []
        
        for feed_url in self.news_sources['rss_feeds']:
            try:
                logger.info(f"Scraping RSS feed: {feed_url}")
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:max_articles_per_feed]:
                    try:
                        # Extract full content
                        article_content = self.extract_article_content(entry.link)
                        if not article_content:
                            continue
                        
                        content_hash = self.calculate_content_hash(article_content)
                        word_count = len(article_content.split())
                        
                        article_data = {
                            'title': entry.title,
                            'content': article_content,
                            'url': entry.link,
                            'published_date': getattr(entry, 'published', ''),
                            'source': urlparse(feed_url).netloc,
                            'keywords': getattr(entry, 'tags', []),
                            'category': 'energy_news',
                            'scraped_at': datetime.now().isoformat(),
                            'content_hash': content_hash,
                            'word_count': word_count,
                            'quality_score': 0.0
                        }
                        
                        # Assess quality
                        quality_score = self.assess_content_quality(article_data)
                        article_data['quality_score'] = quality_score
                        
                        if quality_score >= self.min_quality_score:
                            article = NewsArticle(**article_data)
                            articles.append(article)
                        
                    except Exception as e:
                        logger.error(f"Error processing article from {feed_url}: {e}")
                        continue
                
                # Rate limiting
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Error scraping RSS feed {feed_url}: {e}")
                continue
        
        return articles
    
    def scrape_search_engines(self, max_articles_per_keyword: int = 20) -> List[NewsArticle]:
        """Scrape Google News and Bing for specific keywords"""
        articles = []
        
        for keyword in self.energy_keywords[:10]:  # Limit to top keywords to avoid rate limiting
            try:
                logger.info(f"Scraping search engines for: {keyword}")
                
                # Google News
                google_url = self.news_sources['google_news'].format(keyword.replace(' ', '+'))
                google_articles = self.scrape_search_feed(google_url, keyword, 'Google News')
                articles.extend(google_articles[:max_articles_per_keyword//2])
                
                # Bing News
                bing_url = self.news_sources['bing_news'].format(keyword.replace(' ', '+'))
                bing_articles = self.scrape_search_feed(bing_url, keyword, 'Bing News')
                articles.extend(bing_articles[:max_articles_per_keyword//2])
                
                time.sleep(3)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping search engines for '{keyword}': {e}")
                continue
        
        return articles
    
    def scrape_search_feed(self, feed_url: str, keyword: str, source: str) -> List[NewsArticle]:
        """Scrape a search engine RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                try:
                    article_content = self.extract_article_content(entry.link)
                    if not article_content:
                        continue
                    
                    content_hash = self.calculate_content_hash(article_content)
                    word_count = len(article_content.split())
                    
                    article_data = {
                        'title': entry.title,
                        'content': article_content,
                        'url': entry.link,
                        'published_date': getattr(entry, 'published', ''),
                        'source': source,
                        'keywords': [keyword],
                        'category': 'search_result',
                        'scraped_at': datetime.now().isoformat(),
                        'content_hash': content_hash,
                        'word_count': word_count,
                        'quality_score': 0.0
                    }
                    
                    quality_score = self.assess_content_quality(article_data)
                    article_data['quality_score'] = quality_score
                    
                    if quality_score >= self.min_quality_score:
                        article = NewsArticle(**article_data)
                        articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing search result: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping search feed {feed_url}: {e}")
        
        return articles
    
    def extract_article_content(self, url: str) -> str:
        """Extract full article content from URL"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if len(article.text) >= self.min_word_count:
                return article.text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
        
        return ""
    
    def deduplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on content hash"""
        seen_hashes = set()
        unique_articles = []
        
        for article in articles:
            if article.content_hash not in seen_hashes:
                seen_hashes.add(article.content_hash)
                unique_articles.append(article)
        
        logger.info(f"Removed {len(articles) - len(unique_articles)} duplicate articles")
        return unique_articles
    
    def save_training_data(self, articles: List[NewsArticle], filename: str = None):
        """Save articles as training data"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"energy_training_data_{timestamp}.json"
        
        filepath = self.raw_data_path / filename
        
        # Convert to JSON-serializable format
        articles_data = []
        for article in articles:
            articles_data.append({
                'title': article.title,
                'content': article.content,
                'url': article.url,
                'published_date': article.published_date,
                'source': article.source,
                'keywords': article.keywords,
                'category': article.category,
                'scraped_at': article.scraped_at,
                'content_hash': article.content_hash,
                'word_count': article.word_count,
                'quality_score': article.quality_score
            })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(articles)} articles to {filepath}")
        
        # Also save as CSV for analysis
        df = pd.DataFrame(articles_data)
        csv_filepath = filepath.with_suffix('.csv')
        df.to_csv(csv_filepath, index=False)
        
        return filepath
    
    def run_weekly_collection(self):
        """Run comprehensive weekly data collection"""
        logger.info("🚀 Starting weekly energy news collection for LLM training...")
        
        all_articles = []
        
        # Collect from RSS feeds
        logger.info("📰 Collecting from RSS feeds...")
        rss_articles = self.scrape_rss_feeds(max_articles_per_feed=100)
        all_articles.extend(rss_articles)
        
        # Collect from search engines
        logger.info("🔍 Collecting from search engines...")
        search_articles = self.scrape_search_engines(max_articles_per_keyword=30)
        all_articles.extend(search_articles)
        
        # Deduplicate
        logger.info("🔄 Removing duplicates...")
        unique_articles = self.deduplicate_articles(all_articles)
        
        # Filter by quality
        high_quality_articles = [
            article for article in unique_articles 
            if article.quality_score >= self.min_quality_score
        ]
        
        logger.info(f"✅ Collected {len(high_quality_articles)} high-quality articles")
        
        # Save training data
        if high_quality_articles:
            filepath = self.save_training_data(high_quality_articles)
            
            # Generate statistics
            self.generate_collection_stats(high_quality_articles, filepath)
        
        return high_quality_articles
    
    def generate_collection_stats(self, articles: List[NewsArticle], filepath: Path):
        """Generate statistics about collected data"""
        stats = {
            'total_articles': len(articles),
            'total_words': sum(article.word_count for article in articles),
            'avg_quality_score': sum(article.quality_score for article in articles) / len(articles),
            'sources': list(set(article.source for article in articles)),
            'categories': list(set(article.category for article in articles)),
            'date_range': {
                'start': min(article.scraped_at for article in articles),
                'end': max(article.scraped_at for article in articles)
            },
            'word_count_distribution': {
                'min': min(article.word_count for article in articles),
                'max': max(article.word_count for article in articles),
                'avg': sum(article.word_count for article in articles) / len(articles)
            }
        }
        
        stats_filepath = filepath.with_name(f"stats_{filepath.stem}.json")
        with open(stats_filepath, 'w') as f:
            json.dump(stats, f, indent=2)
        
        logger.info(f"📊 Collection statistics saved to {stats_filepath}")
        return stats

if __name__ == "__main__":
    collector = EnergyDataCollector()
    articles = collector.run_weekly_collection()
    print(f"🎉 Collected {len(articles)} articles for LLM training")
