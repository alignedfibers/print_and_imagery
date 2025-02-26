import cv2
import numpy as np
import pandas as pd

# **Load Image and Convert to Grayscale**
def load_image(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        raise ValueError("Error loading image. Check file path.")
    
    if image.shape[-1] == 4:  # Remove alpha channel if present
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image, gray

# **Analyze Image for Print Resolution Recommendations**
def analyze_print_resolution(image, gray):
    # **Detecting Line Thickness & Smallest Details**
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # **Measure Average Line Thickness**
    if contours:
        line_thicknesses = [cv2.arcLength(cnt, closed=False) / max(len(cnt), 1) for cnt in contours if len(cnt) > 10]
        average_line_thickness = np.mean(line_thicknesses) if line_thicknesses else 0
    else:
        average_line_thickness = 0  # No contours detected

    # **Checking Halftone/Dither Size**
    halftone_variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    # **Checking Gradient Smoothing & Fade Transitions**
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    gradient_shading_complexity = np.abs(gray.astype(float) - blurred.astype(float)).mean()

    # **Assessing Complexity of Design**
    edge_density = np.sum(edges) / (gray.shape[0] * gray.shape[1])
    complexity_score = min(100, int(edge_density * 100))  # Scale to 0-100

    # **Checking Recommended Printer Resolutions for Large and Small Prints**
    
    # **Max recommended printer resolution at large size** (Avoids fade, keeps details crisp)
    if halftone_variance > 1000 and average_line_thickness < 2:
        max_large_printer_resolution = (5760, 1440)  # Highest resolution if halftones & lines are very detailed
    else:
        max_large_printer_resolution = (1440, 600)  # Balanced clarity vs. bleed

    # **Minimal recommended printer resolution at large size** (Prevents excessive ink spread, avoids over-saturation)
    if gradient_shading_complexity < 5:
        min_large_printer_resolution = (1200, 600)  # Lower resolution helps with gradient smoothness
    else:
        min_large_printer_resolution = (1440, 600)  # Keeps shading while reducing potential ink bleeding

    # **Max recommended printer resolution at smallest size** (Ensures tiny lines stay visible without merging)
    if average_line_thickness < 2:
        max_small_printer_resolution = (1440, 600)  # Small prints don't need excessive DPI, but 1440 helps clarity
    else:
        max_small_printer_resolution = (1200, 600)  # Reducing DPI slightly reduces ink spread

    # **Minimal recommended printer resolution at smallest size** (Avoids oversaturation on a tiny print)
    if complexity_score < 50:
        min_small_printer_resolution = (600, 300)  # Lower DPI prevents ink buildup on small prints
    else:
        min_small_printer_resolution = (1200, 600)  # Keeps balance between sharpness and ink diffusion

    # **Understanding Resolution Adjustment Effect on Bleed and Fade**
    adjustment_effect = {
        "Increasing resolution (higher DPI)": "Reduces fade, but may cause more ink bleed if too high.",
        "Decreasing resolution (lower DPI)": "Prevents ink bleed but may cause shading & halftone details to fade."
    }

    # **Final Recommendation Table**
    analysis_print_resolution = {
        "Metric": [
            "Max Recommended Printer Resolution (Large Size)",
            "Min Recommended Printer Resolution (Large Size)",
            "Max Recommended Printer Resolution (Small Size)",
            "Min Recommended Printer Resolution (Small Size)",
            "Effect of Increasing Resolution",
            "Effect of Decreasing Resolution"
        ],
        "Value": [
            f"{max_large_printer_resolution[0]} x {max_large_printer_resolution[1]} DPI",
            f"{min_large_printer_resolution[0]} x {min_large_printer_resolution[1]} DPI",
            f"{max_small_printer_resolution[0]} x {max_small_printer_resolution[1]} DPI",
            f"{min_small_printer_resolution[0]} x {min_small_printer_resolution[1]} DPI",
            adjustment_effect["Increasing resolution (higher DPI)"],
            adjustment_effect["Decreasing resolution (lower DPI)"]
        ]
    }

    # Convert results to DataFrame
    df_print_resolution_analysis = pd.DataFrame(analysis_print_resolution)

    return df_print_resolution_analysis

# **Run Analysis**
if __name__ == "__main__":
    image_path = "your_image.png"  # Update with your actual file path
    image, gray = load_image(image_path)
    df_results = analyze_print_resolution(image, gray)

    # Display results
    print(df_results)

    # Save results for external reference
    df_results.to_csv("Print_Resolution_Recommendations.csv", index=False)
    print("\n✅ Results saved to 'Print_Resolution_Recommendations.csv'")
