#!/usr/bin/env python3
"""
Quick setup to help user create a new video
"""

from models import User
from app import app

def show_video_creation_options():
    """Show available video creation options"""
    
    with app.app_context():
        print("🎬 VIDEO CREATION READY")
        print("=" * 30)
        
        # Check user account
        user = User.query.filter_by(email="jeremyprice50@gmail.com").first()
        if user:
            print(f"✅ Account: {user.email}")
            print(f"📱 User ID: {user.id}")
        
        print("\n🌐 ACCESS OPTIONS:")
        print("1. Web Interface:")
        print("   • Visit: http://localhost:5000/create-video")
        print("   • Upload your image")
        print("   • Add description (like 'smile and wave')")
        print("   • Choose platform (Instagram, TikTok, etc.)")
        print("   • Click 'Generate Video'")
        
        print("\n2. Direct Login:")
        print("   • Go to: http://localhost:5000/login")
        print("   • Email: jeremyprice50@gmail.com")
        print("   • Use your password")
        print("   • Then navigate to 'Create Video'")
        
        print("\n📋 TIPS FOR SUCCESS:")
        print("   • Use clear, high-quality images")
        print("   • Keep descriptions simple (e.g., 'person waving')")
        print("   • Expected generation time: 3-6 minutes")
        print("   • System now working reliably")
        
        print("\n🎯 WHAT TO EXPECT:")
        print("   • Upload → Processing → Complete")
        print("   • Real-time status updates")
        print("   • HD video output (1280x720)")
        print("   • Download from 'My Videos' when ready")
        
        return True

if __name__ == "__main__":
    show_video_creation_options()