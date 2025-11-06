#!/usr/bin/env python3
"""Verify the downloaded videos contain correct content"""

import hashlib
import os

def get_file_hash(filepath):
    """Get MD5 hash of file to verify content"""
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def compare_videos():
    """Compare downloaded videos with source gallery videos"""
    
    # Original gallery videos
    videogram_hash = get_file_hash('static/videos/VideoGram.mp4') if os.path.exists('static/videos/VideoGram.mp4') else None
    dragon_hash = get_file_hash('static/videos/Dragon.mp4') if os.path.exists('static/videos/Dragon.mp4') else None
    memories_hash = get_file_hash('static/videos/Memories.mp4') if os.path.exists('static/videos/Memories.mp4') else None
    
    # Downloaded test videos
    lion_hash = get_file_hash('lion_test.mp4') if os.path.exists('lion_test.mp4') else None
    kindness_hash = get_file_hash('kindness_test.mp4') if os.path.exists('kindness_test.mp4') else None
    
    print("=== Video Content Verification ===")
    print(f"VideoGram.mp4 hash: {videogram_hash}")
    print(f"Dragon.mp4 hash: {dragon_hash}")
    print(f"Memories.mp4 hash: {memories_hash}")
    print()
    print(f"Lion of Judah download hash: {lion_hash}")
    print(f"Kindness download hash: {kindness_hash}")
    print()
    
    # Check if Lion of Judah uses Dragon video (expected)
    if lion_hash == dragon_hash:
        print("✅ Lion of Judah correctly uses Dragon.mp4 (majestic creature)")
    elif lion_hash == videogram_hash:
        print("❌ Lion of Judah incorrectly uses VideoGram.mp4 (placeholder)")
    else:
        print("❓ Lion of Judah uses unknown video content")
    
    # Check if kindness uses Memories video (expected)  
    if kindness_hash == memories_hash:
        print("✅ Kindness correctly uses Memories.mp4 (human connection)")
    elif kindness_hash == videogram_hash:
        print("❌ Kindness incorrectly uses VideoGram.mp4 (placeholder)")
    else:
        print("❓ Kindness uses unknown video content")

if __name__ == "__main__":
    compare_videos()