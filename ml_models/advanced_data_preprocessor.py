"""
Advanced Data Preprocessor for Energy Domain LLM
Processes academic papers, government documents, and news articles
"""

import json
import re
import os
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import nltk

# Try to import spacy, use fallback if not available
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spacy not available, using simplified text processing")

try:
    from transformers import AutoTokenizer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Warning: transformers not available, using basic tokenization")

import textstat
from datetime import datetime
import glob

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class AdvancedEnergyDataPreprocessor:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        # Initialize tokenizer if transformers is available
        if TRANSFORMERS_AVAILABLE:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
            except Exception as e:
                print(f"Warning: Could not load tokenizer, using basic tokenization: {e}")
                self.tokenizer = None
        else:
            self.tokenizer = None
        
        # Initialize spaCy for advanced NLP if available
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                print("⚠️ spaCy model not found. Using basic text processing...")
                # Try to download if spacy is available
                try:
                    os.system("python -m spacy download en_core_web_sm")
                    self.nlp = spacy.load("en_core_web_sm")
                except:
                    print("Could not download spaCy model, using fallback processing")
        
        # Energy domain specific terms and entities
        self.energy_terms = {
            'technologies': [
                'solar', 'photovoltaic', 'pv', 'wind', 'turbine', 'hydroelectric', 'hydro',
                'geothermal', 'biomass', 'nuclear', 'fusion', 'battery', 'storage', 'grid',
                'fuel cell', 'hydrogen', 'biofuel', 'renewable', 'clean energy', 'sustainable'
            ],
            'concepts': [
                'efficiency', 'capacity', 'generation', 'transmission', 'distribution',
                'smart grid', 'microgrid', 'energy transition', 'decarbonization',
                'electrification', 'carbon capture', 'emissions', 'sustainability'
            ],
            'metrics': [
                'kilowatt', 'megawatt', 'gigawatt', 'terawatt', 'kwh', 'mwh', 'gwh', 'twh',
                'btu', 'joule', 'calorie', 'therm', 'capacity factor', 'lcoe', 'efficiency',
                'co2', 'carbon', 'greenhouse gas', 'ghg'
            ]
        }
        
        self.max_sequence_length = 1024
        self.processed_data = []
        
    def load_training_data(self, data_path: str) -> Dict:
        """Load training data from JSON file"""
        print(f"📖 Loading training data from {data_path}")
        
        if data_path.endswith('.json'):
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            # Load from directory with multiple files
            data = {'academic_papers': [], 'government_content': [], 'news_articles': []}
            
            json_files = glob.glob(os.path.join(data_path, "*.json"))
            for file_path in json_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    if isinstance(file_data, dict):
                        for key in data.keys():
                            if key in file_data:
                                data[key].extend(file_data[key])
                    elif isinstance(file_data, list):
                        data['news_articles'].extend(file_data)
        
        print(f"✅ Loaded {sum(len(v) if isinstance(v, list) else 0 for v in data.values())} documents")
        return data
    
    def analyze_document_quality(self, text: str) -> Dict:
        """Analyze document quality and readability"""
        quality_metrics = {
            'length': len(text),
            'word_count': len(text.split()),
            'sentence_count': len(nltk.sent_tokenize(text)),
            'avg_sentence_length': 0,
            'flesch_reading_ease': 0,
            'flesch_kincaid_grade': 0,
            'energy_term_density': 0,
            'technical_complexity': 0
        }
        
        if quality_metrics['sentence_count'] > 0:
            quality_metrics['avg_sentence_length'] = quality_metrics['word_count'] / quality_metrics['sentence_count']
        
        # Readability scores
        try:
            quality_metrics['flesch_reading_ease'] = textstat.flesch_reading_ease(text)
            quality_metrics['flesch_kincaid_grade'] = textstat.flesch_kincaid_grade(text)
        except:
            pass
        
        # Energy domain relevance
        text_lower = text.lower()
        energy_term_count = 0
        for category in self.energy_terms.values():
            for term in category:
                energy_term_count += text_lower.count(term.lower())
        
        if quality_metrics['word_count'] > 0:
            quality_metrics['energy_term_density'] = energy_term_count / quality_metrics['word_count']
        
        # Technical complexity (based on named entities and technical terms)
        doc = self.nlp(text[:100000])  # Limit for performance
        technical_entities = ['ORG', 'PRODUCT', 'TECH', 'CHEMICAL']
        tech_count = sum(1 for ent in doc.ents if ent.label_ in technical_entities)
        quality_metrics['technical_complexity'] = tech_count / len(doc.ents) if doc.ents else 0
        
        return quality_metrics
    
    def extract_energy_entities(self, text: str) -> Dict:
        """Extract energy-specific entities and concepts"""
        doc = self.nlp(text[:100000])  # Limit for performance
        
        entities = {
            'technologies': [],
            'companies': [],
            'locations': [],
            'metrics': [],
            'concepts': []
        }
        
        # Extract named entities
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                entities['companies'].append(ent.text)
            elif ent.label_ in ['GPE', 'LOC']:
                entities['locations'].append(ent.text)
            elif ent.label_ in ['QUANTITY', 'CARDINAL']:
                entities['metrics'].append(ent.text)
        
        # Extract energy-specific terms
        text_lower = text.lower()
        for tech in self.energy_terms['technologies']:
            if tech in text_lower:
                entities['technologies'].append(tech)
        
        for concept in self.energy_terms['concepts']:
            if concept in text_lower:
                entities['concepts'].append(concept)
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def clean_and_normalize_text(self, text: str) -> str:
        """Clean and normalize text for training"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Normalize quotes
        text = re.sub(r'[""''`]', '"', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[.]{3,}', '...', text)
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-"\'/]', '', text)
        
        # Remove very short or very long paragraphs
        paragraphs = text.split('\n')
        filtered_paragraphs = []
        for para in paragraphs:
            para = para.strip()
            if 20 <= len(para) <= 2000:  # Keep reasonable paragraph lengths
                filtered_paragraphs.append(para)
        
        text = '\n'.join(filtered_paragraphs)
        
        return text.strip()
    
    def create_training_sequences(self, text: str, max_length: int = None) -> List[str]:
        """Create training sequences with appropriate length"""
        if max_length is None:
            max_length = self.max_sequence_length
        
        # Split into sentences
        sentences = nltk.sent_tokenize(text)
        
        sequences = []
        current_sequence = ""
        
        for sentence in sentences:
            # Check if adding this sentence would exceed max length
            potential_sequence = current_sequence + " " + sentence if current_sequence else sentence
            
            # Tokenize to check actual token count
            tokens = self.tokenizer.encode(potential_sequence, add_special_tokens=True)
            
            if len(tokens) <= max_length:
                current_sequence = potential_sequence
            else:
                # Save current sequence if it's substantial
                if len(current_sequence.split()) >= 20:  # Minimum 20 words
                    sequences.append(current_sequence.strip())
                
                # Start new sequence with current sentence
                current_sequence = sentence
        
        # Add the last sequence
        if current_sequence and len(current_sequence.split()) >= 20:
            sequences.append(current_sequence.strip())
        
        return sequences
    
    def process_academic_papers(self, papers: List[Dict]) -> List[Dict]:
        """Process academic papers with special handling"""
        processed_papers = []
        
        print("📚 Processing academic papers...")
        
        for paper in papers:
            try:
                # Combine title, abstract, and full text
                content_parts = []
                
                if paper.get('title'):
                    content_parts.append(f"Title: {paper['title']}")
                
                if paper.get('abstract'):
                    content_parts.append(f"Abstract: {paper['abstract']}")
                
                if paper.get('full_text'):
                    content_parts.append(f"Content: {paper['full_text']}")
                
                full_text = '\n\n'.join(content_parts)
                
                # Clean the text
                cleaned_text = self.clean_and_normalize_text(full_text)
                
                if len(cleaned_text.split()) < 50:  # Skip very short papers
                    continue
                
                # Analyze quality
                quality = self.analyze_document_quality(cleaned_text)
                
                # Extract entities
                entities = self.extract_energy_entities(cleaned_text)
                
                # Create training sequences
                sequences = self.create_training_sequences(cleaned_text)
                
                processed_paper = {
                    'original_data': paper,
                    'processed_text': cleaned_text,
                    'sequences': sequences,
                    'quality_metrics': quality,
                    'entities': entities,
                    'document_type': 'academic',
                    'priority_score': self.calculate_priority_score(quality, entities, 'academic')
                }
                
                processed_papers.append(processed_paper)
                
            except Exception as e:
                print(f"❌ Error processing paper: {e}")
                continue
        
        print(f"✅ Processed {len(processed_papers)} academic papers")
        return processed_papers
    
    def process_government_content(self, content_list: List[Dict]) -> List[Dict]:
        """Process government and institutional content"""
        processed_content = []
        
        print("🏛️ Processing government content...")
        
        for content in content_list:
            try:
                # Combine title and content
                content_parts = []
                
                if content.get('title'):
                    content_parts.append(f"Title: {content['title']}")
                
                if content.get('content'):
                    content_parts.append(content['content'])
                
                full_text = '\n\n'.join(content_parts)
                
                # Clean the text
                cleaned_text = self.clean_and_normalize_text(full_text)
                
                if len(cleaned_text.split()) < 30:  # Skip very short content
                    continue
                
                # Analyze quality
                quality = self.analyze_document_quality(cleaned_text)
                
                # Extract entities
                entities = self.extract_energy_entities(cleaned_text)
                
                # Create training sequences
                sequences = self.create_training_sequences(cleaned_text)
                
                processed_item = {
                    'original_data': content,
                    'processed_text': cleaned_text,
                    'sequences': sequences,
                    'quality_metrics': quality,
                    'entities': entities,
                    'document_type': 'government',
                    'priority_score': self.calculate_priority_score(quality, entities, 'government')
                }
                
                processed_content.append(processed_item)
                
            except Exception as e:
                print(f"❌ Error processing government content: {e}")
                continue
        
        print(f"✅ Processed {len(processed_content)} government documents")
        return processed_content
    
    def process_news_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process news articles"""
        processed_articles = []
        
        print("📰 Processing news articles...")
        
        for article in articles:
            try:
                # Combine title and content
                content_parts = []
                
                if article.get('title'):
                    content_parts.append(f"Title: {article['title']}")
                
                if article.get('content'):
                    content_parts.append(article['content'])
                
                full_text = '\n\n'.join(content_parts)
                
                # Clean the text
                cleaned_text = self.clean_and_normalize_text(full_text)
                
                if len(cleaned_text.split()) < 20:  # Skip very short articles
                    continue
                
                # Analyze quality
                quality = self.analyze_document_quality(cleaned_text)
                
                # Extract entities
                entities = self.extract_energy_entities(cleaned_text)
                
                # Create training sequences
                sequences = self.create_training_sequences(cleaned_text)
                
                processed_article = {
                    'original_data': article,
                    'processed_text': cleaned_text,
                    'sequences': sequences,
                    'quality_metrics': quality,
                    'entities': entities,
                    'document_type': 'news',
                    'priority_score': self.calculate_priority_score(quality, entities, 'news')
                }
                
                processed_articles.append(processed_article)
                
            except Exception as e:
                print(f"❌ Error processing news article: {e}")
                continue
        
        print(f"✅ Processed {len(processed_articles)} news articles")
        return processed_articles
    
    def calculate_priority_score(self, quality: Dict, entities: Dict, doc_type: str) -> float:
        """Calculate priority score for training data selection"""
        score = 0.0
        
        # Base score from document type
        type_weights = {'academic': 1.0, 'government': 0.9, 'news': 0.7}
        score += type_weights.get(doc_type, 0.5)
        
        # Quality factors
        if quality['word_count'] >= 100:
            score += 0.3
        if quality['energy_term_density'] > 0.01:
            score += 0.4
        if quality['technical_complexity'] > 0.1:
            score += 0.2
        
        # Entity richness
        total_entities = sum(len(ents) for ents in entities.values())
        if total_entities > 5:
            score += 0.3
        
        # Readability (prefer moderately complex content)
        if 30 <= quality.get('flesch_kincaid_grade', 0) <= 80:
            score += 0.2
        
        return min(score, 3.0)  # Cap at 3.0
    
    def create_training_dataset(self, data: Dict, output_dir: str = "training_data") -> Dict:
        """Create comprehensive training dataset"""
        print("🚀 Creating training dataset...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Process all data types
        processed_data = {
            'academic_papers': self.process_academic_papers(data.get('academic_papers', [])),
            'government_content': self.process_government_content(data.get('government_content', [])),
            'news_articles': self.process_news_articles(data.get('news_articles', []))
        }
        
        # Combine all processed documents
        all_documents = []
        for doc_type, documents in processed_data.items():
            all_documents.extend(documents)
        
        # Sort by priority score
        all_documents.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Create different training splits
        training_splits = self.create_training_splits(all_documents)
        
        # Save processed data
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full processed dataset
        full_dataset_path = os.path.join(output_dir, f"processed_dataset_{timestamp}.json")
        with open(full_dataset_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        # Save training splits
        for split_name, split_data in training_splits.items():
            split_path = os.path.join(output_dir, f"{split_name}_{timestamp}.json")
            with open(split_path, 'w', encoding='utf-8') as f:
                json.dump(split_data, f, indent=2, ensure_ascii=False)
        
        # Create training corpus files
        self.create_training_corpus_files(all_documents, output_dir, timestamp)
        
        # Generate statistics
        stats = self.generate_dataset_statistics(processed_data, all_documents)
        
        stats_path = os.path.join(output_dir, f"dataset_stats_{timestamp}.json")
        with open(stats_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Training dataset created in {output_dir}")
        print(f"📊 Dataset statistics saved to {stats_path}")
        
        return {
            'processed_data': processed_data,
            'training_splits': training_splits,
            'statistics': stats,
            'output_directory': output_dir
        }
    
    def create_training_splits(self, documents: List[Dict]) -> Dict:
        """Create train/validation/test splits"""
        # Sort documents by priority score
        documents.sort(key=lambda x: x['priority_score'], reverse=True)
        
        total_docs = len(documents)
        train_size = int(total_docs * 0.8)
        val_size = int(total_docs * 0.1)
        
        splits = {
            'train': documents[:train_size],
            'validation': documents[train_size:train_size + val_size],
            'test': documents[train_size + val_size:]
        }
        
        return splits
    
    def create_training_corpus_files(self, documents: List[Dict], output_dir: str, timestamp: str):
        """Create training corpus files for different purposes"""
        
        # High-quality corpus (top 70% by priority score)
        high_quality_docs = documents[:int(len(documents) * 0.7)]
        
        # Create text files for training
        corpus_files = {
            'full_corpus': documents,
            'high_quality_corpus': high_quality_docs,
            'academic_only': [d for d in documents if d['document_type'] == 'academic'],
            'government_only': [d for d in documents if d['document_type'] == 'government'],
            'news_only': [d for d in documents if d['document_type'] == 'news']
        }
        
        for corpus_name, corpus_docs in corpus_files.items():
            # Create text file
            text_file_path = os.path.join(output_dir, f"{corpus_name}_{timestamp}.txt")
            with open(text_file_path, 'w', encoding='utf-8') as f:
                for doc in corpus_docs:
                    for sequence in doc['sequences']:
                        f.write(sequence + '\n\n---SEQUENCE_SEPARATOR---\n\n')
            
            # Create JSONL file for modern training frameworks
            jsonl_file_path = os.path.join(output_dir, f"{corpus_name}_{timestamp}.jsonl")
            with open(jsonl_file_path, 'w', encoding='utf-8') as f:
                for doc in corpus_docs:
                    for sequence in doc['sequences']:
                        json_line = {
                            'text': sequence,
                            'document_type': doc['document_type'],
                            'priority_score': doc['priority_score'],
                            'metadata': {
                                'word_count': len(sequence.split()),
                                'energy_term_density': doc['quality_metrics']['energy_term_density']
                            }
                        }
                        f.write(json.dumps(json_line, ensure_ascii=False) + '\n')
    
    def generate_dataset_statistics(self, processed_data: Dict, all_documents: List[Dict]) -> Dict:
        """Generate comprehensive dataset statistics"""
        stats = {
            'overview': {
                'total_documents': len(all_documents),
                'total_sequences': sum(len(doc['sequences']) for doc in all_documents),
                'total_words': sum(doc['quality_metrics']['word_count'] for doc in all_documents),
                'average_priority_score': np.mean([doc['priority_score'] for doc in all_documents])
            },
            'by_document_type': {},
            'quality_distribution': {},
            'entity_analysis': {},
            'readability_stats': {}
        }
        
        # Statistics by document type
        for doc_type in ['academic', 'government', 'news']:
            type_docs = [d for d in all_documents if d['document_type'] == doc_type]
            if type_docs:
                stats['by_document_type'][doc_type] = {
                    'count': len(type_docs),
                    'avg_word_count': np.mean([d['quality_metrics']['word_count'] for d in type_docs]),
                    'avg_priority_score': np.mean([d['priority_score'] for d in type_docs]),
                    'avg_energy_density': np.mean([d['quality_metrics']['energy_term_density'] for d in type_docs])
                }
        
        # Quality distribution
        priority_scores = [doc['priority_score'] for doc in all_documents]
        stats['quality_distribution'] = {
            'min_priority': float(np.min(priority_scores)),
            'max_priority': float(np.max(priority_scores)),
            'mean_priority': float(np.mean(priority_scores)),
            'std_priority': float(np.std(priority_scores))
        }
        
        # Entity analysis
        all_entities = {'technologies': [], 'companies': [], 'locations': [], 'concepts': []}
        for doc in all_documents:
            for entity_type, entities in doc['entities'].items():
                all_entities[entity_type].extend(entities)
        
        stats['entity_analysis'] = {
            entity_type: {
                'total_count': len(entities),
                'unique_count': len(set(entities)),
                'most_common': pd.Series(entities).value_counts().head(10).to_dict() if entities else {}
            }
            for entity_type, entities in all_entities.items()
        }
        
        # Readability statistics
        readability_scores = [doc['quality_metrics']['flesch_reading_ease'] for doc in all_documents if doc['quality_metrics']['flesch_reading_ease'] > 0]
        if readability_scores:
            stats['readability_stats'] = {
                'mean_flesch_ease': float(np.mean(readability_scores)),
                'std_flesch_ease': float(np.std(readability_scores)),
                'min_flesch_ease': float(np.min(readability_scores)),
                'max_flesch_ease': float(np.max(readability_scores))
            }
        
        return stats

if __name__ == "__main__":
    # Example usage
    preprocessor = AdvancedEnergyDataPreprocessor()
    
    # Load data (replace with actual data file)
    data_files = glob.glob("training_data/energy_training_data_*.json")
    if data_files:
        latest_file = max(data_files)
        print(f"📖 Loading data from {latest_file}")
        
        data = preprocessor.load_training_data(latest_file)
        
        # Create training dataset
        result = preprocessor.create_training_dataset(data)
        
        print("🎉 Data preprocessing complete!")
        print(f"📊 Total documents: {result['statistics']['overview']['total_documents']}")
        print(f"📝 Total training sequences: {result['statistics']['overview']['total_sequences']}")
        print(f"💬 Total words: {result['statistics']['overview']['total_words']:,}")
        
    else:
        print("❌ No training data files found. Run the data collector first.")
    
    def process_article(self, article: Dict) -> Dict:
        """Process a single article for training"""
        try:
            # Extract text content
            text = article.get('content', '') or article.get('abstract', '') or article.get('summary', '')
            
            if not text or len(text) < 100:  # Minimum text length
                return None
            
            # Analyze quality
            quality = self.analyze_document_quality(text)
            
            # Create processed article
            processed = {
                'title': article.get('title', ''),
                'content': text,
                'source': article.get('source', 'unknown'),
                'url': article.get('url', ''),
                'date': article.get('date', ''),
                'quality_score': quality.get('overall_score', 0),
                'energy_relevance': quality.get('energy_specific_score', 0),
                'word_count': len(text.split())
            }
            
            return processed
            
        except Exception as e:
            print(f"⚠️ Error processing article: {e}")
            return None
    
    def is_suitable_for_training(self, processed_article: Dict) -> bool:
        """Check if an article is suitable for training"""
        if not processed_article:
            return False
        
        # Minimum quality thresholds
        min_quality = 0.3
        min_energy_relevance = 0.2
        min_words = 50
        
        quality = processed_article.get('quality_score', 0)
        relevance = processed_article.get('energy_relevance', 0)
        word_count = processed_article.get('word_count', 0)
        
        return (quality >= min_quality and 
                relevance >= min_energy_relevance and 
                word_count >= min_words)
