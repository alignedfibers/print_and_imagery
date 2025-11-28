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
import os, sys, shutil, random, string, argparse, mimetypes
import magic
import uuid
import torch
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from pathlib import Path
from PIL import Image

OUTPUT_LEVEL = "PROMPT"
FORBIDDEN_DIRS = {"/", "/root", "/etc", "/var", "/usr", "/dev", "/lib", "/lib64",
                  "/opt", "/run", "/sys", "/snap", "/srv", "/boot", "/cdrom", "/bin", "/sbin", "/1"}

"""
* Begin set of image processing functions
* This can be applied each individually.
"""
def apply_dithering(image):
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected a PIL Image object, got {type(image)} instead.")
    grayscale = image.convert("L")
    dithered = grayscale.convert("1", dither=Image.FLOYDSTEINBERG)
    return dithered

def apply_upscale(image,scale=4):
    """
    Perform image upscaling on CPU 
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected a PIL Image object, got {type(image)} instead.")

    #model_path = "./models/RealESRGAN_x4plus.pth"   
    model_path = str(Path(__file__).resolve().parent / "models" / "RealESRGAN_x4plus_anime_6B.pth")
    do_info(model_path)
    if not os.path.exists(model_path):
        do_info(f"❌ Model file '{model_path}' not found. Download it from the official repo.")
        return

    check_cpu_optimizations()
    upscaler = load_model(model_path, scale)

    #Converts an image from PIL to numpy n-dimensional-array
    img = np.array(image)
    """
    * img should already be in RGB format, use cv2 if BGR to RGB conversion needed
    * img = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    """

    # Enhance resolution
    output, _extra = upscaler.enhance(img, outscale=scale)
    if output is None:
        raise ValueError("Upscaling failed: output is None")
    if output.dtype != np.uint8:
        output = output.astype(np.uint8)
    pil_output = Image.fromarray(output)
    #meta = _extra[0] if _extra else None
    # Save output
    #output = cv2.cvtColor(output, cv2.COLOR_RGB2BGR)
    #cv2.imwrite(output_path, output)
    do_info(f"✅ Upscaling complete returning")
    return pil_output

"""
*Image processing helpers specifically used
*with the apply functions they are for only.
"""
def load_model(model_path, scale):
    """ 
    Load Real-ESRGAN model, forcing CPU execution
    Used with apply_upscale()
    """
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
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=6, num_grow_ch=32, scale=scale)
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
"""
* Common and needed helpers across most / all image processing functions
"""
def check_cpu_optimizations():
    """ 
    Check available CPU optimizations and enable them if supported. 
    Used for upscale and other torch assisted processing 
    """
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
        do_info(f"  {opt}: {'✅ Enabled' if available else '❌ Not Available'}")

    if not any(optimizations.values()):
        do_info("⚠ No CPU optimizations detected. Performance may be slow.")

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
        do_info(f"↳ Skipping file due to error: {thepath}\n   Reason: {type(e).__name__}: {e}")


"""
* Reusable directory, path, 
* and batch helpers
"""
def get_valid_source_dir(source_dir: str) -> Path:
    """
    Function to validate and resolve the source directory
    """
    resolved_path = Path(source_dir).resolve(strict=True)  # Resolves `.` and `..`, follows symlinks, ensures it exists

    if str(resolved_path) in FORBIDDEN_DIRS:
        raise ValueError(f"❌ ERROR: Cannot run on protected system directory '{resolved_path}'.")

    if not resolved_path.is_dir():
        raise ValueError(f"❌ ERROR: Source '{resolved_path}' is not a directory.")

    return resolved_path


def process_images(source_dir: Path, dest_dir: Path):
    """
    Function to find and process image files
    Receives path information from the calling function
    """
    do_info("=== Proces Images Func ===")
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
 
    for file_path in all_files:  # Recursively find all files
        if not file_path.is_file():
            continue  # Skip directories including new random named destination directory
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

        # Extract base name and extension
        base, ext = os.path.splitext(base_name)
        ext = ext.lstrip('.')  # Remove leading dot from extension

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
            do_info(f"New name {dest_file_path}")
            do_info("==")

        original_image = sanitize_imageload(file_path)
        if original_image is None: continue  # Skip failed load
        current_inflight_image = original_image.copy()
        laststate_image = original_image.copy()
        mask1_image = None #stubs later as array of complex diff/origin/svg/id
        mask2_image = None #stubs later as array or complex diff/origin/svg/id
        #current_inflight_image = apply_dithering(current_inflight_image)
        current_inflight_image = apply_upscale(current_inflight_image)
        current_inflight_image.save(dest_file_path)
        # Move the file
        #do_info(f"Moving {file_path} to {dest_file_path}")
        #shutil.move(str(file_path), str(dest_file_path))
    do_info("\n This is the end of the file processing loop \n")

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
    do_info("=== BEGIN ===")
    arguments = parse_args()
    validate_args(arguments)
    flatten_helper(arguments)
    #upscale_image(args.input, args.output, scale=args.scale)
    #upscale_helper(args.input)
