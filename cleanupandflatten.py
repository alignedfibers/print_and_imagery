import os
import shutil
import mimetypes
import argparse
from pathlib import Path

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
def process_images(source_dir: Path):
    dest_dir = source_dir.parent  # Parent directory for file moves
    script_name = Path(__file__).name  # Get this script's filename
    allowed_mime_prefix = "image/"

    print("=== Processing Images ===")
    print(f"📂 Source Directory: {source_dir}")
    print(f"📂 Destination Directory: {dest_dir}")
    print("=========================")

    for file_path in source_dir.rglob("*"):  # Recursively find all files
        if not file_path.is_file():
            continue  # Skip directories

        # Check if the file is inside a forbidden directory
        if any(str(file_path).startswith(forbidden) for forbidden in FORBIDDEN_DIRS):
            print(f"❌ Skipping system directory file: {file_path}")
            continue

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
        if dest_file_path.exists():
            timestamp = int(file_path.stat().st_mtime)
            new_name = f"{base}_{timestamp}.{ext}" if ext else f"{base}_{timestamp}"
            dest_file_path = dest_dir / new_name

        # Move the file
        print(f"Moving {file_path} to {dest_file_path}")
        sh
