#!/usr/bin/env python3
"""
Icon generator for Google Maps Scraper
Author  : Soubarna Karmakar
Copyright: © 2025 Soubarna Karmakar. All rights reserved.

Produces:  assets/icon.ico   (Windows — multi-size)
           assets/icon.icns  (macOS — generated via iconutil on Mac)
           assets/icon.png   (source 256×256)

Requires:  pip install pillow
Run once:  python create_icon.py
"""

import os
import sys
import struct
import zlib

# ── Try Pillow first ─────────────────────────────────────────────────────────
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

def make_icon_pillow(out_dir: str):
    """Generate icons using Pillow."""
    SIZE = 256

    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background circle — Google Maps blue
    margin = 12
    draw.ellipse([margin, margin, SIZE - margin, SIZE - margin],
                 fill=(30, 136, 229, 255))

    # Inner lighter circle
    i2 = 40
    draw.ellipse([i2, i2, SIZE - i2, SIZE - i2],
                 fill=(21, 101, 192, 255))

    # Map pin shape (teardrop)
    cx, cy = SIZE // 2, SIZE // 2 - 10
    r  = 52
    pr = 14  # pin tip radius

    # Circle part of pin
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255, 240))

    # Triangle pointing down
    tip_y = cy + r + 38
    draw.polygon(
        [(cx - r * 0.65, cy + r * 0.4),
         (cx + r * 0.65, cy + r * 0.4),
         (cx,            tip_y)],
        fill=(255, 255, 255, 240),
    )

    # Inner dot of pin
    dot = 18
    draw.ellipse([cx - dot, cy - dot, cx + dot, cy + dot],
                 fill=(30, 136, 229, 255))

    # Save PNG source
    png_path = os.path.join(out_dir, "icon.png")
    img.save(png_path, "PNG")
    print(f"  [OK] PNG:  {png_path}")

    # Save .ico (multiple sizes for Windows)
    ico_path = os.path.join(out_dir, "icon.ico")
    sizes    = [256, 128, 64, 48, 32, 16]
    frames   = [img.resize((s, s), Image.LANCZOS) for s in sizes]
    frames[0].save(
        ico_path, format="ICO",
        sizes=[(s, s) for s in sizes],
        append_images=frames[1:],
    )
    print(f"  [OK] ICO:  {ico_path}")

    # Save a 1024×1024 PNG for macOS icns source
    mac_src = os.path.join(out_dir, "icon_1024.png")
    img.resize((1024, 1024), Image.LANCZOS).save(mac_src, "PNG")
    print(f"  [OK] macOS source: {mac_src}")

    return ico_path, png_path, mac_src


def make_icns_macos(src_png: str, out_dir: str) -> str:
    """Create .icns using macOS iconutil (only works on macOS)."""
    import subprocess, shutil, tempfile

    iconset = tempfile.mkdtemp(suffix=".iconset")
    try:
        sizes = {
            "16": 16, "16@2x": 32,
            "32": 32, "32@2x": 64,
            "128": 128, "128@2x": 256,
            "256": 256, "256@2x": 512,
            "512": 512, "512@2x": 1024,
        }
        img = Image.open(src_png)
        for name, px in sizes.items():
            resized = img.resize((px, px), Image.LANCZOS)
            resized.save(os.path.join(iconset, f"icon_{name}.png"))

        icns_path = os.path.join(out_dir, "icon.icns")
        subprocess.run(["iconutil", "-c", "icns", iconset, "-o", icns_path],
                       check=True)
        print(f"  [OK] ICNS: {icns_path}")
        return icns_path
    except Exception as e:
        print(f"  [WARN] iconutil failed: {e}")
        print("         Manually create icon.icns from icon_1024.png")
        return ""
    finally:
        shutil.rmtree(iconset, ignore_errors=True)


def make_simple_ico_no_pillow(out_dir: str):
    """Fallback: write a minimal valid 32×32 blue-circle .ico without Pillow."""
    # Build a 32×32 RGBA raw image (blue circle on transparent background)
    SIZE   = 32
    pixels = []
    cx = cy = SIZE // 2
    for y in range(SIZE):
        for x in range(SIZE):
            dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
            if dist <= (SIZE // 2 - 2):
                pixels.extend([0x1E, 0x88, 0xE5, 0xFF])   # RGBA blue
            else:
                pixels.extend([0, 0, 0, 0])               # transparent

    raw = bytes(pixels)

    # ICO header + directory entry + BMP header (BITMAPINFOHEADER) + pixels
    bmp_header = struct.pack(
        '<IIIHHIIIIII',
        40,           # header size
        SIZE,         # width
        SIZE * 2,     # height (×2 because ICO includes XOR + AND masks)
        1,            # colour planes
        32,           # bits per pixel
        0,            # compression (BI_RGB)
        len(raw),     # image data size
        0, 0, 0, 0,   # ppm, colours
    )
    image_data = bmp_header + raw

    ico_header = struct.pack('<HHH', 0, 1, 1)             # ICONDIR
    ico_entry  = struct.pack('<BBBBHHII',
        SIZE, SIZE,   # width, height
        0,            # colour count
        0,            # reserved
        1, 32,        # planes, bit-count
        len(image_data),
        6 + 16,       # offset to image data (6-byte header + 16-byte entry)
    )

    ico_path = os.path.join(out_dir, "icon.ico")
    with open(ico_path, "wb") as f:
        f.write(ico_header + ico_entry + image_data)
    print(f"  [OK] Minimal ICO (no Pillow): {ico_path}")
    return ico_path


# ── Main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    out_dir = "assets"
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n  Generating icons into ./{out_dir}/\n")

    if HAS_PILLOW:
        ico, png, mac_src = make_icon_pillow(out_dir)
        if sys.platform == "darwin":
            make_icns_macos(mac_src, out_dir)
        else:
            print("\n  [INFO] To generate icon.icns (macOS):")
            print("         Copy this folder to a Mac and run create_icon.py there.")
    else:
        print("  [INFO] Pillow not found — generating a minimal fallback ICO.")
        print("         For a better icon:  pip install pillow  then re-run.\n")
        make_simple_ico_no_pillow(out_dir)

    print("\n  Done!\n")
    print("  To use the icon in the build:")
    print("    Windows: uncomment  icon='assets/icon.ico'  in scraper.spec")
    print("    macOS:   uncomment  icon='assets/icon.icns' in scraper_mac.spec")
    print("    Inno:    uncomment  SetupIconFile=assets\\icon.ico in installer.iss\n")
