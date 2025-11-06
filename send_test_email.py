#!/usr/bin/env python3
"""
Test email sending to chadmarlatt@yahoo.com
"""

import os
import sys
from email_system import email_system

def send_test_email():
    """Send a test email to Chad Marlatt"""
    
    recipient = "chadmarlatt@yahoo.com"
    sender = "noreply@dreamframe.com"
    subject = "DreamFrame LLC - Test Email"
    
    html_content = """
    <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 28px;">DreamFrame LLC</h1>
            <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Professional Video Production</p>
        </div>
        
        <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
            <h2 style="color: #333; margin-top: 0;">Hello Chad!</h2>
            
            <p style="color: #555; line-height: 1.6;">
                This is a test email from the DreamFrame video production platform. 
                Our email system is now fully operational and ready for business communication.
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                <h3 style="color: #333; margin-top: 0;">Email System Features:</h3>
                <ul style="color: #555;">
                    <li>Professional HTML email templates</li>
                    <li>SendGrid integration for reliable delivery</li>
                    <li>Contact form on website</li>
                    <li>Video completion notifications</li>
                    <li>Business communication support</li>
                </ul>
            </div>
            
            <p style="color: #555; line-height: 1.6;">
                You can contact us anytime through our website contact form, and we'll 
                receive your message instantly through this email system.
            </p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="https://dreamframe.com/contact" 
                   style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                          color: white; padding: 15px 30px; text-decoration: none; 
                          border-radius: 25px; font-weight: bold; display: inline-block;">
                    Visit Our Website
                </a>
            </div>
            
            <p style="color: #888; font-size: 14px; text-align: center; margin: 20px 0 0 0;">
                Best regards,<br>
                The DreamFrame Team
            </p>
        </div>
    </div>
    """
    
    print(f"Sending test email to {recipient}...")
    print(f"Subject: {subject}")
    print("=" * 50)
    
    # Check if SendGrid API key is available
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        print("❌ SendGrid API key not found")
        return False
    
    print(f"✅ SendGrid API key available ({len(api_key)} characters)")
    
    # Send the email
    try:
        result = email_system.send_email(
            to_email=recipient,
            from_email=sender,
            subject=subject,
            html_content=html_content
        )
        
        if result:
            print("✅ Email sent successfully!")
            print(f"📧 Delivered to: {recipient}")
            print("📋 Check Chad's inbox for the test email")
            return True
        else:
            print("❌ Email failed to send")
            print("🔧 This is likely due to SendGrid API key permissions")
            print("💡 The API key needs 'Mail Send' permissions in SendGrid")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

if __name__ == "__main__":
    success = send_test_email()
    
    if success:
        print("\n🎉 Test email completed successfully!")
    else:
        print("\n⚠️  Email system needs SendGrid API key configuration")
        print("📖 Check EMAIL_SYSTEM_STATUS.md for setup instructions")