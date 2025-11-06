"""
Check Video Status and Bucket Configuration
Investigate why videos aren't appearing in Google Cloud bucket
"""

import os
import sys
sys.path.append('.')

from authentic_veo3_vertex import AuthenticVEO3
from datetime import datetime
import time

def check_recent_operation_status():
    """Check the most recent video operation"""
    
    print("🔍 Checking Recent Video Operation Status")
    print("=" * 45)
    
    # Most recent operation ID
    recent_operation = "projects/dreamframe/locations/us-central1/publishers/google/models/veo-3.0-generate-preview/operations/0f478947-c3e8-4630-b958-c8777561bbd3"
    
    try:
        client = AuthenticVEO3()
        
        print(f"📋 Operation ID: 0f478947-c3e8-4630-b958-c8777561bbd3")
        print("🔍 Checking generation status...")
        
        status = client.check_operation_status(recent_operation)
        
        if status:
            print(f"📊 Current Status: {status}")
            
            # Check for completion indicators
            status_str = str(status).lower()
            if 'done' in status_str or 'complete' in status_str:
                print("✅ Video generation completed!")
                return "completed"
            elif 'processing' in status_str or 'running' in status_str:
                print("⏳ Video still processing...")
                return "processing"
            elif 'error' in status_str or 'failed' in status_str:
                print("❌ Video generation failed")
                return "failed"
            else:
                print(f"📊 Status details: {status}")
                return status
        else:
            print("❌ Could not retrieve status")
            return False
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False

def check_bucket_configuration():
    """Check Google Cloud bucket configuration"""
    
    print("\n🪣 Google Cloud Bucket Configuration")
    print("-" * 35)
    
    # Check environment variables
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
    credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    if project_id:
        print(f"✅ Project ID configured: {project_id}")
    else:
        print("❌ GOOGLE_CLOUD_PROJECT_ID not found")
    
    if credentials_path:
        print(f"✅ Credentials configured: {credentials_path}")
    else:
        print("❌ GOOGLE_APPLICATION_CREDENTIALS not found")
    
    print("\n💡 Bucket Investigation:")
    print("   - Videos should appear in your configured bucket")
    print("   - Check Google Cloud Console > Storage")
    print("   - Look for bucket named similar to 'dreamframe' or project ID")
    print("   - Videos may be in subdirectories")

def investigate_veo3_storage_format():
    """Investigate VEO 3 storage format and location"""
    
    print("\n📁 VEO 3 Storage Investigation")
    print("-" * 30)
    
    print("🔍 VEO 3 Video Storage Analysis:")
    print("   1. Videos generated with storageUri parameter")
    print("   2. Should appear in Google Cloud Storage bucket")
    print("   3. May have specific naming convention")
    print("   4. Could be in subdirectories based on operation ID")
    print()
    print("🧐 Possible Issues:")
    print("   - Bucket permissions not configured")
    print("   - StorageUri parameter incorrect")
    print("   - Videos stored in different project/bucket")
    print("   - Generation still in progress")

def main():
    """Check video status and bucket configuration"""
    
    status = check_recent_operation_status()
    check_bucket_configuration()
    investigate_veo3_storage_format()
    
    print("\n" + "=" * 45)
    print("📊 DIAGNOSIS SUMMARY")
    
    if status == "completed":
        print("🎉 VIDEO GENERATION COMPLETED!")
        print("🔍 Issue: Video completed but not visible in bucket")
        print("📋 Next steps:")
        print("   - Check all buckets in Google Cloud Console")
        print("   - Verify bucket permissions")
        print("   - Check if storageUri is correctly configured")
        
    elif status == "processing":
        print("⏳ VIDEO STILL PROCESSING")
        print("⏰ Wait 2-3 more minutes for completion")
        print("🔍 Video should appear in bucket once finished")
        
    elif status == "failed":
        print("❌ VIDEO GENERATION FAILED")
        print("🔧 Need to investigate generation parameters")
        print("📋 May need to adjust VEO 3 request format")
        
    else:
        print("❓ STATUS UNCLEAR")
        print("🔍 Need deeper investigation of VEO 3 operation")
    
    print("\n💡 RECOMMENDATIONS:")
    print("   1. Check Google Cloud Console > Storage for all buckets")
    print("   2. Verify VEO 3 operation completed successfully")
    print("   3. Check if storageUri parameter is correct")
    print("   4. Generate test video with explicit bucket configuration")

if __name__ == "__main__":
    main()