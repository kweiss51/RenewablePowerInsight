"""
Advanced Energy Data Collector
Collects high-quality training data from academic and government sources
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
import feedparser
from newspaper import Article
import re
import scholarly
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import urllib.parse
import pandas as pd
from pathlib import Path

class AdvancedEnergyDataCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Comprehensive academic search terms for Google Scholar
        self.academic_keywords = [
            # Renewable Energy Technologies
            "renewable energy",
            "clean energy",
            "sustainable energy",
            "solar energy",
            "wind energy",
            "hydroelectric power",
            "geothermal energy",
            "biomass energy",
            "ocean energy",
            "tidal energy",
            
            # Energy Storage & Grid
            "energy storage",
            "battery technology",
            "grid storage",
            "smart grid",
            "microgrid",
            "power grid",
            "grid modernization",
            "energy management",
            "demand response",
            "grid stability",
            
            # Emerging Technologies
            "hydrogen energy",
            "fuel cells",
            "nuclear energy",
            "fusion energy",
            "carbon capture",
            "energy efficiency",
            "power electronics",
            "electric vehicles",
            "energy conversion",
            "power systems",
            
            # Policy & Economics
            "energy policy",
            "energy economics",
            "energy markets",
            "energy regulation",
            "energy security",
            "energy planning",
            "climate policy",
            "carbon pricing",
            "energy transition",
            "decarbonization",
            
            # Industrial & Applications
            "industrial energy",
            "building energy",
            "transportation energy",
            "energy consumption",
            "energy production",
            "power generation",
            "electricity markets",
            "energy infrastructure",
            "energy investment",
            "energy innovation"
        ]
        
        # Government and institutional URLs
        self.institutional_sources = {
            'doe': 'https://www.energy.gov',
            'eia': 'https://www.eia.gov',
            'epa': 'https://www.epa.gov',
            'nrel': 'https://www.nrel.gov',
            'ornl': 'https://www.ornl.gov',
            'lbl': 'https://www.lbl.gov',
            'pnnl': 'https://www.pnnl.gov',
            'iea': 'https://www.iea.org',
            'irena': 'https://www.irena.org',
            'eere': 'https://www.energy.gov/eere',
            'arpa_e': 'https://arpa-e.energy.gov'
        }
        
        self.collected_data = []
        self.setup_selenium()
    
    def setup_selenium(self):
        """Setup Selenium webdriver for JavaScript-heavy sites"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            print("✅ Selenium WebDriver initialized")
        except Exception as e:
            print(f"⚠️ Selenium setup failed: {e}")
            self.driver = None
    
    def collect_google_scholar_papers(self, max_papers_per_keyword: int = 20) -> List[Dict]:
        """Collect academic papers from Google Scholar"""
        papers = []
        
        print("📚 Collecting academic papers from Google Scholar...")
        
        for keyword in self.academic_keywords:
            print(f"  🔍 Searching for: {keyword}")
            
            try:
                # Search for papers published in the last 2 years
                search_query = scholarly.search_pubs(keyword)
                
                count = 0
                for paper in search_query:
                    if count >= max_papers_per_keyword:
                        break
                    
                    try:
                        # Get detailed paper information
                        paper_detail = scholarly.fill(paper)
                        
                        # Filter for recent papers (last 2 years)
                        if 'pub_year' in paper_detail:
                            pub_year = int(paper_detail['pub_year'])
                            if pub_year < datetime.now().year - 2:
                                continue
                        
                        paper_data = {
                            'title': paper_detail.get('title', ''),
                            'abstract': paper_detail.get('abstract', ''),
                            'authors': paper_detail.get('author', []),
                            'venue': paper_detail.get('venue', ''),
                            'year': paper_detail.get('pub_year', ''),
                            'citations': paper_detail.get('num_citations', 0),
                            'url': paper_detail.get('pub_url', ''),
                            'source': 'Google Scholar',
                            'keyword': keyword,
                            'content_type': 'academic_paper',
                            'collected_at': datetime.now().isoformat()
                        }
                        
                        # Try to get full text if available
                        if paper_data['url']:
                            full_text = self.extract_paper_content(paper_data['url'])
                            if full_text:
                                paper_data['full_text'] = full_text
                        
                        papers.append(paper_data)
                        count += 1
                        
                    except Exception as e:
                        print(f"    ❌ Error processing paper: {e}")
                        continue
                    
                    # Rate limiting
                    time.sleep(2)
                    
            except Exception as e:
                print(f"  ❌ Error searching for '{keyword}': {e}")
                continue
        
        print(f"📚 Collected {len(papers)} academic papers")
        return papers
    
    def extract_paper_content(self, url: str) -> Optional[str]:
        """Extract full text content from academic papers"""
        try:
            if not self.driver:
                # Fallback to requests
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()
                    text = soup.get_text()
                    return self.clean_text(text)
            else:
                # Use Selenium for JavaScript-heavy sites
                self.driver.get(url)
                time.sleep(3)
                
                # Try to find main content areas
                content_selectors = [
                    '.article-body', '.paper-content', '.abstract', 
                    '.content', '.main-content', 'main', 'article'
                ]
                
                for selector in content_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            text = ' '.join([elem.text for elem in elements])
                            if len(text) > 500:  # Minimum content length
                                return self.clean_text(text)
                    except:
                        continue
                
                # Fallback to body text
                body = self.driver.find_element(By.TAG_NAME, 'body')
                return self.clean_text(body.text)
                
        except Exception as e:
            print(f"    ⚠️ Could not extract content from {url}: {e}")
            return None
    
    def collect_government_data(self) -> List[Dict]:
        """Collect data from government and institutional sources"""
        government_data = []
        
        print("🏛️ Collecting government and institutional data...")
        
        # DOE - Department of Energy
        doe_data = self.scrape_doe_content()
        government_data.extend(doe_data)
        
        # EIA - Energy Information Administration
        eia_data = self.scrape_eia_content()
        government_data.extend(eia_data)
        
        # EPA - Environmental Protection Agency
        epa_data = self.scrape_epa_content()
        government_data.extend(epa_data)
        
        # National Labs
        nrel_data = self.scrape_nrel_content()
        government_data.extend(nrel_data)
        
        # International Energy Agency
        iea_data = self.scrape_iea_content()
        government_data.extend(iea_data)
        
        # IRENA
        irena_data = self.scrape_irena_content()
        government_data.extend(irena_data)
        
        print(f"🏛️ Collected {len(government_data)} government documents")
        return government_data
    
    def scrape_doe_content(self) -> List[Dict]:
        """Scrape Department of Energy content"""
        doe_content = []
        
        try:
            # DOE News and Publications
            urls_to_scrape = [
                'https://www.energy.gov/news',
                'https://www.energy.gov/eere/articles',
                'https://www.energy.gov/science-innovation/science-technology',
                'https://www.energy.gov/policy'
            ]
            
            for url in urls_to_scrape:
                print(f"  📄 Scraping DOE: {url}")
                content = self.scrape_page_content(url, 'Department of Energy')
                if content:
                    doe_content.extend(content)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping DOE: {e}")
        
        return doe_content
    
    def scrape_eia_content(self) -> List[Dict]:
        """Scrape Energy Information Administration content"""
        eia_content = []
        
        try:
            urls_to_scrape = [
                'https://www.eia.gov/analysis',
                'https://www.eia.gov/todayinenergy',
                'https://www.eia.gov/renewable',
                'https://www.eia.gov/electricity'
            ]
            
            for url in urls_to_scrape:
                print(f"  📊 Scraping EIA: {url}")
                content = self.scrape_page_content(url, 'Energy Information Administration')
                if content:
                    eia_content.extend(content)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping EIA: {e}")
        
        return eia_content
    
    def scrape_epa_content(self) -> List[Dict]:
        """Scrape EPA energy and climate content"""
        epa_content = []
        
        try:
            urls_to_scrape = [
                'https://www.epa.gov/energy',
                'https://www.epa.gov/climate-change',
                'https://www.epa.gov/renewable-energy-fact-sheets'
            ]
            
            for url in urls_to_scrape:
                print(f"  🌍 Scraping EPA: {url}")
                content = self.scrape_page_content(url, 'Environmental Protection Agency')
                if content:
                    epa_content.extend(content)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping EPA: {e}")
        
        return epa_content
    
    def scrape_nrel_content(self) -> List[Dict]:
        """Scrape National Renewable Energy Laboratory content"""
        nrel_content = []
        
        try:
            urls_to_scrape = [
                'https://www.nrel.gov/news',
                'https://www.nrel.gov/analysis',
                'https://www.nrel.gov/research'
            ]
            
            for url in urls_to_scrape:
                print(f"  🔬 Scraping NREL: {url}")
                content = self.scrape_page_content(url, 'National Renewable Energy Laboratory')
                if content:
                    nrel_content.extend(content)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping NREL: {e}")
        
        return nrel_content
    
    def scrape_iea_content(self) -> List[Dict]:
        """Scrape International Energy Agency content"""
        iea_content = []
        
        try:
            urls_to_scrape = [
                'https://www.iea.org/news',
                'https://www.iea.org/reports',
                'https://www.iea.org/analysis'
            ]
            
            for url in urls_to_scrape:
                print(f"  🌐 Scraping IEA: {url}")
                content = self.scrape_page_content(url, 'International Energy Agency')
                if content:
                    iea_content.extend(content)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping IEA: {e}")
        
        return iea_content
    
    def scrape_irena_content(self) -> List[Dict]:
        """Scrape IRENA content"""
        irena_content = []
        
        try:
            urls_to_scrape = [
                'https://www.irena.org/newsroom',
                'https://www.irena.org/publications'
            ]
            
            for url in urls_to_scrape:
                print(f"  ♻️ Scraping IRENA: {url}")
                content = self.scrape_page_content(url, 'International Renewable Energy Agency')
                if content:
                    irena_content.extend(content)
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ Error scraping IRENA: {e}")
        
        return irena_content
    
    def scrape_page_content(self, url: str, source: str) -> List[Dict]:
        """Generic page content scraper"""
        content_items = []
        
        try:
            if self.driver:
                self.driver.get(url)
                time.sleep(3)
                
                # Find article links
                article_links = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="article"], a[href*="news"], a[href*="report"], a[href*="analysis"]')
                
                for link in article_links[:10]:  # Limit to 10 articles per page
                    try:
                        href = link.get_attribute('href')
                        if href and href.startswith('http'):
                            article_content = self.extract_article_content(href, source)
                            if article_content:
                                content_items.append(article_content)
                    except:
                        continue
            else:
                # Fallback to requests
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find article links
                    links = soup.find_all('a', href=True)
                    for link in links[:10]:
                        href = link['href']
                        if not href.startswith('http'):
                            href = urllib.parse.urljoin(url, href)
                        
                        if any(keyword in href.lower() for keyword in ['article', 'news', 'report', 'analysis']):
                            article_content = self.extract_article_content(href, source)
                            if article_content:
                                content_items.append(article_content)
                
        except Exception as e:
            print(f"    ❌ Error scraping {url}: {e}")
        
        return content_items
    
    def extract_article_content(self, url: str, source: str) -> Optional[Dict]:
        """Extract content from individual articles"""
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            if len(article.text) < 200:  # Skip very short articles
                return None
            
            return {
                'title': article.title,
                'content': article.text,
                'url': url,
                'source': source,
                'authors': article.authors,
                'publish_date': article.publish_date.isoformat() if article.publish_date else None,
                'keywords': article.keywords,
                'content_type': 'institutional_article',
                'collected_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"    ⚠️ Could not extract article from {url}: {e}")
            return None
    
    def collect_recent_energy_news(self, months_back: int = 6) -> List[Dict]:
        """Collect energy news from the past X months"""
        news_articles = []
        
        print(f"📰 Collecting energy news from the past {months_back} months...")
        
        # News sources RSS feeds
        news_sources = [
            'https://www.renewableenergyworld.com/feeds/all/',
            'https://www.pv-magazine.com/feed/',
            'https://www.windpowerengineering.com/feed/',
            'https://www.energy-storage.news/feed/',
            'https://www.greentechmedia.com/rss/all',
            'https://www.utilitydive.com/feeds/',
            'https://www.smart-energy.com/feed/',
            'https://cleantechnica.com/feed/'
        ]
        
        cutoff_date = datetime.now() - timedelta(days=months_back * 30)
        
        for source_url in news_sources:
            try:
                print(f"  📡 Fetching from: {source_url}")
                feed = feedparser.parse(source_url)
                
                for entry in feed.entries:
                    try:
                        # Check if article is recent enough
                        if hasattr(entry, 'published_parsed'):
                            pub_date = datetime(*entry.published_parsed[:6])
                            if pub_date < cutoff_date:
                                continue
                        
                        # Extract full article content
                        article_content = self.extract_article_content(entry.link, f"News - {feed.feed.get('title', 'Unknown')}")
                        if article_content:
                            news_articles.append(article_content)
                            
                    except Exception as e:
                        print(f"    ⚠️ Error processing news article: {e}")
                        continue
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  ❌ Error fetching from {source_url}: {e}")
                continue
        
        print(f"📰 Collected {len(news_articles)} recent news articles")
        return news_articles
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-"]', '', text)
        
        # Remove very short lines
        lines = text.split('\n')
        lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(lines).strip()
    
    def collect_all_data(self) -> Dict:
        """Collect all training data from all sources"""
        print("🚀 Starting comprehensive energy data collection...")
        
        all_data = {
            'academic_papers': [],
            'government_content': [],
            'news_articles': [],
            'collection_metadata': {
                'collection_date': datetime.now().isoformat(),
                'total_sources': 0,
                'total_documents': 0
            }
        }
        
        # Collect academic papers
        try:
            academic_papers = self.collect_google_scholar_papers()
            all_data['academic_papers'] = academic_papers
        except Exception as e:
            print(f"❌ Academic collection failed: {e}")
        
        # Collect government data
        try:
            government_content = self.collect_government_data()
            all_data['government_content'] = government_content
        except Exception as e:
            print(f"❌ Government collection failed: {e}")
        
        # Collect recent news
        try:
            news_articles = self.collect_recent_energy_news()
            all_data['news_articles'] = news_articles
        except Exception as e:
            print(f"❌ News collection failed: {e}")
        
        # Update metadata
        all_data['collection_metadata']['total_documents'] = (
            len(all_data['academic_papers']) + 
            len(all_data['government_content']) + 
            len(all_data['news_articles'])
        )
        
        print(f"✅ Collection complete!")
        print(f"  📚 Academic papers: {len(all_data['academic_papers'])}")
        print(f"  🏛️ Government content: {len(all_data['government_content'])}")
        print(f"  📰 News articles: {len(all_data['news_articles'])}")
        print(f"  📊 Total documents: {all_data['collection_metadata']['total_documents']}")
        
        return all_data
    
    def save_training_data(self, data: Dict, filename: str = None):
        """Save collected data for training"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"training_data/energy_training_data_{timestamp}.json"
        
        os.makedirs("training_data", exist_ok=True)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved training data to {filename}")
        
        # Also save in different formats for ML training
        self.save_for_ml_training(data, filename.replace('.json', ''))
        
        return filename
    
    def save_for_ml_training(self, data: Dict, base_filename: str):
        """Save data in formats optimized for ML training"""
        
        # Combine all text content
        all_texts = []
        
        for paper in data['academic_papers']:
            text_content = f"Title: {paper.get('title', '')}\n"
            text_content += f"Abstract: {paper.get('abstract', '')}\n"
            if 'full_text' in paper:
                text_content += f"Content: {paper['full_text']}\n"
            all_texts.append(text_content)
        
        for content in data['government_content']:
            text_content = f"Title: {content.get('title', '')}\n"
            text_content += f"Content: {content.get('content', '')}\n"
            all_texts.append(text_content)
        
        for article in data['news_articles']:
            text_content = f"Title: {article.get('title', '')}\n"
            text_content += f"Content: {article.get('content', '')}\n"
            all_texts.append(text_content)
        
        # Save as plain text for training
        with open(f"{base_filename}_training_corpus.txt", 'w', encoding='utf-8') as f:
            f.write('\n\n---DOCUMENT_SEPARATOR---\n\n'.join(all_texts))
        
        # Save as CSV for analysis
        df_data = []
        for paper in data['academic_papers']:
            df_data.append({
                'type': 'academic',
                'title': paper.get('title', ''),
                'content': paper.get('abstract', '') + ' ' + paper.get('full_text', ''),
                'source': paper.get('source', ''),
                'date': paper.get('collected_at', '')
            })
        
        for content in data['government_content']:
            df_data.append({
                'type': 'government',
                'title': content.get('title', ''),
                'content': content.get('content', ''),
                'source': content.get('source', ''),
                'date': content.get('collected_at', '')
            })
        
        for article in data['news_articles']:
            df_data.append({
                'type': 'news',
                'title': article.get('title', ''),
                'content': article.get('content', ''),
                'source': article.get('source', ''),
                'date': article.get('collected_at', '')
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(f"{base_filename}_training_data.csv", index=False)
        
        print(f"💾 Saved ML training files:")
        print(f"  📄 {base_filename}_training_corpus.txt")
        print(f"  📊 {base_filename}_training_data.csv")
    
    def __del__(self):
        """Cleanup Selenium driver"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
    
    def collect_academic_papers(self, max_papers: int = 25, days_back: int = 7) -> List[Dict]:
        """Collect academic papers with date filtering"""
        print("📚 Collecting recent academic papers...")
        papers_per_keyword = max(1, max_papers // len(self.academic_keywords))
        return self.collect_google_scholar_papers(papers_per_keyword)
    
    def collect_institutional_data(self, max_articles: int = 25) -> List[Dict]:
        """Collect data from institutional sources"""
        print("🏛️ Collecting institutional data...")
        articles_per_source = max(1, max_articles // len(self.institutional_sources))
        return self.collect_government_data()

if __name__ == "__main__":
    collector = AdvancedEnergyDataCollector()
    
    # Collect all data
    training_data = collector.collect_all_data()
    
    # Save for training
    collector.save_training_data(training_data)
