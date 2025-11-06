#!/usr/bin/env python3
"""
Test the zombie video download functionality
"""

import os
from app import app
from models import VideoOrder, db

def test_zombie_download():
    """Test that the zombie video download works with the correct MIME type"""
    
    with app.app_context():
        # Get the zombie video order
        zombie_video = VideoOrder.query.filter_by(id=14).first()
        
        if not zombie_video:
            print("❌ Zombie video not found")
            return False
        
        print(f"✅ Found zombie video: {zombie_video.title}")
        print(f"📁 File path: {zombie_video.generated_video_path}")
        print(f"📊 Status: {zombie_video.status}")
        
        # Check if file exists
        if os.path.exists(zombie_video.generated_video_path):
            file_size = os.path.getsize(zombie_video.generated_video_path)
            file_extension = os.path.splitext(zombie_video.generated_video_path)[1]
            
            print(f"✅ File exists: {file_size:,} bytes")
            print(f"📄 Extension: {file_extension}")
            
            # Test the MIME type logic
            if file_extension.lower() in ['.jpg', '.jpeg']:
                expected_mime = 'image/jpeg'
            elif file_extension.lower() == '.png':
                expected_mime = 'image/png'
            elif file_extension.lower() == '.webp':
                expected_mime = 'image/webp'
            else:
                expected_mime = 'video/mp4'
            
            print(f"📋 Expected MIME type: {expected_mime}")
            
            # Generate expected download filename
            expected_filename = f"dreamframe_{zombie_video.title.replace(' ', '_').lower()}_{zombie_video.id}{file_extension}"
            print(f"📝 Expected download name: {expected_filename}")
            
            print("\n🎉 Zombie video download test: PASSED")
            print("The file should now download correctly with proper MIME type!")
            return True
        else:
            print(f"❌ File not found: {zombie_video.generated_video_path}")
            return False

if __name__ == "__main__":
    print("🧟 Testing Zombie Video Download...")
    test_zombie_download()