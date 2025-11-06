"""
VEO 3 Fast Implementation
Testing VEO 3 Fast model which may be more readily available
"""

import os
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from typing import Optional, Dict, Any

class VEO3FastClient:
    def __init__(self):
        self.project_id = "dreamframe"
        self.location = "us-central1"
        # Test different VEO 3 model variations
        self.model_variants = [
            "veo-3-fast",
            "veo-3-fast-001", 
            "veo-3-fast-preview",
            "veo-fast",
            "veo-3"  # fallback
        ]
        self.storage_uri = "gs://dreamframe-videos/"
        
        print(f"🚀 VEO 3 Fast Client initialized")
        print(f"📍 Project: {self.project_id}")
        print(f"🌍 Location: {self.location}")
        print(f"💾 Storage: {self.storage_uri}")
        print(f"🤖 Testing models: {', '.join(self.model_variants)}")
        
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
            
            print("✅ Access token obtained successfully")
            return credentials.token
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    def test_model_availability(self, model_name: str) -> Dict[str, Any]:
        """Test if a specific VEO model is available"""
        
        access_token = self.get_access_token()
        if not access_token:
            return {"available": False, "error": "Authentication failed"}
        
        endpoint = (f"https://{self.location}-aiplatform.googleapis.com/v1/"
                   f"projects/{self.project_id}/locations/{self.location}/"
                   f"publishers/google/models/{model_name}:predictLongRunning")
        
        payload = {
            "instances": [
                {
                    "prompt": "Test availability check - a simple mountain scene"
                }
            ],
            "parameters": {
                "storageUri": self.storage_uri,
                "sampleCount": 1,
                "resolution": "720p"
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id
        }
        
        print(f"🧪 Testing model: {model_name}")
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {model_name} is AVAILABLE!")
                result = response.json()
                return {
                    "available": True,
                    "model": model_name,
                    "operation_name": result.get('name'),
                    "status_code": 200
                }
            else:
                error_text = response.text
                print(f"❌ {model_name}: {response.status_code}")
                
                if "not found" in error_text.lower():
                    print(f"   Model not available in this project/region")
                elif "permission" in error_text.lower():
                    print(f"   Permission denied")
                elif "quota" in error_text.lower():
                    print(f"   Quota exceeded")
                
                return {
                    "available": False,
                    "model": model_name,
                    "status_code": response.status_code,
                    "error": error_text
                }
                
        except Exception as e:
            print(f"❌ {model_name} test failed: {str(e)}")
            return {
                "available": False,
                "model": model_name,
                "error": str(e)
            }
    
    def find_available_model(self) -> Optional[str]:
        """Test all VEO model variants to find an available one"""
        
        print("🔍 SEARCHING FOR AVAILABLE VEO MODELS")
        print("=" * 45)
        
        available_models = []
        
        for model in self.model_variants:
            result = self.test_model_availability(model)
            
            if result.get("available"):
                available_models.append({
                    "model": model,
                    "operation_name": result.get("operation_name")
                })
                print(f"🎉 FOUND AVAILABLE MODEL: {model}")
            
            print()  # spacing between tests
        
        if available_models:
            print(f"✅ Found {len(available_models)} available model(s)")
            best_model = available_models[0]["model"]  # Use first available
            print(f"🚀 Recommended model: {best_model}")
            return best_model
        else:
            print("❌ No VEO models are currently available")
            print("🔧 This confirms the model access issue")
            return None

def test_veo3_fast():
    """Test VEO 3 Fast and other variants"""
    print("🚀 VEO 3 FAST AVAILABILITY TEST")
    print("=" * 35)
    
    client = VEO3FastClient()
    
    # Test for available models
    available_model = client.find_available_model()
    
    if available_model:
        print(f"🎉 SUCCESS! {available_model} is available")
        print("🎬 DreamFrame can use this model for video generation")
        
        # Update main VEO 3 client with working model
        print(f"💡 Update your VEO 3 client to use: {available_model}")
        
        return {
            "success": True,
            "model": available_model,
            "status": "available"
        }
    else:
        print("❌ No VEO models available - need Google Cloud access")
        print("📋 Action required: Request VEO 3 access in Google Cloud Console")
        
        return {
            "success": False,
            "status": "no_models_available",
            "action_required": "Request VEO 3 access from Google"
        }

if __name__ == "__main__":
    test_veo3_fast()