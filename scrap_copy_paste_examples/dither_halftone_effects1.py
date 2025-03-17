import cv2
import numpy as np
from PIL import Image, ImageFilter
from PIL import Image

# Load the uploaded image
image_path = "/mnt/data/file-AMKnSunP1vtJ93FaFdE4rA"
image = Image.open(image_path)

# Display the image to confirm successful loading
image.show()
# Define the functions for each effect
def comic_book_halftone_fade(image):
    image = image.convert("L")  # Convert to grayscale
    width, height = image.size
    mask = Image.new("L", (width, height), 255)

    for y in range(height):
        for x in range(width):
            distance = np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)
            max_distance = np.sqrt((width / 2) ** 2 + (height / 2) ** 2)
            fade_factor = distance / max_distance
            mask.putpixel((x, y), int(fade_factor * 255))

    halftone = image.filter(ImageFilter.CONTOUR)
    halftone = Image.composite(image, halftone, mask)
    return halftone

def regular_halftone_fade(image):
    image = image.convert("L")  # Convert to grayscale
    width, height = image.size
    mask = Image.new("L", (width, height), 255)

    for y in range(height):
        for x in range(width):
            fade_factor = (x / width + y / height) / 2
            mask.putpixel((x, y), int(fade_factor * 255))

    halftone = image.filter(ImageFilter.CONTOUR)
    halftone = Image.composite(image, halftone, mask)
    return halftone

def ink_washout_effect(image):
    image = image.convert("L")  # Convert to grayscale
    width, height = image.size
    mask = Image.new("L", (width, height), 255)

    for y in range(height):
        for x in range(width):
            fade_factor = (x / width + y / height) / 2
            mask.putpixel((x, y), int(fade_factor * 255))

    washed_out = Image.composite(image, Image.new("L", (width, height), 255), mask)
    return washed_out

# Apply the effects to the image
comic_halftone_result = comic_book_halftone_fade(image)
regular_halftone_result = regular_halftone_fade(image)
ink_washout_result = ink_washout_effect(image)

# Save and display results
comic_halftone_result.show(title="Comic Book Halftone Fade")
regular_halftone_result.show(title="Regular Halftone Fade")
ink_washout_result.show(title="Ink Washout Effect")
