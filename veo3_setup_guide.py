#!/usr/bin/env python3
"""
VEO 3 Setup Guide
Complete setup instructions for authentic VEO 3 access via Vertex AI
"""

import os
import json

def check_veo3_setup():
    """Check current VEO 3 setup status and provide next steps"""
    
    print("🔍 VEO 3 Setup Status Check")
    print("="*30)
    
    # Check credentials
    creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    
    print(f"📋 Current Status:")
    print(f"   Credentials: {'✅ Present' if creds else '❌ Missing'}")
    print(f"   Project ID: {'✅ Present' if project_id else '❌ Missing'}")
    
    if creds:
        print(f"   Credentials type: {'JSON' if creds.startswith('{') else 'Email/Path'}")
        if not creds.startswith('{'):
            print("   ⚠️  Credentials appear to be email/path, not full JSON")
    
    print("\n🎯 For Authentic VEO 3 Access, you need:")
    print("="*45)
    
    print("1. 📝 GOOGLE_CLOUD_PROJECT_ID")
    print("   - Your Google Cloud project ID (appears to be 'dreamframe')")
    print("   - Where VEO 3 is enabled")
    
    print("\n2. 🔑 GOOGLE_APPLICATION_CREDENTIALS")
    print("   - Full JSON service account key")
    print("   - Should start with { and contain private_key, client_email, etc.")
    print("   - Download from Google Cloud Console > IAM & Admin > Service Accounts")
    
    print("\n3. 🚀 VEO 3 API Access")
    print("   - Enable Vertex AI API in your Google Cloud project")
    print("   - Request VEO 3 model access (may require waitlist)")
    print("   - Ensure service account has Vertex AI User role")
    
    print("\n📋 Next Steps:")
    print("="*15)
    
    if not creds or not creds.startswith('{'):
        print("❗ IMMEDIATE: Update GOOGLE_APPLICATION_CREDENTIALS")
        print("   - Get full JSON service account key from Google Cloud Console")
        print("   - Replace current value with complete JSON string")
    
    print("❗ ENABLE VEO 3: In Google Cloud Console")
    print("   - Go to Vertex AI > Model Garden")
    print("   - Search for 'VEO 3' or 'video generation'")
    print("   - Enable VEO 3 models for your project")
    
    print("❗ PERMISSIONS: Ensure service account has:")
    print("   - Vertex AI User role")
    print("   - Storage Admin role (for video storage)")
    
    return creds and creds.startswith('{') and project_id

def create_test_veo3_request():
    """Create test request format for VEO 3"""
    
    print("\n🧪 VEO 3 Test Request Format")
    print("="*30)
    
    test_request = {
        "endpoint": "https://us-central1-aiplatform.googleapis.com/v1/projects/dreamframe/locations/us-central1/publishers/google/models/veo-3.0-generate-001:predictLongRunning",
        "method": "POST",
        "headers": {
            "Authorization": "Bearer YOUR_ACCESS_TOKEN",
            "Content-Type": "application/json",
            "X-Goog-User-Project": "dreamframe"
        },
        "payload": {
            "instances": [{
                "prompt": "Professional video of a phoenix rising from flames with cinematic lighting"
            }],
            "parameters": {
                "aspectRatio": "16:9",
                "durationSeconds": 8,
                "enhancePrompt": True,
                "generateAudio": True,
                "resolution": "1080p",
                "sampleCount": 1
            }
        }
    }
    
    print("📡 Request will be sent to:")
    print(f"   {test_request['endpoint']}")
    
    print("\n📝 Expected responses:")
    print("   ✅ 200: VEO 3 generation started (operation name returned)")
    print("   ❌ 404: VEO 3 model not found/enabled")
    print("   ❌ 403: Permission denied (need Vertex AI User role)")
    print("   ❌ 401: Authentication failed (check credentials)")
    
    return test_request

if __name__ == "__main__":
    print("🎬 DreamFrame VEO 3 Setup Guide")
    print("="*35)
    print("Setting up authentic VEO 3 integration for professional video generation")
    print("Competitive quality matching Kling AI standards")
    
    # Check current setup
    setup_complete = check_veo3_setup()
    
    # Show test request format
    create_test_veo3_request()
    
    if setup_complete:
        print("\n🎉 SETUP APPEARS COMPLETE!")
        print("Ready to test VEO 3 access")
    else:
        print("\n⚠️  SETUP INCOMPLETE")
        print("Complete the steps above for authentic VEO 3 access")
    
    print("\n🏆 Once setup is complete:")
    print("   - Customer videos will use authentic VEO 3")
    print("   - Professional quality competitive with Kling AI")
    print("   - No fallbacks - only authentic VEO 3 generation")