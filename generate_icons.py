"""
Social Drishti — PWA Icon Generator
=====================================
Renders sdlogo.svg using headless Chromium into all required PWA icon sizes.

Step 1 — install:
    pip install playwright Pillow
    playwright install chromium

Step 2 — run from the SDlanding folder:
    python generate_icons.py
"""

import os
import sys
import io

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit(
        "\n[ERROR] playwright not found.\n"
        "Run:\n"
        "    pip install playwright\n"
        "    playwright install chromium\n"
    )

try:
    from PIL import Image
except ImportError:
    sys.exit("\n[ERROR] Pillow not found.\nRun:  pip install Pillow\n")

# ── config ────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SVG_PATH   = os.path.join(SCRIPT_DIR, "sdlogo.svg")

ICONS = [
    ("favicon-16x16.png",           16,  16),
    ("favicon-32x32.png",           32,  32),
    ("apple-touch-icon.png",       180, 180),
    ("android-chrome-192x192.png", 192, 192),
    ("android-chrome-512x512.png", 512, 512),
]

ICO_SIZES = [16, 32, 48]

# ── SVG renderer ──────────────────────────────────────────────
def render_svg_to_png_bytes(svg_path: str, size: int) -> bytes:
    """Render SVG at size×size using headless Chromium, return PNG bytes."""
    svg_url = "file:///" + svg_path.replace("\\", "/")

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  html, body {{ width: {size}px; height: {size}px; background: transparent; overflow: hidden; }}
  img {{ width: {size}px; height: {size}px; object-fit: contain; display: block; }}
</style>
</head>
<body><img src="{svg_url}" /></body>
</html>"""

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": size, "height": size})
        page.set_content(html, wait_until="networkidle")
        page.wait_for_timeout(200)
        png_bytes = page.screenshot(
            type="png",
            clip={"x": 0, "y": 0, "width": size, "height": size},
            omit_background=True,
        )
        browser.close()
    return png_bytes


def bytes_to_pil(png_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")


# ── main ──────────────────────────────────────────────────────
def main():
    if not os.path.isfile(SVG_PATH):
        sys.exit(
            f"\n[ERROR] SVG not found:\n  {SVG_PATH}\n"
            "Make sure sdlogo.svg is in the same folder as this script.\n"
        )

    print(f"\n  Source : {SVG_PATH}")
    print(f"  Output : {SCRIPT_DIR}")
    print(f"\n  Launching headless Chromium …\n")

    max_size = max(max(w, h) for _, w, h in ICONS)
    print(f"  Rendering master at {max_size}×{max_size} px …")
    master_bytes = render_svg_to_png_bytes(SVG_PATH, max_size)
    master       = bytes_to_pil(master_bytes)

    for filename, w, h in ICONS:
        out_path = os.path.join(SCRIPT_DIR, filename)
        if w == h == max_size:
            img = master.copy()
        else:
            img = master.resize((w, h), Image.LANCZOS)
        img.save(out_path, "PNG", optimize=True)
        print(f"  ✓  {filename:<35} {w}×{h}")

    ico_frames = [master.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]
    ico_path = os.path.join(SCRIPT_DIR, "favicon.ico")
    ico_frames[0].save(
        ico_path,
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
        append_images=ico_frames[1:],
    )
    print(f"  ✓  {'favicon.ico':<35} 16 / 32 / 48  (multi-size)")
    print("\n  All icons generated successfully!\n")


if __name__ == "__main__":
    main()
