#!/usr/bin/env python3
"""
Integrated GitHub Pages Blog System
Combines AI content generation with Jekyll deployment
"""

import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import subprocess
from typing import Dict, List, Optional

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from simple_blog_app import SimpleBlogController
from scripts.github_pages_generator import GitHubPagesGenerator

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedBlogSystem:
    def __init__(self):
        """Initialize the integrated blog system"""
        self.blog_controller = SimpleBlogController()
        self.pages_generator = GitHubPagesGenerator()
        self.deployment_log = Path('logs/deployment.log')
        
        # Ensure logs directory exists
        self.deployment_log.parent.mkdir(exist_ok=True)
    
    def generate_and_deploy_posts(self, days: int, posts_per_day: int) -> Dict:
        """Generate posts and deploy to GitHub Pages"""
        try:
            logger.info(f"🚀 Starting integrated blog generation and deployment...")
            logger.info(f"📊 Target: {posts_per_day} posts/day for {days} days")
            
            # Start generation session
            session_id = self.blog_controller.start_generation_session(days, posts_per_day)
            
            # Wait for generation to complete
            self._wait_for_generation_completion(session_id)
            
            # Convert posts to Jekyll format
            converted_posts = self.pages_generator.convert_generated_posts_to_jekyll()
            
            # Deploy to GitHub if posts were converted
            if converted_posts:
                deployment_result = self._deploy_to_github(converted_posts)
                
                return {
                    'success': True,
                    'session_id': session_id,
                    'posts_generated': len(converted_posts),
                    'posts_converted': converted_posts,
                    'deployment': deployment_result
                }
            else:
                return {
                    'success': False,
                    'error': 'No posts were converted to Jekyll format'
                }
                
        except Exception as e:
            logger.error(f"Error in integrated generation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _wait_for_generation_completion(self, session_id: str, timeout: int = 1800):
        """Wait for generation session to complete"""
        import time
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.blog_controller.get_status()
            current_session = status.get('current_session')
            
            if not current_session or current_session.get('status') != 'running':
                logger.info("✅ Generation session completed")
                return True
            
            logger.info(f"⏳ Generation in progress... {current_session.get('posts_generated', 0)} posts generated")
            time.sleep(30)  # Check every 30 seconds
        
        raise TimeoutError("Generation session timed out")
    
    def _deploy_to_github(self, converted_posts: List[str]) -> Dict:
        """Deploy converted posts to GitHub"""
        try:
            logger.info("🚀 Starting GitHub deployment...")
            
            # Git operations
            git_commands = [
                ['git', 'add', '_posts/', '_config.yml', 'index.md', 'about.md', 'assets/', 'Gemfile'],
                ['git', 'commit', '-m', f'Add {len(converted_posts)} new energy blog posts'],
                ['git', 'push', 'origin', 'main']
            ]
            
            results = []
            for cmd in git_commands:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=False,
                        cwd=self.pages_generator.repo_path
                    )
                    
                    results.append({
                        'command': ' '.join(cmd),
                        'success': result.returncode == 0,
                        'output': result.stdout,
                        'error': result.stderr
                    })
                    
                    if result.returncode == 0:
                        logger.info(f"✅ Git command successful: {' '.join(cmd)}")
                    else:
                        logger.warning(f"⚠️ Git command failed: {' '.join(cmd)}")
                        logger.warning(f"Error: {result.stderr}")
                
                except Exception as e:
                    logger.error(f"Error running git command {cmd}: {e}")
                    results.append({
                        'command': ' '.join(cmd),
                        'success': False,
                        'error': str(e)
                    })
            
            # Log deployment
            self._log_deployment(converted_posts, results)
            
            return {
                'success': all(r['success'] for r in results),
                'git_operations': results,
                'posts_deployed': converted_posts,
                'deployment_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in GitHub deployment: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _log_deployment(self, posts: List[str], git_results: List[Dict]):
        """Log deployment details"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'posts_deployed': len(posts),
            'post_files': posts,
            'git_operations': git_results,
            'success': all(r['success'] for r in git_results)
        }
        
        # Append to deployment log
        with open(self.deployment_log, 'a') as f:
            f.write(json.dumps(log_entry, indent=2) + '\n\n')
    
    def setup_automated_deployment(self):
        """Setup automated daily deployment"""
        try:
            # Create automation script
            automation_script = Path('deploy_daily_posts.py')
            
            script_content = f'''#!/usr/bin/env python3
"""
Daily automated blog post generation and deployment
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from integrated_blog_system import IntegratedBlogSystem

def main():
    print("🚀 Starting daily blog post generation...")
    
    # Initialize system
    blog_system = IntegratedBlogSystem()
    
    # Generate and deploy daily posts
    result = blog_system.generate_and_deploy_posts(days=1, posts_per_day=5)
    
    if result['success']:
        print(f"✅ Successfully generated and deployed {{result['posts_generated']}} posts")
        print(f"🌐 Check your GitHub Pages site for updates!")
    else:
        print(f"❌ Deployment failed: {{result.get('error', 'Unknown error')}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
            
            with open(automation_script, 'w') as f:
                f.write(script_content)
            
            # Make executable
            automation_script.chmod(0o755)
            
            logger.info("✅ Automated deployment script created")
            
            # Create cron job setup instructions
            cron_instructions = Path('CRON_SETUP.md')
            
            instructions = '''# Automated Daily Blog Post Generation

## Setup Cron Job for Daily Posting

To automatically generate and deploy blog posts daily, set up a cron job:

1. **Open crontab**:
   ```bash
   crontab -e
   ```

2. **Add daily job** (runs at 6 AM daily):
   ```bash
   0 6 * * * cd /path/to/RenewablePowerInsight && python deploy_daily_posts.py >> logs/cron.log 2>&1
   ```

3. **Alternative times**:
   - `0 9 * * *` - 9 AM daily
   - `0 6,18 * * *` - 6 AM and 6 PM daily
   - `0 6 * * 1-5` - 6 AM weekdays only

## Manual Deployment

Run manually anytime:
```bash
python deploy_daily_posts.py
```

## Check Logs

Monitor deployment logs:
```bash
tail -f logs/deployment.log
tail -f logs/cron.log
```

## GitHub Pages

After successful deployment, your posts will be available at:
https://kweiss51.github.io/RenewablePowerInsight/

The GitHub Actions workflow will automatically build and deploy the Jekyll site.
'''
            
            with open(cron_instructions, 'w') as f:
                f.write(instructions)
            
            logger.info("✅ Cron setup instructions created")
            
            return True
            
        except Exception as e:
            logger.error(f"Error setting up automation: {e}")
            return False
    
    def test_integration(self):
        """Test the complete integration pipeline"""
        try:
            logger.info("🧪 Testing integrated blog system...")
            
            # Test 1: Generate a single post
            logger.info("📝 Test 1: Generating test post...")
            result = self.generate_and_deploy_posts(days=1, posts_per_day=1)
            
            if result['success']:
                logger.info("✅ Test 1 passed: Post generation and conversion successful")
            else:
                logger.error(f"❌ Test 1 failed: {result.get('error')}")
                return False
            
            # Test 2: Check Jekyll structure
            logger.info("🏗️ Test 2: Checking Jekyll structure...")
            required_files = ['_config.yml', 'index.md', 'about.md', 'Gemfile']
            missing_files = []
            
            for file in required_files:
                if not (self.pages_generator.repo_path / file).exists():
                    missing_files.append(file)
            
            if missing_files:
                logger.error(f"❌ Test 2 failed: Missing files: {missing_files}")
                return False
            else:
                logger.info("✅ Test 2 passed: Jekyll structure complete")
            
            # Test 3: Check post format
            logger.info("📄 Test 3: Checking post format...")
            posts_dir = self.pages_generator.posts_dir
            
            if not posts_dir.exists() or not list(posts_dir.glob('*.md')):
                logger.error("❌ Test 3 failed: No Jekyll posts found")
                return False
            
            # Check a post file format
            sample_post = list(posts_dir.glob('*.md'))[0]
            with open(sample_post, 'r') as f:
                content = f.read()
            
            if not content.startswith('---') or '---' not in content[3:]:
                logger.error("❌ Test 3 failed: Invalid Jekyll front matter")
                return False
            
            logger.info("✅ Test 3 passed: Post format valid")
            logger.info("🎉 All integration tests passed!")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            return False

def main():
    """Main function for integrated blog system"""
    print("🌐 Renewable Power Insight - Integrated Blog System")
    print("=" * 50)
    
    # Initialize system
    blog_system = IntegratedBlogSystem()
    
    # Setup Jekyll structure
    print("🏗️ Setting up GitHub Pages structure...")
    blog_system.pages_generator.create_gemfile()
    blog_system.pages_generator.create_github_workflow()
    blog_system.pages_generator.generate_readme()
    
    # Setup automation
    print("⚙️ Setting up automated deployment...")
    blog_system.setup_automated_deployment()
    
    # Run integration test
    print("🧪 Running integration tests...")
    if blog_system.test_integration():
        print("✅ Integration setup complete!")
        print("\n📋 Next Steps:")
        print("1. Review the generated Jekyll files")
        print("2. Commit and push to GitHub: git add . && git commit -m 'Setup energy blog' && git push")
        print("3. Enable GitHub Pages in repository settings")
        print("4. Set up cron job for daily posting (see CRON_SETUP.md)")
        print(f"5. Visit your blog at: https://kweiss51.github.io/RenewablePowerInsight/")
    else:
        print("❌ Integration setup failed. Check logs for details.")

if __name__ == "__main__":
    main()
