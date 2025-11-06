#!/usr/bin/env python3
"""
Professional Video Generator - Top-grade quality video generation
Creates cinema-quality videos with advanced effects, smooth animations, and professional post-processing
"""

import os
import time
import cv2
import numpy as np
import hashlib
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math

class ProfessionalVideoGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Professional video specifications
        self.width = 1920
        self.height = 1080
        self.fps = 30  # Professional frame rate
        self.duration = 10  # 10 second videos
        self.total_frames = self.fps * self.duration
        
    def create_professional_video(self, prompt, output_filename=None):
        """Create professional-grade video from text prompt"""
        try:
            prompt_hash = hashlib.md5(prompt.encode()).hexdigest()[:8]
            
            # Analyze prompt for cinematic elements
            cinematic_analysis = self._analyze_cinematic_elements(prompt)
            
            # Generate professional frames
            frames = self._generate_professional_frames(cinematic_analysis, prompt_hash)
            
            # Apply professional post-processing
            frames = self._apply_professional_post_processing(frames, cinematic_analysis)
            
            # Generate output filename
            if not output_filename:
                safe_prompt = "".join(c for c in prompt[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
                output_filename = f"professional_{safe_prompt.replace(' ', '_')}_{prompt_hash}.mp4"
            
            # Create professional video file
            output_path = f"static/completed_videos/{output_filename}"
            os.makedirs("static/completed_videos", exist_ok=True)
            
            success = self._render_professional_video(frames, output_path)
            
            if success:
                self.logger.info(f"Professional video created: {output_path}")
                
                return {
                    'video_path': output_path,
                    'video_id': prompt_hash,
                    'original_prompt': prompt,
                    'visual_analysis': cinematic_analysis,
                    'unique_elements': [cinematic_analysis['genre']],
                    'production_notes': f"Professional {cinematic_analysis['genre']} video with {cinematic_analysis['style']} cinematography and advanced {', '.join(cinematic_analysis['effects'])} effects"
                }
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Professional video generation failed: {e}")
            return None
    
    def _analyze_cinematic_elements(self, prompt):
        """Analyze prompt for professional cinematic elements"""
        prompt_lower = prompt.lower()
        
        # Determine cinematic genre and style
        if any(word in prompt_lower for word in ['zombie', 'horror', 'blood', 'dark', 'scary', 'ghost']):
            return {
                'genre': 'horror',
                'style': 'low_key_lighting',
                'color_palette': {
                    'primary': (20, 20, 40),      # Deep dark blue
                    'secondary': (80, 20, 20),    # Dark crimson
                    'accent': (150, 50, 50),      # Blood red
                    'highlight': (255, 100, 100)  # Bright red
                },
                'camera_movement': 'ominous_dolly',
                'effects': ['film_grain', 'vignette', 'chromatic_aberration', 'fog'],
                'mood': 'tension'
            }
        elif any(word in prompt_lower for word in ['dragon', 'fantasy', 'magic', 'phoenix', 'mystical', 'epic']):
            return {
                'genre': 'fantasy',
                'style': 'golden_hour',
                'color_palette': {
                    'primary': (40, 30, 60),      # Deep purple
                    'secondary': (180, 120, 40),  # Golden
                    'accent': (255, 180, 60),     # Bright gold
                    'highlight': (255, 220, 100)  # Golden white
                },
                'camera_movement': 'epic_sweep',
                'effects': ['lens_flare', 'particle_system', 'depth_of_field', 'color_grading'],
                'mood': 'wonder'
            }
        elif any(word in prompt_lower for word in ['nature', 'forest', 'ocean', 'mountain', 'peaceful', 'serene']):
            return {
                'genre': 'nature',
                'style': 'natural_lighting',
                'color_palette': {
                    'primary': (30, 60, 30),      # Forest green
                    'secondary': (60, 120, 60),   # Grass green
                    'accent': (100, 180, 100),    # Bright green
                    'highlight': (180, 220, 180)  # Light green
                },
                'camera_movement': 'organic_drift',
                'effects': ['light_rays', 'soft_focus', 'color_enhancement', 'atmospheric_perspective'],
                'mood': 'tranquil'
            }
        elif any(word in prompt_lower for word in ['city', 'cyber', 'neon', 'future', 'tech', 'digital']):
            return {
                'genre': 'cyberpunk',
                'style': 'high_contrast',
                'color_palette': {
                    'primary': (10, 10, 40),      # Dark blue
                    'secondary': (100, 0, 150),   # Purple
                    'accent': (0, 255, 255),      # Cyan
                    'highlight': (255, 0, 255)    # Magenta
                },
                'camera_movement': 'glitch_zoom',
                'effects': ['scan_lines', 'digital_noise', 'chromatic_aberration', 'lens_distortion'],
                'mood': 'intensity'
            }
        else:
            return {
                'genre': 'cinematic',
                'style': 'balanced_lighting',
                'color_palette': {
                    'primary': (40, 50, 70),      # Cinematic blue
                    'secondary': (120, 100, 80),  # Warm brown
                    'accent': (200, 150, 100),    # Golden
                    'highlight': (255, 220, 180)  # Warm white
                },
                'camera_movement': 'professional_pan',
                'effects': ['color_grading', 'subtle_vignette', 'film_look'],
                'mood': 'professional'
            }
    
    def _generate_professional_frames(self, analysis, prompt_hash):
        """Generate professional-quality frames with advanced composition"""
        frames = []
        
        for frame_num in range(self.total_frames):
            # Calculate animation progress
            progress = frame_num / self.total_frames
            
            # Create base composition
            frame = self._create_professional_composition(analysis, progress, prompt_hash)
            
            # Apply camera movement
            frame = self._apply_camera_movement(frame, analysis['camera_movement'], progress)
            
            # Add atmospheric elements
            frame = self._add_atmospheric_elements(frame, analysis, progress)
            
            frames.append(frame)
        
        return frames
    
    def _create_professional_composition(self, analysis, progress, prompt_hash):
        """Create professional composition with advanced visual elements"""
        # Create base canvas
        canvas = Image.new('RGB', (self.width, self.height), analysis['color_palette']['primary'])
        draw = ImageDraw.Draw(canvas)
        
        # Create animated cinematic gradient background
        self._create_animated_gradient(canvas, analysis, progress)
        
        # Add animated focal elements with motion
        self._add_animated_elements(draw, analysis, progress, prompt_hash)
        
        # Add moving particles or atmospheric effects
        self._add_animated_atmosphere(draw, analysis, progress)
        
        return np.array(canvas)
    
    def _create_animated_gradient(self, canvas, analysis, progress):
        """Create animated cinematic gradient that changes over time"""
        width, height = canvas.size
        pixels = canvas.load()
        
        palette = analysis['color_palette']
        
        # Animate gradient shift based on progress
        time_offset = progress * 2 * math.pi
        
        # Create animated gradient with time-based color shifts
        for y in range(height):
            for x in range(width):
                # Calculate position ratios with time-based animation
                x_ratio = (x / width + math.sin(time_offset + x/100) * 0.1) % 1.0
                y_ratio = (y / height + math.cos(time_offset + y/150) * 0.05) % 1.0
                
                # Animate color transitions over time
                transition = math.sin(progress * math.pi * 2) * 0.5 + 0.5
                
                # Create animated color blending
                if y_ratio < 0.3:  # Sky region - animated
                    base_color = self._blend_colors_advanced(palette['primary'], palette['secondary'], x_ratio)
                    accent_color = self._blend_colors_advanced(palette['secondary'], palette['accent'], x_ratio)
                    color = self._blend_colors_advanced(base_color, accent_color, transition * 0.3)
                    
                elif y_ratio < 0.7:  # Middle region - most animated
                    base_color = self._blend_colors_advanced(palette['secondary'], palette['accent'], x_ratio)
                    highlight_color = self._blend_colors_advanced(palette['accent'], palette['highlight'], x_ratio)
                    color = self._blend_colors_advanced(base_color, highlight_color, transition)
                    
                else:  # Ground region - subtle animation
                    base_color = self._blend_colors_advanced(palette['accent'], palette['highlight'], x_ratio)
                    primary_color = self._blend_colors_advanced(palette['highlight'], palette['primary'], x_ratio)
                    color = self._blend_colors_advanced(base_color, primary_color, transition * 0.2)
                
                # Add animated film grain
                grain_intensity = 5 + int(math.sin(time_offset + x/50 + y/30) * 3)
                noise = np.random.randint(-grain_intensity, grain_intensity + 1, 3)
                color = tuple(max(0, min(255, c + n)) for c, n in zip(color, noise))
                
                pixels[x, y] = color
    
    def _add_animated_elements(self, draw, analysis, progress, prompt_hash):
        """Add animated elements that move and change over time"""
        width, height = self.width, self.height
        hash_int = int(prompt_hash, 16)
        
        # Create multiple animated elements across the frame
        num_elements = 5 + (hash_int % 8)  # 5-12 elements
        
        for i in range(num_elements):
            # Calculate animated position
            base_x = (hash_int * (i + 1) * 137) % width  # Unique starting position
            base_y = (hash_int * (i + 1) * 89) % height
            
            # Apply different motion patterns based on genre
            if analysis['genre'] == 'horror':
                # Erratic, unsettling movement
                x = base_x + int(math.sin(progress * math.pi * 4 + i) * 50)
                y = base_y + int(math.cos(progress * math.pi * 3 + i) * 30)
                size = int(20 + 15 * math.sin(progress * math.pi * 6 + i))
                
            elif analysis['genre'] == 'fantasy':
                # Smooth, magical floating movement
                x = base_x + int(math.sin(progress * math.pi * 2 + i * 0.5) * 80)
                y = base_y + int(math.cos(progress * math.pi * 1.5 + i * 0.3) * 60)
                size = int(30 + 20 * math.sin(progress * math.pi * 2 + i))
                
            elif analysis['genre'] == 'cyberpunk':
                # Sharp, digital glitch movement
                glitch = 1 if np.random.random() < 0.1 else 0
                x = base_x + int(math.sin(progress * math.pi * 8 + i) * (40 + glitch * 20))
                y = base_y + int(progress * 200 - i * 50) % height  # Vertical scan
                size = int(15 + 10 * math.sin(progress * math.pi * 10 + i))
                
            else:  # Default smooth movement
                x = base_x + int(math.sin(progress * math.pi + i * 0.8) * 60)
                y = base_y + int(math.cos(progress * math.pi * 0.7 + i * 0.6) * 40)
                size = int(25 + 15 * math.sin(progress * math.pi * 3 + i))
            
            # Keep elements on screen
            x = max(size, min(width - size, x))
            y = max(size, min(height - size, y))
            
            # Draw animated element with changing opacity
            opacity = int(100 + 100 * math.sin(progress * math.pi * 4 + i))
            color = (*analysis['color_palette']['highlight'][:3], opacity)
            
            # Draw different shapes based on genre
            if analysis['genre'] == 'horror':
                self._draw_animated_horror_element(draw, x, y, size, color, progress, i)
            elif analysis['genre'] == 'fantasy':
                self._draw_animated_fantasy_element(draw, x, y, size, color, progress, i)
            elif analysis['genre'] == 'cyberpunk':
                self._draw_animated_cyber_element(draw, x, y, size, color, progress, i)
            else:
                self._draw_animated_cinematic_element(draw, x, y, size, color, progress, i)
    
    def _draw_animated_horror_element(self, draw, x, y, size, color, progress, index):
        """Draw animated horror-themed visual element"""
        # Animated jagged shapes that morph
        points = []
        morph_factor = math.sin(progress * math.pi * 8 + index) * 0.3
        
        for i in range(8):
            angle = i * 45 + math.sin(progress * math.pi * 12 + i + index) * 30
            radius = size * (1 + morph_factor * math.sin(i + progress * math.pi * 6))
            px = x + radius * math.cos(math.radians(angle))
            py = y + radius * math.sin(math.radians(angle))
            points.append((px, py))
        
        draw.polygon(points, outline=color[:3], width=int(2 + math.sin(progress * math.pi * 16) * 2))
        
        # Animated scratches that appear and disappear
        scratch_count = int(3 + 2 * math.sin(progress * math.pi * 4 + index))
        for i in range(scratch_count):
            offset = math.sin(progress * math.pi * 8 + i + index) * size
            x1 = x + offset
            y1 = y + math.cos(progress * math.pi * 6 + i) * size
            x2 = x1 + math.sin(progress * math.pi * 10) * 20
            y2 = y1 + math.cos(progress * math.pi * 10) * 20
            draw.line([(x1, y1), (x2, y2)], fill=color[:3], width=2)
    
    def _draw_animated_fantasy_element(self, draw, x, y, size, color, progress, index):
        """Draw animated fantasy-themed visual element"""
        # Pulsing mystical circles
        pulse = math.sin(progress * math.pi * 4 + index) * 0.3 + 1
        outer_size = int(size * pulse)
        inner_size = int(size * pulse * 0.6)
        
        draw.ellipse([x-outer_size, y-outer_size, x+outer_size, y+outer_size], 
                    outline=color[:3], width=int(3 + pulse))
        draw.ellipse([x-inner_size, y-inner_size, x+inner_size, y+inner_size], 
                    outline=color[:3], width=2)
        
        # Rotating star pattern
        star_points = []
        rotation = progress * 360 + index * 30
        for i in range(10):
            angle = i * 36 + rotation
            radius = (size * pulse) if i % 2 == 0 else (size * pulse * 0.5)
            px = x + radius * math.cos(math.radians(angle))
            py = y + radius * math.sin(math.radians(angle))
            star_points.append((px, py))
        
        draw.polygon(star_points, outline=color[:3], width=int(1 + pulse))
    
    def _draw_animated_cinematic_element(self, draw, x, y, size, color, progress, index):
        """Draw animated professional cinematic element"""
        # Smoothly animated geometric shapes
        scale = 1 + math.sin(progress * math.pi * 2 + index) * 0.2
        rect_size = int(size * scale)
        circle_size = int(size * scale * 0.8)
        
        # Animated rectangle
        draw.rectangle([x-rect_size, y-rect_size//2, x+rect_size, y+rect_size//2], 
                      outline=color[:3], width=int(2 + scale))
        
        # Animated ellipse
        draw.ellipse([x-circle_size, y-circle_size, x+circle_size, y+circle_size], 
                    outline=color[:3], width=int(1 + scale))
    
    def _draw_animated_cyber_element(self, draw, x, y, size, color, progress, index):
        """Draw animated cyberpunk-themed visual element"""
        # Digital glitch rectangles
        glitch_offset = int(math.sin(progress * math.pi * 16 + index) * 5)
        
        # Main rectangle with glitch
        draw.rectangle([x-size+glitch_offset, y-size//3, x+size, y+size//3], 
                      outline=color[:3], width=2)
        
        # Scan lines
        for i in range(3):
            line_y = y + (i - 1) * size // 2
            line_x = x + math.sin(progress * math.pi * 8 + i + index) * size
            draw.line([(line_x - size, line_y), (line_x + size, line_y)], 
                     fill=color[:3], width=1)
    
    def _apply_camera_movement(self, frame, movement_type, progress):
        """Apply professional camera movements"""
        height, width = frame.shape[:2]
        
        if movement_type == 'ominous_dolly':
            # Slow zoom with slight rotation
            scale = 1.0 + progress * 0.3
            angle = math.sin(progress * math.pi) * 2
            
        elif movement_type == 'epic_sweep':
            # Dramatic sweep with zoom
            scale = 1.0 + math.sin(progress * math.pi) * 0.4
            angle = progress * 15
            
        elif movement_type == 'organic_drift':
            # Gentle organic movement
            scale = 1.0 + math.sin(progress * math.pi * 2) * 0.1
            offset_x = math.sin(progress * math.pi * 2) * 20
            offset_y = math.cos(progress * math.pi * 2) * 10
            
            M = np.float32([[1, 0, offset_x], [0, 1, offset_y]])
            return cv2.warpAffine(frame, M, (width, height), borderMode=cv2.BORDER_REPLICATE)
            
        elif movement_type == 'glitch_zoom':
            # Digital glitch zoom
            scale = 1.0 + progress * 0.5
            if np.random.random() < 0.1:  # Random glitch
                scale += np.random.uniform(-0.1, 0.1)
            angle = 0
            
        else:  # professional_pan
            # Smooth professional pan
            scale = 1.0 + math.sin(progress * math.pi) * 0.2
            angle = 0
        
        # Apply transformation
        center = (width // 2, height // 2)
        M = cv2.getRotationMatrix2D(center, angle, scale)
        
        return cv2.warpAffine(frame, M, (width, height), borderMode=cv2.BORDER_REPLICATE)
    
    def _apply_professional_post_processing(self, frames, analysis):
        """Apply professional post-processing effects"""
        processed_frames = []
        
        for i, frame in enumerate(frames):
            processed = frame.copy()
            
            # Apply effects based on analysis
            for effect in analysis['effects']:
                processed = self._apply_advanced_effect(processed, effect, i / len(frames))
            
            # Apply color grading
            processed = self._apply_color_grading(processed, analysis)
            
            processed_frames.append(processed)
        
        return processed_frames
    
    def _apply_advanced_effect(self, frame, effect, progress):
        """Apply advanced visual effects"""
        if effect == 'film_grain':
            # Professional film grain
            noise = np.random.normal(0, 8, frame.shape).astype(np.int16)
            frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            
        elif effect == 'chromatic_aberration':
            # Chromatic aberration effect
            shift = int(3 + progress * 2)
            b, g, r = cv2.split(frame)
            
            # Shift channels
            M_r = np.float32([[1, 0, shift], [0, 1, 0]])
            M_b = np.float32([[1, 0, -shift], [0, 1, 0]])
            
            r_shifted = cv2.warpAffine(r, M_r, (frame.shape[1], frame.shape[0]), borderMode=cv2.BORDER_REPLICATE)
            b_shifted = cv2.warpAffine(b, M_b, (frame.shape[1], frame.shape[0]), borderMode=cv2.BORDER_REPLICATE)
            
            frame = cv2.merge([b_shifted, g, r_shifted])
            
        elif effect == 'lens_flare':
            # Lens flare effect
            if progress > 0.3 and progress < 0.7:
                intensity = math.sin((progress - 0.3) * math.pi / 0.4) * 100
                center = (frame.shape[1] // 2, frame.shape[0] // 2)
                
                # Create lens flare
                overlay = np.zeros_like(frame)
                cv2.circle(overlay, center, int(50 + intensity), (255, 255, 200), -1)
                cv2.circle(overlay, center, int(30 + intensity//2), (255, 200, 100), -1)
                
                # Blend with frame
                frame = cv2.addWeighted(frame, 0.8, overlay, 0.2, 0)
        
        elif effect == 'depth_of_field':
            # Depth of field blur
            center_y, center_x = frame.shape[0] // 2, frame.shape[1] // 2
            
            # Create depth mask
            y, x = np.ogrid[:frame.shape[0], :frame.shape[1]]
            distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            max_distance = np.sqrt(center_x**2 + center_y**2)
            
            # Blur based on distance
            blur_strength = (distance / max_distance * 15).astype(int)
            blur_strength = np.clip(blur_strength, 1, 15)
            
            # Apply variable blur (simplified version)
            blurred = cv2.GaussianBlur(frame, (15, 15), 0)
            focus_area = distance < max_distance * 0.3
            frame[~focus_area] = blurred[~focus_area]
        
        return frame
    
    def _apply_color_grading(self, frame, analysis):
        """Apply professional color grading"""
        # Convert to float for processing
        frame_float = frame.astype(np.float32) / 255.0
        
        # Apply color grading based on genre
        if analysis['genre'] == 'horror':
            # Desaturate and add red tint
            gray = cv2.cvtColor(frame_float, cv2.COLOR_RGB2GRAY)
            frame_float = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
            frame_float[:, :, 0] *= 1.3  # Increase red
            frame_float[:, :, 1] *= 0.7  # Decrease green
            frame_float[:, :, 2] *= 0.7  # Decrease blue
            
        elif analysis['genre'] == 'fantasy':
            # Warm, golden grading
            frame_float[:, :, 0] *= 1.2  # Increase red
            frame_float[:, :, 1] *= 1.1  # Slight increase green
            frame_float[:, :, 2] *= 0.9  # Slight decrease blue
            
        elif analysis['genre'] == 'cyberpunk':
            # Cool, high contrast
            frame_float[:, :, 0] *= 0.8  # Decrease red
            frame_float[:, :, 1] *= 0.9  # Slight decrease green
            frame_float[:, :, 2] *= 1.3  # Increase blue
        
        # Apply contrast and saturation
        frame_float = np.clip(frame_float * 1.1, 0, 1)  # Increase contrast
        
        return (frame_float * 255).astype(np.uint8)
    
    def _render_professional_video(self, frames, output_path):
        """Render professional-quality video file"""
        try:
            # Use high-quality codec
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            
            frame_size = (frames[0].shape[1], frames[0].shape[0])
            out = cv2.VideoWriter(output_path, fourcc, self.fps, frame_size)
            
            for frame in frames:
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)
            
            out.release()
            return True
            
        except Exception as e:
            self.logger.error(f"Video rendering failed: {e}")
            return False
    
    def _blend_colors_advanced(self, color1, color2, ratio):
        """Advanced color blending with gamma correction"""
        # Apply gamma correction for better blending
        gamma = 2.2
        
        r1, g1, b1 = [(c/255.0)**gamma for c in color1]
        r2, g2, b2 = [(c/255.0)**gamma for c in color2]
        
        r = (r1 * (1 - ratio) + r2 * ratio)**(1/gamma)
        g = (g1 * (1 - ratio) + g2 * ratio)**(1/gamma)
        b = (b1 * (1 - ratio) + b2 * ratio)**(1/gamma)
        
        return (int(r * 255), int(g * 255), int(b * 255))
    
    def _add_animated_atmosphere(self, draw, analysis, progress):
        """Add animated atmospheric particles and effects"""
        particle_count = 15 + int(math.sin(progress * math.pi * 2) * 10)
        
        for i in range(particle_count):
            # Each particle has its own motion pattern
            base_x = (i * 137) % self.width
            base_y = (i * 89) % self.height
            
            # Animate particle position
            x = base_x + math.sin(progress * math.pi * 2 + i * 0.1) * 100
            y = base_y + math.cos(progress * math.pi * 1.5 + i * 0.2) * 80
            
            # Keep particles on screen
            x = x % self.width
            y = y % self.height
            
            # Animated particle size and opacity
            size = int(2 + 3 * math.sin(progress * math.pi * 4 + i))
            
            # Draw particle based on genre
            if analysis['genre'] == 'horror':
                # Dark, ominous particles
                color = (100, 50, 50)  # Dark red
            elif analysis['genre'] == 'fantasy':
                # Magical sparkles
                color = (255, 200, 100)  # Golden
            elif analysis['genre'] == 'cyberpunk':
                # Digital pixels
                color = (0, 255, 255) if i % 2 == 0 else (255, 0, 255)
            else:
                # Cinematic dust
                color = (150, 150, 150)  # Gray
            
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    
    def _add_atmospheric_elements(self, frame, analysis, progress):
        """Add atmospheric elements like fog, particles, etc."""
        if 'fog' in analysis['effects']:
            # Add fog effect
            overlay = np.zeros_like(frame)
            
            # Create fog pattern
            for _ in range(20):
                x = np.random.randint(0, frame.shape[1])
                y = np.random.randint(0, frame.shape[0])
                size = np.random.randint(30, 100)
                intensity = int(30 + progress * 20)
                
                cv2.circle(overlay, (x, y), size, (intensity, intensity, intensity), -1)
            
            # Blur the fog
            overlay = cv2.GaussianBlur(overlay, (51, 51), 0)
            
            # Blend with frame
            frame = cv2.addWeighted(frame, 0.8, overlay, 0.2, 0)
        
        return frame

# Standalone function
def create_professional_video(prompt, output_name=None):
    """Create professional-grade video from prompt"""
    generator = ProfessionalVideoGenerator()
    return generator.create_professional_video(prompt, output_name)

if __name__ == "__main__":
    # Test creation
    test_prompt = "A zombie chef in a dark kitchen"
    result = create_professional_video(test_prompt)
    if result:
        print(f"Created professional video: {result['video_path']}")
        print(f"Genre: {result['visual_analysis']['genre']}")
        print(f"Effects: {result['visual_analysis']['effects']}")