#!/usr/bin/env python3
"""
Automated Training with Image Scraping Pipeline
Runs the complete training process including image collection and blog integration
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from ml_models.demo_training_system import DemoEnergyDataCollector, DemoEnergyDataPreprocessor, DemoEnergyTrainer
from ml_models.energy_image_scraper import EnergyImageScraper
from ml_models.blog_image_integrator import BlogImageIntegrator

class AutomatedTrainingPipeline:
    """Complete training pipeline with image scraping and blog integration"""
    
    def __init__(self):
        self.collector = DemoEnergyDataCollector()
        self.preprocessor = DemoEnergyDataPreprocessor()
        self.trainer = DemoEnergyTrainer()
        self.image_scraper = EnergyImageScraper()
        self.blog_integrator = BlogImageIntegrator()
        
        # Create logs directory
        self.logs_dir = Path("logs")
        self.logs_dir.mkdir(exist_ok=True)
        
        # Training session info
        self.session_id = f"training_{int(time.time())}"
        self.session_log = self.logs_dir / f"{self.session_id}.json"
        
        self.session_info = {
            "session_id": self.session_id,
            "start_time": datetime.now().isoformat(),
            "steps_completed": [],
            "errors": [],
            "statistics": {}
        }
    
    def log_step(self, step_name: str, success: bool = True, details: dict = None):
        """Log a training step"""
        step_info = {
            "step": step_name,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "details": details or {}
        }
        
        self.session_info["steps_completed"].append(step_info)
        
        # Save log after each step
        with open(self.session_log, 'w') as f:
            json.dump(self.session_info, f, indent=2)
        
        status = "✅" if success else "❌"
        print(f"{status} {step_name} - {datetime.now().strftime('%H:%M:%S')}")
        
        if details:
            for key, value in details.items():
                print(f"   {key}: {value}")
    
    def run_image_scraping(self) -> bool:
        """Run the image scraping process"""
        try:
            print("🖼️ Starting image scraping process...")
            
            # Scrape images for all energy topics
            scraping_results = self.image_scraper.scrape_all_topics()
            
            # Create image index
            image_index = self.image_scraper.create_image_index()
            
            self.log_step("Image Scraping", True, {
                "total_downloaded": scraping_results.get("total_downloaded", 0),
                "topics_processed": len(scraping_results.get("by_topic", {})),
                "indexed_topics": len(image_index)
            })
            
            self.session_info["statistics"]["images_downloaded"] = scraping_results.get("total_downloaded", 0)
            return True
            
        except Exception as e:
            self.log_step("Image Scraping", False, {"error": str(e)})
            self.session_info["errors"].append(f"Image scraping failed: {e}")
            return False
    
    def run_data_collection(self) -> dict:
        """Run the data collection process"""
        try:
            print("📊 Starting data collection...")
            
            # Collect data including images
            collected_data = self.collector.collect_comprehensive_data(include_images=True)
            
            self.log_step("Data Collection", True, {
                "academic_papers": len(collected_data.get("academic_papers", [])),
                "news_articles": len(collected_data.get("news_articles", [])),
                "government_reports": len(collected_data.get("government_reports", [])),
                "image_scraping_included": "image_scraping_results" in collected_data
            })
            
            return collected_data
            
        except Exception as e:
            self.log_step("Data Collection", False, {"error": str(e)})
            self.session_info["errors"].append(f"Data collection failed: {e}")
            return {}
    
    def run_data_preprocessing(self, collected_data: dict) -> dict:
        """Run the data preprocessing"""
        try:
            print("⚙️ Starting data preprocessing...")
            
            processed_data = self.preprocessor.prepare_training_data(collected_data)
            
            self.log_step("Data Preprocessing", True, {
                "processed_texts": len(processed_data.get("processed_texts", [])),
                "training_pairs": len(processed_data.get("training_pairs", [])),
                "total_documents": processed_data.get("metadata", {}).get("total_documents", 0)
            })
            
            return processed_data
            
        except Exception as e:
            self.log_step("Data Preprocessing", False, {"error": str(e)})
            self.session_info["errors"].append(f"Data preprocessing failed: {e}")
            return {}
    
    def run_model_training(self, processed_data: dict) -> dict:
        """Run the model training"""
        try:
            print("🧠 Starting model training...")
            
            training_results = self.trainer.train_model(processed_data)
            
            self.log_step("Model Training", True, {
                "model_version": training_results.get("model_version"),
                "final_accuracy": training_results.get("final_accuracy"),
                "final_loss": training_results.get("final_loss"),
                "training_data_size": training_results.get("training_data_size"),
                "epochs": training_results.get("epochs")
            })
            
            return training_results
            
        except Exception as e:
            self.log_step("Model Training", False, {"error": str(e)})
            self.session_info["errors"].append(f"Model training failed: {e}")
            return {}
    
    def run_blog_integration(self) -> bool:
        """Run blog image integration"""
        try:
            print("📝 Starting blog image integration...")
            
            # Create image report
            image_report = self.blog_integrator.create_image_report()
            
            # Update posts that need images (this will use fallbacks if no scraped images)
            integration_results = self.blog_integrator.update_all_posts(force_update=False)
            
            self.log_step("Blog Integration", True, {
                "total_posts": image_report["total_posts"],
                "posts_with_images": image_report["posts_with_images"],
                "posts_updated": integration_results["updated"],
                "posts_skipped": integration_results["skipped"],
                "errors": integration_results["errors"]
            })
            
            return True
            
        except Exception as e:
            self.log_step("Blog Integration", False, {"error": str(e)})
            self.session_info["errors"].append(f"Blog integration failed: {e}")
            return False
    
    def run_complete_pipeline(self) -> dict:
        """Run the complete training pipeline with image integration"""
        print("🚀 Starting Automated Training Pipeline with Image Integration")
        print("=" * 70)
        
        start_time = time.time()
        
        # Step 1: Image Scraping (can run in parallel with data collection)
        image_success = self.run_image_scraping()
        
        # Step 2: Data Collection
        collected_data = self.run_data_collection()
        if not collected_data:
            return self.finalize_session(success=False)
        
        # Step 3: Data Preprocessing
        processed_data = self.run_data_preprocessing(collected_data)
        if not processed_data:
            return self.finalize_session(success=False)
        
        # Step 4: Model Training
        training_results = self.run_model_training(processed_data)
        if not training_results:
            return self.finalize_session(success=False)
        
        # Step 5: Blog Integration
        blog_success = self.run_blog_integration()
        
        # Finalize
        elapsed_time = time.time() - start_time
        success = image_success and bool(training_results) and blog_success
        
        return self.finalize_session(success, elapsed_time, training_results)
    
    def finalize_session(self, success: bool, elapsed_time: float = 0, training_results: dict = None) -> dict:
        """Finalize the training session"""
        self.session_info.update({
            "end_time": datetime.now().isoformat(),
            "elapsed_time_seconds": elapsed_time,
            "success": success,
            "training_results": training_results,
            "summary": {
                "total_steps": len(self.session_info["steps_completed"]),
                "successful_steps": len([s for s in self.session_info["steps_completed"] if s["success"]]),
                "failed_steps": len([s for s in self.session_info["steps_completed"] if not s["success"]]),
                "errors_count": len(self.session_info["errors"])
            }
        })
        
        # Save final log
        with open(self.session_log, 'w') as f:
            json.dump(self.session_info, f, indent=2)
        
        # Print summary
        print("\\n" + "=" * 70)
        if success:
            print("🎉 Training Pipeline Completed Successfully!")
        else:
            print("❌ Training Pipeline Failed")
        
        print(f"📊 Session Summary:")
        print(f"   Session ID: {self.session_id}")
        print(f"   Duration: {elapsed_time:.1f} seconds")
        print(f"   Steps completed: {self.session_info['summary']['successful_steps']}/{self.session_info['summary']['total_steps']}")
        print(f"   Errors: {self.session_info['summary']['errors_count']}")
        print(f"   Log file: {self.session_log}")
        
        return self.session_info

def main():
    """Run the automated training pipeline"""
    pipeline = AutomatedTrainingPipeline()
    results = pipeline.run_complete_pipeline()
    
    # Exit with appropriate code
    sys.exit(0 if results["success"] else 1)

if __name__ == "__main__":
    main()
