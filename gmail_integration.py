#!/usr/bin/env python3
"""
Gmail Integration for DreamFrame Contact Forms
Completely FREE email service using Gmail SMTP
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class GmailEmailSystem:
    """Free Gmail-based email system"""
    
    def __init__(self):
        # Get Gmail credentials from environment (check both variable names)
        self.gmail_user = os.environ.get('GMAIL_USER', '')
        self.gmail_password = (os.environ.get('GMAIL_APP_PASS', '') or 
                              os.environ.get('GMAIL_APP_PASSWORD', ''))
        self.business_email = self.gmail_user  # Send notifications to your Gmail account
        
        if not self.gmail_user or not self.gmail_password:
            print("⚠️  Gmail credentials not configured")
            print("Set GMAIL_USER and GMAIL_APP_PASS (or GMAIL_APP_PASSWORD) environment variables")
    
    def send_contact_form_email(self, name: str, email: str, message: str) -> bool:
        """Send contact form email via Gmail (FREE)"""
        if not self.gmail_user or not self.gmail_password:
            print("❌ Gmail not configured - saving to database only")
            return False
            
        try:
            # Create professional email
            msg = MIMEMultipart('alternative')
            msg['From'] = self.gmail_user
            msg['To'] = self.business_email
            msg['Subject'] = f"DreamFrame Contact: {name}"
            
            # Create HTML email content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                    <h1 style="color: white; margin: 0;">DreamFrame LLC</h1>
                    <p style="color: white; margin: 5px 0;">New Customer Contact</p>
                </div>
                
                <div style="padding: 30px; background: #f9f9f9;">
                    <h2 style="color: #333;">New Contact Form Submission</h2>
                    
                    <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Name:</strong> {name}</p>
                        <p><strong>Email:</strong> {email}</p>
                        <p><strong>Message:</strong></p>
                        <div style="background: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 10px;">
                            {message.replace(chr(10), '<br>')}
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="mailto:{email}" 
                           style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; padding: 15px 30px; text-decoration: none; 
                                  border-radius: 25px; font-weight: bold; display: inline-block;">
                            Reply to {name}
                        </a>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send via Gmail SMTP with SSL (FREE) - matches Node.js config
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_user, self.gmail_password)
                server.send_message(msg)
            
            print(f"✅ Contact email sent via Gmail: {name} ({email})")
            return True
            
        except Exception as e:
            print(f"❌ Gmail sending failed: {e}")
            return False
    
    def test_connection(self):
        """Test Gmail connection with SSL (matches Node.js config)"""
        if not self.gmail_user or not self.gmail_password:
            return False, "Credentials not configured"
            
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.gmail_user, self.gmail_password)
            
            return True, "Gmail connection successful"
            
        except Exception as e:
            return False, f"Gmail connection failed: {e}"

# Test Gmail setup
if __name__ == "__main__":
    print("🧪 Testing Gmail Integration")
    
    gmail = GmailEmailSystem()
    
    # Test connection
    success, message = gmail.test_connection()
    print(f"Connection test: {message}")
    
    if success:
        # Test sending email
        test_result = gmail.send_contact_form_email(
            name="Test Customer",
            email="test@example.com",
            message="This is a test message from the FREE Gmail integration system."
        )
        
        if test_result:
            print("🎉 Gmail integration working perfectly!")
            print("💰 Cost: Completely FREE (500 emails/day limit)")
        else:
            print("❌ Email sending failed")
    else:
        print("\n📋 Gmail Setup Instructions:")
        print("1. Create Gmail account or use existing")
        print("2. Enable 2-Factor Authentication")
        print("3. Generate App Password in Google Account settings")
        print("4. Set environment variables:")
        print("   GMAIL_USER=your-email@gmail.com")
        print("   GMAIL_APP_PASSWORD=your-16-character-app-password")