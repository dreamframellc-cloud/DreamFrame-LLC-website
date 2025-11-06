"""
Fast Video Generator - VEO 3 Fast Integration
Replaces slow VEO 3 Preview with VEO 3 Fast model for optimal speed
"""

import os
import sys
sys.path.append('.')

from veo3_fast_generator import VEO3FastGenerator
from app import db
from models import VideoOrder, OrderStatus
import time

def generate_fast_customer_video(video_order_id: int, image_path: str, prompt: str):
    """
    Generate customer video using VEO 3 Fast model
    Optimized for speed and reliability
    """
    
    print(f"⚡ Fast video generation for order {video_order_id}")
    print(f"🎬 Prompt: {prompt}")
    print(f"📸 Image: {image_path}")
    
    try:
        # Initialize VEO 3 Fast generator
        generator = VEO3FastGenerator()
        
        # Enhanced prompt with image context
        enhanced_prompt = f"Based on the uploaded image: {prompt}. Create a dynamic video transformation with smooth motion and cinematic quality."
        
        print(f"✨ Enhanced prompt: {enhanced_prompt[:100]}...")
        
        # Generate with VEO 3 Fast
        result = generator.generate_fast_video(enhanced_prompt, duration=8)
        
        if result and result.get('success'):
            print(f"🎉 Fast generation SUCCESS in {result.get('generation_time', 0):.1f}s")
            
            # Update database record
            video_order = VideoOrder.query.get(video_order_id)
            if video_order:
                video_order.veo3_operation_id = result.get('operation_id', '')[:190]
                video_order.status = OrderStatus.COMPLETED
                video_order.prompt_used = enhanced_prompt[:500]
                
                # Set video path based on result
                if result.get('video_data'):
                    video_path = f"static/videos/fast_{video_order_id}.mp4"
                    video_order.generated_video_path = video_path
                
                db.session.commit()
                print(f"✅ Database updated for fast video {video_order_id}")
            
            return {
                'success': True,
                'operation_name': result.get('operation_id'),
                'enhanced_prompt': enhanced_prompt,
                'generation_time': result.get('generation_time'),
                'model': 'veo-3-fast'
            }
        
        else:
            print(f"❌ Fast generation failed: {result.get('error') if result else 'Unknown error'}")
            
            # Update status to failed
            video_order = VideoOrder.query.get(video_order_id)
            if video_order:
                video_order.status = OrderStatus.FAILED
                db.session.commit()
            
            return {
                'success': False,
                'error': result.get('error') if result else 'Fast generation failed'
            }
    
    except Exception as e:
        print(f"💥 Fast video generation error: {e}")
        
        # Update status to failed
        try:
            video_order = VideoOrder.query.get(video_order_id)
            if video_order:
                video_order.status = OrderStatus.FAILED
                db.session.commit()
        except:
            pass
        
        return {
            'success': False,
            'error': f'Fast generation exception: {str(e)}'
        }

def test_fast_generation():
    """Test the fast generation system"""
    
    print("🚀 Testing Fast Video Generation System")
    print("=" * 50)
    
    # Test with mock data
    test_result = generate_fast_customer_video(
        video_order_id=999,  # Test ID
        image_path="test_image.jpg",
        prompt="A magical forest with sparkling lights"
    )
    
    if test_result.get('success'):
        print("✅ Fast generation test PASSED")
        print(f"⚡ Model: {test_result.get('model')}")
        print(f"⏱️  Time: {test_result.get('generation_time', 0):.1f}s")
    else:
        print("❌ Fast generation test FAILED")
        print(f"Error: {test_result.get('error')}")
    
    return test_result

if __name__ == "__main__":
    test_fast_generation()