#!/usr/bin/env python3
"""
Quick Dragon Video Generator - Optimized for fast completion
Creates dragon fire castle video with reduced processing time
"""

import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont

def create_quick_dragon_video():
    """Create dragon video optimized for speed"""
    
    # Optimized settings for speed
    width, height = 1280, 720  # Reduced resolution for speed
    fps = 24  # Standard fps
    duration = 8  # 8 seconds
    total_frames = fps * duration
    
    # Output path
    output_path = "static/completed_videos/dragon_fire_castle_quick.mp4"
    os.makedirs("static/completed_videos", exist_ok=True)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Creating {total_frames} frames for dragon video...")
    
    for frame_num in range(total_frames):
        # Create frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Time-based animation
        t = frame_num / total_frames
        
        # Animated background (castle)
        castle_color = (30 + int(20 * np.sin(t * 4)), 25, 15)  # Dark brown castle
        cv2.rectangle(frame, (0, height//2), (width//3, height), castle_color, -1)
        
        # Dragon body (moving across screen)
        dragon_x = int(width * 0.2 + width * 0.6 * t)
        dragon_y = int(height * 0.3 + 50 * np.sin(t * 8))  # Flying motion
        
        # Dragon body
        dragon_color = (0, 100, 200)  # Orange-red dragon
        cv2.ellipse(frame, (dragon_x, dragon_y), (80, 40), 0, 0, 360, dragon_color, -1)
        
        # Dragon wings (animated)
        wing_offset = int(30 * np.sin(t * 12))  # Wing flapping
        cv2.ellipse(frame, (dragon_x - 40, dragon_y - wing_offset), (60, 30), 0, 0, 360, (150, 150, 0), -1)
        cv2.ellipse(frame, (dragon_x + 40, dragon_y - wing_offset), (60, 30), 0, 0, 360, (150, 150, 0), -1)
        
        # Fire breath (animated)
        fire_length = int(200 + 100 * np.sin(t * 6))
        for i in range(5):
            fire_x = dragon_x + 80 + i * 20
            fire_y = dragon_y + int(20 * np.random.rand() - 10)
            fire_size = max(1, 40 - i * 8)
            fire_color = (0, 50 + i * 40, 255 - i * 30)  # Red-orange fire
            if fire_x < width:
                cv2.circle(frame, (fire_x, fire_y), fire_size, fire_color, -1)
        
        # Sky effects (particles)
        for _ in range(20):
            px = int(width * np.random.rand())
            py = int(height * 0.3 * np.random.rand())
            cv2.circle(frame, (px, py), 2, (100, 100, 100), -1)
        
        # Write frame
        video_writer.write(frame)
        
        if frame_num % 48 == 0:  # Progress every 2 seconds
            print(f"Progress: {frame_num}/{total_frames} frames ({frame_num/total_frames*100:.1f}%)")
    
    # Release video writer
    video_writer.release()
    
    # Check file size
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"SUCCESS: Dragon video created!")
        print(f"Path: {output_path}")
        print(f"Size: {size_mb:.1f} MB")
        return output_path
    else:
        print("FAILED: Video not created")
        return None

if __name__ == "__main__":
    create_quick_dragon_video()