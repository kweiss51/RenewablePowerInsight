"""
SEO-Optimized Blog Generation System
Advanced ML system with comprehensive SEO metrics, quality checking, and analytics tracking
"""

import os
import re
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
import random
import subprocess

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from automated_blog_generator import AutomatedBlogGenerator


class SEOBlogGenerator(AutomatedBlogGenerator):
    """Enhanced blog generator with comprehensive SEO optimization"""
    
    def __init__(self, posts_dir: str = "posts"):
        super().__init__(posts_dir)
        
        # SEO configuration
        self.seo_config = {
            "min_word_count": 800,
            "max_word_count": 2500,
            "target_keyword_density": 0.02,  # 2%
            "max_keyword_density": 0.04,     # 4%
            "min_headings": 3,
            "min_internal_links": 2,
            "min_external_links": 3,
            "required_meta_tags": ["title", "description", "keywords"],
            "max_title_length": 60,
            "max_meta_description_length": 160,
            "min_alt_text_coverage": 0.8,   # 80% of images need alt text
            "required_schema_markup": True
        }
        
        # SEO keywords database
        self.seo_keywords = {
            "solar": [
                "solar panels", "solar energy", "photovoltaic systems", "renewable energy",
                "solar power", "clean energy", "solar installation", "solar efficiency",
                "solar technology", "green energy", "solar farm", "rooftop solar"
            ],
            "wind": [
                "wind energy", "wind turbines", "offshore wind", "wind power",
                "renewable energy", "clean energy", "wind farm", "wind technology",
                "sustainable energy", "green power", "wind generation", "wind resources"
            ],
            "battery": [
                "energy storage", "battery technology", "grid storage", "lithium batteries",
                "energy storage systems", "battery backup", "renewable storage",
                "clean energy storage", "smart grid", "energy security", "power storage"
            ],
            "policy": [
                "energy policy", "renewable incentives", "carbon pricing", "clean energy policy",
                "sustainability regulations", "green legislation", "climate policy",
                "energy transition", "renewable mandates", "carbon credits"
            ],
            "technology": [
                "clean technology", "green tech", "smart grid", "energy innovation",
                "sustainable technology", "cleantech", "energy efficiency", "green innovation",
                "renewable technology", "energy solutions", "climate tech"
            ]
        }
        
        # Internal linking structure
        self.internal_links = {
            "solar": [
                {"text": "Solar Energy Solutions", "url": "/posts/solar/"},
                {"text": "Renewable Energy Insights", "url": "/insights/"},
                {"text": "Solar Technology Research", "url": "/research/"},
                {"text": "Clean Energy Data", "url": "/data/"}
            ],
            "wind": [
                {"text": "Wind Energy Analysis", "url": "/posts/wind/"},
                {"text": "Offshore Wind Research", "url": "/research/"},
                {"text": "Renewable Energy Markets", "url": "/posts/markets/"},
                {"text": "Wind Power Data", "url": "/data/"}
            ],
            "battery": [
                {"text": "Energy Storage Solutions", "url": "/posts/battery/"},
                {"text": "Grid Technology", "url": "/posts/grid-tech/"},
                {"text": "Battery Research", "url": "/research/"},
                {"text": "Energy Storage Data", "url": "/data/"}
            ],
            "policy": [
                {"text": "Energy Policy Analysis", "url": "/posts/policy/"},
                {"text": "Renewable Energy Policy", "url": "/methodology/"},
                {"text": "Climate Policy Research", "url": "/research/"},
                {"text": "Policy Impact Data", "url": "/data/"}
            ],
            "technology": [
                {"text": "Clean Technology News", "url": "/posts/grid-tech/"},
                {"text": "Innovation Research", "url": "/research/"},
                {"text": "Technology Analysis", "url": "/insights/"},
                {"text": "Tech Market Data", "url": "/data/"}
            ]
        }
        
        # Quality metrics tracking
        self.quality_metrics = {
            "total_posts_generated": 0,
            "seo_score_average": 0,
            "readability_score_average": 0,
            "posts_with_perfect_seo": 0,
            "keyword_optimization_rate": 0,
            "image_optimization_rate": 0,
            "internal_linking_rate": 0
        }
    
    def calculate_seo_score(self, content: str, title: str, meta_description: str, 
                           category: str) -> Dict[str, any]:
        """Calculate comprehensive SEO score for generated content"""
        
        score_breakdown = {
            "word_count": 0,
            "keyword_optimization": 0,
            "title_optimization": 0,
            "meta_description": 0,
            "heading_structure": 0,
            "internal_links": 0,
            "external_links": 0,
            "image_optimization": 0,
            "readability": 0,
            "schema_markup": 0
        }
        
        # Clean content for analysis
        text_content = re.sub(r'<[^>]+>', '', content)
        word_count = len(text_content.split())
        
        # 1. Word Count Score (0-10)
        if self.seo_config["min_word_count"] <= word_count <= self.seo_config["max_word_count"]:
            score_breakdown["word_count"] = 10
        elif word_count < self.seo_config["min_word_count"]:
            score_breakdown["word_count"] = max(0, (word_count / self.seo_config["min_word_count"]) * 10)
        else:
            score_breakdown["word_count"] = max(5, 10 - (word_count - self.seo_config["max_word_count"]) / 100)
        
        # 2. Keyword Optimization Score (0-15)
        primary_keywords = self.seo_keywords.get(category, [])
        if primary_keywords:
            keyword_scores = []
            for keyword in primary_keywords[:3]:  # Check top 3 keywords
                keyword_count = text_content.lower().count(keyword.lower())
                keyword_density = keyword_count / word_count if word_count > 0 else 0
                
                if self.seo_config["target_keyword_density"] <= keyword_density <= self.seo_config["max_keyword_density"]:
                    keyword_scores.append(5)
                elif keyword_density > 0:
                    keyword_scores.append(min(5, keyword_density / self.seo_config["target_keyword_density"] * 5))
                else:
                    keyword_scores.append(0)
            
            score_breakdown["keyword_optimization"] = sum(keyword_scores)
        
        # 3. Title Optimization (0-10)
        title_score = 0
        if len(title) <= self.seo_config["max_title_length"]:
            title_score += 5
        if any(keyword.lower() in title.lower() for keyword in primary_keywords[:3]):
            title_score += 5
        score_breakdown["title_optimization"] = title_score
        
        # 4. Meta Description (0-10)
        meta_score = 0
        if meta_description:
            if len(meta_description) <= self.seo_config["max_meta_description_length"]:
                meta_score += 5
            if any(keyword.lower() in meta_description.lower() for keyword in primary_keywords[:3]):
                meta_score += 5
        score_breakdown["meta_description"] = meta_score
        
        # 5. Heading Structure (0-10)
        h2_count = len(re.findall(r'<h2[^>]*>', content))
        h3_count = len(re.findall(r'<h3[^>]*>', content))
        total_headings = h2_count + h3_count
        
        if total_headings >= self.seo_config["min_headings"]:
            score_breakdown["heading_structure"] = min(10, total_headings * 2)
        
        # 6. Internal Links (0-10)
        internal_link_pattern = r'<a[^>]*href=["\'][^"\']*(?:posts|insights|research|data|methodology)[^"\']*["\'][^>]*>'
        internal_links = len(re.findall(internal_link_pattern, content))
        score_breakdown["internal_links"] = min(10, internal_links * 5)
        
        # 7. External Links (0-10)
        external_link_pattern = r'<a[^>]*href=["\']https?://(?!.*renewablepowerinsight)[^"\']*["\'][^>]*>'
        external_links = len(re.findall(external_link_pattern, content))
        score_breakdown["external_links"] = min(10, external_links * 3)
        
        # 8. Image Optimization (0-10)
        img_tags = re.findall(r'<img[^>]*>', content)
        images_with_alt = len(re.findall(r'<img[^>]*alt=["\'][^"\']+["\'][^>]*>', content))
        
        if img_tags:
            alt_coverage = images_with_alt / len(img_tags)
            if alt_coverage >= self.seo_config["min_alt_text_coverage"]:
                score_breakdown["image_optimization"] = 10
            else:
                score_breakdown["image_optimization"] = alt_coverage * 10
        else:
            score_breakdown["image_optimization"] = 5  # Neutral if no images
        
        # 9. Readability (0-10)
        avg_sentence_length = self.calculate_avg_sentence_length(text_content)
        if 15 <= avg_sentence_length <= 25:  # Ideal range
            score_breakdown["readability"] = 10
        else:
            score_breakdown["readability"] = max(0, 10 - abs(avg_sentence_length - 20) * 0.5)
        
        # 10. Schema Markup (0-5)
        if 'itemscope' in content or 'application/ld+json' in content:
            score_breakdown["schema_markup"] = 5
        
        # Calculate total score
        total_score = sum(score_breakdown.values())
        max_possible = 100
        seo_percentage = (total_score / max_possible) * 100
        
        return {
            "total_score": total_score,
            "percentage": round(seo_percentage, 1),
            "breakdown": score_breakdown,
            "grade": self.get_seo_grade(seo_percentage),
            "recommendations": self.generate_seo_recommendations(score_breakdown, category)
        }
    
    def calculate_avg_sentence_length(self, text: str) -> float:
        """Calculate average sentence length for readability"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0
        
        total_words = sum(len(sentence.split()) for sentence in sentences)
        return total_words / len(sentences)
    
    def get_seo_grade(self, percentage: float) -> str:
        """Convert SEO percentage to letter grade"""
        if percentage >= 90:
            return "A+"
        elif percentage >= 85:
            return "A"
        elif percentage >= 80:
            return "B+"
        elif percentage >= 75:
            return "B"
        elif percentage >= 70:
            return "C+"
        elif percentage >= 65:
            return "C"
        elif percentage >= 60:
            return "D+"
        elif percentage >= 55:
            return "D"
        else:
            return "F"
    
    def generate_seo_recommendations(self, breakdown: Dict[str, float], category: str) -> List[str]:
        """Generate specific SEO improvement recommendations"""
        recommendations = []
        
        if breakdown["word_count"] < 8:
            recommendations.append("Increase content length to 800-2500 words for better SEO performance")
        
        if breakdown["keyword_optimization"] < 10:
            keywords = self.seo_keywords.get(category, [])[:3]
            recommendations.append(f"Optimize for primary keywords: {', '.join(keywords)}")
        
        if breakdown["title_optimization"] < 8:
            recommendations.append("Improve title optimization: include target keywords and keep under 60 characters")
        
        if breakdown["meta_description"] < 8:
            recommendations.append("Add compelling meta description under 160 characters with target keywords")
        
        if breakdown["heading_structure"] < 8:
            recommendations.append("Add more headings (H2, H3) to improve content structure")
        
        if breakdown["internal_links"] < 8:
            recommendations.append("Add more internal links to related content on your website")
        
        if breakdown["external_links"] < 8:
            recommendations.append("Include more authoritative external links to credible sources")
        
        if breakdown["image_optimization"] < 8:
            recommendations.append("Ensure all images have descriptive alt text for accessibility and SEO")
        
        if breakdown["readability"] < 8:
            recommendations.append("Improve readability: use shorter sentences and paragraphs")
        
        if breakdown["schema_markup"] < 3:
            recommendations.append("Add structured data markup for better search engine understanding")
        
        return recommendations
    
    def generate_seo_optimized_content(self, category: str) -> Dict[str, any]:
        """Generate content specifically optimized for SEO"""
        
        # Get base content
        base_content = self.generate_sample_content(category)
        if not base_content:
            return None
        
        # Enhance with SEO optimization
        enhanced_content = self.enhance_content_for_seo(base_content, category)
        
        # Calculate SEO metrics
        seo_score = self.calculate_seo_score(
            enhanced_content["content"],
            enhanced_content["title"],
            enhanced_content.get("meta_description", ""),
            category
        )
        
        return {
            **enhanced_content,
            "seo_score": seo_score,
            "category": category,
            "optimization_level": "enhanced"
        }
    
    def enhance_content_for_seo(self, base_content: Dict[str, str], category: str) -> Dict[str, str]:
        """Enhance base content with SEO optimizations"""
        
        title = base_content["title"]
        content = base_content["content"]
        
        # 1. Convert markdown to HTML first
        content = self.format_content_for_html(content)
        
        # 2. Optimize title with primary keyword
        primary_keywords = self.seo_keywords.get(category, [])
        if primary_keywords and primary_keywords[0].lower() not in title.lower():
            title = f"{primary_keywords[0].title()}: {title}"
        
        # Ensure title is under 60 characters
        if len(title) > 60:
            title = title[:57] + "..."
        
        # 3. Generate meta description
        meta_description = self.generate_meta_description(content, category)
        
        # 4. Add internal links
        content = self.add_internal_links(content, category)
        
        # 5. Add external links
        content = self.add_external_links(content, category)
        
        # 6. Enhance with structured data
        content = self.add_schema_markup(content, title, category)
        
        # 7. Add SEO-optimized image with alt text
        content = self.optimize_images_for_seo(content, category)
        
        # 8. Improve heading structure
        content = self.optimize_heading_structure(content, category)
        
        # 9. Add meta keywords
        meta_keywords = ", ".join(primary_keywords[:10])
        
        return {
            "title": title,
            "content": content,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords,
            "canonical_url": self.generate_canonical_url(title)
        }
    
    def generate_meta_description(self, content: str, category: str) -> str:
        """Generate SEO-optimized meta description"""
        
        # Extract first paragraph or key sentence
        text_content = re.sub(r'<[^>]+>', '', content)
        sentences = re.split(r'[.!?]+', text_content)
        
        primary_keyword = self.seo_keywords.get(category, ["renewable energy"])[0]
        
        # Create compelling meta description
        if sentences:
            first_sentence = sentences[0].strip()
            meta_desc = f"Discover the latest in {primary_keyword} technology and innovation. {first_sentence[:100]}..."
        else:
            meta_desc = f"Expert analysis and insights on {primary_keyword} trends, technology, and market developments."
        
        # Ensure it's under 160 characters
        if len(meta_desc) > 160:
            meta_desc = meta_desc[:157] + "..."
        
        return meta_desc
    
    def add_internal_links(self, content: str, category: str) -> str:
        """Add internal links to improve SEO and user experience"""
        
        internal_links = self.internal_links.get(category, [])
        if not internal_links:
            return content
        
        # Add 2-3 internal links strategically
        selected_links = random.sample(internal_links, min(3, len(internal_links)))
        
        # Find good positions to insert links
        paragraphs = content.split('</p>')
        if len(paragraphs) >= 3:
            # Add links in different paragraphs
            for i, link in enumerate(selected_links):
                if i < len(paragraphs) - 1:
                    link_html = f'<a href="{link["url"]}" title="{link["text"]}">{link["text"]}</a>'
                    
                    # Insert link naturally into paragraph
                    paragraphs[i + 1] = paragraphs[i + 1].replace(
                        'renewable energy', 
                        f'<a href="{link["url"]}">{link["text"]}</a>',
                        1
                    ) if 'renewable energy' in paragraphs[i + 1] else paragraphs[i + 1] + f' Learn more about {link_html}.'
        
        return '</p>'.join(paragraphs)
    
    def add_external_links(self, content: str, category: str) -> str:
        """Add high-quality external links for SEO"""
        
        external_links = self.relevant_links.get(category, [])
        if not external_links:
            return content
        
        # Select 3-4 high-quality external links
        selected_links = random.sample(external_links, min(4, len(external_links)))
        
        # Add external links with proper attributes
        for link in selected_links[:2]:  # Add 2 external links
            link_html = f'<a href="{link["url"]}" target="_blank" rel="noopener noreferrer" title="{link["text"]}">{link["text"]}</a>'
            
            # Find a good place to insert the link
            content = content.replace(
                'research shows', 
                f'<a href="{link["url"]}" target="_blank" rel="noopener">{link["text"]}</a> research shows',
                1
            )
        
        return content
    
    def add_schema_markup(self, content: str, title: str, category: str) -> str:
        """Add structured data markup for better SEO"""
        
        schema_data = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": title,
            "author": {
                "@type": "Organization",
                "name": "Renewable Power Insight"
            },
            "publisher": {
                "@type": "Organization",
                "name": "Renewable Power Insight",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://renewablepowerinsight.com/logo.png"
                }
            },
            "datePublished": datetime.now().isoformat(),
            "dateModified": datetime.now().isoformat(),
            "articleSection": category.title(),
            "keywords": ", ".join(self.seo_keywords.get(category, [])),
            "description": self.generate_meta_description(content, category)
        }
        
        schema_script = f'<script type="application/ld+json">{json.dumps(schema_data, indent=2)}</script>'
        
        # Add schema markup to content
        return content + f'\\n\\n{schema_script}'
    
    def optimize_images_for_seo(self, content: str, category: str) -> str:
        """Optimize images with proper alt text and SEO attributes"""
        
        # Find all img tags
        img_pattern = r'<img([^>]*)>'
        images = re.findall(img_pattern, content)
        
        for img_attrs in images:
            # Ensure alt text is present and descriptive
            if 'alt=' not in img_attrs:
                primary_keyword = self.seo_keywords.get(category, ["renewable energy"])[0]
                alt_text = f"{primary_keyword} technology and innovation"
                
                # Add alt text
                new_img_attrs = img_attrs + f' alt="{alt_text}"'
                content = content.replace(f'<img{img_attrs}>', f'<img{new_img_attrs}>')
        
        return content
    
    def optimize_heading_structure(self, content: str, category: str) -> str:
        """Optimize heading structure for better SEO"""
        
        primary_keywords = self.seo_keywords.get(category, [])
        
        # Ensure H2 and H3 tags include keywords where appropriate
        h2_pattern = r'<h2[^>]*>(.*?)</h2>'
        h3_pattern = r'<h3[^>]*>(.*?)</h3>'
        
        # Add keyword variations to headings
        for i, keyword in enumerate(primary_keywords[:3]):
            content = re.sub(
                r'<h2([^>]*)>([^<]*technology[^<]*)</h2>',
                f'<h2\\1>\\2 and {keyword.title()}</h2>',
                content,
                count=1
            )
        
        return content
    
    def format_content_for_html(self, content: str) -> str:
        """Convert markdown-style content to proper HTML formatting"""
        
        # Convert markdown headers to HTML
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', content, flags=re.MULTILINE)
        
        # Convert markdown bold to HTML
        content = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', content)
        
        # Convert markdown links to HTML
        content = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', content)
        
        # Split content into sections by double newlines
        sections = content.split('\n\n')
        formatted_sections = []
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            # Check if this is a header
            if section.startswith('<h'):
                formatted_sections.append(section)
            else:
                # Process as paragraph content
                lines = section.split('\n')
                processed_lines = []
                in_list = False
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Check for bullet points
                    if line.startswith('- ') or line.startswith('* '):
                        if not in_list:
                            processed_lines.append('<ul>')
                            in_list = True
                        processed_lines.append(f'<li>{line[2:].strip()}</li>')
                    else:
                        if in_list:
                            processed_lines.append('</ul>')
                            in_list = False
                        processed_lines.append(f'<p>{line}</p>')
                
                # Close any open lists
                if in_list:
                    processed_lines.append('</ul>')
                
                formatted_sections.extend(processed_lines)
        
        return '\n\n'.join(formatted_sections)
    
    def generate_canonical_url(self, title: str) -> str:
        """Generate canonical URL for the post"""
        
        # Convert title to URL slug
        slug = re.sub(r'[^a-zA-Z0-9\\s-]', '', title.lower())
        slug = re.sub(r'\\s+', '-', slug.strip())
        slug = re.sub(r'-+', '-', slug)
        
        return f"https://renewablepowerinsight.com/posts/{slug}"
    
    def create_seo_blog_post_html(self, content_data: Dict[str, any], category: str) -> str:
        """Create complete HTML with SEO optimizations and analytics tracking"""
        
        # Get category folder
        category_folder = self.category_folders.get(category, "general")
        
        # Generate filename
        slug = re.sub(r'[^a-zA-Z0-9\\s-]', '', content_data["title"].lower())
        slug = re.sub(r'\\s+', '-', slug.strip())
        slug = re.sub(r'-+', '-', slug)
        filename = f"{slug}.html"
        
        # Current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # SEO-optimized HTML template
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content_data["title"]} - Renewable Power Insight</title>
    <meta name="description" content="{content_data['meta_description']}">
    <meta name="keywords" content="{content_data['meta_keywords']}">
    <meta name="author" content="Renewable Power Insight">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{content_data['canonical_url']}">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="{content_data['canonical_url']}">
    <meta property="og:title" content="{content_data['title']}">
    <meta property="og:description" content="{content_data['meta_description']}">
    <meta property="og:site_name" content="Renewable Power Insight">
    
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{content_data['canonical_url']}">
    <meta property="twitter:title" content="{content_data['title']}">
    <meta property="twitter:description" content="{content_data['meta_description']}">
    
    <link rel="stylesheet" href="../../style.css">
    
    <!-- RenewablePowerInsight Analytics -->
<script>
(function() {{
    // Analytics configuration
    const ANALYTICS_CONFIG = {{
        apiEndpoint: '/api/analytics', // Update this to your analytics endpoint
        trackPageViews: true,
        trackSessions: true,
        trackEvents: true,
        trackConversions: true
    }};
    
    // Session tracking
    let sessionId = sessionStorage.getItem('rpi_session_id');
    if (!sessionId) {{
        sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        sessionStorage.setItem('rpi_session_id', sessionId);
        sessionStorage.setItem('rpi_session_start', new Date().toISOString());
        sessionStorage.setItem('rpi_is_new_user', !localStorage.getItem('rpi_returning_user') ? 'true' : 'false');
        localStorage.setItem('rpi_returning_user', 'true');
    }}
    
    // User identification
    let userId = localStorage.getItem('rpi_user_id');
    if (!userId) {{
        userId = 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        localStorage.setItem('rpi_user_id', userId);
    }}
    
    // Device detection
    function getDeviceType() {{
        const userAgent = navigator.userAgent;
        if (/tablet|ipad|playbook|silk/i.test(userAgent)) return 'tablet';
        if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\\\\sce|palm|smartphone|iemobile/i.test(userAgent)) return 'mobile';
        return 'desktop';
    }}
    
    // Traffic source detection
    function getTrafficSource() {{
        const referrer = document.referrer;
        const utm_source = new URLSearchParams(window.location.search).get('utm_source');
        
        if (utm_source) return utm_source;
        if (!referrer) return 'direct';
        
        const hostname = new URL(referrer).hostname;
        if (hostname.includes('google')) return 'google';
        if (hostname.includes('facebook')) return 'facebook';
        if (hostname.includes('twitter')) return 'twitter';
        if (hostname.includes('linkedin')) return 'linkedin';
        if (hostname.includes('youtube')) return 'youtube';
        
        return 'referral';
    }}
    
    // Page tracking
    function trackPageView() {{
        if (!ANALYTICS_CONFIG.trackPageViews) return;
        
        const pageData = {{
            event_type: 'page_view',
            session_id: sessionId,
            user_id: userId,
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer,
            user_agent: navigator.userAgent,
            device_type: getDeviceType(),
            traffic_source: getTrafficSource(),
            timestamp: new Date().toISOString()
        }};
        
        // Send to analytics endpoint
        sendAnalytics(pageData);
    }}
    
    // Session tracking
    function trackSession() {{
        if (!ANALYTICS_CONFIG.trackSessions) return;
        
        const sessionData = {{
            event_type: 'session_start',
            session_id: sessionId,
            user_id: userId,
            is_new_user: sessionStorage.getItem('rpi_is_new_user') === 'true',
            device_type: getDeviceType(),
            traffic_source: getTrafficSource(),
            landing_page: window.location.href,
            start_time: sessionStorage.getItem('rpi_session_start'),
            user_agent: navigator.userAgent
        }};
        
        sendAnalytics(sessionData);
    }}
    
    // Event tracking
    function trackEvent(eventType, properties = {{}}) {{
        if (!ANALYTICS_CONFIG.trackEvents) return;
        
        const eventData = {{
            event_type: 'custom_event',
            session_id: sessionId,
            user_id: userId,
            event_name: eventType,
            properties: properties,
            page_url: window.location.href,
            timestamp: new Date().toISOString()
        }};
        
        sendAnalytics(eventData);
    }}
    
    // Send data to analytics endpoint
    function sendAnalytics(data) {{
        // For now, log to console (replace with actual API call)
        console.log('RPI Analytics:', data);
        
        // Uncomment when you have an analytics endpoint:
        /*
        fetch(ANALYTICS_CONFIG.apiEndpoint, {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify(data)
        }}).catch(error => {{
            console.warn('Analytics tracking failed:', error);
        }});
        */
    }}
    
    // Initialize tracking when page loads
    function initAnalytics() {{
        // Track page view
        trackPageView();
        
        // Track session if it's a new session
        if (!sessionStorage.getItem('rpi_session_tracked')) {{
            trackSession();
            sessionStorage.setItem('rpi_session_tracked', 'true');
        }}
        
        // Track time on page
        let pageLoadTime = Date.now();
        let lastActivityTime = Date.now();
        
        // Update last activity on user interaction
        ['click', 'scroll', 'keypress', 'mousemove'].forEach(event => {{
            document.addEventListener(event, () => {{
                lastActivityTime = Date.now();
            }}, {{ passive: true }});
        }});
        
        // Track page exit
        window.addEventListener('beforeunload', () => {{
            const timeOnPage = (lastActivityTime - pageLoadTime) / 1000;
            
            const exitData = {{
                event_type: 'page_exit',
                session_id: sessionId,
                user_id: userId,
                page_url: window.location.href,
                time_on_page: timeOnPage,
                timestamp: new Date().toISOString()
            }};
            
            // Use sendBeacon for reliable exit tracking
            if (navigator.sendBeacon && ANALYTICS_CONFIG.apiEndpoint !== '/api/analytics') {{
                navigator.sendBeacon(
                    ANALYTICS_CONFIG.apiEndpoint,
                    JSON.stringify(exitData)
                );
            }}
        }});
        
        // Auto-track common events
        document.addEventListener('click', (e) => {{
            const target = e.target;
            
            // Track link clicks
            if (target.tagName === 'A') {{
                trackEvent('link_click', {{
                    link_text: target.textContent,
                    link_url: target.href,
                    link_target: target.target
                }});
            }}
            
            // Track button clicks
            if (target.tagName === 'BUTTON' || target.type === 'submit') {{
                trackEvent('button_click', {{
                    button_text: target.textContent,
                    button_type: target.type
                }});
            }}
        }});
        
        // Track scroll depth
        let maxScroll = 0;
        let scrollTracked = {{}};
        
        window.addEventListener('scroll', () => {{
            const scrollPercent = Math.round(
                (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
            );
            
            if (scrollPercent > maxScroll) {{
                maxScroll = scrollPercent;
                
                // Track scroll milestones
                [25, 50, 75, 90].forEach(milestone => {{
                    if (scrollPercent >= milestone && !scrollTracked[milestone]) {{
                        scrollTracked[milestone] = true;
                        trackEvent('scroll_depth', {{
                            depth_percent: milestone
                        }});
                    }}
                }});
            }}
        }});
    }}
    
    // Expose tracking functions globally
    window.rpiAnalytics = {{
        trackEvent,
        getSessionId: () => sessionId,
        getUserId: () => userId
    }};
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', initAnalytics);
    }} else {{
        initAnalytics();
    }}
}})();
</script>
<!-- End RenewablePowerInsight Analytics -->
    
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
        
        .seo-score {{
            background: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 1rem;
            margin: 1rem 0;
            font-size: 0.9rem;
        }}
        
        .seo-score-header {{
            font-weight: bold;
            color: #495057;
        }}
        
        .grade-a {{ color: #28a745; }}
        .grade-b {{ color: #ffc107; }}
        .grade-c {{ color: #fd7e14; }}
        .grade-d {{ color: #dc3545; }}
        .grade-f {{ color: #6c757d; }}
        
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
        
        .post-content a {{
            color: #007bff;
            text-decoration: none;
        }}
        
        .post-content a:hover {{
            text-decoration: underline;
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
        <article class="post" itemscope itemtype="https://schema.org/Article">
            <header class="post-header">
                <h1 class="post-title" itemprop="headline">{content_data["title"]}</h1>
                <div class="post-meta">
                    Published on <time datetime="{datetime.now().isoformat()}" itemprop="datePublished">{current_date}</time> | 
                    Category: <span itemprop="articleSection">{category.title()}</span>
                </div>
            </header>
            
            <div class="seo-score">
                <div class="seo-score-header">SEO Performance Score</div>
                <div class="grade-{content_data['seo_score']['grade'].lower().replace('+', '')}">
                    Grade: {content_data['seo_score']['grade']} ({content_data['seo_score']['percentage']}%)
                </div>
            </div>
            
            <div class="post-content" itemprop="articleBody">
                {content_data["content"]}
            </div>
            
            <div itemprop="author" itemscope itemtype="https://schema.org/Organization" style="display: none;">
                <span itemprop="name">Renewable Power Insight</span>
            </div>
            
            <a href="../../index.html" class="back-link">← Back to Home</a>
        </article>
    </main>
</body>
</html>"""
        
        return html_template, filename, category_folder
    
    def generate_and_save_seo_post(self, category: str = None) -> Dict[str, any]:
        """Generate and save a complete SEO-optimized blog post"""
        
        try:
            # Generate SEO-optimized content
            content_data = self.generate_seo_optimized_content(category or "solar")
            
            if not content_data:
                return {"success": False, "error": "Failed to generate content"}
            
            # Create HTML with SEO optimizations
            html_content, filename, category_folder = self.create_seo_blog_post_html(content_data, category)
            
            # Save to appropriate folder
            category_path = self.project_root / "posts" / category_folder
            category_path.mkdir(exist_ok=True)
            
            file_path = category_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Update quality metrics
            self.quality_metrics["total_posts_generated"] += 1
            self.quality_metrics["seo_score_average"] = (
                (self.quality_metrics["seo_score_average"] * (self.quality_metrics["total_posts_generated"] - 1) +
                 content_data["seo_score"]["percentage"]) / self.quality_metrics["total_posts_generated"]
            )
            
            if content_data["seo_score"]["percentage"] >= 90:
                self.quality_metrics["posts_with_perfect_seo"] += 1
            
            return {
                "success": True,
                "title": content_data["title"],
                "filename": str(file_path),
                "category": category,
                "seo_score": content_data["seo_score"],
                "quality_metrics": self.quality_metrics
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Demo SEO blog generation
    seo_generator = SEOBlogGenerator()
    
    print("🚀 SEO-Optimized Blog Generation Demo")
    print("=" * 50)
    
    # Generate SEO-optimized post
    result = seo_generator.generate_and_save_seo_post("solar")
    
    if result["success"]:
        print(f"✅ SEO Blog Post Generated:")
        print(f"   Title: {result['title']}")
        print(f"   File: {result['filename']}")
        print(f"   SEO Score: {result['seo_score']['grade']} ({result['seo_score']['percentage']}%)")
        print(f"   Recommendations: {len(result['seo_score']['recommendations'])} items")
        
        for rec in result['seo_score']['recommendations']:
            print(f"   • {rec}")
            
    else:
        print(f"❌ Failed to generate SEO post: {result['error']}")
