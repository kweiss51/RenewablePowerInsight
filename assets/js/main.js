// Renewable Power Insight - RSS Feed Integration & Interactive Features

class EnergyNewsAggregator {
  constructor() {
    this.apiKey = 'YOUR_RSS2JSON_API_KEY'; // Replace with actual API key
    this.feeds = [
      {
        name: "Reuters Energy",
        url: "https://feeds.reuters.com/reuters/environment",
        category: "news",
        index: 1
      },
      {
        name: "CleanTechnica",
        url: "https://cleantechnica.com/feed/",
        category: "technology",
        index: 2
      },
      {
        name: "Renewable Energy World",
        url: "https://www.renewableenergyworld.com/rss.xml",
        category: "industry", 
        index: 3
      },
      {
        name: "Solar Power World",
        url: "https://www.solarpowerworldonline.com/feed/",
        category: "solar",
        index: 4
      },
      {
        name: "Wind Power Engineering",
        url: "https://www.windpowerengineering.com/feed/",
        category: "wind",
        index: 5
      }
    ];
    
    this.newsItems = [
      "Global renewable energy capacity hits new record in 2025",
      "Solar prices drop 15% year-over-year as production scales",
      "New battery storage projects announced across 12 states", 
      "EV sales surge 40% in Q3 2025 as charging infrastructure expands",
      "Offshore wind farms generate record 50GW globally",
      "Green hydrogen production costs fall below $2/kg milestone",
      "Tesla Megapack installations triple in renewable energy projects",
      "European Union announces €500B clean energy investment plan",
      "China leads global solar panel manufacturing with 70% market share",
      "US offshore wind pipeline reaches 100GW development milestone"
    ];
    
    this.init();
  }

  async init() {
    this.initNewsTicker();
    await this.loadAllFeeds();
    this.initNewsletterForm();
    this.initSmoothScrolling();
    this.initScrollAnimations();
  }

  // RSS Feed Loading with fallback to mock data
  async loadAllFeeds() {
    const feedPromises = this.feeds.map(feed => this.loadSingleFeed(feed));
    await Promise.allSettled(feedPromises);
  }

  async loadSingleFeed(feed) {
    try {
      // Try RSS2JSON API first
      const response = await fetch(
        `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(feed.url)}&api_key=${this.apiKey}&count=5`,
        { timeout: 5000 }
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'ok' && data.items) {
          this.displayFeedItems(feed.index, data.items, feed.category, feed.name);
          return;
        }
      }
      
      // Fallback to CORS proxy
      await this.loadFeedWithProxy(feed);
      
    } catch (error) {
      console.error(`Error loading ${feed.name}:`, error);
      this.displayMockFeedItems(feed);
    }
  }

  async loadFeedWithProxy(feed) {
    try {
      const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(feed.url)}`;
      const response = await fetch(proxyUrl);
      const xmlText = await response.text();
      
      const parser = new DOMParser();
      const xmlDoc = parser.parseFromString(xmlText, 'text/xml');
      const items = this.parseRSSXML(xmlDoc);
      
      this.displayFeedItems(feed.index, items, feed.category, feed.name);
    } catch (error) {
      console.error(`Proxy loading failed for ${feed.name}:`, error);
      this.displayMockFeedItems(feed);
    }
  }

  parseRSSXML(xmlDoc) {
    const items = [];
    const itemNodes = xmlDoc.querySelectorAll('item');
    
    itemNodes.forEach((item, index) => {
      if (index < 5) { // Limit to 5 items
        const title = item.querySelector('title')?.textContent || 'No title';
        const link = item.querySelector('link')?.textContent || '#';
        const description = item.querySelector('description')?.textContent || '';
        const pubDate = item.querySelector('pubDate')?.textContent || new Date().toISOString();
        
        items.push({
          title: title.trim(),
          link: link.trim(),
          description: this.stripHTML(description).substring(0, 150),
          pubDate: pubDate
        });
      }
    });
    
    return items;
  }

  stripHTML(html) {
    const doc = new DOMParser().parseFromString(html, 'text/html');
    return doc.body.textContent || '';
  }

  displayFeedItems(feedIndex, items, category, feedName) {
    const container = document.getElementById(`feed-${feedIndex}`);
    if (!container) return;

    const html = items.map(item => `
      <div class="feed-item">
        <h4><a href="${item.link}" target="_blank" rel="noopener">${item.title}</a></h4>
        <p class="feed-excerpt">${item.description || ''}</p>
        <span class="feed-date">${this.formatDate(item.pubDate)}</span>
      </div>
    `).join('');

    container.innerHTML = html;
    
    // Add analytics tracking
    container.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        this.trackFeedClick(feedName, item.title);
      });
    });
  }

  displayMockFeedItems(feed) {
    const mockItems = this.generateMockItems(feed.category);
    this.displayFeedItems(feed.index, mockItems, feed.category, feed.name);
  }

  generateMockItems(category) {
    const mockData = {
      news: [
        { title: "Renewable Energy Investment Reaches $2.8 Trillion Globally", description: "Record investment in clean energy technologies drives unprecedented growth in renewable capacity installations worldwide.", pubDate: new Date().toISOString() },
        { title: "Solar Power Costs Hit New Low in Competitive Auction", description: "Latest solar energy auction results show continued price decline, making renewables the cheapest power source.", pubDate: new Date(Date.now() - 86400000).toISOString() },
        { title: "Battery Storage Market Explodes with Grid-Scale Projects", description: "Energy storage deployments accelerate as utilities invest in grid stabilization and renewable integration.", pubDate: new Date(Date.now() - 172800000).toISOString() }
      ],
      technology: [
        { title: "Next-Generation Perovskite Solar Cells Achieve 31% Efficiency", description: "Breakthrough in solar cell technology promises higher efficiency and lower manufacturing costs for future installations.", pubDate: new Date().toISOString() },
        { title: "AI Optimizes Wind Farm Performance by 25%", description: "Machine learning algorithms improve turbine operations and maintenance scheduling for maximum energy output.", pubDate: new Date(Date.now() - 86400000).toISOString() },
        { title: "Floating Solar Installations Gain Momentum Worldwide", description: "Innovative floating photovoltaic systems offer new opportunities for solar deployment on water bodies.", pubDate: new Date(Date.now() - 172800000).toISOString() }
      ],
      solar: [
        { title: "Agrivoltaics: Combining Solar Power with Agriculture", description: "Dual-use solar installations provide clean energy while maintaining agricultural productivity and crop yields.", pubDate: new Date().toISOString() },
        { title: "Solar Panel Recycling Technology Advances Sustainability", description: "New recycling methods recover 95% of materials from end-of-life solar panels, supporting circular economy.", pubDate: new Date(Date.now() - 86400000).toISOString() },
        { title: "Building-Integrated Solar Transforms Urban Landscapes", description: "BIPV technology seamlessly integrates solar generation into building facades and roofing systems.", pubDate: new Date(Date.now() - 172800000).toISOString() }
      ],
      wind: [
        { title: "Offshore Wind Turbines Reach 15MW Capacity Milestone", description: "Latest generation offshore turbines deliver unprecedented power output, reducing cost per megawatt-hour.", pubDate: new Date().toISOString() },
        { title: "Wind-Solar Hybrid Projects Optimize Land Use Efficiency", description: "Co-located renewable projects maximize energy generation and grid stability through complementary resources.", pubDate: new Date(Date.now() - 86400000).toISOString() },
        { title: "Vertical Axis Wind Turbines Enter Commercial Market", description: "Innovative turbine designs offer new options for urban and distributed wind energy applications.", pubDate: new Date(Date.now() - 172800000).toISOString() }
      ],
      industry: [
        { title: "Corporate Renewable Energy Procurement Hits Record High", description: "Fortune 500 companies accelerate clean energy purchasing through long-term power purchase agreements.", pubDate: new Date().toISOString() },
        { title: "Green Financing Drives Clean Energy Project Development", description: "Sustainable finance instruments mobilize capital for renewable energy and energy efficiency investments.", pubDate: new Date(Date.now() - 86400000).toISOString() },
        { title: "Energy Transition Creates Millions of Clean Jobs Globally", description: "Renewable energy sector employment grows rapidly, outpacing job losses in fossil fuel industries.", pubDate: new Date(Date.now() - 172800000).toISOString() }
      ]
    };

    return mockData[category] || mockData.news;
  }

  formatDate(dateString) {
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric'
      });
    } catch (error) {
      return 'Recent';
    }
  }

  // News Ticker
  initNewsTicker() {
    const ticker = document.getElementById('news-ticker');
    if (!ticker) return;

    let currentIndex = 0;
    
    const showNextNews = () => {
      ticker.style.opacity = '0';
      setTimeout(() => {
        ticker.textContent = this.newsItems[currentIndex];
        ticker.style.opacity = '1';
        currentIndex = (currentIndex + 1) % this.newsItems.length;
      }, 300);
    };
    
    showNextNews();
    setInterval(showNextNews, 4000);
  }

  // Newsletter Form
  initNewsletterForm() {
    const form = document.getElementById('newsletter-form');
    if (!form) return;

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = form.querySelector('input[type="email"]').value;
      
      if (this.validateEmail(email)) {
        this.handleNewsletterSignup(email);
      } else {
        this.showNotification('Please enter a valid email address', 'error');
      }
    });
  }

  validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  async handleNewsletterSignup(email) {
    try {
      // Here you would integrate with your email service (e.g., Mailchimp, ConvertKit)
      // For demo purposes, we'll simulate the signup
      
      const button = document.querySelector('#newsletter-form button');
      const originalText = button.textContent;
      
      button.textContent = 'Subscribing...';
      button.disabled = true;
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      this.showNotification('🎉 Thank you for subscribing! You\'ll receive the latest energy insights.', 'success');
      document.getElementById('newsletter-form').reset();
      
      button.textContent = originalText;
      button.disabled = false;
      
      // Track conversion
      this.trackNewsletterSignup(email);
      
    } catch (error) {
      console.error('Newsletter signup error:', error);
      this.showNotification('Subscription failed. Please try again later.', 'error');
    }
  }

  // Smooth Scrolling
  initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', (e) => {
        e.preventDefault();
        const target = document.querySelector(anchor.getAttribute('href'));
        if (target) {
          target.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
          });
        }
      });
    });
  }

  // Scroll Animations
  initScrollAnimations() {
    const observerOptions = {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in-up');
        }
      });
    }, observerOptions);

    // Observe elements
    document.querySelectorAll('.post-card, .feed-card, .category-card').forEach(el => {
      observer.observe(el);
    });
  }

  // Notification System
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-message">${message}</span>
        <button class="notification-close">&times;</button>
      </div>
    `;

    // Add styles
    Object.assign(notification.style, {
      position: 'fixed',
      top: '20px',
      right: '20px',
      zIndex: '10000',
      maxWidth: '400px',
      padding: '1rem',
      borderRadius: '8px',
      boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
      transform: 'translateX(100%)',
      transition: 'transform 0.3s ease',
      backgroundColor: type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6',
      color: 'white'
    });

    document.body.appendChild(notification);

    // Animate in
    setTimeout(() => {
      notification.style.transform = 'translateX(0)';
    }, 100);

    // Close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
      this.closeNotification(notification);
    });

    // Auto close after 5 seconds
    setTimeout(() => {
      this.closeNotification(notification);
    }, 5000);
  }

  closeNotification(notification) {
    notification.style.transform = 'translateX(100%)';
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 300);
  }

  // Analytics Tracking
  trackFeedClick(feedName, articleTitle) {
    // Google Analytics 4 event tracking
    if (typeof gtag !== 'undefined') {
      gtag('event', 'feed_article_click', {
        feed_name: feedName,
        article_title: articleTitle,
        event_category: 'RSS Feeds'
      });
    }
    
    console.log(`Tracked click: ${feedName} - ${articleTitle}`);
  }

  trackNewsletterSignup(email) {
    // Track newsletter signups
    if (typeof gtag !== 'undefined') {
      gtag('event', 'newsletter_signup', {
        method: 'website_form',
        event_category: 'Lead Generation'
      });
    }
    
    console.log('Tracked newsletter signup:', email);
  }

  // Search Functionality
  initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    
    if (!searchInput) return;

    let searchTimeout;
    
    searchInput.addEventListener('input', (e) => {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        this.performSearch(e.target.value);
      }, 300);
    });
  }

  async performSearch(query) {
    if (query.length < 3) return;
    
    // This would integrate with your search backend
    // For now, we'll search through feed items
    const results = this.searchFeedItems(query);
    this.displaySearchResults(results);
  }

  searchFeedItems(query) {
    const allFeedItems = document.querySelectorAll('.feed-item');
    const results = [];
    
    allFeedItems.forEach(item => {
      const title = item.querySelector('h4 a').textContent;
      const description = item.querySelector('.feed-excerpt')?.textContent || '';
      
      if (title.toLowerCase().includes(query.toLowerCase()) || 
          description.toLowerCase().includes(query.toLowerCase())) {
        results.push({
          title,
          description,
          link: item.querySelector('h4 a').href
        });
      }
    });
    
    return results;
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new EnergyNewsAggregator();
});

// Performance optimization
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js')
      .then(registration => {
        console.log('SW registered: ', registration);
      })
      .catch(registrationError => {
        console.log('SW registration failed: ', registrationError);
      });
  });
}
