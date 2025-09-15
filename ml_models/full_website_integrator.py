"""
Complete Website Integration System
Automatically integrates all existing blog posts into the website structure
Updates both homepage and blog index with real content
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from bs4 import BeautifulSoup
import re

class FullWebsiteIntegrator:
    """
    Comprehensive website integration system that:
    1. Scans all existing blog posts
    2. Updates the main homepage with real content
    3. Updates the blog index with all posts
    4. Creates proper navigation and categorization
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.posts_dir = self.project_root / "posts"
        self.integration_log = []
        
        # Category mapping
        self.category_info = {
            "solar": {
                "name": "Solar Energy",
                "description": "Solar panel technology, photovoltaic systems, and solar power innovations",
                "icon": "☀️"
            },
            "wind": {
                "name": "Wind Power", 
                "description": "Wind turbine technology, offshore wind farms, and wind energy developments",
                "icon": "💨"
            },
            "battery": {
                "name": "Energy Storage",
                "description": "Battery technology, grid storage systems, and energy storage innovations",
                "icon": "🔋"
            },
            "grid-tech": {
                "name": "Smart Grid",
                "description": "Smart grid technology, cybersecurity, and grid modernization",
                "icon": "⚡"
            },
            "policy": {
                "name": "Policy & Markets",
                "description": "Energy policy, market analysis, and regulatory developments",
                "icon": "📊"
            },
            "markets": {
                "name": "Energy Markets",
                "description": "Market trends, investment analysis, and economic developments",
                "icon": "💹"
            },
            "general": {
                "name": "General Energy",
                "description": "General renewable energy topics and industry news",
                "icon": "🌱"
            }
        }
    
    def scan_all_posts(self) -> Dict[str, List[Dict]]:
        """Scan all existing blog posts and extract metadata"""
        print("🔍 Scanning all existing blog posts...")
        
        all_posts = {}
        total_posts = 0
        
        for category_dir in self.posts_dir.iterdir():
            if category_dir.is_dir() and category_dir.name in self.category_info:
                category = category_dir.name
                all_posts[category] = []
                
                for post_file in category_dir.glob("*.html"):
                    try:
                        post_data = self.extract_post_metadata(post_file)
                        if post_data:
                            all_posts[category].append(post_data)
                            total_posts += 1
                    except Exception as e:
                        print(f"⚠️ Error reading {post_file}: {e}")
                
                # Sort posts by date (newest first)
                all_posts[category].sort(key=lambda x: x.get('date_sort', ''), reverse=True)
                
                print(f"📁 {category}: Found {len(all_posts[category])} posts")
        
        print(f"✅ Total posts found: {total_posts}")
        return all_posts
    
    def extract_post_metadata(self, post_file: Path) -> Optional[Dict]:
        """Extract metadata from a blog post HTML file"""
        try:
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title_elem = soup.find('h1', class_='post-title') or soup.find('title')
            title = title_elem.get_text().strip() if title_elem else post_file.stem.replace('-', ' ').title()
            
            # Clean up title (remove "- Renewable Power Insight" suffix)
            title = re.sub(r'\s*-\s*Renewable Power Insight.*$', '', title)
            
            # Extract date from meta or use file modification time
            date_text = "Recent"
            date_sort = datetime.now().strftime("%Y-%m-%d")
            
            meta_elem = soup.find('div', class_='post-meta')
            if meta_elem:
                date_match = re.search(r'(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}', meta_elem.get_text())
                if date_match:
                    date_text = date_match.group(0)
                    try:
                        date_obj = datetime.strptime(date_text, "%B %d, %Y")
                        date_sort = date_obj.strftime("%Y-%m-%d")
                    except:
                        pass
            
            # Extract excerpt from content
            content_div = soup.find('div', class_='post-content')
            excerpt = ""
            if content_div:
                # Get first paragraph that's not a heading
                paragraphs = content_div.find_all('p')
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 50:  # Skip very short paragraphs
                        excerpt = text[:200] + "..." if len(text) > 200 else text
                        break
            
            if not excerpt:
                excerpt = f"Comprehensive analysis of {title.lower()} and its impact on the renewable energy sector."
            
            # Determine category from file path
            category = post_file.parent.name
            
            # Calculate reading time (rough estimate)
            word_count = len(content.split())
            reading_time = max(1, word_count // 200)  # Assume 200 words per minute
            
            return {
                'title': title,
                'filename': post_file.name,
                'url': f"posts/{category}/{post_file.name}",
                'category': category,
                'category_name': self.category_info.get(category, {}).get('name', category.title()),
                'date': date_text,
                'date_sort': date_sort,
                'excerpt': excerpt,
                'reading_time': f"{reading_time} min read",
                'file_path': str(post_file)
            }
            
        except Exception as e:
            print(f"❌ Error extracting metadata from {post_file}: {e}")
            return None
    
    def update_homepage(self, all_posts: Dict[str, List[Dict]]) -> bool:
        """Update the main homepage with real blog post content"""
        print("🏠 Updating homepage with real content...")
        
        try:
            # Get the most recent posts across all categories for featured content
            recent_posts = []
            for category, posts in all_posts.items():
                recent_posts.extend(posts[:2])  # Take top 2 from each category
            
            # Sort by date and take the most recent
            recent_posts.sort(key=lambda x: x.get('date_sort', ''), reverse=True)
            
            # Use modern homepage template
            homepage_path = self.project_root / "index_modern.html"
            if not homepage_path.exists():
                print("❌ Modern homepage template not found")
                return False
            
            with open(homepage_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Update featured article (large card)
            if recent_posts:
                featured_post = recent_posts[0]
                self.update_featured_article(soup, featured_post)
            
            # Update sidebar featured articles
            if len(recent_posts) > 1:
                self.update_sidebar_articles(soup, recent_posts[1:3])
            
            # Update latest articles grid
            if len(recent_posts) > 3:
                self.update_articles_grid(soup, recent_posts[3:7])
            
            # Update sidebar statistics
            self.update_sidebar_stats(soup, all_posts)
            
            # Save the updated homepage
            with open(self.project_root / "index.html", 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print("✅ Homepage updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating homepage: {e}")
            return False
    
    def update_featured_article(self, soup: BeautifulSoup, post: Dict):
        """Update the main featured article"""
        featured_card = soup.find('article', class_='article-card featured')
        if featured_card:
            # Update title and link
            title_elem = featured_card.find('h3', class_='article-title')
            if title_elem:
                link = title_elem.find('a')
                if link:
                    link.string = post['title']
                    link['href'] = post['url']
            
            # Update excerpt
            excerpt_elem = featured_card.find('p', class_='article-excerpt')
            if excerpt_elem:
                excerpt_elem.string = post['excerpt']
            
            # Update meta information
            meta_elem = featured_card.find('div', class_='article-meta')
            if meta_elem:
                time_elem = meta_elem.find('time')
                if time_elem:
                    time_elem.string = post['date']
                    time_elem['datetime'] = post['date_sort']
                
                reading_time = meta_elem.find('span', class_='reading-time')
                if reading_time:
                    reading_time.string = post['reading_time']
            
            # Update category badge
            badge_elem = featured_card.find('span', class_='category-badge')
            if badge_elem:
                badge_elem.string = post['category_name']
    
    def update_sidebar_articles(self, soup: BeautifulSoup, posts: List[Dict]):
        """Update sidebar featured articles"""
        sidebar_div = soup.find('div', class_='featured-sidebar')
        if sidebar_div:
            sidebar_articles = sidebar_div.find_all('article', class_='article-card')
            
            for i, article in enumerate(sidebar_articles[:len(posts)]):
                post = posts[i]
                
                # Update title and link
                title_elem = article.find('h3', class_='article-title')
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        link.string = post['title']
                        link['href'] = post['url']
                
                # Update meta information
                meta_elem = article.find('div', class_='article-meta')
                if meta_elem:
                    time_elem = meta_elem.find('time')
                    if time_elem:
                        time_elem.string = post['date']
                        time_elem['datetime'] = post['date_sort']
                    
                    reading_time = meta_elem.find('span', class_='reading-time')
                    if reading_time:
                        reading_time.string = post['reading_time']
                
                # Update category badge
                badge_elem = article.find('span', class_='category-badge')
                if badge_elem:
                    badge_elem.string = post['category_name']
    
    def update_articles_grid(self, soup: BeautifulSoup, posts: List[Dict]):
        """Update the articles grid section"""
        articles_grid = soup.find('div', class_='articles-grid')
        if articles_grid:
            grid_articles = articles_grid.find_all('article', class_='grid-article')
            
            for i, article in enumerate(grid_articles[:len(posts)]):
                post = posts[i]
                
                # Update title and link
                title_elem = article.find('h3', class_='article-title')
                if title_elem:
                    link = title_elem.find('a')
                    if link:
                        link.string = post['title']
                        link['href'] = post['url']
                
                # Update excerpt
                excerpt_elem = article.find('p', class_='article-excerpt')
                if excerpt_elem:
                    excerpt_elem.string = post['excerpt']
                
                # Update meta information
                meta_elem = article.find('div', class_='article-meta')
                if meta_elem:
                    time_elem = meta_elem.find('time')
                    if time_elem:
                        time_elem.string = post['date']
                        time_elem['datetime'] = post['date_sort']
                    
                    reading_time = meta_elem.find('span', class_='reading-time')
                    if reading_time:
                        reading_time.string = post['reading_time']
                
                # Update category badge
                badge_elem = article.find('span', class_='category-badge')
                if badge_elem:
                    badge_elem.string = post['category_name']
    
    def update_sidebar_stats(self, soup: BeautifulSoup, all_posts: Dict[str, List[Dict]]):
        """Update sidebar with real statistics"""
        sidebar = soup.find('aside', class_='sidebar')
        if sidebar:
            # Update category counts
            category_items = sidebar.find_all('li', class_='sidebar-item')
            
            for item in category_items:
                link = item.find('a')
                if link and link.get('href'):
                    # Extract category from href
                    href = link.get('href', '')
                    for category, posts in all_posts.items():
                        if f"/posts/{category}/" in href:
                            meta_div = item.find('div', class_='sidebar-meta')
                            if meta_div:
                                count_span = meta_div.find('span')
                                if count_span:
                                    count_span.string = f"{len(posts)} articles"
                            break
    
    def update_blog_index(self, all_posts: Dict[str, List[Dict]]) -> bool:
        """Update the blog index page with all posts"""
        print("📝 Updating blog index with all posts...")
        
        try:
            blog_index_path = self.project_root / "blog" / "index_modern.html"
            if not blog_index_path.exists():
                print("❌ Modern blog index template not found")
                return False
            
            with open(blog_index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Update articles grid with all posts
            articles_grid = soup.find('div', class_='articles-grid', id='articles-grid')
            if articles_grid:
                # Clear existing articles except the "coming soon" template
                existing_articles = articles_grid.find_all('article', class_='grid-article')
                for article in existing_articles:
                    if not article.has_attr('class') or 'coming-soon' not in article.get('class', []):
                        article.decompose()
                
                # Add real posts
                all_posts_flat = []
                for category, posts in all_posts.items():
                    all_posts_flat.extend(posts)
                
                # Sort by date (newest first)
                all_posts_flat.sort(key=lambda x: x.get('date_sort', ''), reverse=True)
                
                # Create article elements for each post
                for post in all_posts_flat:
                    article_html = self.create_blog_article_html(post)
                    new_article = BeautifulSoup(article_html, 'html.parser')
                    articles_grid.insert(0, new_article)  # Insert at beginning
            
            # Update filter buttons with real counts
            self.update_filter_buttons(soup, all_posts)
            
            # Save updated blog index
            with open(self.project_root / "blog" / "index.html", 'w', encoding='utf-8') as f:
                f.write(str(soup))
            
            print("✅ Blog index updated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error updating blog index: {e}")
            return False
    
    def create_blog_article_html(self, post: Dict) -> str:
        """Create HTML for a blog article card"""
        return f'''
        <article class="grid-article" data-category="{post['category']}">
            <div class="article-image">
                <img src="../assets/images/blog/placeholder-{post['category']}.jpg" 
                     alt="{post['title']}" 
                     loading="lazy">
                <span class="category-badge">{post['category_name']}</span>
            </div>
            <div class="article-content">
                <h2 class="article-title">
                    <a href="../{post['url']}">
                        {post['title']}
                    </a>
                </h2>
                <p class="article-excerpt">
                    {post['excerpt']}
                </p>
                <div class="article-meta">
                    <span class="reading-time">{post['reading_time']}</span>
                    <span>•</span>
                    <time datetime="{post['date_sort']}">{post['date']}</time>
                </div>
            </div>
        </article>'''
    
    def update_filter_buttons(self, soup: BeautifulSoup, all_posts: Dict[str, List[Dict]]):
        """Update filter buttons with real post counts"""
        filter_buttons = soup.find_all('button', class_='filter-btn')
        
        total_count = sum(len(posts) for posts in all_posts.values())
        
        for button in filter_buttons:
            category = button.get('data-category', '')
            count_span = button.find('span', class_='count')
            
            if count_span:
                if category == 'all':
                    count_span.string = f"({total_count})"
                elif category in all_posts:
                    count_span.string = f"({len(all_posts[category])})"
    
    def perform_full_integration(self) -> Dict[str, any]:
        """Perform complete website integration"""
        print("🚀 Starting full website integration...")
        
        # Scan all posts
        all_posts = self.scan_all_posts()
        
        if not any(posts for posts in all_posts.values()):
            print("❌ No blog posts found to integrate")
            return {'success': False, 'error': 'No posts found'}
        
        # Update homepage
        homepage_success = self.update_homepage(all_posts)
        
        # Update blog index
        blog_success = self.update_blog_index(all_posts)
        
        # Create integration summary
        total_posts = sum(len(posts) for posts in all_posts.values())
        
        result = {
            'success': homepage_success and blog_success,
            'posts_integrated': total_posts,
            'categories': len([cat for cat, posts in all_posts.items() if posts]),
            'homepage_updated': homepage_success,
            'blog_index_updated': blog_success,
            'posts_by_category': {cat: len(posts) for cat, posts in all_posts.items() if posts},
            'timestamp': datetime.now().isoformat()
        }
        
        # Save integration log
        self.save_integration_log(result)
        
        if result['success']:
            print(f"✅ Full website integration completed successfully!")
            print(f"📊 Integrated {total_posts} posts across {result['categories']} categories")
        else:
            print(f"❌ Website integration completed with errors")
        
        return result
    
    def save_integration_log(self, result: Dict):
        """Save integration log for tracking"""
        log_file = self.project_root / "integration_log.json"
        
        try:
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"📋 Integration log saved to {log_file}")
        except Exception as e:
            print(f"⚠️ Could not save integration log: {e}")

if __name__ == "__main__":
    print("🔗 Full Website Integration System")
    print("==================================")
    
    integrator = FullWebsiteIntegrator()
    result = integrator.perform_full_integration()
    
    if result['success']:
        print("\n🎉 Integration Summary:")
        print(f"   📝 Posts integrated: {result['posts_integrated']}")
        print(f"   📁 Categories: {result['categories']}")
        print(f"   🏠 Homepage updated: {result['homepage_updated']}")
        print(f"   📝 Blog index updated: {result['blog_index_updated']}")
        print("\n📊 Posts by category:")
        for category, count in result['posts_by_category'].items():
            print(f"   {category}: {count} posts")
    else:
        print(f"\n❌ Integration failed: {result.get('error', 'Unknown error')}")
