#!/usr/bin/env python3
"""
Complete system health check and status
"""

import os
from models import VideoOrder, OrderStatus, User
from app import app, db

def comprehensive_health_check():
    """Check all system components"""
    
    with app.app_context():
        print("🔍 COMPREHENSIVE SYSTEM CHECK")
        print("=" * 45)
        
        # Database connectivity
        try:
            user_count = User.query.count()
            video_count = VideoOrder.query.count()
            print(f"✅ Database: Connected ({user_count} users, {video_count} videos)")
        except Exception as e:
            print(f"❌ Database: Error - {str(e)}")
        
        # User account status
        try:
            user = User.query.filter_by(email="jeremyprice50@gmail.com").first()
            if user:
                print(f"✅ Your account: Active (ID: {user.id})")
                
                # Your videos
                your_videos = VideoOrder.query.filter_by(user_id=user.id).all()
                print(f"📹 Your videos: {len(your_videos)} total")
                
                for video in your_videos[-3:]:  # Show last 3
                    elapsed = "Unknown"
                    if video.created_at and video.completed_at:
                        elapsed = f"{(video.completed_at - video.created_at).total_seconds() / 60:.1f} min"
                    print(f"   • {video.title}: {video.status.value} ({elapsed})")
                    
            else:
                print("❌ Your account: Not found")
        except Exception as e:
            print(f"❌ Account check: Error - {str(e)}")
        
        # File system
        video_dirs = ['completed_videos', 'uploads', 'static']
        for directory in video_dirs:
            if os.path.exists(directory):
                file_count = len([f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))])
                print(f"✅ {directory}/: {file_count} files")
            else:
                print(f"❌ {directory}/: Not found")
        
        # Available videos for download
        completed = VideoOrder.query.filter_by(status=OrderStatus.COMPLETED).all()
        print(f"\n📥 READY FOR DOWNLOAD:")
        if completed:
            for video in completed[-5:]:  # Show last 5 completed
                file_status = "✅ File ready" if video.generated_video_path and os.path.exists(video.generated_video_path) else "❌ File missing"
                print(f"   • {video.title}: {file_status}")
        else:
            print("   No completed videos yet")
        
        print(f"\n🌐 ACCESS POINTS:")
        print(f"   • Homepage: http://localhost:5000/")
        print(f"   • Your Videos: http://localhost:5000/my-videos")
        print(f"   • Create Video: http://localhost:5000/create-video")
        
        return True

if __name__ == "__main__":
    comprehensive_health_check()