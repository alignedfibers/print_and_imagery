import numpy as np
import pandas as pd
import cv2
import matplotlib.pyplot as plt

# **Load Image and Convert to RGB**
def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Load with alpha if present
    if image is None:
        raise ValueError("Error loading image. Check file path.")
    
    if image.shape[-1] == 4:  # If the image has an alpha channel, remove it
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    return image

# **Check RGB Ratio Variance**
def analyze_rgb_variance(image):
    # Convert the image to float for ratio calculations (avoid division by zero)
    image_float = image.astype(np.float32) + 1

    # Split into R, G, B channels
    R, G, B = cv2.split(image_float)

    # **Calculate Ratios Relative to Red (R)**
    G_ratio = G / R
    B_ratio = B / R
    GB_ratio = G / B

    # **Measure Deviations in G, B Relative to Each Other**
    G_deviation = G_ratio - np.mean(G_ratio)
    B_deviation = B_ratio - np.mean(B_ratio)
    GB_deviation = GB_ratio - np.mean(GB_ratio)

    # **Absolute deviation calculations**
    G_absolute_deviation = np.abs(G_deviation)
    B_absolute_deviation = np.abs(B_deviation)
    GB_absolute_deviation = np.abs(GB_deviation)

    # **Final Variance Analysis for RG, RB, and GB Ratios**
    analysis_rgb_ratio_variances = {
        "Metric": [
            "Mean Absolute Deviation (G to R)",
            "Median Absolute Deviation (G to R)",
            "Average Absolute Deviation (G to R)",
            "Variance of G to R Ratio",
            "Mean Absolute Deviation (B to R)",
            "Median Absolute Deviation (B to R)",
            "Average Absolute Deviation (B to R)",
            "Variance of B to R Ratio",
            "Mean Absolute Deviation (G to B)",
            "Median Absolute Deviation (G to B)",
            "Average Absolute Deviation (G to B)",
            "Variance of G to B Ratio",
        ],
        "Value": [
            np.mean(G_absolute_deviation),
            np.median(G_absolute_deviation),
            np.mean(G_absolute_deviation),
            np.var(G_ratio),
            np.mean(B_absolute_deviation),
            np.median(B_absolute_deviation),
            np.mean(B_absolute_deviation),
            np.var(B_ratio),
            np.mean(GB_absolute_deviation),
            np.median(GB_absolute_deviation),
            np.mean(GB_absolute_deviation),
            np.var(GB_ratio)
        ]
    }

    # Convert results to DataFrame
    df_rgb_ratio_variance_analysis = pd.DataFrame(analysis_rgb_ratio_variances)

    return df_rgb_ratio_variance_analysis

# **Run Analysis**
if __name__ == "__main__":
    image_path = "your_image.png"  # Update with your actual file path
    image = load_image(image_path)
    df_results = analyze_rgb_variance(image)

    # Display results
    print(df_results)
