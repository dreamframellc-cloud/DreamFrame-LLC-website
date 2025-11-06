"""
Proper VEO 3 Client Implementation
Following Google's recommended approach with better timeout handling
"""

import os
import time
import logging
import requests
import base64
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json
from datetime import datetime

class ProperVEO3Client:
    def __init__(self):
        """Initialize proper VEO 3 client with Google Cloud best practices"""
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.model_name = "veo-3.0-generate-001"
        
        # Initialize credentials using existing system
        self.credentials = self._get_credentials()
        self.base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        logging.info("🚀 Proper VEO 3 client initialized with Google Cloud best practices")
    
    def _get_credentials(self):
        """Get service account credentials"""
        credentials_info = {
            'type': 'service_account',
            'project_id': 'dreamframe',
            'private_key_id': '5131dca848e6964f4d5239581bbd4d5a46cbabbf',
            'private_key': '''-----BEGIN PRIVATE KEY-----
MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCKTwFYKTXJQHpz
nXH0oEgzet7BHRIV1QtlRMIRY3XK/ZyNuGuWbs8arnvo5mwYDIbdEbeRC947qsiq
vvoJDI/sthpr1fRwjuEwnm5rDffgvN3qpIFsj3KhNPlXBoOQ/i2rFm2E3bmuHMTR
K8yxq96/ifZ6Rf5zuKCBSJ/KgEflWuGls1tYddGTgQewiESegNJj+A5t3TaO418D
AhZ13WxH+NfW6UcCGILitCsbpSPjVOJTsrePKmo5l8TdZ+XJPrQbXMfbsBU8vOhs
KMw10Vfo9L/jakkNANbnfPNy6vprK27DzYezaoS6+IPalPaEMbu7UyP/Pr1R+CUE
O01GdsWdAgMBAAECggEAGe5Olvgg/rLBUpBcF2x+pPI+NdAsvh2jpZCy3v46DT0n
3zVKrJlpaHv6vNOIxCiDF4sVEtN6Ds9KEKM+Lzik+lE5GmsyiXDsXQhzNMyZYxAd
/jpqDo/Fgt5y+iM9Qw+4wbkyfuTwRWnc58exuMT7vgcQiGO7nXgp1ZtnZBjRgflV
wokYFZusE7TsQ66K3m+B1RF5yicgjAzDvAd/0ADWdRDRlOMIHpoXnndGqTl9fJEw
0S9+Q9b4r7ksdqpViC95qPzyIlKcWnRLmfAYKCfAjIA3+5UxN3b+B2JRaZhvTBVC
N0BisLpYt7ff950seBEEtmIf9FfRTKEUEuQm6Z0MYQKBgQC8p728hQyRLq14dRnF
6SszMWq8ZR8ZM4TLweQq+AyyhJ4+tE6xctN/WGHnPPFvuNv19gpr9+F8jszKWkED
cAhYAKzFvFkLEzopAf/t7mkaAtIM4d/lRTFqUHWUwZI0aYVrNPmTZ0bXzAYOvN3Z
SDbRUvv3646UeuKbLYINX9zB/QKBgQC7rlZ9CHi2UKXpVvKfK0rK7tVJP+trqlDQ
MIBp38bJ0XQDadXCc0Ic+73uNVxAVwYB2qdCgV3921cmX1y8zdrPf1pZd0XGSW/J
fRLJbb/+LnURtr70VpCKTtG5mzqTcMNzwdw2EeU8P4Hjs4Cz8Q3P4ciatuvtA8Q4
0Z6h3WIUIQKBgQC1xEijYu4A1CB/dxQmA8qDwJE+g4+7EFBaoa3dWLGjLvPpJoDL
p/7vK5Do42ccZdhI246fCG5RPKVEMkGBtmfTopLU0exZJ2VaLXsRHCxXy2/myZqX
pFtAO9WORhNAPIs4CAqPY2p2cTVE7eQyfcmTVYlADc2Kcfvz15z+leZ1YQKBgG81
KVhjGavl87lk5NS9wU6n4EfMEUI1pDcIVj7l8xOJAbY4EwpqY0VrQaqRgb06E3wr
xKoan8gZHPXG0duqGrqS2sVicDzDLPL2IpiqaHZDrui1IUcEuBbMB2d0fGv7CEVi
HIsJZYyikOOMbHmzHx0Ly2Mpenhxn+aPBvEgjcohAoGBAKEMHXcfpej4fwuKIlCh
sMPRDbMnebwoEyJMzR8p/Ju2AXWtP6/3jh7G1dMFxmvSdq80jIJeoDR00QuRQzz+
lSepVFr4tzghcWjT9++kdOUcWn9DjQkoBjRmXw31qctpQeq6wZeM1OdI/YzDx18N
/rORf1vl65kWO6XEIlBKDWFO
-----END PRIVATE KEY-----''',
            'client_email': 'dream-frame-robot@dreamframe.iam.gserviceaccount.com',
            'client_id': '112701717089738923417',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token',
            'auth_provider_x509_cert_url': 'https://www.googleapis.com/oauth2/v1/certs',
            'client_x509_cert_url': 'https://www.googleapis.com/robot/v1/metadata/x509/dream-frame-robot%40dreamframe.iam.gserviceaccount.com',
            'universe_domain': 'googleapis.com'
        }
        
        return service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
    
    def _get_access_token(self) -> str:
        """Get fresh access token with proper refresh"""
        req = Request()
        self.credentials.refresh(req)
        return self.credentials.token
    
    def predict_long_running(self, 
                           prompt: str, 
                           image_path: str = None,
                           platform: str = "general",
                           timeout: int = 3600) -> Optional[str]:
        """
        Generate video using proper Google Cloud approach with long-running operation
        
        Args:
            prompt: Video generation prompt
            image_path: Optional source image path
            platform: Target platform (general, instagram, etc.)
            timeout: Maximum timeout in seconds (default 1 hour)
            
        Returns:
            Operation ID if successful, None if failed
        """
        try:
            # Build the proper endpoint URL
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}:predict"
            url = f"{self.base_url}/{endpoint}"
            
            # Optimize prompt for platform
            optimized_prompt = self._optimize_prompt(prompt, platform)
            
            # Build proper VEO 3 request payload
            instances = [{
                "prompt": optimized_prompt,
                "video_config": {
                    "duration": "5s",
                    "aspect_ratio": "16:9" if platform == "general" else "9:16",
                    "quality": "high"
                }
            }]
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = base64.b64encode(f.read()).decode('utf-8')
                    instances[0]["image"] = {
                        "bytes_base64_encoded": image_data,
                        "mime_type": "image/jpeg"
                    }
            
            # Build request payload
            payload = {
                "instances": instances,
                "parameters": {
                    "timeout": f"{timeout}s"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {self._get_access_token()}',
                'Content-Type': 'application/json'
            }
            
            logging.info(f"🎬 Starting VEO 3 long-running prediction")
            logging.info(f"📱 Platform: {platform}, Timeout: {timeout}s")
            
            # Make the long-running prediction request
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=120  # 2 minute request timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract operation ID from response
                operation_id = self._extract_operation_id(result)
                
                if operation_id:
                    logging.info(f"✅ VEO 3 long-running operation started: {operation_id}")
                    return operation_id
                else:
                    logging.warning("⚠️ No operation ID in VEO 3 response")
                    logging.debug(f"Response: {result}")
                    return None
                    
            elif response.status_code == 429:
                logging.warning("⚠️ Rate limited by VEO 3 API")
                return None
                
            else:
                logging.error(f"❌ VEO 3 prediction failed: {response.status_code}")
                logging.error(f"Response: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logging.error(f"⏰ VEO 3 request timed out")
            return None
            
        except Exception as e:
            logging.error(f"❌ VEO 3 prediction error: {e}")
            return None
    
    def get_operation(self, operation_id: str) -> Dict[str, Any]:
        """
        Get operation status using proper Google Cloud operations endpoint
        
        Args:
            operation_id: The operation ID to check
            
        Returns:
            Dictionary with operation status
        """
        try:
            # Use proper operations endpoint
            url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/operations/{operation_id}"
            
            headers = {
                'Authorization': f'Bearer {self._get_access_token()}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # Check if operation is done
                if result.get('done', False):
                    if 'error' in result:
                        return {
                            "status": "failed",
                            "done": True,
                            "error": result['error']
                        }
                    else:
                        # Extract video URL from response
                        video_url = self._extract_video_url(result.get('response', {}))
                        return {
                            "status": "completed",
                            "done": True,
                            "video_url": video_url,
                            "result": result
                        }
                else:
                    # Still running
                    progress = result.get('metadata', {}).get('progressPercentage', 0)
                    return {
                        "status": "running",
                        "done": False,
                        "progress": f"{progress}%"
                    }
                    
            elif response.status_code == 404:
                return {
                    "status": "not_found",
                    "done": True,
                    "error": "Operation not found or expired"
                }
                
            else:
                return {
                    "status": "error",
                    "done": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            logging.error(f"❌ Operation status check failed: {e}")
            return {
                "status": "error",
                "done": False,
                "error": str(e)
            }
    
    def _optimize_prompt(self, prompt: str, platform: str) -> str:
        """Optimize prompt for target platform"""
        base_prompt = prompt.strip()
        
        if platform == "general":
            return f"Create a high-quality cinematic video: {base_prompt}. Professional cinematography, smooth camera movements, detailed textures, 16:9 aspect ratio, 5 seconds duration."
        elif platform == "instagram":
            return f"Create an engaging Instagram story: {base_prompt}. Vertical 9:16 format, vibrant colors, dynamic motion, social media optimized, 5 seconds."
        elif platform == "tiktok":
            return f"Create a viral TikTok video: {base_prompt}. Vertical format, fast-paced action, trending style, eye-catching, 5 seconds."
        else:
            return base_prompt
    
    def _extract_operation_id(self, response: Dict) -> Optional[str]:
        """Extract operation ID from prediction response"""
        # Try common operation ID fields
        for key in ['name', 'operationId', 'operation_id', 'id']:
            if key in response:
                return response[key]
        
        # Check nested metadata
        if 'metadata' in response and 'name' in response['metadata']:
            return response['metadata']['name']
        
        # Check if it's a direct operation response
        if 'operations' in response and len(response['operations']) > 0:
            return response['operations'][0].get('name')
        
        return None
    
    def _extract_video_url(self, response: Dict) -> Optional[str]:
        """Extract video URL from completed operation response"""
        # Try various video URL fields
        for key in ['videoUri', 'video_uri', 'uri', 'url', 'downloadUrl', 'gcsUri']:
            if key in response:
                return response[key]
        
        # Check predictions array
        if 'predictions' in response:
            for prediction in response['predictions']:
                for key in ['videoUri', 'video_uri', 'uri', 'url']:
                    if key in prediction:
                        return prediction[key]
        
        return None

def test_proper_veo3_client():
    """Test the proper VEO 3 client implementation"""
    client = ProperVEO3Client()
    
    # Test with a simple landscape prompt
    test_prompt = "A peaceful mountain landscape with gentle flowing water and soft morning light"
    
    print(f"🧪 Testing proper VEO 3 client")
    print(f"📝 Prompt: {test_prompt}")
    
    # Start long-running prediction
    operation_id = client.predict_long_running(
        prompt=test_prompt,
        platform="general",
        timeout=1800  # 30 minutes
    )
    
    if operation_id:
        print(f"✅ Long-running operation started: {operation_id}")
        
        # Check initial status
        status = client.get_operation(operation_id)
        print(f"📊 Initial status: {status['status']}")
        
        return operation_id
    else:
        print(f"❌ Failed to start long-running operation")
        return None

if __name__ == "__main__":
    test_proper_veo3_client()