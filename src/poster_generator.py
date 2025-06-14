"""
Poster Generator Module for TMDbCollector

This module provides functionality to generate custom collection posters
with text overlay when TMDb doesn't provide poster images.
"""

import os
import tempfile
import uuid
import logging
import time
from typing import Optional
from PIL import Image, ImageDraw, ImageFont

# Configure logger
logger = logging.getLogger(__name__)

# Default settings
DEFAULT_TEMPLATE = "default.png"
# Increased font size range by 30% + 20% as requested
DEFAULT_FONT_SIZE_RANGE = (95, 150)  # min, max font size - significantly increased
DEFAULT_TEXT_COLOR = (255, 255, 255)  # white
# No background as requested
DEFAULT_TEXT_POSITION = 0.5  # 50% from top (center of poster)
DEFAULT_IMAGE_QUALITY = 100
# Standard movie poster resolution for Emby (2:3 aspect ratio)
DEFAULT_POSTER_SIZE = (1000, 1500) 
# Safe margin percentage (% of poster width to keep as margin on each side)
DEFAULT_MARGIN_PCT = 0.105  # Reduced margins by 30% (from 15% to 10.5%)

# Default font path - using the OpenSans-Bold.ttf font we placed in resources/fonts
DEFAULT_FONT_PATH = "OpenSans-Bold.ttf"  # Just the filename, full path is constructed when needed


def generate_custom_poster(
    collection_name: str,
    template_name: Optional[str] = None,
    font_path: Optional[str] = None,
    text_color = None,
    text_position = None,
    resources_dir: Optional[str] = None,
) -> Optional[str]:
    """
    Generate a custom poster with text overlay for a collection.
    
    Args:
        collection_name: Name of the collection to display on the poster
        template_name: Name of template image file (optional, uses default if None)
        font_path: Path to font file to use (optional, uses system font if None)
        text_color: RGB tuple or list for text color (default: white)
        bg_color: RGBA tuple or list for text background color (default: semi-transparent black)
        text_position: Relative vertical position (0-1) for text (default: 0.8)
        resources_dir: Path to resources directory (optional, uses default if None)
        
    Returns:
        Path to generated poster image file or None if generation failed
    """
    
    # Handle default values and type conversions for parameters
    if text_color is None:
        text_color = DEFAULT_TEXT_COLOR
    elif isinstance(text_color, list):
        # Convert list from config to tuple
        text_color = tuple(text_color)
    
    if text_position is None:
        text_position = DEFAULT_TEXT_POSITION
    elif isinstance(text_position, str):
        # Convert string to float if needed
        try:
            text_position = float(text_position)
        except ValueError:
            text_position = DEFAULT_TEXT_POSITION
    # Set up paths
    if not resources_dir:
        # Try multiple possible locations for resources directory
        possible_locations = [
            # Standard location relative to script
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources"),
            # Docker container standard location
            "/app/resources",
            # Additional fallback locations
            os.path.join(os.path.dirname(__file__), "resources"),
            "/opt/tmdbcollector/resources"
        ]
        
        for location in possible_locations:
            if os.path.exists(location) and os.path.isdir(location):
                resources_dir = location
                logger.debug(f"Found resources directory at: {resources_dir}")
                break
        else:
            logger.warning(f"Could not find resources directory in any of the expected locations: {possible_locations}")
            # Fallback to default even if it might not exist
            resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources")
    
    template_path = os.path.join(resources_dir, "templates", template_name or DEFAULT_TEMPLATE)
    
    # Check if template exists
    if not os.path.exists(template_path):
        logger.error(f"Template image not found: {template_path}")
        if template_name and template_name != DEFAULT_TEMPLATE:
            # Try fallback to default template
            logger.warning(f"Falling back to default template: {DEFAULT_TEMPLATE}")
            fallback_path = os.path.join(resources_dir, "templates", DEFAULT_TEMPLATE)
            if os.path.exists(fallback_path):
                template_path = fallback_path
            else:
                logger.error(f"Default template also not found: {fallback_path}")
                return None
        else:
            return None
        
    # Set up font path
    if font_path is None:
        font_dirs = [
            os.path.join(resources_dir, "fonts"),
            "/app/resources/fonts",
            "/usr/share/fonts/truetype",
            "/usr/share/fonts/TTF"
        ]
        
        # Try to find the font in our resources directories first
        for font_dir in font_dirs:
            potential_font_path = os.path.join(font_dir, DEFAULT_FONT_PATH)
            if os.path.exists(potential_font_path):
                font_path = potential_font_path
                logger.debug(f"Found font at: {font_path}")
                break
        else:
            # Fallback to a system font if our custom font isn't found
            logger.warning(f"Could not find font {DEFAULT_FONT_PATH} in any expected locations")
            # On Linux try some common system fonts as fallbacks
            fallback_fonts = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
            ]
            
            for fallback in fallback_fonts:
                if os.path.exists(fallback):
                    font_path = fallback
                    logger.debug(f"Using fallback system font: {font_path}")
                    break
    
    # Create temp file for output
    temp_dir = tempfile.gettempdir()
    output_filename = f"collection_poster_{uuid.uuid4().hex}.jpg"
    output_path = os.path.join(temp_dir, output_filename)
    
    try:
        # Open template image
        logger.debug(f"Opening template image: {template_path}")
        img = Image.open(template_path)
        draw = ImageDraw.Draw(img)
        
        # Calculate optimal font size based on collection name length
        # Using higher baseline sizes as requested
        min_size, max_size = DEFAULT_FONT_SIZE_RANGE  # Now 72-120
        text_length = len(collection_name)
        
        # Enhanced formula for larger text, especially for longer titles
        # We'll use a more aggressive scaling to keep long titles readable
        if text_length <= 12:  # Very short titles get maximum size
            font_size = max_size
        elif text_length <= 25:  # Medium length titles
            # Linear reduction but starting from a higher baseline
            reduction_factor = (text_length - 12) / 13  # 0 to 1 scale
            font_size = int(max_size - (max_size - min_size) * reduction_factor * 0.7)  # Only reduce by 70% of the range
        else:  # Longer titles
            # For very long titles, we'll use a more gradual reduction
            extra_length = text_length - 25
            # Start from 80% of the range between min and max
            base_size = min_size + int((max_size - min_size) * 0.3)
            # Further reduce, but more slowly
            font_size = max(min_size, base_size - int(extra_length * 0.8))
            
        # For extremely long titles that will be wrapped to multiple lines,
        # we can actually use a larger font since each line will be shorter
        if text_length > 40:
            font_size = max(font_size, min_size + 10)  # Ensure it's at least 10pt larger than minimum
        
        # Ensure font size stays within absolute bounds
        font_size = max(min_size, min(max_size, font_size))
        
        logger.debug(f"Using font size {font_size} for '{collection_name}' (length: {text_length})")
        
        # For very long names, we'll need to modify our line-breaking logic later
        
        # Try to load the OpenSans-Bold font we placed in resources/fonts
        try:
            # First try user-provided font if specified
            if font_path and os.path.exists(font_path):
                font = ImageFont.truetype(font_path, font_size)
                logger.debug(f"Using custom font: {font_path}")
            else:
                # Try to load our default OpenSans-Bold font
                default_font_path = os.path.join(resources_dir, "fonts", DEFAULT_FONT_PATH)
                if os.path.exists(default_font_path):
                    font = ImageFont.truetype(default_font_path, font_size)
                    logger.debug(f"Using default font: {default_font_path}")
                else:
                    # Fall back to system default if our font isn't found
                    logger.warning(f"Default font not found at {default_font_path}, using system default")
                    font = ImageFont.load_default()
        except Exception as e:
            logger.warning(f"Error loading font, using default: {e}")
            font = ImageFont.load_default()
        
        # Calculate text dimensions and position
        w, h = img.size
        
        # Get the text size - handle different PIL versions
        if hasattr(draw, 'textsize'):
            text_width, text_height = draw.textsize(collection_name, font=font)
        elif hasattr(font, 'getbbox'):
            bbox = font.getbbox(collection_name)
            text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
        else:
            # Fallback method
            text_width = int(len(collection_name) * font_size * 0.6)  # Rough estimate
            text_height = int(font_size * 1.2)  # Rough estimate
        
        # Center text horizontally
        x_position = (w - text_width) / 2
        
        # Position text vertically according to parameter (default is center)
        y_position = h * text_position - (text_height / 2)  # Center text vertically
        
        # No background rectangle as requested
        # We'll add a slight shadow/outline effect to make text more readable without a background
        # This is done by drawing the text in black with a slight offset in multiple directions
        shadow_offset = max(2, int(font_size / 20))  # Scale shadow based on font size
        
        # Calculate safe margins to keep text within bounds
        margin_x = int(w * DEFAULT_MARGIN_PCT)  # Using the default margin percentage 
        
        # Calculate available width for text after margins
        available_width = w - (margin_x * 2)
        
        # For all text, we'll determine if it needs to be split into multiple lines
        # Get maximum characters per line based on font size and available width
        # This is an estimation that works well with the Open Sans Bold font
        # With 30% larger fonts, we need a larger character width estimate
        char_width_estimate = font_size * 0.65  # Increased for much larger font sizes
        max_chars_per_line = int(available_width / char_width_estimate)
        
        # Make sure we don't allow lines that are too long or too short
        # Significantly reduced maximum to accommodate much larger font
        max_chars_per_line = min(14, max(6, max_chars_per_line))  # More conservative limits for 30% larger fonts
        
        # Force multi-line for any text that might be too long
        force_multiline = len(collection_name) > max_chars_per_line
        
        # For longer text, we'll need to split into multiple lines
        if force_multiline or len(collection_name) > 15:  # Lower threshold for line breaking
            
            # Split text into chunks of reasonable length
            words = collection_name.split()
            lines = []
            current_line = []
            current_line_length = 0
            
            for word in words:
                word_length = len(word)
                # Check if adding this word would exceed our target line length
                if current_line and (current_line_length + word_length + 1) > max_chars_per_line:
                    # Complete the current line and start a new one
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_line_length = word_length
                else:
                    # Add to the current line
                    current_line.append(word)
                    # +1 for the space if not the first word
                    current_line_length += word_length + (1 if current_line_length > 0 else 0)
                        
            if current_line:  # Add the last line
                lines.append(' '.join(current_line))
                
            # Draw each line with shadow effect for readability
            line_spacing = 20  # Spacing between lines (in pixels)
            total_height = len(lines) * (text_height + line_spacing)  # Calculate total text block height
            
            # Calculate vertical starting position to center the entire text block
            # For text_position=0.5, this will center the text block in the middle of the image
            start_y = (h * text_position) - (total_height / 2)
            
            for i, line in enumerate(lines):
                # Get line width with proper error handling
                if hasattr(draw, 'textsize'):
                    line_width, _ = draw.textsize(line, font=font)
                elif hasattr(font, 'getbbox'):
                    bbox = font.getbbox(line)
                    line_width = bbox[2] - bbox[0]
                else:
                    line_width = int(len(line) * font_size * 0.6)  # Rough estimate
                    
                # Center each line horizontally
                line_x = (w - line_width) / 2  # Start with perfect centering
                
                # Only apply margin constraints if text would extend beyond safe area
                if line_x < margin_x:
                    line_x = margin_x  # Constrain to left margin
                
                # Double-check that text doesn't extend beyond right margin
                if line_x + line_width > w - margin_x:
                    # If it would extend beyond right margin, adjust position and potentially reduce line length
                    line_x = margin_x
                    
                    # If the line is still too wide even at the left margin, we need to truncate it
                    if line_width > available_width:
                        # Calculate how many characters we can safely fit
                        safe_char_count = int(available_width / (font_size * 0.55))
                        # If very short, just show what we can
                        if safe_char_count < 5 and len(line) > 0:
                            safe_char_count = 5  # Absolute minimum to show something
                        # Truncate with ellipsis if needed
                        if len(line) > safe_char_count:
                            line = line[:safe_char_count-3] + '...'
                            # Recalculate width with truncated text
                            if hasattr(draw, 'textsize'):
                                line_width, _ = draw.textsize(line, font=font)
                            elif hasattr(font, 'getbbox'):
                                bbox = font.getbbox(line)
                                line_width = bbox[2] - bbox[0]
                            else:
                                line_width = int(len(line) * font_size * 0.6)
                    
                line_y = start_y + i * (text_height + line_spacing)
                
                # Draw the text with no shadow/outline for a cleaner look
                draw.text((line_x, line_y), line, font=font, fill=text_color)
        else:
            # Draw single line text with shadow for better readability
            # Use the same margin as calculated earlier for consistency
            # margin_x is already defined above using DEFAULT_MARGIN_PCT
            
            # Center text horizontally
            x_position = (w - text_width) / 2
            
            # Only constrain to margins if text would extend beyond safe area
            if x_position < margin_x:
                x_position = margin_x
            
            # Double-check that text doesn't extend beyond right margin
            if x_position + text_width > w - margin_x:
                # If it would extend beyond right margin, adjust position
                x_position = margin_x
                
                # If the text is still too wide even at the left margin, we need to truncate it
                if text_width > available_width:
                    # Safer approach: force it to be multi-line instead by returning to the multi-line path
                    logger.debug(f"Text too wide for single line, forcing multi-line rendering for '{collection_name}'")
                    
                    # We'll handle this case by forcing a multi-line rendering
                    # Split text into reasonable chunks and re-run rendering
                    words = collection_name.split()
                    lines = []
                    current_line = []
                    current_line_length = 0
                    
                    for word in words:
                        word_length = len(word)
                        if current_line and (current_line_length + word_length + 1) > max_chars_per_line:
                            lines.append(' '.join(current_line))
                            current_line = [word]
                            current_line_length = word_length
                        else:
                            current_line.append(word)
                            current_line_length += word_length + (1 if current_line_length > 0 else 0)
                    
                    if current_line:  # Add the last line
                        lines.append(' '.join(current_line))
                    
                    # Draw each line with shadow effect for readability
                    line_spacing = 20  # Spacing between lines (in pixels)
                    total_height = len(lines) * (text_height + line_spacing)
                    
                    # Calculate vertical starting position to center the entire text block
                    start_y = (h * text_position) - (total_height / 2)
                    
                    for i, line in enumerate(lines):
                        # Get line width with error handling
                        if hasattr(draw, 'textsize'):
                            line_width, _ = draw.textsize(line, font=font)
                        elif hasattr(font, 'getbbox'):
                            bbox = font.getbbox(line)
                            line_width = bbox[2] - bbox[0]
                        else:
                            line_width = int(len(line) * font_size * 0.6)
                        
                        # Center each line horizontally (consistent with above)
                        line_x = (w - line_width) / 2
                        
                        # Only apply margin constraints if needed
                        if line_x < margin_x:
                            line_x = margin_x
                        if line_x + line_width > w - margin_x:
                            line_x = margin_x
                            # Truncate if still too wide
                            if line_width > available_width:
                                safe_char_count = int(available_width / (font_size * 0.55))
                                if safe_char_count < 5 and len(line) > 0:
                                    safe_char_count = 5
                                if len(line) > safe_char_count:
                                    line = line[:safe_char_count-3] + '...'
                        
                        line_y = start_y + i * (text_height + 20)
                        
                        # No shadow effect for cleaner text rendering
                        
                        # Draw text
                        draw.text((line_x, line_y), line, font=font, fill=text_color)
                    
                    # Skip the regular single-line drawing code by returning early
                    return output_path
                
            # Adjust vertical position to better center single line text
            # For single line text, we can use the exact vertical position
            adjusted_y_position = (h * text_position) - (text_height / 2)
            position = (x_position, adjusted_y_position)
            
            # Draw text with no shadow/outline for a cleaner look
            draw.text(position, collection_name, font=font, fill=text_color)
        
        # Save to temp location
        # Convert to RGB mode if the image has an alpha channel (RGBA), as JPEG doesn't support transparency
        if img.mode == 'RGBA':
            # Create a new RGB image with white background
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            # Paste the original image on top, using its alpha channel as mask
            rgb_img.paste(img, mask=img.split()[3])  # The 4th channel is the alpha
            # Save the RGB image as JPEG
            rgb_img.save(output_path, "JPEG", quality=DEFAULT_IMAGE_QUALITY)
        else:
            # Image is already in RGB mode, save directly
            img.save(output_path, "JPEG", quality=DEFAULT_IMAGE_QUALITY)
        logger.info(f"Successfully generated custom poster for '{collection_name}' at {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating custom poster for '{collection_name}': {e}")
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        return None


def file_to_url(file_path: str) -> str:
    """
    Convert a local file path to a file:// URL that can be used by media servers.
    
    Args:
        file_path: Path to local file
        
    Returns:
        file:// URL to the file
    """
    # Normalize path separators and ensure correct format for file:// URL
    normalized_path = file_path.replace('\\', '/')
    if not normalized_path.startswith('/'):
        normalized_path = '/' + normalized_path
    
    return f"file://{normalized_path}"


def cleanup_temp_posters() -> int:
    """
    Cleanup temporary poster files that may have been left behind.
    Should be called periodically to prevent disk space issues.
    
    Returns:
        Number of files removed
    """
    temp_dir = tempfile.gettempdir()
    count = 0
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith("collection_poster_") and filename.endswith(".jpg"):
                file_path = os.path.join(temp_dir, filename)
                try:
                    # Only remove files older than 1 day
                    file_age = os.path.getmtime(file_path)
                    if (time.time() - file_age) > 86400:  # 24 hours in seconds
                        os.remove(file_path)
                        count += 1
                except Exception as e:
                    logger.warning(f"Failed to remove temp poster {filename}: {e}")
    except Exception as e:
        logger.error(f"Error during temp poster cleanup: {e}")
    
    return count
