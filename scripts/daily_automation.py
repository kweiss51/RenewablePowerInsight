#!/usr/bin/env python3
"""
Daily Energy Content Automation System
Integrates ML training system with automated content generation
"""

import sys
import os
import logging
import schedule
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
import json

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/daily_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailyEnergyAutomation:
    """Daily automation system for energy content generation"""
    
    def __init__(self):
        self.setup_directories()
        self.last_run_file = Path('logs/last_run.json')
        self.max_articles_per_day = 50
        self.max_posts_per_day = 10
        
    def setup_directories(self):
        """Create necessary directories"""
        directories = [
            'logs', 'data', 'training_data', 'model_checkpoints',
            'results/daily_reports'
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def save_run_status(self, status: dict):
        """Save the status of the last run"""
        with open(self.last_run_file, 'w') as f:
            json.dump(status, f, indent=2, default=str)
    
    def load_run_status(self) -> dict:
        """Load the status of the last run"""
        if self.last_run_file.exists():
            with open(self.last_run_file, 'r') as f:
                return json.load(f)
        return {}
    
    def should_run_today(self) -> bool:
        """Check if we should run today based on last run"""
        last_status = self.load_run_status()
        if not last_status:
            return True
        
        last_run_date = last_status.get('date')
        if not last_run_date:
            return True
        
        last_run = datetime.fromisoformat(last_run_date)
        today = datetime.now()
        
        # Run if it's been more than 18 hours since last run
        return (today - last_run) > timedelta(hours=18)
    
    def collect_daily_data(self) -> dict:
        """Collect fresh data for the day"""
        logger.info("🔍 Starting daily data collection...")
        
        try:
            from ml_models.advanced_data_collector import AdvancedEnergyDataCollector
            
            collector = AdvancedEnergyDataCollector()
            
            # Collect academic papers (limit to recent ones)
            academic_data = collector.collect_academic_papers(
                max_papers=self.max_articles_per_day // 2,
                days_back=7  # Only recent papers
            )
            
            # Collect government/institutional data
            institutional_data = collector.collect_institutional_data(
                max_articles=self.max_articles_per_day // 2
            )
            
            # Save collected data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = f"data/daily_collection_{timestamp}.json"
            
            collected_data = {
                'timestamp': timestamp,
                'academic_papers': academic_data,
                'institutional_articles': institutional_data,
                'total_articles': len(academic_data) + len(institutional_data)
            }
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(collected_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Collected {collected_data['total_articles']} articles")
            return collected_data
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            return {'error': str(e), 'total_articles': 0}
    
    def process_daily_data(self, collected_data: dict) -> dict:
        """Process collected data for training and content generation"""
        logger.info("🔧 Processing daily data...")
        
        try:
            from ml_models.advanced_data_preprocessor import AdvancedEnergyDataPreprocessor
            
            preprocessor = AdvancedEnergyDataPreprocessor()
            
            # Combine all articles
            all_articles = []
            if 'academic_papers' in collected_data:
                all_articles.extend(collected_data['academic_papers'])
            if 'institutional_articles' in collected_data:
                all_articles.extend(collected_data['institutional_articles'])
            
            if not all_articles:
                logger.warning("⚠️ No articles to process")
                return {'processed_count': 0}
            
            # Process articles
            processed_articles = []
            for article in all_articles:
                try:
                    processed = preprocessor.process_article(article)
                    if processed and preprocessor.is_suitable_for_training(processed):
                        processed_articles.append(processed)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to process article: {e}")
                    continue
            
            # Save processed data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            processed_file = f"training_data/processed_{timestamp}.json"
            
            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(processed_articles, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Processed {len(processed_articles)} articles for training")
            return {
                'processed_count': len(processed_articles),
                'processed_file': processed_file
            }
            
        except Exception as e:
            logger.error(f"❌ Data processing failed: {e}")
            return {'error': str(e), 'processed_count': 0}
    
    def update_model_training(self, processed_data: dict) -> dict:
        """Update model with new data (incremental training)"""
        logger.info("🏋️ Updating model training...")
        
        try:
            from ml_models.advanced_trainer import AdvancedEnergyTrainer
            
            # Training configuration for daily updates
            config = {
                'base_model': 'gpt2',
                'max_length': 512,
                'batch_size': 2,
                'learning_rate': 5e-6,  # Lower LR for incremental training
                'epochs': 1,  # Just one epoch for daily updates
                'mixed_precision': False,
                'gradient_accumulation_steps': 4,
                'save_steps': 100,
                'logging_steps': 50
            }
            
            trainer = AdvancedEnergyTrainer(config)
            
            # Load processed data
            if 'processed_file' in processed_data and processed_data['processed_count'] > 0:
                training_results = trainer.incremental_training(
                    data_file=processed_data['processed_file'],
                    max_samples=processed_data['processed_count']
                )
                
                logger.info(f"✅ Model training completed: {training_results}")
                return training_results
            else:
                logger.info("ℹ️ No new data for training")
                return {'status': 'skipped', 'reason': 'no_new_data'}
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return {'error': str(e), 'status': 'failed'}
    
    def generate_daily_content(self, processed_data: dict) -> dict:
        """Generate blog posts from processed data"""
        logger.info("✍️ Generating daily content...")
        
        try:
            from src.blog_generator import BlogPostGenerator
            
            # Use the updated custom LLM if available
            generator = BlogPostGenerator(use_custom_llm=True)
            
            # Load processed articles for content generation
            if 'processed_file' in processed_data:
                with open(processed_data['processed_file'], 'r', encoding='utf-8') as f:
                    processed_articles = json.load(f)
                
                # Generate blog posts
                blog_posts = []
                articles_for_posts = processed_articles[:self.max_posts_per_day]
                
                for i, article in enumerate(articles_for_posts):
                    try:
                        post = generator.generate_post_from_article(article)
                        if post:
                            blog_posts.append(post)
                            logger.info(f"✅ Generated post {i+1}/{len(articles_for_posts)}")
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to generate post {i+1}: {e}")
                        continue
                
                # Save blog posts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                posts_file = f"data/blog_posts_{timestamp}.json"
                
                with open(posts_file, 'w', encoding='utf-8') as f:
                    json.dump(blog_posts, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Generated {len(blog_posts)} blog posts")
                return {
                    'posts_count': len(blog_posts),
                    'posts_file': posts_file
                }
            else:
                logger.info("ℹ️ No processed data for content generation")
                return {'posts_count': 0}
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            return {'error': str(e), 'posts_count': 0}
    
    def generate_daily_report(self, results: dict):
        """Generate a daily report of all activities"""
        logger.info("📊 Generating daily report...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"results/daily_reports/report_{timestamp}.json"
        
        report = {
            'date': datetime.now().isoformat(),
            'timestamp': timestamp,
            'data_collection': results.get('data_collection', {}),
            'data_processing': results.get('data_processing', {}),
            'model_training': results.get('model_training', {}),
            'content_generation': results.get('content_generation', {}),
            'summary': {
                'total_articles_collected': results.get('data_collection', {}).get('total_articles', 0),
                'articles_processed': results.get('data_processing', {}).get('processed_count', 0),
                'posts_generated': results.get('content_generation', {}).get('posts_count', 0),
                'training_status': results.get('model_training', {}).get('status', 'unknown')
            }
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        # Log summary
        summary = report['summary']
        logger.info("📈 Daily Summary:")
        logger.info(f"   📚 Articles collected: {summary['total_articles_collected']}")
        logger.info(f"   🔧 Articles processed: {summary['articles_processed']}")
        logger.info(f"   ✍️ Posts generated: {summary['posts_generated']}")
        logger.info(f"   🏋️ Training status: {summary['training_status']}")
        
        return report
    
    def run_daily_automation(self):
        """Run the complete daily automation pipeline"""
        if not self.should_run_today():
            logger.info("ℹ️ Daily automation already completed today. Skipping.")
            return
        
        logger.info("🚀 Starting daily energy content automation...")
        start_time = datetime.now()
        
        results = {}
        
        try:
            # Step 1: Data Collection
            results['data_collection'] = self.collect_daily_data()
            
            # Step 2: Data Processing
            results['data_processing'] = self.process_daily_data(results['data_collection'])
            
            # Step 3: Model Training (incremental)
            results['model_training'] = self.update_model_training(results['data_processing'])
            
            # Step 4: Content Generation
            results['content_generation'] = self.generate_daily_content(results['data_processing'])
            
            # Step 5: Generate Report
            report = self.generate_daily_report(results)
            
            # Save run status
            end_time = datetime.now()
            status = {
                'date': end_time.isoformat(),
                'duration_minutes': (end_time - start_time).total_seconds() / 60,
                'success': True,
                'results': results
            }
            self.save_run_status(status)
            
            logger.info(f"✅ Daily automation completed successfully in {status['duration_minutes']:.1f} minutes")
            
        except Exception as e:
            logger.error(f"❌ Daily automation failed: {e}")
            
            # Save failure status
            status = {
                'date': datetime.now().isoformat(),
                'success': False,
                'error': str(e),
                'results': results
            }
            self.save_run_status(status)
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        # Schedule daily run at 6 AM
        schedule.every().day.at("06:00").do(self.run_daily_automation)
        
        # Also schedule a backup run at 2 PM if morning run failed
        schedule.every().day.at("14:00").do(self.run_daily_automation)
        
        logger.info("⏰ Scheduled daily automation at 6:00 AM and 2:00 PM")
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
        return scheduler_thread

def main():
    """Main function"""
    automation = DailyEnergyAutomation()
    
    # Check if we should run immediately
    if len(sys.argv) > 1 and sys.argv[1] == '--run-now':
        automation.run_daily_automation()
        return
    
    # Start the scheduler
    scheduler_thread = automation.start_scheduler()
    
    logger.info("🤖 Daily Energy Automation System started")
    logger.info("   Use --run-now flag to run immediately")
    logger.info("   Scheduled to run daily at 6:00 AM and 2:00 PM")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(300)  # Sleep for 5 minutes
    except KeyboardInterrupt:
        logger.info("🛑 Stopping daily automation...")

if __name__ == "__main__":
    main()
