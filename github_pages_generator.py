#!/usr/bin/env python3
"""
GitHub Pages Blog Generator for Energy Posts
Generates Jekyll-formatted blog posts for GitHub Pages deployment
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import yaml
import re
import logging
from typing import Dict, List, Optional
import shutil

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GitHubPagesGenerator:
    def __init__(self, repo_path: str = None):
        """Initialize the GitHub Pages generator"""
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
        self.posts_dir = self.repo_path / '_posts'
        self.data_dir = self.repo_path / 'data' / 'generated_posts'
        self.site_config = self.repo_path / '_config.yml'
        
        # Ensure directories exist
        self.posts_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Energy blog configuration
        self.site_title = "Renewable Power Insight"
        self.site_description = "AI-powered insights into renewable energy trends and developments"
        self.base_url = "/RenewablePowerInsight"
        
        self.setup_jekyll_structure()
    
    def setup_jekyll_structure(self):
        """Setup the basic Jekyll structure for GitHub Pages"""
        
        # Create _config.yml
        config = {
            'title': self.site_title,
            'description': self.site_description,
            'baseurl': self.base_url,
            'url': 'https://kweiss51.github.io',
            'theme': 'minima',
            'plugins': ['jekyll-feed', 'jekyll-sitemap', 'jekyll-seo-tag'],
            'markdown': 'kramdown',
            'highlighter': 'rouge',
            'permalink': '/:year/:month/:day/:title/',
            'paginate': 10,
            'paginate_path': '/page:num/',
            'excerpt_separator': '<!--more-->',
            'show_excerpts': True,
            'author': {
                'name': 'Energy AI Team',
                'email': 'contact@renewablepowerinsight.com'
            },
            'social': {
                'github': 'kweiss51',
                'twitter': 'renewablepower'
            }
        }
        
        with open(self.site_config, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info("✅ Jekyll configuration created")
        
        # Create index.md
        self.create_index_page()
        
        # Create about page
        self.create_about_page()
        
        # Create assets directory structure
        self.create_assets_structure()
    
    def create_index_page(self):
        """Create the main index page"""
        index_content = """---
layout: home
title: "Renewable Power Insight"
description: "AI-powered insights into renewable energy trends and developments"
---

# Welcome to Renewable Power Insight

Discover the latest trends, innovations, and insights in renewable energy through AI-powered content generation. Our advanced machine learning system analyzes academic research, government reports, and industry data to bring you comprehensive coverage of the energy transition.

## Latest Energy Insights

Our AI system generates daily content covering:

- **Solar Power Innovations** - Latest developments in photovoltaic technology
- **Wind Energy Trends** - Market analysis and technological advances
- **Energy Storage Solutions** - Battery technology and grid integration
- **Smart Grid Technology** - Modernization and efficiency improvements
- **Electric Vehicle Infrastructure** - Charging networks and integration
- **Energy Policy Analysis** - Government initiatives and regulatory changes
- **Sustainable Technology** - Clean energy breakthroughs and applications

## About Our AI-Generated Content

This blog uses advanced natural language processing trained specifically on energy domain data from:
- Academic journals and research papers
- Government energy reports and statistics
- National laboratory publications
- Industry analysis and market research

All content is generated using cutting-edge machine learning to provide accurate, informative, and up-to-date insights into the renewable energy sector.

<!--more-->

---

*Content generated using AI trained on energy domain data. For questions or feedback, please contact us through GitHub.*
"""
        
        with open(self.repo_path / 'index.md', 'w') as f:
            f.write(index_content)
        
        logger.info("✅ Index page created")
    
    def create_about_page(self):
        """Create the about page"""
        about_content = """---
layout: page
title: About
permalink: /about/
---

# About Renewable Power Insight

Renewable Power Insight is an AI-powered blog that provides comprehensive coverage of renewable energy trends, innovations, and market developments. Our content is generated using advanced machine learning models trained specifically on energy domain data.

## Our Mission

To democratize access to energy industry insights by leveraging artificial intelligence to analyze vast amounts of academic research, government reports, and industry data, making complex energy topics accessible to everyone.

## How It Works

Our system combines:

### 🤖 **Advanced AI Models**
- Custom-trained language models on energy domain data
- Natural language processing for content generation
- Automated research synthesis and analysis

### 📚 **Comprehensive Data Sources**
- Academic journals and research papers
- Government energy statistics and reports
- National laboratory publications
- Industry market analysis and trends

### 🔄 **Continuous Learning**
- Monthly model updates with latest research
- Real-time integration of new energy developments
- Adaptive content generation based on trending topics

## Content Categories

- **Technology Innovation** - Latest breakthroughs in renewable energy tech
- **Market Analysis** - Industry trends and economic insights
- **Policy & Regulation** - Government initiatives and regulatory changes
- **Research Highlights** - Key findings from academic studies
- **Future Outlook** - Predictions and scenario analysis

## Data Sources

Our AI model is trained on data from reputable sources including:
- Google Scholar academic papers
- Department of Energy publications
- National Renewable Energy Laboratory (NREL)
- International Energy Agency (IEA) reports
- Energy industry journals and publications

---

*This is an experimental AI-powered blog. All content is generated automatically and should be considered for informational purposes. For critical decisions, please consult primary sources and expert analysis.*

**Contact:** [GitHub Repository](https://github.com/kweiss51/RenewablePowerInsight)
"""
        
        with open(self.repo_path / 'about.md', 'w') as f:
            f.write(about_content)
        
        logger.info("✅ About page created")
    
    def create_assets_structure(self):
        """Create assets directory structure"""
        assets_dir = self.repo_path / 'assets'
        css_dir = assets_dir / 'css'
        js_dir = assets_dir / 'js'
        images_dir = assets_dir / 'images'
        
        for directory in [assets_dir, css_dir, js_dir, images_dir]:
            directory.mkdir(exist_ok=True)
        
        # Create custom CSS
        custom_css = """---
---

/* Custom styles for Renewable Power Insight */

.site-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-bottom: none;
}

.site-title, .site-title:visited {
    color: white !important;
}

.site-nav .page-link {
    color: rgba(255, 255, 255, 0.9) !important;
}

.site-nav .page-link:hover {
    color: white !important;
}

.post-title {
    color: #333;
    font-weight: 600;
}

.post-meta {
    color: #666;
    font-size: 0.9em;
}

.post-content h2 {
    color: #667eea;
    border-bottom: 2px solid #f1f1f1;
    padding-bottom: 5px;
}

.post-content h3 {
    color: #555;
}

.highlight {
    background: #f8f9fa;
    border-left: 4px solid #667eea;
    padding: 1rem;
    margin: 1rem 0;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    padding: 10px 20px;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    display: inline-block;
    transition: all 0.3s ease;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

.energy-tag {
    background: #e3f2fd;
    color: #1565c0;
    padding: 3px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
    text-transform: uppercase;
    margin-right: 5px;
}

.post-excerpt {
    color: #666;
    line-height: 1.6;
}

footer {
    background: #f8f9fa;
    padding: 2rem 0;
    margin-top: 3rem;
    border-top: 1px solid #dee2e6;
}
"""
        
        with open(css_dir / 'style.scss', 'w') as f:
            f.write(custom_css)
        
        logger.info("✅ Assets structure created")
    
    def generate_jekyll_post(self, post_data: Dict) -> str:
        """Generate a Jekyll-formatted blog post"""
        
        # Extract post information
        title = post_data.get('title', 'Energy Update')
        content = post_data.get('content', '')
        topic = post_data.get('topic', 'energy')
        generated_date = post_data.get('generated_date', datetime.now().isoformat())
        target_date = post_data.get('target_date', datetime.now().strftime('%Y-%m-%d'))
        word_count = post_data.get('word_count', len(content.split()))
        
        # Create Jekyll front matter
        date_obj = datetime.fromisoformat(generated_date.replace('Z', '+00:00')) if 'Z' in generated_date else datetime.fromisoformat(generated_date)
        
        # Generate categories and tags
        categories = self._generate_categories(topic)
        tags = self._generate_tags(content, topic)
        
        # Create slug for filename
        slug = self._create_slug(title)
        filename = f"{date_obj.strftime('%Y-%m-%d')}-{slug}.md"
        
        # Jekyll front matter
        front_matter = {
            'layout': 'post',
            'title': title,
            'date': date_obj.strftime('%Y-%m-%d %H:%M:%S %z') if date_obj.tzinfo else date_obj.strftime('%Y-%m-%d %H:%M:%S +0000'),
            'categories': categories,
            'tags': tags,
            'excerpt': self._generate_excerpt(content),
            'author': 'Energy AI Team',
            'featured': False,
            'word_count': word_count,
            'reading_time': max(1, round(word_count / 200)),
            'topic': topic,
            'generated_by': 'AI',
            'last_modified_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S +0000')
        }
        
        # Format content for Jekyll
        formatted_content = self._format_content_for_jekyll(content)
        
        # Create full post content
        post_content = "---\n"
        post_content += yaml.dump(front_matter, default_flow_style=False)
        post_content += "---\n\n"
        post_content += formatted_content
        post_content += "\n\n---\n\n"
        post_content += "*This post was generated using AI trained on energy domain research and industry data. "
        post_content += "The content synthesizes information from academic papers, government reports, and industry analysis.*\n"
        
        return filename, post_content
    
    def _generate_categories(self, topic: str) -> List[str]:
        """Generate categories based on topic"""
        category_mapping = {
            'solar': ['Technology', 'Solar Power'],
            'wind': ['Technology', 'Wind Energy'],
            'hydroelectric': ['Technology', 'Renewable Energy'],
            'geothermal': ['Technology', 'Renewable Energy'],
            'energy storage': ['Technology', 'Energy Storage'],
            'battery': ['Technology', 'Energy Storage'],
            'smart grid': ['Technology', 'Grid Infrastructure'],
            'electric vehicle': ['Transportation', 'Electric Vehicles'],
            'energy efficiency': ['Policy', 'Efficiency'],
            'carbon': ['Environment', 'Climate'],
            'nuclear': ['Technology', 'Nuclear Power'],
            'policy': ['Policy', 'Regulation'],
            'market': ['Market Analysis', 'Economics']
        }
        
        categories = ['Energy']
        topic_lower = topic.lower()
        
        for key, cats in category_mapping.items():
            if key in topic_lower:
                categories.extend(cats)
                break
        
        return list(set(categories))
    
    def _generate_tags(self, content: str, topic: str) -> List[str]:
        """Generate tags based on content and topic"""
        # Base tags
        tags = ['renewable energy', 'sustainability']
        
        # Topic-specific tags
        if 'solar' in topic.lower():
            tags.extend(['solar power', 'photovoltaic', 'clean energy'])
        elif 'wind' in topic.lower():
            tags.extend(['wind energy', 'turbines', 'offshore wind'])
        elif 'storage' in topic.lower():
            tags.extend(['energy storage', 'batteries', 'grid integration'])
        elif 'electric' in topic.lower():
            tags.extend(['electric vehicles', 'EV charging', 'transportation'])
        elif 'efficiency' in topic.lower():
            tags.extend(['energy efficiency', 'conservation', 'optimization'])
        
        # Content-based tags
        content_lower = content.lower()
        keyword_tags = {
            'innovation': 'innovation',
            'research': 'research',
            'market': 'market trends',
            'technology': 'technology',
            'policy': 'energy policy',
            'investment': 'investment',
            'climate': 'climate change',
            'carbon': 'carbon emissions',
            'grid': 'smart grid',
            'future': 'future outlook'
        }
        
        for keyword, tag in keyword_tags.items():
            if keyword in content_lower:
                tags.append(tag)
        
        return list(set(tags))
    
    def _create_slug(self, title: str) -> str:
        """Create URL-friendly slug from title"""
        # Remove special characters and convert to lowercase
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        # Replace spaces with hyphens
        slug = re.sub(r'[-\s]+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        # Limit length
        return slug[:50]
    
    def _generate_excerpt(self, content: str) -> str:
        """Generate excerpt from content"""
        # Get first paragraph or first 150 characters
        first_paragraph = content.split('\n\n')[0] if '\n\n' in content else content
        if len(first_paragraph) > 150:
            excerpt = first_paragraph[:147] + "..."
        else:
            excerpt = first_paragraph
        
        return excerpt.strip()
    
    def _format_content_for_jekyll(self, content: str) -> str:
        """Format content for Jekyll with proper markdown"""
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Add paragraph
                formatted_paragraphs.append(paragraph.strip())
        
        # Join with double newlines for proper paragraph spacing
        formatted_content = '\n\n'.join(formatted_paragraphs)
        
        # Add read more marker after first paragraph
        if len(formatted_paragraphs) > 1:
            first_break = formatted_content.find('\n\n')
            if first_break > 0:
                formatted_content = (formatted_content[:first_break] + 
                                   '\n\n<!--more-->\n\n' + 
                                   formatted_content[first_break+2:])
        
        return formatted_content
    
    def convert_generated_posts_to_jekyll(self) -> List[str]:
        """Convert all generated posts to Jekyll format"""
        converted_posts = []
        
        if not self.data_dir.exists():
            logger.warning("No generated posts directory found")
            return converted_posts
        
        # Process all JSON post files
        for post_file in self.data_dir.glob('*.json'):
            try:
                with open(post_file, 'r') as f:
                    post_data = json.load(f)
                
                # Generate Jekyll post
                filename, content = self.generate_jekyll_post(post_data)
                
                # Write to _posts directory
                post_path = self.posts_dir / filename
                with open(post_path, 'w') as f:
                    f.write(content)
                
                converted_posts.append(filename)
                logger.info(f"✅ Converted post: {filename}")
                
            except Exception as e:
                logger.error(f"Error converting {post_file}: {e}")
                continue
        
        return converted_posts
    
    def create_github_workflow(self):
        """Create GitHub Actions workflow for automated building"""
        workflow_dir = self.repo_path / '.github' / 'workflows'
        workflow_dir.mkdir(parents=True, exist_ok=True)
        
        workflow_content = """name: Build and Deploy Jekyll Site

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 6 AM UTC to check for new posts
    - cron: '0 6 * * *'

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        
      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.1'
          bundler-cache: true
          cache-version: 0
          
      - name: Setup Pages
        id: pages
        uses: actions/configure-pages@v4
        
      - name: Build with Jekyll
        run: bundle exec jekyll build --baseurl "${{ steps.pages.outputs.base_path }}"
        env:
          JEKYLL_ENV: production
          
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
"""
        
        with open(workflow_dir / 'jekyll.yml', 'w') as f:
            f.write(workflow_content)
        
        logger.info("✅ GitHub Actions workflow created")
    
    def create_gemfile(self):
        """Create Gemfile for Jekyll dependencies"""
        gemfile_content = """source "https://rubygems.org"

gem "jekyll", "~> 4.3.0"
gem "minima", "~> 2.5"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
  gem "jekyll-sitemap"
  gem "jekyll-seo-tag"
  gem "jekyll-paginate"
end

platforms :mingw, :x64_mingw, :mswin, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.1.1", :platforms => [:mingw, :x64_mingw, :mswin]
gem "http_parser.rb", "~> 0.6.0", :platforms => [:jruby]

gem "webrick", "~> 1.7"
"""
        
        with open(self.repo_path / 'Gemfile', 'w') as f:
            f.write(gemfile_content)
        
        logger.info("✅ Gemfile created")
    
    def generate_readme(self):
        """Generate README for the repository"""
        readme_content = """# Renewable Power Insight

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
"""
        
        with open(self.repo_path / 'README.md', 'w') as f:
            f.write(readme_content)
        
        logger.info("✅ README.md created")

def main():
    """Main function to set up GitHub Pages blog"""
    print("🚀 Setting up GitHub Pages Blog for Energy Content...")
    
    # Initialize generator
    generator = GitHubPagesGenerator()
    
    # Create Jekyll structure
    print("📁 Creating Jekyll structure...")
    generator.create_gemfile()
    generator.create_github_workflow()
    generator.generate_readme()
    
    # Convert existing posts
    print("📝 Converting generated posts to Jekyll format...")
    converted = generator.convert_generated_posts_to_jekyll()
    print(f"✅ Converted {len(converted)} posts")
    
    print("🎉 GitHub Pages blog setup complete!")
    print(f"📁 Posts directory: {generator.posts_dir}")
    print("🌐 Push to GitHub to deploy your energy blog!")

if __name__ == "__main__":
    main()
