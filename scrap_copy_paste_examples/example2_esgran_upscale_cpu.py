import torch
from PIL import Image
import numpy as np
import cv2
from realesrgan import RealESRGANer
from basicsr.archs.rrdbnet_arch import RRDBNet  # Required for the model

device = torch.device('cpu')

# Initialize RRDBNet Model (Used by RealESRGANer)
model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)

# Initialize RealESRGANer
upscaler = RealESRGANer(
    scale=4,
    model_path="RealESRGAN_x4plus.pth",
    model=model,
    tile=200,  # Adjust for CPU efficiency
    tile_pad=10,
    pre_pad=0,
    half=False,  # Disable FP16 (CPU cannot use FP16 efficiently)
    device=device
)

# Load input image
path_to_image = 'input_blkbg_2752732759.png'
image = cv2.imread(path_to_image, cv2.IMREAD_COLOR)
if image is None:
    raise FileNotFoundError(f"❌ Image not found: {path_to_image}")

image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert OpenCV BGR to RGB

# Upscale the image
output, _ = upscaler.enhance(image, outscale=4)

# Convert back to BGR and save
output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
cv2.imwrite('sr_image.png', output)

print("✅ Upscaling complete. Output saved to sr_image.png")
