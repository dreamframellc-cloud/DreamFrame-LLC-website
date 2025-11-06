"""
Runway ML Video Generation
Direct alternative to VEO 3 with similar capabilities
"""

import os
import requests
import time
import logging
from typing import Dict, Any, Optional
import json

class RunwayVideoGenerator:
    """Runway ML Gen-3 Alpha video generation - direct VEO 3 alternative"""
    
    def __init__(self):
        self.base_url = "https://api.runwayml.com/v1"
        self.api_key = os.environ.get('RUNWAYML_API_KEY')
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)
    
    def generate_video_from_image(self, image_path: str, prompt: str, duration: int = 5) -> Dict[str, Any]:
        """Generate video from image using Runway ML Gen-3 Alpha (similar to VEO 3)"""
        
        if not self.api_key:
            return {'success': False, 'error': 'Runway ML API key not found'}
        
        start_time = time.time()
        
        try:
            # Step 1: Upload image to Runway
            print("📤 Uploading image to Runway ML...")
            upload_result = self.upload_image(image_path)
            if not upload_result['success']:
                return upload_result
            
            image_url = upload_result['image_url']
            print(f"✅ Image uploaded: {image_url}")
            
            # Step 2: Create video generation task
            print("🎬 Starting Gen-3 Alpha video generation...")
            task_result = self.create_video_task(image_url, prompt, duration)
            if not task_result['success']:
                return task_result
            
            task_id = task_result['task_id']
            print(f"🔄 Generation task created: {task_id}")
            
            # Step 3: Monitor task completion
            print("⏳ Monitoring video generation...")
            completion_result = self.monitor_task_completion(task_id, start_time)
            
            return completion_result
            
        except Exception as e:
            self.logger.error(f"Runway video generation error: {e}")
            return {
                'success': False,
                'error': f'Runway generation failed: {str(e)}',
                'completion_time': time.time() - start_time
            }
    
    def upload_image(self, image_path: str) -> Dict[str, Any]:
        """Upload image to Runway ML storage"""
        if not os.path.exists(image_path):
            return {'success': False, 'error': f'Image file not found: {image_path}'}
        
        url = f"{self.base_url}/uploads"
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers={"Authorization": f"Bearer {self.api_key}"}, files=files)
        
        if response.status_code == 200:
            result = response.json()
            return {'success': True, 'image_url': result['url']}
        else:
            return {'success': False, 'error': f'Image upload failed: {response.status_code}'}
    
    def create_video_task(self, image_url: str, prompt: str, duration: int) -> Dict[str, Any]:
        """Create video generation task using Gen-3 Alpha"""
        url = f"{self.base_url}/image_to_video"
        
        data = {
            "model": "gen3a_turbo",  # Gen-3 Alpha Turbo for speed
            "prompt_image": image_url,
            "prompt_text": prompt,
            "duration": duration,
            "ratio": "16:9",
            "resolution": "720p",
            "seed": None  # Random seed for variety
        }
        
        response = requests.post(url, headers=self.headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            return {'success': True, 'task_id': result['id']}
        else:
            error_detail = response.text
            return {'success': False, 'error': f'Task creation failed: {response.status_code} - {error_detail}'}
    
    def monitor_task_completion(self, task_id: str, start_time: float) -> Dict[str, Any]:
        """Monitor task until completion"""
        url = f"{self.base_url}/tasks/{task_id}"
        
        max_attempts = 120  # 10 minutes max (5 second intervals)
        attempt = 0
        
        while attempt < max_attempts:
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                result = response.json()
                status = result.get('status')
                progress = result.get('progress', 0)
                
                print(f"🔄 Status: {status} ({progress}%) - attempt {attempt + 1}")
                
                if status == 'SUCCEEDED':
                    output = result.get('output', [])
                    if output and len(output) > 0:
                        video_url = output[0]
                        completion_time = time.time() - start_time
                        
                        print(f"✅ Video completed in {completion_time:.1f} seconds!")
                        print(f"🎥 Video URL: {video_url}")
                        
                        return {
                            'success': True,
                            'video_url': video_url,
                            'task_id': task_id,
                            'completion_time': completion_time,
                            'service': 'Runway ML Gen-3'
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'Video completed but no output URL found',
                            'completion_time': time.time() - start_time
                        }
                
                elif status == 'FAILED':
                    error_message = result.get('failure_reason', 'Unknown failure')
                    return {
                        'success': False,
                        'error': f'Runway generation failed: {error_message}',
                        'completion_time': time.time() - start_time
                    }
                
                elif status in ['PENDING', 'RUNNING']:
                    # Continue monitoring
                    pass
                else:
                    print(f"⚠️ Unknown status: {status}")
            
            time.sleep(5)
            attempt += 1
        
        return {
            'success': False,
            'error': 'Runway video generation timeout (10 minutes)',
            'completion_time': time.time() - start_time
        }

def create_runway_video(image_path: str, prompt: str, duration: int = 5) -> Dict[str, Any]:
    """Generate video using Runway ML Gen-3 Alpha (VEO 3 alternative)"""
    generator = RunwayVideoGenerator()
    
    print(f"🛫 Runway ML Gen-3 Alpha Video Generation")
    print(f"📸 Image: {image_path}")
    print(f"📝 Prompt: {prompt}")
    print(f"⏱️ Duration: {duration} seconds")
    
    result = generator.generate_video_from_image(image_path, prompt, duration)
    
    if result['success']:
        print(f"🎉 Runway video completed successfully!")
        print(f"⚡ Generation time: {result['completion_time']:.1f} seconds")
        print(f"🎬 Service: {result['service']}")
    else:
        print(f"❌ Runway generation failed: {result.get('error')}")
    
    return result

if __name__ == "__main__":
    # Test Runway video generation
    test_image = "test_image.png"
    test_prompt = "The woman in the image opens her mouth revealing fangs with dramatic lighting"
    result = create_runway_video(test_image, test_prompt, duration=5)
    print(f"Test result: {result}")