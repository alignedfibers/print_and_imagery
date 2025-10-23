import cv2
import numpy as np
from PIL import Image, ImageEnhance
from rembg import remove
#bgremove
# Load image
image_path = "00311-3047219753_scaled.png"
input_image = Image.open(image_path)

# Boost contrast & saturation
enhancer = ImageEnhance.Contrast(input_image)
input_image = enhancer.enhance(2)  # Increase contrast
enhancer = ImageEnhance.Color(input_image)
input_image = enhancer.enhance(1.5)  # Increase saturation

# Convert to OpenCV format for background change
cv_image = np.array(input_image)
cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGBA2RGB)

# Replace background with solid color (e.g., white)
white_bg = np.full(cv_image.shape, (255, 255, 255), dtype=np.uint8)
mask = cv2.inRange(cv_image, (0, 0, 0), (20, 20, 20))  # Adjust for your image
processed_image = np.where(mask[:, :, None] == 255, white_bg, cv_image)

# Convert back to PIL
processed_pil = Image.fromarray(processed_image)

# Run `rembg` after preprocessing
output_image = remove(processed_pil)

# Save results
output_image.save("processed_foreground.png")


########################

from rembg import remove, new_session
from PIL import Image

#bgremove option 2
# Load image
image_path = "00311-3047219753_scaled.png"
input_image = Image.open(image_path)

# Use a more precise model
session = new_session("u2net_human_seg")  # Works better for fine details

# Run rembg
output_image = remove(input_image, session=session)

# Save output
output_image.save("fixed_foreground.png")

############################

#pip install rembg
#third remake of rembackground script
from rembg import remove
from PIL import Image

# Load the image
image_path = "00311-3047219753_scaled.png"  # Update this to the correct file path
input_image = Image.open(image_path)

# Default `rembg` background removal
output_image_default = remove(input_image)
output_image_default.save("foreground_removed_default.png")

# Refined background removal with alpha matting
output_image_alpha = remove(
    input_image, 
    alpha_matting=True, 
    alpha_matting_foreground_threshold=250, 
    alpha_matting_background_threshold=5, 
    alpha_matting_erode_size=5
)
output_image_alpha.save("foreground_removed_alpha.png")

print("Images saved as 'foreground_removed_default.png' and 'foreground_removed_alpha.png'")
#########################################

#Round and blend corners
import numpy as np
from PIL import Image, ImageDraw

def apply_rounded_corners_with_blending(image, corner_radius_ratio=0.15):
    """
    Apply rounded corners and strong blending at the edges to smoothly transition 
    the image into the underlying canvas using NumPy for performance.
    
    :param image: PIL Image to process.
    :param corner_radius_ratio: Ratio of the image size used to determine the corner rounding.
    :return: Processed PIL Image with rounded corners and blended edges.
    """
    image = image.convert("RGBA")  # Preserve full color with alpha channel
    width, height = image.size

    # Create a NumPy array mask (255 = fully visible, 0 = fully transparent)
    mask = np.ones((height, width), dtype=np.float32) * 255

    # Corner radius calculation
    corner_radius = int(min(width, height) * corner_radius_ratio)

    # Create a corner mask using NumPy (rounding effect)
    y, x = np.ogrid[:corner_radius*2, :corner_radius*2]
    dist = np.sqrt((x - corner_radius)**2 + (y - corner_radius)**2)
    corner_mask = np.where(dist <= corner_radius, 1, 0).astype(np.uint8) * 255

    # Apply corners to the four corners of the mask
    mask[:corner_radius, :corner_radius] = corner_mask[:corner_radius, :corner_radius]
    mask[:corner_radius, -corner_radius:] = corner_mask[:corner_radius, -corner_radius:]
    mask[-corner_radius:, :corner_radius] = corner_mask[-corner_radius:, :corner_radius]
    mask[-corner_radius:, -corner_radius:] = corner_mask[-corner_radius:, -corner_radius:]

    # Compute edge blending effect using NumPy instead of loops
    dist_x = np.minimum(np.arange(width), np.arange(width)[::-1])
    dist_y = np.minimum(np.arange(height), np.arange(height)[::-1])
    edge_blend = np.minimum(dist_x[None, :] / (width * 0.2), dist_y[:, None] / (height * 0.2))
    edge_blend = np.clip(edge_blend, 0, 1)

    # Apply blending effect to the mask
    mask = (mask * edge_blend).astype(np.uint8)

    # Convert NumPy array back to PIL image mask
    mask_image = Image.fromarray(mask, mode="L")

    # Apply mask to image
    blended_image = Image.new("RGBA", (width, height))
    blended_image.paste(image, (0, 0), mask_image)

    return blended_image

# Load image from file (Replace 'input.png' with your actual image path)
input_image_path = "outs/00188-2045048945_merged_3047219644_touched_scaled.png"  # Change this to your image file
output_image_path = "outs/00188-2045048945_merged_3047219644_touched_scaled_rad.png"

image = Image.open(input_image_path)

# Apply rounded corners and blending effect (NumPy Optimized)
rounded_blended_result = apply_rounded_corners_with_blending(image)

# Save result for download
rounded_blended_result.save(output_image_path)

print(f"Processed image saved as: {output_image_path}")

############################

#dithering
# Load the newly attached image
new_image_path = "/mnt/data/00001-1095111020.png"
image = Image.open(new_image_path)

def apply_sparse_edge_dither_with_circular_fade(image):
    """
    Apply sparse dithering only to the edges (top, bottom, left, right) with a maximum width of 1/12th of the image.
    Additionally, apply a circular fade to round and blend the edges into the underlying canvas.
    
    :param image: PIL Image to process.
    :return: Processed PIL Image.
    """
    image = image.convert("RGB")  # Preserve full color
    width, height = image.size
    mask = Image.new("L", (width, height), 255)  # Start with a fully visible image

    max_dither_width = width // 12  # Max dithering range is 1/12th of the image width
    max_dither_height = height // 12  # Max dithering range is 1/12th of the image height

    center_x, center_y = width // 2, height // 2
    max_radius = np.sqrt(center_x**2 + center_y**2)

    for y in range(height):
        for x in range(width):
            # Distance from the closest edge (left, right, top, bottom)
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)

            # Apply effect only within the designated edge areas
            if dist_x < max_dither_width or dist_y < max_dither_height:
                fade_intensity = (min(dist_x, dist_y) / max(max_dither_width, max_dither_height)) ** 1.8  # Smooth fade
            else:
                fade_intensity = 1

            # Apply circular fade effect for blending into the canvas
            dist_to_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            circular_fade = (dist_to_center / max_radius) ** 2.5  # Exponential fade-out

            # Combine both fade effects
            final_intensity = min(fade_intensity, circular_fade)
            mask.putpixel((x, y), int(final_intensity * 255))

    # Apply dithering only to edge areas while keeping the center intact
    dithered = image.convert("L").convert("1")  # Convert to grayscale first for dithering
    final_image = Image.composite(image, dithered, mask)
    return final_image

# Apply sparse dithering only to edges with circular fade effect
sparse_edge_circular_fade_result = apply_sparse_edge_dither_with_circular_fade(image)

# Save result for download
sparse_edge_circular_fade_path = "/mnt/data/sparse_edge_circular_fade.png"
sparse_edge_circular_fade_result.save(sparse_edge_circular_fade_path)

# Provide download link
sparse_edge_circular_fade_path

##################

#Dithering full

from PIL import Image, ImageDraw

def apply_rounded_corners_with_blending(image, corner_radius_ratio=0.15):
    """
    Apply rounded corners and strong blending at the edges to smoothly transition 
    the image into the underlying canvas.
    
    :param image: PIL Image to process.
    :param corner_radius_ratio: Ratio of the image size used to determine the corner rounding.
    :return: Processed PIL Image with rounded corners and blended edges.
    """
    image = image.convert("RGBA")  # Preserve full color with alpha channel
    width, height = image.size

    # Create a mask for rounded corners and edge blending
    mask = Image.new("L", (width, height), 255)
    corner_radius = int(min(width, height) * corner_radius_ratio)

    # Generate rounded corner effect using an ellipse mask
    corner = Image.new("L", (corner_radius * 2, corner_radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, corner_radius * 2, corner_radius * 2), fill=255)

    # Apply corners to mask
    mask.paste(corner.crop((0, 0, corner_radius, corner_radius)), (0, 0))
    mask.paste(corner.crop((corner_radius, 0, corner_radius * 2, corner_radius)), (width - corner_radius, 0))
    mask.paste(corner.crop((0, corner_radius, corner_radius, corner_radius * 2)), (0, height - corner_radius))
    mask.paste(corner.crop((corner_radius, corner_radius, corner_radius * 2, corner_radius * 2)), (width - corner_radius, height - corner_radius))

    # Apply strong blending on edges
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            edge_blend = min(dist_x, dist_y) / (width * 0.2)  # Blend within 20% of image width
            edge_blend = min(max(edge_blend, 0), 1)
            mask.putpixel((x, y), int(mask.getpixel((x, y)) * edge_blend))

    # Apply the rounded corners and edge blending mask
    blended_image = Image.new("RGBA", (width, height))
    blended_image.paste(image, (0, 0), mask)

    return blended_image

# Load image from file (Replace 'input.png' with your actual image path)
input_image_path = "input.png"  # Change this to your image file
output_image_path = "rounded_blended.png"

image = Image.open(input_image_path)

# Apply rounded corners and blending effect
rounded_blended_result = apply_rounded_corners_with_blending(image)

# Save result
rounded_blended_result.save(output_image_path)

print(f"Processed image saved as: {output_image_path}")

#################

##Apply dithering that might have worked?
import argparse
from PIL import Image
import glob

def apply_dithering(input_path, output_path):
    image = Image.open(input_path).convert("L")
    dithered_image = image.convert("1", dither=Image.FLOYDSTEINBERG)
    dithered_image.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply dithering to reduce shading density.")
    parser.add_argument("input", help="Input image or glob pattern")
    parser.add_argument("output", help="Output directory")
    
    args = parser.parse_args()
    
    for file in glob.glob(args.input):
        apply_dithering(file, f"{args.output}/{file.split('/')[-1]}")
###################

#Convert to grascale that might have worked
import argparse
from PIL import Image, ImageOps
import glob

def convert_to_grayscale(input_path, output_path):
    image = Image.open(input_path).convert("RGB")
    grayscale_image = ImageOps.grayscale(image)
    grayscale_image.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert image to grayscale.")
    parser.add_argument("input", help="Input image or glob pattern")
    parser.add_argument("output", help="Output directory")

    args = parser.parse_args()
    
    for file in glob.glob(args.input):
        convert_to_grayscale(file, f"{args.output}/{file.split('/')[-1]}")
######################
#Remove Darker Shading
import argparse
from PIL import Image
import glob

def remove_darker_shading(input_path, output_path, threshold=150):
    image = Image.open(input_path).convert("L")
    light_mask = image.point(lambda p: 255 if p > threshold else p, mode="L")
    light_mask.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Remove darker shading while preserving lighter tones.")
    parser.add_argument("input", help="Input image or glob pattern")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("--threshold", type=int, default=150, help="Threshold for shading removal")

    args = parser.parse_args()
    
    for file in glob.glob(args.input):
        remove_darker_shading(file, f"{args.output}/{file.split('/')[-1]}", args.threshold)
######################

#Increase line density
import argparse
import numpy as np
from PIL import Image
import glob

def thicken_lines(input_path, output_path, kernel_size=3):
    image = Image.open(input_path).convert("L")
    image_array = np.array(image)
    thickened_array = np.maximum.reduce([
        np.roll(image_array, shift, axis)
        for axis in range(2)
        for shift in (-kernel_size, 0, kernel_size)
    ])
    thickened_image = Image.fromarray(thickened_array)
    thickened_image.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Increase line density by thickening edges.")
    parser.add_argument("input", help="Input image or glob pattern")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("--kernel", type=int, default=3, help="Kernel size for thickening")

    args = parser.parse_args()
    
    for file in glob.glob(args.input):
        thicken_lines(file, f"{args.output}/{file.split('/')[-1]}", args.kernel)

########################
# Run example of all simple image scripts
# Re-import required libraries since execution state was reset
import os
import glob
import numpy as np
import argparse
from PIL import Image, ImageOps, ImageFilter

# Re-define functions after reset

def reduce_color_palette(input_path, output_path, num_colors=6):
    image = Image.open(input_path).convert("RGB")
    simplified_image = image.quantize(colors=num_colors, method=2)
    simplified_image.save(output_path)

def enhance_edges(input_path, output_path):
    image = Image.open(input_path).convert("RGB")
    enhanced_image = image.filter(ImageFilter.EDGE_ENHANCE)
    enhanced_image.save(output_path)

def convert_to_grayscale(input_path, output_path):
    image = Image.open(input_path).convert("RGB")
    grayscale_image = ImageOps.grayscale(image)
    grayscale_image.save(output_path)

def apply_dithering(input_path, output_path):
    image = Image.open(input_path).convert("L")
    dithered_image = image.convert("1", dither=Image.FLOYDSTEINBERG)
    dithered_image.save(output_path)

def remove_darker_shading(input_path, output_path, threshold=150):
    image = Image.open(input_path).convert("L")
    light_mask = image.point(lambda p: 255 if p > threshold else p, mode="L")
    light_mask.save(output_path)

def thicken_lines(input_path, output_path, kernel_size=3):
    image = Image.open(input_path).convert("L")
    image_array = np.array(image)
    thickened_array = np.maximum.reduce([
        np.roll(image_array, shift, axis)
        for axis in range(2)
        for shift in (-kernel_size, 0, kernel_size)
    ])
    thickened_image = Image.fromarray(thickened_array)
    thickened_image.save(output_path)

# Recreate directories
input_image_path = "/mnt/data/473190497_1185582846468509_7001657067180195637_n~2.png"
output_dir = "/mnt/data/processed_outputs"
os.makedirs(output_dir, exist_ok=True)

# Define output paths
output_paths = {
    "reduced_palette": os.path.join(output_dir, "reduced_palette.png"),
    "enhanced_edges": os.path.join(output_dir, "enhanced_edges.png"),
    "grayscale": os.path.join(output_dir, "grayscale.png"),
    "dithered": os.path.join(output_dir, "dithered.png"),
    "lighter_shading": os.path.join(output_dir, "lighter_shading.png"),
    "thickened_lines": os.path.join(output_dir, "thickened_lines.png"),
}

# Apply transformations
reduce_color_palette(input_image_path, output_paths["reduced_palette"])
enhance_edges(input_image_path, output_paths["enhanced_edges"])
convert_to_grayscale(input_image_path, output_paths["grayscale"])
apply_dithering(output_paths["grayscale"], output_paths["dithered"])
remove_darker_shading(output_paths["grayscale"], output_paths["lighter_shading"])
thicken_lines(output_paths["lighter_shading"], output_paths["thickened_lines"])

# Return all processed images
output_paths
################################
#Reduce colors, 3,8,12,16
# Define a modified function to allow dynamic color palette testing
def reduce_color_palette_test(input_path, output_path, num_colors):
    image = Image.open(input_path).convert("RGB")
    reduced_image = image.quantize(colors=num_colors, method=2)
    reduced_image.save(output_path)

# Define test cases with different color limits
color_tests = [3, 8, 12, 16]
output_paths_palette = {}

# Process each color variation
for colors in color_tests:
    output_file = f"/mnt/data/processed_outputs/reduced_palette_{colors}.png"
    reduce_color_palette_test(input_image_path, output_file, colors)
    output_paths_palette[f"{colors}_colors"] = output_file

# Return all processed images for review
output_paths_palette
##################################################
#Closes color function
def closest_color(pixel, palette):
    distances = np.linalg.norm(palette - pixel, axis=1)
    return palette[np.argmin(distances)]
####################################################

