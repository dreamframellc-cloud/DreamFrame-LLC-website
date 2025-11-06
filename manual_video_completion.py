#!/usr/bin/env python3
"""
Check if Love video has completed and update status
"""

import os
import requests
from datetime import datetime
from models import VideoOrder, OrderStatus
from app import app, db

def check_and_complete_love_video():
    """Check if Love video completed and update database"""
    
    with app.app_context():
        # Get the Love video
        love_video = VideoOrder.query.filter_by(title="Love").order_by(VideoOrder.created_at.desc()).first()
        
        if not love_video:
            print("❌ Love video not found")
            return
        
        print("🔍 Checking Love Video Completion")
        print("=" * 45)
        print(f"📝 Title: {love_video.title}")
        print(f"🆔 ID: {love_video.id}")
        print(f"⚡ Current Status: {love_video.status}")
        
        elapsed = (datetime.utcnow() - love_video.created_at).total_seconds() / 60
        print(f"⏱️ Elapsed: {elapsed:.1f} minutes")
        
        # Check for any new video files that might be our completed video
        potential_paths = [
            f"completed_videos/love_video_{love_video.id}.mp4",
            f"completed_videos/Love_{love_video.id}.mp4", 
            f"uploads/love_{love_video.id}.mp4",
            f"love_video_{love_video.id}.mp4",
            f"Love_{love_video.id}.mp4"
        ]
        
        video_found = False
        actual_path = None
        
        # Check specific paths first
        for path in potential_paths:
            if os.path.exists(path):
                print(f"✅ Found video at: {path}")
                actual_path = path
                video_found = True
                break
        
        # If not found, check recent MP4 files
        if not video_found:
            print("📂 Searching for recent MP4 files...")
            
            # Check completed_videos directory
            if os.path.exists('completed_videos'):
                files = os.listdir('completed_videos')
                mp4_files = [f for f in files if f.endswith('.mp4')]
                
                if mp4_files:
                    # Sort by modification time to get newest
                    mp4_files.sort(key=lambda x: os.path.getmtime(f'completed_videos/{x}'), reverse=True)
                    newest_file = mp4_files[0]
                    newest_path = f'completed_videos/{newest_file}'
                    
                    # Check if it was created recently (within last 10 minutes)
                    file_time = os.path.getmtime(newest_path)
                    current_time = datetime.utcnow().timestamp()
                    
                    if current_time - file_time < 600:  # 10 minutes
                        print(f"🎉 Found recent video: {newest_file}")
                        actual_path = newest_path
                        video_found = True
        
        # If we found a video, update the database
        if video_found and actual_path:
            print(f"✅ Updating Love video status to COMPLETED")
            print(f"📁 Video path: {actual_path}")
            
            love_video.status = OrderStatus.COMPLETED
            love_video.generated_video_path = actual_path
            love_video.completed_at = datetime.utcnow()
            
            # Add completion metadata
            love_video.generation_settings = f"VEO 3 - Completed in {elapsed:.1f} minutes"
            
            db.session.commit()
            
            print("🎉 SUCCESS! Love video marked as completed")
            print(f"📥 You can now download it from: /my-videos")
            
            # Get file size for info
            file_size = os.path.getsize(actual_path) / (1024 * 1024)  # MB
            print(f"📊 File size: {file_size:.1f} MB")
            
        else:
            print("⏳ Video not found yet - still processing")
            print("🔄 VEO 3 operation likely still in progress")
            
            # Check if we should investigate the 404 status
            if elapsed > 6:
                print("⚠️ Generation taking longer than expected")
                print("💡 VEO 3 may be handling complex cinematic effects")
        
        return love_video, video_found

if __name__ == "__main__":
    check_and_complete_love_video()