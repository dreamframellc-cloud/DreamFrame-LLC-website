#!/usr/bin/env python3
"""
VEO 2 Only System - VEO 2 for all video generation
"""

from simple_veo2_client import SimpleVEO2Client
import time
import os

def generate_veo2_video_only(image_path: str, prompt: str, order_id: int) -> dict:
    """
    Generate video using only VEO 2 (primary system)
    
    Args:
        image_path: Path to the uploaded image
        prompt: Video generation prompt
        order_id: Database order ID
        
    Returns:
        dict: Result with success status and operation details
    """
    
    print(f"🎬 VEO 2 Only Video Generation")
    print(f"📸 Image: {image_path}")
    print(f"📝 Prompt: {prompt}")
    print(f"🆔 Order: {order_id}")
    print("🎬 Using VEO 2 exclusively for motion video generation")
    
    try:
        # Initialize VEO 2 client
        client = SimpleVEO2Client()
        
        if not client.credentials:
            return {
                'success': False,
                'message': 'VEO 2 credentials not available',
                'service': 'VEO 2 Only System'
            }
        
        # Enhanced prompt for better motion
        enhanced_prompt = f"Based on the uploaded image: {prompt}. Create dramatic motion with realistic facial expressions, cinematic lighting, and smooth camera movement."
        
        print(f"🎭 Enhanced Prompt: {enhanced_prompt[:100]}...")
        
        # Generate video with VEO 2
        result = client.generate_video(enhanced_prompt, 6)
        
        if result and result.get('success'):
            operation_id = result.get('operation_id')
            
            print(f"✅ VEO 2 Generation Started: {operation_id}")
            
            return {
                'success': True,
                'operation_id': operation_id,
                'message': f'VEO 2 video generation started successfully',
                'service': 'VEO 2 Only System',
                'model': 'veo-2.0-generate-001',
                'expected_duration': '5-8 seconds',
                'processing_time': '2-5 minutes'
            }
        else:
            error_msg = result.get('message', 'Unknown VEO 2 error') if result else 'No response from VEO 2'
            
            print(f"❌ VEO 2 Generation Failed: {error_msg}")
            
            return {
                'success': False,
                'message': error_msg,
                'service': 'VEO 2 Only System'
            }
    
    except Exception as e:
        print(f"❌ VEO 2 System Error: {e}")
        
        return {
            'success': False,
            'message': f'VEO 2 system error: {str(e)}',
            'service': 'VEO 2 Only System'
        }

def get_system_status():
    """Get current system status"""
    
    client = SimpleVEO2Client()
    
    status = {

        'veo2': 'ACTIVE' if client.credentials else 'UNAVAILABLE',
        'primary_system': 'VEO 2',
        'video_type': 'Motion Videos (5-8 seconds)',
        'processing_time': '2-5 minutes',
        'codec': 'H.264 (browser compatible)'
    }
    
    return status

if __name__ == "__main__":
    print("🎬 VEO 2 Only System Status")
    print("=" * 50)
    
    status = get_system_status()
    
    for key, value in status.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n✅ System configured for VEO 2 only video generation")
    print("✅ System configured for VEO 2 motion video generation")