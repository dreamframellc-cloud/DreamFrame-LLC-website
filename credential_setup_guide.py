#!/usr/bin/env python3
"""
Credential Setup Guide for VEO 3 Integration
"""

import os
import json

def analyze_current_credentials():
    """Analyze what's currently in the credentials"""
    
    print("Analyzing current credential format...")
    
    creds_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    if not creds_env:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS is empty")
        return False
    
    print(f"📊 Current format: {type(creds_env)}")
    print(f"📊 Length: {len(creds_env)} characters")
    print(f"📊 Starts with: {creds_env[:50]}...")
    
    # Check if it's valid JSON
    try:
        data = json.loads(creds_env)
        print("✅ Valid JSON detected")
        
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            print(f"❌ Missing fields: {missing_fields}")
            return False
        else:
            print("✅ All required fields present")
            return True
            
    except json.JSONDecodeError:
        print("❌ Not valid JSON format")
        
        # Check if it looks like raw credential content
        if '"type":' in creds_env and '"project_id":' in creds_env:
            print("🔧 Appears to be JSON content but improperly formatted")
            return "needs_formatting"
        else:
            print("❌ Unrecognized credential format")
            return False

def show_setup_instructions():
    """Show instructions for proper setup"""
    
    print("\n" + "="*60)
    print("CREDENTIAL SETUP INSTRUCTIONS FOR VEO 3")
    print("="*60)
    
    print("""
1. **For Replit Secrets Panel**:
   - Go to Tools → Secrets in Replit
   - Find GOOGLE_APPLICATION_CREDENTIALS
   - The value should be a single line JSON string like:
   
   {"type":"service_account","project_id":"dreamframe",...}

2. **Required JSON Fields**:
   - type: "service_account"
   - project_id: "dreamframe"
   - private_key_id: "your_key_id"
   - private_key: "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n"
   - client_email: "your-service-account@dreamframe.iam.gserviceaccount.com"
   - client_id: "your_client_id"
   - auth_uri: "https://accounts.google.com/o/oauth2/auth"
   - token_uri: "https://oauth2.googleapis.com/token"

3. **Common Issues**:
   - ❌ Multi-line format (needs to be single line)
   - ❌ Missing escape characters in private_key (\\n instead of actual newlines)
   - ❌ Missing quotes around field values
   - ❌ Extra spaces or formatting

4. **Test Setup**:
   After updating the secret, restart your Replit to reload environment variables.
   """)

def create_credential_template():
    """Create a template for proper credential format"""
    
    template = {
        "type": "service_account",
        "project_id": "dreamframe",
        "private_key_id": "YOUR_PRIVATE_KEY_ID",
        "private_key": "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_CONTENT\\n-----END PRIVATE KEY-----\\n",
        "client_email": "your-service-account@dreamframe.iam.gserviceaccount.com",
        "client_id": "YOUR_CLIENT_ID",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40dreamframe.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    print("\n📄 CREDENTIAL TEMPLATE:")
    print("="*40)
    print(json.dumps(template, indent=2))
    
    print("\n🔧 SINGLE LINE FORMAT (for Replit Secrets):")
    print("="*40)
    print(json.dumps(template))

if __name__ == "__main__":
    print("VEO 3 Credential Setup Analysis")
    print("=" * 40)
    
    result = analyze_current_credentials()
    
    if result == True:
        print("\n✅ Credentials appear to be properly formatted!")
        print("If VEO 3 still fails, the issue may be:")
        print("- Model access permissions")
        print("- Project configuration")
        print("- Regional availability")
    else:
        show_setup_instructions()
        create_credential_template()