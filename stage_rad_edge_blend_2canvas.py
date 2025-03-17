from PIL import Image, ImageDraw

# Retry with the missing import added
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
input_image_path = "outs/00231-2045048988.png_scaled.png"  # Change this to your image file
output_image_path = "outs/00231-2045048988.png_scaled_rad.png"

image = Image.open(input_image_path)

# Apply rounded corners and blending effect
rounded_blended_result = apply_rounded_corners_with_blending(image)

# Save result for download
rounded_blended_result.save(output_image_path)

# Provide download link
#rounded_blended_result
def do_warning(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO", "WARNING"):
        return
    print(msg)
def do_yes_no_prompt():
    #Do yes/no prompt
    if OUTPUT_LEVEL != "PROMPT":
        return
    if input("Do you want to continue? (yes/no): ").strip().lower() not in ('yes', 'y'):
        print("Operation cancelled by user.")
        sys.exit(0)
def do_error(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO", "WARNING","ERR"):
        return
    print(msg)
def do_info(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO"):
        return
    print(msg)
         
def validate_args(args):
    #inspect and decorate the arguments according to logic requiring checks
    if args.input_path is None:
        do_warn("All images in current directory will be blended to canvas with 10% margin and saved as with new file names\n \
        No path specified please take caution")
        do_yes_no_prompt()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Corner Radius and Edge Blending")
    parser.add_argument("--input", required=True, help="Path to input image")
    parser.add_argument("--output", required=True, help="Path to save blended edge image")
    parser.add_argument("--depth", type=int, default=4, help="Depth of edge blend in increments of 10ths of image size choose 1-10")
    args = parser.parse_args()
    #validate_args(arguments)
    #apply_rounded_corners_with_blending(image)
    #upscale_image(args.input, args.output, scale=args.scale)
    #corners_and_edge_blend_helper(args.input)