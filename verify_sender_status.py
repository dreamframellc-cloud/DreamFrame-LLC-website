#!/usr/bin/env python3
"""
Check SendGrid sender verification status
"""

import os
import requests
import json

def check_sendgrid_senders():
    """Check verified senders in SendGrid"""
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        print("No API key found")
        return
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Check verified senders
        response = requests.get(
            'https://api.sendgrid.com/v3/verified_senders',
            headers=headers
        )
        
        print(f"Verified Senders Response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            senders = data.get('results', [])
            
            if senders:
                print(f"Found {len(senders)} verified sender(s):")
                for sender in senders:
                    email = sender.get('from_email')
                    verified = sender.get('verified')
                    print(f"  - {email}: {'✅ Verified' if verified else '❌ Not Verified'}")
                
                # Try sending with first verified sender
                verified_senders = [s for s in senders if s.get('verified')]
                if verified_senders:
                    first_verified = verified_senders[0]['from_email']
                    print(f"\n🎯 Using verified sender: {first_verified}")
                    return first_verified
                else:
                    print("\n⚠️ No verified senders found")
            else:
                print("No senders configured")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Error checking senders: {e}")
    
    return None

if __name__ == "__main__":
    verified_email = check_sendgrid_senders()
    if verified_email:
        print(f"\nReady to send emails from: {verified_email}")
    else:
        print("\nSender verification needed")