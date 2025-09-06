# Energy Domain Large Language Model Training System

This directory contains a complete machine learning pipeline for training a custom Large Language Model (LLM) specialized in the energy domain. The system is designed to create an AI that understands renewable energy, energy policy, clean technology, and sustainable energy systems.

## 🚀 Quick Start

### Option 1: Complete Pipeline (Recommended)
```bash
# Run the complete training pipeline
python ml_models/pipeline_orchestrator.py --mode full

# Or run a quick test with minimal data
python ml_models/pipeline_orchestrator.py --mode test
```

### Option 2: Step-by-Step Execution
```bash
# 1. Collect training data
python ml_models/pipeline_orchestrator.py --mode collect

# 2. Preprocess the data
python ml_models/pipeline_orchestrator.py --mode preprocess --data-file training_data/energy_training_data_YYYYMMDD_HHMMSS.json

# 3. Train the model
python ml_models/pipeline_orchestrator.py --mode train

# 4. Evaluate the model
python ml_models/pipeline_orchestrator.py --mode evaluate --model-dir model_checkpoints
```

## 📁 System Architecture

### Core Components

#### 1. **advanced_data_collector.py**
- **Purpose**: Comprehensive data collection from academic and institutional sources
- **Features**:
  - Google Scholar academic paper collection
  - Government website scraping (DOE, EPA, EIA, NREL, IEA, IRENA)
  - 6-month energy news collection
  - Automated content extraction and cleaning
  - ML-ready data formatting

#### 2. **advanced_data_preprocessor.py**
- **Purpose**: Advanced text preprocessing for energy domain training
- **Features**:
  - Energy-specific entity extraction
  - Document quality analysis
  - Training sequence optimization
  - Priority scoring for data selection
  - Multiple output formats (JSON, JSONL, TXT)

#### 3. **advanced_trainer.py**
- **Purpose**: Production-ready training pipeline
- **Features**:
  - Mixed precision training
  - Gradient accumulation
  - Custom learning rate scheduling
  - Weights & Biases integration
  - Automatic checkpointing
  - Memory optimization

#### 4. **pipeline_orchestrator.py**
- **Purpose**: Complete ML pipeline automation
- **Features**:
  - End-to-end automation
  - Dependency management
  - Progress monitoring
  - Error handling and recovery
  - Multiple execution modes

## 🎯 Data Sources

### Academic Sources
- **Google Scholar**: Energy-related research papers
- **ArXiv**: Preprint papers on energy topics
- **Institutional repositories**: University and research center publications

### Government & Institutional Sources
- **U.S. Department of Energy (DOE)**: Policy documents and research reports
- **Environmental Protection Agency (EPA)**: Environmental and energy regulations
- **Energy Information Administration (EIA)**: Energy statistics and forecasts
- **National Renewable Energy Laboratory (NREL)**: Technical documentation
- **International Energy Agency (IEA)**: Global energy analysis
- **International Renewable Energy Agency (IRENA)**: Renewable energy insights

### News Sources
- Energy industry publications
- Renewable energy news websites
- Policy and regulatory updates
- Technology announcements

## 🔧 Configuration

### Default Configuration
The system includes comprehensive default configurations that can be customized:

```python
{
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
    'training': {
        'base_model': 'microsoft/DialoGPT-medium',
        'num_epochs': 3,
        'learning_rate': 5e-5,
        'mixed_precision': True
    }
}
```

### Custom Configuration
Create a custom configuration file:

```bash
python ml_models/pipeline_orchestrator.py --config my_config.json --mode full
```

## 📊 Output Structure

### Training Data
```
training_data/
├── energy_training_data_YYYYMMDD_HHMMSS.json     # Raw collected data
├── processed_dataset_YYYYMMDD_HHMMSS.json        # Processed data
├── high_quality_corpus_YYYYMMDD_HHMMSS.jsonl     # High-quality training data
├── train_YYYYMMDD_HHMMSS.json                    # Training split
├── validation_YYYYMMDD_HHMMSS.json               # Validation split
├── test_YYYYMMDD_HHMMSS.json                     # Test split
└── dataset_stats_YYYYMMDD_HHMMSS.json           # Dataset statistics
```

### Model Outputs
```
model_checkpoints/
├── best_model/                                   # Best performing model
│   ├── config.json
│   ├── pytorch_model.bin
│   └── tokenizer.json
├── checkpoint-epoch-1/                          # Epoch checkpoints
├── checkpoint-epoch-2/
└── logs/                                        # Training logs
```

### Results
```
results/
├── evaluation_results_YYYYMMDD_HHMMSS.json     # Model evaluation results
├── pipeline_summary.json                        # Complete pipeline summary
└── training_metrics.json                        # Training performance metrics
```

## 🔍 Data Quality & Filtering

### Quality Metrics
- **Energy Term Density**: Percentage of energy-related terms in document
- **Technical Complexity**: Ratio of technical entities to total entities
- **Readability Scores**: Flesch reading ease and grade level
- **Document Length**: Word count and sentence structure analysis

### Priority Scoring
Documents are scored based on:
- Source credibility (Academic > Government > News)
- Energy domain relevance
- Technical depth
- Content quality metrics

### Training Data Selection
- Top 70% of documents by priority score for high-quality corpus
- Minimum energy term density threshold
- Balanced representation across document types
- Optimal sequence length for training efficiency

## 🚀 Advanced Features

### Distributed Training
```bash
# Multi-GPU training
CUDA_VISIBLE_DEVICES=0,1,2,3 python ml_models/advanced_trainer.py
```

### Monitoring & Logging
- **Weights & Biases**: Real-time training metrics
- **TensorBoard**: Training visualization
- **Comprehensive logging**: Progress tracking and debugging

### Memory Optimization
- Gradient checkpointing
- Mixed precision training
- Dynamic batching
- Memory-efficient data loading

## 📈 Performance Metrics

### Training Metrics
- Training loss progression
- Validation perplexity
- Learning rate scheduling
- GPU memory utilization

### Model Quality
- Energy domain knowledge assessment
- Response coherence evaluation
- Technical accuracy validation
- Factual consistency checks

## 🔧 Troubleshooting

### Common Issues

1. **Out of Memory Errors**
   ```bash
   # Reduce batch size in configuration
   "train_batch_size": 2,
   "gradient_accumulation_steps": 8
   ```

2. **Data Collection Timeouts**
   ```bash
   # Run collection in stages
   python ml_models/pipeline_orchestrator.py --mode collect
   ```

3. **Model Loading Issues**
   ```bash
   # Check model directory structure
   ls -la model_checkpoints/best_model/
   ```

### Performance Optimization

1. **Training Speed**
   - Use mixed precision training
   - Enable gradient checkpointing
   - Optimize batch size for your hardware

2. **Memory Usage**
   - Reduce sequence length
   - Use gradient accumulation
   - Enable model parallelism for large models

3. **Data Quality**
   - Increase priority threshold
   - Focus on specific document types
   - Use domain-specific filtering

## 🎯 Model Applications

### Integration with Web App
The trained model integrates seamlessly with the main Flask application:

```python
# In src/blog_generator.py
from ml_models.inference import EnergyLLMInference

generator = EnergyLLMInference(model_path='api_models/energy_llm')
blog_post = generator.generate_blog_post(topic, style='informative')
```

### API Deployment
The model can be deployed as a standalone API:

```bash
# Start inference server
python ml_models/inference.py --model-path api_models/energy_llm --port 8080
```

### Custom Applications
- Energy report generation
- Technical documentation creation
- Policy analysis and summarization
- Educational content development

## 📚 Research & Development

### Current Capabilities
- Domain-specific language understanding
- Technical concept explanation
- Policy and regulation interpretation
- Market trend analysis

### Future Enhancements
- Multi-modal capabilities (text + images)
- Real-time knowledge updates
- Specialized fine-tuning for specific energy sectors
- Integration with energy databases and APIs

## 🤝 Contributing

To contribute to the ML system:

1. **Data Sources**: Add new authoritative energy sources
2. **Model Architecture**: Experiment with different base models
3. **Evaluation Metrics**: Develop domain-specific evaluation methods
4. **Performance**: Optimize training and inference speed

## 📄 Citation

If you use this system in your research, please cite:

```
@software{renewable_power_insight_llm,
  title={Energy Domain Large Language Model Training System},
  author={Renewable Power Insight Team},
  year={2024},
  url={https://github.com/your-repo/RenewablePowerInsight}
}
```

---

## 📞 Support

For questions, issues, or contributions:
- Create an issue in the GitHub repository
- Review the troubleshooting section above
- Check the logs in the `logs/` directory for detailed error information

**Happy training! 🚀⚡🌱**
