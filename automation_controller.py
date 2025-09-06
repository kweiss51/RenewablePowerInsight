#!/usr/bin/env python3
"""
Energy Blog Automation Controller
Provides start/stop controls and configurable run parameters
"""

import sys
import os
import signal
import json
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
import threading
import logging

# Add the project root to the path
sys.path.append(str(Path(__file__).parent))

from daily_automation import DailyEnergyAutomation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation_controller.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AutomationController:
    """Controls the automation system with start/stop and configuration capabilities"""
    
    def __init__(self):
        self.automation = DailyEnergyAutomation()
        self.control_file = Path('logs/automation_control.json')
        self.is_running = False
        self.should_stop = False
        self.current_config = {}
        self.stats = {
            'start_time': None,
            'days_completed': 0,
            'posts_generated': 0,
            'total_articles_collected': 0,
            'last_run': None
        }
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, initiating graceful shutdown...")
        self.stop()
    
    def save_control_state(self):
        """Save the current control state"""
        state = {
            'is_running': self.is_running,
            'config': self.current_config,
            'stats': self.stats,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.control_file, 'w') as f:
            json.dump(state, f, indent=2, default=str)
    
    def load_control_state(self):
        """Load the control state"""
        if self.control_file.exists():
            try:
                with open(self.control_file, 'r') as f:
                    state = json.load(f)
                    self.current_config = state.get('config', {})
                    self.stats = state.get('stats', self.stats)
                    # Don't restore running state on startup
                    return state
            except Exception as e:
                logger.warning(f"Failed to load control state: {e}")
        return {}
    
    def start(self, days: int = None, posts_per_day: int = None, 
              hours_interval: int = None, run_immediately: bool = False):
        """
        Start the automation with specified parameters
        
        Args:
            days: Number of days to run (None = indefinite)
            posts_per_day: Maximum posts to generate per day
            hours_interval: Hours between runs (default: 24)
            run_immediately: Whether to run immediately or wait for schedule
        """
        
        if self.is_running:
            logger.warning("⚠️ Automation is already running!")
            return False
        
        # Configuration
        self.current_config = {
            'days': days,
            'posts_per_day': posts_per_day or 10,
            'hours_interval': hours_interval or 24,
            'run_immediately': run_immediately,
            'start_time': datetime.now().isoformat()
        }
        
        # Reset stats
        self.stats = {
            'start_time': datetime.now().isoformat(),
            'days_completed': 0,
            'posts_generated': 0,
            'total_articles_collected': 0,
            'last_run': None
        }
        
        self.is_running = True
        self.should_stop = False
        
        # Update automation settings
        self.automation.max_posts_per_day = self.current_config['posts_per_day']
        
        logger.info("🚀 Starting Energy Blog Automation")
        logger.info(f"   📅 Days to run: {days if days else 'Indefinite'}")
        logger.info(f"   ✍️ Posts per day: {posts_per_day}")
        logger.info(f"   ⏰ Interval: {hours_interval} hours")
        
        self.save_control_state()
        
        # Start the automation thread
        automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        automation_thread.start()
        
        # Run immediately if requested
        if run_immediately:
            logger.info("▶️ Running automation immediately...")
            self._run_automation_cycle()
        
        return True
    
    def stop(self):
        """Stop the automation gracefully"""
        if not self.is_running:
            logger.info("ℹ️ Automation is not running")
            return
        
        logger.info("🛑 Stopping automation...")
        self.should_stop = True
        self.is_running = False
        
        # Save final state
        self.save_control_state()
        
        logger.info("✅ Automation stopped successfully")
    
    def pause(self):
        """Pause the automation without stopping"""
        if not self.is_running:
            logger.info("ℹ️ Automation is not running")
            return
        
        logger.info("⏸️ Pausing automation...")
        self.current_config['paused'] = True
        self.save_control_state()
        logger.info("✅ Automation paused")
    
    def resume(self):
        """Resume paused automation"""
        if not self.is_running:
            logger.info("ℹ️ Automation is not running")
            return
        
        if not self.current_config.get('paused'):
            logger.info("ℹ️ Automation is not paused")
            return
        
        logger.info("▶️ Resuming automation...")
        self.current_config['paused'] = False
        self.save_control_state()
        logger.info("✅ Automation resumed")
    
    def status(self):
        """Get current automation status"""
        state = self.load_control_state()
        
        if self.is_running:
            status_text = "🟢 RUNNING"
            if self.current_config.get('paused'):
                status_text = "🟡 PAUSED"
        else:
            status_text = "🔴 STOPPED"
        
        logger.info("📊 Automation Status:")
        logger.info(f"   Status: {status_text}")
        
        if self.current_config:
            config = self.current_config
            logger.info(f"   📅 Days configured: {config.get('days', 'Indefinite')}")
            logger.info(f"   ✍️ Posts per day: {config.get('posts_per_day', 'N/A')}")
            logger.info(f"   ⏰ Interval: {config.get('hours_interval', 'N/A')} hours")
            
            if config.get('start_time'):
                start_time = datetime.fromisoformat(config['start_time'])
                runtime = datetime.now() - start_time
                logger.info(f"   ⏱️ Runtime: {runtime}")
        
        if self.stats:
            logger.info(f"   📈 Days completed: {self.stats.get('days_completed', 0)}")
            logger.info(f"   ✍️ Posts generated: {self.stats.get('posts_generated', 0)}")
            logger.info(f"   📚 Articles collected: {self.stats.get('total_articles_collected', 0)}")
            
            if self.stats.get('last_run'):
                last_run = datetime.fromisoformat(self.stats['last_run'])
                logger.info(f"   🕐 Last run: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            'running': self.is_running,
            'paused': self.current_config.get('paused', False),
            'config': self.current_config,
            'stats': self.stats
        }
    
    def _automation_loop(self):
        """Main automation loop running in background thread"""
        logger.info("🔄 Automation loop started")
        
        while self.is_running and not self.should_stop:
            try:
                # Check if paused
                if self.current_config.get('paused'):
                    time.sleep(60)  # Check every minute when paused
                    continue
                
                # Check if we should run based on interval
                if self._should_run_now():
                    self._run_automation_cycle()
                
                # Check if we've completed the configured days
                if self._has_completed_duration():
                    logger.info("✅ Completed configured duration, stopping automation")
                    self.stop()
                    break
                
                # Sleep for a minute before checking again
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"❌ Error in automation loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _should_run_now(self):
        """Check if automation should run now based on interval"""
        if not self.stats.get('last_run'):
            return True  # First run
        
        last_run = datetime.fromisoformat(self.stats['last_run'])
        interval_hours = self.current_config.get('hours_interval', 24)
        next_run = last_run + timedelta(hours=interval_hours)
        
        return datetime.now() >= next_run
    
    def _has_completed_duration(self):
        """Check if the configured duration has been completed"""
        days_limit = self.current_config.get('days')
        if not days_limit:
            return False  # No limit set
        
        return self.stats.get('days_completed', 0) >= days_limit
    
    def _run_automation_cycle(self):
        """Run a single automation cycle"""
        if self.current_config.get('paused'):
            return
        
        logger.info("🔄 Starting automation cycle...")
        cycle_start = datetime.now()
        
        try:
            # Run the daily automation
            self.automation.run_daily_automation()
            
            # Update stats
            self.stats['last_run'] = cycle_start.isoformat()
            self.stats['days_completed'] += 1
            
            # Count generated posts (rough estimate)
            self.stats['posts_generated'] += self.current_config.get('posts_per_day', 0)
            
            # Save state
            self.save_control_state()
            
            cycle_duration = datetime.now() - cycle_start
            logger.info(f"✅ Automation cycle completed in {cycle_duration}")
            
        except Exception as e:
            logger.error(f"❌ Automation cycle failed: {e}")
    
    def run_single_cycle(self):
        """Run a single automation cycle manually"""
        if self.is_running:
            logger.warning("⚠️ Automation is already running! Use stop() first.")
            return False
        
        logger.info("🔄 Running single automation cycle...")
        self._run_automation_cycle()
        return True

def main():
    """Command line interface for automation controller"""
    parser = argparse.ArgumentParser(description='Energy Blog Automation Controller')
    parser.add_argument('action', choices=['start', 'stop', 'pause', 'resume', 'status', 'run-once'],
                       help='Action to perform')
    parser.add_argument('--days', type=int, help='Number of days to run (default: indefinite)')
    parser.add_argument('--posts-per-day', type=int, default=10, 
                       help='Maximum posts per day (default: 10)')
    parser.add_argument('--interval', type=int, default=24,
                       help='Hours between runs (default: 24)')
    parser.add_argument('--immediate', action='store_true',
                       help='Run immediately when starting')
    
    args = parser.parse_args()
    
    # Create controller
    controller = AutomationController()
    controller.load_control_state()
    
    try:
        if args.action == 'start':
            success = controller.start(
                days=args.days,
                posts_per_day=args.posts_per_day,
                hours_interval=args.interval,
                run_immediately=args.immediate
            )
            
            if success:
                logger.info("🎯 Automation started! Use 'python automation_controller.py status' to check progress")
                logger.info("   Press Ctrl+C to stop gracefully")
                
                # Keep the main thread alive
                try:
                    while controller.is_running:
                        time.sleep(1)
                except KeyboardInterrupt:
                    logger.info("🛑 Keyboard interrupt received")
                    controller.stop()
        
        elif args.action == 'stop':
            controller.stop()
        
        elif args.action == 'pause':
            controller.pause()
        
        elif args.action == 'resume':
            controller.resume()
        
        elif args.action == 'status':
            controller.status()
        
        elif args.action == 'run-once':
            controller.run_single_cycle()
    
    except KeyboardInterrupt:
        logger.info("🛑 Keyboard interrupt received")
        controller.stop()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
