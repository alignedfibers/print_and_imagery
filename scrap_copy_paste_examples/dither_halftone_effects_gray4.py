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
