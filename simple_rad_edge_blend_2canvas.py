from PIL import ImageDraw

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
input_image_path = "input.png"  # Change this to your image file
output_image_path = "rounded_blended.png"

image = Image.open(input_image_path)

# Apply rounded corners and blending effect
rounded_blended_result = apply_rounded_corners_with_blending(image)

# Save result for download
rounded_blended_result.save(output_image_path)

# Provide download link
rounded_blended_path
