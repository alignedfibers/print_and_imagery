# Apply a stronger darkening by aggressively enhancing contrast and reducing brightness further
strongly_darker_lines = fixed_lines.point(lambda p: max(p - 50, 0))  # Aggressively darken by subtracting brightness

# Save the strongly darkened version
strongly_darker_lines_path = "/mnt/data/strongly_darker_lines_image.png"
strongly_darker_lines.save(strongly_darker_lines_path)

strongly_darker_lines_path
