#!/usr/bin/env python3
"""
Test bypassing social media optimization for speed
"""

import os
from datetime import datetime
from models import VideoOrder, OrderStatus, User
from app import app, db

def create_speed_test_video():
    """Create a video with minimal processing for speed testing"""
    
    with app.app_context():
        # Get user
        user = User.query.filter_by(email="jeremyprice50@gmail.com").first()
        if not user:
            print("❌ User not found")
            return
        
        print("⚡ SPEED TEST VIDEO - NO SOCIAL OPTIMIZATION")
        print("=" * 55)
        
        # Create simplified video order
        speed_test = VideoOrder()
        speed_test.user_id = user.id
        speed_test.title = "Speed Test"
        speed_test.description = "Simple video generation without social media optimization"
        speed_test.platform = "general"  # No platform-specific optimization
        speed_test.status = OrderStatus.PENDING
        speed_test.created_at = datetime.utcnow()
        
        # Use same source image as Smile video
        smile_video = VideoOrder.query.filter_by(title="Smile").order_by(VideoOrder.created_at.desc()).first()
        if smile_video and smile_video.source_image_path:
            speed_test.source_image_path = smile_video.source_image_path
            print(f"📸 Using image: {smile_video.source_image_path}")
        
        db.session.add(speed_test)
        db.session.commit()
        
        print(f"✅ Speed test video created: ID {speed_test.id}")
        print(f"🎯 Platform: general (no optimization)")
        print(f"⏱️ Expected: Faster than social media optimized videos")
        
        # Now generate with minimal settings
        try:
            from vertex_ai_video_generator import VertexAIVideoGenerator
            generator = VertexAIVideoGenerator()
            
            # Simple prompt without platform optimization
            simple_prompt = "A person smiling, natural lighting"
            
            print(f"🚀 Starting speed test generation...")
            print(f"📝 Prompt: {simple_prompt}")
            print(f"⚙️ No social media optimization")
            print(f"📱 Platform: general")
            
            # Generate with minimal duration for speed
            result = generator.generate_video_from_image(
                image_path=speed_test.source_image_path,
                prompt=simple_prompt,
                video_order_id=speed_test.id,
                duration=5  # Minimal duration
            )
            
            if result and result.get('operation_id'):
                speed_test.veo3_operation_id = result['operation_id']
                speed_test.status = OrderStatus.IN_PRODUCTION
                db.session.commit()
                
                print(f"✅ SPEED TEST STARTED!")
                print(f"🔄 Operation: {result['operation_id']}")
                print(f"📊 Compare with Smile video processing time")
                print(f"⏰ Expected: Sub-3 minute completion")
                
                return speed_test
            else:
                print(f"❌ Speed test generation failed")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            speed_test.status = OrderStatus.CANCELLED
            db.session.commit()
        
        return None

if __name__ == "__main__":
    create_speed_test_video()