#!/usr/bin/env python3
"""
View all customer contact messages
Run this script to see all customer inquiries
"""

from simple_contact_logger import get_all_messages, mark_message_responded
from datetime import datetime

def display_messages():
    """Display all customer messages in a nice format"""
    messages = get_all_messages()
    
    if not messages:
        print("📭 No customer messages yet")
        return
    
    print(f"📨 {len(messages)} Customer Messages")
    print("=" * 80)
    
    for msg in messages:
        status_icon = "🟢" if msg['status'] == 'responded' else "🟡" if msg['status'] == 'new' else "🔵"
        
        print(f"\n{status_icon} Message #{msg['id']} - {msg['status'].upper()}")
        print(f"👤 Name: {msg['name']}")
        print(f"📧 Email: {msg['email']}")
        print(f"📅 Date: {msg['created_at']}")
        print(f"💬 Message:")
        print(f"   {msg['message']}")
        print("-" * 80)

def mark_as_responded():
    """Mark messages as responded to"""
    messages = get_all_messages()
    new_messages = [m for m in messages if m['status'] == 'new']
    
    if not new_messages:
        print("✅ No new messages to respond to")
        return
    
    print(f"🟡 {len(new_messages)} new messages:")
    for msg in new_messages:
        print(f"  #{msg['id']}: {msg['name']} - {msg['message'][:50]}...")
    
    try:
        msg_id = int(input("\nEnter message ID to mark as responded (or 0 to cancel): "))
        if msg_id > 0:
            if mark_message_responded(msg_id):
                print(f"✅ Message #{msg_id} marked as responded")
            else:
                print(f"❌ Error updating message #{msg_id}")
    except ValueError:
        print("Invalid input")

if __name__ == "__main__":
    print("🎯 DreamFrame Customer Messages")
    
    while True:
        print("\nOptions:")
        print("1. View all messages")
        print("2. Mark message as responded")
        print("3. Exit")
        
        choice = input("\nChoose option (1-3): ").strip()
        
        if choice == '1':
            display_messages()
        elif choice == '2':
            mark_as_responded()
        elif choice == '3':
            break
        else:
            print("Invalid choice")