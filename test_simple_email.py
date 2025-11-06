#!/usr/bin/env python3
"""
Test SendGrid with a simpler approach
"""

import os
import requests
import json

def test_sendgrid_direct():
    """Test SendGrid API directly with minimal payload"""
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    print(f"Testing SendGrid with API key ({len(api_key)} chars)")
    
    # Simple test payload
    payload = {
        "personalizations": [
            {
                "to": [{"email": "chadmarlatt@yahoo.com"}],
                "subject": "DreamFrame Test"
            }
        ],
        "from": {"email": "test@example.com"},  # Using generic sender
        "content": [
            {
                "type": "text/plain",
                "value": "Hello from DreamFrame! This is a test email."
            }
        ]
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            'https://api.sendgrid.com/v3/mail/send',
            headers=headers,
            data=json.dumps(payload)
        )
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code == 202:
            print("SUCCESS: Email sent!")
            print("Chad should receive the test email")
        elif response.status_code == 403:
            print("FORBIDDEN: API key lacks permissions")
            print("Response:", response.text)
        elif response.status_code == 400:
            print("BAD REQUEST: Invalid email format or content")
            print("Response:", response.text)
        else:
            print(f"UNEXPECTED: {response.status_code}")
            print("Response:", response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_sendgrid_direct()