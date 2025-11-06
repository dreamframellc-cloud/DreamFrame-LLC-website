#!/usr/bin/env python3
"""
Video Completion Notifier
Monitors video generation and sends SMS when complete
"""

import os
import time
import json
from datetime import datetime
from models import VideoOrder, db
from app import app
from send_message import send_twilio_message

def check_video_completion(order_id):
    """Check if video generation has completed and send notification"""
    
    with app.app_context():
        video = VideoOrder.query.get(order_id)
        
        if not video:
            print(f"Order {order_id} not found")
            return False
            
        print(f"Checking completion for: {video.title}")
        print(f"Status: {video.status}")
        print(f"Operation ID: {video.veo3_operation_id}")
        
        # Check if video is completed
        if video.status == 'completed' and video.generated_video_path:
            print(f"✅ Video {video.title} is COMPLETED!")
            
            # Send SMS notification
            try:
                message = f"🎬 DreamFrame Video Complete!\n\n'{video.title}' has finished generating.\n\nYour professional VEO 3 video is ready to view in your dashboard.\n\n- Duration: {video.duration or 'Processing'}\n- Quality: Professional VEO 3\n- Status: Ready for download"
                
                # Use your phone number for notification
                phone_number = "+1234567890"  # Replace with actual number
                send_twilio_message(phone_number, message)
                print(f"📱 SMS notification sent!")
                
            except Exception as e:
                print(f"SMS notification failed: {e}")
                
            return True
        else:
            print(f"⏳ Still generating... ({video.status})")
            return False

def monitor_video_7():
    """Monitor video order #7 specifically"""
    
    print("🔔 Video completion monitor started")
    print("📱 Will send SMS when generation completes")
    
    while True:
        try:
            if check_video_completion(7):
                print("🎉 Notification sent - monitoring complete!")
                break
                
            # Check every 30 seconds
            time.sleep(30)
            
        except KeyboardInterrupt:
            print("\n📱 Monitoring stopped")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    monitor_video_7()