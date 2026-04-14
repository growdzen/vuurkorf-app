"""
Vectorizer service: converts a raster PNG silhouette to SVG using vtracer.
"""
import tempfile
import os
import vtracer


def raster_to_svg(png_bytes: bytes) -> str:
    """
    Convert PNG bytes to SVG string using vtracer.
    Returns SVG as a string.
    """
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_in:
        tmp_in.write(png_bytes)
        tmp_in_path = tmp_in.name

    tmp_out_path = tmp_in_path.replace(".png", ".svg")

    try:
        vtracer.convert_image_to_svg_py(
            tmp_in_path,
            tmp_out_path,
            colormode="binary",
            hierarchical="stacked",
            mode="spline",
            filter_speckle=4,
            color_precision=6,
            layer_difference=16,
            corner_threshold=60,
            length_threshold=4.0,
            max_iterations=10,
            splice_threshold=45,
            path_precision=3,
        )
        with open(tmp_out_path, "r", encoding="utf-8") as f:
            svg_content = f.read()
        return svg_content
    finally:
        if os.path.exists(tmp_in_path):
            os.unlink(tmp_in_path)
        if os.path.exists(tmp_out_path):
            os.unlink(tmp_out_path)
