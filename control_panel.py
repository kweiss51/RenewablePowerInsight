#!/usr/bin/env python3
"""
Web-based Control Panel for Energy Blog Automation
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
import threading
import time

# Add the project root to the path
import sys
sys.path.append(str(Path(__file__).parent))

from automation_controller import AutomationController

app = Flask(__name__, static_folder='static', template_folder='templates')

# Global controller instance
controller = AutomationController()

class ControlPanelServer:
    def __init__(self):
        self.controller = controller
        self.refresh_status()
    
    def refresh_status(self):
        """Refresh the controller status"""
        self.controller.load_control_state()

@app.route('/control')
def control_panel():
    """Main control panel page"""
    status = controller.status()
    
    # Get recent logs
    log_file = Path('logs/automation_controller.log')
    recent_logs = []
    if log_file.exists():
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_logs = lines[-20:]  # Last 20 lines
    
    return render_template('control_panel.html', 
                         status=status, 
                         logs=recent_logs)

@app.route('/api/control/start', methods=['POST'])
def api_start():
    """API endpoint to start automation"""
    try:
        data = request.json or {}
        
        days = data.get('days')
        posts_per_day = data.get('posts_per_day', 10)
        interval = data.get('interval', 24)
        immediate = data.get('immediate', False)
        
        success = controller.start(
            days=days,
            posts_per_day=posts_per_day,
            hours_interval=interval,
            run_immediately=immediate
        )
        
        return jsonify({
            'success': success,
            'message': 'Automation started successfully' if success else 'Failed to start automation'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/stop', methods=['POST'])
def api_stop():
    """API endpoint to stop automation"""
    try:
        controller.stop()
        return jsonify({
            'success': True,
            'message': 'Automation stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/pause', methods=['POST'])
def api_pause():
    """API endpoint to pause automation"""
    try:
        controller.pause()
        return jsonify({
            'success': True,
            'message': 'Automation paused successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/resume', methods=['POST'])
def api_resume():
    """API endpoint to resume automation"""
    try:
        controller.resume()
        return jsonify({
            'success': True,
            'message': 'Automation resumed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/run-once', methods=['POST'])
def api_run_once():
    """API endpoint to run single cycle"""
    try:
        success = controller.run_single_cycle()
        return jsonify({
            'success': success,
            'message': 'Single cycle completed' if success else 'Failed to run cycle'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/status')
def api_status():
    """API endpoint to get status"""
    try:
        status = controller.status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/control/logs')
def api_logs():
    """API endpoint to get recent logs"""
    try:
        log_file = Path('logs/automation_controller.log')
        recent_logs = []
        
        if log_file.exists():
            with open(log_file, 'r') as f:
                lines = f.readlines()
                recent_logs = lines[-50:]  # Last 50 lines
        
        return jsonify({
            'success': True,
            'logs': recent_logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('logs', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("🌐 Starting Control Panel Server...")
    print("   Access at: http://localhost:5001/control")
    
    app.run(debug=True, host='0.0.0.0', port=5001)
