import cv2
import numpy as np
import os

# Load image
image_path = "your_image.png"  # Change this to your image file
image_cv = cv2.imread(image_path)

# Convert image to HSV for color detection
hsv = cv2.cvtColor(image_cv, cv2.COLOR_BGR2HSV)

# Define the HSV range for detecting blue circles
lower_blue = np.array([100, 100, 50])  
upper_blue = np.array([140, 255, 255])  

# Create mask for blue areas
blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

# Find contours of the blue circles
contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Create output folder
output_folder = "extracted_circles"
os.makedirs(output_folder, exist_ok=True)

# Extract regions inside circles
for i, cnt in enumerate(contours):
    x, y, w, h = cv2.boundingRect(cnt)
    roi = image_cv[y:y+h, x:x+w]  # Crop the detected area

    # Save the extracted region
    output_path = os.path.join(output_folder, f"circle_{i}.png")
    cv2.imwrite(output_path, roi)

    print(f"Extracted circle {i}: Position=({x}, {y}), Size=({w}x{h}), Saved to {output_path}")

print(f"Finished! {len(contours)} regions extracted in '{output_folder}'")
