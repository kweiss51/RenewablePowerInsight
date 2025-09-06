#!/bin/bash

# Energy Blog Startup Script
echo "🚀 Starting Energy News Blog Application..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create data directory if it doesn't exist
mkdir -p data

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "📝 Please edit .env file to add your OpenAI API key (optional)"
fi

# Start the application
echo "🌐 Starting Flask application..."
echo "📍 Application will be available at: http://localhost:5000"
echo "📊 Admin dashboard at: http://localhost:5000/admin"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

python app.py
