"""
Website Analytics Integration Script
Automatically adds tracking code to HTML pages
"""

import os
from pathlib import Path
from typing import List
import re

class AnalyticsIntegrator:
    """Integrates analytics tracking code into website pages"""
    
    def __init__(self, website_root: str = "."):
        self.website_root = Path(website_root)
        
    def get_tracking_script(self) -> str:
        """Generate analytics tracking JavaScript code"""
        return """
<!-- RenewablePowerInsight Analytics -->
<script>
(function() {
    // Analytics configuration
    const ANALYTICS_CONFIG = {
        apiEndpoint: '/api/analytics', // Update this to your analytics endpoint
        trackPageViews: true,
        trackSessions: true,
        trackEvents: true,
        trackConversions: true
    };
    
    // Session tracking
    let sessionId = sessionStorage.getItem('rpi_session_id');
    if (!sessionId) {
        sessionId = 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        sessionStorage.setItem('rpi_session_id', sessionId);
        sessionStorage.setItem('rpi_session_start', new Date().toISOString());
        sessionStorage.setItem('rpi_is_new_user', !localStorage.getItem('rpi_returning_user') ? 'true' : 'false');
        localStorage.setItem('rpi_returning_user', 'true');
    }
    
    // User identification
    let userId = localStorage.getItem('rpi_user_id');
    if (!userId) {
        userId = 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        localStorage.setItem('rpi_user_id', userId);
    }
    
    // Device detection
    function getDeviceType() {
        const userAgent = navigator.userAgent;
        if (/tablet|ipad|playbook|silk/i.test(userAgent)) return 'tablet';
        if (/mobile|iphone|ipod|android|blackberry|opera|mini|windows\\sce|palm|smartphone|iemobile/i.test(userAgent)) return 'mobile';
        return 'desktop';
    }
    
    // Traffic source detection
    function getTrafficSource() {
        const referrer = document.referrer;
        const utm_source = new URLSearchParams(window.location.search).get('utm_source');
        
        if (utm_source) return utm_source;
        if (!referrer) return 'direct';
        
        const hostname = new URL(referrer).hostname;
        if (hostname.includes('google')) return 'google';
        if (hostname.includes('facebook')) return 'facebook';
        if (hostname.includes('twitter')) return 'twitter';
        if (hostname.includes('linkedin')) return 'linkedin';
        if (hostname.includes('youtube')) return 'youtube';
        
        return 'referral';
    }
    
    // Page tracking
    function trackPageView() {
        if (!ANALYTICS_CONFIG.trackPageViews) return;
        
        const pageData = {
            event_type: 'page_view',
            session_id: sessionId,
            user_id: userId,
            page_url: window.location.href,
            page_title: document.title,
            referrer: document.referrer,
            user_agent: navigator.userAgent,
            device_type: getDeviceType(),
            traffic_source: getTrafficSource(),
            timestamp: new Date().toISOString()
        };
        
        // Send to analytics endpoint
        sendAnalytics(pageData);
    }
    
    // Session tracking
    function trackSession() {
        if (!ANALYTICS_CONFIG.trackSessions) return;
        
        const sessionData = {
            event_type: 'session_start',
            session_id: sessionId,
            user_id: userId,
            is_new_user: sessionStorage.getItem('rpi_is_new_user') === 'true',
            device_type: getDeviceType(),
            traffic_source: getTrafficSource(),
            landing_page: window.location.href,
            start_time: sessionStorage.getItem('rpi_session_start'),
            user_agent: navigator.userAgent
        };
        
        sendAnalytics(sessionData);
    }
    
    // Event tracking
    function trackEvent(eventType, properties = {}) {
        if (!ANALYTICS_CONFIG.trackEvents) return;
        
        const eventData = {
            event_type: 'custom_event',
            session_id: sessionId,
            user_id: userId,
            event_name: eventType,
            properties: properties,
            page_url: window.location.href,
            timestamp: new Date().toISOString()
        };
        
        sendAnalytics(eventData);
    }
    
    // Conversion tracking
    function trackConversion(conversionType, value = 0, currency = 'USD') {
        if (!ANALYTICS_CONFIG.trackConversions) return;
        
        const conversionData = {
            event_type: 'conversion',
            session_id: sessionId,
            user_id: userId,
            conversion_type: conversionType,
            value: value,
            currency: currency,
            page_url: window.location.href,
            timestamp: new Date().toISOString()
        };
        
        sendAnalytics(conversionData);
    }
    
    // Send data to analytics endpoint
    function sendAnalytics(data) {
        // For now, log to console (replace with actual API call)
        console.log('RPI Analytics:', data);
        
        // Uncomment when you have an analytics endpoint:
        /*
        fetch(ANALYTICS_CONFIG.apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(error => {
            console.warn('Analytics tracking failed:', error);
        });
        */
    }
    
    // Initialize tracking when page loads
    function initAnalytics() {
        // Track page view
        trackPageView();
        
        // Track session if it's a new session
        if (!sessionStorage.getItem('rpi_session_tracked')) {
            trackSession();
            sessionStorage.setItem('rpi_session_tracked', 'true');
        }
        
        // Track time on page
        let pageLoadTime = Date.now();
        let lastActivityTime = Date.now();
        
        // Update last activity on user interaction
        ['click', 'scroll', 'keypress', 'mousemove'].forEach(event => {
            document.addEventListener(event, () => {
                lastActivityTime = Date.now();
            }, { passive: true });
        });
        
        // Track page exit
        window.addEventListener('beforeunload', () => {
            const timeOnPage = (lastActivityTime - pageLoadTime) / 1000;
            
            const exitData = {
                event_type: 'page_exit',
                session_id: sessionId,
                user_id: userId,
                page_url: window.location.href,
                time_on_page: timeOnPage,
                timestamp: new Date().toISOString()
            };
            
            // Use sendBeacon for reliable exit tracking
            if (navigator.sendBeacon && ANALYTICS_CONFIG.apiEndpoint !== '/api/analytics') {
                navigator.sendBeacon(
                    ANALYTICS_CONFIG.apiEndpoint,
                    JSON.stringify(exitData)
                );
            }
        });
        
        // Auto-track common events
        document.addEventListener('click', (e) => {
            const target = e.target;
            
            // Track link clicks
            if (target.tagName === 'A') {
                trackEvent('link_click', {
                    link_text: target.textContent,
                    link_url: target.href,
                    link_target: target.target
                });
            }
            
            // Track button clicks
            if (target.tagName === 'BUTTON' || target.type === 'submit') {
                trackEvent('button_click', {
                    button_text: target.textContent,
                    button_type: target.type
                });
            }
        });
        
        // Track scroll depth
        let maxScroll = 0;
        let scrollTracked = {};
        
        window.addEventListener('scroll', () => {
            const scrollPercent = Math.round(
                (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100
            );
            
            if (scrollPercent > maxScroll) {
                maxScroll = scrollPercent;
                
                // Track scroll milestones
                [25, 50, 75, 90].forEach(milestone => {
                    if (scrollPercent >= milestone && !scrollTracked[milestone]) {
                        scrollTracked[milestone] = true;
                        trackEvent('scroll_depth', {
                            depth_percent: milestone
                        });
                    }
                });
            }
        });
    }
    
    // Expose tracking functions globally
    window.rpiAnalytics = {
        trackEvent,
        trackConversion,
        getSessionId: () => sessionId,
        getUserId: () => userId
    };
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAnalytics);
    } else {
        initAnalytics();
    }
})();
</script>
<!-- End RenewablePowerInsight Analytics -->
"""
    
    def find_html_files(self) -> List[Path]:
        """Find all HTML files in the website"""
        html_files = []
        
        # Look for HTML files in common locations
        patterns = [
            "*.html",
            "**/*.html"
        ]
        
        for pattern in patterns:
            html_files.extend(self.website_root.glob(pattern))
        
        # Remove duplicates and sort
        html_files = sorted(list(set(html_files)))
        
        return html_files
    
    def has_analytics_tracking(self, file_path: Path) -> bool:
        """Check if file already has analytics tracking"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return 'RenewablePowerInsight Analytics' in content
        except:
            return False
    
    def add_tracking_to_file(self, file_path: Path, backup: bool = True) -> bool:
        """Add analytics tracking to a single HTML file"""
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has tracking
            if self.has_analytics_tracking(file_path):
                return False
            
            # Create backup if requested
            if backup:
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Find the best place to insert tracking code
            tracking_script = self.get_tracking_script()
            
            # Try to insert before closing </head> tag
            if '</head>' in content:
                content = content.replace('</head>', tracking_script + '\n</head>')
            # Otherwise try before closing </body> tag
            elif '</body>' in content:
                content = content.replace('</body>', tracking_script + '\n</body>')
            # Otherwise append to end
            else:
                content += tracking_script
            
            # Write updated content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception as e:
            print(f"Error adding tracking to {file_path}: {e}")
            return False
    
    def integrate_all_pages(self, backup: bool = True) -> dict:
        """Add analytics tracking to all HTML pages"""
        html_files = self.find_html_files()
        
        results = {
            'total_files': len(html_files),
            'updated_files': [],
            'skipped_files': [],
            'errors': []
        }
        
        for html_file in html_files:
            if self.has_analytics_tracking(html_file):
                results['skipped_files'].append(str(html_file))
                continue
            
            if self.add_tracking_to_file(html_file, backup):
                results['updated_files'].append(str(html_file))
            else:
                results['errors'].append(str(html_file))
        
        return results
    
    def remove_tracking_from_file(self, file_path: Path) -> bool:
        """Remove analytics tracking from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the analytics block
            start_marker = '<!-- RenewablePowerInsight Analytics -->'
            end_marker = '<!-- End RenewablePowerInsight Analytics -->'
            
            if start_marker in content and end_marker in content:
                start_pos = content.find(start_marker)
                end_pos = content.find(end_marker) + len(end_marker)
                
                # Remove the analytics block and any surrounding whitespace
                new_content = content[:start_pos] + content[end_pos:]
                new_content = re.sub(r'\\n\\s*\\n\\s*\\n', '\\n\\n', new_content)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                return True
            
            return False
            
        except Exception as e:
            print(f"Error removing tracking from {file_path}: {e}")
            return False
    
    def generate_integration_report(self) -> str:
        """Generate a detailed integration report"""
        html_files = self.find_html_files()
        
        report = []
        report.append("# Analytics Integration Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        total_files = len(html_files)
        tracked_files = sum(1 for f in html_files if self.has_analytics_tracking(f))
        
        report.append(f"## Summary")
        report.append(f"- Total HTML files: {total_files}")
        report.append(f"- Files with analytics: {tracked_files}")
        report.append(f"- Files without analytics: {total_files - tracked_files}")
        report.append("")
        
        # File details
        report.append("## File Details")
        report.append("")
        
        for html_file in html_files:
            has_tracking = self.has_analytics_tracking(html_file)
            status = "✅ Tracked" if has_tracking else "❌ Not tracked"
            report.append(f"- `{html_file}` - {status}")
        
        report.append("")
        report.append("## Integration Instructions")
        report.append("")
        report.append("To integrate analytics tracking:")
        report.append("1. Run the integration script")
        report.append("2. Set up an analytics API endpoint")
        report.append("3. Update the API endpoint in the tracking code")
        report.append("4. Test the tracking functionality")
        
        return "\\n".join(report)


def main():
    """Main integration function"""
    integrator = AnalyticsIntegrator()
    
    print("🔍 Scanning for HTML files...")
    html_files = integrator.find_html_files()
    print(f"Found {len(html_files)} HTML files")
    
    # Show current status
    tracked_count = sum(1 for f in html_files if integrator.has_analytics_tracking(f))
    print(f"📊 Files with analytics: {tracked_count}")
    print(f"📄 Files without analytics: {len(html_files) - tracked_count}")
    
    if tracked_count == len(html_files):
        print("✅ All files already have analytics tracking!")
        return
    
    # Ask user if they want to proceed
    response = input("\\n🚀 Add analytics tracking to all HTML files? (y/n): ").lower()
    
    if response == 'y':
        print("\\n📝 Adding analytics tracking...")
        results = integrator.integrate_all_pages(backup=True)
        
        print(f"\\n✅ Integration complete!")
        print(f"📊 Updated files: {len(results['updated_files'])}")
        print(f"⏭️  Skipped files: {len(results['skipped_files'])}")
        print(f"❌ Errors: {len(results['errors'])}")
        
        if results['updated_files']:
            print("\\n📝 Updated files:")
            for file in results['updated_files']:
                print(f"  - {file}")
        
        if results['errors']:
            print("\\n❌ Errors:")
            for file in results['errors']:
                print(f"  - {file}")
        
        print("\\n💾 Backup files created with .backup extension")
        print("🔧 Next: Update the API endpoint in the tracking code")


if __name__ == "__main__":
    from datetime import datetime
    main()
