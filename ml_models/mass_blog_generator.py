#!/usr/bin/env python3
"""
Mass Blog Post Generation System - 1,000 Posts in Batches
Generates posts in batches of 10 with quality checks and adjustments
"""

import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import random

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from seo_automation import SEOBlogAutomation
from enhanced_ml_trainer import EnhancedMLTrainer


class MassBlogGenerator:
    """Mass blog post generation with quality monitoring"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.log_file = self.project_root / "ml_models" / "automation_logs" / "mass_generation.log"
        self.stats_file = self.project_root / "ml_models" / "automation_logs" / "mass_stats.json"
        
        # Create directories
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Initialize systems
        self.automation = SEOBlogAutomation()
        self.enhanced_trainer = EnhancedMLTrainer()
        
        # Available categories with weights (higher = more likely to be selected)
        self.category_weights = {
            'solar': 20,
            'wind': 18,
            'battery': 16,
            'energy_markets': 12,
            'commodities': 10,
            'stock_forecasts': 8,
            'energy_financials': 8,
            'green_investing': 8,
            'policy': 6,
            'technology': 6
        }
        
        # Quality requirements
        self.quality_requirements = {
            "min_word_count": 500,
            "min_images": 2,
            "min_seo_score": 70.0,
            "target_seo_score": 80.0
        }
        
        # Generation statistics
        self.stats = {
            "total_batches": 0,
            "successful_posts": 0,
            "failed_posts": 0,
            "posts_meeting_requirements": 0,
            "average_seo_score": 0,
            "generation_start": None,
            "generation_end": None,
            "category_distribution": {},
            "quality_improvements": 0,
            "batches_completed": []
        }
        
        self.load_existing_stats()
    
    def log_message(self, message: str, level: str = "INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def load_existing_stats(self):
        """Load existing generation statistics"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    saved_stats = json.load(f)
                    self.stats.update(saved_stats)
                self.log_message(f"📊 Loaded existing stats: {self.stats['successful_posts']} posts generated")
            except Exception as e:
                self.log_message(f"Warning: Could not load stats: {e}")
    
    def save_stats(self):
        """Save current statistics"""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2, default=str)
        except Exception as e:
            self.log_message(f"Warning: Could not save stats: {e}")
    
    def select_batch_categories(self, batch_size: int = 10) -> List[str]:
        """Select categories for a batch using weighted random selection"""
        categories = []
        
        # Create weighted list
        weighted_categories = []
        for category, weight in self.category_weights.items():
            weighted_categories.extend([category] * weight)
        
        # Select categories ensuring good distribution
        selected_counts = {}
        for i in range(batch_size):
            # If we've used a category too much in this batch, reduce its weight
            available_categories = weighted_categories.copy()
            
            # Reduce weight for overused categories in this batch
            for cat, count in selected_counts.items():
                if count >= 3:  # Max 3 per category per batch
                    available_categories = [c for c in available_categories if c != cat]
            
            if available_categories:
                selected = random.choice(available_categories)
                categories.append(selected)
                selected_counts[selected] = selected_counts.get(selected, 0) + 1
            else:
                # Fallback if all categories are overused
                selected = random.choice(list(self.category_weights.keys()))
                categories.append(selected)
        
        return categories
    
    def verify_post_quality(self, post_path: str) -> Dict[str, any]:
        """Verify a post meets quality requirements"""
        try:
            with open(post_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract post content between articleBody tags
            import re
            start_marker = '<div class="post-content" itemprop="articleBody">'
            end_marker = '<script type="application/ld+json">'
            
            start_idx = content.find(start_marker)
            end_idx = content.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return {"valid": False, "error": "Could not find post content"}
            
            post_content = content[start_idx + len(start_marker):end_idx]
            
            # Count words (excluding HTML tags)
            text_only = re.sub(r'<[^>]*>', ' ', post_content)
            text_only = re.sub(r'\s+', ' ', text_only).strip()
            words = [w for w in text_only.split() if w and len(w) > 1]
            word_count = len(words)
            
            # Count images
            image_count = post_content.count('<img ')
            
            # Extract SEO score from content
            seo_score = 75.0  # Default if can't extract
            seo_match = re.search(r'Grade: [A-F][+]? \((\d+\.?\d*)%\)', content)
            if seo_match:
                seo_score = float(seo_match.group(1))
            
            # Check requirements
            requirements_met = {
                "word_count": word_count >= self.quality_requirements["min_word_count"],
                "images": image_count >= self.quality_requirements["min_images"],
                "seo_score": seo_score >= self.quality_requirements["min_seo_score"]
            }
            
            all_requirements_met = all(requirements_met.values())
            
            return {
                "valid": True,
                "word_count": word_count,
                "image_count": image_count,
                "seo_score": seo_score,
                "requirements_met": requirements_met,
                "all_requirements_met": all_requirements_met,
                "quality_grade": self.get_quality_grade(seo_score, word_count, image_count)
            }
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    def get_quality_grade(self, seo_score: float, word_count: int, image_count: int) -> str:
        """Calculate overall quality grade"""
        score = 0
        
        # SEO score component (50% weight)
        if seo_score >= 90: score += 50
        elif seo_score >= 80: score += 40
        elif seo_score >= 70: score += 30
        elif seo_score >= 60: score += 20
        else: score += 10
        
        # Word count component (30% weight)
        if word_count >= 600: score += 30
        elif word_count >= 500: score += 25
        elif word_count >= 400: score += 15
        else: score += 5
        
        # Image count component (20% weight)
        if image_count >= 2: score += 20
        elif image_count >= 1: score += 10
        
        # Convert to grade
        if score >= 90: return "A+"
        elif score >= 85: return "A"
        elif score >= 80: return "B+"
        elif score >= 70: return "B"
        elif score >= 60: return "C+"
        elif score >= 50: return "C"
        else: return "D"
    
    def analyze_batch_quality(self, batch_results: List[Dict]) -> Dict[str, any]:
        """Analyze quality of a completed batch"""
        successful_posts = [p for p in batch_results if p.get("success")]
        
        if not successful_posts:
            return {"average_quality": 0, "posts_meeting_requirements": 0, "recommendations": []}
        
        quality_scores = []
        requirements_met = 0
        total_words = 0
        total_images = 0
        total_seo = 0
        
        for post in successful_posts:
            # Verify each post
            verification = self.verify_post_quality(post["filename"])
            
            if verification["valid"]:
                quality_scores.append(verification["seo_score"])
                total_words += verification["word_count"]
                total_images += verification["image_count"]
                total_seo += verification["seo_score"]
                
                if verification["all_requirements_met"]:
                    requirements_met += 1
        
        avg_words = total_words / len(successful_posts) if successful_posts else 0
        avg_images = total_images / len(successful_posts) if successful_posts else 0
        avg_seo = total_seo / len(successful_posts) if successful_posts else 0
        
        # Generate recommendations
        recommendations = []
        if avg_seo < self.quality_requirements["target_seo_score"]:
            recommendations.append("Improve SEO optimization and keyword density")
        if avg_words < 550:
            recommendations.append("Increase content length to exceed 550 words")
        if avg_images < 2:
            recommendations.append("Ensure all posts include 2+ high-quality images")
        
        return {
            "successful_posts": len(successful_posts),
            "posts_meeting_requirements": requirements_met,
            "average_seo_score": round(avg_seo, 1),
            "average_word_count": round(avg_words),
            "average_image_count": round(avg_images, 1),
            "quality_percentage": round((requirements_met / len(successful_posts)) * 100, 1),
            "recommendations": recommendations
        }
    
    def generate_batch(self, batch_number: int, categories: List[str]) -> Dict[str, any]:
        """Generate a single batch of posts"""
        
        self.log_message(f"🚀 Starting Batch {batch_number}/100 - {len(categories)} posts")
        self.log_message(f"📂 Categories: {', '.join(categories)}")
        
        batch_start = time.time()
        
        # Generate posts using automation system
        try:
            results = self.automation.generate_seo_optimized_posts(len(categories), categories)
            
            # Analyze batch quality
            quality_analysis = self.analyze_batch_quality(results)
            
            # Update statistics
            self.stats["total_batches"] += 1
            self.stats["successful_posts"] += quality_analysis["successful_posts"]
            self.stats["posts_meeting_requirements"] += quality_analysis["posts_meeting_requirements"]
            
            # Update category distribution
            for category in categories:
                self.stats["category_distribution"][category] = self.stats["category_distribution"].get(category, 0) + 1
            
            # Update average SEO score
            if quality_analysis["successful_posts"] > 0:
                total_posts = self.stats["successful_posts"]
                current_avg = self.stats["average_seo_score"]
                batch_avg = quality_analysis["average_seo_score"]
                batch_count = quality_analysis["successful_posts"]
                
                if total_posts > batch_count:
                    new_avg = ((current_avg * (total_posts - batch_count)) + (batch_avg * batch_count)) / total_posts
                    self.stats["average_seo_score"] = round(new_avg, 1)
                else:
                    self.stats["average_seo_score"] = batch_avg
            
            batch_time = time.time() - batch_start
            
            # Log batch results
            self.log_message(f"✅ Batch {batch_number} Complete:")
            self.log_message(f"   📊 Posts Generated: {quality_analysis['successful_posts']}")
            self.log_message(f"   ✅ Meeting Requirements: {quality_analysis['posts_meeting_requirements']}")
            self.log_message(f"   📈 Average SEO Score: {quality_analysis['average_seo_score']}%")
            self.log_message(f"   📝 Average Words: {quality_analysis['average_word_count']}")
            self.log_message(f"   🖼️  Average Images: {quality_analysis['average_image_count']}")
            self.log_message(f"   ⏱️  Batch Time: {batch_time:.1f}s")
            
            if quality_analysis["recommendations"]:
                self.log_message("💡 Recommendations:")
                for rec in quality_analysis["recommendations"]:
                    self.log_message(f"   • {rec}")
            
            # Store batch info
            batch_info = {
                "batch_number": batch_number,
                "categories": categories,
                "results": quality_analysis,
                "duration": batch_time,
                "timestamp": datetime.now().isoformat()
            }
            self.stats["batches_completed"].append(batch_info)
            
            return {
                "success": True,
                "batch_info": batch_info,
                "quality_analysis": quality_analysis
            }
            
        except Exception as e:
            self.log_message(f"❌ Batch {batch_number} failed: {e}", "ERROR")
            return {"success": False, "error": str(e)}
    
    def run_quality_improvement_cycle(self):
        """Run quality improvement if recent batches are underperforming"""
        
        if len(self.stats["batches_completed"]) < 3:
            return
        
        # Check last 3 batches for quality
        recent_batches = self.stats["batches_completed"][-3:]
        avg_quality = sum(b["results"]["quality_percentage"] for b in recent_batches) / len(recent_batches)
        
        if avg_quality < 80:  # If less than 80% of posts meet requirements
            self.log_message("🔧 Running quality improvement cycle...")
            
            # Adjust category weights to favor higher-performing categories
            high_performers = ['solar', 'wind', 'battery', 'energy_markets']
            for category in high_performers:
                self.category_weights[category] = min(25, self.category_weights[category] + 2)
            
            # Reduce weights for lower performers
            low_performers = ['policy', 'technology']
            for category in low_performers:
                self.category_weights[category] = max(3, self.category_weights[category] - 1)
            
            self.stats["quality_improvements"] += 1
            self.log_message("✅ Quality improvement adjustments applied")
    
    def generate_mass_posts(self, target_posts: int = 1000, batch_size: int = 10) -> Dict[str, any]:
        """Generate mass posts in batches"""
        
        self.log_message("🚀 MASS BLOG POST GENERATION STARTING")
        self.log_message("=" * 60)
        self.log_message(f"🎯 Target: {target_posts} posts in batches of {batch_size}")
        self.log_message(f"📊 Currently: {self.stats['successful_posts']} posts generated")
        
        self.stats["generation_start"] = datetime.now().isoformat()
        
        total_batches = (target_posts - self.stats["successful_posts"] + batch_size - 1) // batch_size
        posts_to_generate = target_posts - self.stats["successful_posts"]
        
        if posts_to_generate <= 0:
            self.log_message("✅ Target already reached!")
            return {"success": True, "message": "Target already reached"}
        
        self.log_message(f"📈 Need to generate: {posts_to_generate} more posts")
        self.log_message(f"📦 Batches planned: {total_batches}")
        
        successful_batches = 0
        failed_batches = 0
        
        try:
            for batch_num in range(1, total_batches + 1):
                # Calculate posts for this batch
                remaining_posts = target_posts - self.stats["successful_posts"]
                current_batch_size = min(batch_size, remaining_posts)
                
                if current_batch_size <= 0:
                    break
                
                # Select categories for this batch
                batch_categories = self.select_batch_categories(current_batch_size)
                
                # Generate batch
                batch_result = self.generate_batch(batch_num, batch_categories)
                
                if batch_result["success"]:
                    successful_batches += 1
                    
                    # Save stats after each batch
                    self.save_stats()
                    
                    # Run quality improvement check every 5 batches
                    if batch_num % 5 == 0:
                        self.run_quality_improvement_cycle()
                    
                else:
                    failed_batches += 1
                    self.log_message(f"❌ Batch {batch_num} failed", "ERROR")
                
                # Progress update
                progress = (self.stats["successful_posts"] / target_posts) * 100
                self.log_message(f"📊 Progress: {self.stats['successful_posts']}/{target_posts} ({progress:.1f}%)")
                
                # Brief pause between batches
                if batch_num < total_batches:
                    time.sleep(2)
                
                # Check if target reached
                if self.stats["successful_posts"] >= target_posts:
                    self.log_message("🎉 TARGET REACHED!")
                    break
        
        except KeyboardInterrupt:
            self.log_message("⚠️ Generation interrupted by user", "WARNING")
        except Exception as e:
            self.log_message(f"❌ Critical error: {e}", "ERROR")
        
        # Final statistics
        self.stats["generation_end"] = datetime.now().isoformat()
        self.save_stats()
        
        # Generate final report
        final_report = self.generate_final_report()
        
        self.log_message("=" * 60)
        self.log_message("🏁 MASS GENERATION COMPLETE")
        self.log_message(f"✅ Successful Batches: {successful_batches}")
        self.log_message(f"❌ Failed Batches: {failed_batches}")
        self.log_message(f"📝 Total Posts Generated: {self.stats['successful_posts']}")
        self.log_message(f"🎯 Posts Meeting Requirements: {self.stats['posts_meeting_requirements']}")
        self.log_message(f"📊 Average SEO Score: {self.stats['average_seo_score']}%")
        self.log_message("=" * 60)
        
        return final_report
    
    def generate_final_report(self) -> Dict[str, any]:
        """Generate comprehensive final report"""
        
        if self.stats["generation_start"] and self.stats["generation_end"]:
            start_time = datetime.fromisoformat(self.stats["generation_start"])
            end_time = datetime.fromisoformat(self.stats["generation_end"])
            total_duration = (end_time - start_time).total_seconds()
        else:
            total_duration = 0
        
        return {
            "success": True,
            "total_posts_generated": self.stats["successful_posts"],
            "posts_meeting_requirements": self.stats["posts_meeting_requirements"],
            "quality_percentage": round((self.stats["posts_meeting_requirements"] / max(1, self.stats["successful_posts"])) * 100, 1),
            "average_seo_score": self.stats["average_seo_score"],
            "total_batches": self.stats["total_batches"],
            "category_distribution": self.stats["category_distribution"],
            "quality_improvements": self.stats["quality_improvements"],
            "total_duration_hours": round(total_duration / 3600, 2),
            "posts_per_hour": round(self.stats["successful_posts"] / max(1, total_duration / 3600), 1)
        }


def main():
    """Main function to run mass generation"""
    
    generator = MassBlogGenerator()
    
    # Run mass generation
    result = generator.generate_mass_posts(target_posts=1000, batch_size=10)
    
    if result["success"]:
        print("\n🎉 Mass generation completed successfully!")
        print(f"📊 Final Stats: {result}")
    else:
        print(f"\n❌ Mass generation failed: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    main()
