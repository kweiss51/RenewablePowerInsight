# Category-Based Post Organization System

## Overview
The automated blog generator now organizes all blog posts into category-specific subfolders within the posts directory, matching the website's navigation structure. This provides better organization and scalability for the blog content.

## Category Structure

### 📁 Category Folders
Posts are automatically organized into the following categories based on content analysis:

- **`solar/`** - Solar energy technologies, photovoltaic systems, solar panels
- **`wind/`** - Wind energy, turbines, offshore/onshore wind farms
- **`battery/`** - Energy storage, battery technologies, grid-scale storage
- **`grid-tech/`** - Smart grids, grid technology, cybersecurity, AI energy management
- **`markets/`** - Energy markets, investments, financial analysis, market outlook
- **`policy/`** - Energy policy, regulations, government initiatives, incentives
- **`general/`** - General renewable energy topics (fallback category)

### 🔗 Navigation Structure
All posts now use relative paths appropriate for their subfolder location:
- CSS: `../../style.css`
- Home: `../../index.html`
- Navigation links: `../../index.html#section`

## Content Categorization Logic

### Automatic Category Detection
The system analyzes both title and content for keywords:

```python
# Solar Energy
Keywords: 'solar', 'photovoltaic', 'pv'
→ Category: "Solar Energy" → Folder: 'solar'

# Wind Energy  
Keywords: 'wind', 'turbine', 'offshore'
→ Category: "Wind Energy" → Folder: 'wind'

# Energy Storage
Keywords: 'battery', 'storage', 'grid-scale'
→ Category: "Energy Storage" → Folder: 'battery'

# Smart Grid/Technology
Keywords: 'ai', 'smart', 'technology', 'innovation'
→ Category: "Clean Technology" → Folder: 'grid-tech'

# Markets
Keywords: 'investment', 'market', 'funding', 'finance'
→ Category: "Energy Markets" → Folder: 'markets'

# Policy
Keywords: 'policy', 'regulation', 'incentive', 'government'
→ Category: "Energy Policy" → Folder: 'policy'
```

### Manual Category Override
You can specify a custom category when generating posts:
```bash
python blog_automation_controller.py --mode custom --topic "Solar Innovation" --category "Solar Energy"
```

## File Structure Example

```
posts/
├── solar/
│   ├── solar-panel-efficiency-breakthroughs-in-2024.html
│   └── floating-solar-farm-installations-latest-developments.html
├── wind/
│   ├── offshore-wind-energy-developments-technology-breakthrough.html
│   └── wind-turbine-efficiency-improvements-technology-breakthrough.html
├── battery/
│   └── market-outlook-advanced-battery-storage-technology-industry-trends.html
├── grid-tech/
│   └── revolutionary-advances-in-smart-grid-cybersecurity-innovations.html
├── markets/
├── policy/
│   ├── market-outlook-vehicle-to-grid-technology-adoption-industry-trends.html
│   ├── microgrid-technology-innovations-latest-developments.html
│   └── the-future-of-smart-grid-cybersecurity-measures-industry-analysis.html
└── general/
```

## Migration Process

### Automatic Migration
Existing posts are automatically migrated to appropriate category folders using the `migrate_posts.py` script:

1. **Content Analysis**: Reads existing HTML files and extracts title/content
2. **Categorization**: Uses the same logic as new posts to determine category
3. **File Movement**: Moves files to appropriate category subfolders
4. **Verification**: Confirms successful migration

### Migration Script Usage
```bash
cd ml_models
python migrate_posts.py
```

## Benefits

### 🎯 **Organization**
- Clear separation by topic area
- Scalable structure for growing content
- Easier content management

### 🔍 **SEO & User Experience**
- Logical URL structure: `posts/solar/post-name.html`
- Category-based browsing capability
- Better site architecture

### 🛠 **Development**
- Easier to find and manage posts by category
- Supports future category-specific features
- Cleaner repository structure

### 📊 **Analytics**
- Category-based performance tracking
- Content gap analysis by category
- Strategic content planning

## URL Structure

### New URL Format
Posts now have category-specific URLs:
- Solar: `posts/solar/post-name.html`
- Wind: `posts/wind/post-name.html`
- Battery: `posts/battery/post-name.html`
- Grid Tech: `posts/grid-tech/post-name.html`
- Markets: `posts/markets/post-name.html`
- Policy: `posts/policy/post-name.html`

### Navigation Compatibility
All internal links are updated to work from category subfolders:
- Home link: `../../index.html`
- CSS reference: `../../style.css`
- Category sections: `../../index.html#section`

## Verification

### Post Quality Check
Use the updated verification script to check all posts across all categories:
```bash
cd ml_models
python verify_posts.py
```

### Expected Output
```
=== ACCURATE POST VERIFICATION ===

📁 SOLAR Category:
  ✅ VALID - post1.html - Images: 1, Links: 3
  ✅ VALID - post2.html - Images: 1, Links: 3

📁 WIND Category:
  ✅ VALID - post3.html - Images: 1, Links: 3

📊 SUMMARY: X total posts
✅ ALL POSTS VALID
```

## Implementation Details

### Updated Methods
- `setup_category_folders()`: Creates all category directories
- `get_category_folder()`: Maps categories to folder names
- `create_blog_post()`: Saves to appropriate category subfolder
- Updated HTML template with correct relative paths

### Backward Compatibility
- Existing posts are migrated automatically
- URL structure remains accessible
- Navigation links work from any depth
