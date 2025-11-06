#!/usr/bin/env python3
"""
Database initialization script for DreamFrame LLC
Run this script to initialize the database with default data
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_database():
    """Initialize database with default data"""
    try:
        from app import app
        from models import init_database
        
        logger.info("Starting database initialization...")
        init_database(app)
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = initialize_database()
    sys.exit(0 if success else 1)