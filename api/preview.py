"""
GET /api/preview?job_id=...
Returns merged SVG + validation + pricing from /tmp outputs written by process.py.
"""
import json
import sys
import os
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

OUTPUT_DIR = Path("/tmp/vuurkorf_outputs")


def _cors_headers(h):
    h.send_header("Access-Control-Allow-Origin", "*")
    h.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
    h.send_header("Access-Control-Allow-Headers", "Content-Type")


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        job_id = params.get("job_id", [None])[0]

        if not job_id:
            self._error(400, "Geen job_id opgegeven.")
            return

        merged_path = OUTPUT_DIR / f"{job_id}_merged.svg"
        customer_svg_path = OUTPUT_DIR / f"{job_id}_customer.svg"

        if not merged_path.exists():
            self._error(404, f"Preview voor job '{job_id}' niet gevonden. Verwerk het bestand eerst via /api/process.")
            return

        svg_content = merged_path.read_text(encoding="utf-8")

        self._json(200, {
            "job_id": job_id,
            "status": "completed",
            "svg": svg_content,
        })

    def do_GET_svg(self):
        """Raw SVG endpoint — handled via vercel.json routing to /api/preview/svg."""
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        job_id = params.get("job_id", [None])[0]

        if not job_id:
            self._error(400, "Geen job_id opgegeven.")
            return

        merged_path = OUTPUT_DIR / f"{job_id}_merged.svg"
        if not merged_path.exists():
            self._error(404, "SVG niet gevonden.")
            return

        svg_content = merged_path.read_text(encoding="utf-8").encode()
        self.send_response(200)
        self.send_header("Content-Type", "image/svg+xml")
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(svg_content)

    def _json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status, detail):
        self._json(status, {"error": detail})
