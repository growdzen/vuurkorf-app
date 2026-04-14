"""
Image processing service:
1. Remove background using rembg
2. Convert to binary silhouette using Otsu threshold (OpenCV)
3. Return PNG bytes
"""
import io
import cv2
import numpy as np
from PIL import Image


def remove_background(image_bytes: bytes) -> bytes:
    """Remove background from image using rembg."""
    from rembg import remove
    result = remove(image_bytes)
    return result


def to_silhouette(image_bytes: bytes) -> bytes:
    """
    Convert a (possibly RGBA) image to a clean black-on-white silhouette PNG.
    Uses the alpha channel if present, otherwise Otsu threshold on grayscale.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img_array = np.array(img)

    if img_array.shape[2] == 4:
        # Use alpha channel as mask
        alpha = img_array[:, :, 3]
        _, binary = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
    else:
        gray = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Morphological cleanup
    kernel = np.ones((3, 3), np.uint8)
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=2)
    binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

    # Black silhouette on white background
    silhouette = np.ones_like(img_array) * 255
    silhouette[:, :, 0] = np.where(binary > 0, 0, 255)
    silhouette[:, :, 1] = np.where(binary > 0, 0, 255)
    silhouette[:, :, 2] = np.where(binary > 0, 0, 255)
    silhouette[:, :, 3] = 255

    result_img = Image.fromarray(silhouette.astype(np.uint8), "RGBA")
    out = io.BytesIO()
    result_img.save(out, format="PNG")
    return out.getvalue()


def process_image(image_bytes: bytes) -> bytes:
    """Full pipeline: remove background -> silhouette PNG."""
    no_bg = remove_background(image_bytes)
    silhouette = to_silhouette(no_bg)
    return silhouette
