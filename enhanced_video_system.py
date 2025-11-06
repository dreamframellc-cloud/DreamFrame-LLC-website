"""
Enhanced DreamFrame Video System
VEO 2 and VEO 3 video generation system
"""

import os
import time
from typing import Dict, Any

def create_enhanced_dreamframe_video(image_path: str, prompt: str, order_id: int = None) -> Dict[str, Any]:
    """
    Create enhanced video using AI systems:
    1. VEO 2 for motion video generation (primary)
    2. VEO 3 for full video generation (fallback)
    3. Hybrid computer vision as final fallback
    VEO 2 primary system with VEO 3 and hybrid fallbacks.
    """
    
    start_time = time.time()
    
    print(f"🎬 Enhanced DreamFrame Video System")
    print(f"📸 Image: {image_path}")
    print(f"📝 Prompt: {prompt}")
    print(f"🆔 Order: {order_id}")
    
    # VEO 2 PRIMARY SYSTEM
    print("🎬 Using VEO 2 for video generation (primary system)")
    
    # Use VEO 2 for all video generation
    
    try:
        from veo2_customer_generator import generate_veo2_customer_video
        
        result = generate_veo2_customer_video(
            image_path=image_path,
            prompt=prompt,
            order_id=order_id
        )
        
        if result.get('success'):
            print("✅ VEO 2 video generation successful!")
            return result
        else:
            print("⚠️ VEO 2 failed, trying VEO 3...")
    
    except Exception as e:
        print(f"⚠️ VEO 2 error: {e}, trying VEO 3...")
    
    # Fallback to VEO 3 if VEO 2 fails
    print("🚀 Using VEO 3 for video generation")
    
    try:
        from veo3_with_proper_auth import create_properly_authenticated_veo3_video
        
        # Create enhanced prompt for VEO 3
        enhanced_prompt = create_veo3_prompt(prompt, image_path)
        
        result = create_properly_authenticated_veo3_video(
            prompt=enhanced_prompt,
            order_id=order_id
        )
        
        if result.get('success'):
            print("✅ VEO 3 video generation successful!")
            return result
        else:
            print("⚠️ VEO 3 failed, using hybrid fallback...")
    
    except Exception as e:
        print(f"⚠️ VEO 3 error: {e}, using hybrid fallback...")
    
    # Fallback to hybrid system
    print("🔧 Using hybrid facial animation fallback")
    
    from hybrid_facial_animator import create_hybrid_facial_animation
    result = create_hybrid_facial_animation(
        image_path=image_path,
        prompt=prompt,
        order_id=order_id
    )
    
    completion_time = time.time() - start_time
    
    if result.get('success'):
        result['message'] = f"{result.get('message', '')} (Enhanced system with fallback)"
        return result
    else:
        return {
            'success': False,
            'error': 'All video generation methods failed',
            'completion_time': completion_time,
            'service': 'Enhanced DreamFrame System'
        }

def detect_portrait_request(prompt: str) -> bool:
    """Detect if this is a portrait/facial animation request"""
    
    portrait_keywords = [
        'face', 'facial', 'portrait', 'person', 'wink', 'smile', 'laugh',
        'expression', 'eyes', 'mouth', 'head', 'look', 'gaze', 'nod'
    ]
    
    prompt_lower = prompt.lower()
    
    for keyword in portrait_keywords:
        if keyword in prompt_lower:
            return True
    
    return False

def create_veo3_prompt(original_prompt: str, image_path: str) -> str:
    """Create enhanced prompt for VEO 3 based on original prompt and image"""
    
    # Analyze image context (basic analysis)
    image_context = analyze_image_context(image_path)
    
    # Create cinematic prompt for VEO 3
    enhanced_prompt = f"""
    Professional cinematic video: {original_prompt}
    
    Style: High-quality, professional cinematography with smooth camera movements.
    Lighting: Natural, well-balanced lighting with cinematic depth.
    Motion: Fluid, realistic movements with professional video production quality.
    
    {image_context}
    
    Duration: 5-8 seconds of premium video content.
    """
    
    return enhanced_prompt.strip()

def analyze_image_context(image_path: str) -> str:
    """Basic image context analysis for VEO 3 prompting"""
    
    if not os.path.exists(image_path):
        return "Context: Professional video production"
    
    try:
        # Basic file size analysis
        file_size = os.path.getsize(image_path)
        
        if file_size > 1000000:  # > 1MB, likely high quality
            return "Context: High-resolution, professional quality source material"
        else:
            return "Context: Standard quality source material"
            
    except:
        return "Context: Professional video production"

def test_enhanced_system():
    """Test the enhanced video system"""
    
    print("Testing Enhanced DreamFrame Video System...")
    
    # Test with portrait
    portrait_result = create_enhanced_dreamframe_video(
        image_path="uploads/test_portrait.jpg",
        prompt="person winks and smiles at camera",
        order_id=4001
    )
    
    print(f"Portrait test: {portrait_result}")
    
    # Test with landscape
    landscape_result = create_enhanced_dreamframe_video(
        image_path="uploads/test_landscape.jpg", 
        prompt="beautiful mountain landscape with flowing water",
        order_id=4002
    )
    
    print(f"Landscape test: {landscape_result}")

if __name__ == "__main__":
    test_enhanced_system()