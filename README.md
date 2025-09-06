# Renewable Power Insight

An AI-powered blog providing comprehensive coverage of renewable energy trends, innovations, and market developments.

## 🌟 Features

- **AI-Generated Content**: Advanced machine learning models trained on energy domain data
- **Daily Updates**: Automated content generation covering latest energy developments
- **Comprehensive Coverage**: Solar, wind, storage, EVs, policy, and market analysis
- **GitHub Pages Integration**: Automated Jekyll-based website deployment

## 🚀 Live Site

Visit the blog at: [https://kweiss51.github.io/RenewablePowerInsight/](https://kweiss51.github.io/RenewablePowerInsight/)

## 🤖 How It Works

The system uses:
1. **Data Collection**: Automated scraping of academic papers, government reports, and industry data
2. **AI Processing**: Custom-trained language models for energy domain content generation
3. **Jekyll Integration**: Automated conversion to Jekyll-formatted blog posts
4. **GitHub Pages**: Automatic deployment via GitHub Actions

## 📁 Repository Structure

```
├── _posts/                 # Jekyll blog posts
├── _config.yml            # Jekyll configuration
├── assets/                # CSS, JS, and images
├── data/                  # Generated post data
├── ml_models/             # AI model components
├── templates/             # HTML templates
├── simple_blog_app.py     # Blog generation interface
└── github_pages_generator.py  # Jekyll conversion tool
```

## 🛠️ Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/kweiss51/RenewablePowerInsight.git
   cd RenewablePowerInsight
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   bundle install
   ```

3. **Generate content**:
   ```bash
   python simple_blog_app.py
   ```

4. **Convert to Jekyll**:
   ```bash
   python github_pages_generator.py
   ```

5. **Serve locally**:
   ```bash
   bundle exec jekyll serve
   ```

## 📝 Content Generation

The AI system generates content on topics including:
- Solar power innovations
- Wind energy developments
- Energy storage solutions
- Electric vehicle infrastructure
- Smart grid technology
- Energy policy analysis
- Market trends and forecasts

## 🔄 Automation

The system includes:
- **Monthly Training**: AI model updates with latest research
- **Daily Generation**: Automated content creation
- **GitHub Integration**: Automatic post publishing
- **Quality Control**: Content validation and formatting

## 📊 Data Sources

Content is generated from analysis of:
- Academic journals (Google Scholar)
- Government energy reports (DOE, IEA)
- National laboratory publications (NREL, ORNL)
- Industry market analysis
- Energy news and developments

## 🤝 Contributing

This is an experimental AI-powered blog. For suggestions or improvements:
1. Open an issue describing your idea
2. Fork the repository
3. Create a feature branch
4. Submit a pull request

## ⚖️ License

MIT License - See [LICENSE](LICENSE) for details.

## 📧 Contact

For questions about the AI system or content generation:
- **GitHub Issues**: [Open an issue](https://github.com/kweiss51/RenewablePowerInsight/issues)
- **Repository**: [kweiss51/RenewablePowerInsight](https://github.com/kweiss51/RenewablePowerInsight)

---

*All content is generated using AI trained on energy domain data and should be considered for informational purposes. For critical decisions, please consult primary sources and expert analysis.*
