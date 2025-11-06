#!/usr/bin/env python3
"""
Ultra-Fast VEO 3 Generation - Optimized for 2-3 minute completion
"""

import os
import requests
import json
import time
from datetime import datetime
from models import VideoOrder, db
from app import app

def generate_ultra_fast_video():
    """Generate new video with ultra-fast VEO 3 parameters"""
    
    with app.app_context():
        # Get the image from Video 7
        video_7 = VideoOrder.query.get(7)
        if not video_7:
            print("Video 7 not found")
            return
            
        print(f"🚀 Starting ultra-fast generation for: {video_7.title}")
        print(f"📝 Prompt: {video_7.description}")
        
        # Create new video order with optimized settings
        new_video = VideoOrder(
            user_id=video_7.user_id,  # Use same user as original
            title="Beautiful woman (Ultra-Fast)",
            description=video_7.description,
            platform=video_7.platform,
            source_image_path=video_7.source_image_path,
            status='IN_PRODUCTION',
            generation_settings="Ultra-fast VEO 3 - 2min target",
            created_at=datetime.utcnow()
        )
        
        db.session.add(new_video)
        db.session.commit()
        
        print(f"📊 Created new order: ID {new_video.id}")
        
        # Initialize ultra-fast VEO 3
        from authentic_veo3_vertex import AuthenticVEO3
        veo3 = AuthenticVEO3()
        
        # Ultra-fast generation parameters
        ultra_fast_params = {
            "prompt": video_7.description,
            "image_path": video_7.source_image_path,
            "optimization": "speed",
            "resolution": "720p",  # Faster than 1080p
            "motion_intensity": 6,  # Moderate motion for speed
            "duration": 5,  # Shorter duration
            "quality_preset": "fast"
        }
        
        print(f"⚡ Generating with ultra-fast parameters...")
        
        try:
            # Start generation
            operation_id = veo3.generate_video_ultra_fast(**ultra_fast_params)
            
            if operation_id:
                new_video.veo3_operation_id = operation_id
                db.session.commit()
                
                print(f"✅ Ultra-fast generation started!")
                print(f"🔄 Operation: {operation_id}")
                print(f"⏱️ Target completion: 2-3 minutes")
                
                # Send start notification
                send_start_notification(new_video)
                
                return new_video.id
            else:
                print(f"❌ Generation failed to start")
                new_video.status = 'FAILED'
                db.session.commit()
                return None
                
        except Exception as e:
            print(f"Generation error: {e}")
            new_video.status = 'FAILED'
            new_video.error_message = str(e)
            db.session.commit()
            return None

def send_start_notification(video):
    """Send SMS notification that generation started"""
    try:
        from send_message import send_twilio_message
        
        message = f"🚀 DreamFrame Ultra-Fast Generation Started!\n\n'{video.title}' is now generating with optimized VEO 3 parameters.\n\n- Target time: 2-3 minutes\n- Quality: Professional VEO 3\n- Optimization: Speed focused\n\nYou'll receive another notification when ready!"
        
        phone_number = "+1234567890"  # Update with real number
        send_twilio_message(phone_number, message)
        print(f"📱 Start notification sent!")
        
    except Exception as e:
        print(f"SMS notification failed: {e}")

if __name__ == "__main__":
    video_id = generate_ultra_fast_video()
    if video_id:
        print(f"🎬 Ultra-fast generation in progress: Video ID {video_id}")
    else:
        print(f"❌ Failed to start ultra-fast generation")