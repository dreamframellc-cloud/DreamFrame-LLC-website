#!/usr/bin/env python3
"""
Install Google Cloud AI Platform package
"""

import subprocess
import sys
import os

def install_aiplatform():
    """Install google-cloud-aiplatform package"""
    
    print("Installing Google Cloud AI Platform...")
    
    try:
        # Method 1: Try standard pip install
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 
            'google-cloud-aiplatform==1.50.0', '--user'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Installation successful via pip")
            return True
        else:
            print(f"Pip install failed: {result.stderr}")
            
    except Exception as e:
        print(f"Pip method failed: {e}")
    
    # Method 2: Try alternative installation
    try:
        print("Trying alternative installation method...")
        
        # Download and install manually
        import urllib.request
        import zipfile
        import tempfile
        
        # This is a simplified approach - in production would use proper wheel installation
        print("Alternative method not implemented - using existing google-cloud packages")
        return False
        
    except Exception as e:
        print(f"Alternative method failed: {e}")
        return False

def test_import():
    """Test if the import works"""
    
    try:
        from google.cloud import aiplatform
        print(f"✅ Successfully imported aiplatform version: {getattr(aiplatform, '__version__', 'unknown')}")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

if __name__ == "__main__":
    print("Google Cloud AI Platform Installation Script")
    print("=" * 50)
    
    # First check if already available
    if test_import():
        print("Package already available!")
        sys.exit(0)
    
    # Try to install
    if install_aiplatform():
        print("Testing import after installation...")
        if test_import():
            print("✅ Installation and import successful!")
        else:
            print("❌ Installation succeeded but import failed")
    else:
        print("❌ Installation failed")
        print("\nNote: VEO 3 will use existing google-cloud libraries")