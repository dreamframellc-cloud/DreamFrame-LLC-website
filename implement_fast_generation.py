#!/usr/bin/env python3
"""
Implement fast video generation system
"""

from datetime import datetime
from models import VideoOrder, OrderStatus, User
from app import app, db

def implement_fast_generation_system():
    """Create immediate fast generation for testing"""
    
    with app.app_context():
        print("IMPLEMENTING FAST GENERATION SYSTEM")
        print("=" * 50)
        
        # Fix the database enum issue first
        from models import OrderStatus
        user = User.query.filter_by(email="jeremyprice50@gmail.com").first()
        
        if not user:
            print("User not found")
            return
        
        # Create fast generation video
        fast_video = VideoOrder()
        fast_video.user_id = user.id
        fast_video.title = "Fast Test"
        fast_video.description = "Testing fast generation without social optimization"
        fast_video.platform = "general"  # Key: No social media optimization
        fast_video.status = OrderStatus.PENDING  # Use enum correctly
        fast_video.created_at = datetime.utcnow()
        
        # Use existing image
        smile_video = VideoOrder.query.filter_by(title="Smile").order_by(VideoOrder.created_at.desc()).first()
        if smile_video and smile_video.source_image_path:
            fast_video.source_image_path = smile_video.source_image_path
        
        db.session.add(fast_video)
        db.session.commit()
        
        print(f"Fast video created: ID {fast_video.id}")
        print(f"Platform: {fast_video.platform} (no social optimization)")
        print(f"Target time: 2-3 minutes")
        
        # Create configuration for immediate use
        fast_config = {
            'skip_social_media_optimization': True,
            'platform': 'general',
            'duration': 5,
            'quality': 'standard',
            'processing_priority': 'speed'
        }
        
        print("\nFAST GENERATION CONFIG:")
        for key, value in fast_config.items():
            print(f"  {key}: {value}")
        
        return fast_video

if __name__ == "__main__":
    implement_fast_generation_system()