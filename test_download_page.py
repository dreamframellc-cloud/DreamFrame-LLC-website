#!/usr/bin/env python3
"""
Create a simple test download page with working videos
"""

import os

def create_simple_download_page():
    """Create a simple HTML download page"""
    
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Customer Video Downloads</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #1a1a1a; color: white; }
        .video-section { margin: 30px 0; padding: 20px; border: 1px solid #333; }
        video { width: 100%; max-width: 640px; height: auto; }
        .download-btn { 
            background: #4CAF50; color: white; padding: 10px 20px; 
            text-decoration: none; border-radius: 5px; margin: 10px 5px;
            display: inline-block;
        }
        .download-btn:hover { background: #45a049; }
    </style>
</head>
<body>
    <h1>🎬 Customer Video Downloads</h1>
    
    <div class="video-section">
        <h2>Lion of Judah Video</h2>
        <video controls>
            <source src="/lion_test.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <br>
        <a href="/lion_test.mp4" download="Lion_of_Judah_Customer_Video.mp4" class="download-btn">Download Lion Video</a>
        <a href="/lion_test.mp4" target="_blank" class="download-btn">Open in New Tab</a>
    </div>
    
    <div class="video-section">
        <h2>Kindness Video</h2>
        <video controls>
            <source src="/kindness_test.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
        <br>
        <a href="/kindness_test.mp4" download="Kindness_Customer_Video.mp4" class="download-btn">Download Kindness Video</a>
        <a href="/kindness_test.mp4" target="_blank" class="download-btn">Open in New Tab</a>
    </div>
    
    <div class="video-section">
        <h3>Technical Details:</h3>
        <p>• Lion video: 108KB, 8 seconds, generated from customer's lion image</p>
        <p>• Kindness video: 89KB, 5 seconds, generated from customer's portrait</p>
        <p>• Both videos are H.264 MP4 format with no audio</p>
        <p>• Direct file access: Right-click → Save As</p>
    </div>
</body>
</html>
    """
    
    with open('templates/simple_download.html', 'w') as f:
        f.write(html_content)
    
    print("✅ Created simple download test page")

if __name__ == "__main__":
    create_simple_download_page()