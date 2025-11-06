#!/usr/bin/env python3
"""
Format Google Cloud credentials for proper usage
"""

import os
import json
import tempfile

def format_credentials():
    """Format credentials from environment variable"""
    
    # Get the raw credentials
    creds_raw = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
    
    if not creds_raw:
        print("❌ No GOOGLE_APPLICATION_CREDENTIALS found")
        return None
    
    try:
        # Parse as JSON to validate
        creds_dict = json.loads(creds_raw)
        
        # Validate required fields
        required_fields = ['type', 'project_id', 'private_key', 'client_email']
        missing_fields = [field for field in required_fields if field not in creds_dict]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return None
        
        # Create temporary file with proper formatting
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds_dict, f, indent=2)
            temp_path = f.name
        
        print(f"✅ Credentials formatted successfully")
        print(f"Project ID: {creds_dict.get('project_id')}")
        print(f"Service Account: {creds_dict.get('client_email')}")
        print(f"Temp file: {temp_path}")
        
        return temp_path
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in credentials: {e}")
        return None
    
    except Exception as e:
        print(f"❌ Error formatting credentials: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Formatting Google Cloud Credentials")
    print("=" * 50)
    
    temp_file = format_credentials()
    
    if temp_file:
        print(f"\n📝 Use this file path: {temp_file}")
        
        # Test reading the file
        try:
            with open(temp_file, 'r') as f:
                test_data = json.load(f)
            print("✅ Credentials file is readable")
        except Exception as e:
            print(f"❌ Error reading temp file: {e}")
    
    print("\n" + "=" * 50)