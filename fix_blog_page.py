#!/usr/bin/env python3
"""
Fix All Posts Blog Page - Renewable Power Insight

This script fixes the blog page issues:
1. Creates placeholder images for blog posts
2. Updates the blog index page with correct post data
3. Fixes the "Load More" functionality
4. Ensures all images display properly
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json

def create_placeholder_images():
    """Create SVG placeholder images for blog categories"""
    
    # Create blog images directory
    blog_images_dir = Path("assets/images/blog")
    blog_images_dir.mkdir(parents=True, exist_ok=True)
    
    # Category colors and icons
    categories = {
        "solar": {"color": "#FFB000", "icon": "☀"},
        "wind": {"color": "#00B4D8", "icon": "💨"},  
        "battery": {"color": "#00C896", "icon": "🔋"},
        "grid-tech": {"color": "#6D28D9", "icon": "⚡"},
        "policy": {"color": "#DC2626", "icon": "📋"}
    }
    
    print("Creating placeholder images...")
    
    for category, style in categories.items():
        # Create SVG placeholder
        svg_content = f'''<svg width="400" height="200" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad_{category}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{style['color']};stop-opacity:0.8" />
      <stop offset="100%" style="stop-color:{style['color']};stop-opacity:0.6" />
    </linearGradient>
  </defs>
  <rect width="400" height="200" fill="url(#grad_{category})" rx="8"/>
  <text x="200" y="100" font-family="Arial, sans-serif" font-size="48" fill="white" text-anchor="middle" dominant-baseline="central">
    {style['icon']}
  </text>
  <text x="200" y="140" font-family="Arial, sans-serif" font-size="16" fill="white" text-anchor="middle" dominant-baseline="central" opacity="0.9">
    {category.replace('-', ' ').title()}
  </text>
</svg>'''
        
        # Save SVG file
        with open(blog_images_dir / f"placeholder-{category}.svg", 'w') as f:
            f.write(svg_content)
        
        print(f"  ✓ Created placeholder-{category}.svg")

def get_actual_posts():
    """Get information about actual blog posts"""
    
    posts_data = []
    posts_dir = Path("posts")
    
    # Category mapping
    category_names = {
        "solar": "Solar Energy",
        "wind": "Wind Power", 
        "battery": "Energy Storage",
        "grid-tech": "Smart Grid",
        "policy": "Policy & Markets"
    }
    
    for category_dir in posts_dir.iterdir():
        if category_dir.is_dir() and category_dir.name in category_names:
            category = category_dir.name
            
            # Get HTML files (excluding index.html)
            html_files = [f for f in category_dir.glob("*.html") if f.name != "index.html"]
            
            for html_file in html_files:
                try:
                    # Read post content to extract title and excerpt
                    with open(html_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract title from HTML
                    title_match = re.search(r'<title>([^<]+)</title>', content, re.IGNORECASE)
                    h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
                    
                    title = ""
                    if title_match:
                        title = title_match.group(1).replace(" - Renewable Power Insight", "")
                    elif h1_match:
                        title = h1_match.group(1)
                    else:
                        title = html_file.stem.replace('-', ' ').title()
                    
                    # Extract first paragraph for excerpt
                    excerpt_match = re.search(r'<p[^>]*>([^<]{100,300})', content, re.IGNORECASE)
                    excerpt = ""
                    if excerpt_match:
                        excerpt = excerpt_match.group(1).strip()
                        if len(excerpt) > 200:
                            excerpt = excerpt[:200] + "..."
                    else:
                        excerpt = "Comprehensive analysis of renewable energy technologies and market developments."
                    
                    # Get file stats for date
                    file_stats = html_file.stat()
                    mod_date = datetime.fromtimestamp(file_stats.st_mtime)
                    
                    posts_data.append({
                        "category": category,
                        "category_name": category_names[category],
                        "title": title,
                        "excerpt": excerpt,
                        "url": f"../posts/{category}/{html_file.name}",
                        "date": mod_date.strftime("%Y-%m-%d"),
                        "date_display": mod_date.strftime("%B %d, %Y"),
                        "reading_time": "5 min read"  # Default reading time
                    })
                    
                except Exception as e:
                    print(f"  ⚠️  Error processing {html_file}: {e}")
    
    # Sort by date (newest first)
    posts_data.sort(key=lambda x: x['date'], reverse=True)
    
    return posts_data

def update_blog_index(posts_data):
    """Update the blog index page with correct post data and working functionality"""
    
    blog_index_path = Path("blog/index.html")
    
    # Count posts by category
    category_counts = {}
    for post in posts_data:
        category = post['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    total_posts = len(posts_data)
    
    print(f"Updating blog index with {total_posts} posts...")
    
    # Generate articles HTML
    articles_html = ""
    for post in posts_data:
        articles_html += f'''        <article class="grid-article" data-category="{post['category']}">
            <div class="article-image">
                <img src="../assets/images/blog/placeholder-{post['category']}.svg" 
                     alt="{post['title']}" 
                     loading="lazy">
                <span class="category-badge">{post['category_name']}</span>
            </div>
            <div class="article-content">
                <h2 class="article-title">
                    <a href="{post['url']}">
                        {post['title']}
                    </a>
                </h2>
                <p class="article-excerpt">
                    {post['excerpt']}
                </p>
                <div class="article-meta">
                    <span class="reading-time">{post['reading_time']}</span>
                    <span>•</span>
                    <time datetime="{post['date']}">{post['date_display']}</time>
                </div>
            </div>
        </article>
'''
    
    # Create the updated blog index HTML
    blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>All Posts - Renewable Power Insight | Latest Energy Research & Analysis</title>
    <meta name="description" content="Browse our comprehensive collection of renewable energy research articles, market analysis, and technology insights covering solar, wind, battery storage, and smart grid innovations.">
    <meta name="keywords" content="renewable energy blog, energy research articles, solar power analysis, wind energy insights, battery storage news">
    
    <!-- External Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    
    <!-- External CSS -->
    <link rel="stylesheet" href="../style.css">
    
    <!-- Breadcrumb Schema -->
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {{
                "@type": "ListItem",
                "position": 1,
                "name": "Home",
                "item": "../index.html"
            }},
            {{
                "@type": "ListItem",
                "position": 2,
                "name": "All Posts",
                "item": "../blog/index.html"
            }}
        ]
    }}
    </script>
</head>
<body>
    <!-- Skip Navigation -->
    <a class="sr-only" href="#main-content">Skip to main content</a>

    <!-- Header -->
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <div class="header-brand">
                    <a href="../index.html" class="site-title">Renewable Power Insight</a>
                    <span class="site-tagline">Advanced Energy Research</span>
                </div>
                <nav class="main-nav" aria-label="Main navigation">
                    <a href="../index.html" class="nav-link">Home</a>
                    <a href="../posts/solar/index.html" class="nav-link">Solar</a>
                    <a href="../posts/wind/index.html" class="nav-link">Wind</a>
                    <a href="../posts/battery/index.html" class="nav-link">Storage</a>
                    <a href="../posts/grid-tech/index.html" class="nav-link">Smart Grid</a>
                    <a href="../posts/policy/index.html" class="nav-link">Policy</a>
                    <a href="../blog/index.html" class="nav-link active" aria-current="page">All Posts</a>
                </nav>
                <button class="mobile-menu-button" aria-label="Open mobile menu" aria-expanded="false">
                    ☰
                </button>
            </div>
        </div>
    </header>

    <!-- Breadcrumb Navigation -->
    <nav class="breadcrumb-nav" aria-label="Breadcrumb">
        <div class="container">
            <ol class="breadcrumb-list">
                <li class="breadcrumb-item">
                    <a href="../index.html">Home</a>
                </li>
                <li class="breadcrumb-item active" aria-current="page">
                    All Posts
                </li>
            </ol>
        </div>
    </nav>

    <!-- Page Header -->
    <section class="page-header">
        <div class="container">
            <div class="page-header-content">
                <h1 class="page-title">Research Blog</h1>
                <p class="page-subtitle">
                    Comprehensive analysis and insights on renewable energy technologies, 
                    market trends, and policy developments shaping the clean energy future.
                </p>
                
                <!-- Filter Categories -->
                <div class="filter-categories">
                    <button class="filter-btn active" data-category="all" aria-pressed="true">
                        All Posts <span class="count">({total_posts})</span>
                    </button>
                    <button class="filter-btn" data-category="solar" aria-pressed="false">
                        Solar <span class="count">({category_counts.get('solar', 0)})</span>
                    </button>
                    <button class="filter-btn" data-category="wind" aria-pressed="false">
                        Wind <span class="count">({category_counts.get('wind', 0)})</span>
                    </button>
                    <button class="filter-btn" data-category="battery" aria-pressed="false">
                        Storage <span class="count">({category_counts.get('battery', 0)})</span>
                    </button>
                    <button class="filter-btn" data-category="grid-tech" aria-pressed="false">
                        Smart Grid <span class="count">({category_counts.get('grid-tech', 0)})</span>
                    </button>
                    <button class="filter-btn" data-category="policy" aria-pressed="false">
                        Policy <span class="count">({category_counts.get('policy', 0)})</span>
                    </button>
                </div>
            </div>
        </div>
    </section>

    <!-- Main Content -->
    <main id="main-content" class="main-content">
        <div class="container">
            <div class="content-grid">
                <!-- Articles Grid -->
                <div class="articles-container">
                    <div class="articles-grid" id="articles-grid">
{articles_html}
                    </div>
                    
                    <!-- Load More Section -->
                    <div class="load-more-container">
                        <p class="load-more-info">
                            Showing all {total_posts} articles. New content is published regularly - check back soon!
                        </p>
                    </div>
                </div>
                
                <!-- Sidebar -->
                <aside class="sidebar">
                    <div class="sidebar-section">
                        <h3 class="sidebar-title">Browse by Category</h3>
                        <ul class="category-list">
                            <li class="category-item">
                                <a href="../posts/solar/index.html" class="category-link">
                                    <span class="category-name">Solar Energy</span>
                                    <span class="category-count">{category_counts.get('solar', 0)}</span>
                                </a>
                            </li>
                            <li class="category-item">
                                <a href="../posts/wind/index.html" class="category-link">
                                    <span class="category-name">Wind Power</span>
                                    <span class="category-count">{category_counts.get('wind', 0)}</span>
                                </a>
                            </li>
                            <li class="category-item">
                                <a href="../posts/battery/index.html" class="category-link">
                                    <span class="category-name">Energy Storage</span>
                                    <span class="category-count">{category_counts.get('battery', 0)}</span>
                                </a>
                            </li>
                            <li class="category-item">
                                <a href="../posts/grid-tech/index.html" class="category-link">
                                    <span class="category-name">Smart Grid</span>
                                    <span class="category-count">{category_counts.get('grid-tech', 0)}</span>
                                </a>
                            </li>
                            <li class="category-item">
                                <a href="../posts/policy/index.html" class="category-link">
                                    <span class="category-name">Policy & Markets</span>
                                    <span class="category-count">{category_counts.get('policy', 0)}</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                    
                    <div class="sidebar-section">
                        <h3 class="sidebar-title">Popular Tags</h3>
                        <div class="tag-cloud">
                            <a href="#" class="tag" data-count="12">Battery Technology</a>
                            <a href="#" class="tag" data-count="10">Solar Panels</a>
                            <a href="#" class="tag" data-count="8">Wind Turbines</a>
                            <a href="#" class="tag" data-count="6">Smart Grid</a>
                            <a href="#" class="tag" data-count="5">Energy Storage</a>
                            <a href="#" class="tag" data-count="4">Policy Analysis</a>
                            <a href="#" class="tag" data-count="4">Market Trends</a>
                            <a href="#" class="tag" data-count="3">Sustainability</a>
                        </div>
                    </div>
                    
                    <div class="sidebar-section">
                        <h3 class="sidebar-title">Newsletter</h3>
                        <div class="newsletter-signup">
                            <p>Get the latest renewable energy insights delivered to your inbox.</p>
                            <form class="newsletter-form" action="/subscribe" method="post">
                                <div class="form-group">
                                    <label for="email" class="sr-only">Email address</label>
                                    <input type="email" id="email" name="email" class="newsletter-input" 
                                           placeholder="Enter your email" required>
                                </div>
                                <button type="submit" class="newsletter-btn">
                                    Subscribe
                                </button>
                            </form>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    </main>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Research Areas</h3>
                    <ul class="footer-links">
                        <li><a href="../posts/solar/index.html">Solar Technology</a></li>
                        <li><a href="../posts/wind/index.html">Wind Energy</a></li>
                        <li><a href="../posts/battery/index.html">Energy Storage</a></li>
                        <li><a href="../posts/grid-tech/index.html">Smart Grid</a></li>
                        <li><a href="../posts/policy/index.html">Policy Analysis</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Resources</h3>
                    <ul class="footer-links">
                        <li><a href="../blog/index.html">All Articles</a></li>
                        <li><a href="../research/index.html">Research Reports</a></li>
                        <li><a href="../data/index.html">Market Data</a></li>
                        <li><a href="../insights/index.html">Industry Insights</a></li>
                        <li><a href="../methodology/index.html">Methodology</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Company</h3>
                    <ul class="footer-links">
                        <li><a href="../about/index.html">About Us</a></li>
                    </ul>
                </div>
                <div class="footer-section">
                    <h3>Connect</h3>
                    <ul class="footer-links">
                        <li><a href="../newsletter/index.html">Newsletter</a></li>
                        <li><a href="../rss/index.html">RSS Feed</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>© 2024 Renewable Power Insight. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <!-- JavaScript for Blog Functionality -->
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            // Category filtering
            const filterButtons = document.querySelectorAll('.filter-btn');
            const articles = document.querySelectorAll('.grid-article');
            
            filterButtons.forEach(button => {{
                button.addEventListener('click', function() {{
                    const category = this.dataset.category;
                    
                    // Update active button
                    filterButtons.forEach(btn => {{
                        btn.classList.remove('active');
                        btn.setAttribute('aria-pressed', 'false');
                    }});
                    this.classList.add('active');
                    this.setAttribute('aria-pressed', 'true');
                    
                    // Filter articles
                    articles.forEach(article => {{
                        if (category === 'all' || article.dataset.category === category) {{
                            article.style.display = 'block';
                            article.classList.add('fade-in');
                        }} else {{
                            article.style.display = 'none';
                        }}
                    }});
                }});
            }});

            // Newsletter form handling
            const newsletterForm = document.querySelector('.newsletter-form');
            if (newsletterForm) {{
                newsletterForm.addEventListener('submit', function(e) {{
                    e.preventDefault();
                    const email = this.querySelector('input[type="email"]').value;
                    
                    // Basic email validation
                    if (email && email.includes('@')) {{
                        alert('Thank you for subscribing!');
                        this.reset();
                    }}
                }});
            }}

            // Mobile menu functionality
            const mobileMenuButton = document.querySelector('.mobile-menu-button');
            const mainNav = document.querySelector('.main-nav');
            
            if (mobileMenuButton && mainNav) {{
                mobileMenuButton.addEventListener('click', function() {{
                    const isExpanded = this.getAttribute('aria-expanded') === 'true';
                    this.setAttribute('aria-expanded', !isExpanded);
                    mainNav.classList.toggle('mobile-open');
                }});
            }}

            // Intersection Observer for animations
            const observerOptions = {{
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            }};
            
            const observer = new IntersectionObserver(function(entries) {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        entry.target.classList.add('fade-in');
                    }}
                }});
            }}, observerOptions);
            
            // Observe article cards
            articles.forEach(article => {{
                observer.observe(article);
            }});
        }});
    </script>
</body>
</html>'''

    # Write the updated HTML
    with open(blog_index_path, 'w', encoding='utf-8') as f:
        f.write(blog_html)
    
    print(f"  ✓ Updated blog index with {total_posts} posts")
    print(f"  ✓ Categories: Solar ({category_counts.get('solar', 0)}), Wind ({category_counts.get('wind', 0)}), Storage ({category_counts.get('battery', 0)}), Smart Grid ({category_counts.get('grid-tech', 0)}), Policy ({category_counts.get('policy', 0)})")

def main():
    """Main function to fix the blog page"""
    
    print("=" * 60)
    print("FIX ALL POSTS BLOG PAGE")
    print("=" * 60)
    
    # Step 1: Create placeholder images
    create_placeholder_images()
    print()
    
    # Step 2: Get actual post data
    print("Scanning for blog posts...")
    posts_data = get_actual_posts()
    print(f"  ✓ Found {len(posts_data)} blog posts")
    print()
    
    # Step 3: Update blog index
    update_blog_index(posts_data)
    print()
    
    print("=" * 60)
    print("BLOG PAGE FIXES COMPLETE!")
    print("=" * 60)
    print("✅ Issues Fixed:")
    print("  • Created SVG placeholder images for all categories")
    print("  • Updated blog index with actual post data")
    print("  • Fixed post images to display correctly") 
    print("  • Removed broken 'Load More' functionality")
    print("  • Updated category counts with real data")
    print("  • Improved article filtering and display")
    print()
    print("🎉 The All Posts page should now display correctly!")

if __name__ == "__main__":
    main()
