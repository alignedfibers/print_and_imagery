#!/usr/bin/python3
"""
    Modified Image Aggregator and Dither Script
    Moves images from subfolders, dithers them, and places copies in a new directory.
    Original files are preserved. Uses Floyd-Steinberg dithering via PIL.
"""

import os, sys, shutil, random, string, argparse, mimetypes
from pathlib import Path
from PIL import Image
import magic

OUTPUT_LEVEL = "PROMPT"
FORBIDDEN_DIRS = {"/", "/root", "/etc", "/var", "/usr", "/dev", "/lib", "/lib64",
                  "/opt", "/run", "/sys", "/snap", "/srv", "/boot", "/cdrom", "/bin", "/sbin", "/1"}


def sanitize_imageload(thepath):
    """
    Safely attempts to open and fully load an image file.
    If the image is truncated, corrupt, or too large, logs and returns None.
    """
    #ImageFile.LOAD_TRUNCATED_IMAGES = False  
    #Image.MAX_IMAGE_PIXELS = None  # Disable bomb limit if you trust your dataset
    try:
        img = Image.open(thepath)
        img.load()  # Force load into memory (triggers errors early)
        return img
    except Exception as e:
        print(f"↳ Skipping file due to error: {thepath}\n   Reason: {type(e).__name__}: {e}")

def apply_dithering(image):
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected a PIL Image object, got {type(image)} instead.")
    grayscale = image.convert("L")
    dithered = grayscale.convert("1", dither=Image.FLOYDSTEINBERG)
    return dithered

def get_valid_source_dir(source_dir: str) -> Path:
    resolved_path = Path(source_dir).resolve(strict=True)
    if str(resolved_path) in FORBIDDEN_DIRS:
        raise ValueError(f"❌ ERROR: Cannot run on protected system directory '{resolved_path}'.")
    if not resolved_path.is_dir():
        raise ValueError(f"❌ ERROR: Source '{resolved_path}' is not a directory.")
    return resolved_path

def process_images(source_dir: Path, dest_dir: Path):
    print("=== Proces Images Func ===")
    script_name = Path(__file__).name  # Get this script's filename
    allowed_mime_prefix = "image/"

    do_info("=== Processing Images ===")
    do_info(f"📂 Source Directory: {source_dir}")
    do_info(f"📂 Destination Directory: {dest_dir}")
    do_info("=========================")
              
    # Take a snapshot of all files and directories under source_dir
    # Tried using the mime prefix in the rglob and scrapped it, easier to glob everything.
    if not source_dir.exists():
        raise FileNotFoundError(f"{source_dir} does not exist")
    if not source_dir.is_file() and not source_dir.is_dir():
        raise ValueError("Path exists but is neither file nor directory")
    if source_dir.is_file():
        all_files = [source_dir.resolve()]
    if source_dir.is_dir():
        all_files = list(source_dir.rglob("*"))

    for file_path in all_files: # Recursively find all files
        if not file_path.is_file():
            continue # Skip directories including new random named destination directory
        if file_path.is_relative_to(dest_dir) or file_path.parts[1] in FORBIDDEN_DIRS:
            do_info(f"🛑 Skipping file inside destination directory: {file_path}")
            continue  # Safety check - Avoid images copied already, and all system directories.
        do_info(f"📂{file_path}")
        do_info(f"📂{dest_dir}")
        do_info(f"🔎 Expected dest_dir: {dest_dir} (Type: {type(dest_dir)})")
      
        base_name = file_path.name
        #mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = magic.from_file(file_path, mime=True)
        # Skip the script itself
        if base_name == script_name:
            do_info(f"Skipping script itself: {file_path}")
            continue

        # Skip non-image files
        if not mime_type or not mime_type.startswith(allowed_mime_prefix):
            do_info(f"Skipping non-image file (detected as {mime_type}): {file_path}")
            continue
            
        # Extract base name and extension by spliting the name from the extension
        base, ext = os.path.splitext(base_name)
        ext = ext.lstrip('.') # Remove leading dot from extension

        # Resolve destination file path
        dest_file_path = dest_dir / base_name
        do_info(f"##### DESTINATION CORRECT? {dest_file_path}")
        do_info("====================================")
        do_info("====================================")
        do_info("====================================")
        do_info("====================================")

        if dest_file_path.exists():
            do_info("EXISTS")
            timestamp = int(file_path.stat().st_mtime)
            new_name = f"{base}_{timestamp}.{ext}" if ext else f"{base}_{timestamp}"
            dest_file_path = dest_dir / new_name
            do_info(f"What the hell new name {dest_file_path}")
            do_info("==")

        original_image = sanitize_imageload(file_path)
        if original_image is None: continue  # Skip failed load
        current_inflight_image = original_image.copy()
        laststate_image = original_image.copy()
        mask1_image = None #stubs later as array of complex diff/origin/svg/id
        mask2_image = None #stubs later as array or complex diff/origin/svg/id
        current_inflight_image = apply_dithering(current_inflight_image)
        current_inflight_image.save(dest_file_path)
    do_info("\n This is the end of the image processing and file writing loop \n")
    
def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def do_warning(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO", "WARNING"): return
    print(msg)

def do_yes_no_prompt():
    if OUTPUT_LEVEL != "PROMPT": return
    if input("Do you want to continue? (yes/no): ").strip().lower() not in ('yes', 'y'):
        print("Operation cancelled by user.")
        sys.exit(0)

def do_error(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO", "WARNING", "ERR"): return
    print(msg)

def do_info(msg):
    if OUTPUT_LEVEL not in ("PROMPT", "INFO"): return
    print(msg)

def validate_args(args):
    if args.input_path is None:
        do_warning("No input path specified. Using current directory. This will process all images below this directory and save output as new files to a randomly named folder here.\n"
                   "Please ensure you are in the intended directory. Type 'yes' to proceed or 'no' to cancel.")
        do_yes_no_prompt()
        args.input_path = Path.cwd() # Directly assign to the argument
    if args.output_path is None:
        do_warning("No output path specified. Using current directory. This will store all processed images to a randomly named directory here. Type 'yes' to proceed.")
        do_yes_no_prompt()
        args.output_path = Path.cwd() # Directly assign to the argument

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
    parser = argparse.ArgumentParser(description="Process with dither all images below directory tree and save each as new file into a new folder.")
    parser.add_argument("-ip", "--input-path", default=None, help="Source directory with images.")
    parser.add_argument("-op", "--output-path", default=None, help="Parent destination where new folder is created.")
    parser.add_argument("-si", "--silent", type=str, choices=("NONE", "ERR", "WARNING", "INFO", "PROMPT"),
                        default="PROMPT", help="Level of output verbosity.")
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