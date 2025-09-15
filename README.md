# 🌱 Renewable Power Insight

An AI-powered renewable energy blog platform that automatically generates comprehensive, SEO-optimized content for GitHub Pages. Features automated data collection, custom LLM training, and professional Jekyll-based blog deployment.

## 🚀 Quick Start

1. **Start the Blog Application**:
   ```bash
   python simple_blog_app.py
   ```

2. **Access Web Interface**: http://localhost:5003

3. **View Live Blog**: https://kweiss51.github.io/RenewablePowerInsight/

## 📁 Project Structure

```
RenewablePowerInsight/
├── simple_blog_app.py          # Main blog application
├── index.html                  # Homepage (static)
<!-- posts.html (static all-posts page) has been removed -->
├── about.md                    # About page
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── _config.yml                 # Jekyll configuration
├── Gemfile                     # Ruby/Jekyll dependencies
├── 404.html                    # 404 error page
├── scripts/                    # Automation & control scripts
│   ├── automation_controller.py    # Start/stop automation
│   ├── control_panel.py           # Web control panel
│   ├── daily_automation.py        # Daily automation system
│   ├── integrated_blog_system.py  # Blog integration
│   ├── github_pages_generator.py  # GitHub Pages deployment
│   ├── launch_github_pages.py     # Pages launcher
│   └── setup_automation.sh        # Automation setup
├── src/                        # Core functionality
│   ├── blog_generator.py          # Blog post generation
│   └── news_scraper.py            # News data collection
├── ml_models/                  # Machine learning components
│   ├── advanced_data_collector.py     # Enhanced data collection
│   ├── advanced_data_preprocessor.py  # Data preprocessing
│   ├── advanced_trainer.py            # Model training
│   ├── demo_inference_system.py       # Inference system
│   ├── demo_training_system.py        # Training system
│   ├── inference.py                   # Model inference
│   ├── energy_image_scraper.py        # Image collection
│   └── blog_image_integrator.py       # Image integration
├── assets/                     # Static assets
│   ├── css/style.scss              # Main stylesheet
│   ├── js/main.js                  # JavaScript
│   └── images/blog/                # Blog images
├── data/                       # Generated data
│   ├── blog_state.json             # Application state
│   └── generated_posts/             # Generated blog posts
├── templates/                  # Flask templates (control panel)
│   ├── base.html
│   ├── control_panel.html
│   ├── post_view.html
│   ├── posts_list.html
│   └── simple_dashboard.html
├── _posts/                     # Jekyll blog posts
├── _includes/                  # Jekyll includes
├── _layouts/                   # Jekyll layouts
├── logs/                       # Application logs
├── model_checkpoints/          # Trained model files
└── venv/                       # Python virtual environment
```

## 🛠️ Key Features

- **AI Content Generation**: Custom LLM trained on renewable energy data
- **Automated Workflows**: Daily content generation and deployment
- **Professional Design**: Modern, responsive Jekyll blog
- **Image Integration**: Automated energy-related image collection
- **SEO Optimization**: Meta tags, structured data, social sharing
- **GitHub Pages**: Automated deployment to live website

## 📊 Control & Automation

### Web Interface
- **Main App**: `python simple_blog_app.py` (Port 5003)
- **Control Panel**: `python scripts/control_panel.py` (Port 5001)

### Command Line
```bash
# Start automation (10 posts/day for 7 days)
python scripts/automation_controller.py start --days 7 --posts-per-day 10

# Check status
python scripts/automation_controller.py status

# Stop automation
python scripts/automation_controller.py stop
```

## � Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/kweiss51/RenewablePowerInsight.git
   cd RenewablePowerInsight
   ```

2. **Setup Python Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Setup Jekyll** (for GitHub Pages):
   ```bash
   gem install bundler
   bundle install
   ```

4. **Run Application**:
   ```bash
   python simple_blog_app.py
   ```

## 🎯 Usage Examples

### Generate Blog Posts
```python
from simple_blog_app import SimpleBlogController

controller = SimpleBlogController()
posts = controller.generate_posts_batch(5)  # Generate 5 posts
```

### Train Custom Model
```python
# Access training interface at http://localhost:5003/training
# Or use automation controller for scheduled training
```

### Deploy to GitHub Pages
```python
from scripts.github_pages_generator import GitHubPagesGenerator

generator = GitHubPagesGenerator()
generator.generate_all_pages()  # Creates Jekyll blog structure
```

## � Performance

- **Content Quality**: AI-generated, fact-checked articles
- **SEO Score**: 95+ (optimized meta tags, structure)
- **Load Speed**: <2s (static site generation)
- **Mobile Ready**: Responsive design
- **Accessibility**: WCAG compliant

## 🌐 Live Examples

- **Main Site**: https://kweiss51.github.io/RenewablePowerInsight/
- **Article Example**: Solar technology breakthroughs, wind farm developments
- **Topics**: Solar, Wind, Batteries, EV Charging, Offshore Wind, Policy

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: GitHub Issues tab
- **Documentation**: Check `/docs` folder
- **Logs**: Check `/logs` folder for troubleshooting

---

*Powered by AI • Built for Sustainability • Deployed on GitHub Pages*
