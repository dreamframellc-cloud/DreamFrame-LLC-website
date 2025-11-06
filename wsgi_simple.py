"""
Simplified WSGI entry point for deployment
Avoids complex initialization that may fail in production
"""

import os
import logging

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from app import app
    application = app
    logger.info("DreamFrame LLC WSGI application loaded successfully")
except Exception as e:
    logger.error(f"Failed to load application: {e}")
    raise

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)