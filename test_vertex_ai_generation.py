#!/usr/bin/env python3
"""
Test Vertex AI VEO 3 video generation with real image
"""

import os
import base64
import requests
import json
from vertex_ai_video_generator import create_vertex_ai_video

def test_vertex_ai_generation():
    """Test complete video generation workflow"""
    
    print("🎬 Testing Vertex AI VEO 3 Video Generation")
    print("=" * 50)
    
    # Use existing test image
    test_image = "attached_assets/IMG_1439_1753901933903.jpeg"
    
    if not os.path.exists(test_image):
        print(f"❌ Test image not found: {test_image}")
        return False
    
    print(f"✅ Using test image: {test_image}")
    
    # Test parameters
    test_prompt = "Create a cinematic video with smooth camera movements, dramatic lighting effects, and gentle zoom. Transform this image into a professional video with natural motion and atmospheric enhancement."
    duration = 5
    
    print(f"📝 Prompt: {test_prompt[:100]}...")
    print(f"⏱️ Duration: {duration} seconds")
    
    # Create a test video order manually
    from models import VideoOrder
    from app import app, db
    
    with app.app_context():
        # Create test order
        test_order = VideoOrder()
        test_order.title = "Vertex AI Test Generation"
        test_order.customer_email = "test@dreamframe.com"
        test_order.status = 'PENDING'
        test_order.generation_settings = f"Test VEO 3 - {duration}s"
        
        db.session.add(test_order)
        db.session.commit()
        
        order_id = test_order.id
        print(f"📊 Created test order ID: {order_id}")
    
    # Test the generation function
    try:
        print("🚀 Starting Vertex AI video generation...")
        
        result = create_vertex_ai_video(
            image_path=test_image,
            prompt=test_prompt,
            video_order_id=order_id,
            duration=duration
        )
        
        print("📤 Generation request submitted")
        print(f"🔄 Result: {result}")
        
        if result.get('success'):
            print("✅ Generation started successfully!")
            if 'video_path' in result:
                print(f"🎉 Video saved to: {result['video_path']}")
            return True
        else:
            print(f"❌ Generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        return False

def test_api_endpoint():
    """Test the Vertex AI API endpoint directly"""
    
    print("\n🔗 Testing API Endpoint")
    print("=" * 30)
    
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    api_key = os.environ.get("VEO3_API_KEY")
    
    if not all([project_id, api_key]):
        print("❌ Missing required credentials")
        return False
    
    # Test basic API connectivity
    base_url = "https://us-central1-aiplatform.googleapis.com/v1"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Goog-User-Project": project_id
    }
    
    try:
        # Test with a simple health check or model info request
        test_url = f"{base_url}/projects/{project_id}/locations/us-central1/models"
        
        print(f"📡 Testing connectivity to: {base_url}")
        print(f"🔑 Using project: {project_id}")
        
        response = requests.get(test_url, headers=headers, timeout=10)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API connectivity successful")
            return True
        elif response.status_code == 401:
            print("🔐 Authentication issue - check API key")
            return False
        elif response.status_code == 403:
            print("🚫 Permission denied - check project access")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {str(e)}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 Vertex AI VEO 3 Generation Test Suite")
    print("=" * 60)
    
    # Test API connectivity first
    api_ok = test_api_endpoint()
    
    if api_ok:
        print("\n" + "=" * 60)
        # Test generation workflow
        generation_ok = test_vertex_ai_generation()
        
        if generation_ok:
            print("\n🎉 All tests completed successfully!")
            print("🚀 Vertex AI VEO 3 is ready for production use")
        else:
            print("\n⚠️ Generation test failed - check logs for details")
    else:
        print("\n❌ API connectivity failed - cannot proceed with generation test")

if __name__ == "__main__":
    main()