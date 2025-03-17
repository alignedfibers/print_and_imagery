import numpy as np
import cv2

# Load Image (ensure float for precision)
image = cv2.imread("your_image.png", cv2.IMREAD_UNCHANGED).astype(np.float32) + 1e-6  # Avoid division by zero

# Split Channels
R, G, B = cv2.split(image)

# Normalize Each Pixel (Ensuring Sum of 1 Per Pixel)
total = R + G + B
R_norm = R / total
G_norm = G / total
B_norm = B / total

# Compute Global Norm Ratios (Expected Baseline)
global_R_norm = np.mean(R_norm)
global_G_norm = np.mean(G_norm)
global_B_norm = np.mean(B_norm)

# Compute Per-Pixel Deviations
R_dev = R_norm - global_R_norm
G_dev = G_norm - global_G_norm
B_dev = B_norm - global_B_norm

# Compute If Spread Increased (Channels Drift Further Apart)
spread_increase_mask = (np.abs(R_dev - G_dev) > np.abs(global_R_norm - global_G_norm)) | \
                        (np.abs(R_dev - B_dev) > np.abs(global_R_norm - global_B_norm)) | \
                        (np.abs(G_dev - B_dev) > np.abs(global_G_norm - global_B_norm))

# Compute If Spread Decreased (Channels Move Closer Together)
spread_decrease_mask = (np.abs(R_dev - G_dev) < np.abs(global_R_norm - global_G_norm)) & \
                        (np.abs(R_dev - B_dev) < np.abs(global_R_norm - global_B_norm)) & \
                        (np.abs(G_dev - B_dev) < np.abs(global_G_norm - global_B_norm))

# Extract Pixels that Lower or Increase Spread
spread_decrease_pixels = image[spread_decrease_mask]
spread_increase_pixels = image[spread_increase_mask]
