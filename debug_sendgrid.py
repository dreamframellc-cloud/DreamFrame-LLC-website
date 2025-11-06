#!/usr/bin/env python3
"""
Debug SendGrid API key configuration
"""

import os
import requests

def debug_sendgrid():
    """Debug SendGrid API key and permissions"""
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    
    print("SendGrid API Key Debug")
    print("=" * 30)
    
    if not api_key:
        print("❌ No SENDGRID_API_KEY found in environment")
        return
    
    print(f"✅ API Key found: {len(api_key)} characters")
    print(f"   Starts with: {api_key[:10]}...")
    print(f"   Ends with: ...{api_key[-10:]}")
    
    # Test API key validity with SendGrid API
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test 1: Check API key validity
    print("\n🔍 Testing API key validity...")
    try:
        response = requests.get('https://api.sendgrid.com/v3/user/profile', headers=headers)
        print(f"   Profile API: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API key is valid")
        elif response.status_code == 401:
            print("   ❌ API key is invalid or expired")
        elif response.status_code == 403:
            print("   ⚠️  API key valid but lacks permissions")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Test 2: Check scopes/permissions
    print("\n🔍 Testing API key scopes...")
    try:
        response = requests.get('https://api.sendgrid.com/v3/scopes', headers=headers)
        print(f"   Scopes API: {response.status_code}")
        if response.status_code == 200:
            scopes = response.json()
            print(f"   Available scopes: {len(scopes)} total")
            if 'mail.send' in scopes:
                print("   ✅ Mail Send permission available")
            else:
                print("   ❌ Mail Send permission MISSING")
        else:
            print("   ❌ Could not retrieve scopes")
    except Exception as e:
        print(f"   ❌ Scopes check error: {e}")
    
    # Test 3: Simple mail send test
    print("\n🔍 Testing mail send capability...")
    
    test_payload = {
        "personalizations": [
            {
                "to": [{"email": "test@example.com"}],
                "subject": "SendGrid Test"
            }
        ],
        "from": {"email": "noreply@dreamframe.com"},
        "content": [
            {
                "type": "text/plain",
                "value": "Test email"
            }
        ]
    }
    
    try:
        response = requests.post('https://api.sendgrid.com/v3/mail/send', 
                               headers=headers, 
                               json=test_payload)
        print(f"   Mail Send API: {response.status_code}")
        if response.status_code == 202:
            print("   ✅ Mail send permission working")
        elif response.status_code == 403:
            print("   ❌ Mail send permission DENIED")
            print("   💡 Need to enable 'Mail Send' in SendGrid dashboard")
        else:
            print(f"   ⚠️  Unexpected response: {response.text}")
    except Exception as e:
        print(f"   ❌ Mail send test error: {e}")
    
    print("\n📋 Summary:")
    print("   The API key needs 'Mail Send' permissions enabled")
    print("   Go to SendGrid Dashboard > Settings > API Keys")
    print("   Edit your API key and enable 'Mail Send' permission")

if __name__ == "__main__":
    debug_sendgrid()