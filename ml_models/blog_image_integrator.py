"""
Blog Post Image Integration System
Automatically applies scraped images to blog posts based on topic analysis
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional
from .energy_image_scraper import EnergyImageScraper

class BlogImageIntegrator:
    """Integrates scraped images into blog posts"""
    
    def __init__(self):
        self.posts_dir = Path("_posts")
        self.image_scraper = EnergyImageScraper()
        
        # Topic keywords for better matching
        self.topic_keywords = {
            "solar": ["solar", "photovoltaic", "pv", "perovskite", "silicon"],
            "wind": ["wind", "turbine", "onshore", "offshore"],
            "battery": ["battery", "lithium", "storage", "recycling"],
            "ev": ["electric vehicle", "ev", "charging", "automotive"],
            "smart": ["smart grid", "ai", "artificial intelligence", "management"],
            "renewable": ["renewable", "clean energy", "sustainable", "green"]
        }
    
    def analyze_post_topic(self, post_content: str, post_filename: str) -> str:
        """Analyze a blog post to determine its primary energy topic"""
        text = f"{post_content} {post_filename}".lower()
        
        topic_scores = {}
        
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                # Count occurrences of each keyword
                score += text.count(keyword.lower())
            topic_scores[topic] = score
        
        # Return topic with highest score, default to renewable
        best_topic = max(topic_scores, key=topic_scores.get) if max(topic_scores.values()) > 0 else "renewable"
        return best_topic
    
    def get_best_image_for_post(self, topic: str) -> Optional[Dict]:
        """Get the best available image for a specific topic"""
        # Load image index
        index_file = self.image_scraper.base_dir / "image_index.json"
        
        if index_file.exists():
            with open(index_file, 'r') as f:
                image_index = json.load(f)
            
            # Try to find images for the specific topic
            if topic in image_index and image_index[topic]:
                # Return the first available image
                return image_index[topic][0]
        
        # Fallback to Unsplash URLs
        fallback_images = {
            "solar": {
                "url": "https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                "alt": "Advanced solar panel technology"
            },
            "wind": {
                "url": "https://images.unsplash.com/photo-1548337138-e87d889cc369?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                "alt": "Offshore wind turbines generating clean energy"
            },
            "battery": {
                "url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                "alt": "Advanced battery storage technology"
            },
            "ev": {
                "url": "https://images.unsplash.com/photo-1593941707874-ef25b8b4a92b?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                "alt": "Electric vehicle charging infrastructure"
            },
            "smart": {
                "url": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                "alt": "Smart grid and energy management systems"
            },
            "renewable": {
                "url": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                "alt": "Renewable energy technology and infrastructure"
            }
        }
        
        return {
            "path": fallback_images.get(topic, fallback_images["renewable"])["url"],
            "filename": f"fallback_{topic}.jpg",
            "source": "unsplash",
            "alt": fallback_images.get(topic, fallback_images["renewable"])["alt"]
        }
    
    def add_image_to_post(self, post_file: Path, force_update: bool = False) -> bool:
        """Add an appropriate image to a blog post"""
        with open(post_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if post already has images (unless forcing update)
        if not force_update and ('image:' in content or '![' in content):
            return False
        
        # Analyze post topic
        topic = self.analyze_post_topic(content, post_file.name)
        
        # Get appropriate image
        image_info = self.get_best_image_for_post(topic)
        if not image_info:
            return False
        
        # Parse frontmatter
        frontmatter_end = content.find('---', content.find('---') + 3)
        if frontmatter_end == -1:
            return False
        
        frontmatter = content[:frontmatter_end]
        post_content = content[frontmatter_end:]
        
        # Add image to frontmatter if not already there
        if 'image:' not in frontmatter:
            frontmatter += f'\nimage: "{image_info["path"]}"'
        
        # Add hero image to post content if not already there
        if '![' not in post_content[:200]:  # Check first 200 chars
            image_url = image_info["path"]
            alt_text = image_info.get("alt", f"{topic.title()} energy technology")
            caption = f"*{alt_text}*"
            
            hero_image = f'\n\n![{alt_text}]({image_url})\n{caption}\n'
            
            # Find the first content paragraph and insert image before it
            lines = post_content.split('\n')
            content_start = 0
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('#') and not line.startswith('<!--'):
                    content_start = i
                    break
            
            lines.insert(content_start, hero_image)
            post_content = '\n'.join(lines)
        
        # Write back to file
        new_content = frontmatter + post_content
        with open(post_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Added {topic} image to {post_file.name}")
        return True
    
    def update_all_posts(self, force_update: bool = False) -> Dict:
        """Update all blog posts with appropriate images"""
        results = {
            "updated": 0,
            "skipped": 0,
            "errors": 0,
            "posts_updated": []
        }
        
        if not self.posts_dir.exists():
            print(f"❌ Posts directory not found: {self.posts_dir}")
            return results
        
        for post_file in self.posts_dir.glob("*.md"):
            try:
                if self.add_image_to_post(post_file, force_update):
                    results["updated"] += 1
                    results["posts_updated"].append(post_file.name)
                else:
                    results["skipped"] += 1
            except Exception as e:
                print(f"❌ Error processing {post_file.name}: {e}")
                results["errors"] += 1
        
        return results
    
    def create_image_report(self) -> Dict:
        """Create a report of image usage across all posts"""
        report = {
            "total_posts": 0,
            "posts_with_images": 0,
            "posts_without_images": [],
            "topic_distribution": {},
            "image_sources": {}
        }
        
        if not self.posts_dir.exists():
            return report
        
        for post_file in self.posts_dir.glob("*.md"):
            report["total_posts"] += 1
            
            with open(post_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_image = 'image:' in content or '![' in content
            
            if has_image:
                report["posts_with_images"] += 1
                
                # Analyze topic
                topic = self.analyze_post_topic(content, post_file.name)
                report["topic_distribution"][topic] = report["topic_distribution"].get(topic, 0) + 1
                
                # Check image source
                if 'unsplash.com' in content:
                    report["image_sources"]["unsplash"] = report["image_sources"].get("unsplash", 0) + 1
                elif 'pexels.com' in content:
                    report["image_sources"]["pexels"] = report["image_sources"].get("pexels", 0) + 1
                elif '/assets/images/' in content:
                    report["image_sources"]["local"] = report["image_sources"].get("local", 0) + 1
            else:
                report["posts_without_images"].append(post_file.name)
        
        return report

def main():
    """Test the blog image integrator"""
    integrator = BlogImageIntegrator()
    
    print("🖼️ Blog Image Integration Test")
    print("=" * 50)
    
    # Create image report
    print("\n📊 Current image status:")
    report = integrator.create_image_report()
    print(f"   Total posts: {report['total_posts']}")
    print(f"   Posts with images: {report['posts_with_images']}")
    print(f"   Posts without images: {len(report['posts_without_images'])}")
    
    if report['topic_distribution']:
        print("\n   Topic distribution:")
        for topic, count in report['topic_distribution'].items():
            print(f"     {topic}: {count} posts")
    
    if report['image_sources']:
        print("\n   Image sources:")
        for source, count in report['image_sources'].items():
            print(f"     {source}: {count} images")
    
    # Update posts without images
    if report['posts_without_images']:
        print(f"\n🔧 Updating {len(report['posts_without_images'])} posts without images...")
        results = integrator.update_all_posts(force_update=False)
        print(f"   Updated: {results['updated']}")
        print(f"   Skipped: {results['skipped']}")
        print(f"   Errors: {results['errors']}")

if __name__ == "__main__":
    main()
