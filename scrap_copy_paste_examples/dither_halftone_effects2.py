# Re-load the original image
image = Image.open(image_path)

# Apply the effects fresh on the original image
comic_halftone_result = comic_book_halftone_fade(image)
regular_halftone_result = regular_halftone_fade(image)
ink_washout_result = ink_washout_effect(image)

# Save results for download
comic_halftone_path = "/mnt/data/comic_halftone.jpg"
regular_halftone_path = "/mnt/data/regular_halftone.jpg"
ink_washout_path = "/mnt/data/ink_washout.jpg"

comic_halftone_result.save(comic_halftone_path)
regular_halftone_result.save(regular_halftone_path)
ink_washout_result.save(ink_washout_path)

# Provide download links
comic_halftone_path, regular_halftone_path, ink_washout_path
