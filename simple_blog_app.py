#!/usr/bin/env python3
"""
Simple Energy Blog Application
Generate posts for X days with Y posts per day using pre-trained model
Monthly retraining for new information
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import logging
from typing import Dict, List, Optional

# Add the project root to the path
import sys
sys.path.append(str(Path(__file__).parent))

app = Flask(__name__, static_folder='static', template_folder='templates')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/simple_blog.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleBlogController:
    def __init__(self):
        self.data_dir = Path('data')
        self.model_dir = Path('ml_models')
        self.posts_dir = Path('data/generated_posts')
        self.state_file = Path('data/blog_state.json')
        
        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.posts_dir.mkdir(exist_ok=True)
        
        self.state = self.load_state()
        
    def load_state(self) -> Dict:
        """Load application state"""
        default_state = {
            'last_training_date': None,
            'model_version': '1.0',
            'total_posts_generated': 0,
            'generation_sessions': [],
            'current_session': None
        }
        
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Merge with defaults for any missing keys
                    for key, value in default_state.items():
                        if key not in state:
                            state[key] = value
                    return state
            except Exception as e:
                logger.error(f"Error loading state: {e}")
                return default_state
        
        return default_state
    
    def save_state(self):
        """Save application state"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def needs_training(self) -> bool:
        """Check if model needs retraining (monthly)"""
        if not self.state['last_training_date']:
            return True
        
        last_training = datetime.fromisoformat(self.state['last_training_date'])
        days_since_training = (datetime.now() - last_training).days
        
        return days_since_training >= 30
    
    def is_model_ready(self) -> bool:
        """Check if trained model exists"""
        model_path = self.model_dir / 'model_checkpoints' / 'best_model.pth'
        return model_path.exists()
    
    def generate_posts_batch(self, num_posts: int, target_date: str = None) -> List[Dict]:
        """Generate a batch of posts"""
        try:
            # Import here to avoid loading heavy dependencies unless needed
            from ml_models.inference import EnergyInference
            
            if not self.is_model_ready():
                raise Exception("Model not found. Please run training first.")
            
            # Initialize inference engine
            inference = EnergyInference()
            
            posts = []
            target_date = target_date or datetime.now().strftime('%Y-%m-%d')
            
            logger.info(f"Generating {num_posts} posts for {target_date}")
            
            # Generate topics first
            topics = [
                "renewable energy developments",
                "solar power innovations",
                "wind energy trends",
                "energy storage solutions",
                "grid modernization",
                "electric vehicle infrastructure",
                "clean energy policy",
                "sustainable technology",
                "energy efficiency",
                "carbon reduction strategies"
            ]
            
            for i in range(num_posts):
                try:
                    topic = topics[i % len(topics)]
                    prompt = f"Write a comprehensive blog post about {topic} focusing on recent developments and future outlook."
                    
                    # Generate content using the trained model
                    content = inference.generate_content(prompt, max_length=800)
                    
                    post = {
                        'id': f"post_{target_date}_{i+1:03d}",
                        'title': f"Energy Insights: {topic.title()}",
                        'content': content,
                        'topic': topic,
                        'generated_date': datetime.now().isoformat(),
                        'target_date': target_date,
                        'word_count': len(content.split())
                    }
                    
                    posts.append(post)
                    
                    # Save individual post
                    post_file = self.posts_dir / f"{post['id']}.json"
                    with open(post_file, 'w') as f:
                        json.dump(post, f, indent=2)
                    
                    logger.info(f"Generated post {i+1}/{num_posts}: {post['title']}")
                    
                except Exception as e:
                    logger.error(f"Error generating post {i+1}: {e}")
                    continue
            
            return posts
            
        except Exception as e:
            logger.error(f"Error in batch generation: {e}")
            raise
    
    def start_generation_session(self, days: int, posts_per_day: int) -> str:
        """Start a new generation session"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        session = {
            'id': session_id,
            'start_time': datetime.now().isoformat(),
            'days': days,
            'posts_per_day': posts_per_day,
            'total_posts_planned': days * posts_per_day,
            'posts_generated': 0,
            'status': 'running',
            'current_day': 1,
            'daily_progress': {}
        }
        
        self.state['current_session'] = session
        self.state['generation_sessions'].append(session)
        self.save_state()
        
        # Start generation in background thread
        thread = threading.Thread(target=self._run_generation_session, args=(session,))
        thread.daemon = True
        thread.start()
        
        return session_id
    
    def _run_generation_session(self, session: Dict):
        """Run the generation session in background"""
        try:
            start_date = datetime.now()
            
            for day in range(1, session['days'] + 1):
                if session['status'] != 'running':
                    break
                
                target_date = (start_date + timedelta(days=day-1)).strftime('%Y-%m-%d')
                logger.info(f"Generating posts for day {day}/{session['days']} ({target_date})")
                
                # Generate posts for this day
                posts = self.generate_posts_batch(session['posts_per_day'], target_date)
                
                # Update session progress
                session['posts_generated'] += len(posts)
                session['current_day'] = day
                session['daily_progress'][str(day)] = {
                    'date': target_date,
                    'posts_generated': len(posts),
                    'post_ids': [post['id'] for post in posts]
                }
                
                # Update global state
                self.state['total_posts_generated'] += len(posts)
                self.save_state()
                
                logger.info(f"Day {day} complete: {len(posts)} posts generated")
            
            # Mark session as complete
            session['status'] = 'completed'
            session['end_time'] = datetime.now().isoformat()
            self.state['current_session'] = None
            self.save_state()
            
            logger.info(f"Session {session['id']} completed successfully!")
            
        except Exception as e:
            logger.error(f"Session failed: {e}")
            session['status'] = 'failed'
            session['error'] = str(e)
            self.state['current_session'] = None
            self.save_state()
    
    def get_status(self) -> Dict:
        """Get current application status"""
        return {
            'model_ready': self.is_model_ready(),
            'needs_training': self.needs_training(),
            'last_training_date': self.state['last_training_date'],
            'total_posts_generated': self.state['total_posts_generated'],
            'current_session': self.state['current_session'],
            'recent_sessions': self.state['generation_sessions'][-5:],  # Last 5 sessions
            'model_version': self.state['model_version']
        }
    
    def trigger_monthly_training(self):
        """Trigger monthly model retraining"""
        try:
            logger.info("Starting monthly model training...")
            
            # Import training modules
            from ml_models.advanced_data_collector import AdvancedEnergyDataCollector
            from ml_models.advanced_data_preprocessor import AdvancedEnergyDataPreprocessor
            from ml_models.advanced_trainer import AdvancedEnergyTrainer
            
            # Data collection
            collector = AdvancedEnergyDataCollector()
            logger.info("Collecting latest energy data...")
            collected_data = collector.collect_comprehensive_data()
            
            # Data preprocessing
            preprocessor = AdvancedEnergyDataPreprocessor()
            logger.info("Preprocessing collected data...")
            processed_data = preprocessor.prepare_training_data(collected_data)
            
            # Model training
            trainer = AdvancedEnergyTrainer()
            logger.info("Training model with new data...")
            trainer.incremental_training(processed_data)
            
            # Update state
            self.state['last_training_date'] = datetime.now().isoformat()
            self.state['model_version'] = f"{float(self.state['model_version']) + 0.1:.1f}"
            self.save_state()
            
            logger.info("Monthly training completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Monthly training failed: {e}")
            return False

# Global controller instance
controller = SimpleBlogController()

@app.route('/')
def index():
    """Main dashboard"""
    status = controller.get_status()
    return render_template('simple_dashboard.html', status=status)

@app.route('/generate', methods=['POST'])
def generate_posts():
    """Start post generation"""
    try:
        data = request.json
        days = int(data.get('days', 1))
        posts_per_day = int(data.get('posts_per_day', 5))
        
        if days < 1 or days > 365:
            return jsonify({'success': False, 'error': 'Days must be between 1 and 365'}), 400
        
        if posts_per_day < 1 or posts_per_day > 50:
            return jsonify({'success': False, 'error': 'Posts per day must be between 1 and 50'}), 400
        
        if not controller.is_model_ready():
            return jsonify({'success': False, 'error': 'Model not ready. Please run training first.'}), 400
        
        session_id = controller.start_generation_session(days, posts_per_day)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Started generating {posts_per_day} posts per day for {days} days'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/train', methods=['POST'])
def trigger_training():
    """Trigger model training"""
    try:
        if controller.state.get('current_session') and controller.state['current_session']['status'] == 'running':
            return jsonify({'success': False, 'error': 'Cannot train while generation is running'}), 400
        
        # Start training in background
        def run_training():
            controller.trigger_monthly_training()
        
        thread = threading.Thread(target=run_training)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Training started in background. This may take 30-60 minutes.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/status')
def get_status():
    """Get application status"""
    try:
        status = controller.get_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/posts')
def list_posts():
    """List generated posts"""
    try:
        posts = []
        posts_dir = Path('data/generated_posts')
        
        if posts_dir.exists():
            for post_file in posts_dir.glob('*.json'):
                try:
                    with open(post_file, 'r') as f:
                        post = json.load(f)
                        posts.append(post)
                except Exception as e:
                    logger.error(f"Error reading post file {post_file}: {e}")
        
        # Sort by generation date (newest first)
        posts.sort(key=lambda x: x.get('generated_date', ''), reverse=True)
        
        return render_template('posts_list.html', posts=posts)
        
    except Exception as e:
        logger.error(f"Error listing posts: {e}")
        return render_template('posts_list.html', posts=[], error=str(e))

@app.route('/post/<post_id>')
def view_post(post_id):
    """View individual post"""
    try:
        post_file = Path(f'data/generated_posts/{post_id}.json')
        
        if not post_file.exists():
            return "Post not found", 404
        
        with open(post_file, 'r') as f:
            post = json.load(f)
        
        return render_template('post_view.html', post=post)
        
    except Exception as e:
        logger.error(f"Error viewing post {post_id}: {e}")
        return f"Error loading post: {e}", 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data/generated_posts', exist_ok=True)
    
    print("🚀 Starting Simple Energy Blog Application...")
    print("   Dashboard: http://localhost:5002")
    print("   Posts: http://localhost:5002/posts")
    
    app.run(debug=True, host='0.0.0.0', port=5002)
