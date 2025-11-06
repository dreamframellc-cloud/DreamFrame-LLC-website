#!/bin/bash

# DreamFrame LLC Production Startup Script
# This script handles both development and production environments

set -e

echo "Starting DreamFrame LLC application..."

# Create necessary directories
mkdir -p static/videos static/thumbnails static/uploads uploads processed

# Set environment variables for production
export PYTHONPATH="${PYTHONPATH}:."

# Check if we're in production environment
if [ "$REPLIT_DEPLOYMENT" = "1" ] || [ "$ENVIRONMENT" = "production" ]; then
    echo "Production environment detected - using Gunicorn"
    
    # Set production environment variables
    export FLASK_ENV=production
    export GUNICORN_WORKERS=${GUNICORN_WORKERS:-2}
    
    # Start with Gunicorn using simplified WSGI
    exec gunicorn --config gunicorn.conf.py wsgi_simple:application
else
    echo "Development environment detected - using Flask dev server"
    export FLASK_ENV=development
    python wsgi_simple.py
fi