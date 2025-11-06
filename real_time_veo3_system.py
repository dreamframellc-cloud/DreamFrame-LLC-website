#!/usr/bin/env python3
"""
Real-Time VEO 3 System - Handles immediate video retrieval upon completion
Addresses the Google VEO 3 API issue where operations complete but results expire quickly
"""

import asyncio
import time
import requests
import logging
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3
from models import VideoOrder, db
from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealTimeVEO3System:
    def __init__(self):
        self.generator = AuthenticVEO3()
        self.monitoring = {}
        
    def start_generation_with_monitoring(self, video_id, image_path, prompt):
        """Start VEO 3 generation and immediately begin monitoring"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            logger.info(f"Starting VEO 3 generation for: {video.title}")
            
            # Enhanced prompt for better results
            enhanced_prompt = f"{prompt}. High quality cinematic video with realistic physics, natural movement, and professional lighting. Generate with synchronized audio."
            
            # Start generation
            from ultra_fast_veo3 import UltraFastVEO3
            generator = UltraFastVEO3()
            result = generator.generate_ultra_fast_video(image_path, enhanced_prompt)
            
            if result and result.get('operation_name'):
                operation_id = result['operation_name']
                video.veo3_operation_id = operation_id
                video.status = 'IN_PRODUCTION'
                video.prompt_used = enhanced_prompt[:100]
                db.session.commit()
                
                logger.info(f"VEO 3 generation started: {operation_id}")
                
                # Start immediate monitoring in background
                self.start_monitoring(video_id, operation_id)
                return True
            
            return False
    
    def start_monitoring(self, video_id, operation_id):
        """Start monitoring a VEO 3 operation with aggressive polling"""
        logger.info(f"Starting aggressive monitoring for video {video_id}")
        
        def monitor_loop():
            max_attempts = 60  # 10 minutes with 10-second intervals
            attempt = 0
            
            while attempt < max_attempts:
                try:
                    with app.app_context():
                        video = VideoOrder.query.get(video_id)
                        if not video:
                            break
                        
                        status = self.generator.check_operation_status(operation_id)
                        
                        if status and status.get('done'):
                            logger.info(f"VEO 3 completed for video {video_id}!")
                            
                            response = status.get('response', {})
                            video_uri = None
                            
                            # Try multiple URI patterns
                            for key in ['generatedVideoUri', 'videoUri', 'uri', 'outputVideoUri']:
                                if key in response:
                                    video_uri = response[key]
                                    break
                                elif 'generatedVideo' in response and key in response['generatedVideo']:
                                    video_uri = response['generatedVideo'][key]
                                    break
                            
                            if video_uri:
                                success = self.download_video_immediately(video_id, video_uri)
                                if success:
                                    logger.info(f"Successfully retrieved VEO 3 video for {video.title}")
                                    return
                                else:
                                    logger.error(f"Download failed for {video.title}")
                            else:
                                logger.error(f"No video URI found for {video.title}")
                                logger.info(f"Available keys: {list(response.keys())}")
                        
                        elif status is None:
                            # Operation not found - may be completed and archived
                            logger.warning(f"Operation not found - checking if archived: {video.title}")
                            # Try alternative retrieval methods here if needed
                        
                        attempt += 1
                        time.sleep(10)  # Check every 10 seconds
                        
                except Exception as e:
                    logger.error(f"Monitoring error for video {video_id}: {e}")
                    attempt += 1
                    time.sleep(10)
            
            logger.warning(f"Monitoring timeout for video {video_id}")
        
        # Start monitoring in background thread
        import threading
        monitor_thread = threading.Thread(target=monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def download_video_immediately(self, video_id, video_uri):
        """Download video immediately with multiple retry attempts"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            logger.info(f"Downloading VEO 3 video from: {video_uri}")
            
            # Multiple download attempts with different configurations
            for attempt in range(3):
                try:
                    headers = {
                        'User-Agent': 'DreamFrame-VEO3-Client/1.0',
                        'Accept': 'video/mp4,video/*,*/*',
                        'Accept-Encoding': 'identity'
                    }
                    
                    response = requests.get(
                        video_uri, 
                        headers=headers, 
                        timeout=120, 
                        stream=True,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        # Save with unique filename
                        timestamp = int(time.time())
                        video_filename = f"{video.title.lower().replace(' ', '_')}_veo3_{timestamp}.mp4"
                        video_path = f"completed_videos/{video_filename}"
                        
                        total_bytes = 0
                        with open(video_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                                    total_bytes += len(chunk)
                        
                        logger.info(f"Downloaded {total_bytes:,} bytes to {video_path}")
                        
                        # Update database immediately
                        video.generated_video_path = video_path
                        video.status = 'COMPLETED'
                        video.completed_at = datetime.now()
                        db.session.commit()
                        
                        return True
                    else:
                        logger.warning(f"Download attempt {attempt + 1} failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    logger.warning(f"Download attempt {attempt + 1} error: {e}")
                
                time.sleep(2)  # Brief pause between attempts
            
            return False

def regenerate_flag_video():
    """Regenerate the Flag video with real-time monitoring"""
    system = RealTimeVEO3System()
    
    # Enhanced flag prompt
    flag_prompt = """A beautiful flag waving gracefully in a gentle breeze. The flag should show realistic fabric physics with natural ripples, waves, and flowing motion. The flag appears mounted on a flagpole and flutters naturally in the wind with smooth, elegant movement. The fabric should have realistic texture and lighting that highlights the waving motion. Cinematic quality with natural outdoor lighting and realistic wind effects."""
    
    success = system.start_generation_with_monitoring(
        video_id=5,
        image_path="uploads/2_1754017939_IMG_7008.jpeg",
        prompt=flag_prompt
    )
    
    if success:
        print("✅ VEO 3 generation started with real-time monitoring")
        print("⏱️ System will automatically capture the video upon completion")
        return True
    else:
        print("❌ Failed to start VEO 3 generation")
        return False

if __name__ == "__main__":
    regenerate_flag_video()