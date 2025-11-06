#!/usr/bin/env python3
"""
Test direct download functionality
"""

import os

# Check if videos exist and their sizes
files_to_check = [
    'static/completed_videos/DreamFrame_7_Lion_of_Judah.mp4',
    'static/completed_videos/DreamFrame_8_kindness.mp4',
    'static/lion_customer.mp4',
    'static/kindness_customer.mp4',
    'lion_video.mp4',
    'kindness_video.mp4'
]

print("=== FILE STATUS CHECK ===")
for file_path in files_to_check:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"✅ {file_path}: {size} bytes")
    else:
        print(f"❌ {file_path}: NOT FOUND")

print("\n=== DIRECT ACCESS URLS ===")
print("Try these direct URLs:")
print("1. Lion video: /static/completed_videos/DreamFrame_7_Lion_of_Judah.mp4")
print("2. Kindness video: /static/completed_videos/DreamFrame_8_kindness.mp4")
print("3. Copy URL and paste in new tab")
print("4. Right-click -> Save As")