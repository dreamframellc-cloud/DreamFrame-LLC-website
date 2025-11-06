#!/usr/bin/env python3
"""
VEO 3 Capture Daemon - Runs continuously to capture VEO 3 videos immediately
"""

import time
import requests
import os
import threading
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3
from ultra_fast_veo3 import UltraFastVEO3
from models import VideoOrder, db
from app import app

class VEO3CaptureDaemon:
    def __init__(self):
        self.generator = AuthenticVEO3()
        self.running = True
        
    def start_new_flag_generation(self):
        """Start fresh VEO 3 generation for flag video"""
        with app.app_context():
            video = VideoOrder.query.get(5)
            if not video:
                return False
            
            print(f"Starting new VEO 3 generation for: {video.title}")
            
            # Create ultra-realistic flag prompt
            flag_prompt = """A majestic flag waving gracefully in a gentle breeze against a clear sky. The flag shows realistic fabric physics with natural ripples, waves, and flowing motion. The flag is mounted on a tall flagpole and flutters naturally in the wind with smooth, elegant movement. The fabric has realistic texture and natural lighting that highlights the waving motion beautifully. Professional cinematic quality with natural outdoor lighting, realistic wind effects, and synchronized ambient audio."""
            
            ultra_generator = UltraFastVEO3()
            result = ultra_generator.generate_ultra_fast_video(
                video.source_image_path, 
                flag_prompt
            )
            
            if result and result.get('operation_name'):
                operation_id = result['operation_name']
                video.veo3_operation_id = operation_id
                video.status = 'IN_PRODUCTION'
                video.prompt_used = flag_prompt[:100]
                db.session.commit()
                
                print(f"VEO 3 generation started: {operation_id}")
                
                # Start immediate monitoring
                self.monitor_operation(5, operation_id)
                return True
            
            return False
    
    def monitor_operation(self, video_id, operation_id):
        """Monitor VEO 3 operation with very aggressive polling"""
        def monitor_thread():
            print(f"Starting aggressive monitoring for operation: {operation_id}")
            
            # Check every 5 seconds for 15 minutes
            for attempt in range(180):  # 15 minutes * 12 checks per minute
                try:
                    with app.app_context():
                        video = VideoOrder.query.get(video_id)
                        if not video:
                            break
                        
                        status = self.generator.check_operation_status(operation_id)
                        
                        if status and status.get('done'):
                            print(f"VEO 3 COMPLETED! Attempting immediate download...")
                            
                            response = status.get('response', {})
                            
                            # Try all possible video URI keys
                            video_uri = None
                            uri_keys = [
                                'generatedVideoUri', 'videoUri', 'uri', 'outputVideoUri',
                                'videoUrl', 'downloadUrl', 'resultUri', 'mediaUri'
                            ]
                            
                            for key in uri_keys:
                                if key in response:
                                    video_uri = response[key]
                                    print(f"Found video URI with key '{key}': {video_uri}")
                                    break
                                elif 'generatedVideo' in response and key in response['generatedVideo']:
                                    video_uri = response['generatedVideo'][key]
                                    print(f"Found video URI in generatedVideo with key '{key}': {video_uri}")
                                    break
                            
                            if video_uri:
                                success = self.download_immediately(video_id, video_uri)
                                if success:
                                    print(f"SUCCESS! Retrieved authentic VEO 3 video for {video.title}")
                                    return
                                else:
                                    print(f"Download failed, but will keep trying...")
                            else:
                                print(f"No video URI found. Available keys: {list(response.keys())}")
                                # Print full response for debugging
                                import json
                                print("Full response:", json.dumps(response, indent=2))
                        
                        elif status is None:
                            print(f"Operation status not available (attempt {attempt + 1})")
                        else:
                            if attempt % 12 == 0:  # Print every minute
                                print(f"Still processing... (attempt {attempt + 1}/180)")
                        
                        time.sleep(5)  # Check every 5 seconds
                        
                except Exception as e:
                    print(f"Monitoring error (attempt {attempt + 1}): {e}")
                    time.sleep(5)
            
            print(f"Monitoring timeout for operation {operation_id}")
        
        # Start monitoring thread
        thread = threading.Thread(target=monitor_thread)
        thread.daemon = True
        thread.start()
    
    def download_immediately(self, video_id, video_uri):
        """Download video with multiple aggressive retry attempts"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            print(f"Attempting immediate download from: {video_uri}")
            
            # Try 5 times with different approaches
            for attempt in range(5):
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (compatible; DreamFrame-VEO3-Client/1.0)',
                        'Accept': 'video/mp4,video/*,*/*',
                        'Accept-Encoding': 'identity',
                        'Connection': 'keep-alive'
                    }
                    
                    print(f"Download attempt {attempt + 1}...")
                    
                    response = requests.get(
                        video_uri,
                        headers=headers,
                        timeout=180,  # 3 minute timeout
                        stream=True,
                        allow_redirects=True,
                        verify=True
                    )
                    
                    print(f"Response status: {response.status_code}")
                    print(f"Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                    print(f"Content-Length: {response.headers.get('Content-Length', 'unknown')}")
                    
                    if response.status_code == 200:
                        timestamp = int(time.time())
                        video_filename = f"flag_veo3_authentic_{timestamp}.mp4"
                        video_path = f"completed_videos/{video_filename}"
                        
                        total_bytes = 0
                        chunk_count = 0
                        
                        with open(video_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=16384):
                                if chunk:
                                    f.write(chunk)
                                    total_bytes += len(chunk)
                                    chunk_count += 1
                                    
                                    if chunk_count % 100 == 0:  # Progress update
                                        print(f"Downloaded {total_bytes:,} bytes...")
                        
                        if total_bytes > 1000:  # At least 1KB
                            print(f"SUCCESS! Downloaded {total_bytes:,} bytes ({total_bytes/1024/1024:.1f} MB)")
                            print(f"File saved: {video_path}")
                            
                            # Update database
                            video.generated_video_path = video_path
                            video.status = 'COMPLETED'
                            video.completed_at = datetime.now()
                            db.session.commit()
                            
                            print("Database updated - authentic VEO 3 video ready!")
                            return True
                        else:
                            print(f"File too small ({total_bytes} bytes), trying again...")
                            os.remove(video_path)
                    
                    else:
                        print(f"HTTP {response.status_code}: {response.text[:200]}")
                        
                except Exception as e:
                    print(f"Download attempt {attempt + 1} failed: {e}")
                
                time.sleep(2)  # Brief pause between attempts
            
            print("All download attempts failed")
            return False

def main():
    """Start VEO 3 capture daemon"""
    daemon = VEO3CaptureDaemon()
    
    print("🚀 VEO 3 Capture Daemon Starting...")
    print("This will generate and capture authentic VEO 3 content")
    
    success = daemon.start_new_flag_generation()
    
    if success:
        print("✅ VEO 3 generation started with aggressive monitoring")
        print("⏱️  System will capture the video immediately upon completion")
        
        # Keep script running to monitor
        try:
            while True:
                time.sleep(30)
                print("Monitoring active...")
        except KeyboardInterrupt:
            print("Monitoring stopped")
    else:
        print("❌ Failed to start VEO 3 generation")

if __name__ == "__main__":
    main()