#!/usr/bin/env python3
"""
Complete Blog Automation System
Generates blog posts using ML model and automatically posts them with Git integration
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import time

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from automated_blog_generator import AutomatedBlogGenerator


class BlogAutomationSystem:
    """Complete system for automated blog generation and posting"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.posts_dir = self.project_root / "posts"
        self.log_file = self.project_root / "ml_models" / "automation_logs" / "automation.log"
        
        # Create directories
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Initialize blog generator
        self.blog_generator = AutomatedBlogGenerator(str(self.posts_dir))
        
        # Statistics
        self.stats = {
            "total_posts_generated": 0,
            "successful_git_commits": 0,
            "failed_operations": 0,
            "last_run": None
        }
    
    def log_message(self, message: str, level: str = "INFO"):
        """Log message to both console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        # Write to log file
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def generate_single_post(self, category: Optional[str] = None) -> Dict[str, any]:
        """Generate a single blog post"""
        try:
            self.log_message(f"Starting blog post generation for category: {category or 'random'}")
            
            # Available categories (matching energy_topics keys in automated_blog_generator.py)
            categories = [
                "solar",
                "wind", 
                "battery",
                "policy",
                "technology"
            ]
            
            # Select category
            if not category:
                import random
                category = random.choice(categories)
                self.log_message(f"Randomly selected category: {category}")
            elif category not in categories:
                self.log_message(f"Invalid category '{category}', using random selection", "WARNING")
                import random
                category = random.choice(categories)
            
            # Generate content
            sample = self.blog_generator.generate_sample_content(category)
            
            if not sample:
                self.log_message("Failed to generate blog content", "ERROR")
                return {"success": False, "error": "Content generation failed"}
            
            # Prepare post data
            post_data = {
                'title': sample['title'],
                'content': sample['content'],
                'category': category,
                'date': datetime.now().strftime("%B %d, %Y")
            }
            
            # Save the post
            result = self.blog_generator.create_blog_post(
                title=post_data['title'],
                content=post_data['content'],
                custom_category=category,
                auto_git=False  # We'll handle Git ourselves
            )
            
            # Extract filename from result
            filename = result.get('filename') if isinstance(result, dict) else result
            
            if filename:
                self.stats["total_posts_generated"] += 1
                full_path = self.project_root / filename
                
                self.log_message(f"✅ Successfully generated blog post:")
                self.log_message(f"   Title: {sample['title']}")
                self.log_message(f"   Category: {category}")
                self.log_message(f"   File: {filename}")
                
                return {
                    "success": True,
                    "title": sample['title'],
                    "category": category,
                    "filename": filename,
                    "full_path": str(full_path)
                }
            else:
                self.log_message("Failed to save blog post", "ERROR")
                return {"success": False, "error": "Failed to save post"}
                
        except Exception as e:
            self.log_message(f"Error generating blog post: {e}", "ERROR")
            self.stats["failed_operations"] += 1
            return {"success": False, "error": str(e)}
    
    def generate_multiple_posts(self, count: int = 2, categories: Optional[List[str]] = None) -> List[Dict[str, any]]:
        """Generate multiple blog posts"""
        results = []
        
        self.log_message(f"🚀 Starting generation of {count} blog posts")
        
        for i in range(count):
            category = None
            if categories and i < len(categories):
                category = categories[i]
            
            self.log_message(f"Generating post {i+1}/{count}")
            result = self.generate_single_post(category)
            results.append(result)
            
            # Small delay between posts
            if i < count - 1:
                time.sleep(2)
        
        successful = len([r for r in results if r.get("success")])
        self.log_message(f"📊 Generation complete: {successful}/{count} posts successful")
        
        return results
    
    def commit_to_git(self, commit_message: Optional[str] = None) -> bool:
        """Commit changes to Git"""
        try:
            self.log_message("🔄 Starting Git operations...")
            
            # Change to project directory
            os.chdir(self.project_root)
            
            # Check Git status
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                self.log_message("No changes to commit", "INFO")
                return True
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            self.log_message("Added files to Git staging")
            
            # Create commit message
            if not commit_message:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                commit_message = f"🤖 Automated blog post generation - {timestamp}"
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            self.log_message(f"Committed changes: {commit_message}")
            
            # Push to remote (optional)
            try:
                subprocess.run(['git', 'push'], check=True)
                self.log_message("✅ Successfully pushed to remote repository")
                self.stats["successful_git_commits"] += 1
                return True
            except subprocess.CalledProcessError as e:
                self.log_message(f"Warning: Failed to push to remote: {e}", "WARNING")
                self.log_message("Changes committed locally but not pushed")
                return True
                
        except subprocess.CalledProcessError as e:
            self.log_message(f"Git operation failed: {e}", "ERROR")
            self.stats["failed_operations"] += 1
            return False
        except Exception as e:
            self.log_message(f"Unexpected error in Git operations: {e}", "ERROR")
            self.stats["failed_operations"] += 1
            return False
    
    def run_full_automation(self, post_count: int = 2, categories: Optional[List[str]] = None, 
                           auto_commit: bool = True) -> Dict[str, any]:
        """Run complete automation: generate posts and commit to Git"""
        
        start_time = datetime.now()
        self.log_message("🚀 Starting Full Blog Automation System")
        self.log_message("=" * 50)
        
        # Generate posts
        results = self.generate_multiple_posts(post_count, categories)
        successful_posts = [r for r in results if r.get("success")]
        
        # Commit to Git if posts were generated
        git_success = False
        if successful_posts and auto_commit:
            post_titles = [post['title'] for post in successful_posts]
            commit_msg = f"🤖 Generated {len(successful_posts)} new blog posts\\n\\n" + "\\n".join(f"- {title}" for title in post_titles)
            git_success = self.commit_to_git(commit_msg)
        
        # Update stats
        self.stats["last_run"] = start_time.isoformat()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Summary
        summary = {
            "success": len(successful_posts) > 0,
            "posts_generated": len(successful_posts),
            "total_attempts": post_count,
            "git_committed": git_success,
            "duration_seconds": duration,
            "posts": successful_posts,
            "stats": self.stats
        }
        
        self.log_message("📊 Automation Summary:")
        self.log_message(f"   Posts generated: {len(successful_posts)}/{post_count}")
        self.log_message(f"   Git operations: {'✅ Success' if git_success else '❌ Failed'}")
        self.log_message(f"   Duration: {duration:.1f} seconds")
        self.log_message("=" * 50)
        
        return summary
    
    def save_stats(self):
        """Save statistics to file"""
        stats_file = self.project_root / "ml_models" / "automation_logs" / "stats.json"
        try:
            with open(stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.log_message(f"Could not save stats: {e}", "WARNING")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Automated Blog Generation System')
    parser.add_argument('--posts', '-p', type=int, default=2, help='Number of posts to generate (default: 2)')
    parser.add_argument('--categories', '-c', nargs='+', help='Specific categories to use')
    parser.add_argument('--no-commit', action='store_true', help='Skip Git commit operations')
    parser.add_argument('--single', '-s', help='Generate single post with specific category')
    
    args = parser.parse_args()
    
    # Initialize system
    automation = BlogAutomationSystem()
    
    try:
        if args.single:
            # Generate single post
            result = automation.generate_single_post(args.single)
            if result["success"] and not args.no_commit:
                automation.commit_to_git(f"🤖 Generated blog post: {result['title']}")
        else:
            # Run full automation
            automation.run_full_automation(
                post_count=args.posts,
                categories=args.categories,
                auto_commit=not args.no_commit
            )
        
        # Save stats
        automation.save_stats()
        
    except KeyboardInterrupt:
        automation.log_message("\\n👋 Automation cancelled by user")
    except Exception as e:
        automation.log_message(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
