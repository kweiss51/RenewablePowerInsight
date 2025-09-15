# ML Blog Post Automation System

## 🎯 Overview

Your ML system automatically generates and saves blog posts for the RenewablePowerInsight website. The system creates HTML files that match your website's format and saves them to the `posts/` directory.

## 🚀 Quick Start

### 1. Generate Blog Posts Immediately

```bash
# Generate 2 daily posts
python ml_models/blog_automation_controller.py --mode daily --count 2

# Generate 5 weekly posts
python ml_models/blog_automation_controller.py --mode weekly --count 5

# Generate a custom post
python ml_models/blog_automation_controller.py --mode custom --topic "solar energy storage" --category "Solar Energy"

# Check statistics
python ml_models/blog_automation_controller.py --stats
```

### 2. Set Up Automated Scheduling

```bash
# Run the scheduler (generates posts automatically)
python ml_models/scheduled_blog_generator.py --mode scheduler

# Generate daily posts once
python ml_models/scheduled_blog_generator.py --mode daily

# Check scheduler status
python ml_models/scheduled_blog_generator.py --mode status
```

## 📁 Generated Files

Blog posts are automatically saved to:
- **Directory**: `posts/`
- **Format**: HTML files matching your website design
- **URLs**: `posts/filename.html`
- **Categories**: Automatically categorized (Solar, Wind, Storage, Policy, etc.)

## 🎮 System Features

### Automatic Blog Generation
- ✅ **HTML Format**: Matches your website's design exactly
- ✅ **SEO Friendly**: Proper titles, meta tags, and structure
- ✅ **Auto-Categorization**: Automatically sorts posts by energy topic
- ✅ **Embedded Links**: 3-5 relevant external links in each post for SEO and user engagement
- ✅ **Responsive Design**: Works on mobile and desktop
- ✅ **Navigation**: Includes proper back links and site navigation

### Content Quality
- ✅ **Energy-Focused**: All content is about renewable energy topics
- ✅ **Professional Format**: Structured with headers, lists, and paragraphs
- ✅ **External Links**: 3-5 relevant authority links embedded in each post (DOE, NREL, IEA, etc.)
- ✅ **Current Topics**: Covers latest trends in clean energy
- ✅ **Comprehensive**: Detailed articles with multiple sections

### Automation Options
- ✅ **Daily Posts**: Generate 2-3 posts every day
- ✅ **Weekly Batches**: Generate 5-10 posts weekly
- ✅ **Custom Topics**: Generate posts on specific subjects
- ✅ **Scheduling**: Automatic generation at set times

## 🔧 Configuration

The system creates a configuration file `blog_schedule_config.json`:

```json
{
  "daily_posts_count": 2,
  "weekly_posts_count": 5,
  "daily_time": "09:00",
  "weekly_day": "monday",
  "weekly_time": "08:00",
  "enabled": true
}
```

## � Embedded Links System

Each blog post automatically includes **3-5 relevant external links** to authoritative sources:

### Link Sources by Category

**Solar Energy:**
- Department of Energy Solar Research
- National Renewable Energy Laboratory (NREL)
- Solar Energy Industries Association (SEIA)
- International Solar Alliance
- Solar Power World Magazine

**Wind Energy:**
- American Wind Energy Association
- Global Wind Energy Council
- Offshore Wind Research (DOE)
- Wind Power Engineering
- International Energy Agency Wind

**Energy Storage:**
- Battery University
- Energy Storage Association
- DOE Energy Storage Program
- International Battery Association
- Grid Storage Launchpad

**Energy Policy:**
- International Renewable Energy Agency (IRENA)
- Clean Energy Ministerial
- Energy Information Administration (EIA)
- International Energy Agency (IEA)
- Renewable Energy Policy Network

**Technology:**
- Clean Energy Smart Manufacturing
- Smart Grid Research
- Advanced Research Projects Agency (ARPA-E)
- National Labs Energy Innovation

### Link Placement
- Links are intelligently embedded within relevant sentences
- Uses contextual anchor text when possible
- All links open in new tabs (`target="_blank"`)
- Balanced distribution throughout the article
- SEO-optimized for authority and relevance

## �📊 Available Topics

The system covers these energy topics:

### Solar Energy
- Perovskite solar cell efficiency
- Floating solar installations
- Residential solar storage
- Solar panel recycling

### Wind Energy
- Offshore wind innovations
- Vertical axis turbines
- Wind grid integration
- Floating wind platforms

### Energy Storage
- Grid-scale batteries
- Lithium-ion recycling
- Solid-state batteries
- Pumped hydro storage

### Technology
- AI energy management
- Smart grid systems
- Vehicle-to-grid tech
- Microgrids

### Policy & Markets
- Investment trends
- Carbon pricing
- Tax incentives
- Transition policies

## 🛠️ Troubleshooting

### Common Issues

**Posts not generating?**
- Check that the `posts/` directory exists
- Verify file permissions
- Run with `--stats` to check system status

**Wrong file paths?**
- The system automatically uses the correct paths
- Posts are saved to `/posts/` directory relative to your main website

**Need different topics?**
- Edit the topics list in `blog_automation_controller.py`
- Use `--topic` for custom subjects

### System Status

Check system health:
```bash
python ml_models/blog_automation_controller.py --stats
```

This shows:
- Total posts generated
- Recent post filenames
- Posts directory location

## 🔄 Integration with Your Website

The generated HTML files are ready to use:

1. **File Format**: Standard HTML with your website's styling
2. **Navigation**: Includes proper links back to your homepage
3. **Categories**: Automatically organized by energy topic
4. **URLs**: Use format `posts/filename.html` in your links

### Adding Posts to Homepage

To link new posts in your `index.html`:
```html
<h2><a href="posts/filename.html">Post Title</a></h2>
```

The system automatically creates SEO-friendly filenames from post titles.

## 🎯 Next Steps

1. **Run a test generation**:
   ```bash
   python ml_models/blog_automation_controller.py --mode daily --count 1
   ```

2. **Check the generated post**:
   - Look in the `posts/` directory
   - Open the HTML file in a browser
   - Verify it matches your website design

3. **Set up automation**:
   ```bash
   python ml_models/scheduled_blog_generator.py --mode scheduler
   ```

4. **Monitor and adjust**:
   - Use `--stats` to track generation
   - Modify topics as needed
   - Adjust scheduling in config file

Your ML system is now ready to automatically generate professional blog content for your renewable energy website! 🚀
