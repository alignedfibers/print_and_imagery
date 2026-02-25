# Attempt a different method to thicken lines using a repeated filter approach

# Apply multiple passes of edge enhancement to thicken lines
thickened_lines = fixed_lines.filter(ImageFilter.CONTOUR).filter(ImageFilter.MaxFilter(3))

# Enhance the contrast further to make lines more prominent
thickened_and_darker_lines = ImageOps.autocontrast(thickened_lines)

# Save the updated thickened and darker version
final_thickened_lines_path = "/mnt/data/final_thickened_lines_image.png"
thickened_and_darker_lines.save(final_thickened_lines_path)

final_thickened_lines_path
