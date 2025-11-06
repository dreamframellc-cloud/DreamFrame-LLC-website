#!/usr/bin/env python3
"""
Admin Payment Dashboard - Monitor and manage payment notifications
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from payment_monitor import payment_monitor

def show_payment_status():
    """Display current payment monitoring status"""
    print("\n" + "="*60)
    print("🤖 DREAMFRAME PAYMENT MONITOR AI - STATUS DASHBOARD")
    print("="*60)
    
    # Check environment configuration
    print("\n📋 SYSTEM CONFIGURATION:")
    required_vars = {
        'STRIPE_SECRET_KEY': 'Stripe Payment Processing',
        'TWILIO_ACCOUNT_SID': 'SMS Notifications', 
        'TWILIO_AUTH_TOKEN': 'SMS Authentication',
        'TWILIO_PHONE_NUMBER': 'SMS Sender Number',
        'SENDGRID_API_KEY': 'Email Notifications',
        'ADMIN_PHONE': 'Your Phone Number',
        'ADMIN_EMAIL': 'Your Email Address'
    }
    
    for var, description in required_vars.items():
        status = "✅ Configured" if os.environ.get(var) else "❌ Missing"
        print(f"   {description}: {status}")
    
    # Check recent payments
    print("\n💰 RECENT PAYMENT ACTIVITY:")
    try:
        recent_payments = payment_monitor.get_recent_payments(hours=24)
        if recent_payments:
            print(f"   Found {len(recent_payments)} payments in last 24 hours:")
            for payment in recent_payments:
                print(f"   - ${payment['amount']} for {payment['service']} from {payment['customer_email']}")
                print(f"     Time: {payment['created'].strftime('%Y-%m-%d %H:%M:%S UTC')}")
        else:
            print("   No real payments found in last 24 hours")
    except Exception as e:
        print(f"   Error checking payments: {e}")
    
    # Notification settings
    print("\n🔔 NOTIFICATION SETTINGS:")
    admin_phone = os.environ.get('ADMIN_PHONE', 'Not configured')
    admin_email = os.environ.get('ADMIN_EMAIL', 'Not configured') 
    print(f"   SMS Alerts: {admin_phone}")
    print(f"   Email Alerts: {admin_email}")
    
    print("\n🚨 ALERT SYSTEM STATUS:")
    print("   Real Payment Detection: Active")
    print("   Test Payment Filtering: Enabled")
    print("   Instant Notifications: Ready")
    
    print("\n" + "="*60)

def test_notification_system():
    """Test the notification system with a mock payment"""
    print("\n🧪 TESTING NOTIFICATION SYSTEM...")
    
    mock_session = {
        'id': 'cs_test_mock_notification_test',
        'amount_total': 10000,  # $100.00 in cents
        'customer_details': {
            'email': 'test@customer.com'
        },
        'metadata': {
            'service_type': 'project_deposit'
        }
    }
    
    try:
        payment_monitor.monitor_payment(mock_session)
        print("✅ Test notification sent successfully!")
    except Exception as e:
        print(f"❌ Test notification failed: {e}")

def main():
    """Main dashboard interface"""
    
    while True:
        show_payment_status()
        
        print("\n📞 DASHBOARD OPTIONS:")
        print("1. Refresh Status")
        print("2. Test Notification System")
        print("3. Check Recent Payments (48 hours)")
        print("4. Setup Admin Contact Info")
        print("5. Exit")
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                continue  # Refresh by looping
                
            elif choice == '2':
                test_notification_system()
                input("\nPress Enter to continue...")
                
            elif choice == '3':
                print("\n💰 CHECKING 48-HOUR PAYMENT HISTORY:")
                recent = payment_monitor.get_recent_payments(hours=48)
                if recent:
                    for payment in recent:
                        print(f"${payment['amount']} - {payment['service']} - {payment['customer_email']}")
                        print(f"  Time: {payment['created']}")
                else:
                    print("No payments found in last 48 hours")
                input("\nPress Enter to continue...")
                
            elif choice == '4':
                print("\n📱 ADMIN CONTACT SETUP:")
                print("Set these environment variables:")
                print("ADMIN_PHONE=+1234567890")
                print("ADMIN_EMAIL=your@email.com")
                input("\nPress Enter to continue...")
                
            elif choice == '5':
                print("\n👋 Payment Monitor Dashboard closed")
                break
                
            else:
                print("Invalid option. Please select 1-5.")
                input("Press Enter to continue...")
                
        except KeyboardInterrupt:
            print("\n\n👋 Dashboard closed by user")
            break
        except Exception as e:
            print(f"\nError: {e}")
            input("Press Enter to continue...")

if __name__ == '__main__':
    main()