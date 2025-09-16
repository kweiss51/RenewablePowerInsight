#!/usr/bin/env python3
"""
Simple Blog Automation Scheduler
Easy-to-use script for running automated blog generation on schedule
"""

import schedule
import time
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from auto_blog_system import BlogAutomationSystem


class SimpleScheduler:
    """Simple scheduler for blog automation"""
    
    def __init__(self):
        self.automation = BlogAutomationSystem()
        
    def daily_posts(self):
        """Generate daily blog posts"""
        self.automation.log_message("⏰ Daily scheduled blog generation started")
        result = self.automation.run_full_automation(post_count=2)
        
        if result["success"]:
            self.automation.log_message(f"✅ Daily task complete: {result['posts_generated']} posts generated")
        else:
            self.automation.log_message("❌ Daily task failed", "ERROR")
    
    def weekly_posts(self):
        """Generate weekly blog posts (more comprehensive)"""
        self.automation.log_message("📅 Weekly scheduled blog generation started")
        
        # Generate posts for different categories
        categories = ["Solar Energy", "Wind Energy", "Energy Storage", "Energy Policy"]
        result = self.automation.run_full_automation(post_count=4, categories=categories)
        
        if result["success"]:
            self.automation.log_message(f"✅ Weekly task complete: {result['posts_generated']} posts generated")
        else:
            self.automation.log_message("❌ Weekly task failed", "ERROR")
    
    def run_scheduler(self):
        """Run the scheduler"""
        print("🚀 Blog Automation Scheduler Started")
        print("📅 Schedule:")
        print("   - Daily: 2 posts at 9:00 AM")
        print("   - Weekly: 4 posts on Mondays at 8:00 AM") 
        print("   - Press Ctrl+C to stop")
        print()
        
        # Schedule jobs
        schedule.every().day.at("09:00").do(self.daily_posts)
        schedule.every().monday.at("08:00").do(self.weekly_posts)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\\n👋 Scheduler stopped by user")


def main():
    """Main function with CLI options"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        automation = BlogAutomationSystem()
        
        if command == "now":
            # Run immediately
            print("🚀 Running blog automation now...")
            result = automation.run_full_automation(post_count=2)
            print(f"✅ Complete! Generated {result['posts_generated']} posts")
            
        elif command == "single":
            # Generate single post
            category = sys.argv[2] if len(sys.argv) > 2 else None
            print(f"📝 Generating single post for category: {category or 'random'}")
            result = automation.generate_single_post(category)
            if result["success"]:
                automation.commit_to_git(f"🤖 Generated blog post: {result['title']}")
                print(f"✅ Generated: {result['title']}")
            else:
                print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                
        elif command == "schedule":
            # Run scheduler
            scheduler = SimpleScheduler()
            scheduler.run_scheduler()
            
        else:
            print("❌ Unknown command. Use: now, single [category], or schedule")
    else:
        print("🤖 Blog Automation System")
        print("Usage:")
        print("  python simple_automation.py now              # Run immediately")
        print("  python simple_automation.py single           # Generate 1 post")
        print("  python simple_automation.py single 'Solar'   # Generate 1 solar post")
        print("  python simple_automation.py schedule         # Run on schedule")


if __name__ == "__main__":
    # Install schedule if not available
    try:
        import schedule
    except ImportError:
        print("Installing schedule library...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "schedule"])
        import schedule
    
    main()
