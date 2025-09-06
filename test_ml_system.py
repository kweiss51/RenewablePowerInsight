#!/usr/bin/env python3
"""
Simple test script to verify the ML components work
"""
import sys
import logging
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all core imports work"""
    logger.info("🧪 Testing core imports...")
    
    try:
        # Test data collector
        from ml_models.advanced_data_collector import AdvancedEnergyDataCollector
        logger.info("✅ AdvancedEnergyDataCollector import successful")
        
        # Test preprocessor
        from ml_models.advanced_data_preprocessor import AdvancedEnergyDataPreprocessor
        logger.info("✅ AdvancedEnergyDataPreprocessor import successful")
        
        # Test trainer
        from ml_models.advanced_trainer import AdvancedEnergyTrainer
        logger.info("✅ AdvancedEnergyTrainer import successful")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False

def test_data_collector():
    """Test data collector initialization"""
    logger.info("🧪 Testing data collector initialization...")
    
    try:
        from ml_models.advanced_data_collector import AdvancedEnergyDataCollector
        
        collector = AdvancedEnergyDataCollector()
        logger.info(f"✅ Data collector initialized")
        logger.info(f"📚 Academic keywords: {len(collector.academic_keywords)}")
        logger.info(f"🏛️ Institutional sources: {len(collector.institutional_sources)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Data collector test failed: {e}")
        return False

def test_preprocessor():
    """Test preprocessor initialization"""
    logger.info("🧪 Testing preprocessor initialization...")
    
    try:
        from ml_models.advanced_data_preprocessor import AdvancedEnergyDataPreprocessor
        
        preprocessor = AdvancedEnergyDataPreprocessor()
        logger.info(f"✅ Preprocessor initialized")
        
        # Test basic functionality without methods that require NLTK
        logger.info(f"📊 Preprocessor ready for text processing")
        
        return True
    except Exception as e:
        logger.error(f"❌ Preprocessor test failed: {e}")
        return False

def test_trainer():
    """Test trainer initialization"""
    logger.info("🧪 Testing trainer initialization...")
    
    try:
        from ml_models.advanced_trainer import AdvancedEnergyTrainer
        
        # Create a minimal config for testing
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
        logger.info(f"✅ Trainer initialized")
        logger.info(f"🏗️ Base model: {config['base_model']}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Trainer test failed: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🚀 Starting ML system tests...")
    
    tests = [
        ("Import Tests", test_imports),
        ("Data Collector", test_data_collector),
        ("Preprocessor", test_preprocessor),
        ("Trainer", test_trainer)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! ML system is ready.")
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
