"""
Energy Blog Application
Main Flask app that serves the blog and runs scraping/generation
Integrated with ML training system and daily automation
"""

from flask import Flask, render_template, jsonify, request
import json
import os
import glob
from datetime import datetime
import schedule
import time
import threading
from src.news_scraper import EnergyNewsScraper
from src.blog_generator import BlogPostGenerator
from daily_automation import DailyEnergyAutomation

app = Flask(__name__, static_folder='static', template_folder='templates')

class EnergyBlogApp:
    def __init__(self, use_custom_llm=True):
        self.scraper = EnergyNewsScraper()
        self.generator = BlogPostGenerator(use_custom_llm=use_custom_llm)
        self.automation = DailyEnergyAutomation()
        self.latest_posts = []
        self.load_latest_posts()
    
    def load_latest_posts(self):
        """Load the most recent blog posts"""
        try:
            post_files = glob.glob("data/blog_posts_*.json")
            if post_files:
                latest_file = max(post_files)
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.latest_posts = json.load(f)
                print(f"📖 Loaded {len(self.latest_posts)} blog posts from {latest_file}")
            else:
                self.latest_posts = []
                print("📝 No existing blog posts found")
        except Exception as e:
            print(f"Error loading posts: {e}")
            self.latest_posts = []
    
    def run_scraping_and_generation(self):
        """Run the complete scraping and blog generation process"""
        print("🚀 Starting automated scraping and blog generation...")
        
        try:
            # Use the new ML-powered automation system
            self.automation.run_daily_automation()
            
            # Reload latest posts after automation
            self.load_latest_posts()
            
            print("✅ Successfully updated blog with ML-generated content")
                
        except Exception as e:
            print(f"❌ Error during ML automation: {e}")
            
            # Fallback to original scraping method
            try:
                articles = self.scraper.get_trending_topics()
                if articles:
                    self.scraper.save_articles(articles)
                    
                    # Generate blog posts
                    posts = self.generator.generate_all_posts(articles)
                    self.generator.save_blog_posts(posts)
                    
                    # Update latest posts
                    self.latest_posts = posts
                    
                    print("✅ Fallback generation completed")
                else:
                    print("⚠️ No articles found during scraping")
            except Exception as fallback_error:
                print(f"❌ Fallback generation also failed: {fallback_error}")
    
    def schedule_updates(self):
        """Schedule automatic updates using the ML automation system"""
        # Start the daily automation scheduler
        self.automation.start_scheduler()
        
        # Keep the original 4-hour schedule as backup
        schedule.every(4).hours.do(self.run_scraping_and_generation)
        
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(300)  # Check every 5 minutes
        
        # Run scheduler in background thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        print("⏰ ML automation scheduled daily + backup updates every 4 hours")

# Initialize the app
blog_app = EnergyBlogApp()

@app.route('/')
def index():
    """Main blog page"""
    return render_template('index.html', posts=blog_app.latest_posts)

@app.route('/api/posts')
def api_posts():
    """API endpoint for blog posts"""
    return jsonify({
        'posts': blog_app.latest_posts,
        'count': len(blog_app.latest_posts),
        'last_updated': datetime.now().isoformat()
    })

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """Manual trigger for scraping and generation"""
    try:
        blog_app.run_scraping_and_generation()
        return jsonify({
            'success': True,
            'message': 'Scraping and generation completed',
            'posts_count': len(blog_app.latest_posts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ml-automation', methods=['POST'])
def api_ml_automation():
    """Manual trigger for ML automation system"""
    try:
        blog_app.automation.run_daily_automation()
        blog_app.load_latest_posts()  # Reload posts after automation
        return jsonify({
            'success': True,
            'message': 'ML automation completed',
            'posts_count': len(blog_app.latest_posts)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/automation-status')
def api_automation_status():
    """Get status of the automation system"""
    try:
        status = blog_app.automation.load_run_status()
        return jsonify({
            'success': True,
            'last_run': status,
            'should_run_today': blog_app.automation.should_run_today()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/daily-report')
def api_daily_report():
    """Get the latest daily report"""
    try:
        import glob
        report_files = glob.glob("results/daily_reports/report_*.json")
        if report_files:
            latest_report_file = max(report_files)
            with open(latest_report_file, 'r', encoding='utf-8') as f:
                report = json.load(f)
            return jsonify({
                'success': True,
                'report': report
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No reports found'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/post/<int:post_id>')
def view_post(post_id):
    """View individual blog post"""
    if 0 <= post_id < len(blog_app.latest_posts):
        post = blog_app.latest_posts[post_id]
        return render_template('post.html', post=post, post_id=post_id)
    else:
        return "Post not found", 404

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/admin')
def admin():
    """Admin dashboard with ML automation status"""
    # Get stats
    article_files = glob.glob("data/energy_articles_*.json")
    post_files = glob.glob("data/blog_posts_*.json")
    report_files = glob.glob("results/daily_reports/report_*.json")
    training_files = glob.glob("training_data/processed_*.json")
    
    # Get automation status
    automation_status = blog_app.automation.load_run_status()
    
    stats = {
        'total_article_files': len(article_files),
        'total_post_files': len(post_files),
        'total_reports': len(report_files),
        'total_training_files': len(training_files),
        'current_posts': len(blog_app.latest_posts),
        'last_update': datetime.now().isoformat(),
        'automation_status': automation_status,
        'should_run_today': blog_app.automation.should_run_today()
    }
    
    return render_template('admin.html', stats=stats)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    # Start scheduler
    blog_app.schedule_updates()
    
    # Run initial scraping if no posts exist
    if not blog_app.latest_posts:
        print("🔄 Running initial scraping...")
        blog_app.run_scraping_and_generation()
    
    print("🌐 Starting Energy Blog Application...")
    app.run(debug=True, host='0.0.0.0', port=5000)
