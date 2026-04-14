"""
Pillow-only image processor (no rembg/opencv).
Removes background via luminance threshold + flood-fill, returns silhouette PNG bytes.
"""
import io
from PIL import Image, ImageFilter, ImageOps


def remove_background_pillow(image_bytes: bytes) -> bytes:
    """
    Lightweight background removal using Pillow:
    1. Convert to RGBA
    2. Convert to grayscale, apply Gaussian blur to reduce noise
    3. Threshold to separate foreground from (assumed light) background
    4. Use the mask as alpha channel
    Returns RGBA PNG bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    # Work on a copy in grayscale for thresholding
    gray = img.convert("L")
    # Slight blur to smooth edges
    gray = gray.filter(ImageFilter.GaussianBlur(radius=2))
    # Invert: assume light background → foreground is dark
    # Use Otsu-like approach: threshold at mean - 10
    pixels = list(gray.getdata())
    mean_val = sum(pixels) / len(pixels)
    threshold = max(30, min(220, int(mean_val) - 10))

    # Build alpha mask: pixels darker than threshold → foreground (opaque)
    # pixels lighter → background (transparent)
    r, g, b, a = img.split()
    mask = gray.point(lambda p: 0 if p >= threshold else 255, "L")

    # Apply mask as alpha
    img.putalpha(mask)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def to_silhouette(rgba_bytes: bytes) -> bytes:
    """
    Convert RGBA image to clean black-on-white silhouette PNG using alpha channel.
    """
    img = Image.open(io.BytesIO(rgba_bytes)).convert("RGBA")
    # Create white background
    bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    # Use alpha as mask: foreground pixels → black
    r, g, b, a = img.split()
    # Threshold alpha: >10 → black foreground
    fg_mask = a.point(lambda p: 255 if p > 10 else 0, "L")
    # Black silhouette
    black = Image.new("L", img.size, 0)
    # Compose: where mask is white → black pixel; else white
    result = Image.new("RGB", img.size, (255, 255, 255))
    result.paste(Image.new("RGB", img.size, (0, 0, 0)), mask=fg_mask)
    out = io.BytesIO()
    result.save(out, format="PNG")
    return out.getvalue()


def process_image(image_bytes: bytes) -> bytes:
    """Full pipeline: remove background → silhouette PNG."""
    no_bg = remove_background_pillow(image_bytes)
    return to_silhouette(no_bg)
