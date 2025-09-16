"""
Analytics Dashboard for RenewablePowerInsight
Provides web-based visualization of website analytics metrics
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pathlib import Path
import sqlite3

class AnalyticsDashboard:
    """HTML dashboard generator for website analytics"""
    
    def __init__(self, analytics_db_path: str = "analytics/website_analytics.db"):
        self.db_path = Path(analytics_db_path)
        
    def generate_dashboard_html(self, days: int = 30) -> str:
        """Generate complete HTML dashboard"""
        
        # Get data from analytics database
        data = self._get_dashboard_data(days)
        
        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RenewablePowerInsight - Analytics Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            line-height: 1.6;
        }}
        
        .header {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            padding: 2rem 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        .header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .metric-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #28a745;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        
        .metric-card h3 {{
            color: #666;
            font-size: 0.9rem;
            text-transform: uppercase;
            font-weight: 600;
            margin-bottom: 0.5rem;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #28a745;
            margin-bottom: 0.5rem;
        }}
        
        .metric-description {{
            color: #888;
            font-size: 0.9rem;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }}
        
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .chart-card h3 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.3rem;
            font-weight: 600;
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
        }}
        
        .table-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        
        .table-card h3 {{
            color: #333;
            margin-bottom: 1rem;
            font-size: 1.3rem;
            font-weight: 600;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }}
        
        th, td {{
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 0.5px;
        }}
        
        tr:hover {{
            background-color: #f8f9fa;
        }}
        
        .status-indicator {{
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 0.5rem;
        }}
        
        .status-good {{ background-color: #28a745; }}
        .status-warning {{ background-color: #ffc107; }}
        .status-poor {{ background-color: #dc3545; }}
        
        .footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            border-top: 1px solid #eee;
            margin-top: 3rem;
        }}
        
        .refresh-info {{
            background: #e3f2fd;
            border: 1px solid #90caf9;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 2rem;
            color: #1565c0;
        }}
        
        .insights-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}
        
        .insight-card {{
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-left: 4px solid #17a2b8;
        }}
        
        .insight-card h4 {{
            color: #17a2b8;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }}
        
        .insight-card p {{
            color: #666;
            line-height: 1.6;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2rem; }}
            .container {{ padding: 1rem; }}
            .charts-grid {{ grid-template-columns: 1fr; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
            .charts-grid .chart-card {{ min-width: unset; }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <h1>📊 Analytics Dashboard</h1>
        <p>RenewablePowerInsight - Website Performance Metrics</p>
    </header>

    <div class="container">
        <div class="refresh-info">
            📅 <strong>Report Period:</strong> Last {days} days | 
            🕒 <strong>Last Updated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} |
            📈 <strong>Data Points:</strong> {data.get('total_data_points', 'N/A')}
        </div>

        <!-- Key Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📄 Total Page Views</h3>
                <div class="metric-value">{data['page_views']['total']:,}</div>
                <div class="metric-description">Website page impressions</div>
            </div>
            
            <div class="metric-card">
                <h3>👥 Total Sessions</h3>
                <div class="metric-value">{data['sessions']['total']:,}</div>
                <div class="metric-description">Unique visitor sessions</div>
            </div>
            
            <div class="metric-card">
                <h3>⏱️ Avg Session Duration</h3>
                <div class="metric-value">{data['sessions']['avg_duration']:.1f}s</div>
                <div class="metric-description">Time spent per session</div>
            </div>
            
            <div class="metric-card">
                <h3>📊 Bounce Rate</h3>
                <div class="metric-value">{data['sessions']['bounce_rate']:.1f}%</div>
                <div class="metric-description">Single-page sessions</div>
            </div>
            
            <div class="metric-card">
                <h3>🎯 Conversion Rate</h3>
                <div class="metric-value">{data['conversions']['rate']:.1f}%</div>
                <div class="metric-description">Visitors who converted</div>
            </div>
            
            <div class="metric-card">
                <h3>📱 Mobile Traffic</h3>
                <div class="metric-value">{data['devices']['mobile_percentage']:.1f}%</div>
                <div class="metric-description">Mobile device usage</div>
            </div>
        </div>

        <!-- Charts -->
        <div class="charts-grid">
            <div class="chart-card">
                <h3>📈 Daily Page Views</h3>
                <div class="chart-container">
                    <canvas id="pageViewsChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>🚀 Traffic Sources</h3>
                <div class="chart-container">
                    <canvas id="trafficSourcesChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>📱 Device Types</h3>
                <div class="chart-container">
                    <canvas id="deviceTypesChart"></canvas>
                </div>
            </div>
            
            <div class="chart-card">
                <h3>📊 User Types</h3>
                <div class="chart-container">
                    <canvas id="userTypesChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Insights -->
        <div class="insights-grid">
            <div class="insight-card">
                <h4>🎯 Performance Status</h4>
                <p>
                    <span class="status-indicator {self._get_bounce_rate_status(data['sessions']['bounce_rate'])}"></span>
                    Bounce Rate: {self._get_bounce_rate_insight(data['sessions']['bounce_rate'])}
                </p>
                <p>
                    <span class="status-indicator {self._get_conversion_status(data['conversions']['rate'])}"></span>
                    Conversion Rate: {self._get_conversion_insight(data['conversions']['rate'])}
                </p>
            </div>
            
            <div class="insight-card">
                <h4>📱 User Behavior</h4>
                <p>Average pages per session: {data['sessions']['pages_per_session']:.1f}</p>
                <p>Most popular device: {data['devices']['top_device']}</p>
                <p>Primary traffic source: {data['traffic']['top_source']}</p>
            </div>
            
            <div class="insight-card">
                <h4>📈 Growth Trends</h4>
                <p>New vs Returning: {data['sessions']['new_users']} new, {data['sessions']['returning_users']} returning</p>
                <p>Social media referrals: {data['social']['total_referrals']} sessions</p>
                <p>Peak activity: {data.get('peak_hour', 'N/A')}</p>
            </div>
        </div>

        <!-- Top Pages Table -->
        <div class="table-card">
            <h3>🔝 Top Performing Pages</h3>
            <table>
                <thead>
                    <tr>
                        <th>Page Title</th>
                        <th>Views</th>
                        <th>Avg Time</th>
                        <th>Exit Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_top_pages_table(data['top_pages'])}
                </tbody>
            </table>
        </div>

        <!-- Traffic Sources Table -->
        <div class="table-card">
            <h3>🚀 Traffic Source Breakdown</h3>
            <table>
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Sessions</th>
                        <th>Percentage</th>
                        <th>Conversion Rate</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_traffic_sources_table(data['traffic_sources'])}
                </tbody>
            </table>
        </div>

        <!-- Conversion Events Table -->
        <div class="table-card">
            <h3>💰 Conversion Events</h3>
            <table>
                <thead>
                    <tr>
                        <th>Event Type</th>
                        <th>Count</th>
                        <th>Value</th>
                        <th>Percentage</th>
                    </tr>
                </thead>
                <tbody>
                    {self._generate_conversions_table(data['conversion_events'])}
                </tbody>
            </table>
        </div>
    </div>

    <footer class="footer">
        <p>🌱 RenewablePowerInsight Analytics Dashboard | Powered by Custom Analytics Engine</p>
        <p>Last updated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </footer>

    <script>
        // Chart.js configurations and data
        const chartData = {json.dumps(self._prepare_chart_data(data), indent=2)};
        
        // Page Views Chart
        const pageViewsCtx = document.getElementById('pageViewsChart').getContext('2d');
        new Chart(pageViewsCtx, {{
            type: 'line',
            data: {{
                labels: chartData.pageViews.labels,
                datasets: [{{
                    label: 'Page Views',
                    data: chartData.pageViews.data,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ precision: 0 }}
                    }}
                }}
            }}
        }});

        // Traffic Sources Chart
        const trafficCtx = document.getElementById('trafficSourcesChart').getContext('2d');
        new Chart(trafficCtx, {{
            type: 'doughnut',
            data: {{
                labels: chartData.trafficSources.labels,
                datasets: [{{
                    data: chartData.trafficSources.data,
                    backgroundColor: [
                        '#28a745', '#17a2b8', '#ffc107', '#dc3545', '#6f42c1', '#fd7e14'
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // Device Types Chart
        const deviceCtx = document.getElementById('deviceTypesChart').getContext('2d');
        new Chart(deviceCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.deviceTypes.labels,
                datasets: [{{
                    label: 'Sessions',
                    data: chartData.deviceTypes.data,
                    backgroundColor: '#17a2b8',
                    borderRadius: 8
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{ precision: 0 }}
                    }}
                }}
            }}
        }});

        // User Types Chart
        const userTypesCtx = document.getElementById('userTypesChart').getContext('2d');
        new Chart(userTypesCtx, {{
            type: 'pie',
            data: {{
                labels: ['New Users', 'Returning Users'],
                datasets: [{{
                    data: [chartData.userTypes.new, chartData.userTypes.returning],
                    backgroundColor: ['#28a745', '#ffc107'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});

        // Auto-refresh every 5 minutes
        setTimeout(() => {{
            location.reload();
        }}, 300000);
    </script>
</body>
</html>
"""
        return html_template

    def _get_dashboard_data(self, days: int) -> Dict[str, Any]:
        """Fetch all dashboard data from the database"""
        
        if not self.db_path.exists():
            return self._get_empty_data()
            
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Page views
            cursor.execute('SELECT COUNT(*) FROM page_views WHERE timestamp >= ?', (start_date,))
            total_page_views = cursor.fetchone()[0]
            
            # Sessions
            cursor.execute('''
                SELECT 
                    COUNT(*) as total,
                    AVG(duration) as avg_duration,
                    AVG(page_views) as pages_per_session,
                    COUNT(CASE WHEN bounce = 1 THEN 1 END) * 100.0 / COUNT(*) as bounce_rate,
                    COUNT(CASE WHEN is_new_user = 1 THEN 1 END) as new_users,
                    COUNT(CASE WHEN is_new_user = 0 THEN 1 END) as returning_users
                FROM sessions 
                WHERE start_time >= ?
            ''', (start_date,))
            session_data = cursor.fetchone()
            
            # Conversions
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_conversions,
                    COUNT(*) * 100.0 / (SELECT COUNT(*) FROM sessions WHERE start_time >= ?) as conversion_rate
                FROM conversions 
                WHERE timestamp >= ?
            ''', (start_date, start_date))
            conversion_data = cursor.fetchone()
            
            # Device breakdown
            cursor.execute('''
                SELECT device_type, COUNT(*) as sessions
                FROM sessions 
                WHERE start_time >= ?
                GROUP BY device_type
                ORDER BY sessions DESC
            ''', (start_date,))
            device_data = cursor.fetchall()
            
            # Traffic sources
            cursor.execute('''
                SELECT traffic_source, COUNT(*) as sessions
                FROM sessions 
                WHERE start_time >= ?
                GROUP BY traffic_source
                ORDER BY sessions DESC
            ''', (start_date,))
            traffic_data = cursor.fetchall()
            
            # Top pages
            cursor.execute('''
                SELECT 
                    page_url, 
                    page_title, 
                    COUNT(*) as views,
                    AVG(time_on_page) as avg_time,
                    COUNT(CASE WHEN exit_page = 1 THEN 1 END) * 100.0 / COUNT(*) as exit_rate
                FROM page_views 
                WHERE timestamp >= ?
                GROUP BY page_url, page_title
                ORDER BY views DESC
                LIMIT 10
            ''', (start_date,))
            top_pages_data = cursor.fetchall()
            
            # Daily page views for chart
            cursor.execute('''
                SELECT DATE(timestamp) as date, COUNT(*) as views
                FROM page_views 
                WHERE timestamp >= ?
                GROUP BY DATE(timestamp)
                ORDER BY date
            ''', (start_date,))
            daily_views = cursor.fetchall()
            
            # Conversion events
            cursor.execute('''
                SELECT event_type, COUNT(*) as count, SUM(value) as total_value
                FROM conversions 
                WHERE timestamp >= ?
                GROUP BY event_type
                ORDER BY count DESC
            ''', (start_date,))
            conversion_events = cursor.fetchall()
            
            # Social referrals
            cursor.execute('''
                SELECT COUNT(*) FROM social_referrals sr
                JOIN sessions s ON sr.session_id = s.id
                WHERE s.start_time >= ?
            ''', (start_date,))
            social_referrals = cursor.fetchone()[0]
            
            conn.close()
            
            # Process device data
            total_sessions = session_data[0] if session_data[0] else 1
            mobile_sessions = sum(count for device, count in device_data if device == 'mobile')
            mobile_percentage = (mobile_sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            return {
                'total_data_points': total_page_views + total_sessions,
                'page_views': {
                    'total': total_page_views,
                    'daily': daily_views
                },
                'sessions': {
                    'total': session_data[0] or 0,
                    'avg_duration': session_data[1] or 0,
                    'pages_per_session': session_data[2] or 0,
                    'bounce_rate': session_data[3] or 0,
                    'new_users': session_data[4] or 0,
                    'returning_users': session_data[5] or 0
                },
                'conversions': {
                    'total': conversion_data[0] or 0,
                    'rate': conversion_data[1] or 0
                },
                'devices': {
                    'breakdown': device_data,
                    'mobile_percentage': mobile_percentage,
                    'top_device': device_data[0][0] if device_data else 'desktop'
                },
                'traffic': {
                    'breakdown': traffic_data,
                    'top_source': traffic_data[0][0] if traffic_data else 'direct'
                },
                'traffic_sources': traffic_data,
                'top_pages': top_pages_data,
                'conversion_events': conversion_events,
                'social': {
                    'total_referrals': social_referrals
                }
            }
            
        except Exception as e:
            conn.close()
            return self._get_empty_data()
    
    def _get_empty_data(self) -> Dict[str, Any]:
        """Return empty data structure when no data is available"""
        return {
            'total_data_points': 0,
            'page_views': {'total': 0, 'daily': []},
            'sessions': {
                'total': 0, 'avg_duration': 0, 'pages_per_session': 0,
                'bounce_rate': 0, 'new_users': 0, 'returning_users': 0
            },
            'conversions': {'total': 0, 'rate': 0},
            'devices': {'breakdown': [], 'mobile_percentage': 0, 'top_device': 'desktop'},
            'traffic': {'breakdown': [], 'top_source': 'direct'},
            'traffic_sources': [],
            'top_pages': [],
            'conversion_events': [],
            'social': {'total_referrals': 0}
        }
    
    def _prepare_chart_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for Chart.js charts"""
        
        # Daily page views
        daily_views = data['page_views']['daily']
        page_views_labels = [item[0] for item in daily_views] if daily_views else []
        page_views_data = [item[1] for item in daily_views] if daily_views else []
        
        # Traffic sources
        traffic_sources = data['traffic_sources']
        traffic_labels = [item[0] for item in traffic_sources] if traffic_sources else []
        traffic_data = [item[1] for item in traffic_sources] if traffic_sources else []
        
        # Device types
        device_breakdown = data['devices']['breakdown']
        device_labels = [item[0] for item in device_breakdown] if device_breakdown else []
        device_data = [item[1] for item in device_breakdown] if device_breakdown else []
        
        return {
            'pageViews': {
                'labels': page_views_labels,
                'data': page_views_data
            },
            'trafficSources': {
                'labels': traffic_labels,
                'data': traffic_data
            },
            'deviceTypes': {
                'labels': device_labels,
                'data': device_data
            },
            'userTypes': {
                'new': data['sessions']['new_users'],
                'returning': data['sessions']['returning_users']
            }
        }
    
    def _get_bounce_rate_status(self, bounce_rate: float) -> str:
        """Get status class for bounce rate"""
        if bounce_rate <= 30:
            return "status-good"
        elif bounce_rate <= 50:
            return "status-warning"
        else:
            return "status-poor"
    
    def _get_bounce_rate_insight(self, bounce_rate: float) -> str:
        """Get insight text for bounce rate"""
        if bounce_rate <= 30:
            return "Excellent engagement"
        elif bounce_rate <= 50:
            return "Good, room for improvement"
        else:
            return "Needs attention"
    
    def _get_conversion_status(self, conversion_rate: float) -> str:
        """Get status class for conversion rate"""
        if conversion_rate >= 5:
            return "status-good"
        elif conversion_rate >= 2:
            return "status-warning"
        else:
            return "status-poor"
    
    def _get_conversion_insight(self, conversion_rate: float) -> str:
        """Get insight text for conversion rate"""
        if conversion_rate >= 5:
            return "High performing"
        elif conversion_rate >= 2:
            return "Average performance"
        else:
            return "Below average"
    
    def _generate_top_pages_table(self, pages_data: List) -> str:
        """Generate HTML table rows for top pages"""
        if not pages_data:
            return "<tr><td colspan='4'>No data available</td></tr>"
            
        rows = []
        for page in pages_data:
            url, title, views, avg_time, exit_rate = page
            avg_time_display = f"{avg_time:.1f}s" if avg_time else "N/A"
            exit_rate_display = f"{exit_rate:.1f}%" if exit_rate else "N/A"
            
            rows.append(f"""
                <tr>
                    <td>{title or url}</td>
                    <td>{views:,}</td>
                    <td>{avg_time_display}</td>
                    <td>{exit_rate_display}</td>
                </tr>
            """)
        
        return "".join(rows)
    
    def _generate_traffic_sources_table(self, sources_data: List) -> str:
        """Generate HTML table rows for traffic sources"""
        if not sources_data:
            return "<tr><td colspan='4'>No data available</td></tr>"
        
        total_sessions = sum(item[1] for item in sources_data)
        rows = []
        
        for source, sessions in sources_data:
            percentage = (sessions / total_sessions * 100) if total_sessions > 0 else 0
            
            rows.append(f"""
                <tr>
                    <td>{source.replace('_', ' ').title()}</td>
                    <td>{sessions:,}</td>
                    <td>{percentage:.1f}%</td>
                    <td>N/A</td>
                </tr>
            """)
        
        return "".join(rows)
    
    def _generate_conversions_table(self, conversions_data: List) -> str:
        """Generate HTML table rows for conversions"""
        if not conversions_data:
            return "<tr><td colspan='4'>No conversions tracked</td></tr>"
        
        total_conversions = sum(item[1] for item in conversions_data)
        rows = []
        
        for event_type, count, total_value in conversions_data:
            percentage = (count / total_conversions * 100) if total_conversions > 0 else 0
            value_display = f"${total_value:.2f}" if total_value else "N/A"
            
            rows.append(f"""
                <tr>
                    <td>{event_type.replace('_', ' ').title()}</td>
                    <td>{count:,}</td>
                    <td>{value_display}</td>
                    <td>{percentage:.1f}%</td>
                </tr>
            """)
        
        return "".join(rows)
    
    def save_dashboard(self, output_path: str = "analytics/dashboard.html", days: int = 30):
        """Generate and save dashboard HTML file"""
        
        html_content = self.generate_dashboard_html(days)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file


if __name__ == "__main__":
    # Generate dashboard
    dashboard = AnalyticsDashboard()
    output_file = dashboard.save_dashboard()
    
    print(f"📊 Analytics dashboard generated: {output_file}")
    print(f"📂 Open the file in your browser to view the dashboard")
