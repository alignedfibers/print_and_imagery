#!/usr/bin/python3
import os
from rembg import remove
from PIL import Image

# Force CPU processing
os.environ["U2NET_ENABLE_GPU"] = "False"

#input_path = "greentreesinbackground_2752732759.png"  # Replace with your file path
#output_path = "output_greentreesinbackground_2752732759.png"
def do_removebg(input_path,output_path):
    # Open the image - Scoobydo
    image = Image.open(input_path)
    # Remove the background
    output = remove(image)
    # Save the processed image
    output.save(output_path)
    print(f"Background removed and saved as: {output_path}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Remove Background")
    parser.add_argument("--input", required=True, help="Path to input image")
    parser.add_argument("--output", required=True, help="Path to save transparent bg image")
    args = parser.parse_args()
    
    do_removebg(args.input, args.output)
    
