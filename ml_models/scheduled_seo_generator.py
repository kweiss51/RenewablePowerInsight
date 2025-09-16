"""
Scheduled SEO Blog Generator
Automated blog generation with scheduling and monitoring capabilities
"""

import os
import sys
import schedule
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional
import json

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from seo_automation import SEOBlogAutomation


class ScheduledBlogGenerator:
    """Schedule SEO blog generation at regular intervals"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.automation = SEOBlogAutomation(project_root)
        self.log_file = self.project_root / "ml_models" / "automation_logs" / "scheduler.log"
        self.schedule_config_file = self.project_root / "ml_models" / "automation_logs" / "schedule_config.json"
        
        # Create directories
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Default schedule configuration
        self.default_config = {
            "daily_posts": 2,
            "categories": ["solar", "wind", "battery", "policy", "technology"],
            "preferred_times": ["09:00", "15:00"],
            "enabled": True,
            "max_posts_per_day": 5,
            "quality_threshold": 70.0,
            "auto_commit": True,
            "notification_email": None
        }
        
        # Load configuration
        self.config = self.load_schedule_config()
    
    def load_schedule_config(self) -> dict:
        """Load scheduling configuration"""
        try:
            if self.schedule_config_file.exists():
                with open(self.schedule_config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    return {**self.default_config, **config}
            else:
                # Create default config file
                self.save_schedule_config(self.default_config)
                return self.default_config.copy()
        except Exception as e:
            self.logger.error(f"Failed to load config, using defaults: {e}")
            return self.default_config.copy()
    
    def save_schedule_config(self, config: dict):
        """Save scheduling configuration"""
        try:
            with open(self.schedule_config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    def generate_daily_posts(self):
        """Generate daily blog posts according to schedule"""
        
        if not self.config.get("enabled", True):
            self.logger.info("🚫 Scheduled generation is disabled")
            return
        
        self.logger.info("🚀 Starting scheduled blog generation")
        
        try:
            # Determine posts to generate
            posts_to_generate = min(
                self.config.get("daily_posts", 2),
                self.config.get("max_posts_per_day", 5)
            )
            
            # Select categories (rotate through available categories)
            categories = self.config.get("categories", ["solar", "wind"])
            selected_categories = categories[:posts_to_generate]
            
            # Generate posts
            result = self.automation.run_full_seo_automation(
                post_count=posts_to_generate,
                categories=selected_categories,
                auto_commit=self.config.get("auto_commit", True)
            )
            
            # Check quality threshold
            avg_score = result.get("average_seo_score", 0)
            quality_threshold = self.config.get("quality_threshold", 70.0)
            
            if avg_score >= quality_threshold:
                self.logger.info(f"✅ Daily generation completed successfully!")
                self.logger.info(f"📊 Generated {result['posts_generated']} posts with {avg_score}% average SEO score")
            else:
                self.logger.warning(f"⚠️ Posts generated but quality below threshold ({avg_score}% < {quality_threshold}%)")
            
            # Send notification if configured
            if self.config.get("notification_email"):
                self.send_notification(result)
                
        except Exception as e:
            self.logger.error(f"❌ Scheduled generation failed: {e}")
    
    def send_notification(self, result: dict):
        """Send email notification about generation results"""
        # This would integrate with an email service
        # For now, just log the notification
        self.logger.info(f"📧 Would send notification: {result['posts_generated']} posts generated")
    
    def setup_daily_schedule(self):
        """Setup daily posting schedule"""
        
        preferred_times = self.config.get("preferred_times", ["09:00"])
        
        for time_str in preferred_times:
            schedule.every().day.at(time_str).do(self.generate_daily_posts)
            self.logger.info(f"📅 Scheduled daily post generation at {time_str}")
    
    def setup_weekly_maintenance(self):
        """Setup weekly maintenance tasks"""
        
        # Weekly cleanup and metrics review
        schedule.every().sunday.at("02:00").do(self.weekly_maintenance)
        self.logger.info("📅 Scheduled weekly maintenance on Sundays at 02:00")
    
    def weekly_maintenance(self):
        """Perform weekly maintenance tasks"""
        
        self.logger.info("🧹 Starting weekly maintenance...")
        
        try:
            # Review metrics
            metrics = self.automation.automation_metrics
            self.logger.info(f"📊 Weekly Stats: {metrics['successful_posts']} posts, {metrics['average_seo_score']:.1f}% avg score")
            
            # Archive old logs (keep last 30 days)
            self.cleanup_old_logs()
            
            # Generate weekly report
            self.generate_weekly_report()
            
        except Exception as e:
            self.logger.error(f"❌ Weekly maintenance failed: {e}")
    
    def cleanup_old_logs(self):
        """Clean up old log files"""
        
        cutoff_date = datetime.now() - timedelta(days=30)
        logs_dir = self.log_file.parent
        
        for log_file in logs_dir.glob("*.log"):
            try:
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    self.logger.info(f"🗑️ Cleaned up old log: {log_file.name}")
            except Exception as e:
                self.logger.warning(f"Could not clean up {log_file}: {e}")
    
    def generate_weekly_report(self):
        """Generate weekly performance report"""
        
        report_data = {
            "week_ending": datetime.now().strftime("%Y-%m-%d"),
            "total_posts": self.automation.automation_metrics["successful_posts"],
            "average_score": self.automation.automation_metrics["average_seo_score"],
            "categories": self.automation.automation_metrics["categories_generated"],
            "git_commits": self.automation.automation_metrics["git_commits"]
        }
        
        report_file = self.project_root / "ml_models" / "automation_logs" / f"weekly_report_{datetime.now().strftime('%Y_%m_%d')}.json"
        
        try:
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)
            self.logger.info(f"📋 Weekly report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save weekly report: {e}")
    
    def run_scheduler(self):
        """Run the blog generation scheduler"""
        
        self.logger.info("🚀 Starting SEO Blog Scheduler")
        self.logger.info("=" * 50)
        
        # Setup schedules
        self.setup_daily_schedule()
        self.setup_weekly_maintenance()
        
        self.logger.info("⏰ Scheduler is running... Press Ctrl+C to stop")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("\\n👋 Scheduler stopped by user")
    
    def run_test_generation(self):
        """Run a test generation to verify everything works"""
        
        self.logger.info("🧪 Running test generation...")
        
        try:
            result = self.automation.run_full_seo_automation(
                post_count=1,
                categories=["solar"],
                auto_commit=False  # Don't commit test posts
            )
            
            if result["success"]:
                self.logger.info("✅ Test generation successful!")
                return True
            else:
                self.logger.error("❌ Test generation failed")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Test generation error: {e}")
            return False
    
    def show_status(self):
        """Show current scheduler status and metrics"""
        
        print("📊 SEO Blog Scheduler Status")
        print("=" * 40)
        print(f"Enabled: {'✅' if self.config.get('enabled') else '❌'}")
        print(f"Daily Posts: {self.config.get('daily_posts', 0)}")
        print(f"Categories: {', '.join(self.config.get('categories', []))}")
        print(f"Times: {', '.join(self.config.get('preferred_times', []))}")
        print(f"Quality Threshold: {self.config.get('quality_threshold', 0)}%")
        print()
        
        # Show automation metrics
        metrics = self.automation.automation_metrics
        print("📈 Performance Metrics")
        print("-" * 25)
        print(f"Total Posts Generated: {metrics['successful_posts']}")
        print(f"Average SEO Score: {metrics['average_seo_score']:.1f}%")
        print(f"Posts Above 80%: {metrics['posts_above_80_percent']}")
        print(f"Git Commits: {metrics['git_commits']}")
        print(f"Last Run: {metrics.get('last_run', 'Never')}")
        
        if metrics.get('categories_generated'):
            print("\\n📂 Posts by Category")
            print("-" * 20)
            for category, count in metrics['categories_generated'].items():
                print(f"{category.title()}: {count}")


def main():
    """CLI interface for scheduled blog generation"""
    
    parser = argparse.ArgumentParser(description='Scheduled SEO Blog Generator')
    parser.add_argument('--run', action='store_true',
                       help='Start the scheduler (runs continuously)')
    parser.add_argument('--test', action='store_true',
                       help='Run a test generation')
    parser.add_argument('--status', action='store_true',
                       help='Show scheduler status and metrics')
    parser.add_argument('--generate-now', action='store_true',
                       help='Generate posts immediately (one-time run)')
    parser.add_argument('--disable', action='store_true',
                       help='Disable scheduled generation')
    parser.add_argument('--enable', action='store_true',
                       help='Enable scheduled generation')
    parser.add_argument('--config', type=str,
                       help='Update configuration (JSON format)')
    
    args = parser.parse_args()
    
    # Initialize scheduler
    scheduler = ScheduledBlogGenerator()
    
    try:
        if args.status:
            scheduler.show_status()
            
        elif args.test:
            success = scheduler.run_test_generation()
            sys.exit(0 if success else 1)
            
        elif args.generate_now:
            scheduler.generate_daily_posts()
            
        elif args.disable:
            scheduler.config["enabled"] = False
            scheduler.save_schedule_config(scheduler.config)
            print("❌ Scheduled generation disabled")
            
        elif args.enable:
            scheduler.config["enabled"] = True
            scheduler.save_schedule_config(scheduler.config)
            print("✅ Scheduled generation enabled")
            
        elif args.config:
            try:
                new_config = json.loads(args.config)
                scheduler.config.update(new_config)
                scheduler.save_schedule_config(scheduler.config)
                print("✅ Configuration updated")
            except json.JSONDecodeError as e:
                print(f"❌ Invalid JSON: {e}")
                sys.exit(1)
                
        elif args.run:
            scheduler.run_scheduler()
            
        else:
            # Show status by default
            scheduler.show_status()
            print("\\nUse --help for available commands")
            
    except KeyboardInterrupt:
        print("\\n👋 Operation cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
