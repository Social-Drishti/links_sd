"""
Social Drishti - PWA Icon Generator
Uses sdlogo.png + Pillow. No Playwright needed.
Run: pip install Pillow  then  python generate_icons.py
"""
import os, sys
try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow not found. Run: pip install Pillow")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PNG_PATH   = os.path.join(SCRIPT_DIR, "sdlogo.png")
ICON_BG    = (255, 255, 255, 255)

ICONS = [
    ("favicon-16x16.png",           16),
    ("favicon-32x32.png",           32),
    ("apple-touch-icon.png",       180),
    ("android-chrome-192x192.png", 192),
    ("android-chrome-512x512.png", 512),
]

def make_icon(logo, size, bg, pad_frac):
    canvas = Image.new("RGBA", (size, size), bg)
    pad = int(size * pad_frac)
    fit = logo.copy()
    fit.thumbnail((size - 2*pad, size - 2*pad), Image.LANCZOS)
    lw, lh = fit.size
    canvas.paste(fit, ((size-lw)//2, (size-lh)//2), fit)
    return canvas.convert("RGBA")

def main():
    if not os.path.isfile(PNG_PATH):
        sys.exit(f"Logo PNG not found: {PNG_PATH}")
    logo = Image.open(PNG_PATH).convert("RGBA")
    print(f"\n  Source: {PNG_PATH}\n")
    for filename, size in ICONS:
        make_icon(logo, size, ICON_BG, 0.08).save(os.path.join(SCRIPT_DIR, filename), "PNG", optimize=True)
        print(f"  OK  {filename:<40} {size}x{size}  (white bg)")
    for size in [192, 512]:
        fname = f"android-chrome-maskable-{size}x{size}.png"
        make_icon(logo, size, ICON_BG, 0.15).save(os.path.join(SCRIPT_DIR, fname), "PNG", optimize=True)
        print(f"  OK  {fname:<40} {size}x{size}  (white bg)")
    frames = [make_icon(logo, s, ICON_BG, 0.08) for s in [16, 32, 48]]
    frames[0].save(os.path.join(SCRIPT_DIR, "favicon.ico"), format="ICO", sizes=[(s,s) for s in [16,32,48]], append_images=frames[1:])
    print(f"\n  OK  favicon.ico  (16/32/48)")
    print("\n  All icons generated!\n")

if __name__ == "__main__":
    main()
