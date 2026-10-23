#!/usr/bin/python3

import os, sys, shutil, random, string, argparse, mimetypes
import magic
import uuid
import torch
import cv2
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw


def comic_book_halftone_fade(image_path, output_path):
    image = Image.open(image_path).convert("L")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    for y in range(height):
        for x in range(width):
            distance = np.sqrt((x - width / 2) ** 2 + (y - height / 2) ** 2)
            max_distance = np.sqrt((width / 2) ** 2 + (height / 2) ** 2)
            fade_factor = distance / max_distance
            mask.putpixel((x, y), int(fade_factor * 255))
    halftone = image.filter(ImageFilter.CONTOUR)
    halftone = Image.composite(image, halftone, mask)
    halftone.save(output_path)


def regular_halftone_fade(image_path, output_path):
    image = Image.open(image_path).convert("L")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    for y in range(height):
        for x in range(width):
            fade_factor = (x / width + y / height) / 2
            mask.putpixel((x, y), int(fade_factor * 255))
    halftone = image.filter(ImageFilter.CONTOUR)
    halftone = Image.composite(image, halftone, mask)
    halftone.save(output_path)


def ink_washout_effect(image_path, output_path):
    image = Image.open(image_path).convert("L")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    for y in range(height):
        for x in range(width):
            fade_factor = (x / width + y / height) / 2
            mask.putpixel((x, y), int(fade_factor * 255))
    washed_out = Image.composite(image, Image.new("L", (width, height), 255), mask)
    washed_out.save(output_path)


def generate_dither_fade(image, effect_type="comic"):
    #This one may or may not be working. We can talk about it later
    image = image.convert("RGB")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    fade_start = 0.25
    for y in range(height):
        for x in range(width):
            distance_x = min(x / width, (width - x) / width)
            distance_y = min(y / height, (height - y) / height)
            distance = min(distance_x, distance_y)
            if distance > fade_start:
                fade_factor = (distance - fade_start) / (0.5 - fade_start)
                fade_factor = min(max(fade_factor, 0), 1)
                mask.putpixel((x, y), int(fade_factor * 255))
            else:
                mask.putpixel((x, y), 0)
    if effect_type == "comic":
        dithered = image.convert("1")
    elif effect_type == "regular":
        dithered = image.convert("L").convert("1")
    else:
        dithered = image.convert("L").point(lambda p: p * 0.7).convert("RGB")
    return Image.composite(image, dithered.convert("RGB"), mask)


def generate_edge_fade_dither(image, effect_type="comic"):
    #This one may or may not be working. We can talk about it later
    image = image.convert("RGB")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    sigma = min(width, height) * 0.1
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            dist_to_edge = min(dist_x, dist_y)
            fade_intensity = np.exp(-((dist_to_edge / sigma) ** 2))
            mask.putpixel((x, y), int(fade_intensity * 255))
    if effect_type == "comic":
        dithered = image.convert("1")
    elif effect_type == "regular":
        dithered = image.convert("L").convert("1")
    else:
        dithered = image.convert("L").point(lambda p: p * 0.8).convert("RGB")
    return Image.composite(image, dithered.convert("RGB"), mask)


def generate_sparse_edge_dither(image, effect_type="comic"):
    #This one may or may not be working. We can talk about it later
    image = image.convert("RGB")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    max_dither_width = width // 4
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            dist_to_edge = min(dist_x, dist_y)
            if dist_to_edge < max_dither_width:
                fade_intensity = (dist_to_edge / max_dither_width) ** 1.5
                fade_intensity = min(max(fade_intensity, 0), 1)
                mask.putpixel((x, y), int(fade_intensity * 255))
    if effect_type == "comic":
        dithered = image.convert("1")
    elif effect_type == "regular":
        dithered = image.convert("L").convert("1")
    else:
        dithered = image.convert("L").point(lambda p: p * 0.8).convert("RGB")
    return Image.composite(image, dithered.convert("RGB"), mask)


def apply_sparse_edge_dither(image):
    image = image.convert("RGB")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    max_dither_width = width // 4
    max_dither_height = height // 4
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            if dist_x < max_dither_width or dist_y < max_dither_height:
                fade_intensity = (min(dist_x, dist_y) / max(max_dither_width, max_dither_height)) ** 1.8
                fade_intensity = min(max(fade_intensity, 0), 1)
                mask.putpixel((x, y), int(fade_intensity * 255))
    dithered = image.convert("L").convert("1")
    return Image.composite(image, dithered.convert("RGB"), mask)


def apply_sparse_edge_dither_with_circular_fade(image):
    #This one may or may not be working. We can talk about it later
    image = image.convert("RGB")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    max_dither_width = width // 12
    max_dither_height = height // 12
    center_x, center_y = width // 2, height // 2
    max_radius = np.sqrt(center_x**2 + center_y**2)
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            if dist_x < max_dither_width or dist_y < max_dither_height:
                fade_intensity = (min(dist_x, dist_y) / max(max_dither_width, max_dither_height)) ** 1.8
            else:
                fade_intensity = 1
            dist_to_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            circular_fade = (dist_to_center / max_radius) ** 2.5
            final_intensity = min(fade_intensity, circular_fade)
            mask.putpixel((x, y), int(final_intensity * 255))
    dithered = image.convert("L").convert("1")
    return Image.composite(image, dithered.convert("RGB"), mask)


def apply_rounded_corners_with_blending(image, corner_radius_ratio=0.15):
    image = image.convert("RGBA")
    width, height = image.size
    mask = Image.new("L", (width, height), 255)
    corner_radius = int(min(width, height) * corner_radius_ratio)
    corner = Image.new("L", (corner_radius * 2, corner_radius * 2), 0)
    draw = ImageDraw.Draw(corner)
    draw.ellipse((0, 0, corner_radius * 2, corner_radius * 2), fill=255)
    mask.paste(corner.crop((0, 0, corner_radius, corner_radius)), (0, 0))
    mask.paste(corner.crop((corner_radius, 0, corner_radius * 2, corner_radius)), (width - corner_radius, 0))
    mask.paste(corner.crop((0, corner_radius, corner_radius, corner_radius * 2)), (0, height - corner_radius))
    mask.paste(corner.crop((corner_radius, corner_radius, corner_radius * 2, corner_radius * 2)), (width - corner_radius, height - corner_radius))
    for y in range(height):
        for x in range(width):
            dist_x = min(x, width - x)
            dist_y = min(y, height - y)
            edge_blend = min(dist_x, dist_y) / (width * 0.2)
            edge_blend = min(max(edge_blend, 0), 1)
            mask.putpixel((x, y), int(mask.getpixel((x, y)) * edge_blend))
    blended_image = Image.new("RGBA", (width, height))
    blended_image.paste(image, (0, 0), mask)
    return blended_image


def apply_rounded_corners_with_blending_numpy(image, corner_radius_ratio=0.15):
    #This one may or may not be working. We can talk about it later
    image = image.convert("RGBA")
    width, height = image.size
    mask = np.ones((height, width), dtype=np.float32) * 255
    corner_radius = int(min(width, height) * corner_radius_ratio)
    if corner_radius > 0:
        y, x = np.ogrid[:corner_radius*2, :corner_radius*2]
        dist = np.sqrt((x - corner_radius)**2 + (y - corner_radius)**2)
        corner_mask = np.where(dist <= corner_radius, 1, 0).astype(np.uint8) * 255
        mask[:corner_radius, :corner_radius] = corner_mask[:corner_radius, :corner_radius]
        mask[:corner_radius, -corner_radius:] = corner_mask[:corner_radius, -corner_radius:]
        mask[-corner_radius:, :corner_radius] = corner_mask[-corner_radius:, :corner_radius]
        mask[-corner_radius:, -corner_radius:] = corner_mask[-corner_radius:, -corner_radius:]
    dist_x = np.minimum(np.arange(width), np.arange(width)[::-1])
    dist_y = np.minimum(np.arange(height), np.arange(height)[::-1])
    edge_blend = np.minimum(dist_x[None, :] / (width * 0.2), dist_y[:, None] / (height * 0.2))
    edge_blend = np.clip(edge_blend, 0, 1)
    mask = (mask * edge_blend).astype(np.uint8)
    mask_image = Image.fromarray(mask, mode="L")
    blended_image = Image.new("RGBA", (width, height))
    blended_image.paste(image, (0, 0), mask_image)
    return blended_image


def main():
    folder = Path(__file__).resolve().parent
    source = folder / "sailboattestimg.png"
    try:
        with Image.open(source) as loaded:
            loaded.load()
            original = loaded.copy()
    except (OSError, ValueError) as exc:
        print(f"SKIPPED all effects: cannot load {source.name}: {type(exc).__name__}: {exc}")
        return

    tasks = [
        ("comic_halftone", lambda path: comic_book_halftone_fade(source, path)),
        ("regular_halftone", lambda path: regular_halftone_fade(source, path)),
        ("ink_washout", lambda path: ink_washout_effect(source, path)),
    ]
    for kind in ("comic", "regular", "ink_washout"):
        tasks.append((f"dither_fade_{kind}", lambda path, k=kind: generate_dither_fade(original.copy(), k).save(path)))
        tasks.append((f"edge_fade_dither_{kind}", lambda path, k=kind: generate_edge_fade_dither(original.copy(), k).save(path)))
        tasks.append((f"sparse_edge_dither_{kind}", lambda path, k=kind: generate_sparse_edge_dither(original.copy(), k).save(path)))
    tasks += [
        ("sparse_edge_dither", lambda path: apply_sparse_edge_dither(original.copy()).save(path)),
        ("sparse_edge_circular_fade", lambda path: apply_sparse_edge_dither_with_circular_fade(original.copy()).save(path)),
        ("rounded_blended", lambda path: apply_rounded_corners_with_blending(original.copy()).save(path)),
        ("rounded_blended_numpy", lambda path: apply_rounded_corners_with_blending_numpy(original.copy()).save(path)),
    ]
    for name, action in tasks:
        destination = folder / f"sailboattestimg_{name}.png"
        try:
            action(destination)
            print(f"SAVED {destination.name}")
        except Exception as exc:
            print(f"SKIPPED {name}: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()