#!/usr/bin/env python3
"""
Fix Google Cloud credentials for VEO 2 access
"""

import os
import json
import tempfile

def fix_credentials():
    """Fix and validate Google Cloud credentials"""
    
    creds_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    print(f"Raw credentials length: {len(creds_raw)}")
    print(f"First 50 chars: {creds_raw[:50]}")
    
    if not creds_raw:
        print("❌ No credentials found")
        return None
    
    # Try to parse as JSON
    try:
        # Clean the string
        creds_clean = creds_raw.strip()
        
        # Check if it starts with proper JSON
        if not creds_clean.startswith('{'):
            print("❌ Credentials don't start with '{' - not valid JSON")
            return None
        
        # Parse JSON
        creds_dict = json.loads(creds_clean)
        
        # Validate structure
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        for field in required_fields:
            if field not in creds_dict:
                print(f"❌ Missing field: {field}")
                return None
        
        print("✅ Credentials are valid JSON!")
        print(f"Project: {creds_dict['project_id']}")
        print(f"Service Account: {creds_dict['client_email']}")
        
        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds_dict, f, indent=2)
            temp_path = f.name
        
        print(f"✅ Created temp file: {temp_path}")
        
        # Test the temp file
        with open(temp_path, 'r') as f:
            test_data = json.load(f)
        
        print("✅ Temp file is readable")
        return temp_path
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        print(f"Error at position: {e.pos if hasattr(e, 'pos') else 'unknown'}")
        return None

if __name__ == "__main__":
    print("🔧 Fixing Google Cloud Credentials")
    print("=" * 50)
    
    temp_file = fix_credentials()
    
    if temp_file:
        print(f"\n📁 Temporary credentials file: {temp_file}")
        print("\n🧪 Testing with Google OAuth...")
        
        # Test credential loading
        try:
            from google.oauth2 import service_account
            from google.auth.transport.requests import Request
            
            creds = service_account.Credentials.from_service_account_file(
                temp_file,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            print("✅ Credentials loaded successfully")
            
            # Test token refresh
            creds.refresh(Request())
            print("✅ Token refresh successful")
            print(f"Token: {creds.token[:20]}...")
            
        except Exception as e:
            print(f"❌ Credential test failed: {e}")
    
    print("\n" + "=" * 50)