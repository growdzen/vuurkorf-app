"""
Template integrator: merges customer SVG silhouette into the vuurkorf template SVG.
The template has an element with id="motief-gebied" that marks the placement zone.
"""
import os
from lxml import etree
from typing import Optional

TEMPLATE_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "assets", "templates", "vuurkorf_standaard.svg"
)

SVG_NS = "http://www.w3.org/2000/svg"
NSMAP = {"svg": SVG_NS}


def _get_motief_bounds(template_root: etree._Element) -> dict:
    """Extract x, y, width, height from the motief-gebied element."""
    motief = template_root.find(f".//*[@id='motief-gebied']")
    if motief is None:
        # Default fallback bounds
        return {"x": 200, "y": 150, "width": 400, "height": 300}

    tag = etree.QName(motief.tag).localname
    if tag == "rect":
        return {
            "x": float(motief.get("x", 200)),
            "y": float(motief.get("y", 150)),
            "width": float(motief.get("width", 400)),
            "height": float(motief.get("height", 300)),
        }
    # For other shapes, use bounding box approximation
    return {"x": 200, "y": 150, "width": 400, "height": 300}


def integrate_silhouette(
    customer_svg: str,
    scale: float = 1.0,
    offset_x: float = 0.0,
    offset_y: float = 0.0,
) -> str:
    """
    Integrate the customer SVG paths into the vuurkorf template.
    Returns the merged SVG as a string.
    """
    # Parse template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template_content = f.read()

    template_root = etree.fromstring(template_content.encode("utf-8"))
    customer_root = etree.fromstring(customer_svg.encode("utf-8"))

    bounds = _get_motief_bounds(template_root)

    # Get customer SVG viewBox to compute fitting transform
    customer_vb = customer_root.get("viewBox", "0 0 100 100")
    vb_parts = customer_vb.strip().split()
    c_vb_x, c_vb_y, c_vb_w, c_vb_h = (float(v) for v in vb_parts)

    # Fit customer SVG into motief bounds while preserving aspect ratio
    fit_scale_x = bounds["width"] / c_vb_w if c_vb_w else 1.0
    fit_scale_y = bounds["height"] / c_vb_h if c_vb_h else 1.0
    fit_scale = min(fit_scale_x, fit_scale_y) * scale

    # Center within bounds
    scaled_w = c_vb_w * fit_scale
    scaled_h = c_vb_h * fit_scale
    center_x = bounds["x"] + (bounds["width"] - scaled_w) / 2 + offset_x
    center_y = bounds["y"] + (bounds["height"] - scaled_h) / 2 + offset_y

    transform = (
        f"translate({center_x:.2f},{center_y:.2f}) "
        f"scale({fit_scale:.4f}) "
        f"translate({-c_vb_x:.2f},{-c_vb_y:.2f})"
    )

    # Create a group for the customer motif
    g = etree.SubElement(template_root, f"{{{SVG_NS}}}g")
    g.set("id", "klant-motief")
    g.set("transform", transform)
    g.set("fill", "#000000")
    g.set("stroke", "none")

    # Copy all paths from customer SVG into the group
    for child in customer_root:
        tag = etree.QName(child.tag).localname
        if tag in ("path", "g", "polygon", "polyline", "rect", "circle", "ellipse"):
            g.append(child)

    result = etree.tostring(template_root, encoding="unicode", xml_declaration=False)
    return result
