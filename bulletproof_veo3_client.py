"""
Bulletproof VEO 3 Client with Google API Core Retry Decorators
Implements comprehensive retry logic for maximum reliability
"""

import os
import time
import logging
import requests
import base64
from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.api_core import retry
from google.api_core import exceptions
import json
from datetime import datetime

class BulletproofVEO3Client:
    def __init__(self):
        """Initialize bulletproof VEO 3 client with comprehensive retry mechanisms"""
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.model_name = "veo-3.0-generate-001"
        
        # Initialize credentials
        self.credentials = self._get_credentials()
        self.base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        # Configure retry policies
        self.default_retry = retry.Retry(
            predicate=retry.if_exception_type(
                exceptions.DeadlineExceeded,
                exceptions.ServiceUnavailable,
                exceptions.InternalServerError,
                exceptions.TooManyRequests
            ),
            initial=1.0,
            maximum=60.0,
            multiplier=2.0,
            deadline=300.0  # 5 minutes total retry time
        )
        
        self.operation_retry = retry.Retry(
            predicate=retry.if_exception_type(
                exceptions.DeadlineExceeded,
                exceptions.NotFound,
                exceptions.ServiceUnavailable
            ),
            initial=2.0,
            maximum=120.0,
            multiplier=1.5,
            deadline=180.0  # 3 minutes for operation checks
        )
        
        logging.info("🛡️ Bulletproof VEO 3 client initialized with comprehensive retry mechanisms")
    
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
    
    @retry.Retry(
        predicate=retry.if_exception_type(
            exceptions.DeadlineExceeded,
            exceptions.ServiceUnavailable,
            exceptions.InternalServerError
        ),
        initial=1.0,
        maximum=30.0,
        multiplier=2.0
    )
    def _get_access_token(self) -> str:
        """Get fresh access token with retry logic"""
        req = Request()
        self.credentials.refresh(req)
        return self.credentials.token
    
    def generate_video_bulletproof(self, 
                                 prompt: str, 
                                 image_path: str = None,
                                 platform: str = "general",
                                 timeout: int = 3600) -> Optional[str]:
        """
        Generate video with bulletproof retry mechanisms
        
        Args:
            prompt: Video generation prompt
            image_path: Optional source image path
            platform: Target platform (general, instagram, etc.)
            timeout: Maximum timeout in seconds
            
        Returns:
            Operation ID if successful, None if failed
        """
        return self._generate_with_retry(prompt, image_path, platform, timeout)
    
    @retry.Retry(
        predicate=retry.if_exception_type(
            exceptions.DeadlineExceeded,
            exceptions.ServiceUnavailable,
            exceptions.InternalServerError,
            exceptions.TooManyRequests
        ),
        initial=2.0,
        maximum=120.0,
        multiplier=1.5,
        deadline=600.0  # 10 minutes total for generation attempts
    )
    def _generate_with_retry(self, prompt: str, image_path: str, platform: str, timeout: int) -> Optional[str]:
        """Internal generation method with comprehensive retry"""
        try:
            # Build endpoint URL
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}:predict"
            url = f"{self.base_url}/{endpoint}"
            
            # Optimize prompt for platform
            optimized_prompt = self._optimize_prompt(prompt, platform)
            
            # Build payload
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
            
            logging.info(f"🎬 Bulletproof VEO 3 generation attempt")
            logging.info(f"📱 Platform: {platform}, Timeout: {timeout}s")
            
            # Make request with timeout
            response = requests.post(
                url, 
                json=payload, 
                headers=headers,
                timeout=180  # 3 minute request timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                operation_id = self._extract_operation_id(result)
                
                if operation_id:
                    logging.info(f"✅ Bulletproof VEO 3 operation started: {operation_id}")
                    return operation_id
                else:
                    logging.warning("⚠️ No operation ID in response")
                    return None
                    
            elif response.status_code == 429:
                # Rate limiting - let retry decorator handle this
                raise exceptions.TooManyRequests("Rate limited by VEO 3 API")
                
            elif response.status_code >= 500:
                # Server errors - let retry decorator handle this
                raise exceptions.InternalServerError(f"Server error: {response.status_code}")
                
            else:
                logging.error(f"❌ VEO 3 generation failed: {response.status_code}")
                return None
                
        except (exceptions.DeadlineExceeded, exceptions.ServiceUnavailable, 
                exceptions.InternalServerError, exceptions.TooManyRequests):
            # Let retry decorator handle these
            raise
        except Exception as e:
            logging.error(f"❌ Bulletproof VEO 3 generation error: {e}")
            return None
    
    @retry.Retry(
        predicate=retry.if_exception_type(
            exceptions.DeadlineExceeded,
            exceptions.NotFound,
            exceptions.ServiceUnavailable
        ),
        initial=2.0,
        maximum=60.0,
        multiplier=1.5,
        deadline=300.0  # 5 minutes for operation checks
    )
    def check_operation_bulletproof(self, operation_id: str) -> Dict[str, Any]:
        """
        Check operation status with bulletproof retry logic
        
        Args:
            operation_id: The operation ID to check
            
        Returns:
            Dictionary with operation status
        """
        try:
            # Build operation URL
            url = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}/operations/{operation_id}"
            
            headers = {
                'Authorization': f'Bearer {self._get_access_token()}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=90)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('done', False):
                    if 'error' in result:
                        return {
                            "status": "failed",
                            "done": True,
                            "error": result['error']
                        }
                    else:
                        video_url = self._extract_video_url(result.get('response', {}))
                        return {
                            "status": "completed",
                            "done": True,
                            "video_url": video_url,
                            "result": result
                        }
                else:
                    progress = result.get('metadata', {}).get('progressPercentage', 0)
                    return {
                        "status": "running",
                        "done": False,
                        "progress": f"{progress}%"
                    }
                    
            elif response.status_code == 404:
                # Not found - let retry decorator handle this initially, then give up
                raise exceptions.NotFound("Operation not found")
                
            elif response.status_code >= 500:
                # Server errors - let retry decorator handle this
                raise exceptions.ServiceUnavailable(f"Service error: {response.status_code}")
                
            else:
                return {
                    "status": "error",
                    "done": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except (exceptions.DeadlineExceeded, exceptions.NotFound, exceptions.ServiceUnavailable):
            # Let retry decorator handle these, but catch final failure
            raise
        except Exception as e:
            logging.error(f"❌ Bulletproof operation check error: {e}")
            return {
                "status": "error",
                "done": False,
                "error": str(e)
            }
    
    def _optimize_prompt(self, prompt: str, platform: str) -> str:
        """Optimize prompt for target platform"""
        base_prompt = prompt.strip()
        
        if platform == "general":
            return f"Create a high-quality cinematic video: {base_prompt}. Professional cinematography, smooth camera movements, detailed textures, 16:9 aspect ratio, 5 seconds."
        elif platform == "instagram":
            return f"Create an engaging Instagram story: {base_prompt}. Vertical 9:16 format, vibrant colors, dynamic motion, social media optimized, 5 seconds."
        elif platform == "tiktok":
            return f"Create a viral TikTok video: {base_prompt}. Vertical format, fast-paced action, trending style, eye-catching, 5 seconds."
        else:
            return base_prompt
    
    def _extract_operation_id(self, response: Dict) -> Optional[str]:
        """Extract operation ID from response"""
        for key in ['name', 'operationId', 'operation_id', 'id']:
            if key in response:
                return response[key]
        
        if 'metadata' in response and 'name' in response['metadata']:
            return response['metadata']['name']
        
        if 'operations' in response and len(response['operations']) > 0:
            return response['operations'][0].get('name')
        
        return None
    
    def _extract_video_url(self, response: Dict) -> Optional[str]:
        """Extract video URL from response"""
        for key in ['videoUri', 'video_uri', 'uri', 'url', 'downloadUrl', 'gcsUri']:
            if key in response:
                return response[key]
        
        if 'predictions' in response:
            for prediction in response['predictions']:
                for key in ['videoUri', 'video_uri', 'uri', 'url']:
                    if key in prediction:
                        return prediction[key]
        
        return None

def test_bulletproof_client():
    """Test the bulletproof VEO 3 client"""
    client = BulletproofVEO3Client()
    
    # Test with a simple prompt
    test_prompt = "A calm ocean scene with gentle waves and soft lighting"
    
    print(f"🧪 Testing bulletproof VEO 3 client")
    print(f"📝 Prompt: {test_prompt}")
    
    # Start generation with comprehensive retry
    operation_id = client.generate_video_bulletproof(
        prompt=test_prompt,
        platform="general",
        timeout=1800  # 30 minutes
    )
    
    if operation_id:
        print(f"✅ Bulletproof generation started: {operation_id}")
        
        # Check initial status with retry
        try:
            status = client.check_operation_bulletproof(operation_id)
            print(f"📊 Status: {status['status']}")
        except exceptions.NotFound:
            print(f"⚠️ Operation not found (expected with current API issues)")
        
        return operation_id
    else:
        print(f"❌ Bulletproof generation failed after all retries")
        return None

if __name__ == "__main__":
    test_bulletproof_client()