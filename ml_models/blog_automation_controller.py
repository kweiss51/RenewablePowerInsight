#!/usr/bin/env python3
"""
Blog Automation Controller with Website Integration
Manages the complete blog generation and website integration process
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import argparse
import random

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from automated_blog_generator import AutomatedBlogGenerator

# Try to import website integrator and ML components
try:
    from website_integrator import WebsiteIntegrator
    HAS_WEBSITE_INTEGRATION = True
except ImportError as e:
    print(f"⚠️  Website integration not available: {e}")
    HAS_WEBSITE_INTEGRATION = False

try:
    from inference import EnergyInference
    HAS_ML = True
except ImportError as e:
    print(f"⚠️  ML dependencies not available: {e}")
    print("📝 Running in demo mode with sample content generation")
    HAS_ML = False

class BlogAutomationController:
    """
    Controls the complete blog automation process:
    1. Generate blog posts with ML model
    2. Validate content quality (images + links)
    3. Automatically integrate into website structure
    4. Update navigation and index pages
    """
    
    def __init__(self, posts_dir: str = "../posts", website_root: str = None):
        self.posts_dir = Path(posts_dir)
        self.website_root = Path(website_root) if website_root else self.posts_dir.parent
        
        # Initialize components
        self.blog_generator = AutomatedBlogGenerator(posts_dir)
        
        if HAS_WEBSITE_INTEGRATION:
            self.website_integrator = WebsiteIntegrator(posts_dir, website_root)
        else:
            self.website_integrator = None
            print("⚠️  Website integration disabled - posts will be created without integration")
        
        # Initialize ML inference if available
        if HAS_ML:
            try:
                self.ml_inference = EnergyInference()
                print("🤖 ML inference system loaded")
            except Exception as e:
                print(f"⚠️  ML system failed to load: {e}")
                self.ml_inference = None
        else:
            self.ml_inference = None
        
        # Create logs directory
        self.logs_dir = Path("automation_logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        print("🤖 Blog Automation Controller Initialized")
        print(f"📁 Posts Directory: {self.posts_dir.resolve()}")
        print(f"🌐 Website Root: {self.website_root.resolve()}")
        
        # Comprehensive energy topics for diverse content generation
        self.energy_topics = [
            # Solar Energy Technologies
            "solar photovoltaic efficiency improvements",
            "perovskite solar cell breakthroughs", 
            "floating solar farm installations",
            "residential solar energy systems",
            "concentrated solar power developments",
            "solar panel recycling innovations",
            "agrivoltaics and dual land use",
            "building integrated photovoltaics",
            
            # Wind Energy Technologies
            "offshore wind energy developments",
            "vertical axis wind turbine technology",
            "wind energy grid integration solutions",
            "floating wind platform innovations",
            "wind turbine blade technology advances",
            "small scale wind energy systems",
            "wind forecasting and optimization",
            
            # Energy Storage Solutions
            "grid-scale battery storage deployment",
            "lithium-ion battery technology advances",
            "solid-state battery innovations",
            "pumped hydro storage projects",
            "compressed air energy storage",
            "thermal energy storage systems",
            "battery recycling and sustainability",
            "distributed energy storage networks",
            
            # Smart Grid & Infrastructure
            "smart grid cybersecurity measures",
            "microgrid technology development",
            "grid modernization initiatives",
            "demand response programs",
            "power electronics innovations",
            "transmission line upgrades",
            "distribution automation",
            "grid resilience and reliability",
            
            # Electric Vehicles & Transportation
            "electric vehicle charging infrastructure",
            "vehicle-to-grid technology adoption",
            "battery electric vehicle advances",
            "hydrogen fuel cell vehicles",
            "electric aircraft development",
            "marine electrification",
            "public transportation electrification",
            
            # Hydrogen & Fuel Cells
            "green hydrogen production methods",
            "hydrogen fuel cell technology",
            "hydrogen storage solutions",
            "industrial hydrogen applications",
            "hydrogen transportation infrastructure",
            "electrolysis efficiency improvements",
            
            # Nuclear & Advanced Energy
            "nuclear reactor innovations",
            "small modular reactor technology",
            "fusion energy research progress",
            "thorium reactor developments",
            "nuclear waste management",
            "advanced nuclear materials",
            
            # Carbon Management
            "carbon capture and storage",
            "direct air capture technology",
            "carbon utilization innovations",
            "industrial decarbonization",
            "natural carbon sequestration",
            
            # Policy & Economics
            "renewable energy investment trends",
            "clean energy policy frameworks", 
            "carbon pricing mechanisms",
            "energy transition financing",
            "renewable energy subsidies",
            "net metering policies",
            "energy market deregulation",
            "international climate agreements",
            
            # Energy Efficiency & Conservation
            "building energy efficiency",
            "industrial energy optimization",
            "heat pump technology advances",
            "smart home energy systems",
            "energy management software",
            "led lighting innovations",
            
            # Emerging Technologies
            "ocean energy harvesting",
            "tidal energy systems",
            "wave energy converters",
            "geothermal energy expansion",
            "biomass energy innovations",
            "waste-to-energy technologies",
            "artificial intelligence in energy",
            "blockchain energy applications"
        ]
    
    def create_automated_post(self, title: str, content: str = None, topic: str = None, category: str = None) -> Dict:
        """
        Create a blog post with full automation and integration
        
        Args:
            title: Blog post title
            content: Blog post content (if None, will generate from topic)
            topic: Topic for content generation
            category: Optional category override
            
        Returns:
            Complete automation result with all metrics
        """
        automation_start = datetime.now()
        
        print(f"\n🚀 Starting Automated Blog Post Creation")
        print(f"📝 Title: {title}")
        print(f"📂 Category: {category or 'Auto-detected'}")
        print("=" * 60)
        
        # Generate content if not provided
        if not content:
            if self.ml_inference and topic:
                try:
                    print(f"🤖 Generating content with ML system...")
                    content = self.ml_inference.generate_content(topic)
                except Exception as e:
                    print(f"⚠️  ML generation failed: {e}, falling back to demo content")
                    content = self._generate_demo_content(topic or title)
            else:
                print(f"📝 Generating demo content...")
                content = self._generate_demo_content(topic or title)
        
        # Step 1: Generate the blog post
        try:
            post_info = self.blog_generator.create_blog_post(
                title=title,
                content=content,
                custom_category=category
            )
            
            if not post_info:
                raise Exception("Blog post generation failed")
            
            print(f"✅ Blog post generated successfully")
            
        except Exception as e:
            error_msg = f"❌ Blog post generation failed: {e}"
            print(error_msg)
            return self._create_error_result(error_msg, automation_start)
        
        # Step 2: Website Integration (if available)
        if self.website_integrator:
            try:
                integration_success = self.website_integrator.integrate_new_post(
                    Path(post_info['file_path'])
                )
                
                if integration_success:
                    print(f"✅ Website integration completed")
                    post_info['website_integrated'] = True
                else:
                    print(f"⚠️ Website integration failed")
                    post_info['website_integrated'] = False
                    
            except Exception as e:
                print(f"⚠️ Website integration error: {e}")
                post_info['website_integrated'] = False
        else:
            post_info['website_integrated'] = False
        
        # Step 3: Generate automation report
        automation_end = datetime.now()
        automation_result = self._create_success_result(
            post_info, automation_start, automation_end
        )
        
        # Step 4: Log the automation
        self._log_automation(automation_result)
        
        # Step 5: Display summary
        self._display_automation_summary(automation_result)
        
        return automation_result
    
    
    def generate_daily_posts(self, count: int = 3) -> List[Dict[str, str]]:
        """Generate daily blog posts"""
        print(f"📅 Generating {count} daily blog posts...")
        
        # Select random topics to avoid repetition
        selected_topics = random.sample(self.energy_topics, min(count, len(self.energy_topics)))
        
        results = []
        for i, topic in enumerate(selected_topics):
            print(f"\n📝 Creating Post {i + 1}/{count}")
            print("-" * 40)
            
            # Generate title from topic
            title = self._generate_title_from_topic(topic)
            
            # Create automated post
            result = self.create_automated_post(
                title=title,
                topic=topic
            )
            
            results.append(result)
        
        return results
    
    def regenerate_website_structure(self) -> bool:
        """
        Regenerate the entire website structure with all existing posts
        
        Returns:
            Success status
        """
        if not self.website_integrator:
            print("❌ Website integration not available")
            return False
            
        print(f"\n🔄 Regenerating Complete Website Structure")
        print("=" * 60)
        
        try:
            # Get all existing posts
            all_posts = self.website_integrator.get_all_posts()
            print(f"📚 Found {len(all_posts)} existing posts")
            
            # Regenerate website structure
            success = self.website_integrator.integrate_all_posts()
            
            if success:
                print(f"✅ Website structure regenerated successfully")
                print(f"🌐 All {len(all_posts)} posts are now integrated")
                return True
            else:
                print(f"❌ Website structure regeneration failed")
                return False
                
        except Exception as e:
            print(f"❌ Error regenerating website structure: {e}")
            return False
    
    def _generate_demo_content(self, topic: str) -> str:
        """Generate demo content for a given topic"""
        return f"""# Introduction

The renewable energy sector continues to experience groundbreaking developments in {topic}. Recent innovations are reshaping how we approach sustainable energy solutions.

## Key Developments

Recent research has shown significant improvements in efficiency and cost-effectiveness. These advances are making renewable energy more accessible and viable for both residential and commercial applications.

## Market Impact

The integration of these new technologies is expected to:

- Reduce overall system costs by up to 25%
- Increase energy conversion efficiency
- Improve system reliability and longevity
- Enable new applications in challenging environments

## Industry Response

Major players in the energy sector are rapidly adopting these innovations, with several pilot projects already showing promising results.

## Future Outlook

Industry experts predict that these developments will accelerate the global transition to renewable energy, making clean power a dominant force in the energy landscape.

## Conclusion

The continued innovation in {topic} represents a crucial step toward achieving global sustainability goals and energy independence."""
    
    def _generate_title_from_topic(self, topic: str) -> str:
        """Generate an appropriate title from a topic"""
        title_templates = [
            f"Revolutionary Advances in {topic.title()}",
            f"Latest Developments in {topic.title()} Technology",
            f"Market Outlook: {topic.title()} Industry Trends",
            f"{topic.title()}: Technology Breakthrough Innovations",
            f"The Future of {topic.title()}: Industry Analysis",
            f"{topic.title()}: Latest Developments and Market Impact"
        ]
        
        return random.choice(title_templates)
    
    def _create_success_result(self, post_info: Dict, start_time: datetime, end_time: datetime) -> Dict:
        """Create automation success result"""
        return {
            'success': True,
            'timestamp': end_time.isoformat(),
            'duration_seconds': (end_time - start_time).total_seconds(),
            'post_title': post_info['title'],
            'post_filename': post_info['filename'],
            'post_path': post_info['file_path'],
            'post_category': post_info['category'],
            'post_url': post_info['url'],
            'validation_passed': post_info['validation']['is_valid'],
            'image_count': post_info['validation']['image_count'],
            'external_link_count': post_info['validation']['external_link_count'],
            'website_integrated': post_info.get('website_integrated', False),
            'quality_warning': post_info.get('quality_warning', False)
        }
    
    def _create_error_result(self, error_msg: str, start_time: datetime) -> Dict:
        """Create automation error result"""
        return {
            'success': False,
            'timestamp': datetime.now().isoformat(),
            'duration_seconds': (datetime.now() - start_time).total_seconds(),
            'error_message': error_msg,
            'post_title': None,
            'validation_passed': False,
            'website_integrated': False
        }
    
    def _log_automation(self, result: Dict):
        """Log automation result"""
        log_file = self.logs_dir / f"automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    
    def _display_automation_summary(self, result: Dict):
        """Display automation summary"""
        print(f"\n📊 AUTOMATION SUMMARY")
        print("=" * 60)
        
        if result['success']:
            print(f"✅ Status: SUCCESS")
            print(f"📝 Title: {result['post_title']}")
            print(f"📁 File: {result['post_filename']}")
            print(f"📂 Category: {result['post_category']}")
            print(f"🔗 URL: {result['post_url']}")
            print(f"🖼️  Images: {result['image_count']}")
            print(f"🔗 External Links: {result['external_link_count']}")
            print(f"✅ Validation: {'PASSED' if result['validation_passed'] else 'FAILED'}")
            print(f"🌐 Website Integration: {'SUCCESS' if result['website_integrated'] else 'FAILED'}")
            print(f"⏱️  Duration: {result['duration_seconds']:.2f} seconds")
            
            if result.get('quality_warning'):
                print(f"⚠️ Quality Warning: Post may not meet all requirements")
        else:
            print(f"❌ Status: FAILED")
            print(f"❌ Error: {result['error_message']}")
            print(f"⏱️  Duration: {result['duration_seconds']:.2f} seconds")
        
        print("=" * 60)
    
    def generate_weekly_posts(self, count: int = 10) -> List[Dict[str, str]]:
        """Generate weekly batch of blog posts"""
        print(f"📅 Generating {count} weekly blog posts...")
        
        selected_topics = random.sample(self.energy_topics, min(count, len(self.energy_topics)))
        
        if HAS_ML:
            return self.ml_inference.batch_generate_posts(selected_topics, target_length=800)
        else:
            return self._generate_demo_posts(selected_topics)
    
    def generate_custom_post(self, topic: str, category: str = None) -> Dict[str, str]:
        """Generate a single custom blog post"""
        print(f"📝 Generating custom post about: {topic}")
        
        if HAS_ML:
            return self.ml_inference.generate_and_save_blog_post(topic, category=category)
        else:
            return self._generate_demo_post(topic, category)
    
    def _generate_demo_posts(self, topics: List[str]) -> List[Dict[str, str]]:
        """Generate demo posts when ML system is not available"""
        posts_created = []
        
        for topic in topics:
            post_info = self._generate_demo_post(topic)
            posts_created.append(post_info)
        
        return posts_created
    
    def _generate_demo_post(self, topic: str, category: str = None) -> Dict[str, str]:
        """Generate a single demo post"""
        
        # Create title from topic
        title = self._topic_to_title(topic)
        
        # Generate demo content
        content = self._generate_demo_content(topic)
        
        # Save using blog generator (which will automatically add 3-5 embedded links)
        post_info = self.blog_generator.create_blog_post(
            title=title,
            content=content,
            custom_category=category
        )
        
        return post_info
    
    def _topic_to_title(self, topic: str) -> str:
        """Convert topic to blog title"""
        # Capitalize and clean up the topic
        title = topic.replace("-", " ").title()
        
        # Add some variety to titles
        title_templates = [
            "{}: Latest Developments and Market Impact",
            "Revolutionary Advances in {}: 2025 Update",
            "The Future of {}: Industry Analysis",
            "{} Technology: Breakthrough Innovations",
            "Market Outlook: {} Industry Trends",
            "{} Solutions: Powering the Clean Energy Transition"
        ]
        
        template = random.choice(title_templates)
        return template.format(title)
    
    def _generate_demo_content(self, topic: str) -> str:
        """Generate demo content for a topic"""
        
        content_template = f"""# Introduction

The renewable energy sector continues to witness groundbreaking developments in {topic}. These innovations are reshaping the landscape of clean energy and accelerating the global transition toward sustainability.

## Current Market Dynamics

Recent market analysis shows significant growth in the {topic} sector, driven by technological advances, policy support, and increasing investor confidence. Industry leaders are reporting unprecedented demand and expanding their operations to meet growing market needs.

## Technological Breakthroughs

Key technological developments include:

- Enhanced efficiency and performance metrics
- Reduced manufacturing and installation costs
- Improved reliability and lifespan
- Better integration with existing infrastructure
- Advanced monitoring and control systems

## Economic Impact

The economic implications of these developments are substantial:

- Job creation in manufacturing and installation
- Reduced energy costs for consumers
- Increased energy independence
- Attraction of significant investment capital
- Development of new supply chain opportunities

## Environmental Benefits

Environmental advantages include:

- Significant reduction in carbon emissions
- Minimal environmental footprint
- Sustainable resource utilization
- Support for biodiversity conservation
- Contribution to climate change mitigation goals

## Industry Challenges

Despite promising developments, the industry faces several challenges:

- Regulatory and permitting complexities
- Grid integration requirements
- Initial capital investment needs
- Supply chain optimization
- Skilled workforce development

## Future Outlook

Looking ahead, {topic} is positioned to play a crucial role in the global energy transition. Industry experts predict continued growth, technological advancement, and cost reductions that will make these solutions increasingly attractive to consumers and businesses alike.

## Policy Implications

Government policies and regulations continue to shape the development of {topic}. Supportive policy frameworks, including tax incentives, renewable energy standards, and research funding, are essential for continued progress.

## Conclusion

The future of {topic} appears bright, with technological innovations, supportive policies, and market dynamics all contributing to rapid sector growth. As these technologies mature and costs continue to decline, they will play an increasingly important role in achieving global sustainability goals and energy security."""

        return content_template
    
    def get_automation_stats(self) -> Dict[str, any]:
        """Get statistics about generated posts"""
        posts_dir = Path("../posts")
        
        if not posts_dir.exists():
            return {"total_posts": 0, "posts_dir_exists": False}
        
        html_files = list(posts_dir.glob("*.html"))
        
        return {
            "total_posts": len(html_files),
            "posts_dir_exists": True,
            "recent_posts": [f.name for f in sorted(html_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]],
            "posts_directory": str(posts_dir.absolute())
        }

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Automated Blog Post Generator")
    parser.add_argument("--mode", choices=["daily", "weekly", "custom"], default="daily",
                        help="Generation mode")
    parser.add_argument("--count", type=int, default=3,
                        help="Number of posts to generate")
    parser.add_argument("--topic", type=str,
                        help="Custom topic for single post generation")
    parser.add_argument("--category", type=str,
                        help="Category for custom post")
    parser.add_argument("--stats", action="store_true",
                        help="Show automation statistics")
    
    args = parser.parse_args()
    
    # Initialize controller
    controller = BlogAutomationController()
    
    # Handle stats request
    if args.stats:
        stats = controller.get_automation_stats()
        print("\n📊 Blog Automation Statistics")
        print("=" * 30)
        print(f"Total posts: {stats['total_posts']}")
        print(f"Posts directory: {stats['posts_directory']}")
        if stats['recent_posts']:
            print("Recent posts:")
            for post in stats['recent_posts']:
                print(f"  - {post}")
        return
    
    # Generate posts based on mode
    if args.mode == "daily":
        posts = controller.generate_daily_posts(args.count)
    elif args.mode == "weekly":
        posts = controller.generate_weekly_posts(args.count)
    elif args.mode == "custom":
        if not args.topic:
            print("❌ Custom mode requires --topic argument")
            return
        post = controller.generate_custom_post(args.topic, args.category)
        posts = [post]
    
    # Summary
    print(f"\n🎉 Generation Complete!")
    print(f"📊 Generated {len(posts)} posts")
    print(f"📁 Saved to posts/ directory")
    
    # Show generated posts
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post.get('title', 'Untitled')} ({post.get('filename', 'unknown')})")

if __name__ == "__main__":
    main()
