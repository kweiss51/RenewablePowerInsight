#!/usr/bin/env python3
"""
Website Integration System for Automated Blog Posts
Automatically integrates ML-generated blog posts into the website structure
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple
from bs4 import BeautifulSoup
import html

class WebsiteIntegrator:
    def __init__(self, posts_dir: str, website_root: str = None):
        self.posts_dir = Path(posts_dir)
        self.website_root = Path(website_root) if website_root else self.posts_dir.parent
        self.index_file = self.website_root / "index.html"
        
        # Category mapping for navigation
        self.category_mapping = {
            'solar': {'name': 'Solar Energy', 'nav_order': 1},
            'wind': {'name': 'Wind Power', 'nav_order': 2},
            'battery': {'name': 'Energy Storage', 'nav_order': 3},
            'grid-tech': {'name': 'Smart Grid', 'nav_order': 4},
            'policy': {'name': 'Policy & Markets', 'nav_order': 5},
            'general': {'name': 'General News', 'nav_order': 6},
            'markets': {'name': 'Market Analysis', 'nav_order': 7}
        }
        
        print(f"🔗 Website Integrator initialized")
        print(f"📁 Posts directory: {self.posts_dir}")
        print(f"🌐 Website root: {self.website_root}")
        
    def extract_post_metadata(self, post_path: Path) -> Dict:
        """Extract metadata from a blog post HTML file"""
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text().strip() if title_tag else post_path.stem.replace('-', ' ').title()
            
            # Extract excerpt from first paragraph
            first_p = soup.find('p')
            excerpt = first_p.get_text()[:200] + "..." if first_p else ""
            
            # Extract image
            img_tag = soup.find('img')
            image_url = img_tag.get('src', '') if img_tag else ''
            image_alt = img_tag.get('alt', '') if img_tag else ''
            
            # Get file stats
            stats = post_path.stat()
            created_date = datetime.fromtimestamp(stats.st_ctime)
            modified_date = datetime.fromtimestamp(stats.st_mtime)
            
            # Determine category from path
            category = post_path.parent.name if post_path.parent.name != 'posts' else 'general'
            
            metadata = {
                'title': title,
                'excerpt': excerpt,
                'image_url': image_url,
                'image_alt': image_alt,
                'category': category,
                'category_name': self.category_mapping.get(category, {}).get('name', category.title()),
                'file_path': str(post_path.relative_to(self.website_root)),
                'url_path': str(post_path.relative_to(self.website_root)).replace('\\', '/'),
                'filename': post_path.name,
                'created_date': created_date,
                'modified_date': modified_date,
                'word_count': len(soup.get_text().split()),
                'reading_time': max(1, len(soup.get_text().split()) // 200)  # Assume 200 WPM
            }
            
            return metadata
            
        except Exception as e:
            print(f"❌ Error extracting metadata from {post_path}: {e}")
            return None
    
    def get_all_posts(self) -> List[Dict]:
        """Get metadata for all blog posts"""
        posts = []
        
        # Search all HTML files in posts directory and subdirectories
        for post_file in self.posts_dir.rglob("*.html"):
            metadata = self.extract_post_metadata(post_file)
            if metadata:
                posts.append(metadata)
        
        # Sort by created date (newest first)
        posts.sort(key=lambda x: x['created_date'], reverse=True)
        
        print(f"📚 Found {len(posts)} blog posts")
        return posts
    
    def generate_post_html_snippet(self, post: Dict, snippet_type: str = "card") -> str:
        """Generate HTML snippet for a blog post"""
        
        if snippet_type == "hero":
            return f'''
                        <article class="hero-article">
                            <div class="hero-content">
                                <div class="hero-text">
                                    <span class="category-tag">{post['category_name']}</span>
                                    <h1><a href="{post['url_path']}">{html.escape(post['title'])}</a></h1>
                                    <p class="hero-excerpt">{html.escape(post['excerpt'])}</p>
                                    <div class="article-meta">
                                        <span class="read-time">{post['reading_time']} min read</span>
                                        <span class="post-date">{post['created_date'].strftime('%B %d, %Y')}</span>
                                    </div>
                                </div>
                                <div class="hero-image">
                                    <img src="{post['image_url']}" alt="{html.escape(post['image_alt'])}" />
                                </div>
                            </div>
                        </article>'''
        
        elif snippet_type == "featured":
            return f'''
                        <article class="featured-article">
                            <div class="featured-image">
                                <img src="{post['image_url']}" alt="{html.escape(post['image_alt'])}" />
                            </div>
                            <div class="featured-content">
                                <span class="category-tag">{post['category_name']}</span>
                                <h2><a href="{post['url_path']}">{html.escape(post['title'])}</a></h2>
                                <p>{html.escape(post['excerpt'])}</p>
                                <div class="article-meta">
                                    <span class="read-time">{post['reading_time']} min read</span>
                                    <span class="post-date">{post['created_date'].strftime('%B %d, %Y')}</span>
                                </div>
                            </div>
                        </article>'''
        
        elif snippet_type == "card":
            return f'''
                        <article class="article-card">
                            <div class="card-image">
                                <img src="{post['image_url']}" alt="{html.escape(post['image_alt'])}" />
                            </div>
                            <div class="card-content">
                                <span class="category-tag">{post['category_name']}</span>
                                <h3><a href="{post['url_path']}">{html.escape(post['title'])}</a></h3>
                                <p>{html.escape(post['excerpt'][:100])}...</p>
                                <div class="article-meta">
                                    <span class="read-time">{post['reading_time']} min</span>
                                    <span class="post-date">{post['created_date'].strftime('%b %d')}</span>
                                </div>
                            </div>
                        </article>'''
        
        elif snippet_type == "sidebar":
            return f'''
                        <article class="sidebar-article">
                            <h3><a href="{post['url_path']}">{html.escape(post['title'])}</a></h3>
                            <div class="sidebar-meta">
                                <span class="category-tag">{post['category_name']}</span>
                                <span class="post-date">{post['created_date'].strftime('%B %d')}</span>
                            </div>
                        </article>'''
        
        return ""
    
    def update_index_html(self, posts: List[Dict]) -> bool:
        """Update the main index.html file with current posts"""
        try:
            if not self.index_file.exists():
                print(f"❌ Index file not found: {self.index_file}")
                return False
            
            # Read current index.html
            with open(self.index_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Backup the original
            backup_file = self.index_file.with_suffix('.html.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"💾 Created backup: {backup_file}")
            
            # Generate new content sections
            if posts:
                hero_post = posts[0]  # Most recent post as hero
                featured_posts = posts[1:4]  # Next 3 posts as featured
                sidebar_posts = posts[4:10]  # Next 6 posts for sidebar
                
                # Generate HTML snippets
                hero_html = self.generate_post_html_snippet(hero_post, "hero")
                
                featured_html = ""
                for post in featured_posts:
                    featured_html += self.generate_post_html_snippet(post, "featured")
                
                sidebar_html = ""
                for post in sidebar_posts:
                    sidebar_html += self.generate_post_html_snippet(post, "sidebar")
                
                # Replace content sections in index.html
                content = self.replace_content_section(content, "hero-section", hero_html)
                content = self.replace_content_section(content, "featured-articles", featured_html)
                content = self.replace_content_section(content, "sidebar-articles", sidebar_html)
                
                # Update recent posts section
                recent_posts_html = ""
                for post in posts[:6]:
                    recent_posts_html += self.generate_post_html_snippet(post, "card")
                
                content = self.replace_content_section(content, "recent-posts", recent_posts_html)
            
            # Write updated content
            with open(self.index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Updated index.html with {len(posts)} posts")
            return True
            
        except Exception as e:
            print(f"❌ Error updating index.html: {e}")
            return False
    
    def replace_content_section(self, html_content: str, section_id: str, new_content: str) -> str:
        """Replace a content section in HTML"""
        # Try to find existing content section markers
        start_marker = f"<!-- START {section_id.upper()} -->"
        end_marker = f"<!-- END {section_id.upper()} -->"
        
        start_pos = html_content.find(start_marker)
        end_pos = html_content.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Replace existing section
            before = html_content[:start_pos + len(start_marker)]
            after = html_content[end_pos:]
            return before + "\n" + new_content + "\n                " + after
        else:
            # Try to find common patterns and insert content
            patterns = {
                "hero-section": [
                    r'<section[^>]*class="[^"]*hero[^"]*"[^>]*>.*?</section>',
                    r'<div[^>]*class="[^"]*hero[^"]*"[^>]*>.*?</div>'
                ],
                "featured-articles": [
                    r'<section[^>]*class="[^"]*featured[^"]*"[^>]*>.*?</section>',
                    r'<div[^>]*class="[^"]*featured[^"]*"[^>]*>.*?</div>'
                ],
                "sidebar-articles": [
                    r'<aside[^>]*>.*?</aside>',
                    r'<div[^>]*class="[^"]*sidebar[^"]*"[^>]*>.*?</div>'
                ],
                "recent-posts": [
                    r'<section[^>]*class="[^"]*recent[^"]*"[^>]*>.*?</section>',
                    r'<div[^>]*class="[^"]*posts[^"]*"[^>]*>.*?</div>'
                ]
            }
            
            if section_id in patterns:
                for pattern in patterns[section_id]:
                    match = re.search(pattern, html_content, re.DOTALL | re.IGNORECASE)
                    if match:
                        # Insert content within the matched section
                        section_content = match.group(0)
                        # Find the end of the opening tag
                        tag_end = section_content.find('>') + 1
                        updated_section = (section_content[:tag_end] + 
                                         f"\n                {start_marker}\n{new_content}\n                {end_marker}\n                " + 
                                         section_content[tag_end:])
                        return html_content.replace(section_content, updated_section)
            
            print(f"⚠️ Could not find section '{section_id}' to update")
            return html_content
    
    def create_post_index_page(self, posts: List[Dict]) -> bool:
        """Create a comprehensive blog index page"""
        try:
            # Group posts by category
            posts_by_category = {}
            for post in posts:
                category = post['category']
                if category not in posts_by_category:
                    posts_by_category[category] = []
                posts_by_category[category].append(post)
            
            # Generate blog index HTML
            blog_index_content = self.generate_blog_index_html(posts, posts_by_category)
            
            # Write blog index file
            blog_index_file = self.website_root / "blog" / "index.html"
            blog_index_file.parent.mkdir(exist_ok=True)
            
            with open(blog_index_file, 'w', encoding='utf-8') as f:
                f.write(blog_index_content)
            
            print(f"✅ Created blog index page: {blog_index_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error creating blog index page: {e}")
            return False
    
    def generate_blog_index_html(self, posts: List[Dict], posts_by_category: Dict) -> str:
        """Generate HTML for blog index page"""
        
        # Generate category sections
        category_sections = ""
        for category, category_posts in sorted(posts_by_category.items(), 
                                             key=lambda x: self.category_mapping.get(x[0], {}).get('nav_order', 99)):
            category_name = self.category_mapping.get(category, {}).get('name', category.title())
            
            category_sections += f'''
        <section class="category-section">
            <h2 class="category-title">{category_name}</h2>
            <div class="category-posts">'''
            
            for post in category_posts[:6]:  # Limit to 6 posts per category
                category_sections += self.generate_post_html_snippet(post, "card")
            
            category_sections += '''
            </div>
        </section>'''
        
        # Generate all posts list
        all_posts_html = ""
        for post in posts:
            all_posts_html += self.generate_post_html_snippet(post, "card")
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog - Renewable Power Insight</title>
    <link rel="stylesheet" href="../style.css">
</head>
<body>
    <header class="site-header">
        <div class="wrapper">
            <div class="header-brand">
                <a href="../index.html" class="site-title">Renewable Power Insight</a>
                <span class="site-tagline">Clean Energy Intelligence</span>
            </div>
            <nav class="site-navigation">
                <a href="../index.html">Home</a>
                <a href="index.html" class="current">Blog</a>
                <a href="../about.html">About</a>
            </nav>
        </div>
    </header>

    <main class="page-content">
        <div class="wrapper">
            <h1 class="page-title">Latest Energy News & Analysis</h1>
            
            <section class="all-posts">
                <h2>All Posts ({len(posts)})</h2>
                <div class="posts-grid">
                    {all_posts_html}
                </div>
            </section>
            
            {category_sections}
        </div>
    </main>

    <footer class="site-footer">
        <div class="wrapper">
            <p>&copy; 2025 Renewable Power Insight. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''
    
    def integrate_new_post(self, post_path: Path) -> bool:
        """Integrate a single new blog post into the website"""
        try:
            print(f"🔗 Integrating new post: {post_path.name}")
            
            # Extract metadata
            metadata = self.extract_post_metadata(post_path)
            if not metadata:
                print(f"❌ Could not extract metadata from {post_path}")
                return False
            
            # Get all existing posts
            all_posts = self.get_all_posts()
            
            # Update main index page
            self.update_index_html(all_posts)
            
            # Create/update blog index page
            self.create_post_index_page(all_posts)
            
            # Log integration
            self.log_integration(metadata)
            
            print(f"✅ Successfully integrated post: {metadata['title']}")
            return True
            
        except Exception as e:
            print(f"❌ Error integrating post {post_path}: {e}")
            return False
    
    def integrate_all_posts(self) -> bool:
        """Integrate all existing blog posts into the website"""
        try:
            print("🔄 Integrating all blog posts...")
            
            # Get all posts
            all_posts = self.get_all_posts()
            
            if not all_posts:
                print("📭 No blog posts found to integrate")
                return True
            
            # Update main index page
            success = self.update_index_html(all_posts)
            
            # Create blog index page
            if success:
                success = self.create_post_index_page(all_posts)
            
            if success:
                print(f"✅ Successfully integrated {len(all_posts)} blog posts")
                
                # Create integration summary
                self.create_integration_summary(all_posts)
            
            return success
            
        except Exception as e:
            print(f"❌ Error during full integration: {e}")
            return False
    
    def log_integration(self, post_metadata: Dict):
        """Log integration activity"""
        log_file = self.website_root / "integration_log.json"
        
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'post_integrated',
            'post_title': post_metadata['title'],
            'post_path': post_metadata['file_path'],
            'category': post_metadata['category']
        }
        
        # Read existing log
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                logs = []
        
        # Add new entry
        logs.append(log_entry)
        
        # Keep only last 100 entries
        logs = logs[-100:]
        
        # Write updated log
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    
    def create_integration_summary(self, posts: List[Dict]):
        """Create a summary of the integration"""
        summary = {
            'integration_date': datetime.now().isoformat(),
            'total_posts': len(posts),
            'posts_by_category': {},
            'latest_post': posts[0] if posts else None,
            'oldest_post': posts[-1] if posts else None
        }
        
        # Count posts by category
        for post in posts:
            category = post['category']
            if category not in summary['posts_by_category']:
                summary['posts_by_category'][category] = 0
            summary['posts_by_category'][category] += 1
        
        # Write summary
        summary_file = self.website_root / "integration_summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"📊 Integration summary saved: {summary_file}")

if __name__ == "__main__":
    # Example usage
    integrator = WebsiteIntegrator("../posts")
    
    # Integrate all existing posts
    integrator.integrate_all_posts()
