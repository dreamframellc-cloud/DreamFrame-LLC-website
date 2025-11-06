"""
WSGI module for DreamFrame LLC application
This file serves as the entry point for WSGI servers like Gunicorn in production
"""

import os
import logging

# Set up logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Flask application
from app import app

# Configure for production deployment
if os.environ.get('PORT'):
    # Production environment - just expose the app
    application = app
    logger.info("WSGI application configured for production deployment")
else:
    # Development environment - initialize database
    try:
        from models import init_database
        init_database(app)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    application = app

if __name__ == "__main__":
    # For development - use Flask's built-in server
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)