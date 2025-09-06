# Energy LLM - Custom Language Model for Energy News

This directory contains a complete machine learning pipeline for training a custom Large Language Model (LLM) specifically for energy industry content. The model is designed to replace external APIs like OpenAI for generating high-quality energy blog posts.

## 🎯 Overview

The Energy LLM system provides:

- **Custom Language Model**: PyTorch-based transformer architecture trained on energy news
- **Domain Expertise**: Specialized vocabulary and understanding of energy industry terminology
- **Blog Generation**: High-quality, SEO-optimized blog post generation
- **Cost Efficiency**: No external API costs once trained
- **Privacy**: All processing happens locally

## 🏗️ Architecture

### Model Components

1. **EnergyLanguageModel** (`energy_llm.py`)
   - Custom transformer architecture with energy-specific embeddings
   - Multi-head attention with domain specialization
   - Configurable model sizes (small, base, large)

2. **Data Collection** (`data_collector.py`)
   - Automated news scraping from multiple energy sources
   - Content quality assessment and filtering
   - Deduplication and preprocessing

3. **Data Preprocessing** (`data_preprocessor.py`)
   - Text tokenization and encoding
   - Training/validation dataset preparation
   - Custom tokenizer training

4. **Training Pipeline** (`trainer.py`)
   - Complete training loop with mixed precision
   - Learning rate scheduling and optimization
   - Evaluation and checkpointing

5. **Inference Engine** (`inference.py`)
   - Easy-to-use interface for text generation
   - Multiple generation styles (analytical, creative, factual)
   - Blog post generation and analysis

## 🚀 Quick Start

### 1. Setup Dependencies

```bash
# Run the setup script to install all ML dependencies
python setup_ml.py
```

This will install:
- PyTorch (with CUDA support if available)
- Transformers library
- Datasets and tokenizers
- Training utilities (accelerate, wandb)
- Additional dependencies

### 2. Train Your Model

```bash
# Complete pipeline (data collection + training)
python ml_models/train_pipeline.py --stage all --model-size base --num-epochs 3

# Or run stages individually:
python ml_models/train_pipeline.py --stage collect    # Collect training data
python ml_models/train_pipeline.py --stage preprocess # Preprocess data
python ml_models/train_pipeline.py --stage train      # Train model
python ml_models/train_pipeline.py --stage test       # Test model
```

### 3. Use in Blog Generation

The trained model automatically integrates with the blog generation system:

```python
from src.blog_generator import BlogPostGenerator

# Will use custom LLM if available, fallback to OpenAI if not
generator = BlogPostGenerator(use_custom_llm=True)
```

## 📊 Model Configurations

### Small Model
- **Parameters**: ~125M
- **Training Time**: ~2-3 hours
- **Memory**: 4GB GPU
- **Use Case**: Fast inference, basic content

### Base Model (Recommended)
- **Parameters**: ~350M
- **Training Time**: ~6-8 hours
- **Memory**: 8GB GPU
- **Use Case**: Balanced performance and quality

### Large Model
- **Parameters**: ~770M
- **Training Time**: ~12-16 hours
- **Memory**: 16GB GPU
- **Use Case**: Highest quality output

## 🔧 Configuration

### Environment Variables

Create or update `.env` file:

```env
# Optional: OpenAI fallback
OPENAI_API_KEY=your_key_here

# Optional: Experiment tracking
WANDB_API_KEY=your_key_here

# ML pipeline paths
ENERGY_LLM_DATA_DIR=training_data/raw
ENERGY_LLM_PROCESSED_DIR=training_data/processed
ENERGY_LLM_MODEL_DIR=model_checkpoints
```

### Training Configuration

Modify `train_pipeline.py` arguments:

```bash
python ml_models/train_pipeline.py \
  --model-size base \
  --batch-size 8 \
  --learning-rate 2e-5 \
  --num-epochs 3 \
  --max-articles 5000 \
  --use-fp16 \
  --use-wandb
```

## 📁 Directory Structure

```
ml_models/
├── data_collector.py      # News data collection
├── data_preprocessor.py   # Data preprocessing
├── energy_llm.py         # Model architecture
├── trainer.py            # Training pipeline
├── inference.py          # Inference engine
├── train_pipeline.py     # Main pipeline script
└── README.md            # This file

training_data/
├── raw/                 # Raw scraped articles
└── processed/           # Tokenized training data

model_checkpoints/
├── best_model/          # Best performing model
├── final_model/         # Final trained model
└── checkpoint-*/        # Training checkpoints
```

## 🎮 Usage Examples

### Generate Text

```python
from ml_models.inference import EnergyLLMInference

# Load trained model
llm = EnergyLLMInference("model_checkpoints/best_model")

# Generate text
result = llm.generate_text(
    "The future of solar energy technology",
    style='analytical',
    energy_context='technology_review'
)
print(result)
```

### Generate Blog Post

```python
# Generate complete blog post
blog_post = llm.generate_blog_post(
    title="Renewable Energy Investment Trends 2024",
    key_points=[
        "Solar power cost reductions",
        "Wind energy capacity growth",
        "Battery storage innovations"
    ],
    style='analytical'
)

print(blog_post['full_text'])
```

### Analyze News

```python
# Analyze energy news
analysis = llm.analyze_energy_news(
    news_text="Solar panel efficiency reaches new record...",
    analysis_type='comprehensive'
)

print(analysis['analysis'])
```

## 📈 Performance Monitoring

### Training Metrics

The training pipeline provides:
- Loss curves and perplexity
- Learning rate scheduling
- Gradient norms
- Sample text generation

### Inference Performance

Monitor:
- Generation speed (tokens/second)
- Memory usage
- Output quality scores

### Weights & Biases Integration

Enable experiment tracking:

```bash
pip install wandb
wandb login

python ml_models/train_pipeline.py --use-wandb
```

## 🔧 Troubleshooting

### Memory Issues

**GPU Out of Memory:**
```bash
# Reduce batch size
python ml_models/train_pipeline.py --batch-size 4

# Use gradient accumulation
# (Effective batch size = batch_size * accumulation_steps)
```

**CPU Training:**
```python
# Force CPU training
device = 'cpu'
```

### Training Issues

**Slow Convergence:**
- Increase learning rate: `--learning-rate 5e-5`
- More training data: `--max-articles 10000`
- Longer training: `--num-epochs 5`

**Poor Quality Output:**
- Use larger model: `--model-size large`
- More diverse training data
- Adjust generation parameters

### Data Collection Issues

**Insufficient Data:**
```bash
# Increase article limit
python ml_models/train_pipeline.py --max-articles 10000

# Add more news sources in data_collector.py
```

**Content Quality:**
- Adjust quality thresholds in `data_collector.py`
- Add more content filters
- Manual curation of training data

## 🎯 Advanced Usage

### Custom Training Data

Add your own energy content:

```python
# In data_collector.py
def add_custom_content(self, content_list):
    for content in content_list:
        self.articles.append({
            'title': content['title'],
            'content': content['text'],
            'source': 'custom',
            'quality_score': 0.9
        })
```

### Fine-tuning

Fine-tune on specific energy topics:

```python
# Collect domain-specific data
collector = EnergyDataCollector()
collector.focus_keywords = ['solar power', 'photovoltaic']
```

### Model Deployment

Deploy for production:

```python
# Optimize for inference
model.eval()
model = torch.jit.script(model)  # TorchScript
```

## 🤝 Integration

### With Blog Generator

The custom LLM automatically integrates with the blog generation system:

```python
# In src/blog_generator.py
generator = BlogPostGenerator(use_custom_llm=True)

# Will automatically use custom LLM if available
blog_post = generator.generate_blog_post(topic_data)
```

### With Web Application

Enable in Flask app:

```python
# In app.py
app = EnergyBlogApp(use_custom_llm=True)
```

## 📚 References

- [Transformers Documentation](https://huggingface.co/docs/transformers/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Energy Industry Resources](https://www.iea.org/)

## 🔬 Research

This model architecture is based on:
- Transformer architecture (Attention Is All You Need)
- BERT-style masked language modeling
- Domain-specific fine-tuning techniques
- Energy industry best practices

## 📄 License

This ML pipeline is part of the RenewablePowerInsight project and follows the same licensing terms.
