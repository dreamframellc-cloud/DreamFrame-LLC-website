#!/usr/bin/env python3
"""
Deployment verification script for DreamFrame LLC
Checks all deployment requirements and configurations
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_deployment_files():
    """Check if all required deployment files exist"""
    required_files = [
        'wsgi_simple.py',
        'gunicorn.conf.py', 
        'pyproject.toml',
        'Procfile',
        'runtime.txt',
        'start.sh'
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        logger.error(f"Missing deployment files: {missing_files}")
        return False
    
    logger.info("✅ All deployment files present")
    return True

def check_wsgi_configuration():
    """Test WSGI application loading"""
    try:
        from wsgi_simple import application
        logger.info("✅ WSGI application loads successfully")
        return True
    except Exception as e:
        logger.error(f"❌ WSGI application failed to load: {e}")
        return False

def check_gunicorn_config():
    """Verify gunicorn configuration"""
    try:
        # Check if gunicorn.conf.py exists and is syntactically valid
        with open('gunicorn.conf.py', 'r') as f:
            config_content = f.read()
        
        # Try to compile the configuration
        compile(config_content, 'gunicorn.conf.py', 'exec')
        logger.info("✅ Gunicorn configuration is valid")
        return True
    except Exception as e:
        logger.error(f"❌ Gunicorn configuration error: {e}")
        return False

def check_environment_variables():
    """Check required environment variables"""
    required_vars = ['DATABASE_URL', 'SESSION_SECRET']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.info("These will be provided by the deployment environment")
    else:
        logger.info("✅ All environment variables present")
    
    return True

def check_pyproject_config():
    """Verify pyproject.toml has correct configuration"""
    try:
        with open('pyproject.toml', 'r') as f:
            content = f.read()
            
        if '[build-system]' in content:
            logger.error("❌ pyproject.toml still contains [build-system] section")
            return False
        
        if 'setuptools' in content and 'packages' in content:
            logger.error("❌ pyproject.toml contains setuptools package configuration")
            return False
            
        logger.info("✅ pyproject.toml configuration is correct")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to check pyproject.toml: {e}")
        return False

def main():
    """Run all deployment checks"""
    logger.info("Running DreamFrame LLC deployment verification...")
    
    checks = [
        ("Deployment files", check_deployment_files),
        ("WSGI configuration", check_wsgi_configuration), 
        ("Gunicorn configuration", check_gunicorn_config),
        ("Environment variables", check_environment_variables),
        ("PyProject configuration", check_pyproject_config)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        logger.info(f"\n--- Checking {check_name} ---")
        if not check_func():
            all_passed = False
    
    if all_passed:
        logger.info("\n🎉 All deployment checks passed! Ready for deployment.")
    else:
        logger.error("\n❌ Some deployment checks failed. Fix issues before deploying.")
        sys.exit(1)

if __name__ == "__main__":
    main()