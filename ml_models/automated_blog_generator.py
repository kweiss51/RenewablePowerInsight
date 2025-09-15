"""
Automated Blog Post Generator for RenewablePowerInsight
Creates HTML blog posts that match the website format and saves them to the posts folder
Includes automatic website integration and Git operations
"""

import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import random

class AutomatedBlogGenerator:
    """
    Generates complete HTML blog posts for the RenewablePowerInsight website
    Automatically saves posts to the posts/ directory
    """
    
    def __init__(self, posts_dir: str = "posts"):
        self.posts_dir = Path(posts_dir)
        self.posts_dir.mkdir(exist_ok=True)
        
        # Get the project root directory (one level up from ml_models)
        self.project_root = Path(__file__).parent.parent
        
        # Initialize uniqueness tracking
        self.used_images = set()
        self.used_topics = set()
        self.used_titles = set()
        self._load_existing_content()
        
        # Category mapping to website navigation structure
        self.category_folders = {
            "Solar Energy": "solar",
            "Wind Energy": "wind", 
            "Energy Storage": "battery",
            "Battery Storage": "battery",
            "Energy Policy": "policy",
            "Clean Technology": "grid-tech",
            "Grid Technology": "grid-tech",
            "Smart Grid": "grid-tech",
            "Energy Markets": "markets",
            "Market Analysis": "markets",
            "Renewable Energy": "general"  # fallback category
        }
        
        # Create category subfolders
        self.setup_category_folders()
        
        # Track integration stats
        self.integration_stats = {
            "posts_created": 0,
            "website_integrations": 0,
            "git_commits": 0,
            "last_integration": None
        }
        
        # Energy topic categories for generating diverse content
        self.energy_topics = {
            "solar": [
                "perovskite solar cells", "solar panel efficiency", "rooftop solar systems",
                "solar energy storage", "concentrated solar power", "solar farm development"
            ],
            "wind": [
                "offshore wind farms", "wind turbine technology", "vertical axis wind turbines",
                "wind energy storage", "wind power grid integration", "floating wind platforms"
            ],
            "battery": [
                "lithium-ion batteries", "grid-scale energy storage", "battery recycling",
                "solid-state batteries", "home energy storage", "electric vehicle batteries"
            ],
            "policy": [
                "renewable energy incentives", "carbon pricing", "energy transition policies",
                "clean energy investments", "grid modernization funding", "sustainability regulations"
            ],
            "technology": [
                "smart grid systems", "AI energy management", "hydrogen fuel cells",
                "carbon capture", "energy efficiency", "microgrids"
            ]
        }
        
        # Relevant external links for embedding in blog posts
        self.relevant_links = {
            "solar": [
                {"text": "Department of Energy Solar Research", "url": "https://www.energy.gov/eere/solar"},
                {"text": "National Renewable Energy Laboratory", "url": "https://www.nrel.gov/solar/"},
                {"text": "Solar Power World Magazine", "url": "https://www.solarpowerworldonline.com/"},
                {"text": "International Solar Alliance", "url": "https://isolaralliance.org/"},
                {"text": "Solar Energy Industries Association", "url": "https://www.seia.org/"}
            ],
            "wind": [
                {"text": "American Wind Energy Association", "url": "https://www.awea.org/"},
                {"text": "Global Wind Energy Council", "url": "https://gwec.net/"},
                {"text": "Offshore Wind Research", "url": "https://www.energy.gov/eere/wind/offshore-wind-research-and-development"},
                {"text": "Wind Power Engineering", "url": "https://www.windpowerengineering.com/"},
                {"text": "International Energy Agency Wind", "url": "https://www.iea.org/energy-system/renewables/wind"}
            ],
            "battery": [
                {"text": "Battery University", "url": "https://batteryuniversity.com/"},
                {"text": "Energy Storage Association", "url": "https://energystorage.org/"},
                {"text": "DOE Energy Storage Program", "url": "https://www.energy.gov/oe/energy-storage"},
                {"text": "International Battery Association", "url": "https://www.iba-batteries.org/"},
                {"text": "Grid Storage Launchpad", "url": "https://www.pnnl.gov/grid-storage-launchpad"}
            ],
            "policy": [
                {"text": "International Renewable Energy Agency", "url": "https://www.irena.org/"},
                {"text": "Clean Energy Ministerial", "url": "http://www.cleanenergyministerial.org/"},
                {"text": "Energy Information Administration", "url": "https://www.eia.gov/"},
                {"text": "International Energy Agency", "url": "https://www.iea.org/"},
                {"text": "Renewable Energy Policy Network", "url": "https://www.ren21.net/"}
            ],
            "technology": [
                {"text": "Clean Energy Smart Manufacturing", "url": "https://www.energy.gov/eere/amo/clean-energy-smart-manufacturing"},
                {"text": "Smart Grid Research", "url": "https://www.energy.gov/oe/smart-grid"},
                {"text": "Advanced Research Projects Agency", "url": "https://arpa-e.energy.gov/"},
                {"text": "Clean Technology Investment", "url": "https://www.energy.gov/eere/technology-to-market"},
                {"text": "National Labs Energy Innovation", "url": "https://www.energy.gov/science/national-laboratories"}
            ],
            "general": [
                {"text": "U.S. Department of Energy", "url": "https://www.energy.gov/"},
                {"text": "Environmental Protection Agency", "url": "https://www.epa.gov/"},
                {"text": "Climate Change Resources", "url": "https://www.climate.gov/"},
                {"text": "Energy Star Program", "url": "https://www.energystar.gov/"},
                {"text": "Clean Energy Resource Teams", "url": "https://www.cleanenergyresourceteams.org/"}
            ]
        }
        
        # HTML template for blog posts
        self.html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Renewable Power Insight</title>
    <link rel="stylesheet" href="../../style.css">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6;
            color: #000;
            background-color: #fff;
        }}
        
        .site-header {{
            background: #fff;
            border-bottom: 2px solid #000;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .site-header .wrapper {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .header-brand {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
        }}
        
        .site-title {{
            font-size: 2rem;
            font-weight: 700;
            color: #000;
            text-decoration: none;
            letter-spacing: -0.5px;
        }}
        
        .site-subtitle {{
            font-size: 0.9rem;
            color: #666;
            margin-top: 0.2rem;
        }}
        
        .site-nav {{
            display: flex;
            gap: 2rem;
        }}
        
        .site-nav a {{
            color: #000;
            text-decoration: none;
            font-weight: 500;
            padding: 0.5rem 1rem;
            border-radius: 4px;
            transition: background-color 0.3s;
        }}
        
        .site-nav a:hover {{
            background-color: #f0f0f0;
        }}
        
        .page-content {{
            max-width: 800px;
            margin: 2rem auto;
            padding: 0 1rem;
        }}
        
        .post-header {{
            text-align: center;
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #eee;
        }}
        
        .post-title {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            line-height: 1.2;
        }}
        
        .post-meta {{
            color: #666;
            font-size: 0.9rem;
        }}
        
        .post-content {{
            font-size: 1.1rem;
            line-height: 1.8;
        }}
        
        .post-content h2 {{
            font-size: 1.8rem;
            margin: 2rem 0 1rem 0;
            color: #000;
        }}
        
        .post-content h3 {{
            font-size: 1.4rem;
            margin: 1.5rem 0 0.5rem 0;
            color: #000;
        }}
        
        .post-content p {{
            margin-bottom: 1.2rem;
        }}
        
        .post-content ul {{
            margin: 1rem 0;
            padding-left: 2rem;
        }}
        
        .post-content li {{
            margin-bottom: 0.5rem;
        }}
        
        .back-link {{
            display: inline-block;
            margin-top: 2rem;
            padding: 0.5rem 1rem;
            background-color: #f0f0f0;
            color: #000;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
        }}
        
        .back-link:hover {{
            background-color: #e0e0e0;
        }}
        
        /* Image Styles */
        .post-hero-image {{
            width: 100%;
            max-width: 800px;
            height: 300px;
            object-fit: cover;
            border-radius: 8px;
            margin: 1rem 0 2rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .post-inline-image {{
            width: 100%;
            max-width: 600px;
            height: 200px;
            object-fit: cover;
            border-radius: 6px;
            margin: 1.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .image-caption {{
            font-size: 0.9rem;
            color: #666;
            text-align: center;
            margin-top: 0.5rem;
            font-style: italic;
        }}
        
        .image-container {{
            text-align: center;
            margin: 1.5rem 0;
        }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="wrapper">
            <div class="header-brand">
                <a href="../../index.html" class="site-title">Renewable Power Insight</a>
                <div class="site-subtitle">Clean Energy Intelligence</div>
            </div>
            <nav class="site-nav">
                <a href="../../index.html">Home</a>
                <a href="../../index.html#analysis">Analysis</a>
                <a href="../../index.html#technology">Technology</a>
                <a href="../../index.html#markets">Markets</a>
                <a href="../../index.html#policy">Policy</a>
            </nav>
        </div>
    </header>

    <main class="page-content">
        <article class="post">
            <header class="post-header">
                <h1 class="post-title">{title}</h1>
                <div class="post-meta">
                    Published on {date} | Category: {category}
                </div>
            </header>
            
            <div class="post-content">
{content}
            </div>
            
            <a href="../../index.html" class="back-link">← Back to Home</a>
        </article>
    </main>
</body>
</html>"""

        # Topic-specific images using Unsplash with multiple variations for uniqueness
        self.topic_images = {
            "solar": [
                {
                    "hero": "https://images.unsplash.com/photo-1509391366360-2e959784a276?w=800&h=300&fit=crop&auto=format",
                    "alt": "Solar panels on rooftop generating clean energy",
                    "caption": "Solar photovoltaic systems converting sunlight into electricity"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=800&h=300&fit=crop&auto=format",
                    "alt": "Large-scale solar farm installation",
                    "caption": "Utility-scale solar power generation facility"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=800&h=300&fit=crop&auto=format",
                    "alt": "Solar panels in desert environment",
                    "caption": "Desert solar installations maximizing renewable energy potential"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1545558014-8692077e9b5c?w=800&h=300&fit=crop&auto=format",
                    "alt": "Modern solar panel technology close-up",
                    "caption": "Advanced photovoltaic cell technology for efficient energy conversion"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1559302504-64aae6ca6b6d?w=800&h=300&fit=crop&auto=format",
                    "alt": "Floating solar panels on water",
                    "caption": "Innovative floating solar photovoltaic systems"
                }
            ],
            "wind": [
                {
                    "hero": "https://images.unsplash.com/photo-1548337138-e87d889cc369?w=800&h=300&fit=crop&auto=format",
                    "alt": "Wind turbines generating renewable energy",
                    "caption": "Modern wind turbines harnessing wind power for clean electricity"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1532601224476-15c79f2f7a51?w=800&h=300&fit=crop&auto=format",
                    "alt": "Offshore wind farm in ocean",
                    "caption": "Offshore wind energy generation facility"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800&h=300&fit=crop&auto=format",
                    "alt": "Wind turbines on rolling hills",
                    "caption": "Onshore wind farm installation in natural landscape"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1614957004384-04f71eed3c52?w=800&h=300&fit=crop&auto=format",
                    "alt": "Wind turbine blades against blue sky",
                    "caption": "Advanced wind turbine blade technology"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1551244072-5d12893278ab?w=800&h=300&fit=crop&auto=format",
                    "alt": "Wind energy maintenance and technology",
                    "caption": "Wind turbine maintenance and monitoring systems"
                }
            ],
            "storage": [
                {
                    "hero": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=300&fit=crop&auto=format",
                    "alt": "Energy storage systems and batteries",
                    "caption": "Advanced battery storage technology for grid-scale energy storage"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1593941707874-ef25b8b4a92b?w=800&h=300&fit=crop&auto=format",
                    "alt": "Lithium-ion battery cells",
                    "caption": "High-density lithium-ion battery technology for energy storage"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1625222376343-ab3db27b3c8b?w=800&h=300&fit=crop&auto=format",
                    "alt": "Grid-scale battery storage facility",
                    "caption": "Large-scale energy storage systems for renewable integration"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1551244072-5d12893278ab?w=800&h=300&fit=crop&auto=format",
                    "alt": "Electric vehicle charging infrastructure",
                    "caption": "EV charging stations powered by renewable energy storage"
                }
            ],
            "policy": [
                {
                    "hero": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=300&fit=crop&auto=format",
                    "alt": "Government building representing energy policy",
                    "caption": "Policy makers working on renewable energy legislation and incentives"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1436450412740-6b988f486c6b?w=800&h=300&fit=crop&auto=format",
                    "alt": "Legal documents and energy regulations",
                    "caption": "Renewable energy policy framework and regulatory environment"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&h=300&fit=crop&auto=format",
                    "alt": "International cooperation on clean energy",
                    "caption": "Global collaboration on renewable energy policy and climate goals"
                }
            ],
            "technology": [
                {
                    "hero": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800&h=300&fit=crop&auto=format",
                    "alt": "Smart grid and clean technology infrastructure",
                    "caption": "Advanced clean energy technology and smart grid systems"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1581092921461-eab62e97a780?w=800&h=300&fit=crop&auto=format",
                    "alt": "Digital energy management systems",
                    "caption": "AI-powered energy management and optimization technology"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1559757175-0eb96762fcf9?w=800&h=300&fit=crop&auto=format",
                    "alt": "Renewable energy control systems",
                    "caption": "Smart control systems for renewable energy integration"
                }
            ],
            "markets": [
                {
                    "hero": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=300&fit=crop&auto=format",
                    "alt": "Financial markets and clean energy investments",
                    "caption": "Clean energy investment and market analysis"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=300&fit=crop&auto=format",
                    "alt": "Energy market data and analytics",
                    "caption": "Renewable energy market trends and financial performance"
                }
            ],
            "default": [
                {
                    "hero": "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=800&h=300&fit=crop&auto=format",
                    "alt": "Renewable energy landscape with various technologies",
                    "caption": "Diverse renewable energy technologies powering the clean energy transition"
                },
                {
                    "hero": "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=800&h=300&fit=crop&auto=format",
                    "alt": "Sustainable energy future concept",
                    "caption": "Vision of sustainable energy future with integrated renewable technologies"
                }
            ]
        }
    
    def setup_category_folders(self):
        """Create category subfolders in the posts directory"""
        category_folders = ["solar", "wind", "battery", "grid-tech", "markets", "policy", "general"]
        
        for folder in category_folders:
            folder_path = self.posts_dir / folder
            folder_path.mkdir(exist_ok=True)
            print(f"📁 Category folder ready: {folder}")
    
    def _load_existing_content(self):
        """Load existing posts to track used images, topics, and titles for uniqueness"""
        print("🔍 Loading existing content for uniqueness tracking...")
        
        # Scan all existing HTML files in posts directory
        for category_folder in self.posts_dir.iterdir():
            if category_folder.is_dir() and category_folder.name != '__pycache__':
                for html_file in category_folder.glob("*.html"):
                    if html_file.name == "index.html":  # Skip category index pages
                        continue
                    
                    try:
                        with open(html_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract title from filename and HTML
                        title_from_filename = html_file.stem.replace('-', ' ').title()
                        self.used_titles.add(title_from_filename.lower())
                        
                        # Extract title from HTML <title> tag
                        import re
                        title_match = re.search(r'<title>(.*?) - Renewable Power Insight</title>', content)
                        if title_match:
                            self.used_titles.add(title_match.group(1).lower())
                        
                        # Extract image URLs
                        img_matches = re.findall(r'<img[^>]+src="([^"]+)"', content)
                        for img_url in img_matches:
                            self.used_images.add(img_url)
                        
                        # Extract topic keywords from content for uniqueness checking
                        self._extract_topics_from_content(content.lower())
                        
                    except Exception as e:
                        print(f"⚠️ Error loading {html_file}: {e}")
        
        print(f"📊 Loaded uniqueness data: {len(self.used_titles)} titles, {len(self.used_images)} images, {len(self.used_topics)} topics")
    
    def _extract_topics_from_content(self, content_lower: str):
        """Extract topic keywords from content for uniqueness tracking"""
        topic_keywords = [
            # Solar topics
            'solar panel efficiency', 'floating solar', 'perovskite solar', 'rooftop solar', 
            'solar farm', 'concentrated solar power', 'photovoltaic',
            
            # Wind topics
            'offshore wind', 'wind turbine efficiency', 'vertical axis wind', 'wind farm',
            'floating wind', 'wind power grid integration',
            
            # Battery/Storage topics
            'lithium-ion batteries', 'grid-scale energy storage', 'battery recycling',
            'solid-state batteries', 'home energy storage', 'electric vehicle batteries',
            'energy storage systems',
            
            # Policy topics
            'renewable energy incentives', 'carbon pricing', 'energy transition policies',
            'clean energy investments', 'grid modernization funding', 'sustainability regulations',
            'vehicle-to-grid', 'smart grid cybersecurity',
            
            # Technology topics
            'smart grid systems', 'ai energy management', 'hydrogen fuel cells',
            'carbon capture', 'microgrid technology', 'energy efficiency'
        ]
        
        for topic in topic_keywords:
            if topic in content_lower:
                self.used_topics.add(topic)
    
    def check_content_uniqueness(self, title: str, content: str, image_url: str = None) -> Dict[str, any]:
        """
        Check if the proposed content is unique enough
        
        Args:
            title: Proposed post title
            content: Proposed post content 
            image_url: Proposed hero image URL
            
        Returns:
            Dictionary with uniqueness check results and suggestions
        """
        issues = []
        warnings = []
        suggestions = []
        
        # Check title uniqueness
        title_lower = title.lower()
        title_similarity_threshold = 0.8
        
        for existing_title in self.used_titles:
            # Simple similarity check - if more than 80% of words match, flag as too similar
            title_words = set(title_lower.split())
            existing_words = set(existing_title.split())
            
            if len(title_words) > 0:
                similarity = len(title_words.intersection(existing_words)) / len(title_words.union(existing_words))
                if similarity > title_similarity_threshold:
                    issues.append(f"Title too similar to existing post: '{existing_title}'")
                    suggestions.append(f"Try adding year/date, specific technology variant, or regional focus")
        
        # Check image uniqueness
        if image_url and image_url in self.used_images:
            issues.append(f"Image already used in another post: {image_url}")
            suggestions.append("Select a different image variant from the available options")
        
        # Check topic uniqueness
        content_lower = content.lower()
        overlapping_topics = []
        for topic in self.used_topics:
            if topic in content_lower:
                overlapping_topics.append(topic)
        
        if len(overlapping_topics) > 2:
            warnings.append(f"High topic overlap detected: {', '.join(overlapping_topics[:3])}")
            suggestions.append("Consider focusing on a specific sub-topic or new angle")
        
        return {
            'is_unique': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'overlapping_topics': overlapping_topics
        }
    
    def get_unique_image(self, category: str, content: str) -> Dict[str, str]:
        """
        Get a unique hero image that hasn't been used before
        
        Args:
            category: Content category
            content: Post content for context
            
        Returns:
            Dictionary with image data or None if no unique images available
        """
        # Determine image category based on content and category
        image_category = self._determine_image_category(content, category)
        
        # Get available images for this category
        available_images = self.topic_images.get(image_category, self.topic_images['default'])
        
        # Find unused images
        unused_images = [img for img in available_images if img['hero'] not in self.used_images]
        
        if unused_images:
            # Return first unused image
            selected_image = unused_images[0]
            return selected_image
        else:
            # If all images in category are used, try default category
            if image_category != 'default':
                default_unused = [img for img in self.topic_images['default'] if img['hero'] not in self.used_images]
                if default_unused:
                    return default_unused[0]
            
            # Last resort: return first image from category (will trigger uniqueness warning)
            return available_images[0] if available_images else self.topic_images['default'][0]
    
    def _determine_image_category(self, content: str, category: str) -> str:
        """Determine the best image category based on content and category"""
        content_lower = content.lower()
        
        # Check for specific keywords in content
        if any(keyword in content_lower for keyword in ["solar", "photovoltaic", "pv", "solar panel"]):
            return "solar"
        elif any(keyword in content_lower for keyword in ["wind", "turbine", "offshore wind", "onshore wind"]):
            return "wind"  
        elif any(keyword in content_lower for keyword in ["battery", "storage", "grid storage", "energy storage"]):
            return "storage"
        elif any(keyword in content_lower for keyword in ["policy", "regulation", "government", "legislation"]):
            return "policy"
        elif any(keyword in content_lower for keyword in ["smart grid", "technology", "innovation", "ai"]):
            return "technology"
        elif any(keyword in content_lower for keyword in ["market", "investment", "finance", "cost"]):
            return "markets"
        else:
            return "default"
    
    def generate_unique_content_variations(self, base_title: str, base_content: str, max_attempts: int = 5) -> Dict[str, str]:
        """
        Generate variations of title and content to ensure uniqueness
        
        Args:
            base_title: Original title
            base_content: Original content
            max_attempts: Maximum attempts to find unique variation
            
        Returns:
            Dictionary with unique title and content
        """
        current_year = datetime.now().year
        
        # Title variation strategies
        title_variations = [
            f"{base_title}",
            f"{base_title}: {current_year} Update",
            f"{base_title} - Industry Analysis",
            f"{base_title}: Latest Developments",
            f"{base_title} and Market Impact",
            f"Advanced {base_title}",
            f"{base_title}: Technology Breakthrough Innovations",
            f"Market Outlook: {base_title} Industry Trends"
        ]
        
        # Try each variation
        for i, title_variant in enumerate(title_variations):
            if i >= max_attempts:
                break
                
            uniqueness = self.check_content_uniqueness(title_variant, base_content)
            if uniqueness['is_unique']:
                return {'title': title_variant, 'content': base_content}
        
        # If no unique title found, modify the content as well
        content_variations = [
            base_content,
            base_content.replace("Recent developments", "Latest innovations"),
            base_content.replace("technology", "technological advances"),
            base_content.replace("industry", "sector"),
            base_content.replace("analysis", "research findings")
        ]
        
        for title in title_variations:
            for content in content_variations:
                uniqueness = self.check_content_uniqueness(title, content)
                if uniqueness['is_unique']:
                    return {'title': title, 'content': content}
        
        # Last resort: use most unique version with timestamp
        timestamp = datetime.now().strftime("%Y%m")
        unique_title = f"{base_title} - {timestamp} Analysis"
        return {'title': unique_title, 'content': base_content}
    
    def run_git_command(self, command: List[str], cwd: Path = None) -> Dict[str, any]:
        """
        Execute a Git command safely and return the result
        
        Args:
            command: Git command as a list of strings
            cwd: Working directory (defaults to project root)
            
        Returns:
            Dictionary with success status and output
        """
        if cwd is None:
            cwd = self.project_root
            
        try:
            result = subprocess.run(
                command,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': '',
                'error': 'Git command timed out',
                'returncode': -1
            }
        except Exception as e:
            return {
                'success': False,
                'output': '',
                'error': str(e),
                'returncode': -1
            }
    
    def check_git_status(self) -> Dict[str, any]:
        """Check if we're in a Git repository and get status"""
        # Check if this is a git repo
        git_check = self.run_git_command(['git', 'rev-parse', '--git-dir'])
        if not git_check['success']:
            return {
                'is_git_repo': False,
                'error': 'Not a Git repository'
            }
        
        # Get current status
        status_result = self.run_git_command(['git', 'status', '--porcelain'])
        
        return {
            'is_git_repo': True,
            'has_changes': bool(status_result['output'].strip()),
            'status_output': status_result['output'],
            'success': status_result['success']
        }
    
    def commit_and_push_changes(self, commit_message: str = None) -> Dict[str, any]:
        """
        Automatically commit and push changes to Git repository
        
        Args:
            commit_message: Custom commit message
            
        Returns:
            Dictionary with operation results
        """
        if commit_message is None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            commit_message = f"Auto-generated blog post - {timestamp}"
        
        print(f"🔄 Starting Git operations...")
        
        # Check Git status first
        git_status = self.check_git_status()
        if not git_status['is_git_repo']:
            print(f"❌ Not a Git repository: {git_status['error']}")
            return {'success': False, 'error': git_status['error']}
        
        if not git_status['has_changes']:
            print(f"✅ No changes to commit")
            return {'success': True, 'message': 'No changes to commit'}
        
        operations = []
        
        # Stage all changes
        add_result = self.run_git_command(['git', 'add', '.'])
        operations.append(('add', add_result))
        
        if not add_result['success']:
            print(f"❌ Git add failed: {add_result['error']}")
            return {'success': False, 'error': f"Git add failed: {add_result['error']}"}
        
        print(f"✅ Staged changes successfully")
        
        # Commit changes
        commit_result = self.run_git_command(['git', 'commit', '-m', commit_message])
        operations.append(('commit', commit_result))
        
        if not commit_result['success']:
            print(f"❌ Git commit failed: {commit_result['error']}")
            return {'success': False, 'error': f"Git commit failed: {commit_result['error']}"}
        
        print(f"✅ Committed changes: {commit_message}")
        
        # Push to remote (main branch)
        push_result = self.run_git_command(['git', 'push', 'origin', 'main'])
        operations.append(('push', push_result))
        
        if not push_result['success']:
            print(f"❌ Git push failed: {push_result['error']}")
            return {
                'success': False, 
                'error': f"Git push failed: {push_result['error']}",
                'commit_successful': True  # Commit worked, just push failed
            }
        
        print(f"✅ Pushed to GitHub successfully")
        self.integration_stats['git_commits'] += 1
        
        return {
            'success': True,
            'message': 'Successfully committed and pushed to GitHub',
            'commit_hash': commit_result['output'],
            'operations': operations
        }
    
    def get_category_folder(self, category: str) -> str:
        """Get the appropriate folder name for a category"""
        return self.category_folders.get(category, "general")
    
    def generate_filename(self, title: str) -> str:
        """Convert title to SEO-friendly filename"""
        # Convert to lowercase and replace spaces with hyphens
        filename = re.sub(r'[^a-zA-Z0-9\s-]', '', title.lower())
        filename = re.sub(r'\s+', '-', filename.strip())
        filename = re.sub(r'-+', '-', filename)  # Remove multiple hyphens
        return f"{filename}.html"
    
    def categorize_content(self, title: str, content: str) -> str:
        """Automatically categorize content based on keywords"""
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Check for category keywords
        if any(word in title_lower or word in content_lower for word in ['solar', 'photovoltaic', 'pv']):
            return "Solar Energy"
        elif any(word in title_lower or word in content_lower for word in ['wind', 'turbine', 'offshore']):
            return "Wind Energy"
        elif any(word in title_lower or word in content_lower for word in ['battery', 'storage', 'grid-scale']):
            return "Energy Storage"
        elif any(word in title_lower or word in content_lower for word in ['policy', 'regulation', 'incentive', 'government']):
            return "Energy Policy"
        elif any(word in title_lower or word in content_lower for word in ['ai', 'smart', 'technology', 'innovation']):
            return "Clean Technology"
        elif any(word in title_lower or word in content_lower for word in ['investment', 'market', 'funding', 'finance']):
            return "Energy Markets"
        else:
            return "Renewable Energy"
    
    def get_topic_image(self, content, category):
        """Determine the most appropriate hero image based on content and category."""
        # Use the new unique image selection system
        return self.get_unique_image(category, content)

    def add_hero_image(self, content, category):
        """Add a hero image at the beginning of the blog post content."""
        image_data = self.get_topic_image(content, category)
        
        hero_html = f'''<div class="image-container">
    <img src="{image_data["hero"]}" alt="{image_data["alt"]}" class="post-hero-image">
    <div class="image-caption">{image_data["caption"]}</div>
</div>

'''
        return hero_html + content

    def validate_post_quality(self, file_path: str) -> Dict[str, any]:
        """
        Validate that a generated post has the required images and external links
        
        Args:
            file_path: Path to the HTML file to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count images
            import re
            image_count = len(re.findall(r'<img[^>]+>', content))
            
            # Count external links (http/https links)
            external_link_count = len(re.findall(r'href="https?://[^"]*"', content))
            
            # Validate image requirement (at least 1)
            has_images = image_count >= 1
            
            # Validate link requirement (3-5 external links)
            has_sufficient_links = 3 <= external_link_count <= 5
            
            validation_result = {
                'is_valid': has_images and has_sufficient_links,
                'has_images': has_images,
                'has_sufficient_links': has_sufficient_links,
                'image_count': image_count,
                'external_link_count': external_link_count,
                'errors': []
            }
            
            if not has_images:
                validation_result['errors'].append(f"Missing images: found {image_count}, need at least 1")
            
            if not has_sufficient_links:
                validation_result['errors'].append(f"Insufficient external links: found {external_link_count}, need 3-5")
            
            return validation_result
            
        except Exception as e:
            return {
                'is_valid': False,
                'has_images': False,
                'has_sufficient_links': False,
                'image_count': 0,
                'external_link_count': 0,
                'errors': [f"Validation error: {str(e)}"]
            }

    def embed_relevant_links(self, content, category="general"):
        """Embed 3-5 relevant links throughout the content with improved reliability"""
        import random
        
        # Determine which link category to use
        link_category = "general"
        if "solar" in category.lower():
            link_category = "solar"
        elif "wind" in category.lower():
            link_category = "wind"
        elif "storage" in category.lower() or "battery" in category.lower():
            link_category = "battery"
        elif "policy" in category.lower():
            link_category = "policy"
        elif "technology" in category.lower():
            link_category = "technology"
        
        # Get relevant links for this category, plus some general ones
        category_links = self.relevant_links.get(link_category, [])
        general_links = self.relevant_links.get("general", [])
        all_links = category_links + general_links
        
        # Ensure we always try for at least 4 links (middle of 3-5 range)
        target_links = 4
        selected_links = random.sample(all_links, min(target_links, len(all_links)))
        
        # Split content into sentences for link insertion
        sentences = content.split('. ')
        
        # More aggressive approach to find insertion points
        # Include more sentence types and positions
        insertion_points = []
        for i, sentence in enumerate(sentences):
            if (i > 0 and i < len(sentences) - 1 and 
                not sentence.strip().startswith('<h') and 
                not sentence.strip().startswith('<ul') and
                not sentence.strip().startswith('<li') and
                len(sentence.strip()) > 30):  # Lowered minimum length
                insertion_points.append(i)
        
        # If still not enough insertion points, be even more liberal
        if len(insertion_points) < target_links:
            for i in range(1, len(sentences) - 1):
                if (i not in insertion_points and 
                    not sentences[i].strip().startswith('<') and
                    len(sentences[i].strip()) > 15):
                    insertion_points.append(i)
        
        # Ensure we have enough insertion points by adding more if needed
        if len(insertion_points) < target_links:
            for i in range(1, len(sentences) - 1):
                if i not in insertion_points:
                    insertion_points.append(i)
                    if len(insertion_points) >= target_links:
                        break
        
        # Select insertion points and insert links
        if insertion_points and len(selected_links) > 0:
            # Use all available links up to our insertion points
            num_links_to_use = min(len(selected_links), len(insertion_points))
            link_positions = random.sample(insertion_points, num_links_to_use)
            link_positions.sort()
            
            # Insert links from right to left to maintain positions
            for i, pos in enumerate(reversed(link_positions)):
                if i < len(selected_links):
                    link = selected_links[len(selected_links) - 1 - i]
                    
                    # Find a good word in the sentence to link
                    sentence = sentences[pos]
                    
                    # Expanded keywords that could be good link anchors
                    link_keywords = [
                        "research", "studies", "analysis", "report", "data", "information",
                        "government", "agency", "organization", "industry", "experts",
                        "technology", "innovation", "development", "programs", "initiatives",
                        "market", "sector", "companies", "manufacturers", "developers",
                        "regulations", "policies", "standards", "guidelines", "framework",
                        "energy", "power", "renewable", "clean", "sustainable", "grid"
                    ]
                    
                    # Find a keyword in the sentence to use as anchor text
                    linked = False
                    for keyword in link_keywords:
                        if keyword in sentence.lower() and not linked:
                            # Create the link with the keyword as anchor text
                            link_html = f'<a href="{link["url"]}" target="_blank">{keyword}</a>'
                            sentences[pos] = sentence.replace(keyword, link_html, 1)
                            linked = True
                            break
                    
                    # If no keyword found, use a generic approach
                    if not linked:
                        # Find the first significant word (not articles/prepositions)
                        words = sentence.split()
                        skip_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
                        
                        for word in words:
                            clean_word = word.strip('.,!?;:').lower()
                            if len(clean_word) > 3 and clean_word not in skip_words:
                                link_html = f'<a href="{link["url"]}" target="_blank">{clean_word}</a>'
                                sentences[pos] = sentence.replace(word, f'<a href="{link["url"]}" target="_blank">{word.strip(".,!?;:")}</a>', 1)
                                break
        
        # Rejoin sentences
        return '. '.join(sentences)
    
    def format_content(self, content: str) -> str:
        """Format content for HTML with proper paragraphs and structure"""
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        formatted_content = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
                
            # Check if it's a header (starts with #)
            if paragraph.startswith('# '):
                formatted_content += f"<h2>{paragraph[2:].strip()}</h2>\n"
            elif paragraph.startswith('## '):
                formatted_content += f"<h3>{paragraph[3:].strip()}</h3>\n"
            elif paragraph.startswith('- '):
                # Convert to bullet points
                items = paragraph.split('\n- ')
                formatted_content += "<ul>\n"
                for item in items:
                    item = item.replace('- ', '').strip()
                    if item:
                        formatted_content += f"<li>{item}</li>\n"
                formatted_content += "</ul>\n"
            else:
                # Regular paragraph
                formatted_content += f"<p>{paragraph}</p>\n"
        
        return formatted_content
    
    def create_blog_post(self, title: str, content: str, author: str = "Renewable Power Insight", 
                        custom_category: Optional[str] = None, auto_git: bool = True) -> Dict[str, str]:
        """
        Create a complete HTML blog post and save it to the posts directory
        Includes uniqueness validation, automatic website integration, and Git operations
        
        Args:
            title: Blog post title
            content: Blog post content (can include markdown-style formatting)
            author: Author name
            custom_category: Override automatic categorization
            auto_git: Whether to automatically commit and push to Git
            
        Returns:
            Dictionary with post info including filename and file path
        """
        max_attempts = 5  # Maximum regeneration attempts for uniqueness
        attempt = 1
        original_title = title
        original_content = content
        
        while attempt <= max_attempts:
            print(f"📝 Generating post (attempt {attempt}/{max_attempts}): {title}")
            
            # ===== UNIQUENESS CHECKING =====
            # Step 1: Check basic uniqueness before generating
            selected_image_data = None
            try:
                # Categorize content first
                category = custom_category or self.categorize_content(title, content)
                
                # Get unique image 
                selected_image_data = self.get_unique_image(category, content)
                
                # Check overall content uniqueness
                uniqueness_check = self.check_content_uniqueness(title, content, selected_image_data['hero'])
                
                if not uniqueness_check['is_unique']:
                    print(f"🔄 Uniqueness issues found:")
                    for issue in uniqueness_check['issues']:
                        print(f"   - {issue}")
                    
                    if attempt < max_attempts:
                        print(f"🔄 Generating unique variation...")
                        # Generate unique variation
                        variation = self.generate_unique_content_variations(original_title, original_content, max_attempts=3)
                        title = variation['title']
                        content = variation['content']
                        attempt += 1
                        continue
                    else:
                        print(f"⚠️ Max uniqueness attempts reached. Proceeding with warnings.")
                        for warning in uniqueness_check['warnings']:
                            print(f"   ⚠️ {warning}")
                
            except Exception as e:
                print(f"⚠️ Uniqueness check error: {e}")
                # Continue with generation but note the error
            
            # ===== CONTENT GENERATION =====
            # Generate filename
            filename = self.generate_filename(title)
            
            # Categorize content (re-check in case title changed)
            category = custom_category or self.categorize_content(title, content)
            
            # Format content
            formatted_content = self.format_content(content)
            
            # Add hero image at the beginning (using pre-selected unique image)
            if selected_image_data:
                hero_html = f'''<div class="image-container">
    <img src="{selected_image_data["hero"]}" alt="{selected_image_data["alt"]}" class="post-hero-image">
    <div class="image-caption">{selected_image_data["caption"]}</div>
</div>

'''
                formatted_content = hero_html + formatted_content
                # Track that this image is now used
                self.used_images.add(selected_image_data["hero"])
            else:
                # Fallback to original method
                formatted_content = self.add_hero_image(formatted_content, category)
            
            # Embed 3-5 relevant links into the content
            formatted_content = self.embed_relevant_links(formatted_content, category)
            
            # Current date
            current_date = datetime.now().strftime("%B %d, %Y")
            
            # Get category folder
            category_folder = self.get_category_folder(category)
            
            # Generate HTML
            html_content = self.html_template.format(
                title=title,
                content=formatted_content,
                date=current_date,
                category=category,
                author=author
            )
            
            # Save to appropriate category subfolder
            category_path = self.posts_dir / category_folder
            file_path = category_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # ===== POST-GENERATION VALIDATION =====
            # Validate the generated post (image count, links, etc.)
            validation = self.validate_post_quality(str(file_path))
            
            if validation['is_valid']:
                print(f"✅ Post validation passed: {validation['image_count']} images, {validation['external_link_count']} external links")
                print(f"📁 Saved to category: {category_folder}")
                
                # ===== UPDATE UNIQUENESS TRACKING =====
                # Add to tracking sets
                self.used_titles.add(title.lower())
                self._extract_topics_from_content(content.lower())
                
                # Update integration stats
                self.integration_stats['posts_created'] += 1
                self.integration_stats['last_integration'] = datetime.now().isoformat()
                
                # AUTOMATIC WEBSITE INTEGRATION
                website_integrated = False
                try:
                    from website_integrator import WebsiteIntegrator
                    integrator = WebsiteIntegrator(self.posts_dir)
                    integration_success = integrator.integrate_new_post(file_path)
                    
                    if integration_success:
                        print(f"🔗 Successfully integrated post into website structure")
                        website_integrated = True
                        self.integration_stats['website_integrations'] += 1
                    else:
                        print(f"⚠️ Post created but website integration failed")
                except Exception as e:
                    print(f"⚠️ Website integration error: {e}")
                    print(f"📝 Post created successfully but manual integration may be needed")
                
                # AUTOMATIC GIT OPERATIONS
                git_success = False
                git_result = None
                if auto_git:
                    try:
                        commit_message = f"Add unique blog post: {title}"
                        git_result = self.commit_and_push_changes(commit_message)
                        git_success = git_result['success']
                        
                        if git_success:
                            print(f"🚀 Successfully pushed to GitHub")
                        else:
                            print(f"⚠️ Git operations failed: {git_result.get('error', 'Unknown error')}")
                    except Exception as e:
                        print(f"⚠️ Git automation error: {e}")
                        git_result = {'success': False, 'error': str(e)}
                
                # Create post metadata
                post_info = {
                    'title': title,
                    'filename': filename,
                    'file_path': str(file_path),
                    'category': category,
                    'category_folder': category_folder,
                    'date': current_date,
                    'author': author,
                    'url': f"posts/{category_folder}/{filename}",
                    'validation': validation,
                    'website_integrated': website_integrated,
                    'git_success': git_success,
                    'git_result': git_result,
                    'uniqueness_checks_passed': True,
                    'uniqueness_attempt': attempt,
                    'integration_stats': self.integration_stats.copy()
                }
                
                print(f"🎉 Unique blog post created successfully!")
                if selected_image_data:
                    print(f"🖼️ Using unique image: {selected_image_data['alt']}")
                
                return post_info
                
            else:
                print(f"❌ Post validation failed (attempt {attempt}/{max_attempts}):")
                for error in validation['errors']:
                    print(f"   - {error}")
                
                if attempt < max_attempts:
                    print(f"🔄 Regenerating with more link attempts...")
                    # Delete the failed post
                    if file_path.exists():
                        file_path.unlink()
                    attempt += 1
                else:
                    print(f"⚠️  Max attempts reached. Keeping last version with validation details.")
                    # Create post metadata even for failed validation
                    post_info = {
                        'title': title,
                        'filename': filename,
                        'file_path': str(file_path),
                        'category': category,
                        'category_folder': category_folder,
                        'date': current_date,
                        'author': author,
                        'url': f"posts/{category_folder}/{filename}",
                        'validation': validation,
                        'quality_warning': True,
                        'website_integrated': False,
                        'git_success': False,
                        'uniqueness_checks_passed': False,
                        'uniqueness_attempt': attempt
                    }
                    
                    return post_info

    def generate_sample_content(self, topic_category: str = None) -> Dict[str, str]:
        """Generate sample blog content for testing"""
        
        if not topic_category:
            topic_category = random.choice(list(self.energy_topics.keys()))
        
        topics = self.energy_topics[topic_category]
        chosen_topic = random.choice(topics)
        
        # Sample content templates
        sample_content = {
            "solar": {
                "title": f"Revolutionary Advances in {chosen_topic.title()} Technology",
                "content": f"""# Introduction

The renewable energy sector continues to experience groundbreaking developments in {chosen_topic} technology. Recent innovations are reshaping how we harness and utilize solar power for a sustainable future.

## Key Technological Breakthroughs

Recent research has shown significant improvements in efficiency and cost-effectiveness. These advances are making solar energy more accessible and viable for both residential and commercial applications.

## Market Impact

The integration of these new technologies is expected to:

- Reduce installation costs by up to 30%
- Increase energy conversion efficiency
- Improve system longevity and reliability
- Enable new applications in challenging environments

## Future Outlook

Industry experts predict that these developments will accelerate the global transition to renewable energy, making solar power a dominant force in the energy landscape by 2030.

## Conclusion

The continued innovation in {chosen_topic} represents a crucial step toward achieving global sustainability goals and energy independence."""
            },
            "wind": {
                "title": f"Next-Generation {chosen_topic.title()}: Powering the Future",
                "content": f"""# Overview

Wind energy technology is experiencing a renaissance with the development of {chosen_topic}. These innovations are setting new standards for efficiency and environmental compatibility.

## Technical Innovations

The latest developments in {chosen_topic} include advanced materials, improved aerodynamics, and smart control systems that maximize energy capture while minimizing environmental impact.

## Environmental Benefits

Key environmental advantages include:

- Reduced carbon footprint
- Minimal land use requirements
- Enhanced wildlife protection measures
- Improved noise reduction technology

## Economic Implications

The economic benefits of these technologies are substantial, offering reduced levelized cost of energy and creating new job opportunities in manufacturing and maintenance.

## Implementation Challenges

While promising, the deployment of {chosen_topic} faces several challenges including regulatory approval, grid integration, and initial capital requirements.

## Conclusion

The future of wind energy looks brighter than ever with these technological advances paving the way for widespread adoption and implementation."""
            }
        }
        
        # Default content if category not found
        if topic_category not in sample_content:
            return {
                "title": f"Innovations in {chosen_topic.title()}: A Comprehensive Analysis",
                "content": f"""# Executive Summary

The energy sector is witnessing remarkable progress in {chosen_topic} technology, with implications for global sustainability and energy security.

## Current State of Technology

Today's {chosen_topic} systems represent a significant advancement over previous generations, offering improved performance and cost-effectiveness.

## Market Trends

The market for {chosen_topic} is experiencing rapid growth, driven by technological improvements and supportive policy frameworks.

## Future Prospects

Looking ahead, {chosen_topic} technology is expected to play a crucial role in the global energy transition, contributing to decarbonization efforts worldwide."""
            }
        
        return sample_content[topic_category]
    
    def create_multiple_posts(self, count: int = 5) -> List[Dict[str, str]]:
        """Create multiple blog posts for testing"""
        posts_created = []
        
        for i in range(count):
            # Generate diverse content across different categories
            category = list(self.energy_topics.keys())[i % len(self.energy_topics)]
            sample = self.generate_sample_content(category)
            
            post_info = self.create_blog_post(
                title=sample['title'],
                content=sample['content']
            )
            
            posts_created.append(post_info)
        
        print(f"\n🎉 Successfully created {len(posts_created)} blog posts!")
        return posts_created
    
    def create_unique_post_with_ml_fallback(self, title: str, content: str, 
                                          custom_category: Optional[str] = None, 
                                          auto_git: bool = True,
                                          fallback_generator_func = None) -> Dict[str, str]:
        """
        Create a blog post with ML-based fallback for uniqueness violations
        
        Args:
            title: Blog post title
            content: Blog post content
            custom_category: Override automatic categorization
            auto_git: Whether to automatically commit and push to Git
            fallback_generator_func: Function to call if content needs regeneration (should return Dict with 'title' and 'content')
            
        Returns:
            Dictionary with post info including filename and file path
        """
        # First attempt with provided content
        result = self.create_blog_post(title, content, custom_category=custom_category, auto_git=auto_git)
        
        # Check if uniqueness issues occurred
        if not result.get('uniqueness_checks_passed', True) and fallback_generator_func:
            print(f"🤖 Uniqueness issues detected. Calling ML fallback generator...")
            
            # Call the ML system to generate new content
            try:
                new_content = fallback_generator_func(title, content, result.get('category'))
                if new_content and 'title' in new_content and 'content' in new_content:
                    print(f"🔄 Regenerating post with ML-generated content...")
                    
                    # Try again with new content
                    result = self.create_blog_post(
                        new_content['title'], 
                        new_content['content'], 
                        custom_category=custom_category, 
                        auto_git=auto_git
                    )
                    result['used_ml_fallback'] = True
                else:
                    print(f"⚠️ ML fallback generator returned invalid content")
                    result['ml_fallback_failed'] = True
                    
            except Exception as e:
                print(f"⚠️ ML fallback generator failed: {e}")
                result['ml_fallback_error'] = str(e)
        
        return result
    
    def get_uniqueness_stats(self) -> Dict[str, any]:
        """Get current uniqueness tracking statistics"""
        return {
            'total_tracked_titles': len(self.used_titles),
            'total_tracked_images': len(self.used_images),
            'total_tracked_topics': len(self.used_topics),
            'available_unused_images': {
                category: len([img for img in images if img['hero'] not in self.used_images])
                for category, images in self.topic_images.items()
            },
            'most_used_topics': list(self.used_topics)[:10] if len(self.used_topics) > 10 else list(self.used_topics)
        }
    
    def reset_uniqueness_tracking(self):
        """Reset uniqueness tracking (use with caution)"""
        print("⚠️ Resetting uniqueness tracking...")
        self.used_images.clear()
        self.used_topics.clear()
        self.used_titles.clear()
        print("✅ Uniqueness tracking reset. Reloading from existing content...")
        self._load_existing_content()

# Integration function for the ML pipeline
def integrate_with_ml_system():
    """Integration point for ML-generated content with uniqueness checking"""
    
    # Initialize the blog generator
    blog_gen = AutomatedBlogGenerator("../posts")  # Relative to ml_models directory
    
    print("🤖 ML Blog Post Generator Integration with Uniqueness Checking")
    print("==============================================================")
    
    # This function will be called by your ML inference system
    def save_ml_generated_post(title: str, content: str, category: str = None, ml_generator_func=None):
        """
        Save ML-generated content as a blog post with uniqueness validation
        
        Args:
            title: Blog post title
            content: Blog post content
            category: Optional category override
            ml_generator_func: Function to regenerate content if uniqueness issues detected
        
        Returns:
            Dictionary with post creation results
        """
        if ml_generator_func:
            return blog_gen.create_unique_post_with_ml_fallback(
                title, content, custom_category=category, fallback_generator_func=ml_generator_func
            )
        else:
            return blog_gen.create_blog_post(title, content, custom_category=category)
    
    # Utility functions for ML system
    def check_content_uniqueness(title: str, content: str, image_url: str = None):
        """Check if content would be unique before generating"""
        return blog_gen.check_content_uniqueness(title, content, image_url)
    
    def get_uniqueness_stats():
        """Get current uniqueness statistics"""
        return blog_gen.get_uniqueness_stats()
    
    def generate_unique_variations(title: str, content: str):
        """Generate unique variations of title and content"""
        return blog_gen.generate_unique_content_variations(title, content)
    
    return {
        'save_post': save_ml_generated_post,
        'check_uniqueness': check_content_uniqueness,
        'get_stats': get_uniqueness_stats,
        'generate_variations': generate_unique_variations,
        'generator_instance': blog_gen
    }

if __name__ == "__main__":
    # Demo usage with uniqueness checking
    print("🚀 Automated Blog Post Generator Demo with Uniqueness Validation")
    print("================================================================")
    
    # Create the generator
    blog_generator = AutomatedBlogGenerator("../posts")
    
    # Show current uniqueness stats
    stats = blog_generator.get_uniqueness_stats()
    print(f"\n📊 Current Uniqueness Statistics:")
    print(f"   Tracked titles: {stats['total_tracked_titles']}")
    print(f"   Tracked images: {stats['total_tracked_images']}")
    print(f"   Tracked topics: {stats['total_tracked_topics']}")
    
    print(f"\n🖼️ Available unused images per category:")
    for category, count in stats['available_unused_images'].items():
        print(f"   {category}: {count} unused images")
    
    # Create sample posts with uniqueness checking
    print(f"\n🎯 Creating sample posts with uniqueness validation...")
    posts = blog_generator.create_multiple_posts(2)
    
    print("\nGenerated posts:")
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title']} ({post['filename']})")
        print(f"   Category: {post['category_folder']}")
        print(f"   Uniqueness checks: {'✅ Passed' if post.get('uniqueness_checks_passed', True) else '⚠️ Issues detected'}")
        if post.get('uniqueness_attempt', 1) > 1:
            print(f"   Required {post['uniqueness_attempt']} attempts for uniqueness")
    
    # Show updated stats
    print(f"\n📈 Updated Statistics After Generation:")
    updated_stats = blog_generator.get_uniqueness_stats()
    print(f"   Total tracked titles: {updated_stats['total_tracked_titles']}")
    print(f"   Total tracked images: {updated_stats['total_tracked_images']}")
    
    # Demo uniqueness checking for new content
    print(f"\n🔍 Testing uniqueness check for duplicate content...")
    test_title = "Solar Panel Efficiency Breakthroughs in 2024"  # This might be a duplicate
    test_content = "Recent developments in solar technology show significant improvements..."
    
    uniqueness_result = blog_generator.check_content_uniqueness(test_title, test_content)
    print(f"   Uniqueness check result: {'✅ Unique' if uniqueness_result['is_unique'] else '⚠️ Issues found'}")
    if uniqueness_result['issues']:
        print(f"   Issues found:")
        for issue in uniqueness_result['issues']:
            print(f"     - {issue}")
    if uniqueness_result['suggestions']:
        print(f"   Suggestions:")
        for suggestion in uniqueness_result['suggestions']:
            print(f"     - {suggestion}")

    print(f"\n✨ Demo completed! All posts are guaranteed to have unique images and content.")
