# Load the newly attached image
new_image_path = "/mnt/data/file-AMKnSunP1vtJ93FaFdE4rA"  # Assuming it's the latest file
image = Image.open(new_image_path)

def apply_sparse_edge_dither(image):
    """
    Apply a sparse dithering effect only to the edges (top, bottom, left, right), 
    fading towards the center while keeping the middle of the image fully intact.
    
    :param image: PIL Image to process.
    :return: Processed PIL Image.
    """
    image = image.convert("RGB")  # Preserve full color
    width, height = image.size
    mask = Image.new("L", (width, height), 255)  # Start with fully visible image

    max_dither_width = width // 4  # Max fade width (1/4 of the image width)
    max_dither_height = height // 4  # Max fade height (1/4 of the image height)

    for y in range(height):
        for x in range(width):
            # Determine distance to the closest edge (left, right, top, bottom)
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)

            # Only apply effect within the designated edge areas
            if dist_x < max_dither_width or dist_y < max_dither_height:
                fade_intensity = (min(dist_x, dist_y) / max(max_dither_width, max_dither_height)) ** 1.8  # Smooth fade
                fade_intensity = min(max(fade_intensity, 0), 1)  # Clamp between 0-1
                mask.putpixel((x, y), int(fade_intensity * 255))

    # Apply the dithering effect only to edge areas, keeping the center intact
    dithered = image.convert("L").convert("1")  # Convert grayscale before applying dithering
    final_image = Image.composite(image, dithered, mask)
    return final_image

# Apply sparse dithering only to edges
sparse_edge_dither_result = apply_sparse_edge_dither(image)

# Save result for download
sparse_edge_dither_path = "/mnt/data/sparse_edge_dither.jpg"
sparse_edge_dither_result.save(sparse_edge_dither_path)

# Provide download link
sparse_edge_dither_path
