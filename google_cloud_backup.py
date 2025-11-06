#!/usr/bin/env python3
"""
Google Cloud Console Backup Instructions
For manual video retrieval when automated system needs help
"""

def show_manual_instructions():
    """Show manual Google Cloud Console instructions"""
    
    operations = [
        ('edd5e6fc-575f-4762-9cfd-f0f4930d2b17', 'Instagram Business Meeting'),
        ('52f6b4b9-41e7-470e-8970-c01e29d4601c', 'Speed Test'),
        ('a9549d9f-8bf8-47f0-b2ce-1c8d4e03f4a8', 'Fresh Demo Video'),
    ]
    
    print("📋 Manual Video Retrieval Instructions")
    print("=" * 50)
    print()
    print("If the automated system isn't showing your videos,")
    print("you can manually check Google Cloud Console:")
    print()
    print("1. 🌐 Go to: https://console.cloud.google.com")
    print("2. 📁 Select project: dreamframe")
    print("3. 🔍 Search for: Vertex AI")
    print("4. 📊 Go to: Model Garden → Operations")
    print("5. 🎬 Look for: VEO operations")
    print()
    print("🔍 Your Operation IDs:")
    for op_id, description in operations:
        print(f"   • {description}: {op_id}")
    print()
    print("✅ When Complete:")
    print("   • Status will show 'Succeeded'")
    print("   • Click operation to see video download link")
    print("   • Videos are in MP4 format, ready to download")
    print()
    print("⏰ Typical completion time: 5-15 minutes")
    print("📱 Automated system will show videos once complete")

if __name__ == "__main__":
    show_manual_instructions()