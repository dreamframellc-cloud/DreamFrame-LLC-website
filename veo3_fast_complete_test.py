"""
Complete VEO 3 Fast Test with User's Enhanced Format
Testing the full API structure provided by user
"""

import os
import json
import requests
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request

class CompleteVEO3FastTest:
    def __init__(self):
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.storage_uri = "gs://dreamframe-videos/"
        
        print(f"🚀 Complete VEO 3 Fast Test - Enhanced Format")
        print(f"📍 Project: {self.project_id}")
        print(f"🌍 Location: {self.location}")
        print(f"💾 Storage: {self.storage_uri}")
        
    def get_access_token(self):
        """Get authenticated access token"""
        try:
            # Using environment variable for credentials
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_json:
                import json
                creds_data = json.loads(credentials_json)
                credentials = service_account.Credentials.from_service_account_info(
                    creds_data,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            else:
                # Fallback to direct credentials
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
            
            print("✅ Access token obtained")
            return credentials.token
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return None
    
    def test_complete_veo3_fast(self):
        """Test with complete VEO 3 Fast format from user"""
        
        print("🧪 Testing Complete VEO 3 Fast Format")
        print("=" * 40)
        
        access_token = self.get_access_token()
        if not access_token:
            return False
        
        # Use exact endpoint format from user
        endpoint = (f"https://us-central1-aiplatform.googleapis.com/v1/"
                   f"projects/{self.project_id}/locations/us-central1/"
                   f"publishers/google/models/veo-3.0-fast:predictLongRunning")
        
        # Use exact payload structure from user
        payload = {
            "instances": [
                {
                    "prompt": "A cinematic shot of a futuristic city at dusk with neon lights and flying cars"
                }
            ],
            "parameters": {
                "storageUri": self.storage_uri,
                "sampleCount": 1,
                "resolution": "1080p",
                "durationSeconds": 8,
                "generateAudio": True
            }
        }
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id
        }
        
        print(f"🔗 Endpoint: {endpoint}")
        print(f"📦 Payload: Enhanced format with 1080p, 8s duration, audio")
        print(f"📝 Prompt: Futuristic city scene")
        print()
        
        try:
            response = requests.post(endpoint, json=payload, headers=headers, timeout=60)
            
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("🎉 VEO 3 Fast ACCEPTED with complete format!")
                
                if 'name' in result:
                    operation_name = result['name']
                    operation_id = operation_name.split('/')[-1]
                    
                    print(f"🔄 Operation ID: {operation_id}")
                    print(f"🎬 Generating: 1080p, 8 seconds, with audio")
                    print(f"💾 Output location: {self.storage_uri}")
                    print("✅ SUCCESS! VEO 3 Fast is working")
                    
                    return True
                else:
                    print("❌ No operation name in response")
                    return False
            else:
                error_text = response.text
                print(f"❌ Request failed: {response.status_code}")
                print(f"Error: {error_text}")
                
                if "not found" in error_text.lower():
                    print("⚠️  VEO 3 Fast model not enabled in project")
                elif "permission" in error_text.lower():
                    print("⚠️  Service account permission issue")
                elif "quota" in error_text.lower():
                    print("⚠️  API quota exceeded")
                
                return False
                
        except Exception as e:
            print(f"❌ Request error: {str(e)}")
            return False

def run_complete_test():
    """Run the complete VEO 3 Fast test"""
    
    tester = CompleteVEO3FastTest()
    
    success = tester.test_complete_veo3_fast()
    
    if success:
        print()
        print("🎉 VEO 3 FAST IS WORKING!")
        print("✅ DreamFrame can now generate videos")
        print("⚡ Expected processing time: 2-5 minutes")
        print("🎬 Output: 1080p HD with synchronized audio")
    else:
        print()
        print("❌ VEO 3 Fast access still needed")
        print("📋 Check Google Cloud Console for model access")
        print("🔧 Enable VEO 3 Fast in Vertex AI Model Garden")

if __name__ == "__main__":
    run_complete_test()