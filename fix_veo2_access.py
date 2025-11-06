#!/usr/bin/env python3
"""
Fix VEO 2 Access - Test with proper configuration
"""

import os
import json
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def test_veo2_access():
    """Test VEO 2 access with corrected configuration"""
    
    print("🔧 VEO 2 Access Fix Test")
    print("=" * 50)
    
    # Parse credentials properly
    try:
        credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
        if not credentials_json.startswith('{'):
            print("❌ Credentials not in JSON format")
            return False
            
        credentials_dict = json.loads(credentials_json)
        project_id = credentials_dict.get('project_id', 'dreamframe')
        
        print(f"✅ Project ID: {project_id}")
        print(f"✅ Service Account: {credentials_dict.get('client_email')}")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        # Get access token
        credentials.refresh(Request())
        access_token = credentials.token
        
        print("✅ Access token obtained")
        
        # Test VEO 2 endpoint (from Google docs)
        endpoint_url = (
            f"https://us-central1-aiplatform.googleapis.com/v1/"
            f"projects/{project_id}/locations/us-central1/"
            f"publishers/google/models/veo-2.0-generate-001:predictLongRunning"
        )
        
        print(f"🧪 Testing endpoint: {endpoint_url}")
        
        # Test payload based on Google docs
        payload = {
            "instances": [{
                "prompt": "A beautiful landscape with mountains and a lake"
            }],
            "parameters": {
                "duration": 5,
                "aspectRatio": "16:9"
            }
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Make test request
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            print("🎬 VEO 2 IS WORKING!")
            result = response.json()
            print(f"Operation: {result.get('name', 'Generated')}")
            return True
            
        elif response.status_code == 404:
            print("⚠️  VEO 2 Model Not Found")
            print("This might indicate:")
            print("1. VEO 2 not enabled in this project")
            print("2. Different model name required")
            print("3. Regional availability issue")
            
        elif response.status_code == 403:
            print("⚠️  VEO 2 Access Denied")
            print("This might indicate:")
            print("1. Insufficient permissions")
            print("2. Vertex AI API not enabled")
            print("3. Billing not configured")
            
        else:
            print(f"⚠️  API Response: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Response text: {response.text[:200]}")
                
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_veo2_access()
    
    if success:
        print("\n🎯 Next Steps:")
        print("✅ VEO 2 is accessible")
        print("✅ Update DreamFrame to use VEO 2")
        print("✅ Enable customer video generation")
    else:
        print("\n🔍 Debugging Steps:")
        print("1. Check Vertex AI API is enabled")
        print("2. Verify billing is active")
        print("3. Confirm VEO 2 is available in us-central1")
        print("4. Check if project needs VEO 2 approval")