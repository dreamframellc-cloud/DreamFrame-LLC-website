#!/usr/bin/env python3
"""
VEO 3 Video Retriever - Gets actual videos from Google servers
Monitors VEO 3 operations and downloads completed videos
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
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VEO3VideoRetriever:
    def __init__(self):
        self.generator = AuthenticVEO3()
        logger.info("🎬 VEO 3 Video Retriever initialized")
    
    def retrieve_completed_video(self, video_order_id):
        """
        Retrieve a completed VEO 3 video for a specific order
        """
        with app.app_context():
            video = VideoOrder.query.get(video_order_id)
            
            if not video or not video.veo3_operation_id:
                logger.error(f"❌ No video order or operation ID found for ID {video_order_id}")
                return False
            
            logger.info(f"🔍 Checking VEO 3 operation for video: {video.title}")
            logger.info(f"🆔 Operation ID: {video.veo3_operation_id}")
            
            try:
                # Check operation status
                status = self.generator.check_operation_status(video.veo3_operation_id)
                
                if not status:
                    logger.warning("⚠️ Could not get operation status")
                    return False
                
                if not status.get('done'):
                    logger.info("⏳ VEO 3 generation still in progress...")
                    return False
                
                # Operation completed - get video
                response = status.get('response', {})
                
                # Try different possible video URI keys
                video_uri = None
                uri_keys = ['generatedVideoUri', 'videoUri', 'uri']
                
                for key in uri_keys:
                    if key in response:
                        video_uri = response[key]
                        break
                    elif 'generatedVideo' in response and key in response['generatedVideo']:
                        video_uri = response['generatedVideo'][key]
                        break
                
                if not video_uri:
                    logger.error("❌ No video URI found in VEO 3 response")
                    logger.info(f"Available keys: {list(response.keys())}")
                    return False
                
                logger.info(f"🎯 Found video URI: {video_uri}")
                
                # Download the actual VEO 3 video
                logger.info("⬇️ Downloading actual VEO 3 video...")
                
                headers = {
                    'User-Agent': 'DreamFrame-VEO3-Client/1.0',
                    'Accept': 'video/mp4,video/*'
                }
                
                response = requests.get(video_uri, headers=headers, timeout=60, stream=True)
                
                if response.status_code != 200:
                    logger.error(f"❌ Failed to download video: HTTP {response.status_code}")
                    return False
                
                # Save the real VEO 3 video
                video_filename = f"{video.title.lower().replace(' ', '_')}_veo3_real.mp4"
                video_path = f"completed_videos/{video_filename}"
                
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                
                file_size = os.path.getsize(video_path)
                logger.info(f"✅ Successfully downloaded real VEO 3 video!")
                logger.info(f"📁 File: {video_path}")
                logger.info(f"📏 Size: {file_size:,} bytes ({file_size/1024/1024:.1f} MB)")
                
                # Update database with real video
                video.generated_video_path = video_path
                video.status = 'COMPLETED'
                video.completion_date = datetime.now()
                db.session.commit()
                
                logger.info(f"🎉 Video order {video_order_id} completed with real VEO 3 content!")
                return True
                
            except Exception as e:
                logger.error(f"❌ Error retrieving VEO 3 video: {e}")
                import traceback
                traceback.print_exc()
                return False
    
    def monitor_pending_videos(self):
        """
        Monitor all pending VEO 3 operations and retrieve completed videos
        """
        with app.app_context():
            pending_videos = VideoOrder.query.filter(
                VideoOrder.status.in_(['IN_PRODUCTION', 'PENDING']),
                VideoOrder.veo3_operation_id.isnot(None)
            ).all()
            
            logger.info(f"🔍 Found {len(pending_videos)} pending VEO 3 operations")
            
            for video in pending_videos:
                logger.info(f"⏳ Checking video: {video.title} (ID: {video.id})")
                success = self.retrieve_completed_video(video.id)
                
                if success:
                    logger.info(f"✅ Retrieved video: {video.title}")
                else:
                    logger.info(f"⏳ Still processing: {video.title}")
                
                # Small delay to avoid rate limiting
                time.sleep(1)

def main():
    """
    Run video retrieval for specific video or monitor all pending
    """
    import sys
    
    retriever = VEO3VideoRetriever()
    
    if len(sys.argv) > 1:
        # Retrieve specific video
        video_id = int(sys.argv[1])
        logger.info(f"🎯 Retrieving specific video ID: {video_id}")
        success = retriever.retrieve_completed_video(video_id)
        if success:
            print(f"✅ Successfully retrieved video {video_id}")
        else:
            print(f"❌ Failed to retrieve video {video_id}")
    else:
        # Monitor all pending videos
        logger.info("🔄 Monitoring all pending VEO 3 operations...")
        retriever.monitor_pending_videos()

if __name__ == "__main__":
    main()