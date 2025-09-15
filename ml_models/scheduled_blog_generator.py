#!/usr/bin/env python3
"""
Scheduled Blog Post Generator
Automatically generates blog posts on a schedule for the RenewablePowerInsight website
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import schedule
import time
import argparse
from typing import Dict, List

# Add the ml_models directory to the path
sys.path.append(str(Path(__file__).parent))

from blog_automation_controller import BlogAutomationController

class ScheduledBlogGenerator:
    """Manages scheduled blog post generation"""
    
    def __init__(self, config_file: str = "blog_schedule_config.json"):
        self.config_file = Path(config_file)
        self.controller = BlogAutomationController()
        self.load_config()
        
    def load_config(self):
        """Load or create configuration"""
        default_config = {
            "daily_posts_count": 2,
            "weekly_posts_count": 5,
            "daily_time": "09:00",
            "weekly_day": "monday",
            "weekly_time": "08:00",
            "enabled": True,
            "last_daily_run": None,
            "last_weekly_run": None,
            "total_posts_generated": 0
        }
        
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def update_last_run(self, run_type: str):
        """Update the last run timestamp"""
        now = datetime.now().isoformat()
        if run_type == "daily":
            self.config["last_daily_run"] = now
        elif run_type == "weekly":
            self.config["last_weekly_run"] = now
        self.save_config()
    
    def generate_daily_posts(self):
        """Generate daily blog posts"""
        if not self.config["enabled"]:
            print("⏸️  Blog generation is disabled in config")
            return
        
        print(f"📅 Starting daily blog post generation at {datetime.now()}")
        
        try:
            posts = self.controller.generate_daily_posts(self.config["daily_posts_count"])
            self.config["total_posts_generated"] += len(posts)
            self.update_last_run("daily")
            
            print(f"✅ Daily generation complete: {len(posts)} posts created")
            
            # Log generation
            self.log_generation("daily", len(posts))
            
        except Exception as e:
            print(f"❌ Error in daily generation: {e}")
            self.log_error("daily", str(e))
    
    def generate_weekly_posts(self):
        """Generate weekly blog posts"""
        if not self.config["enabled"]:
            print("⏸️  Blog generation is disabled in config")
            return
        
        print(f"📅 Starting weekly blog post generation at {datetime.now()}")
        
        try:
            posts = self.controller.generate_weekly_posts(self.config["weekly_posts_count"])
            self.config["total_posts_generated"] += len(posts)
            self.update_last_run("weekly")
            
            print(f"✅ Weekly generation complete: {len(posts)} posts created")
            
            # Log generation
            self.log_generation("weekly", len(posts))
            
        except Exception as e:
            print(f"❌ Error in weekly generation: {e}")
            self.log_error("weekly", str(e))
    
    def log_generation(self, generation_type: str, post_count: int):
        """Log successful generation"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": generation_type,
            "posts_generated": post_count,
            "status": "success"
        }
        self.append_to_log(log_entry)
    
    def log_error(self, generation_type: str, error_message: str):
        """Log generation error"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": generation_type,
            "error": error_message,
            "status": "error"
        }
        self.append_to_log(log_entry)
    
    def append_to_log(self, log_entry: Dict):
        """Append entry to log file"""
        log_file = Path("blog_generation.log")
        
        # Keep only the last 100 entries
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                except json.JSONDecodeError:
                    logs = []
        else:
            logs = []
        
        logs.append(log_entry)
        logs = logs[-100:]  # Keep only last 100 entries
        
        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def setup_schedule(self):
        """Set up the generation schedule"""
        print("⏰ Setting up blog post generation schedule...")
        
        # Daily posts
        daily_time = self.config["daily_time"]
        schedule.every().day.at(daily_time).do(self.generate_daily_posts)
        print(f"📅 Daily posts scheduled for {daily_time}")
        
        # Weekly posts
        weekly_day = self.config["weekly_day"].lower()
        weekly_time = self.config["weekly_time"]
        
        if weekly_day == "monday":
            schedule.every().monday.at(weekly_time).do(self.generate_weekly_posts)
        elif weekly_day == "tuesday":
            schedule.every().tuesday.at(weekly_time).do(self.generate_weekly_posts)
        elif weekly_day == "wednesday":
            schedule.every().wednesday.at(weekly_time).do(self.generate_weekly_posts)
        elif weekly_day == "thursday":
            schedule.every().thursday.at(weekly_time).do(self.generate_weekly_posts)
        elif weekly_day == "friday":
            schedule.every().friday.at(weekly_time).do(self.generate_weekly_posts)
        elif weekly_day == "saturday":
            schedule.every().saturday.at(weekly_time).do(self.generate_weekly_posts)
        elif weekly_day == "sunday":
            schedule.every().sunday.at(weekly_time).do(self.generate_weekly_posts)
        
        print(f"📅 Weekly posts scheduled for {weekly_day.title()} at {weekly_time}")
    
    def run_scheduler(self):
        """Run the scheduler"""
        self.setup_schedule()
        
        print("🚀 Blog post scheduler started!")
        print(f"📊 Configuration:")
        print(f"   Daily: {self.config['daily_posts_count']} posts at {self.config['daily_time']}")
        print(f"   Weekly: {self.config['weekly_posts_count']} posts on {self.config['weekly_day']} at {self.config['weekly_time']}")
        print(f"   Total posts generated so far: {self.config['total_posts_generated']}")
        print("⏰ Waiting for scheduled times... (Press Ctrl+C to stop)")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n⏹️  Scheduler stopped by user")
    
    def run_once(self, generation_type: str):
        """Run generation once immediately"""
        if generation_type == "daily":
            self.generate_daily_posts()
        elif generation_type == "weekly":
            self.generate_weekly_posts()
        else:
            print(f"❌ Unknown generation type: {generation_type}")
    
    def get_status(self):
        """Get scheduler status"""
        print("📊 Blog Post Scheduler Status")
        print("=" * 30)
        print(f"Enabled: {self.config['enabled']}")
        print(f"Total posts generated: {self.config['total_posts_generated']}")
        print(f"Last daily run: {self.config.get('last_daily_run', 'Never')}")
        print(f"Last weekly run: {self.config.get('last_weekly_run', 'Never')}")
        print(f"Daily schedule: {self.config['daily_posts_count']} posts at {self.config['daily_time']}")
        print(f"Weekly schedule: {self.config['weekly_posts_count']} posts on {self.config['weekly_day']} at {self.config['weekly_time']}")
        
        # Show recent logs
        log_file = Path("blog_generation.log")
        if log_file.exists():
            with open(log_file, 'r') as f:
                try:
                    logs = json.load(f)
                    recent_logs = logs[-5:]  # Last 5 entries
                    if recent_logs:
                        print("\n📝 Recent activity:")
                        for log in recent_logs:
                            status_icon = "✅" if log.get("status") == "success" else "❌"
                            timestamp = log.get("timestamp", "Unknown")[:19]  # Remove microseconds
                            log_type = log.get("type", "unknown")
                            if "posts_generated" in log:
                                print(f"   {status_icon} {timestamp} - {log_type}: {log['posts_generated']} posts")
                            else:
                                print(f"   {status_icon} {timestamp} - {log_type}: {log.get('error', 'Unknown error')}")
                except json.JSONDecodeError:
                    print("\n⚠️  Log file corrupted")

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Scheduled Blog Post Generator")
    parser.add_argument("--mode", choices=["scheduler", "daily", "weekly", "status"], 
                        default="scheduler", help="Operation mode")
    parser.add_argument("--config", default="blog_schedule_config.json",
                        help="Configuration file path")
    
    args = parser.parse_args()
    
    # Initialize scheduler
    scheduler = ScheduledBlogGenerator(args.config)
    
    if args.mode == "scheduler":
        scheduler.run_scheduler()
    elif args.mode == "daily":
        scheduler.run_once("daily")
    elif args.mode == "weekly":
        scheduler.run_once("weekly")
    elif args.mode == "status":
        scheduler.get_status()

if __name__ == "__main__":
    main()
