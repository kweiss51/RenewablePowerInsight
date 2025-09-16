"""
SEO-Focused Blog Automation System
Complete automation with SEO optimization, quality checking, and analytics integration
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import argparse

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from enhanced_ml_trainer import EnhancedMLTrainer


class SEOBlogAutomation:
    """Complete SEO-focused blog automation system"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent
        self.log_file = self.project_root / "ml_models" / "automation_logs" / "seo_automation.log"
        self.metrics_file = self.project_root / "ml_models" / "automation_logs" / "seo_metrics.json"
        
        # Create directories
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Initialize enhanced ML trainer (includes all SEO features)
        self.seo_generator = EnhancedMLTrainer()
        
        # Overall automation metrics
        self.automation_metrics = {
            "total_sessions": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "average_seo_score": 0,
            "posts_above_80_percent": 0,
            "git_commits": 0,
            "last_run": None,
            "categories_generated": {}
        }
        
        # Load existing metrics
        self.load_metrics()
    
    def log_message(self, message: str, level: str = "INFO"):
        """Enhanced logging with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry + "\\n")
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def load_metrics(self):
        """Load existing metrics from file"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    saved_metrics = json.load(f)
                    self.automation_metrics.update(saved_metrics)
        except Exception as e:
            self.log_message(f"Could not load metrics: {e}", "WARNING")
    
    def save_metrics(self):
        """Save metrics to file"""
        try:
            self.automation_metrics["last_run"] = datetime.now().isoformat()
            with open(self.metrics_file, 'w') as f:
                json.dump(self.automation_metrics, f, indent=2)
        except Exception as e:
            self.log_message(f"Could not save metrics: {e}", "WARNING")
    
    def generate_seo_optimized_posts(self, count: int = 1, categories: Optional[List[str]] = None) -> List[Dict[str, any]]:
        """Generate multiple SEO-optimized posts"""
        
        self.log_message(f"🚀 Starting SEO Blog Generation - {count} posts")
        self.automation_metrics["total_sessions"] += 1
        
        available_categories = ["solar", "wind", "battery", "policy", "technology"]
        results = []
        
        for i in range(count):
            # Select category
            if categories and i < len(categories):
                category = categories[i]
            elif categories:
                category = categories[i % len(categories)]
            else:
                import random
                category = random.choice(available_categories)
            
            self.log_message(f"📝 Generating post {i+1}/{count} for category: {category}")
            
            # Generate SEO-optimized post
            result = self.seo_generator.generate_and_save_seo_post(category)
            
            if result["success"]:
                self.log_message(f"✅ Successfully generated SEO-optimized post:")
                self.log_message(f"   📄 Title: {result['title']}")
                self.log_message(f"   📊 SEO Score: {result['seo_score']['grade']} ({result['seo_score']['percentage']}%)")
                self.log_message(f"   📁 File: {result['filename']}")
                
                # Update metrics
                self.automation_metrics["successful_posts"] += 1
                
                # Track category generation
                if category not in self.automation_metrics["categories_generated"]:
                    self.automation_metrics["categories_generated"][category] = 0
                self.automation_metrics["categories_generated"][category] += 1
                
                # Track high-quality posts
                if result['seo_score']['percentage'] >= 80:
                    self.automation_metrics["posts_above_80_percent"] += 1
                
                # Update average SEO score
                total_posts = self.automation_metrics["successful_posts"]
                current_avg = self.automation_metrics["average_seo_score"]
                new_avg = ((current_avg * (total_posts - 1)) + result['seo_score']['percentage']) / total_posts
                self.automation_metrics["average_seo_score"] = round(new_avg, 1)
                
                # Log SEO recommendations if any
                if result['seo_score']['recommendations']:
                    self.log_message("💡 SEO Recommendations:")
                    for rec in result['seo_score']['recommendations'][:3]:  # Show top 3
                        self.log_message(f"   • {rec}")
                
                results.append(result)
                
            else:
                self.log_message(f"❌ Failed to generate post for {category}: {result['error']}", "ERROR")
                self.automation_metrics["failed_posts"] += 1
                results.append(result)
        
        success_count = len([r for r in results if r.get("success")])
        self.log_message(f"📊 Generation Summary: {success_count}/{count} posts successful")
        
        return results
    
    def update_website_navigation(self, new_posts: List[Dict[str, any]]) -> bool:
        """Update website navigation and index pages with new posts"""
        
        try:
            self.log_message("🔗 Updating website navigation...")
            
            # Update category index pages
            for post in new_posts:
                if not post.get("success"):
                    continue
                
                category = post["category"]
                title = post["title"]
                filename = Path(post["filename"]).name
                
                # Update category index page
                category_folder = self.seo_generator.category_folders.get(category, "general")
                index_path = self.project_root / "posts" / category_folder / "index.html"
                
                if index_path.exists():
                    self.add_post_to_index(index_path, title, filename)
            
            self.log_message("✅ Website navigation updated")
            return True
            
        except Exception as e:
            self.log_message(f"❌ Failed to update navigation: {e}", "ERROR")
            return False
    
    def add_post_to_index(self, index_path: Path, title: str, filename: str):
        """Add new post to category index page"""
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Find the posts list and add new post
            new_post_html = f'''
                <article class="post-preview">
                    <h3><a href="{filename}">{title}</a></h3>
                    <p class="post-meta">Published on {datetime.now().strftime("%B %d, %Y")}</p>
                    <p class="post-excerpt">Latest insights on renewable energy technology and market developments.</p>
                </article>
            '''
            
            # Insert after the first post-preview or at the beginning
            if '<article class="post-preview">' in content:
                content = content.replace(
                    '<article class="post-preview">',
                    new_post_html + '<article class="post-preview">',
                    1
                )
            else:
                # Add to main content area
                content = content.replace(
                    '<main class="page-content">',
                    f'<main class="page-content">{new_post_html}'
                )
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
        except Exception as e:
            self.log_message(f"Warning: Could not update {index_path}: {e}", "WARNING")
    
    def commit_to_git(self, posts: List[Dict[str, any]]) -> bool:
        """Commit generated posts to Git with detailed message"""
        
        try:
            self.log_message("🔄 Starting Git operations...")
            
            # Change to project directory
            os.chdir(self.project_root)
            
            # Check if there are changes
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  capture_output=True, text=True, check=True)
            
            if not result.stdout.strip():
                self.log_message("No changes to commit")
                return True
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Create detailed commit message
            successful_posts = [p for p in posts if p.get("success")]
            avg_seo_score = sum(p['seo_score']['percentage'] for p in successful_posts) / len(successful_posts) if successful_posts else 0
            
            commit_message = f"""🚀 SEO-Optimized Blog Posts Generated

📊 Generation Summary:
- Posts created: {len(successful_posts)}
- Average SEO score: {avg_seo_score:.1f}%
- High-quality posts (80%+): {len([p for p in successful_posts if p['seo_score']['percentage'] >= 80])}

📝 New Posts:
{chr(10).join(f"- {p['title']} ({p['seo_score']['grade']} - {p['seo_score']['percentage']}%)" for p in successful_posts)}

✨ Features: SEO optimized, analytics tracking, schema markup, quality validated"""
            
            # Commit changes
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            self.log_message("✅ Changes committed to Git")
            
            # Push to remote
            try:
                subprocess.run(['git', 'push'], check=True)
                self.log_message("✅ Successfully pushed to remote repository")
                self.automation_metrics["git_commits"] += 1
                return True
            except subprocess.CalledProcessError as e:
                self.log_message(f"Warning: Failed to push to remote: {e}", "WARNING")
                return True
                
        except subprocess.CalledProcessError as e:
            self.log_message(f"❌ Git operation failed: {e}", "ERROR")
            return False
    
    def run_quality_check(self, posts: List[Dict[str, any]]) -> Dict[str, any]:
        """Run comprehensive quality checks on generated posts"""
        
        self.log_message("🔍 Running quality checks...")
        
        quality_report = {
            "total_posts": len(posts),
            "successful_posts": len([p for p in posts if p.get("success")]),
            "average_seo_score": 0,
            "seo_grades": {"A+": 0, "A": 0, "B+": 0, "B": 0, "C+": 0, "C": 0, "D": 0, "F": 0},
            "quality_issues": [],
            "recommendations": []
        }
        
        successful_posts = [p for p in posts if p.get("success")]
        
        if successful_posts:
            # Calculate average SEO score
            total_score = sum(p['seo_score']['percentage'] for p in successful_posts)
            quality_report["average_seo_score"] = round(total_score / len(successful_posts), 1)
            
            # Grade distribution
            for post in successful_posts:
                grade = post['seo_score']['grade']
                quality_report["seo_grades"][grade] = quality_report["seo_grades"].get(grade, 0) + 1
            
            # Quality analysis
            low_quality_posts = [p for p in successful_posts if p['seo_score']['percentage'] < 70]
            if low_quality_posts:
                quality_report["quality_issues"].append(f"{len(low_quality_posts)} posts below 70% SEO score")
            
            # Recommendations
            if quality_report["average_seo_score"] < 80:
                quality_report["recommendations"].append("Focus on improving keyword optimization and content structure")
            
            if quality_report["seo_grades"]["F"] > 0:
                quality_report["recommendations"].append("Review failing posts for major SEO issues")
        
        self.log_message(f"📊 Quality Check Results:")
        self.log_message(f"   Average SEO Score: {quality_report['average_seo_score']}%")
        self.log_message(f"   Grade Distribution: {quality_report['seo_grades']}")
        
        if quality_report["quality_issues"]:
            self.log_message("⚠️  Quality Issues:")
            for issue in quality_report["quality_issues"]:
                self.log_message(f"   • {issue}")
        
        return quality_report
    
    def run_full_seo_automation(self, post_count: int = 2, categories: Optional[List[str]] = None, 
                               auto_commit: bool = True) -> Dict[str, any]:
        """Run complete SEO automation pipeline"""
        
        start_time = datetime.now()
        self.log_message("🚀 Starting Complete SEO Blog Automation")
        self.log_message("=" * 60)
        
        # 1. Generate SEO-optimized posts
        posts = self.generate_seo_optimized_posts(post_count, categories)
        
        # 2. Update website navigation
        successful_posts = [p for p in posts if p.get("success")]
        if successful_posts:
            self.update_website_navigation(successful_posts)
        
        # 3. Run quality checks
        quality_report = self.run_quality_check(posts)
        
        # 4. Commit to Git
        git_success = False
        if successful_posts and auto_commit:
            git_success = self.commit_to_git(posts)
        
        # 5. Save metrics
        self.save_metrics()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Final summary
        summary = {
            "success": len(successful_posts) > 0,
            "posts_generated": len(successful_posts),
            "total_attempts": post_count,
            "average_seo_score": quality_report["average_seo_score"],
            "git_committed": git_success,
            "duration_seconds": duration,
            "quality_report": quality_report,
            "automation_metrics": self.automation_metrics
        }
        
        self.log_message("📊 Final Automation Summary:")
        self.log_message(f"   Posts Generated: {len(successful_posts)}/{post_count}")
        self.log_message(f"   Average SEO Score: {quality_report['average_seo_score']}%")
        self.log_message(f"   Quality Grade: {self.get_quality_grade(quality_report['average_seo_score'])}")
        self.log_message(f"   Git Operations: {'✅ Success' if git_success else '❌ Failed'}")
        self.log_message(f"   Duration: {duration:.1f} seconds")
        self.log_message("=" * 60)
        
        return summary
    
    def get_quality_grade(self, score: float) -> str:
        """Convert quality score to grade"""
        if score >= 90: return "Excellent"
        elif score >= 80: return "Good"
        elif score >= 70: return "Fair"
        elif score >= 60: return "Poor"
        else: return "Needs Improvement"


def main():
    """Main CLI interface for SEO automation"""
    
    parser = argparse.ArgumentParser(description='SEO-Optimized Blog Automation System')
    parser.add_argument('--posts', '-p', type=int, default=2, 
                       help='Number of posts to generate (default: 2)')
    parser.add_argument('--categories', '-c', nargs='+', 
                       choices=['solar', 'wind', 'battery', 'policy', 'technology', 
                               'energy_markets', 'commodities', 'stock_forecasts', 
                               'energy_financials', 'green_investing'],
                       help='Specific categories to generate')
    parser.add_argument('--no-commit', action='store_true', 
                       help='Skip Git commit operations')
    parser.add_argument('--quality-only', action='store_true',
                       help='Run quality check on existing posts only')
    parser.add_argument('--metrics', action='store_true',
                       help='Show automation metrics and exit')
    
    args = parser.parse_args()
    
    # Initialize automation system
    automation = SEOBlogAutomation()
    
    try:
        if args.metrics:
            # Show metrics only
            print("📊 SEO Automation Metrics:")
            print(json.dumps(automation.automation_metrics, indent=2))
            return
        
        if args.quality_only:
            # Quality check only
            automation.log_message("🔍 Running quality check on recent posts...")
            # This would check recent posts - simplified for demo
            return
        
        # Run full automation
        result = automation.run_full_seo_automation(
            post_count=args.posts,
            categories=args.categories,
            auto_commit=not args.no_commit
        )
        
        # Exit with appropriate code
        if result["success"]:
            print(f"\\n✅ Automation completed successfully!")
            print(f"📈 Generated {result['posts_generated']} high-quality SEO posts")
            print(f"🎯 Average SEO score: {result['average_seo_score']}%")
        else:
            print("\\n❌ Automation completed with issues")
            sys.exit(1)
            
    except KeyboardInterrupt:
        automation.log_message("\\n👋 Automation cancelled by user")
    except Exception as e:
        automation.log_message(f"❌ Unexpected error: {e}", "ERROR")
        sys.exit(1)


if __name__ == "__main__":
    main()
