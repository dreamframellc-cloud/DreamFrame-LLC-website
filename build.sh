#!/bin/bash
# Build script for Render deployment
# This script runs before the start command

set -e

echo "🚀 Building DreamFrame LLC application..."

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories (they'll be ephemeral but needed for startup)
echo "📁 Creating directories..."
mkdir -p static/videos static/thumbnails static/uploads static/ai_generated uploads processed

# Verify critical files
echo "✅ Verifying critical files..."
if [ ! -f "wsgi_simple.py" ]; then
    echo "❌ Error: wsgi_simple.py not found!"
    exit 1
fi

if [ ! -f "gunicorn.conf.py" ]; then
    echo "❌ Error: gunicorn.conf.py not found!"
    exit 1
fi

echo "✅ Build complete!"

