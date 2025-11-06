"""
Enhanced VEO 3 Manager with Real-time Video Capture
Monitors operations and captures video data immediately upon completion
"""

import os
import sys
sys.path.append('.')

from authentic_veo3_vertex import AuthenticVEO3
from datetime import datetime
import time
import json
import requests
import base64
from urllib.parse import urlparse

class EnhancedVEO3Manager:
    def __init__(self):
        self.client = AuthenticVEO3()
        self.active_operations = {}
        
    def generate_and_monitor_video(self, prompt: str, duration: int = 8, video_name: str = None):
        """Generate video and monitor until completion with immediate capture"""
        
        print(f"🎬 Enhanced VEO 3 Generation: {prompt[:50]}...")
        print("=" * 50)
        
        if not video_name:
            video_name = f"video_{int(time.time())}"
        
        try:
            # Start generation
            print("🚀 Starting VEO 3 generation...")
            result = self.client.generate_customer_video(prompt, duration)
            
            if not result or not result.get('operation_name'):
                print("❌ Failed to start generation")
                return None
            
            operation_name = result['operation_name']
            operation_id = operation_name.split('/')[-1]
            
            print(f"✅ Generation started!")
            print(f"📋 Operation ID: {operation_id}")
            print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
            
            # Store operation info
            self.active_operations[operation_id] = {
                'operation_name': operation_name,
                'prompt': prompt,
                'video_name': video_name,
                'start_time': datetime.now(),
                'status': 'processing'
            }
            
            # Monitor in real-time
            return self.monitor_operation_realtime(operation_name, video_name)
            
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return None
    
    def monitor_operation_realtime(self, operation_name: str, video_name: str, max_wait_minutes: int = 10):
        """Monitor operation with real-time status checks"""
        
        print(f"\n⏱️  Real-time Monitoring: {video_name}")
        print("-" * 40)
        
        operation_id = operation_name.split('/')[-1]
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        check_interval = 30  # Check every 30 seconds
        
        print(f"🔍 Checking every {check_interval} seconds")
        print(f"⏰ Maximum wait: {max_wait_minutes} minutes")
        print()
        
        while time.time() - start_time < max_wait_seconds:
            try:
                current_time = datetime.now().strftime('%H:%M:%S')
                elapsed = int(time.time() - start_time)
                
                print(f"🕐 {current_time} - Checking status (elapsed: {elapsed}s)")
                
                status = self.client.check_operation_status(operation_name)
                
                if status:
                    status_str = str(status).lower()
                    
                    if 'done' in status_str:
                        print("🎉 VIDEO GENERATION COMPLETED!")
                        
                        # Immediately capture video data
                        video_data = self.extract_video_data(status)
                        
                        if video_data:
                            # Save video data
                            saved_path = self.save_video_data(video_data, video_name)
                            
                            if saved_path:
                                print(f"✅ Video saved: {saved_path}")
                                return {
                                    'success': True,
                                    'video_path': saved_path,
                                    'operation_id': operation_id,
                                    'completion_time': datetime.now(),
                                    'video_data': video_data
                                }
                            else:
                                print("⚠️  Video completed but couldn't save data")
                                return {
                                    'success': False,
                                    'reason': 'save_failed',
                                    'video_data': video_data
                                }
                        else:
                            print("⚠️  Video completed but no video data found")
                            print("📊 Full status response:")
                            print(json.dumps(status, indent=2) if isinstance(status, dict) else str(status))
                            return {
                                'success': False,
                                'reason': 'no_video_data',
                                'status_response': status
                            }
                    
                    elif 'error' in status_str or 'failed' in status_str:
                        print("❌ Video generation failed")
                        print(f"📊 Error status: {status}")
                        return {
                            'success': False,
                            'reason': 'generation_failed',
                            'error_status': status
                        }
                    
                    else:
                        print("⏳ Still processing...")
                        
                else:
                    print("❌ Could not retrieve status")
                
                # Wait before next check
                if time.time() - start_time < max_wait_seconds - check_interval:
                    print(f"⏸️  Waiting {check_interval} seconds...")
                    time.sleep(check_interval)
                else:
                    break
                    
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                time.sleep(check_interval)
        
        print("⏰ Monitoring timeout reached")
        return {
            'success': False,
            'reason': 'timeout',
            'elapsed_minutes': max_wait_minutes
        }
    
    def extract_video_data(self, status_response):
        """Extract video data from operation status response"""
        
        print("🔍 Extracting video data...")
        
        if not isinstance(status_response, dict):
            return None
        
        # Check common video data locations
        video_sources = [
            status_response.get('response', {}).get('generatedVideos', []),
            status_response.get('response', {}).get('videos', []),
            status_response.get('generatedVideos', []),
            status_response.get('videos', [])
        ]
        
        for videos in video_sources:
            if videos and isinstance(videos, list) and len(videos) > 0:
                video = videos[0]
                
                # Check for video URL
                video_url = video.get('videoUri') or video.get('uri') or video.get('url')
                if video_url:
                    print(f"🔗 Found video URL: {video_url}")
                    return {
                        'type': 'url',
                        'url': video_url,
                        'source': 'operation_response'
                    }
                
                # Check for base64 data
                video_data = video.get('videoData') or video.get('data')
                if video_data:
                    print("📦 Found base64 video data")
                    return {
                        'type': 'base64',
                        'data': video_data,
                        'source': 'operation_response'
                    }
        
        # Check response directly for video URLs
        response = status_response.get('response', {})
        for key, value in response.items():
            if isinstance(value, str) and ('http' in value and ('video' in value or 'mp4' in value)):
                print(f"🔗 Found video URL in {key}: {value}")
                return {
                    'type': 'url',
                    'url': value,
                    'source': f'response.{key}'
                }
        
        return None
    
    def save_video_data(self, video_data, video_name):
        """Save video data to local file"""
        
        print(f"💾 Saving video: {video_name}")
        
        try:
            if video_data['type'] == 'url':
                # Download from URL
                return self.download_video_from_url(video_data['url'], video_name)
            
            elif video_data['type'] == 'base64':
                # Save base64 data
                return self.save_base64_video(video_data['data'], video_name)
            
            else:
                print(f"❌ Unknown video data type: {video_data['type']}")
                return None
                
        except Exception as e:
            print(f"❌ Save error: {e}")
            return None
    
    def download_video_from_url(self, video_url, video_name):
        """Download video from URL"""
        
        try:
            print(f"⬇️  Downloading from URL...")
            
            response = requests.get(video_url, timeout=60)
            response.raise_for_status()
            
            # Create output directory
            os.makedirs('completed_videos', exist_ok=True)
            
            # Save video file
            video_path = f"completed_videos/{video_name}.mp4"
            with open(video_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ Downloaded {file_size} bytes")
            
            return video_path
            
        except Exception as e:
            print(f"❌ Download error: {e}")
            return None
    
    def save_base64_video(self, base64_data, video_name):
        """Save base64 encoded video data"""
        
        try:
            print("📦 Decoding base64 data...")
            
            video_bytes = base64.b64decode(base64_data)
            
            # Create output directory
            os.makedirs('completed_videos', exist_ok=True)
            
            # Save video file
            video_path = f"completed_videos/{video_name}.mp4"
            with open(video_path, 'wb') as f:
                f.write(video_bytes)
            
            print(f"✅ Saved {len(video_bytes)} bytes")
            
            return video_path
            
        except Exception as e:
            print(f"❌ Base64 save error: {e}")
            return None

def test_enhanced_generation():
    """Test the enhanced VEO 3 manager"""
    
    print("🚀 Testing Enhanced VEO 3 Manager")
    print("=" * 40)
    
    manager = EnhancedVEO3Manager()
    
    # Test with a simple prompt
    test_prompt = "A peaceful mountain stream flowing over rocks, cinematic nature shot"
    video_name = "mountain_stream_test"
    
    print(f"🎬 Test video: {test_prompt}")
    print(f"📁 Video name: {video_name}")
    
    result = manager.generate_and_monitor_video(test_prompt, 8, video_name)
    
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS")
    
    if result and result.get('success'):
        print("🎉 SUCCESS! Video captured successfully!")
        print(f"✅ Video saved: {result['video_path']}")
        print(f"📋 Operation: {result['operation_id']}")
        print("✅ Real-time monitoring worked")
        
    else:
        print("⚠️  Test completed with issues")
        if result:
            print(f"📋 Reason: {result.get('reason', 'unknown')}")
        print("🔧 Enhanced monitoring system is ready for next generation")
    
    return result

if __name__ == "__main__":
    test_enhanced_generation()