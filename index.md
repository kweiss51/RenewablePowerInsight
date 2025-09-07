---
layout: default
---

<style>
/* Main Content */
.main {
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1rem;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 3rem;
}

/* Featured Article */
.featured-article {
    border-bottom: 1px solid #e5e7eb;
    padding-bottom: 2rem;
    margin-bottom: 2rem;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2rem;
    align-items: center;
}

.featured-content h1 {
    font-size: 2.5rem;
    font-weight: bold;
    line-height: 1.2;
    margin-bottom: 1rem;
    color: #000;
}

.featured-content h1 a {
    color: #000;
    text-decoration: none;
}

.featured-content h1 a:hover {
    color: #0066cc;
}

.featured-image {
    width: 100%;
    height: 300px;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.featured-image img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.featured-image:hover img {
    transform: scale(1.05);
}

.article-meta {
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 1rem;
}

.article-excerpt {
    font-size: 1.1rem;
    color: #333;
    line-height: 1.5;
    margin-bottom: 1rem;
}

.read-time {
    color: #666;
    font-size: 0.85rem;
    font-weight: 500;
}

/* Article List */
.article-list {
    list-style: none;
}

.article-item {
    border-bottom: 1px solid #f3f4f6;
    padding: 1.5rem 0;
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 1.5rem;
    align-items: flex-start;
}

.article-item:last-child {
    border-bottom: none;
}

.article-thumbnail {
    width: 100%;
    height: 120px;
    border-radius: 6px;
    overflow: hidden;
    background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
}

.article-thumbnail img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.article-item h2 {
    font-size: 1.3rem;
    font-weight: bold;
    line-height: 1.3;
    margin-bottom: 0.5rem;
}

.article-item h2 a {
    color: #000;
    text-decoration: none;
}

.article-item h2 a:hover {
    color: #0066cc;
}

.article-item .excerpt {
    color: #555;
    font-size: 0.95rem;
    line-height: 1.4;
    margin-bottom: 0.5rem;
}

/* Sidebar */
.sidebar {
    padding-left: 2rem;
}

.sidebar-section {
    margin-bottom: 3rem;
}

.sidebar-title {
    font-size: 1.2rem;
    font-weight: bold;
    color: #000;
    margin-bottom: 1rem;
    border-bottom: 2px solid #000;
    padding-bottom: 0.5rem;
}

.sidebar-list {
    list-style: none;
}

.sidebar-item {
    border-bottom: 1px solid #f3f4f6;
    padding: 1rem 0;
}

.sidebar-item:last-child {
    border-bottom: none;
}

.sidebar-item h3 {
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.3;
    margin-bottom: 0.3rem;
}

.sidebar-item h3 a {
    color: #000;
    text-decoration: none;
}

.sidebar-item h3 a:hover {
    color: #0066cc;
}

.sidebar-meta {
    color: #666;
    font-size: 0.8rem;
}

/* Responsive */
@media (max-width: 768px) {
    .main {
        grid-template-columns: 1fr;
        gap: 2rem;
        padding: 1rem;
    }
    
    .sidebar {
        padding-left: 0;
    }
    
    .featured-article {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .featured-content h1 {
        font-size: 2rem;
    }
    
    .featured-image {
        height: 200px;
    }
    
    .article-item {
        grid-template-columns: 120px 1fr;
        gap: 1rem;
    }
    
    .article-thumbnail {
        height: 80px;
    }
}
</style>

<main class="main">
    <div class="content">
        <!-- Featured Article -->
        <article class="featured-article">
            <div class="featured-content">
                <h1><a href="{{ site.baseurl }}/2025/09/05/breakthrough-in-perovskite-solar-cell-technology-promises-40-percent-efficiency/">Breakthrough in Perovskite Solar Cell Technology Promises 40% Efficiency</a></h1>
                <div class="article-meta">September 5, 2025</div>
                <p class="article-excerpt">Researchers at leading institutions have achieved a groundbreaking advancement in perovskite solar cell technology, demonstrating laboratory efficiencies exceeding 35% while maintaining stability for over 1,000 hours under operational conditions.</p>
                <div class="read-time">5 MIN READ</div>
            </div>
            <div class="featured-image">
                <img src="https://images.unsplash.com/photo-1509391366360-2e959784a276?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80" alt="Advanced Solar Cell Technology" />
            </div>
        </article>

        <!-- Article List -->
        <ul class="article-list">
            <li class="article-item">
                <div class="article-thumbnail">
                    <img src="https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" alt="Global Renewable Energy" />
                </div>
                <div class="article-content">
                    <h2><a href="{{ site.baseurl }}/2025/09/05/global-renewable-energy-capacity-hits-record-3.6-tw-in-2025/">Global Renewable Energy Capacity Hits Record 3.6 TW in 2025</a></h2>
                    <p class="excerpt">The International Renewable Energy Agency reports unprecedented growth in clean energy installations, with solar and wind leading the charge toward a sustainable future.</p>
                    <div class="article-meta">September 5, 2025 • <span class="read-time">4 MIN READ</span></div>
                </div>
            </li>
            
            <li class="article-item">
                <div class="article-thumbnail">
                    <img src="https://images.unsplash.com/photo-1548337138-e87d889cc369?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" alt="Offshore Wind Farms" />
                </div>
                <div class="article-content">
                    <h2><a href="{{ site.baseurl }}/2025/09/05/offshore-wind-farms-generate-record-120-gw-globally-as-costs-plummet/">Offshore Wind Farms Generate Record 120 GW Globally as Costs Plummet</a></h2>
                    <p class="excerpt">Technological advances and economies of scale have driven down offshore wind costs by 60% over the past decade, making it increasingly competitive with fossil fuels.</p>
                    <div class="article-meta">September 5, 2025 • <span class="read-time">6 MIN READ</span></div>
                </div>
            </li>
            
            <li class="article-item">
                <div class="article-thumbnail">
                    <img src="https://images.unsplash.com/photo-1621905251189-08b45d6a269e?ixlib=rb-4.0.3&auto=format&fit=crop&w=400&q=80" alt="Renewable Energy Transition" />
                </div>
                <div class="article-content">
                    <h2><a href="{{ site.baseurl }}/2025/09/05/breaking-renewable-energy-transition-2025-reaches-tipping-point/">Renewable Energy Transition 2025 Reaches Tipping Point</a></h2>
                    <p class="excerpt">Analysis shows global renewable energy capacity expansion accelerating beyond previous forecasts, signaling a fundamental shift in the energy landscape.</p>
                    <div class="article-meta">September 5, 2025 • <span class="read-time">7 MIN READ</span></div>
                </div>
            </li>
        </ul>
    </div>
    
    <aside class="sidebar">
        <div class="sidebar-section">
            <h2 class="sidebar-title">Most Popular</h2>
            <ul class="sidebar-list">
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/breakthrough-in-perovskite-solar-cell-technology-promises-40-percent-efficiency/">Breakthrough in Perovskite Solar Cell Technology</a></h3>
                    <div class="sidebar-meta">5 MIN READ</div>
                </li>
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/offshore-wind-farms-generate-record-120-gw-globally-as-costs-plummet/">Offshore Wind Costs Plummet to Record Lows</a></h3>
                    <div class="sidebar-meta">6 MIN READ</div>
                </li>
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/global-renewable-energy-capacity-hits-record-3.6-tw-in-2025/">Global Renewable Capacity Hits 3.6 TW</a></h3>
                    <div class="sidebar-meta">4 MIN READ</div>
                </li>
            </ul>
        </div>
        
        <div class="sidebar-section">
            <h2 class="sidebar-title">Technology</h2>
            <ul class="sidebar-list">
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/technology-deep-dive-how-renewable-energy-transiti/">How Renewable Energy Transition Works</a></h3>
                    <div class="sidebar-meta">12 MIN READ</div>
                </li>
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/technology-deep-dive-how-ai-powered-energy-managem/">AI-Powered Energy Management Deep Dive</a></h3>
                    <div class="sidebar-meta">15 MIN READ</div>
                </li>
            </ul>
        </div>
        
        <div class="sidebar-section">
            <h2 class="sidebar-title">Markets</h2>
            <ul class="sidebar-list">
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/market-report-renewable-energy-transition-2025-inv/">Renewable Energy Investment Report 2025</a></h3>
                    <div class="sidebar-meta">10 MIN READ</div>
                </li>
                <li class="sidebar-item">
                    <h3><a href="{{ site.baseurl }}/2025/09/05/market-report-offshore-wind-farm-capacity-investme/">Offshore Wind Investment Trends</a></h3>
                    <div class="sidebar-meta">8 MIN READ</div>
                </li>
            </ul>
        </div>
    </aside>
</main>
