#!/bin/bash

# The directory where the script itself resides (this is the source directory)
HOME_ABSPATH=$(dirname "$(realpath "$0")")
SOURCE_DIR="$HOME_ABSPATH"

# Parent directory of SOURCE_DIR is where the files will be moved
DEST_ABSPATH=$(realpath "$SOURCE_DIR"/..)

# Get the name of the script itself
script_name=$(basename "$0")

# Define allowed MIME types for images
allowed_mime_prefixes="image/"

# Echo the key variables to see what they are set to
echo "=== Initial Variable Values ==="
echo "HOME_ABSPATH (Source Directory): $HOME_ABSPATH"
echo "SOURCE_DIR (Source Directory): $SOURCE_DIR"
echo "DEST_ABSPATH (Parent of Source Directory): $DEST_ABSPATH"
echo "Script Name: $script_name"
echo "==============================="

# Use find to locate files in SOURCE_DIR and pipe them into a while loop to process them
find "$SOURCE_DIR" -type f | while read -r file; do
  base_name=$(basename "$file")
  mime_type=$(file --mime-type -b "$file")
  # Log what is being processed
  echo "Processing file: $file"

  # Get the absolute path of the file being moved
  FILE_ABSPATH=$(realpath "$file")

  # Check if the file is the script itself, and skip it if so
  if [ "$base_name" = "$script_name" ]; then
    echo "Skipping the script itself: $file"
    continue  # Skip to the next file
  fi

  # Skip if the file type is not an image.
  if [[ "$mime_type" != $allowed_mime_prefixes* ]]; then
    echo "Skipping non-image file (detected as $mime_type): $file"
    continue
  fi

  # Check if the file has an extension
  if [[ "$base_name" == *.* ]]; then
    ext="${base_name##*.}"
    base="${base_name%.*}"
  else
    ext=""
    base="$base_name"
  fi

  # Resolve the destination file's absolute path
  if [ ! -e "${DEST_ABSPATH}/${base_name}" ]; then
    DEST_FILE_ABSPATH="${DEST_ABSPATH}/${base_name}"
  else
    # If the file already exists, append a timestamp to avoid overwriting
    if [ -n "$ext" ]; then
      DEST_FILE_ABSPATH="${DEST_ABSPATH}/${base}_$(date +%s).${ext}"
    else
      DEST_FILE_ABSPATH="${DEST_ABSPATH}/${base}_$(date +%s)"
    fi
  fi

  # Move the file from FILE_ABSPATH to DEST_FILE_ABSPATH
  echo "Moving $FILE_ABSPATH to $DEST_FILE_ABSPATH"
  mv -n "$FILE_ABSPATH" "$DEST_FILE_ABSPATH"
done
