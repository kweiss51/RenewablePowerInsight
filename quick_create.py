#!/usr/bin/env python3
"""
Quick script to create missing subcategory pages
"""

import os

# Simple template for subcategory pages
def create_page(filename, title, description, category, nav_items):
    # Determine which nav item is active
    active_nav = ''
    for i, (href, label) in enumerate(nav_items):
        if href == filename:
            active_nav = f'<a href="{href}" class="active">{label}</a>'
        else:
            active_nav += f'<a href="{href}">{label}</a>' if active_nav else f'<a href="{href}">{label}</a>'
    
    # Build nav HTML
    nav_html = '\n                '.join([
        f'<a href="{href}"{" class=\"active\"" if href == filename else ""}>{label}</a>' 
        for href, label in nav_items
    ])
    
    # Main nav with active category
    main_nav_active = {
        'wind': 'Wind',
        'battery': 'Battery Storage', 
        'grid': 'Grid Tech',
        'markets': 'Markets',
        'policy': 'Policy'
    }
    
    main_nav = f'''<a href="/">Home</a>
                <a href="posts.html">All Posts</a>
                <a href="solar.html">Solar</a>
                <a href="wind.html"{' class="active"' if category == 'wind' else ''}>Wind</a>
                <a href="battery.html"{' class="active"' if category == 'battery' else ''}>Battery Storage</a>
                <a href="grid.html"{' class="active"' if category == 'grid' else ''}>Grid Tech</a>
                <a href="markets.html"{' class="active"' if category == 'markets' else ''}>Markets</a>
                <a href="policy.html"{' class="active"' if category == 'policy' else ''}>Policy</a>'''

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Renewable Power Insight</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: "Helvetica Neue", Arial, sans-serif; line-height: 1.6; color: #000; background-color: #fff; }}
        .site-header {{ background: #fff; border-bottom: 2px solid #000; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .site-header .wrapper {{ max-width: 1200px; margin: 0 auto; padding: 1rem; display: flex; justify-content: space-between; align-items: center; }}
        .site-title {{ font-size: 1.6rem; font-weight: 700; text-decoration: none; color: #2d5016; letter-spacing: -0.5px; }}
        .site-nav {{ display: flex; gap: 1.5rem; }}
        .site-nav a {{ color: #333; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: color 0.2s ease; }}
        .site-nav a:hover, .site-nav a.active {{ color: #2d5016; }}
        .sub-nav-bar {{ background: #f8f9fa; border-bottom: 1px solid #e5e5e5; padding: 15px 0; }}
        .sub-nav-bar .wrapper {{ max-width: 1200px; margin: 0 auto; padding: 0 20px; }}
        .sub-nav {{ display: flex; gap: 2rem; flex-wrap: wrap; }}
        .sub-nav a {{ color: #666; text-decoration: none; font-weight: 500; font-size: 0.9rem; transition: color 0.2s ease; position: relative; }}
        .sub-nav a:hover, .sub-nav a.active {{ color: #2d5016; }}
        .sub-nav a.active::after {{ content: ''; position: absolute; bottom: -15px; left: 0; right: 0; height: 2px; background: #2d5016; }}
        .main {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; display: grid; grid-template-columns: 1fr 300px; gap: 40px; }}
        .page-header h1 {{ font-size: 2.2rem; font-weight: 700; color: #2d5016; margin-bottom: 10px; }}
        .page-header p {{ font-size: 1.1rem; color: #666; margin-bottom: 20px; }}
        .content {{ background: #fff; border: 1px solid #e5e5e5; border-radius: 8px; padding: 30px; }}
        .sidebar {{ background: #f8f9fa; padding: 30px 25px; border-radius: 8px; height: fit-content; }}
        .sidebar h2 {{ font-size: 1.4rem; font-weight: 700; margin-bottom: 20px; color: #2d5016; }}
        @media (max-width: 968px) {{ .main {{ grid-template-columns: 1fr; gap: 30px; padding: 20px; }} }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="wrapper">
            <a class="site-title" href="/">Renewable Power Insight</a>
            <nav class="site-nav">
                {main_nav}
            </nav>
        </div>
    </header>

    <div class="sub-nav-bar">
        <div class="wrapper">
            <nav class="sub-nav">
                {nav_html}
            </nav>
        </div>
    </div>

    <main class="main">
        <div class="content-area">
            <div class="page-header">
                <h1>{title}</h1>
                <p>{description}</p>
            </div>

            <div class="content">
                <h2>Latest {title} Updates</h2>
                <p>Stay informed about the latest developments in {description.lower()}. This section will feature the most recent news, analysis, and insights.</p>
                <br>
                <p><strong>Coming Soon:</strong> Featured articles and in-depth coverage of {title.lower()} topics.</p>
            </div>
        </div>

        <aside class="sidebar">
            <h2>Quick Links</h2>
            <p>Related topics and resources for {title.lower()}.</p>
        </aside>
    </main>
</body>
</html>'''
    
    return html

def main():
    # Define all subcategories to create
    pages_to_create = [
        # Wind subcategories
        ('wind-offshore.html', 'Offshore Wind', 'Offshore wind farms, floating turbines, and marine wind energy', 'wind',
         [('wind.html', 'All Wind'), ('wind-offshore.html', 'Offshore'), ('wind-onshore.html', 'Onshore'), 
          ('wind-technology.html', 'Technology'), ('wind-manufacturing.html', 'Manufacturing'), 
          ('wind-markets.html', 'Markets'), ('wind-policy.html', 'Policy')]),
        
        ('wind-onshore.html', 'Onshore Wind', 'Land-based wind farms and onshore wind technology', 'wind',
         [('wind.html', 'All Wind'), ('wind-offshore.html', 'Offshore'), ('wind-onshore.html', 'Onshore'), 
          ('wind-technology.html', 'Technology'), ('wind-manufacturing.html', 'Manufacturing'), 
          ('wind-markets.html', 'Markets'), ('wind-policy.html', 'Policy')]),
          
        ('wind-technology.html', 'Wind Technology', 'Wind turbine innovations and technology advances', 'wind',
         [('wind.html', 'All Wind'), ('wind-offshore.html', 'Offshore'), ('wind-onshore.html', 'Onshore'), 
          ('wind-technology.html', 'Technology'), ('wind-manufacturing.html', 'Manufacturing'), 
          ('wind-markets.html', 'Markets'), ('wind-policy.html', 'Policy')]),
          
        # Battery subcategories  
        ('battery-technology.html', 'Battery Technology', 'Battery chemistry and energy storage innovations', 'battery',
         [('battery.html', 'All Storage'), ('battery-residential.html', 'Home Storage'), ('battery-utility.html', 'Utility Scale'),
          ('battery-technology.html', 'Technology'), ('battery-manufacturing.html', 'Manufacturing'),
          ('battery-markets.html', 'Markets'), ('battery-policy.html', 'Policy')]),
          
        # Grid subcategories
        ('grid-smart.html', 'Smart Grid', 'Smart grid technology and grid modernization', 'grid',
         [('grid.html', 'All Grid Tech'), ('grid-smart.html', 'Smart Grid'), ('grid-transmission.html', 'Transmission'),
          ('grid-storage.html', 'Storage'), ('grid-markets.html', 'Markets'), ('grid-policy.html', 'Policy')]),
          
        # Markets subcategories
        ('markets-investment.html', 'Clean Energy Investment', 'Renewable energy investment and funding', 'markets',
         [('markets.html', 'All Markets'), ('markets-investment.html', 'Investment'), ('markets-corporate.html', 'Corporate'),
          ('markets-trading.html', 'Trading'), ('markets-analysis.html', 'Analysis'), ('markets-policy.html', 'Policy')]),
          
        # More wind subcategories
        ('wind-manufacturing.html', 'Wind Manufacturing', 'Wind turbine production and manufacturing', 'wind',
         [('wind.html', 'All Wind'), ('wind-offshore.html', 'Offshore'), ('wind-onshore.html', 'Onshore'), 
          ('wind-technology.html', 'Technology'), ('wind-manufacturing.html', 'Manufacturing'), 
          ('wind-markets.html', 'Markets'), ('wind-policy.html', 'Policy')]),
        
        ('wind-markets.html', 'Wind Markets', 'Wind energy investment and market trends', 'wind',
         [('wind.html', 'All Wind'), ('wind-offshore.html', 'Offshore'), ('wind-onshore.html', 'Onshore'), 
          ('wind-technology.html', 'Technology'), ('wind-manufacturing.html', 'Manufacturing'), 
          ('wind-markets.html', 'Markets'), ('wind-policy.html', 'Policy')]),
        
        ('wind-policy.html', 'Wind Policy', 'Wind energy policies and regulations', 'wind',
         [('wind.html', 'All Wind'), ('wind-offshore.html', 'Offshore'), ('wind-onshore.html', 'Onshore'), 
          ('wind-technology.html', 'Technology'), ('wind-manufacturing.html', 'Manufacturing'), 
          ('wind-markets.html', 'Markets'), ('wind-policy.html', 'Policy')]),
          
        # More battery subcategories
        ('battery-manufacturing.html', 'Battery Manufacturing', 'Battery production and manufacturing', 'battery',
         [('battery.html', 'All Storage'), ('battery-residential.html', 'Home Storage'), ('battery-utility.html', 'Utility Scale'),
          ('battery-technology.html', 'Technology'), ('battery-manufacturing.html', 'Manufacturing'),
          ('battery-markets.html', 'Markets'), ('battery-policy.html', 'Policy')]),
          
        ('battery-markets.html', 'Battery Markets', 'Energy storage investment and markets', 'battery',
         [('battery.html', 'All Storage'), ('battery-residential.html', 'Home Storage'), ('battery-utility.html', 'Utility Scale'),
          ('battery-technology.html', 'Technology'), ('battery-manufacturing.html', 'Manufacturing'),
          ('battery-markets.html', 'Markets'), ('battery-policy.html', 'Policy')]),
          
        ('battery-policy.html', 'Battery Policy', 'Energy storage policies and regulations', 'battery',
         [('battery.html', 'All Storage'), ('battery-residential.html', 'Home Storage'), ('battery-utility.html', 'Utility Scale'),
          ('battery-technology.html', 'Technology'), ('battery-manufacturing.html', 'Manufacturing'),
          ('battery-markets.html', 'Markets'), ('battery-policy.html', 'Policy')]),
          
        # More grid subcategories
        ('grid-transmission.html', 'Grid Transmission', 'Power transmission and grid infrastructure', 'grid',
         [('grid.html', 'All Grid Tech'), ('grid-smart.html', 'Smart Grid'), ('grid-transmission.html', 'Transmission'),
          ('grid-storage.html', 'Storage'), ('grid-markets.html', 'Markets'), ('grid-policy.html', 'Policy')]),
          
        ('grid-storage.html', 'Grid Storage', 'Grid-scale energy storage systems', 'grid',
         [('grid.html', 'All Grid Tech'), ('grid-smart.html', 'Smart Grid'), ('grid-transmission.html', 'Transmission'),
          ('grid-storage.html', 'Storage'), ('grid-markets.html', 'Markets'), ('grid-policy.html', 'Policy')]),
          
        ('grid-markets.html', 'Grid Markets', 'Electricity markets and grid services', 'grid',
         [('grid.html', 'All Grid Tech'), ('grid-smart.html', 'Smart Grid'), ('grid-transmission.html', 'Transmission'),
          ('grid-storage.html', 'Storage'), ('grid-markets.html', 'Markets'), ('grid-policy.html', 'Policy')]),
          
        ('grid-policy.html', 'Grid Policy', 'Grid regulations and infrastructure policy', 'grid',
         [('grid.html', 'All Grid Tech'), ('grid-smart.html', 'Smart Grid'), ('grid-transmission.html', 'Transmission'),
          ('grid-storage.html', 'Storage'), ('grid-markets.html', 'Markets'), ('grid-policy.html', 'Policy')]),
          
        # More markets subcategories
        ('markets-corporate.html', 'Corporate Procurement', 'Corporate renewable energy purchases', 'markets',
         [('markets.html', 'All Markets'), ('markets-investment.html', 'Investment'), ('markets-corporate.html', 'Corporate'),
          ('markets-trading.html', 'Trading'), ('markets-analysis.html', 'Analysis'), ('markets-policy.html', 'Policy')]),
          
        ('markets-trading.html', 'Energy Trading', 'Power markets and energy trading', 'markets',
         [('markets.html', 'All Markets'), ('markets-investment.html', 'Investment'), ('markets-corporate.html', 'Corporate'),
          ('markets-trading.html', 'Trading'), ('markets-analysis.html', 'Analysis'), ('markets-policy.html', 'Policy')]),
          
        ('markets-analysis.html', 'Market Analysis', 'Energy market forecasts and analysis', 'markets',
         [('markets.html', 'All Markets'), ('markets-investment.html', 'Investment'), ('markets-corporate.html', 'Corporate'),
          ('markets-trading.html', 'Trading'), ('markets-analysis.html', 'Analysis'), ('markets-policy.html', 'Policy')]),
          
        ('markets-policy.html', 'Market Policy', 'Energy market regulations and policy', 'markets',
         [('markets.html', 'All Markets'), ('markets-investment.html', 'Investment'), ('markets-corporate.html', 'Corporate'),
          ('markets-trading.html', 'Trading'), ('markets-analysis.html', 'Analysis'), ('markets-policy.html', 'Policy')]),
          
        # Policy subcategories
        ('policy-federal.html', 'Federal Policy', 'National renewable energy policies and legislation', 'policy',
         [('policy.html', 'All Policy'), ('policy-federal.html', 'Federal'), ('policy-state.html', 'State'),
          ('policy-international.html', 'International'), ('policy-incentives.html', 'Incentives'), ('policy-climate.html', 'Climate')]),
          
        ('policy-state.html', 'State Policy', 'State-level renewable energy policies', 'policy',
         [('policy.html', 'All Policy'), ('policy-federal.html', 'Federal'), ('policy-state.html', 'State'),
          ('policy-international.html', 'International'), ('policy-incentives.html', 'Incentives'), ('policy-climate.html', 'Climate')]),
          
        ('policy-international.html', 'International Policy', 'Global climate and renewable energy policies', 'policy',
         [('policy.html', 'All Policy'), ('policy-federal.html', 'Federal'), ('policy-state.html', 'State'),
          ('policy-international.html', 'International'), ('policy-incentives.html', 'Incentives'), ('policy-climate.html', 'Climate')]),
          
        ('policy-incentives.html', 'Incentives & Credits', 'Tax credits and renewable energy incentives', 'policy',
         [('policy.html', 'All Policy'), ('policy-federal.html', 'Federal'), ('policy-state.html', 'State'),
          ('policy-international.html', 'International'), ('policy-incentives.html', 'Incentives'), ('policy-climate.html', 'Climate')]),
          
        ('policy-climate.html', 'Climate Policy', 'Climate change legislation and carbon policies', 'policy',
         [('policy.html', 'All Policy'), ('policy-federal.html', 'Federal'), ('policy-state.html', 'State'),
          ('policy-international.html', 'International'), ('policy-incentives.html', 'Incentives'), ('policy-climate.html', 'Climate')])
    ]
    
    created = 0
    print("🚀 Creating subcategory pages...\n")
    
    for filename, title, description, category, nav_items in pages_to_create:
        if os.path.exists(filename):
            print(f"⚠️  {filename} already exists")
        else:
            try:
                html = create_page(filename, title, description, category, nav_items)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html)
                print(f"✅ Created {filename}")
                created += 1
            except Exception as e:
                print(f"❌ Error creating {filename}: {e}")
    
    print(f"\n🎉 Created {created} new pages!")

if __name__ == "__main__":
    main()
