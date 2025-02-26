# afibers_img_handling_lib/path_lock.py
import fcntl
import os
from pathlib import Path

FORBIDDEN_DIRS = {"/", "/root", "/etc", "/var", "/usr", "/dev", "/lib", "/lib64",
                  "/opt", "/run", "/sys", "/snap", "/srv", "/boot", "/cdrom", "/bin", "/sbin", "/1"}

def lock_output_dir(directory: Path):
    """
    Locks the specified directory (and all its contents) by setting an inherited lock.
    Prevents new files from appearing while processing, but does not block existing reads.    
    """

def mount_input_snapshot():
    """
    Mounts the input directory so it only sees the files that existed
    """

def 