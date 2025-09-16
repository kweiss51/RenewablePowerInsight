"""
Website Analytics Tracking System for RenewablePowerInsight
Based on HubSpot's 16 Key Website Engagement Metrics

This system tracks and analyzes the following metrics:
1. Views (Page Views)
2. Average Time on Page
3. Average Session Duration  
4. Views per User/Pages per Session
5. Engagement Rate/Bounce Rate
6. Traffic Sources
7. Social Referrals
8. New Visitor Sessions/New Users
9. Returning Visitor Sessions
10. Device Type
11. Conversion Rate
12. Exit Rate
13. Top Pages
14. Top Exit Pages
15. Revenue Attribution
16. Event Tracking
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
from collections import defaultdict
import statistics

@dataclass
class PageView:
    """Represents a single page view event"""
    id: str
    timestamp: datetime
    session_id: str
    user_id: str
    page_url: str
    page_title: str
    referrer: str
    user_agent: str
    ip_address: str
    time_on_page: Optional[float] = None  # in seconds
    scroll_depth: Optional[float] = None  # percentage
    exit_page: bool = False
    
@dataclass
class Session:
    """Represents a user session"""
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime]
    page_views: int = 0
    duration: Optional[float] = None  # in seconds
    device_type: str = "desktop"
    browser: str = "unknown"
    operating_system: str = "unknown"
    traffic_source: str = "direct"
    is_new_user: bool = True
    conversions: int = 0
    bounce: bool = False

@dataclass
class User:
    """Represents a unique website user"""
    id: str
    first_visit: datetime
    last_visit: datetime
    total_sessions: int = 1
    total_page_views: int = 1
    total_time_on_site: float = 0.0  # in seconds
    device_preferences: Dict[str, int] = None
    conversion_events: List[str] = None
    
    def __post_init__(self):
        if self.device_preferences is None:
            self.device_preferences = {}
        if self.conversion_events is None:
            self.conversion_events = []

@dataclass
class ConversionEvent:
    """Represents a conversion event"""
    id: str
    session_id: str
    user_id: str
    timestamp: datetime
    event_type: str  # 'form_submit', 'newsletter_signup', 'download', etc.
    page_url: str
    value: Optional[float] = None  # monetary value if applicable
    
@dataclass 
class SocialReferral:
    """Represents traffic from social media"""
    session_id: str
    platform: str  # 'twitter', 'facebook', 'linkedin', etc.
    campaign: Optional[str] = None
    organic: bool = True

class WebsiteAnalytics:
    """Main analytics tracking and reporting class"""
    
    def __init__(self, db_path: str = "analytics/website_analytics.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self.init_database()
        
        # Traffic source patterns
        self.traffic_sources = {
            'organic_search': [
                'google.com', 'bing.com', 'yahoo.com', 'duckduckgo.com',
                'baidu.com', 'yandex.com', 'ecosia.org'
            ],
            'social_media': {
                'facebook': ['facebook.com', 'fb.com', 'm.facebook.com'],
                'twitter': ['twitter.com', 'x.com', 't.co'],
                'linkedin': ['linkedin.com', 'lnkd.in'],
                'instagram': ['instagram.com'],
                'youtube': ['youtube.com', 'youtu.be'],
                'tiktok': ['tiktok.com'],
                'reddit': ['reddit.com'],
                'pinterest': ['pinterest.com', 'pin.it']
            },
            'email': ['mail.google.com', 'outlook.com', 'yahoo.com/mail'],
            'paid_search': ['googleads.', 'bingads.', 'ads.yahoo.']
        }
        
    def init_database(self):
        """Initialize SQLite database with all necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Page Views table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS page_views (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                page_url TEXT NOT NULL,
                page_title TEXT NOT NULL,
                referrer TEXT,
                user_agent TEXT,
                ip_address TEXT,
                time_on_page REAL,
                scroll_depth REAL,
                exit_page BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (session_id) REFERENCES sessions (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                page_views INTEGER DEFAULT 0,
                duration REAL,
                device_type TEXT DEFAULT 'desktop',
                browser TEXT DEFAULT 'unknown',
                operating_system TEXT DEFAULT 'unknown',
                traffic_source TEXT DEFAULT 'direct',
                is_new_user BOOLEAN DEFAULT TRUE,
                conversions INTEGER DEFAULT 0,
                bounce BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                first_visit TEXT NOT NULL,
                last_visit TEXT NOT NULL,
                total_sessions INTEGER DEFAULT 1,
                total_page_views INTEGER DEFAULT 1,
                total_time_on_site REAL DEFAULT 0.0,
                device_preferences TEXT,
                conversion_events TEXT
            )
        ''')
        
        # Conversions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversions (
                id TEXT PRIMARY KEY,
                session_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                page_url TEXT NOT NULL,
                value REAL,
                FOREIGN KEY (session_id) REFERENCES sessions (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Social Referrals table  
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_referrals (
                session_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                campaign TEXT,
                organic BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Create indexes for better query performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_views_timestamp ON page_views (timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_page_views_session ON page_views (session_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_timestamp ON sessions (start_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions (user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversions_timestamp ON conversions (timestamp)')
        
        conn.commit()
        conn.close()
    
    def track_page_view(
        self, 
        page_url: str,
        page_title: str,
        session_id: str,
        user_id: str,
        referrer: str = "",
        user_agent: str = "",
        ip_address: str = "",
        time_on_page: Optional[float] = None,
        scroll_depth: Optional[float] = None
    ) -> str:
        """Track a page view event"""
        
        page_view_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO page_views (
                id, timestamp, session_id, user_id, page_url, page_title,
                referrer, user_agent, ip_address, time_on_page, scroll_depth
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            page_view_id, timestamp, session_id, user_id, page_url, page_title,
            referrer, user_agent, ip_address, time_on_page, scroll_depth
        ))
        
        # Update session page view count
        cursor.execute('''
            UPDATE sessions 
            SET page_views = page_views + 1,
                end_time = ?
            WHERE id = ?
        ''', (timestamp, session_id))
        
        # Update user page view count
        cursor.execute('''
            UPDATE users 
            SET total_page_views = total_page_views + 1,
                last_visit = ?
            WHERE id = ?
        ''', (timestamp, user_id))
        
        conn.commit()
        conn.close()
        
        return page_view_id
    
    def start_session(
        self,
        user_id: str,
        device_type: str = "desktop",
        browser: str = "unknown", 
        operating_system: str = "unknown",
        referrer: str = "",
        is_new_user: bool = False
    ) -> str:
        """Start a new user session"""
        
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        # Determine traffic source from referrer
        traffic_source = self._classify_traffic_source(referrer)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO sessions (
                id, user_id, start_time, device_type, browser, operating_system,
                traffic_source, is_new_user
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session_id, user_id, timestamp, device_type, browser,
            operating_system, traffic_source, is_new_user
        ))
        
        # Track social referral if applicable
        if traffic_source.startswith('social_'):
            platform = traffic_source.replace('social_', '')
            cursor.execute('''
                INSERT INTO social_referrals (session_id, platform, organic)
                VALUES (?, ?, TRUE)
            ''', (session_id, platform))
        
        # Update user session count
        if not is_new_user:
            cursor.execute('''
                UPDATE users 
                SET total_sessions = total_sessions + 1
                WHERE id = ?
            ''', (user_id,))
        
        conn.commit()
        conn.close()
        
        return session_id
    
    def end_session(self, session_id: str, duration: Optional[float] = None):
        """End a user session and calculate metrics"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        
        # Get session info and page view count
        cursor.execute('''
            SELECT user_id, page_views, start_time FROM sessions WHERE id = ?
        ''', (session_id,))
        
        result = cursor.fetchone()
        if not result:
            conn.close()
            return
            
        user_id, page_views, start_time = result
        
        # Calculate duration if not provided
        if duration is None:
            start_dt = datetime.fromisoformat(start_time)
            end_dt = datetime.now()
            duration = (end_dt - start_dt).total_seconds()
        
        # Determine if it's a bounce (single page view, short duration)
        is_bounce = page_views == 1 and duration < 10  # Less than 10 seconds
        
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, duration = ?, bounce = ?
            WHERE id = ?
        ''', (timestamp, duration, is_bounce, session_id))
        
        # Update user total time on site
        cursor.execute('''
            UPDATE users 
            SET total_time_on_site = total_time_on_site + ?
            WHERE id = ?
        ''', (duration, user_id))
        
        conn.commit()
        conn.close()
    
    def track_conversion(
        self,
        session_id: str,
        user_id: str,
        event_type: str,
        page_url: str,
        value: Optional[float] = None
    ) -> str:
        """Track a conversion event"""
        
        conversion_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO conversions (id, session_id, user_id, timestamp, event_type, page_url, value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (conversion_id, session_id, user_id, timestamp, event_type, page_url, value))
        
        # Update session conversion count
        cursor.execute('''
            UPDATE sessions 
            SET conversions = conversions + 1
            WHERE id = ?
        ''', (session_id,))
        
        # Update user conversion events
        cursor.execute('''
            SELECT conversion_events FROM users WHERE id = ?
        ''', (user_id,))
        
        result = cursor.fetchone()
        if result and result[0]:
            events = json.loads(result[0])
        else:
            events = []
            
        events.append(event_type)
        
        cursor.execute('''
            UPDATE users 
            SET conversion_events = ?
            WHERE id = ?
        ''', (json.dumps(events), user_id))
        
        conn.commit()
        conn.close()
        
        return conversion_id
    
    def create_user(self, user_id: Optional[str] = None) -> str:
        """Create a new user record"""
        
        if not user_id:
            user_id = str(uuid.uuid4())
            
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (id, first_visit, last_visit)
                VALUES (?, ?, ?)
            ''', (user_id, timestamp, timestamp))
            
            conn.commit()
        except sqlite3.IntegrityError:
            # User already exists
            pass
            
        conn.close()
        return user_id
    
    def _classify_traffic_source(self, referrer: str) -> str:
        """Classify traffic source based on referrer"""
        
        if not referrer or referrer == "":
            return "direct"
            
        referrer_lower = referrer.lower()
        
        # Check organic search
        for search_engine in self.traffic_sources['organic_search']:
            if search_engine in referrer_lower:
                return "organic_search"
        
        # Check social media
        for platform, domains in self.traffic_sources['social_media'].items():
            for domain in domains:
                if domain in referrer_lower:
                    return f"social_{platform}"
        
        # Check email
        for email_domain in self.traffic_sources['email']:
            if email_domain in referrer_lower:
                return "email"
        
        # Check paid search
        for paid_pattern in self.traffic_sources['paid_search']:
            if paid_pattern in referrer_lower:
                return "paid_search"
        
        # Default to referral
        return "referral"
    
    # ANALYTICS REPORTING METHODS
    
    def get_page_views(self, days: int = 30) -> Dict[str, Any]:
        """Get page view metrics for the specified period"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total page views
        cursor.execute('''
            SELECT COUNT(*) FROM page_views 
            WHERE timestamp >= ?
        ''', (start_date,))
        total_views = cursor.fetchone()[0]
        
        # Top pages by views
        cursor.execute('''
            SELECT page_url, page_title, COUNT(*) as views
            FROM page_views 
            WHERE timestamp >= ?
            GROUP BY page_url, page_title
            ORDER BY views DESC
            LIMIT 10
        ''', (start_date,))
        top_pages = cursor.fetchall()
        
        # Daily page views
        cursor.execute('''
            SELECT DATE(timestamp) as date, COUNT(*) as views
            FROM page_views 
            WHERE timestamp >= ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', (start_date,))
        daily_views = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_views': total_views,
            'top_pages': [{'url': row[0], 'title': row[1], 'views': row[2]} for row in top_pages],
            'daily_views': [{'date': row[0], 'views': row[1]} for row in daily_views]
        }
    
    def get_session_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get session-related metrics"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total sessions
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE start_time >= ?
        ''', (start_date,))
        total_sessions = cursor.fetchone()[0]
        
        # Average session duration
        cursor.execute('''
            SELECT AVG(duration) FROM sessions 
            WHERE start_time >= ? AND duration IS NOT NULL
        ''', (start_date,))
        avg_duration = cursor.fetchone()[0] or 0
        
        # Average pages per session
        cursor.execute('''
            SELECT AVG(page_views) FROM sessions 
            WHERE start_time >= ?
        ''', (start_date,))
        avg_pages_per_session = cursor.fetchone()[0] or 0
        
        # Bounce rate
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN bounce = 1 THEN 1 END) as bounces,
                COUNT(*) as total
            FROM sessions 
            WHERE start_time >= ?
        ''', (start_date,))
        bounce_data = cursor.fetchone()
        bounce_rate = (bounce_data[0] / bounce_data[1] * 100) if bounce_data[1] > 0 else 0
        
        # New vs returning users
        cursor.execute('''
            SELECT 
                COUNT(CASE WHEN is_new_user = 1 THEN 1 END) as new_users,
                COUNT(CASE WHEN is_new_user = 0 THEN 1 END) as returning_users
            FROM sessions 
            WHERE start_time >= ?
        ''', (start_date,))
        user_data = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_sessions': total_sessions,
            'avg_session_duration': round(avg_duration, 2),
            'avg_pages_per_session': round(avg_pages_per_session, 2),
            'bounce_rate': round(bounce_rate, 2),
            'new_users': user_data[0],
            'returning_users': user_data[1]
        }
    
    def get_traffic_sources(self, days: int = 30) -> Dict[str, Any]:
        """Get traffic source breakdown"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT traffic_source, COUNT(*) as sessions
            FROM sessions 
            WHERE start_time >= ?
            GROUP BY traffic_source
            ORDER BY sessions DESC
        ''', (start_date,))
        
        traffic_sources = cursor.fetchall()
        
        # Social referrals detail
        cursor.execute('''
            SELECT sr.platform, COUNT(*) as sessions
            FROM social_referrals sr
            JOIN sessions s ON sr.session_id = s.id
            WHERE s.start_time >= ?
            GROUP BY sr.platform
            ORDER BY sessions DESC
        ''', (start_date,))
        
        social_referrals = cursor.fetchall()
        
        conn.close()
        
        return {
            'traffic_sources': [{'source': row[0], 'sessions': row[1]} for row in traffic_sources],
            'social_referrals': [{'platform': row[0], 'sessions': row[1]} for row in social_referrals]
        }
    
    def get_device_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get device type breakdown"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT device_type, COUNT(*) as sessions
            FROM sessions 
            WHERE start_time >= ?
            GROUP BY device_type
            ORDER BY sessions DESC
        ''', (start_date,))
        
        device_data = cursor.fetchall()
        
        cursor.execute('''
            SELECT browser, COUNT(*) as sessions
            FROM sessions 
            WHERE start_time >= ?
            GROUP BY browser
            ORDER BY sessions DESC
            LIMIT 10
        ''', (start_date,))
        
        browser_data = cursor.fetchall()
        
        conn.close()
        
        return {
            'device_types': [{'device': row[0], 'sessions': row[1]} for row in device_data],
            'browsers': [{'browser': row[0], 'sessions': row[1]} for row in browser_data]
        }
    
    def get_conversion_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get conversion metrics"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total conversions
        cursor.execute('''
            SELECT COUNT(*) FROM conversions 
            WHERE timestamp >= ?
        ''', (start_date,))
        total_conversions = cursor.fetchone()[0]
        
        # Conversion rate
        cursor.execute('''
            SELECT COUNT(*) FROM sessions 
            WHERE start_time >= ?
        ''', (start_date,))
        total_sessions = cursor.fetchone()[0]
        
        conversion_rate = (total_conversions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Conversions by type
        cursor.execute('''
            SELECT event_type, COUNT(*) as count
            FROM conversions 
            WHERE timestamp >= ?
            GROUP BY event_type
            ORDER BY count DESC
        ''', (start_date,))
        conversions_by_type = cursor.fetchall()
        
        # Revenue (if applicable)
        cursor.execute('''
            SELECT SUM(value) FROM conversions 
            WHERE timestamp >= ? AND value IS NOT NULL
        ''', (start_date,))
        total_revenue = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_conversions': total_conversions,
            'conversion_rate': round(conversion_rate, 2),
            'conversions_by_type': [{'type': row[0], 'count': row[1]} for row in conversions_by_type],
            'total_revenue': total_revenue
        }
    
    def get_exit_pages(self, days: int = 30) -> Dict[str, Any]:
        """Get top exit pages"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Top exit pages
        cursor.execute('''
            SELECT 
                pv.page_url,
                pv.page_title,
                COUNT(*) as exits
            FROM page_views pv
            WHERE pv.timestamp >= ? 
            AND pv.exit_page = 1
            GROUP BY pv.page_url, pv.page_title
            ORDER BY exits DESC
            LIMIT 10
        ''', (start_date,))
        
        exit_pages = cursor.fetchall()
        
        # Exit rate by page
        cursor.execute('''
            SELECT 
                pv.page_url,
                COUNT(*) as total_views,
                COUNT(CASE WHEN pv.exit_page = 1 THEN 1 END) as exits,
                ROUND(COUNT(CASE WHEN pv.exit_page = 1 THEN 1 END) * 100.0 / COUNT(*), 2) as exit_rate
            FROM page_views pv
            WHERE pv.timestamp >= ?
            GROUP BY pv.page_url
            HAVING COUNT(*) >= 10  -- Only pages with significant traffic
            ORDER BY exit_rate DESC
            LIMIT 10
        ''', (start_date,))
        
        exit_rates = cursor.fetchall()
        
        conn.close()
        
        return {
            'top_exit_pages': [{'url': row[0], 'title': row[1], 'exits': row[2]} for row in exit_pages],
            'exit_rates': [{'url': row[0], 'total_views': row[1], 'exits': row[2], 'exit_rate': row[3]} for row in exit_rates]
        }
    
    def get_time_on_page_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get average time on page metrics"""
        
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Overall average time on page
        cursor.execute('''
            SELECT AVG(time_on_page) FROM page_views 
            WHERE timestamp >= ? AND time_on_page IS NOT NULL
        ''', (start_date,))
        avg_time_on_page = cursor.fetchone()[0] or 0
        
        # Time on page by URL
        cursor.execute('''
            SELECT 
                page_url,
                page_title,
                AVG(time_on_page) as avg_time,
                COUNT(*) as views
            FROM page_views 
            WHERE timestamp >= ? AND time_on_page IS NOT NULL
            GROUP BY page_url, page_title
            HAVING COUNT(*) >= 5  -- Only pages with multiple views
            ORDER BY avg_time DESC
            LIMIT 10
        ''', (start_date,))
        
        time_by_page = cursor.fetchall()
        
        conn.close()
        
        return {
            'avg_time_on_page': round(avg_time_on_page, 2),
            'time_by_page': [
                {
                    'url': row[0], 
                    'title': row[1], 
                    'avg_time': round(row[2], 2), 
                    'views': row[3]
                } for row in time_by_page
            ]
        }
    
    def generate_comprehensive_report(self, days: int = 30) -> Dict[str, Any]:
        """Generate a comprehensive analytics report"""
        
        return {
            'report_period': f"Last {days} days",
            'generated_at': datetime.now().isoformat(),
            'page_views': self.get_page_views(days),
            'sessions': self.get_session_metrics(days),
            'traffic_sources': self.get_traffic_sources(days),
            'devices': self.get_device_metrics(days),
            'conversions': self.get_conversion_metrics(days),
            'exit_pages': self.get_exit_pages(days),
            'time_on_page': self.get_time_on_page_metrics(days)
        }
    
    def mark_exit_page(self, page_view_id: str):
        """Mark a page view as an exit page"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE page_views 
            SET exit_page = TRUE
            WHERE id = ?
        ''', (page_view_id,))
        
        conn.commit()
        conn.close()
    
    def update_time_on_page(self, page_view_id: str, time_on_page: float):
        """Update time spent on a specific page"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE page_views 
            SET time_on_page = ?
            WHERE id = ?
        ''', (time_on_page, page_view_id))
        
        conn.commit()
        conn.close()


# Example usage and testing
if __name__ == "__main__":
    # Initialize analytics system
    analytics = WebsiteAnalytics()
    
    # Create sample data for testing
    print("🔄 Creating sample analytics data...")
    
    # Create some users
    user1 = analytics.create_user()
    user2 = analytics.create_user()
    user3 = analytics.create_user()
    
    # Create sessions and page views
    session1 = analytics.start_session(
        user_id=user1,
        device_type="desktop",
        browser="Chrome",
        referrer="https://google.com/search?q=renewable+energy",
        is_new_user=True
    )
    
    # Track page views for session 1
    pv1 = analytics.track_page_view(
        page_url="/index.html",
        page_title="Renewable Power Insight - Home",
        session_id=session1,
        user_id=user1,
        referrer="https://google.com/search?q=renewable+energy",
        time_on_page=45.5
    )
    
    pv2 = analytics.track_page_view(
        page_url="/blog/solar-energy-trends.html",
        page_title="Solar Energy Trends 2025",
        session_id=session1,
        user_id=user1,
        time_on_page=125.8
    )
    
    # Track conversion
    analytics.track_conversion(
        session_id=session1,
        user_id=user1,
        event_type="newsletter_signup",
        page_url="/blog/solar-energy-trends.html"
    )
    
    # End session
    analytics.end_session(session1, duration=180.0)
    
    # Create more sample data
    session2 = analytics.start_session(
        user_id=user2,
        device_type="mobile",
        browser="Safari",
        referrer="https://facebook.com",
        is_new_user=True
    )
    
    analytics.track_page_view(
        page_url="/index.html",
        page_title="Renewable Power Insight - Home",
        session_id=session2,
        user_id=user2,
        referrer="https://facebook.com",
        time_on_page=8.2  # Short visit - will be a bounce
    )
    
    analytics.end_session(session2, duration=8.2)
    
    # Generate comprehensive report
    print("\n📊 Generating comprehensive analytics report...")
    report = analytics.generate_comprehensive_report(days=30)
    
    print(f"\n=== WEBSITE ANALYTICS REPORT ({report['report_period']}) ===")
    print(f"Generated: {report['generated_at']}")
    
    print(f"\n📈 PAGE VIEWS:")
    print(f"  Total Views: {report['page_views']['total_views']}")
    print(f"  Top Pages:")
    for page in report['page_views']['top_pages'][:3]:
        print(f"    - {page['title']}: {page['views']} views")
    
    print(f"\n⏱️ SESSION METRICS:")
    print(f"  Total Sessions: {report['sessions']['total_sessions']}")
    print(f"  Avg Session Duration: {report['sessions']['avg_session_duration']}s")
    print(f"  Avg Pages/Session: {report['sessions']['avg_pages_per_session']}")
    print(f"  Bounce Rate: {report['sessions']['bounce_rate']}%")
    print(f"  New Users: {report['sessions']['new_users']}")
    print(f"  Returning Users: {report['sessions']['returning_users']}")
    
    print(f"\n🚀 TRAFFIC SOURCES:")
    for source in report['traffic_sources']['traffic_sources']:
        print(f"  {source['source']}: {source['sessions']} sessions")
    
    print(f"\n📱 DEVICE BREAKDOWN:")
    for device in report['devices']['device_types']:
        print(f"  {device['device']}: {device['sessions']} sessions")
    
    print(f"\n💰 CONVERSIONS:")
    print(f"  Total Conversions: {report['conversions']['total_conversions']}")
    print(f"  Conversion Rate: {report['conversions']['conversion_rate']}%")
    print(f"  Total Revenue: ${report['conversions']['total_revenue']}")
    
    print(f"\n🚪 EXIT PAGES:")
    for page in report['exit_pages']['top_exit_pages'][:3]:
        print(f"  {page['title']}: {page['exits']} exits")
    
    print(f"\n⏰ TIME ON PAGE:")
    print(f"  Avg Time on Page: {report['time_on_page']['avg_time_on_page']}s")
    
    print(f"\n✅ Analytics system successfully initialized and tested!")
    print(f"Database created at: {analytics.db_path}")
