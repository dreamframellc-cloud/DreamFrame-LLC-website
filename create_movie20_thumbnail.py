#!/usr/bin/env python3
"""
Create a custom thumbnail for My Movie 20
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_movie20_thumbnail():
    # Create a 300x200 thumbnail
    width, height = 300, 200
    
    # Create gradient background
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Create gradient effect
    for y in range(height):
        # Purple to blue gradient
        r = int(26 + (102 - 26) * (y / height))  # 1a to 66
        g = int(26 + (126 - 26) * (y / height))  # 1a to 7e
        b = int(46 + (234 - 46) * (y / height))  # 2e to ea
        
        for x in range(width):
            draw.point((x, y), fill=(r, g, b))
    
    # Add title text
    try:
        # Try to use a system font
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except:
        # Fallback to default font
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Add main title
    title = "My Movie 20"
    bbox = draw.textbbox((0, 0), title, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2 - 10
    
    # Add text shadow
    draw.text((x+2, y+2), title, fill=(0, 0, 0, 128), font=font_large)
    # Add main text
    draw.text((x, y), title, fill='white', font=font_large)
    
    # Add subtitle
    subtitle = "Personal Video"
    bbox = draw.textbbox((0, 0), subtitle, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (width - text_width) // 2
    y = y + 50
    
    draw.text((x, y), subtitle, fill='#cccccc', font=font_small)
    
    # Add decorative elements
    # Draw some circles for visual interest
    draw.ellipse([20, 20, 40, 40], fill=(255, 255, 255, 50))
    draw.ellipse([260, 160, 280, 180], fill=(255, 255, 255, 30))
    
    # Save the thumbnail
    output_path = 'static/thumbnails/My_Movie_20_thumbnail.jpg'
    img.save(output_path, 'JPEG', quality=85)
    print(f"Created thumbnail: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_movie20_thumbnail()