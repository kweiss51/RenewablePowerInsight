"""
Analytics API Server
Flask-based API to receive and store analytics data
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime
import json
from pathlib import Path
import logging

# Import our analytics system
import sys
sys.path.append(str(Path(__file__).parent))
from website_analytics import WebsiteAnalytics

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

# Initialize analytics system
analytics = WebsiteAnalytics()

@app.route('/api/analytics', methods=['POST'])
def track_analytics():
    """Receive and process analytics data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        event_type = data.get('event_type')
        
        # Route to appropriate tracking method
        if event_type == 'page_view':
            result = handle_page_view(data)
        elif event_type == 'session_start':
            result = handle_session_start(data)
        elif event_type == 'page_exit':
            result = handle_page_exit(data)
        elif event_type == 'custom_event':
            result = handle_custom_event(data)
        elif event_type == 'conversion':
            result = handle_conversion(data)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return jsonify({'error': f'Unknown event type: {event_type}'}), 400
        
        logger.info(f"Tracked {event_type} for session {data.get('session_id')}")
        return jsonify({'success': True, 'result': result})
        
    except Exception as e:
        logger.error(f"Error processing analytics data: {e}")
        return jsonify({'error': str(e)}), 500

def handle_page_view(data):
    """Handle page view tracking"""
    return analytics.track_page_view(
        session_id=data.get('session_id'),
        user_id=data.get('user_id'),
        page_url=data.get('page_url'),
        page_title=data.get('page_title'),
        referrer=data.get('referrer'),
        user_agent=data.get('user_agent'),
        device_type=data.get('device_type'),
        traffic_source=data.get('traffic_source')
    )

def handle_session_start(data):
    """Handle session start tracking"""
    return analytics.track_session(
        session_id=data.get('session_id'),
        user_id=data.get('user_id'),
        is_new_user=data.get('is_new_user', False),
        device_type=data.get('device_type'),
        traffic_source=data.get('traffic_source'),
        landing_page=data.get('landing_page'),
        user_agent=data.get('user_agent')
    )

def handle_page_exit(data):
    """Handle page exit tracking"""
    # Update the last page view with time on page
    analytics.update_page_time(
        session_id=data.get('session_id'),
        page_url=data.get('page_url'),
        time_on_page=data.get('time_on_page', 0)
    )
    return {'tracked': True}

def handle_custom_event(data):
    """Handle custom event tracking"""
    return analytics.track_custom_event(
        session_id=data.get('session_id'),
        user_id=data.get('user_id'),
        event_name=data.get('event_name'),
        properties=data.get('properties', {}),
        page_url=data.get('page_url')
    )

def handle_conversion(data):
    """Handle conversion tracking"""
    return analytics.track_conversion(
        session_id=data.get('session_id'),
        user_id=data.get('user_id'),
        event_type=data.get('conversion_type'),
        value=data.get('value', 0),
        currency=data.get('currency', 'USD'),
        page_url=data.get('page_url')
    )

@app.route('/api/analytics/dashboard', methods=['GET'])
def get_dashboard_data():
    """Get dashboard data for frontend"""
    try:
        days = request.args.get('days', 30, type=int)
        
        # Get summary data
        summary = analytics.get_summary_report(days)
        
        return jsonify(summary)
        
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/reports/<report_type>', methods=['GET'])
def get_report(report_type):
    """Get specific analytics reports"""
    try:
        days = request.args.get('days', 30, type=int)
        
        if report_type == 'traffic-sources':
            data = analytics.get_traffic_sources_report(days)
        elif report_type == 'top-pages':
            data = analytics.get_top_pages_report(days)
        elif report_type == 'device-breakdown':
            data = analytics.get_device_breakdown_report(days)
        elif report_type == 'user-engagement':
            data = analytics.get_user_engagement_report(days)
        elif report_type == 'conversions':
            data = analytics.get_conversion_report(days)
        else:
            return jsonify({'error': f'Unknown report type: {report_type}'}), 400
        
        return jsonify(data)
        
    except Exception as e:
        logger.error(f"Error getting {report_type} report: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        conn = sqlite3.connect(analytics.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM page_views')
        page_views_count = cursor.fetchone()[0]
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'page_views_tracked': page_views_count,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def index():
    """API information page"""
    return jsonify({
        'service': 'RenewablePowerInsight Analytics API',
        'version': '1.0.0',
        'endpoints': {
            'POST /api/analytics': 'Track analytics events',
            'GET /api/analytics/dashboard': 'Get dashboard data',
            'GET /api/analytics/reports/<type>': 'Get specific reports',
            'GET /api/analytics/health': 'Health check'
        },
        'documentation': 'https://github.com/yourusername/renewablepowerinsight'
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("🚀 Starting RenewablePowerInsight Analytics API")
    print("📊 Database path:", analytics.db_path)
    print("🌐 API will be available at: http://localhost:5001")
    print("📈 Dashboard endpoint: http://localhost:5001/api/analytics/dashboard")
    print("💊 Health check: http://localhost:5001/api/analytics/health")
    
    # Initialize database if it doesn't exist
    analytics.init_database()
    
    app.run(host='0.0.0.0', port=5001, debug=True)
