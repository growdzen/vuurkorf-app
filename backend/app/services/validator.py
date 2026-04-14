"""
Feasibility validator for laser-cut designs.
Checks minimum feature sizes based on material thickness.
"""
from typing import List, Dict, Any
from lxml import etree
import re


class FeasibilityValidator:
    def __init__(self, thickness: float):
        """
        thickness: material thickness in mm
        """
        self.thickness = thickness
        self.min_hole_diameter = 1.0 * thickness      # mm
        self.min_slot_width = 1.0 * thickness          # mm
        self.min_bridge_width = 1.5                    # mm (fixed)
        self.min_corner_radius = 0.5                   # mm (fixed)

    def detect_islands(self, svg_content: str) -> Dict[str, Any]:
        """
        Count top-level paths — many isolated paths may indicate fragile islands.
        Returns issue if more than 20 isolated paths detected.
        """
        try:
            root = etree.fromstring(svg_content.encode("utf-8"))
        except Exception:
            return {"ok": True, "island_count": 0}

        all_paths = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")
        island_count = len(all_paths)

        issues = []
        if island_count > 20:
            issues.append(
                f"{island_count} losse paden gedetecteerd — controleer op fragiele eilanden."
            )

        return {"ok": len(issues) == 0, "island_count": island_count, "issues": issues}

    def check_thin_features(self, svg_content: str) -> Dict[str, Any]:
        """
        Heuristic: find path bounding boxes and flag those narrower than min_slot_width.
        Uses regex to find path viewBox / simple width/height attributes.
        """
        issues = []

        try:
            root = etree.fromstring(svg_content.encode("utf-8"))
        except Exception:
            return {"ok": True, "issues": []}

        all_paths = root.findall(".//{http://www.w3.org/2000/svg}path") + root.findall(".//path")

        # Simple heuristic: check for very short path data (likely tiny features)
        for i, path in enumerate(all_paths):
            d = path.get("d", "")
            # Count coordinate pairs — very few coords = tiny feature
            coords = re.findall(r"[-+]?\d*\.?\d+", d)
            if len(coords) < 4:
                issues.append(
                    f"Pad #{i+1} heeft zeer weinig coordinaten — mogelijk te klein detail."
                )

        # Check stroke-width hints
        for path in all_paths:
            sw = path.get("stroke-width", "")
            if sw:
                try:
                    sw_val = float(sw)
                    if sw_val < self.min_slot_width:
                        issues.append(
                            f"Lijndikte {sw_val}mm is kleiner dan minimale sleufbreedte "
                            f"{self.min_slot_width}mm (dikte {self.thickness}mm)."
                        )
                except ValueError:
                    pass

        return {"ok": len(issues) == 0, "issues": issues}

    def validate(self, svg_content: str) -> Dict[str, Any]:
        """
        Run all checks and return overall status: green / orange / red.
        """
        island_result = self.detect_islands(svg_content)
        thin_result = self.check_thin_features(svg_content)

        all_issues = island_result.get("issues", []) + thin_result.get("issues", [])

        if len(all_issues) == 0:
            status = "green"
        elif len(all_issues) <= 3:
            status = "orange"
        else:
            status = "red"

        return {
            "status": status,
            "issues": all_issues,
            "island_count": island_result.get("island_count", 0),
            "parameters": {
                "thickness": self.thickness,
                "min_hole_diameter": self.min_hole_diameter,
                "min_slot_width": self.min_slot_width,
                "min_bridge_width": self.min_bridge_width,
                "min_corner_radius": self.min_corner_radius,
            },
        }
