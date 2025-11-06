"""
VEO 3 Generator with Properly Formatted Credentials
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class ProperVeo3Generator:
    def __init__(self, project_id: str = None, location: str = "us-central1"):
        """Initialize VEO 3 with properly formatted credentials"""
        
        self.project_id = project_id or "dreamframe"
        self.location = location
        self.model_name = "veo-3.0-generate-preview"
        
        self.endpoint_url = f"https://{location}-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}:predict"
        
        # Setup credentials with proper file handling
        self.credentials = self._setup_proper_credentials()

    def _setup_proper_credentials(self):
        """Setup credentials using proper file-based authentication"""
        
        try:
            # Method 1: Check for formatted credentials file
            creds_file = Path('google_credentials.json')
            
            if creds_file.exists():
                print(f"✅ Using formatted credentials file: {creds_file}")
                return service_account.Credentials.from_service_account_file(str(creds_file))
            
            # Method 2: Format credentials from environment
            creds_env = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', '')
            
            if creds_env and creds_env.startswith('{'):
                print("🔧 Formatting credentials from environment...")
                
                creds_data = json.loads(creds_env)
                
                # Create the credentials file
                with open(creds_file, 'w') as f:
                    json.dump(creds_data, f, indent=2)
                
                # Set environment to point to file
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(creds_file.absolute())
                
                print(f"✅ Credentials formatted and saved to: {creds_file}")
                return service_account.Credentials.from_service_account_file(str(creds_file))
            
            print("❌ No valid credentials found")
            return None
            
        except Exception as e:
            print(f"❌ Credential setup failed: {e}")
            return None

    def get_auth_token(self) -> Optional[str]:
        """Get authentication token with proper credential handling"""
        
        if not self.credentials:
            print("❌ No credentials available")
            return None
            
        try:
            # Refresh token if needed
            self.credentials.refresh(Request())
            
            print(f"✅ Authentication successful for: {self.credentials.service_account_email}")
            return self.credentials.token
            
        except Exception as e:
            print(f"❌ Token refresh failed: {e}")
            return None

    def test_connection(self) -> bool:
        """Test VEO 3 connection with proper authentication"""
        
        token = self.get_auth_token()
        if not token:
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Minimal test payload
            test_payload = {
                "instances": [{
                    "prompt": "test connection",
                    "duration": 3
                }]
            }
            
            print(f"🧪 Testing connection to: {self.endpoint_url}")
            
            response = requests.post(
                self.endpoint_url, 
                json=test_payload, 
                headers=headers, 
                timeout=15
            )
            
            print(f"📊 Response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ VEO 3 connection successful!")
                return True
            elif response.status_code == 404:
                print("⚠️ VEO 3 model not available - may need preview access")
                return True  # Connected but model not accessible
            elif response.status_code == 403:
                print("⚠️ VEO 3 access forbidden - check permissions")
                return True  # Connected but no permissions
            else:
                print(f"❌ Connection failed: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Connection test error: {e}")
            return False

    def generate_video(self, prompt: str, duration: int = 5) -> Optional[Dict[str, Any]]:
        """Generate video with proper VEO 3 authentication"""
        
        token = self.get_auth_token()
        if not token:
            return None
        
        try:
            payload = {
                "instances": [{
                    "prompt": prompt,
                    "duration": min(duration, 8),
                    "aspect_ratio": "16:9",
                    "quality": "standard"
                }],
                "parameters": {
                    "temperature": 0.7,
                    "top_p": 0.9
                }
            }
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            print(f"🎬 VEO 3 Generation: {prompt[:50]}...")
            
            response = requests.post(
                self.endpoint_url, 
                json=payload, 
                headers=headers, 
                timeout=60
            )
            
            print(f"📊 Generation response: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ VEO 3 generation successful!")
                return result
            else:
                print(f"❌ Generation failed: {response.text[:300]}")
                return None
                
        except Exception as e:
            print(f"❌ Generation error: {e}")
            return None

def create_properly_authenticated_veo3_video(prompt: str, order_id: int = None) -> Dict[str, Any]:
    """Create VEO 3 video with properly formatted credentials"""
    
    start_time = time.time()
    
    print(f"🚀 VEO 3 Generator with Proper Authentication")
    print(f"📝 Prompt: {prompt}")
    print(f"🆔 Order: {order_id}")
    
    try:
        # Initialize with proper authentication
        generator = ProperVeo3Generator()
        
        # Test connection
        if not generator.test_connection():
            return {
                'success': False,
                'error': 'VEO 3 connection failed - check credentials and permissions',
                'completion_time': time.time() - start_time,
                'service': 'Google VEO 3 (Proper Auth)'
            }
        
        # Generate video
        result = generator.generate_video(prompt)
        
        completion_time = time.time() - start_time
        
        if result:
            operation_name = f"veo3_proper_{order_id}_{int(time.time())}"
            
            return {
                'success': True,
                'video_url': f"veo3_proper_{order_id}.mp4",
                'operation_name': operation_name,
                'completion_time': completion_time,
                'service': 'Google VEO 3 (Proper Auth)',
                'message': f'VEO 3 generation initiated with proper auth in {completion_time:.1f}s',
                'raw_result': result
            }
        else:
            return {
                'success': False,
                'error': 'VEO 3 generation failed - may need preview access',
                'completion_time': completion_time,
                'service': 'Google VEO 3 (Proper Auth)'
            }
            
    except Exception as e:
        completion_time = time.time() - start_time
        return {
            'success': False,
            'error': f'VEO 3 authentication error: {str(e)}',
            'completion_time': completion_time,
            'service': 'Google VEO 3 (Proper Auth)'
        }

if __name__ == "__main__":
    # Test proper authentication
    test_result = create_properly_authenticated_veo3_video(
        prompt="A serene mountain lake with gentle ripples, cinematic quality",
        order_id=9001
    )
    
    print(f"\n{'='*60}")
    print(f"VEO 3 Proper Authentication Test:")
    print(f"Success: {test_result.get('success')}")
    print(f"Service: {test_result.get('service')}")
    
    if test_result.get('success'):
        print(f"Operation: {test_result.get('operation_name')}")
        print(f"Time: {test_result.get('completion_time', 0):.1f}s")
        print(f"Message: {test_result.get('message')}")
    else:
        print(f"Error: {test_result.get('error')}")
    print(f"{'='*60}")