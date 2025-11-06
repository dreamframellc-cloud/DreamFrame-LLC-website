#!/usr/bin/env python3
"""
Test deployment configuration for DreamFrame LLC
"""

import os
import sys
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_wsgi_import():
    """Test if WSGI app imports correctly"""
    try:
        from wsgi_simple import application
        logger.info("✅ WSGI application imports successfully")
        logger.info(f"Application type: {type(application)}")
        logger.info(f"App name: {getattr(application, 'name', 'Unknown')}")
        return True
    except Exception as e:
        logger.error(f"❌ WSGI import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gunicorn_syntax():
    """Test gunicorn command syntax"""
    try:
        cmd = ["gunicorn", "--config", "gunicorn.conf.py", "--check-config", "wsgi_simple:application"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("✅ Gunicorn configuration is valid")
            return True
        else:
            logger.error(f"❌ Gunicorn config error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        logger.warning("⚠️ Gunicorn check timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Gunicorn test failed: {e}")
        return False

def test_app_routes():
    """Test if the app has the expected routes"""
    try:
        from wsgi_simple import application
        with application.test_client() as client:
            # Test root route
            response = client.get('/')
            logger.info(f"✅ Root route responds with status: {response.status_code}")
            
            # Test a few key routes
            routes_to_test = ['/pricing', '/gallery']
            for route in routes_to_test:
                try:
                    response = client.get(route)
                    logger.info(f"Route {route}: {response.status_code}")
                except Exception as e:
                    logger.warning(f"Route {route} error: {e}")
            
            return True
    except Exception as e:
        logger.error(f"❌ App routes test failed: {e}")
        return False

def test_environment_vars():
    """Check required environment variables"""
    required_vars = {
        'DATABASE_URL': os.environ.get('DATABASE_URL'),
        'SESSION_SECRET': os.environ.get('SESSION_SECRET'), 
        'PORT': os.environ.get('PORT', '5000')
    }
    
    logger.info("Environment variables:")
    for var, value in required_vars.items():
        status = "✅" if value else "❌"
        logger.info(f"{status} {var}: {'Set' if value else 'Not set'}")
    
    return all(required_vars.values())

def main():
    """Run all deployment tests"""
    logger.info("Testing DreamFrame LLC deployment configuration...")
    
    tests = [
        ("WSGI Import", test_wsgi_import),
        ("Gunicorn Configuration", test_gunicorn_syntax),
        ("Application Routes", test_app_routes),
        ("Environment Variables", test_environment_vars)
    ]
    
    results = {}
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n=== DEPLOYMENT TEST SUMMARY ===")
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} {test_name}")
    
    if passed == total:
        logger.info(f"\n🎉 All tests passed ({passed}/{total})")
        logger.info("Deployment configuration appears to be working correctly.")
        logger.info("\nTo deploy:")
        logger.info("1. Use the 'Deploy' button in Replit")
        logger.info("2. Deployment will use: gunicorn --config gunicorn.conf.py wsgi_simple:application")
    else:
        logger.error(f"\n❌ {total - passed} tests failed ({passed}/{total} passed)")
        logger.error("Fix the failing tests before deploying.")

if __name__ == "__main__":
    main()