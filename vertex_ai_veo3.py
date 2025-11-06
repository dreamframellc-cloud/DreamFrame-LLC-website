#!/usr/bin/env python3
"""
Authentic Google Vertex AI VEO 3 Integration
Direct REST API access to VEO 3 for professional video generation
Competes directly with Kling AI using authentic Google VEO 3
"""

import os
import time
import requests
import json
import base64
from typing import Optional, Dict, Any

class VertexAIVEO3:
    """Authentic VEO 3 video generation using Google Vertex AI"""
    
    def __init__(self, project_id: str = None):
        """Initialize Vertex AI VEO 3 system"""
        self.project_id = project_id or os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT_ID required for Vertex AI access")
        
        self.credentials_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if not self.credentials_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS required for authentication")
        
        self.location = "us-central1"
        
        # VEO 3 models available on Vertex AI
        self.available_models = {
            'veo-3.0-generate-001': 'Latest VEO 3 with audio generation',
            'veo-3.0-fast-generate-001': 'VEO 3 Fast for quick generation',
            'veo-2.0-generate-001': 'Previous VEO 2 model'
        }
        
        print(f"Vertex AI VEO 3 initialized for project: {self.project_id}")
        print("Authentic VEO 3 access - no fallbacks, professional quality")
    
    def _get_access_token(self) -> str:
        """Get Google Cloud access token using service account"""
        import subprocess
        import json
        
        try:            
            # Use service account for authentication
            if self.credentials_path:
                # Set the service account credentials
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.credentials_path
                
                # Get access token using gcloud auth
                result = subprocess.run([
                    'gcloud', 'auth', 'application-default', 'print-access-token'
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    print(f"gcloud auth failed: {result.stderr}")
                    
                    # Try alternative method using service account key directly
                    if os.path.exists(self.credentials_path):
                        with open(self.credentials_path, 'r') as f:
                            service_account = json.load(f)
                        
                        # Use requests-oauthlib for JWT token
                        return self._get_jwt_token(service_account)
                    
            raise Exception("Could not get access token")
            
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            raise
    
    def _get_jwt_token(self, service_account: dict) -> str:
        """Generate JWT token from service account"""
        import jwt
        import datetime
        
        now = datetime.datetime.utcnow()
        
        payload = {
            'iss': service_account['client_email'],
            'scope': 'https://www.googleapis.com/auth/cloud-platform',
            'aud': 'https://oauth2.googleapis.com/token',
            'iat': now,
            'exp': now + datetime.timedelta(hours=1)
        }
        
        token = jwt.encode(payload, service_account['private_key'], algorithm='RS256')
        
        # Exchange JWT for access token
        response = requests.post('https://oauth2.googleapis.com/token', data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': token
        })
        
        if response.status_code == 200:
            return response.json()['access_token']
        else:
            raise Exception(f"Token exchange failed: {response.text}")
    
    def generate_video_from_text(self, 
                                prompt: str,
                                model: str = "veo-3.0-generate-001",
                                duration_seconds: int = 8,
                                resolution: str = "1080p",
                                generate_audio: bool = True,
                                aspect_ratio: str = "16:9") -> Optional[Dict[str, Any]]:
        """Generate video from text prompt using authentic VEO 3"""
        
        print(f"Generating VEO 3 video: {prompt[:50]}...")
        print(f"Model: {model}, Duration: {duration_seconds}s, Resolution: {resolution}")
        
        # Vertex AI VEO 3 endpoint
        endpoint = (f"https://{self.location}-aiplatform.googleapis.com/v1/"
                   f"projects/{self.project_id}/locations/{self.location}/"
                   f"publishers/google/models/{model}:predictLongRunning")
        
        # VEO 3 request payload
        payload = {
            "instances": [{
                "prompt": prompt
            }],
            "parameters": {
                "aspectRatio": aspect_ratio,
                "durationSeconds": duration_seconds,
                "enhancePrompt": True,
                "generateAudio": generate_audio,
                "resolution": resolution,
                "sampleCount": 1,
                "personGeneration": "allow_adult"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id
        }
        
        try:
            print("Sending VEO 3 generation request to Vertex AI...")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ VEO 3 generation request accepted")
                
                # VEO 3 uses long-running operations
                if 'name' in result:
                    operation_name = result['name']
                    print(f"Operation ID: {operation_name}")
                    
                    # Poll for completion
                    return self._poll_operation(operation_name)
                else:
                    print("❌ No operation name in response")
                    return None
            else:
                print(f"❌ VEO 3 request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ VEO 3 generation error: {str(e)}")
            return None
    
    def generate_video_from_image(self,
                                 image_path: str,
                                 prompt: str,
                                 model: str = "veo-3.0-generate-001",
                                 duration_seconds: int = 8,
                                 resolution: str = "1080p",
                                 generate_audio: bool = True) -> Optional[Dict[str, Any]]:
        """Generate video from image + text using authentic VEO 3"""
        
        print(f"Generating VEO 3 video from image: {image_path}")
        print(f"Prompt: {prompt[:50]}...")
        
        # Read and encode image
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            # Determine mime type
            mime_type = "image/jpeg"
            if image_path.lower().endswith('.png'):
                mime_type = "image/png"
                
        except Exception as e:
            print(f"❌ Error reading image: {str(e)}")
            return None
        
        # Vertex AI VEO 3 endpoint
        endpoint = (f"https://{self.location}-aiplatform.googleapis.com/v1/"
                   f"projects/{self.project_id}/locations/{self.location}/"
                   f"publishers/google/models/{model}:predictLongRunning")
        
        # VEO 3 image-to-video request payload
        payload = {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": image_base64,
                    "mimeType": mime_type
                }
            }],
            "parameters": {
                "aspectRatio": "16:9",
                "durationSeconds": duration_seconds,
                "enhancePrompt": True,
                "generateAudio": generate_audio,
                "resolution": resolution,
                "sampleCount": 1,
                "personGeneration": "allow_adult"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id
        }
        
        try:
            print("Sending VEO 3 image-to-video request to Vertex AI...")
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ VEO 3 image-to-video generation request accepted")
                
                if 'name' in result:
                    operation_name = result['name']
                    print(f"Operation ID: {operation_name}")
                    
                    # Poll for completion
                    return self._poll_operation(operation_name)
                else:
                    print("❌ No operation name in response")
                    return None
            else:
                print(f"❌ VEO 3 image-to-video request failed: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ VEO 3 image-to-video generation error: {str(e)}")
            return None
    
    def _poll_operation(self, operation_name: str, max_wait_time: int = 300) -> Optional[Dict[str, Any]]:
        """Poll VEO 3 long-running operation for completion"""
        
        print(f"Polling VEO 3 operation: {operation_name}")
        
        # Operation polling endpoint
        poll_endpoint = f"https://{self.location}-aiplatform.googleapis.com/v1/{operation_name}"
        
        headers = {
            "Authorization": f"Bearer {self._get_access_token()}",
            "X-Goog-User-Project": self.project_id
        }
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            try:
                response = requests.get(poll_endpoint, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('done', False):
                        print("✅ VEO 3 generation completed!")
                        
                        if 'response' in result:
                            return self._process_veo3_result(result['response'])
                        elif 'error' in result:
                            print(f"❌ VEO 3 generation error: {result['error']}")
                            return None
                    else:
                        # Still processing
                        progress = result.get('metadata', {}).get('progressPercentage', 0)
                        print(f"🔄 VEO 3 generation in progress: {progress}%")
                        time.sleep(10)
                else:
                    print(f"❌ Polling failed: {response.status_code}")
                    time.sleep(10)
                    
            except Exception as e:
                print(f"❌ Polling error: {str(e)}")
                time.sleep(10)
        
        print("⏰ VEO 3 generation timeout")
        return None
    
    def _process_veo3_result(self, response_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process VEO 3 generation result and save video"""
        
        try:
            predictions = response_data.get('predictions', [])
            
            if not predictions:
                print("❌ No predictions in VEO 3 response")
                return None
            
            prediction = predictions[0]
            
            # VEO 3 video can be in bytesBase64Encoded or gcsUri
            if 'video' in prediction:
                video_data = prediction['video']
                
                if 'bytesBase64Encoded' in video_data:
                    # Decode base64 video
                    video_bytes = base64.b64decode(video_data['bytesBase64Encoded'])
                    
                    # Save VEO 3 video
                    timestamp = int(time.time())
                    output_path = f"static/completed_videos/veo3_authentic_{timestamp}.mp4"
                    
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(video_bytes)
                    
                    print(f"✅ VEO 3 video saved: {output_path}")
                    print(f"📊 Video size: {len(video_bytes) / 1024 / 1024:.1f}MB")
                    
                    return {
                        'success': True,
                        'video_path': output_path,
                        'video_size_mb': len(video_bytes) / 1024 / 1024,
                        'authentic_veo3': True,
                        'competitive_with_kling': True
                    }
                
                elif 'gcsUri' in video_data:
                    gcs_uri = video_data['gcsUri']
                    print(f"✅ VEO 3 video available at: {gcs_uri}")
                    
                    return {
                        'success': True,
                        'gcs_uri': gcs_uri,
                        'authentic_veo3': True,
                        'competitive_with_kling': True
                    }
            
            print("❌ No video data in VEO 3 prediction")
            return None
            
        except Exception as e:
            print(f"❌ Error processing VEO 3 result: {str(e)}")
            return None
    
    def test_veo3_access(self) -> bool:
        """Test authentic VEO 3 access on Vertex AI"""
        
        print("Testing authentic VEO 3 access on Vertex AI...")
        
        # Simple test prompt
        test_prompt = "A professional logo animation with smooth transitions"
        
        result = self.generate_video_from_text(
            prompt=test_prompt,
            model="veo-3.0-fast-generate-001",  # Use fast model for testing
            duration_seconds=8,
            resolution="720p"
        )
        
        if result and result.get('success'):
            print("🎉 AUTHENTIC VEO 3 ACCESS CONFIRMED!")
            print("Ready for professional customer video generation")
            return True
        else:
            print("⚠️ VEO 3 access needs configuration")
            return False

def test_vertex_ai_veo3():
    """Test Vertex AI VEO 3 integration"""
    
    print("Testing Authentic Vertex AI VEO 3 Integration")
    print("="*50)
    
    try:
        # Initialize VEO 3 system
        veo3 = VertexAIVEO3()
        
        # Test access
        access_confirmed = veo3.test_veo3_access()
        
        if access_confirmed:
            print("\n🎉 VERTEX AI VEO 3 READY FOR CUSTOMER GENERATION")
            print("Authentic VEO 3 integration - competitive with Kling AI")
        else:
            print("\n⚠️ VEO 3 setup needs Google Cloud project configuration")
            print("User needs to provide Google Cloud project ID for Vertex AI access")
        
        return access_confirmed
        
    except Exception as e:
        print(f"❌ Vertex AI VEO 3 test error: {str(e)}")
        return False

if __name__ == "__main__":
    test_vertex_ai_veo3()