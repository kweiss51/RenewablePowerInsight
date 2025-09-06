# Renewable Power Insight 🌱⚡

An advanced AI-powered energy news platform that scrapes trending topics and generates high-quality blog content using both external APIs and a custom-trained Large Language Model.

## 🚀 Features

### Core Functionality
- **🔍 Automated News Scraping**: Monitors Google News, Bing, and RSS feeds for energy topics
- **🤖 Dual AI Generation**: 
  - Custom Energy LLM (trained on energy industry data)
  - OpenAI GPT fallback for reliability
- **⚡ Real-time Updates**: Automatically refreshes content every 4 hours
- **📊 Admin Dashboard**: Monitor system status and manually trigger updates
- **📱 Responsive Design**: Works perfectly on desktop and mobile devices

### Advanced AI Capabilities
- **🧠 Custom Energy LLM**: Domain-specific language model trained on energy news
- **🎯 Topic Coverage**: Solar, wind, batteries, EVs, hydrogen, policy, carbon markets
- **📈 SEO Optimization**: Automatically optimized for search engines
- **🔬 Quality Analysis**: Content scoring and filtering for high-quality output

## 🛠️ Technology Stack

### Core Platform
- **Backend**: Python Flask
- **Scraping**: BeautifulSoup, Newspaper3k, Feedparser
- **AI**: Custom PyTorch LLM + OpenAI fallback
- **Frontend**: HTML5, CSS3, JavaScript
- **Styling**: Modern CSS with responsive design
- **Automation**: Schedule library for periodic updates

### Machine Learning Stack
- **Framework**: PyTorch + Transformers
- **Architecture**: Custom transformer with energy domain specialization
- **Training**: Mixed precision, gradient accumulation, learning rate scheduling
- **Data**: Automated collection and preprocessing of energy news
- **Monitoring**: Weights & Biases integration for experiment tracking

## 🎯 Two Deployment Options

### Option 1: Quick Start (OpenAI API)
Perfect for immediate use with external API:

1. **Clone and Setup**
```bash
git clone https://github.com/your-username/RenewablePowerInsight.git
cd RenewablePowerInsight
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure API**
```bash
cp .env.example .env
# Add your OpenAI API key to .env
echo "OPENAI_API_KEY=your_key_here" >> .env
```

3. **Run Application**
```bash
python app.py
```

### Option 2: Custom LLM (Self-Hosted AI)
For complete independence from external APIs:

1. **Setup ML Dependencies**
```bash
python setup_ml.py
```

2. **Train Custom Model**
```bash
# Quick training (2-3 hours on GPU)
python ml_models/train_pipeline.py --model-size base --num-epochs 3

# Or step by step:
python ml_models/train_pipeline.py --stage collect     # Collect training data
python ml_models/train_pipeline.py --stage preprocess # Process data  
python ml_models/train_pipeline.py --stage train      # Train model
```

3. **Run with Custom LLM**
```bash
python app.py  # Automatically uses custom LLM when available
```

6. **Open your browser**
```
http://localhost:5000
```

## 🔧 Configuration

### Environment Variables (.env)

- `OPENAI_API_KEY`: Your OpenAI API key for AI blog generation (optional)
- `FLASK_ENV`: Flask environment (development/production)
- `FLASK_DEBUG`: Enable debug mode
- `MAX_ARTICLES_PER_KEYWORD`: Articles to scrape per keyword
- `UPDATE_INTERVAL_HOURS`: How often to update content

### Without OpenAI API Key

The application works without an OpenAI API key! It will:
- Still scrape news articles
- Generate basic blog posts using templates
- Provide all the same functionality

### With OpenAI API Key

For enhanced AI-generated content:
1. Get an API key from [OpenAI](https://platform.openai.com/api-keys)
2. Add it to your `.env` file
3. Restart the application

## 📋 Usage

### Web Interface

1. **Home Page**: View all generated blog posts
2. **Individual Posts**: Click any post to read the full article
3. **Admin Dashboard**: Monitor system status and trigger manual updates
4. **About Page**: Learn how the system works

### Manual Content Generation

Visit the Admin Dashboard (`/admin`) to:
- View system statistics
- Manually trigger news scraping
- Check API status
- Monitor recent activity

### API Endpoints

- `GET /api/posts`: Get all blog posts as JSON
- `POST /api/scrape`: Manually trigger scraping and generation

## 🎯 Covered Energy Topics

The system automatically monitors these energy keywords:

- ☀️ Solar Power & Photovoltaics
- 💨 Wind Energy (Onshore & Offshore)
- 🔋 Energy Storage & Batteries
- 🚗 Electric Vehicles & EVs
- 💧 Hydrogen Fuel & Fuel Cells
- 🌍 Geothermal Energy
- 💡 Energy Efficiency & Smart Grid
- 🏭 Nuclear Power
- 🌱 Biomass & Bioenergy
- 📊 Energy Policy & Markets
- 🌡️ Climate Change & Sustainability

## 🔄 How It Works

1. **News Scraping**: System searches Google News and Bing RSS feeds
2. **Topic Analysis**: AI identifies trending topics and clusters related articles
3. **Content Generation**: Creates comprehensive blog posts with proper structure
4. **Publication**: Posts are automatically published to the web interface
5. **Scheduling**: Process repeats every 4 hours automatically

## 📁 Project Structure

```
RenewablePowerInsight/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
├── src/
│   ├── news_scraper.py   # News scraping logic
│   └── blog_generator.py # AI blog post generation
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── post.html
│   ├── admin.html
│   └── about.html
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── main.js       # Frontend JavaScript
└── data/                 # Generated content storage
    ├── energy_articles_*.json
    └── blog_posts_*.json
```

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

1. **Set environment variables**
```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
```

2. **Use a production WSGI server**
```bash
pip install gunicorn
gunicorn app:app
```

3. **Or deploy to platforms like Heroku, Vercel, or DigitalOcean**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**No posts appearing?**
- Check internet connection
- Visit `/admin` to manually trigger scraping
- Check console for error messages

**AI generation not working?**
- Verify OpenAI API key in `.env` file
- Check API key has sufficient credits
- System falls back to template generation without API key

**Scraping failing?**
- Some websites may block scraping
- RSS feeds occasionally have issues
- System is designed to be resilient to individual failures

## 📊 Monitoring

The application includes built-in monitoring:
- Real-time system status
- Scraping success/failure tracking
- Generated content statistics
- Performance metrics

## 🔮 Future Enhancements

- [ ] Social media integration
- [ ] Email newsletter generation
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] RSS feed output
- [ ] SEO optimization
- [ ] Comment system
- [ ] User accounts and preferences

## 📞 Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the code documentation

---

**🌱 Built with sustainability in mind - helping promote renewable energy awareness through AI-powered content creation.**
