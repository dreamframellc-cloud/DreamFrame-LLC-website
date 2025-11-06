#!/usr/bin/env python3
"""
System Status - DreamFrame VEO 2 video generation platform
"""

import os
import subprocess

def verify_leonardo_removal():
    """Verify all Leonardo AI references have been removed"""
    
    print("🗑️ Verifying Leonardo AI Removal")
    print("=" * 50)
    
    # Check for remaining Leonardo references
    try:
        result = subprocess.run(
            ['grep', '-r', '-i', 'leonardo', '--include=*.py', '.'],
            capture_output=True, text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("⚠️ Found remaining Leonardo AI references:")
            print(result.stdout)
            return False
        else:
            print("✅ No Leonardo AI references found in Python files")
    except Exception as e:
        print(f"Error checking files: {e}")
    
    # Check for Leonardo-related files
    leonardo_files = [
        'fixed_leonardo_animator.py',
        'leonardo_ai_integration.py',
        'leonardo_motion_generator.py'
    ]
    
    remaining_files = []
    for file in leonardo_files:
        if os.path.exists(file):
            remaining_files.append(file)
    
    if remaining_files:
        print(f"⚠️ Found Leonardo AI files: {remaining_files}")
        return False
    else:
        print("✅ No Leonardo AI files found")
    
    print("\n🎬 Current Video Generation Stack:")
    print("   Primary: VEO 2 (Google)")
    print("   Fallback: VEO 3 (Google)")
    print("   Final Fallback: Hybrid Computer Vision")
    print("   Leonardo AI: COMPLETELY REMOVED")
    
    return True

def get_current_video_systems():
    """Show current video generation systems"""
    
    systems = {
        'VEO 2': 'Primary motion video generation',
        'VEO 3': 'Advanced video generation fallback',
        'Hybrid CV': 'Computer vision final fallback',
        'Leonardo AI': 'REMOVED BY USER REQUEST'
    }
    
    return systems

if __name__ == "__main__":
    print("🎬 DreamFrame Video Generation Stack")
    print("=" * 60)
    
    # Verify removal
    is_clean = verify_leonardo_removal()
    
    if is_clean:
        print("\n✅ SUCCESS: Leonardo AI completely removed from platform")
        print("🎬 DreamFrame now uses VEO 2 exclusively for video generation")
    else:
        print("\n⚠️ Some Leonardo AI references may still exist")
    
    # Show current systems
    print("\n📊 Current Video Generation Systems:")
    systems = get_current_video_systems()
    for system, description in systems.items():
        status_icon = "❌" if "REMOVED" in description else "✅"
        print(f"   {status_icon} {system}: {description}")
    
    print("\n🎯 Platform optimized for VEO 2 motion video generation")