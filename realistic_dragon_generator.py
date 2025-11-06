#!/usr/bin/env python3
"""
Realistic Dragon Generator - Creates a proper dragon breathing fire video
"""

import cv2
import numpy as np
import os
from PIL import Image, ImageDraw, ImageFont
import math

def create_realistic_dragon_video():
    """Create a realistic dragon breathing fire over medieval castle"""
    
    # Video settings
    width, height = 1280, 720
    fps = 30
    duration = 10  # 10 seconds
    total_frames = fps * duration
    
    # Output path
    output_path = "static/completed_videos/realistic_dragon_castle.mp4"
    os.makedirs("static/completed_videos", exist_ok=True)
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    print(f"Creating realistic dragon video with {total_frames} frames...")
    
    for frame_num in range(total_frames):
        # Create dark medieval sky background
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Time progression
        t = frame_num / total_frames
        
        # Dark stormy sky with gradient
        for y in range(height//2):
            color_intensity = int(20 + 30 * (1 - y/(height//2)))
            frame[y, :] = [color_intensity//3, color_intensity//3, color_intensity]
        
        # Medieval castle silhouette (bottom portion)
        castle_height = height // 3
        castle_start_y = height - castle_height
        
        # Main castle wall
        cv2.rectangle(frame, (0, castle_start_y), (width//2, height), (25, 25, 35), -1)
        
        # Castle towers
        tower_width = 80
        for tower_x in [width//6, width//3]:
            cv2.rectangle(frame, (tower_x-tower_width//2, castle_start_y-60), 
                         (tower_x+tower_width//2, height), (30, 30, 40), -1)
            # Tower tops
            cv2.rectangle(frame, (tower_x-tower_width//2-10, castle_start_y-80), 
                         (tower_x+tower_width//2+10, castle_start_y-60), (35, 35, 45), -1)
        
        # Realistic dragon positioning (flies across screen)
        dragon_progress = (t * 1.5) % 1.0  # Complete journey in 2/3 of video, then loop
        dragon_x = int(width * 0.1 + width * 0.8 * dragon_progress)
        dragon_y = int(height * 0.25 + 40 * math.sin(t * 8))  # Undulating flight
        
        # Dragon wing span and body
        wing_span = 200
        body_length = 120
        
        # Wing flapping animation
        wing_beat = math.sin(t * 15)  # Fast wing beats
        wing_angle = int(30 * wing_beat)
        
        # Dragon body (serpentine, scaly appearance)
        dragon_color = (0, 80, 140)  # Dark red dragon
        neck_segments = 5
        
        # Draw dragon neck/body segments
        for i in range(neck_segments):
            segment_x = dragon_x - i * 15
            segment_y = dragon_y + int(10 * math.sin(t * 6 + i * 0.5))
            segment_size = max(20, 40 - i * 4)
            cv2.circle(frame, (segment_x, segment_y), segment_size, dragon_color, -1)
            # Scales/texture
            cv2.circle(frame, (segment_x, segment_y), segment_size-5, (0, 100, 160), 2)
        
        # Dragon head (larger, more detailed)
        head_size = 50
        cv2.ellipse(frame, (dragon_x + 40, dragon_y), (head_size, head_size-10), 0, 0, 360, dragon_color, -1)
        
        # Dragon eyes (glowing)
        eye_color = (0, 255, 255)
        cv2.circle(frame, (dragon_x + 50, dragon_y - 10), 8, eye_color, -1)
        cv2.circle(frame, (dragon_x + 55, dragon_y - 5), 6, eye_color, -1)
        
        # Dragon wings (bat-like, animated)
        wing_color = (20, 60, 120)
        
        # Left wing
        wing_pts = np.array([
            [dragon_x - 60, dragon_y + wing_angle],
            [dragon_x - 120, dragon_y + wing_angle - 40],
            [dragon_x - 140, dragon_y + wing_angle - 20],
            [dragon_x - 100, dragon_y + wing_angle + 20],
            [dragon_x - 40, dragon_y + wing_angle + 10]
        ], np.int32)
        cv2.fillPoly(frame, [wing_pts], wing_color)
        
        # Right wing
        wing_pts_r = np.array([
            [dragon_x + 40, dragon_y - wing_angle],
            [dragon_x + 100, dragon_y - wing_angle - 40],
            [dragon_x + 120, dragon_y - wing_angle - 20],
            [dragon_x + 80, dragon_y - wing_angle + 20],
            [dragon_x + 20, dragon_y - wing_angle + 10]
        ], np.int32)
        cv2.fillPoly(frame, [wing_pts_r], wing_color)
        
        # REALISTIC FIRE BREATHING
        if frame_num % 20 < 15:  # Fire bursts
            fire_start_x = dragon_x + 60
            fire_start_y = dragon_y + 10
            
            # Multiple fire particles with realistic behavior
            for fire_particle in range(25):
                # Fire spreads in cone shape
                angle_spread = (fire_particle / 25.0 - 0.5) * 60  # 60 degree spread
                distance = 100 + fire_particle * 8
                
                fire_x = fire_start_x + int(distance * math.cos(math.radians(angle_spread)))
                fire_y = fire_start_y + int(distance * math.sin(math.radians(angle_spread)) * 0.3)
                
                # Fire colors (hot core to cooler edges)
                if fire_particle < 8:
                    fire_color = (200, 255, 255)  # White hot core
                elif fire_particle < 15:
                    fire_color = (0, 165, 255)   # Orange middle
                else:
                    fire_color = (0, 100, 255)   # Red edges
                
                # Fire particle size varies
                particle_size = max(2, 25 - fire_particle)
                if fire_x < width and fire_y < height:
                    cv2.circle(frame, (fire_x, fire_y), particle_size, fire_color, -1)
                    
                    # Add glow effect
                    if particle_size > 10:
                        cv2.circle(frame, (fire_x, fire_y), particle_size + 5, fire_color, 2)
        
        # Smoke trails
        smoke_color = (40, 40, 40)
        for smoke_i in range(10):
            smoke_x = dragon_x + 180 + smoke_i * 15
            smoke_y = dragon_y - 20 + int(20 * math.sin(t * 3 + smoke_i))
            smoke_size = max(1, 15 - smoke_i)
            if smoke_x < width:
                cv2.circle(frame, (smoke_x, smoke_y), smoke_size, smoke_color, -1)
        
        # Lightning in background (occasionally)
        if frame_num % 90 == 0:
            lightning_x = np.random.randint(width//2, width)
            cv2.line(frame, (lightning_x, 0), (lightning_x + 20, height//3), (255, 255, 255), 3)
        
        # Write frame
        video_writer.write(frame)
        
        if frame_num % 60 == 0:  # Progress every 2 seconds
            print(f"Progress: {frame_num}/{total_frames} frames ({frame_num/total_frames*100:.1f}%)")
    
    # Release video writer
    video_writer.release()
    
    # Check file size
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        print(f"SUCCESS: Realistic dragon video created!")
        print(f"Path: {output_path}")
        print(f"Size: {size_mb:.1f} MB")
        return output_path
    else:
        print("FAILED: Video not created")
        return None

if __name__ == "__main__":
    create_realistic_dragon_video()