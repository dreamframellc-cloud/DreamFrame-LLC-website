#!/usr/bin/env python3
"""
Generate placeholder thumbnail images for the video gallery
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_thumbnail(filename, title, bg_color, text_color=(255, 255, 255)):
    """Create a thumbnail image with title text"""
    # Create image
    width, height = 300, 170
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Try to use a better font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw title centered
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = height - 50
    draw.text((x, y), title, fill=text_color, font=font)
    
    # Draw "VIDEO" label
    draw.text((15, 15), "VIDEO", fill=text_color, font=small_font)
    
    return img

def main():
    # Create thumbnails directory if it doesn't exist
    os.makedirs('static/thumbnails', exist_ok=True)
    
    # Define thumbnails to create
    thumbnails = [
        ('Thumbnail.avatar.jpeg', 'Avatar Intro', (102, 126, 234)),
        ('Thumbnail.siblings.jpeg', 'Siblings Memories', (16, 185, 129)),
        ('Thumbnail.client1.jpeg', 'Client Project 1', (220, 38, 127)),
        ('Thumbnail.client2.jpeg', 'Client Project 2', (139, 69, 19)),
        ('Thumbnail.feature.jpeg', 'Feature Production', (186, 85, 211))
    ]
    
    for filename, title, bg_color in thumbnails:
        img = create_thumbnail(filename, title, bg_color)
        filepath = os.path.join('static/thumbnails', filename)
        img.save(filepath, 'JPEG', quality=85)
        print(f"Created {filepath}")

if __name__ == '__main__':
    main()