#!/usr/bin/env python3
"""
Create a test video order to demonstrate real video generation capabilities
"""

import os
from models import VideoOrder, db, OrderStatus
from app import app
from datetime import datetime

def create_test_video_order():
    """Create a new video order for testing actual MP4 generation"""
    
    with app.app_context():
        # Find a good test image
        image_path = None
        test_images = [
            'uploads/2_1754027739_IMG_1622.jpeg',
            'uploads/2_1754026420_IMG_1580.jpeg',
            'uploads/1_1754003646_IMG_1439_1753901933903.jpeg'
        ]
        
        for img in test_images:
            if os.path.exists(img):
                image_path = img
                break
        
        if not image_path:
            print("❌ No test image found")
            return None
        
        # Create a new video order specifically for MP4 generation
        new_order = VideoOrder(
            user_id=2,  # Assuming user ID 2 exists
            title="Real MP4 Video Test",
            description="Woman smiling and waving at camera, cinematic movement",
            platform="instagram",
            source_image_path=image_path,
            status=OrderStatus.PENDING,
            created_at=datetime.utcnow(),
            prompt_used="Professional woman in business attire smiling warmly and waving at the camera. Smooth cinematic movement, high quality, engaging personality."
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        print(f"✅ Created test video order:")
        print(f"🆔 Video ID: {new_order.id}")
        print(f"📝 Title: {new_order.title}")
        print(f"📁 Image: {image_path}")
        print(f"📊 Status: {new_order.status.value}")
        
        return new_order.id

if __name__ == "__main__":
    video_id = create_test_video_order()
    if video_id:
        print(f"\n🎬 Test video order created with ID: {video_id}")
        print("This order is ready for real MP4 video generation using RunwayML or similar service.")
    else:
        print("\n❌ Failed to create test video order")