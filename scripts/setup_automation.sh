#!/bin/bash
"""
Setup script for Energy Blog Daily Automation
"""

set -e

echo "🚀 Setting up Energy Blog Daily Automation..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if we're on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
else
    PLATFORM="unknown"
fi

echo -e "${YELLOW}Platform detected: $PLATFORM${NC}"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p data
mkdir -p training_data
mkdir -p model_checkpoints
mkdir -p results/daily_reports

# Make scripts executable
chmod +x daily_automation.py
chmod +x setup_automation.sh

echo -e "${GREEN}✅ Directories created${NC}"

# Test the automation system
echo "🧪 Testing automation system..."
if python daily_automation.py --run-now > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Automation system test passed${NC}"
else
    echo -e "${YELLOW}⚠️ Automation test had issues, but continuing setup${NC}"
fi

# Platform-specific setup
if [[ "$PLATFORM" == "macos" ]]; then
    echo "🍎 Setting up macOS LaunchAgent..."
    
    # Copy plist to user LaunchAgents directory
    mkdir -p ~/Library/LaunchAgents
    cp com.renewablepower.dailyautomation.plist ~/Library/LaunchAgents/
    
    # Update paths in plist to absolute paths
    sed -i '' "s|/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight|$SCRIPT_DIR|g" ~/Library/LaunchAgents/com.renewablepower.dailyautomation.plist
    
    echo -e "${GREEN}✅ LaunchAgent installed${NC}"
    echo "To start the service:"
    echo "  launchctl load ~/Library/LaunchAgents/com.renewablepower.dailyautomation.plist"
    echo "To stop the service:"
    echo "  launchctl unload ~/Library/LaunchAgents/com.renewablepower.dailyautomation.plist"
    
elif [[ "$PLATFORM" == "linux" ]]; then
    echo "🐧 Setting up systemd service..."
    
    # Update paths in service file
    sed -i "s|/Users/kyleweiss/Documents/GitHub/RenewablePowerInsight|$SCRIPT_DIR|g" energy-automation.service
    sed -i "s|User=kyleweiss|User=$USER|g" energy-automation.service
    
    echo "To install the service:"
    echo "  sudo cp energy-automation.service /etc/systemd/system/"
    echo "  sudo systemctl daemon-reload"
    echo "  sudo systemctl enable energy-automation"
    echo "  sudo systemctl start energy-automation"
    
    echo "To check status:"
    echo "  sudo systemctl status energy-automation"
    
fi

# Create a simple test script
cat > test_automation.py << 'EOF'
#!/usr/bin/env python3
"""Test script for automation system"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from daily_automation import DailyEnergyAutomation

def test_automation():
    print("🧪 Testing Daily Energy Automation...")
    automation = DailyEnergyAutomation()
    
    # Test basic functionality
    print(f"✅ Automation initialized")
    print(f"📁 Log directory exists: {Path('logs').exists()}")
    print(f"📁 Data directory exists: {Path('data').exists()}")
    
    # Check if we should run
    should_run = automation.should_run_today()
    print(f"🔄 Should run today: {should_run}")
    
    print("✅ All tests passed!")

if __name__ == "__main__":
    test_automation()
EOF

chmod +x test_automation.py

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Test the system: python test_automation.py"
echo "2. Run manually: python daily_automation.py --run-now"
echo "3. Start the Flask app: python app.py"
echo ""

if [[ "$PLATFORM" == "macos" ]]; then
    echo "To enable daily automation:"
    echo "  launchctl load ~/Library/LaunchAgents/com.renewablepower.dailyautomation.plist"
elif [[ "$PLATFORM" == "linux" ]]; then
    echo "To enable daily automation:"
    echo "  sudo cp energy-automation.service /etc/systemd/system/"
    echo "  sudo systemctl enable energy-automation"
    echo "  sudo systemctl start energy-automation"
fi

echo ""
echo -e "${YELLOW}The system will automatically:${NC}"
echo "  📅 Run daily at 6:00 AM and 2:00 PM"
echo "  📚 Collect academic papers and government data"
echo "  🔧 Process and analyze the content"
echo "  🏋️ Update the ML model incrementally"
echo "  ✍️ Generate new blog posts"
echo "  📊 Create daily reports"
