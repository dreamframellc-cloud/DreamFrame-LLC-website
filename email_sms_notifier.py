#!/usr/bin/env python3
"""
Email SMS Notification System
Sends SMS alerts when emails are received at support@dreamframe.com
"""

import os
from datetime import datetime
from twilio.rest import Client
from typing import Optional

class EmailSMSNotifier:
    def __init__(self):
        """Initialize Twilio SMS notification system"""
        self.account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        self.from_phone = os.environ.get("TWILIO_PHONE_NUMBER")
        
        # Your personal phone number (you'll need to set this)
        self.owner_phone = os.environ.get("OWNER_PHONE_NUMBER", "+12345678901")  # Update this
        
        if self.account_sid and self.auth_token and self.from_phone:
            self.client = Client(self.account_sid, self.auth_token)
            print("✅ Twilio SMS notifications initialized")
        else:
            self.client = None
            print("❌ Twilio credentials not found")
    
    def send_email_notification(self, from_email: str, subject: str, content: str = "") -> bool:
        """Send SMS notification when email is received"""
        
        if not self.client:
            print("SMS notifications not configured")
            return False
        
        try:
            # Create notification message
            timestamp = datetime.now().strftime("%I:%M %p")
            
            # Truncate long content
            preview = content[:100] + "..." if len(content) > 100 else content
            
            message_body = f"""📧 NEW EMAIL - {timestamp}

From: {from_email}
Subject: {subject}

{preview}

Reply via support@dreamframe.com"""
            
            # Send SMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_phone,
                to=self.owner_phone
            )
            
            print(f"✅ SMS notification sent: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send SMS notification: {str(e)}")
            return False
    
    def send_urgent_notification(self, alert_type: str, details: str) -> bool:
        """Send urgent business notifications"""
        
        if not self.client:
            return False
        
        try:
            urgent_message = f"""🚨 URGENT: {alert_type}

{details}

Time: {datetime.now().strftime("%I:%M %p")}
Check: support@dreamframe.com"""
            
            message = self.client.messages.create(
                body=urgent_message,
                from_=self.from_phone,
                to=self.owner_phone
            )
            
            print(f"✅ Urgent notification sent: {message.sid}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send urgent notification: {str(e)}")
            return False
    
    def test_notification(self) -> bool:
        """Test SMS notification system"""
        
        if not self.client:
            print("❌ Twilio not configured for testing")
            return False
        
        try:
            test_message = f"""DreamFrame SMS Test

SMS notifications working!
Time: {datetime.now().strftime("%I:%M %p")}

You'll get alerts when customers email support@dreamframe.com"""
            
            print(f"🔍 Sending SMS from {self.from_phone} to {self.owner_phone}")
            
            message = self.client.messages.create(
                body=test_message,
                from_=self.from_phone,
                to=self.owner_phone
            )
            
            print(f"✅ Test SMS sent successfully: {message.sid}")
            print(f"📱 Message status: {message.status}")
            
            # Check message status
            updated_message = self.client.messages(message.sid).fetch()
            print(f"📊 Updated status: {updated_message.status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Test SMS failed: {str(e)}")
            return False

# Initialize global notifier
sms_notifier = EmailSMSNotifier()

def notify_email_received(from_email: str, subject: str, content: str = "") -> bool:
    """Helper function to send email notifications"""
    return sms_notifier.send_email_notification(from_email, subject, content)

def notify_urgent_alert(alert_type: str, details: str) -> bool:
    """Helper function to send urgent notifications"""
    return sms_notifier.send_urgent_notification(alert_type, details)

if __name__ == "__main__":
    # Test the notification system
    print("🧪 Testing SMS notification system...")
    success = sms_notifier.test_notification()
    
    if success:
        print("✅ SMS notifications ready!")
    else:
        print("❌ SMS setup needs attention")