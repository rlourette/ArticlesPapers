#!/usr/bin/env python3
"""
1950s Style Text Overlay Generator - NO OVERLAP VERSION
Adds retro-styled text elements with proper spacing to prevent overlaps
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import os

class RetroTextGenerator:
    def __init__(self, image_path):
        self.img = Image.open(image_path).convert('RGBA')
        self.width, self.height = self.img.size
        
        # Color palette with high contrast
        self.colors = {
            'white': (255, 255, 255, 255),
            'bright_yellow': (255, 255, 100, 255),
            'electric_blue': (30, 144, 255, 255),
            'hot_red': (255, 69, 0, 255),
            'chrome': (220, 220, 220, 255),
            'black': (0, 0, 0, 255),
            'dark_shadow': (0, 0, 0, 220),
            'outline_black': (0, 0, 0, 255)
        }
        
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """Load fonts with conservative sizes to prevent overlap"""
        fonts = {}
        font_paths = [
            "/System/Library/Fonts/Arial.ttc",  # macOS
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "C:/Windows/Fonts/arial.ttf",  # Windows
            "C:/Windows/Fonts/calibri.ttf",  # Windows
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
        ]
        
        available_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                available_font = font_path
                break
        
        try:
            if available_font:
                # More conservative font sizes
                fonts['huge'] = ImageFont.truetype(available_font, 72)    # Reduced from 96
                fonts['large'] = ImageFont.truetype(available_font, 54)   # Reduced from 72
                fonts['medium'] = ImageFont.truetype(available_font, 36)  # Reduced from 48
                fonts['small'] = ImageFont.truetype(available_font, 28)   # Reduced from 32
                fonts['tiny'] = ImageFont.truetype(available_font, 20)    # Reduced from 24
            else:
                default_font = ImageFont.load_default()
                fonts = {
                    'huge': default_font, 'large': default_font, 'medium': default_font,
                    'small': default_font, 'tiny': default_font
                }
        except:
            default_font = ImageFont.load_default()
            fonts = {
                'huge': default_font, 'large': default_font, 'medium': default_font,
                'small': default_font, 'tiny': default_font
            }
        
        return fonts
    
    def add_shadow_text(self, text, position, font_key, color, shadow_offset=(3, 3), shadow_blur=2):
        """Add text with drop shadow - smaller shadows to reduce overlap"""
        font = self.fonts[font_key]
        x, y = position
        
        shadow_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_layer)
        shadow_draw.text((x + shadow_offset[0], y + shadow_offset[1]), 
                        text, font=font, fill=self.colors['dark_shadow'])
        
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(shadow_blur))
        
        text_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_layer)
        text_draw.text((x, y), text, font=font, fill=self.colors[color])
        
        self.img = Image.alpha_composite(self.img, shadow_layer)
        self.img = Image.alpha_composite(self.img, text_layer)
    
    def add_outlined_text(self, text, position, font_key, fill_color, outline_color, outline_width=2):
        """Add text with outline - smaller outlines to prevent overlap"""
        font = self.fonts[font_key]
        x, y = position
        
        text_layer = Image.new('RGBA', self.img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        
        # Smaller outline
        for adj_x in range(-outline_width, outline_width + 1):
            for adj_y in range(-outline_width, outline_width + 1):
                if adj_x != 0 or adj_y != 0:
                    draw.text((x + adj_x, y + adj_y), text, font=font, 
                             fill=self.colors[outline_color])
        
        draw.text((x, y), text, font=font, fill=self.colors[fill_color])
        self.img = Image.alpha_composite(self.img, text_layer)
    
    def get_text_center_x(self, text, font_key):
        """Calculate X position to center text"""
        font = self.fonts[font_key]
        bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        return (self.width - text_width) // 2
    
    def get_text_width(self, text, font_key):
        """Get the width of text"""
        font = self.fonts[font_key]
        bbox = ImageDraw.Draw(Image.new('RGBA', (1, 1))).textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]
    
    def generate_no_overlap_layout(self):
        """Generate layout with guaranteed no overlaps"""
        
        # Calculate spacing zones to prevent overlaps
        margin = 40
        vertical_sections = 8  # Divide image into sections
        section_height = (self.height - 2 * margin) // vertical_sections
        
        current_y = margin
        
        # 1. MAIN TITLE - Top section (takes 2 sections)
        main_text = "MICROSOFT PROXY 4"
        
        # Check if title fits, if not split it
        if self.get_text_width(main_text, 'huge') > (self.width - 2 * margin):
            # Split into two lines
            line1 = "MICROSOFT"
            line2 = "PROXY 4"
            
            line1_x = self.get_text_center_x(line1, 'large')
            line2_x = self.get_text_center_x(line2, 'large')
            
            self.add_outlined_text(line1, (line1_x, current_y), 'large', 'bright_yellow', 'outline_black', 3)
            self.add_outlined_text(line2, (line2_x, current_y + 60), 'large', 'bright_yellow', 'outline_black', 3)
            current_y += section_height * 2 + 20
        else:
            # Single line title
            main_x = self.get_text_center_x(main_text, 'huge')
            self.add_outlined_text(main_text, (main_x, current_y), 'huge', 'bright_yellow', 'outline_black', 3)
            current_y += section_height * 2
        
        # 2. SUBTITLE - Next section
        sub_text = "EMBEDDED TEMPLATE LIBRARY"
        if self.get_text_width(sub_text, 'large') > (self.width - 2 * margin):
            # Use smaller font if too wide
            sub_x = self.get_text_center_x(sub_text, 'medium')
            self.add_outlined_text(sub_text, (sub_x, current_y), 'medium', 'white', 'outline_black', 2)
        else:
            sub_x = self.get_text_center_x(sub_text, 'large')
            self.add_outlined_text(sub_text, (sub_x, current_y), 'large', 'white', 'outline_black', 2)
        
        current_y += section_height + 10
        
        # 3. FEATURE CALLOUT - Next section
        feature_text = "ZERO-ALLOCATION POLYMORPHISM"
        if self.get_text_width(feature_text, 'medium') > (self.width - 2 * margin):
            feature_x = self.get_text_center_x(feature_text, 'small')
            self.add_shadow_text(feature_text, (feature_x, current_y), 'small', 'electric_blue')
        else:
            feature_x = self.get_text_center_x(feature_text, 'medium')
            self.add_shadow_text(feature_text, (feature_x, current_y), 'medium', 'electric_blue')
        
        current_y += section_height + 20
        
        # 4. BENEFITS - Take 2 sections, arranged vertically to avoid overlap
        benefits = [
            "40-60% FASTER CALLS",
            "ZERO HEAP ALLOCATION", 
            "DETERMINISTIC TIMING",
            "SAFETY-CRITICAL READY"
        ]
        
        for i, benefit in enumerate(benefits):
            benefit_x = self.get_text_center_x(benefit, 'small')
            benefit_y = current_y + (i * 40)  # 40px spacing between benefits
            
            color = 'hot_red' if i % 2 == 0 else 'chrome'
            self.add_shadow_text(benefit, (benefit_x, benefit_y), 'small', color)
        
        current_y += section_height * 2
        
        # 5. INDUSTRY TAGS - Bottom section with margin
        industry_text = "AEROSPACE • AUTOMOTIVE • MEDICAL • IoT"
        industry_x = self.get_text_center_x(industry_text, 'small')
        industry_y = self.height - 60  # Fixed position from bottom
        self.add_shadow_text(industry_text, (industry_x, industry_y), 'small', 'white')
        
        # 6. CORNER ELEMENTS - Positioned to not interfere with main content
        corner_elements = [
            ("DO-178C", (30, 30)),                           # Top left
            ("ISO 26262", (self.width - 150, 30)),          # Top right
            ("pro::proxy<>", (30, self.height - 30)),       # Bottom left  
            ("etl::array<>", (self.width - 150, self.height - 30))  # Bottom right
        ]
        
        for text, position in corner_elements:
            self.add_outlined_text(text, position, 'tiny', 'bright_yellow', 'outline_black', 1)
    
    def save(self, output_path):
        """Save the final image"""
        if output_path.lower().endswith('.jpg') or output_path.lower().endswith('.jpeg'):
            rgb_img = Image.new('RGB', self.img.size, (255, 255, 255))
            rgb_img.paste(self.img, mask=self.img.split()[-1])
            rgb_img.save(output_path, 'JPEG', quality=95)
        else:
            self.img.save(output_path)

def main():
    """Main function to process the image"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    input_image = os.path.join(script_dir, "Article_Image.jpg")
    output_image = os.path.join(script_dir, "proxy4_no_overlap.jpg")  # New filename
    
    if not os.path.exists(input_image):
        print(f"Error: Input file '{input_image}' not found!")
        return
    
    try:
        print("Loading image and generating NO-OVERLAP 1950s-style text overlay...")
        
        generator = RetroTextGenerator(input_image)
        generator.generate_no_overlap_layout()  # Using no-overlap layout method
        generator.save(output_image)
        
        print(f"Success! No-overlap styled image saved as: {output_image}")
        
    except Exception as e:
        print(f"Error processing image: {e}")
        print("Make sure PIL (Pillow) is installed: pip install Pillow")

if __name__ == "__main__":
    main()