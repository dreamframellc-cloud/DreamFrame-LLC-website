#!/usr/bin/env python3
"""
Quick video generation using optimized settings
"""

import os
from datetime import datetime
from models import VideoOrder, OrderStatus, User
from app import app, db

def create_quick_video():
    """Create a video using fast generation settings"""
    
    with app.app_context():
        print("🚀 QUICK VIDEO GENERATION")
        print("=" * 40)
        
        # Get user
        user = User.query.filter_by(email="jeremyprice50@gmail.com").first()
        if not user:
            print("❌ User not found")
            return None
        
        # Create optimized video order
        quick_video = VideoOrder()
        quick_video.user_id = user.id
        quick_video.title = "Quick Test"
        quick_video.description = "A person standing in natural outdoor lighting, looking confident"
        quick_video.platform = "general"  # KEY: No social media optimization
        quick_video.status = OrderStatus.PENDING
        quick_video.created_at = datetime.utcnow()
        
        # Use existing source image
        source_image = "uploads/2_1754068203_IMG_1623.jpeg"
        if os.path.exists(source_image):
            quick_video.source_image_path = source_image
            print(f"📸 Using image: {source_image}")
        else:
            print("❌ Source image not found")
            return None
        
        # Add to database
        db.session.add(quick_video)
        db.session.commit()
        
        print(f"✅ Quick video created: ID {quick_video.id}")
        print(f"🎯 Platform: {quick_video.platform} (optimized for speed)")
        print(f"⏱️ Expected: 2-3 minutes processing time")
        
        # Start generation
        try:
            from vertex_ai_video_generator import VertexAIVideoGenerator
            generator = VertexAIVideoGenerator()
            
            # Simple, clear prompt
            prompt = "A person standing confidently in natural lighting"
            
            print(f"🎬 Starting generation...")
            print(f"📝 Prompt: {prompt}")
            print(f"⚙️ Settings: 5 second duration, standard quality")
            
            # Generate with optimized settings
            result = generator.generate_video_from_image(
                image_path=quick_video.source_image_path,
                prompt=prompt,
                video_order_id=quick_video.id,
                duration=5  # Short duration for speed
            )
            
            if result and result.get('success'):
                quick_video.veo3_operation_id = result.get('operation_id')
                quick_video.status = OrderStatus.IN_PRODUCTION
                db.session.commit()
                
                print(f"✅ GENERATION STARTED!")
                print(f"🔄 Operation: {result.get('operation_id')}")
                print(f"📊 Compare with social media videos")
                print(f"⏰ Target completion: 2-3 minutes")
                
                return quick_video
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error during generation: {str(e)}")
            quick_video.status = OrderStatus.CANCELLED
            db.session.commit()
            return None

if __name__ == "__main__":
    create_quick_video()