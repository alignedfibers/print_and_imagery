#!/usr/bin/python3
"""
simple_esgran_upscale_cpu.py
----------------------------
Minimal Real-ESRGAN script that runs exclusively on CPU.
Optimizes for available CPU instructions (MKL, AVX, OpenMP).
Does nothing beyond upscaling an image on CPU.
CPU only and optimized due to both GPU normally in use.
Will make a separate one that checks if CUDA devices available and use GPU
Later combining work on both GPU1 GPU2 and CPU will make fast as possible.

Author: Shawn
"""
import uuid
import torch
import cv2
import os
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
OUTPUT_LEVEL = "PROMPT"

def check_cpu_optimizations():
    """ Check available CPU optimizations and enable them if supported. """
    optimizations = {
        "MKL": torch._C.has_mkl,
        "MKL-DNN": torch.backends.mkldnn.enabled,
        "OpenMP": torch.backends.openmp.is_available(),
        #"AVX": torch.has_avx,
        #"AVX2": torch.has_avx2,
        #"FMA": torch.has_fma,
    }
    
    do_info("\n🔍 CPU Optimizations Available:")
    for opt, available in optimizations.items():
        print(f"  {opt}: {'✅ Enabled' if available else '❌ Not Available'}")

    if not any(optimizations.values()):
        print("⚠ No CPU optimizations detected. Performance may be slow.")

def load_model(model_path, scale):
    """ Load Real-ESRGAN model, forcing CPU execution """
    #This line creates an instance of the RRDBNet model, which is a ResNet-based super-resolution network used in Real-ESRGAN.
    """
        ### **📌 Breaking Down Each Parameter**
        | Parameter        | Value  | What It Does |
        |------------------|--------|-----------------------------------------------------------------------------------------|
        | `num_in_ch=3`    | `3`    | Number of input channels (3 for **RGB images**).                                        |
        | `num_out_ch=3`   | `3`    | Number of output channels (**also RGB**).                                               |
        | `num_feat=64`    | `64`   | Number of feature maps in the first convolution layer (controls model size).            |
        | `num_block=23`   | `23`   | Number of **Residual-in-Residual Dense Blocks (RRDB)** in the network (controls depth). |
        | `num_grow_ch=32` | `32`   | Growth factor for feature channels in dense connections (controls learning power).      |
        | `scale=scale`    | `4` (or user-defined) | Upscaling factor (e.g., **4x for 4x resolution boost**).                 |
    """    
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)
    device = "cpu"
    
    upscaler = RealESRGANer(
        scale=scale,
        model_path=model_path,
        model=model,
        tile=200,  # Adjust if needed
        tile_pad=10,
        pre_pad=0,
        half=False,  # Disable FP16 (not needed for CPU)
        device=device
    )

    return upscaler

def upscale_image(input_path, output_path, scale=4):
    """ Perform image upscaling on CPU """
    model_path = "./models/RealESRGAN_x4plus.pth"
    
    if not os.path.exists(model_path):
        print(f"❌ Model file '{model_path}' not found. Download it from the official repo.")
        return

    check_cpu_optimizations()
    upscaler = load_model(model_path, scale)

    # Load image
    img = cv2.imread(input_path, cv2.IMREAD_COLOR)
    if img is None:
        print(f"❌ Failed to load image: {input_path}")
        return

    #Converts an image from OpenCV's default BGR color format to RGB.
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Enhance resolution
    output, _extra = upscaler.enhance(img, outscale=scale)
    #meta = _extra[0] if _extra else None
    # Save output
    output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, output)
    print(f"✅ Upscaled image saved to: {output_path}")

def upscale_image_runner(input_dir, output_dir, scaleval):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(input_dir):
        if file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")):
            input_path = os.path.join(input_dir, file)
            output_path = os.path.join(output_dir, os.path.splitext(file)[0] + ".png")
            if os.path.exists(output_path): 
                output_path = os.path.join(output_dir, os.path.splitext(file)[0] +str(uuid.uuid4())[-4:]+ ".png")

            try:
                upscale_image(input_path, output_path, scale=scaleval)
                print(f"Upscaled: {input_path} -> {output_path}")
            except Exception as e:
                print(f"Failed to convert {output_path}: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Real-ESRGAN CPU-only Image Upscaler")
    # Recursion flag (like -r in cp)
    parser.add_argument("-r", "--recursion", action="store_true", help="Process images in directories recursively. Ignored if input-path is not a directory")
    # Input path: can be file or directory; if omitted, we use current directory (with a warning)
    parser.add_argument("-ip", "--input-path", default=None, help="Path to input file or directory. If not specified, current directory is used.")
    # Output path: may be a file (when input is file) or a directory
    parser.add_argument("-op", "--output-path", default=None, help="Path to output file or directory. Optional.")
    # Scale factor, with values 0-5 and default of 4
    parser.add_argument("-sc", "--scale", type=int, choices=range(0,6), default=4, help="Upscaling factor (0-5, default: 4)")
    # Silence my friend, has options for silence Errors, Errors+Warnings, Errors+Warnings+Info, Errors+Warnings+Info+Prompts
    parser.add_argument("-si", "--silent", type=str, choices=("NONE","ERR","WARNING","INFO","PROMPT"), default="PROMPT", help="PROMPT is all output and NONE is silent - NONE,ERR,WARNING,INFO,PROMPT")
    return parser.parse_args()     

def do_warning(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO", "WARNING"):
        return
    print(msg)
def do_yes_no_prompt():
    #Do yes/no prompt
    if OUTPUT_LEVEL != "PROMPT":
        return
    if input("Do you want to continue? (yes/no): ").strip().lower() not in ('yes', 'y'):
        print("Operation cancelled by user.")
        sys.exit(0)
def do_error(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO", "WARNING","ERR"):
        return
    print(msg)
def do_info(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO"):
        return
    print(msg)
         
def validate_args(args):
    #inspect and decorate the arguments according to logic requiring checks
    if args.input_path is None:
        do_warn("All images in current directory will be scaled and saved as with new file names\n \
        No path specified please take caution")
        do_yes_no_prompt()
    if args.silent != "PROMPT":
        global OUTPUT_LEVEL
        OUTPUT_LEVEL = args.silent

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Real-ESRGAN CPU-only Image Upscaler")
    parser.add_argument("--input", required=True, help="Path to input image")
    parser.add_argument("--output", required=True, help="Path to save upscaled image")
    parser.add_argument("--scale", type=int, default=4, help="Upscaling factor (default: 4)")
    args = parser.parse_args()
    #validate_args(arguments)
    upscale_image(args.input, args.output, scale=args.scale)
    #upscale_helper(args.input)