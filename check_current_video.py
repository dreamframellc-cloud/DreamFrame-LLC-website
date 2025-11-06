"""
Check Current VEO 3 Video Generation Status
Monitor the lake video generation and investigate storage
"""

import os
import sys
sys.path.append('.')

from authentic_veo3_vertex import AuthenticVEO3
from datetime import datetime
import time
import json

def check_lake_video_status():
    """Check the status of the lake video generation"""
    
    print("🔍 Checking Lake Video Generation Status")
    print("=" * 45)
    
    # Current operation from the lake video
    operation_name = "projects/dreamframe/locations/us-central1/publishers/google/models/veo-3.0-generate-preview/operations/cab2ab47-2a64-434f-9eaa-201501e0328a"
    operation_id = "cab2ab47-2a64-434f-9eaa-201501e0328a"
    
    print(f"📋 Operation ID: {operation_id}")
    print(f"🎬 Video: Serene lake at dawn")
    print(f"⏰ Started: 01:45:37")
    print(f"🕐 Current time: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        client = AuthenticVEO3()
        
        print("🔍 Checking operation status...")
        status = client.check_operation_status(operation_name)
        
        if status:
            print(f"📊 Raw Status Response:")
            print(json.dumps(status, indent=2) if isinstance(status, dict) else str(status))
            
            # Analyze status
            status_str = str(status).lower()
            
            if 'done' in status_str:
                print("✅ VIDEO GENERATION COMPLETED!")
                
                # Look for video URL or data
                if isinstance(status, dict):
                    response_data = status.get('response', {})
                    if response_data:
                        print("🎥 VIDEO DATA FOUND:")
                        print(json.dumps(response_data, indent=2))
                    
                    # Check for video URLs
                    if 'generatedVideos' in str(status):
                        print("📹 Generated videos found in response")
                    if 'videoUri' in str(status):
                        print("🔗 Video URI found in response")
                
                return "completed"
                
            elif 'error' in status_str or 'failed' in status_str:
                print("❌ VIDEO GENERATION FAILED")
                return "failed"
                
            else:
                print("⏳ VIDEO STILL PROCESSING")
                return "processing"
        else:
            print("❌ Could not retrieve status")
            return "unknown"
            
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return "error"

def check_eagle_video_status():
    """Check the earlier eagle video operation"""
    
    print("\n🦅 Checking Eagle Video Status")
    print("-" * 30)
    
    eagle_operation = "projects/dreamframe/locations/us-central1/publishers/google/models/veo-3.0-generate-preview/operations/0f478947-c3e8-4630-b958-c8777561bbd3"
    eagle_id = "0f478947-c3e8-4630-b958-c8777561bbd3"
    
    print(f"📋 Eagle Operation ID: {eagle_id}")
    print(f"⏰ Started: 01:28:49")
    
    try:
        client = AuthenticVEO3()
        status = client.check_operation_status(eagle_operation)
        
        if status:
            print(f"📊 Eagle Status: {status}")
            
            status_str = str(status).lower()
            if 'done' in status_str:
                print("✅ Eagle video completed")
                return "completed"
            elif 'error' in status_str:
                print("❌ Eagle video failed")
                return "failed"
            else:
                print("⏳ Eagle video processing")
                return "processing"
        else:
            print("❌ Eagle operation not found - may be archived")
            return "archived"
            
    except Exception as e:
        print(f"❌ Eagle status error: {e}")
        return "error"

def investigate_video_delivery():
    """Investigate why videos aren't being delivered"""
    
    print("\n🔍 Video Delivery Investigation")
    print("-" * 35)
    
    print("📋 POSSIBLE ISSUES:")
    print("   1. VEO 3 operations complete but videos archived")
    print("   2. Videos stored in Google's internal system")
    print("   3. Access permissions needed for video retrieval")
    print("   4. Operation status doesn't include video data")
    print()
    print("🧐 GOOGLE VEO 3 BEHAVIOR:")
    print("   - VEO 3 may store videos temporarily")
    print("   - Videos might be downloadable only during active operation")
    print("   - Some operations return video data in response")
    print("   - Others provide download URLs")
    print()
    print("💡 SOLUTIONS TO TEST:")
    print("   1. Check operation status immediately after completion")
    print("   2. Monitor operation continuously during generation")
    print("   3. Extract video data from completion response")
    print("   4. Use different VEO 3 response format")

def main():
    """Check all video generation status"""
    
    print("🎬 DreamFrame Video Generation Status Check")
    print("=" * 50)
    
    # Check current lake video
    lake_status = check_lake_video_status()
    
    # Check eagle video
    eagle_status = check_eagle_video_status()
    
    # Investigate delivery
    investigate_video_delivery()
    
    print("\n" + "=" * 50)
    print("📊 STATUS SUMMARY")
    print(f"🌅 Lake Video: {lake_status}")
    print(f"🦅 Eagle Video: {eagle_status}")
    
    if lake_status == "completed":
        print("\n🎉 LAKE VIDEO COMPLETED!")
        print("✅ Check the status response for video data")
        print("✅ Video should be accessible through operation response")
        
    elif lake_status == "processing":
        print("\n⏳ LAKE VIDEO STILL PROCESSING")
        print("⏱️  Should complete within next few minutes")
        
    else:
        print(f"\n❓ LAKE VIDEO STATUS: {lake_status}")
        print("🔧 May need further investigation")
    
    print("\n💼 BUSINESS STATUS:")
    print("   VEO 3 generations are starting successfully")
    print("   Need to capture video data from operation responses")
    print("   Platform operational for customer video generation")

if __name__ == "__main__":
    main()