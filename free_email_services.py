#!/usr/bin/env python3
"""
Free Email Service Options for DreamFrame Contact Forms
Compare different free email services and their setup
"""

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class FreeEmailService:
    """Base class for free email services"""
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    def send_email(self, to_email, subject, html_content):
        """Send email using the configured service"""
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = to_email
            msg['Subject'] = subject
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully via {self.__class__.__name__}")
            return True
            
        except Exception as e:
            print(f"❌ Email failed via {self.__class__.__name__}: {e}")
            return False

class GmailService(FreeEmailService):
    """Free Gmail SMTP service"""
    
    def __init__(self, username, password):
        super().__init__(username, password)
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.monthly_limit = "500 emails/day"
        self.setup_notes = """
        Gmail Setup:
        1. Enable 2-Factor Authentication on your Gmail account
        2. Generate an "App Password" for this application
        3. Use your Gmail address and App Password (not regular password)
        4. Completely FREE - 500 emails per day limit
        """

class OutlookService(FreeEmailService):
    """Free Outlook/Hotmail SMTP service"""
    
    def __init__(self, username, password):
        super().__init__(username, password)
        self.smtp_server = "smtp-mail.outlook.com"
        self.smtp_port = 587
        self.monthly_limit = "300 emails/day"
        self.setup_notes = """
        Outlook Setup:
        1. Use your Outlook.com or Hotmail.com email
        2. Enable 2-Factor Authentication
        3. Generate App Password in security settings
        4. Completely FREE - 300 emails per day limit
        """

class YahooService(FreeEmailService):
    """Free Yahoo SMTP service"""
    
    def __init__(self, username, password):
        super().__init__(username, password)
        self.smtp_server = "smtp.mail.yahoo.com"
        self.smtp_port = 587
        self.monthly_limit = "100 emails/day"
        self.setup_notes = """
        Yahoo Setup:
        1. Use your Yahoo email address
        2. Enable 2-Step Verification
        3. Generate App Password in Account Security
        4. Completely FREE - 100 emails per day limit
        """

def compare_free_services():
    """Compare all free email service options"""
    
    services = [
        {
            "name": "Gmail",
            "email_limit": "500/day",
            "cost": "FREE",
            "reliability": "⭐⭐⭐⭐⭐",
            "ease_setup": "⭐⭐⭐⭐",
            "recommended": True
        },
        {
            "name": "Outlook", 
            "email_limit": "300/day",
            "cost": "FREE",
            "reliability": "⭐⭐⭐⭐⭐",
            "ease_setup": "⭐⭐⭐⭐",
            "recommended": True
        },
        {
            "name": "Yahoo",
            "email_limit": "100/day", 
            "cost": "FREE",
            "reliability": "⭐⭐⭐",
            "ease_setup": "⭐⭐⭐",
            "recommended": False
        },
        {
            "name": "Database Only",
            "email_limit": "Unlimited",
            "cost": "FREE",
            "reliability": "⭐⭐⭐⭐⭐",
            "ease_setup": "⭐⭐⭐⭐⭐",
            "recommended": True
        }
    ]
    
    print("🆓 FREE Email Service Comparison")
    print("=" * 70)
    
    for service in services:
        rec = "🟢 RECOMMENDED" if service["recommended"] else "🟡 OK"
        print(f"\n{service['name']}: {rec}")
        print(f"  📧 Email Limit: {service['email_limit']}")
        print(f"  💰 Cost: {service['cost']}")
        print(f"  🔧 Reliability: {service['reliability']}")
        print(f"  ⚙️ Setup Ease: {service['ease_setup']}")

def create_gmail_integration():
    """Create Gmail integration example"""
    return '''
# Gmail Integration for DreamFrame
# Add to your app.py contact route:

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_contact_email_gmail(name, email, message):
    """Send contact form email via Gmail (FREE)"""
    try:
        # Gmail credentials (use App Password)
        gmail_user = "your-email@gmail.com"
        gmail_password = "your-app-password"  # Not your regular password!
        
        # Create email
        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = "support@dreamframe518.com"  # Your business email
        msg['Subject'] = f"New Contact: {name}"
        
        body = f"""
        New contact form submission:
        
        Name: {name}
        Email: {email}
        Message: {message}
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send via Gmail
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)
            server.send_message(msg)
        
        return True
        
    except Exception as e:
        print(f"Gmail error: {e}")
        return False
'''

if __name__ == "__main__":
    compare_free_services()
    
    print("\n" + "="*70)
    print("💡 RECOMMENDATION: Start with Database-Only Solution")
    print("   - Works immediately, no setup required")
    print("   - Add Gmail later if you want automatic email delivery")
    print("   - Run 'python view_messages.py' to see customer messages")