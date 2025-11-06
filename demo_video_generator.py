"""
Demo Video Generation System
Creates video confirmations for customer orders while external APIs are being configured
"""

import os
import time
import shutil
from typing import Dict, Any

def create_demo_video(image_path: str, prompt: str, **kwargs) -> Dict[str, Any]:
    """Generate a demo video response for customer orders"""
    
    start_time = time.time()
    
    print(f"🎬 Demo Video Generation System")
    print(f"📸 Image: {image_path}")
    print(f"📝 Prompt: {prompt}")
    
    # Simulate processing time
    print("⚡ Processing video generation...")
    time.sleep(2)  # Brief processing simulation
    
    # Copy a demo video from the static gallery
    demo_videos = [
        'static/videos/VideoGram.mp4',
        'static/videos/Memories_h264.mp4',
        'static/videos/Puppy.mp4.MP4'
    ]
    
    # Select an available demo video
    demo_video_path = None
    for video_path in demo_videos:
        if os.path.exists(video_path):
            demo_video_path = video_path
            break
    
    if not demo_video_path:
        # Create a simple video file placeholder
        completed_dir = 'completed_videos'
        os.makedirs(completed_dir, exist_ok=True)
        
        demo_video_path = os.path.join(completed_dir, 'demo_generation.mp4')
        
        # Create a simple demo file
        with open(demo_video_path, 'w') as f:
            f.write("Demo video content - API integration in progress")
    
    completion_time = time.time() - start_time
    
    print(f"✅ Demo video completed in {completion_time:.1f} seconds!")
    
    return {
        'success': True,
        'video_url': demo_video_path,
        'completion_time': completion_time,
        'service': 'Demo Generation',
        'message': 'Video generation in progress - this is a demo response while we configure the AI services'
    }