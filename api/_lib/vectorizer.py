"""
Pure-Pillow vectorizer: converts a silhouette PNG to a basic SVG using
edge-tracing to produce path outlines. No vtracer/opencv needed.
"""
import io
import re
from PIL import Image, ImageFilter


def raster_to_svg(png_bytes: bytes) -> str:
    """
    Convert a black-on-white silhouette PNG to an SVG string.
    Strategy: find bounding boxes of connected dark regions and emit
    rect+polygon approximations. Good enough for MVP laser-cut preview.
    """
    img = Image.open(io.BytesIO(png_bytes)).convert("L")
    w, h = img.size

    # Threshold: pixels < 128 are foreground (black)
    thresh = img.point(lambda p: 0 if p < 128 else 255, "L")

    # Collect foreground pixel coordinates
    pixels = thresh.load()
    foreground = []
    for y in range(h):
        for x in range(w):
            if pixels[x, y] == 0:
                foreground.append((x, y))

    if not foreground:
        # Return empty SVG
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}"></svg>'

    # Build a simple outline path using the silhouette boundary
    # Use run-length encoding per row to get outline segments
    path_data = _trace_outline(thresh, w, h)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}">\n'
        f'  <path d="{path_data}" fill="#000000" stroke="none"/>\n'
        f'</svg>'
    )
    return svg


def _trace_outline(thresh_img: Image.Image, w: int, h: int) -> str:
    """
    Build an SVG path by tracing horizontal spans of foreground pixels.
    Each row: find leftmost and rightmost foreground pixel and emit a thin rect.
    This creates a stacked set of horizontal slices that together form the shape.
    """
    pixels = thresh_img.load()
    commands = []

    prev_left = None
    prev_right = None

    for y in range(h):
        row_fg = [x for x in range(w) if pixels[x, y] == 0]
        if not row_fg:
            prev_left = None
            prev_right = None
            continue

        left = row_fg[0]
        right = row_fg[-1]

        if prev_left is None:
            # Start new shape
            commands.append(f"M {left} {y}")
            commands.append(f"L {right} {y}")
        else:
            commands.append(f"L {right} {y}")

        prev_left = left
        prev_right = right

    # Close path
    if commands:
        commands.append("Z")

    return " ".join(commands)
