#!/usr/bin/env python3
"""
Simple test of Vertex AI VEO 3 integration
"""

import os
import json
import requests
from vertex_ai_video_generator import VertexAIVideoGenerator

def test_credentials():
    print("🔧 Testing Vertex AI Credentials")
    print("=" * 40)
    
    # Initialize generator
    generator = VertexAIVideoGenerator()
    
    print(f"📁 Project ID: {generator.project_id}")
    print(f"🌍 Location: {generator.location}")
    print(f"🤖 Model: {generator.model_name}")
    print(f"🔑 API Key: {'✅ Available' if generator.api_key else '❌ Missing'}")
    
    return generator.project_id and generator.api_key

def test_web_interface():
    print("\n🌐 Testing Web Interface")
    print("=" * 30)
    
    try:
        # Test homepage
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"🏠 Homepage: {response.status_code}")
        
        # Test Vertex AI page
        response = requests.get("http://localhost:5000/vertex-ai/", timeout=5)
        print(f"🎬 Vertex AI page: {response.status_code}")
        
        # Check if VEO 3 is mentioned on the page
        if "VEO 3" in response.text:
            print("✅ VEO 3 interface found")
            return True
        else:
            print("⚠️ VEO 3 interface not detected")
            return False
            
    except Exception as e:
        print(f"❌ Web interface error: {str(e)}")
        return False

def test_image_processing():
    print("\n📷 Testing Image Processing")
    print("=" * 35)
    
    test_image = "attached_assets/IMG_1439_1753901933903.jpeg"
    
    if os.path.exists(test_image):
        print(f"✅ Test image found: {test_image}")
        
        # Get file size
        size = os.path.getsize(test_image)
        print(f"📊 Image size: {size:,} bytes")
        
        # Test base64 encoding
        try:
            import base64
            with open(test_image, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            print(f"📝 Base64 encoded: {len(image_data):,} characters")
            print("✅ Image processing ready")
            return True
            
        except Exception as e:
            print(f"❌ Image processing error: {str(e)}")
            return False
    else:
        print(f"❌ Test image not found: {test_image}")
        return False

def main():
    print("🧪 Vertex AI VEO 3 Simple Test")
    print("=" * 50)
    
    # Test credentials
    creds_ok = test_credentials()
    
    # Test web interface
    web_ok = test_web_interface()
    
    # Test image processing
    image_ok = test_image_processing()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Credentials: {'✅ OK' if creds_ok else '❌ Failed'}")
    print(f"   Web Interface: {'✅ OK' if web_ok else '❌ Failed'}")
    print(f"   Image Processing: {'✅ OK' if image_ok else '❌ Failed'}")
    
    if all([creds_ok, web_ok, image_ok]):
        print("\n🎉 All tests passed! Vertex AI integration is ready.")
        print("🚀 Ready for video generation at: /vertex-ai/generate")
    else:
        print("\n⚠️ Some tests failed - check configuration")

if __name__ == "__main__":
    main()