"""
DXF generator: converts SVG paths to DXF R2010 format.
Layers:
  SNIJLIJN  (color=7, white/black) — cut lines
  GRAVEERLIJN (color=3, green)     — engrave lines
  HULPLIJNEN  (color=8, dark grey) — auxiliary/construction lines
Units: mm, scale 1:1
"""
import io
import re
import ezdxf
from ezdxf.enums import TextEntityAlignment
from typing import List, Optional
from lxml import etree


def _parse_svg_paths(svg_content: str) -> List[str]:
    """Extract all path 'd' attributes from SVG."""
    try:
        root = etree.fromstring(svg_content.encode("utf-8"))
        paths = (
            root.findall(".//{http://www.w3.org/2000/svg}path")
            + root.findall(".//path")
        )
        return [p.get("d", "") for p in paths if p.get("d")]
    except Exception:
        return re.findall(r'<path[^>]+d="([^"]+)"', svg_content)


def _simple_path_to_points(d: str) -> List[tuple]:
    """
    Very simplified parser: extract M/L/Z commands to approximate as polyline points.
    For production, use svgpathtools for full bezier support.
    """
    points = []
    tokens = re.findall(r"[MmLlZzHhVvCcSsQqTtAa]|[-+]?\d*\.?\d+(?:e[-+]?\d+)?", d)
    cmd = None
    i = 0
    cx, cy = 0.0, 0.0

    while i < len(tokens):
        t = tokens[i]
        if re.match(r"[MmLlZzHhVvCcSsQqTtAa]", t):
            cmd = t
            i += 1
        else:
            try:
                if cmd in ("M", "L"):
                    x, y = float(tokens[i]), float(tokens[i + 1])
                    points.append((x, y))
                    cx, cy = x, y
                    i += 2
                elif cmd in ("m", "l"):
                    x, y = cx + float(tokens[i]), cy + float(tokens[i + 1])
                    points.append((x, y))
                    cx, cy = x, y
                    i += 2
                elif cmd in ("H",):
                    x = float(tokens[i])
                    points.append((x, cy))
                    cx = x
                    i += 1
                elif cmd in ("h",):
                    x = cx + float(tokens[i])
                    points.append((x, cy))
                    cx = x
                    i += 1
                elif cmd in ("V",):
                    y = float(tokens[i])
                    points.append((cx, y))
                    cy = y
                    i += 1
                elif cmd in ("v",):
                    y = cy + float(tokens[i])
                    points.append((cx, y))
                    cy = y
                    i += 1
                elif cmd in ("C", "c"):
                    # Cubic bezier — approximate with endpoint only
                    if cmd == "C":
                        x, y = float(tokens[i + 4]), float(tokens[i + 5])
                    else:
                        x, y = cx + float(tokens[i + 4]), cy + float(tokens[i + 5])
                    points.append((x, y))
                    cx, cy = x, y
                    i += 6
                elif cmd in ("Z", "z"):
                    if points:
                        points.append(points[0])  # close path
                    break
                else:
                    i += 1
            except (IndexError, ValueError):
                i += 1

    return points


def svg_to_dxf(svg_content: str, output_path: Optional[str] = None) -> bytes:
    """
    Convert SVG paths to DXF R2010.
    Returns DXF file as bytes.
    """
    doc = ezdxf.new(dxfversion="R2010")
    doc.units = 4  # mm

    msp = doc.modelspace()

    # Define layers
    layers = doc.layers
    if "SNIJLIJN" not in layers:
        doc.layers.add("SNIJLIJN", color=7)
    if "GRAVEERLIJN" not in layers:
        doc.layers.add("GRAVEERLIJN", color=3)
    if "HULPLIJNEN" not in layers:
        doc.layers.add("HULPLIJNEN", color=8)

    paths = _parse_svg_paths(svg_content)

    for i, d in enumerate(paths):
        points = _simple_path_to_points(d)
        if len(points) < 2:
            continue

        # DXF uses Y-up; SVG uses Y-down — flip Y axis
        # Determine layer: first path = cut, rest = cut by default
        layer = "SNIJLIJN"

        dxf_points = [(x, -y, 0) for x, y in points]

        if len(dxf_points) >= 2:
            msp.add_lwpolyline(
                [(p[0], p[1]) for p in dxf_points],
                dxfattribs={"layer": layer, "closed": True},
            )

    # Add title block in HULPLIJNEN layer
    msp.add_text(
        "Vuurkorf Personalisatie — Snijbestand",
        dxfattribs={"layer": "HULPLIJNEN", "height": 5},
    ).set_placement((0, -20), align=TextEntityAlignment.LEFT)

    if output_path:
        doc.saveas(output_path)
        with open(output_path, "rb") as f:
            return f.read()
    else:
        stream = io.StringIO()
        doc.write(stream)
        return stream.getvalue().encode("utf-8")
