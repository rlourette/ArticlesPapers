#!/usr/bin/env python3
"""
Automotive C++26 Article Image Text Overlay Generator
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

class ArticleImageGenerator:
    def __init__(self, image_path):
        self.img = Image.open(image_path).convert('RGBA')
        self.width, self.height = self.img.size
        
        # Professional color scheme with semi-transparent options
        self.colors = {
            'white': (255, 255, 255, 255),
            'bright_cyan': (0, 200, 255, 255),
            'orange': (255, 140, 0, 255),
            'light_blue': (100, 180, 255, 255),
            'dark_overlay': (0, 0, 0, 160),
            'shadow': (0, 0, 0, 220),
            'semi_white': (255, 255, 255, 230)
        }
        
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts with appropriate sizes"""
        fonts = {}
        font_paths = [
            "/System/Library/Fonts/Arial.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        
        available_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                available_font = font_path
                break
        
        try:
            if available_font:
                fonts['title'] = ImageFont.truetype(available_font, 56)
                fonts['subtitle'] = ImageFont.truetype(available_font, 28)
                fonts['accent'] = ImageFont.truetype(available_font, 22)
                fonts['small'] = ImageFont.truetype(available_font, 16)
            else:
                default = ImageFont.load_default()
                fonts = {'title': default, 'subtitle': default, 
                        'accent': default, 'small': default}
        except:
            default = ImageFont.load_default()
            fonts = {'title': default, 'subtitle': default, 
                    'accent': default, 'small': default}
        
        return fonts
    
    def add_dark_panel(self, x, y, width, height, opacity=160):
        """Add a semi-transparent dark panel for text background"""
        panel = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(panel)
        draw.rectangle([(x, y), (x + width, y + height)], 
                      fill=(0, 0, 0, opacity))
        # Blur the edges slightly for smoother blend
        panel = panel.filter(ImageFilter.GaussianBlur(2))
        self.img = Image.alpha_composite(self.img, panel)
    
    def add_text_with_glow(self, text, position, font_key, color, glow_color=None):
        """Add text with a subtle glow effect for visibility"""
        font = self.fonts[font_key]
        x, y = position
        
        # Glow layer
        if glow_color:
            glow_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
            glow_draw = ImageDraw.Draw(glow_layer)
            # Create multiple glow layers for softer effect
            for offset in [(0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                glow_draw.text((x + offset[0], y + offset[1]), 
                             text, font=font, fill=glow_color)
            glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(3))
            self.img = Image.alpha_composite(self.img, glow_layer)
        
        # Main text
        text_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        text_draw.text((x, y), text, font=font, fill=self.colors[color])
        
        self.img = Image.alpha_composite(self.img, text_layer)
    
    def create_article_header(self):
        """Create the article header layout avoiding busy areas"""
        
        # Add subtle dark panel in upper left for main title
        self.add_dark_panel(20, 20, 500, 140, opacity=140)
        
        # Main title - upper left where it's less busy
        title_lines = ["C++26 REFLECTION", "TRANSFORMS"]
        self.add_text_with_glow(title_lines[0], (40, 35), 'title', 'bright_cyan', 
                                glow_color=(0, 100, 150, 100))
        self.add_text_with_glow(title_lines[1], (40, 95), 'title', 'white',
                                glow_color=(0, 100, 150, 100))
        
        # Subtitle - below title in same panel
        subtitle = "Automotive Code Generation"
        self.add_text_with_glow(subtitle, (40, 155), 'subtitle', 'light_blue')
        
        # Key feature - bottom left
        self.add_dark_panel(20, self.height - 120, 320, 100, opacity=140)
        self.add_text_with_glow("FROM HIGH-LEVEL C++", (35, self.height - 105), 
                                'accent', 'white')
        self.add_text_with_glow("TO SAFETY-CERTIFIED C", (35, self.height - 75), 
                                'accent', 'orange')
        self.add_text_with_glow("AT COMPILE TIME", (35, self.height - 45), 
                                'accent', 'bright_cyan')
        
        # Add vertical text on far left edge
        vertical_text_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        vertical_draw = ImageDraw.Draw(vertical_text_layer)
        
        # Rotate text for vertical placement
        temp_img = Image.new('RGBA', (200, 30), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp_img)
        temp_draw.text((0, 0), "ISO 26262 COMPLIANT", 
                      font=self.fonts['small'], fill=self.colors['semi_white'])
        rotated = temp_img.rotate(90, expand=True)
        vertical_text_layer.paste(rotated, (5, self.height//2 - 100))
        
        self.img = Image.alpha_composite(self.img, vertical_text_layer)
        
        # Bottom right corner tag
        self.add_text_with_glow("DRAFT STANDARD 2025", 
                                (self.width - 520, self.height - 25), 
                                'small', 'semi_white')
        
        # Top right performance metrics
        metrics_x = self.width - 280
        metrics_y = 30
        self.add_dark_panel(metrics_x - 10, metrics_y - 5, 270, 80, opacity=120)
        self.add_text_with_glow("ZERO RUNTIME OVERHEAD", (metrics_x, metrics_y), 
                                'small', 'orange')
        self.add_text_with_glow("100% COMPILE-TIME", (metrics_x, metrics_y + 25), 
                                'small', 'bright_cyan')
        self.add_text_with_glow("MISRA-C COMPLIANT OUTPUT", (metrics_x, metrics_y + 50), 
                                'small', 'white')
    
    def save(self, output_path):
        """Save the final image"""
        if output_path.lower().endswith(('.jpg', '.jpeg')):
            rgb_img = Image.new('RGB', self.img.size, (255, 255, 255))
            rgb_img.paste(self.img, mask=self.img.split()[-1] if len(self.img.split()) > 3 else None)
            rgb_img.save(output_path, 'JPEG', quality=95)
        else:
            self.img.save(output_path)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Input source and output image filenames
    input_image = os.path.join(script_dir, "automotive_visualization.jpg")
    output_image = os.path.join(script_dir, "article_header_final.jpg")
    
    if not os.path.exists(input_image):
        print(f"Error: Input file '{input_image}' not found!")
        print("Please save the Grok image as 'automotive_visualization.jpg' in the same directory")
        return
    
    try:
        print("Creating article header with optimized text placement...")
        
        generator = ArticleImageGenerator(input_image)
        generator.create_article_header()
        generator.save(output_image)
        
        print(f"Success! Article header saved as: {output_image}")
        
    except Exception as e:
        print(f"Error processing image: {e}")

if __name__ == "__main__":
    main()