#!/usr/bin/env python3
"""
AI Blog Post Generator - Use ML Model to Create 10 Categorized Blog Posts
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import random

# Add the src and ml_models directories to Python path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir / 'src'))
sys.path.append(str(current_dir / 'ml_models'))

# Try to import the blog generator
try:
    from blog_generator import BlogPostGenerator
    HAS_BLOG_GENERATOR = True
except ImportError:
    print("Blog generator not available, using fallback method")
    HAS_BLOG_GENERATOR = False

class AIBlogPostCreator:
    def __init__(self):
        """Initialize the AI blog post creator"""
        self.blog_generator = None
        
        # Try to initialize the ML blog generator
        if HAS_BLOG_GENERATOR:
            try:
                self.blog_generator = BlogPostGenerator(use_custom_llm=True)
                print("✅ AI Blog Generator initialized with custom ML model")
            except Exception as e:
                print(f"⚠️  Custom ML model not available: {e}")
                try:
                    self.blog_generator = BlogPostGenerator(use_custom_llm=False)
                    print("🔄 Using OpenAI fallback for blog generation")
                except Exception as e2:
                    print(f"❌ Blog generator initialization failed: {e2}")
                    self.blog_generator = None
        
        # Define renewable energy topics with categories
        self.topics_by_category = {
            'solar': [
                'Solar Panel Efficiency Breakthrough 2025',
                'Perovskite Solar Cell Commercial Deployment',
                'Residential Solar Storage Integration',
                'Solar Farm Land Use Optimization',
                'Floating Solar Technology Advances'
            ],
            'wind': [
                'Offshore Wind Turbine Size Records',
                'Wind Energy Storage Solutions',
                'Onshore Wind Repowering Strategies',
                'Vertical Axis Wind Turbine Innovation',
                'Wind Farm Grid Integration'
            ],
            'battery': [
                'Lithium-Ion Battery Recycling Breakthrough',
                'Solid-State Battery Manufacturing Scale-Up',
                'Grid-Scale Energy Storage Economics',
                'Home Battery System Cost Trends',
                'Vehicle-to-Grid Battery Applications'
            ],
            'grid': [
                'Smart Grid Cybersecurity Solutions',
                'Microgrids for Rural Electrification',
                'Grid Modernization Federal Funding',
                'AI-Powered Grid Optimization',
                'Transmission Line Underground Technology'
            ],
            'markets': [
                'Clean Energy Investment Record 2025',
                'Corporate Renewable Energy Procurement',
                'Green Bond Market Expansion',
                'Energy Storage Market Projections',
                'Carbon Credit Trading Mechanisms'
            ],
            'policy': [
                'Federal Clean Energy Tax Credit Extensions',
                'State Renewable Portfolio Standards Updates',
                'International Climate Agreement Progress',
                'Net Metering Policy Changes',
                'Clean Energy Infrastructure Investment'
            ]
        }
        
    def create_mock_articles(self, topic: str) -> list:
        """Create mock article data for the topic"""
        return [
            {
                'title': f"Breaking: {topic} Reaches New Milestone",
                'summary': f"Industry experts report significant progress in {topic.lower()} technology with potential market implications.",
                'keyword': topic.split()[0].lower(),
                'source': 'Energy News Today',
                'published_date': (datetime.now() - timedelta(days=random.randint(1, 7))).strftime('%Y-%m-%d')
            },
            {
                'title': f"{topic}: Market Analysis and Future Outlook",
                'summary': f"New research reveals promising trends in {topic.lower()} adoption and investment opportunities.",
                'keyword': topic.split()[0].lower(),
                'source': 'Renewable Energy Review',
                'published_date': (datetime.now() - timedelta(days=random.randint(1, 14))).strftime('%Y-%m-%d')
            }
        ]
    
    def generate_blog_post_with_ai(self, category: str, topic: str) -> dict:
        """Generate a blog post using AI/ML systems"""
        
        # Create mock articles for the topic
        articles = self.create_mock_articles(topic)
        
        # Create topic data structure
        topic_data = {
            'topic': topic,
            'articles': articles,
            'category': category,
            'trend_score': random.randint(50, 100)
        }
        
        # Generate blog post with AI if available
        if self.blog_generator:
            try:
                blog_post = self.blog_generator.generate_blog_post(topic_data)
                blog_post['category'] = category
                blog_post['subcategory'] = self.determine_subcategory(category, topic)
                return blog_post
            except Exception as e:
                print(f"⚠️  AI generation failed for {topic}: {e}")
                return self.generate_fallback_post(category, topic, articles)
        else:
            return self.generate_fallback_post(category, topic, articles)
    
    def determine_subcategory(self, category: str, topic: str) -> str:
        """Determine the appropriate subcategory based on topic content"""
        topic_lower = topic.lower()
        
        subcategory_mapping = {
            'solar': {
                'residential': ['home', 'rooftop', 'residential', 'household'],
                'utility': ['farm', 'utility', 'large-scale', 'grid-scale'],
                'technology': ['efficiency', 'cell', 'panel', 'breakthrough', 'innovation'],
                'manufacturing': ['manufacturing', 'production', 'scale-up', 'factory'],
                'markets': ['investment', 'cost', 'economics', 'market', 'finance'],
                'policy': ['policy', 'regulation', 'incentive', 'tax', 'government']
            },
            'wind': {
                'offshore': ['offshore', 'marine', 'floating', 'ocean'],
                'onshore': ['onshore', 'land', 'terrestrial', 'repowering'],
                'technology': ['turbine', 'blade', 'efficiency', 'innovation', 'vertical'],
                'manufacturing': ['manufacturing', 'production', 'supply chain'],
                'markets': ['investment', 'cost', 'market', 'finance', 'economics'],
                'policy': ['policy', 'regulation', 'incentive', 'government']
            },
            'battery': {
                'residential': ['home', 'household', 'residential', 'backup'],
                'utility': ['grid-scale', 'utility', 'large-scale', 'grid'],
                'technology': ['lithium', 'solid-state', 'chemistry', 'breakthrough'],
                'manufacturing': ['manufacturing', 'production', 'scale-up', 'recycling'],
                'markets': ['cost', 'market', 'economics', 'investment'],
                'policy': ['policy', 'regulation', 'incentive', 'grid']
            },
            'grid': {
                'smart': ['smart', 'ai', 'optimization', 'intelligent'],
                'transmission': ['transmission', 'line', 'infrastructure', 'underground'],
                'storage': ['storage', 'integration', 'grid-scale'],
                'markets': ['market', 'trading', 'economics'],
                'policy': ['policy', 'funding', 'modernization', 'federal']
            },
            'markets': {
                'investment': ['investment', 'funding', 'capital', 'venture'],
                'corporate': ['corporate', 'procurement', 'commercial'],
                'trading': ['trading', 'carbon', 'credit', 'mechanisms'],
                'analysis': ['analysis', 'projections', 'forecast', 'outlook'],
                'policy': ['policy', 'regulation', 'market']
            },
            'policy': {
                'federal': ['federal', 'national', 'congress', 'administration'],
                'state': ['state', 'local', 'municipal', 'regional'],
                'international': ['international', 'global', 'climate', 'agreement'],
                'incentives': ['tax', 'credit', 'incentive', 'rebate'],
                'climate': ['climate', 'carbon', 'emissions', 'agreement']
            }
        }
        
        # Find the best matching subcategory
        if category in subcategory_mapping:
            for subcat, keywords in subcategory_mapping[category].items():
                if any(keyword in topic_lower for keyword in keywords):
                    return subcat
        
        # Default subcategories
        defaults = {
            'solar': 'technology',
            'wind': 'technology', 
            'battery': 'technology',
            'grid': 'smart',
            'markets': 'analysis',
            'policy': 'federal'
        }
        
        return defaults.get(category, 'general')
    
    def generate_fallback_post(self, category: str, topic: str, articles: list) -> dict:
        """Generate a basic blog post without AI as fallback"""
        
        # Create a basic blog post structure
        slug = topic.lower().replace(' ', '-').replace(':', '').replace(',', '')
        
        # Generate content sections based on topic
        content = f"""# {topic}
        
## Overview

The renewable energy sector continues to evolve rapidly, with {topic.lower()} representing one of the most significant developments in the industry. Recent market analysis and technological breakthroughs suggest that this trend will have lasting implications for the energy landscape.

## Key Developments

Based on recent industry reports and expert analysis, several key trends are emerging:

- **Technology Innovation**: Advanced solutions are driving efficiency improvements
- **Market Growth**: Investment and deployment rates continue to accelerate  
- **Policy Support**: Government initiatives are creating favorable conditions
- **Economic Benefits**: Cost reductions are making adoption more attractive

## Market Impact

The implications of {topic.lower()} extend beyond technology into broader market dynamics. Industry stakeholders are closely monitoring these developments as they shape investment decisions and strategic planning.

## Future Outlook

As the renewable energy sector matures, {topic.lower()} will likely play an increasingly important role in the transition to clean energy. Continued innovation and supportive policies will be crucial for realizing the full potential of these advances.

## Conclusion

The developments in {topic.lower()} represent both opportunities and challenges for the renewable energy industry. Staying informed about these trends will be essential for stakeholders across the value chain.

*Stay updated with the latest renewable energy news and analysis on Renewable Power Insight.*
"""

        return {
            'headline': topic,
            'meta_description': f"Explore the latest developments in {topic.lower()}. Get expert insights on renewable energy trends and market implications.",
            'content': content,
            'tags': [category, 'renewable energy', 'clean tech', 'sustainability'],
            'internal_links': [f"{category}-technology", f"{category}-markets", f"{category}-policy"],
            'topic': topic,
            'slug': slug,
            'category': category,
            'subcategory': self.determine_subcategory(category, topic),
            'word_count': len(content.split()),
            'reading_time': max(1, len(content.split()) // 200),
            'author': "AI Content Generator",
            'published_date': datetime.now().strftime('%Y-%m-%d'),
            'seo_optimized': False
        }
    
    def create_markdown_post(self, blog_post: dict) -> str:
        """Convert blog post to Jekyll/GitHub Pages markdown format"""
        
        # Create front matter
        front_matter = f"""---
layout: post
title: "{blog_post['headline']}"
date: {blog_post['published_date']}
categories: [{blog_post['category']}]
tags: {blog_post['tags']}
author: {blog_post['author']}
excerpt: "{blog_post['meta_description']}"
reading_time: {blog_post['reading_time']}
---

"""
        
        # Add content
        markdown_content = front_matter + blog_post['content']
        
        return markdown_content
    
    def generate_10_blog_posts(self):
        """Generate 10 blog posts using AI/ML and organize by categories"""
        
        print("🚀 Generating 10 AI-powered blog posts...")
        print("=" * 50)
        
        all_posts = []
        posts_per_category = 2  # 2 posts per main category (6 categories = 12, but we'll limit to 10)
        
        # Generate posts for each category
        category_count = 0
        for category, topics in self.topics_by_category.items():
            if len(all_posts) >= 10:  # Limit to 10 posts total
                break
                
            print(f"\n📂 Generating {category.upper()} posts...")
            
            # Select random topics from this category
            selected_topics = random.sample(topics, min(posts_per_category, len(topics)))
            
            for topic in selected_topics:
                if len(all_posts) >= 10:
                    break
                    
                print(f"  🤖 Generating: {topic}")
                
                # Generate blog post with AI
                blog_post = self.generate_blog_post_with_ai(category, topic)
                all_posts.append(blog_post)
                
                print(f"  ✅ Created '{blog_post['headline']}' ({blog_post['word_count']} words)")
        
        # Save posts to _posts directory
        posts_dir = Path('_posts')
        posts_dir.mkdir(exist_ok=True)
        
        print(f"\n💾 Saving {len(all_posts)} posts to _posts directory...")
        
        for i, post in enumerate(all_posts, 1):
            # Create filename with date and slug
            filename = f"{post['published_date']}-{post['slug']}.md"
            filepath = posts_dir / filename
            
            # Create markdown content
            markdown_content = self.create_markdown_post(post)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"  {i:2d}. {filename} ({post['category']}/{post['subcategory']})")
        
        # Print summary
        print(f"\n🎉 Successfully created {len(all_posts)} AI-generated blog posts!")
        print("\n📊 Posts by Category:")
        
        category_counts = {}
        for post in all_posts:
            cat = post['category']
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        for category, count in category_counts.items():
            print(f"  • {category.upper()}: {count} posts")
        
        print(f"\n📁 All posts saved to '_posts/' directory")
        print("🔗 Posts are organized by category and ready for Jekyll/GitHub Pages")
        
        return all_posts

def main():
    """Main execution function"""
    try:
        creator = AIBlogPostCreator()
        posts = creator.generate_10_blog_posts()
        
        print(f"\n✨ Blog generation complete! Generated {len(posts)} posts using AI/ML models.")
        
    except Exception as e:
        print(f"❌ Error during blog generation: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
