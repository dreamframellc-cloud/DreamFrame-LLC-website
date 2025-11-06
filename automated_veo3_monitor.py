#!/usr/bin/env python3
"""
Automated VEO 3 Monitor - Continuously checks and retrieves completed videos
"""

import time
import requests
import os
import logging
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3
from models import VideoOrder, db
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AutomatedVEO3Monitor:
    def __init__(self):
        self.generator = AuthenticVEO3()
        logger.info("🎬 Automated VEO 3 Monitor started")
    
    def retrieve_video_if_ready(self, video_id):
        """Check if VEO 3 video is ready and download it"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            
            if not video or not video.veo3_operation_id:
                return False
            
            try:
                status = self.generator.check_operation_status(video.veo3_operation_id)
                
                if not status:
                    logger.info(f"⏳ {video.title}: Operation status not available yet")
                    return False
                
                if not status.get('done'):
                    logger.info(f"⏳ {video.title}: Still generating...")
                    return False
                
                # Operation completed!
                logger.info(f"✅ {video.title}: VEO 3 generation completed!")
                
                response = status.get('response', {})
                
                # Find video URI
                video_uri = None
                for key in ['generatedVideoUri', 'videoUri', 'uri']:
                    if key in response:
                        video_uri = response[key]
                        break
                    elif 'generatedVideo' in response and key in response['generatedVideo']:
                        video_uri = response['generatedVideo'][key]
                        break
                
                if not video_uri:
                    logger.error(f"❌ {video.title}: No video URI found in response")
                    logger.info(f"Response keys: {list(response.keys())}")
                    return False
                
                logger.info(f"🎯 {video.title}: Downloading from {video_uri}")
                
                # Download the actual VEO 3 video
                headers = {
                    'User-Agent': 'DreamFrame-VEO3-Client/1.0',
                    'Accept': 'video/mp4,video/*'
                }
                
                download_response = requests.get(video_uri, headers=headers, timeout=120, stream=True)
                
                if download_response.status_code != 200:
                    logger.error(f"❌ {video.title}: Download failed with status {download_response.status_code}")
                    return False
                
                # Save the real VEO 3 video
                video_filename = f"{video.title.lower().replace(' ', '_')}_veo3_real.mp4"
                video_path = f"completed_videos/{video_filename}"
                
                total_size = 0
                with open(video_path, 'wb') as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            total_size += len(chunk)
                
                logger.info(f"✅ {video.title}: Downloaded {total_size:,} bytes ({total_size/1024/1024:.1f} MB)")
                
                # Update database
                video.generated_video_path = video_path
                video.status = 'COMPLETED'
                video.completed_at = datetime.now()
                db.session.commit()
                
                logger.info(f"🎉 {video.title}: Successfully completed with real VEO 3 content!")
                return True
                
            except Exception as e:
                logger.error(f"❌ {video.title}: Error retrieving video - {e}")
                return False
    
    def monitor_video(self, video_id, max_wait_minutes=10):
        """Monitor a specific video until completion or timeout"""
        logger.info(f"🔍 Starting monitoring for video ID {video_id}")
        logger.info(f"⏰ Will check every 30 seconds for up to {max_wait_minutes} minutes")
        
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            if self.retrieve_video_if_ready(video_id):
                logger.info(f"🎉 Video {video_id} completed successfully!")
                return True
            
            logger.info(f"⏳ Waiting 30 seconds before next check...")
            time.sleep(30)
        
        logger.warning(f"⏰ Timeout reached for video {video_id} after {max_wait_minutes} minutes")
        return False

def main():
    """Monitor specific video or all pending videos"""
    import sys
    
    monitor = AutomatedVEO3Monitor()
    
    if len(sys.argv) > 1:
        video_id = int(sys.argv[1])
        max_wait = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        
        logger.info(f"🎯 Monitoring video {video_id} for up to {max_wait} minutes")
        success = monitor.monitor_video(video_id, max_wait)
        
        if success:
            print(f"✅ Video {video_id} completed successfully!")
        else:
            print(f"❌ Video {video_id} not completed within timeout")
    else:
        # Monitor all pending videos once
        with app.app_context():
            pending_videos = VideoOrder.query.filter(
                VideoOrder.status.in_(['IN_PRODUCTION', 'PENDING']),
                VideoOrder.veo3_operation_id.isnot(None)
            ).all()
            
            logger.info(f"🔍 Found {len(pending_videos)} pending videos")
            
            for video in pending_videos:
                logger.info(f"Checking video: {video.title} (ID: {video.id})")
                monitor.retrieve_video_if_ready(video.id)

if __name__ == "__main__":
    main()