def generate_dither_fade(image, effect_type="comic"):
    """
    Apply a halftone or dithered fading effect, keeping full color in the center and transitioning 
    into a dither effect toward the edges.
    
    :param image: PIL Image to process.
    :param effect_type: Type of effect ("comic", "regular", "ink_washout").
    :return: Processed PIL Image.
    """
    image = image.convert("RGB")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)

    # Define how much of the image should remain unaltered (e.g., 75% of the width/height)
    fade_start = 0.25  # The transition begins at 25% from the edge

    for y in range(height):
        for x in range(width):
            # Calculate normalized distance from the center to the edge
            distance_x = min(x / width, (width - x) / width)
            distance_y = min(y / height, (height - y) / height)
            distance = min(distance_x, distance_y)

            # Compute fade factor
            if distance > fade_start:  
                fade_factor = (distance - fade_start) / (0.5 - fade_start)
                fade_factor = min(max(fade_factor, 0), 1)  # Clamp values between 0 and 1
                mask.putpixel((x, y), int(fade_factor * 255))
            else:
                mask.putpixel((x, y), 0)

    # Convert to dither effect (comic style uses stronger contrast)
    if effect_type == "comic":
        dithered = image.convert("1")  # 1-bit dithering (black/white dots)
    elif effect_type == "regular":
        dithered = image.convert("L").convert("1")  # Convert grayscale first for finer dithering
    else:  # Ink washout
        dithered = image.convert("L").point(lambda p: p * 0.7).convert("RGB")

    # Apply fading mask to dithered image
    final_image = Image.composite(image, dithered, mask)
    return final_image

# Re-load original image
image = Image.open(image_path)

# Apply effects
comic_dither_result = generate_dither_fade(image, effect_type="comic")
regular_dither_result = generate_dither_fade(image, effect_type="regular")
ink_washout_result = generate_dither_fade(image, effect_type="ink_washout")

# Save results for download
comic_dither_path = "/mnt/data/comic_dither.jpg"
regular_dither_path = "/mnt/data/regular_dither.jpg"
ink_washout_path = "/mnt/data/ink_washout_dither.jpg"

comic_dither_result.save(comic_dither_path)
regular_dither_result.save(regular_dither_path)
ink_washout_result.save(ink_washout_path)

# Provide download links
comic_dither_path, regular_dither_path, ink_washout_path
