#!/usr/bin/env python3
"""
Create direct static file links that bypass all Flask routing
"""

import os
import shutil
import hashlib

def create_direct_links():
    """Create direct downloadable files with simple names"""
    
    # Source files
    lion_source = "static/completed_videos/DreamFrame_7_Lion_of_Judah.mp4"
    kindness_source = "static/completed_videos/DreamFrame_8_kindness.mp4"
    
    # Direct static links (simple names)
    lion_direct = "static/lion_customer.mp4"
    kindness_direct = "static/kindness_customer.mp4"
    
    print("=== CREATING DIRECT CUSTOMER DOWNLOAD LINKS ===")
    
    # Copy Lion video
    if os.path.exists(lion_source):
        shutil.copy2(lion_source, lion_direct)
        size = os.path.getsize(lion_direct)
        with open(lion_direct, 'rb') as f:
            hash_val = hashlib.md5(f.read()).hexdigest()
        print(f"✅ Lion Customer Video: {size} bytes, MD5: {hash_val}")
        print(f"   Direct link: /static/lion_customer.mp4")
    
    # Copy Kindness video
    if os.path.exists(kindness_source):
        shutil.copy2(kindness_source, kindness_direct)
        size = os.path.getsize(kindness_direct)
        with open(kindness_direct, 'rb') as f:
            hash_val = hashlib.md5(f.read()).hexdigest()
        print(f"✅ Kindness Customer Video: {size} bytes, MD5: {hash_val}")
        print(f"   Direct link: /static/kindness_customer.mp4")
    
    return True

if __name__ == "__main__":
    create_direct_links()