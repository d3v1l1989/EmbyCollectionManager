"""
Script to create a default poster template image.
This generates a gradient background that can be used for collection posters.
"""

import os
from PIL import Image, ImageDraw

# Ensure the templates directory exists
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "templates")
os.makedirs(template_dir, exist_ok=True)

# Define the dimensions for a standard movie poster (2:3 ratio)
width = 1000
height = 1500

# Create a new image with a gradient background
img = Image.new('RGB', (width, height), color=(0, 0, 0))
draw = ImageDraw.Draw(img)

# Create a dark gradient background (dark blue to black)
for y in range(height):
    # Calculate gradient color (from dark blue at top to black at bottom)
    blue = max(0, int(120 * (1 - y / height)))
    color = (0, 0, blue)
    
    # Draw a horizontal line with this color
    draw.line([(0, y), (width, y)], fill=color)

# Save the template
template_path = os.path.join(template_dir, "default.jpg")
img.save(template_path, "JPEG", quality=95)

print(f"Created default template at: {template_path}")
