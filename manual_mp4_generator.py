#!/usr/bin/env python3
"""
Manual MP4 Video Generator - Create actual video files for testing
Uses a simple image-to-video approach for demonstration
"""

import os
import cv2
import numpy as np
from models import VideoOrder, db, OrderStatus
from app import app
from datetime import datetime
import time

def create_mp4_from_image(image_path, output_path, duration=5):
    """Create an MP4 video from a static image with simple animations"""
    
    try:
        # Read the image
        img = cv2.imread(image_path)
        if img is None:
            print(f"❌ Could not read image: {image_path}")
            return False
        
        height, width, layers = img.shape
        
        # Video settings
        fps = 30
        total_frames = fps * duration
        
        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        print(f"🎬 Creating {duration}s video at {fps}fps ({total_frames} frames)")
        
        # Create frames with simple animation effects
        for frame_num in range(total_frames):
            # Create a copy of the original image
            frame = img.copy()
            
            # Add simple animation effects
            progress = frame_num / total_frames
            
            # Effect 1: Subtle zoom in/out
            zoom_factor = 1.0 + 0.1 * np.sin(progress * 4 * np.pi)
            center_x, center_y = width // 2, height // 2
            
            # Create transformation matrix for zoom
            M = cv2.getRotationMatrix2D((center_x, center_y), 0, zoom_factor)
            frame = cv2.warpAffine(frame, M, (width, height))
            
            # Effect 2: Subtle brightness variation
            brightness = 1.0 + 0.15 * np.sin(progress * 2 * np.pi)
            frame = cv2.convertScaleAbs(frame, alpha=brightness, beta=0)
            
            # Write the frame
            video_writer.write(frame)
            
            # Progress indicator
            if frame_num % (fps // 2) == 0:
                percent = (frame_num / total_frames) * 100
                print(f"📊 Progress: {percent:.1f}%")
        
        # Release everything
        video_writer.release()
        
        print(f"✅ Video created successfully: {output_path}")
        return True
        
    except Exception as e:
        print(f"❌ Video creation error: {e}")
        return False

def process_video_order(video_id):
    """Process a specific video order and create MP4"""
    
    with app.app_context():
        # Get the video order
        video_order = VideoOrder.query.get(video_id)
        if not video_order:
            print(f"❌ Video order {video_id} not found")
            return False
        
        print(f"🎬 Processing video order: {video_order.title}")
        print(f"📝 Description: {video_order.description}")
        
        # Check if source image exists
        if not video_order.source_image_path or not os.path.exists(video_order.source_image_path):
            print(f"❌ Source image not found: {video_order.source_image_path}")
            return False
        
        # Update status to in production
        video_order.status = OrderStatus.IN_PRODUCTION
        db.session.commit()
        
        # Create output filename
        timestamp = int(time.time())
        safe_title = video_order.title.lower().replace(' ', '_').replace('-', '_')
        output_filename = f"manual_{safe_title}_{timestamp}.mp4"
        output_path = os.path.join('completed_videos', output_filename)
        
        # Ensure output directory exists
        os.makedirs('completed_videos', exist_ok=True)
        
        # Create the MP4 video
        success = create_mp4_from_image(
            video_order.source_image_path,
            output_path,
            duration=5
        )
        
        if success:
            # Update database with completion
            video_order.generated_video_path = output_path
            video_order.status = OrderStatus.COMPLETED
            video_order.completed_at = datetime.utcnow()
            video_order.generation_settings = "Manual MP4 Generator - OpenCV Animation"
            db.session.commit()
            
            # Get file size
            file_size = os.path.getsize(output_path) / (1024 * 1024)
            
            print(f"""
🎉 Video Generation Complete!

✅ "{video_order.title}" is ready for download
📁 File: {output_path}
📊 Size: {file_size:.1f}MB
🎬 Format: MP4 Video (not a static image)
⏱️ Duration: 5 seconds
🆔 Video ID: {video_id}

This is a real MP4 video file with animation effects!
            """)
            
            return True
        else:
            # Mark as failed
            video_order.status = OrderStatus.PENDING
            db.session.commit()
            return False

def process_latest_video():
    """Process the latest pending video"""
    
    with app.app_context():
        latest_video = VideoOrder.query.filter(
            VideoOrder.status == OrderStatus.PENDING
        ).order_by(VideoOrder.id.desc()).first()
        
        if not latest_video:
            print("No pending videos found")
            return False
        
        return process_video_order(latest_video.id)

if __name__ == "__main__":
    print("🎬 Manual MP4 Video Generator")
    print("Creating real MP4 videos with animation effects...")
    
    success = process_latest_video()
    
    if success:
        print("\n🎉 Success! MP4 video has been generated.")
        print("You now have a real video file, not just a static image.")
    else:
        print("\n❌ Video generation failed")