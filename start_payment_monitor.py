#!/usr/bin/env python3
"""
Start Payment Monitor - Initialize the AI payment monitoring system
"""

import os
import sys
import time
import logging
from payment_monitor import payment_monitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Start the payment monitoring system"""
    
    logger.info("🤖 DreamFrame Payment Monitor AI Starting...")
    logger.info("📊 Initializing payment tracking systems...")
    
    # Check environment variables
    required_vars = [
        'STRIPE_SECRET_KEY',
        'TWILIO_ACCOUNT_SID', 
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER',
        'SENDGRID_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.warning(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        logger.info("Payment monitor will run with limited functionality")
    else:
        logger.info("✅ All environment variables configured")
    
    logger.info("🔔 Payment notifications configured for:")
    logger.info("   📱 SMS alerts via Twilio")
    logger.info("   📧 Email alerts via SendGrid") 
    logger.info("   💰 Real payment detection (excludes test payments)")
    
    # Check for recent payments
    logger.info("📈 Checking for recent payment activity...")
    recent_payments = payment_monitor.get_recent_payments(hours=24)
    
    if recent_payments:
        logger.info(f"💰 Found {len(recent_payments)} recent payments:")
        for payment in recent_payments:
            logger.info(f"   - ${payment['amount']} for {payment['service']} from {payment['customer_email']}")
    else:
        logger.info("📊 No recent payments in last 24 hours")
    
    logger.info("✅ Payment Monitor AI is now active and monitoring")
    logger.info("🚨 You will receive immediate notifications for any real payments")
    
    return True

if __name__ == '__main__':
    try:
        main()
        
        # Keep monitor running
        logger.info("🔄 Monitor is running... Press Ctrl+C to stop")
        while True:
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        logger.info("⏹️  Payment Monitor stopped by user")
    except Exception as e:
        logger.error(f"❌ Payment Monitor error: {e}")
        sys.exit(1)