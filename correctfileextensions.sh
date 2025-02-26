#!/bin/bash

# Directory containing the misnamed files (adjust this path)
TARGET_DIR="."

# Go through all files in the target directory with .ext extension
for file in "$TARGET_DIR"/*.ext; do
  # Skip if no .ext files exist
  [ -e "$file" ] || continue

  # Detect the actual file type using the MIME type
  filetype=$(file --mime-type -b "$file")

  # Determine the correct extension based on file type
  case "$filetype" in
    # Text Files
    text/plain)
      ext="txt"
      ;;
    
    # Image Files
    image/jpeg)
      ext="jpg"
      ;;
    image/png)
      ext="png"
      ;;
    image/gif)
      ext="gif"
      ;;
    image/tiff)
      ext="tiff"
      ;;
    image/bmp)
      ext="bmp"
      ;;
    image/webp)
      ext="webp"
      ;;
    image/svg+xml)
      ext="svg"
      ;;
    
    # Video Files
    video/mp4)
      ext="mp4"
      ;;
    video/x-msvideo)
      ext="avi"
      ;;
    video/x-matroska)
      ext="mkv"
      ;;
    video/webm)
      ext="webm"
      ;;
    video/mpeg)
      ext="mpeg"
      ;;
    video/quicktime)
      ext="mov"
      ;;
    video/x-flv)
      ext="flv"
      ;;
    video/x-ms-wmv)
      ext="wmv"
      ;;

    # Audio Files
    audio/mpeg)
      ext="mp3"
      ;;
    audio/wav)
      ext="wav"
      ;;
    audio/ogg)
      ext="ogg"
      ;;
    audio/flac)
      ext="flac"
      ;;
    audio/aac)
      ext="aac"
      ;;
    
    # Archive Files
    application/zip)
      ext="zip"
      ;;
    application/x-tar)
      ext="tar"
      ;;
    application/gzip)
      ext="gz"
      ;;
    application/x-bzip2)
      ext="bz2"
      ;;
    
    # Document Files
    application/pdf)
      ext="pdf"
      ;;
    application/msword)
      ext="doc"
      ;;
    application/vnd.openxmlformats-officedocument.wordprocessingml.document)
      ext="docx"
      ;;
    application/vnd.ms-excel)
      ext="xls"
      ;;
    application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)
      ext="xlsx"
      ;;
    application/vnd.ms-powerpoint)
      ext="ppt"
      ;;
    application/vnd.openxmlformats-officedocument.presentationml.presentation)
      ext="pptx"
      ;;
    
    # Fallback for unknown file types
    *)
      echo "Unknown file type for $file"
      ext=""
      ;;
  esac

  # If an extension was determined, rename the file
  if [ -n "$ext" ]; then
    mv "$file" "${file%.ext}.$ext"
    echo "Renamed $file to ${file%.ext}.$ext"
  else
    echo "Skipping file $file: unknown file type."
  fi
done
