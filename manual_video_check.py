#!/usr/bin/env python3
"""
Manual check of video generation status
"""

from models import VideoOrder, OrderStatus
from app import app, db

def check_love_video():
    """Check the Love video specifically"""
    
    with app.app_context():
        # Get the Love video (most recent)
        love_video = VideoOrder.query.filter_by(title="Love").order_by(VideoOrder.created_at.desc()).first()
        
        if not love_video:
            print("❌ Love video not found")
            return
        
        print("🎬 Love Video Status Check")
        print("=" * 40)
        print(f"📝 Title: {love_video.title}")
        print(f"🆔 ID: {love_video.id}")
        print(f"⚡ Status: {love_video.status}")
        
        # Calculate elapsed time
        from datetime import datetime
        elapsed = (datetime.utcnow() - love_video.created_at).total_seconds() / 60
        print(f"⏱️ Elapsed: {elapsed:.1f} minutes")
        
        # Check operation ID
        if hasattr(love_video, 'veo3_operation_id') and love_video.veo3_operation_id:
            print(f"🔄 Operation: {love_video.veo3_operation_id}")
        
        # Check for generated video
        if love_video.generated_video_path:
            print(f"🎉 Video Ready: {love_video.generated_video_path}")
        else:
            print("⏳ Video still generating...")
        
        # Check if we need to update status
        if elapsed > 5 and love_video.status not in ['COMPLETED', 'FAILED']:
            print(f"⚠️ Video taking longer than expected ({elapsed:.1f} min)")
            print("🔍 Checking if completion was missed...")
            
            # Check if video file exists
            import os
            if love_video.generated_video_path and os.path.exists(love_video.generated_video_path):
                print("✅ Video file found! Updating status...")
                love_video.status = OrderStatus.COMPLETED
                love_video.completed_at = datetime.utcnow()
                db.session.commit()
                print("✅ Status updated to COMPLETED")
            else:
                print("📂 Checking for video files in directories...")
                # Check common video directories
                video_dirs = ['completed_videos', 'uploads', '.']
                for directory in video_dirs:
                    if os.path.exists(directory):
                        files = [f for f in os.listdir(directory) if f.endswith('.mp4')]
                        if files:
                            print(f"📁 Found videos in {directory}: {files[-5:]}")  # Show last 5
        
        return love_video

if __name__ == "__main__":
    check_love_video()