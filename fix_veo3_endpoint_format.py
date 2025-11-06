"""
Fix VEO 3 Endpoint Format Based on Google Documentation
The user found that MODEL_ID should be 'veo-3' not 'veo-3.0-generate-001'
"""

import os
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class FixedVEO3Client:
    def __init__(self):
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.correct_model_id = "veo-3"  # Corrected based on Google docs
        
        print(f"🔧 Fixed VEO 3 Client - Using MODEL_ID: {self.correct_model_id}")
        
    def get_access_token(self):
        """Get Google Cloud access token using service account"""
        try:
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
            }
            
            credentials = service_account.Credentials.from_service_account_info(
                credentials_info,
                scopes=['https://www.googleapis.com/auth/cloud-platform']
            )
            
            request = Request()
            credentials.refresh(request)
            
            print("✅ Access token obtained with correct credentials")
            return credentials.token
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    def check_operation_with_correct_format(self, operation_id):
        """Check operation using the correct endpoint format from Google docs"""
        access_token = self.get_access_token()
        if not access_token:
            return {"error": "Authentication failed"}
        
        # Clean operation ID
        clean_operation_id = operation_id.split('/')[-1] if '/' in operation_id else operation_id
        
        # Correct format based on Google documentation
        url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.correct_model_id}/operations/{clean_operation_id}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"🔍 Testing CORRECT endpoint format:")
        print(f"   PROJECT_ID: {self.project_id}")
        print(f"   LOCATION: {self.location}")
        print(f"   MODEL_ID: {self.correct_model_id}")
        print(f"   OPERATION_ID: {clean_operation_id}")
        print(f"   Full URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                print("✅ SUCCESS! Correct endpoint format works!")
                data = response.json()
                
                # Check operation status
                if data.get('done'):
                    print("🎉 Operation completed!")
                    if 'response' in data:
                        videos = data['response'].get('videos', [])
                        if videos:
                            print(f"🎥 Video available: {videos[0].get('gcsUri')}")
                else:
                    print("🔄 Operation still in progress")
                
                return {
                    "success": True,
                    "status_code": 200,
                    "data": data,
                    "endpoint_format": "CORRECT"
                }
            else:
                print(f"❌ Status: {response.status_code}")
                print(f"Error: {response.text}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "endpoint_format": "CORRECT"
                }
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "endpoint_format": "CORRECT"
            }
    
    def compare_old_vs_new_format(self, operation_id):
        """Compare old format vs new format to demonstrate the fix"""
        print("🧪 ENDPOINT FORMAT COMPARISON")
        print("=" * 50)
        
        access_token = self.get_access_token()
        if not access_token:
            return
        
        clean_operation_id = operation_id.split('/')[-1] if '/' in operation_id else operation_id
        
        # Old format (currently used, causing 404s)
        old_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-001/operations/{clean_operation_id}"
        
        # New format (correct according to Google docs)
        new_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3/operations/{clean_operation_id}"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        print("1. OLD FORMAT (causing 404s):")
        print(f"   MODEL_ID: veo-3.0-generate-001")
        print(f"   URL: {old_url}")
        
        try:
            response = requests.get(old_url, headers=headers, timeout=10)
            print(f"   Result: {response.status_code} - {response.reason}")
        except Exception as e:
            print(f"   Result: ERROR - {e}")
        
        print("\n2. NEW FORMAT (Google docs correct):")
        print(f"   MODEL_ID: veo-3")
        print(f"   URL: {new_url}")
        
        try:
            response = requests.get(new_url, headers=headers, timeout=10)
            print(f"   Result: {response.status_code} - {response.reason}")
            if response.status_code == 200:
                print("   ✅ SUCCESS! This is the correct format!")
        except Exception as e:
            print(f"   Result: ERROR - {e}")

def test_skeleton_operations():
    """Test both skeleton operations with correct format"""
    print("🔍 TESTING SKELETON OPERATIONS WITH CORRECT FORMAT")
    print("=" * 55)
    
    client = FixedVEO3Client()
    
    # Test both skeleton operation IDs
    operation_ids = [
        "411841f5-e5fd-4d37-8639-f639f4fa16d0",  # First skeleton (8+ hours)
        "7ea3a475-4150-4951-ba4b-9beb33dfb4c0"   # Second skeleton (7+ hours)
    ]
    
    for i, op_id in enumerate(operation_ids, 1):
        print(f"\n🧪 Testing Skeleton Operation {i}: {op_id[:8]}...")
        
        # Test with correct format
        result = client.check_operation_with_correct_format(op_id)
        
        if result.get('success'):
            print(f"✅ Skeleton {i}: FOUND with correct endpoint!")
            data = result['data']
            if data.get('done'):
                print(f"🎉 Skeleton {i}: Video generation completed!")
            else:
                print(f"🔄 Skeleton {i}: Still processing...")
        else:
            print(f"❌ Skeleton {i}: Still not found (may be Google API issue)")
        
        # Show comparison
        print(f"\n📊 Format comparison for Skeleton {i}:")
        client.compare_old_vs_new_format(op_id)

if __name__ == "__main__":
    test_skeleton_operations()