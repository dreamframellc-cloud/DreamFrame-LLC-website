"""
Create proper service account authentication and bucket setup
"""

import os
import json
import tempfile
import subprocess

def setup_authentication():
    """Set up Google Cloud authentication using service account"""
    
    print("🔐 Setting up Google Cloud Authentication")
    print("=" * 40)
    
    # Get credentials from environment
    creds_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not creds_json:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not found")
        return False
    
    try:
        # Parse credentials
        creds = json.loads(creds_json)
        
        # Create temporary key file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(creds, f, indent=2)
            key_file = f.name
        
        print(f"📝 Created temporary key file: {key_file}")
        
        # Authenticate with service account
        result = subprocess.run([
            'gcloud', 'auth', 'activate-service-account', 
            creds['client_email'],
            '--key-file', key_file
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Service account authenticated successfully")
            
            # Set project
            project_result = subprocess.run([
                'gcloud', 'config', 'set', 'project', creds['project_id']
            ], capture_output=True, text=True, timeout=30)
            
            if project_result.returncode == 0:
                print(f"✅ Project set to: {creds['project_id']}")
                
                # Clean up key file
                os.unlink(key_file)
                return True
            else:
                print(f"❌ Failed to set project: {project_result.stderr}")
                os.unlink(key_file)
                return False
        else:
            print(f"❌ Authentication failed: {result.stderr}")
            os.unlink(key_file)
            return False
            
    except Exception as e:
        print(f"❌ Authentication setup error: {e}")
        return False

def create_video_bucket():
    """Create bucket for VEO 3 videos"""
    
    print("\n🪣 Creating Video Storage Bucket")
    print("-" * 30)
    
    bucket_name = "dreamframe-generated-videos"
    
    try:
        # Create bucket
        result = subprocess.run([
            'gsutil', 'mb', '-l', 'us-central1', f'gs://{bucket_name}'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ Bucket created: gs://{bucket_name}")
            return f"gs://{bucket_name}/"
        elif "already exists" in result.stderr:
            print(f"✅ Bucket already exists: gs://{bucket_name}")
            return f"gs://{bucket_name}/"
        else:
            print(f"❌ Bucket creation failed: {result.stderr}")
            
            # Try alternative bucket name
            alt_bucket = f"dreamframe-videos-{os.urandom(4).hex()}"
            alt_result = subprocess.run([
                'gsutil', 'mb', '-l', 'us-central1', f'gs://{alt_bucket}'
            ], capture_output=True, text=True, timeout=30)
            
            if alt_result.returncode == 0:
                print(f"✅ Alternative bucket created: gs://{alt_bucket}")
                return f"gs://{alt_bucket}/"
            else:
                print(f"❌ Alternative bucket failed: {alt_result.stderr}")
                return None
                
    except Exception as e:
        print(f"❌ Bucket creation error: {e}")
        return None

def test_bucket_permissions(bucket_uri):
    """Test bucket read/write permissions"""
    
    print(f"\n🧪 Testing Bucket Permissions: {bucket_uri}")
    print("-" * 40)
    
    try:
        # Create test file
        test_content = f"VEO 3 test - {os.urandom(4).hex()}"
        test_file = "/tmp/veo3_bucket_test.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Upload test
        upload_result = subprocess.run([
            'gsutil', 'cp', test_file, f"{bucket_uri}test_upload.txt"
        ], capture_output=True, text=True, timeout=30)
        
        if upload_result.returncode == 0:
            print("✅ Upload successful")
            
            # Download test
            download_result = subprocess.run([
                'gsutil', 'cat', f"{bucket_uri}test_upload.txt"
            ], capture_output=True, text=True, timeout=30)
            
            if download_result.returncode == 0 and test_content in download_result.stdout:
                print("✅ Download successful")
                
                # Cleanup
                subprocess.run([
                    'gsutil', 'rm', f"{bucket_uri}test_upload.txt"
                ], capture_output=True, timeout=30)
                
                os.unlink(test_file)
                return True
            else:
                print("❌ Download failed")
                return False
        else:
            print(f"❌ Upload failed: {upload_result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Permission test error: {e}")
        return False

def main():
    """Set up complete bucket configuration"""
    
    print("🚀 Setting up VEO 3 Bucket Configuration")
    print("=" * 45)
    
    # Authenticate
    if not setup_authentication():
        print("❌ Authentication failed")
        return None
    
    # Create bucket
    bucket_uri = create_video_bucket()
    if not bucket_uri:
        print("❌ Bucket creation failed")
        return None
    
    # Test permissions
    if test_bucket_permissions(bucket_uri):
        print(f"\n🎉 BUCKET CONFIGURATION COMPLETE!")
        print(f"✅ Bucket ready: {bucket_uri}")
        print("✅ Permissions verified")
        print()
        print("🔧 UPDATE VEO 3 CONFIGURATION:")
        print(f"   Set storageUri to: {bucket_uri}")
        
        return bucket_uri
    else:
        print("❌ Permission test failed")
        return None

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n💾 VEO 3 storageUri: {result}")
    else:
        print("\n❌ Bucket setup failed")