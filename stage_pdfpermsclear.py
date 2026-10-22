#!/usr/bin/python3
"""
    ############
    PDF perms add remove
    Handles
    Individual files
    Whole directories

    Author: Shawn
    ############
"""
import os, sys, shutil, random, string, argparse, mimetypes
import magic
import uuid
import torch
import cv2
import pikepdf
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from pathlib import Path
from PIL import Image

OUTPUT_LEVEL = "PROMPT"
FORBIDDEN_DIRS = {"/", "/root", "/etc", "/var", "/usr", "/dev", "/lib", "/lib64",
                  "/opt", "/run", "/sys", "/snap", "/srv", "/boot", "/cdrom", "/bin", "/sbin", "/1"}

"""
* Begin set of pdf processing functions
* This can be applied each individually.
"""

#def apply_pdf_to_png() takes a pdf object and converts a single page to png

def save_pdf_nopassword(pdf):
    """
    Processes pdf to save without restricted permissions & reopens.
    Receive an opened PDF and return it without encryption.
    Encryption removal occurs during save with encryption=False.
    *pdf preopened using passsword "" or actual password before pass-in.
    Password just decides if allow/restrict from pdffile permissions _ original.
    Perms are Comment, Select Copy, Accessibility Copy, Edit Content, Edit Form Field, Print, Sign
    """
    if not isinstance(pdf, pikepdf.Pdf):
        do_error(f"Expected pikepdf.Pdf, got {type(pdf)} instead.")
        #error type pause sequence on this task log fail in task sequence report, do not complete downstream actions, add to unpause review ticket-queue.
        #I am just learning python, this was previous system error as as recommended by chatgpt, but I handle my own alerts and error coms to user.
        #I like the log functionality here, but for coupling and portability, my function loader should accept a logger instead of me direct send via my "do_error"
        #Since java code is where I have read, seem right way to me "log4j" or something I recall, anyways, instead of do error, we should build a logger that 
        #implements do error, do warn excetera internally and exposes a common set of functions for logging. Also instead of handling in function
        #we should raise exceptions from functions, and not handle them, the implementation details that called it should free the developer to easily
        #handle the raised exception. This particularily allows and agent to see more about the internals if called via api, same as regular code.
        #Since some exceptions require specific "safeties" handler/handling before giving control over to the developer or agent, we could create 
        #custom exceptions that have a :before :after for control of how to handle. Since I intend to compose and prioritized functions autonomously, 
        #it is important that we consider differences between "logger" and chain_context project people will understand as "Task">"Activity" network flow
        #where the chained_context tracks the completion state of the intended compostion of tasks, operations and service desk will understand the err as 
        #automation fail tickets, where completion failed for some reason. I see this is "I need a human" and human can unblock. I see tasks as full package
        #and the Activity as work being completed, all having dependencies, but task rolls up to a completed state, how the work or automation within the
        #the activity handling is completed can be across of multiple hybrid ways, and the responsibility will be in the completion error which by work
        #understanding is, "what queue does the failure get placed in?"
        return pdf  
    if not pdf.is_encrypted:
        do_info("PDF is already unencrypted. No changes made.")
    else
        source = Path(pdf.filename)
        original_mode = stat.S_IMODE(source.stat().st_mode)
        fd, temporary = tempfile.mkstemp(
            prefix=".pdfclearperms-",
            suffix=".pdf",
            dir=source.parent
        )
        os.close(fd)

        try:
            pdf.save(temporary, encryption=False)
            with pikepdf.open(temporary) as verified:
                if verified.is_encrypted:
                    do_warn("PDF is still encrypted.")
                if len(verified.pages) != len(pdf.pages):
                    do_warn("Page count changed.")

            os.chmod(temporary, original_mode)
            os.replace(temporary, source)

        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
        try:
            pdf = pikepdf.open(source)
        except (pikepdf.PdfError, OSError) as exc:
            do_warn(f"Failed_lost skipping PDF {source}: {exc}")

        
    pdfperms = pdf.allow

    permissions = {
        "Commenting": pdfperms.modify_annotation,
        "Content copying": pdfperms.extract,
        "Content copying for accessibility": pdfperms.accessibility,
        "Editing file content": pdfperms.modify_other,
        "Filling form fields": pdfperms.modify_form,
        "Printing": pdfperms.print_lowres or pdfperms.print_highres,
    }

    info = (
        f"PDF: {source.name}\n"
        f"Encrypted: {pdf.is_encrypted}\n\n"
        "File permissions:\n"
        + "\n".join(
            f"  {name}: {'Allowed' if allowed else 'Not allowed'}"
            for name, allowed in permissions.items()
        )
    )

    do_info(info)

    return pdf

def save_pdf_withrandompassword(pdf):
    #create a random password
    #save pdf with random password
    #reopen to confirm password works.
    #if exists asymetric device key linked with authenticator
    #then encryptpassword with asymetric device key else vanilla
    #save the new password to current users linux keychain.A
    #same check when decrypt, prompt for authenticator token as needed.
    return pdf

def apply_png_to_pdf_page(image, page_width_in=8.5, page_height_in=11, dpi=300):
    """
    Convert a PIL image into a single PDF-ready page image.
    Fits within a normal page while preserving aspect ratio.
    """
    if not isinstance(image, Image.Image):
        raise TypeError(f"Expected a PIL Image object, got {type(image)} instead.")

    rgb_image = image.convert("RGB")

    page_width_px = int(page_width_in * dpi)
    page_height_px = int(page_height_in * dpi)

    scale = min(page_width_px / rgb_image.width, page_height_px / rgb_image.height)
    new_width = int(rgb_image.width * scale)
    new_height = int(rgb_image.height * scale)

    resized = rgb_image.resize((new_width, new_height), Image.LANCZOS)

    page = Image.new("RGB", (page_width_px, page_height_px), "white")
    x_offset = (page_width_px - new_width) // 2
    y_offset = (page_height_px - new_height) // 2
    page.paste(resized, (x_offset, y_offset))

    return page

"""
*Processing helpers specifically used
*with the apply functions they are for only.
"""
#def
"""
* Common and needed helpers across most / all processing functions
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

def sanitize_pdfload(thepath):
    """
    Safely attempts to open a PDF.
    Returns None for PDFs that cannot be processed.
    """
    try:
        pdf = pikepdf.open(thepath, password="")
        #if not pdf.is_encrypted:
        #    do_info(f"Skipping already unencrypted PDF: {thepath}")
        #    pdf.close()
        #    return None
        return pdf
    except Exception as e:
        do_info(f"↳ Skipping file due to error: {thepath}\n   Reason: {type(e).__name__}: {e}")
        return None

"""
* Reusable directory, path, 
* and batch helpers
"""
def get_valid_parent_dir(parent _dir: str) -> Path:
    """
    Function to validate and resolve the source directory
    """
    resolved_path = Path(parent_dir).resolve(strict=True)  # Resolves `.` and `..`, follows symlinks, ensures it exists
 
    if str(resolved_path) in FORBIDDEN_DIRS: 
        raise ValueError(f"❌ ERROR: Cannot run on protected system directory '{resolved_path}'.")

    if not resolved_path.is_dir():
        raise ValueError(f"❌ ERROR: Source '{resolved_path}' is not a directory.")

    return resolved_path

def process_(input_dir: Path, output_dir: Path):
    """
    Function to find and process pdf files
    Receives path information from the calling function
    """
    do_info("=== Proces PDFs Func ===")
    script_name = Path(__file__).name  # Get this script's filename
    allowed_mime_prefix = "application/pdf"

    do_info("=== Processing PDFs ===")
    do_info(f"📂 Source Directory: {input_dir}")
    do_info(f"📂 Destination Directory: {output_dir}")
    do_info("=========================")
              
    # Take a snapshot of all files and directories under source_dir
    # Tried using the mime prefix in the rglob and scrapped it, easier to glob everything.
    if not input_dir.exists():
        raise FileNotFoundError(f"{input_dir} does not exist")
    if not input_dir.is_file() and not input_dir.is_dir():
        raise ValueError("Path exists but is neither file nor directory")
    if input_dir.is_file():
        all_files = [input_dir.resolve()]
    if input_dir.is_dir():
        all_files = list(input_dir.rglob("*")) 
    
    for file_path in all_files:  # Recursively find all files
        if not file_path.is_file():
            continue  # Skip directories including new random named output directory
        if file_path.is_relative_to(output_dir) or file_path.parts[1] in FORBIDDEN_DIRS:
            if input_dir.is_file() and file_path.parent == output_dir and file_path.parts[1] not in FORBIDDEN_DIRS:
                flag_single_file = True
                do_info("Single file output with same parent directory as input file")
            do_info(f"🛑 Skipping file inside output directory: {file_path}")
            continue  # Safety check - Avoid images copied already, and all system directories.
        do_info(f"📂{file_path}")
        do_info(f"📂{output_dir}")
        do_info(f"🔎 Expected output_dir: {output_dir} (Type: {type(output_dir)})")
      
        base_name = file_path.name
        #mime_type, _ = mimetypes.guess_type(file_path)
        mime_type = magic.from_file(file_path, mime=True)
        # Skip the script itself
        if base_name == script_name:
            do_info(f"Skipping script itself: {file_path}")
            continue

        # Skip non-mime-matching files - this mimestuff will later be routed based on action_meta
        if not mime_type or not mime_type.startswith(allowed_mime_prefix):
            do_info(f"Skipping non-{allowed_mime_prefix} file (detected as {mime_type}): {file_path}")
            continue

        # Extract base name and extension
        base, ext = os.path.splitext(base_name)
        ext = ext.lstrip('.')  # Remove leading dot from extension
        if flag_single_file:
            #this rename should just pre-emptively set a good name
            #since we already know its landing in same directory as its origin.
            base_name = f"{base}{generate_random_name()}.{ext}"
            do_info("Single file will save as sibiling to input file with name {base_name}")

        # Resolve output file path - 
        # So no confusion, output_dir is file path object so adding base_name string after / , the Path object output_dir keeps result assigned a path object.
        output_file_path = output_dir / base_name
        do_info(f"##### DESTINATION CORRECT? {output_file_path}")
        do_info("====================================")
        do_info("====================================")
        do_info("====================================")
        do_info("====================================")
        
        if output_file_path.exists():
            do_info("EXISTS")
            timestamp = int(file_path.stat().st_mtime)
            new_name = f"{base}_{timestamp}.{ext}" if ext else f"{base}_{timestamp}"
            output_file_path = output_dir / new_name
            do_info(f"New name {output_file_path}")
            do_info("==")

        #original_image = sanitize_imageload(file_path)
        #if original_image is None: continue  # Skip failed load
        #current_inflight_image = original_image.copy()
        #laststate_image = original_image.copy()
        #mask1_image = None #stubs later as array of complex diff/origin/svg/id
        #mask2_image = None #stubs later as array or complex diff/origin/svg/id
        #current_inflight_image = apply_dithering(current_inflight_image)
        #current_inflight_image = apply_upscale(current_inflight_image)
        #current_inflight_image.save(output_file_path)
        # Move the file
        #do_info(f"Moving {file_path} to {dest_file_path}")
        #shutil.move(str(file_path), str(dest_file_path))
        original_pdf = sanitize_pdfload(file_path)
        if original_pdf is None: continue  # Skip failed load
            current_inflight_pdf = save_pdf_nopassword(original_pdf)
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
    parser.add_argument("-mps", "--make-parent-single",
                    type=str.lower, choices=("true", "false"), default="false",
                    help="Create a randomly named output directory for a single input file. true or false.")
    return parser.parse_args()

def get_output_dir(input_path, parent_, make_parent_single):
    """
    Determine the output directory without creating it.
    """
    if input_path.is_file():
        if make_parent_single == "false" and input_path.resolve().parent == parent_:
            return parent_
    return parent_ / generate_random_name()

def flatten_helper(args):
    parent_ = get_valid_parent_dir(args.output_path)
    output_dir = get_output_dir(args.input_path,parent_,args.make_parent_single)
    if output_dir != parent_:
        output_dir.mkdir(exist_ok=True)
    process_(args.input_path, output_dir)

if __name__ == "__main__":
    do_info("=== BEGIN ===")
    arguments = parse_args()
    validate_args(arguments)
    flatten_helper(arguments)
    #upscale_image(args.input, args.output, scale=args.scale)
    #upscale_helper(args.input)
