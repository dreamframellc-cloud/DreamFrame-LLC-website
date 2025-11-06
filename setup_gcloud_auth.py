#!/usr/bin/env python3
"""
Setup Google Cloud CLI authentication properly
"""

import os
import json
import subprocess
import tempfile

def setup_gcloud_auth():
    """Setup gcloud authentication with service account"""
    
    print("🔧 Setting up Google Cloud CLI authentication...")
    
    try:
        # Get credentials from environment
        creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
        
        if not creds_json or not creds_json.startswith('{'):
            print("❌ No valid service account credentials found")
            return False
        
        # Parse and validate JSON
        creds_data = json.loads(creds_json)
        
        # Create temporary service account file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds_data, f, indent=2)
            temp_file = f.name
        
        print(f"📄 Created temporary service account file")
        
        # Activate service account
        result = subprocess.run([
            'gcloud', 'auth', 'activate-service-account', 
            '--key-file', temp_file
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Service account activated successfully")
            
            # Set project
            subprocess.run([
                'gcloud', 'config', 'set', 'project', 'dreamframe'
            ], capture_output=True)
            
            # Verify authentication
            auth_result = subprocess.run([
                'gcloud', 'auth', 'list'
            ], capture_output=True, text=True)
            
            print("🔑 Authenticated accounts:")
            print(auth_result.stdout)
            
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
            
            return True
        else:
            print(f"❌ Service account activation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def test_veo3_access():
    """Test VEO 3 access with authenticated gcloud"""
    
    print("\n🧪 Testing VEO 3 access...")
    
    try:
        # Test with gcloud aiplatform models list
        result = subprocess.run([
            'gcloud', 'ai', 'models', 'list', 
            '--region=us-central1',
            '--filter=displayName:veo'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ VEO 3 model access successful")
            print("Available VEO models:")
            print(result.stdout)
            return True
        else:
            print(f"⚠️ VEO 3 access check: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ VEO 3 test failed: {e}")
        return False

if __name__ == "__main__":
    print("Google Cloud CLI Authentication Setup")
    print("=" * 40)
    
    # Setup authentication
    if setup_gcloud_auth():
        print("\n✅ Google CLI authentication complete")
        
        # Test VEO 3 access
        test_veo3_access()
    else:
        print("\n❌ Authentication setup failed")