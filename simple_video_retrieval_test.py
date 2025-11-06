"""
Simple Video Retrieval Test
Focused approaches to solve VEO 3 video access
"""

import os
import sys
sys.path.append('.')

import json
import time
import requests
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3

def test_immediate_capture():
    """Test immediate response capture approach"""
    
    print("🎬 Testing Immediate Video Capture")
    print("=" * 40)
    
    client = AuthenticVEO3()
    access_token = client.get_access_token()
    
    if not access_token:
        print("❌ Failed to get access token")
        return None
    
    # Test with a simple prompt
    test_prompt = "A peaceful forest stream with sunlight filtering through trees"
    
    endpoint_url = "https://us-central1-aiplatform.googleapis.com/v1/projects/dreamframe/locations/us-central1/publishers/google/models/veo-3.0-generate-preview:predictLongRunning"
    
    payload = {
        "instances": [{"prompt": test_prompt, "video_length": 8}],
        "parameters": {"video_length": 8, "aspect_ratio": "16:9"}
    }
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    print(f"📝 Prompt: {test_prompt}")
    print("📡 Starting generation...")
    
    # Send generation request
    response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Generation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return None
    
    operation_data = response.json()
    operation_name = operation_data.get('name')
    operation_id = operation_name.split('/')[-1] if operation_name else 'unknown'
    
    print(f"✅ Operation started: {operation_id}")
    
    # Immediate ultra-fast monitoring
    status_url = f"https://us-central1-aiplatform.googleapis.com/v1/{operation_name}"
    
    print("⚡ Starting rapid monitoring...")
    
    # Check every 200ms for first 10 seconds
    for check in range(50):  # 50 checks * 200ms = 10 seconds
        try:
            response = requests.get(status_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                status_data = response.json()
                
                print(f"🔍 Check #{check + 1}: Processing...")
                
                # Check if operation is done
                if status_data.get('done'):
                    print(f"🎉 OPERATION COMPLETED at check #{check + 1}!")
                    print(f"⏱️  Total time: {(check + 1) * 0.2:.1f} seconds")
                    
                    # Print full response for analysis
                    print("📋 Complete response:")
                    print(json.dumps(status_data, indent=2))
                    
                    # Check for video data in response
                    response_content = status_data.get('response', {})
                    if response_content:
                        print("🎥 Response content found!")
                        print(json.dumps(response_content, indent=2))
                        
                        # Look for video URLs or data
                        video_info = extract_video_info(response_content)
                        if video_info:
                            print(f"🔗 Video info extracted: {video_info}")
                            return {
                                'success': True,
                                'operation_id': operation_id,
                                'video_info': video_info,
                                'completion_time': (check + 1) * 0.2
                            }
                    
                    return {
                        'success': True,
                        'operation_id': operation_id,
                        'status': 'completed_no_video_data',
                        'completion_time': (check + 1) * 0.2,
                        'response_data': status_data
                    }
                
                # Check for errors
                if 'error' in status_data:
                    print(f"❌ Operation failed: {status_data['error']}")
                    return {
                        'success': False,
                        'error': status_data['error']
                    }
            
            elif response.status_code == 404:
                if check > 5:  # If we've seen it before, it was archived
                    print(f"📦 Operation archived at check #{check + 1} - SUCCESS!")
                    print(f"⏱️  Archive time: {(check + 1) * 0.2:.1f} seconds")
                    
                    return {
                        'success': True,
                        'operation_id': operation_id,
                        'status': 'completed_and_archived',
                        'archive_time': (check + 1) * 0.2
                    }
                else:
                    print(f"❌ Operation not found at check #{check + 1}")
            
            else:
                print(f"⚠️  Status {response.status_code} at check #{check + 1}")
            
            time.sleep(0.2)  # 200ms intervals
            
        except Exception as e:
            print(f"❌ Check #{check + 1} error: {e}")
            time.sleep(0.2)
    
    print("⏰ Monitoring timeout")
    return {'success': False, 'reason': 'timeout'}

def extract_video_info(response_data):
    """Extract video information from response data"""
    
    # Check common video data locations
    video_fields = ['videoUri', 'uri', 'url', 'downloadUrl', 'signedUrl', 'video_url']
    data_fields = ['videoData', 'data', 'video_data', 'content']
    
    def search_dict(data, fields):
        if isinstance(data, dict):
            for field in fields:
                if field in data and data[field]:
                    return data[field]
            
            # Recursively search nested dictionaries
            for value in data.values():
                result = search_dict(value, fields)
                if result:
                    return result
        
        elif isinstance(data, list):
            for item in data:
                result = search_dict(item, fields)
                if result:
                    return result
        
        return None
    
    # Look for video URLs
    video_url = search_dict(response_data, video_fields)
    if video_url:
        return {'type': 'url', 'value': video_url}
    
    # Look for video data
    video_data = search_dict(response_data, data_fields)
    if video_data:
        return {'type': 'data', 'value': f"{len(str(video_data))} characters"}
    
    return None

def test_bucket_approach():
    """Test Google Cloud Storage bucket approach"""
    
    print("\n🎬 Testing Bucket Storage Approach")
    print("=" * 42)
    
    try:
        from google.cloud import storage
        
        # Initialize storage client
        storage_client = storage.Client(project="dreamframe")
        
        # Check if bucket exists
        bucket_name = "dreamframe-veo3-videos"
        
        try:
            bucket = storage_client.bucket(bucket_name)
            exists = bucket.exists()
            
            if exists:
                print(f"✅ Bucket exists: {bucket_name}")
                
                # List current files
                blobs = list(bucket.list_blobs())
                print(f"📊 Current files in bucket: {len(blobs)}")
                
                for blob in blobs[-5:]:  # Show last 5 files
                    print(f"   📄 {blob.name} ({blob.size} bytes)")
                
                return {
                    'success': True,
                    'bucket_exists': True,
                    'file_count': len(blobs)
                }
            else:
                print(f"❌ Bucket does not exist: {bucket_name}")
                print("💡 Creating bucket...")
                
                try:
                    bucket = storage_client.create_bucket(bucket_name, location="us-central1")
                    print(f"✅ Bucket created: {bucket_name}")
                    
                    return {
                        'success': True,
                        'bucket_created': True
                    }
                    
                except Exception as create_error:
                    print(f"❌ Bucket creation failed: {create_error}")
                    return {'success': False, 'error': str(create_error)}
        
        except Exception as bucket_error:
            print(f"❌ Bucket access error: {bucket_error}")
            return {'success': False, 'error': str(bucket_error)}
    
    except ImportError:
        print("❌ Google Cloud Storage library not available")
        return {'success': False, 'error': 'library_missing'}
    
    except Exception as e:
        print(f"❌ Bucket test error: {e}")
        return {'success': False, 'error': str(e)}

def main():
    """Run video retrieval tests"""
    
    print("🚀 Video Retrieval Solutions Test")
    print("=" * 45)
    print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test 1: Immediate capture
    result1 = test_immediate_capture()
    
    # Test 2: Bucket approach
    result2 = test_bucket_approach()
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 VIDEO RETRIEVAL TEST SUMMARY")
    
    if result1 and result1.get('success'):
        print("✅ Immediate Capture: SUCCESS")
        print(f"   📋 Status: {result1.get('status', 'completed')}")
        
        if result1.get('video_info'):
            video_info = result1['video_info']
            print(f"   🎥 Video {video_info['type']}: {video_info['value']}")
        
        if 'completion_time' in result1:
            print(f"   ⏱️  Completion time: {result1['completion_time']:.1f}s")
        elif 'archive_time' in result1:
            print(f"   ⏱️  Archive time: {result1['archive_time']:.1f}s")
    else:
        print("❌ Immediate Capture: Failed")
    
    if result2 and result2.get('success'):
        print("✅ Bucket Storage: Available")
        
        if result2.get('bucket_created'):
            print("   📦 New bucket created successfully")
        elif result2.get('file_count'):
            print(f"   📊 Found {result2['file_count']} existing files")
    else:
        print("❌ Bucket Storage: Not available")
    
    print("\n💡 RECOMMENDATIONS:")
    
    if result1 and result1.get('success'):
        if result1.get('video_info'):
            print("   🎉 Video data found in operation response!")
            print("   ✅ This is the solution - extract video from operation completion")
        elif result1.get('status') == 'completed_and_archived':
            print("   📦 Operations complete and archive immediately")
            print("   💡 Need to capture video data in the brief completion window")
        else:
            print("   ⚡ Operations complete but video data location unknown")
            print("   🔍 Need to investigate response structure further")
    
    if result2 and result2.get('success'):
        print("   📂 Google Cloud Storage is configured")
        print("   💡 Can implement bucket-based video delivery")
    
    print("\n🎯 NEXT STEPS:")
    print("   1. Refine millisecond-level capture timing")
    print("   2. Configure VEO 3 to output videos to bucket")
    print("   3. Set up webhook notifications for completion")
    print("   4. Test alternative Google AI Studio endpoints")

if __name__ == "__main__":
    main()