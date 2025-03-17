# Load the newly attached image
new_image_path = "/mnt/data/file-AMKnSunP1vtJ93FaFdE4rA"  # Assuming it's the new file
image = Image.open(new_image_path)

# Define the function to apply sparse dithering only on the edges
def generate_sparse_edge_dither(image, effect_type="comic"):
    """
    Apply a sparse dithering effect only to the edges (top, bottom, left, right) while keeping 
    the center of the image fully intact. Max dithering width is 1/4th of the image.
    
    :param image: PIL Image to process.
    :param effect_type: Type of effect ("comic", "regular", "ink_washout").
    :return: Processed PIL Image.
    """
    image = image.convert("RGB")  # Keep full color
    width, height = image.size
    mask = Image.new("L", (width, height), 255)  # Fully visible by default

    max_dither_width = width // 4  # Max dithering range is 1/4th of the image width

    for y in range(height):
        for x in range(width):
            # Calculate distance from the nearest image edge (left, right, top, bottom)
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            dist_to_edge = min(dist_x, dist_y)

            # Apply fade only within the max dithering width
            if dist_to_edge < max_dither_width:
                fade_intensity = (dist_to_edge / max_dither_width) ** 1.5  # Smooth gradient effect
                fade_intensity = min(max(fade_intensity, 0), 1)  # Clamp values between 0 and 1
                mask.putpixel((x, y), int(fade_intensity * 255))

    # Generate halftone/dither effect only for the fading edges
    if effect_type == "comic":
        dithered = image.convert("1")  # 1-bit dithering for a comic-style effect
    elif effect_type == "regular":
        dithered = image.convert("L").convert("1")  # Grayscale first for a softer dither
    else:  # Ink washout
        dithered = image.convert("L").point(lambda p: p * 0.8).convert("RGB")  # Washed-out effect

    # Apply fading mask to blend dithered edges while keeping the center untouched
    final_image = Image.composite(image, dithered, mask)
    return final_image

# Apply effects with sparse edge dithering
comic_edge_dither_result = generate_sparse_edge_dither(image, effect_type="comic")
regular_edge_dither_result = generate_sparse_edge_dither(image, effect_type="regular")
ink_washout_edge_result = generate_sparse_edge_dither(image, effect_type="ink_washout")

# Save results for download
comic_sparse_edge_dither_path = "/mnt/data/comic_sparse_edge_dither.jpg"
regular_sparse_edge_dither_path = "/mnt/data/regular_sparse_edge_dither.jpg"
ink_washout_sparse_edge_path = "/mnt/data/ink_washout_sparse_edge.jpg"

comic_edge_dither_result.save(comic_sparse_edge_dither_path)
regular_edge_dither_result.save(regular_sparse_edge_dither_path)
ink_washout_edge_result.save(ink_washout_sparse_edge_path)

# Provide download links
comic_sparse_edge_dither_path, regular_sparse_edge_dither_path, ink_washout_sparse_edge_path
