"""
Energy LLM Training Module
Comprehensive training system for the custom Energy Language Model
"""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import LinearLR, CosineAnnealingLR
import numpy as np
import json
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import wandb
from tqdm import tqdm
import time
import os

from energy_llm import EnergyLanguageModel, EnergyLLMConfig, create_energy_llm
from data_preprocessor import EnergyDataPreprocessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TrainingConfig:
    """Training configuration"""
    # Model settings
    model_size: str = 'base'
    max_sequence_length: int = 512
    
    # Training hyperparameters
    batch_size: int = 8
    learning_rate: float = 2e-5
    num_epochs: int = 3
    warmup_steps: int = 1000
    max_grad_norm: float = 1.0
    weight_decay: float = 0.01
    
    # Optimization
    optimizer: str = 'adamw'
    scheduler: str = 'linear'
    accumulation_steps: int = 4
    
    # Evaluation
    eval_steps: int = 500
    save_steps: int = 1000
    logging_steps: int = 100
    
    # Mixed precision
    use_fp16: bool = True
    
    # Checkpointing
    save_total_limit: int = 3
    
    # Monitoring
    use_wandb: bool = True
    wandb_project: str = 'energy-llm'
    
    # Data
    train_data_path: str = 'training_data/processed'
    output_dir: str = 'model_checkpoints'
    
    def to_dict(self):
        return asdict(self)

class EnergyLLMTrainer:
    """Trainer for Energy Language Model"""
    
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
        
        # Setup directories
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize tracking
        self.global_step = 0
        self.epoch = 0
        self.best_eval_loss = float('inf')
        
        # Training history
        self.training_history = {
            'train_loss': [],
            'eval_loss': [],
            'learning_rate': [],
            'steps': [],
            'epochs': []
        }
        
        # Initialize wandb if enabled
        if config.use_wandb:
            wandb.init(
                project=config.wandb_project,
                config=config.to_dict(),
                name=f"energy-llm-{config.model_size}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
    
    def load_data(self):
        """Load preprocessed training data"""
        logger.info("📚 Loading training data...")
        
        # Find latest processed data
        data_path = Path(self.config.train_data_path)
        train_files = list(data_path.glob("train_dataset_*.pt"))
        val_files = list(data_path.glob("val_dataset_*.pt"))
        
        if not train_files or not val_files:
            logger.error("No processed training data found. Run preprocessing first.")
            return None, None, None
        
        # Load latest files
        latest_train = max(train_files, key=os.path.getctime)
        latest_val = max(val_files, key=os.path.getctime)
        
        # Extract timestamp from filename
        timestamp = latest_train.stem.split('_')[-1]
        tokenizer_path = data_path / f"tokenizer_{timestamp}"
        
        logger.info(f"Loading data from timestamp: {timestamp}")
        
        # Load datasets
        train_dataset = torch.load(latest_train)
        val_dataset = torch.load(latest_val)
        
        # Load tokenizer
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
        
        logger.info(f"Loaded {len(train_dataset)} training examples, {len(val_dataset)} validation examples")
        
        return train_dataset, val_dataset, tokenizer
    
    def create_model(self, tokenizer):
        """Create the Energy LLM model"""
        logger.info(f"🧠 Creating {self.config.model_size} Energy LLM...")
        
        # Create model with vocabulary size from tokenizer
        model = create_energy_llm(
            model_size=self.config.model_size,
            vocab_size=len(tokenizer)
        )
        
        # Move to device
        model = model.to(self.device)
        
        # Enable mixed precision if requested
        if self.config.use_fp16:
            model = model.half()
        
        size_info = model.get_model_size()
        logger.info(f"Model created with {size_info['total_parameters']:,} parameters")
        
        return model
    
    def create_optimizer_and_scheduler(self, model, num_training_steps):
        """Create optimizer and learning rate scheduler"""
        # Create optimizer
        no_decay = ['bias', 'LayerNorm.weight']
        optimizer_grouped_parameters = [
            {
                'params': [p for n, p in model.named_parameters() if not any(nd in n for nd in no_decay)],
                'weight_decay': self.config.weight_decay
            },
            {
                'params': [p for n, p in model.named_parameters() if any(nd in n for nd in no_decay)],
                'weight_decay': 0.0
            }
        ]
        
        optimizer = AdamW(
            optimizer_grouped_parameters,
            lr=self.config.learning_rate,
            eps=1e-8
        )
        
        # Create scheduler
        if self.config.scheduler == 'linear':
            scheduler = LinearLR(
                optimizer,
                start_factor=0.1,
                total_iters=self.config.warmup_steps
            )
        elif self.config.scheduler == 'cosine':
            scheduler = CosineAnnealingLR(
                optimizer,
                T_max=num_training_steps - self.config.warmup_steps,
                eta_min=self.config.learning_rate * 0.1
            )
        else:
            scheduler = None
        
        return optimizer, scheduler
    
    def compute_loss(self, model, batch):
        """Compute training loss"""
        input_ids = batch['input_ids'].to(self.device)
        attention_mask = batch['attention_mask'].to(self.device)
        labels = batch['labels'].to(self.device)
        
        outputs = model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            labels=labels
        )
        
        return outputs['loss']
    
    def evaluate(self, model, eval_dataloader):
        """Evaluate model on validation set"""
        model.eval()
        total_eval_loss = 0.0
        num_eval_steps = 0
        
        logger.info("🔍 Running evaluation...")
        
        with torch.no_grad():
            for batch in tqdm(eval_dataloader, desc="Evaluating"):
                loss = self.compute_loss(model, batch)
                total_eval_loss += loss.item()
                num_eval_steps += 1
        
        avg_eval_loss = total_eval_loss / num_eval_steps
        perplexity = torch.exp(torch.tensor(avg_eval_loss))
        
        logger.info(f"Eval loss: {avg_eval_loss:.4f}, Perplexity: {perplexity:.2f}")
        
        return avg_eval_loss, perplexity
    
    def save_checkpoint(self, model, tokenizer, optimizer, scheduler, is_best=False):
        """Save model checkpoint"""
        checkpoint_dir = self.output_dir / f"checkpoint-{self.global_step}"
        if is_best:
            checkpoint_dir = self.output_dir / "best_model"
        
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        model.save_pretrained(checkpoint_dir)
        
        # Save tokenizer
        tokenizer.save_pretrained(checkpoint_dir)
        
        # Save training state
        training_state = {
            'global_step': self.global_step,
            'epoch': self.epoch,
            'best_eval_loss': self.best_eval_loss,
            'training_history': self.training_history,
            'config': self.config.to_dict()
        }
        
        torch.save({
            'optimizer': optimizer.state_dict(),
            'scheduler': scheduler.state_dict() if scheduler else None,
            'training_state': training_state
        }, checkpoint_dir / "training_state.pt")
        
        logger.info(f"{'Best model' if is_best else 'Checkpoint'} saved to {checkpoint_dir}")
        
        # Clean up old checkpoints
        self.cleanup_checkpoints()
    
    def cleanup_checkpoints(self):
        """Remove old checkpoints to save space"""
        checkpoints = list(self.output_dir.glob("checkpoint-*"))
        checkpoints.sort(key=lambda x: int(x.name.split('-')[1]))
        
        while len(checkpoints) > self.config.save_total_limit:
            old_checkpoint = checkpoints.pop(0)
            logger.info(f"Removing old checkpoint: {old_checkpoint}")
            import shutil
            shutil.rmtree(old_checkpoint)
    
    def generate_sample_text(self, model, tokenizer, prompt="The future of renewable energy"):
        """Generate sample text for monitoring"""
        model.eval()
        
        # Tokenize prompt
        input_ids = tokenizer.encode(prompt, return_tensors='pt').to(self.device)
        
        # Generate
        with torch.no_grad():
            generated = model.generate(
                input_ids,
                max_length=100,
                temperature=0.8,
                do_sample=True,
                top_k=50,
                top_p=0.9
            )
        
        # Decode
        generated_text = tokenizer.decode(generated[0], skip_special_tokens=True)
        
        return generated_text
    
    def train(self):
        """Main training loop"""
        logger.info("🚀 Starting Energy LLM training...")
        
        # Load data
        train_dataset, val_dataset, tokenizer = self.load_data()
        if train_dataset is None:
            return None
        
        # Create data loaders
        train_dataloader = DataLoader(
            train_dataset,
            batch_size=self.config.batch_size,
            shuffle=True,
            num_workers=4
        )
        
        val_dataloader = DataLoader(
            val_dataset,
            batch_size=self.config.batch_size,
            shuffle=False,
            num_workers=4
        )
        
        # Create model
        model = self.create_model(tokenizer)
        
        # Calculate training steps
        num_training_steps = len(train_dataloader) * self.config.num_epochs
        
        # Create optimizer and scheduler
        optimizer, scheduler = self.create_optimizer_and_scheduler(model, num_training_steps)
        
        # Mixed precision scaler
        scaler = torch.cuda.amp.GradScaler() if self.config.use_fp16 and torch.cuda.is_available() else None
        
        # Training loop
        logger.info(f"Training for {self.config.num_epochs} epochs, {num_training_steps} total steps")
        
        for epoch in range(self.config.num_epochs):
            self.epoch = epoch
            model.train()
            
            total_loss = 0.0
            optimizer.zero_grad()
            
            progress_bar = tqdm(train_dataloader, desc=f"Epoch {epoch+1}/{self.config.num_epochs}")
            
            for step, batch in enumerate(progress_bar):
                start_time = time.time()
                
                # Forward pass
                if self.config.use_fp16 and scaler:
                    with torch.cuda.amp.autocast():
                        loss = self.compute_loss(model, batch)
                        loss = loss / self.config.accumulation_steps
                    
                    scaler.scale(loss).backward()
                else:
                    loss = self.compute_loss(model, batch)
                    loss = loss / self.config.accumulation_steps
                    loss.backward()
                
                total_loss += loss.item()
                
                # Gradient accumulation
                if (step + 1) % self.config.accumulation_steps == 0:
                    # Gradient clipping
                    if self.config.use_fp16 and scaler:
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(model.parameters(), self.config.max_grad_norm)
                        scaler.step(optimizer)
                        scaler.update()
                    else:
                        torch.nn.utils.clip_grad_norm_(model.parameters(), self.config.max_grad_norm)
                        optimizer.step()
                    
                    if scheduler:
                        scheduler.step()
                    
                    optimizer.zero_grad()
                    self.global_step += 1
                
                # Logging
                if self.global_step % self.config.logging_steps == 0:
                    avg_loss = total_loss / (step + 1)
                    lr = optimizer.param_groups[0]['lr']
                    steps_per_sec = 1.0 / (time.time() - start_time)
                    
                    progress_bar.set_postfix({
                        'loss': f'{avg_loss:.4f}',
                        'lr': f'{lr:.2e}',
                        'step/s': f'{steps_per_sec:.2f}'
                    })
                    
                    # Log to wandb
                    if self.config.use_wandb:
                        wandb.log({
                            'train_loss': avg_loss,
                            'learning_rate': lr,
                            'epoch': epoch,
                            'global_step': self.global_step
                        })
                    
                    # Update history
                    self.training_history['train_loss'].append(avg_loss)
                    self.training_history['learning_rate'].append(lr)
                    self.training_history['steps'].append(self.global_step)
                    self.training_history['epochs'].append(epoch)
                
                # Evaluation
                if self.global_step % self.config.eval_steps == 0:
                    eval_loss, perplexity = self.evaluate(model, val_dataloader)
                    
                    # Log evaluation metrics
                    if self.config.use_wandb:
                        wandb.log({
                            'eval_loss': eval_loss,
                            'perplexity': perplexity,
                            'global_step': self.global_step
                        })
                    
                    self.training_history['eval_loss'].append(eval_loss)
                    
                    # Save best model
                    if eval_loss < self.best_eval_loss:
                        self.best_eval_loss = eval_loss
                        self.save_checkpoint(model, tokenizer, optimizer, scheduler, is_best=True)
                        logger.info(f"🎉 New best model! Eval loss: {eval_loss:.4f}")
                    
                    # Generate sample text
                    sample_text = self.generate_sample_text(model, tokenizer)
                    logger.info(f"Sample generation: {sample_text[:100]}...")
                    
                    if self.config.use_wandb:
                        wandb.log({'sample_text': sample_text})
                    
                    model.train()
                
                # Save checkpoint
                if self.global_step % self.config.save_steps == 0:
                    self.save_checkpoint(model, tokenizer, optimizer, scheduler)
        
        # Final evaluation and save
        logger.info("🏁 Training complete! Running final evaluation...")
        final_eval_loss, final_perplexity = self.evaluate(model, val_dataloader)
        
        # Save final model
        final_dir = self.output_dir / "final_model"
        model.save_pretrained(final_dir)
        tokenizer.save_pretrained(final_dir)
        
        # Save training history
        with open(self.output_dir / "training_history.json", 'w') as f:
            json.dump(self.training_history, f, indent=2)
        
        logger.info(f"✅ Training finished!")
        logger.info(f"Final eval loss: {final_eval_loss:.4f}")
        logger.info(f"Final perplexity: {final_perplexity:.2f}")
        logger.info(f"Best eval loss: {self.best_eval_loss:.4f}")
        
        if self.config.use_wandb:
            wandb.log({
                'final_eval_loss': final_eval_loss,
                'final_perplexity': final_perplexity,
                'best_eval_loss': self.best_eval_loss
            })
            wandb.finish()
        
        return {
            'model': model,
            'tokenizer': tokenizer,
            'final_eval_loss': final_eval_loss,
            'best_eval_loss': self.best_eval_loss,
            'training_history': self.training_history
        }

def main():
    """Main training function"""
    # Configuration
    config = TrainingConfig(
        model_size='base',
        batch_size=4,  # Adjust based on GPU memory
        learning_rate=2e-5,
        num_epochs=3,
        use_fp16=True,
        use_wandb=False,  # Set to True if you have wandb account
    )
    
    # Create trainer
    trainer = EnergyLLMTrainer(config)
    
    # Start training
    result = trainer.train()
    
    if result:
        print("🎉 Training completed successfully!")
        print(f"Best validation loss: {result['best_eval_loss']:.4f}")
    else:
        print("❌ Training failed. Check logs for details.")

if __name__ == "__main__":
    main()
