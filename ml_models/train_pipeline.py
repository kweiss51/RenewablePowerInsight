#!/usr/bin/env python3
"""
Energy LLM Training Pipeline
Complete pipeline for training custom Energy Language Model
"""

import argparse
import logging
import sys
from pathlib import Path
import json
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_packages = []
    
    try:
        import torch
        logger.info(f"✅ PyTorch {torch.__version__} found")
    except ImportError:
        missing_packages.append("torch")
    
    try:
        import transformers
        logger.info(f"✅ Transformers {transformers.__version__} found")
    except ImportError:
        missing_packages.append("transformers")
    
    try:
        import datasets
        logger.info(f"✅ Datasets library found")
    except ImportError:
        missing_packages.append("datasets")
    
    try:
        import numpy as np
        logger.info(f"✅ NumPy {np.__version__} found")
    except ImportError:
        missing_packages.append("numpy")
    
    if missing_packages:
        logger.error(f"❌ Missing required packages: {', '.join(missing_packages)}")
        logger.info("Please install missing packages with:")
        logger.info("pip install torch transformers datasets numpy accelerate wandb tqdm")
        return False
    
    return True

def run_data_collection(args):
    """Run data collection pipeline"""
    logger.info("📚 Starting data collection...")
    
    try:
        from data_collector import EnergyDataCollector
        
        collector = EnergyDataCollector(
            output_dir=args.data_dir,
            max_articles=args.max_articles
        )
        
        # Collect data
        data_info = collector.collect_training_data()
        
        if data_info and data_info['total_articles'] > 0:
            logger.info(f"✅ Collected {data_info['total_articles']} articles")
            return True
        else:
            logger.error("❌ No data collected")
            return False
            
    except Exception as e:
        logger.error(f"❌ Data collection failed: {e}")
        return False

def run_data_preprocessing(args):
    """Run data preprocessing pipeline"""
    logger.info("🔧 Starting data preprocessing...")
    
    try:
        from data_preprocessor import EnergyDataPreprocessor
        
        preprocessor = EnergyDataPreprocessor(
            data_dir=args.data_dir,
            output_dir=args.processed_dir,
            max_length=args.max_length,
            train_split=args.train_split
        )
        
        # Preprocess data
        result = preprocessor.preprocess_for_training()
        
        if result:
            logger.info(f"✅ Preprocessing complete")
            logger.info(f"   - Training samples: {result['train_size']}")
            logger.info(f"   - Validation samples: {result['val_size']}")
            logger.info(f"   - Vocabulary size: {result['vocab_size']}")
            return True
        else:
            logger.error("❌ Preprocessing failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Preprocessing failed: {e}")
        return False

def run_training(args):
    """Run model training"""
    logger.info("🚀 Starting model training...")
    
    try:
        from trainer import EnergyLLMTrainer, TrainingConfig
        
        # Create training configuration
        config = TrainingConfig(
            model_size=args.model_size,
            batch_size=args.batch_size,
            learning_rate=args.learning_rate,
            num_epochs=args.num_epochs,
            max_sequence_length=args.max_length,
            train_data_path=args.processed_dir,
            output_dir=args.output_dir,
            use_fp16=args.use_fp16,
            use_wandb=args.use_wandb
        )
        
        # Create trainer
        trainer = EnergyLLMTrainer(config)
        
        # Start training
        result = trainer.train()
        
        if result:
            logger.info("✅ Training completed successfully!")
            logger.info(f"   - Best validation loss: {result['best_eval_loss']:.4f}")
            logger.info(f"   - Model saved to: {args.output_dir}")
            return True
        else:
            logger.error("❌ Training failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Training failed: {e}")
        return False

def test_inference(args):
    """Test the trained model"""
    logger.info("🧪 Testing trained model...")
    
    try:
        from inference import EnergyLLMInference
        
        # Find best model
        best_model_path = Path(args.output_dir) / "best_model"
        if not best_model_path.exists():
            # Try final model
            best_model_path = Path(args.output_dir) / "final_model"
        
        if not best_model_path.exists():
            logger.error(f"❌ No trained model found in {args.output_dir}")
            return False
        
        # Load model
        llm = EnergyLLMInference(str(best_model_path))
        
        # Test generation
        test_prompts = [
            "The future of solar energy technology",
            "Wind power capacity expansion",
            "Battery storage innovations",
            "Green hydrogen developments"
        ]
        
        logger.info("Testing model with sample prompts...")
        for prompt in test_prompts:
            result = llm.generate_text(
                prompt,
                max_length=100,
                style='analytical'
            )
            logger.info(f"Prompt: {prompt}")
            logger.info(f"Generated: {result[:100]}...")
            logger.info("-" * 50)
        
        # Test blog post generation
        logger.info("Testing blog post generation...")
        blog_post = llm.generate_blog_post(
            "Renewable Energy Investment Trends 2024",
            [
                "Solar power cost reductions",
                "Wind energy capacity growth",
                "Battery storage market expansion"
            ]
        )
        
        logger.info(f"Generated blog post: {blog_post['title']}")
        logger.info(f"Word count: {len(blog_post['full_text'].split())}")
        
        logger.info("✅ Model testing completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model testing failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Energy LLM Training Pipeline")
    
    # General settings
    parser.add_argument('--stage', choices=['all', 'collect', 'preprocess', 'train', 'test'], 
                       default='all', help='Pipeline stage to run')
    parser.add_argument('--data-dir', type=str, default='training_data/raw',
                       help='Directory for raw training data')
    parser.add_argument('--processed-dir', type=str, default='training_data/processed',
                       help='Directory for processed training data')
    parser.add_argument('--output-dir', type=str, default='model_checkpoints',
                       help='Directory for model checkpoints and final model')
    
    # Data collection settings
    parser.add_argument('--max-articles', type=int, default=5000,
                       help='Maximum number of articles to collect')
    
    # Preprocessing settings
    parser.add_argument('--max-length', type=int, default=512,
                       help='Maximum sequence length for training')
    parser.add_argument('--train-split', type=float, default=0.9,
                       help='Training data split ratio')
    
    # Training settings
    parser.add_argument('--model-size', choices=['small', 'base', 'large'], default='base',
                       help='Model size configuration')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Training batch size')
    parser.add_argument('--learning-rate', type=float, default=2e-5,
                       help='Learning rate')
    parser.add_argument('--num-epochs', type=int, default=3,
                       help='Number of training epochs')
    parser.add_argument('--use-fp16', action='store_true',
                       help='Use mixed precision training')
    parser.add_argument('--use-wandb', action='store_true',
                       help='Use Weights & Biases for logging')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create directories
    Path(args.data_dir).mkdir(parents=True, exist_ok=True)
    Path(args.processed_dir).mkdir(parents=True, exist_ok=True)
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info("🎯 Energy LLM Training Pipeline Starting...")
    logger.info(f"Stage: {args.stage}")
    logger.info(f"Model size: {args.model_size}")
    logger.info(f"Max articles: {args.max_articles}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Epochs: {args.num_epochs}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    success = True
    
    # Run pipeline stages
    if args.stage in ['all', 'collect']:
        success &= run_data_collection(args)
        if not success:
            logger.error("❌ Data collection failed, stopping pipeline")
            sys.exit(1)
    
    if args.stage in ['all', 'preprocess']:
        success &= run_data_preprocessing(args)
        if not success:
            logger.error("❌ Data preprocessing failed, stopping pipeline")
            sys.exit(1)
    
    if args.stage in ['all', 'train']:
        success &= run_training(args)
        if not success:
            logger.error("❌ Training failed, stopping pipeline")
            sys.exit(1)
    
    if args.stage in ['all', 'test']:
        success &= test_inference(args)
        if not success:
            logger.error("❌ Model testing failed")
            sys.exit(1)
    
    if success:
        logger.info("🎉 Energy LLM Pipeline completed successfully!")
        
        # Save pipeline info
        pipeline_info = {
            'completion_time': datetime.now().isoformat(),
            'stage': args.stage,
            'model_size': args.model_size,
            'max_articles': args.max_articles,
            'batch_size': args.batch_size,
            'learning_rate': args.learning_rate,
            'num_epochs': args.num_epochs,
            'data_dir': args.data_dir,
            'processed_dir': args.processed_dir,
            'output_dir': args.output_dir
        }
        
        with open(Path(args.output_dir) / 'pipeline_info.json', 'w') as f:
            json.dump(pipeline_info, f, indent=2)
        
        logger.info(f"📄 Pipeline info saved to {args.output_dir}/pipeline_info.json")
        
        if args.stage == 'all':
            logger.info("🚀 Your custom Energy LLM is ready to use!")
            logger.info(f"Model location: {args.output_dir}/best_model")
            logger.info("You can now integrate it with your blog generation system.")
    else:
        logger.error("❌ Pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
