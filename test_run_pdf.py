#!/usr/bin/env python3
import os, sys, random, string, argparse, mimetypes
from pathlib import Path
from PIL import Image

OUTPUT_LEVEL = 'PROMPT'
FORBIDDEN_DIRS = {'/', '/root', '/etc', '/var', '/usr', '/dev', '/lib', '/lib64', '/opt', '/run', '/sys', '/snap', '/srv', '/boot', '/cdrom', '/bin', '/sbin', '/1'}


def apply_png_to_pdf_page(image, page_width_in=8.5, page_height_in=11, dpi=300):
    if not isinstance(image, Image.Image):
        raise TypeError(f'Expected a PIL Image object, got {type(image)} instead.')
    rgb_image = image.convert('RGB')
    page_width_px = int(page_width_in * dpi)
    page_height_px = int(page_height_in * dpi)
    scale = min(page_width_px / rgb_image.width, page_height_px / rgb_image.height)
    new_width = max(1, int(rgb_image.width * scale))
    new_height = max(1, int(rgb_image.height * scale))
    resized = rgb_image.resize((new_width, new_height), Image.LANCZOS)
    page = Image.new('RGB', (page_width_px, page_height_px), 'white')
    x_offset = (page_width_px - new_width) // 2
    y_offset = (page_height_px - new_height) // 2
    page.paste(resized, (x_offset, y_offset))
    return page


def sanitize_imageload(thepath):
    try:
        img = Image.open(thepath)
        img.load()
        return img
    except Exception as e:
        do_info(f'↳ Skipping file due to error: {thepath}\n   Reason: {type(e).__name__}: {e}')
        return None


def get_valid_source_dir(source_dir: str | Path) -> Path:
    resolved_path = Path(source_dir).resolve(strict=True)
    if str(resolved_path) in FORBIDDEN_DIRS:
        raise ValueError(f"❌ ERROR: Cannot run on protected system directory '{resolved_path}'.")
    if not resolved_path.is_dir():
        raise ValueError(f"❌ ERROR: Source '{resolved_path}' is not a directory.")
    return resolved_path


def is_probably_image(file_path: Path) -> bool:
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if mime_type and mime_type.startswith('image/'):
        return True
    try:
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception:
        return False


def process_images_to_pdf(source_dir: Path, dest_dir: Path):
    do_info('=== Process Images To PDF Func ===')
    script_name = Path(__file__).name
    do_info('=== Processing Images To PDF ===')
    do_info(f'📂 Source Directory: {source_dir}')
    do_info(f'📂 Destination Directory: {dest_dir}')
    do_info('=================================')

    if not source_dir.exists():
        raise FileNotFoundError(f'{source_dir} does not exist')
    if not source_dir.is_file() and not source_dir.is_dir():
        raise ValueError('Path exists but is neither file nor directory')

    all_files = [source_dir.resolve()] if source_dir.is_file() else list(source_dir.rglob('*'))

    for file_path in all_files:
        if not file_path.is_file():
            continue
        try:
            if file_path.is_relative_to(dest_dir):
                do_info(f'🛑 Skipping file inside destination directory: {file_path}')
                continue
        except Exception:
            pass
        if file_path.name == script_name:
            do_info(f'Skipping script itself: {file_path}')
            continue
        if not is_probably_image(file_path):
            do_info(f'Skipping non-image file: {file_path}')
            continue

        base = file_path.stem
        dest_file_path = dest_dir / f'{base}.pdf'
        if dest_file_path.exists():
            timestamp = int(file_path.stat().st_mtime)
            dest_file_path = dest_dir / f'{base}_{timestamp}.pdf'

        original_image = sanitize_imageload(file_path)
        if original_image is None:
            continue

        pdf_page = apply_png_to_pdf_page(original_image)
        pdf_page.save(dest_file_path, 'PDF', resolution=300)
        do_info(f'✅ Saved PDF: {dest_file_path}')

    do_info('\nThis is the end of the PDF processing loop\n')


def generate_random_name(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


def do_warning(msg):
    if OUTPUT_LEVEL not in ('PROMPT', 'INFO', 'WARNING'):
        return
    print(msg)


def do_yes_no_prompt():
    if OUTPUT_LEVEL != 'PROMPT':
        return
    if input('Do you want to continue? (yes/no): ').strip().lower() not in ('yes', 'y'):
        print('Operation cancelled by user.')
        sys.exit(0)


def do_error(msg):
    if OUTPUT_LEVEL not in ('PROMPT', 'INFO', 'WARNING', 'ERR'):
        return
    print(msg)


def do_info(msg):
    if OUTPUT_LEVEL not in ('PROMPT', 'INFO'):
        return
    print(msg)


def validate_args(args):
    global OUTPUT_LEVEL
    if args.silent != 'PROMPT':
        OUTPUT_LEVEL = args.silent
    if args.input_path is None:
        args.input_path = Path.cwd()
    if args.output_path is None:
        args.output_path = Path.cwd()

    args.input_path = Path(args.input_path)
    if not args.input_path.exists():
        raise FileNotFoundError(f'Input path does not exist: {args.input_path}')
    if not args.input_path.is_dir():
        raise ValueError(f'Input path is not a directory: {args.input_path}')
    if not os.access(args.input_path, os.R_OK | os.X_OK):
        raise PermissionError(f'Insufficient permissions for input path: {args.input_path}')

    args.output_path = Path(args.output_path)
    if not args.output_path.exists():
        raise FileNotFoundError(f'Output path does not exist: {args.output_path}')
    if not args.output_path.is_dir():
        raise ValueError(f'Output path is not a directory: {args.output_path}')
    if not os.access(args.output_path, os.R_OK | os.W_OK | os.X_OK):
        raise PermissionError(f'Insufficient permissions for output path: {args.output_path}')


def parse_args():
    parser = argparse.ArgumentParser(description='Convert all images from input-path recursively into PDFs in a new random-named folder under output-path.')
    parser.add_argument('-ip', '--input-path', default=None)
    parser.add_argument('-op', '--output-path', default=None)
    parser.add_argument('-si', '--silent', type=str, choices=('NONE', 'ERR', 'WARNING', 'INFO', 'PROMPT'), default='PROMPT')
    return parser.parse_args()


def pdf_helper(args):
    output_parent = get_valid_source_dir(args.output_path)
    output_dir = output_parent / generate_random_name()
    output_dir.mkdir(exist_ok=True)
    process_images_to_pdf(args.input_path, output_dir)
    print(output_dir)


if __name__ == '__main__':
    do_info('=== BEGIN ===')
    arguments = parse_args()
    validate_args(arguments)
    pdf_helper(arguments)
