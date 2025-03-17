def generate_edge_fade_dither(image, effect_type="comic"):
    """
    Apply a halftone or dithered fading effect at the edges of the image while keeping the center fully intact.
    
    :param image: PIL Image to process.
    :param effect_type: Type of effect ("comic", "regular", "ink_washout").
    :return: Processed PIL Image.
    """
    image = image.convert("RGB")  # Keep full color
    width, height = image.size
    mask = Image.new("L", (width, height), 255)  # Start with fully visible image

    # Create a Gaussian fade effect towards the edges
    sigma = min(width, height) * 0.1  # Control fade distance, ~10% of the image size

    for y in range(height):
        for x in range(width):
            # Distance from the nearest edge (X and Y)
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            dist_to_edge = min(dist_x, dist_y)  # Minimum distance to any edge

            # Calculate fade intensity with a Gaussian curve
            fade_intensity = np.exp(-((dist_to_edge / sigma) ** 2))  # Gaussian curve for smooth transition

            # Set mask value (higher fade_intensity means less fading)
            mask.putpixel((x, y), int(fade_intensity * 255))

    # Generate halftone/dither effect only for the fading area
    if effect_type == "comic":
        dithered = image.convert("1")  # 1-bit dithering for a classic comic effect
    elif effect_type == "regular":
        dithered = image.convert("L").convert("1")  # Grayscale first for softer dithering
    else:  # Ink washout
        dithered = image.convert("L").point(lambda p: p * 0.8).convert("RGB")  # Slightly washed-out effect

    # Apply fading mask to merge dithered edges while keeping the center fully colored
    final_image = Image.composite(image, dithered, mask)
    return final_image

# Re-load the original image
image = Image.open(image_path)

# Apply effects to the edges only
comic_edge_dither_result = generate_edge_fade_dither(image, effect_type="comic")
regular_edge_dither_result = generate_edge_fade_dither(image, effect_type="regular")
ink_washout_edge_result = generate_edge_fade_dither(image, effect_type="ink_washout")

# Save results for download
comic_edge_dither_path = "/mnt/data/comic_edge_dither.jpg"
regular_edge_dither_path = "/mnt/data/regular_edge_dither.jpg"
ink_washout_edge_path = "/mnt/data/ink_washout_edge.jpg"

comic_edge_dither_result.save(comic_edge_dither_path)
regular_edge_dither_result.save(regular_edge_dither_path)
ink_washout_edge_result.save(ink_washout_edge_path)

# Provide download links
comic_edge_dither_path, regular_edge_dither_path, ink_washout_edge_path
