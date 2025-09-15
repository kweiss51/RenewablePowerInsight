"""
Automated Blog Pipeline with Git Integration
Complete automation for future blog post generation, website integration, and Git operations
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

from automated_blog_generator import AutomatedBlogGenerator
from full_website_integrator import FullWebsiteIntegrator

class AutomatedBlogPipeline:
    """
    Complete automation pipeline that:
    1. Generates new blog posts from ML content
    2. Integrates posts into website structure
    3. Commits and pushes to Git automatically
    4. Maintains integration logs and statistics
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.posts_dir = self.project_root / "posts"
        
        # Initialize components
        self.blog_generator = AutomatedBlogGenerator(str(self.posts_dir))
        self.website_integrator = FullWebsiteIntegrator(self.project_root)
        
        # Pipeline statistics
        self.pipeline_stats = {
            "sessions_run": 0,
            "posts_generated": 0,
            "successful_integrations": 0,
            "git_operations": 0,
            "last_run": None,
            "errors": []
        }
    
    def generate_and_integrate_post(self, title: str, content: str, 
                                  category: str = None, auto_commit: bool = True) -> Dict[str, any]:
        """
        Complete pipeline: Generate post, integrate into website, commit to Git
        
        Args:
            title: Blog post title
            content: Blog post content
            category: Optional category override
            auto_commit: Whether to automatically commit to Git
            
        Returns:
            Dictionary with pipeline results
        """
        print(f"\n🚀 Starting automated blog pipeline for: {title}")
        print("=" * 60)
        
        pipeline_result = {
            'success': False,
            'post_created': False,
            'website_integrated': False,
            'git_committed': False,
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Step 1: Generate blog post
            print("📝 Step 1: Generating blog post...")
            post_result = self.blog_generator.create_blog_post(
                title=title,
                content=content,
                custom_category=category,
                auto_git=False  # We'll handle Git operations ourselves
            )
            
            if post_result and 'file_path' in post_result:
                print(f"✅ Blog post created: {post_result['filename']}")
                pipeline_result['post_created'] = True
                pipeline_result['post_info'] = post_result
                self.pipeline_stats['posts_generated'] += 1
            else:
                error_msg = "Failed to generate blog post"
                print(f"❌ {error_msg}")
                pipeline_result['errors'].append(error_msg)
                return pipeline_result
            
            # Step 2: Full website integration
            print("🔗 Step 2: Integrating into website...")
            integration_result = self.website_integrator.perform_full_integration()
            
            if integration_result['success']:
                print(f"✅ Website integration completed")
                pipeline_result['website_integrated'] = True
                pipeline_result['integration_info'] = integration_result
                self.pipeline_stats['successful_integrations'] += 1
            else:
                error_msg = f"Website integration failed: {integration_result.get('error', 'Unknown error')}"
                print(f"❌ {error_msg}")
                pipeline_result['errors'].append(error_msg)
            
            # Step 3: Git operations (if enabled)
            if auto_commit:
                print("📤 Step 3: Committing to Git...")
                git_result = self.commit_pipeline_changes(title)
                
                if git_result['success']:
                    print(f"✅ Successfully pushed to GitHub")
                    pipeline_result['git_committed'] = True
                    pipeline_result['git_info'] = git_result
                    self.pipeline_stats['git_operations'] += 1
                else:
                    error_msg = f"Git operations failed: {git_result.get('error', 'Unknown error')}"
                    print(f"❌ {error_msg}")
                    pipeline_result['errors'].append(error_msg)
            
            # Update overall success status
            pipeline_result['success'] = (
                pipeline_result['post_created'] and 
                pipeline_result['website_integrated'] and
                (pipeline_result['git_committed'] or not auto_commit)
            )
            
            if pipeline_result['success']:
                print(f"\n🎉 Pipeline completed successfully!")
                print(f"   📝 Post: {post_result['filename']}")
                print(f"   🔗 Integration: {integration_result['posts_integrated']} total posts")
                if auto_commit:
                    print(f"   📤 Git: Committed and pushed")
            else:
                print(f"\n⚠️ Pipeline completed with errors:")
                for error in pipeline_result['errors']:
                    print(f"   - {error}")
            
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            print(f"❌ {error_msg}")
            pipeline_result['errors'].append(error_msg)
        
        # Update pipeline stats
        self.pipeline_stats['sessions_run'] += 1
        self.pipeline_stats['last_run'] = pipeline_result['timestamp']
        if pipeline_result['errors']:
            self.pipeline_stats['errors'].extend(pipeline_result['errors'])
        
        return pipeline_result
    
    def commit_pipeline_changes(self, post_title: str) -> Dict[str, any]:
        """Commit all pipeline changes to Git"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"Automated blog pipeline: {post_title} - {timestamp}"
        
        return self.blog_generator.commit_and_push_changes(commit_message)
    
    def run_batch_generation(self, posts_data: List[Dict], auto_commit: bool = True) -> Dict[str, any]:
        """
        Run pipeline for multiple posts
        
        Args:
            posts_data: List of dictionaries with 'title', 'content', 'category'
            auto_commit: Whether to commit after each post or at the end
            
        Returns:
            Batch processing results
        """
        print(f"\n🚀 Starting batch blog generation pipeline")
        print(f"📊 Processing {len(posts_data)} posts...")
        print("=" * 60)
        
        batch_result = {
            'total_posts': len(posts_data),
            'successful_posts': 0,
            'failed_posts': 0,
            'post_results': [],
            'batch_success': False,
            'timestamp': datetime.now().isoformat()
        }
        
        for i, post_data in enumerate(posts_data, 1):
            print(f"\n📝 Processing post {i}/{len(posts_data)}")
            
            result = self.generate_and_integrate_post(
                title=post_data.get('title', f'Generated Post {i}'),
                content=post_data.get('content', ''),
                category=post_data.get('category'),
                auto_commit=False  # Commit at the end for batch
            )
            
            batch_result['post_results'].append(result)
            
            if result['success']:
                batch_result['successful_posts'] += 1
            else:
                batch_result['failed_posts'] += 1
        
        # Final Git commit for batch
        if auto_commit and batch_result['successful_posts'] > 0:
            print(f"\n📤 Committing batch changes to Git...")
            git_result = self.commit_pipeline_changes(f"Batch: {batch_result['successful_posts']} posts")
            batch_result['git_result'] = git_result
        
        batch_result['batch_success'] = batch_result['failed_posts'] == 0
        
        print(f"\n🎉 Batch processing completed!")
        print(f"   ✅ Successful: {batch_result['successful_posts']}")
        print(f"   ❌ Failed: {batch_result['failed_posts']}")
        
        return batch_result
    
    def get_pipeline_status(self) -> Dict[str, any]:
        """Get current pipeline status and statistics"""
        return {
            'pipeline_stats': self.pipeline_stats.copy(),
            'blog_generator_stats': self.blog_generator.integration_stats.copy(),
            'project_root': str(self.project_root),
            'posts_directory': str(self.posts_dir),
            'git_status': self.blog_generator.check_git_status()
        }
    
    def setup_scheduled_automation(self, schedule_config: Dict = None):
        """
        Set up scheduled automation (requires separate scheduler)
        This is a configuration method - actual scheduling would be handled externally
        """
        default_config = {
            'daily_posts': 1,
            'posting_time': '09:00',
            'categories_rotation': ['solar', 'wind', 'battery', 'policy', 'grid-tech'],
            'auto_commit': True,
            'backup_enabled': True
        }
        
        config = schedule_config or default_config
        
        print("⏰ Scheduled automation configuration:")
        for key, value in config.items():
            print(f"   {key}: {value}")
        
        return config

# Integration function for external ML systems
def create_automated_post(title: str, content: str, category: str = None) -> Dict[str, any]:
    """
    Simple interface for external ML systems to create posts
    
    Args:
        title: Blog post title
        content: Blog post content
        category: Optional category
        
    Returns:
        Pipeline execution result
    """
    pipeline = AutomatedBlogPipeline()
    return pipeline.generate_and_integrate_post(title, content, category)

if __name__ == "__main__":
    print("🤖 Automated Blog Pipeline System")
    print("=================================")
    
    # Initialize pipeline
    pipeline = AutomatedBlogPipeline()
    
    # Show current status
    status = pipeline.get_pipeline_status()
    print(f"\n📊 Pipeline Status:")
    print(f"   📁 Project root: {status['project_root']}")
    print(f"   🔗 Git repository: {status['git_status']['is_git_repo']}")
    print(f"   📝 Posts generated: {status['blog_generator_stats']['posts_created']}")
    
    # Example: Generate a sample post
    sample_post = {
        'title': 'Advanced Renewable Energy Integration Strategies',
        'content': '''# Introduction

The integration of renewable energy sources into existing power grids represents one of the most significant challenges and opportunities in modern energy systems.

## Key Integration Challenges

Modern power grids face several challenges when incorporating renewable energy:

- Grid stability and frequency regulation
- Energy storage requirements
- Demand response management
- Infrastructure modernization needs

## Technological Solutions

Recent advances in smart grid technology, energy storage systems, and demand response programs are providing solutions to these integration challenges.

## Future Outlook

The continued development of these technologies will enable higher penetration of renewable energy sources while maintaining grid reliability and efficiency.''',
        'category': 'Grid Technology'
    }
    
    print(f"\n🧪 Testing pipeline with sample post...")
    result = pipeline.generate_and_integrate_post(
        title=sample_post['title'],
        content=sample_post['content'],
        category=sample_post['category']
    )
    
    if result['success']:
        print(f"\n✅ Test completed successfully!")
    else:
        print(f"\n❌ Test failed with errors:")
        for error in result['errors']:
            print(f"   - {error}")
