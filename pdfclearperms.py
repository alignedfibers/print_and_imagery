#!/usr/bin/env python3

import os
import stat
import sys
import tempfile
from pathlib import Path

import pikepdf


def clear_permissions(filename):
    source = Path(filename).expanduser().resolve(strict=True)
    original_mode = stat.S_IMODE(source.stat().st_mode)

    with pikepdf.open(source, password="") as pdf:
        if not pdf.is_encrypted:
            print("PDF is already unencrypted. No changes made.")
            return

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
                    raise RuntimeError("PDF is still encrypted.")
                if len(verified.pages) != len(pdf.pages):
                    raise RuntimeError("Page count changed.")

            os.chmod(temporary, original_mode)
            os.replace(temporary, source)

        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    print(f"PDF restrictions removed: {source}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(f"Usage: {sys.argv[0]} file.pdf")

    clear_permissions(sys.argv[1])
