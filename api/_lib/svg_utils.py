"""SVG utility functions — identical to backend version."""
import re
from typing import List
from lxml import etree


def extract_svg_paths(svg_content: str) -> List[str]:
    try:
        root = etree.fromstring(svg_content.encode("utf-8"))
        ns = {"svg": "http://www.w3.org/2000/svg"}
        paths = root.findall(".//svg:path", ns) + root.findall(".//path")
        return [p.get("d", "") for p in paths if p.get("d")]
    except Exception:
        return re.findall(r'<path[^>]+d="([^"]+)"', svg_content)


def path_complexity_score(paths: List[str]) -> float:
    total_commands = 0
    command_pattern = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]")
    for d in paths:
        total_commands += len(command_pattern.findall(d))
    return float(total_commands)
