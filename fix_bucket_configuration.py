"""
Fix VEO 3 Bucket Configuration
Create proper bucket and update VEO 3 storage settings
"""

import subprocess
import os
import sys
sys.path.append('.')

def list_existing_buckets():
    """List all accessible Google Cloud Storage buckets"""
    
    print("🪣 Checking Existing Buckets")
    print("=" * 30)
    
    try:
        result = subprocess.run(['gsutil', 'ls'], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            buckets = result.stdout.strip().split('\n')
            if buckets and buckets[0]:
                print("✅ Found existing buckets:")
                for bucket in buckets:
                    if bucket.strip():
                        print(f"   {bucket}")
                return buckets
            else:
                print("⚠️  No buckets found")
                return []
        else:
            print(f"❌ Error listing buckets: {result.stderr}")
            return []
    except Exception as e:
        print(f"❌ Failed to list buckets: {e}")
        return []

def create_dreamframe_bucket():
    """Create the dreamframe-videos bucket"""
    
    print("\n🆕 Creating DreamFrame Video Bucket")
    print("-" * 35)
    
    bucket_name = "gs://dreamframe-videos-generated"
    
    try:
        print(f"🔨 Creating bucket: {bucket_name}")
        result = subprocess.run([
            'gsutil', 'mb', '-l', 'us-central1', bucket_name
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Bucket created successfully!")
            return bucket_name
        else:
            if "already exists" in result.stderr:
                print("✅ Bucket already exists")
                return bucket_name
            else:
                print(f"❌ Failed to create bucket: {result.stderr}")
                return None
    except Exception as e:
        print(f"❌ Bucket creation error: {e}")
        return None

def test_bucket_access(bucket_uri):
    """Test read/write access to bucket"""
    
    print(f"\n🧪 Testing Bucket Access: {bucket_uri}")
    print("-" * 40)
    
    try:
        # Test write access with a small test file
        test_content = "VEO3 bucket test"
        test_file = "/tmp/veo3_test.txt"
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        # Upload test file
        result = subprocess.run([
            'gsutil', 'cp', test_file, f"{bucket_uri}/test_file.txt"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Write access confirmed")
            
            # Test read access
            read_result = subprocess.run([
                'gsutil', 'cat', f"{bucket_uri}/test_file.txt"
            ], capture_output=True, text=True, timeout=30)
            
            if read_result.returncode == 0 and test_content in read_result.stdout:
                print("✅ Read access confirmed")
                
                # Clean up test file
                subprocess.run(['gsutil', 'rm', f"{bucket_uri}/test_file.txt"], 
                             capture_output=True, timeout=30)
                
                return True
            else:
                print("❌ Read access failed")
                return False
        else:
            print(f"❌ Write access failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Bucket access test error: {e}")
        return False

def main():
    """Fix bucket configuration for VEO 3"""
    
    print("🔧 Fixing VEO 3 Bucket Configuration")
    print("=" * 40)
    
    # Check existing buckets
    existing_buckets = list_existing_buckets()
    
    # Look for dreamframe bucket
    dreamframe_bucket = None
    for bucket in existing_buckets:
        if 'dreamframe' in bucket.lower():
            dreamframe_bucket = bucket.strip()
            break
    
    if dreamframe_bucket:
        print(f"\n✅ Found DreamFrame bucket: {dreamframe_bucket}")
        bucket_uri = dreamframe_bucket
    else:
        # Create new bucket
        bucket_uri = create_dreamframe_bucket()
        if not bucket_uri:
            print("❌ Failed to create bucket")
            return False
    
    # Test bucket access
    if test_bucket_access(bucket_uri):
        print(f"\n🎉 BUCKET CONFIGURATION SUCCESSFUL!")
        print(f"✅ Bucket ready: {bucket_uri}")
        print("✅ Read/write access confirmed")
        print()
        print("🔧 NEXT STEPS:")
        print(f"   Update VEO 3 storageUri to: {bucket_uri}")
        print("   Generate new test video with correct bucket")
        print("   Videos will appear in this bucket")
        
        return bucket_uri
    else:
        print("❌ Bucket access test failed")
        return False

if __name__ == "__main__":
    result = main()
    if result:
        print(f"\n💾 Use this bucket URI in VEO 3: {result}")
    else:
        print("\n⚠️  Manual bucket configuration may be needed")