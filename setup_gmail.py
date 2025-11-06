#!/usr/bin/env python3
"""
Gmail Setup Assistant for DreamFrame Contact Forms
Guides you through setting up FREE Gmail email service
"""

import os
import getpass
from gmail_integration import GmailEmailSystem

def setup_gmail_credentials():
    """Interactive Gmail setup"""
    print("🚀 DreamFrame Gmail Setup (FREE Email Service)")
    print("=" * 60)
    
    print("\n📋 Before we start, make sure you have:")
    print("1. A Gmail account (create one if needed)")
    print("2. 2-Factor Authentication enabled")
    print("3. Generated an App Password (not your regular password)")
    
    input("\nPress Enter when ready to continue...")
    
    # Get Gmail credentials
    print("\n📧 Enter your Gmail information:")
    gmail_user = input("Gmail address (e.g., yourname@gmail.com): ").strip()
    
    print("\n🔑 Enter your Gmail App Password:")
    print("(This is NOT your regular password - it's a 16-character code)")
    print("Generate one at: https://myaccount.google.com/apppasswords")
    gmail_password = getpass.getpass("App Password: ").strip()
    
    # Validate inputs
    if not gmail_user or not gmail_password:
        print("❌ Both email and password are required")
        return False
    
    if "@gmail.com" not in gmail_user:
        print("❌ Please use a Gmail address (@gmail.com)")
        return False
    
    if len(gmail_password) < 16:
        print("❌ App password should be 16 characters")
        return False
    
    # Save credentials securely
    try:
        # Set environment variables for this session
        os.environ['GMAIL_USER'] = gmail_user
        os.environ['GMAIL_APP_PASSWORD'] = gmail_password
        
        # Create .env file for persistence
        env_content = f"""
# Gmail Configuration for DreamFrame Contact Forms
GMAIL_USER={gmail_user}
GMAIL_APP_PASSWORD={gmail_password}
"""
        
        with open('.env', 'a') as f:
            f.write(env_content)
        
        print("✅ Credentials saved securely")
        
        # Test the connection
        print("\n🧪 Testing Gmail connection...")
        gmail = GmailEmailSystem()
        success, message = gmail.test_connection()
        
        if success:
            print("✅ Gmail connection successful!")
            
            # Send test email
            print("\n📤 Sending test email...")
            test_success = gmail.send_contact_form_email(
                name="Test Setup",
                email="setup@test.com",
                message="This is a test email from your new Gmail integration. Setup completed successfully!"
            )
            
            if test_success:
                print("🎉 Test email sent successfully!")
                print(f"📧 Check your inbox at: support@dreamframe518.com")
                print("\n✅ Gmail setup complete!")
                print("💰 Cost: Completely FREE (500 emails/day)")
                return True
            else:
                print("❌ Test email failed")
                return False
        else:
            print(f"❌ Connection failed: {message}")
            print("\n🔧 Common issues:")
            print("1. Make sure you're using an App Password, not your regular password")
            print("2. Enable 2-Factor Authentication first")
            print("3. Generate App Password at: https://myaccount.google.com/apppasswords")
            return False
            
    except Exception as e:
        print(f"❌ Setup error: {e}")
        return False

def show_gmail_instructions():
    """Show detailed Gmail setup instructions"""
    print("\n📖 Gmail App Password Setup Instructions:")
    print("=" * 50)
    print("1. Go to your Google Account settings")
    print("2. Select 'Security' from the left panel")
    print("3. Under 'Signing in to Google', select '2-Step Verification'")
    print("4. Enable 2-Step Verification if not already enabled")
    print("5. Go back to Security and select 'App passwords'")
    print("6. Select 'Mail' as the app and 'Other' as the device")
    print("7. Enter 'DreamFrame Website' as the device name")
    print("8. Copy the 16-character password (no spaces)")
    print("9. Use this App Password in the setup below")
    
    print("\n🔗 Direct link: https://myaccount.google.com/apppasswords")

def main():
    """Main setup flow"""
    print("Welcome to DreamFrame Gmail Integration Setup!")
    
    while True:
        print("\nOptions:")
        print("1. Setup Gmail credentials")
        print("2. Show setup instructions")
        print("3. Test existing setup")
        print("4. Exit")
        
        choice = input("\nChoose option (1-4): ").strip()
        
        if choice == '1':
            success = setup_gmail_credentials()
            if success:
                print("\n🎉 Gmail integration ready!")
                print("Customer contact forms will now be sent via Gmail")
                break
        elif choice == '2':
            show_gmail_instructions()
        elif choice == '3':
            gmail = GmailEmailSystem()
            success, message = gmail.test_connection()
            print(f"Test result: {message}")
        elif choice == '4':
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()