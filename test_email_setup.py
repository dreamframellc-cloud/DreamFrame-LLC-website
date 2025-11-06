#!/usr/bin/env python3
"""
Test script for DreamFrame518.com email system
Tests both contact form and video notification emails
"""

import os
import sys
from email_system import email_system

def test_contact_form_email():
    """Test contact form email delivery"""
    print("🧪 Testing Contact Form Email...")
    print("📧 Sending to: support@dreamframe518.com")
    print("📤 From: noreply@dreamframe518.com")
    
    success = email_system.send_contact_form_email(
        name="Test Customer",
        email="customer@example.com", 
        message="This is a test message from the DreamFrame website contact form. Testing the new dreamframe518.com email system setup."
    )
    
    if success:
        print("✅ Contact form email sent successfully!")
        print("Check your support@dreamframe518.com inbox")
    else:
        print("❌ Contact form email failed")
        print("Check SendGrid configuration and API key permissions")
    
    return success

def test_video_notification_email():
    """Test video completion notification"""
    print("\n🧪 Testing Video Completion Email...")
    print("📧 Sending to: customer@example.com")
    print("📤 From: noreply@dreamframe518.com")
    
    success = email_system.send_video_completion_email(
        customer_email="customer@example.com",
        customer_name="Test Customer",
        video_title="Test Video Generation",
        order_id=12345
    )
    
    if success:
        print("✅ Video notification email sent successfully!")
        print("Check customer@example.com inbox (if using real email)")
    else:
        print("❌ Video notification email failed")
        print("Check SendGrid configuration")
    
    return success

def check_sendgrid_status():
    """Check if SendGrid is properly configured"""
    print("\n🔧 Checking SendGrid Configuration...")
    
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        print("❌ SENDGRID_API_KEY not found in environment")
        return False
    
    print(f"✅ SendGrid API Key found (length: {len(api_key)})")
    
    if email_system.sg:
        print("✅ SendGrid client initialized")
        return True
    else:
        print("❌ SendGrid client not initialized")
        return False

def main():
    """Run all email tests"""
    print("🚀 DreamFrame518.com Email System Test")
    print("=" * 50)
    
    # Check configuration
    config_ok = check_sendgrid_status()
    if not config_ok:
        print("\n❌ Configuration issues found. Fix before testing.")
        return
    
    # Test contact form
    contact_success = test_contact_form_email()
    
    # Test video notifications  
    video_success = test_video_notification_email()
    
    # Summary
    print("\n📊 Test Results Summary:")
    print("=" * 30)
    print(f"Contact Form Email: {'✅ PASS' if contact_success else '❌ FAIL'}")
    print(f"Video Notification: {'✅ PASS' if video_success else '❌ FAIL'}")
    
    if contact_success and video_success:
        print("\n🎉 All email tests passed!")
        print("Your dreamframe518.com email system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check SendGrid configuration.")
        print("Ensure 'Mail Send' permission is enabled for your API key.")

if __name__ == "__main__":
    main()