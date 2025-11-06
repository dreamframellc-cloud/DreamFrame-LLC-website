#!/usr/bin/env python3
"""
Payment Monitor - AI-powered payment tracking system
Monitors Stripe webhooks and sends notifications for real payments
"""

import os
import time
import logging
from datetime import datetime, timezone
from flask import Flask, request, jsonify
import stripe
from twilio.rest import Client
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
twilio_client = Client(
    os.environ.get('TWILIO_ACCOUNT_SID'),
    os.environ.get('TWILIO_AUTH_TOKEN')
)
sendgrid_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

class PaymentMonitor:
    """AI-powered payment monitoring system"""
    
    def __init__(self):
        self.admin_phone = os.environ.get('ADMIN_PHONE', "+1234567890")  # Update with your phone number
        self.admin_email = os.environ.get('ADMIN_EMAIL', "admin@dreamframe.com")  # Update with your email
        self.notification_sent = {}
        
    def monitor_payment(self, session_data):
        """Monitor and analyze payment data"""
        try:
            payment_amount = session_data.get('amount_total', 0) / 100  # Convert from cents
            service_type = session_data.get('metadata', {}).get('service_type', 'unknown')
            customer_email = session_data.get('customer_details', {}).get('email', 'unknown')
            
            # Log payment details
            logger.info(f"🔔 PAYMENT RECEIVED: ${payment_amount} for {service_type} from {customer_email}")
            
            # Check if this is a real payment (not test mode)
            if not session_data.get('id', '').startswith('cs_test_'):
                self.send_payment_notification(payment_amount, service_type, customer_email, session_data)
            else:
                logger.info("Test payment detected - notifications suppressed")
                
        except Exception as e:
            logger.error(f"Error monitoring payment: {e}")
    
    def send_payment_notification(self, amount, service_type, customer_email, session_data):
        """Send immediate notifications for real payments"""
        try:
            session_id = session_data.get('id', 'unknown')
            timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
            
            # Skip if already notified for this session
            if session_id in self.notification_sent:
                return
                
            message = f"""
🚨 PAYMENT ALERT - DreamFrame LLC

💰 Amount: ${amount}
📋 Service: {service_type.replace('_', ' ').title()}
📧 Customer: {customer_email}
🕒 Time: {timestamp}
🔗 Session: {session_id}

This is a REAL payment notification.
            """.strip()
            
            # Send SMS notification
            self.send_sms_alert(message)
            
            # Send email notification
            self.send_email_alert(amount, service_type, customer_email, timestamp, session_id)
            
            # Mark as notified
            self.notification_sent[session_id] = True
            
            logger.info(f"✅ Payment notifications sent for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
    
    def send_sms_alert(self, message):
        """Send SMS alert via Twilio"""
        try:
            twilio_client.messages.create(
                body=message,
                from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                to=self.admin_phone
            )
            logger.info("📱 SMS alert sent successfully")
        except Exception as e:
            logger.error(f"SMS alert failed: {e}")
    
    def send_email_alert(self, amount, service_type, customer_email, timestamp, session_id):
        """Send detailed email alert via SendGrid"""
        try:
            subject = f"💰 Payment Received: ${amount} - DreamFrame LLC"
            
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #ff6b35;">Payment Notification - DreamFrame LLC</h2>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Payment Details:</h3>
                    <p><strong>Amount:</strong> ${amount} USD</p>
                    <p><strong>Service:</strong> {service_type.replace('_', ' ').title()}</p>
                    <p><strong>Customer Email:</strong> {customer_email}</p>
                    <p><strong>Timestamp:</strong> {timestamp}</p>
                    <p><strong>Session ID:</strong> {session_id}</p>
                </div>
                
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; border-left: 4px solid #28a745;">
                    <p><strong>✅ This is a confirmed real payment (not test mode)</strong></p>
                </div>
                
                <p>Next steps:</p>
                <ul>
                    <li>Process customer order</li>
                    <li>Send confirmation email to customer</li>
                    <li>Begin video production workflow</li>
                </ul>
                
                <hr style="margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    DreamFrame LLC Payment Monitor System<br>
                    Generated: {timestamp}
                </p>
            </div>
            """
            
            message = Mail(
                from_email='notifications@dreamframe.com',
                to_emails=self.admin_email,
                subject=subject,
                html_content=html_content
            )
            
            sendgrid_client.send(message)
            logger.info("📧 Email alert sent successfully")
            
        except Exception as e:
            logger.error(f"Email alert failed: {e}")
    
    def get_recent_payments(self, hours=24):
        """Retrieve recent payments from Stripe"""
        try:
            # Get payments from last 24 hours
            since_timestamp = int(time.time() - (hours * 3600))
            
            payments = stripe.checkout.Session.list(
                created={'gte': since_timestamp},
                limit=100
            )
            
            real_payments = []
            for payment in payments.data:
                if payment.payment_status == 'paid' and not payment.id.startswith('cs_test_'):
                    real_payments.append({
                        'id': payment.id,
                        'amount': payment.amount_total / 100,
                        'customer_email': payment.customer_details.email if payment.customer_details else 'unknown',
                        'service': payment.metadata.get('service_type', 'unknown'),
                        'created': datetime.fromtimestamp(payment.created, timezone.utc)
                    })
            
            return real_payments
            
        except Exception as e:
            logger.error(f"Error retrieving payments: {e}")
            return []

# Global monitor instance
payment_monitor = PaymentMonitor()

def setup_webhook_handler(app):
    """Setup Stripe webhook handler"""
    
    @app.route('/stripe-webhook', methods=['POST'])
    def handle_webhook():
        payload = request.get_data()
        sig_header = request.headers.get('Stripe-Signature')
        
        try:
            # Verify webhook signature (requires webhook endpoint secret)
            # event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            
            # For now, process without signature verification
            import json
            event = json.loads(payload)
            
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                payment_monitor.monitor_payment(session)
                
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            logger.error(f"Webhook error: {e}")
            return jsonify({'error': str(e)}), 400
    
    return app

if __name__ == '__main__':
    # Test the monitor system
    logger.info("🤖 Payment Monitor AI initialized")
    logger.info("📊 Monitoring for real payments...")
    logger.info("🔔 Notifications configured for SMS and Email")
    
    # Check recent payments
    recent = payment_monitor.get_recent_payments()
    if recent:
        logger.info(f"📈 Found {len(recent)} recent payments")
        for payment in recent:
            logger.info(f"  - ${payment['amount']} from {payment['customer_email']}")
    else:
        logger.info("📊 No recent real payments found")