import os
import shutil
import mimetypes
import argparse
import fcntl
from pathlib import Path

# Directories to NEVER process
FORBIDDEN_DIRS = {"/", "/root", "/etc", "/var", "/usr", "/dev", "/lib", "/lib64",
                  "/opt", "/run", "/sys", "/snap", "/srv", "/boot", "/cdrom", "/bin", "/sbin", "/1"}

# Function to analyze source path, count files, and check permissions
def analyzeSourcePath(source_dir: str) -> Path:
    resolved_path = Path(source_dir).resolve(strict=True)  # Resolves `.` and `..`, follows symlinks

    # Check if the source directory is inside a forbidden path
    for forbidden in FORBIDDEN_DIRS:
        if str(resolved_path).startswith(forbidden + "/"):  # Ensure we're checking subpaths correctly
            raise ValueError(f"❌ ERROR: Cannot run inside protected system directory '{forbidden}'. Found: {resolved_path}")

    if not resolved_path.is_dir():
        raise ValueError(f"❌ ERROR: Source '{resolved_path}' is not a directory.")

    # Ensure we have read permissions on the directory and subdirectories
    for root, dirs, files in os.walk(resolved_path):
        root_path = Path(root)
        if not os.access(root_path, os.R_OK):
            raise ValueError(f"❌ ERROR: No read permission for '{root_path}'.")

        for file in files:
            file_path = root_path / file
            if not os.access(file_path, os.R_OK):
                raise ValueError(f"❌ ERROR: Cannot read file '{file_path}'. Permission denied.")

    # Count readable files
    total_files = sum(1 for _ in resolved_path.rglob("*") if _.is_file() and os.access(_, os.R_OK))

    print(f"✅ Source directory validated. Total readable files: {total_files}")

    return resolved_path

# Function to lock the directory during processing to prevent writes
def lock_directory(directory: Path):
    lock_file = directory / ".dir_lock"
    lock_file.touch(exist_ok=True)  # Ensure file exists

    try:
        lock_fd = open(lock_file, "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)  # Exclusive lock (non-blocking)
        print(f"🔒 Directory locked: {directory}")
        return lock_fd
    except IOError:
        raise ValueError(f"❌ ERROR: Another process is modifying '{directory}'. Try again later.")

# Function to process images while preventing other writes
def process_images(source_dir: Path):
    dest_dir = source_dir.parent  # Parent directory for file moves
    script_name = Path(__file__).name  # Get this script's filename
    allowed_mime_prefix = "image/"

    lock_fd = lock_directory(source_dir)  # Lock the directory

    print("=== Processing Images ===")
    print(f"📂 Source Directory: {source_dir}")
    print(f"📂 Destination Directory: {dest_dir}")
    print("=========================")

    for file_path in source_dir.rglob("*"):  # Recursively find all files
        if not file_path.is_file():
  
