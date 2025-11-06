"""
Fix VEO 3 404 Errors by Updating API Endpoints
This script addresses the Google VEO 3 API 404 issues by implementing proper endpoint handling
"""

import requests
import logging
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2 import service_account
import json

class FixedVEO3Client:
    def __init__(self):
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.credentials = None
        self.access_token = None
        
        # Multiple endpoint variations to try
        self.model_endpoints = [
            "veo-3",
            "veo-3.0-generate-001",
            "video-generation"
        ]
        
        logging.info("🔧 Fixed VEO 3 client initialized")
    
    def authenticate(self):
        """Get access token for API calls"""
        try:
            # Load service account credentials
            credentials_info = {
                "type": "service_account",
                "project_id": "dreamframe",
                "private_key_id": "5131dca848e6964f4d5239581bbd4d5a46cbabbf",
                "private_key": """-----BEGIN PRIVATE KEY-----
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
SDbRUvv3646UeuKbLYINX9zB/QQKBgQC7rlZ9CHi2UKXpVvKfK0rK7tVJP+trqlDQ
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
-----END PRIVATE KEY-----""",
                "client_email": "dream-frame-robot@dreamframe.iam.gserviceaccount.com",
                "client_id": "112701717089738923417",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dream-frame-robot%40dreamframe.iam.gserviceaccount.com",
                "universe_domain": "googleapis.com"
            }
            
            self.credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            # Refresh token
            request = Request()
            self.credentials.refresh(request)
            self.access_token = self.credentials.token
            
            logging.info("✅ Authentication successful")
            return True
            
        except Exception as e:
            logging.error(f"❌ Authentication failed: {e}")
            return False
    
    def check_operation_status_direct(self, operation_id):
        """Check operation status using direct REST API calls with multiple endpoints"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        # Extract just the operation ID if full path provided
        if '/' in operation_id:
            operation_id = operation_id.split('/')[-1]
        
        # Try different endpoint variations
        for model_name in self.model_endpoints:
            try:
                url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}/operations/{operation_id}"
                
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                }
                
                logging.info(f"🔍 Trying endpoint: {model_name}")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    logging.info(f"✅ Success with endpoint: {model_name}")
                    return {
                        "status_code": 200,
                        "data": response.json(),
                        "endpoint_used": model_name
                    }
                elif response.status_code == 404:
                    logging.warning(f"⚠️ 404 with endpoint: {model_name}")
                    continue
                else:
                    logging.warning(f"⚠️ Status {response.status_code} with endpoint: {model_name}")
                    
            except Exception as e:
                logging.error(f"❌ Error with endpoint {model_name}: {e}")
                continue
        
        return {
            "status_code": 404,
            "error": "All endpoints returned 404 - operation may not exist or API issue",
            "endpoints_tried": self.model_endpoints
        }
    
    def check_operations_api_direct(self, operation_id):
        """Try using Google Cloud Operations API directly"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        try:
            # Extract operation ID
            if '/' in operation_id:
                operation_id = operation_id.split('/')[-1]
            
            # Use operations API directly
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/operations/{operation_id}"
            
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            logging.info("🔍 Trying direct operations API")
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logging.info("✅ Success with operations API")
                return {
                    "status_code": 200,
                    "data": response.json(),
                    "method": "operations_api"
                }
            else:
                logging.warning(f"⚠️ Operations API returned: {response.status_code}")
                return {
                    "status_code": response.status_code,
                    "error": response.text,
                    "method": "operations_api"
                }
                
        except Exception as e:
            logging.error(f"❌ Operations API error: {e}")
            return None

def test_fix_skeleton_404():
    """Test the fixed endpoint with current skeleton operation"""
    print("🧪 Testing VEO 3 404 Fix")
    print("=" * 30)
    
    client = FixedVEO3Client()
    
    # Current skeleton operation ID
    skeleton_operation = "411841f5-e5fd-4d37-8639-f639f4fa16d0"
    
    print(f"🔍 Testing operation: {skeleton_operation[:8]}...")
    
    # Test 1: Try with different model endpoints
    print("\n1. Testing model endpoints:")
    result1 = client.check_operation_status_direct(skeleton_operation)
    
    if result1:
        if result1['status_code'] == 200:
            print(f"✅ SUCCESS: Found with endpoint {result1.get('endpoint_used')}")
            data = result1['data']
            if data.get('done'):
                print("🎉 Operation completed!")
                if 'response' in data:
                    videos = data['response'].get('videos', [])
                    if videos:
                        print(f"🎥 Video available: {videos[0].get('gcsUri')}")
            else:
                print("🔄 Operation still in progress")
        else:
            print(f"❌ All endpoints failed: {result1['error']}")
    
    # Test 2: Try operations API directly
    print("\n2. Testing operations API:")
    result2 = client.check_operations_api_direct(skeleton_operation)
    
    if result2:
        if result2['status_code'] == 200:
            print("✅ SUCCESS: Operations API working")
        else:
            print(f"❌ Operations API failed: {result2['status_code']}")
    
    return result1, result2

if __name__ == "__main__":
    # Test the fix
    test_fix_skeleton_404()