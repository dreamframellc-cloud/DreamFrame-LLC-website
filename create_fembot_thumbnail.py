#!/usr/bin/env python3
"""
Create a futuristic fembot-themed thumbnail
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_fembot_thumbnail():
    """Create a futuristic robot-themed thumbnail"""
    # Create image with futuristic tech theme
    width, height = 300, 170
    # Dark blue/purple gradient background
    img = Image.new('RGB', (width, height), (15, 15, 30))
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(height):
        blue_val = int(15 + (y / height) * 50)  # 15 to 65
        color = (15, 15, blue_val)
        draw.line([(0, y), (width, y)], fill=color)
    
    # Try to use a better font, fallback to default
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # Draw title centered with futuristic styling
    title = "FEMBOT1"
    bbox = draw.textbbox((0, 0), title, font=font)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = height - 60
    
    # Draw text with blue glow effect
    for offset in range(2):
        draw.text((x-offset, y-offset), title, fill=(0, 100, 200), font=font)
    draw.text((x, y), title, fill=(100, 200, 255), font=font)
    
    # Draw "VIDEO" label
    draw.text((15, 15), "VIDEO", fill=(200, 200, 255), font=small_font)
    
    # Add some tech elements - circuit lines
    for i in range(4):
        x1, y1 = 30 + i * 60, 40
        x2, y2 = x1 + 40, y1
        draw.line([(x1, y1), (x2, y2)], fill=(0, 150, 255), width=2)
        draw.rectangle([(x2-5, y1-3), (x2+5, y1+3)], fill=(100, 200, 255))
    
    return img

if __name__ == "__main__":
    # Create thumbnails directory if it doesn't exist
    os.makedirs('static/thumbnails', exist_ok=True)
    
    # Create fembot thumbnail
    img = create_fembot_thumbnail()
    filepath = os.path.join('static/thumbnails', 'Fembot_thumbnail.jpg')
    img.save(filepath, 'JPEG', quality=95)
    print(f"Created fembot thumbnail: {filepath}")