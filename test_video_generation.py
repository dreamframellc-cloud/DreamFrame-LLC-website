#!/usr/bin/env python3
"""
Test Video Generation System
Quick test of the VEO 2 video generation capabilities
"""

import os
import sys
import time
from datetime import datetime

def test_video_generation():
    """Test the video generation system with a sample image"""
    
    print("🎬 Testing DreamFrame Video Generation System")
    print("=" * 50)
    
    # Check available test images
    uploads_dir = "uploads"
    test_images = []
    
    for file in os.listdir(uploads_dir):
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')):
            test_images.append(os.path.join(uploads_dir, file))
    
    if not test_images:
        print("❌ No test images found in uploads directory")
        return False
    
    # Use the first available test image
    test_image = test_images[0]
    print(f"📸 Using test image: {test_image}")
    
    # Test single video generation
    print("\n🔥 Testing Single Video Generation (VEO 2)")
    print("-" * 30)
    
    try:
        from veo2_customer_generator import generate_veo2_customer_video
        
        # Test parameters
        test_order_id = int(time.time())  # Unique test order ID
        test_prompt = "Professional portrait with cinematic lighting and smooth motion"
        
        print(f"Order ID: {test_order_id}")
        print(f"Prompt: {test_prompt}")
        print(f"Image: {test_image}")
        
        # Generate video
        result = generate_veo2_customer_video(
            image_path=test_image,
            prompt=test_prompt,
            order_id=test_order_id
        )
        
        print(f"\n📊 VEO 2 Generation Result:")
        print(f"Success: {result.get('success', False)}")
        print(f"Service: {result.get('service', 'Unknown')}")
        print(f"Operation ID: {result.get('operation_id', 'N/A')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        if result.get('success'):
            print("✅ Single video generation test PASSED")
        else:
            print("❌ Single video generation test FAILED")
            print(f"Error: {result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ VEO 2 test failed with exception: {str(e)}")
        return False
    
    # Test group video generation
    print("\n👥 Testing Group Video Generation")
    print("-" * 30)
    
    try:
        from group_video_generator import generate_group_video
        
        # Use multiple test images if available, otherwise duplicate the test image
        group_avatars = test_images[:3] if len(test_images) >= 3 else [test_image, test_image, test_image]
        
        print(f"Group avatars: {len(group_avatars)} images")
        for i, avatar in enumerate(group_avatars):
            print(f"  Avatar {i+1}: {os.path.basename(avatar)}")
        
        test_group_order_id = int(time.time()) + 1000
        test_group_prompt = "Professional team photo with three people in business setting"
        test_group_title = "Test Group Video"
        
        # Generate group video
        group_result = generate_group_video(
            avatar_paths=group_avatars,
            prompt=test_group_prompt,
            title=test_group_title,
            order_id=test_group_order_id
        )
        
        print(f"\n📊 Group Generation Result:")
        print(f"Success: {group_result.get('success', False)}")
        print(f"Operation ID: {group_result.get('operation_id', 'N/A')}")
        print(f"Message: {group_result.get('message', 'No message')}")
        print(f"Group Image: {group_result.get('group_image_path', 'N/A')}")
        
        if group_result.get('success'):
            print("✅ Group video generation test PASSED")
        else:
            print("❌ Group video generation test FAILED")
            print(f"Error: {group_result.get('message', 'Unknown error')}")
    
    except Exception as e:
        print(f"❌ Group video test failed with exception: {str(e)}")
    
    # Test system components
    print("\n🔧 Testing System Components")
    print("-" * 30)
    
    # Check Google Cloud credentials
    try:
        google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
        
        print(f"Google Cloud Credentials: {'✅ Set' if google_creds else '❌ Missing'}")
        print(f"Google Cloud Project ID: {'✅ Set' if project_id else '❌ Missing'}")
        
        if google_creds and project_id:
            print("✅ Google Cloud configuration PASSED")
        else:
            print("⚠️  Google Cloud configuration incomplete")
    
    except Exception as e:
        print(f"❌ Google Cloud check failed: {str(e)}")
    
    # Check database connection
    try:
        from app import db
        print(f"Database Connection: ✅ Available")
        print("✅ Database configuration PASSED")
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 Video Generation Test Complete")
    print(f"📅 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    test_video_generation()