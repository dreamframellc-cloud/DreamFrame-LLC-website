#!/usr/bin/env python3
"""
Test video creation with the fixed system
"""

import os
from datetime import datetime
from models import VideoOrder, OrderStatus, User
from app import app, db

def test_optimized_video_creation():
    """Test creating a video with the fixed enum system"""
    
    with app.app_context():
        print("🧪 TESTING OPTIMIZED VIDEO CREATION")
        print("=" * 45)
        
        # Get user
        user = User.query.filter_by(email="jeremyprice50@gmail.com").first()
        if not user:
            print("❌ User not found")
            return None
        
        # Create test video order
        test_video = VideoOrder()
        test_video.user_id = user.id
        test_video.title = "Speed Demo"
        test_video.description = "Testing fast generation without social media overhead"
        test_video.platform = "general"  # Key: Bypass social optimization
        test_video.status = OrderStatus.PENDING  # Use enum correctly
        test_video.created_at = datetime.utcnow()
        
        # Use existing image
        source_image = "uploads/2_1754068203_IMG_1623.jpeg"
        if os.path.exists(source_image):
            test_video.source_image_path = source_image
            print(f"📸 Source: {source_image}")
        else:
            print("❌ Source image not found")
            return None
        
        # Save to database
        db.session.add(test_video)
        db.session.commit()
        
        print(f"✅ Test video created: ID {test_video.id}")
        print(f"🎯 Platform: {test_video.platform}")
        print(f"📊 Status: {test_video.status}")
        
        # Test generation with fixed enum
        try:
            from vertex_ai_video_generator import VertexAIVideoGenerator
            generator = VertexAIVideoGenerator()
            
            prompt = "A confident person in natural lighting"
            
            print(f"🚀 Testing generation with fixed enums...")
            print(f"📝 Prompt: {prompt}")
            print(f"⚙️ Duration: 5 seconds")
            print(f"🔧 Fixed database enum issue")
            
            # Test the generation
            result = generator.generate_video_from_image(
                image_path=test_video.source_image_path,
                prompt=prompt,
                video_order_id=test_video.id,
                duration=5
            )
            
            if result and result.get('success'):
                print(f"✅ GENERATION TEST SUCCESSFUL!")
                print(f"🔄 Operation ID: {result.get('operation_id')}")
                print(f"⏱️ Expected completion: 2-3 minutes")
                print(f"🚀 No social media overhead")
                
                # Update database with operation ID
                test_video.veo3_operation_id = result.get('operation_id')
                test_video.status = OrderStatus.IN_PRODUCTION
                db.session.commit()
                
                return test_video
            else:
                print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
                return None
                
        except Exception as e:
            print(f"❌ Error during generation: {str(e)}")
            test_video.status = OrderStatus.CANCELLED
            db.session.commit()
            return None

if __name__ == "__main__":
    test_optimized_video_creation()