# Re-load the files after execution state reset
import cv2
import numpy as np
import matplotlib.pyplot as plt

# Re-load the original image and mask
image_path = "/mnt/data/image_Screenshot from 2025-03-06 17-31-08.png"
mask_path = "/mnt/data/mask_Screenshot from 2025-03-06 17-31-08.png"

image_cv = cv2.imread(image_path)
mask_cv = cv2.imread(mask_path, cv2.IMREAD_UNCHANGED)  # Load with alpha channel if present

# Convert the mask to HSV to detect blue circles
hsv_mask = cv2.cvtColor(mask_cv, cv2.COLOR_BGR2HSV)

# Define HSV range for blue (same as before)
lower_blue = np.array([100, 100, 50])  
upper_blue = np.array([140, 255, 255])  

# Create a mask to detect blue circles
blue_mask = cv2.inRange(hsv_mask, lower_blue, upper_blue)

# Find contours (ROIs) based on the detected blue regions
contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Generate a plot with just the contour areas
fig, ax = plt.subplots(figsize=(10, 5))
ax.imshow(np.zeros_like(mask_cv), alpha=0)  # Transparent background for clarity
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
    rect = plt.Rectangle((x, y), w, h, edgecolor='red', facecolor='none', linewidth=2)
    ax.add_patch(rect)

plt.title("Detected Blue Circles (Mapped from Mask)")
plt.axis("off")
plt.show()

# Now extract these regions from the original image
extracted_rois = [image_cv[y:y+h, x:x+w] for x, y, w, h in [cv2.boundingRect(cnt) for cnt in contours]]

# Display extracted ROIs
num_rois = len(extracted_rois)
cols = min(4, num_rois)
rows = (num_rois // cols) + (num_rois % cols > 0)

fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
axes = axes.flatten() if num_rois > 1 else [axes]

for i, roi in enumerate(extracted_rois):
    axes[i].imshow(cv2.cvtColor(roi, cv2.COLOR_BGR2RGB))
    axes[i].axis("off")
    axes[i].set_title(f"ROI {i}")

for i in range(num_rois, len(axes)):  # Hide unused plots
    axes[i].axis("off")

plt.suptitle("Extracted ROIs from Original Image (Based on Mask)")
plt.show()
