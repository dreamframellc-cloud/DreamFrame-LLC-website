#!/usr/bin/env python3
"""
Quick recovery for timeout issues - recreate Love video
"""

import os
from datetime import datetime
from models import VideoOrder, OrderStatus, User
from app import app, db
import vertex_ai_video_generator

def quick_recovery_love_video():
    """Create a new Love video to replace the timed-out one"""
    
    with app.app_context():
        # Get the timed-out Love video for reference
        old_video = VideoOrder.query.filter_by(title="Love").order_by(VideoOrder.created_at.desc()).first()
        
        if not old_video:
            print("❌ Original Love video not found")
            return
        
        print("🔄 QUICK RECOVERY - Love Video")
        print("=" * 40)
        print(f"📹 Original video: ID {old_video.id}")
        print(f"⏱️ Timeout after: {(datetime.utcnow() - old_video.created_at).total_seconds() / 60:.1f} minutes")
        
        # Check if user exists
        user = User.query.get(old_video.user_id)
        if not user:
            print("❌ User not found")
            return
        
        print(f"👤 Customer: {user.email}")
        
        # Create new video order with same settings
        print("✨ Creating new Love video with same settings...")
        
        new_video = VideoOrder()
        new_video.user_id = old_video.user_id
        new_video.title = "Love (Recovery)"
        new_video.description = old_video.description or "smile and wave"
        new_video.platform = old_video.platform or "instagram"
        new_video.source_image_path = old_video.source_image_path
        new_video.status = OrderStatus.PENDING
        new_video.created_at = datetime.utcnow()
        
        db.session.add(new_video)
        db.session.commit()
        
        print(f"✅ New video created: ID {new_video.id}")
        
        # Immediately start generation
        print("🚀 Starting immediate VEO 3 generation...")
        
        try:
            # Use the same image and prompt
            generator = vertex_ai_video_generator.VertexAIVideoGenerator()
            
            # Generate with optimized settings
            prompt = "A person smiling and waving in a friendly manner, cinematic lighting, professional quality"
            
            if os.path.exists(old_video.source_image_path):
                print(f"📸 Using image: {old_video.source_image_path}")
                
                result = generator.generate_video_from_image(
                    image_path=old_video.source_image_path,
                    prompt=prompt
                )
                
                if result and 'operation_id' in result:
                    new_video.veo3_operation_id = result['operation_id']
                    new_video.status = OrderStatus.IN_PRODUCTION
                    db.session.commit()
                    
                    print(f"🎬 NEW GENERATION STARTED!")
                    print(f"🔄 Operation ID: {result['operation_id']}")
                    print(f"⏰ Expected completion: 3-6 minutes")
                    print(f"📱 Monitor at: /my-videos")
                    
                    return new_video
                    
            else:
                print(f"❌ Original image not found: {old_video.source_image_path}")
                
        except Exception as e:
            print(f"❌ Generation failed: {str(e)}")
            new_video.status = OrderStatus.CANCELLED
            db.session.commit()
            
        return None

if __name__ == "__main__":
    quick_recovery_love_video()