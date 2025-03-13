import os
import shutil
import mimetypes
import random
import string
import argparse
from pathlib import Path

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
    #dest_dir = source_dir.parent  # Parent directory for file moves
    script_name = Path(__file__).name  # Get this script's filename
    allowed_mime_prefix = "image/"

    print("=== Processing Images ===")
    print(f"📂 Source Directory: {source_dir}")
    print(f"📂 Destination Directory: {dest_dir}")
    print("=========================")
    l1_dirs = []  # Store first-level directories
    loop_cancel = False  # Track when to stop looking for first-level dirs
    for f_path in source_dir.rglob("*"):  # Recursively find all files and dirs
        if loop_cancel:  # Stop if we've gone too deep
            break  
        if f_path.is_dir():  # Check if it's a directory
            if len(f_path.parts) == len(source_dir.parts) + 1:  # First-level directory?
                l1_dirs.append(f_path)  # Store first-level dir
            else:
                loop_cancel = True  # We've gone deeper, stop the 
    # Take a snapshot of all files and directories under source_dir
    # Now it's a static list from recursively find all files
    all_files = list(source_dir.rglob("*"))  

    for file_path in all_files:  # Recursively find all files
        if not file_path.is_file():
            continue  # Skip directories
        if file_path.is_relative_to(dest_dir) or file_path.parts[1] in FORBIDDEN_DIRS:
            print(f"🛑 Skipping file inside destination directory: {file_path}")
            continue
        print(f"📂{file_path}")
        print(f"📂{dest_dir}")
        print(f"📂 First-level directories in move loop: {l1_dirs}")
        print(f"🔎 Expected dest_dir: {dest_dir} (Type: {type(dest_dir)})")
      
        base_name = file_path.name
        mime_type, _ = mimetypes.guess_type(file_path)

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

def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

if __name__ == "__main__":
    source_dir = get_valid_source_dir(Path.cwd())  # Get current working directory
    output_dir = source_dir / generate_random_name()  # Create a unique output dir
    output_dir.mkdir(exist_ok=True)

    print(f"📂 Created output directory: {output_dir}")

    # Process images
    process_images(source_dir, output_dir)

    print("=== DONE ===")
