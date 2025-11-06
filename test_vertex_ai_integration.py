#!/usr/bin/env python3
"""
Test Vertex AI VEO 3 integration
"""

import os
import sys
from vertex_ai_video_generator import VertexAIVideoGenerator

def test_vertex_ai_setup():
    """Test Vertex AI VEO 3 setup and credentials"""
    
    print("🎬 Testing Vertex AI VEO 3 Integration")
    print("=" * 50)
    
    # Check environment variables
    print("📊 Environment Variables:")
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
    api_key = os.environ.get("VEO3_API_KEY")
    app_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"   GOOGLE_CLOUD_PROJECT_ID: {'✅ Set' if project_id else '❌ Missing'}")
    print(f"   VEO3_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"   GOOGLE_APPLICATION_CREDENTIALS: {'✅ Set' if app_creds else '❌ Missing'}")
    
    if not all([project_id, api_key]):
        print("❌ Missing required credentials")
        return False
    
    # Initialize generator
    try:
        generator = VertexAIVideoGenerator()
        print("✅ Vertex AI VEO 3 Generator initialized successfully")
        
        # Test basic configuration
        print(f"📁 Project ID: {generator.project_id}")
        print(f"🌍 Location: {generator.location}")
        print(f"🤖 Model: {generator.model_name}")
        print(f"⚙️ API Endpoint: {generator.base_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Generator initialization failed: {str(e)}")
        return False

def test_video_generation_workflow():
    """Test the complete video generation workflow"""
    
    print("\n🔄 Testing Video Generation Workflow")
    print("=" * 50)
    
    # Test image processing
    test_image = "attached_assets/IMG_1439_1753901933903.jpeg"
    if os.path.exists(test_image):
        print(f"✅ Test image found: {test_image}")
        
        # Test prompt enhancement
        generator = VertexAIVideoGenerator()
        test_prompt = "Create a cinematic video with smooth motion"
        enhanced_prompt = generator._enhance_prompt_for_veo3(test_prompt, 5)
        
        print("📝 Prompt Enhancement Test:")
        print(f"   Original: {test_prompt}")
        print(f"   Enhanced: {enhanced_prompt[:100]}...")
        
        # Test request preparation (without actual API call)
        try:
            request_payload = generator._prepare_generation_request(
                test_image, test_prompt, 5
            )
            
            print("✅ Request payload prepared successfully")
            print(f"   Model: {request_payload.get('model', 'Unknown')}")
            print(f"   Contents: {len(request_payload.get('contents', []))} items")
            
            return True
            
        except Exception as e:
            print(f"❌ Request preparation failed: {str(e)}")
            return False
    
    else:
        print(f"❌ Test image not found: {test_image}")
        return False

def main():
    """Run all tests"""
    
    print("🧪 Vertex AI VEO 3 Integration Tests")
    print("=" * 60)
    
    # Test setup
    setup_ok = test_vertex_ai_setup()
    
    if setup_ok:
        # Test workflow
        workflow_ok = test_video_generation_workflow()
        
        print("\n" + "=" * 60)
        if setup_ok and workflow_ok:
            print("🎉 All tests passed! Vertex AI integration is ready.")
            print("🚀 You can now generate videos using:")
            print("   /vertex-ai/generate")
        else:
            print("⚠️ Some tests failed. Check configuration.")
    
    else:
        print("\n❌ Setup failed. Cannot proceed with workflow tests.")

if __name__ == "__main__":
    main()