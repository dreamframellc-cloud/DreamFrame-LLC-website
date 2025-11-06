#!/usr/bin/env python3
"""
Create a horror-themed thumbnail for the Horror video
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_horror_thumbnail():
    """Create a dark horror-themed thumbnail"""
    # Create image with dark horror theme
    width, height = 300, 170
    # Dark red/black gradient background
    img = Image.new('RGB', (width, height), (20, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(height):
        darkness = int(20 + (y / height) * 40)  # 20 to 60
        color = (darkness, 0, 0)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Try to use a better font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw title centered with horror styling
    title = "HORROR"
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = height - 60
    
    # Draw text with red glow effect
    for offset in range(3):
        draw.text((x-offset, y-offset), title, fill=(150, 0, 0), font=font)
    draw.text((x, y), title, fill=(255, 50, 50), font=font)
    
    # Draw "VIDEO" label
    draw.text((15, 15), "VIDEO", fill=(200, 200, 200), font=small_font)
    
    # Add some horror elements - jagged lines
    for i in range(5):
        x1, y1 = 50 + i * 40, 30 + i * 5
        x2, y2 = x1 + 30, y1 + 15
        draw.line([(x1, y1), (x2, y2)], fill=(100, 0, 0), width=2)
    
    return img

if __name__ == "__main__":
    # Create thumbnails directory if it doesn't exist
    os.makedirs('static/thumbnails', exist_ok=True)
    
    # Create horror thumbnail
    img = create_horror_thumbnail()
    filepath = os.path.join('static/thumbnails', 'Horror_thumbnail.jpeg')
    img.save(filepath, 'JPEG', quality=95)
    print(f"Created horror thumbnail: {filepath}")