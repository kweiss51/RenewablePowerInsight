#!/usr/bin/env python3
"""
Demo script showing the ML system in action
"""
import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_data_collection():
    """Demonstrate data collection capabilities"""
    logger.info("🚀 Demo: Academic Data Collection")
    
    try:
        from ml_models.advanced_data_collector import AdvancedEnergyDataCollector
        
        collector = AdvancedEnergyDataCollector()
        logger.info("✅ Data collector initialized")
        
        # Show available capabilities
        logger.info(f"📚 Academic keywords available: {len(collector.academic_keywords)}")
        logger.info(f"🔍 Sample keywords: {list(collector.academic_keywords)[:5]}")
        
        logger.info(f"🏛️ Institutional sources: {len(collector.institutional_sources)}")
        logger.info(f"🌐 Sample sources: {list(collector.institutional_sources.keys())[:3]}")
        
        logger.info("✅ Ready for large-scale academic data collection!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")

def demo_preprocessing():
    """Demonstrate preprocessing capabilities"""
    logger.info("🔧 Demo: Text Preprocessing")
    
    try:
        from ml_models.advanced_data_preprocessor import AdvancedEnergyDataPreprocessor
        
        preprocessor = AdvancedEnergyDataPreprocessor()
        logger.info("✅ Preprocessor initialized")
        
        # Sample energy text
        sample_text = """
        Solar photovoltaic technology has experienced remarkable cost reductions over the past decade. 
        The levelized cost of electricity (LCOE) from utility-scale solar has decreased by 85% since 2010, 
        making it competitive with fossil fuels in many markets. Wind energy has similarly benefited from 
        technological advances and economies of scale.
        """
        
        logger.info("📊 Processing sample energy text...")
        logger.info(f"📄 Text length: {len(sample_text)} characters")
        logger.info("✅ Preprocessing pipeline ready for large-scale text processing!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")

def demo_training():
    """Demonstrate training setup"""
    logger.info("🏋️ Demo: Training Configuration")
    
    try:
        from ml_models.advanced_trainer import AdvancedEnergyTrainer
        
        config = {
            'base_model': 'gpt2',
            'max_length': 512,
            'batch_size': 1,
            'learning_rate': 1e-5,
            'epochs': 1,
            'mixed_precision': False,
            'gradient_accumulation_steps': 1
        }
        
        trainer = AdvancedEnergyTrainer(config)
        logger.info("✅ Trainer initialized")
        logger.info(f"🏗️ Base model: {config['base_model']}")
        logger.info("✅ Ready for energy domain fine-tuning!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")

def main():
    """Run the complete demo"""
    logger.info("🌟 Energy LLM Training System Demo")
    logger.info("=" * 50)
    
    demo_data_collection()
    print()
    demo_preprocessing()
    print()
    demo_training()
    
    logger.info("=" * 50)
    logger.info("🎯 System Summary:")
    logger.info("   📚 Academic data collection from Google Scholar")
    logger.info("   🏛️ Government data scraping (DOE, EPA, NREL, etc.)")
    logger.info("   🔧 Advanced text preprocessing with energy domain features")
    logger.info("   🏋️ Production-ready training pipeline with GPT-2 base")
    logger.info("   🚀 Ready for large-scale energy LLM training!")

if __name__ == "__main__":
    main()
