import cv2
import numpy as np

def create_fade_outline(image_path, output_path, fade_pixels=20, shadow_intensity=0.5):
    """
    Adds a fading dark glow around the subject to ensure visibility when printed on light backgrounds.

    Parameters:
    - image_path: Path to the input image.
    - output_path: Path to save the processed image.
    - fade_pixels: The number of pixels outward the fade should extend.
    - shadow_intensity: Darkness level (0 to 1), where 1 is black.
    """
    
    # Load image
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image is None:
        print("Error: Could not load image.")
        return

    # Convert to grayscale and threshold to find edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)

    # Create a distance transform to spread the effect outward
    dist_transform = cv2.distanceTransform(cv2.bitwise_not(edges), cv2.DIST_L2, 5)
    
    # Normalize to range 0-1
    dist_transform = cv2.normalize(dist_transform, None, 0, 1.0, cv2.NORM_MINMAX)
    
    # Apply fading effect based on distance
    fade_mask = (1 - dist_transform) ** 2  # Adjust falloff curve
    fade_mask = (fade_mask * 255).astype(np.uint8)

    # Limit the fade effect to a specific range
    fade_mask = cv2.GaussianBlur(fade_mask, (fade_pixels, fade_pixels), 0)

    # Convert fade mask to a darkening shadow (multiply channels)
    shadow = np.zeros_like(image, dtype=np.float32)
    for i in range(3):  # Apply shadow to R, G, B channels
        shadow[:, :, i] = image[:, :, i] * (1 - (shadow_intensity * fade_mask / 255))

    # Convert back to 8-bit
    shadow = np.clip(shadow, 0, 255).astype(np.uint8)

    # Save output
    cv2.imwrite(output_path, shadow)
    print(f"Processed image saved to {output_path}")

# Example usage (this will run when executing the script)
if __name__ == "__main__":
    create_fade_outline("input.jpg", "output.jpg", fade_pixels=30, shadow_intensity=0.6)
