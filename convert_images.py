import sys
import os
from PIL import Image

def convert_jpg_to_png(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        if file.lower().endswith(".jpg"):
            jpg_path = os.path.join(input_dir, file)
            png_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".png")

            try:
                with Image.open(jpg_path) as img:
                    img.save(png_path, "PNG")
                print(f"Converted: {jpg_path} -> {png_path}")
            except Exception as e:
                print(f"Failed to convert {jpg_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_images.py <input_dir> <output_dir>")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    convert_jpg_to_png(input_dir, output_dir)
