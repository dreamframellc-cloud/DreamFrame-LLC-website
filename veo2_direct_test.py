#!/usr/bin/env python3
"""
Direct VEO 2 Test - Generate video with user's fangs prompt
"""

from simple_veo2_client import SimpleVEO2Client
import time
import os

def test_veo2_fangs_video():
    """Test VEO 2 with the fangs prompt"""
    
    print("🎬 VEO 2 Direct Test - Fangs Video")
    print("=" * 50)
    
    # Initialize VEO 2 client
    client = SimpleVEO2Client()
    
    if not client.credentials:
        print("❌ VEO 2 credentials missing")
        return False
    
    print(f"✅ VEO 2 Client Ready")
    print(f"Project: {client.project_id}")
    print(f"Model: {client.model_id}")
    
    # User's specific prompt
    prompt = "A mysterious woman opens her mouth to reveal long, sharp fangs, dramatic gothic lighting, cinematic close-up"
    
    print(f"\n📝 Prompt: {prompt}")
    
    # Generate video
    print("\n🎥 Starting VEO 2 generation...")
    result = client.generate_video(prompt, 6)
    
    if result and result.get('success'):
        operation_id = result.get('operation_id')
        print(f"✅ VEO 2 Generation Started!")
        print(f"🆔 Operation ID: {operation_id}")
        print(f"⏱️ Expected duration: 5-8 seconds")
        print(f"📱 Resolution: 720p at 24 FPS")
        print("\n🎬 VEO 2 is now processing your fangs video!")
        
        # In a real implementation, you'd poll for completion
        print("\n📋 Next Steps:")
        print("1. VEO 2 will process the video (typically 2-5 minutes)")
        print("2. Completed video will be available for download")
        print("3. H.264 codec ensures browser compatibility")
        
        return True
        
    else:
        print(f"❌ VEO 2 Generation Failed")
        if result:
            print(f"Error: {result.get('message', 'Unknown error')}")
            if result.get('status_code'):
                print(f"Status Code: {result['status_code']}")
        return False

if __name__ == "__main__":
    success = test_veo2_fangs_video()
    
    if success:
        print("\n🎯 Success! VEO 2 is generating your video.")
        print("The fangs animation will be created using Google's advanced video AI.")
    else:
        print("\n⚠️ VEO 2 test failed. Check credentials and try again.")