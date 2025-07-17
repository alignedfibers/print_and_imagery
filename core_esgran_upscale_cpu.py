#!/usr/bin/python3
"""
    ############
    Just to remember briefly.
    Minimal Real-ESRGAN script that runs exclusively on CPU.
    Optimizes for available CPU instructions (MKL, AVX, OpenMP).
    Does nothing beyond upscaling an image on CPU.
    CPU only and optimized due to both GPU normally in use so let them run.
    Will make a separate one that checks if CUDA devices available and use GPU
    Later combining work on both GPU1 GPU2 and CPU will make fast as possible.
    Takes arg switches of --input-path, -ip and --output-path, -op
    Test images for same name and prepend random string to avoid collisions on move.
    Test the parameters are valid, set to none as default.
    Default "none" is use current directory for input, and creates random destination directory as child.
    *This will move images from all levels of the subtree up to the new destination without collisions.
    *Test and error under any of the system directories. Intended for linux, might work on windows.
    *Only import not standard is "magic" - requirements.txt should list python-magic
    *python-magic will not work unless you have the system library libmagic, ensure to apt,df,yum,exc install it.
    ----------------------------
    Minimal Real-ESRGAN script that runs exclusively on CPU.
    Optimizes for available CPU instructions (MKL, AVX, OpenMP).
    Does nothing beyond upscaling an image on CPU.
    CPU only and optimized due to both GPU normally in use.
    Will make a separate one that checks if CUDA devices available and use GPU
    Later combining work on both GPU1 GPU2 and CPU will make fast as possible.

    Author: Shawn
    ############
"""
import os
import shutil
import magic
import mimetypes
import random
import string
import argparse
import uuid
import torch
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from pathlib import Path
OUTPUT_LEVEL = "PROMPT"

print("=== BEGIN ===")
# Directories to NEVER process
FORBIDDEN_DIRS = {"/", "/root", "/etc", "/var", "/usr", "/dev", "/lib", "/lib64",
                  "/opt", "/run", "/sys", "/snap", "/srv", "/boot", "/cdrom", "/bin", "/sbin", "/1"}

# Function to validate and resolve the source directory
def get_valid_source_dir(source_dir: str) -> Path:
    resolved_path = Path(source_dir).resolve(strict=True)  # Resolves `.` and `..`, follows symlinks, ensures it exists

    if str(resolved_path) in FORBIDDEN_DIRS:
        raise ValueError(f"❌ ERROR: Cannot run on protected system directory '{resolved_path}'.")

    if not resolved_path.is_dir():
        raise ValueError(f"❌ ERROR: Source '{resolved_path}' is not a directory.")

    return resolved_path

# Function to move images recursively while avoiding system-critical directories
def process_images(source_dir: Path, dest_dir: Path):
    print("=== Proces Images Func ===")
    script_name = Path(__file__).name  # Get this script's filename
    allowed_mime_prefix = "image/"

    print("=== Processing Images ===")
    print(f"📂 Source Directory: {source_dir}")
    print(f"📂 Destination Directory: {dest_dir}")
    print("=========================")
              
    # Take a snapshot of all files and directories under source_dir
    # Tried using the mime prefix in the rglob and scrapped it, easier to glob everything.
    all_files = list(source_dir.rglob("*"))  
 
    for file_path in all_files:  # Recursively find all files
        if not file_path.is_file():
            continue  # Skip directories including new random named destination directory
        if file_path.is_relative_to(dest_dir) or file_path.parts[1] in FORBIDDEN_DIRS:
            print(f"🛑 Skipping file inside destination directory: {file_path}")
            continue  # Safety check - Avoid images copied already, and all system directories.
        print(f"📂{file_path}")
        print(f"📂{dest_dir}")
        print(f"🔎 Expected dest_dir: {dest_dir} (Type: {type(dest_dir)})")
      
        base_name = file_path.name
        #mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = magic.from_file(file_path, mime=True)
        # Skip the script itself
        if base_name == script_name:
            print(f"Skipping script itself: {file_path}")
            continue

        # Skip non-image files
        if not mime_type or not mime_type.startswith(allowed_mime_prefix):
            print(f"Skipping non-image file (detected as {mime_type}): {file_path}")
            continue

        # Extract base name and extension
        base, ext = os.path.splitext(base_name)
        ext = ext.lstrip('.')  # Remove leading dot from extension

        # Resolve destination file path
        dest_file_path = dest_dir / base_name
        print(f"##### DESTINATION CORRECT? {dest_file_path}")
        print("====================================")
        print("====================================")
        print("====================================")
        print("====================================")
        
        if dest_file_path.exists():
            print("EXISTS")
            timestamp = int(file_path.stat().st_mtime)
            new_name = f"{base}_{timestamp}.{ext}" if ext else f"{base}_{timestamp}"
            dest_file_path = dest_dir / new_name
            print(f"What the hell new name {dest_file_path}")
            print("==")

        # Move the file
        print(f"Moving {file_path} to {dest_file_path}")
        shutil.move(str(file_path), str(dest_file_path))
    print("\n This is the end of the file move loop \n")

def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

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
        do_warning("Images in this dir and subdirs will be moved to a randomly named folder here.\n"
                   "Please ensure you are in the intended directory. Type 'yes' to proceed or 'no' to cancel.")
        do_yes_no_prompt()
        args.input_path = Path.cwd()  # Directly assign to the argument
    if args.output_path is None:
        do_warning("Images will be moved to a randomly named directory in the current directory.\n"
                   "Please ensure you are in the intended directory. Type 'yes' to proceed or 'no' to cancel.")
        do_yes_no_prompt()
        args.output_path = Path.cwd()  # Directly assign to the argument

    args.input_path = Path(args.input_path)
    if not args.input_path.exists():
        do_error(f"Input path does not exist: {args.input_path}")
    if not args.input_path.is_dir():
        do_error(f"Input path is not a directory: {args.input_path}")
    if not os.access(args.input_path, os.R_OK | os.W_OK | os.X_OK):
        do_error(f"Insufficient permissions for input path: {args.input_path}")

    args.output_path = Path(args.output_path)    
    if not args.output_path.exists():
        do_error(f"Output path does not exist: {args.output_path}") 
    if not args.output_path.is_dir():
        do_error(f"Output path is not a directory: {args.output_path}")  
    if not os.access(args.output_path, os.R_OK | os.W_OK | os.X_OK):
        do_error(f"Insufficient permissions for output path: {args.output_path}")

    if args.silent != "PROMPT":
        global OUTPUT_LEVEL
        OUTPUT_LEVEL = args.silent


def parse_args():
    #This sets defaults to none
    parser = argparse.ArgumentParser(description="Move all images from input-path given or current directory and subdirectory to new random named folder/n created within the current directory or output-path given")
    # Input path: can be file or directory; if omitted, we use current directory (with a warning)
    parser.add_argument("-ip", "--input-path", default=None, help="Path to source directory containing images and subdirectories with images.")
    # Output path: may be a file (when input is file) or a directory
    parser.add_argument("-op", "--output-path", default=None, help="Path to directory acting as parent where we create the archive folder images will be placed in.")
    # Silence my friend, has options for silence Errors, Errors+Warnings, Errors+Warnings+Info, Errors+Warnings+Info+Prompts
    parser.add_argument("-si", "--silent", type=str, choices=("NONE","ERR","WARNING","INFO","PROMPT"), default="PROMPT", help="PROMPT is all output and NONE is silent - NONE,ERR,WARNING,INFO,PROMPT")
    return parser.parse_args()

def flatten_helper(args):
    source_dir = get_valid_source_dir(args.output_path)
    output_dir = source_dir / generate_random_name()
    output_dir.mkdir(exist_ok=True)
    process_images(args.input_path, output_dir)

if __name__ == "__main__":
    arguments = parse_args()
    validate_args(arguments)
    flatten_helper(arguments)
    #upscale_image(args.input, args.output, scale=args.scale)
    #upscale_helper(args.input)
