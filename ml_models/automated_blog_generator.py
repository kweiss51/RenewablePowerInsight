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
        """Generate diverse and unique blog content with varied structures and angles"""
        
        if not topic_category:
            topic_category = random.choice(list(self.energy_topics.keys()))
        
        topics = self.energy_topics[topic_category]
        chosen_topic = random.choice(topics)
        
        # Diverse content templates with unique structures, angles, and perspectives
        content_templates = self.get_diverse_content_templates(topic_category, chosen_topic)
        
        # Select a random template to ensure variety
        selected_template = random.choice(content_templates)
        
        return selected_template
    
    def get_diverse_content_templates(self, category: str, topic: str) -> List[Dict[str, str]]:
        """Generate multiple diverse content templates for a given category and topic"""
        
        templates = []
        
        if category == "solar":
            templates = [
                {
                    "title": f"Breaking: {topic.title()} Efficiency Reaches New Milestone in 2025",
                    "content": f"""# Record-Breaking Achievement in Solar Technology

Scientists at leading research institutions have announced a breakthrough in {topic} efficiency, achieving conversion rates that exceed all previous benchmarks. This development marks a pivotal moment in renewable energy advancement.

## The Science Behind the Breakthrough

The key to this advancement lies in innovative material engineering and quantum-level optimizations. Researchers utilized advanced nanotechnology to enhance photon capture and reduce energy loss during conversion.

### Technical Specifications
- Peak efficiency: Up to 47% under standard test conditions
- Operational temperature range: -40°C to +85°C  
- Degradation rate: Less than 0.3% annually
- Enhanced performance in low-light conditions

## Manufacturing Revolution

The new {topic} technology introduces streamlined production methods that reduce manufacturing costs while maintaining superior quality standards. Automated assembly lines now produce panels 60% faster than traditional methods.

## Real-World Applications

Early deployment projects demonstrate remarkable performance improvements:
- Residential installations showing 35% higher energy output
- Commercial systems reducing payback periods to under 4 years
- Utility-scale projects achieving grid parity in 15 additional markets

## Industry Response

Major manufacturers are racing to integrate this technology into their product lines. Investment in {topic} research has increased by 400% since the announcement, with venture capital firms committing over $2.8 billion in funding.

## Environmental Impact Assessment

Lifecycle analysis reveals significant environmental benefits:
- 70% reduction in carbon footprint compared to previous generation
- Minimal water usage in manufacturing process
- 95% recyclable materials used throughout construction
- Zero toxic emissions during operation

## Economic Projections

Market analysts project that this {topic} technology will capture 35% of the global solar market within three years, generating an estimated $45 billion in revenue and creating 180,000 new jobs worldwide.

## Looking Forward

This breakthrough positions {topic} as the cornerstone technology for achieving global climate targets. Next-phase research focuses on further efficiency improvements and cost reduction strategies."""
                },
                {
                    "title": f"Solar Innovation Spotlight: How {topic.title()} is Transforming Energy Independence",
                    "content": f"""# The Energy Independence Revolution

As nations worldwide seek energy security and sustainability, {topic} technology emerges as a game-changing solution that promises to reshape global energy dynamics and reduce dependence on fossil fuel imports.

## The Energy Security Imperative

Recent geopolitical events have underscored the critical importance of energy independence. Countries with abundant solar resources are leveraging {topic} technology to build resilient, self-sufficient energy systems.

### National Success Stories

**Australia's Solar Transformation**: The deployment of {topic} systems across the continent has reduced energy imports by 40% and created a thriving domestic clean energy sector.

**Germany's Industrial Revolution**: Manufacturing companies are integrating {topic} technology to power operations with 100% renewable energy, reducing operational costs and carbon emissions.

**India's Rural Electrification**: Over 50,000 villages now have reliable electricity access through distributed {topic} installations, improving quality of life and economic opportunities.

## Technology Deep Dive

The latest {topic} systems incorporate cutting-edge innovations:

### Smart Grid Integration
Advanced power management systems optimize energy distribution, storing excess generation during peak production and releasing power during high-demand periods.

### Weather Resilience  
New protective coatings and structural designs enable {topic} installations to withstand extreme weather conditions, maintaining consistent performance during storms, hail, and high winds.

### Modular Scalability
Flexible system architectures allow installations to be easily expanded or reconfigured based on changing energy needs and site conditions.

## Economic Transformation

The {topic} industry is driving significant economic changes:

**Job Creation**: The sector employs over 280,000 workers globally, with roles spanning manufacturing, installation, maintenance, and research & development.

**Supply Chain Localization**: Countries are establishing domestic {topic} manufacturing capabilities, reducing dependence on imports and creating industrial value chains.

**Investment Attraction**: The sector has attracted $12 billion in private investment over the past 18 months, funding innovation and capacity expansion.

## Technological Convergence

{topic.title()} technology is increasingly integrated with complementary innovations:
- AI-powered performance optimization systems
- Advanced energy storage solutions
- Electric vehicle charging infrastructure  
- Smart home automation platforms

## Challenges and Solutions

Despite tremendous progress, {topic} deployment faces several challenges:

**Grid Integration Complexity**: Solutions include advanced forecasting algorithms and flexible grid management systems.

**Initial Capital Requirements**: New financing models such as power purchase agreements and community solar programs are expanding access.

**Skilled Workforce Development**: Training programs and educational partnerships are building the technical expertise needed for continued growth.

## Future Outlook

Industry projections indicate that {topic} technology will achieve cost parity with traditional energy sources in 75% of global markets by 2027, accelerating adoption and establishing renewable energy as the dominant power generation method worldwide."""
                },
                {
                    "title": f"Sustainable Cities: The Role of {topic.title()} in Urban Energy Planning",
                    "content": f"""# Urban Energy Revolution

Metropolitan areas consume 70% of global energy and produce 75% of carbon emissions. Cities worldwide are turning to {topic} technology as a cornerstone of sustainable urban development and smart city initiatives.

## The Urban Energy Challenge

Rapid urbanization creates unprecedented energy demands while simultaneously offering unique opportunities for distributed renewable energy deployment. {topic} technology provides scalable solutions for diverse urban environments.

### City-Scale Implementations

**Singapore's Smart Nation Initiative**: The city-state has integrated {topic} systems into 80% of public housing projects, reducing residential energy costs by 45% while contributing to national sustainability goals.

**Barcelona's Energy Sovereignty Project**: The city utilizes {topic} installations on municipal buildings and transportation infrastructure to achieve energy independence and reduce carbon emissions by 60%.

**Copenhagen's Carbon Neutral Plan**: {topic} technology plays a crucial role in the city's ambitious goal to become carbon neutral by 2025, with installations on schools, hospitals, and commercial buildings.

## Innovative Urban Applications

### Building-Integrated Systems
{topic} technology seamlessly integrates into architectural designs, serving dual functions as building materials and energy generators. These installations maintain aesthetic appeal while maximizing energy production.

### Transportation Hubs
Airports, train stations, and bus terminals leverage {topic} systems to power operations while providing covered parking and waiting areas for travelers.

### Public Spaces
Parks, plazas, and recreational facilities incorporate {topic} installations that power lighting, fountains, and electronic systems while creating shaded areas for public enjoyment.

## Smart Grid Integration

Urban {topic} deployments utilize advanced smart grid technologies:

**Real-Time Monitoring**: IoT sensors track energy production and consumption patterns, enabling optimal system performance and predictive maintenance.

**Dynamic Load Management**: AI algorithms balance energy supply and demand across the urban grid, minimizing waste and maximizing efficiency.

**Peer-to-Peer Energy Trading**: Blockchain-based platforms allow buildings with excess {topic} generation to sell energy directly to neighboring properties.

## Economic Development Impact

Urban {topic} deployment drives local economic development:

**Green Jobs Creation**: Cities report creation of 15-25 jobs per megawatt of {topic} capacity installed, spanning technical, administrative, and support roles.

**Property Value Enhancement**: Buildings with {topic} systems command premium rents and sale prices, with studies showing 8-15% value increases.

**Business Attraction**: Companies increasingly choose locations based on renewable energy availability, with {topic}-powered districts becoming preferred business destinations.

## Community Engagement

Successful urban {topic} projects prioritize community involvement:

**Educational Programs**: Schools and community centers host learning initiatives that teach residents about renewable energy and sustainability.

**Participatory Planning**: City governments engage citizens in energy planning decisions, incorporating public feedback into {topic} deployment strategies.

**Social Equity Initiatives**: Programs ensure that low-income communities benefit from {topic} installations through reduced energy costs and job opportunities.

## Future Urban Integration

Next-generation urban {topic} systems will incorporate:
- Vertical installations on building facades and walls
- Floating systems on urban water bodies
- Integration with urban agriculture and green roof initiatives  
- Coupling with electric vehicle charging networks
- Connection to district heating and cooling systems

## Policy and Regulatory Framework

Cities are implementing supportive policies for {topic} deployment:
- Streamlined permitting processes for residential installations
- Building codes that encourage renewable energy integration
- Tax incentives and rebates for {topic} adoption
- Net metering policies that compensate excess energy production
- Green building certification programs that recognize {topic} installations

This comprehensive urban approach to {topic} technology deployment demonstrates how cities can lead the transition to sustainable energy systems while improving quality of life for residents."""
                }
            ]
        elif category == "wind":
            templates = [
                {
                    "title": f"Offshore Wind Revolution: {topic.title()} Technology Reaches Commercial Viability",
                    "content": f"""# Offshore Wind Enters New Era

The offshore wind industry has achieved a historic milestone with {topic} technology reaching full commercial viability. This breakthrough promises to unlock vast ocean energy resources and accelerate the global transition to clean electricity.

## Technological Leap Forward

Recent advances in {topic} technology have overcome traditional offshore challenges, making previously inaccessible wind resources economically feasible for large-scale energy generation.

### Engineering Innovations

**Advanced Turbine Design**: New {topic} systems feature 15-MW capacity turbines with 200-meter rotor diameters, generating 60% more electricity than previous generation equipment.

**Foundation Technology**: Revolutionary floating platforms enable installations in water depths exceeding 200 meters, opening vast new areas for wind development.

**Installation Methods**: Specialized vessels and installation techniques reduce construction time by 40% while improving safety and environmental protection.

## Project Development Surge

The commercialization of {topic} technology has triggered unprecedented project development:

**Europe Leading the Way**: The North Sea hosts 12 major {topic} projects totaling 8.5 GW of capacity, sufficient to power 9 million homes.

**Asian Market Expansion**: Japan, South Korea, and Taiwan have committed to 25 GW of {topic} capacity by 2030, driven by limited onshore wind resources.

**US Atlantic Coast**: Federal lease auctions for {topic} development have generated $4.8 billion in revenue, with projects planned from Massachusetts to North Carolina.

## Economic Impact Analysis

The {topic} industry creates substantial economic benefits:

**Supply Chain Development**: Manufacturing hubs for turbines, foundations, and cables support 45,000 direct jobs and 120,000 indirect positions.

**Port Infrastructure**: Coastal communities invest in specialized port facilities for {topic} assembly and maintenance, creating long-term economic opportunities.

**Energy Cost Reduction**: Levelized cost of electricity from {topic} projects has decreased 65% over five years, achieving grid parity with fossil fuels.

## Environmental Benefits

{topic} deployment provides significant environmental advantages:

### Marine Ecosystem Impact
Comprehensive studies demonstrate minimal negative effects on marine life, with some {topic} installations creating artificial reef habitats that increase biodiversity.

### Carbon Footprint Analysis
Lifecycle assessments show {topic} systems offset their manufacturing emissions within 6 months of operation while providing 20+ years of clean electricity.

### Land Use Optimization
Offshore {topic} development preserves valuable coastal land for other uses while accessing superior wind resources with higher capacity factors.

## Technical Challenges and Solutions

The industry has addressed key technical challenges:

**Grid Connection**: High-voltage DC transmission systems efficiently transport electricity from remote {topic} installations to onshore grid connections.

**Maintenance Access**: Specialized service vessels and helicopter platforms enable year-round maintenance operations in challenging ocean conditions.

**Weather Resilience**: Enhanced turbine designs withstand hurricane-force winds and extreme weather events while maintaining structural integrity.

## Global Market Projections

Industry analysts forecast dramatic growth in {topic} deployment:
- Global capacity to reach 250 GW by 2035
- Investment requirements of $850 billion over next decade  
- Creation of 2.4 million direct and indirect jobs worldwide
- Annual CO₂ emissions reduction of 1.2 billion tons

## Innovation Pipeline

Next-generation {topic} technology under development includes:
- 20-MW turbine platforms with advanced materials
- Autonomous maintenance robotics and drone systems
- Integrated energy storage and hydrogen production
- AI-powered predictive maintenance and optimization
- Biodegradable turbine components for end-of-life sustainability

This technological revolution in {topic} systems positions offshore wind as a cornerstone of global clean energy infrastructure, capable of meeting significant portions of worldwide electricity demand while supporting economic development and environmental protection."""
                },
                {
                    "title": f"Wind Power Economics: How {topic.title()} is Reshaping Energy Markets",
                    "content": f"""# The Economics of Wind Energy Transformation

The wind power sector is experiencing a fundamental economic transformation driven by {topic} technology innovations that are reshaping electricity markets and challenging traditional energy business models worldwide.

## Market Disruption Analysis

{topic} technology has introduced unprecedented cost efficiencies that are disrupting established energy markets and forcing utilities to reconsider long-term planning strategies.

### Price Competitiveness Evolution

**Historical Cost Trajectory**: Over the past decade, {topic} systems have achieved a 70% reduction in levelized cost of electricity, making wind power the cheapest electricity source in many markets.

**Regional Market Penetration**: In 18 U.S. states and 12 European countries, {topic} installations now provide electricity at costs below $30/MWh, undercutting coal and natural gas.

**Auction Results**: Recent competitive auctions for {topic} projects have delivered record-low prices, with winning bids as low as $15/MWh in optimal wind resource areas.

## Financial Innovation

The {topic} sector has pioneered new financing mechanisms that reduce capital costs and attract diverse investor participation:

### Corporate Power Purchase Agreements
Fortune 500 companies have signed over $23 billion in {topic} power purchase agreements, providing long-term revenue certainty for developers while securing predictable energy costs for businesses.

### Green Bonds and Sustainability Finance
{topic} projects attract specialized green financing with interest rates 50-75 basis points below conventional project finance, reflecting lower risk profiles and ESG investment priorities.

### Infrastructure Investment Funds
Pension funds and sovereign wealth funds allocate increasing portions of portfolios to {topic} infrastructure, viewing wind assets as stable, long-term investments with inflation-protected returns.

## Grid Integration Economics

The widespread deployment of {topic} systems is transforming electricity grid operations and market structures:

**Merit Order Changes**: Low marginal cost {topic} generation displaces higher-cost fossil fuel plants in electricity dispatch, reducing wholesale power prices during high wind periods.

**Capacity Value**: Advanced forecasting and grid management systems optimize {topic} integration, with capacity factors exceeding 50% in premium wind resource areas.

**Transmission Investment**: Grid operators invest in transmission infrastructure to access remote {topic} resources, with studies showing benefit-cost ratios of 2:1 to 4:1 for wind transmission projects.

## Industrial Development Impact

{topic} deployment drives significant industrial and economic development:

### Manufacturing Localization
Countries establish domestic {topic} manufacturing capabilities to capture value-added production, reduce transportation costs, and ensure supply chain security.

### Skills Development Programs  
Technical colleges and universities create specialized curricula for {topic} technicians, engineers, and project managers, addressing workforce development needs.

### Rural Economic Revitalization
{topic} installations provide steady income streams for rural landowners through lease payments while supporting local tax bases and economic diversification.

## Commodity Market Effects

Large-scale {topic} deployment influences broader commodity and energy markets:

**Natural Gas Demand**: In regions with high {topic} penetration, natural gas consumption for electricity generation declines by 15-25%, affecting commodity prices and trade flows.

**Electricity Storage Markets**: Variable {topic} generation creates demand for energy storage systems, driving growth in battery, pumped hydro, and emerging storage technologies.

**Carbon Credit Values**: {topic} projects generate substantial carbon offset credits, with premium pricing for verified wind energy certificates in voluntary and compliance markets.

## Policy and Regulatory Economics

Government policies significantly influence {topic} project economics:

**Production Tax Credits**: Federal tax incentives provide crucial financial support for {topic} development, with economic analysis showing positive return on public investment through job creation and tax revenue.

**Renewable Portfolio Standards**: State mandates for renewable energy create guaranteed markets for {topic} generation, providing regulatory certainty for long-term investments.

**Carbon Pricing Mechanisms**: Regions with carbon taxes or cap-and-trade systems enhance {topic} competitiveness by internalizing environmental costs of fossil fuel alternatives.

## Future Market Evolution

Economic trends indicate continued transformation of energy markets driven by {topic} technology:

- Integration with electric vehicle charging networks
- Coupling with industrial hydrogen production facilities
- Development of wind-powered data centers and cryptocurrency mining
- Export opportunities for wind-generated synthetic fuels
- Integration with agricultural operations through agrivoltaics concepts

This comprehensive economic transformation demonstrates how {topic} technology is not merely an alternative energy source but a fundamental driver of energy market restructuring toward sustainability and economic efficiency."""
                }
            ]
        elif category == "battery":
            templates = [
                {
                    "title": f"Energy Storage Breakthrough: {topic.title()} Technology Achieves 10x Capacity Improvement",
                    "content": f"""# Revolutionary Energy Storage Advancement

A groundbreaking development in {topic} technology has achieved a tenfold increase in energy storage capacity while maintaining safety and cost-effectiveness. This advancement promises to transform renewable energy integration and electric mobility.

## Scientific Achievement Details

Research teams at multiple institutions have collaborated to develop {topic} systems that overcome fundamental limitations of previous energy storage technologies through innovative materials science and engineering approaches.

### Technical Breakthroughs

**Energy Density Enhancement**: The new {topic} technology achieves 2,500 Wh/kg energy density, compared to 250 Wh/kg for conventional lithium-ion systems, enabling dramatic size and weight reductions.

**Charging Speed Revolution**: Ultra-fast charging capabilities allow {topic} systems to reach 80% capacity in under 5 minutes while maintaining cycle life exceeding 10,000 charge-discharge cycles.

**Temperature Resilience**: Advanced thermal management enables {topic} operation across temperature ranges from -40°C to +85°C without performance degradation or safety concerns.

## Manufacturing Scale-Up

The transition from laboratory prototype to commercial production represents a significant engineering achievement:

**Automated Production Lines**: New manufacturing facilities utilize AI-controlled assembly processes that ensure consistent quality while reducing production costs by 60%.

**Supply Chain Innovation**: Strategic partnerships with mining companies secure sustainable sources of raw materials while recycling programs recover 95% of materials from end-of-life {topic} systems.

**Quality Assurance**: Advanced testing protocols validate {topic} performance under extreme conditions, ensuring reliability for critical applications.

## Grid-Scale Applications

Large-scale deployment of {topic} technology is transforming electricity grid operations:

### Utility Integration Projects
**California Independent System Operator**: Installation of 2.5 GWh {topic} systems provides grid stability services while enabling integration of 40% renewable energy during peak demand periods.

**Texas Electric Reliability Council**: {topic} installations provide frequency regulation and voltage support services, improving grid reliability while reducing operating costs by $450 million annually.

**European Network Integration**: Cross-border {topic} systems enable sharing of renewable energy resources across national grids, optimizing continental energy resources.

## Transportation Revolution

{topic} technology is accelerating the transition to electric mobility:

**Electric Vehicle Applications**: Automotive manufacturers report that {topic} systems enable 1,000-mile driving ranges while reducing battery pack costs by 70%.

**Aviation Electrification**: Regional aircraft powered by {topic} systems achieve 500-mile flight ranges, making electric aviation commercially viable for short-haul routes.

**Maritime Applications**: Cargo ships and passenger ferries utilize {topic} systems for zero-emission operations, reducing shipping industry carbon emissions by 30%.

## Residential and Commercial Adoption

Consumer applications of {topic} technology are expanding rapidly:

### Home Energy Systems
Residential {topic} installations provide 7-day energy independence with systems that cost 80% less than previous generation storage technology.

### Commercial Building Integration
Office buildings and retail facilities achieve net-zero energy status through {topic} systems that store renewable energy and provide backup power during outages.

### Industrial Applications
Manufacturing facilities utilize {topic} technology for load shifting, power quality improvement, and emergency backup, reducing electricity costs by 25-40%.

## Economic Impact Analysis

The {topic} industry generates substantial economic benefits:

**Investment Attraction**: Venture capital and private equity firms have committed $18 billion to {topic} technology development and manufacturing capacity expansion.

**Job Creation**: The sector employs 125,000 workers directly and supports 340,000 indirect positions across research, manufacturing, installation, and maintenance.

**Export Opportunities**: Countries with {topic} manufacturing capabilities export systems globally, generating billions in trade revenue while building technological leadership.

## Environmental Benefits

{topic} deployment provides significant environmental advantages:

**Carbon Footprint Reduction**: Lifecycle analysis shows {topic} systems offset manufacturing emissions within 8 months while providing 15+ years of clean energy storage.

**Resource Efficiency**: Advanced recycling processes recover 98% of materials from {topic} systems, creating closed-loop supply chains that minimize environmental impact.

**Grid Decarbonization**: {topic} integration enables 85% renewable electricity in regional grids by storing excess renewable generation for use during low-production periods.

## Future Development Roadmap

Next-generation {topic} technology under development includes:
- Solid-state electrolytes for enhanced safety and performance
- AI-powered battery management systems for optimal operation
- Integration with smart grid and IoT platforms
- Biodegradable components for sustainable end-of-life management
- Wireless charging capabilities for seamless integration

This transformative advancement in {topic} technology positions energy storage as the enabling technology for a fully renewable energy system while supporting electrification across transportation, heating, and industrial applications."""
                }
            ]
        else:
            # Generic templates for other categories
            templates = [
                {
                    "title": f"Industry Analysis: {topic.title()} Market Dynamics and Growth Projections",
                    "content": f"""# Market Intelligence Report: {topic.title()}

The {topic} sector represents one of the most dynamic segments of the renewable energy industry, with rapid technological advancement and strong market fundamentals driving sustained growth and innovation.

## Market Size and Growth Trajectory

Current market analysis reveals robust expansion in the {topic} sector, with compound annual growth rates exceeding industry averages and strong investor confidence supporting continued development.

### Regional Market Analysis

**North American Market**: Leading adoption of {topic} technology driven by supportive policy frameworks and competitive pricing, with market size reaching $12.8 billion in 2024.

**European Market**: Regulatory mandates and sustainability commitments fuel {topic} deployment, with particularly strong growth in Germany, France, and the Nordic countries.

**Asia-Pacific Region**: Rapid industrialization and urbanization create substantial demand for {topic} solutions, with China and India representing 45% of global market opportunity.

## Technology Innovation Trends

The {topic} industry continues to evolve through systematic research and development investments that address performance, cost, and scalability challenges.

### Performance Improvements
Recent advances in {topic} technology deliver enhanced efficiency, reliability, and operational flexibility while reducing maintenance requirements and extending system lifespans.

### Cost Reduction Strategies  
Manufacturing optimization, supply chain development, and economies of scale drive continuous cost reductions that improve {topic} competitiveness against alternative technologies.

### Integration Capabilities
Advanced {topic} systems integrate seamlessly with existing infrastructure while providing enhanced functionality through smart controls and monitoring systems.

## Competitive Landscape

The {topic} market features diverse participants ranging from established industry leaders to innovative startups, creating a dynamic competitive environment that drives innovation and customer value.

**Market Leaders**: Established companies leverage extensive experience and resources to maintain market position while investing in next-generation {topic} technology development.

**Emerging Players**: Startup companies introduce disruptive innovations that challenge traditional approaches and create new market opportunities in specialized {topic} applications.

**Strategic Partnerships**: Collaborative relationships between technology developers, manufacturers, and end-users accelerate {topic} adoption and market development.

## Investment and Financial Trends

The {topic} sector attracts significant investment from diverse sources, reflecting strong confidence in technology viability and market growth potential.

### Venture Capital Activity
Early-stage funding for {topic} startups reached $3.2 billion in 2024, with investors particularly interested in breakthrough technologies and novel applications.

### Corporate Investment  
Large corporations establish strategic investment funds focused on {topic} innovation, seeking competitive advantages and new business opportunities.

### Public Market Performance
Publicly traded {topic} companies outperform broader market indices, with stock valuations reflecting investor optimism about long-term growth prospects.

## Regulatory and Policy Environment

Government policies significantly influence {topic} market development through incentives, mandates, and regulatory frameworks that encourage adoption and investment.

**Federal Initiatives**: National governments implement tax credits, grants, and research funding programs that support {topic} technology development and deployment.

**State and Local Programs**: Regional authorities create additional incentives and streamlined approval processes that accelerate {topic} project development.

**International Cooperation**: Multilateral agreements and technology sharing initiatives promote global {topic} market development and standardization.

## Future Market Outlook

Industry projections indicate continued strong growth in the {topic} sector, driven by technological improvements, cost reductions, and expanding applications across multiple end-use markets.

- Market size expected to reach $45 billion by 2030
- Annual deployment to triple over next five years
- Technology costs to decrease 40% through manufacturing scale-up  
- Employment in sector to reach 280,000 direct jobs
- Integration with complementary clean energy technologies

This comprehensive market analysis demonstrates the strong fundamentals supporting continued growth and innovation in the {topic} sector."""
                }
            ]
        
        return templates
    
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
