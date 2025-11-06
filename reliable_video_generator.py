"""
Reliable Video Generation System
Multiple API integrations for dependable video creation
"""

import os
import requests
import time
import logging
from typing import Dict, Optional, Any

class ReliableVideoGenerator:
    """Multi-service video generation with fallback options"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def generate_video(self, prompt: str, image_path: str = None) -> Dict[str, Any]:
        """Generate video using multiple services with fallbacks"""
        
        # Try RunwayML first (most reliable)
        try:
            result = self.generate_runway_video(prompt, image_path)
            if result['success']:
                return result
        except Exception as e:
            self.logger.error(f"RunwayML failed: {e}")
        
        # Try Pika Labs as backup
        try:
            result = self.generate_pika_video(prompt, image_path)
            if result['success']:
                return result
        except Exception as e:
            self.logger.error(f"Pika Labs failed: {e}")
            
        # Try Stable Video Diffusion
        try:
            result = self.generate_stable_video(prompt, image_path)
            if result['success']:
                return result
        except Exception as e:
            self.logger.error(f"Stable Video failed: {e}")
            
        return {
            'success': False,
            'error': 'All video generation services failed',
            'completion_time': 0
        }
    
    def generate_runway_video(self, prompt: str, image_path: str = None) -> Dict[str, Any]:
        """Generate video using RunwayML API"""
        api_key = os.environ.get('RUNWAYML_API_KEY')
        if not api_key:
            return {'success': False, 'error': 'RunwayML API key not found'}
            
        url = "https://api.runwayml.com/v1/image_to_video"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "gen3a_turbo",
            "prompt_text": prompt,
            "duration": 5,
            "ratio": "16:9",
            "resolution": "720p"
        }
        
        if image_path and os.path.exists(image_path):
            # Upload image first
            with open(image_path, 'rb') as f:
                files = {'image': f}
                upload_response = requests.post(
                    "https://api.runwayml.com/v1/uploads",
                    headers={"Authorization": f"Bearer {api_key}"},
                    files=files
                )
                if upload_response.status_code == 200:
                    data["image"] = upload_response.json()["url"]
        
        start_time = time.time()
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            task_id = result.get('id')
            
            # Poll for completion
            return self.poll_runway_completion(task_id, start_time)
        else:
            return {
                'success': False,
                'error': f'RunwayML API error: {response.status_code}',
                'completion_time': time.time() - start_time
            }
    
    def poll_runway_completion(self, task_id: str, start_time: float) -> Dict[str, Any]:
        """Poll RunwayML for video completion"""
        api_key = os.environ.get('RUNWAYML_API_KEY')
        url = f"https://api.runwayml.com/v1/tasks/{task_id}"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        max_attempts = 60  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                
                if status == 'SUCCEEDED':
                    video_url = result.get('output', [{}])[0].get('url')
                    return {
                        'success': True,
                        'video_url': video_url,
                        'task_id': task_id,
                        'completion_time': time.time() - start_time,
                        'service': 'RunwayML'
                    }
                elif status == 'FAILED':
                    return {
                        'success': False,
                        'error': 'RunwayML generation failed',
                        'completion_time': time.time() - start_time
                    }
            
            time.sleep(5)
            attempt += 1
        
        return {
            'success': False,
            'error': 'RunwayML timeout',
            'completion_time': time.time() - start_time
        }
    
    def generate_pika_video(self, prompt: str, image_path: str = None) -> Dict[str, Any]:
        """Generate video using Pika Labs API (alternative)"""
        # Pika implementation would go here
        return {
            'success': False,
            'error': 'Pika Labs integration pending API access'
        }
    
    def generate_stable_video(self, prompt: str, image_path: str = None) -> Dict[str, Any]:
        """Generate video using Stable Video Diffusion"""
        # Stable Video implementation would go here
        return {
            'success': False,
            'error': 'Stable Video integration pending'
        }

def create_reliable_video(prompt: str, image_path: str = None, customer_name: str = "Customer") -> Dict[str, Any]:
    """Main function for reliable video generation"""
    generator = ReliableVideoGenerator()
    
    print(f"🎬 Reliable Video Generation for {customer_name}")
    print(f"📝 Prompt: {prompt[:100]}...")
    if image_path:
        print(f"📸 Image: {image_path}")
    
    start_time = time.time()
    result = generator.generate_video(prompt, image_path)
    
    if result['success']:
        print(f"✅ Video generated successfully in {result['completion_time']:.1f}s")
        print(f"🎥 Service: {result.get('service', 'Unknown')}")
        print(f"🔗 Video URL: {result.get('video_url', 'N/A')}")
    else:
        print(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
    
    return result

if __name__ == "__main__":
    # Test the reliable video generator
    test_prompt = "A beautiful sunset over the ocean with waves gently rolling onto the shore"
    result = create_reliable_video(test_prompt)
    print(f"Test result: {result}")