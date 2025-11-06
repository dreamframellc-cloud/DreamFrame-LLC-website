#!/usr/bin/env python3
"""
Check status of the new Smile video
"""

from datetime import datetime
from models import VideoOrder, OrderStatus, User
from app import app

def check_smile_video_status():
    """Check the Smile video that just started"""
    
    with app.app_context():
        # Get the Smile video (most recent)
        smile_video = VideoOrder.query.filter_by(title="Smile").order_by(VideoOrder.created_at.desc()).first()
        
        if not smile_video:
            print("❌ Smile video not found")
            return
        
        print("🎬 SMILE VIDEO STATUS")
        print("=" * 30)
        print(f"📹 Title: {smile_video.title}")
        print(f"🆔 Order ID: {smile_video.id}")
        print(f"⚡ Status: {smile_video.status}")
        
        # Calculate elapsed time
        elapsed = (datetime.utcnow() - smile_video.created_at).total_seconds() / 60
        print(f"⏱️ Elapsed: {elapsed:.1f} minutes")
        
        # Check operation details
        if hasattr(smile_video, 'veo3_operation_id') and smile_video.veo3_operation_id:
            print(f"🔄 Operation ID: {smile_video.veo3_operation_id}")
            print("✅ VEO 3 generation confirmed")
        else:
            print("⏳ Operation ID pending...")
        
        # Check source image
        if smile_video.source_image_path:
            print(f"📸 Source image: {smile_video.source_image_path}")
        
        # Provide status update
        if elapsed < 1:
            print("🚀 NEW GENERATION: Just started!")
            print("💫 Using Vertex AI VEO 3")
            print("⏰ Expected completion: 3-6 minutes")
        elif elapsed < 6:
            print(f"🎬 Generation in progress ({elapsed:.1f} min)")
            print("✅ Within normal processing time")
        else:
            print(f"⚠️ Taking longer than expected ({elapsed:.1f} min)")
        
        # Show user info
        if smile_video.user_id:
            user = User.query.get(smile_video.user_id)
            if user:
                print(f"👤 Customer: {user.email}")
        
        print(f"\n📱 Monitor progress at: /my-videos")
        
        return smile_video

if __name__ == "__main__":
    check_smile_video_status()