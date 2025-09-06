"""
Complete ML Pipeline Orchestrator for Energy Domain LLM
Handles data collection, preprocessing, training, and deployment
"""

import os
import sys
import json
import time
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnergyMLPipeline:
    """Complete ML pipeline for energy domain LLM"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.load_config(config_path)
        self.workspace_dir = Path(__file__).parent.parent.absolute()
        self.setup_directories()
        
    def load_config(self, config_path: Optional[str] = None) -> Dict:
        """Load pipeline configuration"""
        default_config = {
            'data_collection': {
                'collect_academic': True,
                'collect_government': True,
                'collect_news': True,
                'months_of_news': 6,
                'max_papers_per_query': 50,
                'energy_queries': [
                    'renewable energy systems',
                    'solar photovoltaic efficiency',
                    'wind energy technology',
                    'battery energy storage',
                    'smart grid infrastructure',
                    'hydrogen fuel cells',
                    'carbon capture storage',
                    'energy transition policy',
                    'sustainable energy economics',
                    'clean energy investment'
                ]
            },
            'preprocessing': {
                'priority_threshold': 0.5,
                'max_sequence_length': 1024,
                'min_word_count': 50,
                'energy_term_density_threshold': 0.01
            },
            'training': {
                'base_model': 'microsoft/DialoGPT-medium',
                'num_epochs': 3,
                'train_batch_size': 4,
                'eval_batch_size': 4,
                'learning_rate': 5e-5,
                'warmup_ratio': 0.1,
                'gradient_accumulation_steps': 4,
                'mixed_precision': True,
                'use_wandb': False,
                'save_steps': 1
            },
            'evaluation': {
                'generate_samples': True,
                'sample_prompts': [
                    "What are the latest developments in solar energy?",
                    "Explain the benefits of energy storage systems.",
                    "How does carbon capture technology work?",
                    "What is the future of renewable energy?",
                    "Describe smart grid technologies."
                ]
            },
            'deployment': {
                'create_api': True,
                'optimize_model': True,
                'quantization': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                user_config = json.load(f)
                # Merge configurations
                default_config.update(user_config)
        
        return default_config
    
    def setup_directories(self):
        """Setup required directories"""
        directories = [
            'training_data',
            'model_checkpoints',
            'logs',
            'results',
            'api_models'
        ]
        
        for directory in directories:
            (self.workspace_dir / directory).mkdir(exist_ok=True)
    
    def install_dependencies(self):
        """Install required dependencies"""
        logger.info("🔧 Installing dependencies...")
        
        try:
            # Install Python packages
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', 
                str(self.workspace_dir / 'requirements.txt')
            ], check=True)
            
            # Download spaCy model
            subprocess.run([
                sys.executable, '-m', 'spacy', 'download', 'en_core_web_sm'
            ], check=True)
            
            # Download NLTK data
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
            nltk.download('averaged_perceptron_tagger', quiet=True)
            
            logger.info("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            raise
    
    def collect_training_data(self):
        """Run data collection pipeline"""
        logger.info("📊 Starting data collection...")
        
        try:
            # Import and run data collector
            sys.path.append(str(self.workspace_dir / 'ml_models'))
            from advanced_data_collector import AdvancedEnergyDataCollector
            
            collector = AdvancedEnergyDataCollector()
            
            # Collect data based on configuration
            data = {}
            
            if self.config['data_collection']['collect_academic']:
                logger.info("📚 Collecting academic papers...")
                academic_data = collector.collect_academic_papers(
                    queries=self.config['data_collection']['energy_queries'],
                    max_papers_per_query=self.config['data_collection']['max_papers_per_query']
                )
                data['academic_papers'] = academic_data
            
            if self.config['data_collection']['collect_government']:
                logger.info("🏛️ Collecting government content...")
                government_data = collector.collect_government_content()
                data['government_content'] = government_data
            
            if self.config['data_collection']['collect_news']:
                logger.info("📰 Collecting news articles...")
                news_data = collector.collect_energy_news(
                    months=self.config['data_collection']['months_of_news']
                )
                data['news_articles'] = news_data
            
            # Save collected data
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_file = self.workspace_dir / 'training_data' / f'energy_training_data_{timestamp}.json'
            
            with open(data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Data collection completed. Saved to {data_file}")
            return str(data_file)
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {e}")
            raise
    
    def preprocess_data(self, data_file: str):
        """Run data preprocessing pipeline"""
        logger.info("🔄 Starting data preprocessing...")
        
        try:
            # Import and run preprocessor
            sys.path.append(str(self.workspace_dir / 'ml_models'))
            from advanced_data_preprocessor import AdvancedEnergyDataPreprocessor
            
            preprocessor = AdvancedEnergyDataPreprocessor()
            
            # Load and preprocess data
            data = preprocessor.load_training_data(data_file)
            result = preprocessor.create_training_dataset(
                data, 
                output_dir=str(self.workspace_dir / 'training_data')
            )
            
            logger.info("✅ Data preprocessing completed")
            return result
            
        except Exception as e:
            logger.error(f"❌ Data preprocessing failed: {e}")
            raise
    
    def train_model(self, preprocessed_data: Dict):
        """Train the energy domain LLM"""
        logger.info("🚀 Starting model training...")
        
        try:
            # Import and run trainer
            sys.path.append(str(self.workspace_dir / 'ml_models'))
            from advanced_trainer import AdvancedEnergyTrainer, create_training_config
            
            # Create training configuration
            config = create_training_config()
            
            # Update with pipeline configuration
            config.update(self.config['training'])
            config['output_dir'] = str(self.workspace_dir / 'model_checkpoints')
            
            # Find latest training data files
            training_data_dir = Path(preprocessed_data['output_directory'])
            high_quality_files = list(training_data_dir.glob('high_quality_corpus_*.jsonl'))
            validation_files = list(training_data_dir.glob('validation_*.jsonl'))
            
            if high_quality_files:
                config['train_data_path'] = str(max(high_quality_files))
            if validation_files:
                config['val_data_path'] = str(max(validation_files))
            
            # Create and run trainer
            trainer = AdvancedEnergyTrainer(config)
            trainer.train()
            
            logger.info("✅ Model training completed")
            return config['output_dir']
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            raise
    
    def evaluate_model(self, model_dir: str):
        """Evaluate the trained model"""
        logger.info("📊 Starting model evaluation...")
        
        try:
            # Import evaluation components
            sys.path.append(str(self.workspace_dir / 'ml_models'))
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Load best model
            best_model_dir = Path(model_dir) / 'best_model'
            if not best_model_dir.exists():
                # Use latest checkpoint
                checkpoints = list(Path(model_dir).glob('checkpoint-epoch-*'))
                if checkpoints:
                    best_model_dir = max(checkpoints)
                else:
                    logger.error("No trained model found")
                    return
            
            tokenizer = AutoTokenizer.from_pretrained(best_model_dir)
            model = AutoModelForCausalLM.from_pretrained(best_model_dir)
            
            # Generate sample outputs
            if self.config['evaluation']['generate_samples']:
                logger.info("🎯 Generating sample outputs...")
                
                results = {}
                device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                model.to(device)
                model.eval()
                
                for prompt in self.config['evaluation']['sample_prompts']:
                    logger.info(f"Generating response for: {prompt}")
                    
                    inputs = tokenizer.encode(prompt, return_tensors='pt').to(device)
                    
                    with torch.no_grad():
                        outputs = model.generate(
                            inputs,
                            max_length=200,
                            num_return_sequences=1,
                            temperature=0.7,
                            do_sample=True,
                            pad_token_id=tokenizer.eos_token_id
                        )
                    
                    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                    response = response[len(prompt):].strip()
                    
                    results[prompt] = response
                
                # Save evaluation results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                results_file = self.workspace_dir / 'results' / f'evaluation_results_{timestamp}.json'
                
                with open(results_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
                
                logger.info(f"✅ Evaluation completed. Results saved to {results_file}")
                
                # Print sample results
                for prompt, response in results.items():
                    print(f"\n🔍 Prompt: {prompt}")
                    print(f"🤖 Response: {response}")
            
            return str(results_file) if 'results_file' in locals() else None
            
        except Exception as e:
            logger.error(f"❌ Model evaluation failed: {e}")
            raise
    
    def deploy_model(self, model_dir: str):
        """Deploy the model for inference"""
        logger.info("🚀 Starting model deployment...")
        
        try:
            if self.config['deployment']['create_api']:
                # Update inference.py to use the trained model
                best_model_dir = Path(model_dir) / 'best_model'
                if not best_model_dir.exists():
                    checkpoints = list(Path(model_dir).glob('checkpoint-epoch-*'))
                    if checkpoints:
                        best_model_dir = max(checkpoints)
                
                # Copy model to api_models directory
                import shutil
                api_model_dir = self.workspace_dir / 'api_models' / 'energy_llm'
                if api_model_dir.exists():
                    shutil.rmtree(api_model_dir)
                shutil.copytree(best_model_dir, api_model_dir)
                
                logger.info(f"✅ Model deployed to {api_model_dir}")
            
            if self.config['deployment']['optimize_model']:
                logger.info("⚡ Optimizing model for inference...")
                # Model optimization could be added here
                pass
            
            logger.info("✅ Model deployment completed")
            
        except Exception as e:
            logger.error(f"❌ Model deployment failed: {e}")
            raise
    
    def run_complete_pipeline(self):
        """Run the complete ML pipeline"""
        logger.info("🚀 Starting complete Energy LLM training pipeline...")
        
        pipeline_start_time = time.time()
        
        try:
            # Step 1: Install dependencies
            self.install_dependencies()
            
            # Step 2: Collect training data
            data_file = self.collect_training_data()
            
            # Step 3: Preprocess data
            preprocessed_data = self.preprocess_data(data_file)
            
            # Step 4: Train model
            model_dir = self.train_model(preprocessed_data)
            
            # Step 5: Evaluate model
            evaluation_results = self.evaluate_model(model_dir)
            
            # Step 6: Deploy model
            self.deploy_model(model_dir)
            
            pipeline_duration = time.time() - pipeline_start_time
            
            logger.info(f"🎉 Complete pipeline finished successfully!")
            logger.info(f"⏱️ Total duration: {pipeline_duration/3600:.2f} hours")
            
            # Create pipeline summary
            summary = {
                'status': 'completed',
                'duration_hours': pipeline_duration / 3600,
                'data_file': data_file,
                'model_directory': model_dir,
                'evaluation_results': evaluation_results,
                'timestamp': datetime.now().isoformat(),
                'statistics': preprocessed_data.get('statistics', {})
            }
            
            summary_file = self.workspace_dir / 'results' / 'pipeline_summary.json'
            with open(summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info(f"📊 Pipeline summary saved to {summary_file}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise
    
    def run_quick_test(self):
        """Run a quick test of the pipeline with minimal data"""
        logger.info("🧪 Running quick pipeline test...")
        
        # Modify config for quick test
        self.config['data_collection']['max_papers_per_query'] = 5
        self.config['data_collection']['months_of_news'] = 1
        self.config['training']['num_epochs'] = 1
        self.config['training']['train_batch_size'] = 2
        
        return self.run_complete_pipeline()

def main():
    parser = argparse.ArgumentParser(description='Energy Domain LLM Training Pipeline')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--mode', choices=['full', 'test', 'collect', 'preprocess', 'train', 'evaluate'], 
                       default='full', help='Pipeline mode to run')
    parser.add_argument('--data-file', type=str, help='Path to training data file (for preprocess mode)')
    parser.add_argument('--model-dir', type=str, help='Path to model directory (for evaluate mode)')
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = EnergyMLPipeline(args.config)
    
    try:
        if args.mode == 'full':
            pipeline.run_complete_pipeline()
        elif args.mode == 'test':
            pipeline.run_quick_test()
        elif args.mode == 'collect':
            pipeline.collect_training_data()
        elif args.mode == 'preprocess':
            if args.data_file:
                pipeline.preprocess_data(args.data_file)
            else:
                logger.error("--data-file required for preprocess mode")
        elif args.mode == 'train':
            if args.data_file:
                preprocessed_data = {'output_directory': 'training_data'}
                pipeline.train_model(preprocessed_data)
            else:
                logger.error("--data-file required for train mode")
        elif args.mode == 'evaluate':
            if args.model_dir:
                pipeline.evaluate_model(args.model_dir)
            else:
                logger.error("--model-dir required for evaluate mode")
                
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    main()
