#!/usr/bin/python3
"""
This uses an image processing kernel / matrix for a dialation effect by checking neighbor pixels for maximum value
This has a dialation effect and it is not biased it treats pixels equally. No edge or tranistion detection.
This started as a gray scale thicken only, but this version is updated to handle RGB thickening also. (probably works better on gray scale)
It is cool math.
Not yet working, needs updates yet. 02/21 3:18 pm
"""

import os   
import numpy as np
from PIL import Image
import argparse

input_path = "missing_FB_IMG_1737749270272.png"  # Replace with your file path
output_path = "output_whitebg_2752732759.png"

# Convert the image to a numpy array for line density adjustments
image_array = np.array(fixed_lines)

def thicken_lines(image_array, kernel_size=3):
    if image_array.ndim == 2:  # Grayscale (H, W)
        return np.maximum.reduce([
            np.roll(image_array, shift, axis)
            for axis in range(2)
            for shift in (-kernel_size, 0, kernel_size)
        ])
    elif image_array.ndim == 3 and image_array.shape[-1] == 3:  # RGB (H, W, 3)
        return np.stack([
            np.maximum.reduce([
                np.roll(image_array[:, :, c], shift, axis)
                for axis in range(2)
                for shift in (-kernel_size, 0, kernel_size)
            ])
            for c in range(3)  # Process R, G, B separately
        ], axis=-1)
    else:
        raise ValueError("Unsupported image format")

# Example usage:
thickened_array = thicken_lines(image_array)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Image Line Thicken with dialation method")
    parser.add_argument("--input", required=True, help="Path to input image")
    parser.add_argument("--output", required=True, help="Path to save upscaled image")
    parser.add_argument("--weight", type=int, default=4, help="Strength of change 1-10 (default: 4)")
    args = parser.parse_args()

    thicken(args.input, args.output, weight=args.weight)
