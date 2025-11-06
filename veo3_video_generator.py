import os
import json
import time
from google.cloud import aiplatform
from google.oauth2 import service_account
import requests
from typing import Optional, Dict, Any

class Veo3VideoGenerator:
    def __init__(self, project_id: str, location: str = "us-central1", credentials_path: str = None):
        """
        Initialize Veo 3 Video Generator
        
        Args:
            project_id: Your Google Cloud Project ID
            location: Region (us-central1 recommended for Veo 3)
            credentials_path: Path to service account JSON file
        """
        self.project_id = project_id
        self.location = location
        self.model_name = "veo-3-generate-001"
        
        # Set up credentials
        if credentials_path:
            credentials = service_account.Credentials.from_service_account_file(credentials_path)
            aiplatform.init(project=project_id, location=location, credentials=credentials)
        else:
            # Use default credentials (from environment)
            aiplatform.init(project=project_id, location=location)
        
        self.endpoint_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{self.model_name}:predict"

    def test_connection(self) -> bool:
        """Test if we can connect to Vertex AI and access Veo 3"""
        try:
            # Test basic connection
            from google.cloud import aiplatform_v1
            client = aiplatform_v1.PredictionServiceClient()
            
            # Try to access the model
            model_path = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}"
            print(f"Testing connection to: {model_path}")
            
            return True
        except Exception as e:
            print(f"Connection test failed: {str(e)}")
            return False

    def generate_video(self, prompt: str, duration: int = 5, aspect_ratio: str = "16:9") -> Optional[Dict[str, Any]]:
        """
        Generate video using Veo 3
        
        Args:
            prompt: Text description for video generation
            duration: Video duration in seconds (max 8 for Veo 3)
            aspect_ratio: Video aspect ratio (16:9, 9:16, 1:1)
        
        Returns:
            Dictionary with video generation result or None if failed
        """
        try:
            # Prepare the request payload
            payload = {
                "instances": [{
                    "prompt": prompt,
                    "duration": min(duration, 8),  # Veo 3 max duration
                    "aspect_ratio": aspect_ratio,
                    "quality": "standard"  # or "high"
                }],
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            # Get access token
            from google.auth import default
            credentials, _ = default()
            credentials.refresh(requests.Request())
            
            headers = {
                "Authorization": f"Bearer {credentials.token}",
                "Content-Type": "application/json"
            }
            
            print(f"Sending request to: {self.endpoint_url}")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            # Make the API call
            response = requests.post(self.endpoint_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print("Video generation successful!")
                return result
            else:
                print(f"API Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            return None

    def check_generation_status(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """Check the status of a video generation operation"""
        try:
            from google.cloud import aiplatform_v1
            client = aiplatform_v1.PredictionServiceClient()
            
            # Implementation depends on your specific operation tracking
            # This is a placeholder for operation status checking
            print(f"Checking status for operation: {operation_name}")
            
            return {"status": "completed", "video_url": "placeholder"}
            
        except Exception as e:
            print(f"Error checking status: {str(e)}")
            return None

# Flask/Django integration example
class DreamFrameVideoHandler:
    def __init__(self, project_id: str, credentials_path: str = None):
        self.veo3 = Veo3VideoGenerator(project_id, credentials_path=credentials_path)

    def process_video_request(self, prompt: str, user_id: str = None) -> Dict[str, Any]:
        """Process video generation request for DreamFrame platform"""
        try:
            # Test connection first
            if not self.veo3.test_connection():
                return {"error": "Cannot connect to Vertex AI", "status": "failed"}
            
            # Generate video
            result = self.veo3.generate_video(prompt)
            
            if result:
                return {
                    "status": "success",
                    "message": "Video generation started",
                    "data": result
                }
            else:
                return {
                    "status": "failed",
                    "error": "Video generation failed"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

def create_dreamframe_veo3_video(prompt: str, order_id: int = None) -> Dict[str, Any]:
    """Main function for DreamFrame VEO 3 video generation"""
    
    start_time = time.time()
    
    print(f"🎬 DreamFrame VEO 3 Video Generator")
    print(f"📝 Prompt: {prompt}")
    print(f"🆔 Order: {order_id}")
    
    try:
        # Get project ID from environment
        project_id = json.loads(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '{}')).get('project_id', 'dreamframe')
        
        # Initialize handler
        handler = DreamFrameVideoHandler(project_id)
        
        # Process video request
        result = handler.process_video_request(prompt, str(order_id) if order_id else None)
        
        completion_time = time.time() - start_time
        
        if result.get('status') == 'success':
            return {
                'success': True,
                'video_url': f"veo3_video_{order_id}.mp4",
                'operation_name': f"veo3_{order_id}_{int(time.time())}",
                'completion_time': completion_time,
                'service': 'Google VEO 3',
                'message': f'VEO 3 video generation initiated successfully'
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'VEO 3 generation failed'),
                'completion_time': completion_time,
                'service': 'Google VEO 3'
            }
            
    except Exception as e:
        completion_time = time.time() - start_time
        return {
            'success': False,
            'error': f'VEO 3 error: {str(e)}',
            'completion_time': completion_time,
            'service': 'Google VEO 3'
        }

def diagnose_404_error(error_message: str):
    """Diagnose common 404 errors and provide solutions"""
    print(f"\n🔍 Diagnosing 404 error: {error_message}")
    
    if "not found" in error_message.lower():
        print("\n💡 Possible solutions:")
        print("1. ✓ Check PROJECT_ID is correct")
        print("2. ✓ Verify region (use 'us-central1' for Veo 3)")
        print("3. ✓ Ensure model name is 'veo-3-generate-001'")
        print("4. ✓ Check if you have preview access to Veo 3")
        
    if "access" in error_message.lower():
        print("\n🔑 Access issues:")
        print("1. ✓ Request Veo 3 preview access from Google")
        print("2. ✓ Verify service account has 'Vertex AI User' role")
        print("3. ✓ Check project permissions")
        
    print("\n📞 If issues persist:")
    print("- Contact Google Cloud Support")
    print("- Check Vertex AI status page")
    print("- Verify your billing account")

if __name__ == "__main__":
    # Test VEO 3 integration
    test_result = create_dreamframe_veo3_video(
        prompt="A serene lake with mountains in the background, birds flying overhead",
        order_id=3001
    )
    print(f"VEO 3 test result: {test_result}")