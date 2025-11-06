#!/usr/bin/env python3
"""Test download functionality for completed projects"""

import requests
import os

def test_download():
    print("Testing download functionality...")
    
    # Test project 7 download
    url = "http://localhost:5000/admin/project/7/download"
    print(f"Testing URL: {url}")
    
    try:
        response = requests.get(url, stream=True)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Download successful!")
            content_length = response.headers.get('content-length', 'unknown')
            print(f"File size: {content_length} bytes")
        else:
            print(f"❌ Download failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_download()