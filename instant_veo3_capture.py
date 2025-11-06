#!/usr/bin/env python3
"""
Instant VEO 3 Capture System - Uses webhooks and continuous polling
to capture VEO 3 results immediately upon completion
"""

import asyncio
import time
import requests
import threading
import json
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3
from ultra_fast_veo3 import UltraFastVEO3
from models import VideoOrder, db
from app import app

class InstantVEO3Capture:
    def __init__(self):
        self.generator = AuthenticVEO3()
        self.active_operations = {}
        
    def start_instant_generation(self, video_id, image_path, prompt):
        """Start VEO 3 generation with instant capture system"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            print(f"🚀 Starting INSTANT VEO 3 capture for: {video.title}")
            
            # Enhanced prompt for maximum quality
            enhanced_prompt = f"{prompt}. Professional cinematic quality, realistic physics, natural lighting, synchronized audio track, smooth motion, high definition."
            
            # Start VEO 3 generation
            ultra_generator = UltraFastVEO3()
            result = ultra_generator.generate_ultra_fast_video(image_path, enhanced_prompt)
            
            if result and result.get('operation_name'):
                operation_id = result['operation_name']
                video.veo3_operation_id = operation_id
                video.status = 'IN_PRODUCTION'
                video.prompt_used = enhanced_prompt[:100]
                db.session.commit()
                
                print(f"VEO 3 operation started: {operation_id}")
                
                # Start INSTANT monitoring with multiple parallel threads
                self.start_instant_monitoring(video_id, operation_id)
                return True
            
            return False
    
    def start_instant_monitoring(self, video_id, operation_id):
        """Start multiple parallel monitoring threads for instant capture"""
        print(f"🎯 Starting INSTANT monitoring with parallel threads")
        
        # Start 3 parallel monitoring threads with different intervals
        for thread_id in range(3):
            interval = 2 + thread_id  # 2s, 3s, 4s intervals
            thread = threading.Thread(
                target=self._monitor_thread,
                args=(video_id, operation_id, thread_id, interval)
            )
            thread.daemon = True
            thread.start()
    
    def _monitor_thread(self, video_id, operation_id, thread_id, interval):
        """Individual monitoring thread with specific interval"""
        print(f"Thread {thread_id}: Starting monitoring (interval: {interval}s)")
        
        max_attempts = 300 // interval  # 5 minutes total
        
        for attempt in range(max_attempts):
            try:
                with app.app_context():
                    video = VideoOrder.query.get(video_id)
                    if not video or video.status == 'COMPLETED':
                        print(f"Thread {thread_id}: Video completed or not found, stopping")
                        return
                    
                    # Check operation status
                    status = self.generator.check_operation_status(operation_id)
                    
                    if status and status.get('done'):
                        print(f"🎉 Thread {thread_id}: VEO 3 COMPLETED! Attempting immediate capture...")
                        
                        success = self._attempt_immediate_download(video_id, status, thread_id)
                        if success:
                            print(f"✅ Thread {thread_id}: Successfully captured VEO 3 video!")
                            return
                        else:
                            print(f"❌ Thread {thread_id}: Download failed, but continuing...")
                    
                    elif status is None:
                        if attempt % 10 == 0:  # Log every 10 attempts
                            print(f"Thread {thread_id}: Operation not found (attempt {attempt + 1})")
                    else:
                        if attempt % 20 == 0:  # Log every 20 attempts
                            print(f"Thread {thread_id}: Still processing (attempt {attempt + 1})")
                    
                    time.sleep(interval)
                    
            except Exception as e:
                print(f"Thread {thread_id} error (attempt {attempt + 1}): {e}")
                time.sleep(interval)
        
        print(f"Thread {thread_id}: Monitoring timeout after {max_attempts} attempts")
    
    def _attempt_immediate_download(self, video_id, status, thread_id):
        """Attempt immediate download with multiple strategies"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            response = status.get('response', {})
            
            # Try multiple URI extraction strategies
            video_uri = None
            uri_strategies = [
                # Direct keys
                lambda r: r.get('generatedVideoUri'),
                lambda r: r.get('videoUri'),
                lambda r: r.get('uri'),
                lambda r: r.get('outputVideoUri'),
                lambda r: r.get('videoUrl'),
                lambda r: r.get('downloadUrl'),
                
                # Nested keys
                lambda r: r.get('generatedVideo', {}).get('uri'),
                lambda r: r.get('generatedVideo', {}).get('videoUri'),
                lambda r: r.get('output', {}).get('videoUri'),
                lambda r: r.get('result', {}).get('videoUri'),
                lambda r: r.get('media', {}).get('uri'),
            ]
            
            for strategy in uri_strategies:
                try:
                    uri = strategy(response)
                    if uri:
                        video_uri = uri
                        print(f"Thread {thread_id}: Found video URI: {uri}")
                        break
                except:
                    continue
            
            if not video_uri:
                print(f"Thread {thread_id}: No video URI found")
                print(f"Thread {thread_id}: Available response keys: {list(response.keys())}")
                return False
            
            # Attempt immediate download with multiple retry strategies
            for retry in range(5):
                try:
                    print(f"Thread {thread_id}: Download attempt {retry + 1}")
                    
                    headers = {
                        'User-Agent': f'DreamFrame-InstantCapture-Thread{thread_id}/1.0',
                        'Accept': 'video/mp4,video/*,*/*',
                        'Accept-Encoding': 'identity',
                        'Connection': 'keep-alive',
                        'Cache-Control': 'no-cache'
                    }
                    
                    response = requests.get(
                        video_uri,
                        headers=headers,
                        timeout=60,
                        stream=True,
                        allow_redirects=True
                    )
                    
                    print(f"Thread {thread_id}: HTTP {response.status_code}")
                    
                    if response.status_code == 200:
                        timestamp = int(time.time())
                        filename = f"flag_veo3_authentic_thread{thread_id}_{timestamp}.mp4"
                        video_path = f"completed_videos/{filename}"
                        
                        total_bytes = 0
                        with open(video_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=32768):
                                if chunk:
                                    f.write(chunk)
                                    total_bytes += len(chunk)
                        
                        if total_bytes > 10000:  # At least 10KB
                            print(f"✅ Thread {thread_id}: Downloaded {total_bytes:,} bytes")
                            
                            # Update database
                            video.generated_video_path = video_path
                            video.status = 'COMPLETED'
                            video.completed_at = datetime.now()
                            db.session.commit()
                            
                            print(f"🎉 Thread {thread_id}: AUTHENTIC VEO 3 VIDEO CAPTURED!")
                            return True
                        else:
                            print(f"Thread {thread_id}: File too small ({total_bytes} bytes)")
                    
                except Exception as e:
                    print(f"Thread {thread_id}: Download error: {e}")
                
                time.sleep(1)  # Brief pause between retries
            
            return False

def main():
    """Start instant VEO 3 capture for flag video"""
    capture_system = InstantVEO3Capture()
    
    flag_prompt = """A beautiful flag waving gracefully in natural wind. The flag displays realistic fabric physics with natural ripples, waves, and flowing motion. Mounted on a flagpole, the flag flutters naturally with smooth, elegant movement. Professional cinematic quality with natural outdoor lighting, realistic wind effects, and ambient audio."""
    
    print("🚀 INSTANT VEO 3 CAPTURE SYSTEM STARTING...")
    print("This system uses parallel monitoring to capture authentic VEO 3 results")
    
    success = capture_system.start_instant_generation(
        video_id=5,
        image_path="uploads/2_1754017939_IMG_7008.jpeg",
        prompt=flag_prompt
    )
    
    if success:
        print("✅ Instant capture system activated with parallel monitoring")
        print("⚡ Multiple threads will capture the video immediately upon completion")
        
        # Keep monitoring active
        try:
            while True:
                time.sleep(30)
                
                # Check if completed
                with app.app_context():
                    video = VideoOrder.query.get(5)
                    if video and video.status == 'COMPLETED':
                        print("🎉 AUTHENTIC VEO 3 VIDEO SUCCESSFULLY CAPTURED!")
                        break
                
                print("Instant monitoring active - waiting for VEO 3 completion...")
        except KeyboardInterrupt:
            print("Monitoring stopped")
    else:
        print("❌ Failed to start instant capture system")

if __name__ == "__main__":
    main()