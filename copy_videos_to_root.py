#!/usr/bin/env python3
"""
Copy videos to root directory for direct access
"""

import shutil
import os

def copy_videos():
    """Copy videos to root directory with simple names"""
    
    # Copy videos to root with simple names
    if os.path.exists('static/lion_customer.mp4'):
        shutil.copy2('static/lion_customer.mp4', 'lion_video.mp4')
        print("✅ Copied lion_video.mp4 to root")
    
    if os.path.exists('static/kindness_customer.mp4'):
        shutil.copy2('static/kindness_customer.mp4', 'kindness_video.mp4')
        print("✅ Copied kindness_video.mp4 to root")
    
    # Create simple download links
    with open('download_links.txt', 'w') as f:
        f.write("Direct Download Links:\n")
        f.write("====================\n\n")
        f.write("Lion Video: lion_video.mp4\n")
        f.write("Kindness Video: kindness_video.mp4\n\n")
        f.write("Instructions:\n")
        f.write("1. Right-click on file in file browser\n")
        f.write("2. Select 'Download' or 'Save As'\n")
        f.write("3. Or drag file to desktop\n")
    
    print("✅ Created download_links.txt with instructions")

if __name__ == "__main__":
    copy_videos()