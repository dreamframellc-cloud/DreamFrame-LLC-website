#!/usr/bin/env python3
"""
Test Runway ML API connection and credentials
"""

import os
import requests
import json

def test_runway_api():
    """Test Runway ML API authentication and endpoints"""
    api_key = os.environ.get('RUNWAYML_API_KEY')
    
    if not api_key:
        print("❌ RUNWAYML_API_KEY not found")
        return False
    
    print(f"🔑 API Key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Test 1: Check API authentication
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Try different base URLs
    base_urls = [
        "https://api.runwayml.com/v1",
        "https://api.dev.runwayml.com/v1", 
        "https://api.runwayml.ai/v1"
    ]
    
    for base_url in base_urls:
        print(f"\n🌐 Testing endpoint: {base_url}")
        
        # Test account/user info endpoint
        test_endpoints = [
            f"{base_url}/me",
            f"{base_url}/user", 
            f"{base_url}/account",
            f"{base_url}/tasks"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = requests.get(endpoint, headers=headers, timeout=10)
                print(f"  📡 {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"  ✅ Success! Response: {response.json()}")
                    return True
                elif response.status_code == 401:
                    print(f"  🔐 Authentication failed")
                elif response.status_code == 404:
                    print(f"  🔍 Endpoint not found")
                else:
                    print(f"  ❓ Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Testing Runway ML API Connection")
    print("=" * 50)
    
    success = test_runway_api()
    
    if success:
        print("\n✅ Runway ML API is working!")
    else:
        print("\n❌ Runway ML API connection failed")
        print("\n💡 Possible solutions:")
        print("   1. Verify API key is correct")
        print("   2. Check if account has credits/subscription")
        print("   3. Try different API endpoints")
        print("   4. Contact Runway ML support")