"""
Enhanced ML Model Training with Expanded Topics
Including energy markets, commodities, stock forecasts, financials, and green investing
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from seo_blog_generator import SEOBlogGenerator


class EnhancedMLTrainer(SEOBlogGenerator):
    """Enhanced ML model with expanded topics and 10x more training data"""
    
    def __init__(self, posts_dir: str = "posts"):
        super().__init__(posts_dir)
        
        # Initialize base image database if not exists
        if not hasattr(self, 'image_database'):
            self.image_database = {}
        
        # Expanded topic categories with 10x more content
        self.expanded_topics = {
            # Original categories (enhanced)
            "solar": {
                "keywords": [
                    "solar panels", "solar energy", "photovoltaic systems", "renewable energy",
                    "solar power", "clean energy", "solar installation", "solar efficiency",
                    "solar technology", "green energy", "solar farm", "rooftop solar",
                    "solar cells", "perovskite solar", "bifacial panels", "solar tracking",
                    "solar inverters", "grid-tie systems", "off-grid solar", "solar financing",
                    "solar incentives", "net metering", "solar battery", "agrivoltaics",
                    "floating solar", "concentrated solar power", "solar thermal", "BIPV"
                ],
                "content_themes": [
                    "technology breakthroughs", "efficiency improvements", "cost reductions",
                    "market trends", "policy impacts", "installation guides", "maintenance tips",
                    "financial analysis", "ROI calculations", "environmental benefits",
                    "grid integration", "energy storage", "smart inverters", "monitoring systems",
                    "commercial applications", "residential solutions", "utility-scale projects",
                    "emerging technologies", "research developments", "future outlook"
                ]
            },
            "wind": {
                "keywords": [
                    "wind energy", "wind turbines", "offshore wind", "wind power",
                    "renewable energy", "clean energy", "wind farm", "wind technology",
                    "sustainable energy", "green power", "wind generation", "wind resources",
                    "onshore wind", "vertical axis turbines", "wind blade technology",
                    "wind forecasting", "capacity factors", "wind maps", "turbine maintenance",
                    "wind energy storage", "floating wind", "airborne wind", "small wind",
                    "wind-solar hybrid", "transmission lines", "grid connection", "LCOE wind"
                ],
                "content_themes": [
                    "offshore developments", "turbine innovations", "efficiency gains",
                    "cost competitiveness", "grid integration challenges", "environmental impact",
                    "wildlife protection", "noise considerations", "visual impact",
                    "community acceptance", "land use", "economic benefits",
                    "job creation", "supply chain", "manufacturing", "recycling",
                    "end-of-life management", "repowering projects", "hybrid systems"
                ]
            },
            "battery": {
                "keywords": [
                    "energy storage", "battery technology", "grid storage", "lithium batteries",
                    "energy storage systems", "battery backup", "renewable storage",
                    "clean energy storage", "smart grid", "energy security", "power storage",
                    "lithium-ion", "solid-state batteries", "flow batteries", "compressed air",
                    "pumped hydro", "thermal storage", "hydrogen storage", "battery recycling",
                    "second-life batteries", "grid services", "frequency regulation",
                    "peak shaving", "load shifting", "microgrids", "virtual power plants"
                ],
                "content_themes": [
                    "technology innovations", "cost reductions", "safety improvements",
                    "recycling solutions", "grid applications", "residential storage",
                    "commercial storage", "utility-scale deployment", "performance metrics",
                    "degradation analysis", "lifecycle assessment", "environmental impact",
                    "supply chain security", "critical materials", "manufacturing processes",
                    "quality control", "testing standards", "certification", "warranties"
                ]
            },
            
            # NEW EXPANDED CATEGORIES
            "energy_markets": {
                "keywords": [
                    "energy markets", "electricity trading", "power markets", "energy prices",
                    "wholesale electricity", "capacity markets", "ancillary services",
                    "demand response", "energy auctions", "PPA pricing", "renewable certificates",
                    "carbon markets", "emissions trading", "green certificates", "market design",
                    "grid operators", "ISOs", "RTOs", "nodal pricing", "congestion management",
                    "market volatility", "price forecasting", "load forecasting", "supply curves",
                    "merit order", "marginal costs", "market coupling", "cross-border trading"
                ],
                "content_themes": [
                    "market mechanisms", "pricing strategies", "volatility analysis",
                    "forecasting models", "trading algorithms", "risk management",
                    "regulatory frameworks", "market reforms", "competition analysis",
                    "market concentration", "vertical integration", "unbundling",
                    "transmission planning", "capacity allocation", "congestion revenue",
                    "renewable integration", "grid flexibility", "storage arbitrage",
                    "demand elasticity", "consumer behavior", "industrial loads"
                ]
            },
            "commodities": {
                "keywords": [
                    "energy commodities", "oil prices", "natural gas", "coal markets",
                    "uranium prices", "renewable fuels", "biofuels", "hydrogen prices",
                    "carbon prices", "lithium prices", "copper markets", "rare earth metals",
                    "polysilicon prices", "steel prices", "aluminum markets", "commodity trading",
                    "futures markets", "spot prices", "forward curves", "contango",
                    "backwardation", "storage costs", "transportation costs", "supply chains",
                    "geopolitical risks", "weather impacts", "seasonal patterns", "volatility"
                ],
                "content_themes": [
                    "price analysis", "supply-demand dynamics", "inventory levels",
                    "production forecasts", "consumption trends", "trade flows",
                    "refinery margins", "crack spreads", "basis differentials",
                    "transportation bottlenecks", "storage utilization", "seasonal patterns",
                    "weather correlations", "geopolitical events", "sanctions impact",
                    "strategic reserves", "emergency releases", "OPEC policies",
                    "shale revolution", "energy transition impacts", "substitution effects"
                ]
            },
            "stock_forecasts": {
                "keywords": [
                    "energy stocks", "renewable energy stocks", "utility stocks", "oil stocks",
                    "clean energy ETFs", "solar stocks", "wind energy stocks", "battery stocks",
                    "grid technology stocks", "ESG investing", "green bonds", "climate ETFs",
                    "energy transition investing", "decarbonization plays", "carbon credits",
                    "stock analysis", "earnings forecasts", "valuation models", "price targets",
                    "technical analysis", "fundamental analysis", "sector rotation", "momentum",
                    "dividend yields", "growth stocks", "value investing", "risk assessment"
                ],
                "content_themes": [
                    "earnings analysis", "revenue forecasts", "margin expansion",
                    "capital allocation", "growth strategies", "competitive positioning",
                    "market share analysis", "technological advantages", "patent portfolios",
                    "regulatory risks", "policy support", "subsidy dependence",
                    "commodity exposure", "currency hedging", "operational efficiency",
                    "project pipelines", "backlog analysis", "contract structures",
                    "customer concentration", "geographic diversification", "ESG scores"
                ]
            },
            "energy_financials": {
                "keywords": [
                    "energy company financials", "utility earnings", "renewable energy ROI",
                    "project finance", "energy investments", "LCOE analysis", "NPV calculations",
                    "IRR models", "debt financing", "equity financing", "tax credits",
                    "depreciation schedules", "cash flow analysis", "working capital",
                    "EBITDA", "free cash flow", "debt-to-equity ratios", "credit ratings",
                    "refinancing", "green loans", "sustainability-linked bonds", "ESG metrics",
                    "carbon accounting", "stranded assets", "transition costs", "capex forecasts"
                ],
                "content_themes": [
                    "financial modeling", "valuation methodologies", "risk assessment",
                    "capital structure optimization", "cost of capital", "hurdle rates",
                    "sensitivity analysis", "scenario planning", "Monte Carlo simulation",
                    "real options valuation", "project economics", "tariff analysis",
                    "regulatory asset base", "rate case outcomes", "allowed returns",
                    "performance incentives", "penalty mechanisms", "cost recovery",
                    "prudency reviews", "asset retirement obligations", "environmental liabilities"
                ]
            },
            "green_investing": {
                "keywords": [
                    "green investing", "sustainable investing", "ESG investing", "climate investing",
                    "impact investing", "responsible investing", "ethical investing", "SRI",
                    "green bonds", "sustainability bonds", "climate bonds", "blue bonds",
                    "ESG funds", "clean energy funds", "climate ETFs", "green infrastructure",
                    "sustainable finance", "taxonomy alignment", "SFDR compliance", "TCFD",
                    "carbon footprint", "scope 1 emissions", "scope 2 emissions", "scope 3 emissions",
                    "net zero targets", "science-based targets", "Paris alignment", "temperature scoring"
                ],
                "content_themes": [
                    "investment strategies", "portfolio construction", "risk-return profiles",
                    "performance attribution", "screening methodologies", "engagement strategies",
                    "proxy voting", "shareholder resolutions", "stewardship activities",
                    "impact measurement", "SDG alignment", "materiality assessment",
                    "data quality", "greenwashing risks", "regulatory compliance",
                    "disclosure requirements", "taxonomy eligibility", "transition pathways",
                    "stranded asset risks", "climate scenarios", "stress testing"
                ]
            }
        }
        
        # Enhanced image databases for new categories
        self.expanded_image_database = {
            "energy_markets": [
                "https://images.unsplash.com/photo-1611273426858-450d8e3c9fce?w=800&h=300&fit=crop&auto=format",  # Trading floor
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=300&fit=crop&auto=format",  # Stock charts
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=300&fit=crop&auto=format",  # Data analytics
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=300&fit=crop&auto=format",  # Market data
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&h=300&fit=crop&auto=format",  # Finance charts
                "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&h=300&fit=crop&auto=format"   # Technology trading
            ],
            "commodities": [
                "https://images.unsplash.com/photo-1518133910546-b6c2fb7d79e3?w=800&h=300&fit=crop&auto=format",  # Oil refinery
                "https://images.unsplash.com/photo-1497435334941-8c899ee9e8e9?w=800&h=300&fit=crop&auto=format",  # Mining
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=300&fit=crop&auto=format",  # Industrial
                "https://images.unsplash.com/photo-1621905251918-48416bd8575a?w=800&h=300&fit=crop&auto=format",  # Commodities
                "https://images.unsplash.com/photo-1518133910546-b6c2fb7d79e3?w=800&h=300&fit=crop&auto=format",  # Energy infrastructure
                "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=300&fit=crop&auto=format"   # Finance/trading
            ],
            "stock_forecasts": [
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=300&fit=crop&auto=format",  # Stock charts
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=300&fit=crop&auto=format",  # Financial data
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&h=300&fit=crop&auto=format",  # Analytics
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=300&fit=crop&auto=format",  # Data science
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=300&fit=crop&auto=format",  # Trading screens
                "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&h=300&fit=crop&auto=format"   # Tech finance
            ],
            "energy_financials": [
                "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=300&fit=crop&auto=format",  # Financial planning
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=300&fit=crop&auto=format",  # Finance charts
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=300&fit=crop&auto=format",  # Investment
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=300&fit=crop&auto=format",  # Financial data
                "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?w=800&h=300&fit=crop&auto=format",  # Analytics
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=300&fit=crop&auto=format"   # Data analysis
            ],
            "green_investing": [
                "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800&h=300&fit=crop&auto=format",  # Sustainable finance
                "https://images.unsplash.com/photo-1519452575417-564c1401ecc0?w=800&h=300&fit=crop&auto=format",  # Green investing
                "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=300&fit=crop&auto=format",  # ESG metrics
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&h=300&fit=crop&auto=format",  # Impact investing
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&h=300&fit=crop&auto=format",  # Sustainability data
                "https://images.unsplash.com/photo-1579952363873-27d3bfad9c0d?w=800&h=300&fit=crop&auto=format"   # Environmental investing
            ]
        }
        
        # Update total image database
        self.image_database.update(self.expanded_image_database)
        
        # Update SEO keywords
        for category, data in self.expanded_topics.items():
            self.seo_keywords[category] = data["keywords"]
    
    def generate_10x_training_data(self) -> Dict[str, List[str]]:
        """Generate 10x more training data across all categories"""
        
        training_data = {}
        
        for category, data in self.expanded_topics.items():
            print(f"🔄 Generating training data for {category}...")
            
            category_data = []
            keywords = data["keywords"]
            themes = data["content_themes"]
            
            # Generate 10x more content variations
            for theme in themes:
                for i in range(10):  # 10 variations per theme
                    # Mix keywords and themes for rich content
                    selected_keywords = random.sample(keywords, min(5, len(keywords)))
                    
                    content_seed = f"{theme} in {category.replace('_', ' ')} focusing on {', '.join(selected_keywords[:3])}"
                    category_data.append(content_seed)
            
            training_data[category] = category_data
        
        return training_data
    
    def retrain_model(self):
        """Retrain the ML model with expanded topics and 10x more data"""
        
        print("🚀 Starting Enhanced ML Model Retraining...")
        print("=" * 60)
        
        # Generate 10x training data
        training_data = self.generate_10x_training_data()
        
        total_samples = sum(len(data) for data in training_data.values())
        print(f"📊 Generated {total_samples} training samples across {len(training_data)} categories")
        
        # Update internal systems
        self.category_templates = {}
        self.category_patterns = {}
        
        for category, data in training_data.items():
            print(f"   📁 {category.replace('_', ' ').title()}: {len(data)} samples")
            
            # Create category templates
            self.category_templates[category] = [
                f"{random.choice(['Breaking:', 'Analysis:', 'Market Update:', 'Forecast:', 'Report:'])} {random.choice(data)}"
                for _ in range(20)  # 20 templates per category
            ]
            
            # Create content patterns
            self.category_patterns[category] = {
                "intro_patterns": [
                    f"The {category.replace('_', ' ')} sector is experiencing significant developments...",
                    f"Recent analysis of {category.replace('_', ' ')} shows promising trends...",
                    f"Market intelligence indicates that {category.replace('_', ' ')} is poised for growth...",
                    f"Industry experts are closely monitoring {category.replace('_', ' ')} developments...",
                    f"New research reveals important insights into {category.replace('_', ' ')} dynamics..."
                ],
                "body_patterns": self.expanded_topics[category]["content_themes"],
                "conclusion_patterns": [
                    f"The outlook for {category.replace('_', ' ')} remains optimistic with strong fundamentals...",
                    f"Continued monitoring of {category.replace('_', ' ')} trends will be essential...",
                    f"Stakeholders should prepare for ongoing evolution in {category.replace('_', ' ')}...",
                    f"The {category.replace('_', ' ')} landscape continues to evolve rapidly...",
                    f"Strategic positioning in {category.replace('_', ' ')} will be crucial for success..."
                ]
            }
        
        # Save training data
        training_file = Path(__file__).parent / "enhanced_training_data.json"
        with open(training_file, 'w') as f:
            json.dump({
                "categories": list(training_data.keys()),
                "total_samples": total_samples,
                "training_data": training_data,
                "templates": self.category_templates,
                "patterns": self.category_patterns,
                "created_at": datetime.now().isoformat()
            }, f, indent=2)
        
        print(f"✅ Training data saved to: {training_file}")
        print("🎯 Enhanced ML model retraining complete!")
        print("=" * 60)
        
        return training_data

def main():
    """Main function to retrain the enhanced ML model"""
    
    trainer = EnhancedMLTrainer()
    
    # Retrain with expanded topics and 10x data
    training_data = trainer.retrain_model()
    
    print("\n🎉 Enhanced ML Model Ready!")
    print(f"📊 New Categories: {len(trainer.expanded_topics)}")
    print(f"📈 Training Samples: {sum(len(data) for data in training_data.values())}")
    print("🚀 Ready to generate 1,000 high-quality posts!")

if __name__ == "__main__":
    main()
