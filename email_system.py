import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DreamFrameEmailSystem:
    def __init__(self):
        # Gmail SMTP configuration (much simpler than SendGrid)
        self.gmail_user = os.environ.get('GMAIL_USER', 'DreamFrameLLC@gmail.com')
        self.gmail_password = os.environ.get('GMAIL_APP_PASSWORD', '')
        self.business_email = 'DreamFrameLLC@gmail.com'  # All emails forward here
        
        if not self.gmail_password:
            logger.warning("Gmail App Password not configured - emails will be saved to database only")
            logger.info("Set GMAIL_APP_PASSWORD environment variable for email functionality")
        else:
            logger.info("Gmail email system initialized successfully")
    
    def send_email(self, to_email: str, subject: str, html_content: str = None, text_content: str = None) -> bool:
        """Send email using Gmail SMTP (FREE and reliable)"""
        if not self.gmail_password:
            logger.error("Gmail App Password not configured - cannot send email")
            return False
        
        try:
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['From'] = f'"DreamFrame LLC" <{self.gmail_user}>'  # Proper from format
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add content
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            elif text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            else:
                logger.error("Either text_content or html_content must be provided")
                return False
            
            # Option B: Port 587 with STARTTLS (troubleshooting alternative)
            import ssl
            context = ssl.create_default_context()
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls(context=context)
            server.login(self.gmail_user, self.gmail_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully via Gmail to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Gmail SMTP error: {e}")
            return False
    
    def send_video_completion_email(self, customer_email: str, customer_name: str, 
                                  video_title: str, order_id: int) -> bool:
        """Send video completion notification"""
        subject = f"Your DreamFrame video '{video_title}' is ready!"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; text-align: center;">
                <h1 style="color: white; margin: 0;">DreamFrame LLC</h1>
                <p style="color: white; margin: 5px 0;">Professional Video Production</p>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9;">
                <h2 style="color: #333;">Hi {customer_name}!</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    Great news! Your video <strong>"{video_title}"</strong> has been completed 
                    and is ready for download.
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3 style="margin: 0 0 10px 0; color: #333;">Order Details:</h3>
                    <p style="margin: 5px 0;"><strong>Video Title:</strong> {video_title}</p>
                    <p style="margin: 5px 0;"><strong>Order ID:</strong> #{order_id}</p>
                    <p style="margin: 5px 0;"><strong>Status:</strong> Completed ✅</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://dreamframe.replit.app/my-videos" 
                       style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                              color: white; padding: 15px 30px; text-decoration: none; 
                              border-radius: 25px; font-weight: bold; display: inline-block;">
                        Download Your Video
                    </a>
                </div>
                
                <p style="color: #555; line-height: 1.6;">
                    Log into your DreamFrame account to download your completed video. 
                    Your video is ready in high quality and optimized for all devices.
                </p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="color: #777; font-size: 14px;">
                    Thank you for choosing DreamFrame LLC for your video production needs!
                </p>
                
                <p style="color: #777; font-size: 12px;">
                    This is an automated message. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=customer_email,
            subject=subject,
            html_content=html_content
        )
    
    def send_contact_form_email(self, name: str, email: str, message: str) -> bool:
        """Send contact form submission"""
        subject = f"New Contact Form Submission from {name}"
        
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h2 style="color: #333;">New Contact Form Submission</h2>
            
            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px;">
                <p><strong>Name:</strong> {name}</p>
                <p><strong>Email:</strong> {email}</p>
                <p><strong>Message:</strong></p>
                <div style="background: white; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    {message.replace(chr(10), '<br>')}
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(
            to_email=self.business_email,  # Forward to DreamFrameLLC@gmail.com
            subject=subject,
            html_content=html_content
        )

# Global email system instance
email_system = DreamFrameEmailSystem()

def send_video_completion_notification(customer_email: str, customer_name: str, 
                                     video_title: str, order_id: int) -> bool:
    """Quick function to send video completion email"""
    return email_system.send_video_completion_email(
        customer_email, customer_name, video_title, order_id
    )

def send_contact_email(name: str, email: str, message: str) -> bool:
    """Quick function to send contact form email"""
    return email_system.send_contact_form_email(name, email, message)

def send_test_email(to_email: str = "DreamFrameLLC@gmail.com") -> bool:
    """Quick function to test Gmail email functionality"""
    return email_system.send_email(
        to_email=to_email,
        subject="DreamFrame Gmail Test",
        html_content="<h1>🎉 Gmail Email Working!</h1><p>Your DreamFrame Gmail email system is configured correctly and working perfectly.</p><p>💰 This email was sent FREE via Gmail SMTP.</p>"
    )

if __name__ == "__main__":
    # Test Gmail email functionality
    print("🧪 Testing DreamFrame Gmail Email System...")
    
    test_result = send_test_email()
    
    if test_result:
        print("✅ Gmail email system working perfectly!")
        print("💰 Cost: Completely FREE (500 emails/day limit)")
    else:
        print("❌ Gmail email sending failed")
        print("📋 Run 'python gmail_setup_guide.py' for setup instructions")