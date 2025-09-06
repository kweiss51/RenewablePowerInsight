"""
Data Preprocessing for Energy LLM Training
Prepares scraped energy news data for training our custom language model
"""

import json
import pandas as pd
import numpy as np
from pathlib import Path
import re
from typing import List, Dict, Tuple, Iterator
from dataclasses import dataclass
import logging
from datetime import datetime
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer
import torch
from torch.utils.data import Dataset, DataLoader
import pickle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ProcessedArticle:
    """Processed article for training"""
    text: str
    tokens: List[int]
    attention_mask: List[int]
    labels: List[int]
    metadata: Dict

class EnergyTextDataset(Dataset):
    """PyTorch Dataset for energy text data"""
    
    def __init__(self, texts: List[str], tokenizer, max_length: int = 512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': encoding['input_ids'].flatten()  # For autoregressive training
        }

class EnergyDataPreprocessor:
    def __init__(self, model_name: str = "gpt2"):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Add special tokens for energy domain
        special_tokens = {
            "additional_special_tokens": [
                "[ENERGY]", "[RENEWABLE]", "[SOLAR]", "[WIND]", "[BATTERY]",
                "[POLICY]", "[TECHNOLOGY]", "[MARKET]", "[RESEARCH]", "[CLIMATE]"
            ]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        
        # Set pad token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        self.raw_data_path = Path('training_data/raw')
        self.processed_data_path = Path('training_data/processed')
        self.processed_data_path.mkdir(parents=True, exist_ok=True)
        
        # Text processing patterns
        self.cleaning_patterns = [
            (r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ''),  # URLs
            (r'<[^>]+>', ''),  # HTML tags
            (r'\[.*?\]', ''),  # References like [1], [Source]
            (r'\n{3,}', '\n\n'),  # Multiple newlines
            (r'\s{3,}', ' '),  # Multiple spaces
            (r'[^\w\s\.\,\!\?\:\;\-\'\"]', ''),  # Non-standard characters
        ]
        
        # Energy domain patterns for enhancement
        self.energy_patterns = {
            'solar': r'\b(?:solar|photovoltaic|pv|solar panel|solar energy|solar power)\b',
            'wind': r'\b(?:wind|wind turbine|wind energy|wind power|offshore wind|onshore wind)\b',
            'battery': r'\b(?:battery|energy storage|lithium|battery storage|grid storage)\b',
            'ev': r'\b(?:electric vehicle|ev|electric car|tesla|charging station|ev charging)\b',
            'hydrogen': r'\b(?:hydrogen|fuel cell|green hydrogen|hydrogen energy|h2)\b',
            'policy': r'\b(?:policy|regulation|carbon tax|renewable standard|net metering)\b',
            'grid': r'\b(?:grid|smart grid|microgrid|transmission|distribution|utility)\b',
            'nuclear': r'\b(?:nuclear|nuclear power|nuclear energy|reactor|uranium)\b'
        }
    
    def load_raw_data(self) -> List[Dict]:
        """Load all raw data files"""
        all_articles = []
        
        for json_file in self.raw_data_path.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        all_articles.extend(data)
                    else:
                        all_articles.append(data)
                logger.info(f"Loaded {len(data)} articles from {json_file}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        logger.info(f"Total articles loaded: {len(all_articles)}")
        return all_articles
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Apply cleaning patterns
        for pattern, replacement in self.cleaning_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Ensure proper sentence endings
        text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)
        
        return text.strip()
    
    def enhance_text_with_domain_tokens(self, text: str) -> str:
        """Add domain-specific tokens to help the model understand energy concepts"""
        enhanced_text = text
        
        for domain, pattern in self.energy_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                domain_token = f"[{domain.upper()}]"
                # Add token at the beginning if this domain is prominent
                if not enhanced_text.startswith(domain_token):
                    enhanced_text = f"{domain_token} {enhanced_text}"
        
        return enhanced_text
    
    def create_training_examples(self, articles: List[Dict]) -> List[str]:
        """Create training examples in various formats"""
        training_examples = []
        
        for article in articles:
            title = article.get('title', '')
            content = article.get('content', '')
            
            if not title or not content:
                continue
            
            # Clean text
            clean_title = self.clean_text(title)
            clean_content = self.clean_text(content)
            
            if len(clean_content.split()) < 50:  # Skip very short articles
                continue
            
            # Format 1: Title + Content
            full_text = f"{clean_title}. {clean_content}"
            enhanced_text = self.enhance_text_with_domain_tokens(full_text)
            training_examples.append(enhanced_text)
            
            # Format 2: Question-Answer style (for instruction tuning)
            qa_text = f"Question: What are the latest developments in {clean_title.lower()}? Answer: {clean_content}"
            training_examples.append(qa_text)
            
            # Format 3: Summary style
            if len(clean_content.split()) > 200:
                summary_text = f"Summary: {clean_title}. Details: {clean_content}"
                training_examples.append(summary_text)
            
            # Format 4: Blog post style
            blog_text = f"Energy News Update: {clean_title}\n\n{clean_content}\n\nThis development in the energy sector shows the ongoing transition towards sustainable technologies."
            training_examples.append(blog_text)
        
        logger.info(f"Created {len(training_examples)} training examples")
        return training_examples
    
    def split_data(self, texts: List[str], test_size: float = 0.1, val_size: float = 0.1) -> Tuple[List[str], List[str], List[str]]:
        """Split data into train, validation, and test sets"""
        # First split: train + val, test
        train_val, test = train_test_split(texts, test_size=test_size, random_state=42)
        
        # Second split: train, val
        val_size_adjusted = val_size / (1 - test_size)
        train, val = train_test_split(train_val, test_size=val_size_adjusted, random_state=42)
        
        logger.info(f"Data split - Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
        return train, val, test
    
    def tokenize_data(self, texts: List[str], max_length: int = 512) -> List[Dict]:
        """Tokenize text data"""
        tokenized_data = []
        
        for text in texts:
            encoding = self.tokenizer(
                text,
                truncation=True,
                padding='max_length',
                max_length=max_length,
                return_tensors='pt'
            )
            
            tokenized_data.append({
                'input_ids': encoding['input_ids'].squeeze().tolist(),
                'attention_mask': encoding['attention_mask'].squeeze().tolist(),
                'text': text
            })
        
        return tokenized_data
    
    def create_datasets(self, train_texts: List[str], val_texts: List[str], test_texts: List[str], max_length: int = 512):
        """Create PyTorch datasets"""
        train_dataset = EnergyTextDataset(train_texts, self.tokenizer, max_length)
        val_dataset = EnergyTextDataset(val_texts, self.tokenizer, max_length)
        test_dataset = EnergyTextDataset(test_texts, self.tokenizer, max_length)
        
        return train_dataset, val_dataset, test_dataset
    
    def save_processed_data(self, train_data, val_data, test_data, tokenizer_info: Dict):
        """Save processed data for training"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save datasets
        torch.save(train_data, self.processed_data_path / f"train_dataset_{timestamp}.pt")
        torch.save(val_data, self.processed_data_path / f"val_dataset_{timestamp}.pt")
        torch.save(test_data, self.processed_data_path / f"test_dataset_{timestamp}.pt")
        
        # Save tokenizer
        self.tokenizer.save_pretrained(self.processed_data_path / f"tokenizer_{timestamp}")
        
        # Save metadata
        metadata = {
            'timestamp': timestamp,
            'model_name': self.model_name,
            'vocab_size': self.tokenizer.vocab_size,
            'train_size': len(train_data),
            'val_size': len(val_data),
            'test_size': len(test_data),
            'special_tokens': list(self.tokenizer.additional_special_tokens),
            **tokenizer_info
        }
        
        with open(self.processed_data_path / f"metadata_{timestamp}.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved processed data with timestamp: {timestamp}")
        return timestamp
    
    def analyze_data_statistics(self, texts: List[str]) -> Dict:
        """Analyze dataset statistics"""
        word_counts = [len(text.split()) for text in texts]
        char_counts = [len(text) for text in texts]
        
        # Energy domain analysis
        domain_counts = {}
        for domain, pattern in self.energy_patterns.items():
            count = sum(1 for text in texts if re.search(pattern, text, re.IGNORECASE))
            domain_counts[domain] = count
        
        stats = {
            'total_examples': len(texts),
            'word_statistics': {
                'mean': np.mean(word_counts),
                'median': np.median(word_counts),
                'std': np.std(word_counts),
                'min': np.min(word_counts),
                'max': np.max(word_counts)
            },
            'char_statistics': {
                'mean': np.mean(char_counts),
                'median': np.median(char_counts),
                'std': np.std(char_counts),
                'min': np.min(char_counts),
                'max': np.max(char_counts)
            },
            'domain_coverage': domain_counts,
            'estimated_tokens': sum(word_counts) * 1.3  # Rough estimate
        }
        
        return stats
    
    def run_preprocessing(self, max_length: int = 512):
        """Run complete preprocessing pipeline"""
        logger.info("🔄 Starting data preprocessing for Energy LLM...")
        
        # Load raw data
        articles = self.load_raw_data()
        if not articles:
            logger.error("No raw data found. Run data collection first.")
            return None
        
        # Create training examples
        training_texts = self.create_training_examples(articles)
        
        # Analyze statistics
        stats = self.analyze_data_statistics(training_texts)
        logger.info(f"📊 Dataset statistics: {stats['total_examples']} examples, avg {stats['word_statistics']['mean']:.1f} words")
        
        # Split data
        train_texts, val_texts, test_texts = self.split_data(training_texts)
        
        # Create datasets
        train_dataset, val_dataset, test_dataset = self.create_datasets(
            train_texts, val_texts, test_texts, max_length
        )
        
        # Save processed data
        timestamp = self.save_processed_data(
            train_dataset, val_dataset, test_dataset, 
            {'max_length': max_length, 'statistics': stats}
        )
        
        logger.info(f"✅ Preprocessing complete! Data saved with timestamp: {timestamp}")
        
        return {
            'timestamp': timestamp,
            'train_dataset': train_dataset,
            'val_dataset': val_dataset,
            'test_dataset': test_dataset,
            'tokenizer': self.tokenizer,
            'statistics': stats
        }

if __name__ == "__main__":
    preprocessor = EnergyDataPreprocessor()
    result = preprocessor.run_preprocessing()
    
    if result:
        print(f"🎉 Preprocessing successful!")
        print(f"📊 Train examples: {len(result['train_dataset'])}")
        print(f"📊 Val examples: {len(result['val_dataset'])}")
        print(f"📊 Test examples: {len(result['test_dataset'])}")
        print(f"🔤 Vocabulary size: {result['tokenizer'].vocab_size}")
    else:
        print("❌ Preprocessing failed. Check logs for details.")
