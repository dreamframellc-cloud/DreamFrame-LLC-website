#!/usr/bin/env python3
"""
Test Payment Notification System
"""

import os
import sys
from payment_monitor import payment_monitor

def test_notification():
    """Test the payment notification system"""
    
    print("🧪 Testing Payment Notification System...")
    print("=" * 50)
    
    # Mock payment session for testing
    mock_session = {
        'id': 'cs_live_test_notification_12345',  # This looks like a real payment ID
        'amount_total': 10000,  # $100.00 in cents
        'customer_details': {
            'email': 'test.customer@example.com'
        },
        'metadata': {
            'service_type': 'project_deposit'
        },
        'created': 1755036152
    }
    
    print(f"📧 Admin Email: {os.environ.get('ADMIN_EMAIL', 'Not set')}")
    print(f"📱 Admin Phone: {os.environ.get('ADMIN_PHONE', 'Not set')}")
    
    try:
        print("\n🔔 Sending test notification...")
        payment_monitor.monitor_payment(mock_session)
        print("✅ Test notification sent successfully!")
        print("\nCheck your phone and email for the test alert.")
        
    except Exception as e:
        print(f"❌ Test notification failed: {e}")
        return False
        
    return True

if __name__ == '__main__':
    success = test_notification()
    if success:
        print("\n🎉 Payment monitoring system is ready!")
        print("Your system will now detect real payments automatically.")
    else:
        print("\n⚠️ Please check your environment variables and try again.")