"""
Advanced Training Pipeline for Energy Domain LLM
Supports both PyTorch and TensorFlow with distributed training
"""

import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
import torch.distributed as dist
import torch.multiprocessing as mp
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, AutoConfig,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling,
    get_linear_schedule_with_warmup
)
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import wandb
from pathlib import Path
import pickle
import time
import gc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnergyTextDataset(Dataset):
    """Custom dataset for energy domain text"""
    
    def __init__(self, 
                 data_path: str, 
                 tokenizer: AutoTokenizer,
                 max_length: int = 1024,
                 data_type: str = "all",
                 priority_threshold: float = 0.0):
        
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data_type = data_type
        self.priority_threshold = priority_threshold
        
        # Load and filter data
        self.sequences = self._load_and_filter_data(data_path)
        logger.info(f"Loaded {len(self.sequences)} training sequences")
    
    def _load_and_filter_data(self, data_path: str) -> List[str]:
        """Load and filter training data based on criteria"""
        sequences = []
        
        if data_path.endswith('.jsonl'):
            # Load JSONL format
            with open(data_path, 'r', encoding='utf-8') as f:
                for line in f:
                    data = json.loads(line)
                    
                    # Filter by data type
                    if self.data_type != "all" and data.get('document_type') != self.data_type:
                        continue
                    
                    # Filter by priority score
                    if data.get('priority_score', 0) < self.priority_threshold:
                        continue
                    
                    sequences.append(data['text'])
        
        elif data_path.endswith('.txt'):
            # Load plain text format
            with open(data_path, 'r', encoding='utf-8') as f:
                content = f.read()
                sequences = content.split('---SEQUENCE_SEPARATOR---')
                sequences = [seq.strip() for seq in sequences if seq.strip()]
        
        elif data_path.endswith('.json'):
            # Load processed JSON format
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract sequences from processed data
                for doc_type, documents in data.items():
                    if self.data_type != "all" and doc_type != self.data_type:
                        continue
                    
                    for doc in documents:
                        if doc.get('priority_score', 0) >= self.priority_threshold:
                            sequences.extend(doc.get('sequences', []))
        
        return sequences
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        text = self.sequences[idx]
        
        # Tokenize with truncation and padding
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # For causal language modeling, labels are the same as input_ids
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': input_ids.clone()
        }

class AdvancedEnergyTrainer:
    """Advanced trainer for energy domain LLM with multiple training strategies"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.setup_logging()
        
        # Initialize tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(config['base_model'])
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load or create model
        self.model = self._load_or_create_model()
        
        # Training components
        self.optimizer = None
        self.scheduler = None
        self.scaler = torch.cuda.amp.GradScaler() if config.get('mixed_precision', False) else None
        
        # Tracking
        self.training_stats = {
            'epoch': 0,
            'global_step': 0,
            'best_loss': float('inf'),
            'training_history': []
        }
        
        # Initialize Weights & Biases if configured
        if config.get('use_wandb', False):
            wandb.init(
                project=config.get('wandb_project', 'energy-llm'),
                name=config.get('run_name', f'energy-llm-{datetime.now().strftime("%Y%m%d-%H%M%S")}'),
                config=config
            )
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path(self.config.get('output_dir', 'model_checkpoints')) / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
    
    def _load_or_create_model(self) -> nn.Module:
        """Load existing model or create new one"""
        
        if self.config.get('resume_from_checkpoint'):
            logger.info(f"Loading model from checkpoint: {self.config['resume_from_checkpoint']}")
            model = AutoModelForCausalLM.from_pretrained(self.config['resume_from_checkpoint'])
        else:
            logger.info(f"Creating new model based on: {self.config['base_model']}")
            
            # Load configuration
            config = AutoConfig.from_pretrained(self.config['base_model'])
            
            # Modify configuration for energy domain
            if self.config.get('modify_architecture', False):
                config.vocab_size = len(self.tokenizer)
                config.max_position_embeddings = self.config.get('max_sequence_length', 1024)
                
                # Add energy-specific configuration
                config.energy_domain_layers = self.config.get('energy_domain_layers', 2)
                config.energy_vocab_size = self.config.get('energy_vocab_size', 5000)
            
            # Create model
            model = AutoModelForCausalLM.from_pretrained(
                self.config['base_model'],
                config=config,
                torch_dtype=torch.float16 if self.config.get('use_fp16', False) else torch.float32
            )
            
            # Resize token embeddings if needed
            model.resize_token_embeddings(len(self.tokenizer))
        
        # Move to device
        model = model.to(self.device)
        
        # Enable gradient checkpointing for memory efficiency
        if self.config.get('gradient_checkpointing', False):
            model.gradient_checkpointing_enable()
        
        return model
    
    def prepare_datasets(self) -> Dict[str, DataLoader]:
        """Prepare training and validation datasets"""
        datasets = {}
        
        # Training dataset
        train_data_path = self.config.get('train_data_path')
        if train_data_path:
            train_dataset = EnergyTextDataset(
                data_path=train_data_path,
                tokenizer=self.tokenizer,
                max_length=self.config.get('max_sequence_length', 1024),
                data_type=self.config.get('train_data_type', 'all'),
                priority_threshold=self.config.get('priority_threshold', 0.0)
            )
            
            train_loader = DataLoader(
                train_dataset,
                batch_size=self.config.get('train_batch_size', 4),
                shuffle=True,
                num_workers=self.config.get('num_workers', 4),
                pin_memory=True,
                drop_last=True
            )
            datasets['train'] = train_loader
        
        # Validation dataset
        val_data_path = self.config.get('val_data_path')
        if val_data_path:
            val_dataset = EnergyTextDataset(
                data_path=val_data_path,
                tokenizer=self.tokenizer,
                max_length=self.config.get('max_sequence_length', 1024),
                data_type=self.config.get('val_data_type', 'all'),
                priority_threshold=self.config.get('priority_threshold', 0.0)
            )
            
            val_loader = DataLoader(
                val_dataset,
                batch_size=self.config.get('eval_batch_size', 4),
                shuffle=False,
                num_workers=self.config.get('num_workers', 4),
                pin_memory=True
            )
            datasets['val'] = val_loader
        
        return datasets
    
    def setup_training_components(self, num_training_steps: int):
        """Setup optimizer and scheduler"""
        
        # Optimizer
        no_decay = ["bias", "LayerNorm.weight"]
        optimizer_grouped_parameters = [
            {
                "params": [p for n, p in self.model.named_parameters() if not any(nd in n for nd in no_decay)],
                "weight_decay": self.config.get('weight_decay', 0.01),
            },
            {
                "params": [p for n, p in self.model.named_parameters() if any(nd in n for nd in no_decay)],
                "weight_decay": 0.0,
            },
        ]
        
        if self.config.get('optimizer', 'adamw') == 'adamw':
            self.optimizer = optim.AdamW(
                optimizer_grouped_parameters,
                lr=self.config.get('learning_rate', 5e-5),
                betas=(0.9, 0.999),
                eps=1e-8
            )
        
        # Learning rate scheduler
        if self.config.get('use_scheduler', True):
            self.scheduler = get_linear_schedule_with_warmup(
                self.optimizer,
                num_warmup_steps=int(num_training_steps * self.config.get('warmup_ratio', 0.1)),
                num_training_steps=num_training_steps
            )
    
    def train_epoch(self, train_loader: DataLoader, epoch: int) -> Dict:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        num_batches = len(train_loader)
        
        epoch_stats = {
            'epoch': epoch,
            'train_loss': 0.0,
            'learning_rate': 0.0,
            'num_batches': num_batches
        }
        
        for batch_idx, batch in enumerate(train_loader):
            # Move batch to device
            batch = {k: v.to(self.device) for k, v in batch.items()}
            
            # Forward pass
            with torch.cuda.amp.autocast(enabled=self.scaler is not None):
                outputs = self.model(**batch)
                loss = outputs.loss
            
            # Backward pass
            if self.scaler:
                self.scaler.scale(loss).backward()
                
                if (batch_idx + 1) % self.config.get('gradient_accumulation_steps', 1) == 0:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.get('max_grad_norm', 1.0))
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.optimizer.zero_grad()
                    
                    if self.scheduler:
                        self.scheduler.step()
            else:
                loss.backward()
                
                if (batch_idx + 1) % self.config.get('gradient_accumulation_steps', 1) == 0:
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), self.config.get('max_grad_norm', 1.0))
                    self.optimizer.step()
                    self.optimizer.zero_grad()
                    
                    if self.scheduler:
                        self.scheduler.step()
            
            total_loss += loss.item()
            self.training_stats['global_step'] += 1
            
            # Logging
            if batch_idx % self.config.get('logging_steps', 100) == 0:
                current_lr = self.scheduler.get_last_lr()[0] if self.scheduler else self.config.get('learning_rate', 5e-5)
                logger.info(
                    f"Epoch {epoch}, Batch {batch_idx}/{num_batches}, "
                    f"Loss: {loss.item():.4f}, LR: {current_lr:.2e}"
                )
                
                if self.config.get('use_wandb', False):
                    wandb.log({
                        'train_loss_step': loss.item(),
                        'learning_rate': current_lr,
                        'global_step': self.training_stats['global_step']
                    })
            
            # Memory cleanup
            if batch_idx % 50 == 0:
                torch.cuda.empty_cache()
                gc.collect()
        
        epoch_stats['train_loss'] = total_loss / num_batches
        epoch_stats['learning_rate'] = self.scheduler.get_last_lr()[0] if self.scheduler else self.config.get('learning_rate', 5e-5)
        
        return epoch_stats
    
    def validate(self, val_loader: DataLoader) -> Dict:
        """Validate the model"""
        self.model.eval()
        total_loss = 0.0
        num_batches = len(val_loader)
        
        with torch.no_grad():
            for batch in val_loader:
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                with torch.cuda.amp.autocast(enabled=self.scaler is not None):
                    outputs = self.model(**batch)
                    loss = outputs.loss
                
                total_loss += loss.item()
        
        avg_loss = total_loss / num_batches
        
        return {
            'val_loss': avg_loss,
            'perplexity': torch.exp(torch.tensor(avg_loss)).item()
        }
    
    def save_checkpoint(self, epoch: int, val_stats: Dict = None):
        """Save model checkpoint"""
        output_dir = Path(self.config.get('output_dir', 'model_checkpoints'))
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model and tokenizer
        model_dir = output_dir / f"checkpoint-epoch-{epoch}"
        self.model.save_pretrained(model_dir)
        self.tokenizer.save_pretrained(model_dir)
        
        # Save training stats
        checkpoint_data = {
            'epoch': epoch,
            'global_step': self.training_stats['global_step'],
            'model_config': self.config,
            'training_stats': self.training_stats,
            'validation_stats': val_stats
        }
        
        with open(model_dir / 'training_checkpoint.json', 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        logger.info(f"Checkpoint saved to {model_dir}")
        
        # Save best model
        if val_stats and val_stats['val_loss'] < self.training_stats['best_loss']:
            self.training_stats['best_loss'] = val_stats['val_loss']
            
            best_model_dir = output_dir / "best_model"
            self.model.save_pretrained(best_model_dir)
            self.tokenizer.save_pretrained(best_model_dir)
            
            logger.info(f"New best model saved to {best_model_dir}")
    
    def train(self):
        """Main training loop"""
        logger.info("Starting training...")
        
        # Prepare datasets
        datasets = self.prepare_datasets()
        train_loader = datasets['train']
        val_loader = datasets.get('val')
        
        # Calculate total training steps
        num_epochs = self.config.get('num_epochs', 3)
        total_steps = len(train_loader) * num_epochs // self.config.get('gradient_accumulation_steps', 1)
        
        # Setup training components
        self.setup_training_components(total_steps)
        
        logger.info(f"Training for {num_epochs} epochs with {len(train_loader)} batches per epoch")
        logger.info(f"Total training steps: {total_steps}")
        
        # Training loop
        for epoch in range(num_epochs):
            logger.info(f"Starting epoch {epoch + 1}/{num_epochs}")
            
            # Train
            train_stats = self.train_epoch(train_loader, epoch + 1)
            
            # Validate
            val_stats = {}
            if val_loader:
                val_stats = self.validate(val_loader)
                logger.info(f"Validation - Loss: {val_stats['val_loss']:.4f}, Perplexity: {val_stats['perplexity']:.2f}")
            
            # Update training stats
            epoch_data = {**train_stats, **val_stats}
            self.training_stats['training_history'].append(epoch_data)
            self.training_stats['epoch'] = epoch + 1
            
            # Log to wandb
            if self.config.get('use_wandb', False):
                wandb.log(epoch_data)
            
            # Save checkpoint
            if (epoch + 1) % self.config.get('save_steps', 1) == 0:
                self.save_checkpoint(epoch + 1, val_stats)
            
            logger.info(f"Epoch {epoch + 1} completed - Train Loss: {train_stats['train_loss']:.4f}")
        
        logger.info("Training completed!")
        
        # Final save
        self.save_checkpoint(num_epochs, val_stats)
        
        if self.config.get('use_wandb', False):
            wandb.finish()

def create_training_config() -> Dict:
    """Create default training configuration"""
    return {
        # Model settings
        'base_model': 'microsoft/DialoGPT-medium',
        'max_sequence_length': 1024,
        'modify_architecture': False,
        
        # Data settings
        'train_data_path': 'training_data/high_quality_corpus_latest.jsonl',
        'val_data_path': 'training_data/validation_latest.jsonl',
        'train_data_type': 'all',  # 'all', 'academic', 'government', 'news'
        'val_data_type': 'all',
        'priority_threshold': 0.5,
        
        # Training settings
        'num_epochs': 3,
        'train_batch_size': 4,
        'eval_batch_size': 4,
        'gradient_accumulation_steps': 4,
        'learning_rate': 5e-5,
        'weight_decay': 0.01,
        'max_grad_norm': 1.0,
        'warmup_ratio': 0.1,
        
        # Optimization settings
        'optimizer': 'adamw',
        'use_scheduler': True,
        'mixed_precision': True,
        'gradient_checkpointing': True,
        'use_fp16': True,
        
        # Logging and saving
        'output_dir': 'model_checkpoints',
        'logging_steps': 50,
        'save_steps': 1,
        'use_wandb': False,
        'wandb_project': 'energy-llm',
        
        # System settings
        'num_workers': 4,
        'resume_from_checkpoint': None
    }

if __name__ == "__main__":
    # Create training configuration
    config = create_training_config()
    
    # Update config with command line arguments or environment variables
    config['use_wandb'] = os.getenv('USE_WANDB', 'false').lower() == 'true'
    config['output_dir'] = os.getenv('OUTPUT_DIR', config['output_dir'])
    
    # Create trainer
    trainer = AdvancedEnergyTrainer(config)
    
    # Start training
    trainer.train()
    
    def incremental_training(self, data_file: str, max_samples: int = None) -> Dict:
        """Perform incremental training with new data"""
        print(f"🏋️ Starting incremental training with {data_file}")
        
        try:
            # Load new data
            with open(data_file, 'r', encoding='utf-8') as f:
                new_data = json.load(f)
            
            if max_samples:
                new_data = new_data[:max_samples]
            
            # Create dataset from new data
            texts = []
            for item in new_data:
                if isinstance(item, dict) and 'content' in item:
                    texts.append(item['content'])
                elif isinstance(item, str):
                    texts.append(item)
            
            if not texts:
                return {'status': 'no_data', 'message': 'No valid training texts found'}
            
            # Tokenize texts
            tokenized = self.tokenizer(
                texts,
                truncation=True,
                padding=True,
                max_length=self.config['max_length'],
                return_tensors='pt'
            )
            
            # Create dataset
            dataset = EnergyTextDataset(tokenized['input_ids'], tokenized['attention_mask'])
            dataloader = DataLoader(
                dataset, 
                batch_size=self.config['batch_size'], 
                shuffle=True
            )
            
            # Set model to training mode
            self.model.train()
            
            # Training loop (single epoch for incremental)
            total_loss = 0
            num_batches = 0
            
            for batch in dataloader:
                input_ids = batch['input_ids'].to(self.device)
                attention_mask = batch['attention_mask'].to(self.device)
                
                # Forward pass
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=input_ids)
                loss = outputs.loss
                
                # Backward pass
                if self.scaler:
                    self.scaler.scale(loss).backward()
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                else:
                    loss.backward()
                    self.optimizer.step()
                
                self.optimizer.zero_grad()
                
                total_loss += loss.item()
                num_batches += 1
            
            avg_loss = total_loss / num_batches if num_batches > 0 else 0
            
            # Save updated model
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_path = f"model_checkpoints/incremental_update_{timestamp}"
            self.model.save_pretrained(model_path)
            self.tokenizer.save_pretrained(model_path)
            
            result = {
                'status': 'success',
                'samples_trained': len(texts),
                'average_loss': avg_loss,
                'model_saved': model_path
            }
            
            print(f"✅ Incremental training completed: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Incremental training failed: {e}")
            return {'status': 'failed', 'error': str(e)}
