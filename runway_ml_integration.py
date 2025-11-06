#!/usr/bin/env python3
"""
RunwayML Gen-3A Turbo Integration - No FFmpeg
Pure AI video generation from customer images
"""

import os
import requests
import time
import json
from google import genai
from google.genai import types

class RunwayMLGenerator:
    def __init__(self):
        self.api_key = os.environ.get('RUNWAY_API_KEY')
        self.client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        self.base_url = "https://api.dev.runwayml.com/v1"
        
    def analyze_customer_image(self, image_path):
        """Analyze customer's image with Gemini for video generation"""
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-pro',
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type='image/jpeg',
                    ),
                    """Analyze this image for AI video generation. Describe:
                    1. Main subject identity and characteristics
                    2. Visual style and artistic elements
                    3. Colors, lighting, and atmosphere
                    4. Suggested motion and animation for video
                    5. Professional video enhancement recommendations
                    
                    Be specific about what you see - this will guide AI video generation."""
                ],
            )
            return response.text if response.text else "Professional content analysis"
        except Exception as e:
            print(f"Image analysis error: {e}")
            return "Dynamic visual content"
    
    def create_video_prompt(self, analysis, customer_request):
        """Create optimized prompt for RunwayML generation"""
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-pro',
                contents=[
                    f"""Image Analysis: {analysis}
                    
                    Customer Request: {customer_request}
                    
                    Create a concise, effective prompt for RunwayML AI video generation that describes:
                    - Realistic motion of the main subject
                    - Camera movement and perspective
                    - Environmental atmosphere
                    - Professional cinematic quality
                    
                    Keep it under 500 characters for optimal AI video generation."""
                ],
            )
            return response.text if response.text else "Professional dynamic video with cinematic motion"
        except Exception as e:
            print(f"Prompt creation error: {e}")
            return "Professional dynamic video with realistic motion and cinematic quality"
    
    def upload_image(self, image_path):
        """Upload customer image to RunwayML"""
        if not self.api_key:
            print("RunwayML API key not available")
            return None
            
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'X-Runway-Version': '2024-11-06'
                }
                
                response = requests.post(
                    f"{self.base_url}/uploads",
                    headers=headers,
                    files=files,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return result.get('id')
                else:
                    print(f"Upload failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            print(f"Upload error: {e}")
            return None
    
    def generate_video(self, image_id, prompt):
        """Generate video using RunwayML Gen-3A Turbo"""
        if not self.api_key or not image_id:
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'X-Runway-Version': '2024-11-06'
            }
            
            data = {
                "promptImage": image_id,
                "promptText": prompt,
                "model": "gen3a_turbo",
                "watermark": False,
                "duration": 10,
                "ratio": "16:9"
            }
            
            response = requests.post(
                f"{self.base_url}/image_to_video",
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code in [200, 201]:
                task = response.json()
                return task.get('id')
            else:
                print(f"Generation failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Generation error: {e}")
            return None
    
    def poll_completion(self, task_id):
        """Poll for video generation completion"""
        if not self.api_key or not task_id:
            return None
            
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        for attempt in range(60):  # 10 minutes max
            try:
                response = requests.get(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    status = response.json()
                    current_status = status.get('status', 'unknown')
                    print(f"Generation status: {current_status}")
                    
                    if current_status == 'SUCCEEDED':
                        outputs = status.get('output', [])
                        if outputs:
                            return outputs[0]
                            
                    elif current_status == 'FAILED':
                        failure = status.get('failure', {})
                        print(f"Generation failed: {failure.get('reason', 'Unknown error')}")
                        return None
                        
                time.sleep(10)
                
            except Exception as e:
                print(f"Polling error: {e}")
                time.sleep(10)
        
        print("Generation timed out")
        return None
    
    def download_video(self, video_url, output_path):
        """Download generated video"""
        try:
            response = requests.get(video_url, stream=True, timeout=300)
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                return True
            else:
                print(f"Download failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Download error: {e}")
            return False

def generate_jeremy_phoenix_runway():
    """Generate Jeremy's Phoenix using RunwayML AI"""
    generator = RunwayMLGenerator()
    
    input_image = 'uploads/projects/9/IMG_1439_20250730_155807.jpeg'
    output_video = 'runway_phoenix_final.mp4'
    customer_request = "Majestic phoenix soaring over Alpena, Michigan"
    
    if not os.path.exists(input_image):
        print("Jeremy's Phoenix image not found")
        return False
    
    print("Analyzing Jeremy's Phoenix image with Gemini AI...")
    analysis = generator.analyze_customer_image(input_image)
    print(f"Analysis complete: {len(analysis)} characters")
    
    print("Creating optimized video generation prompt...")
    prompt = generator.create_video_prompt(analysis, customer_request)
    print(f"Prompt: {prompt[:200]}...")
    
    print("Uploading image to RunwayML...")
    image_id = generator.upload_image(input_image)
    if not image_id:
        print("Failed to upload image")
        return False
    
    print(f"Starting RunwayML generation with image ID: {image_id}")
    task_id = generator.generate_video(image_id, prompt)
    if not task_id:
        print("Failed to start generation")
        return False
    
    print(f"Monitoring generation task: {task_id}")
    video_url = generator.poll_completion(task_id)
    if not video_url:
        print("Generation failed or timed out")
        return False
    
    print(f"Downloading video from: {video_url}")
    success = generator.download_video(video_url, output_video)
    
    if success and os.path.exists(output_video):
        file_size = os.path.getsize(output_video)
        print(f"SUCCESS: RunwayML Phoenix video created: {output_video} ({file_size} bytes)")
        return True
    else:
        print("Failed to download video")
        return False

if __name__ == "__main__":
    generate_jeremy_phoenix_runway()