import re
from typing import List
from lxml import etree


def extract_svg_paths(svg_content: str) -> List[str]:
    """Extract all 'd' attributes from path elements in an SVG string."""
    try:
        root = etree.fromstring(svg_content.encode("utf-8"))
        ns = {"svg": "http://www.w3.org/2000/svg"}
        paths = root.findall(".//svg:path", ns) + root.findall(".//path")
        return [p.get("d", "") for p in paths if p.get("d")]
    except Exception:
        # Fallback: regex
        return re.findall(r'<path[^>]+d="([^"]+)"', svg_content)


def path_complexity_score(paths: List[str]) -> float:
    """
    Return a complexity score based on the total number of path commands.
    Higher score = more complex geometry = higher cutting cost.
    """
    total_commands = 0
    command_pattern = re.compile(r"[MmZzLlHhVvCcSsQqTtAa]")
    for d in paths:
        total_commands += len(command_pattern.findall(d))
    return float(total_commands)
