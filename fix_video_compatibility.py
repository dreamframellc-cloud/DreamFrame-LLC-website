#!/usr/bin/env python3
"""
Fix Video Compatibility - Ensure MP4 videos work across all browsers and devices
"""

import os
import subprocess
import time
from models import VideoOrder, db, OrderStatus
from app import app

def fix_video_compatibility(input_path, output_path):
    """Convert video to web-compatible format using FFmpeg"""
    
    try:
        # FFmpeg command for web-compatible MP4
        cmd = [
            'ffmpeg', '-y',  # -y to overwrite output file
            '-i', input_path,
            '-c:v', 'libx264',  # H.264 video codec
            '-preset', 'medium',  # Encoding speed/quality balance
            '-crf', '23',  # Constant rate factor (quality)
            '-pix_fmt', 'yuv420p',  # Pixel format for compatibility
            '-movflags', '+faststart',  # Web streaming optimization
            '-profile:v', 'baseline',  # H.264 baseline profile
            '-level', '3.0',  # H.264 level
            '-maxrate', '2M',  # Maximum bitrate
            '-bufsize', '4M',  # Buffer size
            output_path
        ]
        
        print(f"🔄 Converting video for web compatibility...")
        print(f"📁 Input: {input_path}")
        print(f"📁 Output: {output_path}")
        
        # Run FFmpeg conversion
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Video converted successfully")
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Conversion error: {e}")
        return False

def create_compatible_video():
    """Create a new web-compatible MP4 video"""
    
    with app.app_context():
        # Get the latest video
        video_order = VideoOrder.query.get(16)
        if not video_order:
            print("❌ Video order not found")
            return False
        
        original_path = video_order.generated_video_path
        if not os.path.exists(original_path):
            print(f"❌ Original video not found: {original_path}")
            return False
        
        # Create compatible version
        timestamp = int(time.time())
        compatible_filename = f"compatible_real_mp4_test_{timestamp}.mp4"
        compatible_path = os.path.join('completed_videos', compatible_filename)
        
        success = fix_video_compatibility(original_path, compatible_path)
        
        if success:
            # Update database with compatible version
            video_order.generated_video_path = compatible_path
            video_order.generation_settings = "Web-Compatible MP4 - H.264/AAC encoding"
            db.session.commit()
            
            # Get file size
            file_size = os.path.getsize(compatible_path) / (1024 * 1024)
            
            print(f"""
🎉 Compatible Video Ready!

✅ Web-compatible MP4 created
📁 File: {compatible_path}
📊 Size: {file_size:.1f}MB
🎬 Format: H.264/AAC MP4 (universal compatibility)
🌐 Browser Support: Chrome, Firefox, Safari, Edge
📱 Device Support: Desktop, mobile, tablet
🆔 Video ID: 16

This video should play perfectly in all browsers and devices!
            """)
            
            return True
        else:
            print("❌ Failed to create compatible version")
            return False

if __name__ == "__main__":
    print("🔧 Video Compatibility Fixer")
    success = create_compatible_video()
    
    if success:
        print("\n🎉 Success! Your video is now web-compatible.")
    else:
        print("\n❌ Compatibility fix failed")