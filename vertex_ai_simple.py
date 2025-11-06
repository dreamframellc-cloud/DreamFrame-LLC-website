#!/usr/bin/env python3
"""
Simplified Vertex AI VEO 3 Integration
Direct authentication approach for authentic VEO 3 access
"""

import os
import time
import requests
import json
import base64
from typing import Optional, Dict, Any

def get_vertex_ai_access_token():
    """Get access token using service account credentials"""
    
    credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS required")
    
    try:
        # Parse JSON credentials
        if credentials_json.startswith('{'):
            # JSON string format
            credentials = json.loads(credentials_json)
        else:
            # File path format
            with open(credentials_json, 'r') as f:
                credentials = json.load(f)
        
        # Create JWT assertion
        import jwt
        import datetime
        
        now = datetime.datetime.utcnow()
        
        payload = {
            'iss': credentials['client_email'],
            'scope': 'https://www.googleapis.com/auth/cloud-platform',
            'aud': 'https://oauth2.googleapis.com/token',
            'iat': now,
            'exp': now + datetime.timedelta(hours=1)
        }
        
        # Sign JWT with private key
        token = jwt.encode(payload, credentials['private_key'], algorithm='RS256')
        
        # Exchange JWT for access token
        response = requests.post('https://oauth2.googleapis.com/token', data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': token
        })
        
        if response.status_code == 200:
            access_token = response.json()['access_token']
            print("✅ Successfully obtained access token")
            return access_token
        else:
            print(f"❌ Token exchange failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {str(e)}")
        return None

def test_vertex_ai_veo3_simple():
    """Simple test of Vertex AI VEO 3 access"""
    
    print("Testing Simplified Vertex AI VEO 3 Access")
    print("="*45)
    
    # Parse project ID from credentials
    credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    if not credentials_json:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not found")
        return False
    
    try:
        if credentials_json.startswith('{'):
            credentials = json.loads(credentials_json)
            project_id = credentials.get('project_id')
        else:
            # Also check GOOGLE_CLOUD_PROJECT_ID env var
            project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
            
        if not project_id:
            print("❌ Could not find project_id in credentials")
            return False
            
        print(f"Project ID: {project_id}")
        
    except Exception as e:
        print(f"❌ Error parsing credentials: {str(e)}")
        return False
    
    # Get access token
    access_token = get_vertex_ai_access_token()
    if not access_token:
        return False
    
    # Test VEO 3 model access
    location = "us-central1"
    model = "veo-3.0-generate-001"
    
    endpoint = (f"https://{location}-aiplatform.googleapis.com/v1/"
               f"projects/{project_id}/locations/{location}/"
               f"publishers/google/models/{model}:predictLongRunning")
    
    # Simple test payload
    payload = {
        "instances": [{
            "prompt": "A professional logo animation with smooth transitions and modern design"
        }],
        "parameters": {
            "aspectRatio": "16:9",
            "durationSeconds": 8,
            "enhancePrompt": True,
            "generateAudio": False,
            "resolution": "720p",
            "sampleCount": 1
        }
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id
    }
    
    print("Testing VEO 3 model access...")
    print(f"Endpoint: {endpoint}")
    
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ VEO 3 request accepted!")
            
            if 'name' in result:
                operation_name = result['name']
                print(f"Operation started: {operation_name}")
                print("🎉 AUTHENTIC VEO 3 ACCESS CONFIRMED!")
                return True
            else:
                print("❌ No operation name in response")
                print(f"Response: {json.dumps(result, indent=2)}")
                return False
        else:
            print(f"❌ VEO 3 request failed: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Check if it's a model availability issue
            if "not found" in response.text.lower():
                print("⚠️ VEO 3 model may not be available in this region/project")
                print("Try enabling VEO 3 in Google Cloud Console or different region")
            
            return False
            
    except Exception as e:
        print(f"❌ Request error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_vertex_ai_veo3_simple()
    
    if success:
        print("\n🎉 READY FOR CUSTOMER VEO 3 GENERATION")
        print("Authentic VEO 3 integration successful - competitive with Kling AI")
    else:
        print("\n⚠️ VEO 3 access needs configuration")
        print("Check Google Cloud Console for VEO 3 model availability")