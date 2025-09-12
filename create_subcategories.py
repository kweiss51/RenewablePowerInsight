#!/usr/bin/env python3
"""
Quick script to create all missing subcategory pages
"""

import os

# Define the subcategories for each main category
SUBCATEGORIES = {
    'wind': [
        ('wind-offshore', 'Offshore Wind', 'Offshore wind farms, floating turbines, and marine wind energy'),
        ('wind-onshore', 'Onshore Wind', 'Land-based wind farms, turbine technology, and onshore installations'),
        ('wind-technology', 'Wind Technology', 'Wind turbine innovations, blade design, and efficiency improvements'),
        ('wind-manufacturing', 'Wind Manufacturing', 'Wind turbine production, supply chain, and manufacturing capacity'),
        ('wind-markets', 'Wind Markets & Finance', 'Wind investment, market trends, and financing models'),
        ('wind-policy', 'Wind Policy', 'Wind energy policies, regulations, and government incentives'),
    ],
    'battery': [
        ('battery-residential', 'Home Energy Storage', 'Residential battery systems, home backup power, and distributed storage'),
        ('battery-utility', 'Utility-Scale Storage', 'Grid-scale battery installations and utility storage projects'),
        ('battery-technology', 'Battery Technology', 'Battery chemistry innovations, solid-state batteries, and energy density'),
        ('battery-manufacturing', 'Battery Manufacturing', 'Battery production, gigafactories, and manufacturing processes'),
        ('battery-markets', 'Battery Markets & Finance', 'Battery investment, market growth, and cost analysis'),
        ('battery-policy', 'Battery Policy', 'Energy storage policies, regulations, and government support'),
    ],
    'grid': [
        ('grid-smart', 'Smart Grid', 'Smart grid technology, digital infrastructure, and grid modernization'),
        ('grid-transmission', 'Transmission', 'High-voltage transmission lines and grid interconnection'),
        ('grid-distribution', 'Distribution', 'Distribution networks, microgrids, and local energy systems'),
        ('grid-storage', 'Grid Storage', 'Grid-scale energy storage and system integration'),
        ('grid-markets', 'Grid Markets', 'Electricity markets, grid economics, and energy trading'),
        ('grid-policy', 'Grid Policy', 'Grid regulations, interconnection policies, and infrastructure planning'),
    ],
    'markets': [
        ('markets-investment', 'Investment Trends', 'Renewable energy investment, funding, and capital flows'),
        ('markets-trading', 'Energy Trading', 'Power purchase agreements, energy trading, and market mechanisms'),
        ('markets-finance', 'Project Finance', 'Project financing, green bonds, and financial instruments'),
        ('markets-analysis', 'Market Analysis', 'Market research, trends analysis, and industry forecasts'),
        ('markets-pricing', 'Energy Pricing', 'Electricity prices, cost analysis, and market dynamics'),
        ('markets-policy', 'Market Policy', 'Market regulations, policy impacts, and regulatory frameworks'),
    ],
    'policy': [
        ('policy-federal', 'Federal Policy', 'National renewable energy policies and federal regulations'),
        ('policy-state', 'State & Local', 'State policies, local initiatives, and regional programs'),
        ('policy-international', 'International', 'Global climate policies, international agreements, and cooperation'),
        ('policy-incentives', 'Incentives', 'Tax credits, subsidies, and financial incentives'),
        ('policy-regulation', 'Regulation', 'Environmental regulations, permitting, and compliance'),
        ('policy-climate', 'Climate Policy', 'Climate change policies, carbon pricing, and emissions targets'),
    ]
}

# HTML template for subcategory pages
HTML_TEMPLATE = '''<!DOCTYPE html>
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
        .main {{ max-width: 1200px; margin: 0 auto; padding: 30px 20px; }}
        .page-header {{ margin-bottom: 30px; }}
        .page-header h1 {{ font-size: 2.2rem; font-weight: 700; color: #2d5016; margin-bottom: 10px; }}
        .page-header p {{ font-size: 1.1rem; color: #666; }}
        .content {{ font-size: 1rem; line-height: 1.6; color: #333; }}
        @media (max-width: 768px) {{
            .site-header .wrapper {{ flex-direction: column; gap: 15px; }}
            .site-nav {{ flex-wrap: wrap; justify-content: center; gap: 1rem; }}
            .sub-nav {{ justify-content: center; gap: 1rem; }}
            .page-header h1 {{ font-size: 1.8rem; }}
        }}
    </style>
</head>
<body>
    <header class="site-header">
        <div class="wrapper">
            <a class="site-title" href="/">Renewable Power Insight</a>
            <nav class="site-nav">
                <a href="/">Home</a>
                <a href="posts.html">All Posts</a>
                <a href="solar.html"{solar_active}>Solar</a>
                <a href="wind.html"{wind_active}>Wind</a>
                <a href="battery.html"{battery_active}>Battery Storage</a>
                <a href="grid.html"{grid_active}>Grid Tech</a>
                <a href="markets.html"{markets_active}>Markets</a>
                <a href="policy.html"{policy_active}>Policy</a>
            </nav>
        </div>
    </header>
    {subnav_html}
    <main class="main">
        <div class="page-header">
            <h1>{title}</h1>
            <p>{description}</p>
        </div>
        <div class="content">
            <p>Content for {title} coming soon. This page will feature the latest news, analysis, and insights about {description.lower()}.</p>
        </div>
    </main>
</body>
</html>'''

def create_subcategory_page(category, slug, title, description):
    """Create a subcategory page"""
    
    # Determine active navigation
    active_flags = {
        'solar_active': ' class="active"' if category == 'solar' else '',
        'wind_active': ' class="active"' if category == 'wind' else '',
        'battery_active': ' class="active"' if category == 'battery' else '',
        'grid_active': ' class="active"' if category == 'grid' else '',
        'markets_active': ' class="active"' if category == 'markets' else '',
        'policy_active': ' class="active"' if category == 'policy' else '',
    }
    
    # Create sub-navigation HTML
    subnav_links = []
    for sub_slug, sub_title, _ in SUBCATEGORIES[category]:
        active_class = ' class="active"' if sub_slug == slug else ''
        subnav_links.append(f'<a href="{sub_slug}.html"{active_class}>{sub_title}</a>')
    
    subnav_html = f'''
    <div class="sub-nav-bar">
        <div class="wrapper">
            <nav class="sub-nav">
                <a href="{category}.html">All {category.title()}</a>
                {' '.join(subnav_links)}
            </nav>
        </div>
    </div>'''
    
    # Generate HTML
    html = HTML_TEMPLATE.format(
        title=title,
        description=description,
        subnav_html=subnav_html,
        **active_flags
    )
    
    # Write file
    filename = f"{slug}.html"
    with open(filename, 'w') as f:
        f.write(html)
    
    return filename

def main():
    """Create all subcategory pages"""
    created_files = []
    
    print("🚀 Creating subcategory pages...")
    
    for category, subcategories in SUBCATEGORIES.items():
        print(f"\n📁 Creating {category} subcategories:")
        
        for slug, title, description in subcategories:
            filename = create_subcategory_page(category, slug, title, description)
            created_files.append(filename)
            print(f"  ✅ {filename}")
    
    print(f"\n🎉 Successfully created {len(created_files)} subcategory pages!")
    return created_files

if __name__ == "__main__":
    main()
