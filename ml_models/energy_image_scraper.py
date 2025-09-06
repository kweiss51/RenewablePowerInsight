"""
Energy Image Scraper - Collects relevant images for blog posts
Integrated with the training system to automatically gather topic-specific images
"""

import requests
import os
import hashlib
import time
import json
from urllib.parse import urlencode, urlparse
from pathlib import Path
import logging
from typing import Dict, List, Tuple

class EnergyImageScraper:
    """Scrapes energy-related images from various sources"""
    
    def __init__(self):
        self.base_dir = Path("assets/images/blog")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Energy topic categories with search terms and naming codes
        self.topic_mappings = {
            # Solar Energy
            "solar": {
                "code": "SOL",
                "search_terms": [
                    "solar panels", "photovoltaic cells", "solar farm", "solar installation",
                    "solar energy", "solar power plant", "rooftop solar", "solar array"
                ],
                "fallback_unsplash": "photo-1509391366360-2e959784a276"
            },
            "perovskite": {
                "code": "PER", 
                "search_terms": [
                    "perovskite solar cells", "advanced solar technology", "solar cell research",
                    "next generation solar", "thin film solar", "solar cell manufacturing"
                ],
                "fallback_unsplash": "photo-1509391366360-2e959784a276"
            },
            
            # Wind Energy
            "wind": {
                "code": "WIN",
                "search_terms": [
                    "wind turbines", "wind farm", "wind energy", "wind power",
                    "onshore wind", "wind mill", "wind generation", "wind technology"
                ],
                "fallback_unsplash": "photo-1548337138-e87d889cc369"
            },
            "offshore": {
                "code": "OFF",
                "search_terms": [
                    "offshore wind", "offshore wind farm", "sea wind turbines",
                    "ocean wind power", "marine wind energy", "floating wind turbines"
                ],
                "fallback_unsplash": "photo-1548337138-e87d889cc369"
            },
            
            # Electric Vehicles & Charging
            "ev": {
                "code": "EVC",
                "search_terms": [
                    "electric vehicles", "EV charging", "electric car charging",
                    "charging station", "electric vehicle infrastructure", "EV technology"
                ],
                "fallback_unsplash": "photo-1593941707874-ef25b8b4a92b"
            },
            "charging": {
                "code": "CHG",
                "search_terms": [
                    "EV charging station", "electric car charger", "fast charging",
                    "charging infrastructure", "public charging", "vehicle charging network"
                ],
                "fallback_unsplash": "photo-1593941707874-ef25b8b4a92b"
            },
            
            # Energy Storage & Batteries
            "battery": {
                "code": "BAT",
                "search_terms": [
                    "battery storage", "energy storage system", "lithium battery",
                    "grid scale battery", "battery technology", "energy storage facility"
                ],
                "fallback_unsplash": "photo-1558618666-fcd25c85cd64"
            },
            "lithium": {
                "code": "LIT",
                "search_terms": [
                    "lithium ion battery", "battery recycling", "lithium mining",
                    "battery manufacturing", "lithium battery technology", "battery cell production"
                ],
                "fallback_unsplash": "photo-1558618666-fcd25c85cd64"
            },
            
            # Smart Grid & AI
            "smart": {
                "code": "SMT",
                "search_terms": [
                    "smart grid", "energy management", "grid technology",
                    "power grid infrastructure", "electrical grid", "energy control center"
                ],
                "fallback_unsplash": "photo-1518709268805-4e9042af2176"
            },
            "ai": {
                "code": "AIM",
                "search_terms": [
                    "AI energy management", "smart energy system", "energy AI",
                    "automated energy control", "intelligent grid", "energy optimization"
                ],
                "fallback_unsplash": "photo-1518709268805-4e9042af2176"
            },
            
            # General Renewable Energy
            "renewable": {
                "code": "REN",
                "search_terms": [
                    "renewable energy", "clean energy", "sustainable energy",
                    "green technology", "renewable power", "clean technology"
                ],
                "fallback_unsplash": "photo-1466611653911-95081537e5b7"
            }
        }
        
        # Image download statistics
        self.download_stats = {
            "total_downloaded": 0,
            "by_topic": {},
            "last_update": None
        }
        
        # Set up logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_unsplash_images(self, search_term: str, count: int = 5) -> List[Dict]:
        """Get images from Unsplash API (free tier)"""
        try:
            # Unsplash Source API (no API key required for basic usage)
            images = []
            for i in range(count):
                # Use search terms to get different images
                search_hash = hashlib.md5(f"{search_term}_{i}".encode()).hexdigest()[:8]
                image_url = f"https://source.unsplash.com/1200x800/?{search_term}&sig={search_hash}"
                
                images.append({
                    "url": image_url,
                    "alt": f"{search_term} - renewable energy technology",
                    "source": "unsplash",
                    "search_term": search_term
                })
            
            return images
        except Exception as e:
            self.logger.error(f"Error getting Unsplash images: {e}")
            return []
    
    def get_pexels_images(self, search_term: str, count: int = 5) -> List[Dict]:
        """Get images from Pexels (backup source)"""
        try:
            # For demo purposes, we'll use direct URLs
            # In production, you'd use the Pexels API
            images = []
            
            # Some curated Pexels image IDs for energy topics
            energy_image_ids = {
                "solar": ["356036", "433308", "2800832", "2800844"],
                "wind": ["414910", "433308", "2800832"],
                "battery": ["163100", "356043", "2800844"],
                "electric": ["110844", "163100", "356043"]
            }
            
            # Map search terms to image categories
            category = "solar"  # default
            if "wind" in search_term:
                category = "wind"
            elif "battery" in search_term or "storage" in search_term:
                category = "battery"
            elif "electric" in search_term or "charging" in search_term:
                category = "electric"
            
            image_ids = energy_image_ids.get(category, energy_image_ids["solar"])
            
            for i, img_id in enumerate(image_ids[:count]):
                images.append({
                    "url": f"https://images.pexels.com/photos/{img_id}/pexels-photo-{img_id}.jpeg?auto=compress&cs=tinysrgb&w=1200&h=800&dpr=1",
                    "alt": f"{search_term} - sustainable energy technology",
                    "source": "pexels", 
                    "search_term": search_term
                })
            
            return images
        except Exception as e:
            self.logger.error(f"Error getting Pexels images: {e}")
            return []
    
    def download_image(self, image_url: str, filename: str) -> bool:
        """Download an image from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            filepath = self.base_dir / filename
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"Downloaded: {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading {image_url}: {e}")
            return False
    
    def generate_filename(self, topic_code: str, search_term: str, index: int, source: str) -> str:
        """Generate standardized filename for images"""
        # Create a hash of the search term for uniqueness
        term_hash = hashlib.md5(search_term.encode()).hexdigest()[:6]
        
        # Format: TOPICCODE_SOURCE_HASH_INDEX.jpg
        filename = f"{topic_code}_{source.upper()}_{term_hash}_{index:02d}.jpg"
        return filename
    
    def scrape_topic_images(self, topic: str, max_images: int = 8) -> Dict:
        """Scrape images for a specific energy topic"""
        if topic not in self.topic_mappings:
            self.logger.warning(f"Unknown topic: {topic}")
            return {"success": False, "downloaded": 0}
        
        topic_info = self.topic_mappings[topic]
        topic_code = topic_info["code"]
        search_terms = topic_info["search_terms"]
        
        self.logger.info(f"Scraping images for topic: {topic} ({topic_code})")
        
        downloaded_count = 0
        images_per_source = max_images // 2  # Split between sources
        
        for i, search_term in enumerate(search_terms[:2]):  # Use first 2 search terms
            # Get images from Unsplash
            unsplash_images = self.get_unsplash_images(search_term, images_per_source)
            
            for j, image_info in enumerate(unsplash_images):
                filename = self.generate_filename(topic_code, search_term, j, "unsplash")
                if self.download_image(image_info["url"], filename):
                    downloaded_count += 1
                
                time.sleep(1)  # Be respectful to the API
            
            # Get images from Pexels as backup
            pexels_images = self.get_pexels_images(search_term, images_per_source)
            
            for j, image_info in enumerate(pexels_images):
                filename = self.generate_filename(topic_code, search_term, j + images_per_source, "pexels")
                if self.download_image(image_info["url"], filename):
                    downloaded_count += 1
                
                time.sleep(1)  # Be respectful to the API
        
        # Update statistics
        self.download_stats["by_topic"][topic] = downloaded_count
        self.download_stats["total_downloaded"] += downloaded_count
        
        return {"success": True, "downloaded": downloaded_count}
    
    def scrape_all_topics(self) -> Dict:
        """Scrape images for all energy topics"""
        self.logger.info("Starting comprehensive energy image scraping...")
        
        total_downloaded = 0
        results = {}
        
        for topic in self.topic_mappings.keys():
            result = self.scrape_topic_images(topic)
            results[topic] = result
            total_downloaded += result.get("downloaded", 0)
            
            # Small delay between topics
            time.sleep(2)
        
        self.download_stats["last_update"] = time.time()
        
        # Save statistics
        stats_file = self.base_dir / "download_stats.json"
        with open(stats_file, 'w') as f:
            json.dump(self.download_stats, f, indent=2)
        
        self.logger.info(f"Scraping complete! Downloaded {total_downloaded} images total")
        
        return {
            "success": True,
            "total_downloaded": total_downloaded,
            "by_topic": results,
            "stats_file": str(stats_file)
        }
    
    def get_image_for_blog_post(self, post_title: str, post_content: str, post_filename: str) -> Tuple[str, str]:
        """Get the best local image for a blog post"""
        # Determine topic from post content and filename
        text_to_analyze = f"{post_title} {post_content} {post_filename}".lower()
        
        # Find the best matching topic
        best_topic = None
        best_score = 0
        
        for topic, info in self.topic_mappings.items():
            score = 0
            for term in info["search_terms"]:
                term_words = term.lower().split()
                for word in term_words:
                    if word in text_to_analyze:
                        score += 1
            
            if score > best_score:
                best_score = score
                best_topic = topic
        
        if not best_topic:
            best_topic = "renewable"  # Default
        
        # Look for local images for this topic
        topic_code = self.topic_mappings[best_topic]["code"]
        
        # Find available images for this topic
        available_images = list(self.base_dir.glob(f"{topic_code}_*.jpg"))
        
        if available_images:
            # Return the first available image
            selected_image = available_images[0]
            image_url = f"/assets/images/blog/{selected_image.name}"
            alt_text = f"{best_topic.title()} energy technology"
            return image_url, alt_text
        else:
            # Fallback to Unsplash URL
            fallback_id = self.topic_mappings[best_topic]["fallback_unsplash"]
            image_url = f"https://images.unsplash.com/{fallback_id}?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80"
            alt_text = f"{best_topic.title()} energy technology"
            return image_url, alt_text
    
    def create_image_index(self) -> Dict:
        """Create an index of all available images"""
        index = {}
        
        for image_file in self.base_dir.glob("*.jpg"):
            # Parse filename: TOPICCODE_SOURCE_HASH_INDEX.jpg
            parts = image_file.stem.split("_")
            if len(parts) >= 4:
                topic_code = parts[0]
                source = parts[1]
                
                # Find topic name from code
                topic_name = None
                for topic, info in self.topic_mappings.items():
                    if info["code"] == topic_code:
                        topic_name = topic
                        break
                
                if topic_name:
                    if topic_name not in index:
                        index[topic_name] = []
                    
                    index[topic_name].append({
                        "filename": image_file.name,
                        "path": f"/assets/images/blog/{image_file.name}",
                        "source": source.lower(),
                        "topic_code": topic_code
                    })
        
        # Save index
        index_file = self.base_dir / "image_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        return index

def main():
    """Test the image scraper"""
    scraper = EnergyImageScraper()
    
    print("🖼️ Energy Image Scraper Test")
    print("=" * 50)
    
    # Test scraping a few topics
    test_topics = ["solar", "wind", "battery", "ev"]
    
    for topic in test_topics:
        print(f"\n📸 Scraping images for: {topic}")
        result = scraper.scrape_topic_images(topic, max_images=4)
        print(f"   Downloaded: {result.get('downloaded', 0)} images")
    
    # Create image index
    print("\n📋 Creating image index...")
    index = scraper.create_image_index()
    print(f"   Indexed {len(index)} topics with images")
    
    # Test image selection for blog post
    print("\n🎯 Testing image selection...")
    image_url, alt_text = scraper.get_image_for_blog_post(
        "Solar Panel Efficiency Breakthrough",
        "New perovskite solar cells achieve record efficiency",
        "solar-efficiency-breakthrough.md"
    )
    print(f"   Selected: {image_url}")
    print(f"   Alt text: {alt_text}")

if __name__ == "__main__":
    main()
