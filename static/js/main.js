// Energy Blog JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('⚡ Energy Blog loaded successfully!');
    
    // Refresh content button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.disabled = true;
            this.textContent = '🔄 Refreshing...';
            
            fetch('/api/scrape', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification('✅ Content refreshed successfully!', 'success');
                        setTimeout(() => location.reload(), 2000);
                    } else {
                        showNotification('❌ Error refreshing content', 'error');
                    }
                })
                .catch(error => {
                    showNotification('❌ Network error', 'error');
                    console.error('Error:', error);
                })
                .finally(() => {
                    this.disabled = false;
                    this.textContent = '🔄 Refresh Content';
                });
        });
    }
    
    // Generate now button
    const generateBtn = document.getElementById('generate-btn');
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            this.disabled = true;
            this.textContent = '🚀 Generating...';
            
            fetch('/api/scrape', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showNotification(`✅ Generated ${data.posts_count} new posts!`, 'success');
                        setTimeout(() => location.reload(), 2000);
                    } else {
                        showNotification('❌ Error generating content', 'error');
                    }
                })
                .catch(error => {
                    showNotification('❌ Network error', 'error');
                    console.error('Error:', error);
                })
                .finally(() => {
                    this.disabled = false;
                    this.textContent = '🚀 Generate Now';
                });
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Auto-refresh stats every 30 seconds on admin page
    if (window.location.pathname === '/admin') {
        setInterval(updateStats, 30000);
    }
    
    // Add loading animations to cards
    addCardAnimations();
    
    // Initialize tooltips
    initTooltips();
});

function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) {
        existing.remove();
    }
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span>${message}</span>
            <button class="notification-close">&times;</button>
        </div>
    `;
    
    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        animation: slideIn 0.3s ease-out;
        max-width: 400px;
    `;
    
    // Add type-specific styles
    if (type === 'success') {
        notification.style.backgroundColor = '#ecfdf5';
        notification.style.color = '#10b981';
        notification.style.border = '1px solid #a7f3d0';
    } else if (type === 'error') {
        notification.style.backgroundColor = '#fef2f2';
        notification.style.color = '#ef4444';
        notification.style.border = '1px solid #fecaca';
    } else {
        notification.style.backgroundColor = '#eff6ff';
        notification.style.color = '#1e40af';
        notification.style.border = '1px solid #bfdbfe';
    }
    
    // Add to page
    document.body.appendChild(notification);
    
    // Add close functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.style.cssText = `
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        margin-left: 1rem;
        opacity: 0.7;
    `;
    
    closeBtn.addEventListener('click', () => {
        notification.remove();
    });
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function updateStats() {
    fetch('/api/posts')
        .then(response => response.json())
        .then(data => {
            // Update any visible stats
            const statsElements = document.querySelectorAll('[data-stat]');
            statsElements.forEach(element => {
                const statType = element.getAttribute('data-stat');
                if (data[statType] !== undefined) {
                    element.textContent = data[statType];
                }
            });
        })
        .catch(error => {
            console.log('Stats update failed:', error);
        });
}

function addCardAnimations() {
    // Add intersection observer for card animations
    const cards = document.querySelectorAll('.post-card, .stat-card, .action-card, .topic-card');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeInUp 0.6s ease-out';
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '50px'
    });
    
    cards.forEach(card => {
        observer.observe(card);
    });
    
    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(100%);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
    `;
    document.head.appendChild(style);
}

function initTooltips() {
    // Add tooltips to emoji elements
    const emojiElements = document.querySelectorAll('[title]');
    emojiElements.forEach(element => {
        element.style.cursor = 'help';
    });
}

// Utility function to format dates
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Utility function to estimate reading time
function estimateReadingTime(wordCount) {
    const wordsPerMinute = 200;
    const minutes = Math.ceil(wordCount / wordsPerMinute);
    return `${minutes} min read`;
}

// Add reading time indicators
document.addEventListener('DOMContentLoaded', function() {
    const wordCountElements = document.querySelectorAll('.word-count');
    wordCountElements.forEach(element => {
        const text = element.textContent;
        const wordCount = parseInt(text.match(/\d+/));
        if (wordCount) {
            const readingTime = estimateReadingTime(wordCount);
            element.title = `Estimated reading time: ${readingTime}`;
        }
    });
});

// Performance monitoring
window.addEventListener('load', function() {
    const loadTime = performance.now();
    console.log(`⚡ Page loaded in ${Math.round(loadTime)}ms`);
    
    // Report to analytics if available
    if (typeof gtag !== 'undefined') {
        gtag('event', 'page_load_time', {
            custom_parameter: Math.round(loadTime)
        });
    }
});
