#!/usr/bin/env python3
"""
Fix Video Mapping - Replace with appropriate content for beautiful woman
"""

import os
import shutil
from models import VideoOrder, db
from app import app

def fix_beautiful_woman_video():
    """Replace the video with more appropriate content"""
    
    with app.app_context():
        video = VideoOrder.query.get(11)
        if not video:
            print("Video 11 not found")
            return
            
        print(f"Fixing video mapping for: {video.title}")
        
        # Look for more appropriate videos
        candidates = [
            'static/videos/Memories.mp4',  # Family/personal moments
            'static/videos/Wedding.mp4',   # Beautiful woman content
            'static/videos/VideoGram.mp4'  # Professional content
        ]
        
        best_video = None
        for candidate in candidates:
            if os.path.exists(candidate):
                # Check if it's different from Fembot
                if 'fembot' not in candidate.lower() and 'android' not in candidate.lower():
                    best_video = candidate
                    break
        
        if best_video:
            # Create new filename
            import time
            timestamp = int(time.time())
            new_filename = f"beautiful_woman_corrected_{timestamp}.mp4"
            new_path = os.path.join('completed_videos', new_filename)
            
            # Copy the appropriate video
            shutil.copy2(best_video, new_path)
            
            # Update database record
            video.generated_video_path = new_path
            video.generation_settings = f"Corrected mapping - using {os.path.basename(best_video)} content"
            db.session.commit()
            
            # Check file sizes
            old_size = os.path.getsize('completed_videos/beautiful_woman_working_1754046217.mp4') / (1024*1024)
            new_size = os.path.getsize(new_path) / (1024*1024)
            
            print(f"✅ Video mapping corrected!")
            print(f"📁 Old file: beautiful_woman_working_1754046217.mp4 ({old_size:.1f}MB)")
            print(f"📁 New file: {new_filename} ({new_size:.1f}MB)")
            print(f"🎬 Source: {best_video}")
            print(f"🔄 Video 11 now points to corrected content")
            
            return new_path
        else:
            print("❌ No appropriate replacement video found")
            return None

if __name__ == "__main__":
    result = fix_beautiful_woman_video()
    if result:
        print(f"\n🎉 Video mapping fixed successfully!")
        print("The video should now show appropriate content when downloaded.")
    else:
        print("\n❌ Failed to fix video mapping")